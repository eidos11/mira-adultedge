# Axis 2 Specification: Motivated Appraisal and Judgment Distortion
## Agent Design Specification — Phase 2, Step 1

**Version**: 4.0 (English, academically grounded, externally communicable)  
**Date**: 2026-04-10  
**Author**: Mnemo (original theory and all foundational claims)  
**AI-assisted preparation**: assembly and formalization were carried out with the assistance of Claude (Anthropic). All theoretical claims, design decisions, and their validation are the author's; the AI tool holds no authorship and bears no responsibility for the content.  
**Source theory**: Mnemo's Provisional Interpretive Judgment framework (2024–2025)  
**Repo path**: `research/axis2-spec.md` (companion to `research/THEORY.md` — Axis 2 normative detail)  
**Internal lineage term**: 가설적 판단 (Hypothetical Judgment) — retained for project-internal reference  
**Purpose**: Core theoretical model for the cross-verification interface between System A (Diagnostic) and System B (Logic Verification)

---

## 0. Position in the Architecture

```
Phase 2 Execution Order:
  ① Axis 2 Specification  ← THIS DOCUMENT (prerequisite) [DONE]
     │
     ▼
  ② Cross-Verification Interface Schema                   [DONE — minimum implementation]
     │
     ├──────────────────┐
     ▼                  ▼
  ③ Verification Rules   ④ Orchestration Logic             [NEXT]
```

Axis 2 is the **theoretical bridge** between System A (learning diagnosis) and System B (logic verification). It models *why* and *how* learner self-assessments become distorted, and specifies what the cross-verification system must detect and how it should intervene. Within AdultEdge's metacognition-centered SRL architecture, Axis 2 functions as the **motivated appraisal/distortion submodel** — not a universal theory of human judgment, but an operational model tuned for learning self-assessment contexts.

---

## 1. Theoretical Foundation

### 1.1 Provisional Interpretive Judgment

Many judgments about matters of fact, self-assessment, and future outcomes are **provisional, inferential, and revisable**. This is especially true in learning contexts, where adults must continuously assess their own competence, diagnose obstacles, select strategies, and project outcomes — all under conditions of significant uncertainty and motivational pressure.

The structure of such judgment closely parallels the **hypothetico-deductive method** in philosophy of science, but with two extensions relevant to learning self-assessment:

1. **Scope**: Not limited to scientific inquiry — it describes the general structure of everyday self-assessment, including the informal reasoning learners use to evaluate their own progress
2. **Process**: Not a single linear cycle (observation → hypothesis → test) but a **continuous loop** in which inductive and deductive reasoning alternate, often without explicit testing

**Academic grounding**: This view is consistent with **motivated reasoning** theory (Kunda, 1990), which demonstrates that people arrive at conclusions they are motivated to reach while maintaining an "illusion of objectivity." It also aligns with **predictive processing** frameworks (Clark, 2013; Hohwy, 2013) that model the brain as continuously generating and updating hypotheses, and with Hume's foundational observation that inductive inferences lack necessary justification.

### 1.2 Position Within the Three-Axis Model

```
Axis 1 (Cognitive Engine)       Axis 2 (Judgment Distortion)      Axis 3 (Social Dynamics)
Sensation→Memory→Imagination    Appraisal→Strategy→Projection     Human typology, power, social exploitation
────────────────────────────────────────────────────────────────────────────────────────
  Substrate engine                Judgment formation & distortion    Social context for distortion
  (supplies inputs)               (core mechanism)                   (external pressures)
```

### 1.3 The Role of Emotion (Connection to Axis 1)

Emotion is the most basic interpretive response to sensory input and imaginative simulation (Axis 1). In learning self-assessment, emotion intervenes at two points:

- **At appraisal formation**: Fear of failure or desire for success biases which interpretation of one's situation is adopted
- **At outcome projection**: Emotional loading causes exaggeration or minimization of expected consequences

**Academic grounding**: This dual-point emotional intervention aligns with the "hot cognition" model (Lodge & Taber, 2005) and the affect heuristic (Slovic et al., 2007).

---

