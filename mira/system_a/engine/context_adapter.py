
"""Context-specific vocabulary for System A heuristic axes."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from functools import lru_cache
from typing import Literal

ContextName = Literal["adult_learning", "governance", "decision"]
StageName = Literal["concept", "framework", "practice", "reality"]
SignalMap = Mapping[str, tuple[str, ...]]
StageSignalMap = Mapping[StageName, tuple[str, ...]]
StageSignatureMap = Mapping[StageName, str]


@dataclass(frozen=True)
class VocabularySet:
    """Signals used by the three System A diagnostic axes."""

    context_type: ContextName
    metacognition_signals: SignalMap
    task_definition_signals: SignalMap
    stage_signals: StageSignalMap
    stage_signatures: StageSignatureMap


ADULT_LEARNING_METACOGNITION_SIGNALS: SignalMap = {
    "low": (
        "많이 공부",
        "열심히",
        "공부를 많이",
        "시간을 많이",
        "노력했",
        "이해한 것 같",
        "이해되는 것 같",
        "아는 것 같",
        "게으",
        "의지",
        "나태",
        "노력 부족",
        "studied a lot",
        "studied hard",
        "worked hard",
        "put in effort",
        "spent hours",
        "read a lot",
        "reread",
        "i think i understand",
        "kind of understand",
        "willpower",
        "lazy",
        "laziness",
    ),
    "high": (
        "설명할 수",
        "적용해 봤",
        "적용했다",
        "테스트해 봤",
        "근거",
        "부분이 약",
        "부분에서 막",
        "부족한 부분",
        "확인해 봤",
        "점검했",
        "검증했",
        "피드백을 받",
        "i can explain",
        "can explain",
        "i applied",
        "tested myself",
        "retrieval",
        "evidence",
        "specific gap",
        "checked whether",
        "verified",
        "got feedback",
    ),
}

ADULT_LEARNING_TASK_DEFINITION_SIGNALS: SignalMap = {
    "noun_goal": (
        "영어",
        "프로그래밍",
        "코딩",
        "수학",
        "통계",
        "논리",
        "문법",
        "어휘",
        "실력",
        "능력",
        "개념",
        "english",
        "coding",
        "programming",
        "python",
        "math",
        "statistics",
        "logic",
        "grammar",
        "vocabulary",
        "skill",
        "ability",
    ),
    "action_goal": (
        "설명할 수",
        "작성할 수",
        "만들 수",
        "풀 수",
        "적용할 수",
        "보고서를 작성",
        "코드를 작성",
        "업무 이메일",
        "합격",
        "통과",
        "i can write",
        "i can explain",
        "i can build",
        "i can solve",
        "i can apply",
        "can write",
        "can explain",
        "can build",
        "can solve",
        "can apply",
        "draft a",
        "build a",
        "produce a",
        "pass the exam",
        "solve problems",
    ),
}

ADULT_LEARNING_STAGE_SIGNALS: StageSignalMap = {
    "concept": (
        "배우고 싶다",
        "배우고 싶",
        "시작하려고",
        "처음",
        "입문",
        "want to learn",
        "getting started",
        "beginner",
        "what is",
    ),
    "framework": (
        "이해했다",
        "구조를 잡았다",
        "구조를 잡",
        "정리했다",
        "체계를 세웠다",
        "I understand the structure",
        "I organized",
        "mapped out",
        "framework",
    ),
    "practice": (
        "연습하고 있다",
        "연습",
        "문제를 풀고 있다",
        "문제를 풀",
        "예제를 해보고",
        "예제를 해",
        "practicing",
        "solving problems",
        "working through exercises",
        "exercise",
    ),
    "reality": (
        "실제 업무에 적용",
        "실무에 적용",
        "프로젝트에서 사용",
        "프로젝트에서",
        "결과를 냈다",
        "결과를 냈",
        "applied at work",
        "used in project",
        "used in my project",
        "got results",
    ),
}

GOVERNANCE_METACOGNITION_SIGNALS: SignalMap = {
    "low": (
        "결정했다",
        "이렇게 하기로",
        "we decided",
        "just do it",
        "항상 이렇게 했다",
        "항상",
        "무조건",
        "검토 없이",
        "we always do it this way",
        "always",
        "never",
    ),
    "high": (
        "검증 기준이 있다",
        "측정 가능한",
        "we have criteria",
        "evidence shows",
        "데이터를 확인",
        "we verified",
        "trade-off를 검토",
        "reviewed alternatives",
        "criteria defined",
    ),
}

GOVERNANCE_TASK_DEFINITION_SIGNALS: SignalMap = {
    "noun_goal": (
        "개선",
        "improvement",
        "효율화",
        "efficiency",
        "품질",
        "quality",
        "디지털 전환",
        "transformation",
        "거버넌스",
        "governance",
    ),
    "action_goal": (
        "를 줄인다",
        "을 줄인다",
        "를 달성한다",
        "을 달성한다",
        "까지 완료",
        "reduce X by Y",
        "deliver by",
        "measurable outcome",
        "완료한다",
        "배포한다",
    ),
}

GOVERNANCE_STAGE_SIGNALS: StageSignalMap = {
    "concept": (
        "제안",
        "구상",
        "아이디어",
        "검토 필요",
        "검토",
        "proposal",
        "ideation",
        "brainstorm",
        "needs review",
    ),
    "framework": (
        "설계",
        "계획 수립",
        "기준 정의",
        "아키텍처",
        "specification",
        "design",
        "architecture",
        "criteria defined",
    ),
    "practice": (
        "시범",
        "파일럿",
        "실험",
        "MVP",
        "프로토타입",
        "pilot",
        "prototype",
        "experiment",
        "trial",
    ),
    "reality": (
        "운영",
        "배포",
        "정착",
        "정책화",
        "production",
        "deployment",
        "enforcement",
        "established",
    ),
}

DECISION_METACOGNITION_SIGNALS: SignalMap = {
    "low": (
        "확정했다",
        "결론은 이미",
        "대안 없이",
        "항상",
        "무조건",
        "just decide",
        "already decided",
        "without alternatives",
        "always",
        "never",
    ),
    "high": (
        "대안 비교",
        "기준 설정",
        "근거를 비교",
        "trade-off 분석",
        "검증 중",
        "comparing alternatives",
        "criteria set",
        "trade-off analysis",
        "evidence reviewed",
        "validating",
    ),
}

DECISION_TASK_DEFINITION_SIGNALS: SignalMap = {
    "noun_goal": (
        "의사결정",
        "결정",
        "정책",
        "우선순위",
        "방향성",
        "decision",
        "policy",
        "priority",
        "direction",
    ),
    "action_goal": (
        "대안을 비교한다",
        "기준을 설정한다",
        "까지 결정",
        "시범 적용",
        "검증한다",
        "decide by",
        "select based on",
        "compare alternatives",
        "validate",
    ),
}

DECISION_STAGE_SIGNALS: StageSignalMap = {
    "concept": (
        "논의 중",
        "의견 수렴",
        "문제 인식",
        "under discussion",
        "gathering input",
        "problem identified",
    ),
    "framework": (
        "대안 비교",
        "기준 설정",
        "trade-off 분석",
        "comparing alternatives",
        "criteria set",
        "trade-off analysis",
    ),
    "practice": (
        "시범 적용",
        "제한적 실행",
        "검증 중",
        "limited rollout",
        "testing",
        "validating",
    ),
    "reality": (
        "확정",
        "전면 시행",
        "정책화",
        "finalized",
        "full implementation",
        "policy enacted",
    ),
}

_STAGE_SIGNATURES: Mapping[ContextName, StageSignatureMap] = {
    "adult_learning": {
        "concept": "adult_learning concept-entry layer",
        "framework": "adult_learning framework-organization layer",
        "practice": "adult_learning practice-feedback layer",
        "reality": "adult_learning reality-transfer layer",
    },
    "governance": {
        "concept": "governance proposal layer",
        "framework": "governance design layer",
        "practice": "governance pilot layer",
        "reality": "governance production layer",
    },
    "decision": {
        "concept": "decision problem-framing layer",
        "framework": "decision criteria-comparison layer",
        "practice": "decision limited-rollout layer",
        "reality": "decision policy-enactment layer",
    },
}

_VOCABULARY: Mapping[ContextName, VocabularySet] = {
    "adult_learning": VocabularySet(
        context_type="adult_learning",
        metacognition_signals=ADULT_LEARNING_METACOGNITION_SIGNALS,
        task_definition_signals=ADULT_LEARNING_TASK_DEFINITION_SIGNALS,
        stage_signals=ADULT_LEARNING_STAGE_SIGNALS,
        stage_signatures=_STAGE_SIGNATURES["adult_learning"],
    ),
    "governance": VocabularySet(
        context_type="governance",
        metacognition_signals=GOVERNANCE_METACOGNITION_SIGNALS,
        task_definition_signals=GOVERNANCE_TASK_DEFINITION_SIGNALS,
        stage_signals=GOVERNANCE_STAGE_SIGNALS,
        stage_signatures=_STAGE_SIGNATURES["governance"],
    ),
    "decision": VocabularySet(
        context_type="decision",
        metacognition_signals=DECISION_METACOGNITION_SIGNALS,
        task_definition_signals=DECISION_TASK_DEFINITION_SIGNALS,
        stage_signals=DECISION_STAGE_SIGNALS,
        stage_signatures=_STAGE_SIGNATURES["decision"],
    ),
}


def normalize_context_type(context_type: str) -> ContextName:
    """Return a supported context name, defaulting unknown values to adult learning."""

    if context_type in _VOCABULARY:
        return context_type  # type: ignore[return-value]
    return "adult_learning"


def get_vocabulary_set(context_type: str) -> VocabularySet:
    """Return the signal bundle used by all System A axis assessors."""

    return _VOCABULARY[normalize_context_type(context_type)]


def count_signal_hits(text: str, signals: tuple[str, ...]) -> int:
    """Count vocabulary hits with case-insensitive matching and simple placeholders."""

    return sum(len(_compile_signal(signal).findall(text)) for signal in signals)


def has_signal(text: str, signals: tuple[str, ...]) -> bool:
    """Return whether any vocabulary signal appears in text."""

    return any(_compile_signal(signal).search(text) for signal in signals)


@lru_cache(maxsize=256)
def _compile_signal(signal: str) -> re.Pattern[str]:
    escaped = re.escape(signal.strip())
    escaped = escaped.replace(r"\ ", r"\s+")
    escaped = re.sub(r"(?<![A-Za-z])X(?![A-Za-z])", r".+?", escaped)
    escaped = re.sub(r"(?<![A-Za-z])Y(?![A-Za-z])", r".+?", escaped)
    return re.compile(escaped, re.IGNORECASE)


__all__ = [
    "ContextName",
    "DECISION_METACOGNITION_SIGNALS",
    "DECISION_STAGE_SIGNALS",
    "DECISION_TASK_DEFINITION_SIGNALS",
    "GOVERNANCE_METACOGNITION_SIGNALS",
    "GOVERNANCE_STAGE_SIGNALS",
    "GOVERNANCE_TASK_DEFINITION_SIGNALS",
    "StageName",
    "VocabularySet",
    "count_signal_hits",
    "get_vocabulary_set",
    "has_signal",
    "normalize_context_type",
]
