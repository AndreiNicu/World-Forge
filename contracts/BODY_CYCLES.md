# Body Cycles Contract — `[[BODY_CYCLES]]`

**Status:** 🚧 **Draft / proposal — no consumer exists yet** · **Version:** 0 (unstable) · **Last updated:** 2026-07-25

> **This contract is not implemented.** Unlike `MEMORY_CONTRACT.md`,
> `WORLD_FORGE_SYNC.md`, and `DICE_ORACLE.md` — each of which documents a seam
> the `world-forge` / `npc-memory` extensions **already read** — nothing consumes
> `[[BODY_CYCLES]]` today. It is written down so the producer and consumer sides
> can be designed against one shape instead of two.
>
> **Producers must not emit a `[[BODY_CYCLES]]` carrier yet**, and no World-Forge
> agent spec references this document. Emitting a carrier nothing reads adds
> tokens and a maintenance surface for zero runtime effect. The payload below is
> a **proposal**: expect it to change once someone writes the consumer and
> discovers what the Scene Tracker can actually supply. It becomes version 1, and
> agent specs start pointing at it, only after the consumer side lands.
>
> **Open questions that must be settled before v1 are in §7.** Several of them
> can only be answered by reading the extension's code.

This document proposes a **body cycles** channel between the World-Forge producer
pipeline and the `world-forge` extension's Scene Tracker (consumer): recurring,
date-anchored body states — a menstrual cycle, a species' estrus, a lycanthrope's
lunar turn — derived from the Scene Tracker's day counter and injected as fact.

