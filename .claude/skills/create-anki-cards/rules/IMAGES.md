# Images on Anki Cards

Read this when a card should carry a diagram/image, or when **attaching an image
to a card that is already in Anki**. Only add genuine dual-coding — a picture that
*shows* what the text can only describe (geometry, dataflow, a curve). No
decorative or redundant images.

## Media constraints (`src/media.py`)

- Image files live **directly** in `cards/media/` — no subfolders.
- Filename must match `^[A-Za-z0-9][A-Za-z0-9._-]*$` and end in one of
  `.gif .jpeg .jpg .png .svg .webp`. Convention: lowercase kebab-case, prefixed
  by the card set, e.g. `codesignal-intro-ml-sigmoid.png`.
- A card's `images` field is a **list** of these bare filenames (not paths).
- `validate_media_filename()` / `resolve_media_path()` enforce the above; a bad
  name raises `ValueError` rather than silently passing.

## How an image renders (`render_anki_note`, `src/anki_notes.py`)

Each filename becomes `<img src="filename">`, inserted **after the Back text and
before the `---` context separator**. Only the filename is HTML-escaped; card
text is trusted (see `docs/adr/0001-card-content-trust-and-escaping.md`).
Always let `render_anki_note` build the field — never hand-splice `<img>` HTML.

---

## Case A — image on a NEW card (not yet added)

Set `images` in the card JSON and let the normal add path do the upload:

```json
{ "front": "...", "back": "...", "context": "...",
  "images": ["codesignal-intro-ml-sigmoid.png"], "tags": ["..."] }
```

`add_card_to_anki` / `add_cards_to_anki` (used by `uv run anki-api review` and the
`add` CLI) call `upload_media_files` (→ `storeMediaFile`) **before** `add_note`, so
the picture is present the moment the note is created. Nothing else to do.

---

## Case B — attach an image to an EXISTING note (already added)

The note exists, so `addNote` is **not** used. Attaching is a two-call transaction:

1. `store_media_file(filename, bytes)` → puts the image in Anki's media collection
   (`storeMediaFile`). **Do this first** — a field referencing a missing file
   renders as a broken image.
2. `update_note_fields(note_id, {"Back": <re-rendered Back>})` → repoints the field
   (`updateNoteFields`).

`update_note_fields` **overwrites** the Back field wholesale. So re-render the Back
with `render_anki_note` (which produces the original Back *plus* the `<img>` in the
right place) rather than editing the live HTML by hand.

### Verify before you mutate

Because the update overwrites, first prove the card JSON still mirrors the live
note — then re-rendering only *adds* the image and changes nothing else:

- For each target, render the card **as it currently stands** (its `images` still
  unset) and diff against the note's live Back
  (`get_note_info([...])` → `fields["Back"]["value"]`).
- **Equal** → in sync → safe to attach.
- **Drift** (live ≠ re-render) or the `<img>` is **already present** → skip/stop.
  Don't blindly overwrite a note that was hand-edited in Anki, and don't
  double-attach. The check makes the whole operation **idempotent**.

### Reference implementation

```python
from src.anki_client import AnkiClient
from src.anki_notes import render_anki_note
from src.media import upload_media_files          # reads cards/media/, calls storeMediaFile
from src.schema import load_cards_from_json, save_cards_to_json

mapping = {1783873142990: "codesignal-intro-ml-sigmoid.png"}  # anki_id -> filename

cards = load_cards_from_json(path)
by_id = {c.anki_id: c for c in cards}
client = AnkiClient()
live = {n["noteId"]: n for n in client.get_note_info(list(mapping))}

for anki_id, filename in mapping.items():
    card = by_id[anki_id]
    live_back = live[anki_id]["fields"]["Back"]["value"]
    if filename in live_back:
        continue                                          # already attached — idempotent
    if live_back != render_anki_note(card)["fields"]["Back"]:
        raise SystemExit(f"drift on {anki_id}: live Back != JSON re-render; not touching it")
    card.images = [filename]                              # set JSON field
    upload_media_files(client, card.images)              # 1. storeMediaFile
    new_back = render_anki_note(card)["fields"]["Back"]
    client.update_note_fields(anki_id, {"Back": new_back})  # 2. updateNoteFields

save_cards_to_json(cards, path)                          # persist images field back to JSON
```

### Confirm it landed

```python
info = {n["noteId"]: n for n in client.get_note_info(list(mapping))}
for anki_id, filename in mapping.items():
    back = info[anki_id]["fields"]["Back"]["value"]
    assert f'<img src="{filename}">' in back            # tag present
    assert back.find(filename) < back.find("---")       # sits before the context rule
# media bytes actually stored:
client._invoke("retrieveMediaFile", {"filename": filename})  # returns base64, not None/False
```

## Don't

- Don't create decks or subfolders for media — files go flat in `cards/media/`.
- Don't hand-write `<img>` HTML into a field; always go through `render_anki_note`.
- Don't overwrite a note's Back without the drift check above.
- Don't attach decorative or redundant images — dual-coding only.
