---
title: "AE 17-pattern Evidence Registry"
version: "v1.0-draft"
date: "2026-05-15"
project: "AdultEdge / Howstudy_AdultEdge"
status: "public snapshot; draft for v1.2 evidence-corpus integration"
coverage: "17-pattern lineage + canonical SSOT expansion: 19 core + 2 extension + 1 dual-use descriptor"
source_mode: "Anderson ACT/ACT-R corpus + Kahneman TFS corpus + AE internal specs + 2020-2026 web verification"
---

# AE_17pattern_evidence_registry.md

## 0. Purpose and Scope

This registry converts the AdultEdge diagnostic pattern taxonomy into a mechanism-oriented evidence layer. Its purpose is not to replace the existing pattern labels. It preserves the legacy pattern names while adding Anderson/ACT-R and Kahneman evidence anchors that can support v1.2 implementation, routing, and future RAG retrieval.

### 0.1 Cardinality note

The historical project term is **“17-pattern”**. The current canonical SSOT resolves the taxonomy as:

- diagnostic core: **19** = D6 + I8 + A5
- diagnostic extension: **2** = social_comparison + catastrophizing
- diagnostic total: **21**
- dual-use input/output descriptor: **1** = willpower_blame

Therefore this file contains **22 entries**: 21 diagnostic items plus the dual-use willpower_blame descriptor. This is deliberate. The filename preserves the 17-pattern lineage for compatibility, while the content follows the canonical registry.

### 0.2 Direct-quote / evidence_quote policy

The requested schema contains `evidence_quote`. Because this registry draws repeatedly from the same copyrighted books, long direct quotations are not repeated per entry. Instead:

1. A small quote key is used where safe.
2. Most entries provide a precise source locator; direct quotes are omitted under a quote-limit policy and can be consulted at the cited source.
3. Mechanism descriptions are paraphrases.

Micro-quote keys used in this draft:

| key | phrase | source family | use |
|---|---|---|---|
| ACT-Q1 | “production rules” | Anderson ACT/ACT-R | production/procedural mappings |
| ACT-Q2 | “chunk is the basic unit” | Anderson ACT/ACT-R | declarative/chunk mappings |
| ACT-Q3 | “expected gain minus cost” | Anderson ACT/ACT-R | utility mappings |
| ACT-Q4 | “goal module” | Anderson ACT/ACT-R | goal/metacognitive mappings |
| KAH-Q1 | “System 1 operates automatically” | Kahneman TFS | fast/intuitive operations |
| KAH-Q2 | “What You See Is All There Is” | Kahneman TFS | missing-evidence/coherence errors |
| KAH-Q3 | “heuristics ... systematic errors” | Kahneman/Tversky | heuristics and biases |
| KAH-Q4 | “loss aversion” | Kahneman TFS/prospect theory | consequence/loss mappings |

### 0.3 Confidence scale

| confidence | meaning |
|---|---|
| high | mapping is directly supported by source concept and fits AE pattern with little distortion |
| medium | mapping is a strong functional analogy but not an isomorphism |
| low | source supports only a broad mechanism; additional domain literature is required |

### 0.4 Correspondence scale

| correspondence | meaning |
|---|---|
| isomorphism | close structural match between AE pattern and source mechanism |
| partial | source mechanism explains a major subpart of the AE pattern |
| functional-analog | source mechanism is useful but works at a different explanatory level |
| divergence | source mechanism conflicts with or constrains the AE interpretation |

## 1. Evidence Backbone

### 1.1 AE internal sources used

> Items marked *(internal)* are internal source material — development artifacts not part of the public release and not redistributed in this registry; the registry's claims about them remain reproducible from the published spec and the cited external literature (§1.2 onward).

- `pattern_registry.yaml` — canonical SSOT and cardinality resolution.
- `axis2-spec.md` — PSR, interpretive latitude, D/I/A verification, intervention matrix (published as `research/axis2-spec.md`).
- AE ACT-R/Newell mapping report *(internal)* — 36 mapping units between AE and ACT-R/Newell.
- AE ACT-R/Newell v1.2 deep-verification *(internal)* — latest ACT-R verification and v1.2 mechanistic triad recommendation.
- AdultEdge LogicEngine Combined Architecture v4.3 *(internal)* — System A/B, three-axis foundation, expanded logic basis.

### 1.2 Anderson / ACT-R source spine

- John R. Anderson, *The Architecture of Cognition* (1983): production systems, declarative/procedural distinction, control, procedural learning.
- John R. Anderson, “Is Human Cognition Adaptive?” (1991): rational analysis, Bayesian/environmental framing, memory/categorization/causal inference/problem solving.
- John R. Anderson, *Rules of the Mind* (1993): ACT-R production systems, chunks, activation, utility, learning, transfer.
- John R. Anderson & colleagues, *Foundations of Knowledge Acquisition: Cognitive Models of Complex Learning* (1993): LISP Tutor, model tracing, production-level skill acquisition.
- John R. Anderson, *Learning and Memory: An Integrated Approach* (2000): learning/memory definitions, retrieval, recognition vs recall, skill acquisition, inductive learning.
- John R. Anderson, *How Can the Human Mind Occur in the Physical Universe?* (2007): ACT-R as cognitive architecture, modular organization, associative memory, adaptive control, metacognition-compatible discussion.

### 1.3 Kahneman source spine

- Daniel Kahneman, *Thinking, Fast and Slow* (2011): System 1/System 2, cognitive ease, WYSIATI, substitution, anchoring, availability, representativeness, base-rate neglect, regression, overconfidence, prospect theory, loss aversion, framing, mental accounting.

### 1.4 Recent verification layer, 2020–2026

- ACT-R remains an active research ecosystem with 2020–2026 workshops and 2025/2026 workshop announcements.
- LLM-ACTR / Cognitive LLMs emerged in 2024–2025 as a concrete ACT-R + LLM integration stream, especially in manufacturing decision-making.
- VSM-ACTR 2 (2025) confirms domain-specific ACT-R decision models with metacognition-like extensions.
- Representativeness classic paradigms were directly replicated in a 2025 pre-registered study: 8/9 problems replicated.
- Base-rate neglect appears to generalize but shows large individual differences and mechanistic heterogeneity.
- Framing effects remain significant after publication-bias correction in at least one 2021 meta-analysis, but effect size can be attenuated.
- Loss aversion should be treated conditionally: 2024 meta-analysis estimates smaller average lambda, and 2025 re-meta-analysis disputes robustness under symmetric unordered designs.

## 2. Pattern Crosswalk Summary

