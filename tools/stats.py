"""Single-source repo statistics for MIRA's public documents.

Public docs (README, VISION, llms.txt, dashboard, CITATION) used to hand-maintain
the same counts (tests passed, diagnostic patterns) in many places, so every update
risked omissions and cross-document contradictions. This tool computes each count
from one source and injects / verifies it, with CI enforcement.

Design contract (stats-injection design v2):
  - tests   : structured pytest output (junit-xml); a non-clean run is refused.
  - patterns: ``pattern_registry.yaml`` -> ``cardinality.diagnostic_total`` (= 21),
              NOT ``len(entries)`` (decision A).
  - prose shows a monotonic floor ("300+"); regenerated artifacts show exact
              (decision B).

Three modes:
  ``stats.py``            report computed values
  ``stats.py --write``    inject into target docs (dry-run diff; ``--yes`` applies)
  ``stats.py --check``    verify docs match the single source (non-zero exit on drift)

Dependencies: stdlib + pyyaml (already a runtime dependency).
"""

from __future__ import annotations

import argparse
import difflib
import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import yaml

REGISTRY_RELPATH = Path("spec") / "shared" / "pattern_registry.yaml"
DEFAULT_MIN_FLOOR = 300


# --------------------------------------------------------------------------- #
# data
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class Stats:
    """Computed counts from the single sources."""

    tests: int
    patterns: int


@dataclass(frozen=True)
class Target:
    """One occurrence of a stat in a public surface (per-occurrence manifest)."""

    file: str
    occurrence_id: str
    stat: str  # "tests" | "patterns"
    render: str  # "floor" | "exact"
    mechanism: str  # "html_marker" | "yaml_field" | "soft_text"
    yaml_key: tuple = field(default_factory=tuple)


class MarkerError(ValueError):
    """Raised when a stats marker is missing, duplicated, or malformed."""


def _stat_value(stats: Stats, stat: str) -> int:
    if stat == "tests":
        return stats.tests
    if stat == "patterns":
        return stats.patterns
    raise ValueError(f"unknown stat: {stat!r}")


# --------------------------------------------------------------------------- #
# compute (pure where possible; the pytest run is injected for testability)
# --------------------------------------------------------------------------- #

def _parse_junit_xml(text: str) -> dict:
    """Extract pass/fail/skip totals from a junit-xml document.

    Sums across all ``<testsuite>`` elements; ``passed = tests - failures -
    errors - skipped``.
    """
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        raise ValueError(f"could not parse junit xml: {exc}") from exc
    suites = root.findall(".//testsuite")
    if not suites and root.tag == "testsuite":
        suites = [root]
    if not suites:
        raise ValueError("no <testsuite> element in junit xml")
    tests = failures = errors = skipped = 0
    for s in suites:
        tests += int(s.get("tests", 0))
        failures += int(s.get("failures", 0))
        errors += int(s.get("errors", 0))
        skipped += int(s.get("skipped", 0))
    return {
        "tests": tests,
        "failures": failures,
        "errors": errors,
        "skipped": skipped,
        "passed": tests - failures - errors - skipped,
    }


def _default_runner(repo_root: Path, junit_path: str) -> int:
    """Run the canonical full suite and write junit xml; return the exit code."""
    cmd = [
        "uv", "run", "--all-extras", "python", "-m", "pytest", "tests",
        "-q", "--color=no", f"--junit-xml={junit_path}",
    ]
    proc = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True)
    if proc.returncode != 0:
        # Surface pytest's own output so a CI failure is actionable.
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
    return proc.returncode


def compute_tests(repo_root: Path, runner=_default_runner) -> int:
    """Passed-test count from a clean full run.

    A non-zero exit or any failure/error refuses to report a count, so a broken
    suite can never silently lower the published number.
    """
    fd, junit = tempfile.mkstemp(prefix="mira-stats-", suffix=".xml")
    os.close(fd)
    try:
        rc = runner(Path(repo_root), junit)
        data = _parse_junit_xml(Path(junit).read_text(encoding="utf-8"))
        if rc != 0 or data["failures"] or data["errors"]:
            raise RuntimeError(
                "pytest did not pass cleanly "
                f"(exit={rc}, failures={data['failures']}, errors={data['errors']})"
            )
        return data["passed"]
    finally:
        try:
            os.unlink(junit)
        except OSError:
            pass


