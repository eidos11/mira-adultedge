"""TDD for `--format json` output structure.

schema 0.2.2: adds top-level `route_vtype` so the report skill (②) can
reconstruct the overlay and reuse `render_report_markdown` for the expert
mode (DRY, design decision 3). The json builder is extracted from `main()`
into `build_json_output(overlay, report)` to keep it unit-testable without
running the full pipeline.
"""

from __future__ import annotations

from mira.__main__ import build_json_output
from mira.contracts.minimal import (
    CVVerificationOverlay,
    PatternCandidate,
    PSRResult,
)


def _overlay(**kw) -> CVVerificationOverlay:
    defaults = dict(
        trace_id="t-json",
        request_id="req-json",
        psr=PSRResult(P_appraisal="P text", S_strategy="S text", R_projection="R text"),
        route_vtype="D",
        overlay_status="verified",
        lane1_pass=True,
        evidence_summary="ev summary",
    )
    defaults.update(kw)
    return CVVerificationOverlay(**defaults)


def test_json_output_includes_route_vtype():
    out = build_json_output(_overlay(route_vtype="I"), "report text")
    assert out["route_vtype"] == "I"


def test_json_output_includes_learner_input():
    out = build_json_output(_overlay(), "report text", learner_input="the learner text")
    assert out["input"] == "the learner text"


def test_json_output_schema_version_is_022():
    out = build_json_output(_overlay(), "report text")
    assert out["schema_version"] == "0.2.2"


def test_json_output_preserves_report_psr_status():
    out = build_json_output(_overlay(), "the report")
    assert out["report"] == "the report"
    assert out["psr"] == {"P": "P text", "S": "S text", "R": "R text"}
    assert out["overlay_status"] == "verified"
    assert out["lane1_pass"] is True


def test_json_output_serializes_patterns_without_lane2_result():
    cand = PatternCandidate(
        pattern_id="willpower_blame",
        canonical_id="PAT-DUAL-01",
        vtype="A",
        lane2_status="pass",
        evidence_trace=["[L3] cue"],
    )
    out = build_json_output(_overlay(pattern_candidates=[cand]), "r")
    assert out["patterns"] == [
        {
            "pattern_id": "willpower_blame",
            "lane2_status": "pass",
            "evidence_trace": ["[L3] cue"],
            "lane3_detected": False,
        }
    ]


def test_json_output_includes_lane2_result_when_present():
    cand = PatternCandidate(
        pattern_id="false_dilemma",
        canonical_id="PAT-LOGIC-02",
        vtype="D",
        lane2_status="pass",
        lane2_result={"verdict": "true"},
        evidence_trace=[],
    )
    out = build_json_output(_overlay(pattern_candidates=[cand]), "r")
    assert out["patterns"][0]["lane2_result"] == {"verdict": "true"}
