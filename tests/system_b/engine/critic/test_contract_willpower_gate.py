"""TDD test for Task 1: check 15 (willpower_blame_trigger) removal.

Spec D4: willpower mention must NOT produce a blocking violation.
"""

from __future__ import annotations

from mira.system_b.engine.critic.contract import (
    LaneOneInput,
    PSRDecomposition,
    contract_critic,
)


def _make_minimal_psr() -> PSRDecomposition:
    return PSRDecomposition(
        P_appraisal="The learner attributes failure to a single cause.",
        P_latitude="medium",
        claim_type="self_assessment",
        S_strategy="The learner plans to keep the same study routine.",
        S_exclusivity="open",
        R_projection="The learner expects ongoing difficulty.",
        R_emotional_load="neutral",
    )


def test_willpower_mention_no_longer_blocks() -> None:
    """check 15 removed per spec D4: willpower mention -> no blocking violation."""
    inp = LaneOneInput(
        psr=_make_minimal_psr(),
        pattern_ids=["false_dilemma"],
        primary_route="D",
        vtype_claimed="D",
        response_text="If your explanation ends with 'lack of willpower' alone...",
        trace_id="t",
    )
    audit = contract_critic(inp)
    blocking = [v for v in audit.violations if v.severity == "blocking"]
    assert not any(v.check_id == 15 for v in blocking), "check 15 must be removed"
