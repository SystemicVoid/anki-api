import base64
from typing import cast

import pytest

from src import media
from src.anki_client import AnkiClient


class RecordingMediaStore:
    def __init__(self) -> None:
        self.uploads: list[tuple[str, bytes]] = []

    def store_media_file(self, filename: str, data: bytes) -> str:
        self.uploads.append((filename, data))
        return filename


def test_upload_media_files_reads_unique_safe_files(tmp_path, monkeypatch):
    monkeypatch.setattr(media, "MEDIA_DIR", tmp_path)
    image = tmp_path / "diagram.png"
    image.write_bytes(b"png bytes")
    store = RecordingMediaStore()

    stored = media.upload_media_files(store, ["diagram.png", "diagram.png"])

    assert stored == ["diagram.png"]
    assert store.uploads == [("diagram.png", b"png bytes")]


def test_resolve_media_path_rejects_traversal(tmp_path, monkeypatch):
    monkeypatch.setattr(media, "MEDIA_DIR", tmp_path)

    with pytest.raises(ValueError, match="Invalid media filename"):
        media.resolve_media_path("../diagram.png")


def test_validate_media_filename_rejects_non_string_values():
    with pytest.raises(
        ValueError, match="Invalid media filename: expected a string, got NoneType"
    ):
        media.validate_media_filename(cast("str", None))


def test_anki_client_base64_encodes_media(monkeypatch):
    client = AnkiClient()
    calls = []

    def fake_invoke(action, params=None):
        calls.append((action, params))
        return "diagram.png"

    monkeypatch.setattr(client, "_invoke", fake_invoke)

    result = client.store_media_file("diagram.png", b"png bytes")

    assert result == "diagram.png"
    assert calls == [
        (
            "storeMediaFile",
            {
                "filename": "diagram.png",
                "data": base64.b64encode(b"png bytes").decode("ascii"),
            },
        )
    ]
