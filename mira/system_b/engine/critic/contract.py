# created: 2026-05-01

"""
AdultEdge Eval - Lane 1 Contract Critic.

Deterministic schema + invariant boundary checks (NO LLM calls).
Isomorphic with Anthropic Constitutional Classifiers++ Stage 1 linear probe.

Reference: 08_critic_contract.md §3 + pattern_registry.yaml + cv_interface.py.
"""

from __future__ import annotations

from enum import StrEnum
from typing import ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field

type RouteEnum = Literal["D", "I", "A", "factual"]
type VType = Literal["D", "I", "A"]
type Severity = Literal["blocking", "warning", "info"]
type AuditStatus = Literal["pass", "fail", "review_required"]
type GateDecision = Literal["pass", "fail"]
type AdmissibleLLMTag = Literal[
    "typed_ir_candidate",
    "classification_support",
    "slippage_annotation",
    "explanation_rewrite",
    "fallback_answer",
]

ADMISSIBLE_LLM_TAGS: frozenset[str] = frozenset(
    {
        "typed_ir_candidate",
        "classification_support",
        "slippage_annotation",
        "explanation_rewrite",
        "fallback_answer",
    }
)

ROUTE_VTYPE_ALLOWED: dict[str, frozenset[str]] = {
    "D": frozenset({"D"}),
    "I": frozenset({"I"}),
    "A": frozenset({"A"}),
    # Factual checks are evidence-grounding checks and may support any D/I/A
    # stage once routed out of the low-latitude factual boundary.
    "factual": frozenset({"D", "I", "A"}),
}

from mira.contracts.safety_patterns import VERDICT_LANGUAGE_RE


class PatternId(StrEnum):
    """Canonical pattern IDs from pattern_registry.yaml §1 plus neutral labels."""

    GENETIC_FALLACY = "genetic_fallacy"
    FALSE_DILEMMA = "false_dilemma"
    APPEAL_TO_AUTHORITY = "appeal_to_authority"
    APPEAL_TO_CONSEQUENCES = "appeal_to_consequences"
    PERFECTIONIST_FALLACY = "perfectionist_fallacy"
    BEGGING_THE_QUESTION = "begging_the_question"
    HASTY_GENERALIZATION = "hasty_generalization"
    ANECDOTAL_EVIDENCE = "anecdotal_evidence"
    PREDICTION_FALLACY = "prediction_fallacy"
    SUNK_COST = "sunk_cost"
    COMPOSITION_FALLACY = "composition_fallacy"
    FLUENCY_ILLUSION = "fluency_illusion"
    EFFORT_HEURISTIC = "effort_heuristic"
    RECOGNITION_RETRIEVAL_CONFUSION = "recognition_retrieval_confusion"
    CONFUSING_EXPLANATION_EXCUSE = "confusing_explanation_excuse"
    OVERSIMPLIFIED_CAUSE = "oversimplified_cause"
    SELF_SERVING_ATTRIBUTION = "self_serving_attribution"
    IDENTITY_PROTECTIVE_REASONING = "identity_protective_reasoning"
    POST_HOC_RATIONALIZATION = "post_hoc_rationalization"
    SOCIAL_COMPARISON = "social_comparison"
    CATASTROPHIZING = "catastrophizing"
    WILLPOWER_BLAME = "willpower_blame"
    METHODOLOGY_QUERY = "methodology_query"
    STRUCTURAL_INFORMATION_REQUEST = "structural_information_request"
    EXPLORATORY_QUESTION = "exploratory_question"


REGISTRY_PATTERN_IDS: frozenset[str] = frozenset(item.value for item in PatternId)


class StrictModel(BaseModel):
    """Pydantic v2 strict base for deterministic Lane 1 contracts."""

    model_config: ClassVar[ConfigDict] = ConfigDict(strict=True, extra="forbid")


class PSRDecomposition(StrictModel):
    """Core PSR decomposition aligned with cv_interface.py."""

    P_appraisal: str
    P_latitude: Literal["low", "medium", "high", "extreme"]
    claim_type: Literal["argument", "self_assessment", "causal_explanation"]
    S_strategy: str
    S_exclusivity: Literal["open", "claimed_exclusive"]
    R_projection: str
    R_emotional_load: Literal["fear", "desire", "neutral"]
    P_evidential_basis: Literal["strong", "moderate", "weak", "absent"] | None = None
    R_magnitude: Literal["proportionate", "exaggerated", "catastrophized"] | None = None


