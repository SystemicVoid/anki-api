# Agent Workflow Guide

This guide explains how coding agents (Claude Code, Codex, etc.) should use the anki-api system to generate flashcards.

## Overview

The agent's role is to:
1. Process content (from URLs, files, or text)
2. Apply EAT 2.0 principles (cognitive science-grounded reasoning, not mechanical rules)
3. Output structured JSON that the user can review
4. Use CLI tools to interact with Anki

**The agent does NOT automatically add cards to Anki** - the user reviews and approves all cards.

**EAT 2.0 Philosophy**: Quality principles guide agent judgment. Mechanical pattern-matching (character counts, keyword detection) is removed. See `docs/EAT_FRAMEWORK.md` for the full cognitive science foundation.

## Complete Workflow Example

### Scenario: User wants flashcards from a web article

**User Request:**
```
"Create flashcards from this article about Python decorators:
https://realpython.com/primer-on-python-decorators/"
```

### Step 1: Scrape Content

**Agent Action:**
```bash
./scrape.sh https://realpython.com/primer-on-python-decorators/
```

**Output:**
```
✓ Scraped content saved to: scraped/primer-on-python-decorators.md
```

### Step 2: Read and Analyze Content

**Agent Action:**
```python
# Read the scraped markdown
with open('scraped/primer-on-python-decorators.md', 'r') as f:
    content = f.read()

# Agent analyzes content to identify:
# - Key concepts
# - Important definitions
# - Practical applications
# - Common pitfalls
# - Examples worth memorizing
```

### Step 3: Generate Flashcards

**Agent applies EAT 2.0 principles:**

#### Encoded → Elaborative Encoding
- Context creates schema connections, not just reminders
- Link new concepts to learner's existing knowledge
- Explain *why* the information matters

