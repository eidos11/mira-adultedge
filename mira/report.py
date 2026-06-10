"""Learner-facing report generation.

M1: 4-block report — diagnostic summary, evidence, limitations, action suggestion.
Boundary: no verdict language, no willpower blame, learner agency preserved.
"""

from __future__ import annotations

import re

from mira.contracts.minimal import CVVerificationOverlay, PatternCandidate
from mira.contracts.safety_patterns import VERDICT_LANGUAGE_RE, WILLPOWER_BLAME_RE
from mira.system_a.coaching.coaching import generate_coaching_block

_STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "summary_h": "## Diagnostic Summary",
        "evidence_h": "## Evidence",
        "limitations_h": "## Limitations",
        "coaching_h": "## Coaching",
        "psr_h": "**PSR Decomposition:**",
        "premise": "Premise (P)",
        "strategy": "Strategy (S)",
        "result": "Result (R)",
        "vtype_D": "deductive",
        "vtype_I": "inductive",
        "vtype_A": "abductive",
        "detected": "During {vt} verification, patterns matching '{names}' were observed.",
        "not_detected": "{vt} verification was performed, but no clear match was found among currently executable patterns. Any coaching below addresses unverified candidates and is explicitly marked tentative.",
        "evidence_for": "evidence for",
        "lim_prolog": "Of {total} patterns, only {executed} underwent Prolog verification.",
        "lim_ai": "This analysis is an AI-assisted tool; final judgment rests with the learner.",
        "lim_tentative": "Identified patterns represent tentative matches based on available evidence.",
        "coach_fallback": "This pattern was observed. Providing more specific context would enable tailored coaching.",
        "coach_needs_review": "Some pattern-related signals were found, but evidence is insufficient. Providing more specific situations or examples would improve analysis precision.",
        "coach_none": "No clear match was found among currently executable patterns. Consider reviewing your learning strategy, or describe your situation in more detail.",
        "coach_reject": (
            "This text was analyzed for potential reasoning patterns. While some initial "
            "signals were detected, structural verification found that the evidence does "
            "not sufficiently support a specific pattern match.\n\n"
            "This may mean:\n"
            "- Your reasoning has more nuance than a simple pattern classification captures\n"
            "- Additional context would help — try describing your situation in more detail\n"
            "- You might benefit from reviewing the self-check questions in our pattern guide\n\n"
            "If you'd like a more thorough analysis, consider providing specific examples "
            "of the decision or situation you're reflecting on."
        ),
        "safe_h": "## Analysis Result",
        "safe_body": "A structural analysis was performed on the provided text, but a safe report could not be generated within the current scope.",
        "safe_lim_h": "## Limitations",
        "safe_note1": "This analysis is an AI-assisted tool; final judgment rests with the learner.",
        "safe_note2": "Providing more detailed learning context may improve analysis quality.",
    },
    "ko": {
        "summary_h": "## 진단 요약",
        "evidence_h": "## 근거",
        "limitations_h": "## 제한사항",
        "coaching_h": "## 코칭",
        "psr_h": "**PSR 분해 결과:**",
        "premise": "전제(P)",
        "strategy": "전략(S)",
        "result": "결과(R)",
        "vtype_D": "연역적",
        "vtype_I": "귀납적",
        "vtype_A": "귀추적",
        "detected": "분석 결과, {vt} 검증 과정에서 '{names}'와 일치하는 패턴이 관찰되었습니다.",
        "not_detected": "{vt} 검증을 수행했으나, 현재 실행 가능한 패턴에서는 뚜렷한 일치가 관찰되지 않았습니다. 아래 코칭이 있다면 이는 미검증 후보에 대한 것이며 잠정 표시와 함께 제공됩니다.",
        "evidence_for": "관련 근거",
        "lim_prolog": "현재 {total}개 패턴 중 {executed}개만 Prolog 검증이 실행되었습니다.",
        "lim_ai": "이 분석은 AI 보조 도구이며, 최종 판단은 학습자 본인에게 있습니다.",
        "lim_tentative": "제시된 패턴은 '~와 일치하는 근거'이며, 잠정적 분석 결과입니다.",
        "coach_fallback": "해당 패턴이 관찰되었습니다. 구체적인 상황을 더 자세히 기술하면 맞춤형 코칭을 제공할 수 있습니다.",
        "coach_needs_review": "일부 패턴과 관련된 신호가 있으나 근거가 충분하지 않습니다. 구체적인 상황이나 사례를 더 자세히 기술하면 분석 정밀도가 향상될 수 있습니다.",
        "coach_none": "현재 실행 가능한 패턴에서 뚜렷한 일치가 관찰되지 않았습니다. 학습 전략을 점검하거나, 구체적 상황을 더 자세히 기술해 보세요.",
        "coach_reject": (
            "제공하신 텍스트에서 일부 추론 패턴 신호가 감지되었으나, 구조적 검증 결과 "
            "특정 패턴에 대한 근거가 충분하지 않았습니다.\n\n"
            "이는 다음을 의미할 수 있습니다:\n"
            "- 단순한 패턴 분류보다 더 섬세한 추론을 하고 계십니다\n"
            "- 추가적인 맥락이 도움이 될 수 있습니다 — 상황을 더 자세히 기술해 보세요\n"
            "- 패턴 가이드의 자기 점검 질문을 활용해 볼 수 있습니다\n\n"
            "보다 심층적인 분석을 원하시면, 고민 중인 결정이나 상황에 대한 "
            "구체적 사례를 제공해 주세요."
        ),
        "safe_h": "## 분석 결과",
        "safe_body": "입력된 내용에 대한 구조적 분석을 수행했으나, 현재 제공 가능한 범위 내에서 안전한 보고서를 생성할 수 없었습니다.",
        "safe_lim_h": "## 제한사항",
        "safe_note1": "이 분석은 AI 보조 도구이며, 최종 판단은 학습자 본인에게 있습니다.",
        "safe_note2": "구체적인 학습 상황을 더 자세히 기술하면 분석 품질이 향상될 수 있습니다.",
    },
}