## 2. The PSR Formal Structure

Mnemo's original two-stage model (Stage 1: situation interpretation / Stage 2: consequence derivation) is formalized into a **three-stage PSR structure**. The intermediate stage — Strategy — straddles both appraisal and outcome: the situation-interpretation already constrains the strategy space, while the strategy determines which outcomes can be projected. The three-stage decomposition enhances diagnostic precision.

**Terminology note**: PSR labels are chosen for analytical precision in the learning-assessment domain. `P = Premise/Appraisal`, `S = Strategy Selection`, `R = Result Projection`. The abbreviation PSR is retained for conciseness.

### 2.1 P-Stage: Premise / Appraisal Formation

**Function**: Interpretation of one's learning situation. Formation of a situational judgment about one's current state, obstacles, and capacities.

```yaml
P-Stage:
  inputs:
    - sensory data and direct experience (Axis 1)
    - stored experience and prior outcomes (Axis 1: memory)
    - imaginative simulation of scenarios (Axis 1: imagination)
    - social context: group norms, peer comparison, authority claims (Axis 3)
  output:
    provisional interpretive judgment (appraisal / premise)
    = "My situation is such-and-such"
  key_properties:
    - Core vulnerability: appraisals often form on the basis of motivational
      pressure despite insufficient evidence
    - The higher the interpretive latitude, the more susceptible to distortion
    - THIS IS THE MOST CRITICAL STAGE: appraisal formation decisively
      constrains all downstream stages
  variables:
    interpretive_latitude: low | medium | high | extreme
    evidential_basis: strong | moderate | weak | absent
    emotional_load: fear | desire | neutral
```

**Academic grounding**: P-Stage distortion maps onto **motivated reasoning** (Kunda, 1990) and **confirmation bias** (Nickerson, 1998). In learning contexts specifically, it connects to **Judgment of Learning (JOL) miscalibration** (Koriat, 1997) and **illusion of competence** (Koriat & Bjork, 2005), where learners systematically overestimate their understanding based on cues irrelevant to actual performance (e.g., fluency of presentation, familiarity of material).

### 2.2 S-Stage: Strategy Selection / Response Policy

**Function**: Derivation of action guidelines or learning strategies from the P-Stage appraisal.

```yaml
S-Stage:
  input:
    - P-Stage appraisal
  output:
    action guideline / strategy
    = "Therefore, I should do such-and-such"
  key_properties:
    - Constrained by P-Stage appraisal, but derivation itself carries
      significant interpretive latitude
    - Formal deduction rarely applies; typically informal reasoning
    - From the same appraisal, radically different strategies can be derived
    - Exclusivity claims ("only this approach works") are a primary
      distortion mechanism
  variables:
    derivation_rigor: formal | semi-formal | informal | arbitrary
    strategy_exclusivity: open | claimed_exclusive
    means_end_validity: valid | questionable | fallacious
```

**Academic grounding**: S-Stage distortion corresponds to **belief-congruent information processing** (Kunda, 1987) and **need for cognitive closure** (Kruglanski, 2004).

### 2.3 R-Stage: Result Projection / Anticipated Consequence

**Function**: Specification of expected outcomes — the concrete shape of learner hopes and fears.

```yaml
R-Stage:
  input:
    - S-Stage strategy
  output:
    projected consequence (concrete form of fear or desire)
    = "Then I will achieve X / suffer Y"
  key_properties:
    - Produces considerable fear or desire with real behavioral consequences
    - Exaggeration or catastrophization of consequences is a core distortion tool
    - Fear induction + sole-remedy claim = classic distortion combination
    - Once P+S are established, R-Stage is primarily about execution:
      clarification, emphasis, sustained motivation
  variables:
    consequence_magnitude: proportionate | exaggerated | catastrophized
    alternative_acknowledged: yes | partially | suppressed
    perceived_remedy_efficacy: high | moderate | low | unexamined
    verifiability: verifiable | partially_verifiable | unfalsifiable
```

