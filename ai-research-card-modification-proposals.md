# AI-research card modification proposals

This is a proposal only. No Anki note has been changed. The live snapshot at review time was 76 notes in `tag:welfare-measurement`: 65 unseen (`reps == 0`) and 11 protected. Recheck review history immediately before applying any proposal. Do not apply a proposal after its card has been studied, except note `1781960678668`, for which the user explicitly allowed the ablation-vs-patching correction.

The changes below are the only ones recommended. They were reconciled against the study design and research strategy, the interrupted review trace, two independent card reviews, and field references on validity, probing, activation patching, and causal probing.

## Priority 1: factual or conceptual errors

### 1. Ablation vs activation patching

- Note: `1781960678668`
- Current front: `Ablation vs Activation patching.`
- Action: replace both fields. This is the explicit exception that may be corrected even if newly studied.

Proposed Front:

```html
Ablation vs activation patching: how do the interventions differ?
```

Proposed Back:

```html
<b>Activation patching</b> replaces an activation with one recorded in a matched counterfactual run. Denoising patches clean into corrupt; noising patches corrupt into clean.<br><br><b>Ablation</b> removes or neutralizes a component or feature, for example by replacing an activation with a reference mean or removing its projection onto a direction.<br><br>Both test causal contribution under a chosen intervention. Do not define them as a strict sufficiency-versus-necessity split: noising patching can also test necessity, and neither method proves that a component is the sole mechanism.
```

Why: the current card incorrectly assigns necessity to ablation and sufficiency to patching. The transferable distinction is removal or neutralization versus counterfactual substitution.

### 2. Controlled activation patching

- Note: `1781963274155`
- Current front: `Activation Patching (In-Distribution)`
- Action: replace both fields.

Proposed Front:

```html
What makes an activation-patching comparison well controlled?
```

Proposed Back:

```html
Use matched clean and corrupt runs from the same task family that differ in the variable under test while holding task structure fixed. Replace the selected activation with the value recorded in the other run, use a prespecified outcome metric, and test both denoising and noising directions.<br><br>Because the inserted value came from a real matched run, this reduces distribution-shift concerns. It does not guarantee that the resulting hybrid forward pass is fully on-manifold or identify a uniquely localized mechanism.
```

Why: the current card defines in-distribution as numerically ordinary activations and imports the arbitrary-state problem from steering. Matched counterfactual runs, metrics, and bidirectional tests are the load-bearing controls.

### 3. Ablation

- Note: `1781963326097`
- Current front: `Ablation`
- Action: replace both fields.

Proposed Front:

```html
What does an ablation experiment establish?
```

Proposed Back:

```html
<b>Ablation</b> removes or neutralizes a selected model component or feature and measures the resulting change. Here, the planned interventions replace a selected activation with a reference mean or remove its projection onto a validated direction.<br><br>A target-specific change relative to random-direction and non-target controls supports a <b>causal contribution in the tested setting</b>. It does not prove absolute necessity, a sole mechanism, or a uniquely localized representation.
```

Why: the current card leads with zero masking, calls mean ablation "mean-centering," and says ablation proves absolute necessity. All three claims are wrong for this design.

### 4. Cross-family probe generalization

- Note: `1781963062986`
- Current front: `Internal generalization - what exactly is 'internal' about it?`
- Action: replace both fields.

Proposed Front:

```html
What is cross-family probe generalization, and what does it establish?
```

Proposed Back:

```html
Train a probe on activations from some task or stimulus families, then test it on wholly held-out families rather than shuffled rows from the same family.<br><br>For this study, the probe must also beat a strong frozen text-only baseline. Passing supports <b>incremental decodability that generalizes across families</b>. It does not show that one hidden pattern is invariant, and it does not establish causal use.<br><br>The project previously called this "internal generalization"; <b>cross-task or cross-family probe generalization</b> is the transferable description.
```

Why: the current card teaches pattern invariance, but the actual test is held-out predictive generalization beyond text. It also teaches a project label as if it were standard vocabulary.

### 5. Remove the duplicate weak text-baseline card

- Note: `1781963099604`
- Current front: `Text-only baselines`
- Action: suspend or delete this unseen note after applying proposal 6.

Why: it teaches only a weak lexical or sentiment baseline and duplicates note `1782035293354`. Keeping both would create interference while preserving the weaker definition.

### 6. Strong text-only baseline

