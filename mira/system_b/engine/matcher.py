"""Pattern matching: 21-pattern registry search.

M1: Searches pattern_registry.yaml for candidates by vtype.
Lane 2 verification is handled downstream by bridge.py in pipeline.py.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from mira.contracts.minimal import (
    PatternCandidate,
    PSRResult,
    VType,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
_REGISTRY_PATH = PROJECT_ROOT / "spec" / "shared" / "pattern_registry.yaml"


class RegistryLoadError(Exception):
    pass


def load_registry(path: Path | None = None) -> list[dict[str, Any]]:
    registry_path = path or _REGISTRY_PATH
    try:
        with open(registry_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        raise RegistryLoadError(f"Registry file not found: {registry_path}")
    except yaml.YAMLError as exc:
        raise RegistryLoadError(f"Malformed YAML in {registry_path}: {exc}")

    if not isinstance(data, dict):
        raise RegistryLoadError(
            f"Registry top-level must be a mapping, got {type(data).__name__}: {registry_path}"
        )

    patterns = data.get("diagnostic_pattern", [])
    if not isinstance(patterns, list):
        raise RegistryLoadError(
            f"diagnostic_pattern must be a list, got {type(patterns).__name__}: {registry_path}"
        )
    if not patterns:
        import warnings
        warnings.warn(
            f"pattern_registry at {registry_path} returned 0 diagnostic patterns — "
            "check key name or file path",
            stacklevel=2,
        )
    return patterns


def _validate_entry(entry: Any, index: int) -> tuple[str, str, str]:
    if not isinstance(entry, dict):
        raise RegistryLoadError(f"Registry entry [{index}] is not a mapping: {type(entry).__name__}")
    pattern_id = entry.get("id")
    if not pattern_id or not isinstance(pattern_id, str):
        raise RegistryLoadError(f"Registry entry [{index}] missing or invalid 'id': {entry}")
    vtype = entry.get("vtype", "")
    canonical_id = entry.get("canonical_id", pattern_id)
    if not isinstance(canonical_id, str):
        raise RegistryLoadError(f"Registry entry [{index}] invalid 'canonical_id': {entry}")
    return pattern_id, canonical_id, vtype


def match_patterns(
    psr: PSRResult,
    route: VType,
    registry: list[dict[str, Any]] | None = None,
) -> list[PatternCandidate]:
    """Find pattern candidates matching the routed vtype."""
    if registry is None:
        registry = load_registry()

    candidates: list[PatternCandidate] = []
    for idx, entry in enumerate(registry):
        pattern_id, canonical_id, vtype = _validate_entry(entry, idx)
        if vtype != route:
            continue

        candidate = PatternCandidate(
            pattern_id=pattern_id,
            canonical_id=canonical_id,
            vtype=route,
        )

        # Lane 2 verification is handled by bridge.py in pipeline.py,
        # after Lane 3 enrichment provides structural features.

        candidates.append(candidate)

    return candidates
