"""Lane 2 Prolog verification bridge for MIRA M1 patch (SemVer 0.2.0).

Orchestrates Step 2 feature extraction (context-segregated from Lane 3 Step 1)
and Prolog verification. Routes to Codex CLI / OpenAI / Anthropic. Returns
dict[pattern_id → BridgeVerdict] with 3-valued verdict (accept/reject/unverified).
"""

from __future__ import annotations

import json
import logging
import os
import re
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from mira.system_b.lane2 import feature_schemas
from mira.system_b.lane2.patterns import SUPPORTED_PATTERNS  # SSOT (C6)

logger = logging.getLogger(__name__)

MIRA_LANE2_ENABLED: bool = os.environ.get("MIRA_LANE2_ENABLED", "true").lower() == "true"
MIRA_LLM_EXTRACT_BACKEND: str = os.environ.get("MIRA_LLM_EXTRACT_BACKEND", "")
MIRA_LLM_EXTRACT_MODEL: str = os.environ.get("MIRA_LLM_EXTRACT_MODEL", "")

_EXTRACT_BACKEND_DEFAULTS: dict[str, str] = {
    "codex": "gpt-5.5",
    "openai": "gpt-5.4",
    "anthropic": "claude-sonnet-4-6",
}

_STEP2_TIMEOUT: int = 30

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_PROLOG_RULES_DIR = _PROJECT_ROOT / "mira" / "system_b" / "rules" / "prolog"
_PATTERN_VERIFY_PL = _PROLOG_RULES_DIR / "pattern_verify.pl"
_PATTERN_PL: dict[str, Path] = {
    "false_dilemma": _PROLOG_RULES_DIR / "false_dilemma.pl",
    "oversimplified_cause": _PROLOG_RULES_DIR / "oversimplified_cause.pl",
}

BridgeVerdictValue = Literal["accept", "reject", "unverified"]


@dataclass(frozen=True)
class BridgeVerdict:
    pattern_id: str
    verdict: BridgeVerdictValue
    features: dict | None = None
    error: str | None = None


def run_lane2_bridge(
    learner_text: str,
    pattern_ids: list[str],
) -> dict[str, BridgeVerdict]:
    """Run Lane 2 verification bridge for detected patterns.

    Returns dict mapping pattern_id → BridgeVerdict.
    Patterns not in SUPPORTED_PATTERNS get verdict="unverified".
    If MIRA_LANE2_ENABLED is false, all patterns get "unverified".

    External LLM consent: the feature-extraction step sends learner text to
    an external LLM, so it shares the explicit opt-in with Lane 3
    (MIRA_ENABLE_LANE3=1). Without the opt-in, supported patterns return
    "unverified" and no external call is made.
    """
    if not MIRA_LANE2_ENABLED:
        logger.info("Lane 2 disabled via MIRA_LANE2_ENABLED=false")
        return {pid: BridgeVerdict(pattern_id=pid, verdict="unverified") for pid in pattern_ids}

    supported = [pid for pid in pattern_ids if pid in SUPPORTED_PATTERNS]
    unsupported = [pid for pid in pattern_ids if pid not in SUPPORTED_PATTERNS]

    results: dict[str, BridgeVerdict] = {
        pid: BridgeVerdict(pattern_id=pid, verdict="unverified") for pid in unsupported
    }

    if not supported:
        return results

    if os.environ.get("MIRA_ENABLE_LANE3") != "1":
        # Consent gate (same opt-in as Lane 3): feature extraction sends
        # learner text to an external LLM, which the docs promise never
        # happens without MIRA_ENABLE_LANE3=1.
        logger.info(
            "External LLM calls disabled (MIRA_ENABLE_LANE3 != 1) — "
            "Lane 2 feature extraction skipped; supported patterns unverified"
        )
        for pid in supported:
            results[pid] = BridgeVerdict(pattern_id=pid, verdict="unverified")
        return results

    backend, model = _resolve_extract_backend()
    if backend == "none":
        logger.info("No Lane 2 LLM backend available — all patterns unverified")
        for pid in supported:
            results[pid] = BridgeVerdict(pattern_id=pid, verdict="unverified")
        return results

    system_prompt = feature_schemas.get_system_prompt()
    user_prompt = feature_schemas.get_user_prompt(learner_text, supported)

    raw_json = _call_step2_with_retry(backend, model, system_prompt, user_prompt)

    if raw_json is None:
        for pid in supported:
            results[pid] = BridgeVerdict(
                pattern_id=pid,
                verdict="unverified",
                error="step2_extraction_failed",
            )
        logger.warning(
            "lane2.error",
            extra={"error_type": "step2_extraction_failed", "backend": backend},
        )
        return results

    extracted = _parse_and_validate_json(raw_json)

    if extracted is None:
        for pid in supported:
            results[pid] = BridgeVerdict(
                pattern_id=pid,
                verdict="unverified",
                error="step2_json_invalid",
            )
        logger.warning(
            "lane2.error",
            extra={"error_type": "step2_json_invalid", "backend": backend},
        )
        return results

    for pid in supported:
        if _fidelity_check(learner_text, pid, extracted) == "unverified":
            results[pid] = BridgeVerdict(
                pattern_id=pid, verdict="unverified", error="feature_fidelity"
            )
            continue
        results[pid] = _run_prolog_verify(pid, extracted, backend)

    return results


