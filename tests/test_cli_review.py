"""CLI review smoke test via CliRunner.

Drives the interactive review command end to end with a fake Anki client
injected in place of ``ensure_anki_running``, confirming the CLI is a thin
adapter over ReviewSession: approve persists an added card, skip persists a
skipped one.
"""

from click.testing import CliRunner

from src.cli.commands import cards as cards_cmd
from src.schema import Flashcard, load_cards_from_json, save_cards_to_json


def test_review_approve_then_skip_persists(tmp_path, monkeypatch, fake_client):
    monkeypatch.setattr(cards_cmd, "ensure_anki_running", lambda: fake_client)
    path = tmp_path / "cards.json"
    save_cards_to_json(
        [Flashcard(front="Q1?", back="A1"), Flashcard(front="Q2?", back="A2")],
        str(path),
    )

    runner = CliRunner()
    result = runner.invoke(cards_cmd.review, [str(path)], input="a\ns\n")

    assert result.exit_code == 0, result.output
    reloaded = load_cards_from_json(str(path))
    assert reloaded[0].status == "added"
    assert reloaded[0].anki_id == 1001
    assert reloaded[1].status == "skipped"
    assert len(fake_client.notes) == 1
