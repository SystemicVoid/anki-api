"""Flashcard schema and validation based on EAT principles."""

from typing import List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
import json
import re


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
    return normalized.replace('\n', '<br>')


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
    tags: List[str] = field(default_factory=list)
    source: str = ""  # Original URL or file path
    deck: str = "Default"
    model: str = "Basic"
    anki_id: Optional[int] = None  # ID of the note in Anki, if added
    status: str = "pending"  # Review status: "pending" | "skipped" | "added"
    added_at: Optional[datetime] = None  # Timestamp when added to Anki

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
            from datetime import datetime
            data = data.copy()
            data["added_at"] = datetime.fromisoformat(data["added_at"])
        return cls(**data)


class ValidationWarning:
    """Represents a validation warning with severity level."""

    def __init__(self, message: str, severity: str = "warning"):
        self.message = message
        self.severity = severity  # 'info', 'warning', 'error'

    def __str__(self):
        icon = {"info": "ℹ️", "warning": "⚠️", "error": "❌"}.get(
            self.severity, "•"
        )
        return f"{icon} {self.message}"


def validate_encoded(card: Flashcard) -> List[ValidationWarning]:
    """Validate 'Encoded' principle - cards should have sufficient context.

    Args:
        card: Flashcard to validate

    Returns:
        List of validation warnings
    """
    warnings = []

    # Check for minimal context
    if not card.context and len(card.back) < 30:
        warnings.append(
            ValidationWarning(
                "Consider adding context for future understanding. "
                "Will you remember what this means in 6 months?",
                "warning",
            )
        )

    # Warn about very short answers without context
    if len(card.back) < 15 and not card.context:
        warnings.append(
            ValidationWarning(
                "Very brief answer without context. Consider explaining more.",
                "warning",
            )
        )

    return warnings


def validate_atomic(card: Flashcard) -> List[ValidationWarning]:
    """Validate 'Atomic' principle - questions should be focused and specific.

    Args:
        card: Flashcard to validate

    Returns:
        List of validation warnings
    """
    warnings = []

    # Check for compound questions (multiple parts)
    compound_indicators = [" and ", " or ", ";", "also"]
    front_lower = card.front.lower()

    for indicator in compound_indicators:
        if indicator in front_lower:
            warnings.append(
                ValidationWarning(
                    f"Question might be compound (contains '{indicator}'). "
                    "Consider splitting into separate cards.",
                    "warning",
                )
            )
            break

    # Check for overly long questions
    if len(card.front) > 200:
        warnings.append(
            ValidationWarning(
                f"Question is very long ({len(card.front)} chars). "
                "Atomic questions should be focused and brief.",
                "warning",
            )
        )

    # Check for vague question starters
    vague_starters = ["what about", "tell me about", "anything", "everything"]
    if any(card.front.lower().startswith(starter) for starter in vague_starters):
        warnings.append(
            ValidationWarning(
                "Question starts with vague phrase. Be more specific to trigger "
                "precise memory retrieval.",
                "warning",
            )
        )

    # Check if front is actually a question
    if not card.front.strip().endswith("?"):
        warnings.append(
            ValidationWarning(
                "Front should be a question (end with '?'). Questions are more "
                "effective than statements.",
                "error",
            )
        )

    return warnings


def validate_timeless(card: Flashcard) -> List[ValidationWarning]:
    """Validate 'Timeless' principle - cards should be self-contained.

    Args:
        card: Flashcard to validate

    Returns:
        List of validation warnings
    """
    warnings = []

    # Check for vague pronouns that need context
    vague_pronouns = ["this", "that", "these", "those", "it", "they"]
    front_words = re.findall(r"\b\w+\b", card.front.lower())

    for pronoun in vague_pronouns:
        if pronoun in front_words:
            warnings.append(
                ValidationWarning(
                    f"Contains vague pronoun '{pronoun}'. "
                    "Ensure the question is clear without prior context.",
                    "warning",
                )
            )
            break

    # Check for time-dependent references
    time_references = [
        "today",
        "yesterday",
        "recently",
        "last week",
        "currently",
        "now",
    ]
    if any(ref in card.front.lower() for ref in time_references):
        warnings.append(
            ValidationWarning(
                "Contains time-dependent reference. "
                "Will this be clear in the future?",
                "warning",
            )
        )

    # Check for undefined abbreviations or jargon
    # Look for short uppercase words that might be abbreviations
    uppercase_words = re.findall(r"\b[A-Z]{2,}\b", card.front)
    if uppercase_words and not card.context:
        warnings.append(
            ValidationWarning(
                f"Contains abbreviations ({', '.join(uppercase_words)}). "
                "Consider adding context to explain them.",
                "info",
            )
        )

    return warnings


def validate_card(card: Flashcard) -> List[ValidationWarning]:
    """Run all EAT principle validations on a card.

    Args:
        card: Flashcard to validate

    Returns:
        List of all validation warnings
    """
    warnings = []

    # Basic field validation
    if not card.front.strip():
        warnings.append(
            ValidationWarning("Front (question) cannot be empty.", "error")
        )

    if not card.back.strip():
        warnings.append(
            ValidationWarning("Back (answer) cannot be empty.", "error")
        )

    # EAT principle validations
    warnings.extend(validate_encoded(card))
    warnings.extend(validate_atomic(card))
    warnings.extend(validate_timeless(card))

    return warnings


def load_cards_from_json(file_path: str) -> List[Flashcard]:
    """Load flashcards from a JSON file.

    Args:
        file_path: Path to JSON file containing card data

    Returns:
        List of Flashcard objects

    Raises:
        ValueError: If JSON is invalid or cards are malformed
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
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


def save_cards_to_json(cards: List[Flashcard], file_path: str) -> None:
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

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=datetime_serializer)
