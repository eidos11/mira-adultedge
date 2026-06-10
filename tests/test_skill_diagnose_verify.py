"""TDD for the mira-diagnose-verify skill — smoke tests.

The skill exposes stages 1-3 of the pipeline (diagnose_only) via a thin
wrapper script (scripts/diagnose.py).  The script emits a diagnosis JSON that:
  - contains overlay data: route_vtype, psr, patterns, overlay_status
  - contains NO coaching key  (pre-coaching stage; coaching is Task 5)
  - contains NO report key    (report requires coaching; this is pre-report)

conftest.py adds ``skills/mira-diagnose-verify/scripts/`` to sys.path so we
can ``import diagnose`` here directly (same pattern as test_skill_ingest.py
importing ``ingest`` and test_skill_render.py importing ``render``).

Subprocess tests use ``uv run python diagnose.py`` with the project root as
cwd (which ensures mira is importable via the installed package).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

# diagnose module is importable via conftest.py sys.path injection
import diagnose as diagnose_mod

_PROJECT_ROOT = Path(__file__).parent.parent
_SCRIPT = _PROJECT_ROOT / "skills" / "mira-diagnose-verify" / "scripts" / "diagnose.py"
_CLAIM = "I failed because I'm not smart enough."


# ---------------------------------------------------------------------------
# Internal API: _build_diagnose_json
# ---------------------------------------------------------------------------

class TestBuildDiagnoseJson:
    """Unit tests for the _build_diagnose_json serializer."""

    @pytest.fixture(scope="class")
    def diag_result(self):
        from mira.pipeline import diagnose_only
        return diagnose_only(_CLAIM, lang="en")

    def test_schema_version_present(self, diag_result):
        out = diagnose_mod._build_diagnose_json(diag_result, learner_input=_CLAIM)
        assert "schema_version" in out

    def test_input_key_present(self, diag_result):
        out = diagnose_mod._build_diagnose_json(diag_result, learner_input=_CLAIM)
        assert "input" in out
        assert out["input"] == _CLAIM

    def test_route_vtype_present(self, diag_result):
        out = diagnose_mod._build_diagnose_json(diag_result, learner_input=_CLAIM)
        assert "route_vtype" in out
        assert out["route_vtype"]

    def test_psr_present_with_keys(self, diag_result):
        out = diagnose_mod._build_diagnose_json(diag_result, learner_input=_CLAIM)
        assert "psr" in out
        psr = out["psr"]
        assert "P" in psr
        assert "S" in psr
        assert "R" in psr

    def test_patterns_present(self, diag_result):
        out = diagnose_mod._build_diagnose_json(diag_result, learner_input=_CLAIM)
        assert "patterns" in out
        assert isinstance(out["patterns"], list)

    def test_overlay_status_present(self, diag_result):
        out = diagnose_mod._build_diagnose_json(diag_result, learner_input=_CLAIM)
        assert "overlay_status" in out

    def test_evidence_summary_present(self, diag_result):
        out = diagnose_mod._build_diagnose_json(diag_result, learner_input=_CLAIM)
        assert "evidence_summary" in out

    def test_coaching_key_absent(self, diag_result):
        """coaching must NOT be in diagnosis output (pre-coaching stage)."""
        out = diagnose_mod._build_diagnose_json(diag_result, learner_input=_CLAIM)
        assert "coaching" not in out, (
            "coaching key must be ABSENT from diagnose-verify output; "
            f"found coaching={out.get('coaching')!r}"
        )

    def test_report_key_absent(self, diag_result):
        """report must NOT be in diagnosis output (no report before coaching)."""
        out = diagnose_mod._build_diagnose_json(diag_result, learner_input=_CLAIM)
        assert "report" not in out, (
            "report key must be ABSENT from diagnose-verify output; "
            f"found report={out.get('report')!r}"
        )

    def test_schema_version_is_string(self, diag_result):
        out = diagnose_mod._build_diagnose_json(diag_result, learner_input=_CLAIM)
        assert isinstance(out["schema_version"], str)
        assert out["schema_version"]  # non-empty


# ---------------------------------------------------------------------------
# Subprocess: CLI surface (diagnose.py run as a script)
# ---------------------------------------------------------------------------

def _run_diagnose_subprocess(args: list[str], stdin_text: str | None = None) -> subprocess.CompletedProcess:
    """Run diagnose.py as a subprocess via the venv Python.

    The project root is injected via ``PYTHONPATH`` so ``import mira`` resolves
    — same approach as the project's ``pythonpath = ["."]`` pytest config.
    """
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


class TestDiagnoseScriptCLI:
    def test_script_file_exists(self):
        assert _SCRIPT.exists(), f"diagnose.py not found at {_SCRIPT}"

    def test_exits_zero_on_valid_input(self):
        result = _run_diagnose_subprocess([_CLAIM])
        assert result.returncode == 0, (
            f"diagnose.py exited with code {result.returncode}.\n"
            f"stderr: {result.stderr}"
        )

    def test_emits_valid_json_to_stdout(self):
        result = _run_diagnose_subprocess([_CLAIM])
        assert result.returncode == 0
        try:
            parsed = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            pytest.fail(f"stdout is not valid JSON: {exc}\nstdout: {result.stdout[:500]}")
        assert isinstance(parsed, dict)

    def test_coaching_absent_in_cli_output(self):
        result = _run_diagnose_subprocess([_CLAIM])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "coaching" not in data

    def test_report_absent_in_cli_output(self):
        result = _run_diagnose_subprocess([_CLAIM])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "report" not in data

    def test_overlay_status_in_cli_output(self):
        result = _run_diagnose_subprocess([_CLAIM])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "overlay_status" in data

    def test_lang_en_flag_accepted(self):
        result = _run_diagnose_subprocess([_CLAIM, "--lang", "en"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "overlay_status" in data

    def test_lang_ko_flag_accepted(self):
        ko_claim = "시험에 떨어진 것은 내가 머리가 나빠서다."
        result = _run_diagnose_subprocess([ko_claim, "--lang", "ko"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "coaching" not in data

    def test_empty_input_exits_nonzero(self):
        result = _run_diagnose_subprocess([""])
        assert result.returncode != 0, "Empty input should exit non-zero"

    def test_stdin_mode_produces_valid_json(self):
        result = _run_diagnose_subprocess(["--stdin"], stdin_text=_CLAIM)
        assert result.returncode == 0, f"stdin mode failed: {result.stderr}"
        data = json.loads(result.stdout)
        assert "coaching" not in data
        assert "report" not in data
        assert "overlay_status" in data
