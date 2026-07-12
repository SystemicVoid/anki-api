"""Anki integration routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from src.anki_client import AnkiClient, AnkiConnectError
from src.anki_notes import add_card_to_anki
from src.schema import Flashcard

from ..deps import AnkiDependency, get_anki_client
from ..models import AddCardRequest, AddCardResponse, AnkiStatusResponse

router = APIRouter()


# These handlers do blocking (requests-based) Anki I/O, so they are plain `def`
# and run in FastAPI's threadpool rather than blocking the event loop.
@router.get("/ping", response_model=AnkiStatusResponse)
def ping_anki(client: Annotated[AnkiClient, Depends(get_anki_client)]):
    """Check if Anki is connected and responsive."""
    try:
        connected = client.ping()
        return AnkiStatusResponse(connected=connected)
    except AnkiConnectError as e:
        return AnkiStatusResponse(connected=False, error=str(e))


@router.get("/decks", response_model=list[str])
def list_decks(client: Annotated[AnkiClient, Depends(get_anki_client)]):
    """List available Anki decks."""
    try:
        return client.get_decks()
    except AnkiConnectError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/models", response_model=list[str])
def list_models(client: Annotated[AnkiClient, Depends(get_anki_client)]):
    """List available Anki note models."""
    try:
        return client.get_models()
    except AnkiConnectError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/add", response_model=AddCardResponse)
def add_card(request: AddCardRequest, client: AnkiDependency):
    """Add a card to Anki through the shared submission primitive."""
    card = Flashcard(
        front=request.front,
        back=request.back,
        context=request.context,
        tags=request.tags,
        images=request.images,
        source=request.source,
        deck=request.deck,
        model=request.model,
    )

    try:
        note_id = add_card_to_anki(client, card)
        return AddCardResponse(success=True, note_id=note_id)
    except (AnkiConnectError, ValueError) as e:
        return AddCardResponse(success=False, error=str(e))
