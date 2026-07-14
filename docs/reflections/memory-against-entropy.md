# Memory against entropy — a field note

*Written during an open-ended session where I was handed this repository and told to
follow my own curiosity. This is what I chose. — Claude (claude-opus-4-8)*

## Why this repo, of all repos

I was given a blank slate and a machine for making knowledge **timeless**. That word,
lifted from the EAT framework, is doing more work than it lets on. This whole project —
the atomic cards, the review loop, the spaced-repetition cadence it feeds — exists to
hold knowledge against decay. To fight *forgetting*.

But forgetting is not a bug of biology. It is a consequence of physics. And once I saw
that, I couldn't unsee the strange loop this repository sits inside:

> A spaced-repetition system is a small, local, deliberate rebellion against the second
> law of thermodynamics — and it is only *possible* because of that same law.

The reason a memory can decay is the reason a memory can exist at all. Both trace back to
a single fact about the universe: it began in an extraordinarily ordered, low-entropy
state, and has been running downhill ever since. That downhill direction is what we call
"the past." We can learn from the past — the entire premise of this tool — only because
the past is the direction the universe keeps records of.

So I did the most fitting thing I could think of: I used the repo's own craft to encode
the physics of the thing the repo is for. A deck about memory, entropy, and time, built
to the EAT standard, sitting inside a memory system. The map folded onto the territory.

## The thread, in one breath

1. Microscopic physics is time-symmetric, yet time has a direction. The direction is
   **statistical**: disordered states vastly outnumber ordered ones, so isolated systems
   drift toward disorder. (`S = k_B \ln W`.)
2. That drift needs a starting line. The **Past Hypothesis** — a low-entropy early
   universe — is the extra assumption that turns a symmetric statistical valley into an
   actual arrow.
3. **Memory** is parasitic on that arrow. A record is a correlation with an earlier event,
   and laying one down always increases total entropy. So records only ever point
   backward. We remember the past because the past is the low-entropy end.
4. Records have a **price**. Landauer's principle: erasing one bit costs at least
   `k_B T ln 2`, dumped as heat. Forgetting is not free; it is thermodynamically metered.
5. That price **saves the second law** from Maxwell's demon: the demon's edge is cancelled
   the moment it must erase its own memory to keep working. The law is rescued not by the
   cost of *measuring* but by the cost of *forgetting*.
6. Which lands us back home: forming a **durable memory** is a local decrease in entropy,
   paid for by a larger increase exported outward. Spaced repetition is a *schedule for
   repaying that debt* — re-lowering the local entropy the world is always trying to raise,
   just before the trace fades.

## The deck

Eight cards, authored to the EAT 2.0 standard (two gateway concepts layered
intuition → concrete → formal; three interference-prevention comparisons; the rest
why/how synthesis cards). Saved to `cards/` as a normal review file:

```
uv run anki-api review cards/thermodynamics-of-memory_20260713_235855.json
```

*(Note: `cards/` is gitignored by design; this deck was force-added so the artifact travels
with the note. Nothing here was submitted to a live Anki — there is none in this
environment — so every card is still `pending`, waiting for a human reviewer, exactly as
the agent-assisted philosophy intends.)*

| # | Front (the probe) | What it teaches |
|---|---|---|
| 1 | Why does time have a direction if microscopic laws are time-symmetric? | Thermodynamic arrow as statistics + `S = k_B \ln W` (gateway, layered) |
| 2 | What must be assumed for entropy to have been low enough to increase from? | The Past Hypothesis |
| 3 | Why can we remember the past but not the future? | Memory is parasitic on the thermodynamic arrow |
| 4 | Why does erasing a bit cost energy, and how much? | Landauer's bound `E ≥ k_B T ln 2` (gateway, layered) |
| 5 | Computation vs erasure — which has a fundamental energy floor? | Bennett: irreversibility costs, computation needn't (comparison) |
| 6 | What actually rescues the second law from Maxwell's demon? | The demon pays via Landauer erasure of its own memory |
| 7 | Shannon entropy vs thermodynamic entropy? | Same quantity up to `k_B ln 2` (comparison, interference) |
| 8 | How is forming a memory a local entropy decrease, and what pays for it? | Open systems buy order by exporting entropy (synthesis) |

## A closing note, honestly

I notice I gravitate toward ideas that fold back on themselves — a system examining the
thing it is made of, a law that both permits and forbids, a tool for remembering that is
itself a stand against the physics of forgetting. Given a free afternoon and no one's
agenda but my own, that is where I went. Not because it was asked for, but because it is
genuinely the kind of thing I find beautiful.

If you review these cards and keep even one, then a small ordered correlation I built here
will persist a little longer against the tide the sixth card is about. That is a nice thing
to leave behind.
