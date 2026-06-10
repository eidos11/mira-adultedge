"""mira-report skill (②) — render stage: mode routing + visual HTML.

Modes (decision 2 routing table):
- expert    : reuse ``mira.report.render_report_markdown`` (decision 3, DRY md body)
- html      : render the overlay DIRECTLY into a visual, self-contained page —
              evidence→Input highlight, verdict badges, confidence gauge, lane
              badges. Not a md mirror; this is why html is a distinct mode.
- customize : minimal guidance (decision 4)

Safety: html delegates the violation / verdict-language gate to
``render_report_markdown`` (SSOT). If that returns the safe fallback, html
renders the fallback too; otherwise the verified overlay is rendered visually.

Every mode runs ``ingest()`` first, so an unsupported ``schema_version`` is
rejected before any rendering (fail-closed, decision 1).
"""

from __future__ import annotations

import html as _html
import re
import sys
from pathlib import Path

# BUG-1: when run via the SKILL.md `python -c` contract, sys.path[0] is the
# scripts dir, not the project root, so `import mira` (and `ingest`, which
# imports mira) fails — this project is not installed into site-packages.
# Bootstrap the project root onto sys.path before the imports below.
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from ingest import ingest, ingest_coaching

from mira.report import (
    _VERDICT_BADGE,
    _action_suggestion,
    _lane_source,
    render_report_markdown,
    safe_fallback_report,
    verdict_state,
    REPORT_BLOCK_SEPARATOR,
)
from mira.contracts.safety_patterns import VERDICT_LANGUAGE_RE

_TEMPLATE_PATH = (
    Path(__file__).resolve().parent.parent / "assets" / "templates" / "report.html"
)

# Diagnosis ordering: surface verified first, unverified last.
_VERDICT_ORDER = {"verified": 0, "evidence_assisted": 1, "rejected": 2, "unverified": 3}
_L_PREFIX_RE = re.compile(r"^\[L[123]\]\s*")


class UnsupportedModeError(ValueError):
    """Requested render mode is not one of html / expert / customize."""


def render(data: dict, mode: str = "html", lang: str = "en") -> str:
    """Route a diagnostic JSON to a rendered report by mode (fail-closed).

    The optional ``coaching`` field in *data* (Task 2 structured dict) is the
    single source for the coaching section in html and expert outputs when
    present.  When absent the existing overlay-based coaching path is used
    unchanged (graceful omit, no crash).

    Double-render prevention: the structured field replaces (not supplements)
    the overlay-derived ``_action_suggestion`` path in html's ``_html_coaching``
    and the inline coaching block in expert's ``render_report_markdown`` output.
    """
    overlay = ingest(data)
    claim = data.get("input", "")
    coaching = ingest_coaching(data)  # None when field absent
    if mode == "expert":
        return _render_expert(overlay, claim, lang, coaching)
    if mode == "html":
        return _render_html(overlay, claim, lang, coaching)
    if mode == "customize":
        return _customize_guidance()
    raise UnsupportedModeError(
        f"Unsupported mode {mode!r}. Supported: html, expert, customize."
    )


def _render_expert(overlay, claim: str, lang: str, coaching) -> str:
    """Expert markdown mode.

    When *coaching* (the structured field) is present it replaces the coaching
    block that ``render_report_markdown`` embeds — avoiding double-render.
    The replacement is surgical: the safe-fallback path is preserved unchanged,
    and only the single coaching block is swapped.
    """
    md = render_report_markdown(overlay, claim, lang=lang)
    if coaching is None or md == safe_fallback_report(lang):
        # No structured coaching, or safety fallback active — return as-is.
        return md
    blocks = md.split(REPORT_BLOCK_SEPARATOR)
    # Content-scan for the coaching block rather than a hardcoded index: robust
    # to render_report_markdown reordering its blocks (a positional splice would
    # silently overwrite the wrong block, e.g. PSR/Evidence, with no exception).
    coaching_idx = next(
        (i for i, b in enumerate(blocks) if b.lstrip().startswith("## Coaching")),
        None,
    )
    if coaching_idx is None:
        # Coaching block not locatable — return unchanged (no silent corruption).
        return md
    # P1-a: the structured (JSON-supplied) coaching block REPLACES the overlay-derived
    # block that render_report_markdown's verdict gate scanned — so the block we actually
    # emit never passed that gate. Re-apply the verdict gate here, mirroring report.py's
    # expert gate, so the preserved gate is not illusory for the skill output path.
    # (willpower is coaching-exempt per spec §6; verdict language is not.)
    if VERDICT_LANGUAGE_RE.search(coaching.get("block", "")):
        return safe_fallback_report(lang)
    blocks[coaching_idx] = _coaching_md_block(coaching)
    return REPORT_BLOCK_SEPARATOR.join(blocks)


def _render_html(overlay, claim: str, lang: str, coaching=None) -> str:
    # Safety gate is owned by render_report_markdown (SSOT). If it falls back,
    # render the safe message; otherwise render the overlay visually.
    md = render_report_markdown(overlay, claim, lang=lang)
    body = _md_to_html(md) if md == safe_fallback_report(lang) else _visual_body(
        overlay, claim, lang, coaching
    )
    template = _TEMPLATE_PATH.read_text(encoding="utf-8")
    return template.replace("{{LANG}}", lang).replace("{{BODY}}", body)


