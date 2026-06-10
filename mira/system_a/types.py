
"""Lightweight System A output types for the minimal pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DiagnosticHypothesis:
    primary_leaks: list[str] = field(default_factory=list)
    weakest_force: str | None = None
    stage_estimate: str = "concept"
    goal_reframed: str | None = None


@dataclass(frozen=True)
class SystemACues:
    possible_claim_type: str = "action_goal"
    possible_cognitive_layer_signature: str | None = None


@dataclass(frozen=True)
class DiagnosticSnapshot:
    trace_id: str
    learner_claim: str
    diagnostic_hypothesis: DiagnosticHypothesis
    system_a_cues: SystemACues
    confidence_band: str = "medium"