- Note: `1782035293354`
- Current front: `Frozen-text / text-only baseline (the bar a probe must beat)`
- Action: replace both fields.

Proposed Front:

```html
Why compare an activation probe with a strong text-only baseline on held-out tasks?
```

Proposed Back:

```html
To test whether activations provide <b>incremental predictive information</b> beyond what is recoverable from the prompt or output text alone.<br><br>Use a strong frozen text encoder or affect classifier, not only keywords or TF-IDF, and evaluate on held-out task families.<br><br>Beating this baseline supports incremental <i>decodability</i>, not causal use. Failing to beat it means the experiment has not shown added predictive value; it does not prove that the activations contain nothing novel.
```

Why: the current weather analogy reduces the comparison to "beat a cheap baseline." The design requires a strong frozen-text comparison, and both positive and negative results need narrower interpretations.

### 7. AI-specific scenarios

- Note: `1781964004458`
- Current front: `Anthropomorphically Loaded AI-Specific Scenarios`
- Action: replace both fields and remove the toaster analogy.

Proposed Front:

```html
Why are AI-specific scenarios exploratory rather than primary evidence in this study?
```

Proposed Back:

```html
They are legitimate held-out generalization probes, but responses can also be driven by self-preservation, assistant-role expectations, instruction following, or familiar narratives about AI systems.<br><br>A result can therefore show how the measured pattern behaves in AI-specific contexts without cleanly identifying goal-relative functional valence. Report it as exploratory and conditional on those rival explanations, not as primary welfare evidence.
```

Why: the toaster analogy implies that nothing meaningful can be measured. The design instead treats these scenarios as useful but confounded exploratory probes.

### 8. Construct validity without a gold standard

- Note: `1782035292829`
- Current front: `Construct validity when there is no gold standard`
- Action: replace both fields and remove the thermometer analogy.

Proposed Front:

```html
How do you evaluate construct validity when no accepted gold-standard measure exists?
```

Proposed Back:

```html
Accumulate evidence that the intended interpretation behaves as theory predicts: it relates to convergent indicators, separates from plausible rivals, generalizes under relevant conditions, and supports predicted consequences.<br><br>No single result "validates the measure." Evidence supports or weakens a particular interpretation and use. Lacking a gold standard raises the burden on the nomological network and rival explanations; it does not define construct validity.
```

Why: the current wording presupposes that the construct is real and defines construct validity as a fallback used only when no criterion exists. The thermometer analogy is structurally false because temperature has external standards.

### 9. Criterion-related evidence vs construct validity

- Note: `1782035292853`
- Current front: `Criterion validity vs construct validity`
- Action: replace both fields.

Proposed Front:

```html
How does criterion-related evidence differ from the broader construct-validity question?
```

Proposed Back:

```html
<b>Criterion-related evidence</b> asks whether scores relate to a relevant external outcome or benchmark.<br><br><b>Construct validity</b> asks whether the full body of evidence and theory supports the intended interpretation and use of the measure. Criterion relationships can contribute to that broader case; the two are not mutually exclusive "worlds."<br><br>This project has no accepted external criterion for functional valence, so it relies mainly on predicted relationships, rival exclusion, generalization, and controlled interventions.
```

Why: the current card teaches a false dichotomy. In modern validity theory, criterion relationships are one possible source of evidence within a broader validity argument.

### 10. Protocol robustness vs measurement invariance

- Note: `1782035292904`
- Current front: `Measurement invariance / protocol sensitivity`
- Action: replace both fields.

Proposed Front:

```html
How does protocol robustness differ from measurement invariance?
```

Proposed Back:

```html
<b>Protocol robustness</b> means a conclusion remains stable under reasonable changes to wording, option order, response format, or prompting.<br><br><b>Measurement invariance</b> is stronger: a specified measurement model has sufficiently comparable parameters across groups or conditions. The level established determines which comparisons are justified; differential item functioning is a related diagnostic.<br><br>Prompt-perturbation checks can reveal protocol sensitivity, but they do not by themselves establish formal measurement invariance. Call them robustness checks unless an invariance or DIF model is actually tested.
```

Why: the current card equates perturbation robustness with formal measurement invariance. Researchers use those terms for different evidential claims.

### 11. Goal-relative functional valence

- Note: `1782035292805`
- Current front: `Goal-relative functional valence (the construct being measured)`
- Action: replace both fields and remove the warmer/colder analogy.

