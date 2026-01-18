#!/usr/bin/env python3
"""
Reformat existing Anki cards to match new formatting guidelines.

This script:
1. Fetches existing cards from Anki
2. Reformats them to remove markdown/HTML and apply plain-text formatting
3. Shows preview of changes before applying
4. Updates cards via AnkiConnect (does NOT affect scheduling/SRS data)
"""

import re

import click

from src.anki_client import AnkiClient


def convert_newlines_to_html(text: str) -> str:
    """Convert plain newlines to HTML <br> tags for Anki display.

    Anki displays card content as HTML, so plain newlines are collapsed.
    This function converts \\n to <br> tags for proper rendering.

    Args:
        text: Text with plain newlines

    Returns:
        Text with <br> tags for HTML rendering
    """
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return normalized.replace("\n", "<br>")


def normalize_html_value(text: str) -> str:
    """Normalize HTML text for safe comparison."""
    return text.replace("\r\n", "\n").strip()


def strip_html_tags(text: str) -> str:
    """Remove HTML tags from text, preserving line breaks."""
    # Remove <br>, <br/>, <br />, etc. → newline
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)

    # Convert block-level HTML tags to newlines
    # Both opening and closing tags become newlines (excess will be cleaned later)
    block_tags = [
        "div",
        "p",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "li",
        "tr",
        "ul",
        "ol",
    ]
    for tag in block_tags:
        # Both opening and closing tags → newline
        text = re.sub(f"</{tag}>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(f"<{tag}[^>]*>", "\n", text, flags=re.IGNORECASE)

    # Remove any remaining HTML tags (inline tags like <b>, <i>, <span>, etc.)
    text = re.sub(r"<[^>]+>", "", text)

    # Decode HTML entities
    text = text.replace("&nbsp;", " ")
    text = text.replace("&amp;", "&")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&quot;", '"')

    return text


def strip_markdown(text: str) -> str:
    """Remove markdown formatting from text."""
    # Remove bold **text**
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)

    # Remove italic *text* or _text_
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"_([^_]+)_", r"\1", text)

    # Remove code blocks ```text```
    text = re.sub(r"```[^`]*```", "", text)

    # Remove inline code `text`
    text = re.sub(r"`([^`]+)`", r"\1", text)

    return text


def fix_separator(text: str) -> str:
    """Fix separator formatting to use clean --- with blank lines."""
    # Match various separator patterns with optional &nbsp; and <br> tags
    patterns = [
        r"&nbsp;---<br><br>",  # Old pattern from example
        r"<br><br>&nbsp;---<br><br>",
        r"\n---\n",  # Single newline
        r"\n\n---\n",  # Missing trailing newlines
        r"\n---\n\n",  # Missing leading newlines
        r"---",  # No newlines at all
    ]

    for pattern in patterns:
        text = re.sub(pattern, "\n\n---\n\n", text)

    return text


def remove_context_label(text: str) -> str:
    """Remove 'Context:' label after separator."""
    # Remove **Context:** or Context: after separator
    text = re.sub(r"(---\s*\n\s*)\*\*Context:\*\*\s*", r"\1", text)
    text = re.sub(r"(---\s*\n\s*)Context:\s*", r"\1", text)

    return text


def fix_list_formatting(text: str) -> str:
    """Fix list formatting: convert (1), (2), (3) to 1., 2., 3. and ensure newlines between items."""
    # Convert parenthetical numbering to standard format
    # Only match single or double digit numbers that appear to be list items
    # Pattern: (N) where N is 1-2 digits, followed by space and text (not just a year in text)
    # Must be at start of line or after newline, and number should be small (1-99)

    def replace_list_item(match):
        """Only replace if it looks like a list item (small number)."""
        num = int(match.group(1))
        if num <= 20:  # Only convert small numbers that are likely list items
            return f"{num}. "
        return match.group(0)  # Keep original for large numbers like years

    # Match (N) followed by space, at start or after newline
    text = re.sub(
        r"(?:^|(?<=\n))\((\d+)\)\s+", replace_list_item, text, flags=re.MULTILINE
    )

    # Ensure each numbered list item (1., 2., 3., etc.) is on its own line
    # Match pattern: comma/period followed by space and then a number with period (next list item)
    # Example: "text,2. next" or "text.2. next" → "text,\n2. next"
    text = re.sub(r"([,.])\s*(\d{1,2}\.\s+)", r"\1\n\2", text)

    # Also handle unordered lists: ensure "- item" patterns have newlines
    # Match: text followed by "- " (single dash with space, not ---)
    # Negative lookbehind to avoid matching --- separator
    text = re.sub(r"([^\n-])\s*(-\s+)(?=[^\-])", r"\1\n\2", text)

    return text


def clean_whitespace(text: str) -> str:
    """Clean up excessive whitespace while preserving intentional spacing."""
    # Remove trailing whitespace from lines
    lines = text.split("\n")
    lines = [line.rstrip() for line in lines]
    text = "\n".join(lines)

    # Collapse multiple blank lines (more than 2) into 2
    text = re.sub(r"\n{4,}", "\n\n\n", text)

    # Remove leading/trailing whitespace from entire text
    text = text.strip()

    return text


