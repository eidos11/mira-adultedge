"""Unit tests for tools/stats.py — single-source stats injection/verification.

Spec: stats-injection design v2 §7.

Pure logic (junit parse, pattern read, floor, marker inject/check) is tested with
synthetic fixtures. The real pytest run (`compute_tests`) is exercised through an
injected fake runner so this suite stays fast and does not recurse into itself.
"""

import sys
from pathlib import Path

import pytest

# tools/ is a top-level sibling of tests/; make `stats` importable without packaging.
_TOOLS = Path(__file__).resolve().parents[1] / "tools"
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

import stats  # noqa: E402


# --------------------------------------------------------------------------- #
# compute — junit parsing (structured output; reject non-clean runs)
# --------------------------------------------------------------------------- #

def test_parse_junit_all_passed():
    xml = (
        '<testsuites><testsuite name="pytest" errors="0" failures="0" '
        'skipped="0" tests="329"></testsuite></testsuites>'
    )
    r = stats._parse_junit_xml(xml)
    assert r["tests"] == 329
    assert r["passed"] == 329
    assert r["skipped"] == 0


def test_parse_junit_with_skips():
    # SWI-Prolog absent: the 17 Prolog tests skip -> 312 passed.
    xml = '<testsuite errors="0" failures="0" skipped="17" tests="329"></testsuite>'
    r = stats._parse_junit_xml(xml)
    assert r["passed"] == 312
    assert r["skipped"] == 17


def test_parse_junit_counts_failures_and_errors():
    xml = '<testsuite errors="1" failures="2" skipped="0" tests="10"></testsuite>'
    r = stats._parse_junit_xml(xml)
    assert r["failures"] == 2
    assert r["errors"] == 1
    assert r["passed"] == 7


def test_parse_junit_malformed_raises():
    with pytest.raises(ValueError):
        stats._parse_junit_xml("this is not xml <<<")


def test_compute_tests_rejects_nonzero_exit():
    def fake_runner(repo_root, junit_path):
        Path(junit_path).write_text(
            '<testsuite errors="0" failures="1" skipped="0" tests="5"></testsuite>'
        )
        return 1  # non-zero -> must refuse to report a partial count

    with pytest.raises(RuntimeError):
        stats.compute_tests(Path("."), runner=fake_runner)


def test_compute_tests_rejects_failures_even_on_zero_exit():
    def fake_runner(repo_root, junit_path):
        Path(junit_path).write_text(
            '<testsuite errors="0" failures="3" skipped="0" tests="50"></testsuite>'
        )
        return 0

    with pytest.raises(RuntimeError):
        stats.compute_tests(Path("."), runner=fake_runner)


def test_compute_tests_returns_passed_on_clean_run():
    def fake_runner(repo_root, junit_path):
        Path(junit_path).write_text(
            '<testsuite errors="0" failures="0" skipped="0" tests="329"></testsuite>'
        )
        return 0

    assert stats.compute_tests(Path("."), runner=fake_runner) == 329


# --------------------------------------------------------------------------- #
# compute — pattern count from registry cardinality field (decision A)
# --------------------------------------------------------------------------- #

def test_compute_patterns_reads_cardinality_field(tmp_path):
    reg = tmp_path / "pattern_registry.yaml"
    reg.write_text(
        "cardinality:\n"
        "  diagnostic_core: 19\n"
        "  diagnostic_extension: 2\n"
        "  diagnostic_total: 21\n"
    )
    assert stats.compute_patterns(reg) == 21


def test_compute_patterns_ignores_entry_count(tmp_path):
    # The canonical field wins even when there are 22 entry-like rows.
    reg = tmp_path / "pattern_registry.yaml"
    reg.write_text(
        "cardinality:\n  diagnostic_total: 21\n"
        "patterns:\n  - id: a\n  - id: b\n  - id: c\n"
    )
    assert stats.compute_patterns(reg) == 21


def test_compute_patterns_missing_field_raises(tmp_path):
    reg = tmp_path / "pattern_registry.yaml"
    reg.write_text("patterns:\n  - id: a\n")
    with pytest.raises(ValueError):
        stats.compute_patterns(reg)


def test_compute_patterns_rejects_nonpositive(tmp_path):
    reg = tmp_path / "pattern_registry.yaml"
    reg.write_text("cardinality:\n  diagnostic_total: 0\n")
    with pytest.raises(ValueError):
        stats.compute_patterns(reg)


# --------------------------------------------------------------------------- #
# floor — monotonic, min_floor protects against public regression (decision B)
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize(
    "n,expected",
    [
        (0, 300), (49, 300), (299, 300), (329, 300),
        (349, 300), (350, 300), (351, 300), (399, 300),
        (400, 400), (450, 400), (250, 300),
    ],
)
def test_floor_boundaries(n, expected):
    assert stats.floor(n, min_floor=300) == expected


def test_floor_never_drops_below_committed_min():
    # Once 400+ is advertised (min_floor bumped), a temporary dip keeps the floor.
    assert stats.floor(329, min_floor=400) == 400