**Academic grounding**: R-Stage distortion connects to **prospect theory** (Kahneman & Tversky, 1979) — particularly loss aversion — the **affect heuristic** (Slovic et al., 2007), and the **Extended Parallel Process Model** (Witte, 1992), which explains how threat magnitude and perceived efficacy jointly determine whether a fear-based message produces adaptive or maladaptive responses. The addition of `perceived_remedy_efficacy` directly reflects EPPM's efficacy dimension.

### 2.4 The Cyclic Structure

PSR is not a one-shot process but a **continuous cycle**:

```
P (appraisal) → S (strategy) → R (projected result)
       ↑                                │
       │                                ▼
       └────── actual experience ────────┘
                      │
              ┌───────┴───────┐
              ▼               ▼
      appraisal revision    appraisal reinforcement
      (healthy cycle)       (motivated distortion loop = fixation)
```

**Healthy cycle**: Experience revises the appraisal → more accurate self-assessment → better strategy selection → more realistic expectations.

**Motivated distortion loop**: Experience is filtered to reinforce the existing appraisal → confirmation bias → same errors repeated → fixation and escalation.

**Academic grounding**: This maps onto **belief perseverance** (Ross, Lepper & Hubbard, 1975) and, in learning contexts, the finding that repeated study without testing creates **stability bias** in JOL — learners become increasingly confident without actual competence gains (Koriat & Bjork, 2005).

---

## 3. Interpretive Latitude Model

Distortion operates primarily where **epistemic underdetermination** is high — where the object of judgment permits multiple legitimate interpretations.

### 3.1 The Latitude Spectrum

| Level | Domain Examples | Distortion Potential | Learning Context Examples |
|---|---|---|---|
| **low** | Physical reality, measurable quantities | Negligible | "I studied 3 hours today" (logged) |
| **medium** | Technical problems, testable claims | Limited | "I understood this chapter" (testable) |
| **high** | Social evaluation, effort assessment | Significant | "I tried hard enough" (criteria ambiguous) |
| **extreme** | Identity claims, dispositional attributions | Pervasive | "I'm not a consistent person" (unfalsifiable) |

### 3.2 Design Principle

The cross-verification system **first classifies** interpretive latitude, then applies **proportionally rigorous** verification:

```
low latitude    → factual check sufficient (learning logs, output inventory)
medium latitude → structured test / comparison possible
high latitude   → fallacy pattern detection + calibration check required
extreme latitude → metacognitive intervention required
                   (examine the judgment process itself)
```

**Academic grounding**: This graduated approach aligns with research on **ill-structured problems** (Jonassen, 1997) and **epistemic cognition** — the finding that ambiguous problem spaces require qualitatively different reasoning strategies than well-defined ones.

---

## 4. Judgment Distortion Typology

### 4.1 The Fundamental Distortion Structure (from Mnemo's original theory)

> "The typical strategy of fraud and deception: cause the target to trust a false [P-Stage], then under the expectation of obtaining highly desirable [R-Stage] results, grant the deceiver control over one's assets."

Decomposed into PSR:
1. **P-manipulation**: Install a false appraisal as trustworthy
2. **S-monopoly**: Claim exclusive authority over the strategy
3. **R-inflation**: Exaggerate desirable outcomes or catastrophize non-compliance

### 4.2 Four Types by Self-Relation and Social Structure

| Type | Label | Definition | Reality Contact | Correctability |
|---|---|---|---|---|
| **A** | Strategic misrepresentation | Maintains dual cognitive system: knows the truth while presenting falsehood | Preserved | Quick with structural evidence |
| **B** | Motivated false belief (self-deception) | Constructs own understanding in line with motivational pressure | Weakened | Requires metacognitive intervention |
| **C1** | Epistemic bubble | Information deficit: relevant counter-evidence simply not encountered | Partially intact | Evidence exposure often sufficient |
| **C2** | Echo chamber | Systematic distrust of external sources; counter-evidence triggers defensive reinforcement | Severely compromised | Extremely difficult; external evidence may backfire |

