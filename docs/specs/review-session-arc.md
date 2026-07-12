# Spec — Review Session arc: one home for card review & Anki submission

- **Status:** Implemented on `refactor/review-session-arc` — commit 1 `8f938c0` (submission primitive), commit 2 `424a41e` (ReviewSession). Each lands green on `uv run pytest` (66) and `prek run`.
- **Branch / worktree:** `refactor/review-session-arc`
- **Date:** 2026-07-12
- **Provenance:** architecture review (`/improve-codebase-architecture`) → grilling (Codex-as-owner, `codex exec` at xhigh) → this spec (`/to-spec`).
- **Design vocabulary:** module, interface, depth, shallow, seam, adapter, leverage, locality (the `codebase-design` glossary).

---

## Problem Statement

Adding a reviewed flashcard to Anki is one operation, but it is written five times. The sequence *upload media → build the AnkiConnect note → add the note → record `status`/`anki_id`/`added_at` → save the file* is copy-pasted across CLI `review`, CLI `add`, CLI `quick`, web `approve`, and web `add` — and it has already **drifted** (media-upload ordering, idempotency, and save-on-error differ between copies). The `pending → added/skipped` review state machine has no owning module, so it re-crystallizes at every call site.

Because the Anki client is hard-constructed at each of those sites (`AnkiClient()` inline), there is **no seam to inject a fake** — and the test surface stops exactly there. The single web test can only assert the invalid-image error branch, because the moment code would talk to Anki there is nowhere to substitute a double. The entire web backend and the CLI review loop are untested.

Two facts are consequences of the same root cause: a change to "what it means to add a card" has zero **locality** (edit five places), and the behavior cannot be verified (no seam = no test).

## Solution

Give the operation a home. Deliver one connected refactor in dependency order — a seam, a submission primitive that uses it, and a Review Session module that owns the lifecycle — so the CLI and web become thin **adapters** over one deep module.

1. **Seam (Candidate 3).** Name the Anki dependency with a `NoteClient` Protocol (extending the existing `MediaStore` Protocol). Web routes receive it via one FastAPI `Depends`; the CLI passes through the client it already obtains from `ensure_anki_running()`. A recording in-memory fake is the second adapter — one adapter is a hypothetical seam, two make it real.
2. **Submission primitive (Candidate 2).** One module owns "a `Flashcard` becomes an Anki note": pure rendering to the AnkiConnect note shape, media upload, and submission. `Flashcard.to_anki_note()` is removed; all callers use the primitive and stop reaching around it.
3. **Review Session (Candidate 1, the destination).** One module owns the card-file lifecycle: load, the `pending → added/skipped` state machine, atomic persistence, idempotent approval, skip, edit, reset, and counts. The CLI review loop keeps only its prompt I/O; the web review routes keep only HTTP translation.

The interface each new module presents **is** its test surface: the state machine and the submission primitive are tested through the same seam the adapters cross in production, using the fake client and a temporary card file.

## Seams (the test surface)

The ideal number of new seams is one; this arc introduces effectively one conceptual seam expressed as a small Protocol pair, plus one reused filesystem seam.

- **`NoteClient` / `BatchNoteClient` (new, the primary seam).** The behavior note submission needs from an Anki client. Real adapter: `AnkiClient`. Test adapter: `FakeAnkiClient`. This is the highest seam available — callers and tests both cross it, and nothing needs to reach past it.
- **`MediaStore` (existing, reused).** Already a Protocol; `NoteClient` extends it so one fake satisfies both media upload and note submission.
- **Card-file location (existing, reused as-is).** The web routes' `CARDS_DIR` module constant remains the filesystem seam for tests (monkeypatched to a temp dir). A first-class project-paths module is **out of scope** (Candidate 4).

## User Stories

