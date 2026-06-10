"""Engine seam tests: diagnose_only / coach_from_overlay.

Seam rationale: stages 1-3 produce the overlay (diagnosis); stage 4 produces
the coaching text. Splitting them lets Skills ② and ③ call either half without
running the full pipeline.

Test plan:
  (a) diagnose_only returns an object with overlay/patterns present and NO
      structured coaching key.
  (b) coach_from_overlay(diagnose_only(...)) fills a structured coaching key
      at the top-level dict (outside the forbid-extra overlay).
  (c) run_minimal_loop still returns the same PipelineResult contract — no
      regression on any field callers depend on.
"""

from __future__ import annotations

import pytest

from mira.pipeline import PipelineResult, diagnose_only, coach_from_overlay, run_minimal_loop

# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

_CLAIM_EN = "I failed because I'm not smart enough."
_CLAIM_KO = "시험에 떨어진 것은 내가 머리가 나빠서다."


# ---------------------------------------------------------------------------
# (a) diagnose_only — diagnosis/overlay present; NO coaching
# ---------------------------------------------------------------------------

class TestDiagnoseOnly:
    def test_returns_something(self):
        result = diagnose_only(_CLAIM_EN, lang="en")
        assert result is not None

    def test_overlay_present(self):
        result = diagnose_only(_CLAIM_EN, lang="en")
        # The overlay must be accessible; attribute name "overlay" matches PipelineResult
        assert result.overlay is not None

    def test_patterns_present(self):
        """pattern_candidates list exists (may be empty, but key must be there)."""
        result = diagnose_only(_CLAIM_EN, lang="en")
        assert hasattr(result.overlay, "pattern_candidates")

    def test_no_coaching_key(self):
        """diagnose_only result must NOT carry a structured 'coaching' key."""
        result = diagnose_only(_CLAIM_EN, lang="en")
        # coaching must not be on the overlay (forbid-extra would raise anyway)
        assert not hasattr(result.overlay, "coaching")
        # coaching must not be on the top-level result object
        assert not hasattr(result, "coaching")

    def test_report_not_populated(self):
        """The pre-coaching object should carry no report attribute at all."""
        result = diagnose_only(_CLAIM_EN, lang="en")
        # DiagnoseResult is the stages 1-3 shape: no report field exists.
        assert not hasattr(result, "report")

    def test_snapshot_present(self):
        result = diagnose_only(_CLAIM_EN, lang="en")
        assert result.diagnostic_snapshot is not None

    def test_request_has_trace_id(self):
        result = diagnose_only(_CLAIM_EN, lang="en")
        assert result.request.trace_id

    def test_lang_kwarg_accepted(self):
        # Should not raise — lang kwarg must be forwarded
        result = diagnose_only(_CLAIM_KO, lang="ko")
        assert result.overlay is not None

    def test_returns_new_object_each_call(self):
        """Immutability check: two calls return distinct objects."""
        r1 = diagnose_only(_CLAIM_EN, lang="en")
        r2 = diagnose_only(_CLAIM_EN, lang="en")
        assert r1 is not r2


# ---------------------------------------------------------------------------
# (b) coach_from_overlay — coaching filled after second step
# ---------------------------------------------------------------------------