| pattern_id | name | vtype | PSR | ACT-R mechanism family | Kahneman family | confidence note |
|---|---|---:|---|---|---|---|
| PAT-D-01 | genetic_fallacy | D | P | declarative, activation, goal | halo effect, affect heuristic, WYSIATI, substitution | ACT medium / KAH medium |
| PAT-D-02 | false_dilemma | D | S | production, goal, conflict_resolution | framing, WYSIATI, substitution | ACT high / KAH medium |
| PAT-D-03 | appeal_to_authority | D | P, S | declarative, utility, production | halo effect, substitution, availability | ACT medium / KAH medium |
| PAT-D-04 | appeal_to_consequences | D | R | utility, goal, production_selection | prospect theory, loss aversion, affect heuristic, framing | ACT medium / KAH medium |
| PAT-D-05 | perfectionist_fallacy | D | S, R | production, utility, goal_stack | loss aversion, status quo bias, planning fallacy, narrow framing | ACT high / KAH medium |
| PAT-D-06 | begging_the_question | D | P, S | production, declarative, goal_loop | WYSIATI, confirmation bias, coherence bias | ACT medium / KAH medium |
| PAT-I-01 | hasty_generalization | I | P | base_level_learning, activation, declarative | law_of_small_numbers, representativeness, base_rate_neglect | ACT high / KAH high |
| PAT-I-02 | anecdotal_evidence | I | P | declarative, analogy, activation | availability, representativeness, WYSIATI | ACT high / KAH high |
| PAT-I-03 | prediction_fallacy | I | R | activation, utility_prediction, rational_analysis | intuitive_prediction, regression_neglect, availability, affect_heuristic | ACT medium / KAH high |
| PAT-I-04 | sunk_cost | I | S | utility, production_strength, goal | loss_aversion, mental_accounting, endowment_effect, narrow_framing | ACT high / KAH medium |
| PAT-I-05 | composition_fallacy | I | R | chunk_hierarchy, production_transfer, goal_structure | substitution, WYSIATI, inside_view, planning_fallacy | ACT high / KAH medium |
| PAT-I-06 | fluency_illusion | I | P | activation, declarative, production_compilation | cognitive_ease, illusion_of_truth, WYSIATI | ACT high / KAH high |
| PAT-I-07 | effort_heuristic | I | P, S | practice, production_strength, utility | substitution, effort_heuristic, sunk_cost_affect | ACT high / KAH medium |
| PAT-I-08 | recognition_retrieval_confusion | I | P | declarative, retrieval, activation, production | cognitive_ease, WYSIATI, substitution | ACT high / KAH high |
| PAT-A-01 | confusing_explanation_excuse | A | P, S | causal_chunk, goal, production_policy | causal_story, substitution, hindsight_bias | ACT medium / KAH medium |
| PAT-A-02 | oversimplified_cause | A | P, S | declarative, activation, utility, production_selection | associative_coherence, WYSIATI, substitution, causal_bias | ACT high / KAH high |
| PAT-A-03 | self_serving_attribution | A | P, S | declarative, utility, goal | overconfidence, illusion_of_validity, substitution | ACT medium / KAH medium |
| PAT-A-04 | identity_protective_reasoning | A | P | goal, declarative, utility, metacognitive_extension | confirmation, coherence, WYSIATI, System_2_laziness | ACT low / KAH medium |
| PAT-A-05 | post_hoc_rationalization | A | cycle | procedural_trace, declarative_reconstruction, verbal_report | hindsight_bias, outcome_bias, illusion_of_understanding | ACT medium / KAH high |
| PAT-EXT-01 | social_comparison | EXT | P, R | declarative, goal, utility, external_cue | anchoring, availability, reference_points, focusing_illusion | ACT low / KAH medium |
| PAT-EXT-02 | catastrophizing | EXT | R | utility, goal, activation, threat_cue | loss_aversion, availability, affect_heuristic, fourfold_pattern | ACT low / KAH medium |
| PAT-DUAL-01 | willpower_blame | DUAL | P, S | declarative, activation, utility, production_policy | substitution, WYSIATI, affect, System_2_laziness | ACT high / KAH medium |

## 3. Pattern Evidence Entries

### 3.1. PAT-D-01 — `genetic_fallacy`

```yaml
pattern_id: PAT-D-01
pattern_name: genetic_fallacy
ae_definition: "A claim or method is accepted/rejected because of source origin, brand, price, prestige, or social provenance rather than task-relevant evidence."
psr_stage: P

anderson_mechanism:
  actr_component: declarative|activation|goal
  mechanism: |
    A source-origin cue is encoded as a declarative chunk and becomes highly retrievable. The learner then lets the source chunk substitute for task evidence, so the goal buffer is populated by provenance rather than output criteria. In ACT-R terms this is not a faulty production alone but an evidential cue-selection error at retrieval/appraisal time.
  source: "Anderson, Rules of the Mind, Ch.2 Knowledge Representation; Ch.3 Performance; Anderson 2007, Ch.3 Human Associative Memory"
  evidence_quote: "ACT-Q2: “chunk is the basic unit”"
  correspondence: functional-analog
  confidence: medium

kahneman_mechanism:
  bias_or_heuristic: halo effect|affect heuristic|WYSIATI|substitution
  mechanism: |
    The learner substitutes an easier source-quality question for the harder question: does this material, method, or instructor produce the target output for my case? A salient positive or negative source cue creates coherence and suppresses missing evidence.
  source: "Kahneman, Thinking, Fast and Slow, Ch.5 Cognitive Ease; Ch.7 WYSIATI; Ch.9 Answering an Easier Question; Ch.13 Availability, Emotion, and Risk"
  evidence_quote: "KAH-Q2: “What You See Is All There Is”"
  correspondence: partial
  confidence: medium

additional_sources:
  - author: "Tversky & Kahneman"
    claim: "Heuristics can be economical but generate systematic errors under uncertainty."
    source: "Judgment under Uncertainty: Heuristics and Biases"
    year: 1974
  - author: "Cialdini"
    claim: "Authority and social proof cues can change compliance independent of evidential adequacy."
    source: "Influence: Science and Practice"
    year: 2001

ae_v12_recommendation: "Add provenance_evidence_split: separate source_trust from task-fit/output evidence. Corrective production should require one concrete performance criterion before accepting or rejecting a method."
limitations: "ACT-R does not itself define “genetic fallacy” as an epistemic norm violation; the mapping is functional, not isomorphic."
```

### 3.2. PAT-D-02 — `false_dilemma`

```yaml
pattern_id: PAT-D-02
pattern_name: false_dilemma
ae_definition: "The learner collapses a multi-option strategy space into two alternatives, usually perfect execution versus total failure or one method versus no method."
psr_stage: S

anderson_mechanism:
  actr_component: production|goal|conflict_resolution
  mechanism: |
    The goal state activates only a narrow production set, so alternative operators never enter conflict resolution. A false dilemma is therefore a search-space and production-candidate collapse, not merely a verbal fallacy. Corrective work should expand candidate productions before choosing among them.
  source: "Anderson, The Architecture of Cognition, Ch.1 Production Systems; Ch.4 Control of Cognition; Rules of the Mind, Ch.3 Performance"
  evidence_quote: "ACT-Q1: “production rules”"
  correspondence: functional-analog
  confidence: high

kahneman_mechanism:
  bias_or_heuristic: framing|WYSIATI|substitution
  mechanism: |
    The available frame defines the whole apparent option set. System 1 treats the represented alternatives as exhaustive, while System 2 often fails to ask what option is absent.
  source: "Thinking, Fast and Slow, Ch.7 A Machine for Jumping to Conclusions; Ch.9 Answering an Easier Question; Ch.34 Frames and Reality"
  evidence_quote: "KAH-Q2"
  correspondence: partial
  confidence: medium

additional_sources:
  - author: "Kruglanski"
    claim: "Need for closure can narrow search and freeze on an available answer."
    source: "The Psychology of Closed Mindedness"
    year: 2004
  - author: "McDonald et al."
    claim: "Framing effects remain significant after publication-bias correction but effect size may be attenuated."
    source: "Valence framing effects on moral judgments: A meta-analysis"
    year: 2021

ae_v12_recommendation: "Implement option_topology_expand: every S-stage binary claim must generate at least three strategy branches plus one minimal reversible experiment."
limitations: "False dilemma is a logical form; ACT-R mapping requires inferring omitted productions, which may be unavailable from surface text alone."
```

### 3.3. PAT-D-03 — `appeal_to_authority`

```yaml
pattern_id: PAT-D-03
pattern_name: appeal_to_authority
ae_definition: "Authority endorsement is treated as sufficient evidence for a learning diagnosis, method, or strategy without checking task fit and output evidence."
psr_stage: P, S

anderson_mechanism:
  actr_component: declarative|utility|production
  mechanism: |
    Authority information can be a useful declarative cue because it lowers search cost. The distortion occurs when the authority cue receives too much activation/utility and bypasses evidence collection or task-specific production testing.
  source: "Rules of the Mind, Ch.2 Knowledge Representation; Ch.3 Production Evaluation; Anderson 1991 Rational Analysis"
  evidence_quote: "direct quote omitted under quote-limit policy; consult the cited source locator"
  correspondence: partial
  confidence: medium

kahneman_mechanism:
  bias_or_heuristic: halo effect|substitution|availability
  mechanism: |
    The learner replaces “is this claim valid for this task?” with “is the speaker credible/famous?” Halo and ease of retrieval create unjustified coherence.
  source: "Thinking, Fast and Slow, Ch.5 Cognitive Ease; Ch.9 Answering an Easier Question; Ch.20 Illusion of Validity"
  evidence_quote: "direct quote omitted under quote-limit policy; consult the cited source locator"
  correspondence: partial
  confidence: medium

additional_sources:
  - author: "Chaiken & Maheswaran"
    claim: "Source cues can dominate under heuristic processing or low elaboration."
    source: "Heuristic processing can bias systematic processing"
    year: 1994
  - author: "Petty & Cacioppo"
    claim: "Peripheral cues influence persuasion when central evaluation is weak."
    source: "Communication and Persuasion: Central and Peripheral Routes"
    year: 1986

ae_v12_recommendation: "Authority claims should create a source_reliability prior, not a verdict. Require task-fit, learner-stage fit, and at least one output-based confirmation."
limitations: "Authority can be a rational prior in expert domains; overcorrection would produce anti-expertise bias."
```

