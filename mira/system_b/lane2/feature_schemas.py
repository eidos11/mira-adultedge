"""Lane 2 feature extraction schemas for Prolog verification bridge.

Defines per-pattern JSON schemas, descriptive user prompt questions,
decoy schemas for context segregation, and JSON → Prolog term conversion.

Architecture: Step 2 feature extraction uses context segregation — pattern
labels are never included in prompts. The LLM receives structural questions
only. Decoy schemas prevent inference of which patterns are under investigation.

Ref: design/2026-05-26-lane2-bridge-design.md §3.3, §3.5, §4
"""
from __future__ import annotations

from mira.system_b.lane2.patterns import SUPPORTED_PATTERNS  # SSOT (C6)

# ── Feature schemas (supported patterns) ───────────────────────────────────

_SCHEMA_OPTIONS_ANALYSIS: dict = {
    "options_analysis": {
        "type": "object",
        "properties": {
            "options_listed": {"type": "array", "items": {"type": "string"}},
            "option_count": {"type": "integer"},
            "exclusivity_markers": {"type": "array", "items": {"type": "string"}},
            "middle_options_mentioned": {"type": "boolean"},
            # F1: True only when a mentioned middle option is left genuinely
            # open (not merely raised to be dismissed). Drives verify/reject.
            "viable_middle_exists": {"type": "boolean"},
            "logical_space_explored": {
                "type": "string",
                "enum": ["explicit", "implicit", "unknown"],
            },
        },
        "required": [
            "options_listed",
            "option_count",
            "exclusivity_markers",
            "middle_options_mentioned",
            "viable_middle_exists",
            "logical_space_explored",
        ],
    }
}

_SCHEMA_CAUSAL_ANALYSIS: dict = {
    "causal_analysis": {
        "type": "object",
        "properties": {
            "causes_listed": {"type": "array", "items": {"type": "string"}},
            "cause_count": {"type": "integer"},
            "alternative_causes_mentioned": {"type": "boolean"},
            "sufficiency_claim_strength": {
                "type": "string",
                "enum": ["strong", "weak", "absent"],
            },
            "temporal_only": {"type": "boolean"},
            "causal_claim_type": {
                "type": "string",
                "enum": [
                    "physical_direct",
                    "behavioral",
                    "social",
                    "statistical",
                    "unknown",
                ],
            },
        },
        "required": [
            "causes_listed",
            "cause_count",
            "alternative_causes_mentioned",
            "sufficiency_claim_strength",
            "temporal_only",
            "causal_claim_type",
        ],
    }
}

# ── Decoy schemas (always transmitted alongside supported schemas) ──────────
# Form is indistinguishable from supported schemas; results are never passed
# to Prolog. Prevents LLM from inferring which patterns triggered Step 2.

_SCHEMA_TEMPORAL_ANALYSIS: dict = {
    "temporal_analysis": {
        "type": "object",
        "properties": {
            "time_references": {"type": "array", "items": {"type": "string"}},
            "temporal_order_claimed": {"type": "boolean"},
        },
        "required": ["time_references", "temporal_order_claimed"],
    }
}

_SCHEMA_AGENT_ANALYSIS: dict = {
    "agent_analysis": {
        "type": "object",
        "properties": {
            "actors_mentioned": {"type": "array", "items": {"type": "string"}},
            "agency_attribution": {
                "type": "string",
                "enum": ["self", "other", "external", "mixed"],
            },
        },
        "required": ["actors_mentioned", "agency_attribution"],
    }
}

# ── Pattern → schema key mapping ───────────────────────────────────────────

_PATTERN_KEY_MAP: dict[str, str] = {
    "false_dilemma": "options_analysis",
    "oversimplified_cause": "causal_analysis",
}

# ── User prompt questions (descriptive, pattern-label-free) ────────────────

_QUESTIONS_FALSE_DILEMMA: list[str] = [
    (
        "List each distinct actionable choice or path the speaker frames as available. "
        "Include partial or implicit alternatives ('I could also...', 'instead', 'partly') "
        "as separate options if they represent a different path."
    ),
    "Quote any phrases that assert exclusivity between options.",
    "Is any option between or beyond the main choices mentioned, even briefly?",
    (
        "If a middle or alternative option is mentioned, is at least one left "
        "genuinely open and viable, or is every alternative raised only to be "
        "dismissed or rejected? Report whether a viable middle option remains open."
    ),
    (
        "Does the speaker explore the full space of possibilities, or frame the "
        "choice as already exhaustive?"
    ),
]

