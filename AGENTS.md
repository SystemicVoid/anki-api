# Repository Guidelines

## Project Structure & Module Organization
- `src/` holds the production code: `cli/` exposes the Click entrypoint behind `uv run anki-api`, `anki_client.py` wraps AnkiConnect HTTP calls, and `schema.py` keeps Flashcard dataclasses plus validators.
- `web/` contains the web interface: `backend/` for the FastAPI server and `frontend/` for the React/Vite UI.
- `cards/` stores JSON payloads for review; keep filenames kebab-cased.
- `scraped/` contains markdown pulled via `./scrape.sh <url>` and is the usual starting point for new study sets.
- `tests/` houses pytest suites; keep files named `test_<module>.py` so pytest auto-discovers them.

## Build, Test, and Development Commands
- `uv sync` installs project dependencies pinned by `uv.lock`.
- `uv run anki-api ping` ensures AnkiConnect is reachable before more expensive flows.
- `uv run anki-api serve --reload` starts the backend API server locally.
- `cd web/frontend && pnpm dev` starts the frontend development server.
- `uv run anki-api review cards/sample.json --deck "Learning"` performs the interactive approval loop; omit `--deck` to keep file-assigned decks.
- `uv run pytest` executes the Python test suite; scope with `-k validator` when iterating quickly.
- `./scrape.sh https://example.com/article` writes markdown into `scraped/` for subsequent processing.
- `uv run anki-api extract source.docx --output scraped/source.md` converts DOCX references into markdown inside `scraped/` (omit `--output` to auto-suffix).

## Coding Style & Naming Conventions
- Python 3.11+, 4-space indentation, and type hints everywhere (match existing dataclasses and function signatures).
- Keep CLI commands short verbs (`review`, `add`, `quick`) and expose new options via snake_case Click arguments.
- Validation warnings in `schema.py` follow EAT terminology; reuse those helper patterns instead of ad-hoc string checks.
- JSON card files should keep only `front`, `back`, `context`, `tags`, `deck`, `model`—omit transient metadata.
- Use inline comments only when intent is unclear, and raise `ValueError` rather than returning `None` for malformed input.

## Testing Guidelines
- Use pytest with plain asserts; fixtures can live in `tests/conftest.py` once you need shared sample cards.
- Name tests `test_<behavior>`, e.g., `test_validate_atomic_flags_compound_question`, to mirror the EAT rules they safeguard.
- Exercise CLI flows by invoking commands through pytest and mock Anki endpoints via `requests` monkeypatching.
- Target at least smoke coverage for every new validator or command, and capture representative card payloads under `tests/fixtures/` if needed.

## Commit & Pull Request Guidelines
- Follow the existing Conventional Commit style (`feat:`, `fix:`, `docs:`, `chore:`) as seen in `git log -5` so history stays readable.
- Commits should stay focused: update code, docs, and sample cards together when behavior changes.
- PRs need a short summary, reproduction or testing notes (`uv run pytest`, `uv run anki-api review cards/foo.json`), and screenshots when UX changes touch CLI output.
- Link related issues or TODO items, and call out any manual setup (e.g., required decks) so reviewers can re-run flows confidently.
