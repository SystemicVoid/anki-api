"""Orchestration commands: serve, up, down, status, logs, flow."""

import sys

import click

from src.cli.anki_lifecycle import ensure_anki_running
from src.cli.output import print_error, print_info, print_success, print_warning
from src.cli.server import (
    BACKEND_URL,
    FRONTEND_URL,
    open_browser,
    open_browser_chrome,
    run_claude_generation,
    wait_for_server,
)
from src.cli.tmux import (
    TMUX_SESSION,
    tmux_attach_session,
    tmux_create_session,
    tmux_kill_session,
    tmux_session_exists,
)


@click.command()
@click.option("--port", default=8080, help="Port for the API server (default: 8080)")
@click.option(
    "--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)"
)
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
def serve(port: int, host: str, reload: bool):
    """Start the backend API server only.

    Launches a FastAPI server for the card review web UI.
    The frontend should be started separately with:
        cd web/frontend && pnpm dev

    Then open http://localhost:5173 in your browser.
    """
    try:
        import uvicorn
    except ImportError:
        print_error("uvicorn not installed. Run: uv sync")
        sys.exit(1)

    print_info(f"Starting Anki Review API server on http://{host}:{port}")
    print_info("Press Ctrl+C to stop\n")

    uvicorn.run(
        "web.backend.main:app",
        host=host,
        port=port,
        reload=reload,
    )


# ── Stack lifecycle: up / down / status / logs ──────────────────────────


@click.command()
@click.option("--no-browser", is_flag=True, help="Don't open browser automatically")
def up(no_browser: bool):
    """Start the full AnkiFlow stack.

    Launches Anki Desktop (if needed), backend API, and frontend dev server
    in a tmux session, then opens the web UI in Chrome.

    \b
    Examples:
        anki-api up              Start everything and open browser
        anki-api up --no-browser Start without opening browser
    """
    # Check if session already running
    if tmux_session_exists():
        print_warning("Stack already running.")
        if click.confirm("Stop existing stack and start fresh?", default=False):
            tmux_kill_session()
        else:
            print_info("Use 'anki-api logs' to view logs")
            return

    # Step 1: Ensure Anki Desktop is running
    ensure_anki_running()

    # Step 2: Create tmux session with servers
    print_info("Starting servers...")
    if not tmux_create_session():
        print_error("Failed to create tmux session")
        sys.exit(1)

    # Step 3: Wait for servers to be ready
    print_info("Waiting for backend...")
    if not wait_for_server(f"{BACKEND_URL}/api/health", timeout=30):
        print_error("Backend server failed to start")
        print_info("Check logs with: anki-api logs")
        sys.exit(1)
    print_success(f"Backend running at {BACKEND_URL}")

    print_info("Waiting for frontend...")
    if not wait_for_server(FRONTEND_URL, timeout=60):
        print_error("Frontend server failed to start")
        print_info("Check logs with: anki-api logs")
        sys.exit(1)
    print_success(f"Frontend running at {FRONTEND_URL}")

    # Step 4: Open browser (Chrome preferred)
    if not no_browser:
        print_info("Opening browser...")
        open_browser_chrome(FRONTEND_URL)

    # Done
    click.echo()
    print_success(f"AnkiFlow ready at {FRONTEND_URL}")
    click.echo()
    print_info("Commands:")
    click.echo("  anki-api logs      View server logs")
    click.echo("  anki-api down      Stop servers")
    click.echo("  anki-api status    Check status")


@click.command()
def down():
    """Stop the running AnkiFlow stack."""
    if tmux_session_exists():
        tmux_kill_session()
        print_success("Stack stopped.")
    else:
        print_warning("No stack running.")


@click.command()
def status():
    """Show AnkiFlow stack status."""
    if tmux_session_exists():
        print_success("AnkiFlow stack is running.")
        print_info(f"  Frontend: {FRONTEND_URL}")
        print_info(f"  Backend:  {BACKEND_URL}")
        print_info("  Run 'anki-api logs' to view logs")
        print_info("  Run 'anki-api down' to stop")
    else:
        print_warning("Stack not running. Start with 'anki-api up'")


@click.command()
def logs():
    """Attach to the tmux session to view server logs.

    Press Ctrl+b d to detach.
    """
    if tmux_session_exists():
        print_info(f"Attaching to session '{TMUX_SESSION}' (Ctrl+b d to detach)...")
        tmux_attach_session()
    else:
        print_warning("No stack running. Start with 'anki-api up'")