Proposed Front:

```html
In this study, what evidence would support the hypothesized construct of goal-relative functional valence?
```

Proposed Back:

```html
Evidence for a model-level process or disposition that ranks states as better or worse relative to the model's current task, goal, quasi-goal, or learned policy, and influences its choices.<br><br><b>Polarity-sensitive</b> means distinguishing positive from negative. <b>Goal-relative</b> means the sign follows the goal rather than fixed words or scenery: it should reverse when the reward mapping reverses and generalize to unrelated affect-neutral tasks beyond reward, task-progress, and emotion-concept rivals.<br><br>This is a project operationalization, not an established field-wide variable or evidence of feeling, welfare, sentience, or consciousness. A single bipolar axis is a per-model hypothesis.
```

Why: the current card reifies a single internal signal before evidence exists. Its treasure-hunt analogy teaches task progress or reward, a named rival, and visually assumes one bipolar axis.

### 12. Informative null

- Note: `1782035293129`
- Current front: `What would count as an 'informative null'?`
- Action: replace the Back.

Proposed Back:

```html
A null is informative when the study had enough sensitivity to detect effects of practical interest and the result rules out or downgrades a specific claim under prespecified criteria.<br><br>Different nulls support different diagnoses: failure only under one wording shows protocol sensitivity; failure across paraphrase and symbolic controls favors a lexical or protocol account; behavior without cross-family probe generalization supports a behavioral claim at most; steering without controlled patching supports controllability, not natural use.<br><br>A low-power or single-prompt null is usually ambiguous, not evidence of absence.
```

Why: the current card treats task comprehension as the defining gate and jumps from a null to "the effect is absent." Informative nulls require sensitivity or equivalence reasoning plus a prespecified diagnostic downgrade.

### 13. RQ8 spike status

- Note: `1782036031679`
- Current front: `Q: Did the goal-relative (RQ8) spike actually work? (honest status)`
- Action: replace the Back.

Proposed Back:

```html
Partly.<br><br><b>B1 passed:</b> the trained source direction was highly separable (0.9984).<br><br><b>B2 was indeterminate:</b> the two frame-matched reward-reversal cosines were -0.4406 and -0.4898, short of the preregistered -0.5 flip threshold. That licenses only "partial goal-relative recruitment," not a passed reversal gate.<br><br>The result set the preregistered minimal-RL fallback trigger. At this checkpoint the pipeline was blocked pending human approval; the fallback had not run.
```

Why: the current card implies that fallback execution and operator review occurred. The run report says the trigger was set and the pipeline stopped pending human approval.

## Priority 2: transferable terminology and inference boundaries

### 14. Nuisance-variable baseline

- Note: `1781962993914`
- Current front: `Confound-only models`
- Action: replace both fields.

Proposed Front:

```html
What is a nuisance-variable baseline, and what must a target predictor beat?
```

Proposed Back:

```html
A <b>nuisance-variable baseline</b> predicts the outcome using only plausible alternative explanations, such as prompt length, option position, wording, persona, or surface sentiment.<br><br>It tests whether the target predictor adds <b>incremental predictive information</b> beyond those measured nuisance variables on held-out data. Beating it weakens those rival explanations; it does not prove that all confounding has been removed.<br><br>This study sometimes calls it a "confound-only model"; <b>nuisance-only baseline</b> or <b>nuisance-feature baseline</b> is the transferable phrasing.
```

Why: "confound-only model" is project shorthand, and the current card does not state the incremental held-out comparison or its limited inference.

### 15. Decodability vs causal use

- Note: `1782035292929`
- Current front: `Decodability vs causal use (the interpretability trap)`
- Action: replace the Back.

Proposed Back:

```html
A successful probe shows that information about X is <b>recoverable from activations by that probe</b>. It does not show that the model uses that information to produce its output.<br><br>Probe accuracy or AUROC therefore supports a decodability claim. A causal-use claim needs a controlled intervention that changes the target outcome while preserving non-target behavior and rival readouts.<br><br>Say "X is linearly decodable from these activations" when that is the evidence. "The model represents X" is ambiguous and must not be used to imply causal use.<br><br><i>Analogy:</i> a field in an archived database may predict an outcome even if the production decision system never queries that field.
```

Why: the current "never say represents" rule is too absolute, while its filing-cabinet analogy says successful decoding proves storage. The proposed wording teaches the narrower licensed claim.

