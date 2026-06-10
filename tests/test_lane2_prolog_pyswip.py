"""Tests for Lane 2 Prolog verification rules (M1 patch feature-based).

Tests the 3-valued verdict engine (pattern_verify.pl) with
false_dilemma.pl and oversimplified_cause.pl feature-based rules.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import pytest

Prolog: Any = None
PYSWIP_IMPORT_ERROR: BaseException | None = None

try:
    from pyswip import Prolog as _Prolog
    Prolog = _Prolog
except Exception as exc:
    PYSWIP_IMPORT_ERROR = exc

ROOT = Path(__file__).resolve().parents[1]
VERIFY_PL = ROOT / "mira/system_b/rules/prolog/pattern_verify.pl"
FALSE_PL = ROOT / "mira/system_b/rules/prolog/false_dilemma.pl"
OVER_PL = ROOT / "mira/system_b/rules/prolog/oversimplified_cause.pl"

pytestmark = pytest.mark.skipif(
    Prolog is None or shutil.which("swipl") is None,
    reason=f"pyswip + SWI-Prolog required; pyswip_error={PYSWIP_IMPORT_ERROR!r}",
)


def _prolog_engine() -> Any:
    prolog = Prolog()
    prolog.consult(str(VERIFY_PL))
    prolog.consult(str(FALSE_PL))
    prolog.consult(str(OVER_PL))
    return prolog


def _verify(prolog: Any, pattern: str, features: str) -> str:
    rows = list(prolog.query(f"verify({pattern}, {features}, Result).", maxresult=1))
    assert rows, "verify/3 must return at least one result"
    return str(rows[0]["Result"])


# ── false_dilemma ──────────────────────────────────────────────────────

class TestFalseDilemmaVerify:
    def test_accept_classic(self) -> None:
        prolog = _prolog_engine()
        features = "[option_count(2),exclusivity_markers(['either...or']),middle_options_mentioned(false),viable_middle_exists(false),logical_space_explored(explicit)]"
        assert _verify(prolog, "false_dilemma", features) == "accept"

    def test_reject_many_options(self) -> None:
        prolog = _prolog_engine()
        features = "[option_count(4),exclusivity_markers(['only']),middle_options_mentioned(false),viable_middle_exists(false),logical_space_explored(explicit)]"
        assert _verify(prolog, "false_dilemma", features) == "reject"

    def test_unverified_empty_exclusivity(self) -> None:
        """exclusivity_markers is the necessary surface signal — its absence never verifies."""
        prolog = _prolog_engine()
        features = "[option_count(2),exclusivity_markers([]),middle_options_mentioned(false),viable_middle_exists(false),logical_space_explored(explicit)]"
        assert _verify(prolog, "false_dilemma", features) == "unverified"

    # ── F1: pragmatic false dilemma (viable vs dismissed middle) ─────────
    def test_accept_dismissed_middle(self) -> None:
        """F1: a third option mentioned but dismissed (not viable) still verifies —
        the speaker still collapsed the real option space (Walton pragmatic FD)."""
        prolog = _prolog_engine()
        features = "[option_count(2),exclusivity_markers(['either...or']),viable_middle_exists(false)]"
        assert _verify(prolog, "false_dilemma", features) == "accept"

    def test_dismissed_middle_no_longer_rejects(self) -> None:
        """F1: a middle option mentioned-but-dismissed (viable_middle_exists false) now
        verifies instead of being rejected (was 'reject' pre-F1)."""
        prolog = _prolog_engine()
        features = "[option_count(2),exclusivity_markers(['either...or']),middle_options_mentioned(true),viable_middle_exists(false)]"
        assert _verify(prolog, "false_dilemma", features) == "accept"

    def test_reject_viable_middle(self) -> None:
        """F1: a genuinely open middle option (not dismissed) defeats false dilemma."""
        prolog = _prolog_engine()
        features = "[option_count(2),exclusivity_markers(['or']),viable_middle_exists(true)]"
        assert _verify(prolog, "false_dilemma", features) == "reject"

    def test_accept_implicit_space_with_dismissed_middle(self) -> None:
        """F1: implicit collapse of the option space is the typical FD move;
        explicit exploration is no longer required to verify."""
        prolog = _prolog_engine()
        features = "[option_count(2),exclusivity_markers(['only']),viable_middle_exists(false),logical_space_explored(implicit)]"
        assert _verify(prolog, "false_dilemma", features) == "accept"

    def test_reject_trumps_accept_conditions(self) -> None:
        """reject > accept priority: viable_middle_exists(true) overrides all accept conditions."""
        prolog = _prolog_engine()
        features = "[option_count(2),exclusivity_markers(['or']),viable_middle_exists(true),logical_space_explored(explicit)]"
        assert _verify(prolog, "false_dilemma", features) == "reject"


# ── oversimplified_cause ───────────────────────────────────────────────

class TestOversimplifiedCauseVerify:
    def test_accept_behavioral_single_cause(self) -> None:
        prolog = _prolog_engine()
        features = "[cause_count(1),alternative_causes_mentioned(false),sufficiency_claim_strength(strong),causal_claim_type(behavioral)]"
        assert _verify(prolog, "oversimplified_cause", features) == "accept"

    def test_accept_social_cause(self) -> None:
        prolog = _prolog_engine()
        features = "[cause_count(1),alternative_causes_mentioned(false),sufficiency_claim_strength(strong),causal_claim_type(social)]"
        assert _verify(prolog, "oversimplified_cause", features) == "accept"

    def test_reject_multiple_causes(self) -> None:
        prolog = _prolog_engine()
        features = "[cause_count(3),alternative_causes_mentioned(false),sufficiency_claim_strength(strong),causal_claim_type(behavioral)]"
        assert _verify(prolog, "oversimplified_cause", features) == "reject"

    def test_reject_alternatives_mentioned(self) -> None:
        prolog = _prolog_engine()
        features = "[cause_count(1),alternative_causes_mentioned(true),sufficiency_claim_strength(strong),causal_claim_type(behavioral)]"
        assert _verify(prolog, "oversimplified_cause", features) == "reject"

    def test_unverified_physical_direct(self) -> None:
        prolog = _prolog_engine()
        features = "[cause_count(1),alternative_causes_mentioned(false),sufficiency_claim_strength(strong),causal_claim_type(physical_direct)]"
        assert _verify(prolog, "oversimplified_cause", features) == "unverified"

    def test_unverified_weak_sufficiency(self) -> None:
        prolog = _prolog_engine()
        features = "[cause_count(1),alternative_causes_mentioned(false),sufficiency_claim_strength(weak),causal_claim_type(behavioral)]"
        assert _verify(prolog, "oversimplified_cause", features) == "unverified"


# ── Cross-pattern isolation ────────────────────────────────────────────

class TestCrossPattern:
    def test_false_dilemma_features_dont_trigger_oversimplified(self) -> None:
        prolog = _prolog_engine()
        features = "[option_count(2),exclusivity_markers(['or']),middle_options_mentioned(false),logical_space_explored(explicit)]"
        assert _verify(prolog, "oversimplified_cause", features) == "unverified"

    def test_oversimplified_features_dont_trigger_false_dilemma(self) -> None:
        prolog = _prolog_engine()
        features = "[cause_count(1),alternative_causes_mentioned(false),sufficiency_claim_strength(strong),causal_claim_type(behavioral)]"
        assert _verify(prolog, "false_dilemma", features) == "unverified"
