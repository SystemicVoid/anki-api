# EAT 2.0 Framework: Cognitive Science-Grounded Flashcard Design

## Introduction

The EAT Framework (Encoded, Atomic, Timeless) guides flashcard creation for durable, retrievable knowledge. Version 2.0 shifts from mechanical rules to cognitive science principles, empowering agents to reason about quality rather than pattern-match against heuristics.

### Why EAT 2.0?

The original EAT implementation used surface-level pattern matching:

| Old Rule | Why It Failed |
|----------|---------------|
| `len(back) < 30` → warn | Character count ≠ understanding |
| Contains "and"/"or" → warn | "Why do A and B both matter?" is a unified concept |
| Must end with "?" → error | Cloze deletions and fill-in-blank are valid |
| Contains "this"/"it" → warn | "What does `this` mean in JavaScript?" is clear |
| Contains uppercase → warn | "DNA", "API" are standard abbreviations |

**The shift**: From *pattern matching* to *semantic engineering*. This document teaches *why* patterns help or hurt learning so agents can reason about edge cases.

---

## Part 1: Cognitive Science Foundation

### 1.1 The Testing Effect (Retrieval Practice)

The act of retrieving information from memory is not passive assessment—it actively strengthens the memory trace. This is the foundation of spaced repetition.

**Key insight**: Not all retrieval is equal. Robert Bjork's "Desirable Difficulties" research shows that effortful retrieval produces superior long-term retention. Conditions that feel "easy" during study (massed practice, passive re-reading) often produce poor retention.

**Implication for cards**: Reject "easy" cards that rely on recognition. Create cards that require *generative* retrieval—forcing the brain to reconstruct the answer from semantic networks rather than recognizing it from surface cues.

### 1.2 The Minimum Information Principle

From Piotr Wozniak: "Simple items are easier to remember than complex ones." This is not brevity for brevity's sake—it's cognitive load management.

**Why complex cards fail**:
- Ambiguous feedback: Recalling 6/7 items—did you "know" the card?
- Interference: Forgetting one part causes entire card failure
- Algorithm degradation: SRS assumes binary memory traces

**Example of failure**:
```
Q: What are the inputs and outputs of the Krebs Cycle?
A: Inputs: Acetyl-CoA, NAD+, FAD, ADP. Outputs: CO2, NADH, FADH2, ATP.
```

This creates the "serial position effect"—primacy and recency dominate, middle items are forgotten.

### 1.3 Interference Theory

For lifelong learners with massive decks, interference is the primary threat to retention.

**Proactive Interference (PI)**: Old memories block retrieval of new ones.
- Example: A C++ programmer struggles to recall Python's `for` syntax because the C++ schema dominates.

**Retroactive Interference (RI)**: New memories degrade recall of old ones.
- Example: Learning a new phone number makes the old one inaccessible.

**The mixed-deck problem**: If you have cards for "The Civil War" (US) and "The Civil War" (Spain), and the cue is "When did the Civil War end?", the brain faces catastrophic interference.

**Solution**: Every card needs a unique "semantic fingerprint"—a cue that maps one-to-one with the target memory.

### 1.4 Context-Dependent Memory

Recall is superior when retrieval context matches encoding context. For digital learning, the "context" is the semantic information in the card itself.

**The trap**: Cards that depend on surrounding cards become "context-bound"—they can't be retrieved in real-world situations where that specific cue sequence is absent.

**Solution**: Cards must be contextually self-sufficient. Provide enough internal context to be answerable in isolation, yet not so much that the answer is given away.

---

## Part 2: The Three Principles Reinterpreted

### 2.1 Encoded → Elaborative Encoding

**Old interpretation**: "Add a context field"

**New interpretation**: Context deepens understanding via schema connections, not just reminders.

Elaborative encoding means connecting new information to existing knowledge structures. A card's context should:
- Link to related concepts the learner already knows
- Explain *why* the information matters
- Provide the "hook" that makes the fact retrievable

**Good context example**:
```
Front: Why does Python 3 require parentheses for print()?
Back: print() is a function in Python 3, not a statement.
Context: Python 2's "print x" was a special language statement, but this
made print inconsistent with other I/O operations. The change to a function
allows print() to be passed as an argument, used in comprehensions, and
extended with keyword arguments like "end" and "sep".
```

**Poor context**: Copy-pasting the source paragraph without synthesis.

### 2.2 Atomic → Database Normalization

**Old interpretation**: "No 'and' or 'or' in questions"

**New interpretation**: Apply database normalization to memory traces.

#### First Normal Form (1NF): The Atomicity Imperative

