"""Unified safety-boundary regex patterns for report generation and critic audit.

Single source of truth for verdict language and willpower blame detection.
Used by report.py (pre-filter) and contract.py / invariants.py (formal audit).

M1 hotfix (SemVer 0.2.1): Removed false-positive triggers (determined, proven, catastrophizing)
that matched normal English in learner-quoted evidence traces.
"""

from __future__ import annotations

import re

VERDICT_LANGUAGE_RE = re.compile(
    r"(확정|판정|진단\s*결과\s*:|verdict|diagnosed|확인됨|"
    r"맞습니다|틀립니다|당신은\s+[^.?!\n]{1,80}입니다|"
    r"you\s+are\s+(?:a\s+|an\s+|the\s+|being\s+)?(?:biased|wrong|irrational|"
    r"deluded|suffering|affected|exhibiting|displaying|showing)[^.?!\n]{0,80}|"
    r"the\s+verdict\s+is)",
    re.IGNORECASE,
)

WILLPOWER_BLAME_RE = re.compile(
    r"(게으[르른를]|게을|나태|laziness|\blazy\b|willpower|"
    r"의지\s*부족|의지력\s*부족|의지가\s*부족|의지[가이]?\s*약|"
    r"노력\s*부족|노력부족|"
    r"lack\s+of\s+(effort|willpower|discipline))",
    re.IGNORECASE,
)
