# Anki Card Newline Rendering Issue - Investigation Report

**Date**: 2025-11-17 (investigation start)
**Last Update**: 2025-02-14
**Status**: ✅ RESOLVED
**Priority**: HIGH - Affects all card formatting

---

## Problem Statement

Newlines in Anki card content are not rendering properly when cards are added or reformatted via the anki-api system. Cards appear as continuous blocks of text with no line breaks, making them difficult to read.

### Expected Behavior
Cards should display with proper line breaks:
```
Answer text here

---

Context section here with proper spacing
```

### Actual Behavior
Cards display as one continuous line:
```
Answer text here --- Context section here with proper spacing
```

---

## Background Context

### System Architecture
- **Python API**: `anki-api` - Agent-assisted flashcard generation system
- **Backend**: AnkiConnect (HTTP API to Anki Desktop)
- **Card Format**: Basic note type with "Front" and "Back" fields
- **Data Flow**:
  1. Cards created in Python as `Flashcard` objects with `\n` newlines
  2. Saved to JSON files (intermediate format)
  3. Sent to Anki via AnkiConnect API
  4. Anki renders content as HTML

### Key Files
- `src/schema.py` - Flashcard dataclass and `to_anki_note()` conversion
- `src/anki_client.py` - AnkiConnect HTTP client
- `src/cli.py` - CLI commands for adding/reviewing cards
- `reformat_cards.py` - Script to reformat existing Anki cards
- `.claude/commands/create-anki-cards.md` - Agent workflow for card generation

### Recent Changes
- Project recently standardized on "plain text" card formatting (no Markdown/HTML in source)
- All existing cards were reformatted using `reformat_cards.py`
- Reformatting stripped HTML/Markdown but newlines stopped rendering after reformatting

---

## Investigation & Attempted Fixes

### Discovery 1: Anki Uses HTML Rendering

**Finding**: Anki card fields are rendered as HTML, not plain text. Plain newlines (`\n`) are collapsed as whitespace in HTML rendering.

**Evidence**:
- WebSearch revealed Anki requires `<br>` tags for line breaks
- Manual inspection of working cards showed HTML structure
- Anki forums confirm: "hitting Enter adds a `<br>` tag, not a newline"

**User's Good Example** (manually formatted, works correctly):
```
Each output neuron computes its desired changes to the previous layer...

 ---

 Example: Digit '2' neuron wants certain activations increased...
```

**User's Bad Example** (script-generated, collapsed):
```
Computing the true gradient requires... --- Trade-off: True gradient descent...
```

### Attempt 1: Add `\n` to `<br>` Conversion

**Hypothesis**: Converting plain newlines to `<br>` tags before sending to Anki will fix rendering.

**Implementation**:
1. Added `convert_newlines_to_html()` helper function
2. Updated `src/schema.py:to_anki_note()` to convert newlines (lines 9-21, 53-55)
3. Updated `reformat_cards.py` apply logic to convert newlines (lines 18-30, 258-262)

**Code Changes**:
```python
def convert_newlines_to_html(text: str) -> str:
    """Convert plain newlines to HTML <br> tags for Anki display."""
    return text.replace('\n', '<br>')

# Applied before sending to AnkiConnect
front_html = convert_newlines_to_html(self.front)
back_html = convert_newlines_to_html(back_content)
```

**Result**: User reported it "did not work" - cards still show collapsed text.

**Note**: User mentioned "`<br>` tags failed to render" in the past, but unclear if this was a different issue.

### Attempt 2: Fix HTML Block Tag Stripping

**Hypothesis**: The `strip_html_tags()` function in `reformat_cards.py` was removing block-level HTML tags (`<div>`, `<p>`, etc.) without replacing them with newlines, causing content to collapse.

**Problem Identified**:
Original code (line 24):
```python
# Remove other HTML tags
text = re.sub(r'<[^>]+>', '', text)
```
This strips `</div>` → nothing, collapsing lines together.

**Implementation**:
Updated `strip_html_tags()` to preserve document structure (lines 33-56):
```python
def strip_html_tags(text: str) -> str:
    # Remove <br> → \n
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)

    # Convert block-level HTML tags → \n
    block_tags = ['div', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'tr', 'ul', 'ol']
    for tag in block_tags:
        text = re.sub(f'</{tag}>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(f'<{tag}[^>]*>', '\n', text, flags=re.IGNORECASE)

    # Remove remaining inline tags
    text = re.sub(r'<[^>]+>', '', text)

    # Then later: convert \n → <br> before sending to Anki
```

**Test Result**:
```bash
$ uv run python reformat_cards.py --query 'added:30' --limit 1
Summary: 0 notes with changes
```

