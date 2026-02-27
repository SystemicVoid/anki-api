# anki-api

Agent-assisted Anki flashcard generation. Agents propose cards from web content, YouTube transcripts, and documents — you review before anything touches your decks.

Built on the **EAT Framework** (Encoded, Atomic, Timeless): cognitive science-grounded principles that prioritize understanding over rote memorization. See [`docs/EAT_FRAMEWORK.md`](docs/EAT_FRAMEWORK.md) for the full framework.

## Prerequisites

- **[Anki Desktop](https://apps.ankiweb.net/)** with **[AnkiConnect](https://ankiweb.net/shared/info/2055492159)** plugin — must be running for all operations
- **Python 3.11+** via [`uv`](https://docs.astral.sh/uv/)
- **Node.js 20+** & **pnpm** — for the web frontend
- **[crawl4ai](https://github.com/unclecode/crawl4ai)** (optional) — web scraping. Set `CRAWL4AI_DIR` or place alongside repo

## Setup

```bash
uv sync
uv run anki-api ping   # verify Anki connection
```

## CLI

All commands: `uv run anki-api <command>`

### Stack Management

```bash
anki-api up          # start full stack (backend + frontend via tmux)
anki-api down        # stop the stack
anki-api status      # show stack status
anki-api logs        # attach to tmux session for logs
anki-api serve       # start backend API server only
```

### Card Operations

```bash
anki-api review <file.json>            # interactive review (approve/edit/skip)
anki-api review <file.json> --deck X   # target specific deck
anki-api add <file.json>               # batch add without review
anki-api quick "Q?" "A" --tags t1,t2   # create single card
anki-api find "deck:Default tag:python" # search notes (Anki query syntax)
anki-api delete <note-id> [--yes]      # delete notes by ID
```

### Content Extraction

```bash
anki-api flow <source>                 # generate cards + launch review UI
anki-api extract doc.docx -o out.md    # DOCX → markdown
./scrape.sh <url>                      # URL → scraped/<name>.md (needs crawl4ai)
```

### Diagnostics

```bash
anki-api ping        # check AnkiConnect
anki-api decks       # list decks
anki-api models      # list note types
```

## Web Interface

React + TypeScript frontend with a FastAPI backend. Used by the `flow` command for card review.

```bash
# Full stack (recommended)
uv run anki-api up

# Manual
uv run anki-api serve --reload   # backend on :8000
cd web/frontend && pnpm dev      # frontend on :5173
```

## Card Format

Cards are stored as JSON in `cards/`. Example:

```json
[
  {
    "front": "Why should you understand material before creating flashcards?",
    "back": "Anki is a scheduling tool for memorization, not a learning mechanism.\n\n---\n\nEAT 'Encoded' principle: elaborative encoding requires existing schema connections.",
    "tags": ["anki", "eat-framework", "type::concept"],
    "source": "https://leananki.com/creating-better-flashcards/",
    "deck": "Learning",
    "model": "Basic"
  }
]
```

Cards use **plain text only** — no Markdown, no HTML. Use `\n\n---\n\n` to separate the core answer from supporting context.

## Project Structure

```
src/
├── anki_client.py     # AnkiConnect HTTP wrapper
├── schema.py          # Flashcard model + validation
├── youtube.py         # YouTube transcript extraction
├── documents.py       # DOCX text extraction
└── cli/commands/
    ├── cards.py       # review, add, quick, find, delete
    ├── orchestration.py  # up, down, status, logs, flow, serve, extract
    └── diagnostics.py # ping, decks, models
web/
├── backend/           # FastAPI (routes/, models.py, main.py)
└── frontend/          # React + Vite + TypeScript
```

## Development

```bash
uv run pytest                  # run tests
prek run --all-files           # all linters + formatters
```

## License

MIT
