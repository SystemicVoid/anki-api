from src.schema import Flashcard, convert_newlines_to_html


def test_convert_newlines_to_html_handles_mixed_endings():
    text = "Line one\r\nLine two\rLine three\nLine four"
    assert convert_newlines_to_html(text) == "Line one<br>Line two<br>Line three<br>Line four"


def test_to_anki_note_converts_back_and_context_to_html():
    card = Flashcard(
        front="What is foo?\nProvide two points?",
        back="First line\nSecond line",
        context="Extra context line 1\nExtra context line 2",
        tags=["test"],
        deck="Learning",
        model="Basic",
    )

    note = card.to_anki_note()

    assert note["fields"]["Front"] == "What is foo?<br>Provide two points?"
    assert (
        note["fields"]["Back"]
        == "First line<br>Second line<br><br>---<br><br>Extra context line 1<br>Extra context line 2"
    )