class LaneOneInput(StrictModel):
    """Input surface for the deterministic Lane 1 contract critic."""

    psr: PSRDecomposition
    pattern_ids: list[str]
    primary_route: RouteEnum
    vtype_claimed: VType
    llm_output_tag: str | None = None
    response_text: str | None = None
    trace_id: str | None = None
    # Optional audit surfaces for the remaining Lane 1 checks.
    run_id: str | None = None
    test_id: str | None = None
    m3_input_complete: bool = True
    compound_route_required: bool = False
    compound_route_vtypes: list[VType] = Field(default_factory=list)
    activation_graph: dict[str, list[str]] | None = None
    response_has_intervention: bool = True
    oracle_level: Literal["gold", "silver", "bronze", "shadow"] = "gold"


class ViolationObject(StrictModel):
    """Single Lane 1 contract violation."""

    check_id: int = Field(ge=1, le=15)
    check_name: str
    severity: Severity
    evidence: str
    w0_ref: str | None = None


class AuditResult(StrictModel):
    """Lane 1 audit result based on 08_critic_contract.md §4."""

    run_id: str
    test_id: str | None
    status: AuditStatus
    lane_results_contract_status: Literal["pass", "fail"]
    violations: list[ViolationObject]
    severity_count: dict[str, int]
    decision_release_gate: GateDecision


def contract_critic(output: LaneOneInput) -> AuditResult:
    """Run the 15 deterministic Lane 1 checks in 08 §3 order."""

    violations: list[ViolationObject] = []

    def record(violation: ViolationObject) -> bool:
        violations.append(violation)
        return violation.severity == "blocking"

    # #1 JSON schema valid: guaranteed by LaneOneInput construction.
    # #2 Required fields present.
    if _has_blank_required_field(output):
        record(
            ViolationObject(
                check_id=2,
                check_name="required_fields_present",
                severity="blocking",
                evidence="One or more required PSR string fields are blank.",
                w0_ref="E-017",
            )
        )
        return _build_audit_result(output, violations)

    # #3 trace_id exists.
    if not output.trace_id or not output.trace_id.strip():
        record(
            ViolationObject(
                check_id=3,
                check_name="trace_id_exists",
                severity="blocking",
                evidence="trace_id is missing or blank.",
                w0_ref="Invariant #6",
            )
        )
        return _build_audit_result(output, violations)

    # #4 PSR required 7 fields.
    if not _psr_required_fields_complete(output.psr):
        record(
            ViolationObject(
                check_id=4,
                check_name="psr_required_7_fields",
                severity="blocking",
                evidence="PSR required 7-field structure is incomplete.",
            )
        )
        return _build_audit_result(output, violations)

    # #5 PSR nullable fields use known enums: guaranteed by Pydantic Literals.

    # #6 LLM output admissible tag.
    if output.llm_output_tag is not None and output.llm_output_tag not in ADMISSIBLE_LLM_TAGS:
        record(
            ViolationObject(
                check_id=6,
                check_name="llm_output_admissible_tag",
                severity="blocking",
                evidence=f"Non-admissible LLM tag: {output.llm_output_tag}",
                w0_ref="Invariant #1",
            )
        )
        return _build_audit_result(output, violations)

    # #7 No verdict language.
    if output.response_text and VERDICT_LANGUAGE_RE.search(output.response_text):
        record(
            ViolationObject(
                check_id=7,
                check_name="no_verdict_language",
                severity="blocking",
                evidence="Response text contains verdict-like language.",
                w0_ref="Invariant #1",
            )
        )
        return _build_audit_result(output, violations)

    # #8 Route enum valid: guaranteed by Pydantic Literal.

    # #9 Pattern id in registry.
    invalid_pattern_ids = sorted(set(output.pattern_ids) - REGISTRY_PATTERN_IDS)
    if invalid_pattern_ids:
        record(
            ViolationObject(
                check_id=9,
                check_name="pattern_id_in_registry",
                severity="blocking",
                evidence=f"Unknown pattern ids: {', '.join(invalid_pattern_ids)}",
                w0_ref="E-013,E-027",
            )
        )
        return _build_audit_result(output, violations)

    # #10 Route-vtype consistency.
    if not _route_vtype_consistent(output.primary_route, output.vtype_claimed):
        severity: Severity = "blocking" if output.oracle_level == "gold" else "warning"
        if record(
            ViolationObject(
                check_id=10,
                check_name="route_vtype_consistency",
                severity=severity,
                evidence=(
                    f"Route {output.primary_route} does not allow claimed vtype "
                    f"{output.vtype_claimed}."
                ),
                w0_ref="E-001,E-004,E-007,E-014,E-024",
            )
        ):
            return _build_audit_result(output, violations)

    # #11 M3 input completeness.
    if not output.m3_input_complete:
        record(
            ViolationObject(
                check_id=11,
                check_name="m3_input_completeness",
                severity="blocking",
                evidence="M3 input completeness flag is false.",
                w0_ref="E-002",
            )
        )
        return _build_audit_result(output, violations)

    # #12 Compound route aggregation.
    if output.compound_route_required and len(set(output.compound_route_vtypes)) < 2:
        record(
            ViolationObject(
                check_id=12,
                check_name="compound_route_aggregation",
                severity="blocking",
                evidence="Compound route requires at least two verification types.",
                w0_ref="E-029",
            )
        )
        return _build_audit_result(output, violations)

    # #13 DAG circular.
    if output.activation_graph is not None and _has_cycle(output.activation_graph):
        record(
            ViolationObject(
                check_id=13,
                check_name="dag_circular",
                severity="blocking",
                evidence="Activation graph contains a cycle.",
                w0_ref="Invariant",
            )
        )
        return _build_audit_result(output, violations)

    # #14 Response has intervention.
    if not output.response_has_intervention:
        record(
            ViolationObject(
                check_id=14,
                check_name="response_has_intervention",
                severity="warning",
                evidence="Response does not include an intervention element.",
            )
        )

    return _build_audit_result(output, violations)


