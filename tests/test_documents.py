"""Tests for DOCX extraction helpers."""

from pathlib import Path

from src.documents import extract_docx_text


def test_extract_docx_text_returns_content():
    repo_root = Path(__file__).resolve().parents[1]
    doc_path = repo_root / "Architecture for an LLM-Assisted Anki Flashcard System.docx"
    text = extract_docx_text(doc_path)

    assert len(text) > 100
    assert "anki" in text.lower()
