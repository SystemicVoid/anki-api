"""Card file management routes.

Thin adapters over :class:`~src.review.ReviewSession`. Mutating handlers run
inside :func:`~src.review.locked_session` so the load -> transition -> save
window is serialised per file (FastAPI runs these ``def`` handlers in a
threadpool), and they map review-state errors to HTTP status codes.
"""

import re
from pathlib import Path

from fastapi import APIRouter, HTTPException

from src.anki_client import AnkiConnectError
from src.review import ReviewSession, ReviewStateError, locked_session
from src.schema import Flashcard, validate_card

from ..deps import AnkiDependency
from ..models import (
    CardResponse,
    CardsFileResponse,
    CardUpdate,
    CardWithValidation,
    FileListResponse,
    FileStat,
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
    return not ("/" in filename or "\\" in filename)


def _resolve_card_file(filename: str) -> Path:
    """Validate the filename and return its path, or raise the right HTTP error."""
    if not validate_filename(filename):
        raise HTTPException(status_code=400, detail="Invalid filename")
    file_path = CARDS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")
    return file_path


def flashcard_to_response(card: Flashcard) -> CardResponse:
    """Convert Flashcard to API response model."""
    return CardResponse(
        front=card.front,
        back=card.back,
        context=card.context,
        tags=card.tags,
        images=card.images,
        source=card.source,
        deck=card.deck,
        model=card.model,
        anki_id=card.anki_id,
        status=card.status,
        added_at=card.added_at,
    )


def get_card_with_validation(
    card: Flashcard, index: int, total: int
) -> CardWithValidation:
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
def list_card_files():
    """List available JSON card files with review statistics."""
    if not CARDS_DIR.exists():
        return FileListResponse(files=[])

    files = []
    for f in CARDS_DIR.iterdir():
        if f.is_file() and f.suffix == ".json":
            try:
                counts = ReviewSession.load(str(f)).counts()
                files.append(
                    FileStat(
                        filename=f.name,
                        total_cards=counts.added + counts.skipped + counts.pending,
                        added_cards=counts.added,
                        skipped_cards=counts.skipped,
                        pending_cards=counts.pending,
                    )
                )
            except Exception:
                files.append(
                    FileStat(
                        filename=f.name,
                        total_cards=0,
                        added_cards=0,
                        skipped_cards=0,
                        pending_cards=0,
                    )
                )

    # Sort by modification time (most recent first)
    files.sort(
        key=lambda item: (CARDS_DIR / item.filename).stat().st_mtime, reverse=True
    )

    return FileListResponse(files=files)


@router.get("/{filename}", response_model=CardsFileResponse)
def get_cards(filename: str):
    """Load all cards from a JSON file with validation warnings."""
    file_path = _resolve_card_file(filename)

    try:
        session = ReviewSession.load(str(file_path))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    cards = session.cards
    cards_with_validation = [
        get_card_with_validation(card, i, len(cards)) for i, card in enumerate(cards)
    ]

    return CardsFileResponse(
        filename=filename,
        cards=cards_with_validation,
        total=len(cards),
    )


@router.put("/{filename}/{index}", response_model=CardWithValidation)
def update_card(filename: str, index: int, update: CardUpdate):
    """Update a not-yet-added card's fields and return new validation warnings."""
    file_path = _resolve_card_file(filename)

    try:
        with locked_session(str(file_path)) as session:
            card = session.edit(
                index,
                front=update.front,
                back=update.back,
                context=update.context,
                tags=update.tags,
                images=update.images,
            )
            return get_card_with_validation(card, index, len(session.cards))
    except IndexError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ReviewStateError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{filename}/{index}/approve", response_model=CardWithValidation)
def approve_card(filename: str, index: int, client: AnkiDependency):
    """Approve a card: add to Anki and persist its note id and timestamp."""
    file_path = _resolve_card_file(filename)

    try:
        with locked_session(str(file_path)) as session:
            card = session.approve(index, client)
            return get_card_with_validation(card, index, len(session.cards))
    except IndexError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ReviewStateError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except AnkiConnectError as e:
        raise HTTPException(status_code=503, detail=f"Anki Connect Error: {e}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{filename}/{index}/skip", response_model=CardWithValidation)
def skip_card(filename: str, index: int):
    """Skip a card: mark as skipped and persist."""
    file_path = _resolve_card_file(filename)

    try:
        with locked_session(str(file_path)) as session:
            card = session.skip(index)
            return get_card_with_validation(card, index, len(session.cards))
    except IndexError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
