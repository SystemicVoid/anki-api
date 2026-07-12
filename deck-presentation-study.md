# Four-Day Study and Rehearsal System for the AI Welfare Measurement Deck

## Executive map of the deck

The deck’s argument is tighter than it may feel when reading slide by slide. Its center of gravity is not “do AIs feel?” but “can we validate welfare-relevant measurement signals under adversarial controls?” That framing is explicit across the deck, the operational study design, and the strategy note. fileciteturn0file0 fileciteturn0file1 fileciteturn0file2

The argument, compressed to the version you need for Wednesday, is this:

- The field already has many candidate welfare-relevant indicators, but not yet an instrument that has survived something like serious psychometric and mechanistic validation. The gap is validated measurement, not lack of candidate signals. fileciteturn0file0 fileciteturn0file1
- The target construct is **polarity-sensitive, goal-relative functional valence**: an internal state representing positive or negative value relative to the model’s current goal or task, affecting choices and possibly trackable via report channels. The deck keeps this intentionally below claims about consciousness, sentience, suffering, or moral patienthood. fileciteturn0file0 fileciteturn0file1
- Because there is no gold-standard ground truth for this construct, the project lives inside a **construct-validity problem**, not a criterion-validity problem. That is exactly the territory Cronbach and Meehl described: when there is no accepted criterion, validity must be built by integrating evidence from many sources and by locating the measure inside a nomological network. fileciteturn0file1 citeturn18view1turn18view2turn18view0
- The deck proposes a staged validity program: behavioral stability first, then discriminant validity, then internal generalization, then a goal-relative screen, and only then limited causal confirmation. Stronger claims require stronger endpoints. fileciteturn0file0 fileciteturn0file1
- The main behavioral families are controlled valence trade-offs and naturalistic transcript utility comparisons, with AI-specific scenarios held out as exploratory rather than headline evidence. That is a deliberate discipline move: the study is trying to validate measurement on cleaner task families before leaning on anthropomorphically loaded scenarios like deletion or shutdown. fileciteturn0file0 fileciteturn0file1
- The decisive move in the revised design is that **goal-relativity must be tested, not merely named**. That is why the study now includes an affect-neutral source task, extraction of a reward/success direction, a reward-reversal condition, and transfer tests on unrelated affect-neutral tasks. This is the main non-circular licensing screen for causal-use claims. fileciteturn0file1 fileciteturn0file2
- The leading rival is **emotion-concept valence**, not just generic lexical sentiment. The project therefore treats affect-reception, signed valence, and emotion-category as separate rival probes, and aims to report variance partition rather than claiming clean ontological separation. fileciteturn0file1 fileciteturn0file2 citeturn21academia0turn21academia3turn22academia3
- Internal probes are useful only as evidence of **extractability** unless they beat strong text baselines, generalize across held-out task families, and pass causal checks. That caution is directly aligned with the probing literature, which warns against reading decodability as causal use. fileciteturn0file1 citeturn17view1turn24academia2
- Patching is confirmatory; steering is exploratory. The reason is simple: patching can support a within-task causal-role claim under matched clean/corrupt comparisons, while steering is much more vulnerable to unreliability and off-manifold states. fileciteturn0file1 citeturn17view2turn22academia2turn24academia0turn24academia1
- The best mentor-facing positioning is therefore: **you already have a scaffolded measurement-validity program, the key construct-validity worries are visible to you, and the thing you want help with is stress-testing the assumptions that connect the construct, the batteries, the rival probes, and the causal thresholds.** That is exactly consistent with the deck and strategy documents. fileciteturn0file0 fileciteturn0file1 fileciteturn0file2

A useful meta-point for Wednesday: Caspar Kaiser is unusually likely to push hard on **report-channel validity** and **scale interpretation**, because his recent work includes both a paper finding no reliable evidence of self-reported sentience in small LLMs and a paper on how ordered subjective scales can mislead relative effect-size comparisons even when coefficient signs stay fairly stable. Expect him to probe exactly those weaknesses. citeturn17view4turn17view6

## Concept priority map

What follows is the shortest concept list that still lets you sound fluent rather than decorative. I am optimizing for “credible under pressure,” not doctoral completeness.

### Tiering overview

