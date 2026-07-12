---
status: accepted
---

# Card content is trusted; only image filenames are escaped

When rendering a Flashcard into an Anki Note (`render_anki_note` in `src/anki_notes.py`), the Front, Back, and Context text are passed through to Anki **unescaped** — only newline-to-`<br>` conversion is applied. Image filenames are the sole exception: they are HTML-escaped before being interpolated into an `<img src="...">` tag. This preserves the historical behaviour of the removed `Flashcard.to_anki_note` byte-for-byte.

## Why

Card content is **trusted local input**. It is authored by the user or by an agent under the user's review, lives in version-controlled `cards/*.json` files, and is rendered into the user's own private Anki collection — never into a shared or network-facing surface. Authors deliberately embed light HTML (`<b>`, `<br>`, lists) and MathJax (`\( ... \)`, `\[ ... \]`) that Anki must receive verbatim to render. HTML-escaping the text fields would double-escape those constructs and break every mathematical and formatted card.

Image filenames are escaped because they flow into an HTML attribute where a stray `"` would corrupt the tag, and because a filename is a mechanical reference rather than authored display content.

## Considered options

- **Escape all fields** (the "safe by default" instinct) — rejected: it breaks intentional HTML/MathJax passthrough, which is a core feature, not an oversight.
- **Escape nothing, including filenames** — rejected: filenames are interpolated into an attribute and are not meant to carry markup, so an unescaped `"` or `<` there is a bug, not a feature.
- **Trust text, escape filenames** (chosen) — matches the authoring model and the prior behaviour.

## Consequences

- The Anki Submission path assumes card content is trusted. **If a future feature ever renders card content into a shared, multi-user, or web-facing surface, that surface must do its own escaping** — the submission layer will not.
- This assumption is deliberately narrow. It is recorded here so a future reader who sees unescaped interpolation in `render_anki_note` understands it is a considered decision, not a missing sanitisation step, and does not "fix" it by escaping the text fields.