1. As a **card-authoring agent**, I want one documented function to turn a `Flashcard` into a persisted Anki note, so that I do not reconstruct AnkiConnect note dicts by hand.
2. As a **CLI reviewer**, I want `review` to walk my pending cards with approve/edit/skip/quit, so that I approve cards deliberately.
3. As a **CLI reviewer**, I want my review progress persisted after each decision, so that an interrupted session resumes at the first unreviewed card.
4. As a **CLI reviewer**, I want `--reset` to re-open my previously skipped cards for another pass, so that I can reconsider them without risking duplicate Anki notes for cards already added.
5. As a **CLI reviewer**, I want a failed Anki add to leave the card pending, so that I can retry it rather than lose it.
6. As a **CLI user**, I want `quick` to add a single card in one command, so that I capture a fact without writing a file.
7. As a **CLI user**, I want `add` to batch-add a reviewed file to Anki, so that I push many cards at once.
8. As a **CLI user**, I want `add` to record which cards were actually accepted, so that the file reflects real submission state rather than lying that accepted cards are still pending.
9. As a **web reviewer**, I want to load a card file, see per-card validation, and approve/skip/edit each card, so that I review in a browser.
10. As a **web reviewer**, I want approval to be idempotent, so that a double-click or retry never creates a duplicate note.
11. As a **web reviewer**, I want two concurrent approvals of the same card to result in at most one Anki note, so that races do not duplicate my cards.
12. As a **web reviewer**, I want a clear error when Anki is unreachable, so that I know to start Anki rather than see a silent failure.
13. As a **maintainer**, I want the add-to-Anki transaction defined once, so that a change to note shape, media handling, or status recording is made in exactly one place.
14. As a **maintainer**, I want to test the review state machine without a running Anki or a CLI runner, so that the core logic is verified in fast unit tests.
15. As a **maintainer**, I want a fake Anki client I can inject in both CLI and web tests, so that I exercise the real submission path against a double.
16. As a **maintainer**, I want golden tests pinning the exact rendered Anki fields, so that removing `to_anki_note()` cannot silently change card output.
17. As a **maintainer**, I want card files written atomically, so that a crash mid-save cannot corrupt a review file.
18. As a **maintainer editing an already-added card**, I want the system to refuse (or clearly gate) the edit, so that the JSON never silently diverges from the real Anki note.
19. As a **future TypeScript migrator**, I want the review and submission contracts and their tests expressed language-neutrally, so that they become the acceptance criteria for a TS port.
20. As a **future TypeScript migrator**, I want one shared schema to drive frontend, backend, files, and validation, so that the card shape and its rules stop being redefined per language.

## Implementation Decisions

### A. Core arc — structural, behavior-preserving

- **A1. Module names.** `ReviewSession` (matches the CLI `review` verb and the frontend `useReviewSession`); the submission module is `anki_notes`. These become domain terms (see G3).
- **A2. Both adapters in one branch.** The CLI and the web backend are migrated together; a CLI-only change would preserve the very drift this removes.
- **A3. Remove `to_anki_note()` outright.** No supported public Python API depends on it; all callers are in-repo and migrate in the same change. No deprecated shim.
- **A4. Rendering leaves `Flashcard` entirely.** `convert_newlines_to_html` moves into `anki_notes` alongside `render_anki_note`, so no rendering logic remains on the dataclass or in `schema.py`.
- **A5. `render_anki_note` is byte-identical to today's output.** Same `<br>` newline handling, image-before-`---`-separator ordering, and the same *unescaped* front/back/context (only image filenames escaped). A structural refactor must not reinterpret existing card content (light HTML, MathJax `\( \)`). Guarded by golden tests (see Testing) and tracked by a follow-up escaping decision (F below).
- **A6. Per-call client injection.** `approve()` takes the client as an argument; load/edit/skip/reset/counts are offline and need no client, keeping the session cheap to construct in tests.
- **A7. Web never auto-starts Anki.** Launching a GUI process from an HTTP handler is wrong for a headless deployment. The CLI's interactive auto-start (`ensure_anki_running`) stays; this CLI/web difference is intentional. (This preserves current web behavior.)
- **A8. Read-only CLI commands unchanged.** `find`, `delete`, and diagnostics keep `get_client()`; they are not on the submission/review seam, so injecting them adds noise without test value now.

### B. Ratified interfaces (decision-encoding snippets)

These signatures encode decisions; file paths are illustrative and may change.

