# Contributing to MIRA AdultEdge

Thank you for your interest in contributing to MIRA AdultEdge.

## Current Status

MIRA is in its early public phase (v0.2.x). The core diagnostic architecture is stabilizing, and we welcome contributions in the following areas:

- **Bug reports** — Open an issue with reproduction steps
- **Documentation improvements** — Typo fixes, clarity improvements, additional examples
- **Test cases** — New diagnostic scenarios, edge cases, bilingual input coverage
- **Feature discussions** — Open an issue before submitting code PRs

Code PRs require an issue-first discussion. The diagnostic patterns, coaching content, and theory specifications are maintained by the project owner and are not open for direct modification without prior discussion.

## Development Setup

```bash
git clone https://github.com/eidos11/mira-adultedge.git
cd mira-adultedge

# Recommended: uv (lockfile-pinned, matches README)
uv sync --all-extras
python -m pytest

# Or with pip/venv:
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest
```

### Optional Dependencies

```bash
pip install -e ".[prolog]"   # Lane 2: SWI-Prolog required separately
pip install -e ".[llm]"     # Lane 3: API key required in .env
```

## Code Standards

- Python 3.12+, Pydantic v2 strict mode
- All tests must pass: `python -m pytest`
- No hardcoded API keys or absolute paths
- English for all code comments, docstrings, and error messages
- Korean regex patterns in diagnostic code are intentional (bilingual NLP)

## Test Discipline

Tests must remain deterministic. No live network calls in the test suite. LLM tests use recorded fixtures. If a contribution adds a test that requires a live API key, it cannot land.

## Language Policy

- All public-facing code and documentation: **English only**
- Korean keywords in diagnostic regex/patterns: **retained** (bilingual input processing)
- `--lang ko` CLI option preserves Korean output for Korean-speaking users

Korean text appears intentionally in three places throughout the codebase: (1) NLP regex patterns and keyword lists that detect Korean learner input, (2) i18n dictionaries (`_STRINGS["ko"]`, `_LABELS["ko"]`) that provide Korean UI output when `--lang ko` is active, and (3) test files that verify the Korean input pipeline with Korean learner utterances. These are core to MIRA's bilingual diagnostic capability and should not be converted to English.

## Releases

Before tagging a release, run `python tools/stats.py --write --yes` to refresh injected counts; CI `--check` enforces this on every PR.

## License

By contributing, you agree that your contributions will be licensed under the MIT License (code) and CC BY 4.0 (theory and design documents).
