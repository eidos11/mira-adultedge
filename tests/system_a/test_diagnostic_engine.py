# M1 minimal — tests for DiagnosticEngine with DiagnosticSnapshot types
# Original (runtime-dependent) tests archived to reference/_archived-code/tests/

from __future__ import annotations

import re

from mira.system_a import DiagnosticEngine, DiagnosticSnapshot, diagnose_claim

_VERDICT_CUE_RE = re.compile(
    r"(pattern_detected|diagnostic_verdict|verdict\s*:|판정|진단\s*결과)"
)


def test_diagnose_returns_snapshot_for_korean_learning_claim() -> None:
    snapshot = DiagnosticEngine().diagnose(
        "영어 실력을 늘리고 싶지만 열심히 공부해도 적용이 어렵다.",
        trace_id="trace-ko-001",
    )

    assert isinstance(snapshot, DiagnosticSnapshot)
    assert snapshot.diagnostic_hypothesis.goal_reframed is not None


def test_diagnose_returns_snapshot_for_english_learning_claim() -> None:
    snapshot = diagnose_claim(
        "I can explain the concept and solve practice problems.",
        trace_id="trace-en-001",
    )

    assert isinstance(snapshot, DiagnosticSnapshot)
    assert snapshot.confidence_band == "high"


def test_diagnose_returns_snapshot_for_governance_claim() -> None:
    snapshot = DiagnosticEngine().diagnose(
        "This proposal moves from pilot review toward production operation.",
        trace_id="trace-gov-001",
        context_type="governance",
    )

    assert isinstance(snapshot, DiagnosticSnapshot)
    assert snapshot.diagnostic_hypothesis.stage_estimate == "reality"
    assert snapshot.system_a_cues.possible_cognitive_layer_signature == (
        "governance production layer"
    )


def test_snapshot_trace_id_matches_input() -> None:
    snapshot = DiagnosticEngine().diagnose("I want to learn coding.", trace_id="trace-match")

    assert snapshot.trace_id == "trace-match"


def test_primary_leaks_populated_when_effort_language_detected() -> None:
    snapshot = DiagnosticEngine().diagnose(
        "많이 공부했고 시간을 많이 썼다.",
        trace_id="trace-leak-001",
    )

    assert "fluency_illusion" in snapshot.diagnostic_hypothesis.primary_leaks


def test_no_verdict_language_in_system_a_cues() -> None:
    snapshot = DiagnosticEngine().diagnose(
        "I can write a project report after working through exercises.",
        trace_id="trace-sds-003",
    )
    cue_values = [
        snapshot.system_a_cues.possible_claim_type,
        snapshot.system_a_cues.possible_cognitive_layer_signature,
    ]

    assert all(value is None or _VERDICT_CUE_RE.search(value) is None for value in cue_values)


def test_confidence_band_is_valid_value() -> None:
    snapshot = DiagnosticEngine().diagnose(
        "I struggle with English but I am working on it.",
        trace_id="trace-conf-001",
    )

    assert snapshot.confidence_band in ("low", "medium", "high")


def test_claim_type_is_noun_or_action() -> None:
    snapshot = DiagnosticEngine().diagnose(
        "I want better English ability.",
        trace_id="trace-claim-001",
    )

    assert snapshot.system_a_cues.possible_claim_type in ("noun_goal", "action_goal")
