"""Pydantic models for API requests and responses."""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class CardResponse(BaseModel):
    """Card data returned from API."""
    front: str
    back: str
    context: str
    tags: List[str]
    source: str
    deck: str
    model: str
    anki_id: Optional[int] = None
    status: str = "pending"
    added_at: Optional[datetime] = None


class CardUpdate(BaseModel):
    """Partial card update request."""
    front: Optional[str] = None
    back: Optional[str] = None
    context: Optional[str] = None
    tags: Optional[List[str]] = None


class ValidationWarningResponse(BaseModel):
    """Validation warning with severity."""
    message: str
    severity: str  # "error", "warning", "info"


class CardWithValidation(BaseModel):
    """Card with its validation warnings."""
    card: CardResponse
    warnings: List[ValidationWarningResponse]
    index: int
    total: int


class CardsFileResponse(BaseModel):
    """Response for loading a cards file."""
    filename: str
    cards: List[CardWithValidation]
    total: int


class AddCardRequest(BaseModel):
    """Request to add a card to Anki."""
    front: str
    back: str
    context: str
    tags: List[str]
    source: str
    deck: str
    model: str


class AddCardResponse(BaseModel):
    """Response from adding a card to Anki."""
    success: bool
    note_id: Optional[int] = None
    error: Optional[str] = None


class AnkiStatusResponse(BaseModel):
    """Anki connection status."""
    connected: bool
    error: Optional[str] = None


class FileStat(BaseModel):
    """Statistics for a card file."""
    filename: str
    total_cards: int
    added_cards: int
    skipped_cards: int
    pending_cards: int


class FileListResponse(BaseModel):
    """List of available card files with stats."""
    files: List[FileStat]
