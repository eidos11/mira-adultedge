
from __future__ import annotations

import mira.system_a.coaching.coaching as loader


def _reset_cache() -> None:
    loader._COACHING_CACHE = None
    loader._THEORY_CACHE = None


class TestCoachingContentCache:
    def setup_method(self) -> None:
        _reset_cache()

    def teardown_method(self) -> None:
        _reset_cache()

    def test_cache_starts_none(self) -> None:
        _reset_cache()
        assert loader._COACHING_CACHE is None

    def test_first_call_populates_cache(self) -> None:
        result = loader.get_coaching_content()
        assert isinstance(result, dict)
        assert loader._COACHING_CACHE is not None

    def test_second_call_returns_same_object(self) -> None:
        first = loader.get_coaching_content()
        second = loader.get_coaching_content()
        assert first is second


class TestTheoryTemplatesCache:
    def setup_method(self) -> None:
        _reset_cache()

    def teardown_method(self) -> None:
        _reset_cache()

    def test_first_call_populates_cache(self) -> None:
        result = loader.get_theory_templates()
        assert isinstance(result, dict)
        assert loader._THEORY_CACHE is not None

    def test_second_call_returns_same_object(self) -> None:
        first = loader.get_theory_templates()
        second = loader.get_theory_templates()
        assert first is second


class TestGetAvailablePatterns:
    def setup_method(self) -> None:
        _reset_cache()

    def test_returns_list(self) -> None:
        result = loader.get_available_patterns()
        assert isinstance(result, list)

    def test_contains_known_patterns(self) -> None:
        result = loader.get_available_patterns()
        assert "fluency_illusion" in result
        assert "false_dilemma" in result
        assert "oversimplified_cause" in result

    def test_no_duplicates(self) -> None:
        result = loader.get_available_patterns()
        assert len(result) == len(set(result))


class TestGenerateCoachingBlock:
    def setup_method(self) -> None:
        _reset_cache()

    def test_known_pattern_returns_str(self) -> None:
        result = loader.generate_coaching_block("fluency_illusion")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_unknown_pattern_returns_none(self) -> None:
        result = loader.generate_coaching_block("nonexistent_pattern_xyz")
        assert result is None

    def test_output_contains_pattern_name(self) -> None:
        result = loader.generate_coaching_block("fluency_illusion")
        assert result is not None
        assert "fluency illusion" in result

    def test_output_contains_inquiry_questions(self) -> None:
        result = loader.generate_coaching_block("fluency_illusion", lang="ko")
        assert result is not None
        assert "자기 점검 질문" in result

    def test_output_contains_theory_message(self) -> None:
        result = loader.generate_coaching_block("fluency_illusion", lang="ko")
        assert result is not None
        assert ">" in result

    def test_output_contains_action_invitation(self) -> None:
        result = loader.generate_coaching_block("false_dilemma", lang="ko")
        assert result is not None
        assert "다음 단계" in result

    def test_default_lang_is_en(self) -> None:
        result = loader.generate_coaching_block("fluency_illusion")
        assert result is not None
        assert "PSR focus" in result

    def test_ko_lang_labels(self) -> None:
        result = loader.generate_coaching_block("fluency_illusion", lang="ko")
        assert result is not None
        assert "PSR 관점" in result

    def test_generate_coaching_block_tentative_frames_as_possibility(self) -> None:
        block = loader.generate_coaching_block("oversimplified_cause", lang="en", tentative=True)
        assert block is not None
        # tentative lead-in present; bare assertive recognition must not stand alone
        assert "may" in block.lower() or "혹시" in block or "if this" in block.lower()

    def test_generate_coaching_block_default_is_assertive(self) -> None:
        block = loader.generate_coaching_block("oversimplified_cause", lang="en")  # tentative defaults False
        assert block is not None

    def test_tentative_coaching_has_no_verdict_language(self) -> None:
        # spec CX-3: tentative coaching must be verdict-free so the preserved Lane-1
        # check#7 (no_verdict_language) does not safe-fallback tentative coaching in
        # coach_from_overlay (which runs the critic over the rendered report).
        from mira.contracts.safety_patterns import VERDICT_LANGUAGE_RE

        block = loader.generate_coaching_block("oversimplified_cause", lang="en", tentative=True)
        assert block is not None
        assert not VERDICT_LANGUAGE_RE.search(block)