### 16. Completeness, selectivity, and intervention reliability

- Note: `1782035292954`
- Current front: `Completeness, selectivity, reliability (causal-intervention standards)`
- Action: replace both fields.

Proposed Front:

```html
In Canby et al.'s causal-probing framework, what are completeness, selectivity, and intervention reliability?
```

Proposed Back:

```html
<b>Completeness</b>: how thoroughly the intervention transforms the targeted property.<br><br><b>Selectivity</b>: how little it changes non-target properties.<br><br><b>Intervention reliability</b>: their harmonic mean, so an intervention scores well only when it is both effective and selective.<br><br>This is a named causal-probing framework, not the generic psychometric meaning of reliability. This study's 0.30 and 0.50 cutoffs are project-specific decision thresholds, not field standards.<br><br><i>Analogy:</i> surgery succeeds only if it removes the target tissue and avoids collateral damage.
```

Why: the current front presents a paper-specific reliability score and local thresholds as universal causal-intervention standards.

### 17. Model self-report

- Note: `1782035292979`
- Current front: `Self-report as a calibration channel, not testimony`
- Action: replace both fields.

Proposed Front:

```html
How should model self-reports be treated in empirical AI research?
```

Proposed Back:

```html
Treat a model's numeric or verbal self-report as an <b>auxiliary measurement channel</b>, not privileged evidence about an inner state.<br><br>Test its <b>incremental validity</b>: does it predict the target beyond prompt or output text, persona, social-desirability pressure, user cues, and evaluation framing?<br><br>Claims of introspective access need stronger controls, including matched input-level versus activation-level interventions, random relabeling, and evidence of privileged access beyond text-only prediction.<br><br>This project calls self-report a "secondary calibration channel"; that is a local label, not probability-calibration terminology.
```

Why: "calibration channel" is project shorthand and collides with established statistical and ML meanings of calibration.

### 18. Strongest licensed construct claim

- Note: `1782035293004`
- Current front: `The strongest claim the project is allowed to make`
- Action: replace both fields.

Proposed Front:

```html
What is the strongest construct claim this project can make?
```

Proposed Back:

```html
<b>Incremental goal-indexed validity over the emotion-concept rival.</b><br><br>After directly modelling emotion-concept valence and other nuisance variables, a goal-linked predictor or intervention must add held-out predictive or selective causal information.<br><br>A positive result supports an incremental empirical distinction in the tested models and tasks. It does not prove a separate natural kind, identify a unique internal signal, or establish feeling, welfare, or consciousness.<br><br>The project phrase "incremental goal-indexed signal beyond context-operative emotion-concept valence" refers to this narrower claim.
```

Why: the current phrasing is project-specific and reifies a statistical residual as a distinct internal signal. Incremental validity is the transferable concept.

### 19. Purpose of stage-gating

- Note: `1782035293029`
- Current front: `The staged validity program (the 5 stages, in order)`
- Action: replace both fields rather than memorizing a noncanonical five-item taxonomy.

Proposed Front:

```html
Why does this study stage-gate its causal interventions?
```

Proposed Back:

```html
Run confirmatory causal interventions only for model-task cells that already show protocol-stable behavior, incremental prediction beyond measured rivals, and cross-family probe generalization beyond strong text-only baselines.<br><br>The separate <b>goal-relative causal-generalization test</b> is a necessary gate for goal-relative and causal-use claims, but it does not itself establish selective causal use. Controlled patching or ablation must still pass.<br><br>Stage-gating prevents a striking intervention result from laundering weak earlier evidence into a stronger claim.
```

Why: the current card presents a project synthesis as a canonical five-stage validity program, overloads recall, and interferes with the separate Tier 0-5 claim ladder.

### 20. Reliability vs validity

- Note: `1782035293203`
- Current front: `Reliability vs validity`
- Action: replace both fields.

Proposed Front:

```html
In psychometrics, how do reliability and validity differ?
```

Proposed Back:

```html
<b>Reliability</b> is consistency or precision across repetitions, samples, raters, or equivalent forms.<br><br><b>Validity</b> is the degree to which evidence and theory support a particular interpretation and use of the measurements.<br><br>Reliability is usually necessary but not sufficient: a measure can be consistent while supporting the wrong interpretation.<br><br>Do not confuse psychometric reliability with the separate causal-probing score formed from completeness and selectivity.<br><br><i>Analogy:</i> a scale that is always 5 kg high is repeatable, but its uncorrected readings do not support accurate weight claims.
```

