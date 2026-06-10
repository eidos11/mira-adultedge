
"""Alpha 31-case regression: NEU FP removal + route-independence (gate redesign).

Encodes the fixed behaviour introduced by the coaching gate redesign (T1-T5):
  - verified   → assertive coaching
  - unverified → tentative coaching  (framed with *may*)
  - rejected   → silent
  - healthy/NEU cases must NOT receive assertive coaching with backend=none

With MIRA_LLM_EXTRACT_BACKEND=none (deterministic), ALL patterns are
``unverified``; no ``pass`` lane2_status is reachable.  Therefore:
  (a) NEU FP regression:  the 4 NEU/healthy cases must NOT show assertive coaching
  (b) Route-independence: coaching type is determined by verification state,
      not by route_vtype; both A-route NEU and D-route NEU remain tentative/silent

Out of scope (backend=none): the verified-assertive path is NOT exercised here.
That path requires backend=ON and is deferred to a future session.
"""

from __future__ import annotations

import pathlib
import re

import pytest

from mira.pipeline import run_minimal_loop
from mira.report import REPORT_BLOCK_SEPARATOR

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ALPHA_DIR = pathlib.Path(__file__).parent.parent / "eval" / "alpha-test"

# Tentative lead phrases produced by generate_coaching_block(tentative=True)
_TENTATIVE_LEADS = (
    "*may* point to the following",
    "*해당할 수 있습니다*",
    "may apply — please check",
)

# Pattern-coaching bold-header line, e.g.:
#   "**false dilemma** — Your reasoning appears..."
# This is the assertive coaching marker (appears for BOTH tentative and
# assertive blocks, but is preceded by a tentative lead only in the
# tentative case).
_BOLD_PATTERN_HEADER_RE = re.compile(r"^\*\*[\w ]+\*\*\s*—\s*\S")


def _coaching_block(result_report: str) -> str:
    """Return the coaching section from a pipeline report string."""
    return result_report.split(REPORT_BLOCK_SEPARATOR)[-1]


def _is_assertive(coaching_block: str) -> bool:
    """Return True if the coaching block contains assertive (non-tentative) coaching.

    A coaching block is ASSERTIVE if it contains a pattern coaching header
    (bold pattern name followed by '—') that is NOT guarded by a *may* tentative
    lead-in at any earlier point in the same coaching section.

    A coaching block is tentative if every bold-header line is preceded (somewhere
    earlier in the block) by a tentative lead phrase.

    A coaching block is silent if it contains no bold-header lines at all
    (coach_none / coach_reject / coach_needs_review text).

    With backend=none no pattern can achieve lane2_status='pass', so any assertive
    coaching would indicate the gate is still keying on route instead of
    verification state — which is the FP we are guarding against.
    """
    lines = coaching_block.split("\n")
    has_tentative_lead = False
    for line in lines:
        # Track whether a tentative lead has appeared
        if any(phrase in line for phrase in _TENTATIVE_LEADS):
            has_tentative_lead = True
        # Bold pattern header line
        if _BOLD_PATTERN_HEADER_RE.match(line.strip()):
            if not has_tentative_lead:
                # Found a bold coaching header with no preceding tentative lead
                return True
            # Each tentative lead covers all bold headers in its block; reset
            # only if a fresh tentative-lead-less section were to start.
            # In practice generate_coaching_block emits one lead per block so
            # the flag should already be set by the time we reach the header.
    return False


def _run_case(case_id: str):
    """Load a named alpha-test case and run it through the full pipeline."""
    path = _ALPHA_DIR / f"{case_id}.txt"
    text = path.read_text()
    return run_minimal_loop(text)


# ---------------------------------------------------------------------------
# NEU / healthy case IDs
# ---------------------------------------------------------------------------

NEU_CASES = [
    "A01-willpower-false-positive",
    "A04-neu-healthy-reasoning",
    "C06-reddit-neu-studying-metacognition",
    "C07-reddit-neu-med-student-exam",
]

# ---------------------------------------------------------------------------
# NEU FP regression tests (primary gate)
# ---------------------------------------------------------------------------


