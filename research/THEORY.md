# MIRA-core: Provisional Interpretive Judgment — Theory-to-System Specification

**Version**: 0.5 (public edition)
**Date**: 2026-07-13
**Author**: Mnemo (original theory and all foundational claims)
**AI-assisted preparation**: assembly, derivation explication, and drafting were carried out with the assistance of Claude (Anthropic). All theoretical claims, design decisions, and their validation are the author's; the AI tool holds no authorship and bears no responsibility for the content.
**Internal lineage terms**: 가설적 판단 (Hypothetical Judgment) → Provisional Interpretive Judgment; MIRA AdultEdge is the first domain instantiation of MIRA-core.

This document is the *integrator*: it states the theory and the system contract in one place, while detailed normative schemas live in companion specs — `axis2-spec.md` (Axis 2 detail, published alongside) and, in future, `axis1-spec.md` / `axis3-spec.md`. The binding state of every source corpus this document references is tracked in an internal coverage index that this document renders from; see §0.3.

---

## §0. Document Status, Method, and Governance

### 0.1 Three-layer publication architecture

- **L0 — Private theory** (Docs 0–2, founder's notebooks; separate book project): not published here. This document cites L0 only at the level of operational skeletons.
- **L1 — Public theory-to-system layer** (this document + axis specs): falsifiable, operational, academically positioned claims only.
- **L2 — Specification and code** (`spec/`, `mira/`): enforceable contracts and implementations.

L0→L1 transformation follows the method already demonstrated in `axis2-spec` v1→v4 and `sup-01`: founder-intent capture → academic parallel mapping → caution layers (epistemic/practical separation, selective applicability, individual protection) → systematized form, with full changelog and decision log.

**Method safeguard**: parallel-mapping sessions must include an adversarial pass — for each cited academic parallel, the strongest *disanalogy* is sought and recorded, not only the analogy. Analogy-only mapping is structurally biased toward flattery.

### 0.2 Revision governance

This specification is itself a *provisional interpretive judgment* in the sense it defines, and is governed accordingly: proposals are made as issues/PRs, evaluated against the falsifiable commitments in §11, and resolved in a public decision log (continuing the practice of `axis2-spec` §10). The founder's framework is the design source; documented empirical conflict triggers review rather than dismissal.

### 0.3 Corpus governance and the Reference Principle

MIRA's authored corpus is large (~28,000 lines across 11+ documents spanning theory, cognitive-science corpora, formal-logic corpora, and a CMP execution-overlay design). This richness is a durable asset and a recurring hazard: in the MVP build, the corpus outran implementation, scattered effort, and became hard to manage even for its author and for coding agents. Two governance commitments address this.

**Binding-state ledger.** Every corpus document has a tracked binding state: **bound** (live-loaded/enforced by code), **distilled** (compressed into a shipped artifact; source not loaded), **taxonomy_bound** (only its IDs reached code, not its mechanism content), or **dormant** (zero code reference). The verified reality is that the corpus is *distilled, not unused*: it reaches running code through a thin surface (the 21-pattern taxonomy in `pattern_registry.yaml`; per-pattern ACT-R/Kahneman/EDU distillates in `theory_templates.yaml`, live-loaded for 6 patterns), while most depth and all formal-logic/CMP material remain dormant. An internal coverage map is the single source of truth; this document and the axis specs are renderings and consumers of it.

**The Reference Principle (adopted from the CMP Foundations document as project-wide compilation discipline).** Theoretical sources are referenced by their *simple intention*, not their full *apparatus*. The three layers — reference, implementation, delivery — are kept asymmetric: reference is to the intention; implementation imports the minimum mechanism that carries the intention; delivery to the user is in language the user can act on, never the technical vocabulary of the implementation. Collapsing these layers (most commonly, delivering judgments in implementation jargon, or expanding implementation to match a cited reference's full apparatus) is the failure this principle guards against. Consequently, any corpus→code compilation imports only what carries the intention and rejects apparatus that does not — and partial technical correctness at the implementation layer is compatible with whole-project failure if the layers are not kept distinct.

Several corpus clusters that this document references only in passing are not yet public: the formal-logic corpora (FAL/FML/MOD), the four-tradition reasoning-philosophy corpora (ARI/MIL/WHE/PEI — Aristotle, Mill, Whewell, Peirce), the Bayesian-formalization corpus (BAY), the cognitive-science distillation sources (ACT/KAH/EDU), and three CMP execution-overlay design documents. All are dormant in the binding-state sense above — authored, but not yet loaded by code or released — and are the project's first-priority publication candidates once the mechanism-compilation work of §7.3 catches up with them. Separately, the founder is developing a fuller, more general theory of causal reasoning and of error — referred to here as *track D* — as an independent book project; a companion note on causation and reasoning is one product of that project. This document cites track D only as a *positioning anchor* (§5.0, §6.1, §10): the operational content MIRA actually carries is restated here in its own terms, never imported wholesale. The founder's private notebooks (Docs 0–2) and the sup-01 ethics supplement are further upstream sources this document draws on but does not publish.

---

## §1. Object and Scope

### 1.0 Purpose and the dual-use condition

MIRA-core exists to *identify and mitigate* distortion in consequential judgment. This purpose is the document's most basic commitment — prior to, and governing, every operational non-goal below.

A theory of distortion is, by its nature, dual-use: the same analysis that exposes how judgment is manipulated can in principle inform manipulation — as a system of law, built for justice and order, can become an instrument for those who profit from injustice. This condition is not a defect to be engineered away; it is an inescapable property of any powerful account of how judgment works (one cannot mint a coin's face without its reverse). This is the learning-domain instance of a more general condition in the parent theory of error: the very same cognitive structure that supports careful reasoning can, in the same stroke, run in a deceptive mode, so that any account of how error works can itself be turned into an instrument of error. MIRA-core therefore does **not** claim to *prevent* misuse. It declares, instead, that misuse runs *against the theory's and its originator's purpose*: the theory is for detection and protection, and any use that constructs or amplifies distortion is contrary to its reason for being. The operational commitments that follow (§1.2) are the *implementation* of this stance, not its foundation.

### 1.1 What MIRA-core audits

MIRA-core audits **consequential provisional interpretive judgments**: judgments formed under uncertainty, on incomplete evidence, under motivational pressure, where the judge bears the consequences. Examples: a learner's self-assessment ("I understand this"), a decision-maker's causal explanation ("we failed because X"), a target's assessment of an offer ("this opportunity is real").

MIRA-core audits the **structure** of such judgments — where and how distortion enters the Premise–Strategy–Result chain — not their ultimate truth. It returns calibrated, evidence-cited, non-directive guidance.

### 1.2 Non-goals (binding)

1. **Not truth adjudication**: MIRA does not rule on contested empirical, political, or religious claims. Extreme-latitude domains appear in this theory as *illustrations of mechanism* (§7 of axis2-spec), never as adjudication targets.
2. **Not personality or character assessment** (Invariant #10, enforced in code).
3. **Not clinical diagnosis or treatment.** Distress signals are out of diagnostic scope and route to scope-disclosure + referral (roadmap).
4. **Not persuasion or compliance tooling.** The theory describes deception mechanics (concealment/alteration, P-manipulation, S-monopoly, R-inflation); the system is committed to **detection and protection use only**. Implementations must not expose deception-construction affordances. (This non-goal implements the dual-use stance of §1.0.)
5. **Not a decision substitute.** Final judgment rests with the person (enforced in report language).

---

## §2. The Three-Axis Model

```
Axis 1 (Cognitive Engine)      Axis 2 (Judgment Formation)     Axis 3 (Social Conditions)
Sensation→Memory→Imagination   Appraisal→Strategy→Projection   Context that amplifies distortion
─────────────────────────────────────────────────────────────────────────────────────────
substrate (supplies evidence)  core mechanism (PSR)            external pressures & incentives
```

### 2.1 Axis 1 — The substrate engine, operationalized as evidence classes

*(This subsection operationalizes the five propositions of the founder's Axis 1 memo (Doc 2) as a **provisional skeleton**. Doc 2 states foundational principles but is deliberately compact and slated for substantial development — interrelated with, and to be augmented alongside, the track-D causation/reasoning research. The three evidence classes below are a stable diagnostic scaffold designed to **absorb** that later depth, not a finished axis-1 theory. Full axis1-spec is future work pending Doc 2 augmentation.)*

The substrate chain — sensation preserved as memory, memory supplied to imagination, imagination functioning as simulation of reality, emotion as the first-pass interpretive reaction to both direct and simulated experience, reason as the refinement of imagination grounded in sensation and memory — yields, for diagnostic purposes, **three evidence classes feeding the P-stage**:

| Evidence class | Source | Typical form | Reliability profile |
|---|---|---|---|
| **E-direct** | current sensation / episodic experience | "I just failed this practice test" | high for what it covers; narrow |
| **E-stored** | memory of outcomes, records, logs | "my last three attempts scored X" | high when consulted; often *not* consulted |
| **E-simulated** | imagination as scenario simulation | "if I continue, I will surely fail" | indispensable for planning; unbounded and emotion-loaded |

Emotion intervenes at two points (direct experience and simulated experience), consistent with the dual intervention points in axis2-spec §1.3.

**Diagnostic payoff** — characteristic distortions are *evidence-class confusions*:
- Access fluency of E-stored (familiarity) misread as competence evidence → fluency illusion, recognition–retrieval confusion.
- E-simulated treated with E-direct confidence → catastrophizing; optimism family.
- E-stored not consulted at all → hasty generalization from a single E-direct episode.
- Effort signals (E-direct) substituted for outcome evidence → effort heuristic.

**Augmentation hook**: as Doc 2 is augmented (with track D, with which it is interrelated), the reliability profiles and the two emotion-intervention points here are the expected points of refinement.

### 2.2 Axis 2 — Judgment formation and distortion

The core mechanism. Summary: judgments form as a P→S→R chain under interpretive latitude and motivational pressure; the chain cycles, and the cycle either self-corrects or self-reinforces. Normative detail: axis2-spec v4 §§1–5 (companion document).

### 2.3 Axis 3 — Social conditions of distortion (sanitized operational layer)

Axis 3 supplies the *conditions* under which Axis 2 distortion is induced, amplified, or exploited. The operational mechanisms admitted to L1:

1. **Induced complexity and ambiguity.** Deception's environmental strategy is to render situations complex, ambiguous, and uncertain so that problems cannot be located or pursued. Diagnostic consequence: rising ambient complexity *raises effective latitude* (§4), which lowers the reliability of unaided judgment.
2. **Concealment / alteration as the two deception primitives.** Concealment (omission; "no evidence = perfect deception") is fundamental; alteration (transformation-based: fabrication, manipulation, interpretive distortion) is used where exposure is unavoidable. These map to detectable signatures: absent evidential basis (P), interpretive overreach (P/S), narrative inconsistency (S/R).
3. **Authority and exclusivity claims.** S-monopoly ("only through this channel") is the central social distortion lever; it is also among the most mechanizable detection targets (§8, coverage map).
4. **Group epistemics.** Collective judgment is reliable for simple, clear matters and degrades — sometimes below individual judgment — under deception, complexity, and ambiguity; confidence may rise as accuracy falls. Diagnostic consequence: social proof is treated as *latitude-dependent* evidence, not as evidence per se.
5. **Incentive structures around persistence and optimism.** Social evaluation/reward systems make sunk-cost weighting and optimism individually costly but socially functional (dual-level framing, sup-01). Diagnostic consequence: these patterns are coached as *modern-context misfires of adaptive mechanisms*, never as personal defects — this grounds the empathic, structural-reattribution coaching stance.

On the concealment/alteration mapping in item 2: the parent error theory treats the correspondence between these two primitives and their detectable signatures as a hypothesis, not a settled result — the underlying cognitive-layer acts and the reasoning-layer failure sites relate many-to-many, with alteration most closely associated with interpretive distortion. MIRA carries the mapping at that hypothesis status, not as an established finding.

**Exclusions from L1** (retained in L0 only): human typologies, political examples, normative claims about power. These are theory-internal materials unsuited to a learner-facing system.

---

## §3. The PSR Formal Schema

### 3.1 Canonical definition

The founder's original two-stage structure (Stage 1: situation interpretation; Stage 2: consequence derivation) is formalized as three stages; Strategy straddles both — interpretation constrains the strategy space, and strategy determines which outcomes can be projected.

- **P — Premise / Appraisal**: "My situation is such-and-such." Variables: `interpretive_latitude` (low|medium|high|extreme), `evidential_basis` (strong|moderate|weak|absent), `emotional_load` (fear|desire|neutral).
- **S — Strategy / Response policy**: "Therefore I should do such-and-such." Variables: `derivation_rigor` (formal|semi-formal|informal|arbitrary), `strategy_exclusivity` (open|claimed_exclusive), `means_end_validity`.
- **R — Result projection**: "Then I will achieve X / suffer Y." Variables: `consequence_magnitude` (proportionate|exaggerated|catastrophized), `alternative_acknowledged`, `perceived_remedy_efficacy`, `verifiability`.
- **Cycle**: experience either revises the appraisal (healthy cycle) or is filtered to reinforce it (motivated distortion loop). Full schemas: axis2-spec v4 §2.

**Terminology reconciliation (binding)**: early drafts used Problem/Solution/Result; the canonical terms are Premise–Appraisal / Strategy / Result-Projection; code uses `P_appraisal / S_strategy / R_projection`. These terms are canonical; the acronym PSR is invariant across readings.

The parent theory frames P, S, and R as three *facets* of a single judgment event rather than discrete stages a judgment passes through in strict sequence — distortion can enter at any facet, and the P→S→R order used throughout this document is an expository convenience, not a claim about temporal order. This is a difference in how the three are described, not a structural change to MIRA: the code contract keeps the three as separate fields (`P_appraisal / S_strategy / R_projection`) regardless.

### 3.2 Worked example A — learning self-assessment (first domain)

| Stage | Content | Variables |
|---|---|---|
| P | "I failed because I'm just not smart enough" | latitude: extreme (dispositional); evidential_basis: absent; emotional_load: fear |
| S | (implicit) "so there is nothing to change in how I work" | derivation_rigor: informal; exclusivity: — |
| R | "future attempts will fail the same way" | magnitude: catastrophized; alternatives: suppressed; verifiability: unfalsifiable |

Detected coordinates: ability attribution (P), oversimplified cause (R); coaching = structural reattribution + multi-factor inquiry.

### 3.3 Worked example B — judgment protection (candidate second domain)

| Stage | Content | Variables |
|---|---|---|
| P | "This insider's market reading is true" | latitude: high; evidential_basis: absent (unverifiable claims); emotional_load: desire |
| S | "Funds must move through this designated channel only" | exclusivity: **claimed_exclusive**; rigor: arbitrary |
| R | "Guaranteed 30% monthly — or miss the chance of a lifetime" | magnitude: exaggerated; alternatives: suppressed; remedy_efficacy: unexamined |

The deception decomposition (P-manipulation, S-monopoly, R-inflation) is identical machinery to example A at different parameter values — demonstrating domain-independence of the core.

### 3.4 Probability-tradition assignment (formal layer)

In the proposed (dormant) formal layer, the three PSR stages *would* draw their normative probability standard from different traditions, by fitness rather than by unification: the **P-stage** from evidence-first epistemic probability (is the learner's confidence warranted by evidence?), the **S-stage** from subjective expected utility (is the choice consistent with the learner's own stated preferences plus evidence?), and the **causal/A-route** from interventional probability (is the learner's causal model consistent with the actual structure?). The diagnostic engine does not require these to be philosophically unified. Instead, a **divergence between the learner's choice-implied subjective probability and the evidence-based posterior is *proposed as* the distortion signal** — the formal restatement of miscalibration. (Source apparatus: the BAY corpus, dormant and not loaded here.)

This assignment originates in the project's own Bayesian-formalization design work (the dormant BAY corpus), not in the separately developing track D book on causal reasoning — the two should not be conflated as though track D had already settled this question.

---

## §4. Interpretive Latitude

Distortion operates where epistemic underdetermination is high. Four bands (low / medium / high / extreme) with **proportional verification rigor**: factual check → structured test → pattern detection + calibration check → metacognitive intervention. Normative table: axis2-spec v4 §3.

**Measurement commitment**: latitude classification must achieve inter-rater agreement κ ≥ [0.6 — placeholder, founder sets] between two human raters (or human + AI rater) on a public sample before the classifier ships; failure triggers spectrum redesign (§11, F2).

---

## §5. Distortion Typology and Dual-Level Ethics

### 5.0 Positioning within a broader theory of error

The four-way typology below and the pattern registry of §7 are the *learning-domain instantiation* of a broader theory of judgment error the founder has developed separately (track D — a theory of causes and its "negative," an error theory). That theory sorts informal error into six families — distorted interpretation, insufficient/over-generalized evidence, causal misjudgment, premise/framing, ambiguity, and social-affective manipulation — and analyzes their dynamics across the P·S·R facets of a judgment. MIRA does **not** import this apparatus. It registers only the coordinates at which those errors *surface in adult learning*, delegating cross-domain transfer to the core/domain cut (§7.4) and carrying the fuller theory as a positioning anchor (§10), not as loaded machinery — the discipline §0.3's Reference Principle requires. The boundary worth stating plainly: naming a richer parent theory does not mean the system detects all of it. MIRA ships six coaching patterns (not a one-to-one cover of the six families); the parent theory serves as broader positioning, not a claim of *coverage* or derivation.

In that parent theory, two of the six families — distorted interpretation and insufficient/over-generalized evidence — function as evaluative axes rather than as first-order labels: every case is ultimately assessed as either a distortion of what a judgment is *about* or a failure of how its conclusion is *supported*, and a case's principal family label can in principle fall anywhere across the six. MIRA's six coaching patterns can be mapped back onto several of these families after the fact, but MIRA does not store or diagnose a principal-family label as part of its own output. One further disambiguation is worth flagging for anyone cross-referencing both documents: MIRA's Type A/B self-relation typology (§5.1) is unrelated to the parent theory's separate kind-versus-degree verdict distinction, which MIRA does not implement, and unrelated again to the formal/informal reasoning split of §6.1 — three different classifications that happen to use similar-looking labels.

### 5.1 Typology

Four types by self-relation and social structure: **A** strategic misrepresentation (dual representation maintained), **B** motivated false belief (self-deception; reality contact weakened), **C1** epistemic bubble (omission; evidence exposure often suffices), **C2** echo chamber (active discrediting; external evidence may backfire). Intervention matrix: axis2-spec v4 §§4, 6.2.

### 5.2 Dual-level ethics (from sup-01, binding on all coaching)

- **Epistemic / practical / justification separation**: recognizing a distortion's adaptive function (epistemic) never licenses leaving it uncorrected (justification leap); intervention design (practical) remains independent.
- **Individual-protection anchor**: social-evolutionary positive expectation of a mechanism never justifies individual cost.
- **Selective applicability**: adaptive-function framing applies only where universality, social-mechanism mapping, and cumulative-culture contribution can be argued; spandrel critique (unfalsifiability) is an explicit admission filter.
- **Stance consequence**: patterns are coached as *evolutionary design + modern misfire*, not personal malfunction — the theoretical ground of the structural-reattribution and no-blame invariants.

---

## §6. From PSR to D/I/A Verification

### 6.1 The expanded logic foundation

The three modes sit under the founder's causal-telos rationale (companion note *Causation and Reasoning* §1: causation as an unreachable **regulative ideal** — in the founder's sense, *intersubjective and evidence-centered*, not Kant's subject-centered Idee — under which the three modes are positioned, not co-equal). **Deductive** reasoning propagates within premises *assumed* given and is non-ampliative (adds no factual content). **Inductive** reasoning is the ampliative route from experience toward the causal telos. **Abductive** reasoning carries the *causal leap* — the discontinuous, hypothetical step induction cannot reach by accumulation alone (distinct from inference-to-best-explanation: the leap is hypothesis *generation*, not best-explanation *selection*). This is why A runs as an independent lane rather than folded into I (§7.6): abduction is *classified within the ampliative family* (the inductive route in the broad sense) yet **functionally independent** — not reduced to an inductive inference-form — because it does the causal-leap work; folding it into general inductive statistics would dissolve the discontinuity that makes causal explanation hard. (The full genealogy — Aristotle/Mill/Whewell/Peirce, the regulative-ideal vs. Kant contrast, fallibilism as the through-line — is in the companion note; this document carries only the operational consequence, and §10 lists the lineages as positioning anchors.)

A further distinction, worth making explicit: induction and abduction are both ampliative, but they differ in where the inferential leap originates and what justifies it. Induction extends and tests a distinction that is already in place; abduction proposes a new candidate distinction in the first place, under criteria such as aim, economy, and whether it can later be tested. (The abduction/inference-to-best-explanation contrast drawn above is MIRA's own operational gloss — a generation-versus-selection distinction — not a verbatim claim from the companion note.) It is also worth being precise about what the causal telos is not: it is a founder-defined regulative orientation, intersubjective and evidence-centered, not an asymptotic approximation to some already-complete inventory of causes.

Not all judgment distortions are narrow logical fallacies. Verification operates on a single expanded logic base differentiated into three modes (decision log, axis2-spec v4 §10.4): **D** deductive (argument-structured claims; Aristotelian tradition — grounded by the dormant FAL/FML/MOD corpora), **I** inductive (self-assessments and generalizations; Mill/Whewell — calibration research supplies the empirical content, WHE corpus), **A** abductive (causal explanations; Peirce — attribution research supplies the content, PEI corpus). Routing target: `claim_type × latitude`; current implementation is keyword-level (per coverage map). Note that the D-route formal-logic corpora are the assets the *critical-thinking* domain (§7.6) would activate.

#### 6.1a The mathematical layer (selective, dormant)

**Two principles govern the proposed (dormant) mathematical layer.** First, PSR is *not reduced* to a Bayesian update; it is a claim-decomposition packet *extended* with an evidence-and-update layer (P bears a prior over hypotheses; S selects a likelihood model; R is a posterior-demanding interface; across cycles, posterior becomes the next prior). Second, the layer applies *selectively by reasoning mode*: deductive (D) checks run rule-first (non-ampliative — not probabilified: at the probability-1 limit the rule-checker already carries the validity, and adding uncertainty machinery only dilutes the signal), while inductive and abductive (I/A) checks carry the Bayesian formalization (ampliative). This selectivity *converges from two distinct routes* — the causal-reasoning hierarchy above (non-ampliative → no probabilistic update) and the diagnostic-fitness rule of the source corpora (D-type errors are primarily structural, not probabilistic): convergence, not identity. The full apparatus lives in the (dormant) BAY corpus; this layer carries the operational consequence only.

**The causal (A) route and Pearl.** The A-route additionally requires the *observation/intervention distinction*: `P(outcome | observe strategy)` and `P(outcome | do(strategy))` are distinct quantities and need not be equal — a formal handle relevant to self-serving attribution and single-cause oversimplification (diagnosis additionally requires a specified graph, causal assumptions, and evidence, and is not reducible to "unblocked confounding paths"). Here Pearl's causal layer enters — read, on *one* of its two motives, as the **empiricist computational methodology** by which reasoning works *toward* the causal telos of §6.1, "the modern Bayes" in the founder's sense (this empiricist reading is one of the two motives track D finds in Pearl — see below — not his settled stance). On that reading — Pearl locates the basis of counterfactuals in Mill's induction — structural-causal models and do-calculus do **not** claim or implement causal *completeness*; they are the **computational innovation that compensates for the practical limits of the ideal-but-infeasible method** (randomized control). MIRA's roadmap adopts Pearl's observation/intervention *distinction* as a conceptual design constraint and a possible future working method — not as a realist claim about Pearl's own commitments (track D reads his corpus as carrying *both* skeptical and realist motives). The current runtime executes neither SCM/do-calculus nor any Bayesian posterior or causal-model comparison. The operational commitment is the *distinction*; the full do-calculus apparatus (identification rules, back-door/front-door criteria, counterfactuals) is **dormant** — A-route detection would begin as Bayesian model comparison over candidate causes (activation per §11 RA-5). **Crucially, this model comparison *evaluates given candidate causes; it does not generate them*. The abductive leap — the discontinuous generation of a new causal hypothesis (companion note §2) — is not captured by model comparison and is *not* reduced to inference-to-best-explanation; where candidate exhaustion is in doubt (an unconsidered cause may dominate), the system would flag candidate-incompleteness rather than ranking.** Generation stays outside the formal layer, where the founder's account places it.

Two further caveats keep this honest. First, even where the do-calculus apparatus were eventually activated, its completeness would be internal to a given problem class and would presuppose a correctly specified causal graph — identifying structure is not the same as identifying an effect, and formal completeness within a model is not the same as causal closure over reality. Second, which formal approach should govern a given case is itself context-dependent rather than fixed by one master formalism — roughly, some situations are dominated by questions of sameness and repetition and others by questions of difference and mechanism — and that choice remains open to revision; the fuller treatment of this point is in the companion track D note.

**Modal representation and the probabilistic layer (MOD ↔ BAY).** The modal-logic corpora (MOD) are not merely a D-route formal-logic asset; they supply *possible-world representation* across PSR — epistemic/doxastic status (knowledge vs. belief) at P, option topology (feasible / exclusive / reachable) at S, temporal reachability (possible EF vs. inevitable AF) at R — over which the probabilistic layer reasons. Modal representation and probabilistic/decision reasoning are a *complementary layering* (what is possible ↔ what is likely / to be chosen), not rivals. Full integration of MOD into the present three-lane architecture is a separate track; here the layering is recorded as a MIRA architectural hypothesis, not a track-D-established result.

### 6.2 Why multiple lanes: metacognition across an organismic architecture

Metacognition, in principle, is cognition that reviews and reflects on cognition itself — a higher-order check on a lower-order process. mira realizes this not as one monolithic system but as an **organismic, multi-level architecture**: like an organism resolved into organs, tissues, and cells, each part has its own boundary and function yet is bound into one internal system. Two views must both be held. *Macroscopically*, mira is one internal system, and verification is the organism auditing its own cognition. *Microscopically*, its parts are strongly independent subsystems in tight federation, and verification is one subsystem checking another across a real boundary. The internal-vs-external audit distinction lives in this duality: review is *internal* to the organism and *external* between its organs at once. (At the learner level the same principle holds one scale up: mira as a whole is external metacognitive scaffolding for the learner's own internal self-review.)

The clearest metacognitive organ is **System B** — a narrow, highly specialized validity-checker, an advanced monitor/evaluator of the judgments that **System A** (the broader-function organ) produces. System B's specialization *is* its metacognitive role: a higher-order evaluator distinct from the cognition it evaluates. Within System B, the **independent lanes** (always-on rule critic; formal verification; LLM extraction) are federated sub-organs whose *agreement* raises epistemic status and whose *independence* keeps the check from collapsing into an echo. **Lane 3** (LLM extraction) is not itself a metacognitive auditor but the *connective tissue* that bridges the gap strict separation opens — linking the formal lanes to the richness of natural-language content; it complements the separation rather than constituting an audit.

Three principles, on distinct axes, govern the federated evaluators. **Separation** (the internal/external duality above): why evaluation is held apart from the cognition evaluated. **Plurality** (Doc 0): redundant independent instances add robustness — a single channel cannot be both source and verifier, and concealment-based deception exploits single-channel judgment. **Consilience** (Whewell): agreement across evaluators of *different kinds* (rule, formal, statistical) carries stronger warrant than repeated agreement of the same kind. The architecture *emphasizes* the external-evaluator pole while remaining a hybrid (each organ also self-checks); which pole is weighted is tunable per function. Lane agreement semantics: rule+formal agreement → verified; single-lane signal → evidence-assisted; none → unverified.

---

## §7. From Theory to Registry: The Generative Principle

### 7.1 Pattern coordinates

**Generative principle**: a diagnostic pattern is a *characteristic distortion located at coordinates* — (PSR stage) × (verification type) × (latitude band) — optionally annotated with an adaptive-function classification (sup-01). The coordinates already exist in the shipped artifacts (`psr_coaching_target`, `vtype`, spec latitude tables); this section makes the principle explicit.

Back-derivation of the six implemented coaching patterns:

| Pattern | PSR | V-type | Latitude | Distortion summary |
|---|---|---|---|---|
| fluency_illusion | P | I | high | familiarity (E-stored fluency) as competence evidence |
| effort_heuristic | P | I | high | effort signal substituted for outcome evidence |
| false_dilemma | S | D | high | option space artificially narrowed |
| sunk_cost | R | I | medium | past investment as warrant for future strategy |
| oversimplified_cause | R | A | high | multi-factor outcome reduced to single cause |
| willpower_blame | R | A | extreme | dispositional attribution blocking structural paths |

Where a pattern's verification type is I or A, its coordinates would carry a **Bayesian signature** that quantifies the distortion — e.g., fluency illusion as a likelihood ratio ≈ 1 treated as ≫ 1; hasty generalization as insufficient shrinkage toward the prior; oversimplified cause as an under-marginalized `P(outcome | do(cause₁ only))`. The full per-pattern formalization is the BAY corpus (dormant); §11 RA-5 is its activation hook.

### 7.2 Two readings of pattern origin

A diagnostic pattern's coordinates can be read two ways: patterns *generated* from the coordinate space (the registry as a map of an already-defined address system), or patterns *collected* empirically from the corpus with coordinates assigned after the fact. This document adopts the compatible reading: the coordinate system is the pattern's address system, and admission of a new pattern proceeds in three steps — empirical identification, coordinate assignment, and meeting the admission criteria of §7.3 below. This reading is also the one the parent error theory supports: its family axis (§5.0) is a super-ordinate classification standing outside the coordinate grid, and MIRA's registered patterns are that grid's learning-domain map of what has been identified so far. A future axis-spec may add a principal-family tag to the admission criteria; it is not part of the current shipped schema.

### 7.3 Pattern admission criteria (registry machinery, core-tier)

A proposed pattern enters the registry only if: (1) **operationalizable** — at least one input-side cue or fixture can detect it; (2) **distinct coordinates** — no existing pattern occupies the same (PSR × V-type × manifestation) cell for the domain; (3) **coachable** — a non-directive, no-blame intervention can be written; (4) **adaptive-function reviewable** — passes sup-01 selective-applicability screening or is explicitly marked non-adaptive; (5) **fixture-expressible** — positive *and negative* (healthy-control) examples exist. Criterion 5 encodes the specificity lesson: a registry without healthy controls produces input-invariant diagnosis.

**Mechanism layer — the highest-leverage dormant asset.** Beyond coordinates, the `AE_17pattern_evidence_registry` defines for each pattern a **mechanistic triad** — `trigger_condition → distorted_production → corrective_production` — and an **EvidencePacket** — the pattern's *required evidence* and *missing-evidence signals*, with the governing rule that **low evidence yields a *candidate* pattern, not a verdict**. This layer is currently `taxonomy_bound`: the 21-pattern taxonomy reached code, but the triad and EvidencePacket did not. It is the single highest-return dormant construct, because it is not abstract theory awaiting grounding — it is an implementable routing-and-intervention specification. (Earlier prototyping work independently re-invented a crude form of it — input cues mapped to patterns, plus a "signal-backed vs neutral" distinction approximating candidate-vs-verdict — which is direct evidence that compiling the existing registry is higher-value than authoring new corpus depth.) Compilation must obey the Reference Principle (§0.3): import the triad/packet structure that carries the diagnostic intention, not the full mechanism prose.

### 7.3a Compilation discipline (corpus → code)

Given the binding-state ledger (§0.3), corpus material enters code under three rules: (a) **intention over apparatus** — import the minimum mechanism that carries the diagnostic intention; (b) **correspondence honesty** — preserve the source-verification downgrades already recorded in `AE_17pattern_evidence_registry_VERIFY_report` (e.g., ACT-R mappings are functional-analog/partial, *not* isomorphic; "AE System A/B ≠ Kahneman System 1/2"; loss aversion treated as context-sensitive per 2024–25 re-analyses); (c) **no authority substitution** — a cited master's endorsement never substitutes for a cue's discriminating power (doing so would instantiate the registry's own `appeal_to_authority` pattern; see §10).

### 7.4 Core / domain cut

| | **MIRA-core (domain-independent)** | **Domain layer (e.g., AdultEdge)** |
|---|---|---|
| Theory | 3-axis model, PSR schema + variables, latitude model, typology, D/I/A foundation | domain manifestations, domain literature grounding |
| Machinery | registry schema + admission criteria, fixture conventions, verification statuses, invariants/calibration contract, intervention matrix form | pattern *content*, coaching templates, source corpus |
| Ethics | no-verdict / no-personality / defensive-use / final-judgment-with-person | domain invariants (e.g., willpower invariant for learning) |

Cross-domain transferability of a distortion pattern is best understood through the same lens the parent theory uses for external validity in causal inference (the transport problem, following Pearl & Bareinboim): a pattern does not automatically carry over to a new domain unless the mechanism it names is actually invariant across both domains. It is worth being precise about what the F1 falsifier (§11.1) does and does not test: F1 tests only *modular portability* — how much core-classified code a port touches — not external validity in this stronger sense. Confirming that a pattern's mechanism is genuinely invariant across domains would require a separate cross-domain fixture test, not yet specified.

### 7.5 Domain Pack Authoring Contract (draft)

A domain expert turns expertise into a MIRA agent by supplying: **(i)** registry extension YAML (pattern ids, coordinates, manifestations); **(ii)** fixtures — positive cases *and healthy controls*; **(iii)** coaching templates (recognition / 3-stage Socratic inquiry / action invitation / self-monitor signal / learner-level theory message); **(iv)** context lock + primary persona; **(v)** domain safety invariants. The authoring path requires no engine code.

Licensing terms for third-party domain packs — for example, how code (MIT) and content (CC BY) licensing apply to an externally authored pack, and whether commercial packs are permitted — are not yet decided and are out of scope here.

### 7.6 Domain roadmap and lane separation

The corpus coverage map shows the planned domains activate *disjoint* dormant corpus clusters — which both validates a multi-domain roadmap and dictates that the domains stay separate:

| Domain | Status | Primary verification route | Dormant corpus it activates |
|---|---|---|---|
| **AdultEdge** (learning) | shipped MVP | I/A + some D | ACT / KAH / EDU distillates + axis2 |
| **Judgment protection** (fraud defense) | proposed pack 2 | **I/A** (likelihood-ratio + attribution) | BAY v2 (LR, CalibrationGate), Doc 1 deception anatomy, Doc 0 (concealment/plurality), WHE/PEI |
| **Critical thinking** (logic training) | proposed pack 3 | **D** (formal verification, Lane 2) | FAL / FML / MOD formal-logic corpora + CMP overlay |

**Lane-separation rationale.** Judgment protection is post-hoc detection ("is this offer deceptive?") running on I/A-route evidence reasoning; critical thinking is prior competence ("is this argument valid?") running on D-route formal verification. They do not share verification lanes. Merging them into one pack would mix I/A and D routing and collapse to lowest-common-denominator output. Kept separate, each pack precisely drains one dormant backlog: judgment protection wakes the Bayesian/attribution corpora, critical thinking wakes the formal-logic corpora (FAL alone is 4,242 lines, currently dormant). Judgment protection is the recommended next pack because it is *theory-native* — Doc 1's deception anatomy (P-manipulation / S-monopoly / R-inflation) is its direct base, and BAY v2's likelihood-ratio reasoning ("guaranteed high return" ≈ LR 1, occurring under both legitimate and fraudulent offers; "independently auditable custody" = strong LR) ports to scam-signal discrimination unmodified.

---

## §8. Verification and Calibration Contract

*(This section documents working code — the system's strongest layer — verified by inspection of the shipped repo. Counts below are code-confirmed, not estimated.)*

- **Lanes**: Lane 1 rule critic (always-on; output contract checks + input-side signal cues), Lane 2 formal verification (Prolog; **3 pattern specs — `false_dilemma`, `fluency_illusion`, `oversimplified_cause`, each with a `spec/system_b/*.yaml`; 2 with live Prolog rules** — `false_dilemma`, `oversimplified_cause`; `fluency_illusion` rule slated Phase 2+), Lane 3 LLM extraction (opt-in). Independence per §6.2.
- **Coaching coverage**: the canonical taxonomy is **21 patterns** (19 core = D6+I8+A5, + 2 extension), plus the `willpower_blame` dual-use descriptor; **6 patterns** currently have full coaching + theory-template entries (`PAT-I-06, PAT-D-02, PAT-DUAL-01, PAT-I-04, PAT-I-07, PAT-A-02`), live-loaded at runtime. The corpus reaches code through a thin **distillation surface** — `pattern_registry.yaml` (taxonomy) + `theory_templates.yaml` (per-pattern ACT-R/Kahneman/EDU distillates) — not by loading the full corpora (§0.3).
- **Epistemic statuses**: verified (✅, formal pass) / evidence-assisted (🟡, signal-backed) / unverified (○) / rejected (✗ → *silence*, no coaching emitted). Statuses are surfaced to expert consumers and govern coaching emission.
- **Invariants (enforced)**: #1 no verdict language; #6 trace completeness; #10 no personality/identity diagnosis; #12 no willpower/character blame in system text (permitted in coaching only as instructional counter-example with structural reattribution); #13 structural-diagnosis style rubric. Violation → safe-fallback report. Input-side blame neutralization precedes processing.
- **Response classes (latitude-proportional intervention, implemented)**: A — signal-backed coaching with disclosed selection basis; B — healthy-reasoning acknowledgment (process-level only; person-level praise barred as the mirror of Invariant #12); C — honest elicitation in place of unrelated coaching.
- **EvidencePacket / CalibrationGate (specified, dormant)**: BAY v2 and the 17-pattern registry specify an EvidencePacket (required + missing evidence per pattern) and a CalibrationGate that, per BAY v2, is a *guardrail, not a posterior oracle* — it checks whether confidence rests on retrieval/output/performance evidence rather than mere fluency, and blocks "accessible = known" conversions. Not yet implemented; it is the operational home of the candidate-vs-verdict rule (§7.3). Formally, the EvidencePacket separates the *stated claim* from *observed evidence* (evidence_type, strength, source_reliability), and the CalibrationGate acts on a fluency-vs-evidence mismatch by *requesting evidence* (e.g., a retrieval check) rather than by directly lowering a posterior — a low-evidence signal yields a *candidate* pattern and an evidence request, never a verdict.
- **Cycle detection — temporal stage of a gated Bayesian pipeline (theory-mandated, not yet implemented)**: A single-claim audit cannot see the distortions the theory most cares about — *chronic, normalized* ones, whose cumulative cost is largest. The founder's weak-continuous / strong-intermittent distinction supplies the **signal asymmetry** (chronic-cost > acute-cost) the verification policy operationalizes. The detection target, in the founder's own terms, is **"this appraisal has recurred N times, unrevised after feedback"** — the case in which the learner's posterior fails to move (posterior = prior) across cycles despite relevant evidence: a *motivated update-refusal* signature, distinct from mere noise. The grounding is the founder's **dynamic-accumulation learner model** (PLDPS): a variable environment that reads the learning *process itself* and **progressively updates a Bayesian belief about the learner's state across cycles**, built on self-regulated learning (forethought–performance–self-reflection) and metacognition — not on graded test items. mira tracks a *latent appraisal/calibration state* on a PSR claim, accumulated across cycles, as that model accumulates mastery/necessity across the learning process; the per-cycle escalation is realized by (BAY corpus, dormant) sequential updating. (Bayesian Knowledge Tracing is a related technique in the same family but is *not* the grounding: it presupposes a ground-truth grader that open judgment lacks.) Cycle detection is the temporal stage of a **gated Bayesian pipeline on the P-route** (BAY corpus, dormant) that the EvidencePacket and CalibrationGate also serve — EvidencePacket (sufficiency gate, §7.3); CalibrationGate (fluency-vs-evidence guardrail, not a posterior oracle); per-cycle update and cycle-persistence escalation (BAY corpus, dormant) — which share a Bayesian *commitment*, not a single update operator. This is a **core-tier requirement, not a convenience feature**; its formalization is the mathematical-formalization layer above (§6.1a), developed jointly with the companion track D note.

  Formally, the per-cycle escalation would realize a **three-zone threshold policy** (BAY corpus, dormant) over a **sequentially updated** latent calibration state (BAY corpus, dormant — each cycle's posterior becomes the next cycle's prior — the Bayes-filter *implementation aspect* of the PLDPS dynamic-accumulation meta-principle, applied here at the level of a single PSR claim's recurrence rather than at the process-integrative level PLDPS originally operates on). A first-cycle miscalibration would default to *caution*; if the same **directionally asymmetric, ego-/effort-protective** non-update persists after R-stage feedback and a second cycle begins, it would escalate to *distortion* — the operational signature of a *motivated update-refusal*, distinguished by **directionality** and **cross-cycle persistence** (subject to magnitude and decision-cost qualifiers that screen out academic-discrepancy false positives; the full four-criterion threshold lives in the same dormant corpus). The non-update is judged against evidence that — by likelihood ratio — *should* have moved the posterior; a non-diagnostic (LR ≈ 1) signal or a justified strong prior is *not* flagged. **The norm against which calibration is judged is the system's own evidence-based posterior computed from the EvidencePacket** (retrieval/output/performance evidence) — a *backend normative model* (cf. §3.4), **not a ground-truth grader**; the distortion signal is the *divergence* between the learner's choice-implied subjective probability and this backend posterior, not a verdict on the truth of the PSR claim. Because open judgment has no ground-truth grader, the tracked quantity is a latent *calibration* state, not graded mastery — consistent with PLDPS reading the learning *process* rather than scored items. This is the **temporal counterpart of the architectural metacognition of §6.2**: §6.2 specifies *how* organs cross-evaluate (spatial-architectural); §8 specifies *how* that evaluation accumulates and escalates across cycles (temporal-dynamic). Both are facets of the single metacognitive commitment; PLDPS supplies the dynamic-accumulation variable structure for the temporal facet.

  The motivated-update-refusal signature this section formalizes is the learning-domain instance of a more general self-reinforcing loop the parent error theory describes — refutation-avoidance through frame-change, selective data use, or affective re-escalation — and it draws on Nguyen's epistemic-bubble/echo-chamber distinction (already cited in §5.1 and §10) and the sampling asymmetry described by Denrell (2005) as its nearest academic parallels. It also reflects a fallibilist commitment the parent theory makes explicit: causal understanding is treated as a measuring discipline that keeps updating, never a finished terminus — which is why MIRA's own stance throughout is that its causal signals are tentative and calibrated, never treated as final causal truth.

---

## §9. Intervention Model

Intervention is selected on (distortion type × latitude × verification type) — matrix in axis2-spec v4 §6.2 — and delivered under binding coaching ethics: **non-directive invitations** (MI: "you might try…", never directives), **3-stage guided discovery** (information → discrepancy → alternative; Padesky adaptation), **self-monitor signals** for recurrence, **structural reattribution** wherever dispositional blame appears, **no person-level verdicts in either direction** (blame or praise), and **the learner holds final judgment**. Where a detected signal has no coaching template, the system discloses the signal honestly rather than substituting unrelated coaching (zero-silent-skip).

---

## §10. Positioning Map

Inherited (founder-approved): the axis2-spec v4 §8 academic reference map — motivated reasoning, predictive processing, JOL/calibration, prospect theory/EPPM, self-deception (von Hippel & Trivers), epistemic bubbles/echo chambers (Nguyen), identity-protective cognition, self-handicapping, D/I/A logical traditions (Aristotle, Mill/Whewell, Peirce — the reasoning_philosophy corpora, per §6.1), attribution theory.

**Proposed additions (≤6, each pending founder review)**:

| Addition | One-line warrant |
|---|---|
| Walton — argumentation schemes & critical questions | formal twin of the pattern-specific Socratic blocks; mature anchoring tradition |
| Toulmin — claim/data/warrant | family resemblance to PSR for argument-structured (D) claims |
| CBT cognitive distortions + Socratic restructuring | clinical twin; MIRA = generalization outside the clinical domain with engineering contracts |
| Olson — stationary vs. roving bandits | Axis 3 power/incentive skeleton's nearest respected anchor |
| Hobbes, *Leviathan* I.1–3 (with Hume) | explicit lineage of the Axis 1 sensation→memory→imagination→reason chain |
| Debiasing-intervention literature (e.g., Morewedge) | empirical neighbor for intervention-efficacy claims |

Track D — the separate, more general theory of causal reasoning and of error introduced in §0.3 and §5.0 — supplies additional positioning anchors that are cited for context only, never loaded as machinery. Two are worth naming directly: the organizing contrast between a regularity-tracking tradition (Hume through Mill to modern statistics) and a hypothesis-construction tradition (Kant through Whewell to Peirce), which converge in the modern potential-outcomes and structural-causal literature (Neyman, Lewis, Pearl) that MIRA's D/I/A modes (§6.1) draw on; and Kunda (1990) on bounded justification, which underlies the four-band latitude model of §4. The fuller set of anchors — additional fallacy-education, sampling-bias, and partial-identification literature — is documented in the companion track D note rather than reproduced here. In the same spirit of honesty, a few widely-cited findings that replicate weakly (for example, in cultural cognition and in lie-detection accuracy, and the "Dunning–Kruger effect" read as a statistical artefact rather than a psychological one) are deliberately *not* used as anchors, even where an earlier map or a pattern warrant might have leaned on them.

**Positioning sentence**: every component has neighbors; the *composition* — a domain-pluggable, calibration-contracted judgment-audit layer with verification-status epistemics and non-directive coaching ethics — is the unoccupied position. Convergent validity is claimed; derivation is not.

**Authority-anchoring self-defense.** Anchoring to established figures (Kahneman, Anderson, Mill/Peirce, and the CMP lineage of Turing/Church/Kowalski/Martin-Löf/De Raedt) aids external credibility but carries a reflexive risk: if "a master endorses this" substitutes for a construct's own discriminating power, MIRA instantiates its own `appeal_to_authority` pattern (`PAT-D-03`). Two existing assets hold this line and must remain live, not be dropped in compilation: (a) the `AE_17pattern_evidence_registry_VERIFY_report`, which records correspondence downgrades against original sources (functional-analog/partial, not isomorphism) and replication caveats; and (b) the CMP Reference Principle (§0.3), which imports a figure's *intention*, not their *apparatus*. Convergent validity is a claim to be defended by these guards, not a borrowed authority.

---

## §11. Falsifiable Commitments and Research Agenda

### 11.1 Architecture-level falsifiers (pre-registered)

This architecture is itself a provisional interpretive judgment; the following conditions, if met, falsify specific design decisions. *(All numeric thresholds are placeholders for founder setting.)*

- **F1 (core/domain cut)**: porting a second domain pack requires modifying > [10%] of core-classified code → the cut is wrong; redraw from the port diff.
- **F2 (latitude model)**: inter-rater κ < [0.6] on latitude banding → redesign the spectrum.
- **F3 (Lane 2 value)**: after [N] further effort-months, formally verified patterns < [5] → demote Lane 2 to constraint-checker or remove (honesty principle applied to ourselves).
- **F4 (calibration UX)**: < [threshold]% of test users notice/use verification statuses → redesign the *presentation*, not the epistemics.
- **F5 (demand thesis)**: voluntary second-session reuse below [threshold] → the standalone-agent thesis is falsified for that segment; pivot to embedded judgment-layer mode.

### 11.2 Validation plan (minimum decisive moves)

(1) Public mini-corpus (50–100 labeled items incl. healthy controls) → cue-layer precision/recall = first empirical claim. (2) Latitude κ study (F2). (3) One predictive pilot in the first domain.

### 11.3 Research agenda (contribution hooks)

| # | Open problem | Done when |
|---|---|---|
| RA-1 | Second domain pack: judgment protection (fraud defense) | registry sketch + 20 fixtures + pilot scoring |
| RA-2 | Latitude classifier | κ ≥ target on public sample |
| RA-3 | S-exclusivity rule detection (most mechanizable spec variable) | rule + fixtures merged |
| RA-4 | Cycle detection (recurrence of unrevised appraisal; PLDPS dynamic-accumulation + BAY-corpus escalation, dormant) | self-reinforcing loop surfaced in report |
| RA-5 | Bayesian formalization of I/A patterns (cues → likelihood ratios; verification statuses → posterior bands; per-PSR-stage probability-tradition assignment, §3.4) | spec note + prototype; canonical source = the BAY corpus (dormant) |
| RA-6 | External pattern contributions via fixture PRs | first outside pattern admitted under §7.3 |
| RA-7 | Public eval/benchmark release | leaderboard-ready harness |
| RA-8 | Foundational-kernel relationship: MIRA-core ↔ EIU-CRD (foundational-agent class) | resolved in the domain 1–3 review; options: System-A domain pack vs. separate-but-linked agent |

**EIU-CRD (sister kernel, not integrated)**: EIU-CRD is a separate instance of the same diagnostic kernel — persona-relative, evidence-cited, verification-statused — diagnosing the *first half* of a path (content receptivity: does it reach the person) where MIRA diagnoses the *second half* (judgment intervention: does it change the person's reasoning). Kept separate by design (verification debt not inherited); listed here, not folded into core. (The formal PSR↔EIU connection remains an open item; see axis2-spec v4 §9.2.) A further question — whether MIRA-core and EIU-CRD are two instances of a *common foundational-kernel class* (each a base framework that domain packs extend, given their shared purpose and mechanism) — is reserved for the domain follow-up review (RA-8), not resolved here.

---

## Appendix A. Coverage Map (spec construct ↔ implementation)

Construct-level (counts are code-verified):

| Construct | shipped (v0.2.3) | post-patch | v1.0 target |
|---|---|---|---|
| PSR 3-stage decomposition | positional heuristic | same | semantic decomposition + variable extraction |
| P variables (latitude·evidence·emotion) | absent | health signals / cue strength = primitive form | full |
| S variables (exclusivity·rigor) | absent | absent | **exclusivity rules first (most mechanizable)** |
| R variables (magnitude·efficacy·verifiability) | absent | catastrophizing cue = primitive form | EPPM-based |
| Interpretive latitude (4-band, proportional rigor) | absent | 3-class response = coarse approximation | latitude classifier |
| D/I/A routing | single-keyword regex | same | claim_type × latitude router |
| Typology A/B/C1/C2 + intervention matrix | absent | absent | v1.0 core candidate |
| Mechanistic triad + EvidencePacket | absent (taxonomy-bound only) | crude cue-form re-invented | **compile from 17-pattern registry (highest leverage)** |
| Cycle detection | absent (no history) | absent | session history + loop visualization |
| Verification statuses + invariants | **implemented, strong** | 3 gate collisions fixed | promote to core contract |
| Formal (Lane 2) specs | 3 specs, 2 live Prolog (false_dilemma, oversimplified_cause; fluency spec-only) | same | expand; critical-thinking pack activates FAL/FML/MOD |
| Coaching templates | **6 live-loaded** (5 core of 21 + 1 dual-use) | ko restored | authoring contract / 21 |

Corpus-level: see the internal coverage map (SSOT) referenced in §0.3. Summary: corpus is *distilled* (thin shipped surface) not unused; highest-value dormant assets are the mechanistic triad/EvidencePacket (registry) and, per domain, BAY v2 (judgment protection) and FAL/FML/MOD+CMP (critical thinking).

## Appendix B. Terminology and Changelog

| Term (KR lineage) | Canonical (EN) | Note |
|---|---|---|
| 가설적 판단 | Provisional Interpretive Judgment | external term since v3 |
| P/S/R | Premise–Appraisal / Strategy / Result-Projection | early Problem/Solution terms superseded |
| 기만 (은폐/변조) | judgment distortion (concealment / alteration) | umbrella sanitized in v3; primitives per registry header |
| 본의 | founder intent | method term, §0.1 |
| binding state | bound / distilled / taxonomy_bound / dormant | corpus governance, §0.3 |

**Changelog** (development history):
- **v0.1** (2026-06-12) — Initial assembly from the axis2-spec (v4), the founder's operational notebooks, the sup-01 ethics supplement, and documentation of the implemented code.
- **v0.2** (2026-06-12) — Added corpus governance and the Reference Principle (§0.3); the mechanism layer (mechanistic triad / EvidencePacket, §7.3) and its compilation discipline (§7.3a); the three-domain roadmap and lane separation (§7.6); code-verified counts throughout §8 and Appendix A; the authority-anchoring self-defense (§10).
- **v0.3** (2026-06-18) — Founder-confirmed integration of the purpose/dual-use stance (§1.0); the evidence-class model marked explicitly as a provisional skeleton pending further development (§2.1); the causal-telos rationale for D/I/A reasoning (§6.1); the organismic-metacognition re-grounding of the multi-lane architecture (§6.2); the PLDPS-based re-grounding of cycle detection (§8); and the foundational-kernel question linking MIRA-core to EIU-CRD (§11, RA-8). Reviewed by independent domain critics.
- **v0.4** (2026-06-19) — Bayesian-formalization layer integrated: the probability-tradition assignment by PSR stage (§3.4); the mathematical layer's scope and limits, including the observation/intervention distinction, the non-reduction of abduction to inference-to-best-explanation, and the modal/probabilistic complementary-layering hypothesis (§6.1a); the formalized cycle-detection policy (§8); per-pattern Bayesian signatures (§7.1); and the corresponding research-agenda item (§11, RA-5).
- **0.5 public edition** (2026-07-13) — Public extraction: integrated the track D cross-references throughout as settled text rather than draft annotations; tightened several passages for tense consistency with the project's dormant/roadmap status (§3.4, §6.1a, §7.1, §8); generalized internal corpus cross-references (specific BAY section numbers abstracted to "BAY corpus, dormant"); and removed internal review scaffolding.
