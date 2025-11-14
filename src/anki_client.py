"""AnkiConnect API client for interacting with Anki."""

import json
from typing import Any, Dict, List, Optional

import requests


class AnkiConnectError(Exception):
    """Raised when AnkiConnect returns an error."""
    pass


class AnkiClient:
    """Client for communicating with AnkiConnect."""

    def __init__(self, url: str = "http://localhost:8765"):
        """Initialize the AnkiConnect client.

        Args:
            url: AnkiConnect API endpoint URL
        """
        self.url = url
        self.version = 6

    def _invoke(self, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Invoke an AnkiConnect action.

        Args:
            action: The API action to invoke
            params: Optional parameters for the action

        Returns:
            The result from AnkiConnect

        Raises:
            AnkiConnectError: If AnkiConnect returns an error
            requests.RequestException: If connection fails
        """
        payload = {
            "action": action,
            "version": self.version,
        }
        if params is not None:
            payload["params"] = params

        try:
            response = requests.post(self.url, json=payload, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            raise AnkiConnectError(
                f"Failed to connect to AnkiConnect at {self.url}. "
                f"Make sure Anki is running with AnkiConnect installed. Error: {e}"
            ) from e

        result = response.json()

        if result.get("error") is not None:
            raise AnkiConnectError(f"AnkiConnect error: {result['error']}")

        return result.get("result")

    def ping(self) -> bool:
        """Check if AnkiConnect is available.

        Returns:
            True if AnkiConnect is responding

        Raises:
            AnkiConnectError: If connection fails
        """
        try:
            self._invoke("version")
            return True
        except Exception:
            return False

    def get_decks(self) -> List[str]:
        """Get list of all deck names.

        Returns:
            List of deck names
        """
        return self._invoke("deckNames")

    def get_models(self) -> List[str]:
        """Get list of all note type (model) names.

        Returns:
            List of model names (e.g., 'Basic', 'Cloze')
        """
        return self._invoke("modelNames")

    def get_model_fields(self, model_name: str) -> List[str]:
        """Get field names for a specific note type.

        Args:
            model_name: Name of the note type

        Returns:
            List of field names for the model
        """
        return self._invoke("modelFieldNames", {"modelName": model_name})

    def add_note(
        self,
        deck_name: str,
        model_name: str,
        fields: Dict[str, str],
        tags: Optional[List[str]] = None,
    ) -> int:
        """Add a single note to Anki.

        Args:
            deck_name: Name of the deck to add the note to
            model_name: Name of the note type (e.g., 'Basic')
            fields: Dictionary mapping field names to values
            tags: Optional list of tags

        Returns:
            Note ID of the created note

        Raises:
            AnkiConnectError: If note creation fails
        """
        note = {
            "deckName": deck_name,
            "modelName": model_name,
            "fields": fields,
            "tags": tags or [],
            "options": {
                "allowDuplicate": False,
                "duplicateScope": "deck",
            }
        }

        return self._invoke("addNote", {"note": note})

    def add_notes_batch(self, notes: List[Dict[str, Any]]) -> List[Optional[int]]:
        """Add multiple notes to Anki in a single request.

        Args:
            notes: List of note dictionaries with keys:
                - deckName: str
                - modelName: str
                - fields: Dict[str, str]
                - tags: List[str] (optional)

        Returns:
            List of note IDs (None for failed additions)
        """
        formatted_notes = []
        for note in notes:
            formatted_note = {
                "deckName": note["deckName"],
                "modelName": note["modelName"],
                "fields": note["fields"],
                "tags": note.get("tags", []),
                "options": {
                    "allowDuplicate": False,
                    "duplicateScope": "deck",
                }
            }
            formatted_notes.append(formatted_note)

        return self._invoke("addNotes", {"notes": formatted_notes})

    def find_notes(self, query: str) -> List[int]:
        """Search for notes using Anki query syntax.

        Args:
            query: Anki search query (e.g., "deck:Default tag:python")

        Returns:
            List of note IDs matching the query
        """
        return self._invoke("findNotes", {"query": query})

    def get_note_info(self, note_ids: List[int]) -> List[Dict[str, Any]]:
        """Get detailed information about notes.

        Args:
            note_ids: List of note IDs

        Returns:
            List of note information dictionaries
        """
        return self._invoke("notesInfo", {"notes": note_ids})

    def update_note_fields(self, note_id: int, fields: Dict[str, str]) -> None:
        """Update the fields of an existing note.

        Args:
            note_id: ID of the note to update
            fields: Dictionary mapping field names to new values
        """
        note = {
            "id": note_id,
            "fields": fields,
        }
        self._invoke("updateNoteFields", {"note": note})

    def delete_notes(self, note_ids: List[int]) -> None:
        """Delete notes by their IDs.

        Args:
            note_ids: List of note IDs to delete
        """
        self._invoke("deleteNotes", {"notes": note_ids})

    def add_tags(self, note_ids: List[int], tags: List[str]) -> None:
        """Add tags to notes.

        Args:
            note_ids: List of note IDs
            tags: List of tags to add
        """
        self._invoke("addTags", {"notes": note_ids, "tags": " ".join(tags)})

    def remove_tags(self, note_ids: List[int], tags: List[str]) -> None:
        """Remove tags from notes.

        Args:
            note_ids: List of note IDs
            tags: List of tags to remove
        """
        self._invoke("removeTags", {"notes": note_ids, "tags": " ".join(tags)})
