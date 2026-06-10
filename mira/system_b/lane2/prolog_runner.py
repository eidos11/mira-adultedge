"""Thin pyswip runner for Lane 2 Prolog rules."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

# Project root resolution after MIRA restructure:
#   __file__ = .../mira/system_b/lane2/prolog_runner.py
#   parents[0] = lane2/
#   parents[1] = system_b/
#   parents[2] = mira/
#   parents[3] = mira_adultedge/  (project root)
PROJECT_ROOT = Path(__file__).resolve().parents[3]

RULE_PATHS = {
    "pattern_verify": Path(
        "mira/system_b/rules/prolog/pattern_verify.pl"
    ),
    "false_dilemma": Path(
        "mira/system_b/rules/prolog/false_dilemma.pl"
    ),
    "oversimplified_cause": Path(
        "mira/system_b/rules/prolog/oversimplified_cause.pl"
    ),
}

_FUNCTOR_SAFE = re.compile(r"[^a-zA-Z0-9_]")


def get_rule_path(pattern_id: str) -> str:
    """Return the absolute Prolog rule path for a supported Lane 2 pattern."""

    try:
        rel_path = RULE_PATHS[pattern_id]
    except KeyError as exc:
        supported = ", ".join(sorted(RULE_PATHS))
        raise ValueError(f"Unsupported pattern_id {pattern_id!r}; expected one of: {supported}") from exc
    return str(PROJECT_ROOT / rel_path)


def run_lane2_check(psr: dict[str, Any], pattern_id: str) -> dict[str, Any]:
    """Run pattern_candidate/3 and diagnostic_verdict/3 for a PSR dict.

    Requires both the Python package ``pyswip`` and a system SWI-Prolog
    installation. The PSR dict is converted to a compact Prolog term:
    ``psr([key(value), ...])``.
    """

    Prolog = _require_prolog()
    rule_path = get_rule_path(pattern_id)
    psr_term = _psr_to_term(psr)

    prolog = Prolog()
    prolog.consult(rule_path)

    candidate_rows = list(
        prolog.query(f"pattern_candidate({pattern_id}, {psr_term}, EvidenceTrace).", maxresult=1)
    )
    candidate = bool(candidate_rows)
    evidence_trace = (
        _normalise_term(candidate_rows[0].get("EvidenceTrace", [])) if candidate_rows else []
    )

    verdict_rows = list(
        prolog.query(f"diagnostic_verdict({pattern_id}, {psr_term}, Verdict).", maxresult=1)
    )
    verdict_value = _normalise_term(verdict_rows[0].get("Verdict")) if verdict_rows else None
    verdict = None if verdict_value in (None, "no_verdict") else str(verdict_value)

    near_miss_rows = list(
        prolog.query(f"near_miss_check({psr_term}, {pattern_id}, Result).", maxresult=1)
    )
    near_miss_value = (
        _normalise_term(near_miss_rows[0].get("Result")) if near_miss_rows else None
    )
    near_miss = None if near_miss_value in (None, "not_near_miss") else str(near_miss_value)

    return {
        "pattern_id": pattern_id,
        "candidate": candidate,
        "verdict": verdict,
        "evidence_trace": evidence_trace,
        "near_miss": near_miss,
    }


def _require_prolog() -> Any:
    try:
        from pyswip import Prolog
    except Exception as exc:  # pragma: no cover - depends on host installation
        raise ImportError(
            "Lane 2 Prolog runner requires pyswip and SWI-Prolog. "
            "Install with: pip install pyswip, and install SWI-Prolog for the OS."
        ) from exc
    return Prolog


def _psr_to_term(psr: dict[str, Any]) -> str:
    features = []
    for key in sorted(psr):
        features.append(f"{_functor_name(key)}({_value_to_prolog(psr[key])})")
    return "psr([" + ",".join(features) + "])"


def _functor_name(key: str) -> str:
    name = _FUNCTOR_SAFE.sub("_", key).lower().strip("_")
    if not name:
        raise ValueError("PSR keys must contain at least one alphanumeric character")
    if name[0].isdigit():
        name = f"f_{name}"
    return name


def _value_to_prolog(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "unknown"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, (list, tuple)):
        return "[" + ",".join(_value_to_prolog(item) for item in value) + "]"
    return _quote_atom(str(value))


def _quote_atom(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'"


def _normalise_term(value: Any) -> Any:
    if isinstance(value, list):
        return [_normalise_term(item) for item in value]
    if value is None:
        return None
    return str(value)

