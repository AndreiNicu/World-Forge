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
>
> The design below is **checked against the consumer as it exists today**
> (`AndreiNicu/SillyTavern@release`, `public/scripts/extensions/world-forge/index.js`,
> extension v0.10.1). Where it depends on current consumer behavior, the code is
> cited so a reviewer can confirm rather than take it on faith.

This document proposes a **body cycles** channel between the World-Forge producer
pipeline and the `world-forge` extension's Scene Tracker (consumer): recurring
body states — a menstrual cycle, a species' estrus, a lycanthrope's lunar turn —
**owned by the Scene Tracker as supplementary per-chat state**, seeded once from
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

### 1.2 Who owns what — the model observes, the tracker accumulates

The Scene Tracker already draws exactly the line this contract needs, and a cycle
should sit on the same side of it as the weekday.

**The model supplies observations, one small value at a time.** The scan prompt
asks for a `dayAdvance` — "the number of WHOLE days that pass within these recent
messages" — and the tracker accumulates it (`scene.day += Math.round(dayAdvance)`,
index.js §scan-apply). One bounded integer per scan, from text the model just
read.

**The tracker owns every accumulation and derivation.** The day counter, the
weekday (`weekdayStart` anchor + counter), and the calendar month (`startMonth` /
`startYear` + counter, rolling over by real month lengths, leap years included)
are all derived rather than asked for. The comment on `WEEKDAYS` states the reason
outright: the weekday "stays consistent as the story spans days **without the
model having to track it**."

That is the whole argument, already made by the existing code. Asking the model
for a per-turn delta is fine; asking it to maintain a running modular computation
is not — the failure would be silent and self-compounding, a character
menstruating on day 47 and again on day 51 with nothing to notice. **A world that
tracks nothing is coherent; one that tracks wrongly is not.**

**The producer cannot own it either.** A world file is authored once and played
for months across many chats. Anything that advances per-chat — a current cycle
day, a suppression that began when a character became pregnant in *this*
playthrough — is chat state (`chat_metadata[SCENE_META_KEY]`), not world data,
and there is no coherent value for the producer to write.

So a cycle is **derived like the weekday, from the day counter and an anchor**,
and the world's only job is to supply that anchor plus some behavioral indices.
That is what this carrier is, and it is why it is a *seed* — read once onto a
pristine scene record, exactly like `[[WORLD_CALENDAR]]`
(`maybeSeedCalendarFromWorld`, `WORLD_FORGE_SYNC.md` §5.1).

### 1.3 Not just menstruation

The carrier is deliberately specified as **generic recurring body state** with
author-defined phases, not as a menstrual-cycle feature with a fixed
follicular/ovulatory/luteal vocabulary. Two reasons:

- **Fantasy and non-human worlds.** A species' estrus, a lycanthrope's lunar
  turn, a magically-imposed rhythm, and a fictional biology that does not match
  human physiology all fit the same mechanism.
- **The consumer stays simple.** Author-defined phases mean the tracker walks a
  list and indexes into it. It needs no domain knowledge, and no contract
  revision when a world wants a phase vocabulary nobody anticipated.

### 1.4 What the producer supplies

Exactly two things, both authored at world-build time and both stable across
every chat in that world:

1. **The shape and the anchor** — the phase list with durations, and which cycle
   day the character is on at story day 1.
2. **Terse per-phase behavioral indices** — one line per phase.

Everything else is runtime: the day counter, derivation, suppression,
corrections. The producer never models any of it.

