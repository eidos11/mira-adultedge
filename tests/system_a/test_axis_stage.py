
"""Tests for System A stage-axis heuristics."""

from __future__ import annotations

from mira.system_a.engine.axis_stage import assess_stage


def test_concept_stage_on_korean_beginner_claim() -> None:
    result = assess_stage("처음이라 논리를 배우고 싶다.")

    assert result.stage_estimate == "concept"


def test_concept_stage_on_english_beginner_claim() -> None:
    result = assess_stage("I am a beginner and want to learn statistics.")

    assert result.stage_estimate == "concept"


def test_framework_stage_on_korean_structure_claim() -> None:
    result = assess_stage("전체 구조를 잡았고 개념을 정리했다.")

    assert result.stage_estimate == "framework"


def test_practice_stage_on_korean_exercise_claim() -> None:
    result = assess_stage("예제를 해보고 문제를 풀고 있다.")

    assert result.stage_estimate == "practice"


def test_reality_stage_on_korean_application_claim() -> None:
    result = assess_stage("실제 업무에 적용했고 결과를 냈다.")

    assert result.stage_estimate == "reality"


def test_governance_concept_stage_on_proposal_claim() -> None:
    result = assess_stage("This proposal needs initial review.", context_type="governance")

    assert result.stage_estimate == "concept"


def test_governance_reality_stage_on_production_claim() -> None:
    result = assess_stage("The policy is now in production operation.", context_type="governance")

    assert result.stage_estimate == "reality"


def test_default_to_concept_on_ambiguous_claim() -> None:
    result = assess_stage("The next step is unclear.")

    assert result.stage_estimate == "concept"
    assert result.cognitive_layer_signature is None


def test_cognitive_layer_signature_populated_on_clear_stage_signal() -> None:
    result = assess_stage("I'm practicing by working through exercises.")

    assert result.cognitive_layer_signature == "adult_learning practice-feedback layer"
