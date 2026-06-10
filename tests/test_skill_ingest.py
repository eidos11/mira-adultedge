"""TDD for the report skill (②) ingest: schema_version gate + overlay rebuild.

Decision 1 (fail-closed): an unsupported / missing schema_version raises an
explicit error with regeneration guidance — never a silent best-effort parse.
The rebuilt overlay must feed render_report_markdown so expert mode reuses the
① renderer (decision 3, DRY).
"""

from __future__ import annotations

import ingest as ingest_mod
import pytest

VALID = {
    "schema_version": "0.2.2",
    "report": "stub report",
    "route_vtype": "I",
    "patterns": [
        {
            "pattern_id": "willpower_blame",
            "lane2_status": "pass",
            "evidence_trace": ["[L3] cue"],
        }
    ],
    "psr": {"P": "p text", "S": "s text", "R": "r text"},
    "overlay_status": "verified",
    "lane1_pass": True,
}


def test_ingest_accepts_supported_schema():
    overlay = ingest_mod.ingest(VALID)
    assert overlay.route_vtype == "I"


def test_ingest_rejects_old_schema_021():
    data = {**VALID, "schema_version": "0.2.1"}
    with pytest.raises(ingest_mod.UnsupportedSchemaVersionError):
        ingest_mod.ingest(data)


def test_ingest_rejects_missing_schema():
    data = {k: v for k, v in VALID.items() if k != "schema_version"}
    with pytest.raises(ingest_mod.UnsupportedSchemaVersionError):
        ingest_mod.ingest(data)


def test_ingest_error_message_guides_regeneration():
    data = {**VALID, "schema_version": "0.1.0"}
    with pytest.raises(ingest_mod.UnsupportedSchemaVersionError, match=r"--format json"):
        ingest_mod.ingest(data)


def test_ingest_reconstructs_psr_and_patterns():
    overlay = ingest_mod.ingest(VALID)
    assert overlay.psr.P_appraisal == "p text"
    assert overlay.psr.S_strategy == "s text"
    assert overlay.psr.R_projection == "r text"
    assert len(overlay.pattern_candidates) == 1
    c = overlay.pattern_candidates[0]
    assert c.pattern_id == "willpower_blame"
    assert c.lane2_status == "pass"
    assert c.evidence_trace == ["[L3] cue"]


def test_ingest_accepts_object_without_coaching():
    """Existing objects without coaching field still pass (additive — backward compat)."""
    overlay = ingest_mod.ingest(VALID)
    assert overlay.route_vtype == "I"
    # coaching is NOT on the overlay (extra="forbid" would raise)
    assert not hasattr(overlay, "coaching")


_VALID_WITH_COACHING = {
    **VALID,
    "coaching": {
        "block": "Try reviewing your metacognitive assumptions.",
        "pattern_id": "willpower_blame",
        "note": None,
    },
}


def test_ingest_accepts_object_with_structured_coaching():
    """Object WITH a structured coaching dict at the top level passes ingest."""
    result = ingest_mod.ingest(_VALID_WITH_COACHING)
    assert result.route_vtype == "I"


def test_ingest_coaching_not_passed_to_overlay():
    """coaching field is NOT injected onto the CVVerificationOverlay (extra='forbid')."""
    result = ingest_mod.ingest(_VALID_WITH_COACHING)
    assert not hasattr(result, "coaching")


def test_ingest_and_ingest_coaching_are_separate_paths():
    """overlay and coaching are retrieved via two separate calls, not one tuple.

    ingest(data) returns the overlay (coaching stripped); ingest_coaching(data)
    returns the structured coaching dict. They round-trip the same input
    independently.
    """
    overlay = ingest_mod.ingest(_VALID_WITH_COACHING)
    assert not hasattr(overlay, "coaching")  # coaching never on the overlay
    coaching = ingest_mod.ingest_coaching(_VALID_WITH_COACHING)
    assert coaching is not None
    assert coaching["block"] == "Try reviewing your metacognitive assumptions."
    assert coaching["pattern_id"] == "willpower_blame"
    assert coaching["note"] is None


def test_ingest_coaching_absent_returns_none():
    """ingest_coaching returns None when coaching field is absent from input."""
    coaching = ingest_mod.ingest_coaching(VALID)
    assert coaching is None


def test_ingest_roundtrip_feeds_render_report_markdown(monkeypatch):
    """The rebuilt overlay must render through the ① renderer (expert DRY)."""
    monkeypatch.setattr(
        "mira.report.generate_coaching_block",
        lambda pattern_id, lang="en": "**reframing prompts** — try one small change.",
    )
    from mira.report import render_report_markdown

    overlay = ingest_mod.ingest(VALID)
    md = render_report_markdown(overlay, "learner claim", lang="en")
    assert "## Diagnosis Summary" in md
    assert "## PSR Decomposition" in md
    assert "## Metadata" in md
