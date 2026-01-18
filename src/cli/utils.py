"""File utilities for CLI."""

import re
from pathlib import Path

SCRAPED_DIR = Path("scraped")


def slugify_filename(name: str) -> str:
    """Convert a filename stem into a safe, kebab-cased slug."""
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "document"


def default_docx_output_path(docx_file: Path) -> Path:
    """Return a unique markdown path under scraped/ for a DOCX file."""
    slug = slugify_filename(docx_file.stem)
    destination = SCRAPED_DIR / f"{slug}.md"
    counter = 1
    while destination.exists():
        counter += 1
        destination = SCRAPED_DIR / f"{slug}-{counter}.md"
    return destination
