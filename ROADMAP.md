# Roadmap

This document correlates future work, technical debt, and ideas for the `anki-api` project.

## Recently Completed
- [x] **Code Quality Tooling** (2026-01-18): Comprehensive pre-commit hooks via prek for one-command code quality. Includes:
  - **Python**: ruff (lint+format), ty (type checking)
  - **TypeScript/JS**: biome (lint+format), knip (dead code detection)
  - **All files**: typos (spell checker), taplo (TOML), shellcheck (shell scripts)
  - Single command: `prek run --all-files` runs all checks
  - Git hooks: `prek install` for pre-commit integration
  - Config: `.pre-commit-config.yaml`, `_typos.toml`, `pyproject.toml [tool.ruff]`, `web/frontend/biome.json`
- [x] **Review Cards Persistence** (2026-01-18): When resuming an interrupted review, users now skip already-processed cards. Features include:
  - Automatic resume from first pending card when re-running `review` command
  - Status persistence to JSON file after each card (added/skipped)
  - Session and total progress tracking displayed in summary
  - `--reset` flag to start fresh review of all cards
- [x] **YouTube Integration** (2026-01-18): Added support for generating flashcards from YouTube video transcripts. Features include:
  - Auto-detection of YouTube URLs (youtube.com, youtu.be, shorts, embed)
  - Transcript fetching via youtube-transcript-api
  - Markdown output with timestamps saved to scraped/
  - Seamless integration with existing card generation UI
- [x] **File Browser UX Enhancement** (2026-01-17): Implemented comprehensive file browser with project/system modes, replacing manual path copy-paste workflow. Features include:
  - Backend: Secure file browsing API with path validation and directory blacklisting
  - Frontend: Tabbed interface (URL vs File) with recent files panel
  - Project mode: Browse scraped/ and cards/ directories
  - System mode: Browse filesystem with security safeguards
  - Recent files: Quick access to recently modified files

## High Priority
- [ ] **CI/CD Pipeline**: Implement GitHub Actions to run `prek run --all-files` and `uv run pytest` on push/PR
- [ ] **Fix Type Errors**: Address pre-existing type errors flagged by ty (currently using `--exit-zero`)
- [ ] **Clean Dead Code**: Remove unused exports flagged by knip (ValidationWarnings.tsx, addCardToAnki, ReviewAction)
- [ ] **Production Configuration**: Parameterize CORS origins in `web/backend/main.py` to support production environments (currently hardcoded to localhost).
- [ ] **Test Coverage**: Expand pytest coverage beyond the current basic smoke tests, particularly for edge cases in card validation.

## Medium Priority
- [ ] **Authentication**: Add API key or JWT authentication for the backend endpoints.
- [ ] **Containerization**: Create a `Dockerfile` for easier deployment.
- [ ] **Documentation**: Generate API documentation using Swagger/OpenAPI (built-in to FastAPI) and expose it properly.

## Low Priority / Ideas
- [ ] **Multi-user Support**: Allow multiple users to manage their own Anki profiles/decks.
- [ ] **LLM Integration**: direct LLM generation of cards from the web interface.
