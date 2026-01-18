"""Pydantic models for API requests and responses."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class CardResponse(BaseModel):
    """Card data returned from API."""

    front: str
    back: str
    context: str
    tags: list[str]
    source: str
    deck: str
    model: str
    anki_id: int | None = None
    status: str = "pending"
    added_at: datetime | None = None


class CardUpdate(BaseModel):
    """Partial card update request."""

    front: str | None = None
    back: str | None = None
    context: str | None = None
    tags: list[str] | None = None


class ValidationWarningResponse(BaseModel):
    """Validation warning with severity."""

    message: str
    severity: str  # "error", "warning", "info"


class CardWithValidation(BaseModel):
    """Card with its validation warnings."""

    card: CardResponse
    warnings: list[ValidationWarningResponse]
    index: int
    total: int


class CardsFileResponse(BaseModel):
    """Response for loading a cards file."""

    filename: str
    cards: list[CardWithValidation]
    total: int


class AddCardRequest(BaseModel):
    """Request to add a card to Anki."""

    front: str
    back: str
    context: str
    tags: list[str]
    source: str
    deck: str
    model: str


class AddCardResponse(BaseModel):
    """Response from adding a card to Anki."""

    success: bool
    note_id: int | None = None
    error: str | None = None


class AnkiStatusResponse(BaseModel):
    """Anki connection status."""

    connected: bool
    error: str | None = None


class FileStat(BaseModel):
    """Statistics for a card file."""

    filename: str
    total_cards: int
    added_cards: int
    skipped_cards: int
    pending_cards: int


class FileListResponse(BaseModel):
    """List of available card files with stats."""

    files: list[FileStat]


class FileNode(BaseModel):
    """File or directory node for file browser."""

    name: str
    path: str  # Relative for project mode, absolute for system mode
    type: Literal["file", "directory"]
    extension: str | None = None
    size: int
    modified: datetime
    readable: bool  # False if permission error


class FileBrowserResponse(BaseModel):
    """Response for file browser endpoint."""

    current_path: str
    parent_path: str | None = None
    nodes: list[FileNode]
    mode: Literal["project", "system"]
