
from __future__ import annotations

import os
from unittest.mock import patch

from mira.system_b.lane3.llm_extractor import (
    _extract_json_block,
    _parse_response,
    _try_parse_json,
    build_extraction_prompt,
    extract_pattern_candidates,
    get_candidate_patterns,
    resolve_backend,
)


class TestGetCandidatePatterns:
    def test_concept_stage_returns_8(self) -> None:
        result = get_candidate_patterns("concept")
        assert len(result) == 8

    def test_framework_stage_returns_8(self) -> None:
        result = get_candidate_patterns("framework")
        assert len(result) == 8

    def test_practice_stage_returns_8(self) -> None:
        result = get_candidate_patterns("practice")
        assert len(result) == 8

    def test_reality_stage_returns_8(self) -> None:
        result = get_candidate_patterns("reality")
        assert len(result) == 8

    def test_unknown_stage_returns_defaults(self) -> None:
        result = get_candidate_patterns("nonexistent_stage")
        assert len(result) == 8
        assert "fluency_illusion" in result

    def test_all_items_are_strings(self) -> None:
        for stage in ("concept", "framework", "practice", "reality"):
            for item in get_candidate_patterns(stage):
                assert isinstance(item, str)


class TestBuildExtractionPrompt:
    def test_contains_learner_claim(self) -> None:
        prompt = build_extraction_prompt("I failed the exam", ["false_dilemma"])
        assert "I failed the exam" in prompt

    def test_contains_all_candidates(self) -> None:
        candidates = ["false_dilemma", "sunk_cost", "fluency_illusion"]
        prompt = build_extraction_prompt("test claim", candidates)
        for c in candidates:
            assert c in prompt

    def test_same_claim_produces_same_prompt(self) -> None:
        candidates = ["false_dilemma", "sunk_cost"]
        p1 = build_extraction_prompt("same claim", candidates)
        p2 = build_extraction_prompt("same claim", candidates)
        assert p1 == p2

    def test_contains_lang_marker(self) -> None:
        prompt = build_extraction_prompt("test", ["false_dilemma"], lang="en")
        assert "(en)" in prompt

    def test_does_not_mutate_input_list(self) -> None:
        candidates = ["b_pattern", "a_pattern"]
        original = candidates.copy()
        build_extraction_prompt("test", candidates)
        assert candidates == original


class TestResolveBackend:
    def test_explicit_codex(self) -> None:
        with patch.dict(os.environ, {"MIRA_LLM_BACKEND": "codex"}, clear=False):
            backend, model = resolve_backend()
            assert backend == "codex"
            assert model == "gpt-5.5"

    def test_explicit_openai(self) -> None:
        with patch.dict(os.environ, {"MIRA_LLM_BACKEND": "openai"}, clear=False):
            backend, model = resolve_backend()
            assert backend == "openai"
            assert model == "gpt-5.4"

    def test_explicit_anthropic(self) -> None:
        with patch.dict(os.environ, {"MIRA_LLM_BACKEND": "anthropic"}, clear=False):
            backend, model = resolve_backend()
            assert backend == "anthropic"
            assert model == "claude-sonnet-4-6"

    def test_explicit_none(self) -> None:
        with patch.dict(os.environ, {"MIRA_LLM_BACKEND": "none"}, clear=False):
            backend, model = resolve_backend()
            assert backend == "none"
            assert model == ""

    def test_model_override(self) -> None:
        env = {"MIRA_LLM_BACKEND": "openai", "MIRA_LLM_MODEL": "gpt-5.5"}
        with patch.dict(os.environ, env, clear=False):
            backend, model = resolve_backend()
            assert backend == "openai"
            assert model == "gpt-5.5"

    def test_anthropic_model_override(self) -> None:
        env = {"MIRA_LLM_BACKEND": "anthropic", "MIRA_LLM_MODEL": "claude-opus-4-6"}
        with patch.dict(os.environ, env, clear=False):
            backend, model = resolve_backend()
            assert backend == "anthropic"
            assert model == "claude-opus-4-6"

    @patch("mira.system_b.lane3.llm_extractor.shutil.which", return_value=None)
    def test_autodetect_no_codex_uses_openai(self, _mock_which: object) -> None:
        env = {"OPENAI_API_KEY": "test-key"}
        with patch.dict(os.environ, env, clear=True):
            backend, model = resolve_backend()
            assert backend == "openai"
            assert model == "gpt-5.4"

    @patch("mira.system_b.lane3.llm_extractor.shutil.which", return_value=None)
    def test_autodetect_no_codex_no_openai_uses_anthropic(self, _mock_which: object) -> None:
        env = {"ANTHROPIC_API_KEY": "test-key"}
        with patch.dict(os.environ, env, clear=True):
            backend, model = resolve_backend()
            assert backend == "anthropic"
            assert model == "claude-sonnet-4-6"

    @patch("mira.system_b.lane3.llm_extractor.shutil.which", return_value=None)
    def test_autodetect_nothing_returns_none(self, _mock_which: object) -> None:
        with patch.dict(os.environ, {}, clear=True):
            backend, model = resolve_backend()
            assert backend == "none"
            assert model == ""

    @patch("mira.system_b.lane3.llm_extractor.shutil.which", return_value="/usr/bin/codex")
    def test_autodetect_codex_available(self, _mock_which: object) -> None:
        with patch.dict(os.environ, {}, clear=True):
            backend, model = resolve_backend()
            assert backend == "codex"
            assert model == "gpt-5.5"


