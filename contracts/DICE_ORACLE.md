# Dice Oracle Contract — `[[DICE_TABLES]]`

**Status:** Established · **Version:** 2 · **Last updated:** 2026-11-05

> **Shared contract — canonical source of truth:**
> [`AndreiNicu/World-Forge`](https://github.com/AndreiNicu/World-Forge) → `contracts/DICE_ORACLE.md`.
> Copies in other repositories (including the SillyTavern fork) are mirrored
> **read-only**. Do not edit a copy — edit the canonical file, then run the
> contract sync (`scripts/sync-contracts.sh`). A CI drift check keeps every copy
> byte-identical to this canonical version.
>
> **What changed in v2:** procedures gain an optional `mode` (§3.7) that frames
> the resolved facts as either a past **recount** (default) or an **event**
> happening *now*, and an optional `turns` duration (§3.6) that keeps a roll
> armed for N model replies instead of just the next one. Both are additive:
> schema-1 payloads and unaware consumers keep working (no `mode` ⇒ recount, no
> `turns` ⇒ 1).

This document specifies the **dice oracle** channel between the World-Forge
producer pipeline and the `world-forge` extension's Scene Tracker (consumer).

| Side | Component | Repo / path |
| --- | --- | --- |
| **Producer** | World-Forge agent pipeline (Architect, Compiler) | [World-Forge](https://github.com/AndreiNicu/World-Forge) |
| **Consumer** | `world-forge` extension — Scene Tracker **Dice** tab | `public/scripts/extensions/world-forge/` |

---

## 1. Purpose and scope

In sandbox roleplay the narrating model is regularly forced to invent facts it
has no basis for: a **recounted past story** ("do you remember the time we
skated down with Alvin?"), or a **temporary, off-manifest NPC** conjured for
one scene. Left to invent these itself, the model latches onto its patterns —
the same kind of man, the same kind of mishap, the same resolution.

The dice oracle moves those decisions out of the model. **Before** the model
writes, the user rolls against world-authored tables; the resolved facts are
injected as authoritative context; the model narrates *around* fixed points.
The dice decide **what** is true, the model decides the texture.

**Scope (deliberately narrow):**

- **Manual activation only** — the user presses **Roll** in the Scene Tracker's
  Dice tab. There is no automatic trigger.
- **Ephemeral facts** — the roll constrains the next reply, or the next **N**
  replies when a duration is set (§3.6), and is then discarded. Rolled facts are
  **not** canon, are not written to npc-memory, and create no NPC ids.
  (Persisting temp-NPC attributes and clearing them once served is a planned
  future step — see §7.)
- **Two tenses** (§3.7) — a procedure resolves either a **recount** of something
  that already happened (the default) or an **event** that is *about to happen
  now*: the same table machinery, framed to the model as present-tense fact.
- Intended uses: (a) recounts of past events that are not part of the roleplay
  or its memory, told by a named NPC when asked; (b) the rough shape of a
  temporary, unnamed/off-manifest NPC featuring in such a story; (c) a random
  event breaking into the current scene, whose shape the dice fix before the
  model narrates it unfolding.

## 2. The carrier: one `[[DICE_TABLES]]` world-info entry

One world-level World Info entry whose `comment` contains the marker token
`[[DICE_TABLES]]` (mirroring `[[WORLD_CALENDAR]]`); its `content` is a single
JSON object (§3). At most one per world — if several are present, the first
returned by the consumer's sorted-entries read wins.

> **Carrier flags — same load-bearing rule as `[[WORLD_CALENDAR]]`
> (`WORLD_FORGE_SYNC.md` §5.2).** The consumer reads candidate entries from
> `getSortedEntries()` and **rejects any with `disable: true`**. The entry MUST
> therefore be **enabled** (`disable: false`) and kept **inert** so it never
> reaches the prompt: `key: []` and `constant: false`. An entry emitted
> `disable: true` is silently skipped and the world provides no tables.

The payload is read fresh per chat; hand-editing the entry and reloading the
Dice tab is a supported authoring loop.

## 3. Payload

```jsonc
{
  "schema": 2,                          // consumer reads what it knows, ignores the rest
  "framing": "Here is some information regarding this encounter. Treat it as true and narrate accordingly:",
                                        // optional lead-in prepended to the injected facts (§3.5)
  "turns": 1,                           // optional default duration in replies (§3.6); the consumer UI can override
  "pools": {                            // named arrays of strings for "pick" steps
    "man_type": ["broad and heavy", "wiry and restless", "soft-spoken giant"],
    "antics":   ["a paint job that went sideways", "skinny-dipping at dawn"]
  },
  "procedures": [                       // ordered; each appears in the consumer's picker
    {
      "id": "past_fling",               // stable snake_case id, unique in the file
      "label": "Past fling (temp man)", // human label for the picker; falls back to id
      "mode": "recount",                // "recount" (default, past) | "event" (about to happen now) — §3.7
      "framing": "…",                   // optional; overrides payload-level framing (§3.5)
      "turns": 1,                       // optional; overrides payload-level turns (§3.6)
      "steps": [
        { "id": "man",   "label": "The man",   "pick": "man_type" },
        { "id": "antic", "label": "The antic", "pick": "antics" },
        { "id": "valence", "label": "How it ended", "roll": "1d20",
          "outcomes": { "1-7": "bad", "8-14": "mixed", "15-20": "great" },
          "text": { "bad":   "it went wrong / ended in embarrassment",
                    "mixed": "a ridiculous mess, but a fond one",
                    "great": "it turned out genuinely great" } },
        { "id": "trace", "label": "Lasting evidence", "roll": "1d6",
          "outcomes": { "1-2": "yes", "3-6": "no" },
          "when": { "valence": ["bad", "mixed"] } }
      ]
    }
  ]
}
```

### 3.1 Top level

| Path | Type | Required | Meaning |
| --- | --- | --- | --- |
| `schema` | int | yes | Contract version of this payload (currently `2`). The consumer is forward-compatible: it reads the fields it recognizes and ignores the rest. |
| `framing` | string | no | Payload-level lead-in for the injected block (§3.5). |
| `turns` | int | no | Payload-level default injection duration in model replies (§3.6). The consumer clamps it to a sane range and its UI can override per roll. Omitted ⇒ 1. |
| `pools` | object | no | Map of pool name → array of strings. Non-string items are dropped; an empty/missing pool makes steps that reference it no-op (§3.2). |
| `procedures` | array | yes | Ordered list of procedures. A procedure with no valid steps is dropped; a payload with no valid procedures counts as absent (§5). |

A procedure object carries `id` (required, unique snake_case), `label`
(optional picker label, falls back to `id`), an optional `mode` (§3.7, default
`recount`), an optional `framing` (§3.5), an optional `turns` (§3.6), and
`steps` (§3.2).

### 3.2 Steps

Each step is exactly one of two forms, plus common fields:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `id` | string | yes | Stable snake_case id, unique within the procedure. Referenced by `when`. |
| `label` | string | no | Display label for the injected fact line; falls back to `id`. |
| `when` | object | no | Gate (§3.3). If unmet, the step is skipped and records nothing. |

**Pick form** — uniform random selection from an array:

| Field | Type | Meaning |
| --- | --- | --- |
| `pick` | string \| string[] | A pool name from `pools`, or an inline array of strings. Empty/unknown pool ⇒ the step is skipped with a console warning. |

**Roll form** — dice roll mapped to a labelled outcome:

| Field | Type | Meaning |
| --- | --- | --- |
| `roll` | string | `NdM`, `NdM+K`, `NdM-K` (case-insensitive, spaces tolerated), or a bare integer. |
| `outcomes` | object | Map of range → **outcome key**. Range is `"a-b"` (inclusive) or a single `"n"`. First matching entry (in object order) wins. Producers SHOULD cover the roll's full range; a total matching no range skips the step with a console warning. |
| `text` | object | Optional map of outcome key → display phrase. The injected fact shows `text[key]` when present, else the key itself. Keys are what `when` matches (§3.3), so keep them short and stable and put the prose in `text`. |

### 3.3 `when` — conditional steps

`when` is a map of previously-resolved step id → accepted value(s)
(`string` or `string[]`). All entries must match for the step to run.
The compared value is the earlier step's **outcome key** (roll form) or its
**picked string** (pick form). A referenced step that was itself skipped (or
appears later in the list) never matches — order steps so dependencies come
first.

### 3.4 Dice semantics

Rolls are uniform pseudo-random, resolved consumer-side in v1. The formula
grammar matches the `rpg-engine-kit` roller: `NdM` sums N independent 1–M
rolls; an optional `+K`/`-K` modifier is added once. There is no advantage /
disadvantage / exploding-dice syntax in schema 2.

### 3.5 `framing` — the injected lead-in

`framing` is a plain-text line (or lines) the consumer prepends to the rolled
facts inside the injected block, before the `label: value` list. It is how the
**world author**, not the extension, sets the register: "Here is some
information regarding this encounter. Treat it as true and narrate
accordingly:".

- A **procedure**'s `framing` overrides the **payload**-level `framing`.
- When neither is set, the consumer supplies a light built-in default **keyed by
  the procedure's `mode`** (§3.7): a *recount* default that establishes the
  facts as an already-true memory, or an *event* default that establishes them
  as happening **now**, based on the roll. Either way it defers interpretation
  to the world's own system-prompt instructions — it does not dictate tone.
- The intended division of labor: `framing` + the facts say **what is true**;
  the world's standing instructions say **how to tell it**. Keep `framing`
  short and let the world prompt carry the interpretation rules (it can key off
  the `<dice_oracle>` block by name).

### 3.6 `turns` — injection duration

By default a roll shapes only the **next** reply and is then released. `turns`
raises that to **N** consecutive model replies: the resolved facts stay injected
(unchanged — a duration keeps the *same* facts in play, it does not re-roll)
until N replies have been shaped, then they clear.

- Set it at the **payload** level (default for every procedure) and/or per
  **procedure** (overrides the payload default). Omitted ⇒ 1, which reproduces
  the original single-reply behavior.
- It is a **default**, not a lock: the consumer surfaces a duration control the
  player can override for a given roll (§4). The value is a positive integer;
  the consumer clamps it to a sane maximum.
- Duration is counted in the model's *replies*, and swipes/regenerations of the
  same reply do not consume a turn (a swipe retells the same beat). This suits
  an **event** that plays out over a few exchanges as much as a recount whose
  details should stay fixed while it is retold.

### 3.7 `mode` — recount vs. event tense

`mode` sets the **tense** the facts are presented in, which selects the built-in
default `framing` (§3.5) when the world supplies none:

| `mode` | Meaning | Default framing establishes… |
| --- | --- | --- |
| `recount` (default) | Something that **already happened** — a memory, a past story, the fixed shape of a character being recalled. | …the facts as an already-true recollection to narrate around. |
| `event` | Something **about to happen now** — a random event breaking into the current scene. | …the facts as what is happening **now**, based on the roll, to be narrated as it unfolds. |

- Any value other than `event` (including omission) is treated as `recount`, so
  schema-1 payloads and unknown values degrade to the safe past tense.
- `mode` only chooses the default register and the built-in framing. A
  procedure-level or payload-level `framing` still wins over both — a world that
  writes its own lead-in controls the exact wording regardless of `mode`.
- Pairs naturally with `turns` (§3.6): an `event` typically wants a duration > 1
  so the unfolding stays in context while it resolves over a few replies.

---

## 4. Consumer behavior (informative)

How the `world-forge` extension consumes the payload. Producers should not
depend on these details, but they explain what the tables drive.

- **Dice tab** in the Scene Tracker window: a procedure picker, a **duration**
  control (how many upcoming replies to keep the facts armed for, §3.6, seeded
  from the procedure/payload `turns` default), **Roll** and **Clear** buttons,
  and the resolved facts with their dice detail (`1d20 → 12`). Tables load
  lazily when the tab is first opened and re-read when the chat changes.
- **Kept results (stacking)**: each **Roll** *adds* a result to a list rather
  than replacing the previous one, so several can be armed at once (e.g. two
  temporary NPCs plus an unfolding event). Every kept result carries its own
  tense, framing, and duration. The user can **re-roll** a single result in
  place (to try alternatives until they like one), **remove** an individual
  result, or **Clear** all of them.
- **Prompt preview**: the tab shows the exact `<dice_oracle>` text the kept
  results currently inject (after macro substitution) — the same string sent to
  the model — so the author can see precisely what the roll contributes.
- **Injection**: while any result is kept, they are injected together near the
  end of the chat as one system-role `<dice_oracle>` block — each result is its
  own group (its `framing` lead-in, chosen by `mode` (§3.7) when the world
  supplies none, followed by a clean `- label: value` list), groups separated
  by a blank line. The dice math (which formula rolled what) stays in the UI
  panel and is **not** sent to the model.
- **N-reply lifecycle**: a result is armed for **N** replies (its rolled
  duration, §3.6; default 1). Each generation consumes the current reply
  (swipes/regenerations of that reply still see the same facts — a swipe means
  "retell it", not "re-roll history"); sending the following user message spends
  one reply from **every** armed result, and a result is released once its own N
  replies have been shaped (results with different durations expire
  independently). **Clear** disarms everything at any point. N = 1 with a single
  kept result reproduces the original one-exchange behavior.
- **Precedence**: a world `[[DICE_TABLES]]` entry with at least one valid
  procedure **fully replaces** the extension's built-in demo tables (no
  per-procedure merging). Otherwise the built-ins are offered so the feature
  is testable in any world.

## 5. Graceful degradation

Absence never errors, matching every other seam in `WORLD_FORGE_SYNC.md`:

- No `[[DICE_TABLES]]` entry, a disabled entry, unparseable JSON, or zero
  valid procedures ⇒ the Dice tab falls back to the built-in demo tables and
  says so; nothing else changes.
- An invalid procedure or step is dropped individually (console warning); the
  rest of the payload still works.
- A `schema: 1` payload is read unchanged: a missing `mode` resolves to
  `recount` and a missing `turns` to 1, so pre-v2 worlds behave exactly as
  before. An out-of-range or non-integer `turns` is clamped/ignored, not an
  error.
- Worlds and exports that predate this contract are unaffected.

## 6. Producer conformance checklist (World-Forge agents)

- [ ] (If the world wants oracle support) exactly one `[[DICE_TABLES]]` entry
      in the World (Tier 1) lorebook, **enabled** (`disable: false`) + inert
      (`key: []`, `constant: false`), marker verbatim in `comment`.
- [ ] Payload is one JSON object with `schema: 2` and ≥ 1 valid procedure.
- [ ] Every `roll` step's `outcomes` covers the formula's full range.
- [ ] Outcome keys are short and stable; prose lives in `text`.
- [ ] (Optional) a `framing` lead-in sets the register; interpretation rules
      live in the world's system prompt, keyed off the `<dice_oracle>` block.
- [ ] (Optional) set `mode: "event"` for imminent-event tables (default
      `recount`); the consumer picks the matching default framing (§3.7).
- [ ] (Optional) set `turns` (payload or procedure) for a default multi-reply
      duration (§3.6); the player can still override it per roll.
- [ ] `when` only references earlier step ids within the same procedure.
- [ ] Pool names referenced by `pick` exist in `pools` and are non-empty.

### 6.1 Authoring guidance: roll the shape, not the choreography (informative)

The payload is well-formed long before it is *well-authored*. The oracle's whole
premise is the what/how split (§1, §3.5): the dice fix **what is true**, the
model narrates **how it plays out**. Procedures that author past that line — that
roll the blow-by-blow — degrade the runtime in two predictable ways: the model
**recites** the facts like a checklist instead of performing them, and
multi-participant scenes get **serialized** (each participant narrated in turn)
instead of played as one encounter. This is a producer-quality concern, not a
schema rule (nothing here changes the payload shape), but it is the difference
between an oracle that helps and one that flattens the scene:

- **Roll shape and flavor; leave choreography to the model.** Fix the setting,
  the cast (as *traits* — who is there), the *configuration* (how they are
  arranged), the *valence* (how it went), and at most one *signature detail*.
  Do **not** roll positions, act-by-act sequence, per-participant acts, or a
  per-participant finish — those are the model's `how`.
- **One encounter is one procedure.** Individuate multiple participants as gated
  *trait* steps inside a single procedure; never emit a procedure per participant
  or roll one procedure once per participant. Concatenated per-person records are
  injected as separate result groups (§4) and narrate in series.
- **State simultaneity in the fact.** A count outcome > 1 must say so in its
  `text` ("two men, together, at the same time"), paired with one
  encounter-level configuration step and **one** shared outcome — never a
  per-participant climax.
- **Framing fixes register, not order.** For a recount, `framing` should assert
  one continuous scene told in-voice and defer choreography to the model; it must
  never invite a sequence ("narrate the sequence of events", "in order").

## 7. Future direction (informative — not part of schema 2)

Recorded so producer and consumer evolve toward the same place. **"More complex
dice" is not one road — it is three, with sharply different cost and different
relationships to this contract's founding scope (§1: the oracle is an *ephemeral
narrative randomizer*, not a stateful game engine).** Keep them separate; the
oracle's statelessness is a feature, not a limitation to grind away.

### 7.1 Richer randomness (stays inside the oracle)

Additive extensions to *how a value is produced*, all backward-compatible (a
future `schema: 3`, uniform/no-op fallback when absent). None require state, so
none threaten §1:

- **Weighted pools** — non-uniform `pick`, e.g. `[{"value":"…","weight":3}]`
  (a ~one-line consumer change over today's uniform pick; the highest-value
  first step). *(Roll `outcomes` are already weighted by range size, and
  degrees-of-success already work today — `1d20 → {1-9:fail,10-14:partial,
  15-20:success}` — so this gap is pools, not rolls.)*
- **Pick N distinct** — draw several different values from one pool in a step.
- **Richer dice grammar** — advantage/disadvantage (`2d20kh1`), keep/drop
  (`4d6kh3`), exploding dice (`d6!`). Each is a self-contained extension to the
  single `NdM(+/-K)` roll-formula grammar (§3.4); no ripple elsewhere.
- **Derived modifiers** — a roll that adds a value resolved by an earlier step.

### 7.2 Resolution mechanics (partly fits)

- **Skill-check-vs-difficulty and success-counting pools** (roll + threshold →
  outcome; count successes ≥ N). The *resolution* half maps cleanly onto the
  existing `outcomes` model. It stays in the oracle right up to the point it
  needs a **stat modifier** (from a character sheet) or the result must
  **persist** — at which point it has left the oracle for §7.3.

### 7.3 Stateful RPG (a separate subsystem — NOT the oracle)

Character sheets, attributes, HP, inventory, combat, and consequences that
**carry forward** are a different system with its own state and its own roll
log. Bolting them onto the ephemeral oracle would destroy exactly what makes it
safe and simple (no state ⇒ no migration, no memory-contract entanglement, no
corruption). When the RPG layer is built it wants its own home:

- **Server-authoritative rolls** — move the roll behind a server plugin
  (rpg-engine-kit pattern) with a per-chat roll log, so rolls are tamper-proof,
  auditable, and produce statistics. This is the substrate a real RPG layer
  needs; the current client-side oracle is not.
- **A character-state channel** — sheets/stats/HP persisted deliberately (likely
  leaning on npc-memory or a new contract), which §7.2 checks would read from.
  **Now drafted as [`RPG_STATS.md`](./RPG_STATS.md)** (status Draft — neither
  side built): the `[[RPG_STATS]]` carrier with the world's stat system, item
  catalog, starting sheets, and bestiary, keyed by the npc-memory slug ids.
- **Temp NPC resolution & persistence** — resolve the unnamed NPC a story
  conjures ("TOM") to a temporary id, attach the rolled attributes so it stays
  consistent while it matters, then clear it. Meshes with npc-memory's
  slugify-miss path (`WORLD_FORGE_SYNC.md` §3) as the temp-NPC detector. (This
  is the bridge between the oracle and persistent state — the first place §7.1
  randomness meets §7.3 memory.)

Also: **procedure auto-suggest** — the Scene Tracker proposing which procedure
fits the current beat — is an independent UX nicety, orthogonal to all three
tiers.

Each §7.1/§7.2 item is a schema/version bump with the usual graceful fallback;
§7.3 is a distinct design, to be specified on its own when the RPG layer is
actually built — not accreted onto this contract.

## 8. Relationship to the other contracts

| Concern | Governed by |
| --- | --- |
| NPC manifest, facets, ids, turn tag, scenes registry | `MEMORY_CONTRACT.md` |
| Director-card tag, alias coverage, `</style_contract>`, `[[WORLD_CALENDAR]]` | `WORLD_FORGE_SYNC.md` |
| `[[DICE_TABLES]]` carrier, roll-table payload, dice-oracle injection | this document |

The three are independently versioned. The `[[DICE_TABLES]]` carrier reuses
`[[WORLD_CALENDAR]]`'s enabled-but-inert flag convention on purpose — one rule
for producers to remember, one code path for consumers to maintain.