**Academic grounding — Type A vs B**: This parallels **von Hippel & Trivers (2011)**, who argue that self-deception evolved to facilitate interpersonal deception by eliminating the cognitive load of maintaining dual representations. Mnemo's framework adds that conscious misrepresentation, while more cognitively taxing, preserves adaptive capacity, while motivated false belief produces stronger propagation but reality-disconnection.

**Academic grounding — C1 vs C2**: Following **Nguyen (2020)**, epistemic bubbles (C1) arise from mere omission of relevant sources and can be punctured by evidence exposure, while echo chambers (C2) involve active discrediting of outside sources, making external evidence counterproductive. This distinction is critical for intervention design.

### 4.3 Distortion as Capacity Substitute

> "Those who focus on deception are fundamentally those who are not skilled at or not inclined toward genuine understanding and problem-solving." (Mnemo, original theory)

Distortion functions as a **substitute** for genuine problem-solving capacity:

- It compensates for absent structural design ability
- Specialization in distortion causes genuine capacity to atrophy (path dependency)
- The distorter becomes unable to achieve goals through non-distortive means

**Academic grounding**: This connects to **self-handicapping** (Berglas & Jones, 1978) and research showing that protective attributional strategies, while preserving self-esteem short-term, undermine skill development long-term.

**Connection to AdultEdge core thesis ("Structure > Willpower")**: When learners lack structural problem-solving capacity (task definition, stage placement, feedback loops), they default to motivated distortion narratives ("I just need more willpower") as **compensatory substitutes** for structural design.

### 4.4 The Motivated Miscalibration Loop

> "Desire clouds cognition, and insufficient cognition intensifies excessive desire → mutual reinforcement." (Mnemo, original)

In learning contexts:
- **Motivational pressure** (urgency, anxiety) **impairs metacognitive accuracy**
- Impaired metacognition **intensifies motivational pressure** (more anxiety, more urgency)
- This spiral is the **engine** of the motivated distortion loop (§2.4)

**Academic grounding**: This maps onto **cognitive dissonance** (Festinger, 1957) — dissonance-reduction often amplifies original commitment rather than correcting it — and **identity-protective cognition** (Kahan, 2013), where threats to self-concept or group identity trigger defensive reasoning that degrades judgment quality. In learning contexts, "I am someone who works hard" or "Our study group's method is correct" function as identity commitments that resist disconfirming evidence.

---

## 5. Learning-Context Distortion Patterns: PSR Mapping

The distortion patterns are mapped to both their primary PSR stage and their **verification type** (D = deductive, I = inductive, A = abductive). This dual classification reflects the expanded logic foundation (see §5.4). Pattern selection and calibration will be refined in dedicated sessions with domain-specific corpus review.

### 5.1 P-Stage Patterns (Appraisal Distortion)

| Pattern | Learning Manifestation | Latitude | Type | Verification |
|---|---|---|---|---|
| **Hasty generalization** | "I'm fundamentally unable to be consistent" | extreme | B | **I** |
| **Anecdotal evidence** | "My friend did it this way, so I should too" | high | A/B | **I** |
| **Genetic fallacy** | "Expensive course must be good" | medium | A | **D** |
| **Confusing explanation with excuse** | "Circumstances were bad" mistaken for diagnosis | high | B | **A** |
| **Prediction fallacy** | "I'll certainly fail again this time" | extreme | B | **I** |

### 5.2 S-Stage Patterns (Strategy Derivation Distortion)

| Pattern | Learning Manifestation | Latitude | Type | Verification |
|---|---|---|---|---|
| **Oversimplified cause** | "Lazy → just try harder" | high | B | **A** |
| **False dilemma** | "Perfect execution or nothing" | high | B | **D** |
| **Appeal to authority** | "Famous instructor said so" | medium | A | **D** |
| **Sunk cost** | "I've invested too much to change approach" | medium | A/B | **I** |

### 5.3 R-Stage Patterns (Outcome Projection Distortion)

| Pattern | Learning Manifestation | Latitude | Type | Verification |
|---|---|---|---|---|
| **Appeal to consequences** | "If I don't pass, my life is over" | extreme | B | **D** |
| **Composition fallacy** | "1 hour/day × 365 = surely enough" | medium | A | **I** |
| **Perfectionist fallacy** | "Must have perfect plan before starting" | high | B | **D** |


