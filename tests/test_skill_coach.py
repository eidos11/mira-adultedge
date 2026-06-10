"""TDD for the mira-coach skill — coaching wrapper tests.

Task 5 acceptance criteria:
  ① A diagnosis JSON with a SUPPORTED pattern → coaching filled
     (block non-empty, pattern_id set, note None).
  ② A diagnosis JSON whose primary pattern is UNSUPPORTED → coaching note
     contains "out of v0.x scope" (explicit, ZERO silent skip).

conftest.py adds ``skills/mira-coach/scripts/`` to sys.path so we can
``import coach`` here directly (same pattern as diagnose/ingest).

Design:
  - coach.py is a THIN wrapper: it accepts a diagnosis JSON dict, reconstructs
    the DiagnoseResult, calls coach_from_overlay, and returns the input dict
    with a 'coaching' key ADDED (input keys preserved, not re-serialized).
  - The honest-skip logic lives in the ENGINE (coach_from_overlay in pipeline.py).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

import mira.contracts.minimal as minimal
from mira.pipeline import DiagnoseResult, coach_from_overlay, _primary_pattern_id
from mira.system_a.coaching.coaching import get_available_patterns

# coach module is importable via conftest.py sys.path injection
import coach as coach_mod

_PROJECT_ROOT = Path(__file__).parent.parent
_SCRIPT = _PROJECT_ROOT / "skills" / "mira-coach" / "scripts" / "coach.py"

# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

_SUPPORTED_PATTERN = "fluency_illusion"   # has a coaching template
_UNSUPPORTED_PATTERN = "identity_protective_reasoning"  # NOT in coaching content

# Verify fixture assumptions at import time
assert _SUPPORTED_PATTERN in get_available_patterns(), (
    f"{_SUPPORTED_PATTERN!r} must be a supported pattern for these tests"
)
assert _UNSUPPORTED_PATTERN not in get_available_patterns(), (
    f"{_UNSUPPORTED_PATTERN!r} must NOT be a supported pattern for these tests"
)


def _make_diagnose_json(
    pattern_id: str,
    lane2_status: str = "pass",
    evidence_trace: list[str] | None = None,
    overlay_status: str = "verified",
) -> dict:
    """Build a minimal diagnosis JSON (mira-diagnose-verify output shape)."""
    return {
        "schema_version": "0.2.2",
        "input": "Fixture learner claim for testing.",
        "route_vtype": "I",
        "psr": {
            "P": "medium metacognitive confidence",
            "S": "action_goal",
            "R": "concept",
        },
        "patterns": [
            {
                "pattern_id": pattern_id,
                "lane2_status": lane2_status,
                "evidence_trace": evidence_trace or ["test evidence"],
            }
        ],
        "overlay_status": overlay_status,
        "evidence_summary": "fixture evidence",
    }


def _make_diag_result(
    pattern_id: str,
    lane2_status: str = "pass",
    evidence_trace: list[str] | None = None,
    overlay_status: str = "verified",
) -> DiagnoseResult:
    """Build a DiagnoseResult with a single pattern candidate (for engine tests)."""
    trace = "test-fixture-001"
    req = minimal.SystemAtoCVRequest(
        trace_id=trace,
        learner_claim="Fixture learner claim for testing.",
        claim_language="en",
    )
    overlay = minimal.CVVerificationOverlay(
        trace_id=trace,
        request_id=f"req-{trace}",
        psr=minimal.PSRResult(
            P_appraisal="medium metacognitive confidence",
            S_strategy="action_goal",
            R_projection="concept",
        ),
        route_vtype="I",
        pattern_candidates=[
            minimal.PatternCandidate(
                pattern_id=pattern_id,
                canonical_id=pattern_id,
                vtype="I",
                lane2_status=lane2_status,
                evidence_trace=evidence_trace or ["test evidence"],
            )
        ],
        overlay_status=overlay_status,
        lane1_pass=True,
        evidence_summary="fixture evidence",
    )
    return DiagnoseResult(request=req, overlay=overlay)


# ---------------------------------------------------------------------------
# ENGINE tests — honest-skip logic in coach_from_overlay (pipeline.py)
# ---------------------------------------------------------------------------

class TestEngineHonestSkip:
    """Tests for the Task 5 honest-skip logic that lives in the engine."""

    def test_supported_pattern_note_is_none(self):
        """A supported pattern → note must be None (coaching available)."""
        diag = _make_diag_result(_SUPPORTED_PATTERN, lane2_status="pass")
        coached = coach_from_overlay(diag, lang="en")
        assert coached["coaching"]["note"] is None, (
            f"Supported pattern {_SUPPORTED_PATTERN!r} must not produce a note; "
            f"got note={coached['coaching']['note']!r}"
        )

    def test_supported_pattern_block_nonempty(self):
        """A supported pattern → block must be non-empty."""
        diag = _make_diag_result(_SUPPORTED_PATTERN, lane2_status="pass")
        coached = coach_from_overlay(diag, lang="en")
        assert coached["coaching"]["block"].strip(), (
            "coaching block must be non-empty for a supported pattern"
        )

    def test_supported_pattern_pattern_id_set(self):
        """A supported pattern → pattern_id must be set to the expected ID."""
        diag = _make_diag_result(_SUPPORTED_PATTERN, lane2_status="pass")
        coached = coach_from_overlay(diag, lang="en")
        assert coached["coaching"]["pattern_id"] == _SUPPORTED_PATTERN, (
            f"Expected pattern_id={_SUPPORTED_PATTERN!r}, "
            f"got {coached['coaching']['pattern_id']!r}"
        )

    def test_unsupported_pattern_note_contains_scope_message(self):
        """An unsupported pattern → note MUST contain 'out of v0.x scope'.

        This is the core honesty requirement: ZERO silent skip.
        """
        diag = _make_diag_result(_UNSUPPORTED_PATTERN, lane2_status="pass")
        coached = coach_from_overlay(diag, lang="en")
        note = coached["coaching"]["note"]
        assert note is not None, (
            f"Unsupported pattern {_UNSUPPORTED_PATTERN!r} must produce an explicit "
            f"note (not None). Got note=None — this is a SILENT SKIP (P1 honesty bug)."
        )
        assert "out of v0.x scope" in note, (
            f"note must contain 'out of v0.x scope'; got {note!r}"
        )

    def test_unsupported_pattern_note_names_the_pattern(self):
        """The out-of-scope note must name the pattern ID explicitly."""
        diag = _make_diag_result(_UNSUPPORTED_PATTERN, lane2_status="pass")
        coached = coach_from_overlay(diag, lang="en")
        note = coached["coaching"]["note"]
        assert note is not None
        assert _UNSUPPORTED_PATTERN in note, (
            f"note must name the pattern {_UNSUPPORTED_PATTERN!r}; got {note!r}"
        )

    def test_unsupported_pattern_coaching_shape_preserved(self):
        """Coaching dict must still have all three keys even for unsupported patterns."""
        diag = _make_diag_result(_UNSUPPORTED_PATTERN, lane2_status="pass")
        coached = coach_from_overlay(diag, lang="en")
        c = coached["coaching"]
        assert "block" in c
        assert "pattern_id" in c
        assert "note" in c

    def test_none_pattern_id_note_is_none(self):
        """When primary_pattern_id is None (no evidenced candidates), note stays None."""
        # No pass or evidenced candidates → pattern_id=None → note stays None
        trace = "test-nopat"
        req = minimal.SystemAtoCVRequest(
            trace_id=trace,
            learner_claim="Fixture no-pattern claim.",
            claim_language="en",
        )
        overlay = minimal.CVVerificationOverlay(
            trace_id=trace,
            request_id=f"req-{trace}",
            psr=minimal.PSRResult(
                P_appraisal="P", S_strategy="S", R_projection="R"
            ),
            route_vtype="I",
            pattern_candidates=[],  # empty — no pattern_id
            overlay_status="insufficient_evidence",
            lane1_pass=True,
            evidence_summary="none",
        )
        diag = DiagnoseResult(request=req, overlay=overlay)
        coached = coach_from_overlay(diag, lang="en")
        assert coached["coaching"]["note"] is None, (
            "When pattern_id is None, note must remain None (not an unsupported-pattern case)"
        )


# ---------------------------------------------------------------------------
# SKILL tests — coach.py thin wrapper
# ---------------------------------------------------------------------------

class TestCoachSkillSupportedPattern:
    """Tests for coach.py with a SUPPORTED pattern: coaching must be filled."""

    @pytest.fixture(scope="class")
    def coached_json(self):
        """Feed a diagnosis JSON with a supported pattern through coach_mod.coach()."""
        diag_json = _make_diagnose_json(_SUPPORTED_PATTERN, lane2_status="pass")
        return coach_mod.coach(diag_json, lang="en")

    def test_coaching_key_present(self, coached_json):
        assert "coaching" in coached_json, "coached JSON must have a 'coaching' key"

    def test_coaching_block_nonempty(self, coached_json):
        assert coached_json["coaching"]["block"].strip(), (
            "coaching.block must be non-empty for a supported pattern"
        )

    def test_coaching_pattern_id_set(self, coached_json):
        assert coached_json["coaching"]["pattern_id"] == _SUPPORTED_PATTERN, (
            f"coaching.pattern_id must be {_SUPPORTED_PATTERN!r}"
        )

    def test_coaching_note_is_none(self, coached_json):
        assert coached_json["coaching"]["note"] is None, (
            "coaching.note must be None for a supported pattern"
        )

    def test_input_keys_preserved(self, coached_json):
        """Input JSON keys (schema_version, input, psr, patterns, etc.) must all be preserved."""
        for key in ("schema_version", "input", "route_vtype", "psr", "patterns",
                    "overlay_status", "evidence_summary"):
            assert key in coached_json, (
                f"Input key {key!r} must be preserved in coached output (not re-serialized)"
            )

    def test_schema_version_unchanged(self, coached_json):
        assert coached_json["schema_version"] == "0.2.2"

    def test_input_text_unchanged(self, coached_json):
        assert coached_json["input"] == "Fixture learner claim for testing."

    def test_psr_unchanged(self, coached_json):
        psr = coached_json["psr"]
        assert psr["P"] == "medium metacognitive confidence"
        assert psr["S"] == "action_goal"
        assert psr["R"] == "concept"

    def test_patterns_unchanged(self, coached_json):
        patterns = coached_json["patterns"]
        assert len(patterns) == 1
        assert patterns[0]["pattern_id"] == _SUPPORTED_PATTERN

    def test_coaching_dict_has_all_keys(self, coached_json):
        c = coached_json["coaching"]
        assert "block" in c
        assert "pattern_id" in c
        assert "note" in c


class TestCoachSkillUnsupportedPattern:
    """Tests for coach.py with an UNSUPPORTED pattern: explicit note required (ZERO silent skip)."""

    @pytest.fixture(scope="class")
    def coached_json(self):
        """Feed a diagnosis JSON with an unsupported pattern through coach_mod.coach()."""
        diag_json = _make_diagnose_json(_UNSUPPORTED_PATTERN, lane2_status="pass")
        return coach_mod.coach(diag_json, lang="en")

    def test_coaching_key_present(self, coached_json):
        assert "coaching" in coached_json

    def test_note_is_not_none(self, coached_json):
        """CORE: note must be set — never None for an unsupported pattern."""
        note = coached_json["coaching"]["note"]
        assert note is not None, (
            f"Unsupported pattern {_UNSUPPORTED_PATTERN!r} MUST produce an explicit note "
            "(not None). Silent skip is a P1 honesty bug."
        )

    def test_note_contains_scope_message(self, coached_json):
        note = coached_json["coaching"]["note"]
        assert "out of v0.x scope" in note, (
            f"note must contain 'out of v0.x scope'; got {note!r}"
        )

    def test_note_names_the_pattern(self, coached_json):
        note = coached_json["coaching"]["note"]
        assert _UNSUPPORTED_PATTERN in note, (
            f"note must name the pattern {_UNSUPPORTED_PATTERN!r}; got {note!r}"
        )

    def test_input_keys_preserved(self, coached_json):
        """Input JSON keys must be preserved even when coaching is unsupported."""
        for key in ("schema_version", "input", "route_vtype", "psr", "patterns",
                    "overlay_status", "evidence_summary"):
            assert key in coached_json, (
                f"Input key {key!r} must be preserved in coached output"
            )

    def test_coaching_shape_preserved(self, coached_json):
        """Coaching dict must always have all three keys."""
        c = coached_json["coaching"]
        assert "block" in c
        assert "pattern_id" in c
        assert "note" in c


# ---------------------------------------------------------------------------
# SKILL script surface tests — coach.py as a CLI script
# ---------------------------------------------------------------------------

def _run_coach_subprocess(
    args: list[str],
    stdin_text: str | None = None,
) -> subprocess.CompletedProcess:
    """Run coach.py as a subprocess via the venv Python."""
    import os

    env = os.environ.copy()
    existing_pp = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (
        str(_PROJECT_ROOT) + os.pathsep + existing_pp
        if existing_pp
        else str(_PROJECT_ROOT)
    )
    cmd = [sys.executable, str(_SCRIPT)] + args
    return subprocess.run(
        cmd,
        input=stdin_text,
        capture_output=True,
        text=True,
        env=env,
        cwd=str(_PROJECT_ROOT),
    )


class TestCoachScriptCLI:
    def test_script_file_exists(self):
        assert _SCRIPT.exists(), f"coach.py not found at {_SCRIPT}"

    def test_stdin_mode_produces_valid_json(self):
        diag_json = _make_diagnose_json(_SUPPORTED_PATTERN, lane2_status="pass")
        result = _run_coach_subprocess(["--stdin"], stdin_text=json.dumps(diag_json))
        assert result.returncode == 0, f"coach.py failed: {result.stderr}"
        parsed = json.loads(result.stdout)
        assert isinstance(parsed, dict)
        assert "coaching" in parsed

    def test_stdin_mode_supported_pattern_note_none(self):
        diag_json = _make_diagnose_json(_SUPPORTED_PATTERN, lane2_status="pass")
        result = _run_coach_subprocess(["--stdin"], stdin_text=json.dumps(diag_json))
        assert result.returncode == 0
        parsed = json.loads(result.stdout)
        assert parsed["coaching"]["note"] is None

    def test_stdin_mode_unsupported_pattern_note_set(self):
        """CLI: unsupported pattern → note contains 'out of v0.x scope'."""
        diag_json = _make_diagnose_json(_UNSUPPORTED_PATTERN, lane2_status="pass")
        result = _run_coach_subprocess(["--stdin"], stdin_text=json.dumps(diag_json))
        assert result.returncode == 0, f"coach.py failed: {result.stderr}"
        parsed = json.loads(result.stdout)
        note = parsed["coaching"]["note"]
        assert note is not None, "CLI: unsupported pattern must produce explicit note"
        assert "out of v0.x scope" in note

    def test_file_mode_produces_coached_json(self, tmp_path):
        diag_json = _make_diagnose_json(_SUPPORTED_PATTERN, lane2_status="pass")
        diag_file = tmp_path / "diag.json"
        diag_file.write_text(json.dumps(diag_json))
        result = _run_coach_subprocess([str(diag_file)])
        assert result.returncode == 0, f"coach.py failed: {result.stderr}"
        parsed = json.loads(result.stdout)
        assert "coaching" in parsed

    def test_empty_stdin_exits_nonzero(self):
        result = _run_coach_subprocess(["--stdin"], stdin_text="")
        assert result.returncode != 0, "Empty stdin should exit non-zero"

    def test_invalid_json_exits_nonzero(self):
        result = _run_coach_subprocess(["--stdin"], stdin_text="not valid json")
        assert result.returncode != 0, "Invalid JSON should exit non-zero"

    def test_lang_flag_accepted(self):
        diag_json = _make_diagnose_json(_SUPPORTED_PATTERN, lane2_status="pass")
        result = _run_coach_subprocess(
            ["--stdin", "--lang", "en"], stdin_text=json.dumps(diag_json)
        )
        assert result.returncode == 0, f"coach.py failed: {result.stderr}"

    def test_ko_lang_flag_accepted(self):
        diag_json = _make_diagnose_json(_SUPPORTED_PATTERN, lane2_status="pass")
        result = _run_coach_subprocess(
            ["--stdin", "--lang", "ko"], stdin_text=json.dumps(diag_json)
        )
        assert result.returncode == 0, f"coach.py failed: {result.stderr}"
        parsed = json.loads(result.stdout)
        assert "coaching" in parsed