### 3.4. PAT-D-04 — `appeal_to_consequences`

```yaml
pattern_id: PAT-D-04
pattern_name: appeal_to_consequences
ae_definition: "The desirability or fearfulness of a projected result is used as evidence that a claim, method, or appraisal is true."
psr_stage: R

anderson_mechanism:
  actr_component: utility|goal|production_selection
  mechanism: |
    Expected outcome value properly belongs to utility selection, not truth evaluation. The distortion contaminates P-stage belief with R-stage reward/threat value, making a production feel compelling because of its consequences rather than its evidence.
  source: "Rules of the Mind, Ch.3 Production Evaluation; Anderson 2007, Ch.4 Adaptive Control of Thought"
  evidence_quote: "ACT-Q3: “expected gain minus cost”"
  correspondence: functional-analog
  confidence: medium

kahneman_mechanism:
  bias_or_heuristic: prospect theory|loss aversion|affect heuristic|framing
  mechanism: |
    Loss/fear and gain/desire change the felt weight of outcomes, and the learner may mistake that affective weight for evidential weight. This is especially strong in high-stakes learning narratives.
  source: "Thinking, Fast and Slow, Ch.13 Availability, Emotion, and Risk; Ch.26 Prospect Theory; Ch.28 Bad Events; Ch.34 Frames and Reality"
  evidence_quote: "KAH-Q4: “loss aversion”"
  correspondence: partial
  confidence: medium

additional_sources:
  - author: "Kahneman & Tversky"
    claim: "Prospect theory models reference-dependent valuation and asymmetric responses to gains/losses."
    source: "Prospect Theory: An Analysis of Decision under Risk"
    year: 1979
  - author: "Walasek et al."
    claim: "Recent meta-analysis estimates smaller average loss-aversion parameters than classic values, with data-quality concerns."
    source: "A meta-analysis of loss aversion in risky contexts"
    year: 2024
  - author: "Yechiam"
    claim: "Re-meta-analysis argues loss aversion is not robust under symmetric unordered gain/loss designs."
    source: "Loss aversion is not robust: A re-meta-analysis"
    year: 2025

ae_v12_recommendation: "Separate truth_check from consequence_check in PSR. R-stage can raise intervention priority, but cannot validate P or S."
limitations: "Kahneman evidence supports valuation distortion more directly than truth-evaluation fallacy; confidence is medium because loss-aversion robustness is condition-dependent."
```

### 3.5. PAT-D-05 — `perfectionist_fallacy`

```yaml
pattern_id: PAT-D-05
pattern_name: perfectionist_fallacy
ae_definition: "Action is delayed or rejected because the plan, understanding, condition, or result is not perfect, even when an imperfect test would be more informative."
psr_stage: S, R

anderson_mechanism:
  actr_component: production|utility|goal_stack
  mechanism: |
    The learner sets an unrealistically high success threshold before firing a practice/output production. Because production compilation requires interpretive use, perfectionism prevents the very practice that would tune the skill.
  source: "Anderson, The Architecture of Cognition, Ch.6 Procedural Learning; Rules of the Mind, Ch.4 Learning; Anderson 2000, Ch.9 Skill Acquisition"
  evidence_quote: "direct quote omitted under quote-limit policy; consult the cited source locator"
  correspondence: functional-analog
  confidence: high

kahneman_mechanism:
  bias_or_heuristic: loss aversion|status quo bias|planning fallacy|narrow framing
  mechanism: |
    Potential error is framed as a loss, while the value of information from a small imperfect action is underweighted. The learner substitutes “is this safe/perfect?” for “what is the next informative action?”
  source: "Thinking, Fast and Slow, Ch.23 Outside View; Ch.24 Optimism; Ch.28 Bad Events; Ch.34 Frames and Reality"
  evidence_quote: "direct quote omitted under quote-limit policy; consult the cited source locator"
  correspondence: functional-analog
  confidence: medium

additional_sources:
  - author: "Flett & Hewitt"
    claim: "Perfectionism can impair performance and adjustment when standards become rigid and evaluative."
    source: "Perfectionism: Theory, Research, and Treatment"
    year: 2002
  - author: "Gollwitzer & Sheeran"
    claim: "Implementation intentions help convert goals into concrete action despite self-regulation barriers."
    source: "Implementation intentions and goal achievement: A meta-analysis"
    year: 2006

ae_v12_recommendation: "Add minimum_viable_output counter-test: require one reversible 20-minute output trial before more planning. Track information gain, not plan completeness."
limitations: "Perfectionism includes affective and personality dimensions outside ACT-R and Kahneman’s central scope; avoid treating it as a stable trait diagnosis."
```

### 3.6. PAT-D-06 — `begging_the_question`

```yaml
pattern_id: PAT-D-06
pattern_name: begging_the_question
ae_definition: "A conclusion about inability, method validity, or necessity is smuggled into the premise and then used to justify itself."
psr_stage: P, S

anderson_mechanism:
  actr_component: production|declarative|goal_loop
  mechanism: |
    A self-confirming declarative chunk repeatedly supplies the premise for the same production, producing a closed loop with no new discriminating evidence. Mechanistically, the issue is not the mere loop but the absence of a corrective production that queries external evidence.
  source: "The Architecture of Cognition, Ch.1 Production Systems; Rules of the Mind, Ch.3 Performance; Anderson 2007, Ch.5 Algebra and goal structures"
  evidence_quote: "ACT-Q4: “goal module”"
  correspondence: functional-analog
  confidence: medium

kahneman_mechanism:
  bias_or_heuristic: WYSIATI|confirmation bias|coherence bias
  mechanism: |
    A coherent story is constructed from the available premise, and absent evidence is ignored. The circularity survives because the story feels explanatory.
  source: "Thinking, Fast and Slow, Ch.7 WYSIATI; Ch.19 Illusion of Understanding; Ch.20 Illusion of Validity"
  evidence_quote: "direct quote omitted under quote-limit policy; consult the cited source locator"
  correspondence: partial
  confidence: medium

additional_sources:
  - author: "Nickerson"
    claim: "Confirmation bias describes selective seeking/weighting of evidence that supports existing beliefs."
    source: "Confirmation Bias: A Ubiquitous Phenomenon in Many Guises"
    year: 1998
  - author: "Baron"
    claim: "Actively open-minded thinking requires search for alternatives and disconfirming evidence."
    source: "Thinking and Deciding"
    year: 2008

ae_v12_recommendation: "Require premise_conclusion_split: rewrite the claim as P, S, R and mark any identical content in P and conclusion. Then require an independent observable test."
limitations: "Surface circularity detection is brittle; some legitimate definitions may look circular without domain context."
```

### 3.7. PAT-I-01 — `hasty_generalization`

```yaml
pattern_id: PAT-I-01
pattern_name: hasty_generalization
ae_definition: "A small number of failures, successes, or salient episodes is generalized into a broad self-assessment, rule, or identity claim."
psr_stage: P

anderson_mechanism:
  actr_component: base_level_learning|activation|declarative
  mechanism: |
    Recent or repeated episodes acquire high base-level activation and dominate retrieval. The learner treats activation-weighted memory availability as population evidence, failing to model sample size, variance, and context diversity.
  source: "Rules of the Mind, Ch.4 Learning/Base-level Activation; Anderson 1991 Rational Analysis; Anderson 2007, Ch.3 Human Associative Memory"
  evidence_quote: "direct quote omitted under quote-limit policy; consult the cited source locator"
  correspondence: partial
  confidence: high

kahneman_mechanism:
  bias_or_heuristic: law_of_small_numbers|representativeness|base_rate_neglect
  mechanism: |
    Small samples are expected to resemble the larger population more than they do. A salient pattern from a few cases becomes a general rule about ability, personality, or method.
  source: "Thinking, Fast and Slow, Ch.10 Law of Small Numbers; Ch.14 Tom W; Ch.16 Causes Trump Statistics"
  evidence_quote: "direct quote omitted under quote-limit policy; consult the cited source locator"
  correspondence: isomorphism
  confidence: high

additional_sources:
  - author: "Tversky & Kahneman"
    claim: "People often believe small samples should closely resemble the population."
    source: "Belief in the Law of Small Numbers"
    year: 1971
  - author: "Mayiwar et al."
    claim: "Pre-registered replication of nine Kahneman & Tversky representativeness problems replicated eight."
    source: "Revisiting representativeness heuristic classic paradigms"
    year: 2025

ae_v12_recommendation: "Add sample_size_gate: identity-level claims require minimum N, context variety, and counterexamples. Otherwise output provisional local appraisal only."
limitations: "Some small samples are diagnostic when prior base rates or task constraints are strong; the gate must allow high-diagnosticity evidence."
```

