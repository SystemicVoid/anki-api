# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**anki-api** is an agent-assisted system for generating high-quality Anki flashcards from web content and documents. It follows the **EAT Framework** (Encoded, Atomic, Timeless) for creating effective flashcards that prioritize understanding over rote memorization.

**Key Design Principles:**
- Agent-assisted (not automated): Agents generate card proposals; users review before adding to Anki
- Quality over quantity: Focus on 5-10 excellent cards rather than 50 mediocre ones
- EAT validation built-in: Automatic checks ensure cards follow learning science principles
- Simple dependencies: requests, pydantic, click - no heavy LLM frameworks

## Development Commands

### Environment Setup
```bash
# Install dependencies (uses uv package manager)
uv sync

# Verify Anki connection (Anki Desktop must be running)
uv run anki-api ping
```

### Common Development Tasks
```bash
# Run tests
uv run pytest

# Execute CLI commands (all commands use this pattern)
uv run anki-api <command>

# Examples:
uv run anki-api list-decks
uv run anki-api review cards/example.json
uv run anki-api find "tag:python"
uv run anki-api extract-docx docs/source.docx --output scraped/source.md
```

### Web Development
```bash
# Start Backend API
uv run anki-api serve --reload

# Start Frontend (React)
cd web/frontend
pnpm dev

# Build Frontend
cd web/frontend
pnpm build
```

Need to read DOCX material without the CLI? Import `extract_docx_text` from `src.documents` to pull markdown-friendly text directly inside agent workflows.

### Code Quality

All code quality checks run through a single command via prek (pre-commit):

```bash
# Run all checks (one command philosophy)
prek run --all-files

# Install git hooks (runs checks on every commit)
prek install
```

**Pre-commit hooks (fast, <5s total):**

| Hook | Scope | Purpose |
|------|-------|---------|
| trailing-whitespace | All | Remove trailing whitespace |
| end-of-file-fixer | All | Ensure files end with newline |
| check-yaml | YAML | Validate YAML syntax |
| check-json | JSON | Validate JSON syntax |
| typos | All | Spell checker (catches agent typos) |
| ruff | Python | Lint + format (replaces flake8/black/isort) |
| ruff-format | Python | Code formatting |
| ty | Python | Type checking (Rust-based, very fast) |
| taplo-format | TOML | Format pyproject.toml |
| shellcheck | Shell | Shell script linting |
| biome | TS/JS | Lint + format (replaces ESLint/Prettier) |
| knip | TS/JS | Dead code detection |

**Frontend-specific commands:**

```bash
cd web/frontend
pnpm check    # biome check
pnpm lint     # biome lint only
pnpm format   # biome format only
pnpm knip     # dead code detection
```

**Configuration files:**
- `.pre-commit-config.yaml` - prek hook orchestration
- `_typos.toml` - spell checker dictionary
- `pyproject.toml` - ruff and ty config under `[tool.ruff]` and `[tool.ty]`
- `web/frontend/biome.json` - biome config
- `web/frontend/knip.json` - knip config

### Web Scraping Workflow
```bash
# Scrape URL to markdown (requires crawl4ai at /home/hugo/Documents/Engineering/crawl4ai)
./scrape.sh https://example.com/article

# Output: scraped/<filename>.md
```

### Flashcard Generation (Agent Task)
```python
# Import card schema
from src.schema import Flashcard, save_cards_to_json
from datetime import datetime

# Create cards
cards = [
    Flashcard(
        front="Question ending with?",
        back="Answer with explanation",
        context="Additional context for future understanding",
        tags=["domain", "topic", "type"],
        source="https://example.com/article"
    )
]

# Save with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
save_cards_to_json(cards, f"cards/topic_{timestamp}.json")
```

## Architecture

### Module Structure

**src/anki_client.py** - AnkiConnect HTTP API wrapper
- Pure HTTP client using requests library
- All Anki operations (add, find, delete notes)
- Error handling for connection failures
- Core methods: `add_note()`, `add_notes_batch()`, `find_notes()`, `delete_notes()`

**src/schema.py** - Data models and EAT validation
- `Flashcard` dataclass: represents a single card
- Validation functions: `validate_encoded()`, `validate_atomic()`, `validate_timeless()`
- JSON serialization: `load_cards_from_json()`, `save_cards_to_json()`
- Returns `ValidationWarning` objects with severity levels (info/warning/error)

**src/cli.py** - Click-based command-line interface
- Commands: ping, list-decks, list-models, review, add, quick, find, delete
- Interactive review workflow with approve/edit/skip/quit options
- Colored output using click.secho()
- Entry point: `anki-api` command (defined in pyproject.toml)

**src/youtube.py** - YouTube transcript extraction
- `is_youtube_url()`: Detect YouTube URLs (youtube.com, youtu.be, shorts, embed)
- `extract_video_id()`: Parse 11-character video ID from URL
- `export_transcript_to_markdown()`: Fetch transcript and save to markdown with timestamps

