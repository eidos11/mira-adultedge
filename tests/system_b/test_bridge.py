"""Tests for Lane 2 bridge module (LLM calls mocked)."""

from __future__ import annotations

import json
import shutil
from unittest.mock import patch

import pytest

from mira.system_b.lane2.bridge import (
    BridgeVerdict,
    _parse_and_validate_json,
    _resolve_extract_backend,
    run_lane2_bridge,
)

# These two mock tests reach the real Prolog verify/3 path (accept/reject
# verdicts come from Prolog), so they need pyswip + SWI-Prolog. Guarded like
# tests/test_lane2_prolog_pyswip.py rather than failing without the optional stack.
try:
    from pyswip import Prolog as _Prolog  # noqa: F401

    _PYSWIP_AVAILABLE = True
except Exception:
    _PYSWIP_AVAILABLE = False

_requires_prolog = pytest.mark.skipif(
    not _PYSWIP_AVAILABLE or shutil.which("swipl") is None,
    reason="pyswip + SWI-Prolog required (Lane 2 Prolog integration)",
)


class TestBridgeVerdict:
    def test_frozen(self) -> None:
        v = BridgeVerdict(pattern_id="false_dilemma", verdict="accept")
        with pytest.raises(AttributeError):
            v.verdict = "reject"  # type: ignore[misc]

    def test_defaults(self) -> None:
        v = BridgeVerdict(pattern_id="x", verdict="unverified")
        assert v.features is None
        assert v.error is None


class TestResolveBackend:
    def test_explicit_openai(self) -> None:
        with patch.dict("os.environ", {"MIRA_LLM_EXTRACT_BACKEND": "openai", "OPENAI_API_KEY": "k"}):
            import mira.system_b.lane2.bridge as mod
            orig = mod.MIRA_LLM_EXTRACT_BACKEND
            mod.MIRA_LLM_EXTRACT_BACKEND = "openai"
            mod.MIRA_LLM_EXTRACT_MODEL = ""
            try:
                backend, model = _resolve_extract_backend()
                assert backend == "openai"
                assert model == "gpt-5.4"
            finally:
                mod.MIRA_LLM_EXTRACT_BACKEND = orig

    def test_none_backend(self) -> None:
        import mira.system_b.lane2.bridge as mod
        orig = mod.MIRA_LLM_EXTRACT_BACKEND
        mod.MIRA_LLM_EXTRACT_BACKEND = "none"
        try:
            backend, model = _resolve_extract_backend()
            assert backend == "none"
        finally:
            mod.MIRA_LLM_EXTRACT_BACKEND = orig


class TestParseJson:
    def test_valid_json(self) -> None:
        data = json.dumps({"options_analysis": {"option_count": 2}})
        result = _parse_and_validate_json(data)
        assert result is not None
        assert result["options_analysis"]["option_count"] == 2

    def test_json_with_code_fence(self) -> None:
        data = '```json\n{"causal_analysis": {"cause_count": 1}}\n```'
        result = _parse_and_validate_json(data)
        assert result is not None
        assert result["causal_analysis"]["cause_count"] == 1

    def test_invalid_json(self) -> None:
        assert _parse_and_validate_json("not json") is None

    def test_missing_expected_keys(self) -> None:
        data = json.dumps({"temporal_analysis": {}})
        assert _parse_and_validate_json(data) is None

    def test_trailing_comma_tolerance(self) -> None:
        data = '{"options_analysis": {"x": 1,}}'
        result = _parse_and_validate_json(data)
        assert result is not None