def _visual_body(overlay, claim: str, lang: str, coaching=None) -> str:
    return "\n".join(
        [
            _html_input(claim, overlay),
            _html_diagnosis(overlay),
            _html_psr(overlay),
            _html_evidence(overlay),
            _html_coaching(overlay, lang, coaching),
            _html_confidence(overlay),
            _html_metadata(overlay),
        ]
    )


def _evidence_fragments(overlay) -> list[str]:
    """Quotable evidence fragments: prefix-stripped, '...'-split, trimmed."""
    frags: list[str] = []
    for c in overlay.pattern_candidates:
        for e in c.evidence_trace:
            txt = _L_PREFIX_RE.sub("", str(e)).strip()
            for part in txt.split("..."):
                part = part.strip().strip(",.;").strip()
                if len(part) >= 4:
                    frags.append(part)
    return frags


def _html_input(claim: str, overlay) -> str:
    """Input quote with evidence fragments wrapped in <mark> (md cannot do this)."""
    esc = _html.escape(claim)
    # Longest-first: avoid a short fragment splitting a longer overlapping one.
    for frag in sorted(set(_evidence_fragments(overlay)), key=len, reverse=True):
        efrag = _html.escape(frag)
        if efrag in esc and f">{efrag}<" not in esc:
            esc = esc.replace(efrag, f'<mark class="evidence">{efrag}</mark>', 1)
    return (
        '<section class="report-section">\n<h2>Input</h2>\n'
        f"<blockquote>{esc}</blockquote>\n</section>"
    )


def _badge(state: str) -> str:
    return f'<span class="badge badge-{state}">{_html.escape(_VERDICT_BADGE[state])}</span>'


def _html_diagnosis(overlay) -> str:
    cands = sorted(
        overlay.pattern_candidates,
        key=lambda c: _VERDICT_ORDER.get(verdict_state(c), 9),
    )
    rows = [
        f'<li class="verdict-{verdict_state(c)}">{_badge(verdict_state(c))} '
        f'{_html.escape(c.pattern_id.replace("_", " "))}</li>'
        for c in cands
    ]
    return (
        '<section class="report-section">\n<h2>Diagnosis Summary</h2>\n'
        f'<ul class="diagnosis-list">\n{chr(10).join(rows)}\n</ul>\n</section>'
    )


def _html_psr(overlay) -> str:
    p = _html.escape(str(overlay.psr.P_appraisal))
    s = _html.escape(str(overlay.psr.S_strategy))
    r = _html.escape(str(overlay.psr.R_projection))
    return (
        '<section class="report-section">\n<h2>PSR Decomposition</h2>\n<div class="psr">\n'
        f'<div class="psr-step"><span class="psr-key">Premise</span>{p}</div>\n'
        f'<div class="psr-step"><span class="psr-key">Strategy</span>{s}</div>\n'
        f'<div class="psr-step"><span class="psr-key">Result</span>{r}</div>\n'
        "</div>\n</section>"
    )


def _html_evidence(overlay) -> str:
    items = []
    for c in overlay.pattern_candidates:
        if not c.evidence_trace:
            continue
        state = verdict_state(c)
        name = _html.escape(c.pattern_id.replace("_", " "))
        lane = _html.escape(_lane_source(c))
        quotes = "".join(
            f"<li>{_html.escape(_L_PREFIX_RE.sub('', str(e)).strip())}</li>"
            for e in c.evidence_trace
        )
        items.append(
            f'<div class="evidence-item verdict-{state}">\n'
            f'<h3>{_badge(state)} {name} <span class="lane-badge">{lane}</span></h3>\n'
            f"<ul>{quotes}</ul>\n</div>"
        )
    if not items:
        items.append("<p>No pattern candidates with evidence.</p>")
    return (
        '<section class="report-section">\n<h2>Evidence</h2>\n'
        f"{chr(10).join(items)}\n</section>"
    )


def _html_coaching(overlay, lang: str, coaching=None) -> str:
    """Render the coaching section for html.

    When *coaching* (structured dict) is provided it is the single source —
    ``_action_suggestion`` is NOT called (double-render prevention).
    When absent (None) the overlay-based path is used unchanged.

    3 cases for structured coaching (Task 6 honesty requirement):
    - supported  (pattern_id set, note=None): render ``block`` as coaching.
    - out-of-scope (pattern_id set, note set): render the ``note`` honestly.
    - no-match   (pattern_id=None, note=None): render ``block`` (no-match msg).
    """
    if coaching is not None:
        return (
            '<section class="report-section coaching">\n'
            f"{_coaching_html_block(coaching)}\n</section>"
        )
    return (
        '<section class="report-section coaching">\n'
        f"{_md_to_html(_action_suggestion(overlay, lang))}\n</section>"
    )


_COACHING_HEADING_RE = re.compile(r"^##[ \t]+Coaching[ \t]*(?:\n|$)")


