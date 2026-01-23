---
name: create-anki-cards
description: Generate high-quality Anki flashcards using the EAT 2.0 framework. Use when asked to study, memorize, create cards, or make flashcards from a URL, video, file, or topic.
allowed-tools:
  - Read
  - Bash(uv:*)
  - Bash(python:*)
  - Bash(./scrape.sh:*)
  - Write
---

# Anki Flashcard Generator (EAT 2.0)

Generate high-quality flashcards following cognitive science principles.

**The EAT principles** (reinterpreted from cognitive science):
- **E**ncoded: Elaborative encoding—context creates schema connections for durable memory
- **A**tomic: Database normalization—one fact per card, contextually self-sufficient
- **T**imeless: Interference management—semantic distinctiveness, comparison cards for similar concepts

## Reference Materials (Read When Needed)

- **EAT Framework**: [rules/EAT_FRAMEWORK.md](rules/EAT_FRAMEWORK.md) - Full cognitive science rationale
- **Math Notation**: [rules/MATH_NOTATION.md](rules/MATH_NOTATION.md) - Anki MathJax rules (use `\( \)` not `$`)

## Input

$ARGUMENTS

## Workflow

### 0. Environment Check

```bash
uv run anki-api ping
```

If Anki is not running, inform the user and ask if they want to continue anyway.

### 1. Acquire Content

**Route by content type:**

| Input Type | Detection | Method |
|------------|-----------|--------|
| YouTube URL | Contains `youtube.com`, `youtu.be` | Python: `src.youtube.export_transcript_to_markdown()` |
| Web URL | Starts with `http` | Bash: `./scrape.sh <url>` |
| Local file | File path exists | Read tool directly |

**YouTube URLs** (youtube.com, youtu.be, shorts, embed):
```python
from pathlib import Path
from src.youtube import export_transcript_to_markdown

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

### 2. Analyze Content (Chain of Thought)

Before generating cards, analyze the content:

1. **Isolate Core Concepts**: List key entities, definitions, causal relationships
2. **Check for Math**: If complex math present, read [rules/MATH_NOTATION.md](rules/MATH_NOTATION.md)
3. **Schema Alignment**: Identify hierarchical domain (e.g., `#python::decorators`)
4. **Interference Scan**: Flag easily-confused concepts for comparison cards
5. **Quality Target**: Aim for 5-10 excellent cards, not 50 mediocre ones

### 3. The 5 Golden Rules

#### Rule 1: Atomicity (1NF)
Each card tests exactly ONE discrete fact.
- If answer has "and", "or", or a list > 2 items → split into multiple cards
- **Exception**: "and" that unifies a single concept is acceptable
  - Bad: "What are the inputs and outputs of X?" (two facts)
  - Good: "Why do both A and B use pattern X?" (one relationship)

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

#### Rule 5: Hierarchical Tagging
- **Hierarchy**: `#Domain::Subdomain::Topic` (schema activation)
- **Facet**: `#Type::Fact`, `#Type::Concept`, `#Type::Procedure`, `#Type::Principle` (metacognition)

Example: `tags=["python::decorators", "type::concept"]`

### 4. Formatting Rules (CRITICAL)

**Anki does NOT render Markdown. Use plain text only.**

**Field separation:**
- **`back`**: Core answer, direct response to the question
- **`context`**: Elaborative encoding—schema connections, related concepts, edge cases

The `---` separator is added automatically when exporting to Anki Desktop (via `to_anki_note()`). In the web UI, context displays in a separate styled frame.

**Formatting rules:**
- **NO markdown** (no `**bold**`, `*italic*`, code blocks)
- **NO HTML tags** (no `<br>`, `<b>`, etc.)
- **Line breaks**: Use plain newlines only
- **Math**: Use `\( inline \)` and `\[ display \]` (NOT `$` or `$$`)

**Lists** (for visual clarity):
```
Three factors converged:
1. First factor explanation
2. Second factor explanation
3. Third factor explanation
```

**Answer vs. Context Balance:**
- **Answer (`back`)**: Core concept, direct response (concise)
- **Context (`context`)**: Why it matters, related concepts, edge cases for future understanding

### 5. Generate and Save Cards

Generate JSON array and pipe to helper script:

```bash
cat << 'EOF' | uv run python .claude/skills/create-anki-cards/scripts/save_cards.py "TOPIC" "SOURCE_URL"
[
  {
    "front": "Why does [concept] work?",
    "back": "Clear explanation of the underlying reason",
    "context": "Schema connections for future understanding",
    "tags": ["domain::topic", "type::concept"],
    "source": ""
  }
]
EOF
```

**Important notes:**
- Use the `context` field for elaborative encoding (why it matters, related concepts, edge cases)
- The `back` field contains the core answer; `context` provides schema connections
- When exporting to Anki Desktop, `to_anki_note()` automatically combines back + context with `---` separator
- The web UI displays the `context` field in a separate styled frame
- Source will be auto-filled by the script if passed as argument

### 6. Report to User

After saving, report:
- Number of cards generated
- Card type breakdown (conceptual, procedural, comparison, etc.)
- Output file path
- Next step: `uv run anki-api review <file>`

## Card Patterns

### Pattern 1: Conceptual Understanding
```json
{
  "front": "Why does [concept] exist/work?",
  "back": "Clear explanation of the underlying reason",
  "context": "How this relates to concepts learner already knows",
  "tags": ["domain::topic", "type::concept"]
}
```

### Pattern 2: Practical Application
```json
{
  "front": "When should you use [technique] instead of [alternative]?",
  "back": "Use cases with reasoning",
  "context": "Trade-offs and edge cases",
  "tags": ["domain::topic", "type::principle"]
}
```

### Pattern 3: Comparison Card (Interference Prevention)
```json
{
  "front": "Distinguish between [X] and [Y] regarding [aspect]?",
  "back": "X = [characteristic]\nY = [characteristic]",
  "context": "When to use each, common confusion points",
  "tags": ["domain::topic", "type::concept"]
}
```

### Pattern 4: Procedural
```json
{
  "front": "In [context], how do you [accomplish task]?",
  "back": "Step or syntax",
  "context": "Why this approach works, gotchas to avoid",
  "tags": ["domain::topic", "type::procedure"]
}
```

## Quality Checklist

Before saving, verify each card:

**Atomicity**
- [ ] Does this test exactly one fact?
- [ ] Would failing part of the answer while knowing others give ambiguous feedback?

**Self-Sufficiency**
- [ ] Could this be answered without seeing surrounding cards?
- [ ] Are ambiguous terms explicitly scoped?

**Interference Prevention**
- [ ] Are there similar concepts that could be confused?
- [ ] If yes, did I create a comparison card?

**Retrieval Quality**
- [ ] Does this require generative retrieval, not just recognition?
- [ ] Am I testing understanding, not just keyword matching?

**Formatting**
- [ ] No markdown formatting (plain text only)
- [ ] Math uses `\( \)` not `$` (if applicable)

## Guidelines Summary

**DO:**
- Focus on "why" and "when" questions (understanding over facts)
- Use specific examples from source material
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
  - 3 conceptual understanding (why/when questions)
  - 2 procedural (syntax/how-to)
  - 2 comparison (interference prevention)

Hierarchical tags applied:
  - python::decorators (domain)
  - type::concept, type::procedure (facets)

Next step:
  uv run anki-api review cards/python-decorators_20250114_143022.json
```
