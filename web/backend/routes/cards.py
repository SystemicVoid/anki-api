"""Card file management routes.

Thin adapters over :class:`~src.review.ReviewSession`. Mutating handlers run
inside :func:`~src.review.locked_session` so the load -> transition -> save
window is serialised per file (FastAPI runs these ``def`` handlers in a
threadpool), and they map review-state errors to HTTP status codes.
"""

import re
from datetime import UTC, datetime
from pathlib import Path
from stat import S_ISREG

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
REVIEW_ACTIVITY_DIRNAME = ".review-activity"


def _activity_path(filename: str) -> Path:
    return CARDS_DIR / REVIEW_ACTIVITY_DIRNAME / filename


def _last_activity_at(filename: str, card_mtime: float) -> datetime:
    """Return review activity without changing the Card File's mtime."""
    try:
        activity_mtime = _activity_path(filename).stat().st_mtime
    except OSError:
        activity_mtime = card_mtime
    return datetime.fromtimestamp(max(card_mtime, activity_mtime), tz=UTC)


def _record_file_activity(filename: str) -> None:
    """Record an open separately from mtimes used for generation discovery."""
    activity_path = _activity_path(filename)
    activity_path.parent.mkdir(exist_ok=True)
    activity_path.touch()


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

    files: list[FileStat] = []
    for file_path in CARDS_DIR.iterdir():
        if file_path.suffix != ".json":
            continue

        try:
            metadata = file_path.stat()
        except OSError:
            continue
        if not S_ISREG(metadata.st_mode):
            continue

        last_activity_at = _last_activity_at(file_path.name, metadata.st_mtime)
        try:
            counts = ReviewSession.load(str(file_path)).counts()
            files.append(
                FileStat(
                    filename=file_path.name,
                    total_cards=counts.added + counts.skipped + counts.pending,
                    added_cards=counts.added,
                    skipped_cards=counts.skipped,
                    pending_cards=counts.pending,
                    last_activity_at=last_activity_at,
                )
            )
        except Exception:
            files.append(
                FileStat(
                    filename=file_path.name,
                    total_cards=0,
                    added_cards=0,
                    skipped_cards=0,
                    pending_cards=0,
                    last_activity_at=last_activity_at,
                )
            )

    files.sort(key=lambda item: (item.filename.casefold(), item.filename))
    files.sort(key=lambda item: item.last_activity_at, reverse=True)

    return FileListResponse(files=files)


@router.post("/{filename}/open", response_model=CardsFileResponse)
def open_card_file(filename: str) -> CardsFileResponse:
    """Load a card file and record the successful open as activity."""
    file_path = _resolve_card_file(filename)

    try:
        with locked_session(str(file_path)) as session:
            cards = session.cards
            response = CardsFileResponse(
                filename=filename,
                cards=[
                    get_card_with_validation(card, i, len(cards))
                    for i, card in enumerate(cards)
                ],
                total=len(cards),
            )
            try:
                _record_file_activity(filename)
            except OSError as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to record file activity: {filename}",
                ) from e
            return response
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


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
        raise HTTPException(status_code=404, detail=str(e)) from e
    except ReviewStateError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/{filename}/{index}/approve", response_model=CardWithValidation)
def approve_card(filename: str, index: int, client: AnkiDependency):
    """Approve a card: add to Anki and persist its note id and timestamp."""
    file_path = _resolve_card_file(filename)

    try:
        with locked_session(str(file_path)) as session:
            card = session.approve(index, client)
            return get_card_with_validation(card, index, len(session.cards))
    except IndexError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except ReviewStateError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    except AnkiConnectError as e:
        raise HTTPException(status_code=503, detail=f"Anki Connect Error: {e}") from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/{filename}/{index}/skip", response_model=CardWithValidation)
def skip_card(filename: str, index: int):
    """Skip a card: mark as skipped and persist."""
    file_path = _resolve_card_file(filename)

    try:
        with locked_session(str(file_path)) as session:
            card = session.skip(index)
            return get_card_with_validation(card, index, len(session.cards))
    except IndexError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