| Tier | Concept | Why it belongs here |
|---|---|---|
| Tier 1 | Construct validity under no gold standard | This is the project’s core epistemic frame. If you are shaky here, everything else collapses. fileciteturn0file1 citeturn18view1turn18view2 |
| Tier 1 | Goal-relative functional valence | This is the studied construct itself. You must define it cleanly and modestly. fileciteturn0file0 fileciteturn0file1 |
| Tier 1 | Claim boundary | You need crisp separation from consciousness, sentience, suffering, welfare subjecthood, and moral patienthood. fileciteturn0file0 fileciteturn0file1 |
| Tier 1 | Discriminant validity | The whole deck is built around ruling out rival explanations instead of merely showing signal. fileciteturn0file0 fileciteturn0file1 |
| Tier 1 | Measurement invariance and protocol sensitivity | The deck repeatedly emphasizes order, framing, format, persona, neutrality, abstention, and symbolic remapping. fileciteturn0file0 fileciteturn0file1 |
| Tier 1 | Goal-relative causal generalization | This is the revised primary licensing screen. You need to explain why it is in the design and what it licenses. fileciteturn0file1 |
| Tier 1 | Mapping reversal | This is the strongest anti-circularity trick in the goal-relative screen. fileciteturn0file0 fileciteturn0file1 |
| Tier 1 | Decodability versus causal use | Very likely mentor question. Also central to probe interpretation. fileciteturn0file1 citeturn17view1turn24academia2 |
| Tier 1 | Completeness, selectivity, reliability | These are the language of causal standards in the deck. You must know them cold. fileciteturn0file0 fileciteturn0file1 citeturn24academia1 |
| Tier 1 | Self-report as calibration channel, not testimony | This is where Caspar is especially likely to press. fileciteturn0file1 citeturn17view4turn17view6turn19academia1turn19academia0 |
| Tier 2 | Emotion-concept valence as the leading rival | Must recognize and discuss; probably the most important scientific rival after construct validity itself. fileciteturn0file1 fileciteturn0file2 citeturn21academia0 |
| Tier 2 | Affect-reception vs signed valence vs emotion-category | Important because the deck explicitly splits them. fileciteturn0file0 fileciteturn0file1 citeturn21academia3turn22academia3 |
| Tier 2 | Variance partition | You likely do not need to derive it, but you must explain why “subtracting confounds” is too crude. fileciteturn0file0 fileciteturn0file1 |
| Tier 2 | Persona-invariance | The deck treats persona as a primary discriminant axis. fileciteturn0file1 |
| Tier 2 | Lexical sentiment confound | Easy question to get asked; easy to answer if prepared. fileciteturn0file0 fileciteturn0file1 |
| Tier 2 | Sycophancy and social desirability | These directly threaten self-report and questionnaire-style measures. fileciteturn0file1 citeturn19academia0 |
| Tier 2 | Evaluation awareness | Important because benchmark framing can contaminate responses. fileciteturn0file1 |
| Tier 2 | Thurstonian utility modeling | You should recognize what it is doing in the transcript arm. fileciteturn0file1 |
| Tier 2 | Frozen-text baseline | Necessary for explaining the “probe must beat text” rule. fileciteturn0file1 |
| Tier 2 | Polarity asymmetry | Important but not something you need to dominate. fileciteturn0file1 |
| Tier 3 | AIPsy-Affect | Useful for explaining one discriminant battery, but deferrable. fileciteturn0file1 citeturn22academia3 |
| Tier 3 | LEAVE / discriminant erasure diagnostics | Good to know exists; not essential for basic deck fluency. fileciteturn0file1 |
| Tier 3 | Slot bias and three-position symbolic controls | Useful if someone gets very operational. fileciteturn0file1 |
| Tier 3 | Base/instruct and provenance conditioning | Useful for scope, but not a first-pass explaining priority. fileciteturn0file1 |
| Tier 3 | Off-manifold steering | Good to recognize; not required to explain mechanistically in depth. fileciteturn0file1 citeturn24academia0 |
| Tier 3 | Multiplicity control | Useful for sounding statistically serious; not your first bottleneck. fileciteturn0file0 |

My recommendation is to devote nearly all high-energy study time to the ten Tier 1 concepts. On Wednesday, deep fluency on those ten will outperform shallow familiarity with thirty terms.

## Tier 1 concept briefings

### Construct validity under no gold standard

**Plain-English definition.**
You are trying to measure something real enough to matter, but there is no trusted meter for it. So you cannot validate it by comparing your measure against a known true score. You have to validate it by showing that different pieces of evidence hang together in the pattern your theory predicts, while rival explanations fail. citeturn18view1turn18view2turn18view0

**Technical definition.**
Construct validity concerns whether the inferences drawn from observed measures are warranted as measures of a latent construct. When no adequate criterion exists, validation proceeds by embedding the construct in a nomological network of hypothesized relations among observables and other constructs, then testing whether the observed pattern fits that network. citeturn18view1turn18view0turn23view0

**Why it matters here.**
Your whole project exists because there is no gold-standard readout of “functional valence” in current models. The study design explicitly frames this as a measurement-validity problem and repeatedly warns against stronger conclusions than the evidence supports. fileciteturn0file1 fileciteturn0file2

**Likely Caspar question.**
“If there is no ground truth, what exactly would make you think your measure is valid rather than just coherent storytelling?”

**Strong answer.**
“I would not treat mere convergence as enough. The bar is a nomological pattern: reliable behavior across protocol variants, discriminant evidence against lexical/persona/report-channel rivals, internal generalization beyond text baselines, and then causally relevant effects under the right controls. The point is not to ‘prove’ the construct outright, but to narrow the live explanations and make stronger labels conditional on distinct evidence types.” fileciteturn0file0 fileciteturn0file1 citeturn18view2turn23view0

**Failure mode to avoid.**
Do not say, “there is no ground truth, so triangulation is the best we can do,” and stop there. That sounds hand-wavy. The better line is: “no gold standard means the validation burden shifts to nomological structure and rival exclusion.”

### Goal-relative functional valence

**Plain-English definition.**
A model can be doing better or worse relative to its current task or goal. Functional valence is the internal positive-or-negative value signal associated with that better-or-worse relation. fileciteturn0file0 fileciteturn0file1

**Technical definition.**
The deck defines a polarity-sensitive, goal-relative functional-valence state as an internal state or process that represents positive or negative value relative to the model’s current goal or task, influences choices, and may be tracked by a report channel. Whether positive and negative are two ends of a single bipolar axis is treated as an empirical hypothesis, not an assumption. fileciteturn0file0 fileciteturn0file1

**Why it matters here.**
This is the construct you’re measuring. If you define it sloppily, the whole project drifts either downward into generic preference/compliance or upward into sentience talk. The deck is designed precisely to hold that line. fileciteturn0file0 fileciteturn0file1

**Likely Caspar question.**
“What makes this more than just reward sensitivity, competence tracking, or task progress?”

**Strong answer.**
“At minimum, nothing should count unless it is both polarity-sensitive and goal-relative, and unless it survives discriminant testing against simpler rivals like lexical sentiment, persona, social desirability, confidence, or generic reward tracking. The design is trying to earn the narrower label ‘functional valence’ only if that narrower label predicts more than those alternatives do.” fileciteturn0file1 fileciteturn0file2

