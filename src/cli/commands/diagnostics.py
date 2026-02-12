"""Diagnostic commands: ping, decks, models."""

import sys

import click

from src.anki_client import AnkiConnectError
from src.cli.anki_lifecycle import get_client
from src.cli.output import print_error, print_info, print_success


@click.command()
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


@click.command("decks")
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


@click.command("models")
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


diagnostics_commands = [ping, list_decks, list_models]