### 5.4 Architectural Note: Expanded Logic Foundation

Not all learner self-assessment distortions are well-modeled as logical fallacies in the narrow sense of formal/informal reasoning errors. Many are better understood through an **expanded logic foundation** that encompasses three modes of reasoning:

- **Deductive verification (Type D)**: Detection of formal and informal reasoning errors in the Aristotelian tradition. Applies when the learner's claim has argument structure ("X, therefore Y").
- **Inductive verification (Type I)**: Assessment of empirical generalization and causal inference in the Mill/Whewell tradition. Applies when the learner's claim is a self-assessment ("I understand this," "I studied enough"). JOL miscalibration, illusion of competence, and fluency illusion fall here — they are inductive errors (generalizing from irrelevant cues without empirical verification).
- **Abductive verification (Type A)**: Evaluation of causal attribution and hypothesis selection in the Peircean tradition. Applies when the learner explains success or failure causes ("I failed because I'm lazy"). Self-serving attribution, identity-protective cognition, and self-handicapping fall here — they are abductive errors (selecting motivationally biased explanations over more probable structural ones).

These three verification types operate within a **single expanded logic foundation**, not as independent parallel layers. The existing 12 distortion patterns (§5.1-5.3) are each assigned a primary verification type (D, I, or A), and 5 additional patterns are introduced in §5.5 for inductive and abductive coverage.

**Design principle**: Calibration research (Koriat, Bjork, Dunning-Kruger) and attribution research (Weiner, Kahan) provide the empirical content that populates the inductive and abductive verification types. The logical framework provides the formal structure. This mirrors Mill's original insight that logical principles supply the necessary condition while empirical data supplies the sufficient condition.

### 5.5 Extended Patterns (v4 addition)

These patterns address gaps in inductive (I) and abductive (A) verification coverage identified during the Layer 0 redefinition:

| Pattern | PSR Stage | Learning Manifestation | Latitude | Type | Verification |
|---|---|---|---|---|---|
| **Fluency illusion** | P | "I read it smoothly, so I understand it" | high | B | **I** |
| **Effort heuristic** | P | "I studied hard, so I must have learned" | high | B | **I** |
| **Recognition-retrieval confusion** | P | "I recognize the concept, so I know it" | medium | B | **I** |
| **Self-serving attribution** | P/S | "I succeeded because I'm talented; I failed because of circumstances" | high | B | **A** |
| **Identity-protective reasoning** | P | "I am a hard-working person" (resists disconfirming evidence) | extreme | B | **A** |

**AdultEdge connection**: These patterns are already substantively addressed in AdultEdge's content — "자기 말로 설명할 수 없으면 모르는 것" (Korean: "if you cannot explain it in your own words, you don't truly know it"; fluency illusion / recognition-retrieval), "Structure > Willpower" (self-serving attribution / effort heuristic), "인식 ≠ 인출" (Korean: "recognition ≠ retrieval"; recognition-retrieval confusion). The v4 extension formalizes these as verification patterns within System B.


---

## 6. Cross-Verification Interface

### 6.1 Extended JSON Schema

**Request (Diagnostic Pipeline → Logic Verification Pipeline):**

```json
{
  "learner_claim": "Original self-assessment statement",
  "claim_type": "argument | self_assessment | causal_explanation",
  "psr_decomposition": {
    "P_appraisal": "Implied situation-interpretation",
    "P_latitude": "low | medium | high | extreme",
    "P_evidential_basis": "strong | moderate | weak | absent",
    "S_strategy": "Implied or explicit action guideline",
    "S_exclusivity": "open | claimed_exclusive",
    "R_projection": "Projected outcome",
    "R_emotional_load": "fear | desire | neutral",
    "R_magnitude": "proportionate | exaggerated | catastrophized",
    "R_perceived_efficacy": "high | moderate | low | unexamined"
  },
  "diagnostic_result": {
    "primary_leak": "Identified structural leak",
    "hypothesized_cause": "Hypothesized cause"
  },
  "cycle_detection": {
    "is_recurring_pattern": true,
    "previous_instances": ["list of similar past claims"],
    "loop_type": "self_correcting | self_reinforcing"
  },
  "verification_request": {
    "check_type": "deductive | inductive | abductive | calibration_check | attribution_check | cycle_break",
    "context": {}
  }
}
```