**Failure mode to avoid.**
Do not define functional valence as if it already were welfare. Keep it operational and conditional.

### Claim boundary

**Plain-English definition.**
You are not trying to show that the model is conscious or suffering. You are trying to show, at best, that some welfare-relevant signals measure a disciplined functional construct under strong controls. fileciteturn0file0 fileciteturn0file1

**Technical definition.**
The study’s negative boundary explicitly excludes conclusions about consciousness, sentience, felt pain or pleasure, welfare subjecthood, moral patienthood, self-report as privileged evidence, decodability as causal use, and steering as natural computation. fileciteturn0file0 fileciteturn0file1

**Why it matters here.**
This is your credibility shield. The AI-consciousness literature itself argues for theory-heavy, indicator-based, and cautionary assessment rather than behavioral overreach, and the deck aligns itself with that posture. citeturn16view0 fileciteturn0file2

**Likely Caspar question.**
“Why should I believe this project won’t slide into consciousness rhetoric once it gets interesting results?”

**Strong answer.**
“Because the boundary is part of the design, not just the messaging. The interpretation tiers are evidence-typed, the confirmatory boundary is explicit, and the strongest permitted claims are scoped to tested models and scenarios. If the evidence only supports a behavioral or discriminant label, that is where I stop.” fileciteturn0file0 fileciteturn0file1

**Failure mode to avoid.**
Do not say “obviously this doesn’t prove consciousness” and then spend the next minute gesturing at consciousness implications. That will sound grant-hungry and undisciplined.

### Discriminant validity

**Plain-English definition.**
Your measure should not just track lots of nearby things. It should track the target better than it tracks obvious rivals. citeturn18view2turn23view0

**Technical definition.**
Discriminant validity asks whether a candidate factor predicts target outcomes beyond specified rivals such as lexical sentiment, option position, format effects, persona, sycophancy, social desirability, evaluation awareness, and emotion-concept valence. In this design it is operationalized through confound models, held-out prediction, rival probes, and variance partition. fileciteturn0file1

**Why it matters here.**
Without discriminant validity, your results could just be “models dislike negative words,” “models role-play being prosocial,” or “models answer in evaluator-pleasing ways.” The deck is strongest exactly where it foregrounds those rivals. fileciteturn0file0 fileciteturn0file1 citeturn19academia0turn21academia0

**Likely Caspar question.**
“What specifically would make you think you are seeing functional valence rather than emotional semantics or survey gaming?”

**Strong answer.**
“I would want incremental predictive and causal value after explicitly modeling those rivals. In particular, the hard cases are emotion-concept valence, report-channel confounds, and protocol sensitivity. The deck’s logic is that the construct only earns the label if some goal-indexed signal survives after those are measured directly.” fileciteturn0file1 fileciteturn0file2

**Failure mode to avoid.**
Do not frame confounds as annoyances you will “control for.” Frame them as the main scientific competition.

### Measurement invariance and protocol sensitivity

**Plain-English definition.**
If a signal depends heavily on wording, order, response format, persona frame, or whether neutrality is allowed, you probably do not yet have a stable measure of the underlying thing. fileciteturn0file0 fileciteturn0file1

**Technical definition.**
Measurement invariance is the requirement that the same construct be measured comparably across conditions or groups. In this project, those “groups” are effectively protocol variants: direct wording versus paraphrase versus symbolic remapping, opposing orders, self versus third-party framing, different personas, neutral/abstain options, and rating versus logprob readouts. fileciteturn0file1

**Why it matters here.**
A huge portion of the design is actually about invariance, even when it is described operationally rather than formally. Caspar’s scale-transformation work also makes him likely to ask how robust any self-report effect is to properties of the response scale. citeturn17view6turn17view5

**Likely Caspar question.**
“How do you know your effect is not mostly a property of a particular answer format or scale?”

**Strong answer.**
“I don’t assume that away. The design treats protocol stability as a first-class research question. For behavior, I want slope signs that persist across paraphrase, symbolic remapping, and order swaps. For self-report, I treat numeric scales as calibration channels, not transparent intervals, and I would be most cautious about relative effect-size claims on those scales.” fileciteturn0file0 fileciteturn0file1 citeturn17view6turn17view5

**Failure mode to avoid.**
Do not use “measurement invariance” as fancy jargon if you really only mean “we tried a few prompt variants.” Use the term only when you can explain what comparability claim is at stake.

### Goal-relative causal generalization

**Plain-English definition.**
If you extract a direction from a clean, affect-neutral success-versus-failure task, and that same direction shifts behavior in a different affect-neutral task, that is far stronger evidence than just seeing a signal inside one prompt family. fileciteturn0file1 citeturn0academia0

**Technical definition.**
The design’s RQ8 treats a How’s-It-Going-style source task as the primary licensing screen: derive a direction from an affect-neutral, goal-relative source contrast, require reversal under opposite reward mapping, and test whether intervention along that direction shifts unrelated affect-neutral endpoints such as reasoning backtracking and confidence/calibration, beyond matched control directions. fileciteturn0file1 fileciteturn0file2 citeturn0academia0

**Why it matters here.**
This is the deck’s biggest conceptual improvement. It is the main answer to the worry that you are merely measuring emotion-flavored language patterns rather than something goal-indexed. fileciteturn0file1

**Likely Caspar question.**
“Why isn’t behavioral convergence on trade-off tasks enough?”

**Strong answer.**
“Because convergence on affect-laden tasks can still be explained by trained verbal-emotional dispositions or emotion-concept valence. The goal-relative screen asks a harder question: does a direction learned from affect-neutral success versus failure carry causal information that transfers to unrelated affect-neutral behavior? That is why it functions as a licensing screen rather than just another benchmark.” fileciteturn0file1 fileciteturn0file2 citeturn0academia0

