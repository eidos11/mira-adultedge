# Changelog

All notable changes to MIRA AdultEdge will be documented in this file.

## [0.3.0] - 2026-07-14 (Research: MIRA-core theory publication)

### Added
- `research/THEORY.md` — the MIRA-core theory-to-system specification lands:
  states the Provisional Interpretive Judgment theory and the system contract
  in one place, with the three-axis model, corpus governance, and falsifiable
  commitments.
- `research/axis2-spec.md` — Axis 2 normative specification (motivated
  appraisal and judgment distortion), the theoretical bridge between System A
  (diagnosis) and System B (verification); companion to `THEORY.md`.
- `research/AE_17pattern_evidence_registry.md` — draft evidence registry
  mapping the diagnostic pattern taxonomy to cognitive-science sources
  (Anderson ACT/ACT-R, Kahneman), a companion reference to the theory
  documents above.
- Cross-references to the newly published theory documents in `README.md`,
  `VISION.md`, `research/README.md`, and the live dashboard footer.

### Notes
- Documentation/research release — no code, spec enforcement, or safety-gate
  changes. `spec/system_b/false_dilemma.yaml` and `oversimplified_cause.yaml`
  gained reference-only comments pointing `psr_coaching_target` readers to the
  authoritative coaching-template SSOT and to `THEORY.md` §7.1; the enforced
  values themselves are unchanged.
- Tests: 596 passed, 2 skipped (undistributed third-party fixtures), CI-gated
  zero failures — unchanged from 0.2.5.

## [0.2.5] - 2026-07-14 (Lane 2/3 robustness + Codex subscription env)

### Fixed
- **Lane 3 truncation salvage** — a long extraction response cut off mid-array
  (or wrapped in an unclosed code fence) no longer drops the whole extraction;
  the complete pattern objects that did arrive are recovered from the partial
  response. The output-token ceiling is raised to 4096 (a ceiling, not a charge —
  only generated tokens are billed) to avoid the truncation in the first place.
- **False-dilemma vacuous verification** — the rule now requires at least two
  options actually on the table (`option_count >= 2`), so a rhetorical
  "not X but Y" marker with nothing listed no longer verifies vacuously.
- **Lane 2 diagnostics readability** — a non-fatal Lane 2 degradation now logs a
  human-readable reason ("Lane 2 verification unavailable …") instead of a bare
  `lane2.error` token; the structured `error_type` / `backend` fields are
  preserved for structured log consumers.

### Changed
- **Codex subscription hygiene** — Codex CLI subprocesses (Lane 2 and Lane 3) now
  run with `OPENAI_API_KEY` stripped from their environment, so Codex always
  authenticates via the ChatGPT subscription and never silently switches to
  per-token API-key billing.

### Notes
- Safety gates unchanged (`safety_patterns`, invariants, enums untouched) — the
  fixes address robustness and diagnostics, not the verification gates.
  Calibration honesty is preserved: a Lane 2 run-to-run flip only ever downgrades
  a verdict to *tentative*, never produces a false "verified" (now documented in
  the README).
- Tests: 596 passed, 2 skipped (undistributed third-party fixtures), CI-gated
  zero failures.

## [0.2.4] - 2026-06-15 (Lane-1 specificity + Korean coaching restoration)

### Fixed
- **Lane-1 detection specificity** — healthy, well-structured reasoning no
  longer receives undifferentiated pattern coaching. Inputs without distortion
  signals now route to a "Class B" observation (no pattern coaching needed),
  removing Barnum-style false positives and learner-as-person praise. Coaching
  selection is now signal-based (`mira/system_b/engine/lane1_cues.py`) rather
  than alphabetical / input-invariant.
- **Korean coaching** — Korean input now emits pattern-specific coaching
  end-to-end. Earlier versions fell back to a conservative safe-report because
  the coaching lead collided with the verdict-token safety gate; the lead is
  rewritten token-free so the gate is preserved without suppressing coaching.

### Notes
- Safety gates unchanged (`safety_patterns`, invariants, enums untouched) — the
  fixes adjust coaching content, not the verification gates. Calibration honesty
  is preserved.
- Tests: 584 passed (11 new specificity / cue-routing cases), CI-gated zero
  failures.

## [0.2.3] - 2026-06-11 (Research corpus landing)

### Added
- `research/howstudy/` — the Howstudy guide corpus lands: the complete English
  adult-learning guide behind Domain Pack v1 (revised edition; front matter,
  16 chapters, appendices A–E, grouped by part), the core part of its Korean
  source edition (각론 §6–§9; the full Korean edition is reserved for
  publication), and the 2003–2007 origin documents (HS-ogn). Licensed
  CC BY-NC 4.0 as a directory-level exception to the CC BY 4.0 content
  license, with additional permissions (CC+) allowing commercial use of
  excerpts and transformative adaptations for HS-ogn and the English
  edition (`research/howstudy/LICENSE`).
- README `Contact` section (email · Notion profile · LinkedIn); LinkedIn
  added to VISION collaboration section