# ── Flow: generate + review ─────────────────────────────────────────────


@click.group(invoke_without_command=True)
@click.argument("source", required=False)
@click.option("--tags", "-t", default=None, help="Comma-separated tags for cards")
@click.option(
    "--review", "review_only", is_flag=True, help="Skip generation, just open review UI"
)
@click.option("--no-browser", is_flag=True, help="Don't open browser automatically")
@click.pass_context
def flow(
    ctx: click.Context,
    source: str | None,
    tags: str | None,
    review_only: bool,
    no_browser: bool,
):
    """Generate cards and launch the review interface.

    \b
    Start with source (generates cards first):
        anki-api flow https://example.com/article
        anki-api flow docs/notes.md --tags python,decorators

    \b
    Review-only mode (skip card generation):
        anki-api flow --review

    \b
    Session management:
        anki-api flow stop      Stop the session
        anki-api flow status    Show session status
        anki-api flow logs      View session logs
    """
    # If a subcommand was invoked, let it run
    if ctx.invoked_subcommand is not None:
        return

    # Starting a new session - validate arguments
    if not review_only and not source:
        print_error("Source required unless using --review flag")
        click.echo("Usage: anki-api flow <url-or-file> or anki-api flow --review")
        sys.exit(1)

    # Check if session already running
    if tmux_session_exists():
        print_warning(f"Session '{TMUX_SESSION}' already running.")
        if click.confirm("Stop existing session and start new one?", default=False):
            tmux_kill_session()
        else:
            print_info("Use 'anki-api flow logs' to view existing session")
            return

    # Step 1: Ensure Anki is running (starts it if needed)
    ensure_anki_running()

    # Step 2: Generate cards (unless --review)
    if not review_only:
        if source is None:
            print_error("Source required for card generation")
            sys.exit(1)
        print_info(f"Generating cards from: {source}")
        if not run_claude_generation(source, tags):
            print_error("Card generation failed")
            sys.exit(1)
        print_success("Card generation complete")

    # Step 3: Create tmux session with servers
    print_info("Starting servers in tmux session...")
    if not tmux_create_session():
        print_error("Failed to create tmux session")
        sys.exit(1)

    # Step 4: Wait for servers to be ready
    print_info("Waiting for backend...")
    if not wait_for_server(f"{BACKEND_URL}/api/health", timeout=30):
        print_error("Backend server failed to start")
        print_info("Check logs with: anki-api flow logs")
        sys.exit(1)
    print_success(f"Backend running at {BACKEND_URL}")

    print_info("Waiting for frontend...")
    if not wait_for_server(FRONTEND_URL, timeout=60):
        print_error("Frontend server failed to start")
        print_info("Check logs with: anki-api flow logs")
        sys.exit(1)
    print_success(f"Frontend running at {FRONTEND_URL}")

    # Step 5: Open browser
    if not no_browser:
        print_info("Opening browser...")
        open_browser(FRONTEND_URL)

    # Done - session runs in background
    click.echo()
    print_success(f"Review UI ready at {FRONTEND_URL}")
    click.echo()
    print_info("Session commands:")
    click.echo("  anki-api flow logs      View server logs")
    click.echo("  anki-api flow stop      Stop servers")
    click.echo("  anki-api flow status    Check status")


@flow.command("stop")
def flow_stop():
    """Stop the running flow session."""
    if tmux_session_exists():
        tmux_kill_session()
        print_success("Session stopped.")
    else:
        print_warning("No session running.")


@flow.command("status")
def flow_status():
    """Show flow session status."""
    if tmux_session_exists():
        print_success(f"Session '{TMUX_SESSION}' is running.")
        print_info(f"  Frontend: {FRONTEND_URL}")
        print_info(f"  Backend:  {BACKEND_URL}")
        print_info("  Run 'anki-api flow logs' to view logs")
        print_info("  Run 'anki-api flow stop' to stop")
    else:
        print_warning("No session running.")


@flow.command("logs")
def flow_logs():
    """Attach to flow session to view logs.

    Press Ctrl+b d to detach.
    """
    if tmux_session_exists():
        print_info(f"Attaching to session '{TMUX_SESSION}' (Ctrl+b d to detach)...")
        tmux_attach_session()
    else:
        print_warning(
            "No session running. Start with 'anki-api flow --review' or 'anki-api flow <source>'"
        )


orchestration_commands = [serve, up, down, status, logs, flow]