### 3.8. PAT-I-02 — `anecdotal_evidence`

```yaml
pattern_id: PAT-I-02
pattern_name: anecdotal_evidence
ae_definition: "A vivid single case, friend story, influencer case, or personal episode is treated as sufficient evidence for a general method or prediction."
psr_stage: P

anderson_mechanism:
  actr_component: declarative|analogy|activation
  mechanism: |
    Anecdotes function like retrieved exemplars or analogs. ACT-R analogy can support transfer when structural conditions match, but the distortion occurs when surface similarity and retrieval ease substitute for structural mapping.
  source: "Rules of the Mind, Ch.4 Learning from Examples and Analogy; Anderson 2000, Ch.10 Inductive Learning"
  evidence_quote: "direct quote omitted under quote-limit policy; consult the cited source locator"
  correspondence: functional-analog
  confidence: high

kahneman_mechanism:
  bias_or_heuristic: availability|representativeness|WYSIATI
  mechanism: |
    A vivid story is easy to retrieve and becomes the visible evidence set. The learner then ignores missing base rates and hidden selection mechanisms.
  source: "Thinking, Fast and Slow, Ch.12 Science of Availability; Ch.14 Representativeness; Ch.16 Causes Trump Statistics"
  evidence_quote: "direct quote omitted under quote-limit policy; consult the cited source locator"
  correspondence: partial
  confidence: high

additional_sources:
  - author: "Tversky & Kahneman"
    claim: "Availability of instances/scenarios affects judgments of frequency and probability."
    source: "Availability: A heuristic for judging frequency and probability"
    year: 1973
  - author: "Nisbett & Ross"
    claim: "Vivid individuating information can dominate statistical evidence in everyday judgment."
    source: "Human Inference"
    year: 1980

ae_v12_recommendation: "Add analogy_validity_check: identify source case, target case, shared structure, differing preconditions, and missing denominator."
limitations: "Anecdotes are not always invalid; they can generate hypotheses. The registry should classify them as weak evidence unless structurally checked."
```

### 3.9. PAT-I-03 — `prediction_fallacy`

```yaml
pattern_id: PAT-I-03
pattern_name: prediction_fallacy
ae_definition: "The learner projects future performance or failure with unjustified certainty from current feeling, recent outcomes, or an untested narrative."
psr_stage: R

anderson_mechanism:
  actr_component: activation|utility_prediction|rational_analysis
  mechanism: |
    Recent outcome chunks and current goal costs bias expected performance. ACT-R-like utility estimates are useful only if grounded in success probability and cost; the distortion is treating current activation/emotion as calibrated forecast.
  source: "Rules of the Mind, Ch.3 Production Evaluation; Anderson 1991 Rational Analysis; Anderson 2000, Ch.7 Retention and Ch.8 Retrieval"
  evidence_quote: "direct quote omitted under quote-limit policy; consult the cited source locator"
  correspondence: partial
  confidence: medium

kahneman_mechanism:
  bias_or_heuristic: intuitive_prediction|regression_neglect|availability|affect_heuristic
  mechanism: |
    System 1 produces a vivid future scenario and neglects uncertainty, base rates, and regression to the mean. The prediction often matches emotional intensity rather than statistical evidence.
  source: "Thinking, Fast and Slow, Ch.17 Regression to the Mean; Ch.18 Taming Intuitive Predictions; Ch.24 Optimism"
  evidence_quote: "direct quote omitted under quote-limit policy; consult the cited source locator"
  correspondence: partial
  confidence: high

additional_sources:
  - author: "Kahneman & Tversky"
    claim: "Intuitive predictions are often insufficiently regressive and overconfident."
    source: "On the Psychology of Prediction"
    year: 1973
  - author: "Griffin & Tversky"
    claim: "Confidence often reflects strength of evidence more than weight of evidence."
    source: "The weighing of evidence and the determinants of confidence"
    year: 1992

ae_v12_recommendation: "Use predict_then_test: require numeric prediction, evidence basis, confidence interval, and post-test calibration update."
limitations: "Some predictions can be legitimate expert forecasts under stable task environments; avoid overcorrecting all confidence."
```

### 3.10. PAT-I-04 — `sunk_cost`

```yaml
pattern_id: PAT-I-04
pattern_name: sunk_cost
ae_definition: "Past investment of time, money, effort, identity, or credential cost is used as a reason to continue a strategy whose future expected value is weak."
psr_stage: S

anderson_mechanism:
  actr_component: utility|production_strength|goal
  mechanism: |
    ACT-R utility should select productions by expected future gain minus cost. Sunk cost distortion occurs when past effort strengthens or emotionally tags the continue-production even when future utility is low.
  source: "Rules of the Mind, Ch.3 Production Evaluation; Ch.4 Production Rule Success and Cost"
  evidence_quote: "ACT-Q3"
  correspondence: functional-analog
  confidence: high

kahneman_mechanism:
  bias_or_heuristic: loss_aversion|mental_accounting|endowment_effect|narrow_framing
  mechanism: |
    Abandoning the course/method is framed as realizing a loss. Mental accounting keeps past investment active and makes switching feel like waste rather than future optimization.
  source: "Thinking, Fast and Slow, Ch.27 Endowment Effect; Ch.28 Bad Events; Ch.32 Keeping Score; Ch.34 Frames and Reality"
  evidence_quote: "KAH-Q4"
  correspondence: partial
  confidence: medium

additional_sources:
  - author: "Arkes & Blumer"
    claim: "People often continue endeavors because of prior investments rather than future returns."
    source: "The psychology of sunk cost"
    year: 1985
  - author: "Yechiam"
    claim: "Recent re-meta-analysis cautions that strong loss aversion may depend on design moderators."
    source: "Loss aversion is not robust"
    year: 2025

ae_v12_recommendation: "Add future_only_utility worksheet: ignore already-spent cost and compare next 2-week expected output across continue/switch/pause."
limitations: "Past cost can carry information about commitment, constraints, or credential lock-in; it should be excluded from utility only when unrecoverable and non-informative."
```

### 3.11. PAT-I-05 — `composition_fallacy`

```yaml
pattern_id: PAT-I-05
pattern_name: composition_fallacy
ae_definition: "Progress in parts, pages, chapters, hours, or micro-skills is assumed to guarantee whole-task mastery or real-world transfer."
psr_stage: R

anderson_mechanism:
  actr_component: chunk_hierarchy|production_transfer|goal_structure
  mechanism: |
    ACT-R supports hierarchical chunks and production transfer, but transfer depends on overlapping productions and usable declarative structure. Part mastery does not automatically compile or coordinate the whole production system.
  source: "Rules of the Mind, Ch.2 Chunk Hierarchies; Ch.9 Identical Elements Theory of Transfer; Ch.10 Programming Transfer"
  evidence_quote: "direct quote omitted under quote-limit policy; consult the cited source locator"
  correspondence: partial
  confidence: high

kahneman_mechanism:
  bias_or_heuristic: substitution|WYSIATI|inside_view|planning_fallacy
  mechanism: |
    The learner substitutes visible component completion for the harder question of integrated performance. The inside view hides coordination costs, transfer demands, and missing whole-task feedback.
  source: "Thinking, Fast and Slow, Ch.9 Substitution; Ch.23 Outside View; Ch.24 Optimism; Ch.34 Frames and Reality"
  evidence_quote: "KAH-Q2"
  correspondence: functional-analog
  confidence: medium

additional_sources:
  - author: "Thorndike & Woodworth"
    claim: "Transfer depends on shared elements rather than general improvement alone."
    source: "The influence of improvement in one mental function upon the efficiency of other functions"
    year: 1901
  - author: "Barnett & Ceci"
    claim: "Transfer varies by content, context, modality, and functional distance."
    source: "When and where do we apply what we learn?"
    year: 2002

ae_v12_recommendation: "Add whole_task_probe after part completion: one integrated output, one transfer item, and one feedback source before marking mastery."
limitations: "Some part-whole relations are compositional by design; the registry should distinguish additive tasks from integrative tasks."
```

