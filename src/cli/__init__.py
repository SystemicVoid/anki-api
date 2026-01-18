"""Command-line interface for anki-api."""

import click

from src.cli.commands.cards import card_commands
from src.cli.commands.diagnostics import diagnostics_commands
from src.cli.commands.orchestration import orchestration_commands


@click.group()
def main():
    """Anki API - Agent-assisted flashcard generation for Anki."""
    pass


# Register all commands
for cmd in diagnostics_commands + card_commands + orchestration_commands:
    main.add_command(cmd)


if __name__ == "__main__":
    main()
