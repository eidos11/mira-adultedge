"""Single source of truth for Lane 2 supported patterns and their registry
metadata. Zero internal deps to avoid bridge<->feature_schemas import cycles.
Values mirror spec/shared/pattern_registry.yaml (false_dilemma, oversimplified_cause).
"""
from __future__ import annotations

# pattern_id -> (canonical_id, vtype)
PATTERN_META: dict[str, tuple[str, str]] = {
    "false_dilemma": ("PAT-D-02", "D"),
    "oversimplified_cause": ("PAT-A-02", "A"),
}

SUPPORTED_PATTERNS: frozenset[str] = frozenset(PATTERN_META)
