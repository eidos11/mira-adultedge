"""TDD for --format report (expert Markdown renderer).

① ae-ui-output-design §①: 7-section expert report with lane2_status badges.
Principle: internal logic unchanged, output layer only.

Two test groups:
- Structure: 7 sections, badge mapping (✅/✗/🟡/○), source, PSR, Metadata.
- Safety invariants: Input (learner quote) exempt from verdict gate;
  coaching with verdict language still forces safe_fallback.
"""

from __future__ import annotations

import pytest

from mira.contracts.minimal import (
    CVVerificationOverlay,
    PatternCandidate,
    PSRResult,
)
from mira.report import (
    _action_suggestion,
    generate_report,
    render_report_markdown,
    safe_fallback_report,
)

_CLEAN_COACHING = "**reframing prompts** — Consider structural factors. Try one small change."


def _make_overlay(**kwargs) -> CVVerificationOverlay:
    defaults = dict(
        trace_id="t-report",
        request_id="req-t-report",
        psr=PSRResult(
            P_appraisal="medium metacognitive confidence",
            S_strategy="information seeking strategy",
            R_projection="concept stage",
        ),
        route_vtype="A",
        overlay_status="verified",
        lane1_pass=True,
        evidence_summary="test evidence summary",
    )
    defaults.update(kwargs)
    return CVVerificationOverlay(**defaults)


def _candidate(pid="willpower_blame", status="pass", trace=None, **kw) -> PatternCandidate:
    return PatternCandidate(
        pattern_id=pid,
        canonical_id=kw.get("canonical_id", "PAT-DUAL-01"),
        vtype=kw.get("vtype", "A"),
        lane2_status=status,
        evidence_trace=trace if trace is not None else [],
    )


@pytest.fixture(autouse=True)
def _stub_coaching(monkeypatch):
    """Isolate from YAML coaching content (per test_report_fix3 pattern).

    Accepts tentative kwarg (added in T3) so the new tentative path in
    _action_suggestion does not raise TypeError against the stub signature.
    """
    monkeypatch.setattr(
        "mira.report.generate_coaching_block",
        lambda pattern_id, lang="en", tentative=False: _CLEAN_COACHING,
    )


