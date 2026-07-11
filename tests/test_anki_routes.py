"""Tests for Anki API route error handling."""

import asyncio

from web.backend.models import AddCardRequest
from web.backend.routes.anki import add_card


def test_add_card_returns_structured_error_for_invalid_image_filename():
    request = AddCardRequest(
        front="What does the diagram show?",
        back="A matrix operation.",
        context="",
        tags=[],
        images=["../diagram.png"],
        source="",
        deck="Default",
        model="Basic",
    )

    response = asyncio.run(add_card(request))

    assert response.success is False
    assert response.note_id is None
    assert response.error == "Invalid media filename: ../diagram.png"