### 3.12. PAT-I-06 — `fluency_illusion`

```yaml
pattern_id: PAT-I-06
pattern_name: fluency_illusion
ae_definition: "Smooth reading, listening, following, or recognition is mistaken for understanding, retrieval ability, or transfer-ready competence."
psr_stage: P

anderson_mechanism:
  actr_component: activation|declarative|production_compilation
  mechanism: |
    High activation and processing fluency make a chunk easy to access, but production competence requires retrieval without cues and interpretive use. The distortion misreads accessibility as procedural readiness.
  source: "Rules of the Mind, Ch.3 Data Activation; Ch.4 Learning; Anderson 2000, Ch.8 Retrieval and Ch.9 Skill Acquisition"
  evidence_quote: "direct quote omitted under quote-limit policy; consult the cited source locator"
  correspondence: partial
  confidence: high

kahneman_mechanism:
  bias_or_heuristic: cognitive_ease|illusion_of_truth|WYSIATI
  mechanism: |
    Cognitive ease produces familiarity, reduced vigilance, and a feeling that the material is true or understood. The learner’s System 2 accepts the fluent impression unless an output test interrupts it.
  source: "Thinking, Fast and Slow, Ch.5 Cognitive Ease; Ch.7 WYSIATI; Ch.8 Basic Assessments"
  evidence_quote: "KAH-Q1: “System 1 operates automatically”"
  correspondence: partial
  confidence: high

additional_sources:
  - author: "Koriat"
    claim: "Judgments of learning depend on cues that may not be diagnostic of later performance."
    source: "Monitoring one’s own knowledge during study"
    year: 1997
  - author: "Koriat & Bjork"
    claim: "Learners can overestimate future recall when study cues differ from test cues."
    source: "Illusions of competence in monitoring one’s knowledge during study"
    year: 2005
  - author: "Bjork, Dunlosky & Kornell"
    claim: "Retrieval practice and desirable difficulties improve calibration and durable learning."
    source: "Self-regulated learning: Beliefs, techniques, and illusions"
    year: 2013

ae_v12_recommendation: "Make retrieval_test mandatory for confirmation. Runtime should distinguish follow/recognize/explain/use layers and update confidence only from output."
limitations: "Fluency can correlate with expertise in familiar domains; distortion requires absent or failed retrieval/output evidence."
```

### 3.13. PAT-I-07 — `effort_heuristic`

```yaml
pattern_id: PAT-I-07
pattern_name: effort_heuristic
ae_definition: "Amount of time, strain, or sincerity of effort is treated as direct evidence of learning, strategy quality, or future success."
psr_stage: P, S

anderson_mechanism:
  actr_component: practice|production_strength|utility
  mechanism: |
    Practice strengthens what is actually practiced, not whatever the learner intended to improve. Effort becomes misleading when it repeatedly fires passive, avoidance, or wrong productions while output evidence remains weak.
  source: "Anderson & Corbett, LISP Tutor work in Foundations of Knowledge Acquisition; Rules of the Mind, Ch.4 Learning; Anderson 2000, Ch.9 Skill Acquisition"
  evidence_quote: "direct quote omitted under quote-limit policy; consult the cited source locator"
  correspondence: partial
  confidence: high

kahneman_mechanism:
  bias_or_heuristic: substitution|effort_heuristic|sunk_cost_affect
  mechanism: |
    The learner answers the hard question “did my capability change?” with the easier question “did I work hard?” Effort has moral and affective salience but is not the same as output.
  source: "Thinking, Fast and Slow, Ch.2 Attention and Effort; Ch.9 Answering an Easier Question; Ch.32 Keeping Score"
  evidence_quote: "direct quote omitted under quote-limit policy; consult the cited source locator"
  correspondence: functional-analog
  confidence: medium

additional_sources:
  - author: "Kruger, Wirtz, Van Boven & Altermatt"
    claim: "People use effort as a cue to quality/value, sometimes independent of objective quality."
    source: "The effort heuristic"
    year: 2004
  - author: "Ericsson, Krampe & Tesch-Römer"
    claim: "Improvement requires structured deliberate practice, feedback, and task-specific challenge, not effort quantity alone."
    source: "The role of deliberate practice in the acquisition of expert performance"
    year: 1993

ae_v12_recommendation: "Separate effort_log from output_evidence. Add practiced_production audit: what exact action was repeated, with what feedback, and what changed?"
limitations: "Effort remains a real input and can be diagnostically useful; the error is equating it with competence or causal sufficiency."
```

### 3.14. PAT-I-08 — `recognition_retrieval_confusion`

```yaml
pattern_id: PAT-I-08
pattern_name: recognition_retrieval_confusion
ae_definition: "The learner confuses recognizing material when cued with being able to recall, explain, solve, or use it without cues."
psr_stage: P

anderson_mechanism:
  actr_component: declarative|retrieval|activation|production
  mechanism: |
    Recognition can occur with strong cues and familiarity, while recall/use requires successful chunk retrieval and often production firing. The distortion collapses cue-supported recognition into independent retrieval competence.
  source: "Anderson 2000, Ch.8 Retrieval of Memories; Rules of the Mind, Ch.3 Performance; Ch.4 Learning"
  evidence_quote: "direct quote omitted under quote-limit policy; consult the cited source locator"
  correspondence: partial
  confidence: high

kahneman_mechanism:
  bias_or_heuristic: cognitive_ease|WYSIATI|substitution
  mechanism: |
    Familiarity feels like knowing. System 1 supplies a positive knowing signal, and absent cue-removal evidence is ignored.
  source: "Thinking, Fast and Slow, Ch.5 Cognitive Ease; Ch.7 WYSIATI; Ch.8 Basic Assessments"
  evidence_quote: "direct quote omitted under quote-limit policy; consult the cited source locator"
  correspondence: partial
  confidence: high

additional_sources:
  - author: "Tulving"
    claim: "Recognition and recall are distinct retrieval situations with different cues and demands."
    source: "Elements of Episodic Memory"
    year: 1983
  - author: "Karpicke & Roediger"
    claim: "Retrieval practice improves long-term retention more than additional study."
    source: "The critical importance of retrieval for learning"
    year: 2008

ae_v12_recommendation: "Add cue_removal_gate: every “I know this” claim must specify recognition, cued recall, free recall, explanation, or transfer level."
limitations: "Recognition may be sufficient for some real tasks; classification must depend on target performance criterion."
```

### 3.15. PAT-A-01 — `confusing_explanation_excuse`

```yaml
pattern_id: PAT-A-01
pattern_name: confusing_explanation_excuse
ae_definition: "A causal explanation is mistaken for a justification, or a legitimate constraint is dismissed as mere excuse, preventing accurate structural diagnosis."
psr_stage: P, S

anderson_mechanism:
  actr_component: causal_chunk|goal|production_policy
  mechanism: |
    Causal chunks guide strategy selection, but ACT-R does not itself distinguish explanatory adequacy from moral responsibility. The distortion lies in routing causal analysis into blame/permission productions rather than repair productions.
  source: "Anderson 1991 Rational Analysis: causal inference; Anderson 2000, Ch.10 Inductive Learning/Causal Inference; Rules of the Mind, Ch.3 Performance"
  evidence_quote: "direct quote omitted under quote-limit policy; consult the cited source locator"
  correspondence: functional-analog
  confidence: medium

kahneman_mechanism:
  bias_or_heuristic: causal_story|substitution|hindsight_bias
  mechanism: |
    System 1 prefers coherent causal stories. Once a story explains the outcome, the learner may substitute social/moral evaluation for structural intervention analysis.
  source: "Thinking, Fast and Slow, Ch.6 Norms, Surprises, and Causes; Ch.19 Illusion of Understanding; Ch.20 Hindsight/Outcome Bias"
  evidence_quote: "direct quote omitted under quote-limit policy; consult the cited source locator"
  correspondence: partial
  confidence: medium

additional_sources:
  - author: "Weiner"
    claim: "Attributions vary by locus, stability, and controllability, shaping emotion and future action."
    source: "An attributional theory of achievement motivation and emotion"
    year: 1985
  - author: "Heider"
    claim: "People organize social events through causal attribution."
    source: "The Psychology of Interpersonal Relations"
    year: 1958

ae_v12_recommendation: "Add explanation_vs_permission split: explanation identifies causal levers; excuse/justification concerns responsibility. Intervention should ask what changes next, not who is morally at fault."
limitations: "Boundary is socially and ethically sensitive; automated labeling should avoid accusing the learner of excuse-making."
```

