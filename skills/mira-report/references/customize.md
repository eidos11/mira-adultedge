# Customize the HTML report — mira-report

The `customize` mode helps you produce a branded or restyled HTML report
without changing the skill's logic or the diagnostic content.

## Steps

1. Copy the template into your project:
   ```bash
   cp assets/templates/report.html my-report-template.html
   ```
2. Edit the inline `<style>` block (or the surrounding structure). Keep the two
   placeholders intact:
   - `{{BODY}}` — replaced with the rendered report body (HTML).
   - `{{LANG}}` — replaced with the output language (`en` / `ko`).
3. Point the render at your template — the render stage reads
   `assets/templates/report.html`, so swap that file or adapt `_TEMPLATE_PATH`
   in `scripts/render.py`.

## What you can change

- Colors, fonts, spacing in the inline `<style>` (inline keeps it self-contained).
- Header / footer text around `{{BODY}}`.
- A logo — embed it as an inline `data:` URI to stay single-file.

## What to keep

- The `{{BODY}}` and `{{LANG}}` placeholders (render substitution points).
- Self-containment: avoid external CSS/JS/font URLs so the report stays one file.

## What is intentionally not customizable here

The report **content** — sections, lane2 badges, and safety gating — comes from
the ① renderer `mira.report.render_report_markdown`. Keeping content out of the
template preserves calibration and the safety invariants (no verdict language,
no willpower blame). Customize presentation, not diagnosis.