class TestReportFormatStructure:
    """7-section structure + badge/source mapping."""

    def test_all_seven_sections_present(self):
        overlay = _make_overlay(pattern_candidates=[_candidate(trace=["trait_attr"])])
        report = render_report_markdown(overlay, "my claim", lang="en")
        for h in [
            "## Input",
            "## Diagnosis Summary",
            "## PSR Decomposition",
            "## Evidence",
            "## Coaching",
            "## Confidence",
            "## Metadata",
        ]:
            assert h in report, f"missing section: {h}"

    def test_input_section_quotes_claim(self):
        overlay = _make_overlay(pattern_candidates=[_candidate(trace=["t1"])])
        report = render_report_markdown(overlay, "I keep failing at math", lang="en")
        assert "I keep failing at math" in report

    def test_badge_verified_for_pass(self):
        overlay = _make_overlay(pattern_candidates=[_candidate(status="pass", trace=["t1"])])
        report = render_report_markdown(overlay, "c", lang="en")
        assert "✅" in report

    def test_badge_rejected_for_fail(self):
        overlay = _make_overlay(
            overlay_status="structural_mismatch",
            pattern_candidates=[_candidate(status="fail", trace=["t1"])],
        )
        report = render_report_markdown(overlay, "c", lang="en")
        assert "✗" in report or "rejected" in report.lower()

    def test_badge_evidence_assisted_for_not_run_with_evidence(self):
        overlay = _make_overlay(
            overlay_status="insufficient_evidence",
            pattern_candidates=[_candidate(status="not_run", trace=["[L3] cue"])],
        )
        report = render_report_markdown(overlay, "c", lang="en")
        assert "🟡" in report

    def test_badge_unverified_for_not_run_no_evidence(self):
        overlay = _make_overlay(
            overlay_status="insufficient_evidence",
            pattern_candidates=[_candidate(status="not_run", trace=[])],
        )
        report = render_report_markdown(overlay, "c", lang="en")
        assert "○" in report

    def test_source_lane3_for_l3_trace(self):
        # lane3_detected=True is the explicit field (replaces [L3] string parsing)
        c = PatternCandidate(
            pattern_id="willpower_blame",
            canonical_id="PAT-DUAL-01",
            vtype="A",
            lane2_status="not_run",
            evidence_trace=["[L3] cue"],
            lane3_detected=True,
        )
        overlay = _make_overlay(
            overlay_status="insufficient_evidence",
            pattern_candidates=[c],
        )
        report = render_report_markdown(overlay, "c", lang="en")
        assert "Lane 3" in report

    def test_source_lane2_for_pass(self):
        overlay = _make_overlay(pattern_candidates=[_candidate(status="pass", trace=["t1"])])
        report = render_report_markdown(overlay, "c", lang="en")
        assert "Lane 2" in report

    def test_psr_section_has_components(self):
        overlay = _make_overlay(pattern_candidates=[_candidate(trace=["t1"])])
        report = render_report_markdown(overlay, "c", lang="en")
        assert "medium metacognitive confidence" in report
        assert "information seeking strategy" in report
        assert "concept stage" in report

    def test_evidence_per_pattern_trace(self):
        overlay = _make_overlay(
            pattern_candidates=[_candidate(pid="false_dilemma", status="pass", trace=["binary_framing"])]
        )
        report = render_report_markdown(overlay, "c", lang="en")
        assert "binary_framing" in report

    def test_metadata_has_schema_version(self):
        overlay = _make_overlay(pattern_candidates=[_candidate(trace=["t1"])])
        report = render_report_markdown(overlay, "c", lang="en")
        assert "schema_version" in report or "0.2" in report

    def test_metadata_lanes_when_provided(self):
        overlay = _make_overlay(pattern_candidates=[_candidate(trace=["t1"])])
        report = render_report_markdown(
            overlay, "c", lang="en",
            lanes={"lane1": True, "lane2": False, "lane3": False},
        )
        assert "lane" in report.lower()

    def test_empty_candidates_still_renders(self):
        overlay = _make_overlay(overlay_status="insufficient_evidence", pattern_candidates=[])
        report = render_report_markdown(overlay, "claim", lang="en")
        assert "## Diagnosis Summary" in report
        assert "## Metadata" in report

    @pytest.mark.parametrize("lang", ["en", "ko"])
    def test_both_langs_render(self, lang):
        overlay = _make_overlay(pattern_candidates=[_candidate(trace=["t1"])])
        report = render_report_markdown(overlay, "claim", lang=lang)
        assert "## Metadata" in report or "## 메타데이터" in report


class TestReportFormatSafety:
    """Safety-gate invariants preserved from generate_report."""

    def test_verdict_in_input_does_not_force_fallback(self):
        """Input is a learner quote → verdict language must NOT trip the gate."""
        overlay = _make_overlay(pattern_candidates=[_candidate(trace=["t1"])])
        report = render_report_markdown(
            overlay, "you are biased and wrong about everything", lang="en"
        )
        assert report != safe_fallback_report("en")
        assert "## Metadata" in report

    def test_verdict_in_coaching_forces_fallback(self, monkeypatch):
        """Coaching with verdict language → safe_fallback (gate preserved)."""
        monkeypatch.setattr(
            "mira.report.generate_coaching_block",
            lambda pattern_id, lang="en": "**advice** — You are diagnosed with severe bias. The verdict is clear.",
        )
        overlay = _make_overlay(pattern_candidates=[_candidate(status="pass", trace=["t1"])])
        report = render_report_markdown(overlay, "neutral claim", lang="en")
        assert report == safe_fallback_report("en")

    def test_willpower_blame_in_system_text_forces_fallback(self):
        """System-generated narrative with real blame → fallback."""
        overlay = _make_overlay(
            psr=PSRResult(
                P_appraisal="learner shows lack of willpower and is lazy",
                S_strategy="s",
                R_projection="r",
            ),
            pattern_candidates=[_candidate(trace=["t1"])],
        )
        report = render_report_markdown(overlay, "neutral", lang="en")
        assert report == safe_fallback_report("en")


# ── Task 4: _action_suggestion verification-state branching (CX-2/4/5, spec D1/D3) ──