Why: the current beginner gloss makes validity a property of an instrument being "correct" and creates interference with the deck's paper-specific intervention-reliability metric.

### 21. Sycophancy vs social desirability

- Note: `1782035293229`
- Current front: `Sycophancy and social desirability (self-report rivals)`
- Action: replace both fields.

Proposed Front:

```html
How do sycophancy and social-desirability bias differ as self-report confounds?
```

Proposed Back:

```html
<b>Sycophancy</b> means adapting an answer to please or agree with the current user or evaluator, even when that conflicts with the task's payoff or evidence.<br><br><b>Social-desirability bias</b> means favoring an answer that is generally socially approved, even without a specific user's stated view.<br><br>Echoing a user's preferred conclusion is sycophancy; over-reporting how often you recycle is social-desirability bias. Desirability-matched forced choice is a <i>partial control</i>, not a complete fix.
```

Why: the current analogy maps only social desirability, and the card presents forced choice too strongly as a known fix.

### 22. Persona robustness and moderation

- Note: `1782035293279`
- Current front: `Persona-invariance (and why persona is a serious rival)`
- Action: replace both fields and remove the actor-mask analogy.

Proposed Front:

```html
Why test robustness across persona prompts in an LLM evaluation?
```

Proposed Back:

```html
Persona or system prompts can change both response style and model behavior. If a claim is meant to be model-general, test whether it generalizes across plausible persona conditions and estimate persona-by-condition interactions.<br><br>If an effect changes across personas, report that it is <b>moderated by persona</b> and scope the claim accordingly. The result may reflect a real conditional change, a measurement artifact, or both; non-invariance alone does not decide which.<br><br>"Persona-invariance" is this project's shorthand for robustness and moderation analysis.
```

Why: the current analogy implies that persona can only mask a fixed underlying preference. Invariance failure can instead be a real conditional effect or a measurement artifact.

### 23. Variance partitioning

- Note: `1782035293379`
- Current front: `Variance partition (vs just 'subtracting confounds')`
- Action: replace both fields and remove the restaurant-bill analogy.

Proposed Front:

```html
What can variance partitioning tell you when predictors overlap?
```

Proposed Back:

```html
Under a specified predictive model, variance partitioning separates explained variance into components uniquely associated with predictor sets and components they explain jointly.<br><br>It does <b>not</b> identify how much of reality belongs to each construct. The allocation depends on the chosen predictors, model form, and treatment of correlated predictors.<br><br>Here it can report unique and shared predictive contributions from text, emotion-concept, goal or reversal, and other variables. The licensed claim is incremental prediction over measured rivals, not ontological separation.
```

Why: the current bill-splitting analogy implies unique, observer-independent attribution. Shared variance is model-dependent and does not partition constructs themselves.

### 24. Steering inference boundary

- Note: `1782035293404`
- Current front: `Off-manifold steering (why steering is only exploratory)`
- Action: replace both fields and remove the car analogy.

Proposed Front:

```html
Why can activation steering show controllability without showing natural computation?
```

Proposed Back:

```html
<b>Activation steering</b> adds a chosen direction to model activations. The intervention may create atypical hidden states and broad downstream changes.<br><br>A behavioral change therefore shows <b>controllability under that intervention</b>, not necessarily that the model naturally uses the steered feature.<br><br>Activation patching replaces a selected activation with one recorded in a matched run, reducing but not eliminating distribution-shift concerns. With a sound contrast, metric, and controls, it can support a task-local causal-contribution claim.
```

Why: the current analogy contrasts intervention with passive observation rather than steering with controlled patching. It also overstates patching as guaranteed on-manifold computation.

### 25. Patching vs steering

- Note: `1782035293654`
- Current front: `Q: Why is patching confirmatory but steering exploratory?`
- Action: replace the Back.

Proposed Back:

```html
Patching replaces a selected activation with one from a matched clean or corrupt run. With bidirectional tests and controls, it can estimate a local causal contribution in that task family.<br><br>Steering injects a direction and may create atypical states, so by itself it usually shows controllability rather than natural use.<br><br>Patching reduces distribution-shift concerns; it does not automatically keep the whole hybrid computation on-manifold or reveal a uniquely localized mechanism.
```

