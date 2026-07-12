"""Shared pytest fixtures.

``FakeAnkiClient`` is the in-memory adapter that satisfies the ``NoteClient``
seam. It records what would have been sent to Anki so tests can assert on the
submission without a running Anki Desktop — the same interface the CLI and web
adapters cross in production.
"""

from collections.abc import Iterable
from typing import Any, cast

import pytest

from src.anki_client import AnkiConnectError
from src.schema import Flashcard


class FakeAnkiClient:
    """Records note/media submissions and hands back synthetic note ids.

    Failure switches let tests exercise the submission error paths without a
    running Anki:

    - ``fail_on_add`` — ``add_note`` raises ``AnkiConnectError``.
    - ``null_add`` — ``add_note`` returns ``None`` (as AnkiConnect can, e.g. a
      ``{"result": null, "error": null}`` reply) without raising.
    - ``fail_media`` — ``store_media_file`` raises ``AnkiConnectError``.
    - ``batch_reject_indices`` — positions in an ``add_notes_batch`` call that
      come back as ``None`` (as Anki does for a duplicate).
    """

    def __init__(
        self,
        *,
        fail_on_add: bool = False,
        null_add: bool = False,
        fail_media: bool = False,
        batch_reject_indices: Iterable[int] = (),
    ) -> None:
        self.notes: list[dict[str, Any]] = []
        self.batched: list[dict[str, Any]] = []
        self.media: list[tuple[str, bytes]] = []
        self.fail_on_add = fail_on_add
        self.null_add = null_add
        self.fail_media = fail_media
        self.batch_reject_indices = set(batch_reject_indices)
        self._next_id = 1000

    def store_media_file(self, filename: str, data: bytes) -> str:
        if self.fail_media:
            raise AnkiConnectError("simulated media failure")
        self.media.append((filename, data))
        return filename

    def add_note(
        self,
        deck_name: str,
        model_name: str,
        fields: dict[str, str],
        tags: list[str] | None = None,
    ) -> int:
        if self.fail_on_add:
            raise AnkiConnectError("simulated add failure")
        if self.null_add:
            # Mirror AnkiConnect handing back a null result with no error; the
            # real add_note is typed -> int, so cast keeps the fake conformant.
            return cast("int", None)
        self._next_id += 1
        self.notes.append(
            {
                "deckName": deck_name,
                "modelName": model_name,
                "fields": fields,
                "tags": tags or [],
            }
        )
        return self._next_id

    def add_notes_batch(self, notes: list[dict[str, Any]]) -> list[int | None]:
        ids: list[int | None] = []
        for index, note in enumerate(notes):
            if index in self.batch_reject_indices:
                ids.append(None)
                continue
            self._next_id += 1
            self.batched.append(note)
            ids.append(self._next_id)
        return ids


@pytest.fixture
def fake_client() -> FakeAnkiClient:
    return FakeAnkiClient()


@pytest.fixture
def sample_cards() -> list[Flashcard]:
    return [
        Flashcard(front="Q1?", back="A1", tags=["topic::a"]),
        Flashcard(front="Q2?", back="A2", context="why it matters"),
    ]
