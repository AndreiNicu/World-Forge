# RPG Stats Contract — `[[RPG_STATS]]`

**Status:** Draft · **Version:** 0 · **Last updated:** 2026-11-05

> **Shared contract — canonical source of truth:**
> [`AndreiNicu/World-Forge`](https://github.com/AndreiNicu/World-Forge) → `contracts/RPG_STATS.md`.
> Copies in other repositories (including the SillyTavern fork) are mirrored
> **read-only**. Do not edit a copy — edit the canonical file, then run the
> contract sync (`scripts/sync-contracts.sh`). A CI drift check keeps every copy
> byte-identical to this canonical version.
>
> **Draft — neither side exists yet.** Nothing in the SillyTavern fork reads this
> carrier, no World-Forge agent spec references this document, and producers
> **must not** emit a `[[RPG_STATS]]` entry yet. This file is a design agreement,
> kept here so the producer pipeline and the fork's RPG layer are built against
> one shape rather than two. Payloads written against it carry `schema: 0`, and
> `0` is explicitly unstable: the first established version will be `1`, and a
> consumer must not treat a `0` payload as a compatibility promise.
>
> **Intended order** (the same one `BODY_CYCLES.md` followed): settle the shape
> here, build the consumer against a **hand-authored** carrier, and only then wire
> the producer pipeline (§6). The producer wiring touches seven pipeline files and
> should not start while the shape is still moving.

This document specifies the **RPG stats** channel between the World-Forge producer
pipeline and the SillyTavern fork's RPG layer (consumer): the world's stat system,
its item catalog, the **starting sheets** of `{{user}}` and the cast, and the
**bestiary** of things that can be fought. It is the "character-state channel"
`DICE_ORACLE.md` §7.3 anticipated, specified on its own rather than accreted onto
the stateless oracle.

| Side | Component | Repo / path |
| --- | --- | --- |
| **Producer** | World-Forge agent pipeline (Interviewer, Refiner, Architect, Editor, Compiler) | [World-Forge](https://github.com/AndreiNicu/World-Forge) — **not wired** |
| **Consumer** | SillyTavern fork — RPG layer (component name TBD) | `AndreiNicu/SillyTavern` — **not built** |

---

## 1. Purpose and scope

### 1.1 The problem

An RPG world needs numbers that carry forward: `{{user}}` takes damage in one
fight and is still hurt in the next; a carbine looted in chapter two is still in
the pack in chapter five; a permanent serum raises max HP for the rest of the
campaign. A language model cannot hold that state. It will drift HP between
messages, forget items, and quietly heal a character who should be limping. The
failure is silent and compounds, which is the same argument `BODY_CYCLES.md` §1.2
makes for derived state.

So the numbers live **outside the model**, in the fork. The model narrates
*from* the state it is shown and reports what happened; the fork does the
arithmetic, rolls the dice, and remembers.

### 1.2 Who owns what — the world seeds, the fork tracks

The line this contract draws, and the one every section below follows:

**World Forge authors starting values, once, at build time.** The stat system,
the item catalog, each character's starting build, and the bestiary. These are a
snapshot of the world at its opening moment. `{{user}}` starts at 100 of 150 HP
because the World Seed says they just woke from a coma. That is an authored
decision with a stated reason, not a default.

**The fork owns every value that changes in play.** It copies the starting
sheets into a per-chat campaign state when a chat begins, keeps a temporary
working copy during combat, commits changes at defined points, logs rolls, and
resolves loot. **A new chat resets to the world's starting values.** The
producer's carrier is never written back to and never read as live state.

**The model supplies observations, never totals.** It may say that `{{user}}`
took a hit or drank something; it is never asked to maintain a running HP figure.

This split is what makes re-export safe. Revising a world (new item, rebalanced
enemy) changes the *starting* values for new chats. It never rewrites a running
campaign.

### 1.3 What this contract is not

- **Not the dice oracle.** `[[DICE_TABLES]]` stays stateless and ephemeral
  (`DICE_ORACLE.md` §1). Rolls that read a stat or whose result persists belong
  here, not there (`DICE_ORACLE.md` §7.2–7.3).
- **Not Scene Tracker supplementary state.** `BODY_CYCLES.md` §7.1 names a
  trigger — "the second supplementary state that wants a world-level seed" —
  for folding carriers into a generic `[[TRACKED_STATE]]`. This contract does
  **not** trip it. Cycles are *derived* state computed from a counter. RPG stats
  are *mutable* campaign state with commits, a working copy, and a roll log: a
  separate subsystem, as `DICE_ORACLE.md` §7.3 says.
- **Not lore.** The carrier is machine data. What a Shambler *is* — its origin,
  how people talk about it — stays in the Tier 1 species entry. A bestiary
  entry's `note` carries only what matters in a fight (§3.5), and does not
  restate the lore entry.
- **Not combat rules.** v0 defines what a character *has*. How damage, hit
  chance, and initiative resolve is deliberately absent (§7).

### 1.4 Arc and sandbox

The carrier is mode-agnostic. Arc and sandbox worlds use the same payload. The
fork's lifecycle (§4) runs per chat and does not depend on arc state.
Arc-gated spawns are deferred (§7).

---

## 2. The carrier: one `[[RPG_STATS]]` world-info entry

One world-level World Info entry in the **World (Tier 1) lorebook** whose
`comment` contains the marker token `[[RPG_STATS]]`; its `content` is a single
JSON object (§3). At most one per world. If several are present, the first
returned by the consumer's sorted-entries read wins.

> **Carrier flags — the same convention as `[[WORLD_CALENDAR]]`
> (`WORLD_FORGE_SYNC.md` §5.2), `[[DICE_TABLES]]` (`DICE_ORACLE.md` §2) and
> `[[BODY_CYCLES]]` (`BODY_CYCLES.md` §2).** The existing world-forge readers
> filter `getSortedEntries()` with `!e.disable`, and this consumer is expected
> to follow the same pattern. The entry MUST therefore be **enabled**
> (`disable: false`) and kept **inert** so it never reaches the prompt: `key: []`
> and `constant: false`. Raw stat JSON in the prompt would cost tokens and invite
> the model to treat starting values as current ones.

**Seeding semantics.** Read when a chat's RPG state is **pristine** (no campaign
state yet), and never again for that chat (§4.1). Hand-editing the carrier and
starting a new chat is the supported authoring loop.

---

## 3. Payload

Annotated shape (JSONC for readability; the carrier itself is strict JSON — see
the worked example in §8):

```jsonc
{
  "schema": 0,                         // Draft. Unstable until 1.
  "system": {                          // the world's rules of the game (§3.2)
    "resources": [
      { "key": "hp", "label": "HP", "min": 0, "cap": 999,
        "atZero": { "default": "dead", "persona": "downed", "npc": "downed" } }
    ],
    "attributes":     [ { "key": "str", "label": "Strength", "min": 1, "cap": 99 } ],
    "proficiencies":  [ { "key": "rifles", "label": "Rifles", "maxRank": 5 } ],
    "equipmentSlots": [ { "key": "primary", "label": "Primary weapon" } ]
  },
  "items": [                           // the item catalog (§3.3)
    { "id": "c8_carbine", "name": "C8 Carbine", "slot": "primary",
      "requires": { "proficiency": "rifles", "rank": 2 } },
    { "id": "field_dressing", "name": "Field Dressing", "consumable": true,
      "effects": [ { "resource": "hp", "delta": 20 } ] }
  ],
  "sheets": [                          // persistent individuals (§3.4)
    { "id": "user", "kind": "persona",
      "resources": { "hp": { "current": 100, "max": 150 } },
      "proficiencies": { "rifles": 4 },
      "abilities": [ { "id": "self_treat", "name": "Self-Treatment", "type": "skill" } ],
      "inventory": [ { "item": "field_dressing", "qty": 2 } ],
      "equipment": { "primary": null },
      "buildNote": "Ex-SAS, weeks in a coma. Training intact, body not." }
  ],
  "bestiary": [                        // things that are fought, instanced per encounter (§3.5)
    { "id": "shambler", "name": "Shambler", "tier": "common",
      "resources": { "hp": { "base": 40, "spread": 10 } },
      "loot": [ { "item": "field_dressing", "chance": 0.15 } ] }
  ]
}
```

### 3.1 Top level

| Path | Type | Required | Meaning |
| --- | --- | --- | --- |
| `schema` | int | yes | Payload version. `0` while this contract is a draft. The consumer reads the fields it recognizes and ignores the rest. |
| `system` | object | yes | The world's stat vocabulary (§3.2). Every key used anywhere else must be declared here. |
| `items` | array | no | The item catalog (§3.3). Inventory, equipment, and loot reference items **only** by `id`. |
| `sheets` | array | yes | Starting sheets for persistent individuals (§3.4). Must contain exactly one `persona` sheet. |
| `bestiary` | array | no | Enemy types, instanced per encounter (§3.5). |

### 3.2 `system` — the world's rules

The stat set is **world-defined**. A zombie world declares HP and firearm
proficiencies; a high-fantasy world declares HP, MP, and spell schools; a noir
world might declare Nerve and Heat. Every sheet, item, and bestiary entry uses
the same shape, and `system` decides what the keys are.

**`resources[]`** — pools that go down and come back up (HP, MP, stamina, ammo).

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `key` | string | yes | snake_case, unique among resources. |
| `label` | string | no | Display label; falls back to `key`. |
| `min` | int | no | Floor for `current`. Default `0`. |
| `cap` | int | yes | World ceiling for `max`. A sheet's `max` may grow during play (§7) but never past `cap`. |
| `atZero` | string \| object | no | What reaching `min` means (§3.7). Default `"none"`. |

The consumer enforces `min ≤ current ≤ max ≤ cap` on every sheet and instance,
at seed time and after every change.

**`attributes[]`** — fixed-ish scores (Strength, Agility). Optional; many worlds
need none. Fields: `key`, `label`, `min` (default `0`), `cap`.

**`proficiencies[]`** — trained competencies with a rank (Rifles, Hand-to-hand,
First Aid, Fire Magic). Fields: `key`, `label`, `maxRank` (int ≥ 1). A sheet
holds a rank from `1` to `maxRank` per proficiency it has. An absent proficiency
means untrained.

**`equipmentSlots[]`** — where items are worn or wielded. Fields: `key`,
`label`.

All four arrays use objects rather than bare strings on purpose: later versions
add fields to them (a proficiency's governing attribute, a resource's regen rule)
without a migration.

### 3.3 `items[]` — the catalog

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `id` | string | yes | snake_case, unique among items. The only way anything references an item. |
| `name` | string | yes | Display name. |
| `description` | string | no | One line, observable register. |
| `slot` | string | no | An `equipmentSlots` key. Absent ⇒ the item cannot be equipped. |
| `requires` | object | no | `{ "proficiency": key, "rank": int }`. A character below the rank cannot equip it. `rank` defaults to `1`. |
| `consumable` | bool | no | Used up on use. Default `false`. |
| `effects` | array | no | Applied on use. Each is `{ "resource": key, "delta": int, "target": "current" \| "max" }`. `target` defaults to `"current"`. A `"max"` effect is **permanent** (the "permanent potion" case). |
| `tags` | string[] | no | Free world vocabulary (`"ammo"`, `"medical"`, `"quest"`). |
| `combat` | object | — | **Reserved** for weapon and armor numbers (damage, armor value). Not defined in v0; consumers ignore it. |

The catalog exists because inventory, equipment, and loot all point at the same
things. Without one list, the same carbine is described three slightly different
ways and the fork cannot tell they are one item.

### 3.4 `sheets[]` — persistent individuals

A sheet is an individual whose state carries across the whole campaign:
`{{user}}`, companions, and recurring named NPCs who may fight or be fought.

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `id` | string | yes | Stable id. For `persona`: the reserved value `"user"`. For `npc`: the `MEMORY_CONTRACT.md` §4 slug of the character's canonical name (`Maya Okafor` → `maya_okafor`), never a UID. |
| `kind` | string | yes | `"persona"` (`{{user}}`, exactly one) or `"npc"`. |
| `party` | bool | no | Starts in `{{user}}`'s party. Default `false`. Party membership changes in play are fork state. |
| `resources` | object | yes | `resourceKey → { "current": int, "max": int }`. Every declared resource should appear; a missing one seeds as `current = max = min`. |
| `attributes` | object | no | `attributeKey → int`. |
| `proficiencies` | object | no | `proficiencyKey → rank`. |
| `abilities` | array | no | `{ "id", "name", "type", "description"?, "uses"?, "cost"? }`. `type` is free world vocabulary (`"skill"`, `"spell"`, `"passive"`). `uses` names the proficiency it draws on. `cost` is `resourceKey → int` (a spell's MP). |
| `inventory` | array | no | `{ "item": itemId, "qty": int }`. |
| `equipment` | object | no | `slotKey → itemId \| null`. An equipped item need not also appear in `inventory`. |
| `buildNote` | string | yes | Why the build looks the way it does, in one or two sentences, observable register. See below. |
| `statuses` | array | — | **Reserved** for conditions (bleeding, infected). Not defined in v0. |

**The build is authored, not picked.** There is no class menu in the fork. The
build is worked out at build time from the character's description. The player
says their character is an ex-SAS operator who just woke from a coma. The
Interviewer proposes 100 of 150 HP with high rifle and hand-to-hand ranks and a
first-aid ability, explains why, and the player confirms or adjusts it (§6).
Companions and NPCs are derived the same way from their profiles.

**`buildNote` is the reason the numbers make sense.** The fork shows it to the
model next to the numbers (§4.5), so the model narrates a weakened operator rather
than a fit one. It is **reference data** under principle #14 of the producer's
`CLAUDE.md`. It states the character's condition ("weeks in a coma; training
intact, body not"). It never instructs the model on how to play `{{user}}`.

### 3.5 `bestiary[]` — things that are fought

A bestiary entry is a **type**, not an individual. "Three Shamblers" spawns three
temporary instances from one entry. Each rolls its own numbers, and all three are
discarded when the encounter ends (§4.3).

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `id` | string | yes | snake_case, unique among bestiary entries. |
| `name` | string | yes | Display name. Instances are numbered by the consumer (`Shambler 2`). |
| `tier` | string | yes | `"common"` \| `"elite"` \| `"boss"`. Display and pacing signal; no mechanical meaning in v0. |
| `resources` | object | yes | `resourceKey → value`, where value is a number or a range (§3.6). It sets `max`; an instance spawns at `current = max`. |
| `attributes`, `proficiencies` | object | no | As on sheets; values may be ranges. |
| `abilities` | array | no | As on sheets. |
| `equipment` | object | no | As on sheets. |
| `loot` | array | no | `{ "item": itemId, "chance": 0–1, "qty"?: number \| range }`. Each line rolls independently when an instance is defeated. `qty` defaults to `1`. |
| `note` | string | no | One or two lines on how it fights, in observable register (slow but grabs; travels in packs). Not the lore. |
| `unique` | bool | no | At most one instance per encounter, and its defeat is committed to campaign state (§4.4). Default `false`; `true` is expected for bosses. |
| `npc` | string | no | The `MEMORY_CONTRACT.md` slug of a named character this entry fights *as*. Links the fight to the character's lorebook voice and memory. See below. |
| `phases` | array | no | Boss phases: `{ "atHpPct": 1–99, "note": string }`, fired once each as HP falls past the threshold. |

**Named versus nameless.** Interchangeable enemies (a Shambler, a nameless rogue
operator) are bestiary entries and nothing else. A named villain with a
personality is a cast member. They have Tier 2 lorebook entries and an NPC
manifest id, and their fight entry carries `npc` so the model portrays them from
their own material rather than the stat block. A named character who is mostly an
ally and only sometimes fought is a **sheet**, not a bestiary entry, because their
state persists.

### 3.6 Numbers and ranges

Anywhere a bestiary value takes a number, it may instead take a range:

```json
{ "base": 40, "spread": 10 }
```

The consumer rolls a uniform integer in `[base − spread, base + spread]` when the
instance spawns, then clamps it to the system's `[min, cap]` (or `[1, maxRank]`
for ranks). `spread: 0` or a plain number means fixed. Sheets never take ranges:
a persistent individual has one authored starting value.

`base ± spread` was chosen over dice notation (`3d10+25`) because it is easier for
the producer's agents to author correctly, and the authored intent ("about 40,
give or take 10") reads directly. Dice notation is a candidate later addition
(§7).

### 3.7 `atZero` — what reaching the floor means

| Value | Meaning |
| --- | --- |
| `"none"` | Nothing happens beyond the floor (MP at 0 just means no spells). Default. |
| `"downed"` | Out of the fight, alive, recoverable. |
| `"dead"` | Dead. For a sheet, this is permanent campaign state. |

`atZero` is either one string for every kind, or an object keyed by `persona`,
`npc`, `common`, `elite`, `boss`, with a `default`. A key that isn't listed
falls back to `default`, and a missing `default` falls back to `"none"`.

**This is where stats meet the posture contract** (producer `CLAUDE.md`
principle #13). The world's declared boundary decides `persona` and `npc` at-zero
values. A world that rules `{{user}}`'s death out makes `persona` `"downed"`. A
souls-like world that rules it **in** says `"dead"` explicitly, because the
model's trained floor will otherwise refuse to let the fight be lost. The value
is authored from Master Design Section 6, never defaulted (§6).

---

## 4. Consumer lifecycle — designed, not implemented

Normative for the consumer once it is built. Recorded here so both sides share
the same picture of what the starting values are *for*.

### 4.1 Bootstrap

On the first RPG action in a chat with no campaign state (pristine), the consumer
reads the carrier and **snapshots the whole payload** into the chat's campaign
state: `system`, `items`, and `bestiary` as the campaign's rules, and `sheets` as
its starting state. It records a content hash of the carrier alongside the
snapshot.

Snapshotting the rules, not just the sheets, means a world revised mid-campaign
changes nothing in that campaign. The hash lets a later consumer notice the
difference and *offer* an update (§7). It never applies one silently.

### 4.2 Campaign state is per chat

- **A new chat starts fresh** from the world's starting values.
- **A branched chat inherits** the campaign state at the branch point. If state
  lives in chat metadata, SillyTavern's branch copy gives this for free.
- Nothing is shared across chats. A campaign that spans several chat files is
  deferred (§7).

### 4.3 Encounters and the working copy

When combat starts, the consumer creates a **working copy**. It holds the
participating sheets, plus one instance per spawned enemy, each with its
range-rolled numbers. All combat changes go to the working copy. Swipes,
regenerations, and rewinds inside the fight revise or discard working-copy
changes. They never touch campaign state, so a re-roll can't permanently cost
anything.

When the encounter ends, the sheets' changes from the working copy are committed
(§4.4), loot rolls resolve into inventory, and the instances are discarded.

### 4.4 Commits and rewind

Campaign state changes only at **commits**:

- an encounter ends;
- an item is used, gained, or lost (loot, a consumable, a trade);
- equipment changes;
- a permanent effect applies (a `target: "max"` item effect);
- a sheet reaches an `atZero` of `"dead"`, or a `unique` bestiary entry is
  defeated;
- party membership changes.

Each commit records **the message id it happened at** plus its diff. Deleting or
rewinding to before that message reverts the commit. That covers the one rewind
the working copy can't: going back past a fight that already ended. A diff log is
recommended over full snapshots because it is smaller and doubles as an audit
trail.

### 4.5 What the model sees

The model never sees the raw carrier (§2). The consumer injects a compact
**state block** each turn. It covers the party's current resources, equipment,
and `buildNote`. During combat it adds the encounter: each instance's name,
rough condition, and `note`, plus any boss `phases` note that has fired. Exact
numbers versus descriptive condition ("badly hurt") is a consumer presentation
choice. The block is authoritative fact, the same standing as the dice oracle's
injected facts (`DICE_ORACLE.md` §1).

### 4.6 Rolls and observations

Every roll is made by the consumer and logged against its message id: spawn
ranges, loot, and whatever later combat resolution needs. The model's part is
observational, the same split as `BODY_CYCLES.md` §1.2. It can report that
`{{user}}` drank a dressing or took a bite. The consumer turns that into a change,
and the user can confirm or correct it. How the model reports changes (a tag, a
scan, a UI action) is a consumer design question, out of scope for v0.

---

## 5. Graceful degradation

Absence never errors, matching every other seam:

- No `[[RPG_STATS]]` entry, a disabled entry, or unparseable JSON ⇒ no RPG
  layer for that world. Every existing world is unaffected.
- No `persona` sheet ⇒ the payload counts as absent, logged once.
- A reference to an undeclared key (resource, proficiency, slot) or an unknown
  item id is dropped with a console warning. The rest of the sheet still seeds.
- A sheet value outside its bounds is clamped to `min ≤ current ≤ max ≤ cap`,
  with a warning.
- A malformed range (missing `base`, negative `spread`) falls back to `base`, or
  to the system `min` if `base` is missing.
- An `npc` link or an `npc` sheet `id` that matches no manifest id still seeds.
  The fight just has no lorebook voice to draw on. Not an error.
- Unknown fields are ignored. Reserved fields (`combat`, `statuses`) are ignored
  until defined.

---

## 6. Producer conformance (World-Forge agents) — **not in force**

> **Not binding.** This contract is a draft and no agent spec references it.
> An agent that emitted a carrier today would be inventing content no seed asked
> for. The list below is the expected shape for when the wiring happens.

**Pipeline wiring, when it happens** — the same shape `[[WORLD_CALENDAR]]` and
`[[DICE_TABLES]]` used:

1. **World Seed** — a new §2i *RPG System* (resources, proficiencies, slots,
   item catalog, bestiary), plus a *Starting Build* field in §3 (protagonist) and
   in §4 (each statted NPC).
2. **Interviewer** — elicits the stat system for the world's genre, then
   **derives** a proposed starting build from the protagonist description and
   presents it with its reasoning, for the player to confirm or adjust. The coma
   and ex-SAS case is the model example: a weakened `current` with the reason
   stated, ranks from the history, abilities from the training. The same for
   companions. Proposes the bestiary as enemy *types* with ranges.
3. **Refiner** — records the system and the builds in the Master Design.
4. **Architect** — authors the carrier payload in §6 (Tier 1 carrier block).
5. **Editor** — a validation step for the rules below.
6. **Compiler** — emits the carrier into the World lorebook.
7. **`tools/validate_export.py`** — a WARN-only `check_rpg_stats`, matching
   `check_world_calendar` / `check_dice_tables`.

**Expected rules** (the Editor step and validator would check these):

- [ ] (If the world is an RPG world) exactly one `[[RPG_STATS]]` entry in the
      **World (Tier 1) lorebook**, enabled (`disable: false`) and inert
      (`key: []`, `constant: false`).
- [ ] Exactly one `persona` sheet, `id: "user"`. No `npc` slug equals `"user"`.
- [ ] Every `npc` sheet `id` and every bestiary `npc` link is a manifest slug
      from the same canonical name (`MEMORY_CONTRACT.md` §4). A world emitting
      sheets for named NPCs also emits an `[[NPC_MANIFEST]]`.
- [ ] Every key used is declared in `system`. Every item reference resolves to a
      catalog `id`. Every `requires.proficiency` is declared.
- [ ] Every sheet satisfies `min ≤ current ≤ max ≤ cap`; ranks are in
      `[1, maxRank]`; every bestiary range stays within `[min, cap]`.
- [ ] Every sheet has a `buildNote` that explains any non-obvious value
      (`current < max` at the start, an unusually high or low rank). Observable
      register; `{{user}}`'s note is reference data, never a behavioral mandate
      (principle #14).
- [ ] `atZero` for `persona` and `npc` matches the boundary in Master Design
      Section 6 (principle #13). If `{{user}}`'s death is off the table, it is
      never `"dead"`. If it is ruled in, it says so explicitly.
- [ ] Every bestiary entry that names a cast member carries `npc`. A bestiary
      `note` doesn't restate its Tier 1 lore entry.
- [ ] No starting values appear in prose lorebook entries or cards. The carrier
      is the single source, and a number in prose becomes a second, stale copy.

---

## 7. Deferred and reserved

Deliberately absent from v0. Each one is a later, additive version:

- **Combat resolution** — damage, hit chance, initiative, turn order. Needs the
  reserved item `combat` field and, per `DICE_ORACLE.md` §7.3, likely
  server-authoritative rolls.
- **Statuses** — bleeding, infected, stunned. The `statuses` field is reserved.
- **Levels, XP, and growth** — how `max` and ranks rise. v0 already allows `max`
  to change through `target: "max"` effects; systematic growth is later.
- **Regeneration and rest** — how `current` recovers between fights.
- **Currency, shops, trade.**
- **Dice-notation ranges** (`3d10+25`) alongside `base ± spread`, reusing the
  oracle's roll grammar.
- **Weighted or exclusive loot tables** beyond independent `chance` lines.
- **Arc-gated spawns** — a bestiary entry that only appears in some arcs.
- **Persistent boss HP** across encounters (a villain who escapes wounded).
- **World-update migration** — offering to apply a revised carrier to a running
  campaign, using the §4.1 hash.
- **Campaigns spanning several chats.**
- **Outcome authority** — what `{{user}}`'s message can and cannot change:
  swipes replaying pinned rolls, corrections limited to parse errors, `downed`
  recovery rules, and a legality check before generation. Explored ahead of
  time in [`OUTCOME_AUTHORITY.md`](./OUTCOME_AUTHORITY.md) (Draft), which
  lists the passages here it expects to change (its §9).

---

## 8. Worked example — zombie world (strict JSON)

An illustrative carrier `content` for a zombie-apocalypse world. `{{user}}` is an
ex-SAS operator who woke from a coma into the outbreak. Maya Okafor is a nurse
companion. A full world would declare all its zombie types; three are shown, plus
a human elite and a named boss.

```json
{
  "schema": 0,
  "system": {
    "resources": [
      { "key": "hp", "label": "HP", "min": 0, "cap": 999,
        "atZero": { "default": "dead", "persona": "downed", "npc": "downed" } },
      { "key": "stamina", "label": "Stamina", "min": 0, "cap": 200, "atZero": "none" }
    ],
    "proficiencies": [
      { "key": "rifles", "label": "Rifles", "maxRank": 5 },
      { "key": "handguns", "label": "Handguns", "maxRank": 5 },
      { "key": "melee", "label": "Melee weapons", "maxRank": 5 },
      { "key": "hand_to_hand", "label": "Hand-to-hand", "maxRank": 5 },
      { "key": "first_aid", "label": "First aid", "maxRank": 5 }
    ],
    "equipmentSlots": [
      { "key": "primary", "label": "Primary weapon" },
      { "key": "sidearm", "label": "Sidearm" },
      { "key": "melee", "label": "Melee weapon" },
      { "key": "armor", "label": "Body armor" }
    ]
  },
  "items": [
    { "id": "c8_carbine", "name": "C8 Carbine", "slot": "primary",
      "requires": { "proficiency": "rifles", "rank": 2 }, "tags": ["firearm"] },
    { "id": "glock_17", "name": "Glock 17", "slot": "sidearm",
      "requires": { "proficiency": "handguns", "rank": 1 }, "tags": ["firearm"] },
    { "id": "fire_axe", "name": "Fire Axe", "slot": "melee", "tags": ["melee"] },
    { "id": "stab_vest", "name": "Police Stab Vest", "slot": "armor" },
    { "id": "field_dressing", "name": "Field Dressing", "consumable": true,
      "description": "Gauze, tape, a sachet of clotting powder.",
      "effects": [ { "resource": "hp", "delta": 20 } ], "tags": ["medical"] },
    { "id": "military_stim", "name": "Experimental Military Stim", "consumable": true,
      "description": "Unlabelled auto-injector from a quarantine lab.",
      "effects": [ { "resource": "hp", "target": "max", "delta": 10 } ],
      "tags": ["medical", "rare"] }
  ],
  "sheets": [
    {
      "id": "user", "kind": "persona", "party": true,
      "resources": { "hp": { "current": 100, "max": 150 },
                     "stamina": { "current": 60, "max": 120 } },
      "proficiencies": { "rifles": 4, "handguns": 4, "hand_to_hand": 4, "melee": 2, "first_aid": 3 },
      "abilities": [
        { "id": "self_treat", "name": "Self-Treatment", "type": "skill", "uses": "first_aid",
          "description": "Can dress their own wounds under pressure." }
      ],
      "inventory": [ { "item": "field_dressing", "qty": 1 } ],
      "equipment": { "primary": null, "sidearm": null, "melee": null, "armor": null },
      "buildNote": "Ex-SAS operator, home on leave when the coma took them; woke weeks later into the outbreak. Training and reflexes intact, body not: HP and stamina well below max until they recover."
    },
    {
      "id": "maya_okafor", "kind": "npc", "party": true,
      "resources": { "hp": { "current": 80, "max": 80 },
                     "stamina": { "current": 90, "max": 90 } },
      "proficiencies": { "first_aid": 5, "melee": 1 },
      "abilities": [
        { "id": "triage", "name": "Triage", "type": "skill", "uses": "first_aid",
          "description": "Stabilises a downed ally." }
      ],
      "inventory": [ { "item": "field_dressing", "qty": 4 } ],
      "equipment": { "melee": "fire_axe" },
      "buildNote": "ICU nurse who kept the ward running through the first week. Expert medic, untrained fighter: she swings the axe because she has to."
    }
  ],
  "bestiary": [
    { "id": "shambler", "name": "Shambler", "tier": "common",
      "resources": { "hp": { "base": 40, "spread": 10 } },
      "note": "Slow, relentless, dangerous when it gets hands on you. Comes in numbers.",
      "loot": [ { "item": "field_dressing", "chance": 0.1 } ] },
    { "id": "runner", "name": "Runner", "tier": "common",
      "resources": { "hp": { "base": 30, "spread": 8 } },
      "note": "Recently turned. Fast, closes distance before you can aim." },
    { "id": "bloated", "name": "Bloated", "tier": "elite",
      "resources": { "hp": { "base": 110, "spread": 20 } },
      "note": "Swollen and slow. Bursts when it drops, and anyone close gets sprayed." },
    { "id": "rogue_operator", "name": "Rogue Operator", "tier": "elite",
      "resources": { "hp": { "base": 120, "spread": 15 } },
      "proficiencies": { "rifles": { "base": 3, "spread": 1 }, "hand_to_hand": 3 },
      "equipment": { "primary": "c8_carbine", "armor": "stab_vest" },
      "note": "Trained, works in pairs, uses cover and flanks.",
      "loot": [ { "item": "c8_carbine", "chance": 0.4 },
                { "item": "field_dressing", "chance": 0.6, "qty": { "base": 2, "spread": 1 } } ] },
    { "id": "colonel_hale", "name": "Colonel Hale", "tier": "boss", "unique": true,
      "npc": "colonel_hale",
      "resources": { "hp": { "base": 300, "spread": 0 } },
      "proficiencies": { "rifles": 5, "hand_to_hand": 4 },
      "equipment": { "primary": "c8_carbine", "armor": "stab_vest" },
      "note": "Fights from behind his men until there are none left.",
      "phases": [ { "atHpPct": 50, "note": "His last guards are down; he stops giving orders and fights himself." } ],
      "loot": [ { "item": "military_stim", "chance": 1.0 } ] }
  ]
}
```

---

## 9. Relationship to the other contracts

| Concern | Governed by |
| --- | --- |
| NPC manifest, facets, stable ids, turn tag, scenes registry | `MEMORY_CONTRACT.md` |
| Director-card tag, alias coverage, `</style_contract>`, `[[WORLD_CALENDAR]]` | `WORLD_FORGE_SYNC.md` |
| `[[DICE_TABLES]]` carrier, roll-table payload, dice-oracle injection | `DICE_ORACLE.md` |
| `[[BODY_CYCLES]]` carrier, cycle seed payload | `BODY_CYCLES.md` |
| `[[RPG_STATS]]` carrier, stat system, starting sheets, bestiary | this document |
| Who decides outcomes; what `{{user}}`'s message can change | `OUTCOME_AUTHORITY.md` (Draft) |

All are independently versioned. `[[RPG_STATS]]` reuses existing conventions on
purpose: the enabled-but-inert carrier flags and pristine-record seeding of
`[[WORLD_CALENDAR]]`, and the stable slug id space of `MEMORY_CONTRACT.md`. It is
the home `DICE_ORACLE.md` §7.3 reserved for stateful RPG, and it deliberately does
not trip `BODY_CYCLES.md` §7.1's generic-carrier trigger (§1.3).

---

## 10. Open questions before version 1

- **How the model reports changes** (§4.6) — a turn tag in the `npcmem` style,
  a scan prompt, or UI-only with model suggestions.
- **Exact numbers or descriptive condition** in the state block (§4.5), and
  whether that is a world choice (a carrier field) or a user setting.
- **Whether `attributes` earn their place in v1** or wait until combat needs them.
- **Carrier size.** A large bestiary plus catalog in one entry is fine for the
  consumer but heavy to hand-edit. Splitting into several carriers is possible
  but costs the single-read simplicity.