def _s(lang: str) -> dict[str, str]:
    return _STRINGS.get(lang, _STRINGS["en"])


# Separator joining the report's 4 blocks (diagnostic / evidence / limitations
# / coaching). Shared with pipeline._extract_coaching_from_report so the
# coaching-extraction split stays in lockstep with the report format.
REPORT_BLOCK_SEPARATOR = "\n\n---\n\n"


def safe_fallback_report(lang: str = "en") -> str:
    s = _s(lang)
    return (
        f"{s['safe_h']}\n\n{s['safe_body']}\n\n"
        f"{s['safe_lim_h']}\n\n- {s['safe_note1']}\n- {s['safe_note2']}"
    )


_SAFE_FALLBACK_REPORT = safe_fallback_report("en")


def generate_report(
    overlay: CVVerificationOverlay,
    learner_claim: str,
    *,
    lang: str = "en",
) -> str:
    diagnostic = _diagnostic_summary(overlay, lang)
    evidence = _evidence_block(overlay, lang)
    limitations = _limitations_block(overlay, lang)
    coaching = _action_suggestion(overlay, lang)

    system_text = REPORT_BLOCK_SEPARATOR.join([diagnostic, limitations])
    violation = _check_report_violations(system_text)
    if violation:
        return safe_fallback_report(lang)

    report = REPORT_BLOCK_SEPARATOR.join([diagnostic, evidence, limitations, coaching])
    # spec D1/CX-3: coaching-level verdict-language gate removed — tentative coaching does
    # not emit verdict language, so this gate was redundant. system_text willpower blocking
    # stays above (_check_report_violations); the Lane-1 no-verdict invariant (check #7)
    # still guards the rendered report via coach_from_overlay.
    return report


