from src.schema import (
    Flashcard,
    ValidationWarning,
    convert_newlines_to_html,
    validate_card,
)


def test_convert_newlines_to_html_handles_mixed_endings():
    text = "Line one\r\nLine two\rLine three\nLine four"
    assert (
        convert_newlines_to_html(text)
        == "Line one<br>Line two<br>Line three<br>Line four"
    )


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


# EAT 2.0: Simplified validation tests
# Only structural errors (empty front/back) should fail


def test_validate_card_empty_front_returns_error():
    """Empty front is a structural error."""
    card = Flashcard(front="", back="Some answer", tags=["test"])
    warnings = validate_card(card)

    assert len(warnings) == 1
    assert warnings[0].severity == "error"
    assert "Front cannot be empty" in warnings[0].message


def test_validate_card_empty_back_returns_error():
    """Empty back is a structural error."""
    card = Flashcard(front="What is X?", back="", tags=["test"])
    warnings = validate_card(card)

    assert len(warnings) == 1
    assert warnings[0].severity == "error"
    assert "Back cannot be empty" in warnings[0].message


def test_validate_card_whitespace_only_returns_error():
    """Whitespace-only content is treated as empty."""
    card = Flashcard(front="   \n\t  ", back="Answer", tags=["test"])
    warnings = validate_card(card)

    assert len(warnings) == 1
    assert warnings[0].severity == "error"


def test_validate_card_valid_card_no_warnings():
    """A valid card should pass with no warnings."""
    card = Flashcard(
        front="Why does Python 3 require parentheses for print?",
        back="print() is a function in Python 3, not a statement",
        context="Python 2's print was a language statement",
        tags=["python", "type::concept"],
    )
    warnings = validate_card(card)

    assert len(warnings) == 0


# EAT 2.0: Previously problematic patterns should no longer trigger warnings


def test_validate_card_and_in_question_no_warning():
    """'and' in question should NOT trigger warning (EAT 2.0)."""
    card = Flashcard(
        front="Why do both Python decorators and context managers use wrapper patterns?",
        back="Both need to execute code before/after an operation",
        tags=["python"],
    )
    warnings = validate_card(card)

    # Should have NO warnings - the old mechanical rule is removed
    assert len(warnings) == 0


def test_validate_card_pronoun_this_no_warning():
    """Technical pronouns like 'this' should NOT trigger warning (EAT 2.0)."""
    card = Flashcard(
        front="What does `this` refer to in a JavaScript arrow function?",
        back="The lexical scope (parent context), not the function itself",
        tags=["javascript"],
    )
    warnings = validate_card(card)

    assert len(warnings) == 0


def test_validate_card_abbreviation_no_warning():
    """Common abbreviations like DNA, API should NOT trigger warning (EAT 2.0)."""
    card = Flashcard(
        front="How does DNA replication begin?",
        back="Helicase unwinds the double helix",
        tags=["biology"],
    )
    warnings = validate_card(card)

    assert len(warnings) == 0


def test_validate_card_no_question_mark_no_error():
    """Cards without question marks should NOT error (cloze cards are valid)."""
    card = Flashcard(
        front="print('Hello') is valid syntax in {{Python 3}}",
        back="Python 3",
        tags=["python", "type::fact"],
    )
    warnings = validate_card(card)

    # Should have NO errors - cloze deletions are valid
    assert len(warnings) == 0


def test_validate_card_short_answer_no_warning():
    """Short answers should NOT trigger warning (atomicity is good)."""
    card = Flashcard(
        front="What is the default HTTP port?",
        back="80",
        tags=["networking"],
    )
    warnings = validate_card(card)

    # Atomic facts with short answers are GOOD in EAT 2.0
    assert len(warnings) == 0


def test_validation_warning_str_representation():
    """ValidationWarning should have proper string representation."""
    warning = ValidationWarning("Test message", "error")
    assert "❌" in str(warning)
    assert "Test message" in str(warning)

    warning_info = ValidationWarning("Info message", "info")
    assert "ℹ️" in str(warning_info)