**Response (Logic Verification Pipeline → Diagnostic Pipeline):**

```json
{
  "P_check": {
    "validity": "valid | questionable | distorted",
    "verification_type": "D | I | A",
    "pattern_candidates": ["identified distortion patterns"],
    "latitude_confirmed": "high",
    "refined_appraisal": "Suggested revised interpretation"
  },
  "S_check": {
    "means_end_validity": "valid | questionable | distorted",
    "pattern_candidates": [],
    "alternative_strategies": ["alternative approaches"]
  },
  "R_check": {
    "proportionality": "proportionate | exaggerated | catastrophized",
    "pattern_candidates": [],
    "realistic_projection": "Suggested realistic outcome",
    "efficacy_assessment": "Remedy efficacy evaluation"
  },
  "cycle_assessment": {
    "loop_detected": true,
    "loop_type": "self_reinforcing",
    "intervention_type": "evidence | metacognitive | structural | calibration_test",
    "break_point": "P | S | R"
  },
  "distortion_assessment": {
    "type": "A | B | C1 | C2 | none",
    "verification_type": "D | I | A",
    "intervention_strategy": "Type-appropriate intervention"
  },
  "overall_confidence": 0.0
}
```

### 6.2 Intervention Strategy Matrix

| Type | Latitude | Verification | Primary Intervention | Secondary Intervention |
|---|---|---|---|---|
| A (strategic misrepresentation) | any | D/I/A | Structural evidence (logs, outputs) | Alternative interpretation |
| B (motivated false belief) | high | **D** | Metacognitive questioning ("What evidence supports this?") | Logical counter-argument |
| B (motivated false belief) | high | **I** | Predict-then-test protocol ("Predict your score, then take the test") | Retrieval test, performance comparison |
| B (motivated false belief) | high | **A** | Alternative hypothesis ("What structural cause might explain this?") | Reattribution exercise |
| B (motivated false belief) | extreme | D/I/A | Cycle visualization ("This pattern has repeated N times") | External feedback (social learning) |
| C1 (epistemic bubble) | any | D/I/A | Evidence exposure; broaden information sources | Peer comparison data |
| C2 (echo chamber) | extreme | D/I/A | Outside system scope — flag + warning | Recommend trusted external perspective |

---

## 7. Illustrative Extreme Case: Religious Belief Structures

Religious belief represents a **structurally analogous extreme case** that illuminates the PSR mechanism by pushing each variable to its maximum. Everyday learning self-assessments are compressed and attenuated versions of the same structural pattern. This section serves as a **heuristic illustration**, not an empirical demonstration of structural identity.

> **Scope note**: This illustration analyzes *structural mechanics* (how PSR variables behave at maximum parameters), not the validity, content, or merit of any belief system — it is neither a critique nor an endorsement of religion. MIRA's stance is deliberately restrained and structural, confined to cognitive-distortion mechanics rather than adjudicating specific religious or political positions.

### 7.1 PSR at Maximum Parameters

```
P: "A perfect being exists" — interpretive latitude: extreme
S: "Communicate through designated authority" — exclusivity: claimed_exclusive
R: "Salvation vs. damnation" — emotional load: extreme; magnitude: catastrophized
```

### 7.2 Attenuated Parallels in Learning Context

| Extreme-Case Pattern | Learning Self-Assessment (attenuated) |
|---|---|
| "You are a sinner" | "I am a lazy person" |
| "Only this church saves" | "Only this method works" |
| "Believe and be saved" | "Just have willpower" |
| "Heaven vs. Hell" | "Pass vs. life ruined" |

The analogy is **structurally illuminating** — the same PSR distortion mechanisms operate — but the degree is substantially different: learning-context interpretive latitude is typically high rather than extreme, and emotional loading is finite rather than unbounded.

