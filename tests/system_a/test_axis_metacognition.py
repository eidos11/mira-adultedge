
"""Tests for System A metacognition-axis heuristics."""

from __future__ import annotations

import pytest

from mira.system_a.engine.axis_metacognition import assess_metacognition


def test_low_metacognition_on_effort_volume_korean_claim() -> None:
    result = assess_metacognition("열심히 많이 공부했으니 이해했을 것이다.")

    assert result.confidence_band == "low"


def test_low_metacognition_on_effort_volume_english_claim() -> None:
    result = assess_metacognition("I studied a lot and worked hard, so I understand it.")

    assert result.confidence_band == "low"


def test_high_metacognition_on_evidence_based_korean_claim() -> None:
    result = assess_metacognition("개념을 설명할 수 있고 예제에 적용해 봤다.")

    assert result.confidence_band == "high"


def test_high_metacognition_on_evidence_based_english_claim() -> None:
    result = assess_metacognition("I can explain the idea and tested myself without notes.")

    assert result.confidence_band == "high"


def test_medium_metacognition_on_mixed_signals() -> None:
    result = assess_metacognition("열심히 공부했지만 어떤 부분이 약한지도 확인해 봤다.")

    assert result.confidence_band == "medium"


def test_low_metacognition_detects_fluency_illusion_leak() -> None:
    result = assess_metacognition("I read a lot and spent hours rereading.")

    assert "fluency_illusion" in result.primary_leaks


@pytest.mark.parametrize(
    ("claim", "expected"),
    [
        ("I studied a lot.", (0.2, 0.3, 0.3, 0.2)),
        ("I can explain it with evidence.", (0.6, 0.2, 0.15, 0.05)),
        ("I studied hard, but I checked my weak part.", (0.4, 0.3, 0.2, 0.1)),
    ],
)
def test_judgment_distribution_is_proportional_to_confidence_band(
    claim: str,
    expected: tuple[float, float, float, float],
) -> None:
    result = assess_metacognition(claim)

    assert result.judgment_distribution is not None
    assert result.judgment_distribution.certain == pytest.approx(expected[0])
    assert result.judgment_distribution.reserved == pytest.approx(expected[1])
    assert result.judgment_distribution.needs_more_info == pytest.approx(expected[2])
    assert result.judgment_distribution.undecidable == pytest.approx(expected[3])


def test_empty_or_neutral_claim_returns_medium_by_default() -> None:
    result = assess_metacognition("")

    assert result.confidence_band == "medium"
    assert result.primary_leaks == []
    assert result.judgment_distribution is None
