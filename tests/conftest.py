"""Pytest path setup for Agent Skills.

Each skill lives in ``skills/<skill-name>/`` (kebab-case per Agent Skills
convention).  Its ``scripts/`` directory is added to ``sys.path`` so the test
suite can ``import`` the skill's Python modules directly (e.g. ``import ingest``
/ ``import render`` / ``import diagnose``), mirroring the runtime path that
applies when the skill runs its own entry point
(``python skills/<skill>/scripts/<module>.py``), where the script directory is
``sys.path[0]``.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent

for _skill_dir in (
    "mira-report",
    "mira-diagnose-verify",
    "mira-coach",
):
    _scripts = _ROOT / "skills" / _skill_dir / "scripts"
    if _scripts.exists() and str(_scripts) not in sys.path:
        sys.path.insert(0, str(_scripts))
