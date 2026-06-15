"""Regression tests for improvements #1-#3 (draft).

#1 cue→coaching wiring   — detected input cues drive coaching selection
#2 specificity           — healthy/neutral inputs no longer receive
                           input-invariant pattern coaching
#3 Korean path repair    — ko reports no longer collapse to safe fallback

These tests encode the new contract: coaching is emitted ONLY for
signal-backed candidates; class B (healthy) and class C (neutral)
replace the previous alphabetical template dump.
"""

from __future__ import annotations

import re

from mira.pipeline import diagnose_only, run_minimal_loop
from mira.report import generate_report, safe_fallback_report
from mira.system_b.engine.critic.adapter import run_reduced_critic
from mira.system_b.engine.lane1_cues import (
    extract_cues,
    extract_health_signals,
)

_HANGUL = re.compile(r"[가-힣]")


def _report(text: str, lang: str = "en") -> str:
    res = run_minimal_loop(text, claim_language=lang)
    return res.report


def _critic_pass(text: str, lang: str = "en") -> bool:
    diag = diagnose_only(text, lang=lang)
    report = generate_report(diag.overlay, diag.request.learner_claim, lang=lang)
    ok, _ = run_reduced_critic(
        diag.overlay.psr,
        diag.overlay.pattern_candidates,
        diag.overlay.route_vtype,
        response_text=report,
        trace_id=diag.overlay.trace_id,
    )
    return ok


# ── improvement #1: cue → coaching wiring ──────────────────────────────

def test_willpower_input_gets_willpower_coaching():
    report = _report("I keep failing because I am lazy and have no willpower.")
    assert "willpower blame" in report
    assert "Why this surfaced" in report


def test_false_dilemma_input_gets_false_dilemma_first():
    report = _report(
        "Either I pass this certification exam on the first try, "
        "or my career in data science is over."
    )
    coaching = report.split("## Coaching")[1]
    assert "false dilemma" in coaching
    # catastrophizing cue ("career is over") may also surface — as a
    # no-template note, never silently.
    assert coaching.index("false dilemma") < len(coaching)


def test_ability_attribution_surfaces_named_signal():
    # genetic_fallacy has no coaching template; the honest no-template
    # note must name the signal instead of silently coaching noise.
    report = _report("I failed because I am just not smart enough.")
    assert "genetic fallacy" in report or "oversimplified cause" in report
    assert "Why this surfaced" in report


def test_cue_extractor_bilingual():
    hits = {h.pattern_id for h in extract_cues("둘 중 하나야. 여기까지 했는데 포기 못 해.")}
    assert "false_dilemma" in hits
    assert "sunk_cost" in hits


# ── improvement #2: specificity (class B / class C) ────────────────────

def test_healthy_input_receives_no_pattern_coaching():
    healthy = (
        "I failed the exam, so I reviewed which topics I missed, "
        "made an error log, and scheduled practice tests for my weak areas."
    )
    assert len(extract_health_signals(healthy)) >= 2
    report = _report(healthy)
    coaching = report.split("## Coaching")[1]
    assert "false dilemma" not in coaching
    assert "oversimplified cause" not in coaching
    assert "No pattern coaching is needed" in coaching


def test_neutral_input_receives_elicitation_not_coaching():
    report = _report("The course starts next month.")
    coaching = report.split("## Coaching")[1]
    assert "false dilemma" not in coaching
    assert "What evidence makes you think so?" in coaching


def test_class_b_is_process_level_not_person_level():
    healthy = (
        "I failed the exam, so I reviewed which topics I missed, "
        "made an error log, and scheduled practice tests for my weak areas."
    )
    report = _report(healthy)
    # Invariant #12 symmetry: no person-level verdicts, positive included.
    assert not re.search(r"you are\s+(smart|talented|a good learner)", report, re.I)


# ── improvement #3: Korean path repair ─────────────────────────────────

def test_korean_report_is_not_safe_fallback():
    report = _report("시험에 떨어진다는 건 머리가 나쁜 거겠지", lang="ko")
    assert report != safe_fallback_report("ko")
    assert "코칭" in report


def test_korean_coaching_text_is_korean():
    report = _report("나는 머리가 나빠서 안 되는 것 같아. 그것 때문이다.", lang="ko")
    coaching = report.split("## 코칭")[1]
    hangul_chars = len(_HANGUL.findall(coaching))
    assert hangul_chars > 40, "ko coaching must render Korean, not English"


def test_korean_healthy_input_class_b():
    report = _report("오답을 점검하고 틀린 부분을 기록했어요. 약한 부분 복습 계획도 세웠습니다.", lang="ko")
    assert "패턴 코칭이 필요하지 않습니다" in report


# ── safety: every new output class passes the Lane 1 critic ───────────

def test_all_classes_pass_reduced_critic():
    samples = [
        ("I keep failing because I am lazy and have no willpower.", "en"),
        ("Either I pass or my career is over.", "en"),
        ("I reviewed which topics I missed and made an error log.", "en"),
        ("The course starts next month.", "en"),
        ("시험에 떨어진다는 건 머리가 나쁜 거겠지", "ko"),
        ("오답을 점검하고 틀린 부분을 기록했어요.", "ko"),
    ]
    for text, lang in samples:
        assert _critic_pass(text, lang), f"critic failed for: {text!r} ({lang})"
