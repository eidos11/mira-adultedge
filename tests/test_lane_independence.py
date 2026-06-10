"""Tests for Lane Independence Restoration — Task C3 and beyond.

spec: design/2026-06-04-lane-independence-restoration-design.md
"""

from mira.contracts.minimal import PatternCandidate


def test_pattern_candidate_lane3_detected_defaults_false():
    c = PatternCandidate(pattern_id="false_dilemma", canonical_id="PAT-D-02", vtype="D")
    assert c.lane3_detected is False


def test_lane2_status_accepts_unverified():
    c = PatternCandidate(
        pattern_id="false_dilemma", canonical_id="PAT-D-02", vtype="D",
        lane2_status="unverified",
    )
    assert c.lane2_status == "unverified"


def test_supported_patterns_single_source():
    from mira.system_b.lane2 import patterns, bridge, feature_schemas
    assert bridge.SUPPORTED_PATTERNS == patterns.SUPPORTED_PATTERNS
    assert feature_schemas.SUPPORTED_PATTERNS == patterns.SUPPORTED_PATTERNS


def test_pattern_meta_has_registry_values():
    from mira.system_b.lane2 import patterns
    assert patterns.PATTERN_META["false_dilemma"] == ("PAT-D-02", "D")
    assert patterns.PATTERN_META["oversimplified_cause"] == ("PAT-A-02", "A")


def test_prolog_rule_mapping_matches_supported():   # codex B4
    from mira.system_b.lane2 import bridge, patterns
    assert set(bridge._PATTERN_PL) == set(patterns.SUPPORTED_PATTERNS)


def test_merge_injects_missing_supported_pattern():   # codex B1 (routing-independent unit test)
    from mira.system_b.lane2.bridge import BridgeVerdict
    from mira.pipeline import _merge_bridge_verdict_candidates

    out = _merge_bridge_verdict_candidates(
        [], {"false_dilemma": BridgeVerdict(pattern_id="false_dilemma", verdict="accept")})
    assert len(out) == 1 and out[0].pattern_id == "false_dilemma"
    assert out[0].lane2_status == "pass"
    assert (out[0].canonical_id, out[0].vtype) == ("PAT-D-02", "D")


def test_lane2_runs_and_injects_without_lane3(monkeypatch):
    monkeypatch.delenv("MIRA_ENABLE_LANE3", raising=False)

    def fake_bridge(text, pattern_ids):
        assert pattern_ids == sorted({"false_dilemma", "oversimplified_cause"})
        return {pid: BridgeVerdict(pattern_id=pid, verdict="accept") for pid in pattern_ids}

    from mira.system_b.lane2.bridge import BridgeVerdict
    monkeypatch.setattr("mira.pipeline.run_lane2_bridge", fake_bridge)
    from mira.pipeline import diagnose_only
    diag = diagnose_only("Either I study or I fail — there's no other way.", lang="en")
    by_id = {c.pattern_id: c for c in diag.overlay.pattern_candidates}
    assert "false_dilemma" in by_id
    assert by_id["false_dilemma"].lane2_status == "pass"
    assert by_id["false_dilemma"].canonical_id == "PAT-D-02"
    assert by_id["false_dilemma"].vtype == "D"


def test_enrich_sets_lane3_detected():
    from mira.pipeline import _enrich_with_lane3

    base = [PatternCandidate(pattern_id="false_dilemma", canonical_id="PAT-D-02", vtype="D")]
    llm = [{"pattern_id": "false_dilemma", "evidence": ["either/or framing"]}]
    out = {c.pattern_id: c for c in _enrich_with_lane3(base, llm)}
    assert out["false_dilemma"].lane3_detected is True
    # new pattern from LLM also flagged
    llm2 = [{"pattern_id": "sunk_cost", "evidence": ["already invested"]}]
    out2 = {c.pattern_id: c for c in _enrich_with_lane3(base, llm2)}
    assert out2["sunk_cost"].lane3_detected is True


# ── Task C4: report coaching matrix alignment + B2 ──────────────────────────

from mira.report import _lane_source, _action_suggestion
from mira.contracts.minimal import CVVerificationOverlay, PSRResult