#### Atomic → Database Normalization
- **1NF**: One fact per card (split lists)
- **2NF**: Contextually self-sufficient (explicit domain for ambiguous terms)
- **3NF**: No hint shortcuts (don't allow deducing answer from surface cues)

#### Timeless → Interference Management
- Create comparison cards for easily-confused concepts
- Ensure unique "semantic fingerprint" for each cue
- Consider: could this card be confused with another?

**Key shift**: Reason about *why* patterns help/hurt learning, not mechanical rule-matching.

**Agent generates cards:**

```python
from src.schema import Flashcard, save_cards_to_json
from datetime import datetime

cards = [
    Flashcard(
        front="When should you use a Python decorator?",
        back="Use decorators to modify or extend function behavior without "
             "changing the function's code. Common use cases: logging, timing, "
             "authentication, caching, and validation.",
        context="Decorators are functions that take another function as argument "
                "and return a modified version. They use @ syntax.",
        tags=["python", "decorators", "design-patterns"],
        source="https://realpython.com/primer-on-python-decorators/"
    ),

    Flashcard(
        front="What is the syntax for applying a decorator in Python?",
        back="@decorator_name\ndef function_name():\n    pass",
        context="The @ symbol is syntactic sugar for: "
                "function_name = decorator_name(function_name)",
        tags=["python", "decorators", "syntax"],
        source="https://realpython.com/primer-on-python-decorators/"
    ),

    Flashcard(
        front="Why do decorators often use functools.wraps?",
        back="@functools.wraps preserves the original function's metadata "
             "(name, docstring, etc.) when creating a wrapper. Without it, "
             "the wrapped function loses its identity.",
        context="Example: @wraps(func) before defining the wrapper function",
        tags=["python", "decorators", "functools", "best-practices"],
        source="https://realpython.com/primer-on-python-decorators/"
    ),

    Flashcard(
        front="How do you create a decorator that accepts arguments?",
        back="Use a decorator factory - a function that returns a decorator. "
             "This creates three levels: factory(args) -> decorator(func) -> wrapper(*args)",
        context="Example: @repeat(num_times=3) requires a factory function "
                "that returns the actual decorator",
        tags=["python", "decorators", "advanced"],
        source="https://realpython.com/primer-on-python-decorators/"
    ),

    Flashcard(
        front="What is a common pitfall when decorating functions that return values?",
        back="Forgetting to return the result from the wrapper function. "
             "The wrapper must return wrapper_result = func(*args, **kwargs) "
             "and then return wrapper_result.",
        context="Without returning, the decorated function always returns None",
        tags=["python", "decorators", "common-mistakes"],
        source="https://realpython.com/primer-on-python-decorators/"
    ),
]

# Save to JSON
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f"cards/python-decorators_{timestamp}.json"
save_cards_to_json(cards, output_file)
print(f"Generated {len(cards)} flashcards -> {output_file}")
```

### Step 4: Inform User

**Agent Message:**
```
Generated 5 flashcards from the Python decorators article.
Saved to: cards/python-decorators_20250114_143022.json

To review and add to Anki:
  uv run anki-api review cards/python-decorators_20250114_143022.json
```

### Step 5: User Reviews Cards

**User runs:**
```bash
uv run anki-api review cards/python-decorators_20250114_143022.json
```

**Interactive review process:**
```
[1/5]
Front: When should you use a Python decorator?
Back: Use decorators to modify or extend function behavior...
Context: Decorators are functions that take another function...
Tags: python, decorators, design-patterns

⚠️ Question might be compound (contains ' and '). Consider splitting.

(a)pprove  (e)dit  (s)kip  (q)uit: a
✓ Card added to Anki (ID: 1234567890)

[2/5] ...
```

## Guidelines for Agents

### Content Analysis Strategy

1. **Scan for Key Concepts**
   - Look for definitions, explanations, examples
   - Identify "why", "when", "how" information
   - Note practical applications

2. **Prioritize Understanding**
   - Focus on conceptual understanding, not rote facts
   - Create "why" and "when" questions, not just "what"
   - Link concepts together

3. **Avoid Over-Generating**
   - Quality over quantity (5-10 good cards > 50 mediocre ones)
   - Don't create cards for every detail
   - Focus on information worth remembering long-term

### Card Creation Patterns

#### Pattern 1: Conceptual Understanding
```python
Flashcard(
    front="Why does [concept] work/exist?",
    back="Explanation of the underlying reason",
    context="Additional context or example"
)
```

#### Pattern 2: Practical Application
```python
Flashcard(
    front="When should you use [technique/tool]?",
    back="Use cases and scenarios",
    context="Contrasting with alternatives"
)
```

#### Pattern 3: Common Mistakes
```python
Flashcard(
    front="What is a common pitfall when [doing X]?",
    back="The mistake and why it happens",
    context="How to avoid or fix it"
)
```

#### Pattern 4: Syntax/API
```python
Flashcard(
    front="How do you [accomplish task] in [language/framework]?",
    back="Code example or syntax",
    context="When/why you'd use this"
)
```

### Tagging Strategy (EAT 2.0)

Tags serve as **cognitive scaffolding**—they prime the brain's schema before retrieval.

**Two-tier structure:**
1. **Hierarchy** (the "where"): `#Domain::Subdomain::Topic`
2. **Facet** (the "what"): `#Type::Fact`, `#Type::Concept`, `#Type::Procedure`, `#Type::Principle`

**Example:**
```python
tags=["python::decorators", "type::concept"]
```

**The 5 Facets:**
| Facet | Use When | Retrieval Mode |
|-------|----------|----------------|
| `type::fact` | Discrete data (dates, constants) | Rote recall |
| `type::concept` | Abstract definitions, theories | Semantic reconstruction |
| `type::procedure` | Algorithms, "how-to" steps | Procedural memory |
| `type::principle` | Heuristics, mental models | Application logic |
| `type::comparison` | Similar concepts (interference risk) | Discrimination |

**Why it matters**: Seeing `#python::decorators` pre-activates the schema for functions, wrapping, and @ syntax—reducing cognitive load for the specific question.

### Context Guidelines

Context should answer: "Will I understand this question in 6 months without re-reading the article?"

**Good context examples:**
- Brief explanation of related concepts
- Alternative terminology
- Common use cases
- Links to related concepts

**Poor context:**
- Copy-pasting large blocks of text
- Vague references ("see above")
- Information already in the question

### Source Attribution

Always include the source URL or file path:
```python
source="https://example.com/article"
source="scraped/article.md"  # If no URL available
```

## Common Agent Tasks

### Task 1: Generate from Scraped Content

```python
from src.schema import Flashcard, save_cards_to_json, load_cards_from_json

# Read content
with open('scraped/article.md', 'r') as f:
    content = f.read()

# Generate cards (agent implements logic)
cards = generate_flashcards_from_content(content)

# Save
save_cards_to_json(cards, 'cards/output.json')
```

### Task 2: Generate from Local File

```python
# Read PDF, MD, TXT, etc.
with open('/path/to/document.txt', 'r') as f:
    content = f.read()

# Generate cards
cards = []  # Agent creates cards
save_cards_to_json(cards, 'cards/document.json')
```

### Task 3: Generate from User Text

**User provides text directly:**

```python
user_text = """
[User pastes or describes content]
"""

cards = []  # Agent creates cards from text
save_cards_to_json(cards, 'cards/user-content.json')
```

### Task 4: Verify Anki Connection

Before generating cards, check Anki is available:

```python
from src.anki_client import AnkiClient, AnkiConnectError

client = AnkiClient()
try:
    if not client.ping():
        print("⚠️ Warning: Cannot connect to Anki. Make sure Anki is running.")
except AnkiConnectError as e:
    print(f"⚠️ Anki connection error: {e}")
```

### Task 5: List Available Decks

Help user choose a deck:

```python
from src.anki_client import AnkiClient

client = AnkiClient()
decks = client.get_decks()
print("Available decks:")
for deck in decks:
    print(f"  - {deck}")
```

## Quality Checklist (EAT 2.0)

Before saving cards, reason through these questions:

### Atomicity (1NF)
- [ ] Does this card test exactly ONE fact?
- [ ] Would failing part of the answer while knowing others give ambiguous feedback?
- [ ] If answer contains "and" or a list, should it be split?
  - **Exception**: "and" that unifies a single concept is OK ("Why do A and B both use pattern X?")

### Contextual Self-Sufficiency (2NF)
- [ ] Could this card be answered without seeing surrounding cards?
- [ ] Are ambiguous terms explicitly scoped? ("In Python...", "In Cell Biology...")
- [ ] Would my future self understand the question without re-reading the source?

### Interference Prevention
- [ ] Are there similar concepts that could be confused with this?
- [ ] If yes, did I create a comparison card?
- [ ] Is my cue specific enough to map one-to-one with the target memory?

### Retrieval Quality
- [ ] Does this require generative retrieval, not just recognition?
- [ ] Am I testing understanding, not just keyword matching?
- [ ] Would someone who understood the concept answer correctly, while someone pattern-matching might fail?

### Structural
- [ ] Back directly answers the front
- [ ] Context creates schema connections (not just copy-pasted text)
- [ ] Tags use hierarchical format (`domain::topic`, `type::concept`)
- [ ] Source is attributed

## Example: Processing Multiple Articles

**User Request:**
```
"Create flashcards from these 3 articles about async Python:
- https://example.com/async-basics
- https://example.com/asyncio-patterns
- https://example.com/async-pitfalls"
```

**Agent Workflow:**

```bash
# Scrape all articles
./scrape.sh https://example.com/async-basics
./scrape.sh https://example.com/asyncio-patterns
./scrape.sh https://example.com/async-pitfalls
```

```python
from src.schema import Flashcard, save_cards_to_json

all_cards = []

# Process each file
files = [
    'scraped/async-basics.md',
    'scraped/asyncio-patterns.md',
    'scraped/async-pitfalls.md',
]

for file in files:
    with open(file, 'r') as f:
        content = f.read()

    # Generate cards for this file
    cards = generate_cards_from_content(content)
    all_cards.extend(cards)

# Save combined set
save_cards_to_json(all_cards, 'cards/async-python-complete.json')
print(f"Generated {len(all_cards)} flashcards from {len(files)} articles")
```

## Tips for Agents

1. **Read the source material carefully** - Don't hallucinate information
2. **Focus on "why" and "when"** - Not just "what"
3. **Use examples from the source** - They help with context
4. **Keep questions focused** - One concept per card
5. **Add meaningful context** - Think 6 months in the future
6. **Tag consistently** - Helps with organization
7. **Validate before saving** - Run through quality checklist

## Anti-Patterns to Avoid

### ❌ Don't Create Definition Cards
```python
# Bad
front="What is a decorator?"
back="A decorator is a function that modifies another function"
```

Instead, focus on understanding:
```python
# Good
front="Why would you use a decorator instead of directly modifying a function?"
back="Decorators allow reusable behavior without changing the original function's code..."
```

### ❌ Don't Create List Cards (1NF Violation)
```python
# Bad - Serial position effect, ambiguous feedback
front="What are the inputs of the Krebs Cycle?"
back="Acetyl-CoA, NAD+, FAD, ADP"
```

Instead, create atomic cards:
```python
# Good - Each fact can be scheduled independently
front="What is the primary carbon-based input of the Krebs Cycle?"
back="Acetyl-CoA"

front="Which electron carrier is reduced to NADH in the Krebs Cycle?"
back="NAD+"
```

### ❌ Don't Allow Ambiguous Cues (2NF Violation)
```python
# Bad - "nucleus" exists in physics, biology, neuroanatomy
front="What is the function of the nucleus?"
back="It contains the cell's genetic material"
```

Instead, provide explicit context:
```python
# Good - Unique semantic fingerprint
front="In Cell Biology, what is the primary function of the nucleus?"
back="It stores genetic material/DNA"
```

### ❌ Don't Ignore Interference Risk
```python
# Bad - Creates competing memory traces
# Card 1: Define Mitosis → ...
# Card 2: Define Meiosis → ...
# User will confuse these!
```

Instead, add a comparison card:
```python
# Good - Encodes the difference as primary feature
front="Distinguish between Mitosis and Meiosis regarding daughter cell genetics?"
back="Mitosis = Genetically Identical (Diploid); Meiosis = Genetically Unique (Haploid)"
```

### ❌ Don't Copy-Paste Large Blocks
```python
# Bad
back="[5 paragraphs of text from article]"
```

Instead, summarize and synthesize:
```python
# Good
back="Key points: [concise summary in your own words]"
context="Schema connection—how this relates to concepts learner already knows"
```

### ✅ When "and" IS Acceptable
```python
# This is FINE - tests a unified relationship, not two separate facts
front="Why do both Python decorators and context managers use wrapper patterns?"
back="Both need to execute code before/after an operation while preserving..."

# Agent reasoning: The 'and' compares two related concepts sharing a pattern.
# The card tests understanding of *why* they're similar - a unified concept.
# No split needed.
```

## Conclusion

The agent's role is to be a **cognitive tutor** that:
- Processes content intelligently
- Applies EAT 2.0 principles (cognitive science, not mechanical rules)
- Reasons about each card's learning value
- Generates high-quality card proposals with proper interference management

The **user maintains control** through the review process, ensuring every card added to Anki meets their standards.

**EAT 2.0 shift**: From pattern-matching rules to cognitive science reasoning. The agent doesn't blindly warn about "and" or "this"—it reasons about whether patterns help or hurt learning in each specific context.

**Reference**: See `docs/EAT_FRAMEWORK.md` for the full cognitive science foundation.