def compute_patterns(registry_path: Path) -> int:
    """Canonical diagnostic pattern count from the registry's cardinality field."""
    data = yaml.safe_load(Path(registry_path).read_text(encoding="utf-8"))
    try:
        total = int(data["cardinality"]["diagnostic_total"])
    except (KeyError, TypeError) as exc:
        raise ValueError(
            f"cardinality.diagnostic_total not found in {registry_path}"
        ) from exc
    if total <= 0:
        raise ValueError(f"cardinality.diagnostic_total must be positive, got {total}")
    return total


def compute(repo_root: Path, runner=_default_runner) -> Stats:
    repo_root = Path(repo_root)
    return Stats(
        tests=compute_tests(repo_root, runner=runner),
        patterns=compute_patterns(repo_root / REGISTRY_RELPATH),
    )


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #

def floor(n: int, min_floor: int = DEFAULT_MIN_FLOOR) -> int:
    """Monotonic display floor: ``max(min_floor, (n // 100) * 100)``.

    ``min_floor`` is committed to the repo and only moves forward, so a temporary
    dip in the real count never lowers the advertised number.
    """
    return max(min_floor, (n // 100) * 100)


def render_value(value: int, render: str, min_floor: int = DEFAULT_MIN_FLOOR) -> str:
    if render == "floor":
        return f"{floor(value, min_floor)}+"
    if render == "exact":
        return str(value)
    raise ValueError(f"unknown render mode: {render!r}")


def render_for_target(stats: Stats, target: Target, min_floor: int) -> str:
    return render_value(_stat_value(stats, target.stat), target.render, min_floor)


# --------------------------------------------------------------------------- #
# markers
# --------------------------------------------------------------------------- #

def _open_re(occ_id: str) -> str:
    return rf"<!--\s*stats:{re.escape(occ_id)}\s*-->"


def _close_re(occ_id: str) -> str:
    return rf"<!--\s*/stats:{re.escape(occ_id)}\s*-->"


def _pair_re(occ_id: str) -> re.Pattern:
    return re.compile(f"({_open_re(occ_id)})(.*?)({_close_re(occ_id)})", re.DOTALL)


def _require_single_pair(text: str, occ_id: str) -> re.Match:
    opens = len(re.findall(_open_re(occ_id), text))
    closes = len(re.findall(_close_re(occ_id), text))
    matches = list(_pair_re(occ_id).finditer(text))
    if opens != 1 or closes != 1 or len(matches) != 1:
        raise MarkerError(
            f"marker 'stats:{occ_id}' must appear exactly once and be well-formed "
            f"(opens={opens}, closes={closes}, pairs={len(matches)})"
        )
    return matches[0]


def inject_marker(text: str, occ_id: str, value: str) -> str:
    """Replace the content between a single well-formed marker pair (idempotent)."""
    match = _require_single_pair(text, occ_id)
    return text[: match.start(2)] + value + text[match.end(2):]


def read_marker(text: str, occ_id: str) -> str:
    return _require_single_pair(text, occ_id).group(2)


_ANY_MARKER_RE = re.compile(
    r"<!--\s*stats:([\w-]+)\s*-->.*?<!--\s*/stats:\1\s*-->", re.DOTALL
)
_STRAY_COUNT_RE = re.compile(r"\b\d{3,}\s*tests?\b", re.IGNORECASE)


def find_stray_counts(text: str) -> list:
    """Bare exact test counts outside markers (floor notation like ``300+`` is ok)."""
    return _STRAY_COUNT_RE.findall(_ANY_MARKER_RE.sub("", text))


# High-signal "pattern total" phrasings. A count ABOVE canonical is the real drift
# (e.g. the stale 22 = published 21 + 1 candidate); a lower lineage label such as
# "17-pattern" (registry historical_label) is legitimate and must not flag.
# Deliberately narrow so coaching ("6 patterns"), candidates ("14 candidate
# patterns"), and "cy-pattern" never false-positive.
_STRAY_PATTERN_RES = (
    re.compile(r"\b(\d+)-patterns?\b", re.IGNORECASE),
    re.compile(r"\b(\d+)\s+diagnostic\s+patterns?\b", re.IGNORECASE),
    re.compile(r"\b2\s*(?:/|of)\s*(\d+)\b", re.IGNORECASE),
)


def find_stray_pattern_counts(text: str, canonical: int) -> list:
    """Pattern-total phrasings whose count exceeds ``canonical`` (e.g. a stale ``22``)."""
    stripped = _ANY_MARKER_RE.sub("", text)
    bad = []
    for rx in _STRAY_PATTERN_RES:
        for match in rx.finditer(stripped):
            if int(match.group(1)) > canonical:
                bad.append(match.group(0))
    return bad


def _value_present(text: str, expected: str) -> bool:
    """True if ``expected`` appears with numeric boundaries (so '300+' != '1300+')."""
    return bool(re.search(rf"(?<!\d){re.escape(expected)}(?!\d)", text))


# --------------------------------------------------------------------------- #
# atomic write
# --------------------------------------------------------------------------- #

def write_text_atomic(path: Path, content: str) -> None:
    """Write via a temp file + ``os.replace``; preserve exact bytes (no EOL rewrite)."""
    path = Path(path)
    parent = path.parent if str(path.parent) else Path(".")
    fd, tmp = tempfile.mkstemp(dir=str(parent), prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
            fh.write(content)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


# --------------------------------------------------------------------------- #
# targets manifest
# --------------------------------------------------------------------------- #

def load_targets(path: Path):
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    min_floor = int(data.get("min_floor", DEFAULT_MIN_FLOOR))
    targets = [
        Target(
            file=t["file"],
            occurrence_id=t["occurrence_id"],
            stat=t["stat"],
            render=t["render"],
            mechanism=t["mechanism"],
            yaml_key=tuple(t.get("yaml_key", ())),
        )
        for t in data.get("targets", [])
    ]
    return min_floor, targets


# --------------------------------------------------------------------------- #
# inject (write) and check (verify)
# --------------------------------------------------------------------------- #

def _apply_to_text(text: str, ftargets, stats: Stats, min_floor: int) -> str:
    for t in ftargets:
        value = render_for_target(stats, t, min_floor)
        if t.mechanism == "html_marker":
            text = inject_marker(text, t.occurrence_id, value)
        elif t.mechanism in ("soft_text", "yaml_field"):
            # Maintained in place (plain prose / YAML scalar); verified by check,
            # not auto-rewritten, so we never corrupt surrounding text.
            continue
        else:
            raise ValueError(f"unknown mechanism: {t.mechanism!r}")
    return text


def apply_targets(repo_root: Path, stats: Stats, targets, min_floor: int, write: bool = False) -> dict:
    """Inject computed values. Returns ``{file: (original, updated)}`` for changes."""
    repo_root = Path(repo_root)
    by_file = defaultdict(list)
    for t in targets:
        by_file[t.file].append(t)
    diffs = {}
    for fname, ftargets in by_file.items():
        path = repo_root / fname
        original = path.read_text(encoding="utf-8")
        updated = _apply_to_text(original, ftargets, stats, min_floor)
        if updated != original:
            diffs[fname] = (original, updated)
            if write:
                write_text_atomic(path, updated)
    return diffs


def check(repo_root: Path, stats: Stats, targets, min_floor: int) -> list:
    """Verify every surface matches the single source. Returns a list of errors."""
    repo_root = Path(repo_root)
    errors = []
    by_file = defaultdict(list)
    for t in targets:
        by_file[t.file].append(t)
    for fname, ftargets in by_file.items():
        path = repo_root / fname
        if not path.exists():
            errors.append(f"{fname}: target file missing")
            continue
        text = path.read_text(encoding="utf-8")
        for t in ftargets:
            expected = render_for_target(stats, t, min_floor)
            if t.mechanism == "html_marker":
                try:
                    current = read_marker(text, t.occurrence_id)
                except MarkerError as exc:
                    errors.append(f"{fname}[{t.occurrence_id}]: {exc}")
                    continue
                if current != expected:
                    errors.append(
                        f"{fname}[{t.occurrence_id}]: doc={current!r} expected={expected!r}"
                    )
            elif t.mechanism in ("soft_text", "yaml_field"):
                if not _value_present(text, expected):
                    errors.append(
                        f"{fname}[{t.occurrence_id}]: expected {expected!r} not present "
                        f"({t.mechanism})"
                    )
            else:
                errors.append(f"{fname}[{t.occurrence_id}]: unknown mechanism {t.mechanism!r}")
        stray = find_stray_counts(text)
        if stray:
            errors.append(f"{fname}: bare test counts outside markers: {stray}")
        stray_patterns = find_stray_pattern_counts(text, stats.patterns)
        if stray_patterns:
            errors.append(
                f"{fname}: stale pattern totals (expected {stats.patterns}): {stray_patterns}"
            )
    return errors


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def _print_diff(fname: str, original: str, updated: str, applied: bool) -> None:
    tag = "written" if applied else "would change"
    print(f"--- {fname} ({tag})")
    for line in difflib.unified_diff(
        original.splitlines(keepends=True),
        updated.splitlines(keepends=True),
        fromfile=f"a/{fname}",
        tofile=f"b/{fname}",
    ):
        sys.stdout.write(line)


def _resolve_paths(args):
    here = Path(__file__).resolve()
    repo_root = Path(args.repo_root).resolve() if args.repo_root else here.parents[1]
    targets_path = Path(args.targets).resolve() if args.targets else here.parent / "stats_targets.yaml"
    return repo_root, targets_path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Compute, inject, or verify MIRA's published stats from a single source."
    )
    parser.add_argument("--write", action="store_true", help="inject computed values into target docs")
    parser.add_argument("--yes", action="store_true", help="apply --write changes (default: dry-run diff)")
    parser.add_argument("--check", action="store_true", help="verify docs match the single source (CI gate)")
    parser.add_argument("--repo-root", default=None, help="repo root (default: parent of tools/)")
    parser.add_argument("--targets", default=None, help="path to stats_targets.yaml")
    args = parser.parse_args(argv)

    repo_root, targets_path = _resolve_paths(args)
    stats = compute(repo_root)
    if args.check or args.write:
        min_floor, targets = load_targets(targets_path)
    else:  # report mode: the targets manifest is optional
        min_floor, targets = (
            load_targets(targets_path) if targets_path.exists() else (DEFAULT_MIN_FLOOR, [])
        )

    if args.check:
        errors = check(repo_root, stats, targets, min_floor)
        for err in errors:
            print(f"FAIL: {err}", file=sys.stderr)
        if errors:
            print(f"stats --check: {len(errors)} problem(s)", file=sys.stderr)
            return 1
        print(
            f"stats --check: OK (tests {floor(stats.tests, min_floor)}+ "
            f"[{stats.tests} exact], patterns {stats.patterns})"
        )
        return 0

    if args.write:
        diffs = apply_targets(repo_root, stats, targets, min_floor, write=args.yes)
        if not diffs:
            print("stats --write: docs already match the single source")
            return 0
        for fname, (original, updated) in diffs.items():
            _print_diff(fname, original, updated, applied=args.yes)
        if not args.yes:
            print("\n(dry-run — re-run with --yes to apply)")
        return 0

    print(
        f"tests={stats.tests} (floor {floor(stats.tests, min_floor)}+)  "
        f"patterns={stats.patterns}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
