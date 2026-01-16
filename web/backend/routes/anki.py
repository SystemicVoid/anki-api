"""Anki integration routes."""

from typing import List

from fastapi import APIRouter, HTTPException

from src.anki_client import AnkiClient, AnkiConnectError
from src.schema import Flashcard

from ..models import AddCardRequest, AddCardResponse, AnkiStatusResponse

router = APIRouter()


def get_anki_client() -> AnkiClient:
    """Get AnkiConnect client instance."""
    return AnkiClient()


@router.get("/ping", response_model=AnkiStatusResponse)
async def ping_anki():
    """Check if Anki is connected and responsive."""
    client = get_anki_client()
    try:
        connected = client.ping()
        return AnkiStatusResponse(connected=connected)
    except AnkiConnectError as e:
        return AnkiStatusResponse(connected=False, error=str(e))


@router.get("/decks", response_model=List[str])
async def list_decks():
    """List available Anki decks."""
    client = get_anki_client()
    try:
        return client.get_decks()
    except AnkiConnectError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/models", response_model=List[str])
async def list_models():
    """List available Anki note models."""
    client = get_anki_client()
    try:
        return client.get_models()
    except AnkiConnectError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/add", response_model=AddCardResponse)
async def add_card(request: AddCardRequest):
    """Add a card to Anki."""
    client = get_anki_client()

    # Create Flashcard object to use its to_anki_note conversion
    card = Flashcard(
        front=request.front,
        back=request.back,
        context=request.context,
        tags=request.tags,
        source=request.source,
        deck=request.deck,
        model=request.model,
    )

    anki_note = card.to_anki_note()

    try:
        note_id = client.add_note(
            deck_name=anki_note["deckName"],
            model_name=anki_note["modelName"],
            fields=anki_note["fields"],
            tags=anki_note["tags"],
        )
        return AddCardResponse(success=True, note_id=note_id)
    except AnkiConnectError as e:
        return AddCardResponse(success=False, error=str(e))