class TestCoachFromOverlay:
    def test_returns_dict_with_coaching(self):
        diag = diagnose_only(_CLAIM_EN, lang="en")
        coached = coach_from_overlay(diag)
        assert isinstance(coached, dict)
        assert "coaching" in coached

    def test_coaching_is_structured_dict(self):
        """coaching must be a dict with block/pattern_id/note keys (Task 2 schema)."""
        diag = diagnose_only(_CLAIM_EN, lang="en")
        coached = coach_from_overlay(diag)
        c = coached["coaching"]
        assert isinstance(c, dict), f"Expected dict, got {type(c)}"
        assert "block" in c, "coaching must have 'block' key"
        assert "pattern_id" in c, "coaching must have 'pattern_id' key"
        assert "note" in c, "coaching must have 'note' key"

    def test_coaching_block_is_non_empty_string(self):
        """coaching['block'] must be a non-empty string."""
        diag = diagnose_only(_CLAIM_EN, lang="en")
        coached = coach_from_overlay(diag)
        assert isinstance(coached["coaching"]["block"], str)
        assert coached["coaching"]["block"].strip() != ""

    def test_coaching_pattern_id_is_str_or_none(self):
        """coaching['pattern_id'] must be str or None."""
        diag = diagnose_only(_CLAIM_EN, lang="en")
        coached = coach_from_overlay(diag)
        pid = coached["coaching"]["pattern_id"]
        assert pid is None or isinstance(pid, str)

    def test_coaching_note_is_none(self):
        """coaching['note'] must be None at this stage (Task 5 fills it)."""
        diag = diagnose_only(_CLAIM_EN, lang="en")
        coached = coach_from_overlay(diag)
        assert coached["coaching"]["note"] is None

    def test_coaching_key_not_on_overlay(self):
        """coaching lives at dict level, NOT injected onto the overlay."""
        diag = diagnose_only(_CLAIM_EN, lang="en")
        coached = coach_from_overlay(diag)
        assert not hasattr(coached.get("overlay", diag.overlay), "coaching")

    def test_coached_dict_carries_overlay(self):
        """Coached dict contains a CVVerificationOverlay with matching trace_id.

        coach_from_overlay always calls model_copy (immutability — new object),
        so we check value equality on the stable fields rather than identity.
        """
        diag = diagnose_only(_CLAIM_EN, lang="en")
        coached = coach_from_overlay(diag)
        assert "overlay" in coached
        # model_copy returns a new object — identity check would always fail.
        assert coached["overlay"].trace_id == diag.overlay.trace_id
        assert coached["overlay"].route_vtype == diag.overlay.route_vtype
        assert coached["overlay"].pattern_candidates == diag.overlay.pattern_candidates

    def test_coached_dict_carries_report(self):
        """The full report string should be populated after coach_from_overlay."""
        diag = diagnose_only(_CLAIM_EN, lang="en")
        coached = coach_from_overlay(diag)
        assert "report" in coached
        assert coached["report"] and coached["report"].strip() != ""

    def test_coached_report_has_diagnostic_summary(self):
        diag = diagnose_only(_CLAIM_EN, lang="en")
        coached = coach_from_overlay(diag)
        assert "Diagnostic Summary" in coached["report"]

    def test_input_not_mutated(self):
        """Immutability: diagnose_only result must be unchanged after coach_from_overlay."""
        diag = diagnose_only(_CLAIM_EN, lang="en")
        original_overlay_id = id(diag.overlay)
        coach_from_overlay(diag)
        # overlay object identity must be preserved
        assert id(diag.overlay) == original_overlay_id

    def test_ko_language_coaching(self):
        diag = diagnose_only(_CLAIM_KO, lang="ko")
        coached = coach_from_overlay(diag, lang="ko")
        assert "coaching" in coached
        c = coached["coaching"]
        assert isinstance(c, dict)
        assert c["block"].strip() != ""


# ---------------------------------------------------------------------------
# (c) run_minimal_loop regression — same contract as before
# ---------------------------------------------------------------------------

class TestRunMinimalLoopRegression:
    def test_returns_pipeline_result(self):
        result = run_minimal_loop(_CLAIM_EN, claim_language="en")
        assert isinstance(result, PipelineResult)

    def test_result_has_all_four_fields(self):
        result = run_minimal_loop(_CLAIM_EN, claim_language="en")
        assert result.request is not None
        assert result.overlay is not None
        assert isinstance(result.report, str)
        # diagnostic_snapshot may be None only for empty claims; valid input must have it
        assert result.diagnostic_snapshot is not None

    def test_report_has_coaching_block(self):
        """Coaching content must still appear in the full report string."""
        result = run_minimal_loop(_CLAIM_EN, claim_language="en")
        assert "Coaching" in result.report

    def test_report_has_diagnostic_summary(self):
        result = run_minimal_loop(_CLAIM_EN, claim_language="en")
        assert "Diagnostic Summary" in result.report

    def test_overlay_avoids_willpower_blame(self):
        result = run_minimal_loop(_CLAIM_EN, claim_language="en")
        assert result.overlay.avoid_willpower_blame is True

    def test_trace_id_consistent(self):
        result = run_minimal_loop(_CLAIM_EN, claim_language="en", trace_id="seam-001")
        assert result.request.trace_id == "seam-001"
        assert result.overlay.trace_id == "seam-001"

    def test_compose_equivalence(self):
        """run_minimal_loop result must be equivalent to diagnose_only + coach_from_overlay."""
        claim = _CLAIM_EN
        full = run_minimal_loop(claim, claim_language="en", trace_id="eq-001")
        diag = diagnose_only(claim, lang="en", trace_id="eq-001")
        coached = coach_from_overlay(diag, lang="en")
        # Both paths must produce a non-empty report
        assert full.report.strip() != ""
        assert coached["report"].strip() != ""
        # Overlay contracts must match (pattern count, status, lane1_pass)
        assert full.overlay.overlay_status == coached["overlay"].overlay_status
        assert full.overlay.lane1_pass == coached["overlay"].lane1_pass
        assert len(full.overlay.pattern_candidates) == len(coached["overlay"].pattern_candidates)
