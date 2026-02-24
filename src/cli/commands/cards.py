"""Card management commands: extract, review, add, quick, find, delete."""

import sys
from datetime import UTC, datetime
from pathlib import Path

import click

from src.anki_client import AnkiConnectError
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
from src.schema import (
    Flashcard,
    load_cards_from_json,
    save_cards_to_json,
    validate_card,
)


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
    help="Reset all cards to pending status and start fresh review",
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
    Use --reset to start a fresh review of all cards.
    """
    # Ensure Anki is running (starts it if needed)
    client = ensure_anki_running()

    # Load cards
    try:
        cards = load_cards_from_json(str(file))
    except ValueError as e:
        print_error(str(e))
        sys.exit(1)

    if not cards:
        print_warning("No cards found in file.")
        sys.exit(0)

    # Reset all cards to pending if requested
    if reset:
        for card in cards:
            card.status = "pending"
            card.anki_id = None
            card.added_at = None
        save_cards_to_json(cards, str(file))
        print_info("Reset all cards to pending status.")

    # Find pending cards (not yet reviewed)
    pending_indices = [i for i, card in enumerate(cards) if card.status == "pending"]

    if not pending_indices:
        print_success("All cards have been reviewed!")
        # Show summary of existing statuses
        added = sum(1 for c in cards if c.status == "added")
        skipped = sum(1 for c in cards if c.status == "skipped")
        click.echo(f"  Previously added: {added}")
        click.echo(f"  Previously skipped: {skipped}")
        click.echo("\nUse --reset to review all cards again.")
        sys.exit(0)

    # Show resume info if some cards were already reviewed
    already_reviewed = len(cards) - len(pending_indices)
    if already_reviewed > 0:
        print_info(f"Resuming review: {already_reviewed} cards already processed")
        added = sum(1 for c in cards if c.status == "added")
        skipped = sum(1 for c in cards if c.status == "skipped")
        click.echo(f"  Added: {added}, Skipped: {skipped}")
        click.echo()

    print_info(f"Reviewing {len(pending_indices)} pending cards from {file.name}")
    print_success("✓ Connected to Anki\n")

    session_added = 0
    session_skipped = 0

    for review_num, card_idx in enumerate(pending_indices, 1):
        card = cards[card_idx]

        # Override deck if specified
        if deck:
            card.deck = deck

        # Print card (show position as "review X of Y pending")
        print_card(card, review_num, len(pending_indices))

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
            print_info("\nStopped reviewing. Progress has been saved.")
            break

        elif action.lower() == "s":
            print_warning("Skipped card.")
            card.status = "skipped"
            save_cards_to_json(cards, str(file))
            session_skipped += 1
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
                card.status = "skipped"
                save_cards_to_json(cards, str(file))
                session_skipped += 1
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
            card.status = "added"
            card.anki_id = note_id
            card.added_at = datetime.now(UTC)
            save_cards_to_json(cards, str(file))
            session_added += 1
        except AnkiConnectError as e:
            print_error(f"Failed to add card: {e}")
            # Don't change status on error - let user retry
            session_skipped += 1

    # Summary
    click.echo(f"\n{'=' * 60}")
    print_success("Review session complete!")
    click.echo(f"  This session - Added: {session_added}, Skipped: {session_skipped}")

    # Show total progress
    total_added = sum(1 for c in cards if c.status == "added")
    total_skipped = sum(1 for c in cards if c.status == "skipped")
    total_pending = sum(1 for c in cards if c.status == "pending")
    click.echo(
        f"  Total progress - Added: {total_added}, Skipped: {total_skipped}, Pending: {total_pending}"
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

    Use this for batch adding cards you've already reviewed.
    """
    # Ensure Anki is running (starts it if needed)
    client = ensure_anki_running()

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