def _diagnostic_summary(overlay: CVVerificationOverlay, lang: str) -> str:
    s = _s(lang)
    vtype_label = {"D": s["vtype_D"], "I": s["vtype_I"], "A": s["vtype_A"]}
    vt = vtype_label.get(overlay.route_vtype, overlay.route_vtype)

    detected = [c for c in overlay.pattern_candidates if c.lane2_status == "pass"]
    if detected:
        names = ", ".join(c.pattern_id.replace("_", " ") for c in detected)
        summary = s["detected"].format(vt=vt, names=names)
    else:
        summary = s["not_detected"].format(vt=vt)

    return f"{s['summary_h']}\n\n{summary}"


def _evidence_block(overlay: CVVerificationOverlay, lang: str) -> str:
    s = _s(lang)
    lines = [s["evidence_h"]]
    lines.append(f"\n{s['psr_h']}")
    lines.append(f"- {s['premise']}: {overlay.psr.P_appraisal}")
    lines.append(f"- {s['strategy']}: {overlay.psr.S_strategy}")
    lines.append(f"- {s['result']}: {overlay.psr.R_projection}")

    for c in overlay.pattern_candidates:
        if c.evidence_trace:
            traces = ", ".join(c.evidence_trace)
            lines.append(f"\n**{c.pattern_id}** {s['evidence_for']}: {traces}")

    return "\n".join(lines)


def _limitations_block(overlay: CVVerificationOverlay, lang: str) -> str:
    s = _s(lang)
    total = len(overlay.pattern_candidates)
    executed = sum(1 for c in overlay.pattern_candidates if c.lane2_status != "not_run")
    return (
        f"{s['limitations_h']}\n\n"
        f"- {s['lim_prolog'].format(total=total, executed=executed)}\n"
        f"- {s['lim_ai']}\n"
        f"- {s['lim_tentative']}"
    )


def _action_suggestion(overlay: CVVerificationOverlay, lang: str) -> str:
    s = _s(lang)
    sections = [f"{s['coaching_h']}\n"]

    verified = [c for c in overlay.pattern_candidates if c.lane2_status == "pass"]
    # rejected (lane2_status == "fail") -> SILENCE: produce no coaching output (spec §4 / CX-4)
    evidenced = [
        c for c in overlay.pattern_candidates
        if c.lane2_status not in ("pass", "fail") and c.evidence_trace
    ]
    unverified = [
        c for c in overlay.pattern_candidates
        if c.lane2_status == "unverified" and c not in evidenced
    ]
    # CX-2 + CX-5: merge evidenced + unverified into ONE tentative set; deterministic
    # sort (evidence-rich first, then pattern_id alphabetical).
    # P1-b: the cap bounds EMITTED coaching blocks (3), NOT candidates scanned. Slicing
    # the candidate list to [:3] BEFORE template resolution could starve all coaching when
    # the evidence-richest candidates lack templates — spec §4 wants 1-3 ACTUAL blocks, so
    # template-missing candidates must not consume a cap slot.
    tentative_pool = sorted(
        evidenced + unverified,
        key=lambda c: (-len(c.evidence_trace or []), c.pattern_id),
    )

    if verified:
        for c in verified:
            coaching = generate_coaching_block(c.pattern_id, lang=lang)
            if coaching:
                sections.append(coaching)
            else:
                # verified = confirmed pattern; a minimal acknowledgement fallback is OK
                sections.append(
                    f"- **{c.pattern_id.replace('_', ' ')}**: {s['coach_fallback']}"
                )

    tentative_emitted = 0
    for c in tentative_pool:
        if tentative_emitted >= 3:
            break
        coaching = generate_coaching_block(c.pattern_id, lang=lang, tentative=True)
        if coaching:
            sections.append(coaching)
            tentative_emitted += 1
        # template-missing -> SKIP (no assertive fallback for unverified patterns; spec §4);
        # does NOT consume a cap slot, so an available template lower in the order surfaces.

    if not verified and tentative_emitted == 0:
        if overlay.overlay_status in ("needs_review", "structural_mismatch"):
            sections.append(s["coach_needs_review"])
        else:
            sections.append(s["coach_none"])

    return "\n".join(sections)


