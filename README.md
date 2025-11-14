# Anki API - Agent-Assisted Flashcard Generation

A simple, agent-friendly system for generating high-quality Anki flashcards from web content and documents using coding agents like Claude Code.

## Philosophy

This tool follows the **EAT Framework** for creating effective flashcards:

- **E**ncoded: Learn before you memorize (understand first)
- **A**tomic: Specific, focused questions
- **T**imeless: Design for your future self (self-contained)

Based on principles from [LeanAnki](https://leananki.com/creating-better-flashcards/).

## Features

- 🤖 **Agent-assisted**: Designed for use with coding agents (no automated LLM calls)
- 🔍 **Web scraping**: Integrate with crawl4ai for clean markdown extraction
- ✅ **Review workflow**: Approve/edit/skip cards before adding to Anki
- 🎯 **EAT validation**: Automatic checks for flashcard quality principles
- 📦 **Simple dependencies**: Just requests, pydantic, and click
- 🔌 **AnkiConnect integration**: Direct API access to Anki Desktop

## Prerequisites

1. **Anki Desktop** with **AnkiConnect** plugin installed
   - Download: https://apps.ankiweb.net/
   - AnkiConnect: https://ankiweb.net/shared/info/2055492159

2. **Python 3.11+** (via `uv`)

3. **crawl4ai** (for web scraping)
   - Already installed at `/home/hugo/Documents/Engineering/crawl4ai`

## Installation

```bash
cd /home/hugo/Documents/Engineering/anki-api

# Install dependencies
uv sync

# Verify Anki connection (make sure Anki is running)
uv run anki ping
```

## Quick Start

### 1. Scrape Web Content

```bash
# Scrape a URL to markdown
./scrape.sh https://leananki.com/creating-better-flashcards/

# Output: scraped/creating-better-flashcards.md
```

### 2. Generate Flashcards (with Agent)

Ask your coding agent (Claude Code, Codex, etc.):

```
"Generate flashcards from scraped/creating-better-flashcards.md
following EAT principles. Save to cards/eat-framework.json"
```

The agent will:
1. Read the markdown content
2. Identify key concepts
3. Create atomic, question-based cards
4. Add appropriate context and tags
5. Save to JSON file

### 3. Review and Add Cards

```bash
# Interactive review (recommended)
uv run anki review cards/eat-framework.json

# Batch add without review
uv run anki add cards/eat-framework.json --deck "Learning"
```

## CLI Commands

### Connection & Info

```bash
# Check Anki connection
uv run anki ping

# List available decks
uv run anki list-decks

# List note types (Basic, Cloze, etc.)
uv run anki list-models
```

### Card Management

```bash
# Review cards interactively (approve/edit/skip)
uv run anki review cards/my-cards.json

# Add cards to specific deck
uv run anki review cards/my-cards.json --deck "Programming"

# Skip validation warnings
uv run anki review cards/my-cards.json --skip-validation

# Batch add without review
uv run anki add cards/my-cards.json
```

### Quick Card Creation

```bash
# Create a single card quickly
uv run anki quick \
  "What is the capital of France?" \
  "Paris" \
  --tags geography,capitals \
  --deck "Geography"
```

### Search & Delete

```bash
# Find notes by query
uv run anki find "deck:Default tag:python"
uv run anki find "tag:ai-generated"
uv run anki find "front:*capital*"

# Delete notes by ID
uv run anki delete 1496198395707
uv run anki delete 1234567890 1234567891 --yes
```

## Card JSON Format

Example `cards/example.json`:

```json
[
  {
    "front": "Why should you avoid using Anki for initial learning?",
    "back": "Anki is a scheduling tool for memorization, not a learning mechanism. You must understand material before creating flashcards.",
    "context": "EAT Framework - 'Encoded' principle from LeanAnki",
    "tags": ["anki", "learning-principles", "eat-framework"],
    "source": "https://leananki.com/creating-better-flashcards/",
    "deck": "Learning",
    "model": "Basic"
  },
  {
    "front": "What makes a flashcard question 'atomic'?",
    "back": "An atomic question is specific and focused, triggering precise memory retrieval. It tests one concept at a time without compound parts.",
    "context": "EAT Framework - 'Atomic' principle",
    "tags": ["anki", "flashcard-design"],
    "source": "https://leananki.com/creating-better-flashcards/",
    "deck": "Learning",
    "model": "Basic"
  }
]
```

## EAT Principle Validation

The system automatically validates cards against EAT principles:

### Encoded (Context)
- ⚠️ Warns if context is missing for short answers
- ⚠️ Suggests adding context for future understanding

### Atomic (Focused)
- ⚠️ Detects compound questions (with "and", "or", ";")
- ⚠️ Warns about overly long questions
- ❌ Errors if front doesn't end with "?"
- ⚠️ Flags vague question starters

### Timeless (Self-contained)
- ⚠️ Detects vague pronouns ("this", "that", "it")
- ⚠️ Warns about time-dependent references
- ℹ️ Notes undefined abbreviations

## Agent Workflow Example

**User:** "Create flashcards from this article: https://example.com/python-decorators"

**Agent Steps:**

1. **Scrape content:**
   ```bash
   ./scrape.sh https://example.com/python-decorators
   ```

2. **Read markdown:**
   ```python
   # Agent reads: scraped/python-decorators.md
   ```

3. **Generate cards:** (Agent writes this code or does it interactively)
   ```python
   from src.schema import Flashcard, save_cards_to_json

   cards = [
       Flashcard(
           front="When should you use a Python decorator?",
           back="Use decorators to modify or extend function behavior without changing the function's code. Common uses: logging, timing, authentication, caching.",
           context="Python decorators use @ syntax and are functions that wrap other functions",
           tags=["python", "decorators", "patterns"],
           source="https://example.com/python-decorators",
           deck="Programming",
       ),
       # ... more cards
   ]

   save_cards_to_json(cards, "cards/python-decorators.json")
   ```

4. **Review cards:**
   ```bash
   uv run anki review cards/python-decorators.json
   ```

5. **Done!** Cards are now in Anki for spaced repetition.

## Project Structure

```
anki-api/
├── pyproject.toml           # Project configuration
├── README.md                # This file
├── scrape.sh                # Web scraping wrapper
├── src/
│   ├── __init__.py
│   ├── anki_client.py       # AnkiConnect API wrapper
│   ├── schema.py            # Flashcard schema & validation
│   └── cli.py               # Command-line interface
├── scraped/                 # Scraped markdown files (gitignored)
├── cards/                   # Generated card JSON files (gitignored)
├── examples/                # Example workflows
└── tests/                   # Unit tests
```

## Tips for Creating Good Flashcards

### ✅ Good Examples

**Question-based, specific:**
```
Q: When should you use list comprehensions instead of for loops in Python?
A: Use list comprehensions when creating a new list from an iterable
   with simple transformation or filter. They're more readable and
   faster for simple operations.
```

**Includes context:**
```
Q: What is the time complexity of binary search?
A: O(log n)
Context: Binary search requires a sorted array and works by repeatedly
         dividing the search space in half.
```

### ❌ Bad Examples

**Statement instead of question:**
```
Front: "Python list comprehension"
Back: "[x for x in range(10)]"
```

**Compound question:**
```
Q: What is a decorator and how do you use it?
```
(Split into: "What is a decorator?" and "How do you apply a decorator?")

**Vague pronoun:**
```
Q: What does this do?
```
(This what? Will you remember in 6 months?)

## Troubleshooting

### "Failed to connect to AnkiConnect"

1. Make sure Anki Desktop is running
2. Check AnkiConnect plugin is installed (Tools → Add-ons)
3. Verify AnkiConnect settings allow localhost connections

### "Unable to determine which files to ship"

This happens if the `src/` directory doesn't exist. Run:
```bash
mkdir -p src && touch src/__init__.py
uv sync
```

### Scrape script not working

1. Verify crawl4ai is installed:
   ```bash
   cd /home/hugo/Documents/Engineering/crawl4ai
   uv run scrape_to_markdown.py --help
   ```

2. Check Playwright browsers are installed:
   ```bash
   playwright install chromium
   ```

## Advanced Usage

### Custom Validation

Implement custom validators in `src/schema.py`:

```python
def validate_custom(card: Flashcard) -> List[ValidationWarning]:
    warnings = []
    # Your custom validation logic
    return warnings
```

### Batch Processing Multiple URLs

Create a script:

```bash
#!/bin/bash
urls=(
    "https://example.com/article1"
    "https://example.com/article2"
)

for url in "${urls[@]}"; do
    ./scrape.sh "$url"
done

# Then ask agent to process all scraped/*.md files
```

### Alternative Note Types

To use Cloze deletions instead of Basic:

```python
card = Flashcard(
    front="Python's {{c1::decorator}} syntax uses the @ symbol",
    back="",  # Not used in Cloze
    model="Cloze",
    deck="Programming"
)
```

## Development

### Run Tests

```bash
uv run pytest
```

### Code Structure

- `anki_client.py`: Pure HTTP client for AnkiConnect API
- `schema.py`: Data models and validation logic
- `cli.py`: Click-based command-line interface

### Adding New Commands

Edit `src/cli.py` and add a new command:

```python
@main.command()
@click.argument("arg")
def mycommand(arg: str):
    """Your command description."""
    # Implementation
```

## Resources

- [LeanAnki: Creating Better Flashcards](https://leananki.com/creating-better-flashcards/)
- [AnkiConnect API Documentation](https://foosoft.net/projects/anki-connect/)
- [Anki Manual](https://docs.ankiweb.net/)
- [crawl4ai Documentation](https://github.com/unclecode/crawl4ai)

## License

MIT

## Contributing

This is a personal tool, but feel free to fork and adapt for your needs!
