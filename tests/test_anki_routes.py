"""Tests for Anki API route error handling.

The route is a plain ``def`` taking an injected ``NoteClient``, so these call it
directly with a ``FakeAnkiClient`` — no event loop, no dependency-override
plumbing, no running Anki.
"""

from conftest import FakeAnkiClient

from web.backend.models import AddCardRequest
from web.backend.routes.anki import add_card


def _request(**overrides) -> AddCardRequest:
    base = {
        "front": "Q?",
        "back": "A",
        "context": "",
        "tags": [],
        "images": [],
        "source": "",
        "deck": "Default",
        "model": "Basic",
    }
    base.update(overrides)
    return AddCardRequest(**base)


def test_add_card_returns_structured_error_for_invalid_image_filename():
    request = _request(
        front="What does the diagram show?",
        back="A matrix operation.",
        images=["../diagram.png"],
    )

    response = add_card(request, FakeAnkiClient())

    assert response.success is False
    assert response.note_id is None
    assert response.error == "Invalid media filename: ../diagram.png"


def test_add_card_submits_through_primitive_and_returns_id():
    client = FakeAnkiClient()
    request = _request(front="What is broadcasting?", back="Reusing a vector.")

    response = add_card(request, client)

    assert response.success is True
    assert response.note_id == 1001
    assert len(client.notes) == 1
    assert client.notes[0]["deckName"] == "Default"
