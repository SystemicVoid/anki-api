"""The review lifecycle for a card file.

A :class:`ReviewSession` owns one ``cards/*.json`` file: it loads the cards,
exposes the ``pending -> added/skipped`` state machine, persists after every
transition, and submits approved cards to Anki through the injected client. The
CLI review loop and the web review routes are thin adapters over this one
interface — the single home for review state, so a change to "what it means to
add, skip, edit, or reset a card" is made in exactly one place.

Concurrency: :func:`locked_session` serialises the load -> transition -> save
window per file within a process (the web adapter runs route handlers in a
threadpool). Cross-process coordination is out of scope — see
``docs/specs/review-session-arc.md``.
"""

from __future__ import annotations

import threading
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

from src.anki_notes import add_card_to_anki, add_cards_to_anki
from src.schema import load_cards_from_json, save_cards_to_json

if TYPE_CHECKING:
    from collections.abc import Iterator

    from src.anki_notes import BatchNoteClient, NoteClient
    from src.schema import Flashcard


class ReviewStateError(ValueError):
    """Raised when a review action is illegal for a card's current status.

    Subclasses ``ValueError`` so existing ``except ValueError`` handlers keep
    working, while adapters that care can map it to a distinct response (the web
    layer returns 409 Conflict).
    """


class ReviewCounts(NamedTuple):
    """Tally of a card file's review statuses."""

    added: int
    skipped: int
    pending: int


class ReviewSession:
    """A card file plus the transitions allowed over its cards."""

    def __init__(self, path: str | Path, cards: list[Flashcard]) -> None:
        self.path = str(path)
        self.cards = cards

    @classmethod
    def load(cls, path: str | Path) -> ReviewSession:
        """Load a session from a JSON card file.

        Raises ``ValueError`` if the file is missing or malformed (propagated
        from :func:`~src.schema.load_cards_from_json`).
        """
        cards = load_cards_from_json(str(path))
        return cls(path, cards)

    def save(self) -> None:
        """Persist the current cards back to the file (atomic write)."""
        save_cards_to_json(self.cards, self.path)

    def card(self, index: int) -> Flashcard:
        """Return the card at ``index`` or raise ``IndexError``."""
        if index < 0 or index >= len(self.cards):
            raise IndexError(f"Card index {index} out of range")
        return self.cards[index]

    def counts(self) -> ReviewCounts:
        """Tally cards by review status."""
        return ReviewCounts(
            added=sum(1 for c in self.cards if c.status == "added"),
            skipped=sum(1 for c in self.cards if c.status == "skipped"),
            pending=sum(1 for c in self.cards if c.status == "pending"),
        )

    def pending_indices(self) -> tuple[int, ...]:
        """Indices of cards not yet reviewed, in file order."""
        return tuple(i for i, c in enumerate(self.cards) if c.status == "pending")

    def reset(self) -> None:
        """Re-open skipped cards for another pass; leave added cards linked.

        Only ``skipped`` cards return to ``pending``. Cards already ``added``
        keep their ``anki_id``/``added_at`` so a reset never orphans an existing
        Anki note or invites a duplicate resubmission.
        """
        changed = False
        for card in self.cards:
            if card.status == "skipped":
                card.status = "pending"
                changed = True
        if changed:
            self.save()

    def edit(
        self,
        index: int,
        *,
        front: str | None = None,
        back: str | None = None,
        context: str | None = None,
        tags: list[str] | None = None,
        images: list[str] | None = None,
    ) -> Flashcard:
        """Apply field changes to a not-yet-added card and persist.

        Only non-``None`` fields are changed. Raises ``ReviewStateError`` if the
        card is already ``added`` — its text is committed to an Anki note, and
        editing the JSON would silently diverge the file from Anki.
        """
        card = self.card(index)
        if card.status == "added":
            raise ReviewStateError(
                f"Card {index} is already added to Anki and cannot be edited"
            )
        if front is not None:
            card.front = front
        if back is not None:
            card.back = back
        if context is not None:
            card.context = context
        if tags is not None:
            card.tags = tags
        if images is not None:
            card.images = images
        self.save()
        return card

    def skip(self, index: int) -> Flashcard:
        """Mark a pending card as ``skipped`` and persist.

        Idempotent: a card that is not ``pending`` is returned unchanged.
        """
        card = self.card(index)
        if card.status == "pending":
            card.status = "skipped"
            self.save()
        return card

    def approve(
        self,
        index: int,
        client: NoteClient,
        *,
        deck_override: str | None = None,
    ) -> Flashcard:
        """Add a card to Anki, mark it ``added``, and persist.

        Idempotent: a card already ``added`` with an ``anki_id`` is returned
        unchanged (Anki is not called again). A card marked ``added`` *without*
        an ``anki_id`` is an invalid persisted state and raises
        ``ReviewStateError`` rather than blindly resubmitting. On an
        ``AnkiConnectError`` or ``ValueError`` the exception propagates and the
        card's status is left untouched, so it can be retried.
        """
        card = self.card(index)
        if card.status == "added":
            if card.anki_id is not None:
                return card
            raise ReviewStateError(
                f"Card {index} is marked added but has no Anki id; refusing to resubmit"
            )
        note_id = add_card_to_anki(client, card, deck_override=deck_override)
        if deck_override is not None:
            card.deck = deck_override
        card.anki_id = note_id
        card.status = "added"
        card.added_at = datetime.now(UTC)
        self.save()
        return card

    def submit_all(
        self,
        client: BatchNoteClient,
        *,
        deck_override: str | None = None,
    ) -> list[int | None]:
        """Batch-submit every not-yet-added card, mark accepted ones, persist.

        Cards already ``added`` are skipped (idempotent — never resubmitted).
        Returns the note ids for the submitted cards in order (``None`` for any
        Anki rejected, e.g. a duplicate); rejected cards keep their prior status
        so they remain reviewable. Persists once if anything changed.
        """
        targets = [(i, c) for i, c in enumerate(self.cards) if c.status != "added"]
        note_ids = add_cards_to_anki(
            client, [card for _, card in targets], deck_override=deck_override
        )
        changed = False
        for (_, card), note_id in zip(targets, note_ids, strict=True):
            if note_id is not None:
                if deck_override is not None:
                    card.deck = deck_override
                card.anki_id = note_id
                card.status = "added"
                card.added_at = datetime.now(UTC)
                changed = True
        if changed:
            self.save()
        return note_ids


_locks: dict[str, threading.Lock] = {}
_locks_guard = threading.Lock()


def _lock_for(path: str | Path) -> threading.Lock:
    key = str(Path(path).resolve())
    with _locks_guard:
        lock = _locks.get(key)
        if lock is None:
            lock = threading.Lock()
            _locks[key] = lock
        return lock


@contextmanager
def locked_session(path: str | Path) -> Iterator[ReviewSession]:
    """Load a session under a per-file lock, held across the whole block.

    Serialises the read -> transition -> write window so two concurrent handlers
    for the same file can't both load a ``pending`` card and both submit it. The
    lock is process-local; the web adapter runs route handlers in a threadpool,
    so this covers the concurrency it actually creates.
    """
    lock = _lock_for(path)
    with lock:
        yield ReviewSession.load(path)
