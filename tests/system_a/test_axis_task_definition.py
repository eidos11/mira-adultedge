
"""Tests for System A task-definition-axis heuristics."""

from __future__ import annotations

from mira.system_a.engine.axis_task_definition import assess_task_definition


def test_noun_goal_detected_on_domain_only_korean_claim() -> None:
    result = assess_task_definition("영어 실력을 늘리고 싶다.")

    assert result.is_noun_goal is True


def test_noun_goal_detected_on_domain_only_english_claim() -> None:
    result = assess_task_definition("I want better English ability.")

    assert result.is_noun_goal is True


def test_action_goal_detected_on_verb_output_korean_claim() -> None:
    result = assess_task_definition("영어로 업무 이메일을 작성할 수 있어야 한다.")

    assert result.is_noun_goal is False


def test_action_goal_detected_on_verb_output_english_claim() -> None:
    result = assess_task_definition("I can write a short project report in English.")

    assert result.is_noun_goal is False


def test_goal_reframed_populated_when_noun_goal_detected() -> None:
    result = assess_task_definition("프로그래밍 실력을 키우고 싶다.")

    assert result.goal_reframed == "coding"


def test_goal_reframed_is_none_when_action_goal_detected() -> None:
    result = assess_task_definition("I can build a small script and test it.")

    assert result.goal_reframed is None


def test_weakest_force_identified_from_claim_content() -> None:
    result = assess_task_definition("시간이 부족하고 피곤해서 계획을 유지하기 어렵다.")

    assert result.weakest_force == "time_energy"


def test_empty_claim_returns_default_noun_goal_without_reframe() -> None:
    result = assess_task_definition("")

    assert result.is_noun_goal is True
    assert result.goal_reframed is None
    assert result.weakest_force is None
