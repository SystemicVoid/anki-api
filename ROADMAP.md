# Roadmap

This document correlates future work, technical debt, and ideas for the `anki-api` project.

## Recently Completed
- [x] **File Browser UX Enhancement** (2026-01-17): Implemented comprehensive file browser with project/system modes, replacing manual path copy-paste workflow. Features include:
  - Backend: Secure file browsing API with path validation and directory blacklisting
  - Frontend: Tabbed interface (URL vs File) with recent files panel
  - Project mode: Browse scraped/ and cards/ directories
  - System mode: Browse filesystem with security safeguards
  - Recent files: Quick access to recently modified files

## High Priority
- [ ] **CI/CD Pipeline**: Implement GitHub Actions for automated testing and linting on push.
- [ ] **Youtube Integration**: Add support for scraping youtube videos and creating cards from their transcripts using https://github.com/jdepoix/youtube-transcript-api
- [ ] **Production Configuration**: Parameterize CORS origins in `web/backend/main.py` to support production environments (currently hardcoded to localhost).
- [ ] **Test Coverage**: Expand pytest coverage beyond the current basic smoke tests, particularly for edge cases in card validation.

## Medium Priority
- [ ] **Authentication**: Add API key or JWT authentication for the backend endpoints.
- [ ] **Containerization**: Create a `Dockerfile` for easier deployment.
- [ ] **Documentation**: Generate API documentation using Swagger/OpenAPI (built-in to FastAPI) and expose it properly.

## Low Priority / Ideas
- [ ] **Multi-user Support**: Allow multiple users to manage their own Anki profiles/decks.
- [ ] **LLM Integration**: direct LLM generation of cards from the web interface.