### 3.16. PAT-A-02 — `oversimplified_cause`

```yaml
pattern_id: PAT-A-02
pattern_name: oversimplified_cause
ae_definition: "A multi-factor learning failure is reduced to a single cause such as laziness, talent, method, time, AI, teacher, or textbook."
psr_stage: P, S

anderson_mechanism:
  actr_component: declarative|activation|utility|production_selection
  mechanism: |
    The most available causal chunk wins retrieval and drives a simple production. Because the one-cause explanation lowers cognitive cost, it can gain high utility even when it is structurally incomplete.
  source: "Anderson 1991 Rational Analysis: causal inference; Rules of the Mind, Ch.3 Production Evaluation; Anderson 2000, Ch.10 Causal Inference"
  evidence_quote: "ACT-Q3"
  correspondence: partial
  confidence: high

kahneman_mechanism:
  bias_or_heuristic: associative_coherence|WYSIATI|substitution|causal_bias
  mechanism: |
    System 1 quickly imposes causal coherence and ignores absent variables. The learner answers “what is the whole causal structure?” with “what cause comes most easily?”
  source: "Thinking, Fast and Slow, Ch.4 Associative Machine; Ch.6 Causes; Ch.7 WYSIATI; Ch.16 Causes Trump Statistics"
  evidence_quote: "KAH-Q2"
  correspondence: partial
  confidence: high

additional_sources:
  - author: "Kelley"
    claim: "Causal attribution should compare consensus, distinctiveness, and consistency rather than rely on one cue."
    source: "Attribution theory in social psychology"
    year: 1967
  - author: "Pearl"
    claim: "Causal claims require structure over variables, interventions, and counterfactuals."
    source: "Causality"
    year: 2000

ae_v12_recommendation: "Require causal_graph_min5: task clarity, stage fit, method, time-energy, feedback/return path. One-cause claims are provisional until alternatives are tested."
limitations: "Sometimes a bottleneck cause dominates; the aim is not to forbid single causes but to prevent premature causal closure."
```

### 3.17. PAT-A-03 — `self_serving_attribution`

```yaml
pattern_id: PAT-A-03
pattern_name: self_serving_attribution
ae_definition: "Success is attributed to stable internal virtue while failure is attributed to external circumstance, or the reverse when self-blame preserves identity in a familiar way."
psr_stage: P, S

anderson_mechanism:
  actr_component: declarative|utility|goal
  mechanism: |
    Attribution chunks that protect self-concept may be more available and have higher affective utility than structurally diagnostic chunks. ACT-R can model retrieval and utility competition, but not the social meaning of self-protection by itself.
  source: "Rules of the Mind, Ch.3 Performance/Utility; Anderson 2007, Ch.6 architecture and human cognition"
  evidence_quote: "direct quote omitted under quote-limit policy; consult the cited source locator"
  correspondence: functional-analog
  confidence: medium

kahneman_mechanism:
  bias_or_heuristic: overconfidence|illusion_of_validity|substitution
  mechanism: |
    The learner’s causal story preserves a favorable self-model and may overestimate the validity of a preferred explanation. TFS supports overconfidence and story-coherence mechanisms, though not self-serving attribution as a primary named heuristic.
  source: "Thinking, Fast and Slow, Ch.19 Illusion of Understanding; Ch.20 Illusion of Validity; Ch.24 Optimism"
  evidence_quote: "direct quote omitted under quote-limit policy; consult the cited source locator"
  correspondence: functional-analog
  confidence: medium

additional_sources:
  - author: "Miller & Ross"
    claim: "Self-serving attribution explains asymmetric explanations of success and failure."
    source: "Self-serving biases in the attribution of causality"
    year: 1975
  - author: "Weiner"
    claim: "Achievement attributions shape expectancy, emotion, and persistence."
    source: "An attributional theory of achievement motivation and emotion"
    year: 1985

ae_v12_recommendation: "Add attribution_balance check: for each success/failure, list internal/external, stable/unstable, controllable/uncontrollable causes and one testable structural lever."
limitations: "Attribution asymmetry may be adaptive for motivation in some contexts; do not treat every self-protective explanation as distortion."
```

### 3.18. PAT-A-04 — `identity_protective_reasoning`

```yaml
pattern_id: PAT-A-04
pattern_name: identity_protective_reasoning
ae_definition: "Evidence about learning performance is filtered to protect an identity claim such as diligent person, smart person, practical person, independent learner, or victim of unfair systems."
psr_stage: P

anderson_mechanism:
  actr_component: goal|declarative|utility|metacognitive_extension
  mechanism: |
    Identity claims can function as high-priority goal/context chunks that bias retrieval and production selection. ACT-R gives mechanisms for goal-buffer control and retrieval, but identity defense is an AE-level social/metacognitive extension.
  source: "Anderson 2007, Ch.2 Modular Organization/goal module; Anderson & Fincham (2014) metacognitive extension (citation-to-claim mapping: pending verification); Rules of the Mind, Ch.3"
  evidence_quote: "ACT-Q4"
  correspondence: partial
  confidence: low

kahneman_mechanism:
  bias_or_heuristic: confirmation|coherence|WYSIATI|System_2_laziness
  mechanism: |
    System 1 builds a coherent self-story; System 2 may endorse it unless motivated to search for disconfirming evidence. Kahneman supports the cognitive pathway, but identity-protection itself requires additional social-cognition literature.
  source: "Thinking, Fast and Slow, Ch.3 Lazy Controller; Ch.7 WYSIATI; Ch.19 Illusion of Understanding"
  evidence_quote: "direct quote omitted under quote-limit policy; consult the cited source locator"
  correspondence: functional-analog
  confidence: medium

additional_sources:
  - author: "Kahan"
    claim: "Identity-protective cognition makes people process evidence in ways that protect group or self-defining commitments."
    source: "Ideology, motivated reasoning, and cognitive reflection"
    year: 2013
  - author: "Kunda"
    claim: "Motivated reasoning can bias the search for and evaluation of evidence while preserving an impression of objectivity."
    source: "The case for motivated reasoning"
    year: 1990

ae_v12_recommendation: "Add identity_safe_reframe: protect dignity while detaching evidence from identity. Use “this output under these conditions” rather than “you are X”."
limitations: "Direct ACT-R is weak; this pattern requires social identity and motivated reasoning sources beyond Anderson/Kahneman."
```

### 3.19. PAT-A-05 — `post_hoc_rationalization`

