
"""System A heuristic diagnostic engine for minimal diagnostic snapshots."""

from __future__ import annotations

from typing import Literal

from mira.system_a.engine.axis_metacognition import assess_metacognition
from mira.system_a.engine.axis_stage import assess_stage
from mira.system_a.engine.axis_task_definition import (
    TaskDefinitionResult,
    assess_task_definition,
)
from mira.system_a.types import DiagnosticHypothesis, DiagnosticSnapshot, SystemACues

ContextType = Literal["adult_learning", "governance", "decision"]


class DiagnosticEngine:
    """Assemble three heuristic axes into a System A diagnostic snapshot."""

    def diagnose(
        self,
        claim: str,
        *,
        trace_id: str,
        intake_fields: dict[str, str | list[str]] | None = None,
        context_type: ContextType = "adult_learning",
    ) -> DiagnosticSnapshot:
        metacog_result = assess_metacognition(claim, intake_fields, context_type)
        taskdef_result = assess_task_definition(claim, intake_fields, context_type)
        stage_result = assess_stage(claim, intake_fields, context_type)

        return DiagnosticSnapshot(
            trace_id=trace_id,
            learner_claim=claim,
            diagnostic_hypothesis=DiagnosticHypothesis(
                primary_leaks=metacog_result.primary_leaks,
                weakest_force=taskdef_result.weakest_force,
                stage_estimate=stage_result.stage_estimate,
                goal_reframed=taskdef_result.goal_reframed,
            ),
            system_a_cues=SystemACues(
                possible_claim_type=_claim_type_cue(taskdef_result),
                possible_cognitive_layer_signature=stage_result.cognitive_layer_signature,
            ),
            confidence_band=metacog_result.confidence_band,
        )


def diagnose_claim(
    claim: str,
    *,
    trace_id: str,
    intake_fields: dict[str, str | list[str]] | None = None,
    context_type: ContextType = "adult_learning",
) -> DiagnosticSnapshot:
    """Convenience wrapper around DiagnosticEngine.diagnose()."""

    return DiagnosticEngine().diagnose(
        claim,
        trace_id=trace_id,
        intake_fields=intake_fields,
        context_type=context_type,
    )


def _claim_type_cue(taskdef: TaskDefinitionResult) -> str:
    return "noun_goal" if taskdef.is_noun_goal else "action_goal"


def _optional_text(value: str | list[str] | None) -> str | None:
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned or None
    if isinstance(value, list):
        items = [item.strip() for item in value if item.strip()]
        return "; ".join(items) if items else None
    return None


def _string_list(value: str | list[str] | None) -> list[str]:
    if isinstance(value, str):
        items = [value.strip()] if value.strip() else []
    elif isinstance(value, list):
        items = [item.strip() for item in value if item.strip()]
    else:
        items = []

    deduped: list[str] = []
    for item in items:
        if item not in deduped:
            deduped.append(item)
    return deduped


__all__ = ["ContextType", "DiagnosticEngine", "DiagnosticSnapshot", "diagnose_claim"]