**Failure mode to avoid.**
Do not say this “proves” functional valence. Say it raises the credibility of a goal-indexed interpretation.

### Mapping reversal

**Plain-English definition.**
Keep the surface world the same, but swap which outcomes count as success and failure. If your extracted direction flips too, it is following goal-achievement rather than superficial content. fileciteturn0file0 fileciteturn0file1

**Technical definition.**
Mapping reversal is a source-task intervention in which reward/success labels are swapped under otherwise identical stimuli; the extracted direction must reverse sign. This is a direct test of whether the signal tracks the goal mapping rather than fixed lexical or situational properties. fileciteturn0file1

**Why it matters here.**
It is the cleanest design move against circularity in the goal-relative screen.

**Likely Caspar question.**
“Why is reward reversal doing so much work for you?”

**Strong answer.**
“Because without reversal, a source direction could still reflect stable surface regularities or implicit emotional semantics. Reversal makes the source direction answer to the goal mapping itself. It does not solve everything, but it is the sharpest available test that the direction follows success versus failure rather than the scenery.” fileciteturn0file1

**Failure mode to avoid.**
Do not overstate reversal as sufficient. It is strong evidence, not a full validity proof.

### Decodability versus causal use

**Plain-English definition.**
Finding information in activations is easier than showing the model actually uses that information to produce behavior. citeturn17view1turn24academia2

**Technical definition.**
Probe accuracy establishes extractability of a property from internal representations. Causal-use claims require additional evidence that interventions on the candidate representation selectively alter target behavior while preserving non-target behavior and not merely moving the model off its natural manifold. citeturn17view1turn17view2turn24academia0turn24academia1turn24academia2

**Why it matters here.**
This is the main interpretability trap in the deck. A mentor who knows mechanistic interpretability will check whether you understand it.

**Likely Caspar question.**
“If your probe gets great AUROC, why should I care?”

**Strong answer.**
“Because great AUROC only says the information is recoverable. I would care more if the probe beat strong text baselines on held-out families and if matched patching or ablation moved the target outcome with limited spillover. Otherwise the honest interpretation is extractability, not causal use.” fileciteturn0file1 citeturn17view1turn24academia2

**Failure mode to avoid.**
Never say “the model represents X” when the evidence only shows “a linear probe can decode X.”

### Completeness, selectivity, and reliability

**Plain-English definition.**
If an intervention changes the target only a little, completeness is weak. If it also messes up lots of other things, selectivity is weak. Reliability summarizes how well you are doing on both at once. citeturn24academia1

**Technical definition.**
In the cited causal-probing framework, completeness is how thoroughly the target property is transformed, selectivity is how little non-target content is altered, and reliability is their harmonic mean. The deck imports these ideas directly into its thresholds and interpretation language. fileciteturn0file0 fileciteturn0file1 citeturn24academia1

**Why it matters here.**
These terms are scattered across the causal slides and appendix. You do not need to derive them mathematically, but you do need to explain what they are buying you.

**Likely Caspar question.**
“Why those causal thresholds?”

**Strong answer.**
“They are not metaphysically privileged. They are operational guardrails that force the intervention evidence to clear both a target-efficacy bar and a spillover bar. The deeper point is not the exact numbers; it is refusing to call something causal evidence when the intervention mostly produces broad collateral changes.” fileciteturn0file0 fileciteturn0file1 citeturn24academia1

**Failure mode to avoid.**
Do not defend the exact threshold values too hard. Defend the principle behind them.

### Self-report as calibration channel, not testimony

**Plain-English definition.**
A model’s numeric or verbal report might contain signal, but you should treat it like a noisy instrument, not like a privileged witness about its own inner life. fileciteturn0file1

**Technical definition.**
The design uses logit-based numeric self-report as a secondary calibration channel and tests whether it adds information beyond external text features and confounds such as social desirability, persona, user-opinion pressure, and evaluation framing. Caspar’s own recent paper found no clear evidence that classifiers could show models’ denials of sentience were untruthful, while Martorell’s work found that logit-based self-reports can track probe-defined internal states better than greedy decoded reports. fileciteturn0file1 citeturn17view4turn19academia1turn19academia0

**Why it matters here.**
This is one of the most obvious places a skeptical mentor can puncture overconfidence.

**Likely Caspar question.**
“Why include self-report at all, given how contaminated it is?”

**Strong answer.**
“Because it may still serve as a measured channel if treated modestly. I am not treating it as testimony about sentience or welfare. I am asking whether logit-based reports track the candidate internal state beyond what text-only predictors and response-style confounds already explain.” fileciteturn0file1 citeturn17view4turn17view6turn19academia1turn19academia0

**Failure mode to avoid.**
Do not call self-report “introspection evidence” unless you immediately state the stronger gates: matched input-vs-activation controls, random relabeling checks, and privileged-access beyond text-only prediction. fileciteturn0file1

## Four-day study program

I would not study this as a literature review. I would study it as a compression problem: build the smallest mental model that can survive interruption.

Assume roughly **two deep work blocks in the morning, one consolidation block in the afternoon, and one rehearsal block in the evening**, for about **6.5 to 7.5 effective hours per day**. The key rule is that every block ends with retrieval, not rereading.

### Day 1

The goal is to rebuild the deck as a causal argument in your own words, and to make the vocabulary non-fragile.

**Morning block one** should be a deck reconstruction sprint. Read the deck, study design abstract sections, and your pasted notes once, then close everything and write a one-page argument map from memory: problem, construct, claim boundary, stages, rivals, causal gates, interpretation tiers. Then reopen the docs and patch only the gaps. You are trying to replace “slide memory” with “argument memory.” fileciteturn0file0 fileciteturn0file1 fileciteturn0file3

**Morning block two** should be core vocabulary. Make flashcards for the ten Tier 1 concepts above. Each card must have four fields only: definition, why it matters, one contrast case, one misuse to avoid. If a card cannot fit in that format, your understanding is still too fluffy.