```yaml
pattern_id: PAT-A-05
pattern_name: post_hoc_rationalization
ae_definition: "After choosing or failing, the learner constructs a plausible reason that protects the decision rather than reconstructing the actual cause or updating the strategy."
psr_stage: cycle

anderson_mechanism:
  actr_component: procedural_trace|declarative_reconstruction|verbal_report
  mechanism: |
    ACT-R can model production traces, but human verbal explanations may reconstruct rather than reveal the true production path. The distortion occurs when a post-action declarative narrative is treated as causal evidence.
  source: "Rules of the Mind, Ch.12 Creating Production-Rule Models/Verbal Protocols [structure summary]; Anderson 2007, Ch.6 consciousness/report; Architecture of Cognition, Ch.4 Control"
  evidence_quote: "direct quote omitted under quote-limit policy; consult the cited source locator"
  correspondence: partial
  confidence: medium

kahneman_mechanism:
  bias_or_heuristic: hindsight_bias|outcome_bias|illusion_of_understanding
  mechanism: |
    After the outcome is known, the story of why it happened becomes more coherent and obvious than it was. This can prevent genuine PSR revision.
  source: "Thinking, Fast and Slow, Ch.19 Illusion of Understanding; Ch.20 Illusion of Validity; Ch.21 Intuitions vs Formulas"
  evidence_quote: "direct quote omitted under quote-limit policy; consult the cited source locator"
  correspondence: partial
  confidence: high

additional_sources:
  - author: "Nisbett & Wilson"
    claim: "People often lack direct introspective access to the causes of their choices and may confabulate explanations."
    source: "Telling more than we can know"
    year: 1977
  - author: "Festinger"
    claim: "Dissonance reduction can produce post-choice rationalization."
    source: "A Theory of Cognitive Dissonance"
    year: 1957

ae_v12_recommendation: "Require precommitment trace: prediction, planned reason, and decision rule must be logged before action; post-hoc reasons are marked as hypotheses only."
limitations: "Post-hoc reflection can be useful if explicitly treated as hypothesis generation; distortion occurs when it is treated as verified cause."
```

### 3.20. PAT-EXT-01 — `social_comparison`

```yaml
pattern_id: PAT-EXT-01
pattern_name: social_comparison
ae_definition: "Progress, worth, or strategy quality is judged primarily by comparison with peers, rankings, cohorts, or online exemplars rather than personal task evidence."
psr_stage: P, R

anderson_mechanism:
  actr_component: declarative|goal|utility|external_cue
  mechanism: |
    Social cues become salient declarative inputs and can shift utility toward status maintenance rather than skill acquisition. ACT-R can represent cue-driven goals but does not natively model social comparison norms.
  source: "Anderson 2007, Ch.1 architecture as structure-function relation; Rules of the Mind, Ch.3 utility; AE architecture Axis 3 for social dynamics"
  evidence_quote: "direct quote omitted under quote-limit policy; consult the cited source locator"
  correspondence: functional-analog
  confidence: low

kahneman_mechanism:
  bias_or_heuristic: anchoring|availability|reference_points|focusing_illusion
  mechanism: |
    Peer outcomes become anchors and reference points. The learner over-focuses on visible comparison data while ignoring hidden denominators, different constraints, and personal target function.
  source: "Thinking, Fast and Slow, Ch.11 Anchors; Ch.12 Availability; Ch.26 Prospect Theory/reference points; Ch.38 Focusing Illusion"
  evidence_quote: "direct quote omitted under quote-limit policy; consult the cited source locator"
  correspondence: partial
  confidence: medium

additional_sources:
  - author: "Festinger"
    claim: "People evaluate abilities and opinions through comparison with others when objective standards are absent."
    source: "A theory of social comparison processes"
    year: 1954
  - author: "Dijkstra et al."
    claim: "Social comparison in classrooms can affect motivation, self-concept, and learning behavior."
    source: "Social comparison in the classroom: A review"
    year: 2008

ae_v12_recommendation: "Add comparison_denominator check: compare only when cohort constraints, starting point, target, and evidence metric are comparable; otherwise convert to personal output benchmark."
limitations: "Social comparison can calibrate standards and motivate; distortion depends on unexamined comparability and identity threat."
```

### 3.21. PAT-EXT-02 — `catastrophizing`

```yaml
pattern_id: PAT-EXT-02
pattern_name: catastrophizing
ae_definition: "A setback, delay, mistake, or exam failure is projected into an extreme future loss disproportionate to the evidence and available remedies."
psr_stage: R

anderson_mechanism:
  actr_component: utility|goal|activation|threat_cue
  mechanism: |
    Threat-related chunks can dominate retrieval and make avoidance productions appear high-utility because the cost of imagined failure is enormous. ACT-R has utility mechanisms but limited native affect/threat modeling, so this is an extension-level mapping.
  source: "Rules of the Mind, Ch.3 utility; Anderson 2000, Ch.7 retention of emotionally charged material; AE Axis2 R-stage variables"
  evidence_quote: "ACT-Q3"
  correspondence: functional-analog
  confidence: low

kahneman_mechanism:
  bias_or_heuristic: loss_aversion|availability|affect_heuristic|fourfold_pattern
  mechanism: |
    Vivid bad outcomes are easy to imagine, emotionally weighted, and can be overweighted relative to probability and remedy efficacy. Recent loss-aversion evidence suggests caution about treating this as a universal mechanism.
  source: "Thinking, Fast and Slow, Ch.13 Availability and Emotion; Ch.28 Bad Events; Ch.29 Fourfold Pattern; Ch.30 Rare Events"
  evidence_quote: "KAH-Q4"
  correspondence: partial
  confidence: medium

additional_sources:
  - author: "Witte"
    claim: "Threat messages depend on perceived severity, susceptibility, response efficacy, and self-efficacy."
    source: "Putting the fear back into fear appeals: EPPM"
    year: 1992
  - author: "Beck"
    claim: "Catastrophic misinterpretation is a common cognitive distortion in anxiety."
    source: "Cognitive therapy and the emotional disorders"
    year: 1976
  - author: "Yechiam"
    claim: "Loss-aversion strength depends heavily on design features; treat loss-based explanations as conditional."
    source: "Loss aversion is not robust"
    year: 2025

ae_v12_recommendation: "Add threat_calibration: estimate probability, magnitude, reversibility, time horizon, remedy efficacy, and smallest next action."
limitations: "High-stakes consequences can be real; intervention must not minimize legitimate risk."
```

### 3.22. PAT-DUAL-01 — `willpower_blame`

```yaml
pattern_id: PAT-DUAL-01
pattern_name: willpower_blame
ae_definition: "Learning failure is attributed to laziness, weak will, lack of discipline, or moral defect, suppressing structural diagnosis and repair."
psr_stage: P, S

anderson_mechanism:
  actr_component: declarative|activation|utility|production_policy
  mechanism: |
    Failure episodes retrieve identity/self-blame chunks more strongly than structural-cause chunks. The “try harder” production has low cognitive cost and familiar utility, but may strengthen the same ineffective loop. Mechanistically, this is best modeled as oversimplified_cause plus effort_heuristic.
  source: "Rules of the Mind, Ch.3 utility and Ch.4 learning; Anderson 2000, Ch.9 Skill Acquisition; AE_ACTR_Newell v1.2 triad recommendation"
  evidence_quote: "direct quote omitted under quote-limit policy; consult the cited source locator"
  correspondence: partial
  confidence: high

kahneman_mechanism:
  bias_or_heuristic: substitution|WYSIATI|affect|System_2_laziness
  mechanism: |
    The learner substitutes a simple moral/trait story for a multi-variable structure question. Coherent self-blame feels explanatory even when it has low repair value.
  source: "Thinking, Fast and Slow, Ch.3 Lazy Controller; Ch.7 WYSIATI; Ch.9 Substitution; Ch.19 Illusion of Understanding"
  evidence_quote: "direct quote omitted under quote-limit policy; consult the cited source locator"
  correspondence: functional-analog
  confidence: medium

additional_sources:
  - author: "Weiner"
    claim: "Controllability and stability attributions shape shame, guilt, expectancy, and future effort."
    source: "An attributional theory of achievement motivation and emotion"
    year: 1985
  - author: "Dweck"
    claim: "Trait-like ability interpretations can impair adaptive response to difficulty."
    source: "Mindset"
    year: 2006
  - author: "Gollwitzer & Sheeran"
    claim: "Concrete implementation plans outperform vague intention or willpower framing."
    source: "Implementation intentions and goal achievement"
    year: 2006

ae_v12_recommendation: "Keep as dual-use: detect in learner input, forbid in system output unless paired with structural reattribution. Implement compound route A primary + I secondary."
limitations: "Sometimes effort regulation is a real factor; AE must reframe it structurally rather than deny agency."
```


## 4. Low-Confidence and Recheck Items

