---
name: mira-report
description: >-
  Render a MIRA diagnostic JSON (from `python -m mira --format json`) into a
  shareable report: a self-contained HTML page (html mode), an expert Markdown
  report matching the 7 sections of `mira --format report` (expert mode), or scaffold a custom
  template (customize mode). Use when the user has a MIRA AdultEdge diagnostic
  JSON and wants a formatted or shareable report, an HTML view of a diagnosis,
  or wants to customize the report layout.
---

# mira-report

Turn a MIRA AdultEdge diagnostic JSON into a formatted report.

## When to use

Trigger this skill when the user has a diagnostic JSON from
`python -m mira --format json "<text>"` and asks to:

1. produce a **self-contained HTML** report to view or share (`html`),
2. get an **expert Markdown** report — same 7 sections as
   `mira --format report` (`expert`), or
3. **customize** the HTML template for their own layout (`customize`).

Do not trigger for raw learner text (run `mira` first to get the JSON) or for
plain text/JSON output already produced by the CLI.

## Input contract

Input must be a diagnostic JSON with `schema_version: "0.2.2"`. Older or missing
versions are rejected with regeneration guidance (fail-closed). See
[references/input-schema.md](references/input-schema.md).

## Modes

| mode | output | how |
|------|--------|-----|
| `html` | self-contained **visual** HTML — evidence highlight, verdict badges, confidence gauge, lane badges | ingest → overlay **direct** visual render (md only for the safety fallback) |
| `expert` | expert Markdown, 7 sections | ingest → `mira.report.render_report_markdown` (same 7 sections as `mira --format report`; the CLI additionally appends a runtime `lanes active` line) |
| `customize` | guidance to copy/edit the template | see [references/customize.md](references/customize.md) |

`summary` / `batch` are future extensions — add one table row + one reference.

## Usage

```bash
# 1) generate a diagnostic JSON
python -m mira --format json "I keep failing because I'm just not smart enough" > diag.json

# 2) render it
python -c "
import json, sys; sys.path.insert(0, 'scripts')
import render
print(render.render(json.load(open('diag.json')), mode='html'))
" > report.html
```

API: `render(data: dict, mode='html', lang='en') -> str`
— `mode` ∈ {`html`, `expert`, `customize`}, `lang` ∈ {`en`, `ko`}.

## Structure

- `scripts/ingest.py` — schema_version gate + overlay rebuild
- `scripts/render.py` — mode routing + dependency-free MD→HTML
- `assets/templates/report.html` — inline-CSS HTML shell (`{{BODY}}`, `{{LANG}}`)
- `references/` — input schema, customize guide

## Design notes

- **expert reuses the ① renderer** (`mira.report.render_report_markdown`), so the
  7 report sections are identical to `mira --format report`. The CLI additionally
  appends a runtime `- lanes active:` line (execution provenance from
  `_detect_lanes()`) that the skill omits — a re-render has no live lane context.
  DRY holds on the report body.
- **fail-closed schema gate**: an unsupported `schema_version` raises an
  explicit error with regeneration guidance — never a silent best-effort parse.
- Dependency-free beyond `mira` itself (pydantic + PyYAML); no Markdown library.
- **html is a distinct visual renderer**, not a md mirror — it reads the overlay
  directly to highlight evidence in the Input, color-code verdict badges, draw a
  confidence gauge, and tag verification lanes. Safety (violation / verdict-language
  gate) is delegated to `render_report_markdown` (SSOT).
