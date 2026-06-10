"""i18n output guards: a report must not leak the other language.

Regression guard for the PSR "suggested action frame" reframe, which was hard-coded
in Korean and leaked into English reports (E1 finding, 2026-06-02). The reframe is
now stored as a language-neutral key and localized at render time (reframe_text).
"""

import re

from mira.pipeline import run_minimal_loop
from mira.system_a.engine.axis_task_definition import REFRAME_FRAMES, reframe_text

_HANGUL = re.compile(r"[가-힣]")


def test_reframe_text_localizes_by_language():
    assert reframe_text("coding", "en") == "be able to implement a small feature and confirm it with a test"
    assert reframe_text("coding", "ko") == "작은 기능을 구현하고 테스트로 확인할 수 있다"


def test_reframe_text_falls_back_to_english_generic():
    assert reframe_text("no_such_key", "en") == REFRAME_FRAMES["en"]["generic"]
    assert reframe_text("coding", "xx") == REFRAME_FRAMES["en"]["coding"]


def test_english_report_has_no_korean_leak():
    # A noun-goal English claim exercises the PSR "suggested action frame" path.
    result = run_minimal_loop("I want to get better at math.", claim_language="en")
    assert not _HANGUL.search(result.report)


def test_korean_report_does_not_use_english_reframe():
    result = run_minimal_loop("수학 실력을 키우고 싶다.", claim_language="ko")
    assert "be able to explain the solution steps" not in result.report