def _overlay(cands):
    return CVVerificationOverlay(
        trace_id="t1", request_id="req-t1",
        psr=PSRResult(P_appraisal="p", S_strategy="s", R_projection="r"),
        route_vtype="D", pattern_candidates=cands,
        overlay_status="insufficient_evidence", lane1_pass=True,
        evidence_summary="none",
    )


def test_lane_source_uses_lane3_detected_field():
    c = PatternCandidate(
        pattern_id="false_dilemma", canonical_id="PAT-D-02", vtype="D",
        lane3_detected=True,
    )
    assert _lane_source(c) == "Lane 3 (LLM)"


def test_unverified_gets_suggested_coaching_not_none():
    c = PatternCandidate(
        pattern_id="false_dilemma", canonical_id="PAT-D-02", vtype="D",
        lane2_status="unverified",
    )
    out = _action_suggestion(_overlay([c]), "en")
    assert "false dilemma" in out.lower() or "false_dilemma" in out


def test_primary_pattern_id_selects_unverified():   # codex B2
    from mira.pipeline import _primary_pattern_id
    c = PatternCandidate(
        pattern_id="false_dilemma", canonical_id="PAT-D-02", vtype="D",
        lane2_status="unverified",
    )
    assert _primary_pattern_id(_overlay([c])) == "false_dilemma"


# ── Task C3: lane3_detected round-trip ────────────────────────────────────────

def test_lane3_detected_survives_candidate_roundtrip():
    c = PatternCandidate(
        pattern_id="false_dilemma", canonical_id="PAT-D-02", vtype="D",
        lane3_detected=True,
    )
    restored = PatternCandidate(**c.model_dump())
    assert restored.lane3_detected is True


def test_lane3_detected_survives_skill_json():   # codex B3 — real hand-rolled path
    from mira.__main__ import build_json_output
    ov = _overlay([PatternCandidate(
        pattern_id="false_dilemma", canonical_id="PAT-D-02", vtype="D",
        lane2_status="pass", lane3_detected=True)])
    data = build_json_output(ov, "report", "input")
    assert data["patterns"][0]["lane3_detected"] is True
    import importlib.util, pathlib
    spec = importlib.util.spec_from_file_location(
        "ingest", pathlib.Path("skills/mira-report/scripts/ingest.py"))
    ingest = importlib.util.module_from_spec(spec); spec.loader.exec_module(ingest)
    assert ingest._rebuild_overlay(data).pattern_candidates[0].lane3_detected is True


def test_isolation_symmetric_verdict(monkeypatch):   # codex B6
    """Lane 3 evidence must NOT change Lane 2 verdict (real evidence flows in on ON)."""
    from mira.system_b.lane2.bridge import BridgeVerdict
    from mira.pipeline import diagnose_only
    seen = []
    def fake_bridge(text, pattern_ids):
        seen.append(tuple(pattern_ids))
        return {pid: BridgeVerdict(pattern_id=pid, verdict="accept") for pid in pattern_ids}
    monkeypatch.setattr("mira.pipeline.run_lane2_bridge", fake_bridge)
    claim = "Either I study or I fail."

    monkeypatch.delenv("MIRA_ENABLE_LANE3", raising=False)
    monkeypatch.setattr("mira.pipeline.extract_pattern_candidates", lambda *a, **k: [])
    off = {c.pattern_id: c.lane2_status for c in diagnose_only(claim, lang="en").overlay.pattern_candidates}

    monkeypatch.setenv("MIRA_ENABLE_LANE3", "1")
    monkeypatch.setattr("mira.pipeline.extract_pattern_candidates",
                        lambda *a, **k: [{"pattern_id": "false_dilemma", "evidence": ["either/or"]}])
    on = {c.pattern_id: c.lane2_status for c in diagnose_only(claim, lang="en").overlay.pattern_candidates}

    for pid in ("false_dilemma", "oversimplified_cause"):
        assert off.get(pid) == on.get(pid)
    assert all(ids == tuple(sorted({"false_dilemma", "oversimplified_cause"})) for ids in seen)


