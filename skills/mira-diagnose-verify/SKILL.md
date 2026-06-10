---
name: mira-diagnose-verify
description: >-
  diagnosis + cross-model verification of reasoning text
---

# mira-diagnose-verify

Run stages 1-3 of the MIRA pipeline (diagnosis + System B verification) on
reasoning text and emit a structured diagnosis JSON — **without coaching**.

The coaching stage is intentionally absent: this skill produces the pre-coaching
overlay so a caller can inspect, store, or pipe the diagnosis into `mira-coach`
(skill ④) to obtain the full coaching response.

## When to use

Trigger this skill when the user wants to:

1. **diagnose** reasoning text for cognitive patterns (PSR decomposition, pattern
   matching, System B overlay) without generating coaching output yet, or
2. **pipe** the diagnosis JSON into `mira-coach` for the full coached response.

Do not trigger for users who want a complete report in one step — run
`python -m mira --format json "<text>"` followed by `mira-report` for that.

## Output contract

The diagnosis JSON contains:

| key | description |
|-----|-------------|
| `schema_version` | contract version (mirrors `mira.report.SCHEMA_VERSION`) |
| `input` | the original learner text |
| `route_vtype` | verification type (I / A / C / …) |
| `psr` | `{P, S, R}` PSR decomposition |
| `patterns` | list of `{pattern_id, lane2_status, evidence_trace}` |
| `overlay_status` | overall verdict: `verified` / `structural_mismatch` / `insufficient_evidence` |
| `evidence_summary` | aggregated evidence text |

**Coaching is absent.** Keys `coaching` and `report` are intentionally omitted.

## 2-step CLI usage contract

```bash
# Step 1 — diagnose reasoning text, emit pre-coaching JSON
python skills/mira-diagnose-verify/scripts/diagnose.py \
    "I failed because I'm not smart enough." \
    > diag.json

# Step 2 — pipe into mira-coach (skill ④) to obtain coaching
python skills/mira-coach/scripts/coach.py < diag.json > coached.json
```

Or via stdin in step 1:

```bash
echo "I failed because I'm not smart enough." | \
    python skills/mira-diagnose-verify/scripts/diagnose.py --stdin \
    > diag.json
```

Language flag:

```bash
python skills/mira-diagnose-verify/scripts/diagnose.py \
    --lang ko "시험에 떨어진 것은 내가 머리가 나빠서다." \
    > diag_ko.json
```

## Structure

- `scripts/diagnose.py` — thin wrapper: calls `mira.pipeline.diagnose_only`,
  serializes the diagnosis-subset JSON (no `report`, no `coaching`) to stdout.

## Design notes

- **Thin wrapper only**: all diagnosis logic lives in `mira.pipeline.diagnose_only`
  (stages 1-3). This script delegates entirely; it contains no engine logic.
- **Coaching absent by design**: `DiagnoseResult` has no `report` or `coaching`
  field. The serializer (`_build_diagnose_json`) explicitly omits them.
- **Pattern**: mirrors `mira-report` skill's script conventions — argparse,
  stdin-or-positional input, JSON stdout, error to stderr + exit 1.
- **Schema version**: reuses `mira.report.SCHEMA_VERSION` ("0.2.2") so
  downstream tools (`mira-report`, `mira-coach`) can gate on the same version.
