"""MIRA AdultEdge CLI entry point.

Usage:
    python -m mira "I failed because I'm not smart enough"
    python -m mira path/to/file.txt
    python -m mira --lang ko "learner text in Korean"
    python -m mira --format json "text"
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mira.contracts.minimal import CVVerificationOverlay


def _detect_lanes() -> dict[str, bool]:
    lanes = {"lane1": True}
    try:
        import pyswip  # noqa: F401
        lanes["lane2"] = True
    except ImportError:
        lanes["lane2"] = False
    lanes["lane3"] = bool(
        os.environ.get("MIRA_ENABLE_LANE3") == "1"
        and (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY"))
    )
    return lanes


def _print_lane_status(lanes: dict[str, bool]) -> None:
    labels = {
        "lane1": ("Lane 1 (Rule-based)", "Always active"),
        "lane2": ("Lane 2 (Prolog)", 'pip install ".[prolog]" + SWI-Prolog required'),
        "lane3": ("Lane 3 (LLM)", "Set MIRA_ENABLE_LANE3=1 plus an API key to enable"),
    }
    print("\n--- Lane Status ---")
    for key, (name, hint) in labels.items():
        if lanes[key]:
            print(f"  ✓ {name}: active")
        else:
            print(f"  ○ {name}: inactive → {hint}")
    print()


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


def build_json_output(
    overlay: CVVerificationOverlay, report: str, learner_input: str = ""
) -> dict:
    """Serialize a diagnostic overlay into the versioned json contract.

    schema 0.2.2 adds top-level ``route_vtype`` and ``input`` (the learner's
    original text) so the report skill (②) can rebuild the overlay and feed
    ``render_report_markdown`` for expert mode (DRY, design decision 3).
    """
    from mira.report import SCHEMA_VERSION

    return {
        "schema_version": SCHEMA_VERSION,
        "input": learner_input,
        "report": report,
        "route_vtype": overlay.route_vtype,
        "patterns": [
            {
                "pattern_id": c.pattern_id,
                "lane2_status": c.lane2_status,
                "evidence_trace": c.evidence_trace,
                "lane3_detected": c.lane3_detected,
                **({"lane2_result": c.lane2_result} if c.lane2_result else {}),
            }
            for c in overlay.pattern_candidates
        ],
        "psr": {
            "P": overlay.psr.P_appraisal,
            "S": overlay.psr.S_strategy,
            "R": overlay.psr.R_projection,
        },
        "overlay_status": overlay.overlay_status,
        "lane1_pass": overlay.lane1_pass,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="mira",
        description="MIRA AdultEdge — Cognitive science-based judgment bias diagnostic agent",
    )
    parser.add_argument(
        "input",
        help="Learner text (direct input or file path)",
    )
    parser.add_argument(
        "--lang", default="en", choices=["ko", "en"],
        help="Output language (default: en)",
    )
    parser.add_argument(
        "--format", default="text", choices=["text", "json", "report"],
        dest="output_format",
        help="Output format: text | json | report (expert Markdown) (default: text)",
    )
    # --stage was removed in v0.2.2: the flag was accepted but never reached the
    # pipeline (run_minimal_loop has no stage parameter), so exposing it
    # promised behavior the CLI did not deliver. Stage estimation is internal;
    # a stage override can return once the pipeline accepts one.

    args = parser.parse_args()

    _load_dotenv()

    input_path = Path(args.input)
    try:
        is_file = input_path.exists() and input_path.is_file()
    except OSError:
        is_file = False
    if is_file:
        claim = input_path.read_text(encoding="utf-8").strip()
    else:
        claim = args.input

    if not claim:
        print("Error: input text is empty.", file=sys.stderr)
        sys.exit(1)

    from mira.pipeline import run_minimal_loop

    result = run_minimal_loop(
        claim,
        claim_language=args.lang,
        context_type="adult_learning",
    )

    if args.output_format == "json":
        output = build_json_output(result.overlay, result.report, claim)
        print(json.dumps(output, ensure_ascii=False, indent=2))
    elif args.output_format == "report":
        from mira.report import render_report_markdown

        print(
            render_report_markdown(
                result.overlay, claim, lang=args.lang, lanes=_detect_lanes()
            )
        )
    else:
        print(result.report)

    if args.output_format == "text":
        lanes = _detect_lanes()
        if not all(lanes.values()):
            _print_lane_status(lanes)


if __name__ == "__main__":
    main()
