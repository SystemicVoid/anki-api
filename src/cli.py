"""Command-line interface for anki-api."""

import re
import subprocess
import sys
import time
from pathlib import Path
from typing import List

import click
import requests

from src.anki_client import AnkiClient, AnkiConnectError
from src.documents import export_docx_to_markdown
from src.schema import (
    Flashcard,
    load_cards_from_json,
    save_cards_to_json,
    validate_card,
    ValidationWarning,
)

SCRAPED_DIR = Path("scraped")


def get_client() -> AnkiClient:
    """Create and return an AnkiClient instance."""
    return AnkiClient()


def print_error(message: str) -> None:
    """Print error message in red."""
    click.secho(f"Error: {message}", fg="red", err=True)


def print_success(message: str) -> None:
    """Print success message in green."""
    click.secho(message, fg="green")


def print_warning(message: str) -> None:
    """Print warning message in yellow."""
    click.secho(message, fg="yellow")


def print_info(message: str) -> None:
    """Print info message in blue."""
    click.secho(message, fg="blue")


def slugify_filename(name: str) -> str:
    """Convert a filename stem into a safe, kebab-cased slug."""
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "document"


def default_docx_output_path(docx_file: Path) -> Path:
    """Return a unique markdown path under scraped/ for a DOCX file."""
    slug = slugify_filename(docx_file.stem)
    destination = SCRAPED_DIR / f"{slug}.md"
    counter = 1
    while destination.exists():
        counter += 1
        destination = SCRAPED_DIR / f"{slug}-{counter}.md"
    return destination


def print_card(card: Flashcard, index: int = None, total: int = None) -> None:
    """Print a formatted flashcard.

    Args:
        card: Flashcard to print
        index: Optional card index (1-based)
        total: Optional total number of cards
    """
    if index and total:
        click.echo(f"\n{'=' * 60}")
        click.secho(f"[{index}/{total}]", fg="cyan", bold=True)
    else:
        click.echo(f"\n{'=' * 60}")

    click.echo()
    click.secho("Front:", fg="yellow", bold=True)
    click.echo(f"  {card.front}")
    click.echo()
    click.secho("Back:", fg="yellow", bold=True)
    click.echo(f"  {card.back}")

    if card.context:
        click.echo()
        click.secho("Context:", fg="yellow", bold=True)
        click.echo(f"  {card.context}")

    if card.tags:
        click.echo()
        click.secho("Tags:", fg="yellow", bold=True)
        click.echo(f"  {', '.join(card.tags)}")

    if card.source:
        click.echo()
        click.secho("Source:", fg="yellow", bold=True)
        click.echo(f"  {card.source}")

    click.echo()
    click.secho(f"Deck: {card.deck} | Model: {card.model}", fg="cyan")


def print_validation_warnings(warnings: List[ValidationWarning]) -> None:
    """Print validation warnings with colors.

    Args:
        warnings: List of validation warnings
    """
    if not warnings:
        return

    click.echo()
    for warning in warnings:
        if warning.severity == "error":
            click.secho(f"  {warning}", fg="red")
        elif warning.severity == "warning":
            click.secho(f"  {warning}", fg="yellow")
        else:  # info
            click.secho(f"  {warning}", fg="blue")


PROJECT_DIR = Path(__file__).parent.parent
FRONTEND_DIR = PROJECT_DIR / "web" / "frontend"
BACKEND_URL = "http://127.0.0.1:8080"
FRONTEND_URL = "http://localhost:5173"


def is_anki_running() -> bool:
    """Check if Anki Desktop is running via pgrep."""
    result = subprocess.run(["pgrep", "-x", "anki"], capture_output=True)
    return result.returncode == 0


