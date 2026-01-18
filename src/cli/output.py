"""Output formatting helpers for CLI."""

import click

from src.schema import Flashcard, ValidationWarning


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


def print_card(
    card: Flashcard, index: int | None = None, total: int | None = None
) -> None:
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


def print_validation_warnings(warnings: list[ValidationWarning]) -> None:
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
