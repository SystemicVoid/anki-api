"""Tests for card file routes (web/backend/routes/cards.py).

The routes are plain ``def`` handlers, so these call them directly with a
monkeypatched CARDS_DIR and a FakeAnkiClient — no TestClient, no running Anki.
They verify the adapter maps ReviewSession outcomes to the right HTTP codes.
"""

import pytest
from fastapi import HTTPException

from src.schema import Flashcard, load_cards_from_json, save_cards_to_json
from web.backend.models import CardUpdate
from web.backend.routes import cards as cards_route


def _seed(tmp_path, monkeypatch, cards, name="deck.json") -> str:
    monkeypatch.setattr(cards_route, "CARDS_DIR", tmp_path)
    save_cards_to_json(cards, str(tmp_path / name))
    return name


def test_approve_route_adds_and_persists(tmp_path, monkeypatch, fake_client):
    name = _seed(tmp_path, monkeypatch, [Flashcard(front="Q?", back="A")])

    result = cards_route.approve_card(name, 0, fake_client)

    assert result.card.status == "added"
    assert result.card.anki_id == 1001
    assert len(fake_client.notes) == 1
    reloaded = load_cards_from_json(str(tmp_path / name))
    assert reloaded[0].status == "added"


def test_approve_route_conflicts_when_added_without_id(
    tmp_path, monkeypatch, fake_client
):
    name = _seed(
        tmp_path,
        monkeypatch,
        [Flashcard(front="Q?", back="A", status="added")],
    )

    with pytest.raises(HTTPException) as exc:
        cards_route.approve_card(name, 0, fake_client)

    assert exc.value.status_code == 409
    assert fake_client.notes == []


def test_approve_route_out_of_range_is_404(tmp_path, monkeypatch, fake_client):
    name = _seed(tmp_path, monkeypatch, [Flashcard(front="Q?", back="A")])

    with pytest.raises(HTTPException) as exc:
        cards_route.approve_card(name, 9, fake_client)

    assert exc.value.status_code == 404


def test_update_route_rejects_edit_of_added_card(tmp_path, monkeypatch):
    name = _seed(
        tmp_path,
        monkeypatch,
        [Flashcard(front="Q?", back="A", status="added", anki_id=1)],
    )

    with pytest.raises(HTTPException) as exc:
        cards_route.update_card(name, 0, CardUpdate(front="new?"))

    assert exc.value.status_code == 409


def test_update_route_out_of_range_is_404(tmp_path, monkeypatch):
    name = _seed(tmp_path, monkeypatch, [Flashcard(front="Q?", back="A")])

    with pytest.raises(HTTPException) as exc:
        cards_route.update_card(name, 5, CardUpdate(front="new?"))

    assert exc.value.status_code == 404


def test_skip_route_marks_skipped(tmp_path, monkeypatch):
    name = _seed(tmp_path, monkeypatch, [Flashcard(front="Q?", back="A")])

    result = cards_route.skip_card(name, 0)

    assert result.card.status == "skipped"


def test_get_cards_route_returns_validation(tmp_path, monkeypatch):
    name = _seed(tmp_path, monkeypatch, [Flashcard(front="Q?", back="A")])

    resp = cards_route.get_cards(name)

    assert resp.total == 1
    assert resp.cards[0].card.front == "Q?"


def test_list_files_route_reports_counts(tmp_path, monkeypatch, fake_client):
    name = _seed(
        tmp_path,
        monkeypatch,
        [Flashcard(front="Q1?", back="A1"), Flashcard(front="Q2?", back="A2")],
    )
    cards_route.approve_card(name, 0, fake_client)

    listing = cards_route.list_card_files()

    stat = next(f for f in listing.files if f.filename == name)
    assert stat.total_cards == 2
    assert stat.added_cards == 1
    assert stat.pending_cards == 1


def test_invalid_filename_is_400(tmp_path, monkeypatch):
    monkeypatch.setattr(cards_route, "CARDS_DIR", tmp_path)

    with pytest.raises(HTTPException) as exc:
        cards_route.get_cards("../etc/passwd")

    assert exc.value.status_code == 400