### Fixed
- LICENSE-CONTENT scope list referred to `reference/` — the published
  directory is `research/`

## [0.2.2] - 2026-06-10 (Pre-publication review fixes)

Corrections from a three-party independent pre-publication review (author /
Claude Code / GPT) conducted on the private repository before the public
switch.

### Added
- `skills/` — the three Anthropic Agent Skills documented in README were
  missing from the initial packaging
- Self-authored eval fixtures referenced by tests (third-party-derived
  fixtures are not redistributed; the affected tests skip with an explicit
  reason)
- Honesty note on Korean-language support: Korean input detection and report
  rendering are implemented, but end-to-end Korean coaching output is still
  being validated in v0.x

### Changed
- Published test count is now the collected count under a zero-failure gate,
  identical in every environment that runs the suite cleanly
- Dashboard: schema_version sample updated to 0.2.2, verification wording
  aligned with actual behavior (unverified candidates are explicitly marked
  tentative), pattern-legend counting clarified
- README: Lane 1 check list corrected (3 content + 3 structural checks),
  non-clinical scope statement added, model availability caveat added
- SECURITY: data-handling statement now states provider-side processing
  explicitly when external LLM lanes are opted in

### Fixed
- LICENSE / LICENSE-CONTENT pointed to a stale path for the CC BY 4.0
  coaching content (`mira/system_a/coaching/*.yaml`)
- `pip install -e .` failed on setuptools flat-layout auto-discovery
  (explicit package discovery added); CI is green on both workflows
- `--stage` CLI flag removed — it was accepted but never reached the pipeline

## [0.2.1] - 2026-06-10 (First Public Release)

### Added
- PSR (Premise-Strategy-Result) diagnostic framework for learner text analysis,
  built on the author's original theory of hypothetical judgment
- 3-lane verification architecture: rule-based critic checks (Lane 1) +
  Prolog formal rules (Lane 2) + LLM candidate extraction (Lane 3)
- Lane 2 neurosymbolic bridge: LLM feature extraction feeding Prolog
  3-valued verdicts (`accept` / `reject` / `unverified`)
- System A diagnostic engine with 3-axis analysis (metacognition, learning
  stage, task definition)
- 21-pattern judgment distortion registry — 19 core + 2 extension patterns
  (one further candidate under review, not counted); 6 patterns with dedicated
  coaching content
- Agent Skills: `mira-diagnose-verify` (diagnosis + cross-model verification),
  `mira-coach` (coaching overlay), `mira-report` (HTML / expert / customize
  rendering)
- CLI interface: `python -m mira "text"` with English/Korean support
- Output formats: `--format json` (versioned schema) and `--format report`
  (expert Markdown with per-lane verification status)
- Bilingual input processing (English + Korean) and i18n report output
  (`--lang en/ko`)
- Theory-grounded coaching for each actively detected pattern
- Public dashboard (GitHub Pages, `docs/index.html`)
- 575 automated tests collected — as distributed, 555 passing, 20 skipped
  (skips: optional SWI-Prolog runtime absent, plus two third-party-derived
  eval fixtures that are not redistributed); deterministic, no live API calls
- CI: pytest workflow + documentation statistics check (`tools/stats.py`
  computes public counts from one source and verifies them)
- MIT license (code) + CC BY 4.0 (theory/design content)
- Academic citation support (CITATION.cff with ORCID)

### Architecture
- Contract-enforced safety: no verdict language, no willpower blame
- Single LLM consent gate: `MIRA_ENABLE_LANE3` opts in both Lane 2 feature
  extraction and Lane 3; without it no external calls are made and no learner
  text leaves the machine
- Optional LLM backends: Codex CLI (default), OpenAI GPT, Anthropic Claude
- Pydantic v2 strict mode throughout
- Dual licensing: MIT for code, CC BY 4.0 for theory/design (SPDX:
  `MIT AND CC-BY-4.0`)

### Documentation
- VISION.md: research foundation, honest statistics with method notes, the
  mira-core bigger picture (4-layer architecture and Domain Pack lineage),
  roadmap, and collaboration channels
- README maturity matrix: component-by-component honest status
- Pattern registry with per-pattern definitions and D/I/A classification
- LLM backend selection guide (use-case balanced, including excluded models)

### Configuration
- `.env.example` template documenting the consent gate and backend selection
- Lane 2/3 LLM calls auto-skipped unless `MIRA_ENABLE_LANE3` is set
- Learning stage selection: `--stage concept|framework|practice|reality`

### Known Limitations
- Lane 2 (Prolog): 2 of 21 patterns have formal rules with a verified accept
  path; remaining patterns rely on Lane 1+3
- Lane 3 (LLM): requires explicit opt-in and a configured backend; without it,
  detection is limited to Lane 1+2
- Dedicated coaching content covers 6 of 21 patterns; others return generic
  guidance
- Input: single-text analysis only; multi-turn conversation not supported
- Research Preview: APIs may change between versions