def reformat_card_field(text: str) -> str:
    """Apply all reformatting rules to a card field."""
    if not text:
        return text

    # Order matters here
    text = strip_html_tags(text)
    text = strip_markdown(text)
    text = fix_separator(text)
    text = remove_context_label(text)
    text = fix_list_formatting(text)
    text = clean_whitespace(text)

    return text


def preview_changes(
    original: str, reformatted: str, field_name: str, note_id: int
) -> None:
    """Display a diff-like preview of changes."""
    if original == reformatted:
        click.secho(f"\n{field_name} (Note {note_id}): No changes needed", fg="green")
        return

    click.secho(f"\n{field_name} (Note {note_id}):", fg="yellow", bold=True)
    click.secho("BEFORE:", fg="red")
    click.echo(original[:300] + ("..." if len(original) > 300 else ""))
    click.secho("\nAFTER:", fg="green")
    click.echo(reformatted[:300] + ("..." if len(reformatted) > 300 else ""))
    click.echo("-" * 80)


def preview_html_only_change(field_name: str, note_id: int, preview_text: str) -> None:
    """Preview output for newline-only fixes."""
    click.secho(f"\n{field_name} (Note {note_id}):", fg="yellow", bold=True)
    click.secho(
        "No text edits required — converting plain newlines to <br> tags for Anki.",
        fg="cyan",
    )
    if preview_text:
        click.echo(preview_text[:300] + ("..." if len(preview_text) > 300 else ""))
        click.echo("-" * 80)


@click.command()
@click.option(
    "--query",
    default="added:30",
    help="Anki search query (default: added:30 for last 30 days)",
)
@click.option(
    "--limit",
    default=5,
    type=int,
    help="Number of cards to process (default: 5 for preview)",
)
@click.option(
    "--apply", is_flag=True, help="Actually apply changes (default: preview only)"
)
def main(query: str, limit: int, apply: bool):
    """Reformat Anki cards to match new formatting guidelines."""

    client = AnkiClient()

    # Check connection
    click.echo("Checking Anki connection...")
    if not client.ping():
        click.secho("❌ Anki is not running or AnkiConnect is not installed", fg="red")
        return

    click.secho("✓ Connected to Anki", fg="green")

    # Find notes
    click.echo(f"\nSearching for notes with query: {query}")
    note_ids = client.find_notes(query)

    if not note_ids:
        click.secho("No notes found matching query", fg="yellow")
        return

    # Limit to requested number
    note_ids = note_ids[:limit]
    click.echo(f"Found {len(note_ids)} notes to process")

    # Get note details
    click.echo("Fetching note details...")
    notes = client.get_note_info(note_ids)

    # Process each note
    changes: list[tuple[int, dict[str, str]]] = []

    for note in notes:
        note_id = note["noteId"]
        reformatted_fields = {}
        has_changes = False

        for field_name, field_data in note["fields"].items():
            original = field_data.get("value", "")
            reformatted_plain = reformat_card_field(original)
            reformatted_html = convert_newlines_to_html(reformatted_plain)

            reformatted_fields[field_name] = reformatted_html

            html_changed = normalize_html_value(original) != normalize_html_value(
                reformatted_html
            )
            text_changed = original != reformatted_plain

            if html_changed:
                has_changes = True
                if not apply:
                    if text_changed:
                        preview_changes(
                            original,
                            reformatted_plain,
                            field_name,
                            note_id,
                        )
                    else:
                        preview_html_only_change(
                            field_name,
                            note_id,
                            reformatted_plain,
                        )

        if has_changes:
            changes.append((note_id, reformatted_fields))

    # Summary
    click.echo("\n" + "=" * 80)
    click.secho(f"\nSummary: {len(changes)} notes with changes", fg="cyan", bold=True)

    if not apply:
        click.secho("\n⚠️  PREVIEW MODE - No changes applied", fg="yellow", bold=True)
        click.echo("\nTo apply these changes, run with --apply flag:")
        click.echo(
            f"  uv run python reformat_cards.py --query '{query}' --limit {limit} --apply"
        )
        click.echo("\nTo process ALL matching cards:")
        click.echo(
            f"  uv run python reformat_cards.py --query '{query}' --limit 99999 --apply"
        )
        click.echo(
            "\n📖 Editing card content does NOT affect Anki's scheduling/SRS data"
        )
        click.echo("   (Review history, intervals, and ease factors remain unchanged)")
    else:
        # Apply changes
        click.echo("\n" + "=" * 80)
        if not changes:
            click.secho("No changes to apply!", fg="green")
            return

        click.secho(
            f"\n⚠️  About to update {len(changes)} notes", fg="yellow", bold=True
        )
        click.echo("This will NOT affect scheduling, intervals, or review history.")

        if not click.confirm("\nProceed with updates?"):
            click.echo("Aborted.")
            return

        click.echo("\nApplying changes...")
        for note_id, reformatted_fields in changes:
            try:
                client.update_note_fields(note_id, reformatted_fields)
                click.secho(f"✓ Updated note {note_id}", fg="green")
            except Exception as e:
                click.secho(f"✗ Failed to update note {note_id}: {e}", fg="red")

        click.secho(
            f"\n✓ Completed! Updated {len(changes)} notes", fg="green", bold=True
        )


if __name__ == "__main__":
    main()
