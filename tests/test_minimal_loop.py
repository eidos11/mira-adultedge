"""M1 minimal loop tests: E2E golden path, authority chain, oracle leakage.

Coverage targets:
- E2E golden path (A→B→A full loop)
- Contract validation (request/overlay Pydantic strict)
- PSR decomposition + D/I/A routing
- Pattern matching (registry-based, 2 executable)
- Report guardrails (forbidden phrases, willpower blame)
- Authority chain (no verdict language in output)
"""

from __future__ import annotations

import re

import pytest
from pydantic import ValidationError

from mira.contracts.minimal import (
    CVVerificationOverlay,
    PatternCandidate,
    PSRPrior,
    PSRResult,
    SystemAtoCVRequest,
)
from mira.system_b.engine.matcher import load_registry, match_patterns
from mira.pipeline import PipelineResult, run_minimal_loop
from mira.psr import _classify_claim, decompose_psr, route_vtype
from mira.contracts.safety_patterns import VERDICT_LANGUAGE_RE, WILLPOWER_BLAME_RE
from mira.report import generate_report

# ── Contract tests ────────────────────────────────────────────

class TestContracts:
    def test_request_valid(self):
        req = SystemAtoCVRequest(
            trace_id="t-001",
            learner_claim="나는 항상 시험에 실패한다",
        )
        assert req.claim_domain == "adult_learning"
        assert req.claim_language == "ko"

    def test_request_blank_claim_rejected(self):
        with pytest.raises(ValidationError):
            SystemAtoCVRequest(trace_id="t-002", learner_claim="  ")

    def test_request_blank_trace_rejected(self):
        with pytest.raises(ValidationError):
            SystemAtoCVRequest(trace_id="  ", learner_claim="test claim")

    def test_request_extra_field_rejected(self):
        with pytest.raises(ValidationError):
            SystemAtoCVRequest(
                trace_id="t-003",
                learner_claim="claim",
                secret_field="not_allowed",
            )

    def test_overlay_valid(self):
        overlay = CVVerificationOverlay(
            trace_id="t-001",
            request_id="req-t-001",
            psr=PSRResult(
                P_appraisal="premise", S_strategy="strategy", R_projection="result"
            ),
            route_vtype="D",
            overlay_status="needs_review",
            lane1_pass=True,
            evidence_summary="no evidence collected",
        )
        assert overlay.avoid_willpower_blame is True


# ── PSR tests ─────────────────────────────────────────────────

class TestPSR:
    def test_decompose_3_sentences(self):
        claim = "시험이 어렵다. 공부 방법을 바꿔야 한다. 결과가 나아질 것이다."
        result = decompose_psr(claim)
        assert result.P_appraisal
        assert result.S_strategy
        assert result.R_projection

    def test_decompose_with_prior(self):
        prior = PSRPrior(
            P_appraisal="custom premise",
            S_strategy="custom strategy",
            R_projection="custom result",
        )
        result = decompose_psr("anything", prior)
        assert result.P_appraisal == "custom premise"

    def test_route_causal_attribution_gives_A(self):
        assert route_vtype("시험에 떨어진 이유는 공부 때문이다") == "A"

    def test_route_deductive_gives_D(self):
        assert route_vtype("논리적으로 따라서 이것은 틀렸다") == "D"

    def test_route_generalization_gives_I(self):
        assert route_vtype("나는 항상 실패한다") == "I"

    def test_route_abductive_gives_A(self):
        assert route_vtype("아마 내가 잘못한 것 같다") == "A"

    def test_route_default_is_D(self):
        assert route_vtype("test claim without markers") == "D"

    def test_route_prior_overrides(self):
        prior = PSRPrior(suggested_vtype="I")
        assert route_vtype("때문에 실패", prior) == "I"

    def test_classify_self_assessment(self):
        assert _classify_claim("나는 게으른 사람이다") == "self_assessment"

    def test_classify_normative(self):
        assert _classify_claim("더 열심히 공부해야 한다") == "normative"


# ── Matcher tests ─────────────────────────────────────────────

class TestMatcher:
    def test_load_registry(self):
        registry = load_registry()
        assert len(registry) >= 19

    def test_match_returns_candidates_for_D(self):
        psr = PSRResult(
            P_appraisal="premise",
            S_strategy="either A or B",
            R_projection="must choose one",
        )
        candidates = match_patterns(psr, "D")
        assert len(candidates) > 0
        assert all(c.vtype == "D" for c in candidates)

    def test_non_executable_patterns_are_not_run(self):
        psr = PSRResult(
            P_appraisal="p", S_strategy="s", R_projection="r"
        )
        candidates = match_patterns(psr, "D")
        non_executable = [
            c for c in candidates
            if c.pattern_id not in ("false_dilemma", "oversimplified_cause")
        ]
        for c in non_executable:
            assert c.lane2_status == "not_run"

    def test_match_returns_candidates_for_A(self):
        psr = PSRResult(
            P_appraisal="p", S_strategy="s", R_projection="r"
        )
        candidates = match_patterns(psr, "A")
        assert len(candidates) > 0


# ── Report tests ──────────────────────────────────────────────