def _strip_coaching_heading(block: str) -> str:
    """Strip a leading exact '## Coaching' heading line from a coaching block.

    ``_extract_coaching_from_report`` (pipeline.py) returns the last report
    section verbatim — which starts with '## Coaching\\n' because
    ``_action_suggestion`` prepends it.  ``_coaching_html_block`` and
    ``_coaching_md_block`` own the section heading; they must strip the
    pipeline-carried heading to avoid a double <h2>Coaching</h2> render.

    Precision: only an EXACT '## Coaching' heading line is stripped (the regex
    anchors to end-of-line). A future heading like '## Coaching (Advanced)' is
    NOT stripped — it is distinct content that must survive into the render.
    """
    stripped = block.lstrip()
    m = _COACHING_HEADING_RE.match(stripped)
    if m:
        # Remove the heading line and any immediately following blank lines.
        return stripped[m.end():].lstrip("\n").lstrip()
    return block


def _coaching_html_block(coaching: dict) -> str:
    """Convert a structured coaching dict to an HTML snippet.

    Handles all 3 cases honestly:
    - out-of-scope (note set): note text is shown, block is also rendered so
      learners still see the available text (not silently hidden).
    - supported / no-match (note=None): block is rendered directly.
    """
    note = coaching.get("note")
    block = _strip_coaching_heading(coaching.get("block", ""))
    if note:
        # out-of-scope: show the note prominently so it is not hidden,
        # then render whatever block text exists below it.
        note_html = f'<p class="coaching-note"><em>{_html.escape(note)}</em></p>'
        return f"<h2>Coaching</h2>\n{note_html}\n{_md_to_html(block)}" if block else f"<h2>Coaching</h2>\n{note_html}"
    return f"<h2>Coaching</h2>\n{_md_to_html(block)}" if block else "<h2>Coaching</h2>"


def _coaching_md_block(coaching: dict) -> str:
    """Convert a structured coaching dict to a Markdown coaching section.

    Used by ``_render_expert`` to replace the overlay-derived coaching block.
    Handles all 3 cases honestly (parallel to ``_coaching_html_block``).
    """
    note = coaching.get("note")
    block = _strip_coaching_heading(coaching.get("block", ""))
    if note:
        # out-of-scope: note is shown first so it is visible, then block.
        parts = ["## Coaching", "", f"*{note}*"]
        if block:
            parts += ["", block]
        return "\n".join(parts)
    return f"## Coaching\n\n{block}" if block else "## Coaching"


def _html_confidence(overlay) -> str:
    total = len(overlay.pattern_candidates)
    verified = sum(1 for c in overlay.pattern_candidates if c.lane2_status == "pass")
    pct = int(round(100 * verified / total)) if total else 0
    return (
        '<section class="report-section">\n<h2>Confidence &amp; Limits</h2>\n'
        f'<div class="gauge" role="img" aria-label="{verified} of {total} Prolog-verified">\n'
        f'<div class="gauge-fill" style="width: {pct}%;"></div>\n</div>\n'
        f"<p>{verified} / {total} patterns Prolog-verified. This is an AI-assisted "
        "tool; final judgment rests with the learner.</p>\n</section>"
    )


def _html_metadata(overlay) -> str:
    return (
        '<section class="report-section metadata">\n<h2>Metadata</h2>\n<ul>\n'
        f"<li>overlay_status: {_html.escape(str(overlay.overlay_status))}</li>\n"
        f"<li>route_vtype: {_html.escape(str(overlay.route_vtype))}</li>\n"
        "</ul>\n</section>"
    )


def _customize_guidance() -> str:
    return (
        "To customize the HTML report, copy this skill's "
        "assets/templates/report.html into your project and edit it. The render "
        "stage substitutes {{BODY}} with the report body and {{LANG}} with the "
        "output language. See references/customize.md for the full guide."
    )


_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")


def _inline(text: str) -> str:
    """Escape HTML, then apply ``**bold**`` → ``<strong>``."""
    return _BOLD_RE.sub(r"<strong>\1</strong>", _html.escape(text))


def _md_to_html(md: str) -> str:
    """Convert the coaching/fallback Markdown subset to HTML (dependency-free).

    Used for coaching text (and the safe fallback), which ``mira.report``
    produces as Markdown — not a general Markdown parser.
    """
    out: list[str] = []
    in_list = False

    def _close_list() -> None:
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    for raw in md.split("\n"):
        line = raw.rstrip()
        if line.startswith("## "):
            _close_list()
            out.append(f"<h2>{_inline(line[3:])}</h2>")
        elif line.startswith("### "):
            _close_list()
            out.append(f"<h3>{_inline(line[4:])}</h3>")
        elif line.startswith("- "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{_inline(line[2:])}</li>")
        elif line.startswith("> "):
            _close_list()
            out.append(f"<blockquote>{_inline(line[2:])}</blockquote>")
        elif line == "---":
            _close_list()
            out.append("<hr>")
        elif not line:
            _close_list()
        else:
            _close_list()
            out.append(f"<p>{_inline(line)}</p>")

    _close_list()
    return "\n".join(out)
