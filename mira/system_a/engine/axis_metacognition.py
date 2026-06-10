
"""Metacognition-axis heuristics for System A diagnostic snapshots."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from mira.contracts import JudgmentDistribution
from mira.system_a.engine.context_adapter import get_vocabulary_set, has_signal

ConfidenceBand = Literal["low", "medium", "high"]


@dataclass(frozen=True)
class MetacognitionResult:
    """Sparse metacognition assessment produced by keyword heuristics."""

    confidence_band: ConfidenceBand
    judgment_distribution: JudgmentDistribution | None
    primary_leaks: list[str]


_EFFORT_VOLUME_RE = re.compile(
    r"("
    r"많이\s*공부|열심히|공부를?\s*많이|시간을?\s*많이|노력했|"
    r"studied\s+(a\s+lot|hard)|study\s+a\s+lot|worked\s+hard|put\s+in\s+effort|"
    r"spent\s+hours|many\s+hours|read\s+a\s+lot|reread"
    r")",
    re.IGNORECASE,
)
_VAGUE_SELF_ASSESSMENT_RE = re.compile(
    r"("
    r"이해한\s*것\s*같|이해되는\s*것\s*같|아는\s*것\s*같|될\s*것\s*같|"
    r"i\s+think\s+i\s+understand|i\s+feel\s+like\s+i\s+understand|"
    r"seems\s+like\s+i\s+understand|kind\s+of\s+understand|probably\s+understand"
    r")",
    re.IGNORECASE,
)
_WILLPOWER_RE = re.compile(
    r"(게으|의지|나태|노력\s*부족|lazy|laziness|willpower|no\s+discipline)",
    re.IGNORECASE,
)
_EXTERNAL_BLAME_RE = re.compile(
    r"(탓|때문에\s*망|선생님\s*때문|환경\s*때문|because\s+of\s+the|not\s+my\s+fault)",
    re.IGNORECASE,
)
_EVIDENCE_BASED_RE = re.compile(
    r"("
    r"설명할\s*수|적용해\s*봤|적용했다|테스트해\s*봤|근거|"
    r"i\s+can\s+explain|can\s+explain|i\s+applied|applied\s+it|"
    r"tested\s+myself|retrieval|evidence|example\s+without\s+looking"
    r")",
    re.IGNORECASE,
)
_SPECIFIC_GAP_RE = re.compile(
    r"("
    r"부분이\s*약|부분에서\s*막|어렵다|부족한\s*부분|헷갈리는\s*부분|"
    r"struggle\s+with|weak\s+in|gap\s+in|specific\s+gap|not\s+yet\s+able"
    r")",
    re.IGNORECASE,
)
_MONITORING_RE = re.compile(
    r"("
    r"확인해\s*봤|점검했|검증했|비교해\s*봤|피드백을?\s*받|"
    r"i\s+checked|checked\s+whether|verified|monitored|compared|got\s+feedback"
    r")",
    re.IGNORECASE,
)

_DISTRIBUTIONS: dict[ConfidenceBand, dict[str, float]] = {
    "low": {
        "certain": 0.2,
        "reserved": 0.3,
        "needs_more_info": 0.3,
        "undecidable": 0.2,
    },
    "medium": {
        "certain": 0.4,
        "reserved": 0.3,
        "needs_more_info": 0.2,
        "undecidable": 0.1,
    },
    "high": {
        "certain": 0.6,
        "reserved": 0.2,
        "needs_more_info": 0.15,
        "undecidable": 0.05,
    },
}


def assess_metacognition(
    claim: str,
    intake_fields: dict[str, object] | None = None,
    context_type: str = "adult_learning",
) -> MetacognitionResult:
    """Assess whether self-judgment is effort-based, evidence-based, or mixed."""

    text = _with_intake_text(claim, intake_fields)
    vocabulary = get_vocabulary_set(context_type)
    context_low_signals = vocabulary.metacognition_signals.get("low", ())
    context_high_signals = vocabulary.metacognition_signals.get("high", ())

    low_matches = [
        bool(_EFFORT_VOLUME_RE.search(text)),
        bool(_VAGUE_SELF_ASSESSMENT_RE.search(text)),
        bool(_WILLPOWER_RE.search(text)),
        bool(_EXTERNAL_BLAME_RE.search(text)),
        has_signal(text, context_low_signals),
    ]
    high_matches = [
        bool(_EVIDENCE_BASED_RE.search(text)),
        bool(_SPECIFIC_GAP_RE.search(text)),
        bool(_MONITORING_RE.search(text)),
        has_signal(text, context_high_signals),
    ]

    has_low_signal = any(low_matches)
    has_high_signal = any(high_matches)
    has_any_signal = has_low_signal or has_high_signal

    if has_low_signal and not has_high_signal:
        confidence: ConfidenceBand = "low"
    elif has_high_signal and not has_low_signal:
        confidence = "high"
    else:
        confidence = "medium"

    distribution = (
        JudgmentDistribution(**_DISTRIBUTIONS[confidence]) if has_any_signal else None
    )
    return MetacognitionResult(
        confidence_band=confidence,
        judgment_distribution=distribution,
        primary_leaks=_primary_leaks(text),
    )


def _primary_leaks(text: str) -> list[str]:
    leaks: list[str] = []
    if _EFFORT_VOLUME_RE.search(text):
        leaks.append("fluency_illusion")
    if _VAGUE_SELF_ASSESSMENT_RE.search(text):
        leaks.append("calibration_gap")
    if _WILLPOWER_RE.search(text):
        leaks.append("willpower_blame")
    if _EXTERNAL_BLAME_RE.search(text):
        leaks.append("self_serving_attribution")
    return leaks


def _with_intake_text(claim: str, intake_fields: dict[str, object] | None) -> str:
    parts = [claim]
    if intake_fields:
        for value in intake_fields.values():
            if isinstance(value, str):
                parts.append(value)
            elif isinstance(value, list):
                parts.extend(item for item in value if isinstance(item, str))
    return " ".join(part.strip() for part in parts if part and part.strip())


__all__ = ["MetacognitionResult", "assess_metacognition"]