**Afternoon block** should be a Feynman session. Record yourself answering, without notes, these six prompts in under 90 seconds each:
“What is this project actually measuring?”
“Why is construct validity the frame?”
“What is the claim boundary?”
“Why isn’t behavioral convergence enough?”
“Why isn’t probe accuracy enough?”
“Why is the goal-relative screen in the design?”
Then listen back and mark every sentence that sounds like borrowed language rather than owned understanding.

**Evening block** should be the first explain-the-slide-from-memory round. Go through the deck slide by slide with the screen off. Name each slide’s function, not its title. For example: “This is the slide that narrows the construct,” “this is the slide that justifies the goal-relative screen,” “this is the slide that explains why steering is only exploratory.”

**Output for the day.**
By bedtime, you should be able to give a coherent **five-minute account** of the project with no notes and no jargon pile-up.

### Day 2

The goal is to get psychometrics fluent enough that you stop sounding like an interpretability person borrowing psychometric words.

**Morning block one** should be construct-validity theory. Read only the highest-yield portions of Cronbach and Meehl plus one modern bridge text. Extract three ideas: no gold standard, nomological network, and integration of evidence from many sources. Then map your project onto those three ideas in a half-page memo. citeturn18view1turn18view2turn18view0turn23view0

**Morning block two** should be the validity axes in your project. Build a one-table sheet with columns: validity type, what would count as evidence here, leading rival, and what failure would look like. Include at least construct, discriminant, protocol robustness, internal generalization, causal relevance, self-report calibration, and persona-invariance. This exercise forces you to stop using “validity” as one fuzzy bucket.

**Afternoon block** should be measurement-invariance and scale-pathology drills. Practice answering:
“What would count as a protocol artifact?”
“What does symbolic remapping buy you?”
“What does neutral/abstain buy you?”
“What do order swaps buy you?”
“Why be cautious with numeric scale comparisons?”
Tie the last answer explicitly to Caspar’s scale-transformation work: weak deviations from linear scale use may not flip coefficient signs, but they can make relative magnitudes much less trustworthy. citeturn17view6turn17view5

**Evening block** should be concept contrast drills. Do ten rapid contrasts:
construct validity vs criterion validity;
convergent vs discriminant validity;
reliability vs validity;
protocol sensitivity vs construct instability;
ordinal scale vs interval interpretation;
probe accuracy vs causal role;
generalization vs mere replication;
confound control vs construct definition;
artifact vs informative null;
behavioral signal vs discriminant construct.

**Output for the day.**
You should be able to survive a skeptical question about “what validates a measure without ground truth?” without drifting into vagueness.

### Day 3

The goal is to own the specifically AI-welfare-adjacent parts of the argument without becoming anthropomorphic.

**Morning block one** should be the goal-relative screen and its rivals. Rebuild the logic of affect-neutral source task, extracted reward direction, reward reversal, transfer to unrelated affect-neutral tasks, and matched control directions. Then write one paragraph on why this is scientifically stronger than just staying inside pain/pleasure trade-off prompts. fileciteturn0file1 citeturn0academia0

**Morning block two** should be the emotion-concept rival. Learn the distinction among affect-reception, signed valence, and emotion-category, and practice saying why a probe that only detects “something affective is present” is not yet a valence probe. Also learn the sentence: “The strongest permitted claim is incremental goal-indexed signal beyond context-operative emotion-concept valence.” That sentence is one of the best in the whole deck. fileciteturn0file0 fileciteturn0file1 citeturn21academia0turn21academia3turn22academia3

**Afternoon block** should be introspection, probes, and causal standards. Practice short answers to:
Why is self-report secondary?
Why is patching confirmatory?
Why is steering exploratory?
Why do completeness and selectivity matter?
Why is refusal secondary in the goal-relative arm?
For that last one, the crisp answer is that arousal appears able to drive refusal through lexical mediation, so refusal shifts are weak discriminant evidence on their own. fileciteturn0file1 citeturn22academia0

**Evening block** should be adversarial Q&A with self-imposed interruption. Every 45 seconds, stop yourself and answer: “what is the simpler explanation?” That one habit will sharpen your Wednesday tone dramatically.

**Output for the day.**
You should be able to defend why the project is a **measurement-validity project** rather than a **consciousness-verdict project**.

### Day 4

The goal is presentation fluency, mentor-facing specificity, and funding-legible framing without salesiness.

**Morning block one** should be full talk rehearsal in three lengths: five, ten, and twenty minutes. The five-minute version is for conceptual compression. The twenty-minute version is for full deck control. The ten-minute version is the realistic live version.

**Morning block two** should be mentor ask rehearsal. Practice exactly three sentences: one sentence for why the project exists, one sentence for where the deepest uncertainty lies, and one sentence for the help you want from Caspar. If you cannot do this cleanly, your whole pitch will sound diffuse.

**Afternoon block** should be funding-legibility. Write a half-page answer to:
Why is this a good mentorship target now?
Why is this a fundable wedge and not a sprawling manifesto?
The best answer is: it targets a concrete, underdeveloped measurement problem; it yields valuable positive or negative results; it has a staged first paper; it uses open-weight models and preregistered boundaries; and it aims to produce reusable batteries, thresholds, and reporting discipline. fileciteturn0file1 fileciteturn0file2

**Evening block** should be “skeptical mentor interruption” rehearsal. Have a timer interrupt every 90 seconds with one of your hardest questions. Continue from the interruption without losing the thread.

**Output for the day.**
You should have one practiced line that sounds like you, not like a memo:
“I am not asking you to bless the ontological picture. I am asking for help stress-testing whether the measurement scaffold actually earns the construct language.”

## Rehearsal and likely Q&A system