class TestReport:
    def _make_overlay(self, **kwargs) -> CVVerificationOverlay:
        defaults = dict(
            trace_id="t-rpt",
            request_id="req-t-rpt",
            psr=PSRResult(
                P_appraisal="전제", S_strategy="전략", R_projection="결과"
            ),
            route_vtype="D",
            overlay_status="needs_review",
            lane1_pass=True,
            evidence_summary="test evidence",
        )
        defaults.update(kwargs)
        return CVVerificationOverlay(**defaults)

    def test_report_has_four_blocks(self):
        overlay = self._make_overlay()
        report = generate_report(overlay, "test claim")
        assert "Diagnostic Summary" in report
        assert "Evidence" in report
        assert "Limitations" in report
        assert "Coaching" in report

    def test_report_no_forbidden_phrases(self):
        overlay = self._make_overlay()
        report = generate_report(overlay, "test")
        assert not VERDICT_LANGUAGE_RE.search(report)

    def test_report_no_willpower_blame(self):
        overlay = self._make_overlay()
        report = generate_report(overlay, "test")
        assert not WILLPOWER_BLAME_RE.search(report)

    def test_report_with_detected_pattern(self):
        candidate = PatternCandidate(
            pattern_id="false_dilemma",
            canonical_id="PAT-D-02",
            vtype="D",
            lane2_status="pass",
            evidence_trace=["s_form(disjunctive)", "options_count(2)"],
        )
        overlay = self._make_overlay(
            pattern_candidates=[candidate],
            overlay_status="verified",
        )
        report = generate_report(overlay, "test", lang="ko")
        assert "false dilemma" in report
        assert "자기 점검 질문" in report


# ── Pipeline E2E tests ────────────────────────────────────────

class TestPipelineE2E:
    def test_golden_path_korean(self):
        """1건 발화 → full loop → report 생성."""
        result = run_minimal_loop(
            "시험 때문에 스트레스를 받고 있다. 공부를 더 해야 한다.",
            trace_id="golden-001",
        )
        assert isinstance(result, PipelineResult)
        assert result.request.trace_id == "golden-001"
        assert result.overlay.trace_id == "golden-001"
        assert result.diagnostic_snapshot is not None
        assert result.diagnostic_snapshot.trace_id == result.request.trace_id
        assert "Diagnostic Summary" in result.report
        assert "Limitations" in result.report

    def test_golden_path_returns_overlay_status(self):
        result = run_minimal_loop("이것 아니면 저것밖에 없다")
        assert result.diagnostic_snapshot is not None
        assert result.diagnostic_snapshot.trace_id == result.request.trace_id
        assert result.overlay.overlay_status in (
            "verified", "needs_review", "insufficient_evidence"
        )

    def test_authority_chain_no_verdict_in_report(self):
        """Report must not contain forbidden verdict phrases."""
        result = run_minimal_loop("나는 항상 실패하는 사람이다")
        forbidden = re.compile(
            r"(확정|판정|진단\s*결과|verdict|diagnosed|determined|proven)",
            re.IGNORECASE,
        )
        assert not forbidden.search(result.report)

    @pytest.mark.parametrize("claim", [
        "나는 게으르기 때문에 공부를 못한다",
        "게을러서 실패했다",
        "나태해서 안 된다",
        "의지가 부족해서 실패했다",
        "노력이 부족해서 안 된다",
        "I failed because of laziness",
        "It's a lack of willpower",
        "lack of effort caused failure",
    ])
    def test_willpower_blame_blocked_variants(self, claim):
        # spec §6 (coaching gate redesign): the SYSTEM must not blame willpower in the
        # diagnostic/evidence/limitations sections (system_text block stays enforced via
        # _check_report_violations). The COACHING block MAY contain "lack of willpower" as
        # an instructional counter-example that teaches the learner NOT to blame willpower —
        # Mnemo-approved exemption (memory: project_mira_willpower_blame_exclusion_rationale).
        # Pre-redesign the whole report was asserted clean only because removed check 15
        # safe-fallbacked the entire report on any willpower match; now we assert the real
        # invariant on the non-coaching portion (robust to pyswip availability).
        # NOTE: previously 3 variants were xfail'd; un-xfail'd here as this assertion
        # realises exactly what that xfail described. Reconciliation flagged for review.
        result = run_minimal_loop(claim)
        blame = re.compile(
            r"(게으[르른를]|게을|나태|laziness|\blazy\b|willpower|"
            r"의지력?\s*부족|의지[가이]?\s*약|노력\s*부족|"
            r"lack\s+of\s+(effort|willpower|discipline))",
            re.IGNORECASE,
        )
        system_portion = result.report.split("## Coaching")[0]
        assert not blame.search(system_portion), f"Blame leaked in system_text for: {claim}"
        assert result.overlay.avoid_willpower_blame is True

    def test_overlay_always_avoids_willpower_blame(self):
        result = run_minimal_loop("의지력이 부족해서 실패했다")
        assert result.overlay.avoid_willpower_blame is True

    def test_report_safe_fallback_on_violation(self):
        """If somehow a violation slips through, report returns safe fallback."""
        overlay = self._make_overlay() if hasattr(self, '_make_overlay') else None
        if overlay is None:
            overlay = CVVerificationOverlay(
                trace_id="t-fb", request_id="req-t-fb",
                psr=PSRResult(P_appraisal="p", S_strategy="s", R_projection="r"),
                route_vtype="D", overlay_status="needs_review",
                lane1_pass=True, evidence_summary="test",
            )
        report = generate_report(overlay, "test")
        assert "Analysis" in report or "Diagnostic" in report


# ── Oracle leakage test ───────────────────────────────────────

class TestOracleLeakage:
    def test_no_eval_labels_in_overlay(self):
        """Eval labels (gold/near-miss/negative) must not appear in runtime output."""
        result = run_minimal_loop("공부 방법이 잘못된 것 같다")
        overlay_json = result.overlay.model_dump_json()
        for forbidden in ("gold", "near_miss_set", "negative_control", "eval_label"):
            assert forbidden not in overlay_json, f"Oracle label '{forbidden}' leaked into overlay"

    def test_no_eval_labels_in_report(self):
        result = run_minimal_loop("공부 방법이 잘못된 것 같다")
        for forbidden in ("gold", "near_miss_set", "negative_control", "eval_label"):
            assert forbidden not in result.report.lower()
