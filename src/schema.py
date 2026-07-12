"""Flashcard schema and validation based on EAT principles."""

import json
import os
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

from src.media import resolve_media_path


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
    images: list[str] = field(default_factory=list)  # Filenames under cards/media
    source: str = ""  # Original URL or file path
    deck: str = "Default"
    model: str = "Basic"
    anki_id: int | None = None  # ID of the note in Anki, if added
    status: str = "pending"  # Review status: "pending" | "skipped" | "added"
    added_at: datetime | None = None  # Timestamp when added to Anki

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

    for filename in card.images:
        try:
            resolve_media_path(filename)
        except ValueError as e:
            warnings.append(ValidationWarning(str(e), "error"))

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
    """Save flashcards to a JSON file atomically.

    The cards are written to a temporary file in the same directory and then
    :func:`os.replace`-d over the target, so a crash mid-write can never leave a
    partially-written (corrupt) card file — a reader sees either the old file or
    the complete new one. Review progress is persisted after every transition,
    so this durability matters.

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

    target = Path(file_path)
    # A unique temp name (not a fixed ".{name}.tmp") so two writers to the same
    # target never clobber each other's in-progress file before the replace.
    fd, tmp_name = tempfile.mkstemp(
        dir=target.parent, prefix=f".{target.name}.", suffix=".tmp"
    )
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(
                data, f, indent=2, ensure_ascii=False, default=datetime_serializer
            )
            f.flush()
            os.fsync(f.fileno())
        tmp.replace(target)
    finally:
        tmp.unlink(missing_ok=True)
