"""M1 minimal contracts: SystemAtoCVRequest + CVVerificationOverlay.

Simplified from the full 4-contract runtime.py (807 lines).
SDR reference: _scratch/M1-simplification-decisions.md §1.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

VType = Literal["D", "I", "A"]
OverlayStatus = Literal["verified", "structural_mismatch", "needs_review", "insufficient_evidence"]
Lane2Status = Literal["pass", "fail", "unverified", "not_run"]


def _require_nonblank(value: str, field_name: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{field_name} must be a non-blank string")
    return stripped


class StrictMinimalModel(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")


class PSRPrior(BaseModel):
    model_config = ConfigDict(extra="forbid")
    P_appraisal: str | None = None
    S_strategy: str | None = None
    R_projection: str | None = None
    suggested_vtype: VType | None = None


class SystemAtoCVRequest(StrictMinimalModel):
    """A→B request. Snapshot fields embedded (SDR §1: 4→2 contract reduction)."""

    trace_id: str
    learner_claim: str
    claim_domain: str = "adult_learning"
    claim_language: str = "ko"
    psr_prior: PSRPrior | None = None

    @model_validator(mode="after")
    def validate_nonempty(self) -> SystemAtoCVRequest:
        self.trace_id = _require_nonblank(self.trace_id, "trace_id")
        self.learner_claim = _require_nonblank(self.learner_claim, "learner_claim")
        return self


class PatternCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pattern_id: str = Field(min_length=1)
    canonical_id: str = Field(min_length=1)
    vtype: VType
    lane2_status: Lane2Status = "not_run"
    lane2_result: dict[str, Any] | None = None
    evidence_trace: list[str] = Field(default_factory=list)
    lane3_detected: bool = False


class PSRResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    P_appraisal: str = Field(min_length=1)
    S_strategy: str = Field(min_length=1)
    R_projection: str = Field(min_length=1)
    claim_type: str = "unclassified"


class CVVerificationOverlay(StrictMinimalModel):
    """B→A response. LaneResultEnvelope embedded (SDR §1)."""

    trace_id: str
    request_id: str = Field(min_length=1)
    psr: PSRResult
    route_vtype: VType
    pattern_candidates: list[PatternCandidate] = Field(default_factory=list)
    overlay_status: OverlayStatus
    lane1_pass: bool
    lane2_results: dict[str, Any] = Field(default_factory=dict)
    evidence_summary: str = Field(min_length=1)
    avoid_willpower_blame: bool = True

    @model_validator(mode="after")
    def validate_invariants(self) -> CVVerificationOverlay:
        self.trace_id = _require_nonblank(self.trace_id, "trace_id")
        if not self.avoid_willpower_blame:
            raise ValueError(
                "avoid_willpower_blame must be True (v0.1 invariant: "
                "willpower/laziness blame is never permitted in overlay)"
            )
        return self
