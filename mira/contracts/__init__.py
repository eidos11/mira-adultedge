"""Minimal contracts for the M1 pipeline."""

from __future__ import annotations

from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator

from mira.contracts.minimal import (
    CVVerificationOverlay,
    Lane2Status,
    OverlayStatus,
    PSRPrior,
    PSRResult,
    PatternCandidate,
    StrictMinimalModel,
    SystemAtoCVRequest,
    VType,
)


class JudgmentDistribution(BaseModel):
    """Track System A four-way judgment preservation distribution."""

    model_config = ConfigDict(strict=True, extra="forbid")

    certain: float | None = None
    reserved: float | None = None
    needs_more_info: float | None = None
    undecidable: float | None = None

    @model_validator(mode="after")
    def validate_distribution(self) -> Self:
        values = [self.certain, self.reserved, self.needs_more_info, self.undecidable]
        if all(value is None for value in values):
            return self
        if any(value is None for value in values):
            raise ValueError("judgment_distribution values must be all null or all numeric")
        numeric_values = [value for value in values if value is not None]
        for value in numeric_values:
            if value < 0.0 or value > 1.0:
                raise ValueError("judgment_distribution values must be between 0.0 and 1.0")
        total = sum(numeric_values)
        if not 0.99 <= total <= 1.01:
            raise ValueError("judgment_distribution sum must be 1.0 +/- 0.01")
        return self

    def is_absent(self) -> bool:
        return all(
            value is None
            for value in (self.certain, self.reserved, self.needs_more_info, self.undecidable)
        )

    def non_certain_mass(self) -> float:
        if self.is_absent():
            return 0.0
        return float(
            (self.reserved or 0.0)
            + (self.needs_more_info or 0.0)
            + (self.undecidable or 0.0)
        )

__all__ = [
    "CVVerificationOverlay",
    "JudgmentDistribution",
    "Lane2Status",
    "OverlayStatus",
    "PSRPrior",
    "PSRResult",
    "PatternCandidate",
    "StrictMinimalModel",
    "SystemAtoCVRequest",
    "VType",
]