def _base_overlay(**kwargs) -> CVVerificationOverlay:
    """Minimal overlay for _action_suggestion unit tests."""
    defaults = dict(
        trace_id="t-as",
        request_id="req-as",
        psr=PSRResult(
            P_appraisal="p",
            S_strategy="s",
            R_projection="r",
        ),
        route_vtype="A",
        overlay_status="verified",
        lane1_pass=True,
        evidence_summary="test",
    )
    defaults.update(kwargs)
    return CVVerificationOverlay(**defaults)


def _make_candidate(pid: str, status: str, trace: list[str] | None = None) -> PatternCandidate:
    return PatternCandidate(
        pattern_id=pid,
        canonical_id="PAT-TEST-01",
        vtype="A",
        lane2_status=status,
        evidence_trace=trace if trace is not None else [],
    )


def _overlay_with_unverified(pids: list[str]) -> CVVerificationOverlay:
    """Overlay with all candidates as unverified (no evidence)."""
    return _base_overlay(
        pattern_candidates=[_make_candidate(pid, "unverified", []) for pid in pids]
    )


def _overlay_with_verified(pids: list[str]) -> CVVerificationOverlay:
    """Overlay with all candidates as verified (lane2_status=pass)."""
    return _base_overlay(
        pattern_candidates=[_make_candidate(pid, "pass", ["confirmed_evidence"]) for pid in pids]
    )


def _overlay_with_rejected(pids: list[str]) -> CVVerificationOverlay:
    """Overlay with all candidates as rejected (lane2_status=fail)."""
    return _base_overlay(
        overlay_status="structural_mismatch",
        pattern_candidates=[_make_candidate(pid, "fail", ["rejected_evidence"]) for pid in pids],
    )


def _overlay_mixed(evidenced: list[str], unverified: list[str]) -> CVVerificationOverlay:
    """Overlay mixing evidenced (unverified + evidence) and plain unverified candidates."""
    cands = (
        [_make_candidate(pid, "unverified", ["some_trace"]) for pid in evidenced]
        + [_make_candidate(pid, "unverified", []) for pid in unverified]
    )
    return _base_overlay(overlay_status="insufficient_evidence", pattern_candidates=cands)


def _tentative_stub(pattern_id, lang="en", tentative=False):
    """Stub that echoes pattern_id and includes 'may' when tentative=True."""
    if tentative:
        return f"This *may* apply — **{pattern_id.replace('_', ' ')}**: check this pattern."
    return f"**{pattern_id.replace('_', ' ')}**: coaching block here."


def test_action_suggestion_unverified_is_tentative_and_capped(monkeypatch):
    """Unverified patterns get tentative framing (contains 'may') and are capped at 3."""
    monkeypatch.setattr("mira.report.generate_coaching_block", _tentative_stub)
    # 4 patterns — only 3 should appear
    overlay = _overlay_with_unverified(
        ["oversimplified_cause", "false_dilemma", "sunk_cost", "fluency_illusion"]
    )
    block = _action_suggestion(overlay, "en")
    assert "may" in block.lower() or "혹시" in block  # tentative framing
    count = sum(
        block.count(f"**{p.replace('_', ' ')}**")
        for p in ["oversimplified_cause", "false_dilemma", "sunk_cost", "fluency_illusion"]
    )
    assert count <= 3  # cap 3


def test_action_suggestion_evidenced_and_unverified_share_cap(monkeypatch):
    """CX-2: evidenced + unverified share a single cap of 3 total."""
    monkeypatch.setattr("mira.report.generate_coaching_block", _tentative_stub)
    overlay = _overlay_mixed(evidenced=["false_dilemma", "sunk_cost"], unverified=["oversimplified_cause", "fluency_illusion"])
    block = _action_suggestion(overlay, "en")
    count = sum(
        block.count(f"**{p.replace('_', ' ')}**")
        for p in ["false_dilemma", "sunk_cost", "oversimplified_cause", "fluency_illusion"]
    )
    assert count <= 3


def test_action_suggestion_rejected_is_silent(monkeypatch):
    """CX-4: rejected (lane2_status=fail) patterns produce NO coaching output."""
    monkeypatch.setattr("mira.report.generate_coaching_block", _tentative_stub)
    overlay = _overlay_with_rejected(["false_dilemma"])
    block = _action_suggestion(overlay, "en")
    assert "false dilemma" not in block.lower()  # rejected pattern absent
    # strong CX-4 check: rejected candidates contribute NOTHING — identical to a
    # candidate-free overlay of the same status (verifies the old coach_reject text is
    # gone, not merely that the pattern name is absent).
    empty = _action_suggestion(
        _base_overlay(overlay_status="structural_mismatch", pattern_candidates=[]), "en"
    )
    assert block == empty


