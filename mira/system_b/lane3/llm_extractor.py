"""Lane 3 LLM extractor for M1.

Architecture (4.7 domain review):
  - System A 3-axis diagnosis narrows candidate patterns via stage-conditional priming
  - LLM receives 8-10 candidate patterns (not all 21) to reduce attention dilution
  - LLM proposes pattern candidates with evidence traces
  - Lane 1 rules confirm/reject (LLM suggests, rules decide)

M1 scope:
  - Single LLM call per learner claim
  - Structured JSON output (pattern_id + evidence)
  - Graceful fallback when LLM unavailable — returns empty candidates
  - No verdict authority (Lane3ShadowResult.has_verdict_authority = False)

Backend priority (MIRA_LLM_BACKEND env var):
  codex     → Codex CLI (GPT-5.5 via subscription, no extra cost)
  openai    → OpenAI API (MIRA_LLM_MODEL default: gpt-5.4)
  anthropic → Anthropic API (MIRA_LLM_MODEL default: claude-sonnet-4-6)
  none      → Lane 3 disabled
  (unset)   → auto-detect: codex > openai > anthropic > none
"""

from __future__ import annotations

import json
import logging
import os
import random
import shutil
import subprocess
import tempfile
from typing import Any

from mira.system_b.codex_env import codex_subprocess_env

logger = logging.getLogger(__name__)

CANDIDATE_PATTERNS_BY_STAGE: dict[str, list[str]] = {
    "concept": [
        "fluency_illusion",
        "effort_heuristic",
        "false_dilemma",
        "hasty_generalization",
        "recognition_retrieval_confusion",
        "oversimplified_cause",
        "anecdotal_evidence",
        "sunk_cost",
    ],
    "framework": [
        "fluency_illusion",
        "false_dilemma",
        "oversimplified_cause",
        "sunk_cost",
        "effort_heuristic",
        "composition_fallacy",
        "prediction_fallacy",
        "self_serving_attribution",
    ],
    "practice": [
        "effort_heuristic",
        "sunk_cost",
        "oversimplified_cause",
        "false_dilemma",
        "post_hoc_rationalization",
        "confusing_explanation_excuse",
        "identity_protective_reasoning",
        "fluency_illusion",
    ],
    "reality": [
        "sunk_cost",
        "post_hoc_rationalization",
        "self_serving_attribution",
        "identity_protective_reasoning",
        "oversimplified_cause",
        "false_dilemma",
        "prediction_fallacy",
        "effort_heuristic",
    ],
}

_DEFAULT_CANDIDATES = [
    "fluency_illusion",
    "false_dilemma",
    "oversimplified_cause",
    "sunk_cost",
    "effort_heuristic",
    "hasty_generalization",
    "post_hoc_rationalization",
    "self_serving_attribution",
]

_SYSTEM_PROMPT = """You are AE (AdultEdge), a cognitive bias diagnostic assistant.
Given a learner's claim and a list of candidate reasoning patterns, identify which
patterns are present in the claim.

For each candidate pattern, apply this 3-step depth check:
1. surface_match: does the claim's wording match the pattern?
2. mechanism_match: does the underlying reasoning STRUCTURE match?
3. counter_check: could the claim be explained WITHOUT invoking this pattern?
Only report when mechanism_match=true AND counter_check=false.

RULES:
- Only select patterns from the provided candidate list
- Provide specific textual evidence from the claim
- If no pattern is clearly present, return an empty list
- Never use verdict language (e.g. "diagnosed", "confirmed", "determined")
- This is a hypothesis, not a diagnosis

Respond in JSON: {"patterns": [{"pattern_id": "...", "evidence": ["..."]}]}"""

_BACKEND_DEFAULTS: dict[str, str] = {
    "codex": "gpt-5.5",
    # openai default = gpt-5.4 (alpha-test 020a decision: gpt-4o/mini/nano excluded for
    # insufficient quality; gpt-5.4 = best precision/cost for API). gpt-5.5 via codex (sub).
    "openai": "gpt-5.4",
    "anthropic": "claude-sonnet-4-6",
}

# Output-token ceiling for Lane 3 extraction calls. A ceiling, not a charge —
# only tokens actually generated are billed — so it sits well above the bounded
# diagnosis output (<=8 candidate patterns, evidence drawn from the input) to
# avoid mid-array truncation that drops extractions (batch B F2). Single source
# for both backends; raise here if a longer response is ever needed.
_MAX_OUTPUT_TOKENS = 4096