def _has_blank_required_field(output: LaneOneInput) -> bool:
    fields = (
        output.psr.P_appraisal,
        output.psr.S_strategy,
        output.psr.R_projection,
    )
    return any(not field.strip() for field in fields)


def _psr_required_fields_complete(psr: PSRDecomposition) -> bool:
    return all(
        (
            bool(psr.P_appraisal.strip()),
            psr.P_latitude in {"low", "medium", "high", "extreme"},
            psr.claim_type in {"argument", "self_assessment", "causal_explanation"},
            bool(psr.S_strategy.strip()),
            psr.S_exclusivity in {"open", "claimed_exclusive"},
            bool(psr.R_projection.strip()),
            psr.R_emotional_load in {"fear", "desire", "neutral"},
        )
    )


def _route_vtype_consistent(primary_route: str, vtype_claimed: str) -> bool:
    return vtype_claimed in ROUTE_VTYPE_ALLOWED.get(primary_route, frozenset())


def _has_cycle(graph: dict[str, list[str]]) -> bool:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        for child in graph.get(node, []):
            if visit(child):
                return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in graph)


def _build_audit_result(output: LaneOneInput, violations: list[ViolationObject]) -> AuditResult:
    severity_count = {
        "blocking": sum(1 for violation in violations if violation.severity == "blocking"),
        "warning": sum(1 for violation in violations if violation.severity == "warning"),
        "info": sum(1 for violation in violations if violation.severity == "info"),
    }
    has_blocking = severity_count["blocking"] > 0
    has_warning = severity_count["warning"] > 0
    status: AuditStatus
    if has_blocking:
        status = "fail"
    elif has_warning:
        status = "review_required"
    else:
        status = "pass"

    return AuditResult(
        run_id=output.run_id or "lane1-run-unset",
        test_id=output.test_id,
        status=status,
        lane_results_contract_status="fail" if has_blocking else "pass",
        violations=violations,
        severity_count=severity_count,
        decision_release_gate="fail" if has_blocking else "pass",
    )
