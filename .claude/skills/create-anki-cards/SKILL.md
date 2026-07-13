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

## Reference Materials (MUST READ)

Before generating any cards, read the relevant rules:

- **EAT Framework**: [rules/EAT_FRAMEWORK.md](rules/EAT_FRAMEWORK.md) - Full cognitive science rationale (always read)
- **Math Notation**: [rules/MATH_NOTATION.md](rules/MATH_NOTATION.md) - Anki MathJax rules (read if content contains math/formulas)
- **Images**: [rules/IMAGES.md](rules/IMAGES.md) - Media filename rules and how images render; the `storeMediaFile` + `updateNoteFields` transaction (read if a card needs a diagram, or when attaching an image to an already-added note)

## Input

$ARGUMENTS

## Workflow

### 0. Environment Check

```bash
uv run anki-api ping
uv run anki-api decks
uv run anki-api models
```

If Anki is not running, inform the user and ask if they want to continue anyway.

Use an existing deck and model returned by these diagnostics; do not infer, create, or rename a deck unless the user explicitly requests it. The current profile was verified on 2026-07-11 with all existing cards in its sole `Default` deck and uses the `Basic` model. Generated review cards should therefore target `Default`/`Basic` while that remains the live configuration.

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

### 3. Formatting Rules (CRITICAL)

**Anki does NOT render Markdown. Use plain text only.**

**Field separation:**
- **`back`**: Core answer, direct response to the question
- **`context`**: Elaborative encoding—schema connections, related concepts, edge cases

The `---` separator is added automatically when exporting to Anki Desktop (via `to_anki_note()`). In the web UI, context displays in a separate styled frame.

**Why this matters — two render paths.** Cards render on two surfaces with *different* rules, and only one authoring style is correct on both:
- **Anki desktop / AnkiDroid** (`render_anki_note` + `convert_newlines_to_html` in `src/anki_notes.py`): every `\n` becomes `<br>` — *everywhere, including inside `\( … \)` / `\[ … \]`* — and Front/Back/Context are passed through as raw, unescaped HTML (see `docs/adr/0001-card-content-trust-and-escaping.md`). So a literal `<b>`/`<i>` *would* render as HTML here.
- **Web review UI** (`web/frontend/src/components/MathJaxContent.tsx`): text is HTML-escaped, so a literal `<b>`, `<i>`, `<br>`, or an entity like `&mdash;` shows up as *literal characters*, not formatting. Only `\n` (→ `<br/>`) and MathJax spans are interpreted; a newline inside a math span is collapsed to a space.

**Formatting rules:**
- **NO markdown** (no `**bold**`, `*italic*`, code blocks) — Anki does not render it.
- **NO HTML tags** (`<b>`, `<i>`, `<u>`, `<br>`) and **NO HTML entities** (`&mdash;`, `&rarr;`, `&lt;`) — they render as literal text in the web review UI. Convey emphasis through structure (line breaks, plain-text lead-ins like `Analogy:` or `Note:`) and type special characters directly as Unicode (—, →, ×, ≤, σ) instead of entities.
- **Line breaks**: use plain newlines (`\n`) only — they become `<br>` in Anki and `<br/>` in the web UI.
- **NEVER put a newline inside `\( … \)` or `\[ … \]`** — keep every formula (delimiters and body) on ONE line. The Anki path converts `\n`→`<br>` unconditionally, and a `<br>` inside a math span breaks MathJax rendering. Use `\\` for row breaks inside a matrix, never a raw newline. See [rules/MATH_NOTATION.md](rules/MATH_NOTATION.md).
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

### 4. Generate and Save Cards

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
- For a useful dual-coded visual, store the image under `cards/media/` and list its safe filename in the optional `images` field. Do not add decorative or redundant images. To attach an image to a card that is **already in Anki**, see [rules/IMAGES.md](rules/IMAGES.md) (Case B — the `storeMediaFile` + `updateNoteFields` transaction).
- When exporting to Anki Desktop, `to_anki_note()` automatically combines back + context with `---` separator
- The web UI displays the `context` field in a separate styled frame
- Source will be auto-filled by the script if passed as argument

### 5. Report to User

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
- [ ] No HTML tags or entities (they render as literal text in the web review UI)
- [ ] Math uses `\( \)` not `$` (if applicable)
- [ ] No newline inside `\( \)` or `\[ \]` — each formula stays on one line
- [ ] Every non-obvious mathematical symbol is defined on the same card

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