> **Why the indices live in the carrier rather than only in a phase-keyed
> lorebook entry — now verified.** The tidier split would put *state* in the
> carrier and *behavior* in a Tier 2 entry keyed on the phase name, letting the
> injected state line fire the authored substrate as a keyword. **As the consumer
> is currently written, that does not work.**
>
> The Scene Tracker injects through `setExtensionPrompt`, whose fifth parameter
> is the world-info scan flag (`setExtensionPrompt(key, value, position, depth,
> scan = false, role, filter)`, `script.js`). Core only feeds an extension prompt
> into the scan buffer when that flag is set — `if
> (context.extensionPrompts[key]?.scan) buffer.addInject(prompt)`
> (`world-info.js`). The Scene Tracker passes **`false`**
> (`updateSceneExtensionPrompt`), so its block is never scanned and a phase-keyed
> entry would silently never fire: substrate authored but never reached, the
> exact failure the pipeline works hardest to avoid.
>
> It is a one-flag change — the native Author's Note exposes the same thing as a
> user setting (`extension_settings.note.allowWIScan`) — so keyword composition
> could be enabled later. **This contract must not depend on it.** The terse index
> in the carrier is the **floor**: it always reaches the model, costs one line,
> and depends on no scan behavior. Richer per-phase substrate can still be
> authored in Tier 2, and if the flag is ever flipped it composes on top. Floor in
> the carrier, depth in the lorebook.

---

## 2. The carrier: one `[[BODY_CYCLES]]` world-info entry

One world-level World Info entry whose `comment` contains the marker token
`[[BODY_CYCLES]]` (mirroring `[[WORLD_CALENDAR]]` and `[[DICE_TABLES]]`); its
`content` is a single JSON object (§3). At most one per world — if several are
present, the first returned by the consumer's sorted-entries read wins.

> **Carrier flags — same load-bearing rule as `[[WORLD_CALENDAR]]`
> (`WORLD_FORGE_SYNC.md` §5.2) and `[[DICE_TABLES]]` (`DICE_ORACLE.md` §2).** Both
> existing readers filter with `.find(e => e && !e.disable && …)` over
> `getSortedEntries()`, so the entry MUST be **enabled** (`disable: false`) and
> kept **inert** so it never reaches the prompt: `key: []` and `constant: false`.
> An entry emitted `disable: true` is silently skipped and the world seeds
> nothing.

**Seeding semantics — identical to `[[WORLD_CALENDAR]]`.** Read when a chat's
scene record is **pristine**, and never again, so hand-set values are never
clobbered. `maybeSeedCalendarFromWorld` establishes the pattern, including its
re-check of pristineness after the async world-info load and its
`CHAT_CHANGED` binding.

---

## 3. Payload