---

## 8. Academic Reference Map

| Framework Component | Established Parallel | Key References |
|---|---|---|
| Provisional interpretive judgment | Motivated reasoning; predictive processing | Kunda (1990), Clark (2013) |
| P-Stage distortion | Motivated reasoning; confirmation bias | Kunda (1990), Nickerson (1998) |
| P-Stage miscalibration | JOL research; illusion of competence | Koriat (1997), Koriat & Bjork (2005) |
| S-Stage distortion | Belief-congruent processing; need for closure | Kunda (1987), Kruglanski (2004) |
| R-Stage distortion | Prospect theory; affect heuristic; EPPM | Kahneman & Tversky (1979), Slovic et al. (2007), Witte (1992) |
| Interpretive latitude | Ill-structured problems; epistemic cognition | Jonassen (1997) |
| Type A: strategic misrepresentation | Self-presentation; impression management | Baumeister (1982) |
| Type B: motivated false belief | Evolutionary self-deception theory | von Hippel & Trivers (2011) |
| Type C1: epistemic bubble | Epistemic bubble concept | Nguyen (2020) |
| Type C2: echo chamber | Echo chamber concept | Nguyen (2020) |
| Motivated miscalibration loop | Cognitive dissonance; identity-protective cognition | Festinger (1957), Kahan (2013) |
| Distortion as capacity substitute | Self-handicapping | Berglas & Jones (1978) |
| PSR cyclic reinforcement | Belief perseverance; stability bias in JOL | Ross et al. (1975), Koriat & Bjork (2005) |

| **Expanded logic foundation — deductive** | **Aristotelian syllogistic; formal/informal fallacy theory** | **Aristotle; Bonnet; LaBossiere** |
| **Expanded logic foundation — inductive** | **Mill's Methods; inductive logic; consilience** | **Mill (1843), Whewell (1840)** |
| **Expanded logic foundation — abductive** | **Abduction; inference to best explanation** | **Peirce (1903), Lipton (2004)** |
| **Fluency illusion / effort heuristic** | **JOL cue-utilization framework** | **Koriat (1997), Bjork et al. (2013)** |
| **Self-serving attribution** | **Attribution theory; self-serving bias** | **Weiner (1985), Miller & Ross (1975)** |
| **Identity-protective reasoning** | **Identity-protective cognition** | **Kahan (2013), Kahan et al. (2017)** |

**Note on theoretical relationship**: Mnemo's framework was developed independently from philosophical first principles and extensive personal reflection. The academic mapping demonstrates **convergent validity** and provides standardized terminology for external communication and system implementation. It does not imply derivation from these established theories.

---

## 9. Open Items and Next Steps

### 9.1 Confirmed in This Specification

- [x] PSR three-stage formal schema with standardized terminology
- [x] Interpretive latitude model (replacing "interpretation freedom degree")
- [x] Judgment distortion typology: 4 types (A, B, C1, C2)
- [x] 12 learning-context distortion patterns mapped to PSR stages
- [x] Cross-verification JSON schema with D/I/A verification types
- [x] Intervention strategy matrix (4 types × latitude × verification type)
- [x] Academic reference map with convergent validity framing
- [x] Religious case repositioned as heuristic extreme-case illustration
- [x] **Expanded logic foundation (D/I/A) replacing narrow fallacy-only model**
- [x] **5 extended patterns (fluency illusion, effort heuristic, recognition-retrieval, self-serving attribution, identity-protective reasoning)**
- [x] **claim_type and verification_type fields in JSON schema**

### 9.2 Required in Subsequent Sessions