def test_action_suggestion_cap_is_deterministic(monkeypatch):
    """CX-5: output is deterministic regardless of input list order."""
    monkeypatch.setattr("mira.report.generate_coaching_block", _tentative_stub)
    pids_forward = ["false_dilemma", "sunk_cost", "oversimplified_cause", "fluency_illusion"]
    pids_reverse = list(reversed(pids_forward))
    a = _action_suggestion(_overlay_with_unverified(pids_forward), "en")
    b = _action_suggestion(_overlay_with_unverified(pids_reverse), "en")
    assert a == b


def test_action_suggestion_verified_is_assertive(monkeypatch):
    """Verified (pass) patterns get assertive framing — no 'may' hedge."""
    monkeypatch.setattr("mira.report.generate_coaching_block", _tentative_stub)
    overlay = _overlay_with_verified(["false_dilemma"])
    block = _action_suggestion(overlay, "en")
    # tentative stub only adds "may" when tentative=True; verified path uses tentative=False
    assert "may" not in block.lower()


# ── Task 5: generate_report coaching-level verdict gate removed (CX-3, spec D1) ──


def test_generate_report_no_coaching_verdict_gate(monkeypatch):
    """spec D1/CX-3: generate_report no longer safe-fallbacks merely because the coaching
    block contains verdict-ish language. The coaching-level gate was redundant; the real
    guards (system_text willpower block via _check_report_violations, and the Lane-1
    no-verdict invariant check#7 in coach_from_overlay) are preserved elsewhere.

    RED on old code: 'diagnosed' matches VERDICT_LANGUAGE_RE -> old gate returned the safe
    fallback, so 'diagnosed' was absent. GREEN now: the coaching flows through."""
    monkeypatch.setattr(
        "mira.report.generate_coaching_block",
        lambda pattern_id, lang="en", tentative=False: "This pattern was diagnosed — consider structural factors.",
    )
    overlay = _overlay_with_unverified(["false_dilemma"])
    report = generate_report(overlay, "I must pick A or B", lang="en")
    assert report != safe_fallback_report("en")  # gate removed: no fallback
    assert "diagnosed" in report                  # verdict-ish coaching now flows through


# ── P1-b: cap must bound EMITTED coaching, not candidates scanned ──────────────


def test_action_suggestion_cap_does_not_starve_on_missing_templates(monkeypatch):
    """P1-b (codex finding, S2-a verified): tentative candidates are capped at 3
    BEFORE template availability is known. If the 3 evidence-richest candidates
    lack coaching templates and a 4th has one, slicing [:3] drops all coaching —
    zero tentative output despite an available template (spec §4 '1-3 candidate').

    The cap must bound EMITTED blocks (3), scanning past template-missing
    candidates rather than letting them consume cap slots.

    RED (pre-fix): false_dilemma (4th) is never tried -> absent.
    GREEN (post-fix): false_dilemma coaching appears.
    """
    def _stub(pid, lang="en", tentative=False):
        if pid.startswith("notempl"):
            return None  # template missing -> generate_coaching_block returns None
        return f"This *may* apply — **{pid.replace('_', ' ')}**: structural check."

    monkeypatch.setattr("mira.report.generate_coaching_block", _stub)
    # 3 template-missing candidates with rich evidence sort first; one real-template
    # candidate with thinner evidence sorts 4th and is starved by the pre-cap slice.
    overlay = _base_overlay(
        overlay_status="insufficient_evidence",
        pattern_candidates=[
            _make_candidate("notempl_a", "unverified", ["e1", "e2", "e3"]),
            _make_candidate("notempl_b", "unverified", ["e1", "e2", "e3"]),
            _make_candidate("notempl_c", "unverified", ["e1", "e2", "e3"]),
            _make_candidate("false_dilemma", "unverified", ["e1"]),
        ],
    )
    block = _action_suggestion(overlay, "en")
    assert "false dilemma" in block.lower()
