"""Orchestration commands: serve, flow, start."""

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
    """Start the web review interface.

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


@click.command()
@click.argument("source", required=False)
@click.option("--tags", "-t", default=None, help="Comma-separated tags for cards")
@click.option(
    "--review", "review_only", is_flag=True, help="Skip generation, just open review UI"
)
@click.option("--no-browser", is_flag=True, help="Don't open browser automatically")
@click.option("--stop", "do_stop", is_flag=True, help="Stop the running review session")
@click.option("--attach", "do_attach", is_flag=True, help="Attach to existing session")
@click.option("--status", "do_status", is_flag=True, help="Show session status")
def flow(
    source: str | None,
    tags: str | None,
    review_only: bool,
    no_browser: bool,
    do_stop: bool,
    do_attach: bool,
    do_status: bool,
):
    """Generate cards and launch review interface in tmux.

    Start with source (generates cards first):
        anki flow https://example.com/article
        anki flow docs/notes.md --tags python,decorators

    Review-only mode (skip card generation):
        anki flow --review

    Session management:
        anki flow --attach    Attach to running session
        anki flow --stop      Stop the session
        anki flow --status    Show session status
    """
    # Handle --stop
    if do_stop:
        if tmux_session_exists():
            tmux_kill_session()
            print_success("Session stopped.")
        else:
            print_warning("No session running.")
        return

    # Handle --status
    if do_status:
        if tmux_session_exists():
            print_success(f"Session '{TMUX_SESSION}' is running.")
            print_info(f"  Frontend: {FRONTEND_URL}")
            print_info(f"  Backend:  {BACKEND_URL}")
            print_info("  Run 'anki flow --attach' to view logs")
            print_info("  Run 'anki flow --stop' to stop")
        else:
            print_warning("No session running.")
        return

    # Handle --attach
    if do_attach:
        if tmux_session_exists():
            print_info(f"Attaching to session '{TMUX_SESSION}' (Ctrl+b d to detach)...")
            tmux_attach_session()
        else:
            print_warning(
                "No session running. Start with 'anki flow --review' or 'anki flow <source>'"
            )
        return

    # Starting a new session - validate arguments
    if not review_only and not source:
        print_error("Source required unless using --review flag")
        click.echo("Usage: anki flow <url-or-file> or anki flow --review")
        sys.exit(1)

    # Check if session already running
    if tmux_session_exists():
        print_warning(f"Session '{TMUX_SESSION}' already running.")
        if click.confirm("Stop existing session and start new one?", default=False):
            tmux_kill_session()
        else:
            print_info("Use 'anki flow --attach' to view existing session")
            return

    # Step 1: Ensure Anki is running (starts it if needed)
    ensure_anki_running()

    # Step 3: Generate cards (unless --review)
    if not review_only:
        print_info(f"Generating cards from: {source}")
        if not run_claude_generation(source, tags):
            print_error("Card generation failed")
            sys.exit(1)
        print_success("Card generation complete")

    # Step 4: Create tmux session with servers
    print_info("Starting servers in tmux session...")
    if not tmux_create_session():
        print_error("Failed to create tmux session")
        sys.exit(1)

    # Step 5: Wait for servers to be ready
    print_info("Waiting for backend...")
    if not wait_for_server(f"{BACKEND_URL}/api/health", timeout=30):
        print_error("Backend server failed to start")
        print_info("Check logs with: anki flow --attach")
        sys.exit(1)
    print_success(f"Backend running at {BACKEND_URL}")

    print_info("Waiting for frontend...")
    if not wait_for_server(FRONTEND_URL, timeout=60):
        print_error("Frontend server failed to start")
        print_info("Check logs with: anki flow --attach")
        sys.exit(1)
    print_success(f"Frontend running at {FRONTEND_URL}")

    # Step 6: Open browser
    if not no_browser:
        print_info("Opening browser...")
        open_browser(FRONTEND_URL)

    # Done - session runs in background
    click.echo()
    print_success(f"Review UI ready at {FRONTEND_URL}")
    click.echo()
    print_info("Session commands:")
    click.echo("  anki flow --attach    View server logs")
    click.echo("  anki flow --stop      Stop servers")
    click.echo("  anki flow --status    Check status")


@click.command()
@click.option("--stop", "do_stop", is_flag=True, help="Stop the running stack")
@click.option("--status", "do_status", is_flag=True, help="Show stack status")
@click.option("--attach", "do_attach", is_flag=True, help="Attach to tmux session")
@click.option("--no-browser", is_flag=True, help="Don't open browser automatically")
def start(
    do_stop: bool,
    do_status: bool,
    do_attach: bool,
    no_browser: bool,
):
    """Start the AnkiFlow web interface.

    Launches Anki Desktop (if needed), backend API, and frontend dev server.
    Opens the web UI in Chrome (or default browser).

    Examples:
        anki-api start           Start everything and open browser
        anki-api start --stop    Stop the running stack
        anki-api start --attach  View server logs in tmux
        anki-api start --status  Check if servers are running
    """
    # Handle --stop
    if do_stop:
        if tmux_session_exists():
            tmux_kill_session()
            print_success("Stack stopped.")
        else:
            print_warning("No stack running.")
        return

    # Handle --status
    if do_status:
        if tmux_session_exists():
            print_success("AnkiFlow stack is running.")
            print_info(f"  Frontend: {FRONTEND_URL}")
            print_info(f"  Backend:  {BACKEND_URL}")
            print_info("  Run 'anki-api start --attach' to view logs")
            print_info("  Run 'anki-api start --stop' to stop")
        else:
            print_warning("Stack not running.")
        return

    # Handle --attach
    if do_attach:
        if tmux_session_exists():
            print_info(f"Attaching to session '{TMUX_SESSION}' (Ctrl+b d to detach)...")
            tmux_attach_session()
        else:
            print_warning("No stack running. Start with 'anki-api start'")
        return

    # Check if session already running
    if tmux_session_exists():
        print_warning("Stack already running.")
        if click.confirm("Stop existing stack and start fresh?", default=False):
            tmux_kill_session()
        else:
            print_info("Use 'anki-api start --attach' to view logs")
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
        print_info("Check logs with: anki-api start --attach")
        sys.exit(1)
    print_success(f"Backend running at {BACKEND_URL}")

    print_info("Waiting for frontend...")
    if not wait_for_server(FRONTEND_URL, timeout=60):
        print_error("Frontend server failed to start")
        print_info("Check logs with: anki-api start --attach")
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
    click.echo("  anki-api start --attach    View server logs")
    click.echo("  anki-api start --stop      Stop servers")
    click.echo("  anki-api start --status    Check status")


orchestration_commands = [serve, flow, start]
