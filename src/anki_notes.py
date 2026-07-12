"""Turn Flashcards into Anki notes and submit them.

This module is the single home for the "a Flashcard becomes a persisted Anki
note" transaction: rendering the card into AnkiConnect's note shape, uploading
its media, and adding it. Callers pass a :class:`~src.schema.Flashcard` and an
injected client; they never build note dicts, unpack them by hand, or construct
an :class:`~src.anki_client.AnkiClient` themselves.

The ``NoteClient`` Protocol is the seam: production passes a real ``AnkiClient``,
tests pass an in-memory fake. Because it extends ``MediaStore``, one fake
satisfies both the media-upload seam and the note-submission seam.

Content-trust note: Front/Back/Context are rendered *unescaped* (only newlines
become ``<br>``); only image filenames are HTML-escaped. Card content is trusted
local input and may carry intentional HTML/MathJax. See
``docs/adr/0001-card-content-trust-and-escaping.md``.
"""

from __future__ import annotations

import html
from typing import TYPE_CHECKING, Any, Protocol, TypedDict, cast

from src.anki_client import AnkiConnectError
from src.media import MediaStore, upload_media_files, validate_media_filename

if TYPE_CHECKING:
    from collections.abc import Sequence

    from src.schema import Flashcard


class AnkiNote(TypedDict):
    """The AnkiConnect note shape. Its keys live only in this module."""

    deckName: str
    modelName: str
    fields: dict[str, str]
    tags: list[str]


def convert_newlines_to_html(text: str) -> str:
    """Convert plain newlines to HTML ``<br>`` tags for Anki display.

    Anki renders card content as HTML, so plain newlines collapse. This turns
    ``\\n`` (and ``\\r\\n``/``\\r``) into ``<br>`` so authored line breaks survive.
    """
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return normalized.replace("\n", "<br>")


class NoteClient(MediaStore, Protocol):
    """The behaviour single-note submission needs from an Anki client.

    Any object with these methods (the real ``AnkiClient`` or a test fake) can
    be injected wherever a ``NoteClient`` is expected.
    """

    def add_note(
        self,
        deck_name: str,
        model_name: str,
        fields: dict[str, str],
        tags: list[str] | None = None,
    ) -> int: ...


class BatchNoteClient(NoteClient, Protocol):
    """A ``NoteClient`` that can also add many notes in one request.

    The parameter is typed ``list[dict[str, Any]]`` (not ``list[AnkiNote]``) to
    match the concrete ``AnkiClient`` and stay assignable under list invariance;
    ``render_anki_note`` still produces the precise ``AnkiNote`` shape.
    """

    def add_notes_batch(self, notes: list[dict[str, Any]]) -> list[int | None]: ...


def render_anki_note(card: Flashcard) -> AnkiNote:
    """Render a card into an AnkiConnect note dict.

    The note dict's shape (``deckName``/``modelName``/``fields``/``tags``) lives
    only here. Output is byte-for-byte identical to the historical
    ``Flashcard.to_anki_note``: newlines become ``<br>``, images render before
    the ``---`` context separator, and only image filenames are HTML-escaped
    (front/back/context are passed through unescaped — see the module ADR).
    """
    back_html = convert_newlines_to_html(card.back)

    if card.images:
        image_html = "".join(
            f'<img src="{html.escape(validate_media_filename(filename))}">'
            for filename in card.images
        )
        back_html += f"<br><br>{image_html}"

    if card.context:
        back_html += "<br><br>---<br><br>" + convert_newlines_to_html(card.context)

    front_html = convert_newlines_to_html(card.front)

    return {
        "deckName": card.deck,
        "modelName": card.model,
        "fields": {"Front": front_html, "Back": back_html},
        "tags": card.tags,
    }


def add_card_to_anki(
    client: NoteClient,
    card: Flashcard,
    *,
    deck_override: str | None = None,
) -> int:
    """Upload the card's media and add it to Anki as a single note.

    ``deck_override`` sends the note to a different deck than the card records,
    without mutating the card. Returns the new note id. Raises
    ``AnkiConnectError`` or ``ValueError`` on failure so callers decide how to
    surface it — this function never swallows errors or mutates card state.

    A null AnkiConnect result (no note id) is raised as ``AnkiConnectError``
    rather than returned, so the single-note contract truly yields an ``int``
    and callers never persist an "added" card with ``anki_id=None``. The batch
    path keeps ``None`` per note, because there it is Anki's expected
    rejection signal (e.g. a duplicate), not a contract violation.
    """
    upload_media_files(client, card.images)
    note = render_anki_note(card)
    note_id = client.add_note(
        deck_name=deck_override or note["deckName"],
        model_name=note["modelName"],
        fields=note["fields"],
        tags=note["tags"],
    )
    if note_id is None:
        raise AnkiConnectError(
            "AnkiConnect returned no note id for the add (the note may be a "
            "duplicate or otherwise rejected); not recording it as added"
        )
    return note_id


def add_cards_to_anki(
    client: BatchNoteClient,
    cards: Sequence[Flashcard],
    *,
    deck_override: str | None = None,
) -> list[int | None]:
    """Upload media for many cards and add them in one batch request.

    ``deck_override`` retargets every note's deck without mutating the cards.
    Returns the resulting note ids in order (``None`` for any note Anki
    rejected, e.g. a duplicate).
    """
    upload_media_files(
        client,
        (filename for card in cards for filename in card.images),
    )
    notes = [render_anki_note(card) for card in cards]
    if deck_override:
        for note in notes:
            note["deckName"] = deck_override
    return client.add_notes_batch(cast("list[dict[str, Any]]", notes))
