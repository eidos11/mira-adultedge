
"""Stage-axis heuristics for System A diagnostic snapshots."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from mira.system_a.engine.context_adapter import count_signal_hits, get_vocabulary_set

StageEstimate = Literal["concept", "framework", "practice", "reality"]


@dataclass(frozen=True)
class StageResult:
    """Heuristic stage estimate and optional layer cue."""

    stage_estimate: StageEstimate
    cognitive_layer_signature: str | None


_ADULT_LEARNING_PATTERNS: dict[StageEstimate, re.Pattern[str]] = {
    "concept": re.compile(
        r"(배우고\s*싶|시작하려|처음|입문|want\s+to\s+learn|getting\s+started|beginner|what\s+is)",
        re.IGNORECASE,
    ),
    "framework": re.compile(
        r"(이해했다|구조를?\s*잡|정리했|i\s+understand\s+the\s+structure|organized|mapped\s+out|framework)",
        re.IGNORECASE,
    ),
    "practice": re.compile(
        r"(연습|문제를?\s*풀|예제를?\s*해|practicing|solving\s+problems|working\s+through\s+exercises|exercise)",
        re.IGNORECASE,
    ),
    "reality": re.compile(
        r"(실제\s*업무|프로젝트에서|결과를?\s*냈|실무에\s*적용|applied\s+at\s+work|used\s+in\s+my\s+project|got\s+results)",
        re.IGNORECASE,
    ),
}
_STAGE_ORDER: tuple[StageEstimate, ...] = ("concept", "framework", "practice", "reality")


def assess_stage(
    claim: str,
    intake_fields: dict[str, object] | None = None,
    context_type: str = "adult_learning",
) -> StageResult:
    """Estimate the learner or governance stage from vocabulary signals."""

    text = _with_intake_text(claim, intake_fields)
    vocabulary = get_vocabulary_set(context_type)

    scores = {
        stage: _stage_score(text, stage, vocabulary.stage_signals[stage])
        for stage in _STAGE_ORDER
    }
    best_stage = max(_STAGE_ORDER, key=lambda stage: (scores[stage], _STAGE_ORDER.index(stage)))
    if scores[best_stage] == 0:
        return StageResult(stage_estimate="concept", cognitive_layer_signature=None)

    return StageResult(
        stage_estimate=best_stage,
        cognitive_layer_signature=vocabulary.stage_signatures[best_stage],
    )


def _stage_score(text: str, stage: StageEstimate, signals: tuple[str, ...]) -> int:
    pattern_score = len(_ADULT_LEARNING_PATTERNS[stage].findall(text))
    signal_score = count_signal_hits(text, signals)
    return pattern_score + signal_score


def _with_intake_text(claim: str, intake_fields: dict[str, object] | None) -> str:
    parts = [claim]
    if intake_fields:
        for value in intake_fields.values():
            if isinstance(value, str):
                parts.append(value)
            elif isinstance(value, list):
                parts.extend(item for item in value if isinstance(item, str))
    return " ".join(part.strip() for part in parts if part and part.strip())


__all__ = ["StageEstimate", "StageResult", "assess_stage"]
