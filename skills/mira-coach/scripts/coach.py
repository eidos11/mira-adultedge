"""mira-coach skill — coaching stage.

Thin wrapper around ``mira.pipeline.coach_from_overlay``.  Accepts a diagnosis
JSON produced by ``mira-diagnose-verify`` (or ``python -m mira --format json``)
and emits the same JSON with a ``coaching`` key ADDED.

Input keys are preserved exactly; coaching is added additively.
No third from-scratch serializer — this mirrors the input dict and adds one key.

Honest-skip guarantee (§5): if the primary pattern has no coaching template,
``coaching.note`` is set to an explicit "out of v0.x scope" message.
The engine (``coach_from_overlay`` in pipeline.py) holds this logic.

Reconstruction note:
  The diagnosis JSON (mira-diagnose-verify output) intentionally omits
  ``lane1_pass`` — that field is computed by ``run_reduced_critic`` inside
  ``coach_from_overlay``.  We set ``lane1_pass=True`` as a placeholder when
  rebuilding the CVVerificationOverlay; ``coach_from_overlay`` immediately
  overwrites it via ``model_copy(update={"lane1_pass": lane1_pass})``.
  This is safe and DRY: the placeholder is never surfaced to the caller.

Usage:
    python coach.py diag.json > coached.json
    python coach.py --stdin < diag.json > coached.json
    echo '{...}' | python coach.py --stdin --lang ko > coached.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

# BUG-1: when run directly (python skills/.../scripts/coach.py), sys.path[0] is
# the script dir, not the project root, so `import mira` fails — this project is
# not installed into site-packages. Bootstrap the project root onto sys.path.
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


def _load_dotenv() -> None:
    env_path = Path.cwd() / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip()
            if key and key not in os.environ:
                os.environ[key] = value


def _rebuild_diag_result(data: dict[str, Any], lang: str) -> Any:
    """Reconstruct a DiagnoseResult from a diagnosis JSON dict.

    The diagnosis JSON (mira-diagnose-verify output) lacks ``lane1_pass``
    — that field is computed inside ``coach_from_overlay``.  We use
    ``lane1_pass=True`` as a placeholder; it is overwritten immediately
    by ``coach_from_overlay`` via ``model_copy``.

    claim_language is taken from ``lang`` (the --lang flag or "en" default),
    since the diagnosis JSON does not carry a claim_language field.
    """
    import mira.contracts.minimal as minimal
    from mira.pipeline import DiagnoseResult

    route_vtype = data["route_vtype"]
    psr_data = data["psr"]

    candidates = [
        minimal.PatternCandidate(
            pattern_id=p["pattern_id"],
            canonical_id="ingested",       # render-irrelevant; mirrors mira-report/ingest.py
            vtype=route_vtype,             # mirrors ingest.py convention
            lane2_status=p.get("lane2_status", "not_run"),
            lane2_result=p.get("lane2_result"),
            evidence_trace=p.get("evidence_trace", []),
            lane3_detected=p.get("lane3_detected", False),
        )
        for p in data.get("patterns", [])
    ]

    # Use a deterministic trace_id from the JSON; fall back to "ingested"
    trace_id = data.get("trace_id", "ingested")
    if not trace_id:
        trace_id = "ingested"

    overlay = minimal.CVVerificationOverlay(
        trace_id=trace_id,
        request_id=f"req-{trace_id}",
        psr=minimal.PSRResult(
            P_appraisal=psr_data["P"],
            S_strategy=psr_data["S"],
            R_projection=psr_data["R"],
        ),
        route_vtype=route_vtype,
        pattern_candidates=candidates,
        overlay_status=data["overlay_status"],
        lane1_pass=True,               # placeholder — overwritten by coach_from_overlay
        evidence_summary=(
            data.get("evidence_summary")
            or f"Reconstructed from diagnosis JSON (schema {data.get('schema_version', '?')})."
        ),
    )

    learner_claim = data.get("input", "")
    # Require non-empty claim: coach_from_overlay needs it for generate_report
    if not learner_claim.strip():
        raise ValueError(
            "Diagnosis JSON 'input' field is empty — cannot run coaching without "
            "the original learner claim."
        )

    request = minimal.SystemAtoCVRequest(
        trace_id=trace_id,
        learner_claim=learner_claim,
        claim_language=lang,
    )

    return DiagnoseResult(request=request, overlay=overlay, diagnostic_snapshot=None)


def coach(diag_json: dict[str, Any], *, lang: str = "en") -> dict[str, Any]:
    """Run coaching on a diagnosis JSON dict and return the dict with 'coaching' added.

    Input keys are preserved exactly (additive — no re-serialization from scratch).
    The returned dict is the input dict with one new top-level key: 'coaching'.

    coaching shape: {block: str, pattern_id: str | None, note: str | None}
      - Supported pattern:     pattern_id set, note=None, block non-empty (coaching given).
      - Unsupported pattern:   pattern_id set, note="out of v0.x scope: pattern '<id>'...",
                               block may be a generic fallback.
      - No resolvable pattern: pattern_id=None, note=None, block carries no-match guidance.

    NOTE: note=None is AMBIGUOUS on its own — it covers BOTH "supported pattern
    (coaching provided)" AND "no pattern evidenced (no clear match)". Consumers
    must read pattern_id to tell them apart: note=None + pattern_id set means
    coaching was given; note=None + pattern_id=None means no clear match. The
    "out of v0.x scope" note fires ONLY for a resolved-but-unsupported pattern.
    """
    from mira.pipeline import coach_from_overlay

    diag = _rebuild_diag_result(diag_json, lang=lang)
    result = coach_from_overlay(diag, lang=lang)

    # Additive: preserve all input keys, add 'coaching' (do NOT re-serialize the overlay).
    # Immutability: return a new dict, never mutate diag_json.
    return {**diag_json, "coaching": result["coaching"]}


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="coach",
        description=(
            "mira-coach — run coaching (stage 4) on a diagnosis JSON produced "
            "by mira-diagnose-verify, and emit the same JSON with 'coaching' added. "
            "Unsupported patterns produce an explicit note (never silently skipped)."
        ),
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Path to a diagnosis JSON file (omit to use --stdin)",
    )
    parser.add_argument(
        "--lang",
        default="en",
        choices=["ko", "en"],
        help="Output language for coaching content (default: en)",
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read diagnosis JSON from stdin instead of a file argument",
    )

    args = parser.parse_args()

    _load_dotenv()

    # Resolve input: --stdin, positional file path, or error
    if args.stdin:
        raw = sys.stdin.read().strip()
    elif args.input is not None:
        input_path = Path(args.input)
        try:
            is_file = input_path.exists() and input_path.is_file()
        except OSError:
            is_file = False
        if is_file:
            raw = input_path.read_text(encoding="utf-8").strip()
        else:
            print(
                f"Error: {args.input!r} is not a file. "
                "Pass a JSON file path or use --stdin.",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        print("Error: provide a diagnosis JSON file path or use --stdin.", file=sys.stderr)
        sys.exit(1)

    if not raw:
        print("Error: input is empty.", file=sys.stderr)
        sys.exit(1)

    try:
        diag_json = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"Error: input is not valid JSON: {exc}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(diag_json, dict):
        print("Error: diagnosis JSON must be a JSON object.", file=sys.stderr)
        sys.exit(1)

    try:
        coached = coach(diag_json, lang=args.lang)
    except (ValueError, KeyError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(coached, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