_PATTERN_ID_DISPLAY = re.compile(
    r"\*\*[\w ]+\*\*"
    r"|"
    r"'[\w ]+'"
)


def _check_report_violations(report: str) -> str | None:
    if VERDICT_LANGUAGE_RE.search(report):
        return "forbidden_verdict_language"
    narrative = _PATTERN_ID_DISPLAY.sub("", report)
    if WILLPOWER_BLAME_RE.search(narrative):
        return "willpower_blame_language"
    return None


# ── Expert report (① --format report) ────────────────────────────────
# Output-layer only: internal diagnosis logic unchanged. lane2_status is
# surfaced as a visible badge to make verification level transparent (F5).

# Single source of truth for the diagnostic-JSON contract version.
# 0.2.2: --format json gained a top-level route_vtype so the report skill (②)
# can rebuild the overlay and reuse render_report_markdown (expert mode, DRY).
SCHEMA_VERSION = "0.2.2"
_REPORT_SCHEMA_VERSION = SCHEMA_VERSION


def verdict_state(candidate: PatternCandidate) -> str:
    """Verdict 판정 SSOT — lane2_status / evidence_trace → 상태값.

    expert md badge(``_lane2_badge``)와 html 렌더(② skill)가 공유한다.
    판정 규칙이 한 곳에만 있어야 두 출력 경로가 어긋나지 않는다.
    """
    if candidate.lane2_status == "pass":
        return "verified"
    if candidate.lane2_status == "fail":
        return "rejected"
    if candidate.lane2_status == "unverified":
        return "unverified"
    if candidate.evidence_trace:
        return "evidence_assisted"
    return "unverified"


_VERDICT_BADGE = {
    "verified": "✅ verified",
    "rejected": "✗ rejected",
    "evidence_assisted": "🟡 evidence-assisted",
    "unverified": "○ unverified",
}


def _lane2_badge(candidate: PatternCandidate) -> str:
    return _VERDICT_BADGE[verdict_state(candidate)]


def _lane_source(candidate: PatternCandidate) -> str:
    if candidate.lane2_status in ("pass", "fail", "unverified"):
        return "Lane 2 (Prolog)"
    if candidate.lane3_detected:
        return "Lane 3 (LLM)"
    if candidate.evidence_trace:
        return "Lane 1 (rule)"
    return "—"


def _diagnosis_summary_expert(overlay: CVVerificationOverlay, lang: str) -> str:
    s = _s(lang)
    vtype_label = {"D": s["vtype_D"], "I": s["vtype_I"], "A": s["vtype_A"]}
    vt = vtype_label.get(overlay.route_vtype, overlay.route_vtype)
    detected = [c for c in overlay.pattern_candidates if c.lane2_status == "pass"]
    lines = ["## Diagnosis Summary", ""]
    if detected:
        names = ", ".join(c.pattern_id.replace("_", " ") for c in detected)
        lines.append(s["detected"].format(vt=vt, names=names))
    else:
        lines.append(s["not_detected"].format(vt=vt))
    if overlay.pattern_candidates:
        lines.append("")
        for c in overlay.pattern_candidates:
            lines.append(f"- **{c.pattern_id.replace('_', ' ')}** {_lane2_badge(c)}")
    return "\n".join(lines)


def _psr_block_expert(overlay: CVVerificationOverlay, lang: str) -> str:
    s = _s(lang)
    return (
        "## PSR Decomposition\n\n"
        f"- {s['premise']}: {overlay.psr.P_appraisal}\n"
        f"- {s['strategy']}: {overlay.psr.S_strategy}\n"
        f"- {s['result']}: {overlay.psr.R_projection}"
    )


def _evidence_block_expert(overlay: CVVerificationOverlay, lang: str) -> str:
    s = _s(lang)
    lines = ["## Evidence"]
    if not overlay.pattern_candidates:
        lines.append("")
        lines.append("- (no pattern candidates)")
        return "\n".join(lines)
    for c in overlay.pattern_candidates:
        lines.append("")
        lines.append(f"### {c.pattern_id.replace('_', ' ')} {_lane2_badge(c)}")
        lines.append(f"- status: `{c.lane2_status}` (source: {_lane_source(c)})")
        if c.evidence_trace:
            lines.append(f"- {s['evidence_for']}: {', '.join(c.evidence_trace)}")
    return "\n".join(lines)


