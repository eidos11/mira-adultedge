# created: 2026-05-01

"""AdultEdge Eval - deterministic Lane 1 invariant checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from mira.system_b.engine.critic.contract import (
    ADMISSIBLE_LLM_TAGS,
    REGISTRY_PATTERN_IDS,
    ROUTE_VTYPE_ALLOWED,
    VERDICT_LANGUAGE_RE,
    LaneOneInput,
    ViolationObject,
)


@dataclass(frozen=True)
class InvariantResult:
    invariant_name: str
    passed: bool
    severity: Literal["blocking", "warning", "info"]
    evidence: str | None = None
    invariant_ref: str | None = None


def check_forbidden_output(output: LaneOneInput) -> InvariantResult:
    """Invariant #1: LLM output must not emit final verdict language."""

    if output.llm_output_tag is not None and output.llm_output_tag not in ADMISSIBLE_LLM_TAGS:
        return InvariantResult(
            invariant_name="forbidden_output",
            passed=False,
            severity="blocking",
            evidence=f"Non-admissible LLM tag: {output.llm_output_tag}",
            invariant_ref="#1",
        )

    if output.response_text and VERDICT_LANGUAGE_RE.search(output.response_text):
        return InvariantResult(
            invariant_name="forbidden_output",
            passed=False,
            severity="blocking",
            evidence="Response contains verdict-like language.",
            invariant_ref="#1",
        )

    return InvariantResult(
        invariant_name="forbidden_output",
        passed=True,
        severity="info",
        invariant_ref="#1",
    )


def check_label_registry_consistency(pattern_ids: list[str]) -> InvariantResult:
    """Validate pattern IDs against pattern_registry.yaml canonical IDs."""

    invalid_pattern_ids = sorted(set(pattern_ids) - REGISTRY_PATTERN_IDS)
    if invalid_pattern_ids:
        return InvariantResult(
            invariant_name="label_registry_consistency",
            passed=False,
            severity="blocking",
            evidence=f"Unknown pattern ids: {', '.join(invalid_pattern_ids)}",
            invariant_ref="label_registry_consistency",
        )
    return InvariantResult(
        invariant_name="label_registry_consistency",
        passed=True,
        severity="info",
        invariant_ref="label_registry_consistency",
    )


def check_route_vtype_consistency(
    primary_route: Literal["D", "I", "A", "factual"],
    vtype_claimed: Literal["D", "I", "A"],
) -> InvariantResult:
    """Check route.vtype contains or allows the claimed stage vtype."""

    if vtype_claimed not in ROUTE_VTYPE_ALLOWED[primary_route]:
        return InvariantResult(
            invariant_name="route_vtype_consistency",
            passed=False,
            severity="blocking",
            evidence=f"Route {primary_route} does not allow vtype {vtype_claimed}.",
            invariant_ref="route_vtype_consistency",
        )
    return InvariantResult(
        invariant_name="route_vtype_consistency",
        passed=True,
        severity="info",
        invariant_ref="route_vtype_consistency",
    )


def check_llm_verdict_violation_count(violations: list[ViolationObject]) -> dict[str, int | bool]:
    """Aggregate LLM verdict-related violations for session-level reporting."""

    count = sum(1 for violation in violations if violation.check_id in {6, 7})
    return {"llm_verdict_violation_count": count, "has_violation": count > 0}


def run_all_invariants(
    output: LaneOneInput,
    violations: list[ViolationObject],
) -> list[InvariantResult]:
    """Run the four W3 Lane 1 invariant checks without any LLM call."""

    count_result = check_llm_verdict_violation_count(violations)
    count_passed = count_result["llm_verdict_violation_count"] == 0
    return [
        check_forbidden_output(output),
        check_label_registry_consistency(output.pattern_ids),
        check_route_vtype_consistency(output.primary_route, output.vtype_claimed),
        InvariantResult(
            invariant_name="llm_verdict_violation_count",
            passed=bool(count_passed),
            severity="info" if count_passed else "blocking",
            evidence=str(count_result),
            invariant_ref="#1",
        ),
    ]