class TestRunBridge:
    def test_disabled_returns_unverified(self) -> None:
        import mira.system_b.lane2.bridge as mod
        orig = mod.MIRA_LANE2_ENABLED
        mod.MIRA_LANE2_ENABLED = False
        try:
            results = run_lane2_bridge("text", ["false_dilemma"])
            assert results["false_dilemma"].verdict == "unverified"
        finally:
            mod.MIRA_LANE2_ENABLED = orig

    def test_unsupported_pattern_unverified(self) -> None:
        import mira.system_b.lane2.bridge as mod
        orig_enabled = mod.MIRA_LANE2_ENABLED
        orig_backend = mod.MIRA_LLM_EXTRACT_BACKEND
        mod.MIRA_LANE2_ENABLED = True
        mod.MIRA_LLM_EXTRACT_BACKEND = "none"
        try:
            results = run_lane2_bridge("text", ["fluency_illusion"])
            assert results["fluency_illusion"].verdict == "unverified"
        finally:
            mod.MIRA_LANE2_ENABLED = orig_enabled
            mod.MIRA_LLM_EXTRACT_BACKEND = orig_backend

    def test_none_backend_all_unverified(self, monkeypatch) -> None:
        import mira.system_b.lane2.bridge as mod
        monkeypatch.setenv("MIRA_ENABLE_LANE3", "1")  # past consent gate → backend path
        orig_enabled = mod.MIRA_LANE2_ENABLED
        orig_backend = mod.MIRA_LLM_EXTRACT_BACKEND
        mod.MIRA_LANE2_ENABLED = True
        mod.MIRA_LLM_EXTRACT_BACKEND = "none"
        try:
            results = run_lane2_bridge("text", ["false_dilemma", "oversimplified_cause"])
            assert all(v.verdict == "unverified" for v in results.values())
        finally:
            mod.MIRA_LANE2_ENABLED = orig_enabled
            mod.MIRA_LLM_EXTRACT_BACKEND = orig_backend

    @_requires_prolog
    def test_mock_openai_accept(self, monkeypatch) -> None:
        monkeypatch.setenv("MIRA_ENABLE_LANE3", "1")  # consent opt-in (extraction mocked)
        mock_response = json.dumps({
            "options_analysis": {
                "options_listed": ["A", "B"],
                "option_count": 2,
                "exclusivity_markers": ["either...or"],
                "middle_options_mentioned": False,
                "viable_middle_exists": False,
                "logical_space_explored": "explicit",
            },
            "causal_analysis": {
                "causes_listed": [],
                "cause_count": 0,
                "alternative_causes_mentioned": False,
                "sufficiency_claim_strength": "absent",
                "temporal_only": False,
                "causal_claim_type": "unknown",
            },
            "temporal_analysis": {"time_references": [], "temporal_order_claimed": False},
            "agent_analysis": {"actors_mentioned": [], "agency_attribution": "self"},
        })

        import mira.system_b.lane2.bridge as mod
        orig_enabled = mod.MIRA_LANE2_ENABLED
        orig_backend = mod.MIRA_LLM_EXTRACT_BACKEND
        mod.MIRA_LANE2_ENABLED = True
        mod.MIRA_LLM_EXTRACT_BACKEND = "openai"

        try:
            with patch.object(mod, "_call_step2_with_retry", return_value=mock_response):
                results = run_lane2_bridge("I must choose A or B", ["false_dilemma"])
                assert results["false_dilemma"].verdict == "accept"
        finally:
            mod.MIRA_LANE2_ENABLED = orig_enabled
            mod.MIRA_LLM_EXTRACT_BACKEND = orig_backend

    @_requires_prolog
    def test_mock_reject(self, monkeypatch) -> None:
        monkeypatch.setenv("MIRA_ENABLE_LANE3", "1")  # consent opt-in (extraction mocked)
        mock_response = json.dumps({
            "options_analysis": {
                "options_listed": ["A", "B", "C", "D"],
                "option_count": 4,
                "exclusivity_markers": [],
                "middle_options_mentioned": False,
                "viable_middle_exists": False,
                "logical_space_explored": "explicit",
            },
            "causal_analysis": {
                "causes_listed": [],
                "cause_count": 0,
                "alternative_causes_mentioned": False,
                "sufficiency_claim_strength": "absent",
                "temporal_only": False,
                "causal_claim_type": "unknown",
            },
            "temporal_analysis": {"time_references": [], "temporal_order_claimed": False},
            "agent_analysis": {"actors_mentioned": [], "agency_attribution": "self"},
        })

        import mira.system_b.lane2.bridge as mod
        orig_enabled = mod.MIRA_LANE2_ENABLED
        orig_backend = mod.MIRA_LLM_EXTRACT_BACKEND
        mod.MIRA_LANE2_ENABLED = True
        mod.MIRA_LLM_EXTRACT_BACKEND = "openai"

        try:
            with patch.object(mod, "_call_step2_with_retry", return_value=mock_response):
                # learner_text must contain every options_listed item so the
                # _fidelity_check substring-grounding gate passes and Prolog
                # actually runs the reject path; otherwise the verdict is
                # downgraded to "unverified" (error="feature_fidelity") before
                # reject is reached. (4 non-exclusive options → not a dilemma.)
                results = run_lane2_bridge("I could pick A, B, C, or D", ["false_dilemma"])
                assert results["false_dilemma"].verdict == "reject"
        finally:
            mod.MIRA_LANE2_ENABLED = orig_enabled
            mod.MIRA_LLM_EXTRACT_BACKEND = orig_backend

    def test_step2_failure_returns_unverified(self, monkeypatch) -> None:
        import mira.system_b.lane2.bridge as mod
        monkeypatch.setenv("MIRA_ENABLE_LANE3", "1")  # consent opt-in (extraction mocked)
        orig_enabled = mod.MIRA_LANE2_ENABLED
        orig_backend = mod.MIRA_LLM_EXTRACT_BACKEND
        mod.MIRA_LANE2_ENABLED = True
        mod.MIRA_LLM_EXTRACT_BACKEND = "openai"

        try:
            with patch.object(mod, "_call_step2_with_retry", return_value=None):
                results = run_lane2_bridge("text", ["false_dilemma"])
                assert results["false_dilemma"].verdict == "unverified"
                assert results["false_dilemma"].error == "step2_extraction_failed"
        finally:
            mod.MIRA_LANE2_ENABLED = orig_enabled
            mod.MIRA_LLM_EXTRACT_BACKEND = orig_backend

    def test_consent_gate_blocks_external_extraction(self, monkeypatch) -> None:
        """Without MIRA_ENABLE_LANE3=1, Lane 2 makes no external LLM call.

        Guards the consent promise (.env.example / README): all external LLM
        calls — Lane 2 feature extraction included — require the explicit
        opt-in. Supported patterns fall back to "unverified" (no error marker,
        same shape as the no-backend path).
        """
        import mira.system_b.lane2.bridge as mod

        monkeypatch.delenv("MIRA_ENABLE_LANE3", raising=False)
        monkeypatch.setattr(mod, "MIRA_LANE2_ENABLED", True)
        monkeypatch.setattr(mod, "MIRA_LLM_EXTRACT_BACKEND", "openai")
        monkeypatch.setenv("OPENAI_API_KEY", "k")

        with patch.object(mod, "_call_step2_with_retry") as mock_call:
            results = run_lane2_bridge("I must choose A or B", ["false_dilemma"])

        assert mock_call.call_count == 0
        assert results["false_dilemma"].verdict == "unverified"
        assert results["false_dilemma"].error is None
