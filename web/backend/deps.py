"""Shared FastAPI dependencies.

``get_anki_client`` is the web seam for talking to Anki: routes declare it with
``Depends`` so tests can substitute a fake via ``app.dependency_overrides``
instead of the routes constructing an ``AnkiClient`` inline.
"""

from typing import Annotated

from fastapi import Depends

from src.anki_client import AnkiClient
from src.anki_notes import NoteClient


def get_anki_client() -> AnkiClient:
    """Provide an AnkiConnect client to a request handler."""
    return AnkiClient()


# Routes that only submit notes annotate with the seam, not the concrete client,
# so the dependency reads as "something that can add a note" and tests can pass a
# fake. ``Depends`` marks it as an injected dependency (not a request body).
AnkiDependency = Annotated[NoteClient, Depends(get_anki_client)]