def _resolve_extract_backend() -> tuple[str, str]:
    """Resolve (backend, model) for Step 2. Auto-detects if env var unset.

    Reads MIRA_LLM_EXTRACT_BACKEND and MIRA_LLM_EXTRACT_MODEL from the
    environment AT CALL TIME (B5) so that test monkeypatches and runtime
    env changes take effect without reimporting the module. Falls back to
    module-level globals if the env var is not set (backward compat).
    """
    backend = (os.environ.get("MIRA_LLM_EXTRACT_BACKEND") or MIRA_LLM_EXTRACT_BACKEND).lower()
    model = os.environ.get("MIRA_LLM_EXTRACT_MODEL") or MIRA_LLM_EXTRACT_MODEL

    if backend in _EXTRACT_BACKEND_DEFAULTS:
        return (backend, model or _EXTRACT_BACKEND_DEFAULTS[backend])
    if backend == "none":
        return ("none", "")

    if shutil.which("codex"):
        return ("codex", model or _EXTRACT_BACKEND_DEFAULTS["codex"])
    if os.environ.get("OPENAI_API_KEY"):
        return ("openai", model or _EXTRACT_BACKEND_DEFAULTS["openai"])
    if os.environ.get("ANTHROPIC_API_KEY"):
        return ("anthropic", model or _EXTRACT_BACKEND_DEFAULTS["anthropic"])

    return ("none", "")


_FALLBACK_ORDER: list[str] = ["codex", "openai", "anthropic"]


def _call_step2_with_retry(
    backend: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
) -> str | None:
    """Call Step 2 LLM with 1 retry, then fallback to next available backend."""
    for attempt in range(2):
        result = _call_step2(backend, model, system_prompt, user_prompt)
        if result is not None:
            return result
        if attempt == 0:
            logger.warning(
                "lane2.error",
                extra={"error_type": "step2_attempt1_failed", "backend": backend},
            )

    for fallback in _FALLBACK_ORDER:
        if fallback == backend:
            continue
        fb_model = _EXTRACT_BACKEND_DEFAULTS.get(fallback, "")
        if fallback == "codex" and not shutil.which("codex"):
            continue
        if fallback == "openai" and not os.environ.get("OPENAI_API_KEY"):
            continue
        if fallback == "anthropic" and not os.environ.get("ANTHROPIC_API_KEY"):
            continue
        logger.info("lane2.fallback", extra={"from": backend, "to": fallback})
        result = _call_step2(fallback, fb_model, system_prompt, user_prompt)
        if result is not None:
            return result

    return None


