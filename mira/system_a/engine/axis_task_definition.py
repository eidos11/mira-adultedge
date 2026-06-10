
"""Task-definition-axis heuristics for System A diagnostic snapshots."""

from __future__ import annotations

import re
from dataclasses import dataclass

from mira.system_a.engine.context_adapter import get_vocabulary_set, has_signal


@dataclass(frozen=True)
class TaskDefinitionResult:
    """Heuristic estimate of whether a learning goal is noun-like or action-like."""

    goal_reframed: str | None
    weakest_force: str | None
    is_noun_goal: bool


_ACTION_GOAL_RE = re.compile(
    r"("
    r"설명할\s*수|작성할\s*수|만들\s*수|풀\s*수|적용할\s*수|"
    r"보고서를?\s*작성|코드를?\s*작성|업무\s*이메일|합격|통과|"
    r"i\s+can\s+(write|explain|build|solve|apply)|can\s+(write|explain|build|solve|apply)|"
    r"write\s+(an?|the)|draft\s+(an?|the)|build\s+(an?|the)|produce\s+(an?|the)|"
    r"pass\s+the\s+exam|solve\s+problems|apply\s+.+\s+to"
    r")",
    re.IGNORECASE,
)
_NOUN_GOAL_RE = re.compile(
    r"("
    r"영어|프로그래밍|코딩|수학|통계|논리|문법|어휘|실력|능력|개념|"
    r"\benglish\b|\bcoding\b|\bprogramming\b|\bpython\b|\bmath\b|\bstatistics\b|"
    r"\blogic\b|\bgrammar\b|\bvocabulary\b|\bskill\b|\bability\b"
    r")",
    re.IGNORECASE,
)
_MOTIVE_RE = re.compile(
    r"(왜|목표가?\s*불분명|방향|목적|why|unclear\s+goal|direction|purpose)",
    re.IGNORECASE,
)
_TIME_ENERGY_RE = re.compile(
    r"(시간|마감|피곤|체력|에너지|바쁘|deadline|time|tired|energy|busy)",
    re.IGNORECASE,
)
_METHOD_RE = re.compile(
    r"(방법|공부법|전략|계획|어떻게|루틴|method|strategy|plan|routine|how\s+to)",
    re.IGNORECASE,
)
_FEEDBACK_RE = re.compile(
    r"(피드백|확인|점검|검증|틀렸는지|feedback|check|verify|review|tested)",
    re.IGNORECASE,
)


def assess_task_definition(
    claim: str,
    intake_fields: dict[str, object] | None = None,
    context_type: str = "adult_learning",
) -> TaskDefinitionResult:
    """Assess whether the task is framed as a domain label or observable output."""

    text = _with_intake_text(claim, intake_fields)
    if not text:
        return TaskDefinitionResult(goal_reframed=None, weakest_force=None, is_noun_goal=True)

    vocabulary = get_vocabulary_set(context_type)
    action_signals = vocabulary.task_definition_signals.get("action_goal", ())
    noun_signals = vocabulary.task_definition_signals.get("noun_goal", ())

    has_action_goal = bool(_ACTION_GOAL_RE.search(text)) or has_signal(text, action_signals)
    has_noun_goal = bool(_NOUN_GOAL_RE.search(text)) or has_signal(text, noun_signals)
    is_noun_goal = has_noun_goal and not has_action_goal

    return TaskDefinitionResult(
        goal_reframed=_reframe_goal(text, vocabulary.context_type) if is_noun_goal else None,
        weakest_force=_weakest_force(text, intake_fields),
        is_noun_goal=is_noun_goal,
    )


# Reframe suggestions are stored language-neutrally (as keys) at diagnosis time and
# localized only when the report is rendered: the diagnostic snapshot is language-
# agnostic, while the output language is a report-time concern (CLI --lang). Baking a
# localized string here would leak it into reports of the other language.
REFRAME_FRAMES: dict[str, dict[str, str]] = {
    "en": {
        "governance": "define a measurable governance output and its verification criteria",
        "decision": "make the alternatives and criteria explicit so the decision can be verified",
        "english": "be able to write a work email in English",
        "coding": "be able to implement a small feature and confirm it with a test",
        "math": "be able to explain the solution steps and solve similar problems",
        "grammar": "be able to use the new expression correctly within a sentence",
        "generic": "define a concrete output you can verify in a real situation",
    },
    "ko": {
        "governance": "측정 가능한 거버넌스 산출물과 검증 기준을 정한다",
        "decision": "대안과 기준을 명시해 검증 가능한 결정 절차를 만든다",
        "english": "영어로 업무 이메일을 작성할 수 있다",
        "coding": "작은 기능을 구현하고 테스트로 확인할 수 있다",
        "math": "문제 풀이 과정을 설명하고 유사 문제를 풀 수 있다",
        "grammar": "새 표현을 문장 안에서 정확히 사용할 수 있다",
        "generic": "구체적 산출물을 정해 실제 상황에서 확인할 수 있다",
    },
}


def reframe_text(reframe_key: str, lang: str = "en") -> str:
    """Localize a reframe key at render time; fall back to the English generic frame."""
    frames = REFRAME_FRAMES.get(lang, REFRAME_FRAMES["en"])
    return frames.get(reframe_key) or REFRAME_FRAMES["en"]["generic"]


def _reframe_goal(text: str, context_type: str = "adult_learning") -> str:
    """Return a language-neutral reframe key (localized later via reframe_text)."""
    if context_type == "governance":
        return "governance"
    if context_type == "decision":
        return "decision"
    if re.search(r"(영어|\benglish\b)", text, re.IGNORECASE):
        return "english"
    if re.search(r"(프로그래밍|코딩|\bcoding\b|\bprogramming\b|\bpython\b)", text, re.IGNORECASE):
        return "coding"
    if re.search(r"(수학|통계|\bmath\b|\bstatistics\b)", text, re.IGNORECASE):
        return "math"
    if re.search(r"(문법|어휘|\bgrammar\b|\bvocabulary\b)", text, re.IGNORECASE):
        return "grammar"
    return "generic"


def _weakest_force(
    text: str,
    intake_fields: dict[str, object] | None,
) -> str | None:
    scores = {
        "feedback_loop": len(_FEEDBACK_RE.findall(text)),
        "time_energy": len(_TIME_ENERGY_RE.findall(text)),
        "method_strategy": len(_METHOD_RE.findall(text)),
        "motive_clarity": len(_MOTIVE_RE.findall(text)),
    }
    if intake_fields:
        if _has_nonblank(intake_fields.get("time_constraints")) or _has_nonblank(
            intake_fields.get("energy_pattern")
        ):
            scores["time_energy"] += 1
        if _has_nonblank(intake_fields.get("current_materials")):
            scores["method_strategy"] += 1
        if _has_nonblank(intake_fields.get("support_map")):
            scores["feedback_loop"] += 1
        if _has_nonblank(intake_fields.get("goal_raw")):
            scores["motive_clarity"] += 1

    force, score = max(scores.items(), key=lambda item: item[1])
    return force if score > 0 else None


def _has_nonblank(value: object) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return any(isinstance(item, str) and item.strip() for item in value)
    return False


def _with_intake_text(claim: str, intake_fields: dict[str, object] | None) -> str:
    parts = [claim]
    if intake_fields:
        for value in intake_fields.values():
            if isinstance(value, str):
                parts.append(value)
            elif isinstance(value, list):
                parts.extend(item for item in value if isinstance(item, str))
    return " ".join(part.strip() for part in parts if part and part.strip())


__all__ = ["TaskDefinitionResult", "assess_task_definition", "reframe_text", "REFRAME_FRAMES"]
