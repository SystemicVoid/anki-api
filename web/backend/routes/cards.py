"""Card file management routes."""

import os
import re
from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException

from src.schema import Flashcard, load_cards_from_json, save_cards_to_json, validate_card

from ..models import (
    CardResponse,
    CardUpdate,
    CardWithValidation,
    CardsFileResponse,
    FileListResponse,
    ValidationWarningResponse,
)

router = APIRouter()

# Cards directory relative to project root
CARDS_DIR = Path(__file__).parent.parent.parent.parent / "cards"


def validate_filename(filename: str) -> bool:
    """Validate filename to prevent path traversal attacks."""
    if not filename:
        return False
    # Only allow alphanumeric, underscore, hyphen, and .json extension
    if not re.match(r"^[\w\-]+\.json$", filename):
        return False
    # No path separators
    if "/" in filename or "\\" in filename:
        return False
    return True


def flashcard_to_response(card: Flashcard) -> CardResponse:
    """Convert Flashcard to API response model."""
    return CardResponse(
        front=card.front,
        back=card.back,
        context=card.context,
        tags=card.tags,
        source=card.source,
        deck=card.deck,
        model=card.model,
    )


def get_card_with_validation(card: Flashcard, index: int, total: int) -> CardWithValidation:
    """Get card with its validation warnings."""
    warnings = validate_card(card)
    return CardWithValidation(
        card=flashcard_to_response(card),
        warnings=[
            ValidationWarningResponse(message=w.message, severity=w.severity)
            for w in warnings
        ],
        index=index,
        total=total,
    )


@router.get("/files", response_model=FileListResponse)
async def list_card_files():
    """List available JSON card files."""
    if not CARDS_DIR.exists():
        return FileListResponse(files=[])

    files = [
        f.name for f in CARDS_DIR.iterdir()
        if f.is_file() and f.suffix == ".json"
    ]
    # Sort by modification time, newest first
    files.sort(key=lambda f: (CARDS_DIR / f).stat().st_mtime, reverse=True)
    return FileListResponse(files=files)


@router.get("/{filename}", response_model=CardsFileResponse)
async def get_cards(filename: str):
    """Load all cards from a JSON file with validation warnings."""
    if not validate_filename(filename):
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_path = CARDS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")

    try:
        cards = load_cards_from_json(str(file_path))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    cards_with_validation = [
        get_card_with_validation(card, i, len(cards))
        for i, card in enumerate(cards)
    ]

    return CardsFileResponse(
        filename=filename,
        cards=cards_with_validation,
        total=len(cards),
    )


@router.put("/{filename}/{index}", response_model=CardWithValidation)
async def update_card(filename: str, index: int, update: CardUpdate):
    """Update a card's fields and return with new validation warnings."""
    if not validate_filename(filename):
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_path = CARDS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")

    try:
        cards = load_cards_from_json(str(file_path))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if index < 0 or index >= len(cards):
        raise HTTPException(status_code=404, detail=f"Card index {index} out of range")

    card = cards[index]

    # Apply updates
    if update.front is not None:
        card.front = update.front
    if update.back is not None:
        card.back = update.back
    if update.context is not None:
        card.context = update.context
    if update.tags is not None:
        card.tags = update.tags

    # Save back to file
    save_cards_to_json(cards, str(file_path))

    return get_card_with_validation(card, index, len(cards))