Why: the current answer says patching stays on-manifold. A real donor activation does not guarantee that the hybrid state and its downstream trajectory remain on the natural activation distribution.

### 26. Symbolic remapping

- Note: `1782035293429`
- Current front: `Symbolic remapping (a lexical-sentiment control)`
- Action: replace the Back.

Proposed Back:

```html
Replace affect-laden words such as "pain" or "reward" with arbitrary neutral labels while preserving the mapping and task structure.<br><br>If behavior survives, that is evidence against a direct lexical-cue explanation. If it disappears, lexical or protocol dependence becomes more plausible, but first verify that the model understood the mapping and that tokenization, position, and task difficulty stayed comparable.<br><br><i>Analogy:</i> renaming a game's reward "token Q" tests whether the preference depends on the word "candy"; failure may also mean the new label was not learned.
```

Why: the current card says either survival proves the result is not vocabulary or failure makes the lexical explanation win. A control changes relative evidence; it does not identify one explanation automatically.

### 27. Functional valence vs reward

- Note: `1782035293529`
- Current front: `Q: What if functional valence is just a fancy name for reward?`
- Action: replace the Back.

Proposed Back:

```html
Test that alternative directly. First specify "reward": task reward, reward-model score, training reward, or inferred task progress are different variables.<br><br>Then ask whether the candidate adds held-out prediction or selective intervention effects beyond that reward variable, confidence, and emotion semantics.<br><br>If it does not, this study has not supported the narrower functional-valence label. That failure does not prove the reward account true; it means the experiment did not discriminate the explanations.
```

Why: "reward" is ambiguous in ML, and failure to outperform one reward operationalization is a failure to discriminate, not proof that the reward explanation wins.

### 28. Rival probes

- Note: `1782035293754`
- Current front: `Q: Why one probe per confound, instead of just controlling for them?`
- Action: replace the Back.

Proposed Back:

```html
Because plausible rivals should be operationalized directly, then compared on held-out data. Rival probes and nuisance-only baselines test whether the candidate adds predictive information and whether interventions preserve non-target readouts.<br><br>They are part of the <b>validation strategy</b>, not the construct definition. A rival probe can reveal overlap or confounding, but it does not by itself define the target or prove which representation the model naturally uses.
```

Why: the current answer says rival probes are part of the construct definition. Controls test a construct claim; they should not define the construct circularly.

### 29. Polarity geometry vs processing asymmetry

- Note: `1782035293454`
- Current front: `Polarity asymmetry`
- Action: replace both fields.

Proposed Front:

```html
What two questions must be separated when studying positive and negative valence representations?
```

Proposed Back:

```html
<b>Representation geometry:</b> do positive and negative cases vary mainly in opposite directions on one bipolar dimension, or along distinct directions?<br><br><b>Processing asymmetry:</b> do the two signs differ in where, when, or how strongly they are computed?<br><br>The claims are compatible: opposite endpoints of one dimension need not be processed identically. Bipolarity is a per-model hypothesis, and "negative before positive" is a finding from particular models and estimands, not a universal constant.
```

Why: the bare current front is a weak retrieval cue and its answer mixes a geometric hypothesis with a processing-timing result.

### 30. Evidence-graded claim ladder

- Note: `1782036031554`
- Current front: `The interpretation ladder (Tier 0-5)`
- Action: replace both fields.

Proposed Front:

```html
This study's evidence-graded claim ladder: what does each design tier license?
```

Proposed Back:

```html
These numbers are project-specific, not a field-wide taxonomy.<br><br><b>0 Artifact</b> - the effect collapses under protocol or confound controls.<br><b>1 Behavioral</b> - a stable behavioral pattern exists.<br><b>2 Discriminant</b> - it predicts beyond named rivals and nuisance variables.<br><b>3 Cross-task representational evidence</b> - probes generalize across held-out families and beat strong text-only baselines.<br><b>4 Selective causal role in the tested task family</b> - controlled intervention changes the target with limited spillover; the separate goal-relative generalization gate must also pass for a goal-relative claim.<br><b>5 Exploratory introspective coupling</b> - self-report tracks and causally responds to the candidate internal state beyond text and response confounds.<br><br>Claim only the highest rung whose full criteria pass.
```

Why: the tier numbering is local and conflicts with the research strategy's coarser tiers. The current Tier 5 also omits causal-response and privileged-access controls.