```python
class AnkiNote(TypedDict):
    deckName: str
    modelName: str
    fields: dict[str, str]
    tags: list[str]

class NoteClient(MediaStore, Protocol):        # media upload + single-note add
    def add_note(self, deck_name: str, model_name: str,
                 fields: dict[str, str], tags: list[str] | None = None) -> int: ...

class BatchNoteClient(NoteClient, Protocol):   # adds only batch capability
    # param typed list[dict[str, Any]] (not list[AnkiNote]) to match the real
    # AnkiClient under list invariance — see B5
    def add_notes_batch(self, notes: list[dict[str, Any]]) -> list[int | None]: ...

def render_anki_note(card: Flashcard) -> AnkiNote: ...              # pure, compat-preserving
def add_card_to_anki(client: NoteClient, card: Flashcard, *,
                     deck_override: str | None = None) -> int: ...  # upload + render + add
def add_cards_to_anki(client: BatchNoteClient, cards: Sequence[Flashcard], *,
                      deck_override: str | None = None) -> list[int | None]: ...

class ReviewStateError(ValueError):
    """A requested transition violates the persisted review state."""

class ReviewSession:
    @classmethod
    def load(cls, path: str | Path) -> "ReviewSession": ...
    def card(self, index: int) -> Flashcard: ...
    def pending_indices(self) -> tuple[int, ...]: ...
    def counts(self) -> ReviewCounts: ...          # added / skipped / pending
    def reset(self) -> None: ...
    def edit(self, index: int, *, front=None, back=None,
             context=None, tags=None, images=None) -> Flashcard: ...
    def skip(self, index: int) -> Flashcard: ...
    def approve(self, index: int, client: NoteClient, *,
                deck_override: str | None = None) -> Flashcard: ...
    def submit_all(self, client: BatchNoteClient, *,          # batch add for CLI `add`
                   deck_override: str | None = None) -> list[int | None]: ...

def get_anki_client() -> AnkiClient: ...           # shared FastAPI dependency
AnkiDependency = Annotated[NoteClient, Depends(get_anki_client)]
```

- **B1.** `render_anki_note` returns a typed `AnkiNote`, not `dict[str, Any]` — the canonical note shape lives in one place and is not reassembled by callers or re-string-indexed.
- **B2.** The seam is split: `NoteClient` requires only media + `add_note`; `BatchNoteClient` adds `add_notes_batch`. Single-note consumers (review `approve`, `quick`) do not depend on batch.
- **B3.** `deck_override` is a keyword on `approve`/`add_card_to_anki`/`add_cards_to_anki`, not an adapter-side mutation of `card.deck`. The effective deck is submitted and persisted only after Anki returns an id.
- **B4.** Submission functions never mutate review state or write files; the `ReviewSession` owns state and persistence.
- **B5.** `render_anki_note` returns the precise `AnkiNote` TypedDict, but `BatchNoteClient.add_notes_batch` is typed `list[dict[str, Any]]` to match the concrete `AnkiClient`. `list[AnkiNote]` is not assignable to `list[dict[str, Any]]` under **list invariance**, so the seam speaks the client's type; the single `add_cards_to_anki` call bridges it with an explicit `cast`. (`submit_all` lives on `ReviewSession`, not in the ratified snippet above, because batch status-marking is review state and belongs with the other transitions.)

### C. Review state machine

Transitions the `ReviewSession` enforces:

| From | Action | To | Notes |
|------|--------|----|-------|
| `pending` | approve | `added` | submits to Anki; records `anki_id`, `added_at`; persists |
| `pending` | skip | `skipped` | persists |
| `pending` | edit | `pending` | applies non-`None` fields; persists |
| `added` (with `anki_id`) | approve | `added` | **no-op**, no Anki call (idempotent) |
| `skipped` | skip | `skipped` | no-op |
| `skipped` | approve | `added` | allowed: reconsidering a skipped card |
| `added` | edit | — | **`ReviewStateError`** (see F3) |
| `added` (no `anki_id`) | approve | — | invalid persisted state, not blind resubmission |

- **C1. Approval idempotency, precisely.** A card persisted as `added` with a non-`None` `anki_id` returns unchanged with no Anki call. This is *repeat-safe after a recorded success* — **not** exactly-once across a crash between Anki accepting the note and the file save (see Further Notes).
- **C2. Error semantics.** `ValueError`/`AnkiConnectError` during `approve` propagate with review state unchanged and unpersisted, so the caller reports and retries.
- **C3. Bounds & transitions map to HTTP.** Out-of-range index → `IndexError` → 404; `ReviewStateError` → 409; invalid payload/media → 400; unreachable Anki → 503; unexpected persistence failure → 500.

### D. Persistence & concurrency

- **D1. Atomic saves.** `save_cards_to_json` writes to a temp file (flush + `fsync`) and atomically `Path.replace`s it over the target, so an interrupted save cannot corrupt the review file. (This hardens the shared function; all writers benefit.)
- **D2. In-process per-file lock.** A process-local lock keyed by the resolved file path is held across *load → transition → save* for approval in the web adapter, so two concurrent `approve` requests cannot both observe `pending` and create two notes.
- **D3. Multi-process writers unsupported.** Cross-process safety (OS file lock) is explicitly out of scope and documented as a limitation.

