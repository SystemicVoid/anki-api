"""Card file management routes."""

import os
import re
from pathlib import Path
from typing import List
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from src.anki_client import AnkiClient, AnkiConnectError
from src.schema import Flashcard, load_cards_from_json, save_cards_to_json, validate_card

from ..models import (
    CardResponse,
    CardUpdate,
    CardWithValidation,
    CardsFileResponse,
    FileListResponse,
    ValidationWarningResponse,
    FileStat,
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
        anki_id=card.anki_id,
        status=card.status,
        added_at=card.added_at,
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
    """List available JSON card files with review statistics."""
    if not CARDS_DIR.exists():
        return FileListResponse(files=[])

    files = []
    for f in CARDS_DIR.iterdir():
        if f.is_file() and f.suffix == ".json":
            try:
                cards = load_cards_from_json(str(f))

                # Calculate statistics based on status field
                added_count = sum(1 for c in cards if c.status == "added")
                skipped_count = sum(1 for c in cards if c.status == "skipped")
                pending_count = sum(1 for c in cards if c.status == "pending")

                files.append(FileStat(
                    filename=f.name,
                    total_cards=len(cards),
                    added_cards=added_count,
                    skipped_cards=skipped_count,
                    pending_cards=pending_count,
                ))
            except Exception:
                files.append(FileStat(
                    filename=f.name,
                    total_cards=0,
                    added_cards=0,
                    skipped_cards=0,
                    pending_cards=0,
                ))

    # Sort by modification time (most recent first)
    files.sort(key=lambda item: (CARDS_DIR / item.filename).stat().st_mtime, reverse=True)

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


@router.post("/{filename}/{index}/approve", response_model=CardWithValidation)
async def approve_card(filename: str, index: int):
    """Approve a card: Add to Anki and save resulting ID and timestamp to file."""
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
    client = AnkiClient()

    try:
        if card.status == "added" and card.anki_id:
            # Already approved, return as-is (idempotent)
            pass
        else:
            anki_note = card.to_anki_note()
            note_id = client.add_note(
                deck_name=anki_note["deckName"],
                model_name=anki_note["modelName"],
                fields=anki_note["fields"],
                tags=anki_note["tags"],
            )
            card.anki_id = note_id
            card.status = "added"
            card.added_at = datetime.now(timezone.utc)
            save_cards_to_json(cards, str(file_path))

    except AnkiConnectError as e:
        raise HTTPException(status_code=500, detail=f"Anki Connect Error: {e}")

    return get_card_with_validation(card, index, len(cards))


@router.post("/{filename}/{index}/skip", response_model=CardWithValidation)
async def skip_card(filename: str, index: int):
    """Skip a card: Mark as skipped and persist to file."""
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

    # Only update if not already processed (idempotent)
    if card.status == "pending":
        card.status = "skipped"
        save_cards_to_json(cards, str(file_path))

    return get_card_with_validation(card, index, len(cards))
