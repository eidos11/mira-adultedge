"""Lane 1 input-side cue extraction (signal-level pattern evidence).

Draft for review — improvement priorities #1 (cue→coaching wiring) and
#2 (specificity / healthy-reasoning path).

Design intent
-------------
Lane 1 previously contained only OUTPUT-side contract checks (verdict
language, willpower blame, registry ids). This module adds a lightweight
INPUT-side rule layer: bilingual regex cues that map learner phrasing to
registry pattern ids, producing evidence_trace entries of the form
``[L1-cue] {cue_id}: "{excerpt}"``.

Consequences downstream (no semantic change elsewhere required):
  * report.py already sorts the tentative coaching pool evidence-first —
    cue-backed patterns therefore surface ahead of alphabetical noise.
  * The expert badge semantics are preserved: cue-backed candidates are
    "evidence-assisted" (🟡), NOT "verified" (✅). Lane 1 cues are signals,
    not deductive verification — calibration language is unchanged.
  * Excerpts are sanitized (blame-neutralized + gate-token-scrubbed) so a
    quoted learner phrase can never trip output invariants #1/#12.

Epistemic status: regex cues are precision-first and intentionally
conservative; recall gaps fall through to the neutral elicitation path
(class C) rather than to wrong coaching. Cross-reference:
mira/system_a/engine/axis_metacognition.py keeps its own (display-layer)
cue regexes; duplication here is deliberate to preserve the System A /
System B layering boundary.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from mira.contracts.safety_patterns import WILLPOWER_BLAME_RE
from mira.psr.psr import neutralize_blame

# ── pattern_id → vtype (registry facts; used when a cue-hit pattern is
#    injected outside the routed vtype, mirroring the Lane 2 bridge
#    injection precedent in pipeline._merge_bridge_verdict_candidates) ──
CUE_PATTERN_VTYPE: dict[str, str] = {
    "false_dilemma": "D",
    "genetic_fallacy": "D",
    "perfectionist_fallacy": "D",
    "oversimplified_cause": "A",
    "self_serving_attribution": "A",
    "willpower_blame": "A",
    "catastrophizing": "A",
    "sunk_cost": "I",
    "fluency_illusion": "I",
    "effort_heuristic": "I",
}


@dataclass(frozen=True)
class CueHit:
    pattern_id: str
    cue_id: str
    excerpt: str
    strength: int  # 2 = explicit marker, 1 = weak/inferential marker


# ── distortion cue regexes (bilingual, precision-first) ─────────────────
_FALSE_DILEMMA_RE = re.compile(
    r"(\beither\b[^.?!\n]{0,80}\bor\b"
    r"|only\s+(two|2)\s+(options?|choices?|ways?)"
    r"|no\s+other\s+(way|choice|option)"
    r"|둘\s*중\s*하나"
    r"|방법이?\s*없"
    r"|수밖에\s*없"
    r"|길은\s*[^\n]{0,12}뿐)",
    re.IGNORECASE,
)
_OVERSIMPLIFIED_STRONG_RE = re.compile(
    r"(the\s+only\s+reason|all\s+because|simply\s+because|entirely\s+because"
    r"|(전부|전적으로|순전히|오로지|단지)\s*[^\n]{0,16}(때문|탓)"
    r"|때문이다\s*[.!?]?\s*$)",
    re.IGNORECASE,
)
_OVERSIMPLIFIED_WEAK_RE = re.compile(
    r"\bbecause\b(?![^.?!\n]*\b(and|also|plus|partly|among)\b)"
    r"|때문(?![^.?!\n]*(그리고|또한?|랑|및))",
    re.IGNORECASE,
)
_SUNK_COST_RE = re.compile(
    r"(already\s+(spent|invested|put\s+in)"
    r"|come\s+this\s+far|can'?t\s+(quit|stop)\s+now"
    r"|too\s+late\s+to\s+(change|switch)"
    r"|여기까지\s*(왔|했)|이만큼\s*(했|들였|투자)"
    r"|지금\s*와서\s*(포기|그만|바꾸)"
    r"|들인\s*(시간|돈|노력)[이가]?\s*아까)",
    re.IGNORECASE,
)
_ABILITY_ATTRIBUTION_RE = re.compile(  # registry label: genetic_fallacy
    r"(not\s+smart\s+enough|just\s+not\s+(smart|good|talented|cut\s+out)"
    r"|wasn'?t\s+born\s+(for|with)|no\s+talent|too\s+(dumb|stupid)"
    r"|머리가\s*나(쁘|쁜|빠|쁠)|머리가?\s*안\s*좋|멍청|재능이\s*없|타고나[지질]\s*(못|않)"
    r"|똑똑하지\s*않|원래\s*못)",
    re.IGNORECASE,
)
_CATASTROPHIZING_RE = re.compile(
    r"(career\s+is\s+over|it'?s\s+(all\s+)?over|ruined\s+everything"
    r"|never\s+recover|인생\s*끝|끝장|망했|돌이킬\s*수\s*없)",
    re.IGNORECASE,
)
_EXTERNAL_BLAME_RE = re.compile(
    r"(not\s+my\s+fault"
    r"|because\s+of\s+(the\s+)?(teacher|professor|instructor|test|exam)"
    r"|teacher'?s\s+fault"
    r"|선생님?\s*때문|강사\s*때문|시험이\s*이상|문제가\s*잘못|환경\s*탓)",
    re.IGNORECASE,
)
# compound markers (co-occurrence cues)
_READ_RE = re.compile(
    r"(read|reread|reading|훑|읽었|읽어)", re.IGNORECASE
)
_VAGUE_UNDERSTAND_RE = re.compile(
    r"(i\s+(think|feel)\s+i\s+understand|feels?\s+familiar|seems?\s+clear"
    r"|kind\s+of\s+understand|이해한?\s*것\s*같|아는\s*것\s*같|익숙)",
    re.IGNORECASE,
)
_EFFORT_RE = re.compile(
    r"(studied\s+(hard|a\s+lot)|worked\s+hard|spent\s+hours|many\s+hours"
    r"|put\s+in\s+(a\s+lot|effort)|열심히|많이\s*공부|시간을?\s*많이)",
    re.IGNORECASE,
)
_OUTCOME_CLAIM_RE = re.compile(
    r"(so\s+i\s+(should|deserve|will)|surely|must\s+be\s+(fine|ready)"
    r"|probably\s+(fine|ready)|괜찮겠|당연히|했으니|봤으니|충분(히|할))",
    re.IGNORECASE,
)

# ── healthy-reasoning signal regexes (improvement #2) ───────────────────
# Cross-ref: axis_metacognition uses sibling regexes for the confidence
# band; these are detection-grade copies kept in System B intentionally.
_HEALTH_SIGNALS: list[tuple[str, re.Pattern[str]]] = [
    (
        "monitoring",
        re.compile(
            r"(reviewed|checked|verified|compared|got\s+feedback|made\s+an?\s+"
            r"(error\s+)?log|scheduled|점검|확인해\s*봤|복습\s*계획|피드백을?\s*받|기록했)",
            re.IGNORECASE,
        ),
    ),
    (
        "specific_gap",
        re.compile(
            r"(topics?\s+i\s+missed|weak\s+(areas?|in)|struggle\s+with"
            r"|specific\s+gap|wrong\s+answers?|오답|틀린\s*(문제|부분|주제)"
            r"|약한\s*(부분|영역)|막히는\s*부분|놓친\s*(주제|부분))",
            re.IGNORECASE,
        ),
    ),
    (
        "evidence_based",
        re.compile(
            r"(can\s+explain|i\s+applied|tested\s+myself|retrieval"
            r"|without\s+looking|설명할\s*수|적용해\s*봤|검증했|풀어\s*봤)",
            re.IGNORECASE,
        ),
    ),
]

_GATE_TOKEN_SCRUB = re.compile(
    r"(확정|판정|진단\s*결과|verdict|diagnosed|determined|proven)",
    re.IGNORECASE,
)
_EXCERPT_MAX = 36


def _sanitize_excerpt(text: str) -> str:
    """Make a learner-text excerpt safe to quote in system output.

    blame-neutralized (Invariant #12) + verdict-token-scrubbed (Invariant #1)
    + truncated. Guarantees a quoted cue can never trip output gates.
    """
    out = neutralize_blame(text)
    out = WILLPOWER_BLAME_RE.sub("…", out)  # residual partial tokens (e.g. '게을')
    out = _GATE_TOKEN_SCRUB.sub("…", out)
    out = re.sub(r"\s+", " ", out).strip()
    if len(out) > _EXCERPT_MAX:
        out = out[:_EXCERPT_MAX].rstrip() + "…"
    return out


def _hit(pattern_id: str, cue_id: str, m: re.Match[str], strength: int) -> CueHit:
    return CueHit(
        pattern_id=pattern_id,
        cue_id=cue_id,
        excerpt=_sanitize_excerpt(m.group(0)),
        strength=strength,
    )


def extract_cues(claim: str) -> list[CueHit]:
    """Scan the RAW learner claim (pre-neutralization) for distortion cues.

    Returns at most one CueHit per pattern (strongest first occurrence).
    Order of checks is irrelevant; ranking happens via evidence counts.
    """
    hits: dict[str, CueHit] = {}

    def add(pid: str, cid: str, m: re.Match[str] | None, strength: int) -> None:
        if m and (pid not in hits or hits[pid].strength < strength):
            hits[pid] = _hit(pid, cid, m, strength)

    add("false_dilemma", "binary_option_marker", _FALSE_DILEMMA_RE.search(claim), 2)
    add("sunk_cost", "past_investment_marker", _SUNK_COST_RE.search(claim), 2)
    add("genetic_fallacy", "ability_attribution_marker",
        _ABILITY_ATTRIBUTION_RE.search(claim), 2)
    # Ability attribution is, structurally, a single-cause attribution to a
    # stable trait (Weiner): it therefore also weakly cues oversimplified_cause,
    # whose coaching template ("would removing that cause solve it 100%?")
    # is the correct intervention while genetic_fallacy lacks its own template.
    add("oversimplified_cause", "trait_as_single_cause",
        _ABILITY_ATTRIBUTION_RE.search(claim), 1)
    add("catastrophizing", "irreversibility_marker",
        _CATASTROPHIZING_RE.search(claim), 2)
    add("self_serving_attribution", "external_blame_marker",
        _EXTERNAL_BLAME_RE.search(claim), 2)
    add("willpower_blame", "character_attribution_marker",
        WILLPOWER_BLAME_RE.search(claim), 2)

    m_strong = _OVERSIMPLIFIED_STRONG_RE.search(claim)
    if m_strong:
        add("oversimplified_cause", "exclusive_cause_marker", m_strong, 2)
    else:
        add("oversimplified_cause", "single_cause_attribution",
            _OVERSIMPLIFIED_WEAK_RE.search(claim), 1)

    # compound cues
    if _READ_RE.search(claim) and (m := _VAGUE_UNDERSTAND_RE.search(claim)):
        add("fluency_illusion", "familiarity_as_understanding", m, 2)
    if _EFFORT_RE.search(claim) and (m := _OUTCOME_CLAIM_RE.search(claim)):
        add("effort_heuristic", "effort_to_outcome_inference", m, 2)

    return list(hits.values())


def extract_health_signals(claim: str) -> list[str]:
    """Detect well-structured-reasoning signals (monitoring / specific gap /
    evidence-based self-assessment). Used by the class-B positive path."""
    return [name for name, rx in _HEALTH_SIGNALS if rx.search(claim)]


def evidence_lines(hit: CueHit) -> list[str]:
    """Render a CueHit as evidence_trace entries.

    Strength-2 cues contribute two lines so the existing evidence-count
    sort in report.py ranks explicit markers above weak ones without any
    change to that sort key.
    """
    line = f'[L1-cue] {hit.cue_id}: "{hit.excerpt}"'
    return [line] * hit.strength
