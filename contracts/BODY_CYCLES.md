# Body Cycles Contract — `[[BODY_CYCLES]]`

**Status:** 🚧 **Draft / proposal — consumer not yet written** · **Version:** 0 (unstable) · **Last updated:** 2026-07-25

> **This contract is not implemented.** Unlike `MEMORY_CONTRACT.md`,
> `WORLD_FORGE_SYNC.md`, and `DICE_ORACLE.md` — each of which documents a seam
> the `world-forge` / `npc-memory` extensions **already read** — nothing consumes
> `[[BODY_CYCLES]]` today. It is written down so the producer and consumer sides
> can be designed against one shape instead of two.
>
> **Producers must not emit a `[[BODY_CYCLES]]` carrier yet**, and no World-Forge
> agent spec references this document. It becomes version 1, and binding on
> producers, only after the Scene Tracker's supplementary-state support lands.

This document proposes a **body cycles** channel between the World-Forge producer
pipeline and the `world-forge` extension's Scene Tracker (consumer): recurring
body states — a menstrual cycle, a species' estrus, a lycanthrope's lunar turn —
**tracked by the Scene Tracker as supplementary per-chat state**, seeded once from
the world.

| Side | Component | Repo / path |
| --- | --- | --- |
| **Producer** | World-Forge agent pipeline (Architect, Compiler) | [World-Forge](https://github.com/AndreiNicu/World-Forge) |
| **Consumer** | `world-forge` extension — Scene Tracker, supplementary state | `public/scripts/extensions/world-forge/` — **not yet written** |

---

## 1. Purpose and scope

### 1.1 The problem

A cycle is **state that advances with in-world time**. World Forge has nowhere to
put that: its three tiers are permanent world truth (Tier 1), permanent character
truth (Tier 2), and arc-or-sandbox narrative state (Tier 3). A cycle is none of
them — it is not permanent, and it advances with the *calendar* rather than with
the *story*.

### 1.2 The Scene Tracker owns the state; the world only seeds it

Two candidate owners were rejected before this design.

**The model cannot own it.** The cheapest implementation states the parameters in
a lorebook (`length 28, day 1 was story day 3`) and lets the model compute the
phase from an injected `Day 47`. Language models are unreliable at sustained
modular arithmetic over a running counter, and the failure is silent and
self-compounding: a character menstruates on day 47 and again on day 51, nothing
notices, and the world asserts a physical state it cannot maintain. A world that
tracks nothing is coherent; one that tracks wrongly is not.

**The producer cannot own it either.** A world file is authored once and then
played for months across many chats. Anything that advances per-chat — a current
cycle day, a suppression that began when a character became pregnant in *this*
playthrough — is chat state, not world data, and there is no coherent value for
the producer to write.

So the Scene Tracker owns it, alongside the state it already tracks by default
(health, location, clothing, mood). A cycle is **supplementary tracked state**:
world-specific, opt-in, and advanced by the tracker as in-world days pass. The
tracker computes deterministically, persists per chat, and exposes the value to
the user for correction.

**The world's only job is to supply a starting point and some behavioral
indices.** That is what this carrier is, and it is why it is a *seed* — read once
onto a pristine scene record, exactly like `[[WORLD_CALENDAR]]`
(`WORLD_FORGE_SYNC.md` §5.1) — rather than a payload re-read and re-derived every
turn.

### 1.3 Not just menstruation

The carrier is deliberately specified as **generic recurring body state** with
author-defined phases, not as a menstrual-cycle feature with a fixed
follicular/ovulatory/luteal vocabulary. Two reasons:

- **Fantasy and non-human worlds.** A species' estrus, a lycanthrope's lunar
  turn, a magically-imposed rhythm, and a fictional biology that does not match
  human physiology all fit the same mechanism.
- **The consumer stays simple.** Author-defined phases mean the tracker walks a
  list and advances a counter. It needs no domain knowledge, and no contract
  revision when a world wants a phase vocabulary nobody anticipated.

### 1.4 What the producer supplies

Exactly two things, both authored at world-build time and both stable across
every chat in that world:

1. **The shape and the starting point** — the phase list with durations, and
   which phase the character is in when the roleplay begins.
2. **Terse per-phase behavioral indices** — one line per phase, enough to color
   behavior on the turns the tracker injects it.

Everything else is runtime: the current day, advancement, suppression,
corrections. The producer never models any of it.

> **Why the indices live in the carrier rather than only in the lorebook.** The
> tidier split would put *state* in the carrier and *behavior* in a Tier 2 entry
> keyed on the phase name, letting the injected state line fire the authored
> substrate. That may work, but it rests on an assumption this draft cannot
> verify: that extension-injected text lands inside SillyTavern's world-info scan
> buffer. If it does not, the keyed entry silently never fires and the substrate
> is authored but never reached — the exact failure mode the pipeline works
> hardest to avoid.
>
> A terse index in the carrier is therefore the **floor**: it always reaches the
> model, costs one line, and depends on no scan behavior. Richer per-phase
> substrate can still be authored in Tier 2, and if keyword firing does work it
> composes on top. Floor in the carrier, depth in the lorebook — the same
> relationship the compact roster stat blocks have with organic enrichment.

---

## 2. The carrier: one `[[BODY_CYCLES]]` world-info entry

One world-level World Info entry whose `comment` contains the marker token
`[[BODY_CYCLES]]` (mirroring `[[WORLD_CALENDAR]]` and `[[DICE_TABLES]]`); its
`content` is a single JSON object (§3). At most one per world — if several are
present, the first returned by the consumer's sorted-entries read wins.

> **Carrier flags — same load-bearing rule as `[[WORLD_CALENDAR]]`
> (`WORLD_FORGE_SYNC.md` §5.2) and `[[DICE_TABLES]]` (`DICE_ORACLE.md` §2).** The
> consumer reads candidate entries from `getSortedEntries()` and **rejects any
> with `disable: true`**. The entry MUST therefore be **enabled**
> (`disable: false`) and kept **inert** so it never reaches the prompt:
> `key: []` and `constant: false`. An entry emitted `disable: true` is silently
> skipped and the world seeds nothing.

**Seeding semantics — identical to `[[WORLD_CALENDAR]]`.** The carrier is read
when a chat's scene record is **pristine**, and never again. Hand-set or
tracker-advanced values are never clobbered. A user forty days into a playthrough
who has corrected a phase by hand keeps their state; re-importing the world
changes nothing.

---

## 3. Payload

```jsonc
{
  "schema": 1,
  "cycles": [
    {
      "id": "anna_larsson",       // stable slug — same id space as MEMORY_CONTRACT §4
      "label": "cycle",           // optional; how the tracker names it in the UI
      "start": "luteal",          // phase name, or an integer cycle day
      "phases": [
        { "name": "menstrual",  "days": 5,
          "note": "Cramping the first two days; short-tempered and does not explain why." },
        { "name": "follicular", "days": 8,
          "note": "Energy returns; the most sociable stretch of her month." },
        { "name": "ovulation",  "days": 3,
          "note": "Appetite up and she knows it; more direct about what she wants." },
        { "name": "luteal",     "days": 12,
          "note": "Sore, tired, wants contact without performance." }
      ]
    }
  ]
}
```

### 3.1 Top level

| Path | Type | Required | Meaning |
| --- | --- | --- | --- |
| `schema` | int | yes | Contract version of this payload. `1` when ratified; `0` while unstable. |
| `cycles` | array | yes | Zero or more per-character cycle definitions. An empty array is valid and identical in effect to no carrier. |

### 3.2 A cycle

| Path | Type | Required | Meaning |
| --- | --- | --- | --- |
| `id` | string | yes | Stable slug identifying whose cycle this is. **Same id space and derivation rule as `MEMORY_CONTRACT.md` §4** — lowercase, non-alphanumerics → `_`, collapsed, trimmed. Reusing that id space is deliberate: one identity convention across all contracts, and a world already shipping an `[[NPC_MANIFEST]]` gets the join for free. |
| `label` | string | no | Human-readable name for this cycle in the tracker UI. Defaults to `"cycle"`. |
| `start` | string \| int | no | Where this character is when the roleplay begins. A **phase name** resolves to the first day of that phase; an **integer** is a 1-indexed cycle day. Omitted ⇒ day 1. |
| `phases` | array | yes | Ordered list of phases, each with a duration. See §3.3. |

### 3.3 Phases

Each phase is `{ "name": string, "days": int ≥ 1, "note": string? }`.

- **Order in the array is the order of the cycle.** The last phase wraps to the
  first.
- **Total cycle length is the sum of `days`** — it is not declared separately.
  Durations rather than day ranges make gaps and overlaps structurally
  impossible, so there is no tiling to validate and no day that can fall outside
  a phase.
- `name` is free text; the consumer never interprets it, only displays and
  injects it.
- `note` is the optional per-phase behavioral index (§1.4). **Keep it to one
  line.** It is injected on every turn the phase is active, so it pays rent
  continuously. Write what colors behavior, not a paragraph of physiology — the
  register rule that governs the Intimacy Architect's embodied baseline applies
  here for the same reason: this text reaches the model's context and the model
  echoes the register it is given.

---

## 4. Consumer behavior (informative — **unimplemented**)

This section describes what the Scene Tracker *would* do. No such code exists; it
is written to make the producer side reviewable.

- **On a pristine scene record**, read the carrier and seed one supplementary
  state per cycle: the character, the phase list, and the current position
  resolved from `start`. Never touch a non-pristine record.
- **Advance** the cycle day as in-world days pass, wrapping after the last phase.
  Ownership of the day counter, the wrap, and persistence is entirely the
  tracker's.
- **Expose it in the UI** alongside the default tracked state (health, location,
  clothing, mood) so the user can see the current phase, correct it, suspend it,
  or turn it off per chat.
- **Inject** a compact line while the state is active — the phase and its note:

  ```
  [Anna Larsson — cycle: luteal (day 21). Sore, tired, wants contact without performance.]
  ```

Injection depth, position, and how supplementary state is filtered by who is in
scene are the tracker's design decisions, not this contract's. The producer emits
the same payload regardless.

---

## 5. Graceful degradation

Absence never errors, matching every other seam in `WORLD_FORGE_SYNC.md`:

- No `[[BODY_CYCLES]]` entry, a disabled entry, unparseable JSON, or an empty
  `cycles` array ⇒ nothing is seeded. Every existing world is unaffected.
- A malformed cycle (missing `id` or `phases`, empty `phases`, a phase with
  `days < 1`) is dropped with a console warning; the remaining cycles still seed.
- A `start` naming a phase that does not exist, or an integer beyond the total
  length, falls back to day 1 rather than erroring.
- A missing `note` simply means nothing extra is injected for that phase.
- An `id` matching no character in the world seeds a state the tracker can show
  and the user can delete. Not an error.
- Unknown fields are ignored. The consumer is forward-compatible on `schema`.
- Because the carrier is seed-only, a world that adds, removes, or edits cycles
  after a chat has started changes nothing in that chat. This is the same
  trade-off `[[WORLD_CALENDAR]]` already makes, and the same remedy applies: the
  user edits the value in the tracker UI.

---

## 6. Producer conformance (World-Forge agents) — **not yet in force**

> Nothing below is binding while this contract is a draft. No agent spec
> references it, and no agent should emit a carrier.

When the consumer lands, the expected producer shape is:

- [ ] (If the world wants cycle support) exactly one `[[BODY_CYCLES]]` entry in
      the **World (Tier 1) lorebook**, **enabled** (`disable: false`) and inert
      (`key: []`, `constant: false`).
- [ ] `id` derived by the `MEMORY_CONTRACT.md` §4 slug rule from the same
      canonical name the NPC manifest uses — never a UID, never a display name.
- [ ] `phases` ordered, each with `days ≥ 1`.
- [ ] Each `note` is one line, written in observable register rather than
      clinical vocabulary.
- [ ] `start` reflects where the character actually is at the world's opening
      moment — an authored dramatic choice, not a default.
- [ ] `tools/validate_export.py` gains a `check_body_cycles` (WARN-only, matching
      `check_world_calendar` / `check_dice_tables`): carrier flags, JSON parse,
      slug validity, non-empty ordered phases, `days ≥ 1`, `start` resolvable.

---

## 7. Deferred by design (v0 → later)

The following are **runtime state owned by the Scene Tracker**, deliberately
absent from this contract's first version. The strategy is to ship the rudimentary
seed, let it stabilize in play, and add producer-side declarations only where
experience shows the world genuinely knows something the tracker cannot.

- **Suppression — pregnancy, contraception, illness, magic, age.** A cycle that
  keeps ticking through a pregnancy is precisely the "tracks wrongly" failure
  §1.2 argues against, so this must be handled — but as **tracker state**, not
  producer data. Suppression begins because of something that happened in *this*
  chat, which a world file cannot know. First version: the user suspends or
  clears the state in the tracker UI. A later version may add a
  producer-declared suppression vocabulary — a named condition the tracker can
  switch into, so a world can ship "pregnancy" as a known state with phases of
  its own. That is a natural extension of this same seed mechanism and should
  reuse it rather than invent a parallel one.
- **Irregularity and variance.** Deterministic regularity is the honest
  simplification for a fiction tool. If play shows it matters, variance belongs
  in the tracker's advancement logic, not in the seed.
- **`{{user}}` cycles.** The producer-side bright line (`{{user}}` reference data
  is never a behavioral mandate) suggests the state may be tracked and a `note`
  may describe what others observe, but nothing may instruct the model on what
  `{{user}}` does. The id space also differs — `MEMORY_CONTRACT.md` treats the
  protagonist as a `persona`, not an `npc` — so `id` needs a rule for that case
  before this is allowed.

### 7.1 One open design question

**Should this be a cycle-specific carrier, or one generic supplementary-state
seed?** The Scene Tracker's supplementary-state slot is explicitly extensible, and
cycles are only its first inhabitant. If several more world-seeded supplementary
states arrive, N carriers is worse than one `[[TRACKED_STATE]]` carrier with a
typed payload.

This draft keeps `[[BODY_CYCLES]]` because generalizing before a second use case
exists would be speculative — the shape of a generic carrier should be derived
from two real cases, not one real and one imagined. **The decision point is the
second supplementary state that wants a world-level seed:** at that moment, prefer
folding both into one generic carrier over adding a third marker token.

---

## 8. Relationship to the other contracts

| Concern | Governed by |
| --- | --- |
| NPC manifest, facets, stable ids, turn tag, scenes registry | `MEMORY_CONTRACT.md` |
| Director-card tag, alias coverage, `</style_contract>`, `[[WORLD_CALENDAR]]` | `WORLD_FORGE_SYNC.md` |
| `[[DICE_TABLES]]` carrier, roll-table payload, dice-oracle injection | `DICE_ORACLE.md` |
| `[[BODY_CYCLES]]` carrier, cycle seed payload | this document (draft) |

All are independently versioned. `[[BODY_CYCLES]]` reuses three existing
conventions on purpose — `[[WORLD_CALENDAR]]`'s enabled-but-inert carrier flags,
its pristine-record seeding semantics, and `MEMORY_CONTRACT.md`'s stable slug id
space — so producers have one rule to remember and consumers one code path to
maintain.

It relates to `[[WORLD_CALENDAR]]` only indirectly: the calendar seeds the day
counter whose advancement moves a cycle along, but the two are independent seeds
and either works without the other.