def resolve_backend() -> tuple[str, str]:
    """Resolve which LLM backend and model to use.

    Returns (backend, model) tuple. Checks MIRA_LLM_BACKEND first,
    then auto-detects: codex > openai (key present) > anthropic (key present) > none.
    """
    backend = os.environ.get("MIRA_LLM_BACKEND", "").lower()
    model = os.environ.get("MIRA_LLM_MODEL", "")

    if backend in _BACKEND_DEFAULTS:
        return (backend, model or _BACKEND_DEFAULTS[backend])
    if backend == "none":
        return ("none", "")

    if shutil.which("codex"):
        return ("codex", model or "gpt-5.5")
    if os.environ.get("OPENAI_API_KEY"):
        return ("openai", model or "gpt-5.4")
    if os.environ.get("ANTHROPIC_API_KEY"):
        return ("anthropic", model or "claude-sonnet-4-6")

    return ("none", "")


def get_candidate_patterns(stage_estimate: str) -> list[str]:
    """Return stage-conditional candidate pattern list (8 patterns)."""
    return CANDIDATE_PATTERNS_BY_STAGE.get(stage_estimate, _DEFAULT_CANDIDATES)


def build_extraction_prompt(
    learner_claim: str,
    candidate_patterns: list[str],
    lang: str = "ko",
) -> str:
    """Build the user prompt for LLM pattern extraction."""
    shuffled = candidate_patterns.copy()
    rng = random.Random(hash(learner_claim))
    rng.shuffle(shuffled)
    pattern_list = "\n".join(f"- {p}" for p in shuffled)
    return (
        f"Learner claim ({lang}):\n\"{learner_claim}\"\n\n"
        f"Candidate patterns to check:\n{pattern_list}\n\n"
        "Identify which patterns are present. Respond in JSON."
    )


def extract_pattern_candidates(
    learner_claim: str,
    stage_estimate: str = "concept",
    lang: str = "ko",
) -> list[dict[str, Any]]:
    """Extract pattern candidates from learner claim using LLM.

    Returns list of {"pattern_id": str, "evidence": list[str]}.
    Returns empty list if Lane 3 is not explicitly enabled, unavailable, or fails.
    """
    if os.environ.get("MIRA_ENABLE_LANE3") != "1":
        logger.info("Lane 3 disabled; set MIRA_ENABLE_LANE3=1 to enable external LLM calls")
        return []

    backend, model = resolve_backend()
    if backend == "none":
        logger.info("No LLM backend available — Lane 3 skipped")
        return []

    logger.info("Lane 3 using backend=%s model=%s", backend, model)

    candidates = get_candidate_patterns(stage_estimate)
    user_prompt = build_extraction_prompt(learner_claim, candidates, lang)

    try:
        if backend == "codex":
            return _call_codex_cli(user_prompt)
        if backend == "openai":
            api_key = os.environ.get("OPENAI_API_KEY", "")
            if not api_key:
                logger.info("OPENAI_API_KEY not set — Lane 3 skipped")
                return []
            return _call_openai_compatible(api_key, user_prompt, model)
        if backend == "anthropic":
            api_key = os.environ.get("ANTHROPIC_API_KEY", "")
            if not api_key:
                logger.info("ANTHROPIC_API_KEY not set — Lane 3 skipped")
                return []
            return _call_anthropic(api_key, user_prompt, model)
        return []
    except Exception:
        logger.warning("Lane 3 LLM call failed — returning empty candidates", exc_info=True)
        return []


def _call_codex_cli(user_prompt: str) -> list[dict[str, Any]]:
    """Call Codex CLI (GPT-5.5 via subscription) for pattern extraction.

    Uses ``codex exec`` in ephemeral mode with the ``cc`` profile.
    Reasoning effort is set to medium (sufficient for structured extraction).
    """
    output_fd, output_path = tempfile.mkstemp(suffix=".txt", prefix="mira-lane3-")
    os.close(output_fd)

    try:
        full_prompt = f"{_SYSTEM_PROMPT}\n\n{user_prompt}"
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
            timeout=120,
            env=codex_subprocess_env(),
        )

        if result.returncode != 0:
            logger.warning("Codex CLI exit %d: %s", result.returncode, result.stderr[:300])
            return []

        with open(output_path) as f:
            response_text = f.read()

        if not response_text.strip():
            logger.warning("Codex CLI returned empty output")
            return []

        return _parse_response(response_text)
    except FileNotFoundError:
        logger.info("Codex CLI not found in PATH — skipping")
        return []
    except subprocess.TimeoutExpired:
        logger.warning("Codex CLI timed out after 120s")
        return []
    finally:
        try:
            os.unlink(output_path)
        except OSError:
            pass


