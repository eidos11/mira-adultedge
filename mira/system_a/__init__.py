"""Heuristic System A diagnostic engine package.

Re-exports from engine/ subpackage for backward-compatible imports.
"""

from __future__ import annotations

from mira.system_a.engine import (
    ContextType,
    DiagnosticEngine,
    DiagnosticHypothesis,
    DiagnosticSnapshot,
    MetacognitionResult,
    StageResult,
    SystemACues,
    TaskDefinitionResult,
    assess_metacognition,
    assess_stage,
    assess_task_definition,
    diagnose_claim,
)

__all__ = [
    "ContextType",
    "DiagnosticEngine",
    "DiagnosticHypothesis",
    "DiagnosticSnapshot",
    "MetacognitionResult",
    "StageResult",
    "SystemACues",
    "TaskDefinitionResult",
    "assess_metacognition",
    "assess_stage",
    "assess_task_definition",
    "diagnose_claim",
]
