---
name: mira-coach
description: >-
  Run coaching (stage 4) on a MIRA diagnosis JSON produced by
  mira-diagnose-verify and emit the same JSON with a structured `coaching`
  key added. Unsupported patterns receive an explicit out-of-scope note —
  never a silent skip. Use when the user has a diagnosis JSON and wants
  coaching output, or wants to chain diagnose → coach in a pipeline.
---

# mira-coach

Add structured coaching to a MIRA diagnosis JSON.

## When to use

Trigger this skill when the user has a diagnosis JSON from `mira-diagnose-verify`
(or `python -m mira --format json`) and wants:

1. **structured coaching** for the detected cognitive pattern (`coaching.block`,
   `coaching.pattern_id`), or
2. **explicit out-of-scope marking** when the detected pattern has no coaching
   template yet (see §5 honesty rule below).

Do not trigger for raw learner text — run `mira-diagnose-verify` first to get
the diagnosis JSON.

## Input contract

Input must be a diagnosis JSON produced by `mira-diagnose-verify`:

| key | description |
|-----|-------------|
| `schema_version` | must be `"0.2.2"` |
| `input` | the original learner claim text (required for coaching) |
| `route_vtype` | verification type (`I` / `A` / `D`) |
| `psr` | `{P, S, R}` PSR decomposition |
| `patterns` | list of `{pattern_id, lane2_status, evidence_trace}` |
| `overlay_status` | overall verdict |
| `evidence_summary` | aggregated evidence text |

The `coaching` and `report` keys must be absent (pre-coaching stage output).

## Output contract

The output is the **input JSON with one key added**: `coaching`.

```json
{
  "schema_version": "0.2.2",
  "input": "...",
  ...all original diagnosis keys preserved...,
  "coaching": {
    "block": "## Coaching\n\n...",
    "pattern_id": "fluency_illusion",
    "note": null
  }
}
```

### `coaching` sub-fields

| field | description |
|-------|-------------|
| `block` | Coaching text (Socratic prompts + action invitation) |
| `pattern_id` | Primary pattern addressed; `null` if none resolved |
| `note` | `null` for a supported pattern OR no clear match; out-of-scope message for a resolved-but-unsupported pattern (disambiguate via `pattern_id` — see below) |

> **`note=null` is ambiguous on its own** — it covers two distinct cases.
> Consumers must read `pattern_id` to tell them apart:
>
> | `pattern_id` | `note` | meaning |
> |--------------|--------|---------|
> | set | `null` | supported pattern — coaching provided in `block` |
> | `null` | `null` | **no clear match** — no pattern evidenced; `block` carries no-match guidance |
> | set | out-of-scope message | a pattern was resolved but has **no coaching template** |

### Honesty rule (§5) — ZERO silent skip

If a pattern **is resolved but has no coaching template**, `coaching.note` is set to:

```
"out of v0.x scope: pattern '<id>' has no coaching template"
```

It is never silently left as `null`. A silent skip is a P1 honesty violation.
(The "no clear match" case — `pattern_id=null` — is distinct: there is no
resolved pattern to mark out-of-scope, so `note` stays `null`.)

Supported patterns (v0.x): `fluency_illusion`, `false_dilemma`,
`oversimplified_cause`, `sunk_cost`, `effort_heuristic`, `willpower_blame`.

## 2-step CLI usage contract

```bash
# Step 1 — diagnose reasoning text
python skills/mira-diagnose-verify/scripts/diagnose.py \
    "I failed because I'm not smart enough." \
    > diag.json

# Step 2 — add coaching
python skills/mira-coach/scripts/coach.py < diag.json > coached.json
# or equivalently:
python skills/mira-coach/scripts/coach.py diag.json > coached.json
```

Language flag:

```bash
python skills/mira-coach/scripts/coach.py --lang ko < diag.json > coached_ko.json
```

## API

```python
# scripts directory must be on sys.path
import coach
coached_dict = coach.coach(diag_json_dict, lang="en")
```

`coach(diag_json, *, lang="en") -> dict`

Accepts the diagnosis JSON as a Python `dict`. Returns the same dict with
`coaching` added. Input dict is never mutated (immutability).

## Structure

- `scripts/coach.py` — thin wrapper: reconstructs `DiagnoseResult` from the
  diagnosis JSON → calls `mira.pipeline.coach_from_overlay` → returns input
  dict with `coaching` added (additive, not re-serialized from scratch).

## Design notes

- **Thin wrapper only**: all coaching and honest-skip logic lives in
  `mira.pipeline.coach_from_overlay` (engine). `coach.py` contains no
  coaching logic of its own.
- **Additive output**: the input JSON is preserved exactly; `coaching` is
  added as a new top-level key. This avoids a third from-scratch serializer
  (DRY — only `diagnose.py` and `mira/__main__.py` serialize from pipeline
  output; `coach.py` reuses the diagnosis JSON directly).
- **Reconstruction**: the diagnosis JSON lacks `lane1_pass` (set by
  `run_reduced_critic` inside `coach_from_overlay`). A `lane1_pass=True`
  placeholder is used; `coach_from_overlay` overwrites it immediately.
- **Immutability**: input dict is never mutated; `coach()` returns a new dict.
- **Pattern**: mirrors `mira-diagnose-verify` conventions — argparse, stdin
  or file input, JSON stdout, errors to stderr + exit 1.