class TestNEUFalsePositiveRegression:
    """Gate: NEU/healthy cases must NOT receive assertive coaching (backend=none).

    With backend=none all patterns are unverified → coaching must be framed
    with '*may*' tentative lead-in (or be silent / coach_none).  Assertive
    (non-tentative, non-silent) coaching on a healthy case is a false positive.

    These 4 cases were the original FP corpus that motivated the redesign.
    """

    @pytest.mark.parametrize("case_id", NEU_CASES)
    def test_neu_case_not_assertive(self, case_id: str) -> None:
        """NEU/healthy case must NOT produce assertive coaching (FP=0 target)."""
        result = _run_case(case_id)
        cb = _coaching_block(result.report)

        assert not _is_assertive(cb), (
            f"REGRESSION: {case_id} produced assertive coaching.\n"
            f"route_vtype={result.overlay.route_vtype!r}\n"
            f"overlay_status={result.overlay.overlay_status!r}\n"
            f"coaching_block (first 400 chars):\n{cb[:400]}"
        )

    def test_all_neu_cases_fp_count_zero(self) -> None:
        """Aggregate gate: total assertive-coaching count across all 4 NEU cases = 0."""
        fp_cases = []
        for case_id in NEU_CASES:
            result = _run_case(case_id)
            cb = _coaching_block(result.report)
            if _is_assertive(cb):
                fp_cases.append(case_id)

        assert fp_cases == [], (
            f"REGRESSION: {len(fp_cases)} NEU case(s) received assertive coaching:\n"
            + "\n".join(f"  - {c}" for c in fp_cases)
        )


# ---------------------------------------------------------------------------
# Route-independence tests
# ---------------------------------------------------------------------------


class TestRouteIndependence:
    """Gate: coaching tone is determined by verification state, not route.

    Pre-redesign, route=A forced oversimplified_cause coaching assertively;
    route=D/I produced silent output.  This caused NEU(route=A) cases to be
    wrongly flagged (FP) while NEU(route=D) were silently correct for the
    wrong reason.

    Post-redesign: coaching type depends only on lane2_status:
      - verified (pass)    → assertive
      - unverified + evidenced (tentative cap-3) → tentative
      - rejected (fail)    → silent
    Route is NEVER the deciding factor.

    With backend=none, all patterns stay unverified → all cases produce tentative
    or silent output regardless of route.  A NEU case on route A and a NEU case
    on route D must both be non-assertive.
    """

    def test_neu_route_a_not_assertive(self) -> None:
        """NEU cases with route=A must not be assertive (old FP path)."""
        route_a_neu = []
        for case_id in NEU_CASES:
            result = _run_case(case_id)
            if result.overlay.route_vtype == "A":
                cb = _coaching_block(result.report)
                if _is_assertive(cb):
                    route_a_neu.append(case_id)

        assert route_a_neu == [], (
            f"REGRESSION: route=A NEU case(s) still assertive: {route_a_neu}"
        )

    def test_neu_route_d_not_assertive(self) -> None:
        """NEU cases with route=D must not be assertive (old silent-for-wrong-reason path)."""
        route_d_neu = []
        for case_id in NEU_CASES:
            result = _run_case(case_id)
            if result.overlay.route_vtype == "D":
                cb = _coaching_block(result.report)
                if _is_assertive(cb):
                    route_d_neu.append(case_id)

        assert route_d_neu == [], (
            f"REGRESSION: route=D NEU case(s) still assertive: {route_d_neu}"
        )

    def test_different_routes_same_coaching_type_for_neu(self) -> None:
        """A01 (route=A, NEU) and A04 (route=D, NEU) must both be non-assertive.

        This is the cross-route parity check: two NEU cases on DIFFERENT routes
        must receive the SAME (non-assertive) coaching type, showing that route
        no longer determines coaching tone.
        """
        a01 = _run_case("A01-willpower-false-positive")
        a04 = _run_case("A04-neu-healthy-reasoning")

        # Verify routes ARE different (so the test is meaningful)
        assert a01.overlay.route_vtype != a04.overlay.route_vtype, (
            "Precondition failed: A01 and A04 should have different routes for this test"
        )

        a01_assertive = _is_assertive(_coaching_block(a01.report))
        a04_assertive = _is_assertive(_coaching_block(a04.report))

        assert not a01_assertive, (
            f"A01 (route={a01.overlay.route_vtype}) produced assertive coaching — FP"
        )
        assert not a04_assertive, (
            f"A04 (route={a04.overlay.route_vtype}) produced assertive coaching — FP"
        )