Every card tests exactly ONE discrete fact. Lists violate 1NF.

**Violation**:
```
Q: What is the primary carbon-based input of the Krebs Cycle?
A: Acetyl-CoA, NAD+, FAD, ADP
```

**1NF Compliant** (multiple cards):
```
Card 1: What is the primary carbon-based input of the Krebs Cycle? → Acetyl-CoA
Card 2: Which electron carrier is reduced to NADH in the Krebs Cycle? → NAD+
```

#### Second Normal Form (2NF): Contextual Self-Sufficiency

The answer must depend *fully* on the question, with all necessary context present.

**Violation**:
```
Q: What is the function of the nucleus?
A: It contains the cell's genetic material.
```

**Problem**: "Nucleus" exists in physics (atoms), biology (cells), and neuroanatomy (brain). The cue is ambiguous.

**2NF Compliant**:
```
Q: In Cell Biology, what is the primary function of the nucleus?
A: It stores genetic material/DNA
```

#### Third Normal Form (3NF): No Shortcut Hints

Remove "hints" that allow deducing the answer without actual retrieval.

**Violation**:
```
Q: What large organ in the abdomen filters blood and produces bile?
A: Liver
```

**Problem**: Learner triggers "Liver" from "produces bile" alone, bypassing "filters blood" and "abdomen" pathways. This creates shallow pattern matching.

**3NF Compliant** (separate cards for distinct learning objectives):
```
Card 1: Which organ produces bile? → Liver
Card 2: What is the primary blood-filtering organ in the upper right abdomen? → Liver
```

### 2.3 Timeless → Interference Management

**Old interpretation**: "No pronouns, no time-dependent references"

**New interpretation**: Semantic distinctiveness and comparison cards prevent interference.

**The real problem with pronouns**: Not that "this" is inherently bad, but that unclear referents create retrieval ambiguity. "What does `this` mean in JavaScript arrow functions?" is perfectly clear.

**When interference risk is high**, create comparison cards:

**Source text mentions Mitosis and Meiosis**:
```
Standard cards (risk interference):
Card 1: Define Mitosis → Cell division producing identical diploid cells
Card 2: Define Meiosis → Cell division producing unique haploid cells

Better: Add a Comparison Card
Q: Distinguish between Mitosis and Meiosis regarding daughter cell genetics.
A: Mitosis = Genetically Identical (Diploid); Meiosis = Genetically Unique (Haploid)
```

The comparison card encodes the *difference* as a primary feature, creating a "boundary" that prevents proactive and retroactive interference.

---

## Part 3: The 5 Golden Rules

These are executable principles for card generation.

### Rule 1: Atomicity (1NF)

> Each card tests exactly ONE discrete fact.

**Test**: If the answer contains "and", "or", or a list > 2 items, it likely violates atomicity and should be split.

**Exception**: When "and" unifies a single concept:
```
✓ "Why do both Python decorators and context managers use wrapper patterns?"
  → Tests understanding of a shared design principle, not two separate facts
```

### Rule 2: Contextual Self-Sufficiency (2NF)

> The question contains all necessary context to be answered in isolation.

**Implementation**:
- Explicit domain when terms are ambiguous: "In Python...", "In Cell Biology..."
- No pronouns that require external context
- But: technical pronouns like JavaScript's `this` keyword are fine when that IS the subject

### Rule 3: Interference Inhibition

> For similar concepts, generate Comparison Cards.

**Trigger**: Source text discusses concepts that could be confused:
- Mitosis/Meiosis
- TCP/UDP
- list/tuple
- proactive/retroactive interference

**Format**: "Distinguish between X and Y regarding Z."

### Rule 4: Cloze vs Q&A Selection

| Card Type | Use When | Example |
|-----------|----------|---------|
| **Cloze** | Atomic facts, syntax, exact wording | `print('Hello') is valid syntax in {{Python 3}}` |
| **Q&A** | Reasoning, "why"/"how" questions | `Why does Python 3 require parentheses for print?` |

**Cloze risk**: Shallow pattern matching—memorizing sentence shape instead of the fact.

**Mitigation**: Generate multiple cloze variations for important facts:
```
Card A: {{Mitochondria}} produce ATP.
Card B: Mitochondria produce {{ATP}}.
Card C: Mitochondria produce ATP via {{cellular respiration}}.
```

### Rule 5: Hierarchical Tagging

Tags are cognitive scaffolding, not just organization.

**Structure**:
- **Hierarchy** (the "where"): `#Domain::Subdomain::Topic`
- **Facet** (the "what"): `#Type::Fact`, `#Type::Concept`, `#Type::Procedure`, `#Type::Principle`