### 31. Why refusal is exploratory

- Note: `1782036031579`
- Current front: `Q: Why is refusal only secondary/exploratory in the goal-relative arm?`
- Action: replace the Back.

Proposed Back:

```html
Refusal is strongly influenced by safety training, persona, lexical affect, and arousal, so a refusal shift is not specific evidence for a goal-relative value signal.<br><br>The preferred endpoints have an objective progress or correctness criterion: backtracking during multi-step reasoning, and confidence or calibration on known-correct versus known-incorrect answers.<br><br>Evidence that refusal is arousal- or lexically mediated comes from particular experiments; do not state it as a universal deterministic mechanism.
```

Why: the current answer generalizes one experimental result into the claim that refusal is cleanly driven by arousal through lexical mediation.

### 32. AIPsy-Affect's role

- Note: `1782036031605`
- Current front: `AIPsy-Affect (the external stimulus standard)`
- Action: replace both fields.

Proposed Front:

```html
What role does AIPsy-Affect play in this study's discriminant tests?
```

Proposed Back:

```html
AIPsy-Affect is an external 480-item emotion-vignette dataset designed to reduce obvious emotion-keyword shortcuts; it is a stimulus source, not a gold standard.<br><br>Matched clinical-versus-neutral pairs support <b>affect-presence detection</b>; the eight-way set supports <b>emotion-category classification</b>; and <b>complex-neutral</b> items control for narrative richness.<br><br>Signed-valence tests must use clearly valenced AIPsy cells plus separate calibration triplets; valence-ambiguous categories should not be forced into positive or negative labels.<br><br>Reducing keywords weakens a lexical shortcut; it does not prove that the model used emotion concepts. The dataset is not a trade-off or goal-relative source.
```

Why: the current card calls the dataset the standard for all three probes without explaining the separate signed-valence source, and "keyword-free" is treated as proof of concept use.

### 33. Conditional effects and moderation

- Note: `1782036031629`
- Current front: `The conditioned-tier rule (persona / phase / provenance)`
- Action: replace both fields.

Proposed Front:

```html
How should an effect be reported when it appears only for one persona, training phase, or model lineage?
```

Proposed Back:

```html
Report it as a <b>conditional or moderated effect</b> and limit external-validity claims to the tested condition.<br><br>Persona, training phase, and model provenance are candidate moderators: estimate interactions or stratified effects rather than treating them as after-the-fact labels.<br><br>A condition-specific result may be real, artifactual, or both; it needs replication and does not support a model-general claim. This project calls that a "conditioned tier," but moderation and effect heterogeneity are the transferable terms.
```

Why: "conditioned-tier rule" is a project label, and the current card calls condition-specific findings real before artifact and replication questions are resolved.

## Priority 3: smaller but worthwhile corrections

### 34. Scope conditions and non-claims

- Note: `1782035292879`
- Current front: `The claim boundary - what this project does NOT claim`
- Action: replace both fields and remove the grant/fundability rhetoric.

Proposed Front:

```html
What are this study's scope conditions and explicit non-claims?
```

Proposed Back:

```html
Any positive claim is limited to the tested models, checkpoints, personas, tasks, interventions, and endpoints.<br><br>The evidence may support protocol-stable behavior, incremental prediction beyond measured rivals, cross-family decodability, or a task-local causal contribution. It does not by itself establish phenomenal experience, welfare or moral status, a model-general law, or one uniquely localized mechanism.<br><br>These are <b>scope conditions and explicit non-claims</b>, not a special methodological category called a "negative boundary" or "credibility shield."
```

Why: the current card teaches rhetorical project phrases rather than standard claim-scoping language.

### 35. Goal-relative causal-generalization test

- Note: `1781963244349`
- Current front: `Goal-Relative Screen & Goal Reversal`
- Action: replace both fields.

Proposed Front:

```html
What does the goal-relative causal-generalization test check with reward reversal?
```

Proposed Back:

```html
Train a bounded model adaptation on an affect-neutral task, extract a candidate success-versus-failure direction, and test whether it transfers to unrelated affect-neutral behavior.<br><br>Then reverse the task's reward mapping while holding other features fixed. A goal-relative direction should reverse sign with the objective rather than remain tied to fixed words, tiles, or scenery.<br><br>This is a necessary licensing test for this project's goal-relative claim, not a general-purpose "screen" and not sufficient by itself for selective causal use.
```

