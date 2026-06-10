
"""M1 minimal A→B→A pipeline orchestration.

Full loop: learner claim → request → PSR → route → match → overlay → report.
Reference: M1-minimal-spec.md, Architecture v4.3.

Seam entry points (Tasks 2-7 build on these):
  diagnose_only()      — stages 1-3: diagnosis + overlay, no coaching.
  coach_from_overlay() — stage 4: full report + structured coaching dict.
  run_minimal_loop()   — composes both; public contract unchanged.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, TypedDict, cast

import mira.contracts.minimal as minimal
from mira.psr import decompose_psr, route_vtype
from mira.report import REPORT_BLOCK_SEPARATOR, safe_fallback_report, generate_report
from mira.system_a import DiagnosticEngine
from mira.system_a.coaching.coaching import get_available_patterns
from mira.system_a.engine.diagnostic_engine import ContextType
from mira.system_a.engine.axis_task_definition import reframe_text
from mira.system_a.types import DiagnosticSnapshot
from mira.system_b.engine.critic.adapter import run_reduced_critic
from mira.system_b.engine.matcher import match_patterns
from mira.system_b.lane2.bridge import run_lane2_bridge
from mira.system_b.lane2.patterns import PATTERN_META, SUPPORTED_PATTERNS
from mira.system_b.lane3.llm_extractor import extract_pattern_candidates


@dataclass(frozen=True)
class PipelineResult:
    request: minimal.SystemAtoCVRequest
    overlay: minimal.CVVerificationOverlay
    report: str
    diagnostic_snapshot: DiagnosticSnapshot | None = None


@dataclass(frozen=True)
class DiagnoseResult:
    """Stages 1-3 result: request + overlay (no coaching, no report).

    CVVerificationOverlay uses extra="forbid", so coaching cannot live there.
    coach_from_overlay() returns a plain dict with 'coaching' at the top level.
    """

    request: minimal.SystemAtoCVRequest
    overlay: minimal.CVVerificationOverlay
    diagnostic_snapshot: DiagnosticSnapshot | None = None


class Coaching(TypedDict):
    """Structured coaching object returned by coach_from_overlay.

    block       — the coaching text extracted from the report (from
                  _extract_coaching_from_report).
    pattern_id  — the primary pattern this coaching addresses (first pass
                  candidate from overlay.pattern_candidates; first evidenced
                  candidate if none passed; None if no candidates match).
    note        — out-of-scope marker; str or None. Disambiguate with pattern_id:
                    • note=None, pattern_id set    → supported pattern, coaching
                      provided in block (normal case).
                    • note=None, pattern_id=None   → NO pattern was evidenced
                      ("no clear match"); block carries the no-match guidance.
                      This is NOT an out-of-scope skip.
                    • note set,  pattern_id set    → a pattern WAS resolved but
                      has no coaching template; note reads
                      "out of v0.x scope: pattern '<id>' has no coaching template"
                      (Task 5 honesty rule: ZERO silent skip).
                  Consumers (Task 6 render, Task 7) must read pattern_id to tell
                  the two note=None cases apart — note alone is ambiguous.

    SYNC: this is an intentional manual mirror of ingest.CoachingDict (kept in
    sync by hand to avoid a skill→pipeline import). If coaching grows fields,
    Task 5 should consider promoting both to a shared type (e.g. mira/types.py).
    """

    block: str
    pattern_id: str | None
    note: str | None


class CoachResult(TypedDict):
    """Return shape of coach_from_overlay (stage 4 output).

    coaching lives here at the dict top level, NOT on the overlay, because
    CVVerificationOverlay uses extra="forbid".
    """

    overlay: minimal.CVVerificationOverlay
    report: str
    coaching: Coaching
    request: minimal.SystemAtoCVRequest
    diagnostic_snapshot: DiagnosticSnapshot | None


def diagnose_only(
    learner_claim: str,
    *,
    lang: str = "en",
    claim_domain: str = "adult_learning",
    trace_id: str | None = None,
    context_type: str = "adult_learning",
) -> DiagnoseResult:
    """Run stages 1-3 only: engine.diagnose → _system_b_verify → overlay.

    Returns a DiagnoseResult with request, overlay, and diagnostic_snapshot.
    No coaching is performed; no report string is generated.
    Immutable: always returns a new DiagnoseResult object.
    """
    tid = trace_id or f"v1-{uuid.uuid4().hex[:12]}"

    engine = DiagnosticEngine()
    snapshot = engine.diagnose(
        learner_claim,
        trace_id=tid,
        context_type=_coerce_context_type(context_type),
    )

    minimal_request = minimal.SystemAtoCVRequest(
        trace_id=tid,
        learner_claim=learner_claim,
        claim_domain=claim_domain,
        claim_language=lang,
        psr_prior=_psr_prior_from_snapshot(snapshot, lang),
    )

    stage = snapshot.diagnostic_hypothesis.stage_estimate
    overlay = _system_b_verify(minimal_request, stage_estimate=stage)

    return DiagnoseResult(
        request=minimal_request,
        overlay=overlay,
        diagnostic_snapshot=snapshot,
    )


def coach_from_overlay(
    diag: DiagnoseResult,
    *,
    lang: str | None = None,
) -> CoachResult:
    """Run stage 4 on a DiagnoseResult: generate report + structured coaching.

    Returns a plain dict (not a dataclass) so 'coaching' can exist at the
    top level without touching the extra="forbid" CVVerificationOverlay.

    Keys returned:
      overlay     — same overlay object from diag (possibly updated for lane1_pass)
      report      — full report string (str)
      coaching    — structured Coaching dict with block/pattern_id/note keys
      request     — original request object from diag
      diagnostic_snapshot — original snapshot from diag

    coaching sub-fields:
      block       — coaching text extracted from the report
      pattern_id  — primary pattern addressed (first pass candidate; first
                    evidenced candidate if none passed; None otherwise)
      note        — None when coaching was provided (pattern_id set) OR when no
                    pattern was evidenced (pattern_id None — "no clear match");
                    "out of v0.x scope: pattern '<id>' has no coaching template"
                    only when a pattern was resolved but has no template (Task 5
                    honesty rule: ZERO silent skip). See Coaching TypedDict for
                    the full pattern_id-vs-note disambiguation table.

    Immutability: diag and its overlay are never mutated; new objects are returned.
    """
    effective_lang = lang if lang is not None else diag.request.claim_language
    learner_claim = diag.request.learner_claim
    overlay = diag.overlay

    report = generate_report(overlay, learner_claim, lang=effective_lang)

    lane1_pass, _audit = run_reduced_critic(
        overlay.psr, overlay.pattern_candidates, overlay.route_vtype,
        response_text=report,
        trace_id=overlay.trace_id,
    )

    if not lane1_pass:
        report = safe_fallback_report(effective_lang)

    # model_copy returns a new object — overlay is never mutated
    updated_overlay = overlay.model_copy(update={"lane1_pass": lane1_pass})

    # Extract coaching section from the report string for the structured key.
    # Coaching is embedded in the report (Task 0 fact #1); we surface it as a
    # separate dict key so callers don't need to parse the report string.
    coaching_block = _extract_coaching_from_report(report)
    primary_pid = _primary_pattern_id(updated_overlay)

    # Honest-skip logic (Task 5, §5): if the primary pattern has no coaching
    # template, set an explicit note — NEVER silently skip.
    # Only fires when primary_pid is a real pattern ID (not None); a None
    # primary_pid means no pattern was resolved at all (not an unsupported-
    # pattern case), so note stays None in that branch.
    coaching_note: str | None = None
    if primary_pid is not None and primary_pid not in get_available_patterns():
        coaching_note = (
            f"out of v0.x scope: pattern '{primary_pid}' has no coaching template"
        )

    coaching: Coaching = {
        "block": coaching_block,
        "pattern_id": primary_pid,
        "note": coaching_note,
    }

    return {
        "overlay": updated_overlay,
        "report": report,
        "coaching": coaching,
        "request": diag.request,
        "diagnostic_snapshot": diag.diagnostic_snapshot,
    }


def run_minimal_loop(
    learner_claim: str,
    *,
    claim_domain: str = "adult_learning",
    claim_language: str = "en",
    trace_id: str | None = None,
    context_type: str = "adult_learning",
) -> PipelineResult:
    """Execute the full M1 A→B→A minimal viable loop.

    Composes diagnose_only() + coach_from_overlay(). Public contract unchanged:
    returns PipelineResult with the same four fields as before.

    The ``claim_language`` argument is the legacy public name; it is forwarded
    internally as ``lang`` to diagnose_only()/coach_from_overlay() (the name is
    kept for backward compatibility with existing callers).
    """
    diag = diagnose_only(
        learner_claim,
        lang=claim_language,
        claim_domain=claim_domain,
        trace_id=trace_id,
        context_type=context_type,
    )
    coached = coach_from_overlay(diag, lang=claim_language)

    return PipelineResult(
        request=coached["request"],
        overlay=coached["overlay"],
        report=coached["report"],
        diagnostic_snapshot=coached["diagnostic_snapshot"],
    )


def _primary_pattern_id(overlay: minimal.CVVerificationOverlay) -> str | None:
    """Resolve the primary pattern_id addressed by the coaching block.

    Priority:
      1. First candidate whose lane2_status == "pass" (Prolog-verified).
      2. First candidate whose lane2_status == "unverified" (structured coaching).
      3. First candidate with non-empty evidence_trace (LLM/rule-evidenced).
      4. None — no resolvable pattern.

    Note on single-id vs multi-block divergence: when multiple patterns produce
    coaching text in the report block (report._action_suggestion iterates all
    verified/evidenced/unverified candidates), this returns ONLY the primary
    one — the first pass candidate, else the first unverified, else the first
    evidenced. So coaching["block"] may address several patterns while
    coaching["pattern_id"] names just the primary. This is intentional:
    pattern_id is a single machine-readable anchor, not an exhaustive list.

    Immutable: reads overlay only; never mutates.
    """
    candidates = overlay.pattern_candidates
    # Priority 1: verified pass
    for c in candidates:
        if c.lane2_status == "pass":
            return c.pattern_id
    # Priority 2: unverified (structured coaching, suggested tone)
    for c in candidates:
        if c.lane2_status == "unverified":
            return c.pattern_id
    # Priority 3: evidenced (not_run but has trace)
    for c in candidates:
        if c.evidence_trace:
            return c.pattern_id
    return None


def _extract_coaching_from_report(report: str) -> str:
    """Extract the coaching section text from a generated report string.

    The coaching block is the last block after the report's block separator
    (generate_report joins 4 blocks with REPORT_BLOCK_SEPARATOR).
    Falls back to the full report if the separator is not found (e.g. safe
    fallback report).
    """
    if REPORT_BLOCK_SEPARATOR in report:
        return report.split(REPORT_BLOCK_SEPARATOR)[-1]
    return report


def _coerce_context_type(context_type: str) -> ContextType:
    if context_type in ("adult_learning", "governance", "decision"):
        return cast(ContextType, context_type)
    return "adult_learning"


def _psr_prior_from_snapshot(snapshot: DiagnosticSnapshot, lang: str = "en") -> minimal.PSRPrior:
    hyp = snapshot.diagnostic_hypothesis
    confidence = snapshot.confidence_band

    if hyp.primary_leaks:
        p_appraisal = f"{confidence} metacognitive confidence with cues: {', '.join(hyp.primary_leaks)}"
    else:
        p_appraisal = f"{confidence} metacognitive confidence with no named leak"

    if hyp.goal_reframed:
        s_strategy = (
            f"{snapshot.system_a_cues.possible_claim_type}; "
            f"suggested action frame: {reframe_text(hyp.goal_reframed, lang)}"
        )
    elif hyp.weakest_force:
        s_strategy = f"weakest force: {hyp.weakest_force}"
    else:
        s_strategy = snapshot.system_a_cues.possible_claim_type

    return minimal.PSRPrior(
        P_appraisal=p_appraisal,
        S_strategy=s_strategy,
        R_projection=hyp.stage_estimate,
    )


def _system_b_verify(
    request: minimal.SystemAtoCVRequest,
    stage_estimate: str = "concept",
) -> minimal.CVVerificationOverlay:
    psr = decompose_psr(request.learner_claim, request.psr_prior)
    vtype = route_vtype(request.learner_claim, request.psr_prior)
    candidates = match_patterns(psr, vtype)

    llm_candidates = extract_pattern_candidates(
        request.learner_claim,
        stage_estimate=stage_estimate,
        lang=request.claim_language,
    )
    candidates = _enrich_with_lane3(candidates, llm_candidates)

    # Lane 2 is independent of Lane 3 (C1): always verify the supported set.
    bridge_results = run_lane2_bridge(
        request.learner_claim, sorted(SUPPORTED_PATTERNS)
    )
    candidates = _merge_bridge_verdict_candidates(candidates, bridge_results)

    lane2_results = {}
    for c in candidates:
        if c.lane2_result:
            lane2_results[c.pattern_id] = c.lane2_result

    has_accept = any(c.lane2_status == "pass" for c in candidates)
    has_reject = any(c.lane2_status == "fail" for c in candidates)
    if has_accept:
        status = "verified"
    elif has_reject:
        status = "structural_mismatch"
    else:
        status = "insufficient_evidence"

    evidence_parts = []
    for c in candidates:
        if c.evidence_trace:
            evidence_parts.append(f"{c.pattern_id}: {', '.join(c.evidence_trace)}")
    evidence_summary = "; ".join(evidence_parts) if evidence_parts else "no evidence collected"

    return minimal.CVVerificationOverlay(
        trace_id=request.trace_id,
        request_id=f"req-{request.trace_id}",
        psr=psr,
        route_vtype=vtype,
        pattern_candidates=candidates,
        overlay_status=status,
        lane1_pass=True,
        lane2_results=lane2_results,
        evidence_summary=evidence_summary,
        avoid_willpower_blame=True,
    )


def _merge_bridge_verdict_candidates(
    candidates: list[minimal.PatternCandidate],
    bridge_results: dict,
) -> list[minimal.PatternCandidate]:
    """Apply Lane 2 verdicts to existing candidates and inject verdicts for
    supported patterns that matcher (Lane 1) did not surface (C1).

    Immutable: returns a new list of new PatternCandidate objects.
    """
    if not bridge_results:
        return candidates

    _verdict_to_status = {"accept": "pass", "reject": "fail", "unverified": "unverified"}

    def _apply(c: minimal.PatternCandidate, bv) -> minimal.PatternCandidate:
        lane2_status = _verdict_to_status.get(bv.verdict, "not_run")
        lane2_result = {"bridge_verdict": bv.verdict}
        if bv.features:
            lane2_result["features"] = bv.features
        if bv.error:
            lane2_result["error"] = bv.error
        return minimal.PatternCandidate(
            pattern_id=c.pattern_id,
            canonical_id=c.canonical_id,
            vtype=c.vtype,
            lane2_status=lane2_status,
            lane2_result=lane2_result,
            evidence_trace=c.evidence_trace,
            lane3_detected=c.lane3_detected,
        )

    seen = {c.pattern_id for c in candidates}
    updated = [
        _apply(c, bridge_results[c.pattern_id]) if c.pattern_id in bridge_results else c
        for c in candidates
    ]

    # Inject supported patterns that produced a verdict but were not candidates.
    for pid, bv in bridge_results.items():
        if pid in seen:
            continue
        canonical_id, vtype = PATTERN_META.get(pid, (pid, "I"))
        status = _verdict_to_status.get(bv.verdict, "not_run")
        lane2_result = {"bridge_verdict": bv.verdict}
        if bv.features:
            lane2_result["features"] = bv.features
        if bv.error:
            lane2_result["error"] = bv.error
        updated.append(
            minimal.PatternCandidate(
                pattern_id=pid,
                canonical_id=canonical_id,
                vtype=vtype,
                lane2_status=status,
                lane2_result=lane2_result,
            )
        )
    return updated


def _enrich_with_lane3(
    candidates: list[minimal.PatternCandidate],
    llm_candidates: list[dict[str, Any]],
) -> list[minimal.PatternCandidate]:
    """Merge Lane 3 LLM suggestions into existing candidates.

    LLM evidence enriches existing candidates' evidence_trace.
    New patterns from LLM are added as not_run (Lane 1 rules must confirm).
    """
    if not llm_candidates:
        return candidates

    existing_ids = {c.pattern_id for c in candidates}
    enriched = list(candidates)

    for llm_item in llm_candidates:
        pid = llm_item.get("pattern_id", "")
        evidence = llm_item.get("evidence", [])

        if pid in existing_ids:
            enriched = [
                minimal.PatternCandidate(
                    pattern_id=c.pattern_id,
                    canonical_id=c.canonical_id,
                    vtype=c.vtype,
                    lane2_status=c.lane2_status,
                    lane2_result=c.lane2_result,
                    evidence_trace=c.evidence_trace + [f"[L3] {e}" for e in evidence],
                    lane3_detected=True,
                )
                if c.pattern_id == pid
                else c
                for c in enriched
            ]
        else:
            enriched.append(
                minimal.PatternCandidate(
                    pattern_id=pid,
                    canonical_id=pid,
                    vtype="I",
                    lane2_status="not_run",
                    evidence_trace=[f"[L3] {e}" for e in evidence],
                    lane3_detected=True,
                )
            )
            existing_ids.add(pid)  # codex F7/F1: avoid duplicate candidate on repeated LLM PID

    return enriched
