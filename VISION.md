# MIRA AdultEdge — Vision & Collaboration

> **What this is:** the research foundation, differentiation, roadmap, and
> collaboration path behind MIRA. For installation and usage see [README](README.md);
> for an honest component-by-component maturity breakdown see
> [README → Maturity](README.md#maturity); for a one-page overview see the
> [live dashboard](https://eidos11.github.io/mira-adultedge/).

## The problem

Adults learning hard skills (programming, data, careers) routinely misdiagnose
*why* they struggle — "I'm just bad at math," "I lack willpower," "it's this or
nothing." These are not motivational slips; they are **structured judgment
distortions** that quietly block the path to improvement.

Worse, the usual remedy — asking peers online — often **amplifies** the
distortion. In an informal internal analysis of 106 peer replies across 15
public learning-advice threads (Reddit; single-annotator labeling), replies
*reinforced* the original bias about a third of the time and *corrected* it
only about a fifth — for prediction-style fallacies, reinforcement reached
roughly 6 in 10. This is consistent with external behavioral-science
literature; rigorous measurement (multi-annotator, registered protocol) is
future work. Advice networks tend to reproduce bias, not calibrate it.

**MIRA exists to provide the calibrated, theory-grounded diagnosis that human
advice networks usually don't.**

## What makes MIRA different

1. **Original diagnostic theory (PSR).** MIRA is built on an independent theory
   of hypothetical judgment that decomposes reasoning into **Premise → Strategy →
   Result**, locating *where* a distortion enters. ("Hypothetical judgment" is a
   founder-original construct — the cognitive mechanism by which judgment forms
   on insufficient evidence, driven by intent — distinct from the term's older
   philosophical usages; parallels such as Peirce's abduction and Bayesian
   reasoning serve as reference anchors only.) The theory is researched on its
   own terms (academic write-up in progress) and is the project's core original
   contribution.

2. **Calibrated, not credulous.** Most LLM tools simply trust the model's output.
   MIRA runs a **neurosymbolic architecture**: LLM candidate extraction is
   *verified* — by Prolog formal rules where a pattern admits deductive structure,
   and by rule-based critic checks throughout. The system is designed to say
   "unverified" rather than over-claim. Calibration is the product, not a feature.
   (Here "calibration" means honest, verdict-free reporting of evidence strength —
   the colloquial sense; quantitative ML calibration (Brier/ECE) is roadmap work.)

3. **Original-theory-grounded taxonomy.** A 21-pattern judgment-bias registry
   derived from the author's judgment theory (PSR) as its primary base, with
   cognitive-science anchors (ACT-R, Kahneman dual-process) and educational
   psychology connected as secondary, reinforcing references. The three anchor
   layers sit at different levels of analysis (cognitive architecture / judgment
   heuristics / instructional design); PSR is the bridge that integrates them
   per pattern. The coaching design pairs each pattern with pattern-specific
   Socratic coaching; in v0.x, 6 of the 21 patterns have dedicated templates
   (see README Maturity).

## The bigger picture — mira-core

MIRA AdultEdge is the first embodiment of a broader thesis: **judgment
verification is infrastructure, and it is domain-independent.** Generative AI
produces fluent answers; what high-stakes domains lack is a layer that checks
the *judgment behind* an answer — its premises, inference structure, and
uncertainty — without handing verdict authority to the model itself.

We call that layer **mira-core**. This repository already contains its embryo,
organized as three core layers plus a domain layer:

| Layer | What it is | Domain-bound? |
|-------|------------|:---:|
| **Kernel — judgment verification** | PSR decomposition, pattern-registry mechanics, rule-based critic, Prolog formal rules | No |
| **Pipeline & bridge** | diagnose → verify → coach orchestration with typed A↔B contracts | No |
| **Skill execution framework** | Agent Skills skeleton (`mira-diagnose-verify` / `mira-coach` / `mira-report`) | No |
| **Domain Pack — adult learning (v1)** | the 21-pattern instantiation, coaching content, fixtures, examples | Yes |

**Why these domains — and why MIRA exists.** MIRA was built because the author
needed it. Working as an independent researcher across several human-sciences
domains, he needed a layer that could check and coach the judgment behind his
own decisions. Adult learning became **Domain Pack v1** because it carries the
deepest lineage: a learning guide the author wrote for secondary students and
published through his learning-counseling site in 2003, later reworked for
adult learners, with an English edition whose key chapters are planned for
`/research` — and ultimately re-grounded in his independent theory of
hypothetical judgment (PSR).

Further packs adapt prior projects already substantially developed in the
author's research ecosystem — **EIU** (content-receivability diagnosis:
Easiness · Interest · Utility) and **LSAi** (a logic · strategy · AI-operations
education model), with business-strategy and investment-thesis auditing as
later candidates. These projects are themselves headed for open-source release
on the same model as MIRA. Extension here means *adapting existing assets to
the kernel / Domain-Pack structure* — not imagining new markets.

Two principles govern the stack:

- **AI as interface, not judge.** LLMs and external tools contribute candidates
  and evidence; verdicts come only from verifiable rules, critic checks, and
  auditable traces.
- **Human-sciences epistemology.** Engineering-style "one right answer"
  verification fits only part of human judgment. Where a pattern admits
  deductive structure, MIRA verifies it formally; everywhere else it holds the
  human-sciences standard — best-available alternatives, explicit uncertainty,
  and feedback-driven improvement.

*Honest status:* this repo ships the adult-learning slice end-to-end (Domain
Pack v1). The kernel / Domain-Pack boundary is extracted progressively (see
Roadmap); further packs exist today as the author's pre-MIRA projects and
concept-stage contracts, not yet as shipped packs.

## Why a Research Preview (and why now)

MIRA was built **depth-first** — the theory and architecture came before the
product. That produced an unusually deep foundation (the PSR theory, a grounded
21-pattern taxonomy, a substantial corpus) but a longer road to a shippable
slice. We are now **productizing that depth**: shipping a verifiable executable
slice publicly (this repo) while the broader research foundation is added
progressively under `/research` (see *Two-tier repository* below).

Releasing early and openly is deliberate — real-world verification by many beats
private polishing, and an open, timestamped foundation gives the ideas a public
provenance record. Formal academic priority rests on the write-up in progress;
the repository supports it.

## Two-tier repository

- **Executable slice (now):** the full diagnose → detect → coach pipeline,
  <!--stats:tests-->500+<!--/stats:tests--> tests, reproducible. MIT-licensed code.
- **Research foundation (progressive, `/research`):** research write-ups behind
  the system — guide chapters, pattern derivations, methodology notes. CC BY 4.0 —
  open, with attribution. First planned landings include key chapters of the
  English adult-learning guide behind Domain Pack v1. The author's core theory
  memos (Docs 0–2) remain unpublished pending the academic write-up; `spec/`
  carries their operational form.

You can *run and verify* MIRA today, and *understand and build on* its depth as
the foundation lands.

## Roadmap

| Stage | Focus |
|-------|-------|
| **v0.x — Research Preview (now)** | Full pipeline, 21-pattern registry, 2 patterns deductively verified (Prolog), calibrated coaching |
| **M2 (~v0.3.x)** | Expand formal verification coverage, typed contracts, more diagnostic axes, expert/HTML output tooling |
| **toward v1.0 (production)** | Full RAG, end-to-end tracking, multi-host verification, expert-validated coaching quality, kernel / Domain-Pack separation (mira-core) |

"1.0" is reserved for production-grade, expert-validated quality — a deliberate
bar, not a number to rush.

## Research context & collaboration

MIRA is developed by an **independent researcher** advancing, in parallel, both
the agent and the underlying theory of metacognition and reasoning (academic
publication in progress). The project runs on a deliberately small footprint.
MIRA is open because the author uses it on his own projects — and because
judgment tooling improves faster through many experts' and users' experience
than through any single researcher's effort.

**Open to:** research collaboration, advisory engagements, integration
partnerships, and research-role or sponsorship arrangements that let the work
continue at focus. Domain experts (cognitive science, education, coaching) are
especially welcome — the pattern registry and coaching content are designed for
expert contribution (see README → Contributing). The aim is modest and concrete
— sustaining a focused research effort, not scaling a company.

**Reach out:** open an issue or discussion on this repository, or email
**eidos11@naver.com**. Author profile:
[mnemo.notion.site/global-profile](https://mnemo.notion.site/global-profile).

## Deployment paths (B2B2C)

MIRA is built for **experts and developers** to deploy to **learners** —
*learner-facing quality, held to an expert evaluation standard.*

- **Business (B):** edtech, coaching, HR / L&D, and assessment platforms needing
  defensible, theory-grounded judgment diagnosis.
- **Developer / expert (2nd B):** integrators who customize MIRA's patterns,
  coaching, and output (skills, templates) for their own domain.
- **Learner (C):** receives calibrated, actionable, non-judgmental coaching.

---

*MIRA AdultEdge is a research preview. See [README](README.md) for current
capability and honest limitations.*