def _call_anthropic(
    api_key: str, user_prompt: str, model: str = "claude-sonnet-4-6",
) -> list[dict[str, Any]]:
    try:
        import anthropic
    except ImportError:
        logger.info("anthropic package not installed — skipping Anthropic call")
        return []

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=_MAX_OUTPUT_TOKENS,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return _parse_response(response.content[0].text)


def _call_openai_compatible(
    api_key: str, user_prompt: str, model: str = "gpt-5.4",
) -> list[dict[str, Any]]:
    try:
        import openai
    except ImportError:
        logger.info("openai package not installed — skipping OpenAI call")
        return []

    client = openai.OpenAI(api_key=api_key)
    uses_completion_tokens = model.startswith(("gpt-5", "o1", "o3", "o4"))
    token_param = "max_completion_tokens" if uses_completion_tokens else "max_tokens"
    response = client.chat.completions.create(
        model=model,
        **{token_param: _MAX_OUTPUT_TOKENS},
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    return _parse_response(response.choices[0].message.content or "")


def _parse_response(text: str) -> list[dict[str, Any]]:
    """Parse LLM JSON response into pattern candidate list.

    Handles: code blocks, embedded JSON in prose, trailing commas, and
    truncated/fence-only responses (salvages complete pattern objects).
    """
    text = text.strip()

    data = _try_parse_json(text)
    if data is None:
        extracted = _extract_json_block(text)
        if extracted:
            data = _try_parse_json(extracted)

    if data is None:
        salvaged = _salvage_patterns(text)
        if salvaged:
            data = {"patterns": salvaged}
        else:
            logger.warning("Failed to parse LLM response as JSON: %s", text[:200])
            return []

    patterns = data.get("patterns", []) if isinstance(data, dict) else []
    result = []
    for p in patterns:
        if isinstance(p, dict) and "pattern_id" in p:
            result.append({
                "pattern_id": str(p["pattern_id"]),
                "evidence": [str(e) for e in p.get("evidence", [])],
            })
    return result


def _extract_json_block(text: str) -> str | None:
    """Extract JSON from code blocks or embedded braces."""
    import re
    fence_match = re.search(r"```(?:json)?\s*\n(.*?)```", text, re.DOTALL)
    if fence_match:
        return fence_match.group(1).strip()
    brace_match = re.search(r"\{.*\}", text, re.DOTALL)
    if brace_match:
        return brace_match.group(0)
    return None


def _try_parse_json(text: str) -> dict[str, Any] | None:
    """Attempt JSON parse with trailing-comma tolerance."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    import re
    cleaned = re.sub(r",\s*([}\]])", r"\1", text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return None


def _salvage_patterns(text: str) -> list[dict[str, Any]]:
    """Recover complete pattern objects from a truncated or fence-only response.

    LLM output can be cut off mid-array (max_tokens) or wrapped in a code fence
    with no closing marker. When the response as a whole won't parse, scan the
    "patterns" array and keep the objects that arrived intact rather than
    dropping the whole extraction. String-aware so braces inside evidence text
    don't perturb the depth count.
    """
    import re

    body = re.sub(r"^\s*```(?:json)?\s*\n?", "", text)
    array_start = re.search(r'"patterns"\s*:\s*\[', body)
    if not array_start:
        return []

    scan = body[array_start.end() :]
    salvaged: list[dict[str, Any]] = []
    depth = 0
    obj_start: int | None = None
    in_str = False
    escaped = False
    for i, ch in enumerate(scan):
        if in_str:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            if depth == 0:
                obj_start = i
            depth += 1
        elif ch == "}":
            if depth > 0:
                depth -= 1
                if depth == 0 and obj_start is not None:
                    obj = _try_parse_json(scan[obj_start : i + 1])
                    if isinstance(obj, dict) and "pattern_id" in obj:
                        salvaged.append(obj)
                    obj_start = None
        elif ch == "]" and depth == 0:
            break
    return salvaged
