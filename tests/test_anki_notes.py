"""Tests for the Anki submission primitive (src/anki_notes.py).

Rendering goldens pin ``render_anki_note``'s output byte-for-byte to the
historical ``Flashcard.to_anki_note`` so the extraction cannot silently change
what reaches Anki. Submission tests drive ``add_card_to_anki`` /
``add_cards_to_anki`` against the in-memory ``FakeAnkiClient`` seam.
"""

import pytest
from conftest import FakeAnkiClient

from src import media
from src.anki_client import AnkiConnectError
from src.anki_notes import (
    add_card_to_anki,
    add_cards_to_anki,
    convert_newlines_to_html,
    render_anki_note,
)
from src.schema import Flashcard

# --- convert_newlines_to_html (moved here from schema) ---


def test_convert_newlines_handles_mixed_endings():
    text = "Line one\r\nLine two\rLine three\nLine four"
    assert (
        convert_newlines_to_html(text)
        == "Line one<br>Line two<br>Line three<br>Line four"
    )


# --- render_anki_note goldens (byte-identical to old to_anki_note) ---


def test_render_converts_front_back_and_context_to_html():
    card = Flashcard(
        front="What is foo?\nProvide two points?",
        back="First line\nSecond line",
        context="Extra context line 1\nExtra context line 2",
        tags=["test"],
        deck="Learning",
        model="Basic",
    )

    note = render_anki_note(card)

    assert note["fields"]["Front"] == "What is foo?<br>Provide two points?"
    assert note["fields"]["Back"] == (
        "First line<br>Second line<br><br>---<br><br>"
        "Extra context line 1<br>Extra context line 2"
    )
    assert note["deckName"] == "Learning"
    assert note["modelName"] == "Basic"
    assert note["tags"] == ["test"]


def test_render_includes_attached_images_before_context():
    card = Flashcard(
        front="What does the diagram show?",
        back="Broadcasting a vector across matrix rows.",
        context="The vector is reused without changing its stored values.",
        images=["broadcasting.png"],
    )

    note = render_anki_note(card)

    assert note["fields"]["Back"] == (
        "Broadcasting a vector across matrix rows.<br><br>"
        '<img src="broadcasting.png"><br><br>---<br><br>'
        "The vector is reused without changing its stored values."
    )


# --- add_card_to_anki ---


def test_add_card_submits_and_returns_id(fake_client):
    card = Flashcard(front="Q?", back="A", tags=["topic::x"], deck="Learning")

    note_id = add_card_to_anki(fake_client, card)

    assert note_id == 1001
    assert len(fake_client.notes) == 1
    submitted = fake_client.notes[0]
    assert submitted["deckName"] == "Learning"
    assert submitted["tags"] == ["topic::x"]
    assert submitted["fields"] == render_anki_note(card)["fields"]


def test_add_card_deck_override_does_not_mutate_card(fake_client):
    card = Flashcard(front="Q?", back="A", deck="Original")

    add_card_to_anki(fake_client, card, deck_override="Elsewhere")

    assert fake_client.notes[0]["deckName"] == "Elsewhere"
    assert card.deck == "Original"


def test_add_card_uploads_media_before_submitting(tmp_path, monkeypatch, fake_client):
    monkeypatch.setattr(media, "MEDIA_DIR", tmp_path)
    (tmp_path / "diagram.png").write_bytes(b"png-bytes")
    card = Flashcard(front="Q?", back="A", images=["diagram.png"])

    add_card_to_anki(fake_client, card)

    assert fake_client.media == [("diagram.png", b"png-bytes")]
    assert '<img src="diagram.png">' in fake_client.notes[0]["fields"]["Back"]


def test_add_card_rejects_invalid_image_before_submitting(fake_client):
    card = Flashcard(front="Q?", back="A", images=["../evil.png"])

    with pytest.raises(ValueError, match="Invalid media filename"):
        add_card_to_anki(fake_client, card)

    assert fake_client.notes == []


def test_add_card_propagates_media_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(media, "MEDIA_DIR", tmp_path)
    (tmp_path / "diagram.png").write_bytes(b"png-bytes")
    client = FakeAnkiClient(fail_media=True)
    card = Flashcard(front="Q?", back="A", images=["diagram.png"])

    with pytest.raises(AnkiConnectError):
        add_card_to_anki(client, card)

    assert client.notes == []


# --- add_cards_to_anki ---


def test_add_cards_batches_and_returns_ids(fake_client, sample_cards):
    ids = add_cards_to_anki(fake_client, sample_cards)

    assert ids == [1001, 1002]
    assert len(fake_client.batched) == 2


def test_add_cards_returns_none_for_rejected_notes(sample_cards):
    client = FakeAnkiClient(batch_reject_indices=[0])

    ids = add_cards_to_anki(client, sample_cards)

    assert ids[0] is None
    assert ids[1] == 1001
    assert len(client.batched) == 1


def test_add_cards_uploads_each_image_once(tmp_path, monkeypatch, fake_client):
    monkeypatch.setattr(media, "MEDIA_DIR", tmp_path)
    (tmp_path / "shared.png").write_bytes(b"x")
    cards = [
        Flashcard(front="Q1?", back="A", images=["shared.png"]),
        Flashcard(front="Q2?", back="B", images=["shared.png"]),
    ]

    add_cards_to_anki(fake_client, cards)

    assert fake_client.media == [("shared.png", b"x")]


def test_add_cards_deck_override_retargets_every_note(fake_client, sample_cards):
    add_cards_to_anki(fake_client, sample_cards, deck_override="Elsewhere")

    assert all(note["deckName"] == "Elsewhere" for note in fake_client.batched)
    assert all(card.deck == "Default" for card in sample_cards)


def test_add_card_raises_when_anki_returns_no_id():
    """A null AnkiConnect result is an error, not a success with no note id.

    The single-note contract is ``-> int``; a null add (e.g. a duplicate, or a
    bare ``result: null`` reply) must raise so callers never persist or report
    an added card with no id. Contrast the batch path, which keeps ``None``.
    """
    client = FakeAnkiClient(null_add=True)

    with pytest.raises(AnkiConnectError):
        add_card_to_anki(client, Flashcard(front="Q?", back="A"))