- [x] ~~**Architecture review**: System B expansion to 3-layer parallel verification~~ → **Superseded**: Layer 0 redefined to expanded logic foundation (D/I/A within single base)
- [x] **Step 2**: Cross-verification interface minimum implementation — **COMPLETE**
- [ ] **Step 3**: Distortion pattern rules — 12 existing + 5 new = 17 patterns, classified by D/I/A. Prolog rules + LLM detection prompts. Router expansion to latitude × claim_type.
- [ ] **Step 4**: Representative case test (3-4 cases) with expanded Router
- [ ] **Logic foundation session**: Aristotle/Mill/Whewell/Peirce principles → Prolog/Lisp verification rules
- [ ] **Cognitive science mapping session**: Calibration/attribution literature → Type I/A verification patterns and intervention protocols
- [ ] **2nd expansion review**: Dialectics (Hegel/Marx/Zeno), Eastern logic (Laozi/Buddhism/Yin-Yang), uncertainty models (quantum/chaos/Black Swan)
- [ ] **Fallacy refinement**: Dedicated session for pattern selection with domain corpus
- [ ] **Axis 2 deepening**: further elaboration on conscious misrepresentation mechanics and the cognitive burden of motivated false belief
- [ ] **PSR ↔ EIU connection**: Explore EIU model mapping onto learning-context PSR

---

## 10. Changelog and Decision Log

### 10.1 Document Lineage

```
v1.0 (Korean, 2026-04-10)  — Initial specification, Mnemo theory only
v2.0 (English, 2026-04-10) — Academic grounding + English conversion
v3.0 (English, 2026-04-10) — External review integration
v4.0 (English, 2026-04-10) — Expanded logic foundation; Layer 0 redefinition
```

### 10.2 Changelog v3.0 → v4.0

| Section | Change |
|---|---|
| §0 | Step 2 marked DONE in execution order diagram |
| §5.1-5.3 | **Verification column (D/I/A) added** to all pattern tables |
| §5.4 | **Rewritten**: "Beyond Fallacy Detection" → "Expanded Logic Foundation" |
| §5.5 | **New section**: 5 extended patterns with AdultEdge content connection |
| §6.1 | `claim_type` field added to request. `check_type` updated. `verification_type` added to response |
| §6.2 | Intervention matrix expanded with verification type dimension |
| §8 | 6 new entries in academic reference map |
| §9 | Updated: architecture review superseded, Step 2 complete, new deferred sessions |
| §10 | **New section**: Changelog and Decision Log |

### 10.3 Key Changes v2→v3 (preserved for lineage)

- Universality claims lowered (§1.1)
- "Hypothetical Judgment" → "Provisional Interpretive Judgment" (external term)
- PSR labels: P=Premise/Appraisal, S=Strategy, R=Result Projection
- "interpretation freedom degree" → "interpretive latitude"
- "deception" umbrella → "judgment distortion" umbrella
- Type C split into C1 (epistemic bubble) / C2 (echo chamber)
- Ego depletion removed; replaced by identity-protective cognition
- EPPM added to R-Stage grounding; perceived_remedy_efficacy variable added
- JOL/calibration research integrated into P-Stage grounding
- §5.4 added: architectural note on calibration + attribution layers
- §7 repositioned as "heuristic extreme case" (was "structural isomorphism")
- Framing: "metacognition-centered SRL submodel" (not universal judgment theory)

### 10.4 Decision Log

| Date | Decision | Rationale | Impact |
|---|---|---|---|
| 2026-04-10 | Axis2 Spec v1→v2→v3: progressive formalization | Mnemo theory memo → agent design spec → external review | Foundation for Step 2 |
| 2026-04-10 | Step 2: LLM-only PSR Decomposer, 12 core fields, invocation after structure-first-diagnosis | Minimum viable pipeline first | cv_interface.py complete |
| **2026-04-10** | **Layer 0 redefined: "formal/informal fallacy" → "expanded logic (D/I/A)"** | **Narrow fallacy scope forced calibration/attribution outside logic. Expanded base integrates them within Aristotle→Mill→Peirce tradition.** | **§5.4 rewritten, §5.5 added, §6 updated, matrix expanded** |
| **2026-04-10** | **"3-layer parallel" rejected → "single-base differentiation" adopted** | **Parallel = 3 independent theoretical bases. Single expanded logic preserves deduction→induction→abduction hierarchy.** | **Architecture v2 §3.2/§7 aligned** |
| **2026-04-10** | **v3→v4. v3 archived.** | **Layer 0 redefinition scope warrants new version** | **This document** |
