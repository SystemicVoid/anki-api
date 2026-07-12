# anki-api

The domain of turning source material into high-quality flashcards and reviewing them into a personal Anki collection. Agents propose cards; a human reviews each one before it is submitted to Anki.

This is a glossary of the project's ubiquitous language — the terms to use when designing and talking about the system, independent of any implementation language.

## Language

### The card

**Flashcard**:
Our unit of study — a question (front), an answer (back), supplementary context, tags, a source, and optional images — authored to the EAT standard. Distinct from what Anki stores.
_Avoid_: Card (ambiguous with Anki Card), Note, item.

**Front / Back / Context**:
The three authored text parts of a Flashcard: the prompt, the answer, and the supplementary understanding shown after a separator. "Context" here is a Flashcard field, not this glossary.
_Avoid_: question/answer/notes as field names in design talk.

**Tag**:
A hierarchical label on a Flashcard (`domain::topic`, `type::concept`) used to organise the collection instead of splitting it across decks.

**Source**:
Where a Flashcard's content originated — a URL, a document, or a transcript.

**Card Image**:
An image attached to a Flashcard, stored in Anki's media collection and referenced by filename.
_Avoid_: media (that is the storage, not the picture), attachment.

**EAT**:
The quality standard every Flashcard targets — Encoded (understanding before memorising), Atomic (one fact), Timeless (self-contained). Detailed in `docs/EAT_FRAMEWORK.md`.

### The review

**Card File**:
An ordered collection of Flashcards persisted together; the unit that is reviewed, version-controlled, and carries each card's Review Status.
_Avoid_: batch, deck file, card set.

**Review Session**:
The resumable activity of reviewing one Card File — deciding each Flashcard's fate and recording it so an interrupted pass resumes where it left off. It is the activity *around* a Card File, not the file itself.
_Avoid_: review file, batch, run.

**Review Status**:
A Flashcard's place in the review lifecycle: `pending` (undecided), `added` (submitted to Anki — terminal, never resubmitted), or `skipped` (set aside, may be reconsidered later).
_Avoid_: state (overloaded), stage.

**Approve / Skip / Edit / Reset**:
The Reviewer's actions on a Flashcard within a Review Session. Approve submits a pending (or reconsidered) card to Anki; Skip sets one aside; Edit changes the text of an undecided card; Reset re-opens skipped cards for another pass while leaving added cards linked to their Anki Note.
_Avoid_: accept/reject, delete (for skip).

**Reviewer**:
The person deciding each Flashcard's fate, working through either the command line or the web review interface. Both are surfaces onto the same Review Session.
_Avoid_: user (too vague), approver.

### The Anki boundary

**Anki Submission**:
The act of turning an approved Flashcard into a persisted note in Anki — rendering it, uploading its images, and adding it. Repeat-safe once recorded as added: an already-added Flashcard is never submitted twice.
_Avoid_: add, push, sync, export.

**Anki Note**:
Anki's stored representation of a Flashcard after submission — its deck, model, fields, and tags. Distinct from the Flashcard we author.
_Avoid_: note dict, record.

**Anki Card**:
The review unit Anki *generates* from an Anki Note (what the Reviewer's future self actually studies). We never create these directly; a Note may yield one or more Cards.
_Avoid_: using "card" for this without the "Anki" qualifier.

**Deck**:
An Anki grouping of Anki Cards. This project deliberately uses a single deck (`Default`) and organises with Tags instead of many decks.
_Avoid_: category, folder.

**Model**:
The Anki template that defines a note's fields (this project uses `Basic`). Anki's newer UI calls this a "note type".
_Avoid_: card type; using "note type" and "model" interchangeably in the same design.

**AnkiConnect**:
The local HTTP bridge to a running Anki Desktop through which every Anki Submission and query passes. If it is unreachable, no submission can happen.