class TestExtractPatternCandidatesNoApi:
    def test_returns_empty_when_lane3_disabled(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            result = extract_pattern_candidates("test claim")
            assert result == []

    @patch("mira.system_b.lane3.llm_extractor.shutil.which", return_value=None)
    def test_returns_empty_without_any_backend(self, _mock_which: object) -> None:
        env = {"MIRA_ENABLE_LANE3": "1"}
        with patch.dict(os.environ, env, clear=True):
            result = extract_pattern_candidates("test claim")
            assert result == []

    @patch("mira.system_b.lane3.llm_extractor.shutil.which", return_value=None)
    def test_returns_list_type(self, _mock_which: object) -> None:
        env = {"MIRA_ENABLE_LANE3": "1"}
        with patch.dict(os.environ, env, clear=True):
            result = extract_pattern_candidates("test claim")
            assert isinstance(result, list)

    def test_returns_empty_with_explicit_none_backend(self) -> None:
        env = {"MIRA_ENABLE_LANE3": "1", "MIRA_LLM_BACKEND": "none"}
        with patch.dict(os.environ, env, clear=False):
            result = extract_pattern_candidates("test claim")
            assert result == []

    def test_returns_empty_when_openai_backend_but_no_key(self) -> None:
        env = {"MIRA_ENABLE_LANE3": "1", "MIRA_LLM_BACKEND": "openai"}
        with patch.dict(os.environ, env, clear=True):
            result = extract_pattern_candidates("test claim")
            assert result == []

    def test_returns_empty_when_anthropic_backend_but_no_key(self) -> None:
        env = {"MIRA_ENABLE_LANE3": "1", "MIRA_LLM_BACKEND": "anthropic"}
        with patch.dict(os.environ, env, clear=True):
            result = extract_pattern_candidates("test claim")
            assert result == []


class TestTryParseJson:
    def test_valid_json_object(self) -> None:
        result = _try_parse_json('{"patterns": []}')
        assert result == {"patterns": []}

    def test_valid_json_with_patterns(self) -> None:
        text = '{"patterns": [{"pattern_id": "sunk_cost", "evidence": ["invested time"]}]}'
        result = _try_parse_json(text)
        assert result is not None
        assert len(result["patterns"]) == 1

    def test_trailing_comma_object(self) -> None:
        result = _try_parse_json('{"a": 1,}')
        assert result == {"a": 1}

    def test_trailing_comma_array(self) -> None:
        result = _try_parse_json('{"patterns": [1,]}')
        assert result is not None
        assert result["patterns"] == [1]

    def test_invalid_json_returns_none(self) -> None:
        result = _try_parse_json("not json at all")
        assert result is None

    def test_empty_string_returns_none(self) -> None:
        result = _try_parse_json("")
        assert result is None


class TestExtractJsonBlock:
    def test_code_fence_json(self) -> None:
        text = 'Here is output:\n```json\n{"patterns": []}\n```\nDone.'
        result = _extract_json_block(text)
        assert result is not None
        assert "patterns" in result

    def test_code_fence_no_lang(self) -> None:
        text = 'Output:\n```\n{"patterns": []}\n```'
        result = _extract_json_block(text)
        assert result is not None

    def test_bare_braces(self) -> None:
        text = 'The result is {"patterns": []} and that is all.'
        result = _extract_json_block(text)
        assert result is not None
        assert result.startswith("{")

    def test_no_match_returns_none(self) -> None:
        result = _extract_json_block("no json here")
        assert result is None


class TestParseResponse:
    def test_valid_json_response(self) -> None:
        text = '{"patterns": [{"pattern_id": "sunk_cost", "evidence": ["time invested"]}]}'
        result = _parse_response(text)
        assert len(result) == 1
        assert result[0]["pattern_id"] == "sunk_cost"
        assert result[0]["evidence"] == ["time invested"]

    def test_code_fenced_response(self) -> None:
        text = '```json\n{"patterns": [{"pattern_id": "false_dilemma", "evidence": ["only two options"]}]}\n```'
        result = _parse_response(text)
        assert len(result) == 1
        assert result[0]["pattern_id"] == "false_dilemma"

    def test_filters_missing_pattern_id(self) -> None:
        text = '{"patterns": [{"evidence": ["no id"]}, {"pattern_id": "sunk_cost", "evidence": []}]}'
        result = _parse_response(text)
        assert len(result) == 1
        assert result[0]["pattern_id"] == "sunk_cost"

    def test_coerces_evidence_to_strings(self) -> None:
        text = '{"patterns": [{"pattern_id": "test", "evidence": [123, true]}]}'
        result = _parse_response(text)
        assert result[0]["evidence"] == ["123", "True"]

    def test_invalid_json_returns_empty(self) -> None:
        result = _parse_response("this is not json")
        assert result == []

    def test_empty_patterns_list(self) -> None:
        result = _parse_response('{"patterns": []}')
        assert result == []

    def test_missing_evidence_key_defaults_empty(self) -> None:
        text = '{"patterns": [{"pattern_id": "test"}]}'
        result = _parse_response(text)
        assert result[0]["evidence"] == []
