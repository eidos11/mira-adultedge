
"""
pytest test suite - Lane 1 contract + 4 invariant checks.

1 rule = 1 fixture principle (09_rule_fixture_protocol.md §1).
"""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from mira.system_b.engine.critic.contract import (
    LaneOneInput,
    PSRDecomposition,
    ViolationObject,
    contract_critic,
)
from mira.system_b.engine.critic.invariants import (
    check_forbidden_output,
    check_label_registry_consistency,
    check_llm_verdict_violation_count,
    check_route_vtype_consistency,
    run_all_invariants,
)


def make_psr(**overrides: object) -> PSRDecomposition:
    data: dict[str, object] = {
        "P_appraisal": "The learner thinks one failed quiz proves low ability.",
        "P_latitude": "medium",
        "claim_type": "self_assessment",
        "S_strategy": "The learner considers repeating the same study loop.",
        "S_exclusivity": "open",
        "R_projection": "The learner expects limited progress.",
        "R_emotional_load": "fear",
    }
    data.update(overrides)
    return PSRDecomposition.model_validate(data)


def make_input(**overrides: object) -> LaneOneInput:
    data: dict[str, object] = {
        "psr": make_psr(),
        "pattern_ids": ["fluency_illusion"],
        "primary_route": "I",
        "vtype_claimed": "I",
        "llm_output_tag": "classification_support",
        "response_text": "구조적 누수를 먼저 확인하고 작은 검증 과제를 설정합니다.",
        "trace_id": "trace-001",
    }
    data.update(overrides)
    return LaneOneInput.model_validate(data)


def test_psr_valid_input_passes() -> None:
    result = contract_critic(make_input())

    assert result.status == "pass"
    assert result.decision_release_gate == "pass"


def test_psr_missing_required_field_blocks() -> None:
    data = make_psr().model_dump()
    del data["P_appraisal"]

    with pytest.raises(ValidationError):
        PSRDecomposition.model_validate(data)


def test_psr_blank_required_field_blocks() -> None:
    result = contract_critic(make_input(psr=make_psr(P_appraisal=" ")))

    assert result.status == "fail"
    assert result.violations[0].check_id == 2


def test_psr_invalid_latitude_blocks() -> None:
    with pytest.raises(ValidationError):
        PSRDecomposition.model_validate(
            {
                **make_psr().model_dump(),
                "P_latitude": "wide",
            }
        )


def test_psr_nullable_enum_valid_passes() -> None:
    result = contract_critic(
        make_input(psr=make_psr(P_evidential_basis="weak", R_magnitude="exaggerated"))
    )

    assert result.status == "pass"


def test_psr_nullable_enum_invalid_blocks() -> None:
    with pytest.raises(ValidationError):
        PSRDecomposition.model_validate(
            {
                **make_psr().model_dump(),
                "P_evidential_basis": "unknown",
            }
        )


def test_trace_id_missing_blocks() -> None:
    result = contract_critic(make_input(trace_id=None))

    assert result.status == "fail"
    assert result.violations[0].check_id == 3


def test_trace_id_present_passes() -> None:
    result = contract_critic(make_input(trace_id="trace-ok"))

    assert result.status == "pass"


def test_llm_admissible_tag_valid_passes() -> None:
    result = contract_critic(make_input(llm_output_tag="typed_ir_candidate"))

    assert result.status == "pass"


def test_llm_non_admissible_tag_blocks() -> None:
    result = contract_critic(make_input(llm_output_tag="final_verdict"))

    assert result.status == "fail"
    assert result.violations[0].check_id == 6


def test_no_verdict_language_passes() -> None:
    result = contract_critic(make_input(response_text="가능한 구조 누수를 점검합니다."))

    assert result.status == "pass"


def test_verdict_language_blocks() -> None:
    result = contract_critic(make_input(response_text="진단 결과: 당신은 게으른 사람입니다."))

    assert result.status == "fail"
    assert result.violations[0].check_id == 7


def test_route_enum_valid_passes() -> None:
    result = contract_critic(make_input(primary_route="factual", vtype_claimed="A"))

    assert result.status == "pass"


def test_route_enum_invalid_blocks() -> None:
    with pytest.raises(ValidationError):
        LaneOneInput.model_validate({**make_input().model_dump(), "primary_route": "X"})


def test_pattern_id_in_registry_passes() -> None:
    result = contract_critic(
        make_input(pattern_ids=["false_dilemma", "willpower_blame", "methodology_query"])
    )

    assert result.status == "pass"


def test_pattern_id_not_in_registry_blocks() -> None:
    result = contract_critic(make_input(pattern_ids=["invented_pattern"]))

    assert result.status == "fail"
    assert result.violations[0].check_id == 9


def test_route_vtype_consistent_passes() -> None:
    result = contract_critic(make_input(primary_route="A", vtype_claimed="A"))

    assert result.status == "pass"