def start_anki_desktop() -> subprocess.Popen:
    """Launch Anki Desktop in background."""
    return subprocess.Popen(
        ["anki"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def wait_for_anki_connect(client: AnkiClient, timeout: int = 30) -> bool:
    """Poll AnkiConnect until ready or timeout."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            if client.ping():
                return True
        except AnkiConnectError:
            pass
        time.sleep(1)
    return False


def run_claude_generation(source: str, tags: str | None) -> bool:
    """Run Claude Code to generate cards. Returns True on success."""
    cmd = ["claude", "-p", "--dangerously-skip-permissions"]
    prompt = f"/create-anki-cards {source}"
    if tags:
        prompt += f" --tags {tags}"
    result = subprocess.run(cmd + [prompt])
    return result.returncode == 0


def start_backend() -> subprocess.Popen:
    """Start FastAPI backend server."""
    return subprocess.Popen(
        ["uv", "run", "anki", "serve"],
        cwd=PROJECT_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def start_frontend() -> subprocess.Popen:
    """Start Vite dev server."""
    return subprocess.Popen(
        ["pnpm", "dev"],
        cwd=FRONTEND_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def wait_for_server(url: str, timeout: int = 30) -> bool:
    """Poll URL until it responds or timeout."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            resp = requests.get(url, timeout=2)
            if resp.status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(1)
    return False


def get_last_activity() -> float:
    """Get timestamp of last API activity from backend."""
    resp = requests.get(f"{BACKEND_URL}/api/activity", timeout=2)
    return resp.json()["last_activity"]


def open_browser(url: str) -> None:
    """Open URL in default browser."""
    subprocess.Popen(
        ["xdg-open", url],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def cleanup_processes(processes: list[subprocess.Popen]) -> None:
    """Terminate all background processes gracefully."""
    for proc in processes:
        if proc.poll() is None:  # Still running
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()


@click.group()
def main():
    """Anki API - Agent-assisted flashcard generation for Anki."""
    pass


@main.command()
def ping():
    """Check if Anki is running with AnkiConnect."""
    client = get_client()

    try:
        if client.ping():
            print_success("✓ Connected to Anki successfully!")
            print_info(f"  AnkiConnect URL: {client.url}")
        else:
            print_error("Failed to connect to Anki.")
            sys.exit(1)
    except AnkiConnectError as e:
        print_error(str(e))
        sys.exit(1)


@main.command("list-decks")
def list_decks():
    """List all available Anki decks."""
    client = get_client()

    try:
        decks = client.get_decks()
        print_success(f"Found {len(decks)} decks:")
        for deck in sorted(decks):
            click.echo(f"  • {deck}")
    except AnkiConnectError as e:
        print_error(str(e))
        sys.exit(1)


@main.command("list-models")
def list_models():
    """List all available note types (models)."""
    client = get_client()

    try:
        models = client.get_models()
        print_success(f"Found {len(models)} note types:")
        for model in sorted(models):
            click.echo(f"  • {model}")
    except AnkiConnectError as e:
        print_error(str(e))
        sys.exit(1)


@main.command("extract-docx")
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    help="Optional markdown output path (default: scraped/<filename>.md)",
)
def extract_docx(file: Path, output: Path | None):
    """Convert a DOCX file into markdown for downstream card generation."""
    destination = output or default_docx_output_path(file)

    try:
        export_docx_to_markdown(file, destination)
    except ValueError as e:
        print_error(str(e))
        sys.exit(1)
    except Exception as e:
        print_error(f"Failed to extract DOCX: {e}")
        sys.exit(1)

    print_success("✓ Extracted DOCX contents to markdown")
    print_info(f"  Source: {file}")
    print_info(f"  Output: {destination}")

    click.echo("\nNext steps for agents:")
    click.echo(f"  • Review {destination} to identify flashcard-worthy sections")
    click.echo("  • Use src.schema.Flashcard to craft cards and save to cards/*.json")


@main.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--deck",
    default=None,
    help="Override deck name for all cards (default: use card's deck)",
)
@click.option(
    "--show-warnings",
    is_flag=True,
    help="Display EAT principle validation warnings during review",
)
def review(file: Path, deck: str, show_warnings: bool):
    """Review and approve cards from a JSON file before adding to Anki.

    Interactively review each card with options to:
    - (a)pprove: Add card to Anki
    - (e)dit: Modify card fields
    - (s)kip: Skip this card
    - (q)uit: Stop reviewing
    """
    client = get_client()

    # Check Anki connection
    try:
        if not client.ping():
            print_error("Cannot connect to Anki. Make sure Anki is running.")
            sys.exit(1)
    except AnkiConnectError as e:
        print_error(str(e))
        sys.exit(1)

    # Load cards
    try:
        cards = load_cards_from_json(str(file))
    except ValueError as e:
        print_error(str(e))
        sys.exit(1)

    if not cards:
        print_warning("No cards found in file.")
        sys.exit(0)

    print_info(f"Loaded {len(cards)} cards from {file.name}")
    print_success("✓ Connected to Anki\n")

    added_count = 0
    skipped_count = 0

    for idx, card in enumerate(cards, 1):
        # Override deck if specified
        if deck:
            card.deck = deck

        # Print card
        print_card(card, idx, len(cards))

        # Validate card (always run validation, but only display if flag is set)
        warnings = validate_card(card)
        if show_warnings:
            print_validation_warnings(warnings)

        # Get user action
        click.echo()
        action = click.prompt(
            "Action",
            type=click.Choice(["a", "e", "s", "q"], case_sensitive=False),
            default="a",
            show_choices=True,
        )

        if action.lower() == "q":
            print_info("\nStopped reviewing.")
            break

        elif action.lower() == "s":
            print_warning("Skipped card.")
            skipped_count += 1
            continue

        elif action.lower() == "e":
            # Edit mode
            click.echo("\nEdit card (press Enter to keep current value):")
            new_front = click.prompt("Front", default=card.front)
            new_back = click.prompt("Back", default=card.back)
            new_context = click.prompt("Context", default=card.context)
            new_tags = click.prompt(
                "Tags (comma-separated)", default=",".join(card.tags)
            )

            card.front = new_front
            card.back = new_back
            card.context = new_context
            card.tags = [t.strip() for t in new_tags.split(",") if t.strip()]

            # Ask to approve after editing
            if not click.confirm("\nApprove edited card?", default=True):
                print_warning("Skipped card after edit.")
                skipped_count += 1
                continue

        # Add card to Anki (action == 'a' or after edit approval)
        try:
            note_id = client.add_note(
                deck_name=card.deck,
                model_name=card.model,
                fields=card.to_anki_note()["fields"],
                tags=card.tags,
            )
            print_success(f"✓ Card added to Anki (ID: {note_id})")
            added_count += 1
        except AnkiConnectError as e:
            print_error(f"Failed to add card: {e}")
            skipped_count += 1

    # Summary
    click.echo(f"\n{'=' * 60}")
    print_success(f"Review complete!")
    click.echo(f"  Added: {added_count}")
    click.echo(f"  Skipped: {skipped_count}")


@main.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--deck",
    default=None,
    help="Override deck name for all cards (default: use card's deck)",
)
def add(file: Path, deck: str):
    """Add cards from JSON file directly to Anki without review.

    Use this for batch adding cards you've already reviewed.
    """
    client = get_client()

    # Check Anki connection
    try:
        if not client.ping():
            print_error("Cannot connect to Anki. Make sure Anki is running.")
            sys.exit(1)
    except AnkiConnectError as e:
        print_error(str(e))
        sys.exit(1)

    # Load cards
    try:
        cards = load_cards_from_json(str(file))
    except ValueError as e:
        print_error(str(e))
        sys.exit(1)

    if not cards:
        print_warning("No cards found in file.")
        sys.exit(0)

    print_info(f"Adding {len(cards)} cards to Anki...")

    # Override deck if specified
    if deck:
        for card in cards:
            card.deck = deck

    # Prepare notes for batch add
    notes = []
    for card in cards:
        notes.append(card.to_anki_note())

    # Add cards
    try:
        note_ids = client.add_notes_batch(notes)
        success_count = sum(1 for nid in note_ids if nid is not None)
        failed_count = len(note_ids) - success_count

        print_success(f"✓ Successfully added {success_count} cards")
        if failed_count > 0:
            print_warning(f"  Failed to add {failed_count} cards (duplicates?)")

    except AnkiConnectError as e:
        print_error(f"Failed to add cards: {e}")
        sys.exit(1)


