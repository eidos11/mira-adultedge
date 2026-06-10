"""TDD for the report skill (②) render: mode routing + self-contained HTML.

- expert  → reuse mira.report.render_report_markdown (DRY, decision 3)
- html    → same renderer, then a dependency-free MD→HTML pass into an
            inline-CSS template (self-contained single file)
- customize → minimal guidance (decision 4)
- unsupported mode / bad schema → explicit error (fail-closed)
"""

from __future__ import annotations

import pytest
import render as render_mod

VALID = {
    "schema_version": "0.2.2",
    "input": "I failed the exam because I'm just not smart enough.",
    "report": "stub report",
    "route_vtype": "A",
    "patterns": [
        {
            "pattern_id": "willpower_blame",
            "lane2_status": "pass",
            "evidence_trace": ["[L3] cue"],
        }
    ],
    "psr": {"P": "low confidence", "S": "avoidance", "R": "give up"},
    "overlay_status": "verified",
    "lane1_pass": True,
}


@pytest.fixture(autouse=True)
def _stub_coaching(monkeypatch):
    monkeypatch.setattr(
        "mira.report.generate_coaching_block",
        lambda pattern_id, lang="en": "**reframing prompts** — try one small change.",
    )


def test_render_expert_returns_markdown():
    out = render_mod.render(VALID, mode="expert")
    assert "## Diagnosis Summary" in out
    assert "## Metadata" in out


def test_render_expert_includes_learner_input():
    out = render_mod.render(VALID, mode="expert")
    assert "I failed the exam" in out


def test_render_html_is_self_contained():
    out = render_mod.render(VALID, mode="html")
    assert out.strip().startswith("<!DOCTYPE html>")
    assert "<style>" in out
    assert "Diagnosis Summary" in out


def test_render_html_converts_headings_and_bold():
    out = render_mod.render(VALID, mode="html")
    assert "<h2>" in out
    assert "<strong>" in out


def test_render_html_escapes_learner_input():
    data = {**VALID, "input": "1 < 2 & 3 > 2"}
    out = render_mod.render(data, mode="html")
    assert "&lt;" in out and "&amp;" in out
    assert "<script" not in out


def test_render_customize_returns_guidance():
    out = render_mod.render(VALID, mode="customize")
    assert "template" in out.lower()


def test_render_unsupported_mode_raises():
    with pytest.raises(render_mod.UnsupportedModeError):
        render_mod.render(VALID, mode="pdf")


def test_render_propagates_schema_gate():
    from ingest import UnsupportedSchemaVersionError

    bad = {**VALID, "schema_version": "0.1.0"}
    with pytest.raises(UnsupportedSchemaVersionError):
        render_mod.render(bad, mode="expert")


def test_md_to_html_basic_elements():
    html = render_mod._md_to_html("## Title\n\n- item\n\n> quote\n\n---")
    assert "<h2>" in html
    assert "<li>item</li>" in html
    assert "<blockquote>" in html
    assert "<hr>" in html


# ---------------------------------------------------------------------------
# Task 6 — structured coaching field rendering (3 cases)
# ---------------------------------------------------------------------------

_COACHING_SUPPORTED = {
    "block": "Try reframing: focus on effort, not innate ability.",
    "pattern_id": "willpower_blame",
    "note": None,
}

_COACHING_OUT_OF_SCOPE = {
    "block": "Some coaching block text.",
    "pattern_id": "rare_pattern",
    "note": "out of v0.x scope: pattern 'rare_pattern' has no coaching template",
}

_COACHING_NO_MATCH = {
    "block": "No clear match found. Consider reviewing your learning strategy.",
    "pattern_id": None,
    "note": None,
}


def _with_coaching(coaching: dict) -> dict:
    """Return a valid diagnostic dict with the given structured coaching field."""
    return {**VALID, "coaching": coaching}


# The overlay-derived coaching text, produced by mira.report._action_suggestion
# via the stubbed generate_coaching_block (see _stub_coaching fixture). When a
# structured coaching field is supplied this text MUST be absent — it would only
# appear if the overlay path were (wrongly) rendered alongside the structured one.
_OVERLAY_COACHING_TEXT = "reframing prompts"


# --- Case 1: supported (pattern_id set, note=None) -------------------------

