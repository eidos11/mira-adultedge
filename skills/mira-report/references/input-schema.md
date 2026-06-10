# Input schema — mira-report

The skill ingests a **diagnostic JSON** produced by:

```bash
python -m mira --format json "<learner text>"
```

## Supported versions

| schema_version | status |
|----------------|--------|
| `0.2.2` | ✅ supported |
| `< 0.2.2` or missing | ❌ rejected (fail-closed) — regenerate with current `mira` |

An unsupported or missing `schema_version` raises `UnsupportedSchemaVersionError`
with regeneration guidance. The skill never best-effort parses an unknown
contract — this keeps it calibrated and safe for B2B2C customization, where the
input contract must be unambiguous.

## Required fields (0.2.2)

| field | type | used by | notes |
|-------|------|---------|-------|
| `schema_version` | str | gate | must be `"0.2.2"` |
| `input` | str | expert/html Input section | learner's original text |
| `route_vtype` | str (`D`/`I`/`A`) | diagnosis summary | deductive / inductive / abductive route |
| `psr` | object `{P,S,R}` | PSR section | premise / strategy / result appraisal |
| `patterns` | array | evidence + diagnosis | each item below |
| `overlay_status` | str | coaching fallback | e.g. `verified`, `needs_review` |
| `lane1_pass` | bool | (carried) | rule-lane gate result |
| `report` | str | (carried) | base 4-block report text |

Each `patterns[]` item:

| field | type | notes |
|-------|------|-------|
| `pattern_id` | str | e.g. `willpower_blame` |
| `lane2_status` | str | `pass` / `fail` / `not_run` |
| `evidence_trace` | array of str | cues; `[L3] …` marks LLM-sourced |
| `lane2_result` | object | optional; present only when Prolog ran |

> Render-irrelevant overlay fields (`trace_id`, `request_id`,
> `evidence_summary`; per-pattern `canonical_id`, `vtype`) are **not** required
> in the JSON — ingest fills deterministic placeholders that never affect output.

## Optional additive fields (0.2.2)

| field | type | notes |
|-------|------|-------|
| `coaching` | object | structured coaching dict; absent in pre-Task-2 outputs |

`coaching` sub-fields (when present):

| sub-field | type | notes |
|-----------|------|-------|
| `block` | str | coaching text extracted from the report |
| `pattern_id` | str \| null | primary pattern addressed; null if none resolved |
| `note` | str \| null | out-of-scope/skip message; null here — Task 5 (mira-coach) fills it |

> **CRITICAL**: `coaching` is a top-level field only. It is **never** passed into
> `CVVerificationOverlay` (which uses `extra="forbid"`). Use `ingest_coaching(data)`
> to retrieve it separately from `ingest(data)`.

> schema_version is unchanged at `"0.2.2"` — this field is purely additive.

## Example

```json
{
  "schema_version": "0.2.2",
  "input": "I keep failing because I'm just not smart enough",
  "route_vtype": "A",
  "report": "## Diagnostic Summary ...",
  "patterns": [
    {"pattern_id": "willpower_blame", "lane2_status": "not_run", "evidence_trace": ["[L3] self-blame cue"]}
  ],
  "psr": {"P": "low metacognitive confidence", "S": "avoidance", "R": "give up"},
  "overlay_status": "needs_review",
  "lane1_pass": true
}
```