@main.command()
@click.argument("front")
@click.argument("back")
@click.option("--deck", default="Default", help="Deck name (default: Default)")
@click.option("--tags", default="", help="Comma-separated tags")
@click.option("--context", default="", help="Additional context")
@click.option(
    "--show-warnings",
    is_flag=True,
    help="Display EAT principle validation warnings",
)
def quick(front: str, back: str, deck: str, tags: str, context: str, show_warnings: bool):
    """Quickly create a single flashcard.

    Example:
        anki quick "What is the capital of France?" "Paris" --tags geography
    """
    client = get_client()

    # Check Anki connection
    try:
        if not client.ping():
            print_error("Cannot connect to Anki. Make sure Anki is running.")
            sys.exit(1)
    except AnkiConnectError as e:
        print_error(str(e))
        sys.exit(1)

    # Create card
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    card = Flashcard(
        front=front,
        back=back,
        context=context,
        tags=tag_list,
        deck=deck,
        model="Basic",
    )

    # Validate card (always run validation, but only display if flag is set)
    warnings = validate_card(card)
    if show_warnings and warnings:
        print_warning("Validation warnings:")
        print_validation_warnings(warnings)
        click.echo()

    # Add to Anki
    try:
        note_id = client.add_note(
            deck_name=card.deck,
            model_name=card.model,
            fields=card.to_anki_note()["fields"],
            tags=card.tags,
        )
        print_success(f"✓ Card added to Anki (ID: {note_id})")
    except AnkiConnectError as e:
        print_error(f"Failed to add card: {e}")
        sys.exit(1)


