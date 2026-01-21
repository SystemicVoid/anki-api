---
description: Generate flashcards from content using EAT principles
---

# Task: Generate Anki Flashcards (EAT 2.0)

Create high-quality Anki flashcards from the provided content following the **EAT 2.0 Framework**—a cognitive science-grounded approach to knowledge encoding.

**The EAT principles** (reinterpreted from cognitive science):
- **E**ncoded: Elaborative encoding—context creates schema connections for durable memory
- **A**tomic: Database normalization—one fact per card, contextually self-sufficient
- **T**imeless: Interference management—semantic distinctiveness, comparison cards for similar concepts

**Reference**: See `docs/EAT_FRAMEWORK.md` for full cognitive science rationale.

## Arguments Handling

Parse the provided arguments:
- **URL**: If starts with `http`, route based on URL type (see Content Acquisition)
- **File path**: If file exists, read directly with the Read tool
- **Tags**: Use `--tags <tag1,tag2>` or auto-generate from topic

## Workflow

### 0. Prep the Environment
- Install deps once with `uv sync`.
- Ensure Anki is running, then verify with `uv run anki-api ping` so downstream commands do not fail mid-run.

### 1. Acquire Content

**Route by content type:**

| Input Type | Detection | Method |
|------------|-----------|--------|
| YouTube URL | Contains `youtube.com`, `youtu.be` | Python: `src.youtube` module |
| Web URL | Starts with `http` | Bash: `./scrape.sh <url>` |
| Local file | File path exists | Read tool directly |

**YouTube URLs** (youtube.com, youtu.be, shorts, embed):
```python
from pathlib import Path
from src.youtube import export_transcript_to_markdown

# IMPORTANT: output_dir must be a Path object, not a string
output_path = export_transcript_to_markdown(
    "https://www.youtube.com/watch?v=VIDEO_ID",
    Path("scraped")
)
print(output_path)  # e.g., scraped/youtube_VIDEO_ID_20250120_143022.md
```

**Web URLs** (articles, documentation, blogs):
```bash
./scrape.sh <url>
# Saves to scraped/<filename>.md
```

**Local files:**
Use the Read tool directly—no preprocessing needed.

### 2. Semantic Decomposition (Chain of Thought)

Before generating cards, analyze the content systematically:

1. **Isolate Core Concepts**: List key entities, definitions, and causal relationships
2. **Schema Alignment**: Identify the hierarchical domain (e.g., `#python::decorators`)
3. **Atomization Check**: Break complex sentences into atomic propositions
4. **Interference Scan**: Flag concepts easily confused with others (e.g., list vs tuple, TCP vs UDP) for Comparison Cards

**Quality over quantity**: Aim for 5-10 excellent cards, not 50 mediocre ones.

### 3. Apply the 5 Golden Rules

#### Rule 1: Atomicity (1NF)
Each card tests exactly ONE discrete fact.
- If answer has "and", "or", or a list > 2 items → split into multiple cards
- **Exception**: "and" that unifies a single concept is acceptable
  - ✗ "What are the inputs and outputs of X?" (two facts)
  - ✓ "Why do both A and B use pattern X?" (one relationship)

