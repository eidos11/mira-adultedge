"""Fuzzy fidelity grounding tests for ``bridge._fidelity_check``.

Plan: design/2026-06-08-fidelity-fuzzy-grounding-implementation-plan.md (v0.2).
Replaces exact-substring grounding with a 3-stage fuzzy check so that
legitimate LLM paraphrase quotes (ellipsis, normalization, summarization)
are accepted as grounded, while hallucinated quotes stay blocked.

Two test families:
- *Drive* (fail against current exact-substring): legitimate paraphrase must
  now ground (RED-A/B/E-hi/D/causes).
- *Guard / preservation* (already green; must STAY green): hallucination,
  vacuous-pass, short-token FP, and existing exact behavior.

Threshold T = 0.55 (Mnemo-approved, FP-averse). See plan §1.
"""

from __future__ import annotations

from mira.system_b.lane2 import bridge


def _opts(*quotes: str) -> dict:
    """Minimal extracted dict for false_dilemma (options_analysis)."""
    return {"options_analysis": {"options_listed": list(quotes)}}


def _causes(*quotes: str) -> dict:
    """Minimal extracted dict for oversimplified_cause (causal_analysis)."""
    return {"causal_analysis": {"causes_listed": list(quotes)}}


# ── Stage 1: normalized substring ──────────────────────────────────────────

def test_stage1_exact_substring_still_grounded():
    """RED-F5 (preservation): existing exact matches stay grounded (superset)."""
    text = "I could study harder or just give up entirely."
    extracted = _opts("study harder")
    assert bridge._fidelity_check(text, "false_dilemma", extracted) == "ok"


def test_stage1_normalizes_punctuation_difference():
    """RED-F6 (drive): comma/whitespace-only difference grounds via normalize."""
    text = "I study, work, and rest daily."
    extracted = _opts("I study work and rest daily")  # no commas
    assert bridge._fidelity_check(text, "false_dilemma", extracted) == "ok"


# ── Stage 2: ellipsis / clause split ───────────────────────────────────────

def test_stage2_ellipsis_pieces_grounded():
    """RED-A (drive): ellipsis quote grounds when each piece is in the text."""
    text = "Every time I hit a formula in the textbook I freeze completely."
    extracted = _opts("Every time I hit a formula ... I freeze")
    assert bridge._fidelity_check(text, "false_dilemma", extracted) == "ok"


# ── Stage 3: content-token overlap (T = 0.55) ──────────────────────────────

def test_stage3_paraphrase_above_threshold_grounded():
    """RED-B (drive): summarized paraphrase (overlap 0.75) grounds via Stage 3."""
    text = "I could attempt video courses or study the documentation thoroughly."
    # tokens {attempt, video, tutorials, documentation}; 3/4 = 0.75 in text.
    extracted = _opts("attempt video tutorials documentation")
    assert bridge._fidelity_check(text, "false_dilemma", extracted) == "ok"


def test_stage3_boundary_overlap_060_grounded():
    """RED-E-hi (drive): overlap 0.60 (>= 0.55) grounds."""
    text = "alpha bravo charlie delta echo foxtrot golf"
    # {alpha,bravo,charlie,xray,yankee}; 3/5 = 0.60.
    extracted = _opts("alpha bravo charlie xray yankee")
    assert bridge._fidelity_check(text, "false_dilemma", extracted) == "ok"


def test_stage3_boundary_overlap_050_unverified():
    """RED-E-lo (guard): overlap 0.50 (< 0.55) stays blocked."""
    text = "alpha bravo charlie delta echo foxtrot golf"
    # {alpha,bravo,xray,yankee}; 2/4 = 0.50.
    extracted = _opts("alpha bravo xray yankee")
    assert bridge._fidelity_check(text, "false_dilemma", extracted) == "unverified"


def test_causes_listed_paraphrase_grounded():
    """Drive: causal_analysis path grounds a paraphrase (overlap 1.0)."""
    text = "The failure happened because of poor planning and limited resources."
    extracted = _causes("poor planning limited resources")
    assert bridge._fidelity_check(text, "oversimplified_cause", extracted) == "ok"


# ── Hallucination defense (guards) ─────────────────────────────────────────

def test_hallucination_unrelated_unverified():
    """RED-C (preservation): fabricated, unrelated quote stays blocked."""
    text = "I could study harder or just give up entirely."
    extracted = _opts("buy a new sports car this weekend")
    assert bridge._fidelity_check(text, "false_dilemma", extracted) == "unverified"


def test_short_quote_two_tokens_not_grounded_by_overlap():
    """RED-C2 (guard): a 2-content-token quote must NOT pass via Stage 3.

    Both tokens appear in the text (non-contiguous), so a naive overlap would
    be 2/2 = 1.0. The min-content-token guard (>=3) must prevent grounding.
    """
    text = "alpha bravo charlie delta echo foxtrot golf"
    extracted = _opts("alpha foxtrot")  # 2 tokens, both present but not adjacent
    assert bridge._fidelity_check(text, "false_dilemma", extracted) == "unverified"


# ── Edge cases (guards / preservation) ─────────────────────────────────────

def test_empty_quote_skipped_grounded():
    """RED-F1 (preservation): empty/whitespace quote is skipped (grounded)."""
    text = "I could study harder or give up."
    extracted = _opts("   ")
    assert bridge._fidelity_check(text, "false_dilemma", extracted) == "ok"


def test_punctuation_only_quote_not_vacuously_grounded():
    """RED-F2 (guard): punctuation-only quote (normalizes to empty) is NOT grounded.

    normalize("...") == "" must NOT vacuously satisfy `"" in text`.
    """
    text = "I could study harder or give up."
    extracted = _opts("...")
    assert bridge._fidelity_check(text, "false_dilemma", extracted) == "unverified"


def test_non_dict_block_treated_as_no_quotes():
    """RED-F3 (preservation): non-dict feature block yields no quotes -> grounded."""
    text = "I could study harder or give up."
    extracted = {"options_analysis": "not a dict"}
    assert bridge._fidelity_check(text, "false_dilemma", extracted) == "ok"


def test_multi_quote_one_hallucinated_unverified():
    """RED-F4 (preservation): if any quote is ungrounded, the whole check fails."""
    text = "I could study harder or give up entirely."
    extracted = _opts("study harder", "buy a sports car in another city")
    assert bridge._fidelity_check(text, "false_dilemma", extracted) == "unverified"


# ── Semantic drift (characterization — documents a known limitation) ───────

def test_semantic_drift_currently_passes_characterization():
    """RED-D (characterization): meaning-reversed paraphrase passes (lexical limit).

    fidelity is a LEXICAL grounding gate (plan §0.1). A quote that shares the
    content tokens but reverses meaning ({binary, middle, path}, 3/3 = 1.0)
    is grounded. Catching this is delegated to Prolog / extraction layers
    (plan §6). This test records current behavior, not desired blocking.
    """
    text = "I do not think it is binary because there is a middle path."
    extracted = _opts("it is binary there is no middle path")
    assert bridge._fidelity_check(text, "false_dilemma", extracted) == "ok"
