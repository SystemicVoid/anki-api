"""End-to-end web wiring tests via FastAPI TestClient.

Where test_card_routes.py calls the handlers directly (fast, logic-focused),
these exercise the real app: route registration, path/response-model
serialization, and the get_anki_client dependency (overridden with a fake). This
is the coverage Codex E1/E2 asked for — the class of wiring bug a direct call
cannot catch.
"""

import pytest
from conftest import FakeAnkiClient
from fastapi.testclient import TestClient

from src.schema import Flashcard, load_cards_from_json, save_cards_to_json
from web.backend.deps import get_anki_client
from web.backend.main import app
from web.backend.routes import cards as cards_route


@pytest.fixture
def web(tmp_path, monkeypatch):
    """A TestClient with CARDS_DIR pointed at tmp_path and Anki faked."""
    monkeypatch.setattr(cards_route, "CARDS_DIR", tmp_path)
    fake = FakeAnkiClient()
    app.dependency_overrides[get_anki_client] = lambda: fake
    try:
        yield TestClient(app), fake, tmp_path
    finally:
        app.dependency_overrides.clear()


def _seed(tmp_path, cards, name="deck.json") -> str:
    save_cards_to_json(cards, str(tmp_path / name))
    return name


def test_approve_route_end_to_end(web):
    client, fake, tmp_path = web
    name = _seed(tmp_path, [Flashcard(front="Q?", back="A")])

    resp = client.post(f"/api/cards/{name}/0/approve")

    assert resp.status_code == 200
    body = resp.json()
    assert body["card"]["status"] == "added"
    assert body["card"]["anki_id"] == 1001
    assert len(fake.notes) == 1
    assert load_cards_from_json(str(tmp_path / name))[0].status == "added"


def test_approve_route_conflict_is_409(web):
    client, fake, tmp_path = web
    name = _seed(tmp_path, [Flashcard(front="Q?", back="A", status="added")])

    resp = client.post(f"/api/cards/{name}/0/approve")

    assert resp.status_code == 409
    assert fake.notes == []


def test_approve_route_bad_index_is_404(web):
    client, _fake, tmp_path = web
    name = _seed(tmp_path, [Flashcard(front="Q?", back="A")])

    resp = client.post(f"/api/cards/{name}/9/approve")

    assert resp.status_code == 404


def test_update_route_rejects_added_card_409(web):
    client, _fake, tmp_path = web
    name = _seed(tmp_path, [Flashcard(front="Q?", back="A", status="added", anki_id=1)])

    resp = client.put(f"/api/cards/{name}/0", json={"front": "changed?"})

    assert resp.status_code == 409


def test_skip_route_end_to_end(web):
    client, _fake, tmp_path = web
    name = _seed(tmp_path, [Flashcard(front="Q?", back="A")])

    resp = client.post(f"/api/cards/{name}/0/skip")

    assert resp.status_code == 200
    assert resp.json()["card"]["status"] == "skipped"


def test_get_cards_route_end_to_end(web):
    client, _fake, tmp_path = web
    name = _seed(tmp_path, [Flashcard(front="Q?", back="A")])

    resp = client.get(f"/api/cards/{name}")

    assert resp.status_code == 200
    assert resp.json()["total"] == 1


def test_anki_add_route_end_to_end(web):
    client, fake, _tmp_path = web

    resp = client.post(
        "/api/anki/add",
        json={
            "front": "What is broadcasting?",
            "back": "Reusing a vector across rows.",
            "context": "",
            "tags": ["ml"],
            "images": [],
            "source": "",
            "deck": "Default",
            "model": "Basic",
        },
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["note_id"] == 1001
    assert len(fake.notes) == 1