@main.command()
@click.argument("query")
def find(query: str):
    """Search for notes using Anki query syntax.

    Examples:
        anki find "deck:Default tag:python"
        anki find "tag:ai-generated"
        anki find "front:*capital*"
    """
    client = get_client()

    try:
        note_ids = client.find_notes(query)

        if not note_ids:
            print_warning("No notes found.")
            sys.exit(0)

        print_success(f"Found {len(note_ids)} notes:")

        # Get note info
        notes_info = client.get_note_info(note_ids)

        for note_info in notes_info[:20]:  # Limit to first 20 for display
            note_id = note_info["noteId"]
            fields = note_info["fields"]
            tags = note_info["tags"]

            click.echo(f"\n  ID: {note_id}")
            click.echo(f"  Tags: {', '.join(tags) if tags else '(none)'}")

            # Show first field (usually Front)
            for field_name, field_value in fields.items():
                content = field_value["value"]
                # Strip HTML and truncate
                content = content.replace("<br>", " ")
                content = content[:80] + "..." if len(content) > 80 else content
                click.echo(f"  {field_name}: {content}")
                break  # Only show first field

        if len(note_ids) > 20:
            print_info(f"\n(Showing first 20 of {len(note_ids)} results)")

    except AnkiConnectError as e:
        print_error(str(e))
        sys.exit(1)


@main.command()
@click.argument("note_ids", nargs=-1, type=int, required=True)
@click.option("--yes", is_flag=True, help="Skip confirmation prompt")
def delete(note_ids: tuple, yes: bool):
    """Delete notes by their IDs.

    Example:
        anki delete 1234567890
        anki delete 1234567890 1234567891 --yes
    """
    client = get_client()

    if not yes:
        click.confirm(
            f"Delete {len(note_ids)} note(s)?",
            abort=True,
        )

    try:
        client.delete_notes(list(note_ids))
        print_success(f"✓ Deleted {len(note_ids)} note(s)")
    except AnkiConnectError as e:
        print_error(str(e))
        sys.exit(1)