**web/** - Web Interface
- **backend/**: FastAPI application (`main.py`, `models.py`, `routes/`)
- **frontend/**: React + TypeScript application (Vite based)

### Data Flow

1. **Content Acquisition**:
   - Web URLs → `scrape.sh` → `scraped/*.md`
   - YouTube URLs → `youtube.py` → `scraped/youtube_*.md`
   - DOCX files → `documents.py` → `scraped/*.md`
2. **Card Generation**: Agent reads content → creates `Flashcard` objects → validates with EAT principles
3. **Persistence**: `save_cards_to_json()` → `cards/*.json`
4. **Review**: User runs `uv run anki-api review` → interactive approval
5. **Anki Integration**: Approved cards → `AnkiClient.add_note()` → AnkiConnect API → Anki Desktop

### Key Design Decisions

**Why agent-assisted, not automated?**
- User maintains control over quality
- Agents propose, humans review and approve
- Prevents low-quality card generation

**Why separate validation from CLI?**
- Validation logic (schema.py) is reusable
- CLI (cli.py) handles user interaction
- Agent workflows can use validation directly

**Why JSON intermediate format?**
- Human-readable and editable
- Version controllable (can track card evolution)
- Decouples generation from addition

## EAT Framework Validation

The system enforces three principles through `src/schema.py`:

### Encoded (Understanding-based)
- Warns if context missing for short answers
- Ensures cards support long-term recall, not just rote memorization

### Atomic (Focused)
- **ERROR** if front doesn't end with "?"
- **WARNING** for compound questions (contains "and", "or", ";")
- **WARNING** for overly long questions (>200 chars)
- **WARNING** for vague starters ("What about...", "Tell me about...")

### Timeless (Self-contained)
- **WARNING** for vague pronouns ("this", "that", "it")
- **WARNING** for time-dependent references ("recently", "currently")
- **INFO** for undefined abbreviations (uppercase words without context)

## Card Formatting

**CRITICAL**: Anki does not render Markdown. All card content must use plain text formatting only.

### Standard Format

```
[Main answer text, potentially with enumerated points]

---

[Contextual information without any label]
```

### Formatting Rules

- **NO markdown formatting**: No bold (`**text**`), italic (`*text*`), code blocks, or other markdown
- **NO HTML tags**: No `<br>`, `<b>`, `<i>`, or any HTML
- **Line breaks**: Use plain newlines (`\n`) only
- **Separator**: Use `---` with blank lines before and after (`\n\n---\n\n`)
- **Context section**: Start directly with content (no "Context:" prefix)

### Lists (for visual clarity)

Use newlines between items to create visually clear, scannable content:

- **Ordered lists**: `1.\n2.\n3.` format
- **Unordered lists**: `-\n-\n-` format

**Example:**
```
Three factors converged:
1. Compute power increased, enabling training of massive models
2. Large-scale quality datasets became available
3. Algorithmic innovations like transformers (2017) enabled efficient parallel processing

---

Historical AI limitations weren't theoretical but practical. Modern systems like ChatGPT require all three elements. Quality matters as much as quantity for data—medical textbooks provide better training than equivalent volumes of Twitter posts.
```

### Answer vs. Context Balance

- **Answer**: Core concept, direct response to question
- **Context**: Detailed explanations, examples, caveats, related information
- **Guideline**: Bias slightly towards moving verbose details to context section

## Claude Code Slash Command

**`/create-anki-cards`** - Primary command for flashcard generation
- Location: `.claude/commands/create-anki-cards.md`
- Handles URL scraping or direct file reading
- Applies EAT validation automatically
- Applies proper formatting rules (no markdown, plain text only)
- Generates timestamped JSON output in `cards/` directory
- Provides next-step instructions for review

## Integration Points

**AnkiConnect API**
- Must be installed in Anki Desktop: https://ankiweb.net/shared/info/2055492159
- Default URL: http://localhost:8775
- Anki must be running for all operations

**crawl4ai Web Scraper**
- External dependency at `/home/hugo/Documents/Engineering/crawl4ai`
- Invoked by `scrape.sh` wrapper script
- Converts web pages to clean markdown
- Uses flags: `--output-dir`, `--non-interactive`, `--quiet`

## Common Agent Patterns

### Pattern 1: Generate from URL
```python
# 1. Scrape
# bash: ./scrape.sh <url>

# 2. Read scraped content
with open('scraped/<filename>.md', 'r') as f:
    content = f.read()

# 3. Generate cards (agent analyzes content)
# 4. Save to cards/*.json
# 5. Report: "Run: uv run anki-api review <file>"
```

### Pattern 2: Validate Before Saving
```python
from src.schema import validate_card

for card in cards:
    warnings = validate_card(card)
    # Check for errors (severity='error')
    if any(w.severity == 'error' for w in warnings):
        # Fix or skip card
```

### Pattern 3: Check Anki Connection
```python
from src.anki_client import AnkiClient, AnkiConnectError

client = AnkiClient()
try:
    if not client.ping():
        print("⚠️ Anki is not running")
except AnkiConnectError as e:
    print(f"⚠️ Connection error: {e}")
```

## Card Quality Guidelines

**DO:**
- Focus on "why" and "when" questions (understanding)
- Use specific examples from source material
- Add context that will be helpful in 6 months
- Keep questions focused (one concept per card)
- Use hierarchical tags: `["domain", "topic", "type"]`

**DON'T:**
- Create definition cards ("What is X?" → focus on "Why use X?")
- Make list cards ("Name the 5 principles..." → separate cards for each)
- Copy-paste large text blocks (summarize and synthesize)
- Generate cards for every detail (be selective)
- Use vague pronouns without context

## File Locations

- **Scraped content**: `scraped/` (gitignored)
- **Generated cards**: `cards/` (gitignored)
- **Examples**: `examples/agent_workflow.md` (comprehensive agent guide)
- **Tests**: `tests/` (use pytest)

## Reference Materials

- EAT Framework: https://leananki.com/creating-better-flashcards/
- AnkiConnect API: https://foosoft.net/projects/anki-connect/
- Agent workflow guide: `examples/agent_workflow.md` (detailed patterns and anti-patterns)
