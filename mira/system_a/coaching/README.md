# System A Coaching

Pattern-specific coaching content and its loader:

- `coaching_content.yaml` — Socratic 3-stage coaching templates per pattern (CC BY 4.0)
- `theory_templates.yaml` — theory-grounding templates (ACT-R / Kahneman / educational psychology, CC BY 4.0)
- `coaching.py` — loader that fills the additive `coaching` field on diagnosis results

Coaching is deterministic (template-based) in v0.x; adaptive, context-sensitive
Socratic dialogue is on the roadmap (see VISION.md). For the agent-facing
interfaces, see the real Agent Skills under the repository-level `skills/`.

The Socratic 3-stage scaffold follows the guided-discovery tradition (applied
non-clinically): Padesky, C. A. (1993). *Socratic questioning: Changing minds
or guiding discovery?* Keynote address, European Congress of Behavioural and
Cognitive Therapies, London.
