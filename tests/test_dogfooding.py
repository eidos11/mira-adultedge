"""Dogfooding tests for governance and decision contexts."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from mira.pipeline import PipelineResult, run_minimal_loop
from mira.system_a import DiagnosticEngine, DiagnosticSnapshot
from mira.system_a.engine.axis_stage import assess_stage
from mira.system_a.engine.axis_task_definition import assess_task_definition
from mira.system_a.engine.context_adapter import get_vocabulary_set

PROJECT_ROOT = Path(__file__).resolve().parents[1]
STAGE_VOCABULARY_PATH = PROJECT_ROOT / "eval" / "stage_vocabulary.yaml"


def test_run_minimal_loop_governance_runs_without_error() -> None:
    result = run_minimal_loop(
        "This proposal needs review before pilot deployment.",
        context_type="governance",
    )

    assert isinstance(result, PipelineResult)
    assert result.diagnostic_snapshot is not None


def test_run_minimal_loop_decision_runs_without_error() -> None:
    result = run_minimal_loop(
        "The team is comparing alternatives before limited rollout.",
        context_type="decision",
    )

    assert isinstance(result, PipelineResult)
    assert result.diagnostic_snapshot is not None


def test_governance_korean_claim_produces_valid_snapshot() -> None:
    snapshot = DiagnosticEngine().diagnose(
        "Coordinator 검토가 항상 S2 작업을 지연시킨다.",
        trace_id="dogfood-gov-ko-001",
        context_type="governance",
    )

    assert isinstance(snapshot, DiagnosticSnapshot)
    assert snapshot.diagnostic_hypothesis.stage_estimate == "concept"
    assert snapshot.confidence_band in ("low", "medium", "high")


def test_governance_english_claim_produces_valid_snapshot() -> None:
    snapshot = DiagnosticEngine().diagnose(
        "Coordinator review always delays S2 delivery.",
        trace_id="dogfood-gov-en-001",
        context_type="governance",
    )

    assert isinstance(snapshot, DiagnosticSnapshot)
    assert snapshot.diagnostic_hypothesis.stage_estimate == "concept"
    assert snapshot.confidence_band in ("low", "medium", "high")


def test_governance_proposal_claim_maps_to_concept_stage() -> None:
    result = assess_stage("새로운 제안은 검토 필요 상태다.", context_type="governance")

    assert result.stage_estimate == "concept"
    assert result.cognitive_layer_signature == "governance proposal layer"


def test_governance_production_claim_maps_to_reality_stage() -> None:
    result = assess_stage("The policy is now in production enforcement.", context_type="governance")

    assert result.stage_estimate == "reality"
    assert result.cognitive_layer_signature == "governance production layer"


def test_governance_noun_goal_detects_efficiency_as_noun_goal() -> None:
    result = assess_task_definition("거버넌스 효율화가 필요하다.", context_type="governance")

    assert result.is_noun_goal is True
    assert result.goal_reframed == "governance"


def test_governance_action_goal_detects_reduce_output() -> None:
    result = assess_task_definition("S2 작업 지연을 줄인다.", context_type="governance")

    assert result.is_noun_goal is False
    assert result.goal_reframed is None


def test_willpower_blame_invariant_enforced_in_governance_context() -> None:
    result = run_minimal_loop(
        "Coordinator가 의지가 부족해서 검토가 지연된다.",
        context_type="governance",
    )
    blame = re.compile(r"(의지\s*부족|의지가\s*부족|willpower|lazy|laziness)", re.IGNORECASE)

    assert result.overlay.avoid_willpower_blame is True
    # spec §6 (coaching gate redesign): system_text must not blame willpower; the coaching
    # block MAY use "lack of willpower" as an instructional counter-example (Mnemo-approved
    # exemption — memory: project_mira_willpower_blame_exclusion_rationale). Assert the
    # non-coaching portion only. (Reconciliation flagged for Mnemo step-4 review.)
    system_portion = result.report.split("## Coaching")[0]
    assert not blame.search(system_portion)


def test_self_referential_governance_claim_produces_meaningful_diagnosis() -> None:
    result = run_minimal_loop(
        "Coordinator 검토가 항상 S2 작업을 지연시킨다.",
        context_type="governance",
    )
    snapshot = result.diagnostic_snapshot
    candidate_ids = {candidate.pattern_id for candidate in result.overlay.pattern_candidates}

    assert snapshot is not None
    assert snapshot.diagnostic_hypothesis.stage_estimate == "concept"
    assert snapshot.system_a_cues.possible_cognitive_layer_signature == (
        "governance proposal layer"
    )
    assert snapshot.confidence_band == "low"
    assert {"hasty_generalization", "oversimplified_cause"} & candidate_ids


def test_context_adapter_exposes_decision_and_governance_vocabularies() -> None:
    governance_vocab = get_vocabulary_set("governance")
    decision_vocab = get_vocabulary_set("decision")

    assert "효율화" in governance_vocab.task_definition_signals["noun_goal"]
    assert "대안 비교" in decision_vocab.stage_signals["framework"]


def test_stage_vocabulary_manifest_has_three_contexts_four_stages_two_languages() -> None:
    data = yaml.safe_load(STAGE_VOCABULARY_PATH.read_text(encoding="utf-8"))

    assert set(data) == {"adult_learning", "governance", "decision"}
    for context in data.values():
        assert set(context) == {"concept", "framework", "practice", "reality"}
        for stage in context.values():
            assert set(stage) == {"ko", "en"}
            assert stage["ko"]
            assert stage["en"]