def _confidence_block_expert(overlay: CVVerificationOverlay, lang: str) -> str:
    s = _s(lang)
    total = len(overlay.pattern_candidates)
    prolog_verified = sum(
        1 for c in overlay.pattern_candidates if c.lane2_status == "pass"
    )
    candidate = sum(
        1
        for c in overlay.pattern_candidates
        if c.lane2_status not in ("pass", "fail") and c.evidence_trace
    )
    executed = sum(
        1 for c in overlay.pattern_candidates if c.lane2_status != "not_run"
    )
    return (
        "## Confidence & Limits\n\n"
        f"- Prolog-verified: {prolog_verified} / LLM-or-rule candidate: {candidate}\n"
        f"- {s['lim_prolog'].format(total=total, executed=executed)}\n"
        f"- {s['lim_ai']}\n"
        f"- {s['lim_tentative']}"
    )


def _metadata_block_expert(
    overlay: CVVerificationOverlay,
    lanes: dict[str, bool] | None,
) -> str:
    lines = [
        "## Metadata",
        "",
        f"- schema_version: {_REPORT_SCHEMA_VERSION}",
        f"- overlay_status: {overlay.overlay_status}",
        f"- route_vtype: {overlay.route_vtype}",
    ]
    if lanes is not None:
        active = ", ".join(
            f"{k}={'active' if v else 'inactive'}" for k, v in lanes.items()
        )
        lines.append(f"- lanes active: {active}")
    return "\n".join(lines)


def render_report_markdown(
    overlay: CVVerificationOverlay,
    learner_claim: str,
    *,
    lang: str = "en",
    lanes: dict[str, bool] | None = None,
) -> str:
    """Expert-format report (① --format report).

    7 sections: Input, Diagnosis Summary, PSR Decomposition, Evidence,
    Coaching, Confidence & Limits, Metadata. lane2_status is surfaced as a
    badge (✅/✗/🟡/○) — F5 partial realization with no internal-logic change.

    Safety: only system-generated narrative (diagnosis, PSR, confidence) goes
    through the violation gate, and coaching through the verdict gate. The
    learner's Input and evidence traces are quotes and are exempt — mirroring
    generate_report's treatment of the evidence block.
    """
    input_block = f"## Input\n\n> {learner_claim}"
    diagnosis = _diagnosis_summary_expert(overlay, lang)
    psr_block = _psr_block_expert(overlay, lang)
    evidence = _evidence_block_expert(overlay, lang)
    coaching = _action_suggestion(overlay, lang)
    confidence = _confidence_block_expert(overlay, lang)
    metadata = _metadata_block_expert(overlay, lanes)

    system_text = "\n\n".join([diagnosis, psr_block, confidence])
    if _check_report_violations(system_text):
        return safe_fallback_report(lang)
    # spec D1/CX-3: expert render is a STANDALONE renderer (CLI `--format report` /
    # mira-report skill) that RE-RENDERS coaching from the overlay and has NO check#7
    # backstop — unlike generate_report, whose sole caller coach_from_overlay guards its
    # output with check#7. So this coaching verdict gate is NOT a redundant double-check;
    # it is the *only* verdict guard for the expert output path. PRESERVED (defense-in-depth).
    # Only generate_report's redundant gate was removed (spec §5-5). [Deviation from plan
    # v0.3 which removed both gates — backstop asymmetry; flagged for Mnemo step-4 review.]
    if VERDICT_LANGUAGE_RE.search(coaching):
        return safe_fallback_report(lang)

    return REPORT_BLOCK_SEPARATOR.join(
        [input_block, diagnosis, psr_block, evidence, coaching, confidence, metadata]
    )
