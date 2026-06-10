"""TDD: html 렌더 시각화 (② skill) — overlay 직접 렌더의 매체 강점.

evidence→Input 하이라이트 / verdict 색상 배지 / 신뢰도 게이지 / 레인 뱃지.
md 미러가 아니라 html이어야 하는 이유를 테스트로 고정한다.
"""

from __future__ import annotations

import pytest
import render as render_mod

HTML_RICH = {
    "schema_version": "0.2.2",
    "input": "I must either pass this exam or give up entirely; there is no middle ground.",
    "report": "stub",
    "route_vtype": "D",
    "patterns": [
        {
            "pattern_id": "false_dilemma",
            "lane2_status": "pass",
            "evidence_trace": [
                "[L3] either pass this exam or give up entirely",
                "[L3] no middle ground",
            ],
        },
        {
            "pattern_id": "genetic_fallacy",
            "lane2_status": "not_run",
            "evidence_trace": [],
        },
    ],
    "psr": {"P": "p", "S": "s", "R": "r"},
    "overlay_status": "verified",
    "lane1_pass": True,
}


@pytest.fixture(autouse=True)
def _stub_coaching(monkeypatch):
    monkeypatch.setattr(
        "mira.report.generate_coaching_block",
        lambda pattern_id, lang="en": "**reframing** — try one small change.",
    )


def test_html_highlights_evidence_in_input():
    """evidence 인용이 Input 원문에 <mark>로 하이라이트된다 (md 불가)."""
    out = render_mod.render(HTML_RICH, mode="html")
    assert "<mark" in out
    assert "no middle ground" in out


def test_html_verdict_badge_carries_state_class():
    """verdict 상태가 CSS class로 인코딩된다 (verified/unverified 구분)."""
    out = render_mod.render(HTML_RICH, mode="html")
    assert "verdict-verified" in out
    assert "verdict-unverified" in out


def test_html_confidence_gauge_present():
    """신뢰도가 게이지 요소로 시각화된다."""
    out = render_mod.render(HTML_RICH, mode="html")
    assert "gauge" in out


def test_html_lane_shown_as_badge():
    """검증 레인이 뱃지로 표시된다."""
    out = render_mod.render(HTML_RICH, mode="html")
    assert "lane-badge" in out


def test_html_still_self_contained():
    """재작성 후에도 자체완결·의존성 0 유지 (회귀 방지)."""
    out = render_mod.render(HTML_RICH, mode="html")
    assert out.strip().startswith("<!DOCTYPE html>")
    assert "<style>" in out
    assert "http" not in out
    assert "<script" not in out


def test_html_escapes_learner_input():
    """하이라이트 중에도 HTML 이스케이프 유지 (회귀 방지)."""
    data = {**HTML_RICH, "input": "1 < 2 & 3 > 2 with no middle ground"}
    out = render_mod.render(data, mode="html")
    assert "&lt;" in out and "&amp;" in out
    assert "<script" not in out
