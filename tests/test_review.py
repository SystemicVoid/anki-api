"""Tests for the ReviewSession state machine (src/review.py).

ReviewSession is the single home for review state, so these tests are the
behaviour contract for approve/skip/edit/reset/submit_all — including the three
confirmed behaviour changes: reset re-queues skipped only, editing an added card
is refused, and batch submit persists per-card outcomes.
"""

import pytest
from conftest import FakeAnkiClient

from src.anki_client import AnkiConnectError
from src.review import ReviewCounts, ReviewSession, ReviewStateError, locked_session
from src.schema import Flashcard, load_cards_from_json, save_cards_to_json


def _make_file(tmp_path, cards) -> str:
    path = tmp_path / "cards.json"
    save_cards_to_json(cards, str(path))
    return str(path)


def _session(tmp_path, cards=None) -> ReviewSession:
    if cards is None:
        cards = [
            Flashcard(front="Q1?", back="A1"),
            Flashcard(front="Q2?", back="A2"),
            Flashcard(front="Q3?", back="A3"),
        ]
    return ReviewSession.load(_make_file(tmp_path, cards))


# --- approve ---


def test_approve_adds_marks_added_and_persists(tmp_path, fake_client):
    session = _session(tmp_path)

    card = session.approve(0, fake_client)

    assert card.status == "added"
    assert card.anki_id == 1001
    assert len(fake_client.notes) == 1
    reloaded = load_cards_from_json(session.path)
    assert reloaded[0].status == "added"
    assert reloaded[0].anki_id == 1001


def test_approve_is_idempotent(tmp_path, fake_client):
    session = _session(tmp_path)

    session.approve(0, fake_client)
    again = session.approve(0, fake_client)

    assert again.anki_id == 1001
    assert len(fake_client.notes) == 1  # not re-added


def test_approve_added_without_anki_id_raises(tmp_path, fake_client):
    session = _session(tmp_path, [Flashcard(front="Q?", back="A", status="added")])

    with pytest.raises(ReviewStateError):
        session.approve(0, fake_client)

    assert fake_client.notes == []


def test_approve_failure_leaves_card_pending(tmp_path):
    client = FakeAnkiClient(fail_on_add=True)
    session = _session(tmp_path)

    with pytest.raises(AnkiConnectError):
        session.approve(0, client)

    assert session.card(0).status == "pending"
    reloaded = load_cards_from_json(session.path)
    assert reloaded[0].status == "pending"


def test_approve_deck_override_sets_deck(tmp_path, fake_client):
    session = _session(tmp_path)

    card = session.approve(0, fake_client, deck_override="Elsewhere")

    assert card.deck == "Elsewhere"
    assert fake_client.notes[0]["deckName"] == "Elsewhere"


# --- skip ---


def test_skip_marks_skipped_and_leaves_added_untouched(tmp_path, fake_client):
    session = _session(tmp_path)

    session.skip(1)
    assert session.card(1).status == "skipped"

    session.approve(0, fake_client)
    session.skip(0)  # skip is a no-op on an added card
    assert session.card(0).status == "added"


# --- edit (F3: refuse edits of added cards) ---


def test_edit_applies_changes_and_persists(tmp_path):
    session = _session(tmp_path)

    session.edit(0, front="new front?", tags=["t::x"])

    assert session.card(0).front == "new front?"
    assert session.card(0).tags == ["t::x"]
    reloaded = load_cards_from_json(session.path)
    assert reloaded[0].front == "new front?"


def test_edit_of_added_card_raises(tmp_path, fake_client):
    session = _session(tmp_path)
    session.approve(0, fake_client)

    with pytest.raises(ReviewStateError):
        session.edit(0, front="changed?")

    assert session.card(0).front == "Q1?"


# --- reset (F2: re-queue skipped only) ---


def test_reset_requeues_skipped_only(tmp_path, fake_client):
    session = _session(tmp_path)
    session.approve(0, fake_client)  # card 0 -> added
    session.skip(1)  # card 1 -> skipped
    # card 2 stays pending

    session.reset()

    assert session.card(0).status == "added"
    assert session.card(0).anki_id == 1001  # still linked to its Anki note
    assert session.card(1).status == "pending"
    assert session.card(2).status == "pending"


# --- counts / pending_indices / bounds ---


def test_counts_and_pending_indices(tmp_path, fake_client):
    session = _session(tmp_path)
    session.approve(0, fake_client)
    session.skip(1)

    assert session.counts() == ReviewCounts(added=1, skipped=1, pending=1)
    assert session.pending_indices() == (2,)


def test_card_index_out_of_range_raises(tmp_path):
    session = _session(tmp_path)

    with pytest.raises(IndexError):
        session.card(99)


# --- submit_all (F1: batch persists per-card outcomes) ---


def test_submit_all_marks_accepted_and_skips_already_added(tmp_path, fake_client):
    cards = [
        Flashcard(front="Q1?", back="A1"),
        Flashcard(front="Q2?", back="A2", status="added", anki_id=555),
        Flashcard(front="Q3?", back="A3"),
    ]
    session = _session(tmp_path, cards)

    ids = session.submit_all(fake_client)

    assert len(ids) == 2  # card 1 (already added) is not resubmitted
    assert session.card(0).status == "added"
    assert session.card(1).anki_id == 555  # untouched
    assert session.card(2).status == "added"
    reloaded = load_cards_from_json(session.path)
    assert [c.status for c in reloaded] == ["added", "added", "added"]


def test_submit_all_leaves_rejected_cards_pending(tmp_path):
    client = FakeAnkiClient(batch_reject_indices=[0])
    cards = [Flashcard(front="Q1?", back="A1"), Flashcard(front="Q2?", back="A2")]
    session = _session(tmp_path, cards)

    ids = session.submit_all(client)

    assert ids[0] is None
    assert session.card(0).status == "pending"
    assert session.card(1).status == "added"


# --- locked_session ---


def test_locked_session_loads_and_persists(tmp_path, fake_client):
    path = _make_file(tmp_path, [Flashcard(front="Q?", back="A")])

    with locked_session(path) as session:
        session.approve(0, fake_client)

    reloaded = load_cards_from_json(path)
    assert reloaded[0].status == "added"