| item | reason | action |
|---|---|---|
| PAT-A-04 identity_protective_reasoning — ACT-R | ACT-R supports goal/retrieval/utility control, but identity protection is social-cognitive rather than native ACT-R. | Keep ACT-R confidence low; use Kahan/Kunda as primary evidence. |
| PAT-EXT-01 social_comparison — ACT-R | Social comparison requires social/self-evaluation theory beyond ACT-R. | Treat ACT-R as external-cue/utility scaffold only. |
| PAT-EXT-02 catastrophizing — ACT-R | ACT-R has utility and activation but weak native affect/threat modeling. | Use EPPM/CBT/anxiety literature as primary evidence. |
| PAT-D-04 appeal_to_consequences — Kahneman loss route | Loss aversion evidence is condition-dependent in recent meta-analytic work. | Keep confidence medium unless task context clearly matches validated loss/choice paradigms. |
| PAT-I-04 sunk_cost — Kahneman loss route | Sunk cost is robust in many settings, but loss-aversion explanation is not the only mechanism. | Add mental accounting and commitment/escalation sources. |

## 5. ACT ↔ KAH Tension Notes

1. **Mechanism vs. bias vocabulary**
   - ACT-R asks how a production, chunk, activation value, or utility estimate generates behavior.
   - Kahneman asks why intuitive judgment predictably deviates from normative logic/statistics.
   - AE should use ACT-R for mechanistic decomposition and Kahneman for diagnostic warning labels.

2. **Adaptivity vs. normativity**
   - Anderson’s rational analysis often treats cognition as adapted to environmental structure.
   - Kahneman emphasizes systematic error relative to rational/statistical norms.
   - AE must preserve both: many “distortions” are adaptive shortcuts misfiring in modern adult learning environments.

3. **Activation/accessibility vs. truth/evidence**
   - ACT-R activation predicts accessibility and latency, not epistemic justification.
   - Kahneman’s WYSIATI and cognitive ease explain why accessibility becomes overtrusted.
   - AE’s calibration gate should explicitly block “accessible = true/known” conversions.

4. **Utility vs. value/loss framing**
   - ACT-R utility concerns production selection under success probability and cost.
   - Prospect theory concerns subjective value under gains/losses and reference points.
   - AE should not collapse these. Utility belongs mainly to S-stage strategy choice; prospect/loss framing belongs mainly to R-stage projection and threat/desire weighting.

5. **System A/B naming caveat**
   - Kahneman’s System 1/2 are useful fictions, not literal modules.
   - AE System A/B are engineering roles: Coach and Verifier.
   - Therefore pattern evidence must avoid claiming that AE System A = System 1 or AE System B = System 2.

## 6. v1.2 Implementation Recommendations

1. **Preserve legacy labels**
   - Do not replace `primary_leaks: ["fluency_illusion"]` with nested objects in legacy outputs.
   - Add `extensions.mechanistic_triads` only in extended serialization.

2. **Adopt pattern triads**
   - `trigger_condition → distorted_production → corrective_production` should be added as optional overlay.
   - Use triads to improve routing and intervention, not to change legacy taxonomy.

3. **Route by mechanism, not keyword only**
   - Fluency/recognition patterns often lack explicit causal or logical markers; they need I-route hints.
   - Willpower_blame should route A primary + I secondary.

4. **EvidencePacket integration**
   - Each pattern should define required evidence and missing-evidence signals.
   - Low evidence should produce “candidate pattern,” not final verdict.

5. **Counter-test first**
   - Every corrective production should include a behavioral counter-test: retrieval test, output probe, attribution reframe, option expansion, future-only utility, or external feedback.

## 7. Reference Register

### 7.1 Anderson / ACT-R

- Anderson, J. R. (1983). *The Architecture of Cognition*. Harvard University Press.
- Anderson, J. R. (1991). “Is human cognition adaptive?” *Behavioral and Brain Sciences*, 14(3), 471–517. DOI: 10.1017/S0140525X00070801.
- Anderson, J. R. (1993/2014). *Rules of the Mind*. Psychology Press reprint. DOI: 10.4324/9781315806938.
- Anderson, J. R. (2000). *Learning and Memory: An Integrated Approach*. 2nd ed.
- Anderson, J. R. (2007). *How Can the Human Mind Occur in the Physical Universe?* Oxford University Press.
- Anderson, J. R., & Fincham, J. M. (2014). “Extending problem-solving procedures through reflection.” *Cognitive Psychology*, 74, 1–34.
- Lieder, F., & Griffiths, T. L. (2020). “Resource-rational analysis.” *Behavioral and Brain Sciences*, 43, e1.
- Dimov, C. M., Anderson, J. R., & Betts, S. A. (2024). “Tight resource-rational analysis.” *Cognitive Systems Research*, 86.
- Wu, S., Oltramari, A., Francis, J., Giles, C. L., & Ritter, F. E. (2024/2025). LLM-ACTR / Cognitive LLMs papers.
- Wu, S., Oltramari, A., & Ritter, F. E. (2025). “VSM-ACTR 2: a human-like decision making model with metacognition for manufacturing solutions.”

### 7.2 Kahneman / heuristics and biases

- Kahneman, D. (2011). *Thinking, Fast and Slow*. Farrar, Straus and Giroux.
- Tversky, A., & Kahneman, D. (1971). “Belief in the law of small numbers.” *Psychological Bulletin*, 76, 105–110.
- Tversky, A., & Kahneman, D. (1973). “Availability: A heuristic for judging frequency and probability.” *Cognitive Psychology*, 5, 207–232.
- Tversky, A., & Kahneman, D. (1974). “Judgment under uncertainty: Heuristics and biases.” *Science*, 185, 1124–1131.
- Kahneman, D., & Tversky, A. (1979). “Prospect theory: An analysis of decision under risk.” *Econometrica*, 47, 263–291.
- Tversky, A., & Kahneman, D. (1981). “The framing of decisions and the psychology of choice.” *Science*, 211, 453–458.
- Mayiwar, L., Wan, K. H., Løhre, E., & Feldman, G. (2025). “Revisiting representativeness heuristic classic paradigms.” *Quarterly Journal of Experimental Psychology*, 78(4), 707–730.
- McDonald, K. et al. (2021). “Valence framing effects on moral judgments: A meta-analysis.” *Cognition*.
- Stengård, E., Juslin, P., Hahn, U., & van den Berg, R. (2022). “On the generality and cognitive basis of base-rate neglect.” *Cognition*.
- Walasek, L. et al. (2024). “A meta-analysis of loss aversion in risky contexts.” *Journal of Economic Psychology*.
- Yechiam, E. (2025). “Loss aversion is not robust: A re-meta-analysis.”

### 7.3 Learning / metacognition / attribution

- Koriat, A. (1997). “Monitoring one’s own knowledge during study: A cue-utilization approach to judgments of learning.” *Journal of Experimental Psychology: General*.
- Koriat, A., & Bjork, R. A. (2005). “Illusions of competence in monitoring one’s knowledge during study.” *Journal of Experimental Psychology: Learning, Memory, and Cognition*.
- Bjork, R. A., Dunlosky, J., & Kornell, N. (2013). “Self-regulated learning: Beliefs, techniques, and illusions.” *Annual Review of Psychology*.
- Weiner, B. (1985). “An attributional theory of achievement motivation and emotion.” *Psychological Review*.
- Miller, D. T., & Ross, M. (1975). “Self-serving biases in the attribution of causality.” *Psychological Bulletin*.
- Kunda, Z. (1990). “The case for motivated reasoning.” *Psychological Bulletin*.
- Kahan, D. M. (2013). “Ideology, motivated reasoning, and cognitive reflection.” *Judgment and Decision Making*.
- Festinger, L. (1957). *A Theory of Cognitive Dissonance*.
- Festinger, L. (1954). “A theory of social comparison processes.” *Human Relations*.
- Witte, K. (1992). “Putting the fear back into fear appeals: The Extended Parallel Process Model.” *Communication Monographs*.

## 8. Final Status

- Coverage: all canonical pattern registry diagnostic items plus dual-use willpower_blame.
- Strongest evidence clusters: fluency/recognition/retrieval; hasty generalization/representativeness; sunk cost/utility; oversimplified cause/causal attribution.
- Weakest direct ACT-R clusters: identity-protective reasoning, social comparison, catastrophizing.
- v1.2 priority: implement triad overlay for `fluency_illusion`, `effort_heuristic`, `recognition_retrieval_confusion`, `oversimplified_cause`, and `willpower_blame` first.
