# MIRA AdultEdge

[![Tests](https://github.com/eidos11/mira-adultedge/actions/workflows/tests.yml/badge.svg)](https://github.com/eidos11/mira-adultedge/actions/workflows/tests.yml)
[![Code: MIT](https://img.shields.io/badge/code-MIT-green.svg)](LICENSE)
[![Content: CC BY 4.0](https://img.shields.io/badge/content-CC%20BY%204.0-lightgrey.svg)](LICENSE-CONTENT)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](pyproject.toml)

**Memory-Imagination-Reason Architecture for adult learning diagnosis and coaching.**

> Adult learners receive cognitive-science-grounded diagnosis of judgment biases
> from their own reasoning text, and improve judgment quality through
> pattern-specific differentiated coaching.

> MIRA does not diagnose personality, mental health, or learner ability; it
> surfaces candidate reasoning patterns for educational self-reflection.

> **Status: v0.x — Research Preview.** The full diagnostic pipeline runs
> end-to-end and is reproducible; verification coverage and output tooling are
> actively expanding. See [Maturity](#maturity) for an honest, component-by-component
> breakdown, [VISION.md](VISION.md) for the research foundation, roadmap, and
> collaboration, and the [live dashboard](https://eidos11.github.io/mira-adultedge/)
> for a one-page overview.

---

## What It Does

MIRA analyzes reasoning text to detect judgment biases and provides
theory-grounded coaching for improvement. It combines:

- **3-axis diagnosis** — metacognition, task definition, learning stage
- **21-pattern bias registry** — 19 core + 2 extension patterns (one further
  candidate under review, not counted) — built on the author's original judgment
  theory (PSR) and reinforced with cognitive-science anchors
- **3-lane matching** — rule-based critic checks, Prolog formal verification, LLM candidate extraction
- **Differentiated coaching** — Socratic 3-stage scaffold (guided discovery after Padesky 1993, applied non-clinically) with pattern-specific strategies (deterministic templates in v0.x; adaptive dialogue on roadmap)
- **Theory grounding** — ACT-R, Kahneman dual-process, educational psychology 3-layer templates


## Architecture

```
         Claim (reasoning text)
              |
         +----v----+
         | System A |  3-axis diagnosis: metacognition x task x stage
         | Diagnose |  -> PSR decomposition (Premise / Strategy / Result)
         +----+----+
              | PSRResult
         +----v----+
         | System B |  3-lane pattern matching:
         | Detect   |    Lane 1: Rule-based critic checks (always active)
         |          |    Lane 2: Prolog formal rules (optional)
         |          |    Lane 3: LLM candidate extraction (optional)
         +----+----+
              | MatchResult[]
         +----v----+
         | System A |  Coaching: pattern-specific content + theory templates
         | Coach    |  -> Final report with diagnosis + coaching + theory
         +---------+
```

## Agent Skills

MIRA exposes its diagnose → verify → coach pipeline as three Anthropic Agent Skills
(`skills/`) — thin agent interfaces over the Python engine, which holds all judgment logic:

| Skill | Input | Output |
|-------|-------|--------|
| `mira-diagnose-verify` | learner text | diagnosis JSON (PSR, pattern candidates, neurosymbolic verification overlay) |
| `mira-coach` | diagnosis JSON | same JSON with `coaching` filled (additive field) |
| `mira-report` | coached JSON | rendered report (`html` / `expert` / `customize`) |

The CLI (`python -m mira`) composes all three internally, so most users never invoke
them directly. Coaching uses deterministic 6-pattern templates — adaptive,
context-sensitive Socratic dialogue is on the roadmap (see [VISION.md](VISION.md)).

## Maturity

MIRA v0.x is a **research preview**: the full diagnose → detect → coach pipeline
runs end-to-end and is reproducible, with verification depth honestly bounded and
transparently reported.

| Component | Status | Detail |
|-----------|--------|--------|
| Pipeline (A→B→A) | ✅ operational | Full diagnose → detect → coach loop |
| Pattern registry | ✅ <!--stats:patterns-maturity-->21<!--/stats:patterns-maturity--> patterns | 19 core + 2 extension (+1 candidate under review) |
| Lane 1 — Rule-based critic | ✅ 6 checks | 3 content checks (#6, #7, #9) + 3 structural checks (#2, #3, #4), always active; willpower-blame blocking is enforced at report generation |
| Lane 2 — Prolog formal | 🟡 2 / <!--stats:patterns-verified-->21<!--/stats:patterns-verified--> deductively verified | `false_dilemma`, `oversimplified_cause` (neurosymbolic bridge) |
| Lane 3 — LLM extraction | 🟡 14 candidates | Stage-conditional priming across 4 stages (evidence-assisted, optional) |
| System A diagnosis | ✅ 3 axes | metacognition, task_definition, stage (interacting dimensions, not strictly orthogonal) |
| Coaching | ✅ 6 patterns | Socratic 3-stage structure (Padesky-inspired) — deterministic templates; adaptive dialogue on roadmap |
| Theory grounding | ✅ 3-layer | ACT-R + Kahneman + educational psychology |
| Tests | ✅ <!--stats:tests-->500+<!--/stats:tests--> passing | Unit + integration + dogfooding |

**What this means honestly:** 2 of 21 patterns have formal Prolog verification
(deductive); the remaining patterns operate through LLM-based candidate extraction
and rule-based contract checks. Likewise, pattern-specific coaching covers 6 of
21 patterns today — the remaining patterns receive diagnosis and theory grounding
without dedicated coaching templates. Expanding both is the primary roadmap
focus — see [VISION.md](VISION.md).

## Quick Start

```bash
# Requirements: Python 3.12
git clone https://github.com/eidos11/mira-adultedge.git
cd mira-adultedge

# Install with uv (recommended)
uv sync

# Or with pip
pip install -e .

# Run tests
python -m pytest tests/ -v

# Run the minimal diagnostic loop
python -c "
from mira.pipeline import run_minimal_loop
result = run_minimal_loop('I failed because I am just not smart enough.')
print(result.report)
"
```

For the full pipeline (Prolog verification + LLM extraction), opt in to
external LLM calls with `MIRA_ENABLE_LANE3=1` — see
[LLM Configuration](#llm-configuration).

### Sample output (trimmed)

```text
$ python -m mira "$(cat examples/sample_en.txt)"

## Diagnostic Summary
inductive verification was performed, but no clear match was found among
currently executable patterns. Any coaching below addresses unverified
candidates and is explicitly marked tentative.

## Evidence
**PSR Decomposition:**
- Premise (P): low metacognitive confidence with cues: fluency_illusion
- Strategy (S): noun_goal; suggested action frame: be able to explain the
  solution steps and solve similar problems
- Result (R): concept

## Coaching
This *may* point to the following — not a confirmed diagnosis; please check:
**false dilemma** — Your reasoning appears to narrow the option space to two
alternatives.
...
```

This run uses Lane 1 only (no LLM configured) — note the calibrated language:
hints are offered as *unconfirmed*, never as verdicts. `examples/` contains
English and Korean sample inputs.

## Bilingual Support

MIRA accepts learner input in both **English** and **Korean**. The diagnostic
engine includes bilingual regex patterns for pattern detection in both languages.

**English input** (default output language):

```bash
python -m mira "I failed because I am just not smart enough."
```

**Korean input** with Korean output:

```bash
python -m mira "시험에 떨어진다는 건 머리가 나쁜 거겠지..." --lang ko
```

Default output is English. Use `--lang ko` to switch the report output to Korean.
Korean regex patterns in code are intentional NLP features, not artifacts.

> **v0.x honesty note**: the English path is fully exercised end-to-end. Korean
> input detection and Korean report rendering are implemented, but end-to-end
> Korean coaching output is still being validated — Korean-language runs
> currently tend to produce a conservative safe-fallback report rather than
> pattern-specific coaching. Restoring full Korean coaching content is on the
> v0.x roadmap.

## LLM Configuration

MIRA uses a 3-lane architecture for pattern detection:

- **Lane 1 — rule-based critic checks**: always on, fully local, no LLM.
- **Lane 2 — Prolog formal verification**: the Prolog rules run locally, but the
  feature-extraction step that feeds them sends learner text to an LLM.
- **Lane 3 — LLM candidate extraction**: optional breadth layer (external LLM).

**Consent switch**: all external LLM calls are governed by a single opt-in,
`MIRA_ENABLE_LANE3=1` (off by default — the name is historical; it gates Lane 2
feature extraction *and* Lane 3). Until you set it, no learner text leaves your
machine: MIRA runs Lane 1 fully, and Lane 2 reports its patterns as `unverified`.

| Environment Variable | Purpose | Required |
|---------------------|---------|----------|
| `MIRA_ENABLE_LANE3` | Set to `1` to allow external LLM calls (Lane 2 extraction + Lane 3) | Optional |
| `MIRA_LLM_BACKEND` | Force a backend: `codex` / `openai` / `anthropic` / `none` (default: auto-detect) | Optional |
| `MIRA_LLM_MODEL` | Override the backend's default model | Optional |
| `OPENAI_API_KEY` | OpenAI API key (default model `gpt-5.4`) | Optional |
| `ANTHROPIC_API_KEY` | Anthropic API key (default model `claude-sonnet-4-6`) | Optional |

Backend auto-detect priority: **Codex CLI → OpenAI → Anthropic** (if both API
keys are set, OpenAI is picked first — force Anthropic with
`MIRA_LLM_BACKEND=anthropic`).

### Choosing a backend

| Backend | Cost | Character | Use it when |
|---------|------|-----------|-------------|
| **Codex CLI** (`gpt-5.5`) | no per-call billing (ChatGPT subscription; subject to its limits) | slower (~15s/call), conservative | you have the Codex CLI + a subscription — recommended default |
| **OpenAI** (`gpt-5.4`) | ≈ $0.004/call | fast (~4s), batch-friendly | API batch runs, cost-sensitive use |
| **Anthropic** (`claude-sonnet-4-6`) | ≈ $0.008/call | broad pattern recall | you want detection breadth |
| ~~`gpt-4o-mini` / `gpt-5.4-mini` / `-nano`~~ | — | insufficient quality (missed patterns in our tests) | do not use |

Model IDs and per-call costs reflect our internal tests at the time of writing
and change quickly — verify availability and pricing with your provider, and
override the default with `MIRA_LLM_MODEL` as needed.

No LLM at all? MIRA still runs — Lane 1 critic checks work free and instantly,
with reduced detection breadth (Lane 2 reports `unverified`, Lane 3 is skipped).

**Setup:**

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```
2. Set `MIRA_ENABLE_LANE3=1` and, for API backends, add a key. See
   [.env.example](.env.example) for the full template, including advanced
   overrides (`MIRA_LLM_EXTRACT_BACKEND` / `MIRA_LLM_EXTRACT_MODEL` for Lane 2,
   `MIRA_LANE2_ENABLED`).

## Project Structure

```
mira-adultedge/
├── mira/                    # Source code (MIT)
│   ├── pipeline.py          # A->B->A diagnostic pipeline
│   ├── psr/                 # PSR decomposition + D/I/A routing
│   ├── report.py            # Report generation
│   ├── contracts/           # Minimal contracts
│   ├── system_a/            # Diagnosis + coaching
│   │   ├── engine/          # 3-axis diagnostic engine
│   │   └── coaching/        # Coaching content + theory templates (CC BY 4.0)
│   └── system_b/            # Pattern detection
│       ├── engine/          # Matcher + critic
│       ├── lane2/           # Prolog runner + neurosymbolic bridge
│       └── lane3/           # LLM extractor
├── skills/                  # Agent Skills (mira-diagnose-verify, mira-coach, mira-report)
├── spec/                    # Pattern registry + invariants + enums (CC BY 4.0)
├── tests/                   # Test suite
├── examples/                # Sample inputs
└── research/                # Theory foundation & corpus (added progressively — see VISION.md)
```

> Code is **MIT**; knowledge content (theory, `spec/`, coaching/theory YAML) is
> **CC BY 4.0**. See [LICENSE](LICENSE) and [LICENSE-CONTENT](LICENSE-CONTENT).

## Testing

```bash
python -m pytest tests/ -v          # Full suite
python -m pytest tests/ -q          # Quick summary
python -m pytest tests/ --tb=short  # With short tracebacks
```

> **Note:** the neurosymbolic Prolog lane (17 tests) requires SWI-Prolog. Without
> it, those tests skip; install via `uv sync --all-extras` (with SWI-Prolog on
> PATH) to run the full suite.

## Contributing

We welcome contributions from cognitive scientists, software engineers, and
anyone interested in judgment bias detection. Please review and follow our
[Code of Conduct](CODE_OF_CONDUCT.md) when participating in this project.

### Development Setup

```bash
git clone https://github.com/eidos11/mira-adultedge.git
cd mira-adultedge
uv sync --all-extras              # install dependencies (dev, prolog, llm)
python -m pytest tests/ -v        # run the full test suite
cp .env.example .env              # configure optional API keys
```

Linting and formatting use `ruff` and `mypy` (configured in `pyproject.toml`) —
see [CONTRIBUTING.md](CONTRIBUTING.md) for the contribution workflow.

### How to Contribute

1. **Open an issue** describing the problem or enhancement you have in mind.
2. **Fork** the repository and create a feature branch (`git checkout -b feat/your-feature`).
3. **Write tests first** — the project follows a test-driven workflow (80%+ coverage target).
4. **Submit a PR** against `main` with a clear description and link to the issue.
5. Maintainers will review and may request changes before merging.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full contribution guide.

### Areas for Contribution

- **Prolog rules**: Only 2 of 21 patterns have formal rules — expand Lane 2 coverage.
- **New patterns**: Propose additional judgment distortion patterns with supporting literature.
- **Existing patterns & coaching**: refine pattern definitions, evidence criteria, and coaching content (`spec/`, coaching YAML — CC BY 4.0). No code required — domain expertise (cognitive science, education, coaching) is the scarce input here.
- **Translations**: Help localize coaching outputs and documentation beyond English and Korean.
- **Examples**: Add diagnostic examples (owned or synthetic) to `examples/`.

## License

This project uses a dual license:

- **Code** (`mira/`, `tests/`): [MIT License](LICENSE)
- **Knowledge content** — theoretical frameworks, design documents, the pattern
  registry (`spec/`), and coaching/theory knowledge files
  (`mira/system_a/coaching/*.yaml`): [CC BY 4.0](LICENSE-CONTENT)

When using the theoretical frameworks (PSR theory, 21-pattern taxonomy,
3-axis diagnostic model, coaching architecture) in academic or commercial
work, you must provide appropriate attribution to the original author.

## Citation

If you use MIRA or its theoretical frameworks in academic work, please cite:

```bibtex
@software{mnemo2026mira,
  author    = {Mnemo},
  title     = {MIRA AdultEdge: Cognitive Science-Based Diagnostic and Coaching Agent},
  year      = {2026},
  url       = {https://github.com/eidos11/mira-adultedge},
  note      = {Research preview. v0.x}
}
```

See [CITATION.cff](CITATION.cff) for machine-readable citation metadata.

## Contact

Questions, collaboration, or partnership inquiries: open an issue or
discussion on this repository, or email **eidos11@naver.com**.
Author profile: [Notion](https://mnemo.notion.site/global-profile) ·
[LinkedIn](https://www.linkedin.com/in/mnemofantasy).

## Disclaimer

> **Research Preview** — This is an active research project, not production
> software. APIs may change between versions. The diagnostic results are
> intended for educational self-reflection, not clinical or professional
> assessment.

## Roadmap

See [VISION.md](VISION.md) for the full research roadmap and collaboration, and
[CHANGELOG.md](CHANGELOG.md) for release history. In brief:

**Next (M2, ~v0.3.x):**
- Expand Lane 2 Prolog verification beyond the current 2 patterns
- Typed runtime contracts
- Additional System A axes (motive, time-energy, feedback, AI boundary)
- Output tooling: additional report formats + public dashboard deployment

**Future (toward v1.0 production):**
- Knowledge Layer Stack, full RAG pipeline
- End-to-end tracking system
- Multi-host formal verification