def test_html_coaching_supported_shows_block():
    """Supported coaching block appears in html output."""
    data = _with_coaching(_COACHING_SUPPORTED)
    out = render_mod.render(data, mode="html")
    assert "Try reframing" in out


def test_expert_coaching_supported_shows_block():
    """Supported coaching block appears in expert (md) output."""
    data = _with_coaching(_COACHING_SUPPORTED)
    out = render_mod.render(data, mode="expert")
    assert "Try reframing" in out


def test_expert_coaching_rendered_exactly_once():
    """Structured coaching is the SINGLE source — no double-render in expert.

    Exactly one '## Coaching' heading, and the overlay-derived _action_suggestion
    text is absent (it would appear only if both paths rendered).
    """
    data = _with_coaching(_COACHING_SUPPORTED)
    out = render_mod.render(data, mode="expert")
    assert out.count("## Coaching") == 1
    assert _OVERLAY_COACHING_TEXT not in out


def test_html_coaching_rendered_exactly_once():
    """Structured coaching is the SINGLE source — no double-render in html.

    Exactly one Coaching heading, and the overlay-derived _action_suggestion
    text is absent (it would appear only if both paths rendered).
    """
    data = _with_coaching(_COACHING_SUPPORTED)
    out = render_mod.render(data, mode="html")
    assert out.count("<h2>Coaching</h2>") == 1
    assert _OVERLAY_COACHING_TEXT not in out


# --- Case 2: out-of-scope (pattern_id set, note set) -----------------------

def test_html_coaching_out_of_scope_shows_note_honestly():
    """Out-of-scope note is shown honestly in html — not hidden, and emphasized."""
    data = _with_coaching(_COACHING_OUT_OF_SCOPE)
    out = render_mod.render(data, mode="html")
    assert "out of v0.x scope" in out
    # Structural emphasis (not just substring presence): the honesty intent
    # depends on the note being visually distinct, so guard the class hook.
    assert 'class="coaching-note"' in out


def test_expert_coaching_out_of_scope_shows_note_honestly():
    """Out-of-scope note is shown honestly in expert — not hidden."""
    data = _with_coaching(_COACHING_OUT_OF_SCOPE)
    out = render_mod.render(data, mode="expert")
    assert "out of v0.x scope" in out


# --- Case 3: no coaching field (absence graceful) --------------------------

def test_html_renders_fine_without_coaching_field():
    """html render does not crash when coaching field is absent."""
    assert "coaching" not in VALID  # sanity: VALID has no coaching field
    out = render_mod.render(VALID, mode="html")
    assert out.strip().startswith("<!DOCTYPE html>")
    assert "Diagnosis Summary" in out


def test_expert_renders_fine_without_coaching_field():
    """expert render does not crash when coaching field is absent."""
    assert "coaching" not in VALID  # sanity
    out = render_mod.render(VALID, mode="expert")
    assert "## Diagnosis Summary" in out


# --- Case 4 (bonus): no-match (pattern_id=None, note=None) -----------------

def test_html_coaching_no_match_shows_block():
    """No-match coaching block is rendered in html (not silently dropped)."""
    data = _with_coaching(_COACHING_NO_MATCH)
    out = render_mod.render(data, mode="html")
    assert "No clear match found" in out


def test_expert_coaching_no_match_shows_block():
    """No-match coaching block is rendered in expert."""
    data = _with_coaching(_COACHING_NO_MATCH)
    out = render_mod.render(data, mode="expert")
    assert "No clear match found" in out


# --- P1-a: structured coaching must not bypass the expert verdict gate ------

def test_expert_structured_coaching_obeys_verdict_gate():
    """P1-a (codex finding, S2-a verified): render_report_markdown's preserved
    verdict gate scans the OVERLAY-derived coaching, but _render_expert then
    REPLACES that block with the JSON-supplied structured block — which never
    passed the gate. A structured coaching block containing verdict language must
    therefore be caught here (safe-fallback), else the preserved gate is illusory
    for the skill output path.

    RED (pre-fix): the verdict block is spliced in and flows through unchecked.
    GREEN (post-fix): the structured block is gated -> safe_fallback_report.
    """
    from mira.report import safe_fallback_report

    data = _with_coaching(
        {
            "block": "The verdict is that you are wrong about this.",
            "pattern_id": "willpower_blame",
            "note": None,
        }
    )
    out = render_mod.render(data, mode="expert")
    assert out == safe_fallback_report("en")