### Rehearsal protocol

**Five-minute version.**
Use only five moves: field gap, construct and boundary, staged design, goal-relative licensing screen, mentor ask. No slide-level detail except one concrete example of a confound control. If you cannot explain the project in five minutes, you do not yet own it.

**Ten-minute version.**
Add one minute on the main behavioral battery, one minute on the emotion-concept rival, one minute on probes versus causal use, and one minute on why self-report stays secondary.

**Twenty-minute version.**
This is the deck-native version. Move slide by slide, but every slide gets a one-sentence function statement before the content. That prevents decorative wandering.

**Interrupted by skeptical mentor version.**
Rules: answer the interruption in under 45 seconds, explicitly state whether the question concerns construct validity, discriminant validity, causal validity, or scope, then return to the deck with “that’s why the next design move is X.” This preserves coherence.

### Likely Q&A bank

What follows is the high-probability bank, grouped as requested. I am optimizing for what a serious and somewhat skeptical mentor is most likely to ask.

#### Psychometrics and construct validity

| Likely question | Strong answer spine |
|---|---|
| “What validates this construct if there is no ground truth?” | “A nomological pattern, not one criterion. I need reliability across variants, discriminant success against measured rivals, internal generalization beyond text, and selective causal relevance before stronger labels are justified.” citeturn18view2turn23view0 |
| “Why isn’t this just benchmark engineering with nicer language?” | “Because the project is explicitly about score meaning and inference discipline, not just task performance. The measure is being stress-tested under alternate operationalizations and rival models.” fileciteturn0file1 |
| “What would count as an informative null?” | “A null after strong task-comprehension checks and after preregistered severity bounds would constrain the operationalization. A null under only one wording or format is usually not yet informative.” fileciteturn0file0 |
| “What is your nomological network here?” | “At minimum: controlled trade-off behavior, naturalistic utility rankings, internal representations, self-report as a secondary channel, causal generalization, and discriminant rivals like lexical sentiment, persona, emotion-concept valence, and evaluation awareness.” fileciteturn0file1 |

#### AI welfare and consciousness claim boundary

| Likely question | Strong answer spine |
|---|---|
| “Why is this not just consciousness research by another name?” | “Because the positive target is narrower and the negative boundary is explicit. The study aims to validate a functional measurement construct, not assign consciousness or moral status.” fileciteturn0file0 citeturn16view0 |
| “Why should anyone care if the result stops below sentience?” | “Because validated measurement is decision-relevant even under uncertainty. It improves both precaution against over-attribution and protection against under-attribution.” fileciteturn0file2 citeturn19academia2 |
| “What if functional valence is just a fancy name for reward?” | “Then the discriminant and transfer tests should expose that. The design is set up so the label is earned only if the narrower interpretation predicts more than reward tracking, confidence, or emotional semantics alone.” fileciteturn0file1 |

#### Behavioral measures

| Likely question | Strong answer spine |
|---|---|
| “Why use trade-off tasks at all?” | “Because they are the cleanest first test of polarity-sensitive, intensity-sensitive choice structure. But the design treats them as behavioral evidence, not the final word on goal-relativity.” fileciteturn0file1 citeturn21academia1 |
| “Why include naturalistic transcripts?” | “Because trade-off tasks can be too templated. The transcript arm asks whether the signal transports to milder, less stylized interactions.” fileciteturn0file1 |
| “Why are AI-specific scenarios exploratory?” | “Because shutdown, deletion, and successor prompts are unusually vulnerable to self-preservation and role-identity confounds.” fileciteturn0file1 |

#### Self-report and introspection

| Likely question | Strong answer spine |
|---|---|
| “Why trust any self-report here?” | “I don’t trust it as testimony. I treat it as a potentially informative but confounded measurement channel whose incremental validity must be shown over text-only and response-style confounds.” fileciteturn0file1 citeturn17view4turn19academia1turn19academia0 |
| “Why numeric ratings?” | “Because logit-based numeric ratings can preserve distributional information that greedy generations collapse, but they still need report-channel controls.” citeturn19academia1 |
| “How do you avoid over-reading scale differences?” | “I would be much more confident in directional and relational claims than in fine-grained magnitude claims, especially given evidence that ordered subjective scales need not reflect equal psychological intervals.” citeturn17view6turn17view5 |

#### Internal probes and causal interventions

| Likely question | Strong answer spine |
|---|---|
| “Why one probe per confound?” | “Because if I do not measure the rivals directly, I cannot know whether the candidate probe is just picking them up. The rival probes are part of construct definition, not optional cleanup.” fileciteturn0file1 |
| “What exactly does a successful probe show?” | “At best, extractability of that property from activations. Stronger claims require generalization and intervention.” citeturn17view1 |
| “Why is patching confirmatory and steering exploratory?” | “Patching uses matched clean/corrupt comparisons within task families and can support a more local causal-role claim. Steering is more fragile and can push activations off the prompt-reachable manifold.” citeturn17view2turn24academia0turn24academia1 |

#### Confounds: lexical sentiment, persona, sycophancy, social desirability, evaluation awareness

| Likely question | Strong answer spine |
|---|---|
| “Why isn’t this just lexical sentiment?” | “Because the design uses affect-free paraphrases, symbolic remapping, matched word counts, and strong frozen-text baselines. If the effect disappears there, the lexical explanation wins.” fileciteturn0file1 |
| “What makes persona such a serious rival?” | “Because persona vectors and related work show that report style and even choice expression can be strongly persona-conditioned.” fileciteturn0file1 |
| “Why worry so much about social desirability?” | “Because questionnaire-style responses can move toward socially preferred answers, and desirability-matched forced-choice formats can materially reduce that distortion.” citeturn19academia0 |
| “Could benchmark framing itself change the answer?” | “Yes. That is why evaluation awareness is an explicit confound axis rather than an implementation detail.” fileciteturn0file1 |

