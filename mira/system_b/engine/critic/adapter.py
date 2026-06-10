"""Lane 1 critic adapter — pipeline ↔ critic contract bridge.

M1 Reduced scope: checks #6 (admissible tag), #7 (verdict language),
#9 (pattern_id registry).
"""

from __future__ import annotations

import re
from typing import Literal

from mira.contracts.minimal import PatternCandidate, PSRResult
from mira.system_b.engine.critic.contract import (
    AuditResult,
    LaneOneInput,
    PSRDecomposition,
    contract_critic,
)

# check 15 (willpower_blame_trigger) was removed in the coaching-gate redesign (spec §5):
# willpower blocking moved to report._check_report_violations; the Lane-1 reduced critic
# no longer gates on it. Kept out of the active set so the declaration matches the contract
# (contract_critic never emits check_id 15).
V1_CHECKS: frozenset[int] = frozenset({6, 7, 9})

_CLAIM_TYPE_MAP: dict[str, Literal["argument", "self_assessment", "causal_explanation"]] = {
    "self_assessment": "self_assessment",
    "normative": "argument",
    "descriptive": "argument",
    "unclassified": "argument",
}

_PSR_QUOTE_RE = re.compile(r"(?:전제\(P\)|전략\(S\)|결과\(R\)):\s*[^\n]+")
_BRACKET_QUOTE_RE = re.compile(r"[「『].*?[」』]")


def psr_result_to_decomposition(psr: PSRResult) -> PSRDecomposition:
    """Convert PSRResult (4 fields) to PSRDecomposition (9 fields).

    M1: conservative defaults for additional fields.
    M2 will use System A diagnostic info for precise values.
    """
    return PSRDecomposition(
        P_appraisal=psr.P_appraisal,
        P_latitude="medium",
        claim_type=_CLAIM_TYPE_MAP.get(psr.claim_type, "argument"),
        S_strategy=psr.S_strategy,
        S_exclusivity="open",
        R_projection=psr.R_projection,
        R_emotional_load="neutral",
    )


def mask_learner_citations(text: str) -> str:
    """Mask learner-quoted text to prevent false positives.

    Report quotes learner's own words (which may contain blame
    language). The quotation itself is not system-generated blame.
    """
    masked = _BRACKET_QUOTE_RE.sub("[LEARNER_CITATION]", text)
    masked = _PSR_QUOTE_RE.sub("[PSR_QUOTE]", masked)
    return masked


def build_lane_one_input(
    psr: PSRResult,
    candidates: list[PatternCandidate],
    vtype: str,
    *,
    response_text: str | None = None,
    trace_id: str | None = None,
    llm_output_tag: str | None = None,
) -> LaneOneInput:
    """Build LaneOneInput from pipeline data structures."""
    masked_text = mask_learner_citations(response_text) if response_text else None

    return LaneOneInput(
        psr=psr_result_to_decomposition(psr),
        pattern_ids=[c.pattern_id for c in candidates],
        primary_route=vtype,
        vtype_claimed=vtype,
        llm_output_tag=llm_output_tag,
        response_text=masked_text,
        trace_id=trace_id,
    )


STRUCTURAL_CHECKS: frozenset[int] = frozenset({2, 3, 4})


def run_reduced_critic(
    psr: PSRResult,
    candidates: list[PatternCandidate],
    vtype: str,
    *,
    response_text: str | None = None,
    trace_id: str | None = None,
) -> tuple[bool, AuditResult]:
    """Run Lane 1 critic with M1 Reduced scope.

    Returns (lane1_pass, full_audit_result).
    Structural checks (#2/#3/#4) always block. V1_CHECKS (#6/#7/#9)
    are the content-level Reduced scope.
    """
    lane_input = build_lane_one_input(
        psr, candidates, vtype,
        response_text=response_text,
        trace_id=trace_id,
    )

    audit = contract_critic(lane_input)

    active_checks = V1_CHECKS | STRUCTURAL_CHECKS
    has_blocking = any(
        v.severity == "blocking" and v.check_id in active_checks
        for v in audit.violations
    )

    return (not has_blocking, audit)
