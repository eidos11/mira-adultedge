"""Load coaching content and theory templates for pattern-specific responses."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

_SKILLS_DIR = Path(__file__).parent
_COACHING_CACHE: dict[str, Any] | None = None
_THEORY_CACHE: dict[str, Any] | None = None


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_coaching_content() -> dict[str, Any]:
    global _COACHING_CACHE
    if _COACHING_CACHE is None:
        _COACHING_CACHE = _load_yaml(_SKILLS_DIR / "coaching_content.yaml")
    return _COACHING_CACHE


def get_theory_templates() -> dict[str, Any]:
    global _THEORY_CACHE
    if _THEORY_CACHE is None:
        _THEORY_CACHE = _load_yaml(_SKILLS_DIR / "theory_templates.yaml")
    return _THEORY_CACHE


_LABELS = {
    "en": {
        "psr_focus": "PSR focus",
        "self_check": "Self-check questions:",
        "next_step": "Next step:",
        "recurrence": "Recurrence signal",
    },
    "ko": {
        "psr_focus": "PSR 관점",
        "self_check": "자기 점검 질문:",
        "next_step": "다음 단계:",
        "recurrence": "재발 신호",
    },
}


def generate_coaching_block(
    pattern_id: str,
    lang: str = "en",
    tentative: bool = False,
    basis: str | None = None,
) -> str | None:
    """Generate a coaching block for a detected pattern.

    Returns a formatted markdown string with Socratic inquiry + action invitation,
    or None if no coaching content template exists for this pattern.

    Args:
        pattern_id: The pattern identifier to generate coaching for.
        lang: Language code ("en" or "ko").
        tentative: When True, prepends a hypothetical lead-in before the recognition
            line to frame the pattern as a possibility rather than a confirmed finding.
            Intended for unverified patterns (spec D3). Default False (assertive).
        basis: Optional pre-formatted selection-basis line (e.g. the learner phrase
            that triggered a Lane 1 cue). Rendered right after the recognition line
            so the learner can see WHY this coaching surfaced (improvement #1).
    """
    skills = get_coaching_content()
    theory = get_theory_templates()

    skill = skills.get(pattern_id)
    if skill is None:
        return None

    lb = _LABELS.get(lang, _LABELS["en"])
    lines: list[str] = []

    recognition = skill.get("recognition", {}).get(lang)
    if recognition:
        if tentative:
            _TENTATIVE_LEADS = {
                "en": "This *may* point to the following — not a confirmed diagnosis; please check:",
                # NOTE (Korean gate fix, improvement #3): the previous lead
                # "확정 진단이 아니니" contained '확정', which matches
                # VERDICT_LANGUAGE_RE — critic check #7 then collapsed every
                # Korean coaching report into the safe fallback. Reworded to a
                # gate-token-free equivalent.
                "ko": "다음 패턴에 *해당할 수 있습니다* — 단정이 아닌 가설이니 직접 점검해 보세요:",
            }
            lead = _TENTATIVE_LEADS.get(lang, "This *may* apply — please check:")
            lines.append(lead)
            lines.append("")
        lines.append(f"**{pattern_id.replace('_', ' ')}** — {recognition}")
        lines.append("")
        if basis:
            lines.append(f"*{basis}*")
            lines.append("")

    psr_focus = skill.get(f"psr_coaching_focus_{lang}") or skill.get("psr_coaching_focus")
    if psr_focus:
        lines.append(f"*{lb['psr_focus']}: {psr_focus}*")
        lines.append("")

    inquiries = skill.get("socratic_inquiry", [])
    if inquiries:
        lines.append(f"**{lb['self_check']}**")
        for q in inquiries:
            question = q.get(lang, q.get("en", q.get("ko", "")))
            if question:
                lines.append(f"- {question}")
        lines.append("")

    action = skill.get("action_invitation", {}).get(lang)
    if action:
        lines.append(f"**{lb['next_step']}** {action}")
        lines.append("")

    theory_entry = theory.get(pattern_id)
    if theory_entry:
        # Language-aware theory message (improvement #3): prefer
        # learner_message_<lang>, fall back to the base learner_message.
        learner_msg = theory_entry.get(f"learner_message_{lang}") or theory_entry.get(
            "learner_message"
        )
        if learner_msg:
            lines.append(f"> {learner_msg}")
            lines.append("")

    signal = skill.get("self_monitor_signal", {}).get(lang)
    if signal:
        lines.append(f"*{lb['recurrence']}: {signal}*")

    return "\n".join(lines) if lines else None


def get_available_patterns() -> list[str]:
    """Return pattern IDs that have coaching content."""
    return list(get_coaching_content().keys())