def _call_step2(
    backend: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
) -> str | None:
    """Dispatch Step 2 call to the appropriate backend."""
    t_start = time.monotonic()
    raw: str | None = None

    try:
        if backend == "codex":
            raw = _call_codex_cli(system_prompt, user_prompt)
        elif backend == "openai":
            raw = _call_openai(system_prompt, user_prompt, model)
        elif backend == "anthropic":
            raw = _call_anthropic(system_prompt, user_prompt, model)
    except Exception:
        logger.warning("lane2.error", extra={"error_type": "backend_exception", "backend": backend}, exc_info=True)
        return None
    finally:
        duration_ms = int((time.monotonic() - t_start) * 1000)
        logger.info("lane2.latency", extra={"backend": backend, "duration_ms": duration_ms})

    return raw


def _call_codex_cli(system_prompt: str, user_prompt: str) -> str | None:
    """Call Codex CLI (GPT-5.5 via subscription)."""
    output_fd, output_path = tempfile.mkstemp(suffix=".txt", prefix="mira-lane2-")
    os.close(output_fd)

    try:
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        result = subprocess.run(
            [
                "codex", "exec",
                "-p", "cc",
                "-c", 'model_reasoning_effort="medium"',
                "--ephemeral",
                "--skip-git-repo-check",
                "-o", output_path,
                full_prompt,
            ],
            capture_output=True,
            text=True,
            timeout=_STEP2_TIMEOUT,
        )

        if result.returncode != 0:
            logger.warning(
                "lane2.error",
                extra={"error_type": "codex_nonzero_exit", "backend": "codex"},
            )
            return None

        with open(output_path) as f:
            text = f.read().strip()

        return text if text else None

    except FileNotFoundError:
        logger.warning("lane2.error", extra={"error_type": "codex_not_found", "backend": "codex"})
        return None
    except subprocess.TimeoutExpired:
        logger.warning("lane2.error", extra={"error_type": "step2_timeout", "backend": "codex"})
        return None
    finally:
        try:
            os.unlink(output_path)
        except OSError:
            pass