```jsonc
{
  "schema": 1,
  "cycles": [
    {
      "id": "anna_larsson",       // stable slug — same id space as MEMORY_CONTRACT §4
      "label": "cycle",           // optional; how the tracker names it in the UI
      "startDay": 17,             // cycle day on story day 1 (anchor; cf. weekdayStart)
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
| `id` | string | yes | Stable slug identifying whose cycle this is. **Same id space and derivation rule as `MEMORY_CONTRACT.md` §4** — lowercase, non-alphanumerics → `_`, collapsed, trimmed. The tracker's roster is keyed by display **name** (`ScenePerson.name`), so the consumer resolves slug → name through the same manifest reconciliation the memory channel already performs. |
| `label` | string | no | Human-readable name for this cycle in the tracker UI. Defaults to `"cycle"`. |
| `startDay` | int ≥ 1 | no | **The cycle day this character is on at story day 1** — an anchor, deliberately the same shape as the Scene Tracker's `weekdayStart` ("the weekday Day 1 falls on"). Omitted ⇒ 1. Authoring note: a world that wants "she is mid-luteal when play opens" sets the day that falls there; the producer computes it from the phase list at build time so the consumer never has to resolve names. |
| `phases` | array | yes | Ordered list of phases, each with a duration. See §3.3. |

### 3.3 Phases

Each phase is `{ "name": string, "days": int ≥ 1, "note": string? }`.

- **Order in the array is the order of the cycle.** The last phase wraps to the
  first.
- **Total cycle length is the sum of `days`** — not declared separately.
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

### 3.4 Phase derivation

Given the tracker's day counter `day` (1-indexed; `0` means day tracking is off):

```
length   = sum(phases[].days)
cycleDay = ((day - 1 + startDay - 1) mod length) + 1
```

then walk `phases` accumulating durations until the running total reaches
`cycleDay`; that phase is the current one.

This is **stateless derivation, not stored advancement** — the same shape as the
weekday and the anchored month. Nothing to persist, nothing to drift, and a user
who corrects the day counter gets a corrected cycle for free. `day === 0` ⇒ no
cycle is derived or injected, matching how the tracker already suppresses the
weekday and calendar month when day tracking is off.

---

## 4. Consumer behavior (informative — **unimplemented**)

This section describes what the Scene Tracker *would* do. No such code exists; it
is written to make the producer side reviewable.

- **On a pristine scene record**, read the carrier and store the cycle
  definitions in the scene record — the anchor and phase list, not a current
  position. Never touch a non-pristine record.
- **Derive** the current phase per §3.4 whenever the block is built. No
  advancement code, no counter of its own.
- **Never scan for it.** `ScenePerson`'s existing fields (`health`, `condition`,
  `clothing`, `mood`, `lastLocation`) are populated by asking the model in the
  scan prompt. A cycle is the opposite kind of value: derived, not observed. It
  must not be added to the scan JSON, or the model's guess will overwrite the
  arithmetic — which is the failure §1.2 exists to prevent.
- **Expose it in the UI** next to the per-person fields so the user can see the
  current phase, correct the anchor, suspend it, or turn it off per chat.
- **Inject** a compact line while active — phase and note:

  ```
  [Anna Larsson — cycle: luteal (day 21 of 28). Sore, tired, wants contact without performance.]
  ```

Injection placement is already solved for the block as a whole: the Scene Tracker
injects one assembled block under its own `setExtensionPrompt` key with
user-configurable position, depth, role, and interval. A cycle line is a
contribution to that block, not a new injection point — so this contract
specifies no depth, position, or cadence of its own.

---

## 5. Graceful degradation

Absence never errors, matching every other seam in `WORLD_FORGE_SYNC.md`:

- No `[[BODY_CYCLES]]` entry, a disabled entry, unparseable JSON, or an empty
  `cycles` array ⇒ nothing is seeded. Every existing world is unaffected.
- **`day === 0`** (day tracking off) ⇒ no cycle is derived or injected, even with
  a valid carrier. Cycles are opt-in behind the day counter the user already
  controls.
- A malformed cycle (missing `id` or `phases`, empty `phases`, a phase with
  `days < 1`) is dropped with a console warning; the remaining cycles still seed.
- A `startDay` beyond the total length wraps rather than erroring (the modulo in
  §3.4 handles it); a non-integer or `< 1` value falls back to 1.
- A missing `note` simply means nothing extra is injected for that phase.
- An `id` that resolves to nobody in the world seeds a definition the tracker can
  show and the user can delete. Not an error.
- Unknown fields are ignored. The consumer is forward-compatible on `schema`.
- Because the carrier is seed-only, a world that adds, removes, or edits cycles
  after a chat has started changes nothing in that chat — the same trade-off
  `[[WORLD_CALENDAR]]` already makes, with the same remedy: edit it in the UI.

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
      A world emitting cycles should also emit an `[[NPC_MANIFEST]]`, or the
      consumer has no reliable slug → roster-name join.
- [ ] `phases` ordered, each with `days ≥ 1`.
- [ ] Each `note` is one line, written in observable register rather than
      clinical vocabulary.
- [ ] `startDay` reflects where the character actually is at the world's opening
      moment — an authored dramatic choice, not a default. The producer resolves
      any "starts mid-luteal" intent into the integer at build time.
- [ ] `tools/validate_export.py` gains a `check_body_cycles` (WARN-only, matching
      `check_world_calendar` / `check_dice_tables`): carrier flags, JSON parse,
      slug validity, non-empty ordered phases, `days ≥ 1`, `startDay` in range.

---

## 7. Deferred by design (v0 → later)

The following are **runtime state owned by the Scene Tracker**, deliberately
absent from this contract's first version. The strategy is to ship the rudimentary
seed, let it stabilize in play, and add producer-side declarations only where
experience shows the world genuinely knows something the tracker cannot.

- **Suppression — pregnancy, contraception, illness, magic, age.** A cycle that
  keeps ticking through a pregnancy is precisely the "tracks wrongly" failure
  §1.2 argues against, so this must be handled — but as **tracker state**, not
  producer data. Suppression begins from something that happened in *this* chat,
  which a world file cannot know. Since §3.4 is stateless derivation, suppression
  is the one piece of genuinely *mutable* per-chat cycle state: a suspend flag
  (and later, perhaps, an override phase) stored in the scene record and honored
  ahead of the derivation. First version: the user suspends or clears it in the
  UI. A later version may add a producer-declared suppression vocabulary — a
  named condition with phases of its own, so a world can ship "pregnancy" as a
  known state — which is a natural extension of this same seed mechanism and
  should reuse it rather than grow a parallel one.
- **Irregularity and variance.** Deterministic regularity is the honest
  simplification for a fiction tool. If play shows it matters, variance belongs
  in the tracker's derivation, not in the seed.
- **`{{user}}` cycles.** The producer-side bright line (`{{user}}` reference data
  is never a behavioral mandate) suggests the state may be tracked and a `note`
  may describe what others observe, but nothing may instruct the model on what
  `{{user}}` does. The id space also differs — `MEMORY_CONTRACT.md` treats the
  protagonist as a `persona`, not an `npc`, while the tracker's roster does carry
  a `role: 'user'` person — so `id` needs a rule for that case before this is
  allowed.

### 7.1 One open design question

**Should this be a cycle-specific carrier, or one generic supplementary-state
seed?** The Scene Tracker's per-person record is explicitly extensible (`health`,
`condition`, `clothing`, `mood`, `lastLocation` today), and cycles are only the
first *world-seeded* addition to it. If several more arrive, N carriers is worse
than one `[[TRACKED_STATE]]` carrier with a typed payload.

This draft keeps `[[BODY_CYCLES]]` because generalizing before a second use case
exists would be speculative — a generic shape should be derived from two real
cases, not one real and one imagined. **The decision point is the second
supplementary state that wants a world-level seed:** at that moment, prefer
folding both into one generic carrier over adding a third marker token.

Note the distinction that would govern such a carrier, and that cycles illustrate:
**scanned** state (what the model observes each turn — mood, clothing) and
**derived** state (what the tracker computes from the counter — weekday, month,
cycle) are different kinds of thing. Only derived state needs a world-level seed
at all; scanned state needs nothing from the producer.

---

## 8. Relationship to the other contracts

| Concern | Governed by |
| --- | --- |
| NPC manifest, facets, stable ids, turn tag, scenes registry | `MEMORY_CONTRACT.md` |
| Director-card tag, alias coverage, `</style_contract>`, `[[WORLD_CALENDAR]]` | `WORLD_FORGE_SYNC.md` |
| `[[DICE_TABLES]]` carrier, roll-table payload, dice-oracle injection | `DICE_ORACLE.md` |
| `[[BODY_CYCLES]]` carrier, cycle seed payload | this document (draft) |

All are independently versioned. `[[BODY_CYCLES]]` reuses four existing
conventions on purpose — `[[WORLD_CALENDAR]]`'s enabled-but-inert carrier flags,
its pristine-record seeding, its anchor-plus-counter derivation shape, and
`MEMORY_CONTRACT.md`'s stable slug id space — so producers have one rule to
remember and consumers one code path to maintain.

It depends on `[[WORLD_CALENDAR]]` only indirectly: the calendar seeds the day
counter a cycle derives from, but the two are independent seeds and a user who
sets the day by hand gets cycles with no calendar carrier present.
