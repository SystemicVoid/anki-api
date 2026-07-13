# AnkiFlow review stack — shortcuts over the anki-api CLI.
#
# These recipes are a THIN alias layer. The real lifecycle logic (the
# `anki-flow` tmux session, backend/frontend health-check polling, and
# browser launch) lives in src/cli/commands/orchestration.py. Keep these
# delegating to `uv run anki-api <cmd>` so the two never drift out of sync.

# List available recipes (runs on a bare `just`)
default:
    @just --list

# Start the full stack: Anki + backend (:8080) + frontend (:5173), opens Chrome (pass --no-browser to skip)
up *args:
    uv run anki-api up {{args}}

# Stop the stack (kills the anki-flow tmux session, both servers)
down:
    uv run anki-api down

# Show whether the stack is running
status:
    uv run anki-api status

# Attach to the tmux session to tail server logs (Ctrl+b then d to detach)
logs:
    uv run anki-api logs