def _call_openai(system_prompt: str, user_prompt: str, model: str) -> str | None:
    try:
        import openai
    except ImportError:
        logger.warning("lane2.error", extra={"error_type": "openai_not_installed", "backend": "openai"})
        return None

    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        logger.warning("lane2.error", extra={"error_type": "openai_key_missing", "backend": "openai"})
        return None

    client = openai.OpenAI(api_key=api_key, timeout=_STEP2_TIMEOUT)
    uses_completion_tokens = model.startswith(("gpt-5", "o1", "o3", "o4"))
    token_param = "max_completion_tokens" if uses_completion_tokens else "max_tokens"

    response = client.chat.completions.create(
        model=model,
        **{token_param: 1024},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content or None


def _call_anthropic(system_prompt: str, user_prompt: str, model: str) -> str | None:
    try:
        import anthropic
    except ImportError:
        logger.warning("lane2.error", extra={"error_type": "anthropic_not_installed", "backend": "anthropic"})
        return None

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        logger.warning("lane2.error", extra={"error_type": "anthropic_key_missing", "backend": "anthropic"})
        return None

    client = anthropic.Anthropic(api_key=api_key, timeout=_STEP2_TIMEOUT)
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    text = response.content[0].text if response.content else None
    return text if text else None


def _parse_and_validate_json(raw: str) -> dict[str, Any] | None:
    """Parse Step 2 JSON response. Requires at least one supported schema key."""
    text = raw.strip()
    data = _try_parse_json(text)
    if data is None:
        block = _extract_json_block(text)
        if block:
            data = _try_parse_json(block)

    if not isinstance(data, dict):
        return None

    expected_keys = {"options_analysis", "causal_analysis"}
    if not expected_keys.intersection(data.keys()):
        return None

    return data


def _try_parse_json(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    cleaned = re.sub(r",\s*([}\]])", r"\1", text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return None


def _extract_json_block(text: str) -> str | None:
    fence = re.search(r"```(?:json)?\s*\n(.*?)```", text, re.DOTALL)
    if fence:
        return fence.group(1).strip()
    brace = re.search(r"\{.*\}", text, re.DOTALL)
    if brace:
        return brace.group(0)
    return None


# ── Fidelity fuzzy grounding (plan 2026-06-08 v0.2) ────────────────────────
# Threshold and guards are empirical baselines (design §4.2, n=338), revisited
# by 024 re-validation (plan §1 T3) — not static constants.
_FIDELITY_T: float = 0.55  # Stage 3 token-overlap threshold (Mnemo-approved, FP-averse)
_FIDELITY_MIN_TOKENS: int = 3  # Stage 3 applies only to quotes with >= this many content tokens (C1)
_FIDELITY_MIN_PIECE: int = 4  # Stage 2 split pieces shorter than this (normalized) are ignored

# Common English function words excluded from content-token overlap so that
# shared stopwords do not inflate grounding.
_STOPWORDS: frozenset[str] = frozenset({
    "the", "a", "an", "and", "or", "but", "if", "then", "of", "to", "in", "on",
    "at", "for", "with", "as", "is", "are", "was", "were", "be", "been", "being",
    "am", "do", "does", "did", "not", "no", "i", "you", "he", "she", "it", "we",
    "they", "me", "him", "her", "them", "my", "your", "his", "its", "our",
    "their", "this", "that", "these", "those", "there", "here", "so", "because",
    "than", "too", "very", "can", "could", "would", "should", "will", "shall",
    "may", "might", "must", "about", "into", "over", "just", "from", "by",
})

_FIDELITY_SPLIT_RE = re.compile(r"\.{3}|…|,|\band\b|\bor\b", re.IGNORECASE)


def _normalize(text: str) -> str:
    """Lowercase, replace punctuation with spaces, and collapse whitespace."""
    spaced = re.sub(r"[^\w\s]", " ", text.lower())
    return re.sub(r"\s+", " ", spaced).strip()


def _content_tokens(text: str) -> set[str]:
    """Normalized tokens, excluding stopwords and tokens shorter than 3 chars."""
    return {
        tok
        for tok in _normalize(text).split()
        if len(tok) >= 3 and tok not in _STOPWORDS
    }


def _token_overlap(quote_tokens: set[str], text_tokens: set[str]) -> float:
    """Fraction of the quote's content tokens that also appear in the text.

    Returns 0.0 when the quote has no content tokens, so a token-less quote
    cannot pass Stage 3 vacuously.
    """
    if not quote_tokens:
        return 0.0
    return len(quote_tokens & text_tokens) / len(quote_tokens)


def _is_grounded(quote: str, norm_text: str, text_tokens: set[str]) -> bool:
    """Return True if *quote* is grounded in the text via any of 3 fuzzy stages."""
    # Stage 1 — normalized substring (case/punctuation/whitespace-insensitive).
    norm_quote = _normalize(quote)
    if norm_quote and norm_quote in norm_text:
        return True
    # Stage 2 — ellipsis / clause split: every substantive piece must be present.
    pieces = [_normalize(p) for p in _FIDELITY_SPLIT_RE.split(quote)]
    substantive = [p for p in pieces if len(p) >= _FIDELITY_MIN_PIECE]
    if substantive and all(p in norm_text for p in substantive):
        return True
    # Stage 3 — content-token overlap (only when the quote has enough tokens).
    quote_tokens = _content_tokens(quote)
    if len(quote_tokens) >= _FIDELITY_MIN_TOKENS:
        if _token_overlap(quote_tokens, text_tokens) >= _FIDELITY_T:
            return True
    return False


def _fidelity_check(learner_text: str, pattern_id: str, extracted: dict) -> str:
    """Guard against LLM Step 2 hallucinating quoted items absent from the text.

    Each non-empty quote in ``options_listed`` / ``causes_listed`` must be
    *grounded* in *learner_text* via a 3-stage fuzzy check (plan v0.2 §1):
    (1) normalized substring, (2) ellipsis/clause split where every substantive
    piece is a normalized substring, (3) content-token overlap >= ``_FIDELITY_T``
    for quotes with >= ``_FIDELITY_MIN_TOKENS`` content tokens. Returns
    ``"unverified"`` if any quote is ungrounded (so the verdict is downgraded
    before Prolog evaluation), else ``"ok"``.

    Design rationale: Prolog evaluates feature values literally, so a
    hallucinated ``options_listed`` entry could yield a false ``accept``. The
    earlier exact-substring check also blocked legitimate LLM paraphrase
    (ellipsis/summarization), so the assertive path never reached verify; the
    fuzzy stages restore that while still blocking unrelated fabrication.

    This is a *lexical* grounding gate (plan §0.1): it cannot detect a
    meaning-reversed paraphrase that shares content tokens (semantic drift).
    Catching that is delegated to Prolog verify / extraction layers (plan §6).
    """
    norm_text = _normalize(learner_text)
    text_tokens = _content_tokens(learner_text)
    key = feature_schemas.get_supported_key(pattern_id)
    block = extracted.get(key, {})
    if not isinstance(block, dict):
        block = {}
    for list_field in ("options_listed", "causes_listed"):
        for quote in block.get(list_field, []) or []:
            if not str(quote).strip():
                continue
            if not _is_grounded(str(quote), norm_text, text_tokens):
                return "unverified"
    return "ok"


def _run_prolog_verify(
    pattern_id: str,
    extracted: dict[str, Any],
    backend: str,
) -> BridgeVerdict:
    """Convert extracted JSON features to Prolog terms and run verify/3."""
    try:
        prolog_terms = feature_schemas.json_to_prolog_terms(pattern_id, extracted)
    except Exception:
        logger.warning(
            "lane2.error",
            extra={"error_type": "prolog_term_conversion_failed", "backend": backend},
            exc_info=True,
        )
        return BridgeVerdict(pattern_id=pattern_id, verdict="unverified", error="prolog_term_conversion_failed")

    try:
        verdict_value = _query_prolog(pattern_id, prolog_terms)
    except Exception:
        logger.warning(
            "lane2.error",
            extra={"error_type": "prolog_execution_error", "backend": backend},
            exc_info=True,
        )
        return BridgeVerdict(pattern_id=pattern_id, verdict="unverified", error="prolog_execution_error")

    features_out = {k: extracted.get(k) for k in extracted if k in {"options_analysis", "causal_analysis"}}
    logger.info(
        "lane2.verdict",
        extra={"pattern": pattern_id, "verdict": verdict_value, "backend": backend},
    )
    return BridgeVerdict(pattern_id=pattern_id, verdict=verdict_value, features=features_out)


def _query_prolog(pattern_id: str, prolog_terms: list[str]) -> BridgeVerdictValue:
    """Consult pattern_verify.pl + pattern-specific .pl, then query verify/3."""
    from mira.system_b.lane2.prolog_runner import _require_prolog

    Prolog = _require_prolog()
    prolog = Prolog()

    common_pl = str(_PATTERN_VERIFY_PL)
    prolog.consult(common_pl)

    pattern_pl = str(_PATTERN_PL[pattern_id])
    prolog.consult(pattern_pl)

    pattern_atom = pattern_id
    feature_list = "[" + ",".join(prolog_terms) + "]"
    query = f"verify({pattern_atom}, {feature_list}, Result)."

    rows = list(prolog.query(query, maxresult=1))
    if not rows:
        return "unverified"

    result_raw = rows[0].get("Result")
    result_str = str(result_raw).lower() if result_raw is not None else ""

    if result_str == "accept":
        return "accept"
    if result_str == "reject":
        return "reject"
    return "unverified"