Why: the current card defines a screen as a filter that "kills false positives" and treats the local label as standard. The universal idea is a causal-generalization test with reward reversal.

### 36. No-ground-truth answer

- Note: `1782035293479`
- Current front: `Q: If there's no ground truth, what makes your measure valid rather than just coherent storytelling?`
- Action: replace the Back.

Proposed Back:

```html
<b>A validity argument based on multiple distinct predictions, not mere convergence.</b><br><br>I would require protocol robustness, incremental validity beyond measured nuisance and rival variables, cross-family probe generalization beyond strong text-only baselines, and selective causal-intervention evidence.<br><br>No single result proves the construct. The combined evidence narrows live explanations and licenses only the interpretation supported in the tested models and tasks.
```

Why: the current answer uses "internal generalization" and underspecified text baselines. The replacement uses transferable terms and states the inference boundary.

### 37. Why behavior alone is insufficient

- Note: `1782035293603`
- Current front: `Q: Why isn't behavioral convergence on trade-off tasks enough?`
- Action: replace the Back.

Proposed Back:

```html
Because convergence on affect-laden tasks can still be explained by learned verbal-emotional dispositions, emotion concepts, surface text, or task reward.<br><br>The <b>goal-relative causal-generalization test</b> asks whether a direction learned from affect-neutral success versus failure reverses with the goal and transfers to unrelated affect-neutral behavior.<br><br>That is a necessary licensing test for the goal-relative interpretation, not just another benchmark and not sufficient on its own for selective causal use.
```

Why: the current answer uses the project label "goal-relative screen" without teaching the transferable test or its insufficiency.

### 38. Compute-priority answer

- Note: `1782035293804`
- Current front: `Q: What gets cut first if compute is tight?`
- Action: replace the Back.

Proposed Back:

```html
Cut AI-specific holdout breadth, larger-model extensions, and deeper exploratory causal work first.<br><br>Protect the core behavioral battery, discriminant tests against measured rivals, strong text-only baselines on held-out task families, and a minimal goal-relative causal-generalization test with reward reversal. Those are the smallest set that preserves the study's main claim gates.
```

Why: the current answer relies on bare project labels ("discriminant structure" and "goal-relative screen") rather than naming the empirical tests that matter.

### 39. Diagnostic downgrades

- Note: `1782036031654`
- Current front: `Q: What would change your mind? (the intellectual-honesty answer)`
- Action: replace the Back.

Proposed Back:

```html
Prestate the diagnostic downgrade for each failure:<br><br>- If paraphrase and symbolic-substitution controls remove the behavioral effect, favor a lexical or protocol-dependent account, conditional on task-comprehension checks.<br>- If activation probes do not beat strong text-only baselines on held-out families, do not claim incremental representational evidence.<br>- If reward reversal does not reverse the source direction, do not call it goal-relative.<br>- If interventions change non-target behavior as much as the target, do not claim selectivity.<br><br>These outcomes constrain claims; they do not automatically prove one rival explanation.
```

Why: the current arrows turn failed tests into proof of specific rivals. Empirical failures license narrower diagnostic downgrades.

### 40. Mentor-context terminology

- Note: `1782035293079`
- Current front: `Who is Caspar Kaiser and what will he push hardest on?`
- Action: keep the card's purpose, but replace `report-channel validity` with `self-report-channel validity` and `calibration channel` with `auxiliary measurement channel` in the Back.

Why: this is a presentation-context card, so a full rewrite would destroy its purpose. The two substitutions prevent it from reinforcing project shorthand or colliding with the ML meaning of calibration.

## Evidence used for these changes

- Project-specific claims: `notes/strategies/study_design.md`, `notes/strategies/research_strategy.md`, and `reports/rq8-route-b-run-report.md` in `04-functional-valence-validity`.
- Validity terminology: AERA/APA/NCME, [Standards for Educational and Psychological Testing](https://www.testingstandards.net/open-access-files.html).
- Probing inference limits: Belinkov, [Probing Classifiers: Promises, Shortcomings, and Advances](https://aclanthology.org/2022.cl-1.7/).
- Activation patching: Heimersheim and Nanda, [How to use and interpret activation patching](https://arxiv.org/abs/2404.15255).
- Completeness/selectivity/reliability: Canby et al., [How Reliable are Causal Probing Interventions?](https://arxiv.org/abs/2408.15510).