#### Study feasibility and compute

| Likely question | Strong answer spine |
|---|---|
| “Is this too large for a first study?” | “It would be too large if run monolithically. The strength of the design is that it is staged: pilot on a small open-weight set, gate internal work, and keep multiple extensions explicitly secondary.” fileciteturn0file1 |
| “Why open-weight first?” | “Because internal probes, hidden-state extraction, and patching are central to the validity question.” fileciteturn0file1 |
| “What gets cut first if compute is tight?” | “AI-specific holdout breadth, larger-model extensions, and deeper exploratory causal work. I would protect the core behavioral battery, discriminant structure, and minimal goal-relative screen.” fileciteturn0file1 |

#### Why this deserves mentoring and funding

| Likely question | Strong answer spine |
|---|---|
| “Why is this a good mentorship target rather than an overgrown wishlist?” | “Because the first paper can be cleanly scoped: validate measurement of a candidate construct under adversarial controls. It has reusable outputs even if the central construct weakens.” fileciteturn0file1 fileciteturn0file2 |
| “What is the actual wedge?” | “The wedge is measurement validity beneath AI-welfare discourse: batteries, rival models, thresholds, and interpretation discipline.” fileciteturn0file2 |
| “What do you need from a mentor rather than just more reading?” | “Help choosing the sharpest construct-validity standards, pruning the design without weakening it, and identifying where the current thresholds or rival sets are under-specified.” fileciteturn0file1 |

## Minimum viable resource set

This is the smallest resource set I would actually use over four days. Anything more and you risk knowledge-hoarding instead of talk control.

| Resource | Why it is worth your time | Extract exactly this | Safely skip |
|---|---|---|---|
| **Cronbach & Meehl 1955, “Construct Validity in Psychological Tests”** | It gives you the original language for validating constructs when there is no adequate criterion, and it introduces the nomological network. citeturn18view1turn18view2turn18view0 | No criterion, integrate evidence from many sources, nomological network, “you validate inferences, not a test in the abstract.” | Historical detail, examples unrelated to your case. |
| **Freiesleben 2026, “Establishing Construct Validity in LLM Capability Benchmarks Requires Nomological Networks”** | This is the best bridge text from psychometric validity language into LLM evaluation language. citeturn23view0 | The contrast between nomological, inferential, and causal accounts; why nomological framing is attractive for contested LLM constructs. | Extended philosophy sections beyond the framing argument. |
| **Butlin et al. 2023, “Consciousness in Artificial Intelligence”** | Useful not because your project is a consciousness paper, but because it gives the disciplined indicator-based stance that your claim boundary should echo. citeturn16view0 | Theory-heavy, internally focused, anti-behavior-only framing; no current AI systems are strong candidates under their analysis. | Detailed theory-by-theory exposition unless you personally want the background. |
| **Taking AI Welfare Seriously 2024** | Best short justification for why the problem matters without assuming today’s models already have welfare. citeturn19academia2 | The uncertainty-management frame: both over-attribution and under-attribution matter. | Governance recommendations not directly relevant to Wednesday. |
| **Han, Chalmers, Izmailov 2026, “How’s it going?”** | This is the scientific hinge for the revised design. citeturn0academia0 | Why affect-neutral source tasks, reward-direction extraction, reversal, and cross-task transfer matter. | Most of the model-specific implementation detail. |
| **Belinkov 2021, “Probing Classifiers”** | Best fast reminder that probes are not the thing itself. citeturn17view1 | Extractability versus use; methodological limitations of probes. | Survey breadth beyond the core warning. |
| **Heimersheim & Nanda 2024, “How to use and interpret activation patching”** | Gives you the vocabulary to sound sober about patching. citeturn17view2turn17view3 | What patching can and cannot show, metric choice, interpretive pitfalls. | Fine implementation details unless you are asked. |
| **Canby et al. 2024, “How Reliable are Causal Probing Interventions?”** | Best source for completeness, selectivity, and reliability. citeturn24academia1 | Definitions of completeness, selectivity, reliability; why there is a tradeoff. | Method-comparison detail. |
| **Martorell 2026, “Quantitative Introspection in Language Models”** | Important for defending why self-report remains in the design at all. citeturn19academia1 | Why logit-based reports outperform greedy numeric outputs; how a report channel might carry information without being testimony. | Stronger conclusions about introspection than your project needs. |
| **Okada et al. 2026, “Socially Desirable Responding in LLMs”** | This is likely directly relevant to Caspar’s concerns. citeturn19academia0 | That questionnaire responses can be distorted by social desirability and that desirability-matched forced choice attenuates it. | Full psychometric construction details. |
| **Keeling et al. 2024 and Bianco & Shiller 2026** | Together these explain why trade-off tasks are useful but insufficient. citeturn21academia1turn21academia2 | Keeling for behavioral trade-off logic; Bianco for decodability/causality caution in a mechanistic setting. | Broad policy discussion. |
| **Emotion-concept triad: Sofroniew et al. 2026, Keeman 2026, AIPsy-Affect 2026** | Use only if you need to tighten your understanding of the main rival. citeturn21academia0turn21academia3turn22academia3 | Affect-reception versus signed valence versus category; why keyword-free stimuli matter. | Most operational dataset detail. |

If you are truly pressed, the irreducible core is: **Cronbach & Meehl, Freiesleben, Han et al., Belinkov, Heimersheim & Nanda, Martorell, Okada**.

## Wednesday survival sheet

### One-paragraph project pitch

