"""TDD: verdict_state — verdict 판정 SSOT (report.py).

html 렌더(②)와 expert md(①)가 동일한 verdict 판정을 공유하도록,
lane2_status / evidence_trace → 상태 문자열을 단일 함수로 추출한다.
"""

from __future__ import annotations

from mira.contracts.minimal import PatternCandidate


def _cand(lane2_status: str = "not_run", evidence_trace=None) -> PatternCandidate:
    return PatternCandidate(
        pattern_id="x",
        canonical_id="c",
        vtype="D",
        lane2_status=lane2_status,
        lane2_result=None,
        evidence_trace=evidence_trace or [],
    )


def test_verdict_state_pass_is_verified():
    from mira.report import verdict_state

    assert verdict_state(_cand(lane2_status="pass")) == "verified"


def test_verdict_state_fail_is_rejected():
    from mira.report import verdict_state

    assert verdict_state(_cand(lane2_status="fail")) == "rejected"


def test_verdict_state_evidence_only_is_assisted():
    from mira.report import verdict_state

    assert verdict_state(_cand(evidence_trace=["[L3] cue"])) == "evidence_assisted"


def test_verdict_state_default_is_unverified():
    from mira.report import verdict_state

    assert verdict_state(_cand()) == "unverified"


def test_lane2_badge_preserved_via_verdict_state():
    """리팩터 후에도 _lane2_badge 표시 문자열은 동작 보존."""
    from mira.report import _lane2_badge

    assert "verified" in _lane2_badge(_cand(lane2_status="pass"))
    assert "rejected" in _lane2_badge(_cand(lane2_status="fail"))
    assert "evidence-assisted" in _lane2_badge(_cand(evidence_trace=["x"]))
    assert "unverified" in _lane2_badge(_cand())
