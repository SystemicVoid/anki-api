---
description: Generate flashcards from content using EAT principles
---

# Task: Generate Anki Flashcards

Create high-quality Anki flashcards from the provided content following the **EAT Framework**:
- **E**ncoded: Understanding-based (not rote memorization)
- **A**tomic: One focused concept per card
- **T**imeless: Self-contained with sufficient context

## Arguments Handling

Parse the provided arguments:
- **URL**: If starts with `http`, scrape using `./scrape.sh <url>`
- **File path**: If file exists, read directly
- **Tags**: Use `--tags <tag1,tag2>` or auto-generate from topic

## Workflow

### 0. Prep the environment
- Install deps once with `uv sync`.
- Ensure Anki is running, then verify with `uv run anki ping` so downstream commands do not fail mid-run.

### 1. Acquire Content

**If URL provided:**
```bash
./scrape.sh <url>
# This saves to scraped/<filename>.md
```

**If file path provided:**
Read the file directly.

### 2. Analyze Content

Read and identify:
- Key concepts worth long-term retention
- Practical applications and use cases
- Common pitfalls or mistakes
- Important relationships between ideas

**Quality over quantity**: Aim for 5-10 excellent cards, not 50 mediocre ones.

### 3. Generate Flashcards

Use `src.schema` to create cards and keep all data in the `Flashcard` dataclass:

```python
from datetime import datetime

from src.schema import Flashcard, save_cards_to_json, validate_card

cards: list[Flashcard] = []

# Pattern 1: Conceptual Understanding
cards.append(
    Flashcard(
        front="Why does [concept] work/exist?",
        back="Clear explanation of the underlying reason",
        context="Additional context or related concepts",
        tags=["topic", "subtopic", "concept"],
        source="<url or file>"
    )
)

# Pattern 2: Practical Application
cards.append(
    Flashcard(
        front="When should you use [technique]?",
        back="Use cases and scenarios with reasoning",
        context="Contrast with alternatives if relevant",
        tags=["topic", "subtopic", "application"],
        source="<url or file>"
    )
)

# Pattern 3: Common Pitfalls
cards.append(
    Flashcard(
        front="What is a common mistake when [doing X]?",
        back="The mistake and why it happens",
        context="How to avoid or fix it",
        tags=["topic", "subtopic", "pitfalls"],
        source="<url or file>"
    )
)
```

### 4. Card Formatting Rules

**IMPORTANT**: Anki does not render Markdown. Use only plain text formatting:

**Structure:**
```
[Main answer text]

---

[Contextual information]
```

**Formatting rules:**
- **NO markdown** (no bold `**text**`, no italic `*text*`, no code blocks)
- **NO HTML tags** (no `<br>`, `<b>`, etc.)
- **Separator**: Use `---` with blank lines before and after (`\n\n---\n\n`)
- **Context section**: Start directly with content (no "Context:" label)
- **Line breaks**: Use plain newlines only

**Lists** (for visual clarity):
- **Ordered lists**: Use `1.\n2.\n3.` format with newlines between items
- **Unordered lists**: Use `-\n-\n-` format with newlines between items

**Example:**
```
Three factors converged:
1. Compute power increased, enabling training of massive models
2. Large-scale quality datasets became available
3. Algorithmic innovations like transformers (2017) enabled efficient parallel processing

---

Historical AI limitations weren't theoretical but practical. Modern systems like ChatGPT require all three elements. Quality matters as much as quantity for data—medical textbooks provide better training than equivalent volumes of Twitter posts.
```

**Answer vs. Context Balance:**
- Keep answers concise and focused on core concepts
- Move detailed explanations, examples, and caveats to context section
- Bias slightly towards context for verbose details

### 5. Apply EAT Validation

Ensure each card meets these criteria:

**Encoded:**
- Add context that explains the "why" not just the "what"
- Include enough information for future understanding

**Atomic:**
- Front MUST be a question (end with "?")
- One concept per card (no "and", "or", compound questions)
- Avoid vague starters like "What about..." or "Tell me about..."

**Timeless:**
- Replace vague pronouns ("this", "that") with specific nouns
- Avoid time-dependent references ("recently", "currently")
- Define abbreviations in context

Validate programmatically with `validate_card` to avoid missing rules:

```python
for card in cards:
    warnings = validate_card(card)
    errors = [w for w in warnings if w.severity == "error"]
    if errors:
        raise ValueError(
            f"Fix errors before saving {card.front!r}: "
            + "; ".join(str(w) for w in errors)
        )
    if warnings:
        print(f"EAT warnings for {card.front!r}:")
        for warning in warnings:
            print(f"  - {warning}")
```

### 6. Save and Report

```python
# Generate timestamp-based filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
topic = "<derive_from_content>"  # e.g., "python-decorators"
output_file = f"cards/{topic}_{timestamp}.json"

save_cards_to_json(cards, output_file)
```

**Report to user:**
- Number of cards generated
- Output file path
- Validation summary (any warnings or confirmations that all cards passed)
- Next step command: `uv run anki review <file>`

Encourage the user to run `uv run anki review <file>` (or `uv run anki add <file>` if they've already approved cards) so the CLI handles Anki-side validation and submission.

## Guidelines

**DO:**
- Focus on "why" and "when" questions (understanding)
- Use specific, concrete examples from the source
- Add meaningful context (think: will I understand this in 6 months?)
- Use hierarchical tags: `[domain, topic, type]`
- Keep questions focused and answers concise

**DON'T:**
- Create definition cards ("What is X?")
- Make list cards ("Name the 5 principles...")
- Copy-paste large blocks of text
- Create cards for every detail (be selective)
- Use vague or ambiguous language

## Reference Materials

- Full workflow guide: `examples/agent_workflow.md`
- EAT principles: https://leananki.com/creating-better-flashcards/
- Card schema: `src/schema.py`
- CLI tools: `uv run anki --help`

## Example Output

```
Generated 7 flashcards from: <source>
Saved to: cards/topic_20250114_143022.json

Cards created:
  • 3 conceptual understanding
  • 2 practical application
  • 2 common pitfalls

Next step:
  uv run anki review cards/topic_20250114_143022.json
```

**Note:** All cards will be reviewed by user before being added to Anki. Focus on quality and adherence to EAT principles.