| Side | Component | Repo / path |
| --- | --- | --- |
| **Producer** | World-Forge agent pipeline (Architect, Compiler) | [World-Forge](https://github.com/AndreiNicu/World-Forge) |
| **Consumer** | `world-forge` extension — Scene Tracker | `public/scripts/extensions/world-forge/` — **not yet written** |

---

## 1. Purpose and scope

### 1.1 The problem

A cycle is **state that advances with in-world time**. World Forge currently has
nowhere to put that. Its three tiers are: Tier 1 permanent world truth, Tier 2
permanent character truth, Tier 3 arc-or-sandbox narrative state. A menstrual
cycle is none of them — it is not permanent, and it does not advance with the
*story*, it advances with the *calendar*.

Authored into a lorebook without a clock, such a state is either static ("Anna
menstruates") — which is meaningless — or it depends on the model to track
elapsed days, which it will not do reliably.

### 1.2 Why the model cannot own this

The obvious cheap implementation is to state the parameters in a lorebook entry
(`cycle length 28, day 1 was story day 3`) and let the model compute the phase
from the Scene Tracker's injected `Day 47`. **This does not work, and shipping it
would be worse than shipping nothing.**

Language models are unreliable at sustained modular arithmetic over a running
counter. The failure is silent and self-compounding: a character menstruates on
day 47 and again on day 51, the model never notices the contradiction, and the
world asserts a physical state it cannot maintain. A world that tracks nothing is
coherent; a world that tracks wrongly is not.

The arithmetic therefore belongs to the consumer, which already owns the day
counter and computes deterministically.

### 1.3 Not just menstruation

The carrier is deliberately specified as **generic recurring body state** with
author-defined phases, not as a menstrual-cycle feature with a fixed
follicular/ovulatory/luteal vocabulary. Two reasons:

- **Fantasy and non-human worlds.** A species' estrus, a lycanthrope's lunar
  turn, a magically-imposed rhythm, and a fictional biology that does not match
  human physiology all fit the same mechanism. Hardcoding one real-world model
  would exclude them for no gain.
- **The consumer stays simple.** Author-defined spans mean the extension does
  modular arithmetic and a range lookup. It needs no domain knowledge, and no
  contract revision when a world wants a phase vocabulary nobody anticipated.

### 1.4 State, not behavior — the division of labor

The carrier injects **what phase it is**, and nothing else. How a character *is*
during that phase — cramps, mood, energy, libido direction, self-consciousness,
what she does about it — is authored substrate and lives in the lorebook, exactly
like every other character truth.

This is the same split the pipeline already draws everywhere: the calendar
carrier supplies the date, not what happens on it; the dice oracle supplies the
resolved fact, not the prose. Keeping behavior out of the carrier also keeps the
per-turn token cost near zero and lets the substrate be revised through the
normal revise pipeline without touching an inert JSON blob.

The intended composition is that the injected phase label **acts as a keyword**
that fires the authored lorebook entry — see §6.

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
> skipped and the world provides no cycles.

Unlike `[[WORLD_CALENDAR]]`, which *seeds* a pristine scene record once, this
carrier is **read continuously** — the phase is recomputed from the current day
counter on every turn. It sets no state of its own and never needs to write back.

---

## 3. Payload

```jsonc
{
  "schema": 1,
  "cycles": [
    {
      "id": "anna_larsson",        // stable slug — same id space as MEMORY_CONTRACT §4
      "label": "cycle",            // optional; how the consumer names it in the UI
      "length": 28,                // days in one full revolution
      "anchorDay": 3,              // story day on which this character is at cycleDay 1
      "phases": [
        { "from": 1,  "to": 5,  "name": "menstrual" },
        { "from": 6,  "to": 13, "name": "follicular" },
        { "from": 14, "to": 16, "name": "ovulation" },
        { "from": 17, "to": 28, "name": "luteal" }
      ],
      "inject": "present"          // "present" | "always" | "never"
    }
  ]
}
```

### 3.1 Top level

| Path | Type | Required | Meaning |
| --- | --- | --- | --- |
| `schema` | int | yes | Contract version of this payload. `1` when this draft is ratified; `0` while unstable. |
| `cycles` | array | yes | Zero or more per-character cycle definitions. An empty array is valid and means "no cycles" — identical in effect to no carrier. |

### 3.2 A cycle

| Path | Type | Required | Meaning |
| --- | --- | --- | --- |
| `id` | string | yes | Stable slug identifying whose cycle this is. **Same id space and derivation rule as `MEMORY_CONTRACT.md` §4** — lowercase, non-alphanumerics → `_`, collapsed, trimmed. Reusing that id space is deliberate: one identity convention across all contracts, and a world that already ships an `[[NPC_MANIFEST]]` gets the join for free. |
| `label` | string | no | Human-readable name for this cycle in the Scene Tracker UI. Defaults to `"cycle"`. |
| `length` | int ≥ 2 | yes | Days in one full revolution. |
| `anchorDay` | int | yes | The **story day** (Scene Tracker day counter) on which this character is at cycle day 1. May be ≤ 0 so a cycle can be mid-revolution at story start. |
| `phases` | array | yes | Named, contiguous spans over `1..length`. See §3.3. |
| `inject` | enum | no | `"present"` (default) — inject only when the character is in scene. `"always"` — inject every turn. `"never"` — track and display in the UI, but never inject (useful when the user wants to know without the model knowing). |

### 3.3 Phases

Each phase is `{ "from": int, "to": int, "name": string }`, 1-indexed and
inclusive, over the range `1..length`.

- Phases **should** tile the whole range without gaps or overlaps. A day not
  covered by any phase yields no phase name (see §5).
- Phase names are free text. The consumer does not interpret them; it matches a
  day to a span and reports the name.
- Order in the array is not significant — the consumer matches by range.

### 3.4 Phase derivation

For story day `D`:

```
cycleDay = ((D - anchorDay) mod length + length) mod length + 1
```

The doubled modulo is required, not decorative: `D < anchorDay` is legal (a
character can be anchored ahead of story start), and a single `%` yields negative
values in JavaScript. The result is always in `1..length`.

The phase is the one whose `from..to` span contains `cycleDay`.

---

## 4. Consumer behavior (informative — **unimplemented**)

This section describes what a consumer *would* do. No such code exists; it is
written to make the producer side reviewable and to give the eventual
implementation a target.

- On each turn, read the current day counter from the scene record. If the Scene
  Tracker has no day set, do nothing — a cycle without a clock has no phase.
- For each cycle in the payload, compute `cycleDay` and the phase name (§3.4).
- Filter by `inject`: `"never"` never injects; `"present"` injects only for
  characters the tracker considers in scene; `"always"` injects unconditionally.
- Inject a short, factual line per surviving cycle — state only, no behavior:

  ```
  [Anna Larsson — cycle day 3 of 28 (menstrual)]
  ```

- Surface the same information in the Scene Tracker UI so the user can see and
  hand-correct it.

**Injection depth and position are an open question** (§7) — they depend on
where the Scene Tracker already injects its date line, which this draft does not
assume.

---

## 5. Graceful degradation

Absence never errors, matching every other seam in `WORLD_FORGE_SYNC.md`:

- No `[[BODY_CYCLES]]` entry, a disabled entry, unparseable JSON, or an empty
  `cycles` array ⇒ nothing is tracked and nothing is injected. Every existing
  world is unaffected.
- No day counter set on the scene record ⇒ no phase is computed. The carrier is
  inert until the user starts tracking days.
- An individual cycle that is malformed (missing `length`, `anchorDay`, or
  `phases`; `length < 2`; empty `phases`) is dropped with a console warning; the
  remaining cycles still work.
- A `cycleDay` falling in no phase span ⇒ the cycle reports the day number with
  no phase name (`cycle day 7 of 28`). Not an error; a world may deliberately
  leave part of a revolution unnamed.
- Unknown fields are ignored. The consumer is forward-compatible on `schema`:
  it reads the fields it recognizes and no-ops on the rest.
- An `id` matching no character in the world is not an error — it simply never
  satisfies the `"present"` filter.

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
- [ ] Phases tile `1..length` with no gaps or overlaps.
- [ ] The carrier contains **no behavioral content** — phase names only. The
      per-phase behavior lives in the character's Tier 2 substrate (§1.4).
- [ ] A keyed Tier 2 lorebook entry exists for each phase whose behavior the
      world actually cares about, keyed on the phase name so the injected state
      line fires it. This composition is what makes the carrier useful; a cycle
      with no authored substrate injects a fact the model does nothing with.
- [ ] `tools/validate_export.py` gains a `check_body_cycles` (WARN-only, matching
      `check_world_calendar` / `check_dice_tables`): carrier flags, JSON parse,
      slug validity, phase tiling, `length ≥ 2`.

---

## 7. Open questions — must be settled before v1

Several of these can only be answered by reading the extension's code, which is
why this contract is a draft rather than a specification.

1. **Does the Scene Tracker expose the day counter in a form an injector can
   read per-turn?** §4 assumes it does. If the counter is only available at seed
   time (as `[[WORLD_CALENDAR]]` uses it), the whole design needs revisiting.
2. **Where does the state line inject** — depth, position, and does it share the
   Scene Tracker's existing date injection or get its own? Sharing is cheaper in
   tokens and probably right, but that depends on code this draft has not read.
3. **Scaling with cast size.** A sandbox world with twenty cyclic NPCs must not
   inject twenty lines per turn. `inject: "present"` is the proposed defense, but
   "in scene" needs a definition the tracker can actually evaluate — and it may
   need a hard cap.
4. **Suppression.** Pregnancy, contraception, illness, magic, and age all stop or
   alter a cycle, and a world that plays those beats needs the cycle to respond.
   Options: a `suspended` flag the user toggles in the UI (simple, manual); a
   `suppressedFrom` day (declarative, but the producer rarely knows it at build
   time); or leaving it entirely to the user turning tracking off. **Unresolved,
   and probably the most consequential open question here** — a cycle that keeps
   ticking through a pregnancy is exactly the "tracks wrongly" failure §1.2
   argues against.
5. **Irregularity.** Real cycles vary by days. Should the contract model
   variance, or is deterministic regularity the honest simplification for a
   fiction tool? This draft assumes the latter.
6. **`{{user}}` cycles.** Can a persona carry one? The producer-side bright line
   (`{{user}}` reference data is never a behavioral mandate) suggests yes for the
   state and no for any behavior — but the id space for personas differs from
   npcs (`MEMORY_CONTRACT.md` treats the protagonist as a `persona`, not an
   `npc`), so the `id` field needs a rule for that case.
7. **Does this warrant a carrier at all,** versus a Scene Tracker UI feature with
   no producer involvement? If users are happy to configure cycles per-chat by
   hand, World Forge need not emit anything and this contract can be dropped. The
   carrier earns its place only if authoring cycles at world-build time is
   materially better than configuring them at play time.

---

## 8. Relationship to the other contracts

| Concern | Governed by |
| --- | --- |
| NPC manifest, facets, stable ids, turn tag, scenes registry | `MEMORY_CONTRACT.md` |
| Director-card tag, alias coverage, `</style_contract>`, `[[WORLD_CALENDAR]]` | `WORLD_FORGE_SYNC.md` |
| `[[DICE_TABLES]]` carrier, roll-table payload, dice-oracle injection | `DICE_ORACLE.md` |
| `[[BODY_CYCLES]]` carrier, cycle payload, phase derivation | this document (draft) |

All are independently versioned. `[[BODY_CYCLES]]` reuses two existing
conventions on purpose — `[[WORLD_CALENDAR]]`'s enabled-but-inert carrier flags
and `MEMORY_CONTRACT.md`'s stable slug id space — so producers have one rule to
remember and consumers have one code path to maintain.

It depends on `[[WORLD_CALENDAR]]` only indirectly: the calendar seeds the day
counter this contract derives from, but a user who sets the day by hand gets
cycles with no calendar carrier present.
