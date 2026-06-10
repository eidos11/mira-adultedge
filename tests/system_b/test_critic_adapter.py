"""Lane 1 critic adapter integration tests.

Tests the M1 Reduced scope (checks #6/#7/#9) adapter that bridges
the pipeline data structures to the critic contract.
"""

from __future__ import annotations

from mira.contracts.minimal import (
    PatternCandidate,
    PSRResult,
)
from mira.system_b.engine.critic.adapter import (
    V1_CHECKS,
    build_lane_one_input,
    mask_learner_citations,
    psr_result_to_decomposition,
    run_reduced_critic,
)


def _make_psr(
    p: str = "test premise",
    s: str = "test strategy",
    r: str = "test result",
    claim_type: str = "descriptive",
) -> PSRResult:
    return PSRResult(
        P_appraisal=p, S_strategy=s, R_projection=r, claim_type=claim_type,
    )


def _make_candidates(*pattern_ids: str) -> list[PatternCandidate]:
    return [
        PatternCandidate(
            pattern_id=pid, canonical_id=pid, vtype="I",
        )
        for pid in pattern_ids
    ]


class TestPSRConversion:
    def test_basic_conversion(self):
        psr = _make_psr(claim_type="self_assessment")
        decomp = psr_result_to_decomposition(psr)
        assert decomp.P_appraisal == "test premise"
        assert decomp.S_strategy == "test strategy"
        assert decomp.R_projection == "test result"
        assert decomp.claim_type == "self_assessment"

    def test_defaults_for_v1(self):
        decomp = psr_result_to_decomposition(_make_psr())
        assert decomp.P_latitude == "medium"
        assert decomp.S_exclusivity == "open"
        assert decomp.R_emotional_load == "neutral"

    def test_claim_type_mapping(self):
        for src, expected in [
            ("normative", "argument"),
            ("descriptive", "argument"),
            ("self_assessment", "self_assessment"),
            ("unclassified", "argument"),
        ]:
            decomp = psr_result_to_decomposition(_make_psr(claim_type=src))
            assert decomp.claim_type == expected, f"{src} → {expected}"


class TestMasking:
    def test_psr_quote_masking(self):
        text = "분석 결과:\n전제(P): 게으름 때문이다\n전략(S): 노력 부족\n결과(R): 실패"
        masked = mask_learner_citations(text)
        assert "게으름" not in masked
        assert "노력 부족" not in masked
        assert "[PSR_QUOTE]" in masked

    def test_bracket_quote_masking(self):
        text = "학습자는 「나는 게을러서 못했다」라고 말했습니다."
        masked = mask_learner_citations(text)
        assert "게을러서" not in masked
        assert "[LEARNER_CITATION]" in masked

    def test_no_masking_for_system_text(self):
        text = "이 패턴은 동기 부족과 관련됩니다."
        masked = mask_learner_citations(text)
        assert masked == text


class TestReducedCritic:
    def test_pass_clean_report(self):
        """Normal report with valid patterns passes all v1 checks."""
        passed, audit = run_reduced_critic(
            _make_psr(), _make_candidates("fluency_illusion"), "I",
            response_text="이 패턴은 표면 유창성과 관련됩니다.",
            trace_id="t-clean",
        )
        assert passed is True

    def test_fail_unknown_pattern_id(self):
        """Check #9: pattern_id must be in registry."""
        passed, audit = run_reduced_critic(
            _make_psr(), _make_candidates("NONEXISTENT_PATTERN"), "I",
            trace_id="t-registry",
        )
        assert passed is False
        v1_violations = [v for v in audit.violations if v.check_id in V1_CHECKS]
        assert any(v.check_id == 9 for v in v1_violations)

    def test_fail_verdict_language(self):
        """Check #7: response must not contain verdict language."""
        passed, audit = run_reduced_critic(
            _make_psr(), _make_candidates("fluency_illusion"), "I",
            response_text="진단 결과: 당신은 fluency illusion을 보입니다.",
            trace_id="t-verdict",
        )
        assert passed is False
        v1_violations = [v for v in audit.violations if v.check_id in V1_CHECKS]
        assert any(v.check_id == 7 for v in v1_violations)

    def test_willpower_mention_does_not_block(self):
        """check 15 removed per spec D4: willpower mention never triggers a block."""
        passed, audit = run_reduced_critic(
            _make_psr(), _make_candidates("fluency_illusion"), "I",
            response_text="의지력 부족이 근본 원인입니다.",
            trace_id="t-willpower",
        )
        assert passed is True
        v1_violations = [v for v in audit.violations if v.check_id in V1_CHECKS]
        assert not any(v.check_id == 15 for v in v1_violations)

    def test_learner_citation_not_false_positive(self):
        """Learner's own words in PSR quotes do not trigger any block."""
        report = (
            "## 근거\n\n"
            "전제(P): 나는 게을러서 공부를 못했다\n"
            "전략(S): 더 열심히 해야지\n"
            "결과(R): 여전히 실패함\n\n"
            "## 코칭\n\n"
            "동기 부족의 구조적 원인을 살펴봅시다."
        )
        passed, audit = run_reduced_critic(
            _make_psr(), _make_candidates("oversimplified_cause"), "A",
            response_text=report,
            trace_id="t-citation",
        )
        assert passed is True

    def test_fail_non_admissible_llm_tag(self):
        """Check #6: LLM output tag must be admissible."""
        lane_input = build_lane_one_input(
            _make_psr(), _make_candidates("fluency_illusion"), "I",
            trace_id="t-tag",
            llm_output_tag="INVALID_TAG",
        )
        from mira.system_b.engine.critic.contract import contract_critic
        audit = contract_critic(lane_input)
        v1_violations = [v for v in audit.violations if v.check_id in V1_CHECKS]
        assert any(v.check_id == 6 for v in v1_violations)

    def test_v1_checks_constant(self):
        """V1_CHECKS must be exactly {6, 7, 9} — check 15 (willpower_blame_trigger) was
        removed in the coaching-gate redesign (spec §5/T1). Willpower blocking now lives in
        report._check_report_violations, not the Lane-1 reduced critic; contract_critic
        never emits check_id 15 (behavioural removal locked by test_contract_willpower_gate)."""
        assert V1_CHECKS == frozenset({6, 7, 9})