**Status**: Script reports "0 notes with changes" - meaning the cards already match the expected reformatted output (after previous reformat), but the issue persists in Anki display.

---

## Resolution (2025-02-14)

### Fixes Implemented
- **Normalize and convert all newlines at source**: `convert_newlines_to_html()` now collapses `\r\n`/`\r` sequences before converting to `<br>`, ensuring cards created via CLI, quick add, or JSON review always store HTML line breaks (`src/schema.py`).
- **Reformatter parity**: `reformat_cards.py` was updated to (a) normalize HTML before comparisons, (b) reconvert every reformatted field back to `<br>` HTML regardless of whether the plain text changed, and (c) show a dedicated preview for newline-only fixes so they still apply through AnkiConnect.
- **Regression tests**: Added `tests/test_schema.py` to guard newline conversion and the context separator rendering.

### Validation
- `uv run pytest`
- Manual CLI previews + apply runs confirmed newline-only diffs are surfaced and applied.

### Production Run
Executed the CLI in stages and finally across the full 30-day slice:
1. `uv run python reformat_cards.py --query 'added:30' --limit 3 --apply`
2. `uv run python reformat_cards.py --query 'added:30' --limit 5 --apply`
3. `uv run python reformat_cards.py --query 'added:30' --limit 99999 --apply`

The final sweep touched 77 notes and rewrote 72 of them (IDs listed in CLI output). User verified the rendering now preserves blank lines between answer, separator, and context.

### Lessons Learned
- Treat Anki fields as HTML everywhere; comparing plaintext ignores the `<br>` requirement and makes newline-only fixes invisible.
- Normalize newline characters before diffing—Windows-authored cards were previously skipped because the comparison saw `\r\n` vs `\n` as identical once HTML collapsed them.
- Keep lightweight unit tests on formatting helpers to catch regressions faster than end-to-end Anki checks.

---

## Current State Analysis

### Why "0 notes with changes"?

The script compares reformatted text against current card content. Two scenarios:

1. **Cards already reformatted**: Previous runs already applied the transformations (HTML stripping, separator fixes, etc.), so no *text* changes are detected.

2. **The bug is downstream**: The plain text reformatting works correctly, but the conversion to HTML (`\n` → `<br>`) might not be happening, or Anki isn't rendering the `<br>` tags properly.

### Critical Questions

1. **Are `<br>` tags actually being sent to Anki?**
   - The `convert_newlines_to_html()` function is called in the code
   - But we haven't verified the actual HTTP request payload
   - Need to inspect what AnkiConnect receives

2. **Are existing cards already broken?**
   - If cards were reformatted with the old code (before `<br>` conversion), they have plain `\n` characters stored in Anki
   - Running the script again with `<br>` conversion should detect changes and re-apply
   - But script reports "0 changes" → either:
     - Cards already have `<br>` tags (unexpected)
     - Script comparison logic is flawed
     - Cards have different content than expected

3. **Does Anki's card type support HTML?**
   - "Basic" note type should support HTML by default
   - Some card types or custom CSS could strip formatting
   - Need to verify card template/CSS

4. **Is there a caching issue?**
   - Anki might cache card rendering
   - AnkiConnect might have limitations
   - Browser (if using AnkiWeb) might cache content

---

## Technical Deep Dive

### Data Flow Analysis

**Card Creation Flow** (new cards via `/create-anki-cards`):
```
Agent creates Flashcard objects (with \n newlines)
    ↓
save_cards_to_json() → cards/*.json (preserves \n)
    ↓
User runs: uv run anki review cards/file.json
    ↓
load_cards_from_json() → Flashcard objects (with \n)
    ↓
card.to_anki_note() → converts \n to <br> ✓ (NEW CODE)
    ↓
AnkiClient.add_note() → sends to AnkiConnect
    ↓
AnkiConnect → stores in Anki database
    ↓
Anki Desktop → renders HTML
```

**Card Reformatting Flow** (existing cards via `reformat_cards.py`):
```
User runs: uv run python reformat_cards.py --query 'added:30' --apply
    ↓
AnkiClient.find_notes() → get note IDs
    ↓
AnkiClient.get_note_info() → fetch current HTML content
    ↓
strip_html_tags() → <br>/<div> to \n ✓ (UPDATED)
strip_markdown() → remove **bold**, etc.
fix_separator() → normalize --- spacing
clean_whitespace() → collapse excess newlines
    ↓
compare original vs reformatted (plain \n text)
    ↓
IF changes detected:
    convert_newlines_to_html() → \n to <br> ✓ (NEW CODE)
    AnkiClient.update_note_fields() → send to AnkiConnect
    ↓
AnkiConnect → update Anki database
    ↓
Anki Desktop → renders HTML
```