def test_feature_fidelity_downgrades_hallucinated_quote():   # codex/domain F3
    from mira.system_b.lane2 import bridge
    extracted = {"options_analysis": {
        "options_listed": ["a fabricated option not in text"],
        "option_count": 2,
        "exclusivity_markers": ["either...or"],
        "middle_options_mentioned": False,
        "viable_middle_exists": False,
        "logical_space_explored": "explicit",
    }}
    verdict = bridge._fidelity_check("Either I study or I fail.", "false_dilemma", extracted)
    assert verdict == "unverified"


def test_backend_resolved_at_call_time(monkeypatch):   # codex B5
    from mira.system_b.lane2 import bridge
    monkeypatch.setenv("MIRA_LLM_EXTRACT_BACKEND", "none")
    assert bridge._resolve_extract_backend()[0] == "none"


# ── Task 2: remove detect_structural_leak (coaching gate redesign D1/D4) ────

def test_pipeline_no_longer_imports_detect_structural_leak():
    """Task 2 effective check: source-level assertion that the removed fn is gone."""
    import inspect
    import mira.pipeline as P
    src = inspect.getsource(P)
    assert "detect_structural_leak" not in src, (
        "detect_structural_leak call/import remains in pipeline.py"
    )


def test_coach_from_overlay_no_structural_leak_dependency(monkeypatch):
    """Willpower-candidate presence must NOT change coaching path (no structural_leak gate).

    Two overlays — one WITH willpower_blame candidate, one WITHOUT — must
    produce the same coaching outcome (both coaching or both fallback).
    """
    from mira.pipeline import coach_from_overlay, DiagnoseResult
    from mira.contracts.minimal import CVVerificationOverlay, PSRResult, SystemAtoCVRequest

    # Minimal DiagnoseResult factory
    def _make_diag(cands):
        ov = CVVerificationOverlay(
            trace_id="t-task2", request_id="req-task2",
            psr=PSRResult(P_appraisal="p", S_strategy="s", R_projection="r"),
            route_vtype="D", pattern_candidates=cands,
            overlay_status="insufficient_evidence", lane1_pass=True,
            evidence_summary="none",
        )
        req = SystemAtoCVRequest(
            trace_id="t-task2",
            learner_claim="Either I study or I fail.",
            claim_language="en",
        )
        return DiagnoseResult(request=req, overlay=ov)

    without_wb = _make_diag([
        PatternCandidate(pattern_id="false_dilemma", canonical_id="PAT-D-02", vtype="D"),
    ])
    with_wb = _make_diag([
        PatternCandidate(pattern_id="false_dilemma", canonical_id="PAT-D-02", vtype="D"),
        PatternCandidate(pattern_id="willpower_blame", canonical_id="PAT-W-01", vtype="I"),
    ])

    # Stub run_reduced_critic so both calls pass (we only test routing, not checks).
    # Use the real contract_critic to build a valid AuditResult stub.
    from mira.system_b.engine.critic.contract import contract_critic, LaneOneInput, PSRDecomposition
    _stub_input = LaneOneInput(
        psr=PSRDecomposition(
            P_appraisal="p", P_latitude="medium",
            claim_type="argument",
            S_strategy="s", S_exclusivity="open",
            R_projection="r", R_emotional_load="neutral",
        ),
        pattern_ids=["false_dilemma"],
        primary_route="D",
        vtype_claimed="D",
        response_text="구조적 원인을 점검합니다.",
        trace_id="stub",
    )
    _stub_audit = contract_critic(_stub_input)
    monkeypatch.setattr(
        "mira.pipeline.run_reduced_critic",
        lambda *a, **kw: (True, _stub_audit),
    )

    result_without = coach_from_overlay(without_wb)
    result_with = coach_from_overlay(with_wb)

    # Both must produce a non-fallback report (coaching path, same branch).
    # CoachResult is a TypedDict (plain dict), so use dict access.
    from mira.pipeline import safe_fallback_report
    fallback_en = safe_fallback_report("en")
    assert result_without["overlay"].lane1_pass is True
    assert result_with["overlay"].lane1_pass is True
    # The presence of willpower_blame must not force fallback
    assert result_with["report"] != fallback_en, (
        "willpower_blame candidate forced fallback — structural_leak gate still active"
    )
