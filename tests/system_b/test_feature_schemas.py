"""Tests for Lane 2 feature_schemas module."""

from __future__ import annotations

from mira.system_b.lane2.feature_schemas import (
    SUPPORTED_PATTERNS,
    get_combined_schema,
    get_supported_key,
    get_system_prompt,
    get_user_prompt,
    json_to_prolog_terms,
)


class TestConstants:
    def test_supported_patterns(self) -> None:
        assert SUPPORTED_PATTERNS == frozenset({"false_dilemma", "oversimplified_cause"})

    def test_supported_key_false_dilemma(self) -> None:
        assert get_supported_key("false_dilemma") == "options_analysis"

    def test_supported_key_oversimplified(self) -> None:
        assert get_supported_key("oversimplified_cause") == "causal_analysis"

    def test_unsupported_key_raises(self) -> None:
        import pytest
        with pytest.raises(KeyError):
            get_supported_key("unknown_pattern")


class TestSystemPrompt:
    def test_contains_analyst_role(self) -> None:
        prompt = get_system_prompt()
        assert "text structure analyst" in prompt

    def test_contains_json_instruction(self) -> None:
        prompt = get_system_prompt()
        assert "JSON" in prompt


class TestUserPrompt:
    def test_includes_learner_text(self) -> None:
        prompt = get_user_prompt("I must choose A or B", ["false_dilemma"])
        assert "I must choose A or B" in prompt

    def test_includes_all_four_schemas(self) -> None:
        prompt = get_user_prompt("text", ["false_dilemma"])
        assert "options_analysis" in prompt
        assert "causal_analysis" in prompt
        assert "temporal_analysis" in prompt
        assert "agent_analysis" in prompt

    def test_context_segregation_no_pattern_names(self) -> None:
        prompt = get_user_prompt("text", ["false_dilemma", "oversimplified_cause"])
        assert "false_dilemma" not in prompt
        assert "oversimplified_cause" not in prompt

    def test_includes_questions_for_requested_patterns(self) -> None:
        prompt = get_user_prompt("text", ["false_dilemma"])
        assert "actionable choice" in prompt

    def test_empty_pattern_ids_still_has_schemas(self) -> None:
        prompt = get_user_prompt("text", [])
        assert "options_analysis" in prompt

    def test_oversimplified_question_scopes_to_speaker_own_attribution(self) -> None:
        # L1 refinement (design v0.2): the causal cause-listing question must
        # scope to the speaker's OWN attribution and exclude symptoms / action
        # options, instead of "every cause, factor, or contributing element"
        # (which over-extracts symptoms, restatements, and others' views ->
        # inflated cause_count -> Prolog reject). The behavioral effect is
        # validated by re-validation (deferred); this pins the prompt contract.
        prompt = get_user_prompt("text", ["oversimplified_cause"])
        assert "every cause, factor, or contributing element" not in prompt
        assert "attributes their own" in prompt
        assert "symptoms" in prompt
        assert "action options" in prompt

    def test_oversimplified_question_requires_verbatim_grounding(self) -> None:
        # L2 refinement (design v0.2 §5 follow-up): L1 merging drifts the
        # extracted text away from the source, tripping the fuzzy fidelity guard
        # (026 re-validation: 11/12 unverified / feature_fidelity). Requiring a
        # verbatim phrase per cause grounds the merge to the source (the sonnet
        # success pattern: abstract cause + 'bad at math' quote -> fidelity
        # pass). Behavioral effect validated by re-validation; this pins the
        # prompt contract.
        prompt = get_user_prompt("text", ["oversimplified_cause"])
        assert "verbatim phrase" in prompt
        assert "grounded" in prompt


class TestCombinedSchema:
    def test_all_four_sections_present(self) -> None:
        schema = get_combined_schema(["false_dilemma"])
        assert "options_analysis" in schema
        assert "causal_analysis" in schema
        assert "temporal_analysis" in schema
        assert "agent_analysis" in schema

    def test_schema_structure(self) -> None:
        schema = get_combined_schema([])
        oa = schema["options_analysis"]
        assert oa["type"] == "object"
        assert "option_count" in oa["properties"]

    def test_options_schema_has_viable_middle(self) -> None:
        """F1: viable_middle_exists distinguishes dismissed vs genuinely open middle."""
        schema = get_combined_schema([])
        oa = schema["options_analysis"]
        assert "viable_middle_exists" in oa["properties"]


class TestPrologConversion:
    def test_false_dilemma_basic(self) -> None:
        features = {
            "options_analysis": {
                "options_listed": ["study", "party"],
                "option_count": 2,
                "exclusivity_markers": ["either...or"],
                "middle_options_mentioned": False,
                "viable_middle_exists": False,
                "logical_space_explored": "explicit",
            }
        }
        terms = json_to_prolog_terms("false_dilemma", features)
        assert "option_count(2)" in terms
        assert "middle_options_mentioned(false)" in terms
        assert "viable_middle_exists(false)" in terms
        assert "logical_space_explored(explicit)" in terms

    def test_oversimplified_cause_basic(self) -> None:
        features = {
            "causal_analysis": {
                "causes_listed": ["laziness"],
                "cause_count": 1,
                "alternative_causes_mentioned": False,
                "sufficiency_claim_strength": "strong",
                "temporal_only": False,
                "causal_claim_type": "behavioral",
            }
        }
        terms = json_to_prolog_terms("oversimplified_cause", features)
        assert "cause_count(1)" in terms
        assert "alternative_causes_mentioned(false)" in terms
        assert "sufficiency_claim_strength(strong)" in terms
        assert "causal_claim_type(behavioral)" in terms

    def test_boolean_true(self) -> None:
        features = {"options_analysis": {"middle_options_mentioned": True}}
        terms = json_to_prolog_terms("false_dilemma", features)
        assert "middle_options_mentioned(true)" in terms

    def test_array_conversion(self) -> None:
        features = {"options_analysis": {"exclusivity_markers": ["only", "must"]}}
        terms = json_to_prolog_terms("false_dilemma", features)
        term = [t for t in terms if "exclusivity_markers" in t][0]
        assert "['only', 'must']" in term

    def test_missing_key_returns_empty(self) -> None:
        terms = json_to_prolog_terms("false_dilemma", {})
        assert terms == []
