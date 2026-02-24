"""Flashcard schema and validation based on EAT principles."""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path


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


@dataclass
class Flashcard:
    """Represents a single flashcard with EAT principles validation.

    EAT Framework:
    - Encoded: Learn before you memorize (requires understanding)
    - Atomic: Specific and focused questions
    - Timeless: Design for your future self (self-contained)
    """

    front: str  # Question (should end with ?)
    back: str  # Answer
    context: str = ""  # Supplementary context for future understanding
    tags: list[str] = field(default_factory=list)
    source: str = ""  # Original URL or file path
    deck: str = "Default"
    model: str = "Basic"
    anki_id: int | None = None  # ID of the note in Anki, if added
    status: str = "pending"  # Review status: "pending" | "skipped" | "added"
    added_at: datetime | None = None  # Timestamp when added to Anki

    def to_anki_note(self) -> dict:
        """Convert to AnkiConnect note format.

        Returns:
            Dictionary formatted for AnkiConnect addNote
        """
        # Combine back and context if context exists
        back_content = self.back
        if self.context:
            back_content += f"\n\n---\n\n{self.context}"

        # Convert newlines to HTML for Anki display
        front_html = convert_newlines_to_html(self.front)
        back_html = convert_newlines_to_html(back_content)

        return {
            "deckName": self.deck,
            "modelName": self.model,
            "fields": {
                "Front": front_html,
                "Back": back_html,
            },
            "tags": self.tags,
        }

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Flashcard":
        """Create Flashcard from dictionary."""
        # Parse datetime string if present
        if "added_at" in data and isinstance(data["added_at"], str):
            data = data.copy()
            data["added_at"] = datetime.fromisoformat(data["added_at"])
        return cls(**data)


class ValidationWarning:
    """Represents a validation warning with severity level."""

    def __init__(self, message: str, severity: str = "warning"):
        self.message = message
        self.severity = severity  # 'info', 'warning', 'error'

    def __str__(self):
        icon = {"info": "ℹ️", "warning": "⚠️", "error": "❌"}.get(self.severity, "•")
        return f"{icon} {self.message}"


def validate_card(card: Flashcard) -> list[ValidationWarning]:
    """Validate card structure.

    EAT 2.0 Philosophy: Mechanical pattern-matching rules (character counts,
    keyword detection) are removed. Quality principles like atomicity,
    contextual self-sufficiency, and interference management are now
    guidance for agent judgment, not programmatic checks.

    See docs/EAT_FRAMEWORK.md for the cognitive science-grounded principles
    that should guide card creation.

    This function only validates unambiguous structural requirements:
    - Front and back cannot be empty

    Args:
        card: Flashcard to validate

    Returns:
        List of validation warnings (errors only for structural issues)
    """
    warnings = []

    if not card.front.strip():
        warnings.append(ValidationWarning("Front cannot be empty.", "error"))

    if not card.back.strip():
        warnings.append(ValidationWarning("Back cannot be empty.", "error"))

    return warnings


def load_cards_from_json(file_path: str) -> list[Flashcard]:
    """Load flashcards from a JSON file.

    Args:
        file_path: Path to JSON file containing card data

    Returns:
        List of Flashcard objects

    Raises:
        ValueError: If JSON is invalid or cards are malformed
    """
    try:
        with Path(file_path).open(encoding="utf-8") as f:
            data = json.load(f)

        # Handle both single card and array of cards
        if isinstance(data, dict):
            data = [data]

        cards = [Flashcard.from_dict(card_data) for card_data in data]
        return cards

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {file_path}: {e}") from e
    except Exception as e:
        raise ValueError(f"Error loading cards from {file_path}: {e}") from e


def save_cards_to_json(cards: list[Flashcard], file_path: str) -> None:
    """Save flashcards to a JSON file.

    Args:
        cards: List of Flashcard objects
        file_path: Path to output JSON file
    """

    def datetime_serializer(obj):
        """Custom JSON serializer for datetime objects."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    data = [card.to_dict() for card in cards]

    with Path(file_path).open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=datetime_serializer)
