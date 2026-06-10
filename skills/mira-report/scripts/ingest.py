"""mira-report skill (②) — ingest stage.

Validate a diagnostic JSON (produced by ``python -m mira --format json``) and
rebuild the ``CVVerificationOverlay`` so the render stage can reuse the
``mira.report`` renderers (expert mode = DRY, decision 3).

schema_version gate (decision 1, fail-closed): an unsupported or missing
version raises an explicit error with regeneration guidance rather than a
silent best-effort parse. This keeps the skill calibrated and safe for
B2B2C customization, where input contracts must be unambiguous.

Fields the JSON omits but the strict overlay requires (``trace_id``,
``request_id``, ``evidence_summary``; per-pattern ``canonical_id``, ``vtype``)
are render-irrelevant and filled with deterministic placeholders — they never
affect rendered output.

Task 2 additive: the ``coaching`` field (structured dict with block/pattern_id/note)
is an optional top-level field in the diagnostic JSON.  It is NEVER passed to
``CVVerificationOverlay`` (which uses ``extra="forbid"``).  Use ``ingest_coaching``
to extract it separately.  schema_version is unchanged at "0.2.2" (additive only).
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TypedDict

# BUG-1: when imported via the SKILL.md `python -c` contract, sys.path[0] is the
# scripts dir, not the project root, so the module-level `import mira` below
# fails — this project is not installed into site-packages. Bootstrap the
# project root onto sys.path before importing mira.
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from mira.contracts.minimal import (
    CVVerificationOverlay,
    PatternCandidate,
    PSRResult,
)

SUPPORTED_SCHEMA_VERSIONS = ("0.2.2",)


class UnsupportedSchemaVersionError(ValueError):
    """Input ``schema_version`` is missing or not in SUPPORTED_SCHEMA_VERSIONS."""


class CoachingDict(TypedDict):
    """Shape of the optional ``coaching`` field in the diagnostic JSON.

    SYNC: this is an intentional manual mirror of ``mira.pipeline.Coaching``,
    kept local so this skill has no import dependency on the pipeline module.
    The two are synced by hand. If coaching grows fields, Task 5 should consider
    promoting both to a shared type (e.g. mira/types.py).

    block       — coaching text (from pipeline's _extract_coaching_from_report)
    pattern_id  — primary pattern addressed; str or None
    note        — out-of-scope/skip message; None here (Task 5 fills it)
    """

    block: str
    pattern_id: str | None
    note: str | None


def ingest(data: dict) -> CVVerificationOverlay:
    """Validate ``schema_version`` then rebuild the overlay (fail-closed).

    The optional ``coaching`` field in ``data`` is silently ignored here —
    it is never passed to the overlay (``extra="forbid"``).  Use
    ``ingest_coaching`` to extract it.
    """
    version = data.get("schema_version")
    if version not in SUPPORTED_SCHEMA_VERSIONS:
        supported = ", ".join(SUPPORTED_SCHEMA_VERSIONS)
        raise UnsupportedSchemaVersionError(
            f"Unsupported schema_version {version!r} (supported: {supported}). "
            f"Regenerate the diagnostic with `python -m mira --format json <input>` "
            f"from a mira build that emits schema {supported}."
        )
    return _rebuild_overlay(data)


def ingest_coaching(data: dict) -> CoachingDict | None:
    """Extract the optional structured coaching dict from diagnostic JSON.

    Returns the ``coaching`` sub-dict if present and well-formed (has at least
    a ``block`` key), or ``None`` if the field is absent.  schema_version is
    NOT re-validated here — call ``ingest`` first for the gate check.

    coaching is kept OUTSIDE the overlay (``CVVerificationOverlay`` uses
    ``extra="forbid"``); this function is the only path to retrieve it.
    """
    raw = data.get("coaching")
    if raw is None:
        return None
    return CoachingDict(
        block=raw.get("block", ""),
        pattern_id=raw.get("pattern_id"),
        note=raw.get("note"),
    )


def _rebuild_overlay(data: dict) -> CVVerificationOverlay:
    route_vtype = data["route_vtype"]
    psr = data["psr"]
    candidates = [
        PatternCandidate(
            pattern_id=p["pattern_id"],
            canonical_id="ingested",        # render-irrelevant placeholder
            vtype=route_vtype,              # render reads overlay.route_vtype only
            lane2_status=p.get("lane2_status", "not_run"),
            lane2_result=p.get("lane2_result"),
            evidence_trace=p.get("evidence_trace", []),
            lane3_detected=p.get("lane3_detected", False),
        )
        for p in data.get("patterns", [])
    ]
    return CVVerificationOverlay(
        trace_id="ingested",                # render-irrelevant placeholder
        request_id="ingested",              # render-irrelevant placeholder
        psr=PSRResult(
            P_appraisal=psr["P"],
            S_strategy=psr["S"],
            R_projection=psr["R"],
        ),
        route_vtype=route_vtype,
        pattern_candidates=candidates,
        overlay_status=data["overlay_status"],
        lane1_pass=data.get("lane1_pass", True),  # absent in diagnose-verify/coach path (computed inside coach_from_overlay); True is safe — lane1 critic ran and either approved or triggered safe_fallback_report before we get here
        evidence_summary=(
            f"Reconstructed from diagnostic JSON (schema {data['schema_version']})."
        ),
    )