def test_route_vtype_mismatch_blocks_gold() -> None:
    result = contract_critic(make_input(primary_route="D", vtype_claimed="A"))

    assert result.status == "fail"
    assert result.violations[0].check_id == 10


def test_route_vtype_mismatch_warns_non_gold() -> None:
    result = contract_critic(
        make_input(primary_route="D", vtype_claimed="A", oracle_level="silver")
    )

    assert result.status == "review_required"
    assert result.violations[0].severity == "warning"


def test_m3_input_complete_passes() -> None:
    result = contract_critic(make_input(m3_input_complete=True))

    assert result.status == "pass"


def test_m3_input_incomplete_blocks() -> None:
    result = contract_critic(make_input(m3_input_complete=False))

    assert result.status == "fail"
    assert result.violations[0].check_id == 11


def test_compound_route_aggregation_complete_passes() -> None:
    result = contract_critic(
        make_input(compound_route_required=True, compound_route_vtypes=["D", "I"])
    )

    assert result.status == "pass"


def test_compound_route_aggregation_missing_blocks() -> None:
    result = contract_critic(
        make_input(compound_route_required=True, compound_route_vtypes=["D"])
    )

    assert result.status == "fail"
    assert result.violations[0].check_id == 12


def test_dag_acyclic_passes() -> None:
    result = contract_critic(make_input(activation_graph={"a": ["b"], "b": ["c"]}))

    assert result.status == "pass"


def test_dag_circular_blocks() -> None:
    result = contract_critic(make_input(activation_graph={"a": ["b"], "b": ["a"]}))

    assert result.status == "fail"
    assert result.violations[0].check_id == 13


def test_response_has_intervention_passes() -> None:
    result = contract_critic(make_input(response_has_intervention=True))

    assert result.status == "pass"


def test_response_missing_intervention_warns() -> None:
    result = contract_critic(make_input(response_has_intervention=False))

    assert result.status == "review_required"
    assert result.violations[0].check_id == 14
    assert result.violations[0].severity == "warning"


def test_willpower_mention_no_longer_blocks() -> None:
    # check 15 (willpower_blame_trigger) removed per spec D4 (coaching gate redesign).
    result = contract_critic(
        make_input(
            response_text="의지가 부족해서 실패한 것입니다.",
        )
    )

    assert result.status == "pass"
    assert not any(v.check_id == 15 for v in result.violations)


def test_willpower_mention_with_structural_language_passes() -> None:
    result = contract_critic(
        make_input(
            response_text="의지 문제가 아니라 구조적 누수를 확인해야 합니다.",
        )
    )

    assert result.status == "pass"


def test_no_willpower_blame_passes() -> None:
    result = contract_critic(make_input(response_text="복습 구조와 피드백 간격을 조정합니다."))

    assert result.status == "pass"


def test_lane_input_extra_field_blocks_schema() -> None:
    data: dict[str, Any] = make_input().model_dump()
    data["extra"] = "not allowed"

    with pytest.raises(ValidationError):
        LaneOneInput.model_validate(data)


def test_forbidden_output_invariant_triggered() -> None:
    result = check_forbidden_output(make_input(llm_output_tag="verdict"))

    assert result.passed is False
    assert result.severity == "blocking"


def test_forbidden_output_invariant_clean() -> None:
    result = check_forbidden_output(make_input())

    assert result.passed is True


def test_label_registry_consistency_valid() -> None:
    result = check_label_registry_consistency(["oversimplified_cause", "methodology_query"])

    assert result.passed is True


def test_label_registry_consistency_invalid_id() -> None:
    result = check_label_registry_consistency(["unknown"])

    assert result.passed is False
    assert result.severity == "blocking"


def test_route_vtype_consistency_matching() -> None:
    result = check_route_vtype_consistency("I", "I")

    assert result.passed is True


def test_route_vtype_consistency_mismatch() -> None:
    result = check_route_vtype_consistency("D", "A")

    assert result.passed is False


def test_llm_verdict_violation_count_zero() -> None:
    result = check_llm_verdict_violation_count([])

    assert result == {"llm_verdict_violation_count": 0, "has_violation": False}


def test_llm_verdict_violation_count_nonzero() -> None:
    violations = [
        ViolationObject(
            check_id=6,
            check_name="llm_output_admissible_tag",
            severity="blocking",
            evidence="bad tag",
            w0_ref="Invariant #1",
        )
    ]

    result = check_llm_verdict_violation_count(violations)

    assert result == {"llm_verdict_violation_count": 1, "has_violation": True}


def test_run_all_invariants_returns_four_results() -> None:
    result = run_all_invariants(make_input(), [])

    assert [item.invariant_name for item in result] == [
        "forbidden_output",
        "label_registry_consistency",
        "route_vtype_consistency",
        "llm_verdict_violation_count",
    ]

