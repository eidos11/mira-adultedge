"""PSR decomposition and D/I/A routing.

PSR = Premise / Strategy / Result (hypothesis-based judgment framework, founder-original, distinct from Popper).
D/I/A = Deductive / Inductive / Abductive verification type.
Reference: Architecture v4.3 §4.2, PSR 3-stage anchor.
"""

from __future__ import annotations

import re
from typing import Literal

from mira.contracts.minimal import PSRPrior, PSRResult, VType

_CAUSAL_ATTRIBUTION_MARKERS = re.compile(
    r"(때문|because|원인|이유|cause|탓)", re.IGNORECASE
)
_DEDUCTIVE_MARKERS = re.compile(
    r"(therefore|그러므로|따라서|if\s.*then|이면\s.*이다|반드시|논리적으로)",
    re.IGNORECASE,
)
_GENERALIZATION_MARKERS = re.compile(
    r"(항상|always|\bevery\b|never|모두|전부)", re.IGNORECASE
)
_ABDUCTIVE_MARKERS = re.compile(
    r"(아마|maybe|probably|perhaps|것\s*같|인\s*것\s*같|추측|guess)",
    re.IGNORECASE,
)


def decompose_psr(claim: str, prior: PSRPrior | None = None) -> PSRResult:
    """Extract P/S/R components from a learner claim.

    M1: heuristic extraction. Sentences are split and assigned to P/S/R
    based on position and keyword signals. Prior hints override when present.
    """
    claim_clean = neutralize_blame(claim)
    sentences = _split_sentences(claim_clean)

    if prior and prior.P_appraisal and prior.S_strategy and prior.R_projection:
        return PSRResult(
            P_appraisal=neutralize_blame(prior.P_appraisal),
            S_strategy=neutralize_blame(prior.S_strategy),
            R_projection=neutralize_blame(prior.R_projection),
            claim_type=_classify_claim(claim),
        )

    if len(sentences) >= 3:
        p, s, r = sentences[0], sentences[1], sentences[-1]
    elif len(sentences) == 2:
        p, s, r = sentences[0], sentences[1], sentences[1]
    else:
        p = s = r = sentences[0] if sentences else claim

    return PSRResult(
        P_appraisal=neutralize_blame(prior.P_appraisal if prior and prior.P_appraisal else p),
        S_strategy=neutralize_blame(prior.S_strategy if prior and prior.S_strategy else s),
        R_projection=neutralize_blame(prior.R_projection if prior and prior.R_projection else r),
        claim_type=_classify_claim(claim),
    )


def route_vtype(claim: str, prior: PSRPrior | None = None) -> VType:
    """Determine D/I/A verification type from claim signals.

    Architecture v4.3: causal attribution ("X 때문에 Y") → A (oversimplified_cause).
    Formal deduction ("X이면 반드시 Y") → D. Generalization → I.
    """
    if prior and prior.suggested_vtype:
        return prior.suggested_vtype

    if _DEDUCTIVE_MARKERS.search(claim):
        return "D"
    if _CAUSAL_ATTRIBUTION_MARKERS.search(claim):
        return "A"
    if _GENERALIZATION_MARKERS.search(claim):
        return "I"
    if _ABDUCTIVE_MARKERS.search(claim):
        return "A"
    return "D"


def _classify_claim(claim: str) -> str:
    lowered = claim.lower()
    if any(kw in lowered for kw in ("나는", "i am", "i'm", "내가", "저는")):
        return "self_assessment"
    if any(kw in lowered for kw in ("해야", "should", "must", "ought")):
        return "normative"
    return "descriptive"


_BLAME_NEUTRALIZE = [
    (re.compile(r"게으[르른를][기며고서]?", re.IGNORECASE), "동기 부족으로"),
    (re.compile(r"게으름", re.IGNORECASE), "동기 부족"),
    (re.compile(r"게을러[서]?", re.IGNORECASE), "동기가 부족하여"),
    (re.compile(r"나태[하해한]?[서며고]?", re.IGNORECASE), "자기조절 어려움으로"),
    (re.compile(r"의지력?\s*[이가]?\s*부족", re.IGNORECASE), "자기 조절 어려움"),
    (re.compile(r"의지[가이]?\s*약", re.IGNORECASE), "자기 조절 어려움"),
    (re.compile(r"노력\s*[이이]?\s*부족", re.IGNORECASE), "학습 전략 미비"),
    (re.compile(r"laziness|lazy", re.IGNORECASE), "low motivation"),
    (re.compile(r"willpower", re.IGNORECASE), "self-regulation"),
    (re.compile(r"lack\s+of\s+(effort|willpower|discipline)", re.IGNORECASE), "learning strategy gap"),
]


def neutralize_blame(text: str) -> str:
    for pattern, replacement in _BLAME_NEUTRALIZE:
        text = pattern.sub(replacement, text)
    return text


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"[.!?。]\s*|\n+", text.strip())
    return [p.strip() for p in parts if p.strip()]
