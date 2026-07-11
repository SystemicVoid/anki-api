"""Safe local media handling for flashcard images."""

import re
from collections.abc import Iterable
from pathlib import Path
from typing import Protocol

MEDIA_DIR = Path(__file__).resolve().parent.parent / "cards" / "media"
_SAFE_MEDIA_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_SUPPORTED_IMAGE_SUFFIXES = {".gif", ".jpeg", ".jpg", ".png", ".svg", ".webp"}


class MediaStore(Protocol):
    """An object capable of storing a named media payload."""

    def store_media_file(self, filename: str, data: bytes) -> str: ...


def validate_media_filename(filename: str) -> str:
    """Return a safe image filename or raise ``ValueError``."""
    if not isinstance(filename, str):
        raise ValueError(
            f"Invalid media filename: expected a string, got {type(filename).__name__}"
        )
    if not _SAFE_MEDIA_NAME.fullmatch(filename):
        raise ValueError(f"Invalid media filename: {filename}")
    if Path(filename).suffix.lower() not in _SUPPORTED_IMAGE_SUFFIXES:
        raise ValueError(f"Unsupported image type: {filename}")
    return filename


def resolve_media_path(filename: str) -> Path:
    """Resolve an existing card image inside the repository media directory."""
    safe_name = validate_media_filename(filename)
    path = MEDIA_DIR / safe_name
    if not path.is_file():
        raise ValueError(f"Card image not found: {safe_name}")
    return path


def upload_media_files(client: MediaStore, filenames: Iterable[str]) -> list[str]:
    """Upload each unique card image to Anki and return stored filenames."""
    stored: list[str] = []
    for filename in dict.fromkeys(filenames):
        path = resolve_media_path(filename)
        stored.append(client.store_media_file(filename, path.read_bytes()))
    return stored