@main.command()
@click.option("--port", default=8080, help="Port for the API server (default: 8080)")
@click.option("--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
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


@main.command()
@click.argument("source", required=False)
@click.option("--tags", "-t", default=None, help="Comma-separated tags for cards")
@click.option("--review", "review_only", is_flag=True, help="Skip generation, just open review UI")
@click.option("--no-browser", is_flag=True, help="Don't open browser automatically")
@click.option("--idle-timeout", default=30, type=int, help="Shutdown after N seconds of idle (0 to disable)")
def flow(source: str | None, tags: str | None, review_only: bool, no_browser: bool, idle_timeout: int):
    """Generate cards and launch review interface.

    Full workflow with source:
        uv run anki flow https://example.com/article
        uv run anki flow docs/notes.md --tags python,decorators

    Review-only mode (skip card generation):
        uv run anki flow --review
    """
    # Validate arguments
    if not review_only and not source:
        print_error("Source required unless using --review flag")
        click.echo("Usage: anki flow <url-or-file> or anki flow --review")
        sys.exit(1)

    processes: list[subprocess.Popen] = []

    try:
        # Step 1: Check/start Anki Desktop
        print_info("Checking Anki Desktop...")
        if not is_anki_running():
            print_warning("Anki not running. Starting Anki Desktop...")
            anki_proc = start_anki_desktop()
            processes.append(anki_proc)
            time.sleep(2)  # Give Anki time to initialize

        # Step 2: Wait for AnkiConnect
        print_info("Waiting for AnkiConnect...")
        client = get_client()
        if not wait_for_anki_connect(client, timeout=30):
            print_error("AnkiConnect not responding. Is Anki running with AnkiConnect installed?")
            sys.exit(1)
        print_success("Connected to AnkiConnect")

        # Step 3: Generate cards (unless --review)
        if not review_only:
            print_info(f"Generating cards from: {source}")
            if not run_claude_generation(source, tags):
                print_error("Card generation failed")
                sys.exit(1)
            print_success("Card generation complete")

        # Step 4: Start backend server
        print_info("Starting backend server...")
        backend_proc = start_backend()
        processes.append(backend_proc)

        if not wait_for_server(f"{BACKEND_URL}/api/health", timeout=30):
            print_error("Backend server failed to start")
            sys.exit(1)
        print_success(f"Backend running at {BACKEND_URL}")

        # Step 5: Start frontend dev server
        print_info("Starting frontend server...")
        frontend_proc = start_frontend()
        processes.append(frontend_proc)

        if not wait_for_server(FRONTEND_URL, timeout=60):
            print_error("Frontend server failed to start")
            sys.exit(1)
        print_success(f"Frontend running at {FRONTEND_URL}")

        # Step 6: Open browser
        if not no_browser:
            print_info("Opening browser...")
            open_browser(FRONTEND_URL)

        # Step 7: Monitor for idle or wait for Ctrl+C
        if idle_timeout > 0:
            print_info(f"Review UI ready. Auto-shutdown after {idle_timeout}s idle. Press Ctrl+C to stop.")
            while True:
                time.sleep(5)
                try:
                    last = get_last_activity()
                    idle_seconds = time.time() - last
                    if idle_seconds > idle_timeout:
                        click.echo(f"\nNo activity for {idle_timeout}s. Shutting down...")
                        break
                except requests.RequestException:
                    # Server died
                    click.echo("\nServer stopped unexpectedly.")
                    break
        else:
            print_info("Review UI ready. Press Ctrl+C to stop.")
            while True:
                time.sleep(1)
                # Check if processes are still running
                if backend_proc.poll() is not None or frontend_proc.poll() is not None:
                    click.echo("\nServer stopped unexpectedly.")
                    break

    except KeyboardInterrupt:
        click.echo("\nShutting down...")

    finally:
        # Step 8: Cleanup
        cleanup_processes(processes)
        print_success("Servers stopped.")


if __name__ == "__main__":
    main()