_QUESTIONS_OVERSIMPLIFIED_CAUSE: list[str] = [
    # L1 refinement (design v0.2): scope cause-listing to the speaker's own
    # attribution and exclude symptoms / action options, so cause_count
    # reflects distinct attributed causes (not symptoms, restatements, or
    # others' views). Prevents over-extraction -> spurious Prolog reject.
    # L2 refinement (design v0.2 §5 follow-up): require a verbatim phrase per
    # cause so merged/abstracted causes stay grounded to the source and pass the
    # fuzzy fidelity guard (026: L1-only -> 11/12 unverified / feature_fidelity).
    (
        "List the distinct underlying cause(s) the speaker attributes their own "
        "problem or outcome to. Merge restatements of the same cause into one, "
        "and for each cause include a short verbatim phrase from the text "
        "(the speaker's own words) so the cause is grounded in the source. "
        "Exclude: (a) symptoms or effects (what results from the cause), "
        "(b) action options or solutions the speaker is considering."
    ),
    "Does the text acknowledge any alternative causes or moderating factors?",
    (
        "Is the causal claim based solely on temporal sequence "
        "('X happened, then Y happened, so X caused Y')?"
    ),
    (
        "Is the cause described a direct physical event, a behavioral choice, "
        "a social factor, or a statistical claim?"
    ),
]

_PATTERN_QUESTIONS: dict[str, list[str]] = {
    "false_dilemma": _QUESTIONS_FALSE_DILEMMA,
    "oversimplified_cause": _QUESTIONS_OVERSIMPLIFIED_CAUSE,
}

# ── System prompt ───────────────────────────────────────────────────────────

_SYSTEM_PROMPT = (
    "You are a text structure analyst. Given a learner's text, describe objective\n"
    "structural properties that are explicitly present in the text. Focus on\n"
    "counting, quoting, and classifying what the text states. Interpretation of\n"
    "the author's intent or psychological state is outside this task's scope.\n\n"
    "Respond in JSON matching the provided schema."
)

# ── Prolog type conversion helpers ─────────────────────────────────────────

def _escape_prolog_atom(s: str) -> str:
    return s.replace("\\", "\\\\").replace("'", "\\'")


def _to_prolog_value(value: object) -> str:
    """Convert a single JSON value to its Prolog term representation."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, list):
        items = ", ".join(
            f"'{_escape_prolog_atom(str(item))}'" if isinstance(item, str) else str(item)
            for item in value
        )
        return f"[{items}]"
    s = str(value)
    if s.replace("_", "").isalpha() and s == s.lower():
        return s
    return f"'{_escape_prolog_atom(s)}'"


# ── Public API ──────────────────────────────────────────────────────────────

def get_system_prompt() -> str:
    """Return the Step 2 system prompt for feature extraction."""
    return _SYSTEM_PROMPT


def get_supported_key(pattern_id: str) -> str:
    """Map pattern_id to its feature schema key.

    false_dilemma        → options_analysis
    oversimplified_cause → causal_analysis

    Raises KeyError for unsupported pattern_id.
    """
    return _PATTERN_KEY_MAP[pattern_id]


def get_combined_schema(pattern_ids: list[str]) -> dict:
    """Return combined JSON schema for all 4 analysis sections.

    Always includes both supported schemas and both decoy schemas regardless
    of which pattern_ids are requested (context segregation, §3.5).
    """
    schema: dict = {}
    schema.update(_SCHEMA_OPTIONS_ANALYSIS)
    schema.update(_SCHEMA_CAUSAL_ANALYSIS)
    schema.update(_SCHEMA_TEMPORAL_ANALYSIS)
    schema.update(_SCHEMA_AGENT_ANALYSIS)
    return schema


def get_user_prompt(learner_text: str, pattern_ids: list[str]) -> str:
    """Build Step 2 user prompt with supported + decoy schemas.

    Always includes all 4 schemas (2 supported + 2 decoy) regardless of
    which pattern_ids are requested. Pattern names are excluded from the
    prompt (context segregation principle, §3.3).
    """
    schema = get_combined_schema(pattern_ids)
    import json

    questions: list[str] = []
    for pid in _PATTERN_QUESTIONS:
        questions.extend(_PATTERN_QUESTIONS[pid])

    question_block = "\n".join(f"{i + 1}. {q}" for i, q in enumerate(questions))
    schema_block = json.dumps(schema, indent=2)

    return (
        f"Learner text:\n{learner_text}\n\n"
        f"Answer the following questions about the text's structure:\n"
        f"{question_block}\n\n"
        f"Respond using this JSON schema:\n{schema_block}"
    )


def json_to_prolog_terms(pattern_id: str, features: dict) -> list[str]:
    """Convert extracted features to Prolog terms for a specific pattern.

    Type mapping (§4.5):
    - integer  → numeric:      option_count(2)
    - boolean  → atom:         middle_options_mentioned(false)
    - string   → quoted atom:  sufficiency_claim_strength('strong')
    - array    → list:         exclusivity_markers(['either...or'])
    - string enum → atom:      logical_space_explored(explicit)

    Args:
        pattern_id: One of SUPPORTED_PATTERNS.
        features:   The value of the pattern's feature key from the JSON response
                    (e.g. the dict at features["options_analysis"]).

    Returns:
        List of Prolog terms as strings.
    """
    key = get_supported_key(pattern_id)
    feature_dict: dict = features.get(key, {})
    terms: list[str] = []
    for field, value in feature_dict.items():
        prolog_val = _to_prolog_value(value)
        terms.append(f"{field}({prolog_val})")
    return terms
