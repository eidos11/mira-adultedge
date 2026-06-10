# Changelog

All notable changes to MIRA AdultEdge will be documented in this file.

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
