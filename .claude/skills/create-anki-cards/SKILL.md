---
name: create-anki-cards
description: Generate high-quality Anki flashcards using the EAT 2.0 framework. Use when asked to study, memorize, create cards, or make flashcards from a URL, video, file, or topic.
allowed-tools:
  - Read
  - Bash(uv:*)
  - Bash(python:*)
  - Bash(./scrape.sh:*)
  - Write
  - oracle
---

# Anki Flashcard Generator (EAT 2.0)

Generate high-quality flashcards following cognitive science principles.

**The EAT principles** (reinterpreted from cognitive science):
- **E**ncoded: Elaborative encoding—context creates schema connections for durable memory
- **A**tomic: Database normalization—one fact per card, contextually self-sufficient
- **T**imeless: Interference management—semantic distinctiveness, comparison cards for similar concepts

## Reference Materials (MUST READ)

Before generating any cards, read the relevant rules:

- **EAT Framework**: [rules/EAT_FRAMEWORK.md](rules/EAT_FRAMEWORK.md) - Full cognitive science rationale (always read)
- **Math Notation**: [rules/MATH_NOTATION.md](rules/MATH_NOTATION.md) - Anki MathJax rules (read if content contains math/formulas)

## Input

$ARGUMENTS

## Workflow

### 0. Environment Check

```bash
uv run anki-api ping
```

If Anki is not running, inform the user and ask if they want to continue anyway.

### 1. Read Rules

**MANDATORY**: Read the EAT framework before generating cards:
```
Read: rules/EAT_FRAMEWORK.md
```

**If content contains math** (formulas, equations, vectors, matrices):
```
Read: rules/MATH_NOTATION.md
```

### 2. Acquire Content

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

### 3. Generate Cards via Oracle (REQUIRED)

**ALWAYS use the oracle tool for card generation.** The oracle provides deeper reasoning about card quality, interference prevention, and schema connections.

Call the oracle with:
- **task**: Generate 6-10 exceptional Anki flashcards applying EAT 2.0 framework rigorously
- **context**: Include the source content summary and any domain-specific notes
- **files**: Include the scraped/source file path

**Oracle prompt template:**
```
Generate 6-10 exceptional Anki flashcards from this content. Apply EAT 2.0 framework rigorously.

REQUIREMENTS:
1. Focus on deep conceptual understanding (why/when), not definitions
2. Each card must be atomic (1NF) and contextually self-sufficient (2NF)
3. Create comparison cards where interference risk exists
4. Context field should create schema connections for 6-month future recall
5. [If math content] Use proper MathJax: \\( \\) for inline, \\[ \\] for display
   - Vectors: \\mathbf{v}, basis: \\hat{\\imath}, \\hat{\\jmath}, \\hat{k}
   - JSON-escape all backslashes

Output JSON array with: front, back, context, tags (hierarchical + type facet)

KEY CONCEPTS TO COVER:
[List 4-6 core concepts from the source material]
```

**Why oracle is mandatory:**
- Deeper reasoning about what makes each card valuable for long-term retention
- Better interference detection between similar concepts
- Higher quality schema connections in context fields
- Consistent application of EAT cognitive science principles

### 4. The 5 Golden Rules (Reference for Oracle)

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

### 5. Formatting Rules (CRITICAL)

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

### 6. Save Cards

Take the JSON array from the oracle's response and pipe to helper script:

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

### 7. Report to User

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
