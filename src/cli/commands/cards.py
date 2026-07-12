"""Card management commands: extract, review, add, quick, find, delete."""

import sys
from pathlib import Path

import click

from src.anki_client import AnkiConnectError
from src.anki_notes import add_card_to_anki
from src.cli.anki_lifecycle import ensure_anki_running, get_client
from src.cli.output import (
    print_card,
    print_error,
    print_info,
    print_success,
    print_validation_warnings,
    print_warning,
)
from src.cli.utils import default_docx_output_path
from src.documents import export_docx_to_markdown
from src.review import ReviewSession
from src.schema import Flashcard, validate_card


@click.command("extract")
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


@click.command()
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
@click.option(
    "--reset",
    is_flag=True,
    help="Re-open skipped cards for another review pass",
)
def review(file: Path, deck: str, show_warnings: bool, reset: bool):
    """Review and approve cards from a JSON file before adding to Anki.

    Interactively review each card with options to:
    - (a)pprove: Add card to Anki
    - (e)dit: Modify card fields
    - (s)kip: Skip this card
    - (q)uit: Stop reviewing

    Review progress is persisted to the file. If interrupted, the review
    will resume from the first unreviewed card on next run.
    Use --reset to re-open skipped cards for another pass (already-added
    cards stay linked to their Anki notes).
    """
    # Ensure Anki is running (starts it if needed)
    client = ensure_anki_running()

    try:
        session = ReviewSession.load(str(file))
    except ValueError as e:
        print_error(str(e))
        sys.exit(1)

    if not session.cards:
        print_warning("No cards found in file.")
        sys.exit(0)

    if reset:
        session.reset()
        print_info("Re-opened skipped cards for review.")

    pending = session.pending_indices()

    if not pending:
        print_success("All cards have been reviewed!")
        counts = session.counts()
        click.echo(f"  Previously added: {counts.added}")
        click.echo(f"  Previously skipped: {counts.skipped}")
        click.echo("\nUse --reset to re-open skipped cards.")
        sys.exit(0)

    # Show resume info if some cards were already reviewed
    already_reviewed = len(session.cards) - len(pending)
    if already_reviewed > 0:
        print_info(f"Resuming review: {already_reviewed} cards already processed")
        counts = session.counts()
        click.echo(f"  Added: {counts.added}, Skipped: {counts.skipped}")
        click.echo()

    print_info(f"Reviewing {len(pending)} pending cards from {file.name}")
    print_success("✓ Connected to Anki\n")

    session_added = 0
    session_skipped = 0

    for review_num, card_idx in enumerate(pending, 1):
        card = session.card(card_idx)

        # Print card (show position as "review X of Y pending")
        print_card(card, review_num, len(pending))

        if show_warnings:
            print_validation_warnings(validate_card(card))

        # Get user action
        click.echo()
        action = click.prompt(
            "Action",
            type=click.Choice(["a", "e", "s", "q"], case_sensitive=False),
            default="a",
            show_choices=True,
        ).lower()

        if action == "q":
            print_info("\nStopped reviewing. Progress has been saved.")
            break

        if action == "s":
            print_warning("Skipped card.")
            session.skip(card_idx)
            session_skipped += 1
            continue

        if action == "e":
            # Edit mode
            click.echo("\nEdit card (press Enter to keep current value):")
            new_front = click.prompt("Front", default=card.front)
            new_back = click.prompt("Back", default=card.back)
            new_context = click.prompt("Context", default=card.context)
            new_tags = click.prompt(
                "Tags (comma-separated)", default=",".join(card.tags)
            )
            session.edit(
                card_idx,
                front=new_front,
                back=new_back,
                context=new_context,
                tags=[t.strip() for t in new_tags.split(",") if t.strip()],
            )

            if not click.confirm("\nApprove edited card?", default=True):
                print_warning("Skipped card after edit.")
                session.skip(card_idx)
                session_skipped += 1
                continue

        # Approve (action == 'a' or after edit approval)
        try:
            approved = session.approve(card_idx, client, deck_override=deck)
            print_success(f"✓ Card added to Anki (ID: {approved.anki_id})")
            session_added += 1
        except (AnkiConnectError, ValueError) as e:
            print_error(f"Failed to add card: {e}")
            # Status left untouched so the card can be retried
            session_skipped += 1

    # Summary
    click.echo(f"\n{'=' * 60}")
    print_success("Review session complete!")
    click.echo(f"  This session - Added: {session_added}, Skipped: {session_skipped}")

    counts = session.counts()
    click.echo(
        f"  Total progress - Added: {counts.added}, "
        f"Skipped: {counts.skipped}, Pending: {counts.pending}"
    )


@click.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--deck",
    default=None,
    help="Override deck name for all cards (default: use card's deck)",
)
def add(file: Path, deck: str):
    """Add cards from JSON file directly to Anki without review.

    Use this for batch adding cards you've already reviewed. Cards already
    added are skipped; accepted cards are marked added and the file is saved.
    """
    # Ensure Anki is running (starts it if needed)
    client = ensure_anki_running()

    try:
        session = ReviewSession.load(str(file))
    except ValueError as e:
        print_error(str(e))
        sys.exit(1)

    if not session.cards:
        print_warning("No cards found in file.")
        sys.exit(0)

    print_info(f"Adding cards from {file.name} to Anki...")

    try:
        note_ids = session.submit_all(client, deck_override=deck)
    except (AnkiConnectError, ValueError) as e:
        print_error(f"Failed to add cards: {e}")
        sys.exit(1)

    added = sum(1 for nid in note_ids if nid is not None)
    rejected = len(note_ids) - added
    counts = session.counts()

    print_success(f"✓ Successfully added {added} cards")
    if rejected > 0:
        print_warning(f"  {rejected} cards not added (duplicates?)")
    click.echo(
        f"  Total in file - Added: {counts.added}, "
        f"Skipped: {counts.skipped}, Pending: {counts.pending}"
    )


@click.command()
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
def quick(
    front: str, back: str, deck: str, tags: str, context: str, show_warnings: bool
):
    """Quickly create a single flashcard.

    Example:
        anki quick "What is the capital of France?" "Paris" --tags geography
    """
    # Ensure Anki is running (starts it if needed)
    client = ensure_anki_running()

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
        note_id = add_card_to_anki(client, card)
        print_success(f"✓ Card added to Anki (ID: {note_id})")
    except (AnkiConnectError, ValueError) as e:
        print_error(f"Failed to add card: {e}")
        sys.exit(1)


@click.command()
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


@click.command()
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


card_commands = [extract_docx, review, add, quick, find, delete]