def test_render_value_floor_and_exact():
    assert stats.render_value(329, "floor", min_floor=300) == "300+"
    assert stats.render_value(329, "exact", min_floor=300) == "329"
    assert stats.render_value(21, "exact", min_floor=300) == "21"


# --------------------------------------------------------------------------- #
# inject — html marker substitution, idempotent, fails closed on bad markers
# --------------------------------------------------------------------------- #

def test_inject_replaces_marker_content():
    text = "Tests: <!--stats:tests-->999+<!--/stats:tests--> passing"
    out = stats.inject_marker(text, "tests", "300+")
    assert out == "Tests: <!--stats:tests-->300+<!--/stats:tests--> passing"


def test_inject_is_idempotent():
    text = "P: <!--stats:patterns-->21<!--/stats:patterns-->"
    once = stats.inject_marker(text, "patterns", "21")
    twice = stats.inject_marker(once, "patterns", "21")
    assert once == twice == text


def test_inject_missing_marker_raises():
    with pytest.raises(stats.MarkerError):
        stats.inject_marker("no marker here", "tests", "300+")


def test_inject_duplicate_marker_raises():
    text = "<!--stats:t-->1<!--/stats:t--> <!--stats:t-->2<!--/stats:t-->"
    with pytest.raises(stats.MarkerError):
        stats.inject_marker(text, "t", "9")


def test_inject_unclosed_marker_raises():
    with pytest.raises(stats.MarkerError):
        stats.inject_marker("<!--stats:t-->1", "t", "9")


# --------------------------------------------------------------------------- #
# atomic write — preserves exact bytes / trailing newline
# --------------------------------------------------------------------------- #

def test_write_text_atomic_roundtrip(tmp_path):
    f = tmp_path / "doc.md"
    f.write_text("hello\n", encoding="utf-8")
    stats.write_text_atomic(f, "world\nline2\n")
    assert f.read_text(encoding="utf-8") == "world\nline2\n"


def test_write_text_atomic_preserves_crlf(tmp_path):
    f = tmp_path / "doc.md"
    stats.write_text_atomic(f, "a\r\nb\r\n")
    assert f.read_bytes() == b"a\r\nb\r\n"


# --------------------------------------------------------------------------- #
# de-number guard — bare exact counts outside markers are violations
# --------------------------------------------------------------------------- #

def test_denumber_guard_flags_bare_count():
    assert stats.find_stray_counts("run the 329 tests now")


def test_denumber_guard_allows_floor_notation():
    assert not stats.find_stray_counts("over 300+ tests pass")


def test_denumber_guard_ignores_marker_content():
    text = "<!--stats:tests-->329<!--/stats:tests--> tests"
    assert not stats.find_stray_counts(text)


def test_denumber_guard_not_fooled_by_mismatched_marker_ids():
    # open 'foo' / close 'bar' is not a valid span; the count between them must
    # stay visible to the guard rather than being silently stripped (HIGH-1).
    text = "<!--stats:foo-->329 tests<!--/stats:bar-->"
    assert stats.find_stray_counts(text)


# --------------------------------------------------------------------------- #
# pattern stray guard — catches a stale total (22) without false-positives
# --------------------------------------------------------------------------- #

def test_stray_patterns_flags_stale_total():
    assert stats.find_stray_pattern_counts("a 22-pattern registry", 21)
    assert stats.find_stray_pattern_counts("the 22-pattern taxonomy", 21)
    assert stats.find_stray_pattern_counts("2 of 22 verified", 21)
    assert stats.find_stray_pattern_counts("2 / 22 deductively verified", 21)


def test_stray_patterns_allows_canonical():
    assert not stats.find_stray_pattern_counts("a 21-pattern registry", 21)
    assert not stats.find_stray_pattern_counts("2 of 21 patterns verified", 21)


def test_stray_patterns_ignores_legit_other_counts():
    # coaching skills, candidate patterns, and the cytoscape element id are not totals
    assert not stats.find_stray_pattern_counts("Coaching (6 patterns)", 21)
    assert not stats.find_stray_pattern_counts("across all 14 candidate patterns", 21)
    assert not stats.find_stray_pattern_counts("var cy = cy-pattern element", 21)


def test_stray_patterns_allows_lower_lineage_label():
    # "17-pattern" is the registry historical_label (lineage), not an overclaim.
    assert not stats.find_stray_pattern_counts("PSR + 17-pattern spec", 21)
    assert not stats.find_stray_pattern_counts("17pattern evidence mapping", 21)


def test_stray_patterns_ignores_marker_content():
    text = "<!--stats:p-->22<!--/stats:p-->-pattern registry"
    assert not stats.find_stray_pattern_counts(text, 21)


# --------------------------------------------------------------------------- #
# check — unified "docs must equal single source" gate (CI)
# --------------------------------------------------------------------------- #

def _stats(tests=329, patterns=21):
    return stats.Stats(tests=tests, patterns=patterns)


def _target(file, occ, stat, render="exact", mech="html_marker"):
    return stats.Target(file=file, occurrence_id=occ, stat=stat, render=render, mechanism=mech)


