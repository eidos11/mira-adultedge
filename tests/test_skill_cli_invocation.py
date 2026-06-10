"""BUG-1 regression — skill CLI must run as documented WITHOUT a PYTHONPATH crutch.

Real users invoke each skill via its SKILL.md usage contract, e.g.::

    python skills/mira-diagnose-verify/scripts/diagnose.py "text"

When a script is run directly, ``sys.path[0]`` is the SCRIPT's directory
(``skills/<skill>/scripts``), NOT the project root.  This project is not
installed into site-packages (``uv`` reports "not packaged"), so ``import mira``
raises ``ModuleNotFoundError`` unless the script bootstraps the project root
onto ``sys.path`` itself.

The existing roundtrip suite (``test_skill_family_roundtrip.py``) injects the
project root into ``PYTHONPATH`` via ``_env_with_pythonpath`` — which MASKS this
bug.  These tests deliberately STRIP ``PYTHONPATH`` to reproduce the real
first-use condition every downstream user faces.

Scope: these tests assert specifically that ``import mira`` succeeds.  The
optional ``pyswip`` (prolog extra) is a SEPARATE concern — Lane 2 degrades
gracefully (exit 0, ``lane2.error`` on stderr) when it is absent — so its
presence or absence does not affect this BUG-1 regression.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).parent.parent
_DIAGNOSE = _PROJECT_ROOT / "skills" / "mira-diagnose-verify" / "scripts" / "diagnose.py"
_COACH = _PROJECT_ROOT / "skills" / "mira-coach" / "scripts" / "coach.py"
_REPORT_SCRIPTS = _PROJECT_ROOT / "skills" / "mira-report" / "scripts"

_CLAIM = "I failed because I'm not smart enough."


def _env_no_pythonpath() -> dict:
    """Real first-use condition: the user has NO PYTHONPATH crutch set."""
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    return env


def _run_no_pp(argv: list[str], stdin_text: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        argv,
        input=stdin_text,
        capture_output=True,
        text=True,
        env=_env_no_pythonpath(),
        cwd=str(_PROJECT_ROOT),
    )


def test_diagnose_runs_directly_without_pythonpath():
    """``python skills/.../diagnose.py "text"`` must work with no PYTHONPATH (BUG-1)."""
    result = _run_no_pp([sys.executable, str(_DIAGNOSE), _CLAIM])
    assert "No module named 'mira'" not in result.stderr, result.stderr
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == "0.2.2"


def test_coach_runs_directly_without_pythonpath(tmp_path):
    """``python skills/.../coach.py diag.json`` must work with no PYTHONPATH (BUG-1)."""
    diag = _run_no_pp([sys.executable, str(_DIAGNOSE), _CLAIM])
    assert diag.returncode == 0, diag.stderr
    diag_file = tmp_path / "diag.json"
    diag_file.write_text(diag.stdout, encoding="utf-8")

    result = _run_no_pp([sys.executable, str(_COACH), str(diag_file)])
    assert "No module named 'mira'" not in result.stderr, result.stderr
    assert result.returncode == 0, result.stderr
    assert "coaching" in json.loads(result.stdout)


def test_render_runs_directly_without_pythonpath(tmp_path):
    """render via the SKILL.md ``python -c`` contract must work with no PYTHONPATH.

    ``render.py`` does ``from mira.report import ...`` at module level, so merely
    importing it — even through the documented invocation that only puts the
    scripts dir on ``sys.path`` — fails without the project-root bootstrap.
    """
    diag = _run_no_pp([sys.executable, str(_DIAGNOSE), _CLAIM])
    assert diag.returncode == 0, diag.stderr
    coached = _run_no_pp([sys.executable, str(_COACH), "--stdin"], stdin_text=diag.stdout)
    assert coached.returncode == 0, coached.stderr
    coached_file = tmp_path / "coached.json"
    coached_file.write_text(coached.stdout, encoding="utf-8")

    program = (
        "import json, sys; "
        f"sys.path.insert(0, {str(_REPORT_SCRIPTS)!r}); "
        "import render; "
        f"print(render.render(json.load(open({str(coached_file)!r})), mode='html'))"
    )
    result = _run_no_pp([sys.executable, "-c", program])
    assert "No module named 'mira'" not in result.stderr, result.stderr
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip().startswith("<!DOCTYPE html>")
