"""MIRA System A Engine — diagnostic pipeline Python glue."""

from mira.system_a.engine.axis_metacognition import (
    MetacognitionResult,
    assess_metacognition,
)
from mira.system_a.engine.axis_stage import StageResult, assess_stage
from mira.system_a.engine.axis_task_definition import (
    TaskDefinitionResult,
    assess_task_definition,
)
from mira.system_a.engine.diagnostic_engine import (
    ContextType,
    DiagnosticEngine,
    diagnose_claim,
)
from mira.system_a.types import DiagnosticHypothesis, DiagnosticSnapshot, SystemACues

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
