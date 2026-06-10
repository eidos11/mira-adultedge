"""Contract round-trip test for the mira skill family.

Proves that the 3-skill pipeline composes end-to-end:

    text → diagnose-verify → diag.json (no coaching)
         → mira-coach      → coached.json (coaching added, all diag keys preserved)
         → mira-report     → html / expert md

Acceptance criteria (Task 7):
  1. diagnose output has no coaching key (pre-coaching stage invariant).
  2. coached output has structured coaching + ALL original diag keys preserved
     (accumulating-object invariant: diag keys ⊆ coached keys).
  3. coached JSON is accepted by the report stage (ingest does not reject it).
  4. final html contains a coaching section consistent with the case.
  5. final expert md contains a coaching section.
  6. schema consistency across hops (each stage's output is valid input to next).

Known contract mismatch gated:
  ingest.py line 122 reads data["lane1_pass"] — but diagnose.py (and coach.py)
  do NOT emit lane1_pass (it is absent by design in the pre-coaching stage;
  it is computed inside coach_from_overlay and lives on updated_overlay, not on
  the dict surface that coach.py returns).
  If the mismatch is present this suite will raise a KeyError in test_render_*
  proving the gap is real and must be reconciled.

Design:
  - At least one full subprocess CLI chain (most faithful to "skill family").
  - Also uses the Python API for accumulating-object assertions (faster, same contract).
  - conftest.py puts skill scripts on sys.path (same pattern as other skill tests).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

# conftest.py injects skills/.../scripts into sys.path
import diagnose as diagnose_mod
import coach as coach_mod
import render as render_mod
from ingest import ingest, UnsupportedSchemaVersionError

_PROJECT_ROOT = Path(__file__).parent.parent
_DIAGNOSE_SCRIPT = _PROJECT_ROOT / "skills" / "mira-diagnose-verify" / "scripts" / "diagnose.py"
_COACH_SCRIPT = _PROJECT_ROOT / "skills" / "mira-coach" / "scripts" / "coach.py"
_REPORT_SCRIPTS_DIR = _PROJECT_ROOT / "skills" / "mira-report" / "scripts"

# A real reasoning text that exercises the fluency_illusion / willpower_blame patterns.
_CLAIM_EN = "I failed because I'm not smart enough — I just don't have what it takes."

# Keys that diagnose-verify emits (its full contract, per _build_diagnose_json docstring).
_DIAGNOSE_KEYS = {
    "schema_version",
    "input",
    "route_vtype",
    "psr",
    "patterns",
    "overlay_status",
    "evidence_summary",
}

# Keys that MUST be absent from diagnose output (pre-coaching stage invariant).
_DIAGNOSE_ABSENT_KEYS = {"coaching", "report", "lane1_pass"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _env_with_pythonpath() -> dict:
    """Return an env dict with PROJECT_ROOT injected into PYTHONPATH."""
    env = os.environ.copy()
    existing_pp = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (
        str(_PROJECT_ROOT) + os.pathsep + existing_pp
        if existing_pp
        else str(_PROJECT_ROOT)
    )
    return env


def _run_subprocess(script: Path, args: list[str], stdin_text: str | None = None) -> subprocess.CompletedProcess:
    """Run a skill script as a subprocess."""
    return subprocess.run(
        [sys.executable, str(script)] + args,
        input=stdin_text,
        capture_output=True,
        text=True,
        env=_env_with_pythonpath(),
        cwd=str(_PROJECT_ROOT),
    )


def _run_render_subprocess(coached_json_path: Path, mode: str) -> subprocess.CompletedProcess:
    """Run the mira-report render stage as a real subprocess.

    render.py exposes no argparse CLI; its documented invocation (SKILL.md
    "Usage") is ``python -c "...; import render; print(render.render(...))"``.
    This mirrors that contract exactly so the full chain (diagnose → coach →
    render) is end-to-end via subprocess.
    """
    program = (
        "import json, sys; "
        f"sys.path.insert(0, {str(_REPORT_SCRIPTS_DIR)!r}); "
        "import render; "
        f"print(render.render(json.load(open({str(coached_json_path)!r})), mode={mode!r}))"
    )
    return subprocess.run(
        [sys.executable, "-c", program],
        capture_output=True,
        text=True,
        env=_env_with_pythonpath(),
        cwd=str(_PROJECT_ROOT),
    )


# ---------------------------------------------------------------------------
# Fixtures — shared across the test class
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def diag_json_via_api() -> dict:
    """Run diagnose_only + _build_diagnose_json via Python API (fast, same contract)."""
    from mira.pipeline import diagnose_only
    diag = diagnose_only(_CLAIM_EN, lang="en")
    return diagnose_mod._build_diagnose_json(diag, learner_input=_CLAIM_EN)


@pytest.fixture(scope="module")
def coached_json_via_api(diag_json_via_api: dict) -> dict:
    """Run coach.coach() on the diagnose output via Python API."""
    return coach_mod.coach(diag_json_via_api, lang="en")


@pytest.fixture(scope="module")
def subprocess_chain_coached_file(tmp_path_factory) -> Path:
    """Full CLI subprocess chain: diagnose.py | coach.py → coached.json on disk.

    This is the most faithful end-to-end test — same as users running the
    2-step pipeline from the SKILL.md usage contract. Returns the PATH to the
    coached JSON so a downstream render subprocess can consume it directly.
    """
    tmp = tmp_path_factory.mktemp("roundtrip_cli")
    diag_file = tmp / "diag.json"
    coached_file = tmp / "coached.json"

    # Step 1: diagnose.py → diag.json
    result1 = _run_subprocess(_DIAGNOSE_SCRIPT, [_CLAIM_EN])
    assert result1.returncode == 0, (
        f"diagnose.py failed (exit {result1.returncode}):\n{result1.stderr}"
    )
    diag_file.write_text(result1.stdout, encoding="utf-8")

    # Step 2: coach.py diag.json → coached.json
    result2 = _run_subprocess(_COACH_SCRIPT, [str(diag_file)])
    assert result2.returncode == 0, (
        f"coach.py failed (exit {result2.returncode}):\n{result2.stderr}"
    )
    coached_file.write_text(result2.stdout, encoding="utf-8")

    return coached_file


@pytest.fixture(scope="module")
def subprocess_chain_result(subprocess_chain_coached_file: Path) -> dict:
    """The final coached JSON dict from the subprocess diagnose → coach chain."""
    return json.loads(subprocess_chain_coached_file.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Stage 1: diagnose output contract
# ---------------------------------------------------------------------------

class TestDiagnoseContract:
    """Verify diagnose-verify output satisfies its contract (pre-coaching stage)."""

    def test_all_required_keys_present(self, diag_json_via_api):
        missing = _DIAGNOSE_KEYS - set(diag_json_via_api)
        assert not missing, f"diagnose output missing keys: {missing}"

    def test_coaching_absent(self, diag_json_via_api):
        assert "coaching" not in diag_json_via_api, (
            "coaching MUST be absent from diagnose output (pre-coaching stage)"
        )

    def test_report_absent(self, diag_json_via_api):
        assert "report" not in diag_json_via_api

    def test_lane1_pass_absent(self, diag_json_via_api):
        """lane1_pass is intentionally absent — computed in coach_from_overlay."""
        assert "lane1_pass" not in diag_json_via_api, (
            "lane1_pass must NOT appear in diagnose output "
            "(it is computed by run_reduced_critic inside coach_from_overlay)"
        )

    def test_schema_version_supported(self, diag_json_via_api):
        assert diag_json_via_api["schema_version"] == "0.2.2"

    def test_input_preserved(self, diag_json_via_api):
        assert diag_json_via_api["input"] == _CLAIM_EN

    def test_psr_has_p_s_r(self, diag_json_via_api):
        psr = diag_json_via_api["psr"]
        assert "P" in psr and "S" in psr and "R" in psr

    def test_patterns_is_list(self, diag_json_via_api):
        assert isinstance(diag_json_via_api["patterns"], list)


# ---------------------------------------------------------------------------
# Stage 2: coached output — accumulating-object invariant
# ---------------------------------------------------------------------------

class TestCoachAccumulatingObject:
    """Verify that coach preserves all diagnose keys and adds coaching (additive only)."""

    def test_coaching_key_added(self, coached_json_via_api):
        assert "coaching" in coached_json_via_api, (
            "coached output must have a 'coaching' key"
        )

    def test_all_diag_keys_preserved(self, coached_json_via_api):
        """Accumulating-object invariant: every key in diagnose output must survive."""
        missing = _DIAGNOSE_KEYS - set(coached_json_via_api)
        assert not missing, (
            f"Accumulating-object invariant VIOLATED: "
            f"coach dropped these diagnose keys: {missing}"
        )

    def test_coach_adds_only_coaching_key(self, coached_json_via_api, diag_json_via_api):
        """Additive direction: coach adds EXACTLY 'coaching' — no other new keys.

        Closes the additive-direction gap: test_all_diag_keys_preserved checks
        that no diagnose key is DROPPED; this checks that no UNEXPECTED key is
        ADDED (catches an accidental lane1_pass / report / etc. leaking into the
        coached object). Together they pin the accumulating object to exactly
        diag_keys ∪ {coaching}.
        """
        added = set(coached_json_via_api) - set(diag_json_via_api)
        assert added == {"coaching"}, (
            f"coach must add ONLY the 'coaching' key (strict additive contract); "
            f"unexpected extra keys: {sorted(added - {'coaching'})}"
        )

    def test_input_text_unchanged(self, coached_json_via_api):
        assert coached_json_via_api["input"] == _CLAIM_EN

    def test_schema_version_unchanged(self, coached_json_via_api):
        assert coached_json_via_api["schema_version"] == "0.2.2"

    def test_psr_unchanged(self, coached_json_via_api, diag_json_via_api):
        assert coached_json_via_api["psr"] == diag_json_via_api["psr"]

    def test_patterns_unchanged(self, coached_json_via_api, diag_json_via_api):
        assert coached_json_via_api["patterns"] == diag_json_via_api["patterns"]

    def test_overlay_status_unchanged(self, coached_json_via_api, diag_json_via_api):
        assert coached_json_via_api["overlay_status"] == diag_json_via_api["overlay_status"]

    def test_coaching_has_all_sub_fields(self, coached_json_via_api):
        c = coached_json_via_api["coaching"]
        assert "block" in c, "coaching.block must be present"
        assert "pattern_id" in c, "coaching.pattern_id must be present"
        assert "note" in c, "coaching.note must be present"

    def test_coaching_block_nonempty_or_no_match(self, coached_json_via_api):
        """block must be non-empty (coaching text or no-match guidance)."""
        c = coached_json_via_api["coaching"]
        assert c["block"].strip(), "coaching.block must not be empty"

    def test_lane1_pass_absent_from_coached_json(self, coached_json_via_api):
        """coach.py does NOT surface lane1_pass on the JSON dict (only coaching is added).

        This documents the known absence: ingest.py must handle it gracefully.
        """
        assert "lane1_pass" not in coached_json_via_api, (
            "lane1_pass must not appear in coached JSON dict "
            "(coach.py contract: additive, only 'coaching' is added to diag keys)"
        )


# ---------------------------------------------------------------------------
# Stage 3: schema consistency gate — coached JSON accepted by ingest
# ---------------------------------------------------------------------------

class TestSchemaConsistency:
    """Verify that the coached JSON passes the ingest schema gate.

    This is the critical contract-mismatch test: if ingest.py requires
    lane1_pass and coached JSON lacks it, a KeyError surfaces here —
    proving the gap that this task was designed to surface.
    """

    def test_ingest_accepts_coached_json(self, coached_json_via_api):
        """ingest() must not raise on a coached JSON produced by the skill chain.

        If ingest.py does data["lane1_pass"] and coached JSON lacks lane1_pass,
        this test raises KeyError — confirming the contract mismatch.
        """
        try:
            overlay = ingest(coached_json_via_api)
        except KeyError as exc:
            pytest.fail(
                f"CONTRACT MISMATCH: ingest(coached_json) raised KeyError {exc!r}. "
                f"coached JSON keys: {sorted(coached_json_via_api)}. "
                f"ingest.py accesses data['lane1_pass'] but coached JSON has no lane1_pass key. "
                f"ingest.py must use data.get('lane1_pass', True) to accept the coached path."
            )
        except UnsupportedSchemaVersionError as exc:
            pytest.fail(
                f"CONTRACT MISMATCH: ingest(coached_json) rejected schema_version: {exc}"
            )
        assert overlay is not None

    def test_ingest_produces_valid_overlay(self, coached_json_via_api):
        """The overlay rebuilt by ingest must have the expected attributes."""
        overlay = ingest(coached_json_via_api)
        assert hasattr(overlay, "psr")
        assert hasattr(overlay, "pattern_candidates")
        assert hasattr(overlay, "overlay_status")

    def test_schema_version_gate_fires_on_bad_version(self):
        """Sanity: schema gate still rejects bad versions."""
        bad_data = {
            "schema_version": "0.1.0",
            "input": "test",
            "route_vtype": "I",
            "psr": {"P": "x", "S": "y", "R": "z"},
            "patterns": [],
            "overlay_status": "insufficient_evidence",
            "evidence_summary": "none",
            "coaching": {"block": "", "pattern_id": None, "note": None},
        }
        with pytest.raises(UnsupportedSchemaVersionError):
            ingest(bad_data)


# ---------------------------------------------------------------------------
# Stage 4: render — coached JSON → html and expert md
# ---------------------------------------------------------------------------

class TestRenderFromCoachedJson:
    """Verify that render() produces output for both html and expert modes
    when given the coached JSON from the skill chain.
    """

    def test_render_html_does_not_raise(self, coached_json_via_api):
        """render(coached, mode='html') must not raise."""
        out = render_mod.render(coached_json_via_api, mode="html")
        assert out.strip().startswith("<!DOCTYPE html>")

    def test_render_html_contains_coaching_section(self, coached_json_via_api):
        """HTML output must contain a Coaching section."""
        out = render_mod.render(coached_json_via_api, mode="html")
        assert "<h2>Coaching</h2>" in out, (
            "html render must include a Coaching section "
            "(coaching field present in coached JSON)"
        )

    def test_render_html_coaching_block_content_present(self, coached_json_via_api):
        """HTML must contain ACTUAL TEXT from the coaching block (not just the heading).

        Extracts a multi-word phrase from the block body — stripped of the
        leading '## Coaching' heading and markdown bullet/bold markers — and
        asserts it survives into the rendered HTML. This verifies genuine
        content rendering, not merely the presence of the section heading.
        """
        coaching_block = coached_json_via_api["coaching"]["block"]
        assert coaching_block.strip(), "fixture precondition: coaching block must be non-empty"

        # Find a real content line (skip the heading, blank lines, bullet markers).
        fragment = None
        for raw in coaching_block.splitlines():
            line = raw.strip().lstrip("-> ").strip()
            # Drop a leading '## Coaching' heading line and any other heading.
            if line.startswith("#"):
                continue
            # Strip markdown bold so the fragment matches the escaped HTML text.
            line = line.replace("**", "")
            # Coaching lines use "pattern name — description" format. The
            # pattern name becomes <strong>text</strong> in HTML (split from
            # the following " — "), so take the fragment from the DESCRIPTION
            # part (after " — ") when that separator is present.
            if " — " in line:
                line = line.split(" — ", 1)[1]
            words = line.split()
            if len(words) >= 3:
                # Take a 3-word window — long enough to be distinctive, short
                # enough to survive _md_to_html line-by-line transformation.
                fragment = " ".join(words[:3])
                break

        assert fragment is not None, (
            f"could not extract a content fragment from coaching block: {coaching_block!r}"
        )

        out = render_mod.render(coached_json_via_api, mode="html")
        assert fragment in out, (
            f"coaching block text fragment {fragment!r} must appear in rendered html "
            f"(content rendering, not just the <h2>Coaching</h2> heading)"
        )

    def test_render_html_is_self_contained(self, coached_json_via_api):
        """HTML report is a self-contained page (has DOCTYPE, style, body)."""
        out = render_mod.render(coached_json_via_api, mode="html")
        assert "<style>" in out
        assert "Diagnosis Summary" in out

    def test_render_expert_does_not_raise(self, coached_json_via_api):
        """render(coached, mode='expert') must not raise."""
        out = render_mod.render(coached_json_via_api, mode="expert")
        assert "## Diagnosis Summary" in out

    def test_render_expert_contains_coaching_section(self, coached_json_via_api):
        """Expert md must contain a Coaching section."""
        out = render_mod.render(coached_json_via_api, mode="expert")
        assert "## Coaching" in out, (
            "expert render must include a ## Coaching section "
            "(coaching field present in coached JSON)"
        )

    def test_render_expert_coaching_not_double_rendered(self, coached_json_via_api):
        """Coaching must appear exactly once (no double-render from both paths)."""
        out = render_mod.render(coached_json_via_api, mode="expert")
        assert out.count("## Coaching") == 1, (
            f"## Coaching appears {out.count('## Coaching')} times; expected exactly 1 "
            "(structured coaching must replace, not supplement, overlay coaching)"
        )


# ---------------------------------------------------------------------------
# Full CLI subprocess chain — most faithful end-to-end
# ---------------------------------------------------------------------------

class TestSubprocessChain:
    """End-to-end test using real subprocess CLI invocations.

    This mirrors exactly how users run the 2-step pipeline from SKILL.md.
    """

    def test_subprocess_chain_produces_valid_json(self, subprocess_chain_result):
        assert isinstance(subprocess_chain_result, dict)

    def test_subprocess_chain_coaching_present(self, subprocess_chain_result):
        assert "coaching" in subprocess_chain_result, (
            "CLI chain output must have 'coaching' key"
        )

    def test_subprocess_chain_all_diag_keys_preserved(self, subprocess_chain_result):
        """Accumulating-object invariant: subprocess chain must preserve diag keys."""
        missing = _DIAGNOSE_KEYS - set(subprocess_chain_result)
        assert not missing, (
            f"CLI chain: diagnose keys missing in coached output: {missing}"
        )

    def test_subprocess_chain_schema_version(self, subprocess_chain_result):
        assert subprocess_chain_result["schema_version"] == "0.2.2"

    def test_subprocess_chain_input_text(self, subprocess_chain_result):
        assert subprocess_chain_result["input"] == _CLAIM_EN

    def test_subprocess_chain_ingest_accepts_output(self, subprocess_chain_result):
        """The real subprocess output must pass the ingest schema gate."""
        try:
            overlay = ingest(subprocess_chain_result)
        except (KeyError, UnsupportedSchemaVersionError) as exc:
            pytest.fail(
                f"CONTRACT MISMATCH in subprocess chain: ingest raised {exc!r}. "
                f"coached JSON keys: {sorted(subprocess_chain_result)}"
            )
        assert overlay is not None

    def test_subprocess_chain_render_html(self, subprocess_chain_result):
        """CLI chain output is renderable to html (in-process render)."""
        out = render_mod.render(subprocess_chain_result, mode="html")
        assert out.strip().startswith("<!DOCTYPE html>")

    def test_subprocess_chain_render_expert(self, subprocess_chain_result):
        """CLI chain output is renderable to expert md (in-process render)."""
        out = render_mod.render(subprocess_chain_result, mode="expert")
        assert "## Diagnosis Summary" in out
        assert "## Coaching" in out

    # --- Fully-subprocess end-to-end: diagnose → coach → render all subprocess --

    def test_full_subprocess_chain_render_html(self, subprocess_chain_coached_file):
        """diagnose.py → coach.py → render(html) — ALL three stages via subprocess.

        Completes a fully-subprocess end-to-end chain using each skill's
        documented invocation (render via the SKILL.md ``python -c`` contract).
        """
        result = _run_render_subprocess(subprocess_chain_coached_file, mode="html")
        assert result.returncode == 0, (
            f"render subprocess (html) failed (exit {result.returncode}):\n{result.stderr}"
        )
        out = result.stdout
        assert out.strip().startswith("<!DOCTYPE html>")
        assert "Diagnosis Summary" in out
        assert "<h2>Coaching</h2>" in out

    def test_full_subprocess_chain_render_expert(self, subprocess_chain_coached_file):
        """diagnose.py → coach.py → render(expert) — ALL three stages via subprocess."""
        result = _run_render_subprocess(subprocess_chain_coached_file, mode="expert")
        assert result.returncode == 0, (
            f"render subprocess (expert) failed (exit {result.returncode}):\n{result.stderr}"
        )
        out = result.stdout
        assert "## Diagnosis Summary" in out
        assert "## Coaching" in out
        # Single coaching section even through the full subprocess chain.
        assert out.count("## Coaching") == 1