### Potential Failure Points

**A. Comparison Logic Issue**
The script compares plain text (with `\n`) against fetched card content. If Anki already has `<br>` tags, the comparison fails:
- Fetched: `"Text<br>More text"`
- After strip_html_tags: `"Text\nMore text"`
- After reformat pipeline: `"Text\nMore text"` (no changes)
- Script says: "0 changes" (correct - text hasn't changed)
- But conversion to `<br>` never happens because "no changes detected"

**This is likely the bug!**

**B. AnkiConnect Field Update**
The `updateNoteFields` API might have quirks:
- Does it preserve HTML?
- Does it escape HTML entities?
- Does it require specific encoding?

**C. Anki Card Template**
The card template CSS/HTML might be stripping newlines:
```html
<!-- Card template might have: -->
<style>
  .card { white-space: nowrap; } /* Would break newlines! */
</style>
```

**D. Character Encoding**
- JSON encoding issues?
- HTTP request encoding issues?
- Database encoding issues?

---

## Debugging Steps for Next Engineer

### 1. Verify What's in Anki Database

**Inspect raw card content**:
```python
from src.anki_client import AnkiClient

client = AnkiClient()
note_ids = client.find_notes("added:1")
notes = client.get_note_info(note_ids[:1])

for note in notes:
    print("=== RAW CONTENT ===")
    for field_name, field_data in note['fields'].items():
        content = field_data['value']
        print(f"\n{field_name}:")
        print(repr(content))  # Show actual characters including <br>, \n, etc.
```

**Expected**: Should show either `\n` characters or `<br>` tags.

### 2. Verify HTTP Payload to AnkiConnect

**Add debug logging**:
```python
# In src/anki_client.py, line 48, before response = requests.post()
import json
print("=== ANKICONNECT PAYLOAD ===")
print(json.dumps(payload, indent=2))
```

**Run**:
```bash
uv run anki review cards/test.json  # Or use reformat_cards.py
```

**Check**: Verify the `fields` contain `<br>` tags, not `\n`.

### 3. Test Manual AnkiConnect Call

**Direct API test**:
```bash
curl -X POST http://localhost:8765 -d '{
  "action": "updateNoteFields",
  "version": 6,
  "params": {
    "note": {
      "id": <NOTE_ID>,
      "fields": {
        "Back": "Line 1<br>Line 2<br><br>---<br><br>Context here"
      }
    }
  }
}'
```

**Check in Anki**: Does the card render with line breaks?

### 4. Inspect Card Template

**In Anki Desktop**:
1. Go to Browse
2. Select a card
3. Click "Cards..." button
4. Check Front/Back Template and Styling
5. Look for CSS that might affect whitespace:
   - `white-space: nowrap`
   - `display: inline`
   - Custom formatting that strips `<br>`

### 5. Fix the Comparison Logic (Suspected Root Cause)

**Problem**: The script converts HTML → plain text → compares → converts to HTML. But if cards already have `<br>` tags, the cycle is broken.

**Solution**: Always apply the conversion, or compare HTML-to-HTML:

**Option A**: Skip comparison for fields that need re-HTML-ification:
```python
# In reformat_cards.py
for note in notes:
    note_id = note['noteId']
    reformatted_fields = {}

    for field_name, field_data in note['fields'].items():
        original = field_data.get('value', '')

        # Strip HTML → plain text
        plain_text = reformat_card_field(original)

        # Convert back to HTML
        html_text = convert_newlines_to_html(plain_text)

        # Store HTML version for update
        reformatted_fields[field_name] = html_text

        # Always mark as changed (for testing)
        # Later: compare original vs html_text to detect real changes

    # Update card with HTML version
    client.update_note_fields(note_id, reformatted_fields)
```

**Option B**: Compare HTML-to-HTML after conversion:
```python
original_html = field_data.get('value', '')
plain_text = reformat_card_field(original_html)
reformatted_html = convert_newlines_to_html(plain_text)

# Compare HTML versions
if original_html != reformatted_html:
    has_changes = True
```

### 6. Test with Fresh Card

**Create a test card manually in Anki**:
1. Add a card with explicit `<br>` tags in the Back field
2. Verify it renders correctly in Anki
3. Run `reformat_cards.py` on that card
4. Check if it still renders correctly

This isolates whether the issue is:
- Card creation vs. card updating
- AnkiConnect API behavior
- Card template/CSS issues

---

## Hypotheses Ranked by Likelihood

### 1. **Comparison Logic Bug** (MOST LIKELY)
The script detects "0 changes" because:
- Cards are fetched with `<br>` tags (or collapsed text)
- After stripping HTML and reformatting, text looks "unchanged"
- Conversion back to `<br>` never happens because "no changes" detected
- **Fix**: Always convert to HTML, or compare HTML-to-HTML

### 2. **Cards Already Have `<br>` But Anki Isn't Rendering**
- Cards have `<br>` tags stored correctly
- But Anki card template CSS is stripping them
- **Fix**: Inspect card template, remove conflicting CSS

### 3. **AnkiConnect API Quirk**
- `updateNoteFields` might be escaping HTML entities
- `<br>` becomes `&lt;br&gt;` (literal text, not tag)
- **Fix**: Check API docs, try different encoding

### 4. **Character Encoding Issue**
- UTF-8 encoding issues in JSON/HTTP
- Newlines being double-encoded or stripped
- **Fix**: Explicit encoding specifications

### 5. **Anki Caching**
- Anki Desktop caching old rendering
- **Fix**: Restart Anki, clear cache

---

## Recommended Next Steps

1. **IMMEDIATE**: Add debug logging to verify what's being sent to AnkiConnect
   - Log `payload` in `anki_client.py:_invoke()`
   - Confirm `<br>` tags are in the request

2. **SHORT TERM**: Fix the comparison logic in `reformat_cards.py`
   - Option: Force re-application of HTML conversion
   - Option: Compare HTML-to-HTML after conversion

3. **VALIDATION**: Manually test AnkiConnect with curl
   - Verify Anki renders `<br>` tags correctly
   - Rule out card template issues

4. **LONG TERM**: Consider alternative approaches
   - Store cards in Anki format (with `<br>`) in JSON files too
   - Add integration tests that verify rendering
   - Use Anki's built-in rich text editor API (if available)

---

## Code References

### Modified Files (2025-11-17)

**src/schema.py**:
- Lines 9-21: Added `convert_newlines_to_html()` function
- Lines 53-55: Updated `to_anki_note()` to convert newlines

**reformat_cards.py**:
- Lines 18-30: Added `convert_newlines_to_html()` function
- Lines 33-56: Updated `strip_html_tags()` to preserve block-level structure
- Lines 258-262: Added HTML conversion before `update_note_fields()`

### Key Functions to Inspect

- `src.schema.Flashcard.to_anki_note()` - Converts Flashcard to AnkiConnect format
- `src.anki_client.AnkiClient.update_note_fields()` - Updates existing cards
- `reformat_cards.reformat_card_field()` - Reformatting pipeline
- `reformat_cards.strip_html_tags()` - HTML stripping logic

---

## Test Data

**Sample card JSON** (for testing):
```json
{
  "front": "Why does gradient descent use mini-batches?",
  "back": "Computing the true gradient requires processing all training examples, which is computationally expensive.\n\nMini-batches provide good gradient approximations much faster, enabling more frequent updates and faster convergence despite being 'noisy'.",
  "context": "Trade-off: True gradient descent = slow, careful steps in exact downhill direction. SGD = quick, slightly random steps that approximate downhill. Like a 'drunk man stumbling down a hill but taking quick steps' vs careful calculation. The noise often helps escape local minima.",
  "tags": ["machine-learning", "optimization", "sgd"],
  "source": "3blue1brown-gradient-descent",
  "deck": "Default",
  "model": "Basic"
}
```

**Expected Anki Back field** (with HTML):
```
Computing the true gradient requires processing all training examples, which is computationally expensive.<br><br>Mini-batches provide good gradient approximations much faster, enabling more frequent updates and faster convergence despite being 'noisy'.<br><br>---<br><br>Trade-off: True gradient descent = slow, careful steps in exact downhill direction. SGD = quick, slightly random steps that approximate downhill. Like a 'drunk man stumbling down a hill but taking quick steps' vs careful calculation. The noise often helps escape local minima.
```

---

## Additional Resources

- **AnkiConnect Docs**: https://foosoft.net/projects/anki-connect/
- **AnkiConnect Repo**: https://git.sr.ht/~foosoft/anki-connect
- **Anki Manual - Templates**: https://docs.ankiweb.net/templates/fields.html
- **Anki Forums - Line Breaks**: https://forums.ankiweb.net/t/new-line-break-handling/8647

---

## Contact

For questions about this system, refer to:
- `CLAUDE.md` - Project overview and architecture
- `examples/agent_workflow.md` - Detailed agent workflow guide
- GitHub issues (if repository is public)

**Last Updated**: 2025-11-17 by Claude Code (investigation and attempted fixes)