### E. Web wiring

- **E1.** One shared `get_anki_client` dependency; every Anki-backed route declares it. The duplicate route-local factory in `routes/anki.py` is removed.
- **E2.** Card-file routes load a `ReviewSession`, call one transition, translate its domain exceptions to HTTP, and never construct `AnkiClient`, mutate card state, or write JSON directly.
- **E3.** Card routes doing synchronous file/HTTP work become ordinary `def` handlers (run in FastAPI's threadpool) rather than `async def` blocking the event loop — consistent with the per-file lock under real thread concurrency.

### F. Correctness decisions surfaced by grilling — **behavior changes, confirmed for this arc**

These change existing behavior and were **confirmed by the owner for inclusion** in this arc (2026-07-12). Each is marked (CHANGE) with its trade-off.

- **F1. Batch `add` records outcomes (CHANGE — confirmed).** Today `add` never writes the file. Decision: mark cards accepted by `add_notes_batch` as `added` (with `anki_id`/`added_at`), leave `None`-result cards `pending`, and save atomically. Rationale: `status` describes real submission state, not whether a review dialog was used. Side effect: `add` now writes to its input file.
- **F2. `reset()` requeues skipped only (CHANGE — confirmed).** Today `--reset` sets *all* cards to `pending` and clears `anki_id`/`added_at`, which lets re-approval create **duplicate Anki notes**. Decision: `reset()` requeues `skipped → pending` and leaves `added` cards linked. Truly re-adding an added card (deleting the old Anki note first) is out of scope. Side effect: `--reset` no longer wipes `added` cards.
- **F3. Edit of an `added` card is refused (CHANGE — confirmed).** Today the web `update` route edits any card, silently diverging the JSON from the real Anki note. Decision: `edit` on an `added` card raises `ReviewStateError` (409). Alternative kept on the table for a future change: allow it and also update the Anki note via `updateNoteFields` (larger scope, deferred).
- **F4. Escaping policy follow-up (NO change now).** The current unescaped front/back/context is preserved byte-identically. `docs/adr/0001-card-content-trust-and-escaping.md` (written in this arc) records the trusted-local-input assumption, the deliberate HTML/MathJax passthrough over injection-safety, and the requirement that any future shared/web-facing rendering surface do its own escaping. No rendering change in this arc.

### G. Process

- **G1. Two green commits + a docs commit**, in dependency order; "3 → 2 → 1" is not licence to leave a commit with broken callers.
  - **Commit 1 — seam + primitive:** `anki_notes` (`AnkiNote`, `NoteClient`, `BatchNoteClient`, `render_anki_note`, `add_card_to_anki`, `add_cards_to_anki`), shared `get_anki_client` dependency, `FakeAnkiClient`; migrate `quick`, `add`, web `add_card`; remove `to_anki_note`; move `convert_newlines_to_html`; add golden + submission tests. Tests green.
  - **Commit 2 — Review Session:** `ReviewSession` (+ `ReviewStateError`, `ReviewCounts`, `submit_all`, atomic save, per-file `locked_session`); rewire CLI `review` + `add` and web `approve`/`skip`/`update`/`get_cards`/`list_card_files`; land F1/F2/F3; add state-machine, web-route, and CliRunner smoke tests. Tests green. (CLI `add` was migrated to the primitive in commit 1 preserving old write-free behaviour, then to `submit_all` here for F1.)
  - **Commit 3 — docs:** this spec, `CONTEXT.md` glossary, and `docs/adr/0001-card-content-trust-and-escaping.md`.
- **G2. Spec is authoritative and local** under `docs/specs/`; a thin GitHub issue may link to it to track rollout/migration, not duplicate it.
- **G3. Seed `CONTEXT.md`** with the durable, language-neutral terms: *Review Session*, *Anki submission*, *persisted-added idempotency*, *NoteClient seam*.

## Testing Decisions

A good test here asserts **external behavior across the seam**, not internals: it drives a `ReviewSession` or a route with a `FakeAnkiClient` and a temp file, then asserts persisted state, returned cards, and what the fake received — never private helpers.

- **T1. Submission unit tests** (`anki_notes`): `render_anki_note` golden output for back/context, image-before-context, and deck/model/tags; `add_card_to_anki` uploads media then adds with the rendered fields and returns the id; `deck_override` applied; invalid image → `ValueError`; `add_cards_to_anki` de-dupes media and returns one positional result per card including `None` rejections.
- **T2. State-machine unit tests** (`ReviewSession`): approve persists `added`/`anki_id`/`added_at`; approve idempotent (no second Anki call); approve failure leaves `pending` and unpersisted; skip/edit/reset semantics per the transition table; `reset` requeues skipped only; edit-of-added raises `ReviewStateError`; out-of-range → `IndexError`; `counts`.
- **T3. Web route tests** by calling the plain `def` route handlers directly with a `FakeAnkiClient` and `CARDS_DIR` monkeypatched to `tmp_path` — no `TestClient`/httpx dependency, since making the routes `def` with an injected client makes them ordinary callables: real `approve` happy path (fake receives the note, file marked `added`), error translation (400/404/409), and count reporting.
- **T4. CLI smoke test** via `CliRunner`: a scripted `review` approval end-to-end, because the mid-migration WIP proved unit tests alone miss broken CLI wiring (removed methods, missing imports).
- **T5. Fake capabilities.** `FakeAnkiClient` records notes/media and returns synthetic ids; supports single-add failure, configurable per-entry batch rejection (`None`), and preferably media-upload failure — enough to test ordering, partial success, and untouched-state-on-error.
- **Prior art:** the existing `MediaStore` Protocol + `RecordingMediaStore` in `test_media.py` is the model this follows.

## Commit-by-commit acceptance

Each commit must leave `uv run pytest` and `prek run --all-files` green. Commit 1 removes `to_anki_note` only once every caller and the schema tests are migrated; the golden tests land in the same commit as the removal.

## Out of Scope

- **Candidate 4** — a first-class project-paths / filesystem-layout module. `CARDS_DIR` stays; tests monkeypatch it.
- **Candidate 5** — unifying the three card-shape definitions (dataclass / Pydantic / TS). Deferred to the TS migration (one shared schema).
- **Candidate 6** — unifying the two renderers (Anki HTML vs React DOM). They are different output adapters by design; only a shared content/escaping *policy* could unify, which depends on F4.
- **Multi-process / cross-process file locking**, media-orphan cleanup, and exactly-once submission across crashes.
- **The TypeScript migration itself** — this arc only makes its contract explicit and portable.

## TypeScript migration (language-neutral contract)

The owner is weighing a full TS rebuild for unified FE/BE types. Decision: **do this bounded Python arc now and keep its contract and tests language-neutral**, so they become acceptance criteria for a port — not sunk cost, provided the arc does not expand into Python-side schema generation, renderer unification, path infrastructure, or framework cleanup.

- **Ports cleanly:** `ReviewSession` → a TS domain service; `anki_notes` → pure render/submit functions; `NoteClient`/`BatchNoteClient` → structural TS interfaces; `FakeAnkiClient` → an in-memory test implementation; the transition table and failure semantics → unchanged.
- **Does not port:** Click, dataclasses, Pydantic, FastAPI DI, synchronous `Path` I/O. The CLI should be **re-implemented in TS**, not deprecated in favor of the web UI.
- **Migration shape:** incremental, **contracts first**. Establish a shared **Zod** package (the single source of truth for JSON files, backend inputs, API responses, and React types — this is the headline benefit and the reason not to pursue Candidate 5 in Python). Then replace the backend behind the existing `/api` contract, keep React, and finally port the CLI. AnkiConnect is plain HTTP+JSON and trivial to port; generation, subprocess/tmux orchestration, document extraction, and the agent SDK argue against a big-bang rewrite.
- **Caveat:** TS unifies schemas only if frontend, backend, files, and tests import the *same* package; and it does **not** make React rendering and Anki HTML serialization identical — Candidate 6's shared render/escaping policy is still required.

## Further Notes — risks & known limitations

- **Idempotency is repeat-safe, not exactly-once.** If Anki accepts a note but the response or the subsequent save fails, the file cannot prove whether submission occurred; a retry may duplicate. Documented, not solved here.
- **Media upload is a separate side effect.** A failed `add_note` after a successful media upload leaves orphaned media in Anki's collection (deduped/reused, low harm). Not cleaned up.
- **Batch add is not transactional.** Some notes may be accepted while others return `None`; a crash before persistence loses the returned ids. Mitigated by persisting immediately after the batch response.
- **`counts()` ignores unknown status strings** rather than rejecting malformed state; acceptable for now.
- **Shipped as two green commits** (`8f938c0`, `424a41e`). The mid-migration WIP that still referenced the removed `to_anki_note` was completed per the commit plan, not shipped as-is; each commit lands green on `uv run pytest` and `prek run`.
