"""Command-line interface for anki-api."""

import click

from src.cli.commands.cards import card_commands
from src.cli.commands.diagnostics import diagnostics_commands
from src.cli.commands.orchestration import orchestration_commands

COMMAND_SECTIONS = [
    ("Stack", ["up", "down", "status", "logs"]),
    ("Cards", ["add", "review", "quick", "find", "delete"]),
    ("Generation", ["flow", "extract"]),
    ("Server", ["serve"]),
    ("Diagnostics", ["ping", "decks", "models"]),
]


class GroupedGroup(click.Group):
    """Click group that displays commands in labelled sections."""

    def format_commands(self, ctx: click.Context, formatter: click.HelpFormatter):
        commands = {
            name: self.get_command(ctx, name) for name in self.list_commands(ctx)
        }
        shown: set[str] = set()

        for section, names in COMMAND_SECTIONS:
            rows = []
            for name in names:
                cmd = commands.get(name)
                if cmd is None or cmd.hidden:
                    continue
                help_text = cmd.get_short_help_str(limit=formatter.width)
                rows.append((name, help_text))
                shown.add(name)
            if rows:
                with formatter.section(section):
                    formatter.write_dl(rows)

        # Catch-all for any commands not in sections
        leftover = []
        for name, cmd in commands.items():
            if cmd is None or name in shown or cmd.hidden:
                continue
            leftover.append((name, cmd.get_short_help_str(limit=formatter.width)))
        if leftover:
            with formatter.section("Other"):
                formatter.write_dl(leftover)


@click.group(cls=GroupedGroup)
def main():
    """Anki API - agent-assisted flashcard generation for Anki."""


# Register all commands
for cmd in diagnostics_commands + card_commands + orchestration_commands:
    main.add_command(cmd)


if __name__ == "__main__":
    main()