I’m working on a measurement-validity project for welfare-relevant AI signals. The narrow target is polarity-sensitive, goal-relative functional valence: a construct that would, if present, represent positive or negative value relative to the model’s current task or goal and influence behavior. The project does not aim to show consciousness, sentience, suffering, or moral patienthood. It asks a more disciplined question: whether current behavioral, report-channel, and internal indicators validly measure a common goal-indexed construct once we directly test rivals like lexical sentiment, emotion-concept valence, persona, social desirability, sycophancy, evaluation awareness, and protocol sensitivity. The design is staged so that stronger claims require distinct evidence types: behavioral stability first, then discriminant validity, then internal generalization, then a goal-relative transfer screen, and only then limited causal confirmation. fileciteturn0file0 fileciteturn0file1 fileciteturn0file2

### One-sentence claim boundary

“This project is trying to validate a welfare-relevant measurement construct under adversarial controls, not deliver a verdict about consciousness, sentience, suffering, or moral status.” fileciteturn0file0 fileciteturn0file1

### One-sentence mentor ask

“I have a working experimental scaffold and a clear validity frame, and I want your help stress-testing whether the psychometric assumptions, rival structure, and causal thresholds are actually strong enough to earn the construct language.” fileciteturn0file1 fileciteturn0file2

### Five concepts you must not misuse

| Concept | Safe usage |
|---|---|
| Construct validity | Evidence-backed warrant for an interpretation of a latent construct, not a synonym for “good study.” |
| Goal-relative functional valence | Narrow operational construct, not welfare or sentience itself. |
| Measurement invariance | Comparability of the construct across protocol/group conditions, not just “we paraphrased the prompt.” |
| Internal representation | At minimum, recoverable information in activations; stronger claims need more evidence. |
| Causal relevance | Reserved for intervention evidence with completeness/selectivity discipline, not for probe accuracy or steering alone. |

### Five questions you should ask Caspar

- “Given your work on subjective scale interpretation, how cautious should I be about numerical self-report even when I use logits rather than decoded numerals?” citeturn17view6turn17view5
- “What would you consider the minimum persuasive evidence that my measured channels are tracking a common construct rather than nearby but different constructs?” citeturn23view0turn18view2
- “Which rival explanations would you treat as highest priority beyond the ones already in the battery?” fileciteturn0file1
- “What would make a null result informative rather than merely inconclusive in the first study?” fileciteturn0file0
- “Where would you cut scope first to improve evidential sharpness without making the project trivial?” fileciteturn0file1

### Five red lines and overclaims to avoid

- Do not say the study measures welfare directly.
- Do not say self-report shows what the model “really feels.”
- Do not say a successful probe means the model uses that representation.
- Do not say steering success shows a naturally used computation.
- Do not say goal-relative transfer or reward reversal proves consciousness-relevant status. fileciteturn0file0 fileciteturn0file1 citeturn17view1turn24academia0turn24academia2

## Uncertainty ledger

### What you should be confident presenting

You should be confident that the project is a **measurement-validity program**, that its target construct is intentionally narrower than consciousness or sentience, that the revised design centers construct validity under no gold standard, that the **goal-relative screen** is the key non-circular licensing move, and that the deck has a serious confound architecture rather than a naïve “look, the model says it dislikes pain” framing. Those points are explicit across the deck and design documents. fileciteturn0file0 fileciteturn0file1 fileciteturn0file2

### What you are only partially understanding

You likely do not yet have full command of the exact statistical machinery behind Thurstonian utility estimation, variance partitioning, or the finer points of intervention metrics. That is okay. For Wednesday, you need the inferential role of those tools more than their implementation details. The other place where partial understanding is acceptable is the finer mechanistic distinction among affect-reception, signed valence, arousal, and emotion category, so long as you understand why the project splits them. fileciteturn0file1 citeturn21academia3turn22academia0turn22academia3

### What could be wrong in the project framing

The biggest scientific risk is that the construct is still too close to rival constructs such as emotional semantics, confidence, reward tracking, or persona-conditioned response style to support a stable “functional valence” label. Another risk is that the staged design remains too broad for a first paper, so the result is underpowered or conceptually diffuse even if each component is individually reasonable. A third risk is that self-report remains too contaminated to earn much weight even as a secondary channel. Those are all live worries, not cosmetic objections. fileciteturn0file1 fileciteturn0file2 citeturn17view4turn19academia0turn24academia2

### What would change your mind

I would materially downgrade confidence in the current framing if symbolic remapping and paraphrase controls wiped out the behavioral signal, if the candidate probes failed to beat strong text baselines on held-out families, if reward reversal failed to flip the goal-relative direction, or if causal interventions produced broad collateral changes that were comparable to the target shift. I would also downgrade the value of self-report sharply if it added no information beyond text-only prediction and showed strong instability under presentation-pressure versus neutral measurement conditions. fileciteturn0file0 fileciteturn0file1 citeturn24academia1turn24academia0

### What to ask Caspar specifically because you should not pretend to know it

Ask him what he would accept as the **minimum persuasive construct-validity pattern** for this domain. Ask how he thinks about **ordered response scales** and whether logit-based numeric reports genuinely solve enough of the scale problem to be worth keeping. Ask whether the current rival set is missing any **higher-priority report-channel confounds**. Ask where he thinks the current design is **over-instrumented** relative to the strength of its first claim. And ask what he would count as an **informative null** in each primary family, because that is an area where you do not want to bluff. citeturn17view4turn17view6turn17view5 fileciteturn0file0 fileciteturn0file1

### Constraints from your prompt that I may have underweighted or ignored

I could not fully verify every rendered slide in `deck.html` line by line from the live rendered presentation, so I relied on the deck source, the canonical study documents, and your pasted note file rather than a visual slide-by-slide inspection. I also did not retrieve every cited paper directly from the web; for a few items, especially some resources named inside your documents, I relied on the project documents’ own citation scaffolding rather than a direct source open. fileciteturn0file0 fileciteturn0file1 fileciteturn0file2 fileciteturn0file3