#### Rule 2: Contextual Self-Sufficiency (2NF)
The question contains all necessary context to be answered in isolation.
- Explicit domain for ambiguous terms: "In Python...", "In Cell Biology..."
- No pronouns requiring external context (but technical pronouns like JS's `this` are fine when that IS the subject)

#### Rule 3: Interference Inhibition
For similar concepts, generate Comparison Cards.
- Format: "Distinguish between X and Y regarding Z."
- Triggers: Mitosis/Meiosis, TCP/UDP, list/tuple, proactive/retroactive interference

#### Rule 4: Cloze vs Q&A Selection

| Card Type | Use When | Example |
|-----------|----------|---------|
| **Cloze** | Atomic facts, syntax, exact wording | `print() is valid syntax in {{Python 3}}` |
| **Q&A** | Reasoning, "why"/"how" questions | `Why does Python 3 require parentheses for print?` |

**Note**: For important facts, consider multiple cloze variations to prevent pattern-matching:
```
Card A: {{Mitochondria}} produce ATP.
Card B: Mitochondria produce {{ATP}}.
```

#### Rule 5: Hierarchical Tagging
- **Hierarchy**: `#Domain::Subdomain::Topic` (schema activation)
- **Facet**: `#Type::Fact`, `#Type::Concept`, `#Type::Procedure`, `#Type::Principle` (metacognition)

Example: `tags=["python::decorators", "type::concept"]`

### 4. Generate Flashcards

> **Execution Note**: For card generation with multiline strings, use the **Write tool** to create a temporary Python script, then execute it. Avoid bash heredocs (`<< 'EOF'`) with Python multiline strings—the shell's line-by-line parsing conflicts with Python's triple-quoted strings.

Use `src.schema` to create cards:

```python
from datetime import datetime

from src.schema import Flashcard, save_cards_to_json

cards: list[Flashcard] = []

# Pattern 1: Conceptual Understanding
cards.append(
    Flashcard(
        front="Why does [concept] work/exist?",
        back="Clear explanation of the underlying reason",
        context="Schema connections—how this relates to concepts learner already knows",
        tags=["domain::topic", "type::concept"],
        source="<url or file>"
    )
)

# Pattern 2: Practical Application
cards.append(
    Flashcard(
        front="When should you use [technique] instead of [alternative]?",
        back="Use cases with reasoning",
        context="Trade-offs and edge cases",
        tags=["domain::topic", "type::principle"],
        source="<url or file>"
    )
)

# Pattern 3: Comparison Card (for interference prevention)
cards.append(
    Flashcard(
        front="Distinguish between [X] and [Y] regarding [aspect]?",
        back="X = [characteristic]; Y = [characteristic]",
        context="When to use each, common confusion points",
        tags=["domain::topic", "type::concept"],
        source="<url or file>"
    )
)

# Pattern 4: Syntax/Procedure (Cloze-style in Q&A format)
cards.append(
    Flashcard(
        front="In Python, what decorator preserves a wrapped function's metadata?",
        back="@functools.wraps(func)",
        context="Without this, the wrapper function loses __name__, __doc__, etc.",
        tags=["python::decorators", "type::procedure"],
        source="<url or file>"
    )
)
```

### 5. Card Formatting Rules

**IMPORTANT**: Anki does not render Markdown. Use only plain text formatting.

**Structure:**
```
[Main answer text]

---

[Contextual information]
```

**Formatting rules:**
- **NO markdown** (no `**bold**`, `*italic*`, code blocks)
- **NO HTML tags** (no `<br>`, `<b>`, etc.)
- **Separator**: Use `---` with blank lines before and after (`\n\n---\n\n`)
- **Context section**: Start directly with content (no "Context:" label)
- **Line breaks**: Use plain newlines only

**Lists** (for visual clarity):
```
Three factors converged:
1. First factor explanation
2. Second factor explanation
3. Third factor explanation

---

Contextual information explaining why these factors matter together.
```

**Answer vs. Context Balance:**
- **Answer**: Core concept, direct response (concise)
- **Context**: Elaborative encoding—why it matters, related concepts, edge cases

### 6. Self-Check Before Saving

For each card, verify:

**Atomicity**
- Does this test exactly one fact?
- Would failing part of the answer while knowing others give ambiguous feedback?

**Self-Sufficiency**
- Could this be answered without seeing surrounding cards?
- Are ambiguous terms explicitly scoped?

**Interference Prevention**
- Are there similar concepts that could be confused?
- If yes, did I create a comparison card?

**Retrieval Quality**
- Does this require generative retrieval, not just recognition?
- Am I testing understanding, not just keyword matching?

### 7. Save and Report

**Execution pattern** (avoids heredoc issues):

1. **Write** the complete Python script to a temp file:
```python
# File: cards/_generate_temp.py
from datetime import datetime
from src.schema import Flashcard, save_cards_to_json

cards = []

cards.append(
    Flashcard(
        front="...",
        back="""Multiline content works fine
in a proper .py file.

---

Context section here.""",
        context="",
        tags=["domain::topic", "type::concept"],
        source="<url>"
    )
)

# ... more cards ...

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
topic = "topic-name"  # e.g., "python-decorators"
output_file = f"cards/{topic}_{timestamp}.json"
save_cards_to_json(cards, output_file)
print(f"Saved to: {output_file}")
print(f"Total cards: {len(cards)}")
```

2. **Execute** the script:
```bash
uv run python cards/_generate_temp.py
```

3. **Clean up** the temp file:
```bash
rm cards/_generate_temp.py
```

**Report to user:**
- Number of cards generated
- Card type breakdown (conceptual, procedural, comparison, etc.)
- Output file path
- Next step: `uv run anki-api review <file>`

## Guidelines Summary

**DO:**
- Focus on "why" and "when" questions (understanding over facts)
- Use specific examples from the source material
- Add context that creates schema connections (will I understand this in 6 months?)
- Create comparison cards for easily-confused concepts
- Use hierarchical tags: `["domain::topic", "type::concept"]`

**DON'T:**
- Create definition cards ("What is X?" → focus on "Why use X?")
- Make list cards ("Name the 5 principles..." → separate cards)
- Copy-paste large blocks (summarize and synthesize)
- Generate cards for every detail (be selective—quality over quantity)
- Apply mechanical rules blindly (reason about each card's learning value)

## Example Output

```
Generated 7 flashcards from: <source>
Saved to: cards/python-decorators_20250114_143022.json

Cards created:
  • 3 conceptual understanding (why/when questions)
  • 2 procedural (syntax/how-to)
  • 2 comparison (interference prevention)

Hierarchical tags applied:
  • python::decorators (domain)
  • type::concept, type::procedure (facets)

Next step:
  uv run anki-api review cards/python-decorators_20250114_143022.json
```

## Reference Materials

- Full framework guide: `docs/EAT_FRAMEWORK.md`
- Cognitive science research: `AI Flashcard Design Framework Research.md`
- Card schema: `src/schema.py`
- CLI tools: `uv run anki-api --help`
