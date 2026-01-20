#!/usr/bin/env -S uv run
"""Save flashcards from stdin JSON to timestamped file.

Usage:
    echo '[{"front":"Q","back":"A","tags":[]}]' | uv run python scripts/save_cards.py topic [source_url]

This script is designed to be executed (not loaded into context) by Claude.
It validates cards against the Flashcard schema and saves to a timestamped file.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

from src.schema import Flashcard, save_cards_to_json, validate_card


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: save_cards.py <topic> [source]", file=sys.stderr)
        print("Reads JSON array of cards from stdin", file=sys.stderr)
        sys.exit(1)

    topic = sys.argv[1]
    source = sys.argv[2] if len(sys.argv) > 2 else ""

    # Read JSON from stdin
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, list):
        data = [data]

    # Convert to Flashcard objects with validation
    cards: list[Flashcard] = []
    errors: list[str] = []

    for i, card_data in enumerate(data):
        try:
            # Add source if not present
            if source and not card_data.get("source"):
                card_data["source"] = source

            card = Flashcard(**card_data)
            warnings = validate_card(card)

            if any(w.severity == "error" for w in warnings):
                error_msgs = [str(w) for w in warnings if w.severity == "error"]
                errors.append(f"Card {i + 1}: {error_msgs}")
            else:
                cards.append(card)
        except Exception as e:
            errors.append(f"Card {i + 1}: {e}")

    if errors:
        print("VALIDATION ERRORS:", file=sys.stderr)
        for err in errors:
            print(f"  {err}", file=sys.stderr)
        if not cards:
            sys.exit(1)
        print(f"Continuing with {len(cards)} valid cards...", file=sys.stderr)

    # Ensure cards directory exists
    Path("cards").mkdir(exist_ok=True)

    # Save cards with timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Sanitize topic for filename (keep alphanumeric, hyphens, underscores)
    safe_topic = "".join(c if c.isalnum() or c in "-_" else "-" for c in topic).strip(
        "-"
    )
    output_file = f"cards/{safe_topic}_{timestamp}.json"

    save_cards_to_json(cards, output_file)

    print(f"SUCCESS: Saved {len(cards)} cards to {output_file}")


if __name__ == "__main__":
    main()