**Example**:
```
tags: ["medicine::cardiology::pharmacology", "type::procedure"]
```

**Why it matters**: Seeing `#medicine::cardiology` pre-activates the schema for heart, blood, vessels—reducing cognitive load for the specific question.

---

## Part 4: Edge Cases & Nuanced Decisions

### When "and" is Acceptable

**Split required** (tests multiple facts):
```
❌ "What are the inputs and outputs of the Krebs Cycle?"
```

**Unified concept** (tests one relationship):
```
✓ "Why do both HTTP and HTTPS use TCP instead of UDP?"
→ Tests understanding of TCP's reliability guarantees for web protocols
```

**Decision heuristic**: Does the "and" connect two independent facts, or does it frame a comparison/relationship that is itself the learning objective?

### When Pronouns are Acceptable

**Problematic** (ambiguous referent):
```
❌ "What does it return?" (what is "it"?)
❌ "Why did this happen?" (what is "this"?)
```

**Acceptable** (pronoun IS the subject):
```
✓ "What does `this` refer to in a JavaScript arrow function?"
✓ "In Python, what does `self` represent in a method definition?"
```

### When Abbreviations Need Context

**Needs context** (domain-specific):
```
"What does MVC stand for?" → Which MVC? (Model-View-Controller? or Mitral Valve Closure?)
Better: "In software architecture, what does MVC stand for?"
```

**Self-evident** (universal):
```
"How does DNA replication begin?" → DNA is unambiguous
"What port does HTTP use by default?" → HTTP is unambiguous in tech context
```

### Short Answers vs. Elaborated Answers

**Not a problem** (atomic fact):
```
Q: What is the default HTTP port?
A: 80
```

**Problem** (deceptive brevity):
```
Q: What is functional programming?
A: Using functions
→ This passes no character-count test but teaches nothing
```

**Quality test**: Does the answer enable the learner to apply the knowledge, or just recognize a keyword?

---

## Part 5: Self-Check Questions

Before saving each card, mentally verify:

### Atomicity
- [ ] Does this card test exactly one fact?
- [ ] If the answer has multiple parts, should they be separate cards?
- [ ] Would failing one part of the answer while knowing others give ambiguous feedback?

### Contextual Self-Sufficiency
- [ ] Could this card be answered correctly without seeing surrounding cards?
- [ ] Are ambiguous terms explicitly scoped? (e.g., "In Python...")
- [ ] Would my future self understand the question without re-reading the source?

### Interference Prevention
- [ ] Are there similar concepts that could be confused with this?
- [ ] If yes, have I created a comparison card?
- [ ] Is my cue specific enough to map one-to-one with the target memory?

### Retrieval Quality
- [ ] Does this card require generative retrieval, not just recognition?
- [ ] Am I testing understanding, not just keyword matching?
- [ ] Would someone who understood the concept answer correctly, while someone pattern-matching might fail?

---

## Part 6: Quick Reference

### Card Type Decision Tree

```
Is the learning objective a specific fact, syntax, or exact wording?
├─ Yes → Use Cloze
│        - Generate multiple cloze variations for important facts
│        - Watch for pattern-matching risk
└─ No  → Is it a "why" or "how" question requiring reasoning?
         ├─ Yes → Use Q&A
         └─ No  → Is it a comparison between similar concepts?
                  ├─ Yes → Use Comparison Card format
                  │        "Distinguish between X and Y regarding Z."
                  └─ No  → Default to Q&A
```

### The 5 Facets (Tag Types)

| Facet | Definition | Retrieval Mode |
|-------|------------|----------------|
| `#Type::Fact` | Discrete data (dates, constants, names) | Rote recall |
| `#Type::Concept` | Abstract definitions, theories | Semantic reconstruction |
| `#Type::Procedure` | Algorithms, "how-to" steps | Procedural memory |
| `#Type::Principle` | Heuristics, laws, mental models | Application logic |
| `#Type::Visual` | Diagrams, anatomy | Visuospatial processing |

---

## References

This framework synthesizes research from:

- Bjork, R.A. - Desirable Difficulties in Learning
- Wozniak, P. - Twenty Rules of Formulating Knowledge (SuperMemo)
- Roediger & Karpicke - The Testing Effect
- Matuschak, A. - Notes on Spaced Repetition Memory Systems
- Database Normalization theory (1NF, 2NF, 3NF)
- Interference Theory (Proactive and Retroactive Interference)
- Context-Dependent Memory research
- Dual Coding Theory (Paivio)

For the full research synthesis, see: `AI Flashcard Design Framework Research.md`