def test_check_passes_when_docs_match(tmp_path):
    (tmp_path / "README.md").write_text(
        "T <!--stats:tests-->300+<!--/stats:tests--> "
        "P <!--stats:patterns-->21<!--/stats:patterns-->\n"
    )
    targets = [
        _target("README.md", "tests", "tests", render="floor"),
        _target("README.md", "patterns", "patterns", render="exact"),
    ]
    assert stats.check(tmp_path, _stats(), targets, min_floor=300) == []


def test_check_fails_on_overclaim(tmp_path):
    (tmp_path / "README.md").write_text("<!--stats:tests-->400+<!--/stats:tests-->\n")
    targets = [_target("README.md", "tests", "tests", render="floor")]
    errs = stats.check(tmp_path, _stats(tests=329), targets, min_floor=300)
    assert errs  # advertised 400+ but floor(329)=300


def test_check_fails_on_pattern_mismatch(tmp_path):
    (tmp_path / "README.md").write_text("<!--stats:patterns-->22<!--/stats:patterns-->\n")
    targets = [_target("README.md", "patterns", "patterns", render="exact")]
    errs = stats.check(tmp_path, _stats(patterns=21), targets, min_floor=300)
    assert errs  # doc says 22, single source says 21


def test_check_fails_on_denumber_regression(tmp_path):
    (tmp_path / "README.md").write_text(
        "<!--stats:tests-->300+<!--/stats:tests--> and also 329 tests leaked\n"
    )
    targets = [_target("README.md", "tests", "tests", render="floor")]
    errs = stats.check(tmp_path, _stats(), targets, min_floor=300)
    assert errs  # stray "329 tests" outside the marker


def test_check_fails_on_missing_marker(tmp_path):
    (tmp_path / "README.md").write_text("no markers at all\n")
    targets = [_target("README.md", "patterns", "patterns", render="exact")]
    errs = stats.check(tmp_path, _stats(), targets, min_floor=300)
    assert errs


def test_check_flags_stray_pattern_total(tmp_path):
    (tmp_path / "README.md").write_text(
        "registry <!--stats:patterns-->21<!--/stats:patterns--> "
        "but elsewhere 2 of 22 verified\n"
    )
    targets = [_target("README.md", "patterns", "patterns", render="exact")]
    errs = stats.check(tmp_path, _stats(patterns=21), targets, min_floor=300)
    assert errs  # marker is right (21) but a stale "2 of 22" leaked in prose


def test_check_soft_text_floor_present(tmp_path):
    (tmp_path / "llms.txt").write_text("- 300+ tests, all deterministic\n")
    targets = [_target("llms.txt", "tests", "tests", render="floor", mech="soft_text")]
    assert stats.check(tmp_path, _stats(), targets, min_floor=300) == []


def test_check_soft_text_missing_floor_fails(tmp_path):
    (tmp_path / "llms.txt").write_text("- many tests, all deterministic\n")
    targets = [_target("llms.txt", "tests", "tests", render="floor", mech="soft_text")]
    assert stats.check(tmp_path, _stats(), targets, min_floor=300)


def test_value_present_rejects_substring_overclaim():
    assert stats._value_present("over 300+ tests pass", "300+")
    assert not stats._value_present("a whopping 1300+ tests", "300+")
    assert stats._value_present("a 21-pattern registry", "21")
    assert not stats._value_present("released in 2021", "21")


def test_check_soft_text_overclaim_fails(tmp_path):
    # "1300+" contains "300+" as a substring but is an overclaim the floor check
    # must reject; the de-number guard alone misses it (HIGH-2).
    (tmp_path / "llms.txt").write_text("- 1300+ tests, all deterministic\n")
    targets = [_target("llms.txt", "tests", "tests", render="floor", mech="soft_text")]
    assert stats.check(tmp_path, _stats(), targets, min_floor=300)


# --------------------------------------------------------------------------- #
# apply — dry-run produces a diff but writes nothing; --yes writes atomically
# --------------------------------------------------------------------------- #

def test_apply_dry_run_does_not_write(tmp_path):
    f = tmp_path / "README.md"
    f.write_text("<!--stats:patterns-->22<!--/stats:patterns-->\n")
    targets = [_target("README.md", "patterns", "patterns", render="exact")]
    diffs = stats.apply_targets(tmp_path, _stats(patterns=21), targets, min_floor=300, write=False)
    assert "README.md" in diffs
    assert f.read_text(encoding="utf-8") == "<!--stats:patterns-->22<!--/stats:patterns-->\n"


def test_apply_write_updates_file_and_is_idempotent(tmp_path):
    f = tmp_path / "README.md"
    f.write_text("<!--stats:patterns-->22<!--/stats:patterns-->\n")
    targets = [_target("README.md", "patterns", "patterns", render="exact")]
    stats.apply_targets(tmp_path, _stats(patterns=21), targets, min_floor=300, write=True)
    assert f.read_text(encoding="utf-8") == "<!--stats:patterns-->21<!--/stats:patterns-->\n"
    # second pass: no further change
    diffs = stats.apply_targets(tmp_path, _stats(patterns=21), targets, min_floor=300, write=True)
    assert diffs == {}
