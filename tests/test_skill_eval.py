"""End-to-end eval: real pipeline → skill render, no mocks (regression guard).

Covers the 3 Phase-1 modes against a genuine diagnostic so the Phase 0 json
contract (route_vtype + input) and the skill stay wired together. This is the
skill's ≥3-scenario trigger eval (decision: html / expert / customize).
"""

from __future__ import annotations

import pytest
import render as render_mod

from mira.__main__ import build_json_output
from mira.pipeline import run_minimal_loop

_CLAIM = "I keep failing my exams because I am just lazy and not smart enough"


@pytest.fixture(scope="module")
def real_diag() -> dict:
    result = run_minimal_loop(
        _CLAIM, claim_language="en", context_type="adult_learning"
    )
    return build_json_output(result.overlay, result.report, _CLAIM)


def test_real_json_has_022_contract(real_diag):
    assert real_diag["schema_version"] == "0.2.2"
    assert real_diag["route_vtype"] in ("D", "I", "A")
    assert real_diag["input"] == _CLAIM


def test_html_mode_self_contained_from_real_diag(real_diag):
    out = render_mod.render(real_diag, mode="html")
    assert out.strip().startswith("<!DOCTYPE html>")
    assert "</html>" in out


def test_expert_mode_markdown_from_real_diag(real_diag):
    out = render_mod.render(real_diag, mode="expert")
    # normal report starts with "## Input"; safe_fallback with "## Analysis Result"
    assert out.lstrip().startswith("##")


def test_customize_mode_from_real_diag(real_diag):
    out = render_mod.render(real_diag, mode="customize")
    assert "template" in out.lower()
