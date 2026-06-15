"""Night 2 FIX3 regression tests — pattern_id display strip in _check_report_violations.

Bug: pattern names like **willpower_blame** or 'willpower blame' in the report
tripped _WILLPOWER_PHRASES, forcing safe_fallback even on correct diagnoses.
Fix: strip _PATTERN_ID_DISPLAY before willpower check.
"""

from __future__ import annotations

import pytest

from mira.contracts.minimal import (
    CVVerificationOverlay,
    PatternCandidate,
    PSRResult,
)
from mira.report import (
    _PATTERN_ID_DISPLAY,
    _check_report_violations,
    generate_report,
    render_report_markdown,
    safe_fallback_report,
)
from mira.system_a.coaching.coaching import generate_coaching_block as load_coaching_block


class TestFix3PatternIdStrip:
    """FIX3: pattern_id display markers must not trigger willpower fallback."""

    def _make_overlay(self, **kwargs) -> CVVerificationOverlay:
        defaults = dict(
            trace_id="t-fix3",
            request_id="req-t-fix3",
            psr=PSRResult(
                P_appraisal="premise area",
                S_strategy="strategy area",
                R_projection="result area",
            ),
            route_vtype="A",
            overlay_status="verified",
            lane1_pass=True,
            evidence_summary="willpower_blame pattern matched on R-axis",
        )
        defaults.update(kwargs)
        return CVVerificationOverlay(**defaults)

    # ── Scenario A — FIX3 regression (integration) ──────────────

    def test_fix3_willpower_pattern_does_not_force_fallback(self, monkeypatch):
        """willpower_blame detected → report has coaching, not safe_fallback.

        Monkeypatches coaching to isolate FIX3 from YAML content issues.
        """
        clean_coaching = (
            "**reframing prompts** — Consider structural factors: task "
            "design, feedback timing, environment. Try one small change."
        )
        monkeypatch.setattr(
            "mira.report.generate_coaching_block",
            lambda pattern_id, lang="en": clean_coaching,
        )

        candidate = PatternCandidate(
            pattern_id="willpower_blame",
            canonical_id="PAT-DUAL-01",
            vtype="A",
            lane2_status="pass",
            evidence_trace=["trait_attribution(R-axis)", "structural_cause_blocked"],
        )
        overlay = self._make_overlay(pattern_candidates=[candidate])
        report = generate_report(overlay, "test claim", lang="en")

        assert report != safe_fallback_report("en")
        assert "reframing prompts" in report
        assert "willpower blame" in report

    # ── Scenario B — True blame language still blocked ──────────

    def test_coaching_willpower_exempt_but_forbidden_still_checked(self, monkeypatch):
        """Coaching is exempt from WILLPOWER check, but FORBIDDEN still applies.

        Coaching text with FORBIDDEN verdict language (e.g. "diagnosed") → fallback.
        Coaching text with only willpower/lazy reframing language → allowed.
        """
        verdict_coaching = (
            "**advice** — You are diagnosed with a severe cognitive bias. "
            "The verdict is clear."
        )
        monkeypatch.setattr(
            "mira.report.generate_coaching_block",
            lambda pattern_id, lang="en": verdict_coaching,
        )

        candidate = PatternCandidate(
            pattern_id="willpower_blame",
            canonical_id="PAT-DUAL-01",
            vtype="A",
            lane2_status="pass",
            evidence_trace=["t1"],
        )
        overlay = self._make_overlay(pattern_candidates=[candidate])
        # spec D1/CX-3: generate_report's coaching verdict gate was removed (redundant — its
        # only caller coach_from_overlay backstops with check#7). The verdict-forbidden
        # invariant for a STANDALONE render is now guarded by the expert renderer's own gate
        # (no check#7 backstop there), so verify via render_report_markdown which keeps it.
        report = render_report_markdown(overlay, "test", lang="en")

        assert report == safe_fallback_report("en")

    # ── Scenario C — _check_report_violations unit tests ────────

    def test_violations_bold_marker_allowed(self):
        """**willpower_blame** in bold → stripped → None."""
        text = (
            "## Diagnostic Summary\n\n"
            "**willpower_blame** evidence for: trait_attribution"
        )
        assert _check_report_violations(text) is None

    def test_violations_quoted_marker_allowed(self):
        """'willpower blame' in quotes → stripped → None."""
        text = "patterns matching 'willpower blame' were observed."
        assert _check_report_violations(text) is None

    def test_violations_korean_blame_detected(self):
        """Korean blame outside markers → willpower_blame_language."""
        text = (
            "**willpower_blame** 패턴 관찰. "
            "당신의 의지력 부족이 원인입니다."
        )
        assert _check_report_violations(text) == "willpower_blame_language"

    def test_violations_english_lazy_detected(self):
        """'lazy' outside markers → violation detected."""
        text = "Some narrative. The learner is lazy. End."
        violation = _check_report_violations(text)
        assert violation is not None

    def test_violations_marker_plus_real_blame(self):
        """Pattern name stripped, real blame still caught."""
        text = "**willpower_blame** 패턴 관찰. 의지력 부족이 원인."
        assert _check_report_violations(text) == "willpower_blame_language"

    def test_violations_clean_report_none(self):
        """No pattern name, no blame → None."""
        text = (
            "## Diagnostic Summary\n\n"
            "Patterns matching 'false dilemma' were observed.\n"
            "Consider exploring intermediate options."
        )
        assert _check_report_violations(text) is None

    def test_violations_pattern_name_only_no_blame(self):
        """FIX3 core regression: pattern name present, no blame → None.

        Without FIX3: 'willpower' in marker matches → "willpower_blame_language".
        With FIX3: marker stripped, narrative clean → None.
        """
        text = (
            "## Diagnostic Summary\n\n"
            "During abductive verification, patterns matching "
            "'willpower blame' were observed.\n\n"
            "**willpower_blame** evidence for: trait_attribution(R-axis)"
        )
        assert _check_report_violations(text) is None

    # ── CC Independent Review — Coverage gap additions ──────────
    # Added by CC during cross-verification with Codex (2026-05-23).
    # Each test references gap class A/B/C/D from cc-goal-fix3-review.txt.

    # ── Gap A: _PATTERN_ID_DISPLAY strip 범위 정밀도 ─────────────

    def test_violations_korean_pattern_name_marker_stripped(self):
        """Gap A2: Korean pattern names in **...** are stripped (Unicode \\w).

        Python 3 default re uses Unicode \\w, so 한글 matches. Future ko
        pattern IDs (e.g. **의지력_탓**) won't trip the willpower check.
        """
        text = "**의지력_탓** 패턴 관찰. 외부 요인을 살펴봅시다."
        assert _check_report_violations(text) is None

    def test_violations_quoted_underscore_marker_stripped(self):
        """Gap A3a: 'willpower_blame' (single-quote + underscore) stripped."""
        text = "patterns matching 'willpower_blame' were observed in narrative."
        assert _check_report_violations(text) is None

    def test_violations_spaces_only_marker_stripped(self):
        """Gap A4a: '**  **' (spaces inside markers) handled gracefully.

        [\\w ]+ allows space-only content. Empty body markers are stripped.
        """
        text = "**  ** unrelated content here."
        assert _check_report_violations(text) is None

    def test_violations_italic_single_marker_NOT_stripped(self):
        """Gap A5: italic *willpower* not stripped — current regex covers
        only **bold** and 'quoted', not single-asterisk italic.

        Spec-freeze: if report.py later emits italic markers, this test
        will fail and force explicit support decision.
        """
        text = "*willpower* in italic — current regex misses single-star."
        assert _check_report_violations(text) == "willpower_blame_language"

    def test_violations_backtick_marker_NOT_stripped(self):
        """Gap A6: `willpower_blame` (backtick) not stripped.

        Spec-freeze. Backtick code-style markers are common in markdown
        but the current regex does not cover them.
        """
        text = "code-style `willpower_blame` reference here."
        assert _check_report_violations(text) == "willpower_blame_language"

    def test_violations_double_quote_marker_NOT_stripped(self):
        """Gap A7: \"willpower blame\" (double-quote) not stripped.

        Spec-freeze. Only single-quote markers are stripped.
        """
        text = 'patterns matching "willpower blame" reported.'
        assert _check_report_violations(text) == "willpower_blame_language"

    # ── Gap B: FORBIDDEN_PHRASES strip 미적용 ───────────────────

    def test_violations_pattern_name_with_forbidden_substring_false_positive(self):
        """M1 hotfix (SemVer 0.2.1): catastrophizing removed from VERDICT_LANGUAGE_RE
        because it is a legitimate pattern name. Pattern names in
        evidence blocks should not trigger the safety fallback.
        """
        text = "**catastrophizing_thoughts** pattern observed."
        assert _check_report_violations(text) is None

    def test_violations_quoted_marker_with_forbidden_false_positive(self):
        """Gap B: Even quoted-marker pattern names with FORBIDDEN words
        trip the FORBIDDEN check.

        Spec-freeze. 'verdict bias' inside quotes is still detected as
        forbidden_verdict_language because FORBIDDEN runs before strip.
        """
        text = "patterns matching 'verdict bias' were observed."
        assert _check_report_violations(text) == "forbidden_verdict_language"

    # ── Gap C: 실제 운영 시나리오 ────────────────────────────────

    def test_real_yaml_willpower_blame_coaching_delivered(self):
        """Real coaching_skills.yaml willpower_blame content now outputs correctly.

        Coaching block is exempt from WILLPOWER violation check, so the
        reframing language ("willpower", "lazy" in educational context)
        no longer triggers safe_fallback. This is the core M1 fix.
        """
        candidate = PatternCandidate(
            pattern_id="willpower_blame",
            canonical_id="PAT-DUAL-01",
            vtype="A",
            lane2_status="pass",
            evidence_trace=["trait_attribution(R-axis)"],
        )
        overlay = self._make_overlay(pattern_candidates=[candidate])
        report = generate_report(overlay, "test claim", lang="en")
        assert report != safe_fallback_report("en")
        assert "willpower blame" in report
        assert "Coaching" in report or "coaching" in report.lower()

    def test_violations_pattern_ko_lang_marker_strip_e2e(self, monkeypatch):
        """Gap C: Korean (lang='ko') report path also benefits from marker
        strip. End-to-end via generate_report with a clean coaching block.
        """
        clean_ko = (
            "**reframing prompts** — 구조적 요인을 살펴봅시다: 과제 설계, "
            "피드백 타이밍, 환경. 한 가지 작은 변화부터 시도해 보세요."
        )
        monkeypatch.setattr(
            "mira.report.generate_coaching_block",
            lambda pattern_id, lang="en": clean_ko,
        )

        candidate = PatternCandidate(
            pattern_id="willpower_blame",
            canonical_id="PAT-DUAL-01",
            vtype="A",
            lane2_status="pass",
            evidence_trace=["trait_attribution(R-axis)"],
        )
        overlay = self._make_overlay(pattern_candidates=[candidate])
        report = generate_report(overlay, "test claim", lang="ko")

        assert report != safe_fallback_report("ko")
        assert "willpower blame" in report
        assert "reframing prompts" in report

    # ── Gap D: 경계 테스트 ──────────────────────────────────────

    def test_violations_empty_report(self):
        """Gap D1: empty input → None (no false positives on empty)."""
        assert _check_report_violations("") is None

    def test_violations_many_pattern_markers_no_blame(self):
        """Gap D2: 10+ pattern_id markers in a single report still strip
        cleanly. No accidental match through interaction.
        """
        markers = " ".join(f"**pattern_{i}**" for i in range(10))
        text = f"{markers} **willpower_blame** narrative is clean."
        assert _check_report_violations(text) is None

    def test_pattern_id_display_regex_covers_underscore_space_and_unicode(self):
        """_PATTERN_ID_DISPLAY must strip current pattern marker forms."""
        assert _PATTERN_ID_DISPLAY.fullmatch("**willpower_blame**")
        assert _PATTERN_ID_DISPLAY.fullmatch("'willpower blame'")
        assert _PATTERN_ID_DISPLAY.fullmatch("**의지력 부족**")

    def test_forbidden_check_runs_before_pattern_marker_strip(self):
        """M1 hotfix (SemVer 0.2.1): determined and catastrophizing removed from VERDICT_LANGUAGE_RE.
        Only actual verdict language (e.g. 'diagnosed') should trigger."""
        assert _check_report_violations("Pattern **determined_cause** observed.") is None
        assert _check_report_violations("Pattern **determined cause** observed.") is None
        assert _check_report_violations("Pattern **catastrophizing** observed.") is None
        assert (
            _check_report_violations("The patient was diagnosed with bias.")
            == "forbidden_verdict_language"
        )

    def test_fix3_willpower_pattern_does_not_force_korean_fallback(self, monkeypatch):
        """lang='ko' follows the same FIX3 marker-strip path as lang='en'."""
        clean_coaching = (
            "**structure prompts** — 상황 구조, 피드백 시점, 과제 단위를 "
            "나누어 점검해 보세요."
        )
        monkeypatch.setattr(
            "mira.report.generate_coaching_block",
            lambda pattern_id, lang="ko": clean_coaching,
        )

        candidate = PatternCandidate(
            pattern_id="willpower_blame",
            canonical_id="PAT-DUAL-01",
            vtype="A",
            lane2_status="pass",
            evidence_trace=["trait_attribution(R-axis)", "structural_cause_blocked"],
        )
        overlay = self._make_overlay(pattern_candidates=[candidate])
        report = generate_report(overlay, "test claim", lang="ko")

        assert report != safe_fallback_report("ko")
        assert "## 코칭" in report
        assert "structure prompts" in report

    @pytest.mark.parametrize("lang", ["en", "ko"])
    def test_real_willpower_blame_coaching_template_trips_safety_gate(self, lang):
        """Characterization: the EN skill template still contains bare
        willpower-blame phrases (Mnemo-approved instructional counter-example,
        spec §6 coaching exemption).

        CONTRACT CHANGE (improvement #3 draft): the KO template was rewritten
        gate-token-free — the Korean coaching achieves Invariant #12 compliance
        by construction instead of relying on the coaching-section exemption.
        (Previously the ko block only tripped the gate via the shared ENGLISH
        psr_coaching_focus line; with psr_coaching_focus_ko it no longer does.)
        """
        coaching = load_coaching_block("willpower_blame", lang=lang)

        assert coaching is not None
        if lang == "en":
            assert _check_report_violations(coaching) == "willpower_blame_language"
        else:
            assert _check_report_violations(coaching) is None
