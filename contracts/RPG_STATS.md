# RPG Stats Contract — `[[RPG_STATS]]`

**Status:** Draft · **Version:** 0 · **Last updated:** 2026-11-09

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
its item catalog (including weapons, magazines, and ammunition), the **starting
sheets** of `{{user}}` and the cast, the **bestiary** of things that can be
fought, and a small **economy** (currency, prices, vendors). It is the "character-state channel"
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
- **Not combat rules.** v0 defines what a character *has*, and the
  bookkeeping of what they carry: rounds loaded, magazines full or empty, a
  blade's wear, money in the pocket (§3.8–§3.11). How damage, hit chance, and
  initiative resolve is deliberately absent (§7). Weapon logistics work without
  combat resolution; weapon numbers do not.

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
    "equipmentSlots": [ { "key": "main", "label": "Main weapon" } ],
    "currency": { "item": "dollar", "symbol": "$" },          // money is an item (§3.10)
    "refill": { "outOfCombat": "free",                        // refilling magazines (§3.8.4)
                "inCombat": { "outcomes": { "success": "full", "partial": "half", "fail": "none" } } },
    "pricing": { "condition": { "floor": 0.2, "broken": 0.05 } },   // value follows wear (§3.10.1)
    "carry": { "unit": "kg",                                  // weight limit and encumbrance (§3.13)
               "tiers": [ { "atPct": 60, "state": "burdened", "note": "Slower on foot; tires faster." } ] }
  },
  "items": [                           // the item catalog (§3.3)
    { "id": "c8_carbine", "name": "C8 Carbine", "type": "firearm.rifle", "slot": "main",
      "price": 900, "weight": 3.4, "requires": { "proficiency": "rifles", "rank": 2 },
      "ammo": { "feed": "magazine", "magazines": ["stanag_30"] },             // §3.8
      "fireModes": [ { "key": "single", "rounds": 1 }, { "key": "burst", "rounds": 3 } ] },
    { "id": "stanag_30", "name": "STANAG Magazine", "type": "ammo.magazine", "price": 25,
      "magazine": { "accepts": ["round_556"], "capacity": 30 } },
    { "id": "round_556", "name": "5.56mm Round", "type": "ammo.round", "price": 2 },
    { "id": "katana", "name": "Katana", "type": "melee.blade", "slot": "main", "price": 400,
      "durability": { "max": 100, "atZero": "broken" } },                     // §3.9
    { "id": "field_dressing", "name": "Field Dressing", "type": "consumable.medical",
      "consumable": true, "effects": [ { "resource": "hp", "delta": 20 } ] },
    { "id": "dollar", "name": "Dollar", "type": "currency.note" }
  ],
  "sheets": [                          // persistent individuals (§3.4)
    { "id": "user", "kind": "persona",
      "resources": { "hp": { "current": 100, "max": 150 } },
      "proficiencies": { "rifles": 4 },
      "abilities": [ { "id": "self_treat", "name": "Self-Treatment", "type": "skill" } ],
      "inventory": [ { "item": "field_dressing", "qty": 2 },
                     { "item": "stanag_30", "qty": 2, "loaded": 30 },        // copies with state (§3.11)
                     { "item": "dollar", "qty": 40 } ],
      "equipment": { "main": { "item": "c8_carbine", "mode": "single",
                               "magazine": { "item": "stanag_30", "loaded": 30 } } },
      "carry": { "max": 50 },                                                // §3.13
      "buildNote": "Ex-SAS, weeks in a coma. Training intact, body not." }
  ],
  "bestiary": [                        // things that are fought, instanced per encounter (§3.5)
    { "id": "shambler", "name": "Shambler", "tier": "common",
      "resources": { "hp": { "base": 40, "spread": 10 } },
      "loot": [ { "item": "field_dressing", "chance": 0.15 } ] }
  ],
  "vendors": [                         // places and people that buy and sell (§3.10)
    { "id": "junction_trader", "kind": "fixed", "name": "Junction Trader",
      "location": "Junction Market", "funds": { "base": 300, "spread": 150 },
      "stock": [ { "item": "round_556", "qty": 200 } ], "buyRate": 0.5 },
    { "id": "squatter_trader", "kind": "wandering", "name": "Squatter Trader",
      "funds": { "base": 120, "spread": 80 },
      "stockTable": [ { "item": "field_dressing", "chance": 0.6, "qty": { "base": 2, "spread": 1 } } ] }
  ],
  "scavenge": [                        // what kinds of place hold, rolled on search (§3.12)
    { "id": "pharmacy", "name": "Pharmacy", "aliases": ["chemist", "drugstore"], "depletes": true,
      "loot": [ { "item": "field_dressing", "chance": 0.5, "qty": { "base": 2, "spread": 1 } } ] }
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
| `vendors` | array | no | Places and people that buy and sell: fixed settlement vendors and wandering vendor types (§3.10). Requires `system.currency`. |
| `scavenge` | array | no | Scavenge tables: what kinds of place hold, rolled when searched (§3.12). |

### 3.2 `system` — the world's rules

The stat set is **world-defined**. A zombie world declares HP and firearm
proficiencies; a high-fantasy world declares HP, MP, and spell schools; a noir
world might declare Nerve and Heat. Every sheet, item, and bestiary entry uses
the same shape, and `system` decides what the keys are.

**`resources[]`** — pools on a character that go down and come back up (HP, MP,
stamina). Ammunition is **not** a resource: rounds, arrows, and magazines are
items, because they are looted, bought, sold, and loaded into a specific weapon
(§3.8).

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
`label`. The slot set is world-defined like every other key. For weapons, the
**recommended default** (and the Interviewer's opening proposal, §6) is three
slots by role:

| Slot key | Role | Examples |
| --- | --- | --- |
| `main` | the main weapon | rifle, shotgun, katana, longsword |
| `secondary` | the small weapon carried alongside | pistol, revolver, dagger, machete |
| `ranged` | the non-firearm ranged weapon | bow, crossbow, throwing knives |

A slot is a **role**, not a type: a katana and a rifle are both `main`. What
kind of object a weapon is lives on the item's `type` (§3.3). Worlds that want
other roles declare them (`main_hand` / `off_hand`, `heavy`, `armor`). A longbow
archer's world may well put bows in `main`.

All four arrays use objects rather than bare strings on purpose: later versions
add fields to them (a proficiency's governing attribute, a resource's regen rule)
without a migration.

**`currency`** — optional. `{ "item": itemId, "symbol"?: string }`. Names the
catalog item that is money (§3.10). `symbol` is a display prefix for the HUD and
state block (`"$"`, `"€"`, `"₽"`); absent ⇒ the item's `name` is used. Required
when `vendors` or any `price` is present.

**`refill`** — optional. How magazines and internal-feed weapons are loaded
from loose rounds (§3.8.4):

| Field | Type | Meaning |
| --- | --- | --- |
| `outOfCombat` | `"free"` \| check object | Default `"free"`: a refill outside an encounter is a plain commit. |
| `inCombat` | `"free"` \| check object | Default: a check reading the `requires.proficiency` of the weapon being loaded (for a magazine: the equipped weapon that takes it), untrained if it has none, with outcomes `full` / `half` / `none`. |

A **check object** is `{ "check"?: key, "outcomes": { "success", "partial", "fail" } }`.
`check` names a proficiency or attribute key the roll reads (a world that wants
refilling to test Dexterity or Nerve rather than weapon training names it here);
absent ⇒ the loaded weapon's `requires.proficiency`, as above. Each outcome is
`"full"` (every magazine being refilled is filled), `"half"` (half the rounds that
would have gone in, rounded down), or `"none"` (no rounds loaded; the time is
still spent). How the roll turns a rank into success / partial / fail belongs to
combat resolution and is deferred (§7); until it exists the consumer may use any
documented scheme.

**`pricing`** — optional. `{ "condition": { "floor": 0–1, "broken": 0–1 } }`.
How wear changes what an item is worth (§3.10.1). Absent ⇒ condition doesn't
affect price.

**`carry`** — optional. Enables the weight limit (§3.13): `{ "unit": string,
"tiers": [ { "atPct": 1–99, "state": string, "note": string } ] }`. `unit` is a
display label (`"kg"`, `"lb"`). Absent ⇒ no weight tracking, and every `weight`
and `carry` field is ignored.

### 3.3 `items[]` — the catalog

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `id` | string | yes | snake_case, unique among items. The only way anything references an item. |
| `name` | string | yes | Display name. |
| `type` | string | see note | `class.type` from the shared classification vocabulary (`OUTCOME_AUTHORITY.md` §4.5): `firearm.rifle`, `melee.blade`, `ranged.bow`, `ammo.magazine`, `currency.note`, … Possession is matched by type (`OUTCOME_AUTHORITY.md` §3.1). **Required** on weapons, magazines, ammunition, and the currency item; recommended on everything else. |
| `nature` | string[] | no | From the same vocabulary: `mundane`, `magical`, `futuristic`, `legendary`. Default `["mundane"]`. |
| `description` | string | no | One line, observable register. |
| `slot` | string | no | An `equipmentSlots` key. Absent ⇒ the item cannot be equipped. |
| `requires` | object | no | `{ "proficiency": key, "rank": int }`. A character below the rank cannot equip it. `rank` defaults to `1`. |
| `consumable` | bool | no | Used up on use. Default `false`. |
| `effects` | array | no | Applied on use. Each is `{ "resource": key, "delta": int, "target": "current" \| "max" }`. `target` defaults to `"current"`. A `"max"` effect is **permanent** (the "permanent potion" case). |
| `price` | int | no | Base value in currency units, for a pristine copy (§3.10). Absent ⇒ not for sale and worth nothing to a vendor. Never set on the currency item itself. |
| `weight` | number | no | Per unit, in `system.carry.unit` (§3.13). Default `0`. A magazine's weight is the same full or empty; loaded rounds are not weighed separately. |
| `ammo` | object | no | Makes the item a ranged weapon and says how it is fed (§3.8). |
| `fireModes` | array | no | Firearm fire modes and the rounds each pull of the trigger spends (§3.8.2). |
| `magazine` | object | no | Makes the item a magazine: `{ "accepts": [itemId], "capacity": int }` (§3.8.1). |
| `durability` | object | no | Wear: `{ "max": int, "perUse"?: int, "atZero": "broken" \| "destroyed" }` (§3.9). |
| `recover` | number | no | `0–1`. Chance each spent unit is recovered after the encounter (arrows, bolts, throwing knives; §3.8.3). Default `0`. |
| `tags` | string[] | no | Free world vocabulary (`"medical"`, `"quest"`, `"rare"`). |
| `combat` | object | — | **Reserved** for weapon and armor numbers (damage, range, accuracy, armor value, what a fire mode does to a hit). Not defined in v0; consumers ignore it. |

The catalog exists because inventory, equipment, and loot all point at the same
things. Without one list, the same carbine is described three slightly different
ways and the fork cannot tell they are one item.

**Stateful items.** An item with `ammo` (internal feed), `magazine`, or
`durability` carries per-copy state: two katanas can be at different wear, two
magazines at different fill. Such items do not merge into a fungible stack; the
consumer tracks each copy separately (§3.11). Every other item stacks by `qty`.

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
| `inventory` | array | no | `{ "item": itemId, "qty": int }`, plus optional per-copy state for stateful items (`loaded`, `durability`; §3.11). |
| `equipment` | object | no | `slotKey → itemId \| copy object \| null`. A plain id is a pristine copy; a copy object carries state (`mode`, `loaded`, `magazine`, `durability`; §3.11). An equipped item need not also appear in `inventory`. |
| `carry` | object | no | `{ "max": number }`: the most this character can carry, inventory and equipment together, in `system.carry.unit` (§3.13). Required on party sheets when `system.carry` is declared. Part of the authored build. |
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
| `equipment` | object | no | As on sheets. Instances **do not track** ammunition, magazines, or durability: an enemy's weapon never runs dry or breaks, and the instance is discarded at encounter end anyway. |
| `loot` | array | no | `{ "item": itemId, "chance": 0–1, "qty"?: number \| range, "loaded"?: number \| range, "durability"?: number \| range }`. Each line rolls independently when an instance is defeated. `qty` defaults to `1`. `loaded` and `durability` set the state of a dropped stateful item (a magazine with `{ "base": 12, "spread": 10 }` rounds left, a carbine at half wear); absent ⇒ pristine. Currency drops are ordinary loot lines on the currency item. |
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

Two places outside the bestiary also take ranges: loot `loaded` / `durability`
(rolled when the drop resolves, clamped to the item's `capacity` / `max`), and a
fire mode's `rounds` (rolled **per trigger pull**, §3.8.2).

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

### 3.8 Weapons and ammunition

A weapon is a catalog item with a `slot` and a weapon `type`. A **ranged**
weapon also carries `ammo`, which says how it is fed. There are three feeds,
because "reloading" means three different things in play:

| `feed` | Weapons | Where the rounds are | Fields |
| --- | --- | --- | --- |
| `"magazine"` | rifles, pistols, SMGs | in a detachable magazine, which is its own item with its own fill | `magazines`: the magazine item ids it takes |
| `"internal"` | pump shotguns, revolvers, bolt-action rifles | in the weapon itself | `accepts`: round item ids; `capacity`: int |
| `"direct"` | bows, crossbows, thrown weapons | nowhere — each use draws one unit from the inventory stack | `accepts`: item ids drawn |

Melee weapons carry no `ammo`. They may carry `durability` (§3.9), as may any
weapon.

```jsonc
{ "id": "glock_17", "type": "firearm.handgun", "slot": "secondary",
  "ammo": { "feed": "magazine", "magazines": ["glock_mag_17"] } }
{ "id": "remington_870", "type": "firearm.shotgun", "slot": "main",
  "ammo": { "feed": "internal", "accepts": ["shell_12g"], "capacity": 6 } }
{ "id": "recurve_bow", "type": "ranged.bow", "slot": "ranged",
  "ammo": { "feed": "direct", "accepts": ["arrow"] } }
{ "id": "throwing_knife", "type": "ranged.thrown", "slot": "ranged", "recover": 0.7,
  "ammo": { "feed": "direct", "accepts": ["throwing_knife"] } }
```

A thrown weapon names **itself** as its ammunition: equipping throwing knives
equips the stack, and each throw spends one from inventory. No special case.

#### 3.8.1 Magazines

A magazine is an item with a `magazine` block: `{ "accepts": [roundItemId],
"capacity": int }`. Each copy has its own `loaded` count (§3.11). A magazine-fed
weapon holds **one inserted magazine** at a time; its other magazines sit in
inventory, full, partial, or empty.

Magazines exist as tracked items, rather than as a loose-round count on the
gun, because of what happens when the last one runs dry. Loose rounds in the
pack are useless until they are pressed into magazines, and that takes time a
fight may not give (§3.8.4). A gun with ammunition in the pack and no loaded
magazine is the tension this design is for.

#### 3.8.2 Fire modes

`fireModes` is an array of `{ "key": string, "label"?: string, "rounds": number
| range }`. `rounds` is what one trigger pull spends: `single` 1, `burst` 3,
`auto` a range rolled per pull (`{ "base": 8, "spread": 3 }`). The first entry is
the default mode. A firearm without `fireModes` spends one round per shot.

The current mode is per-copy state (`mode`, §3.11). Switching mode spends
nothing and is not a commit inside an encounter (it lives in the working copy);
outside one it commits with the next change. What a mode does to a hit is
combat resolution, reserved for `combat` (§7). Here it only counts rounds.

#### 3.8.3 Recovery

`recover` (0–1) on a `direct`-feed ammunition item is the chance that each unit
spent during an encounter is found again afterwards: arrows pulled from bodies,
throwing knives picked up. The consumer rolls once per spent unit at encounter
end and returns the recovered units to inventory. Rounds and shells don't
recover (`recover` absent ⇒ `0`).

#### 3.8.4 Reload and refill

Two different actions, kept apart on purpose:

- **Reload** — swap the inserted magazine for a fuller one from inventory. The
  removed magazine goes back to inventory with whatever it still holds, **even
  when empty**. It is never destroyed. A reload with no magazine in inventory
  holding a single round fails (`OUTCOME_AUTHORITY.md` §4.1a).
- **Refill** — press loose rounds from an inventory stack into magazines, or load
  them into an `internal`-feed weapon. Governed by `system.refill` (§3.2): free
  outside combat by default, a check inside it. The roll is pinned to the player
  message that attempted it (`OUTCOME_AUTHORITY.md` §4.2), so a swipe replays the
  same result. A `"fail"` loads nothing **and still costs the time**. The model
  narrates fumbled rounds while the threat closes in, as the world's answer
  (`OUTCOME_AUTHORITY.md` §3.3). Refilling with no loose rounds that fit fails.

How long a refill takes in turns is deferred with initiative and turn order
(§7). Until then, "it took too long" is something the model narrates from the
check's outcome, not a number.

### 3.9 Durability

`durability: { "max": int, "perUse"?: int, "atZero": "broken" | "destroyed" }`.
Each copy has its own current value (§3.11), starting at `max` unless authored.

- **`perUse`** (default `1`) is subtracted for each use the fork observes: a
  strike for a melee weapon, a trigger pull for a firearm. A narrated extra hit
  (the blade chips on bone, the rifle takes a fall) is an observation like any
  other (§4.6) and may cost more.
- **`"broken"`** — at `0` the copy stays in inventory and cannot be used until
  repaired. Repair is deferred (§7). **`"destroyed"`** — at `0` the copy is
  removed.
- Durability is optional on any item. Swords, axes, firearms (a jam-prone rifle),
  armor.

### 3.10 Currency, pricing, and vendors

**Money is an item.** `system.currency.item` names it — dollars, euros, bottle
caps, ration chits, whatever the world uses. Because it is an ordinary stackable
item, loot drops it with plain loot lines, possession checks find it ("I pay 50"
with 30 in the pocket fails, `OUTCOME_AUTHORITY.md` §4.1a), and trade is an
item swap. A world has one currency in v0.

**`price`** on a catalog item is its base value in currency units, for a
pristine copy.

#### 3.10.1 Condition pricing

With `system.pricing.condition` declared, a copy's **value** follows its wear:

```
value = price × max(floor, durability / max)     working copy
value = price × broken                           broken copy
```

Items without `durability` always use the full `price`. Rounds loaded in a
magazine or an `internal`-feed weapon are valued separately at their own round
price and added. Values round to the nearest whole unit.

Value applies in both directions. A vendor sells a worn copy for its value
(a stock line's `price` override replaces `price` in the formula). A vendor buys
from the party at `value × buyRate`.

**Rarity by condition falls out of this. It needs no rarity field.** Loot and
scavenge lines roll `durability` ranges, so weapons found in the world come out
worn and sell cheap. A pristine copy only exists where the world authors one: a
stock line with no `durability` (pristine), optionally with a `price` override
above base as a scarcity premium. "A perfect-condition M9 at the gunsmith,
priced like it" is one stock line. Scavenging enough worn guns to afford it is
the loop.

#### 3.10.2 Vendors: fixed and wandering

| `kind` | What it is | Lifecycle |
| --- | --- | --- |
| `"fixed"` (default) | A settlement trader. An authored individual, like a sheet. | Exists from the start. Its stock is campaign state; its funds re-roll on refresh. |
| `"wandering"` | A **type**, like a bestiary entry. A squatter barricaded in an apartment who'll deal, a convoy passing through. | Spawns as a temporary instance (§3.12, §4.3) with randomly rolled funds and stock. Discarded when the party leaves. |

| Field | Applies to | Type | Meaning |
| --- | --- | --- | --- |
| `id` | both | string | snake_case, unique among vendors. Required. |
| `kind` | both | string | `"fixed"` \| `"wandering"`. Default `"fixed"`. |
| `name` | both | string | Display name. Required. |
| `npc` | fixed | string | `MEMORY_CONTRACT.md` slug of the character who runs it. Links trade to that character's lorebook voice. A wandering vendor has none: if a trader should recur as a person, author them as `fixed`. |
| `location` | fixed | string | Free-text place name, matching the location's lorebook naming. Where trade can happen (§3.10.3). |
| `funds` | both | number \| range | Cash the vendor can pay out. Absent ⇒ unlimited. |
| `fundsRefresh` | fixed | string | When funds re-roll: `"visit"` (default), `"day"`, or `"never"`. |
| `stock` | both | array | `{ "item": itemId, "qty"?: int, "price"?: int, "loaded"?, "durability"? }`. Fixed: the starting stock (required). Wandering: guaranteed lines (optional). `qty` absent ⇒ unlimited. `price` overrides the item's base `price` here. |
| `stockTable` | wandering | array | Loot-style lines rolled at spawn: `{ "item", "chance": 0–1, "qty"?, "price"?, "loaded"?, "durability"? }`, values may be ranges (§3.6). On a `fixed` vendor the field is **reserved** for restocking (§7). |
| `buyRate` | both | number | Fraction of a copy's value the vendor pays when buying from the party (§3.10.1). Default `0.5`. `0` ⇒ buys nothing. |
| `buys` | both | string[] | Item `type`s or `class.*` patterns the vendor will buy (`["ammo.*", "firearm.*"]`). Absent ⇒ buys anything with a `price`. |
| `note` | both | string | One line on how the vendor deals, observable register (cash only; haggles hard; won't let you past the door chain). |

**Funds.** Money the party pays a vendor goes into its funds; money the vendor
pays out comes out of them. A sale the vendor can't cover fails
(`OUTCOME_AUTHORITY.md` §4.1a). The party can sell part of what it brought and
carry the rest to someone else.

**Refresh** re-rolls `funds` from its range and **replaces** the current value:
the trader's cash in hand has changed since the party last saw them.

- `"visit"` — a visit begins when the party arrives at the vendor's `location`
  and ends when it leaves (the Scene Tracker location changes). Each new visit
  re-rolls. Walking out and straight back in also re-rolls, so a player can fish
  for a rich day; the world accepts that.
- `"day"` — at most once per in-world day (the Scene Tracker day counter), on
  the first visit that day. The choice for worlds that want the fishing closed.
- `"never"` — rolled once at bootstrap; only trade moves it.

Without a location signal, the consumer treats each opening of an explicit
trade action as a visit.

Fixed-vendor **stock doesn't refresh** in v0. What the party buys out stays
bought out; restocking is deferred (§7).

**Wandering spawns.** A wandering instance appears only from a fork roll: a
`vendor` line in a scavenge table (§3.12), or the consumer's encounter logic (the
same trigger that spawns bestiary encounters, a consumer design question). Its
funds and `stockTable` roll once at spawn, and its `stock` lines are added as
they are. The model narrating a stranger with things to sell creates no vendor.
That is scenery, with no mechanics (`OUTCOME_AUTHORITY.md` §3.2). The instance is
discarded when the party leaves the place it spawned or the scene ends, and
whatever wasn't bought is gone with it.

#### 3.10.3 Where trade happens

Trade with a **fixed** vendor requires the party to be at its `location` (the
Scene Tracker's current location, matched case-insensitively), or the vendor's
`npc` to be present in the scene (the `present` list of the `npcmem` turn tag,
`MEMORY_CONTRACT.md`). With neither signal available, the consumer gates trade
through an explicit HUD trade action. A **wandering** instance is present by
construction for as long as it exists. A trade attempted away from the vendor
fails (`OUTCOME_AUTHORITY.md` §4.1a): Sal can't be sold to from across the map.

### 3.11 Item copies and their state

Stateful items (§3.3) are tracked **per copy**. The catalog `id` says *what* an
item is; the copy says *which one*.

- **The producer never authors copy ids.** The consumer assigns them at bootstrap
  (§4.1) and whenever a stateful item enters the campaign (loot, purchase).
- **Authoring state.** An inventory line may carry state for every copy it
  creates:

  ```jsonc
  { "item": "stanag_30", "qty": 3, "loaded": 30 }   // three full magazines
  { "item": "stanag_30", "qty": 1, "loaded": 0 }    // one empty
  { "item": "katana", "qty": 1, "durability": 62 }
  ```

  The consumer expands each line into `qty` separate copies. Omitted state means
  pristine: `loaded` = `capacity`, `durability` = `max`.
- **Equipped copies.** An equipment value is a plain id (a pristine copy) or a
  copy object:

  | Field | For | Meaning |
  | --- | --- | --- |
  | `item` | all | Catalog id. |
  | `durability` | items with `durability` | Current wear. |
  | `mode` | weapons with `fireModes` | Current fire mode `key`. Default: the first mode. |
  | `magazine` | `magazine` feed | The inserted magazine: `{ "item", "loaded" }`, or `null` for none inserted. Default: a full one of the first listed type. |
  | `loaded` | `internal` feed | Rounds in the weapon. Default: `capacity`. |

  A `direct`-feed weapon has no loaded state; its count is the inventory stack of
  what it `accepts`.
- **Non-default starting state needs a reason in `buildNote`.** An empty gun or a
  worn blade at the opening moment is an authored decision, like `current < max`
  on a resource.

### 3.12 `scavenge[]` — searching the world

A scavenge table is a loot table attached to a **kind of place** rather than to
an enemy: a pharmacy, a police cruiser, a gas station, a gutted apartment. It is
the authored answer to "what's in here," so neither the player nor the model has
to invent one.

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `id` | string | yes | snake_case, unique among scavenge tables. |
| `name` | string | yes | Display name of the kind of place. |
| `aliases` | string[] | no | Other names the consumer matches against (`"chemist"`, `"drugstore"`). |
| `loot` | array | yes | Loot lines as in §3.5 (`item`, `chance`, `qty`, `loaded`, `durability`, ranges allowed), plus **vendor lines**: `{ "vendor": vendorId, "chance": 0–1 }`, naming a `wandering` vendor the search can turn up. |
| `depletes` | bool | no | Default `true`: a place searched once stays searched (below). |
| `check` | check object | no | As in `system.refill` (§3.2): `full` rolls the table as authored, `half` halves every line's `chance`, `none` finds nothing and still spends the time. Absent ⇒ no check; the table rolls as authored. |
| `fallback` | bool | no | At most one table. Used for a search the consumer can't match to any table. |
| `note` | string | no | One line, observable register (already picked over; the back room is locked). |

**A search is an attempt.** `{{user}}` says what they search. The consumer
matches the place against table `name` and `aliases`, using the player's message
and the Scene Tracker location. The small-model classification pass
(`OUTCOME_AUTHORITY.md` §4.1b) is a natural later helper for unmatched names.
The consumer rolls the table, pins the roll to that user message (swipes replay
it), and injects the result as authoritative fact. The model narrates finding
it. If nothing matches and there is no `fallback` table, the search finds no
catalog items: whatever the scene supports is scenery and carries no stats.

**Depletion** is keyed by table and place: the table `id` plus the Scene
Tracker's current location. Searching a depleted place finds nothing ("the
shelves were cleared already"), including on a later visit. Without a location
signal, depletion can't be tracked and is skipped. Places refilling over time is
deferred (§7).

**Vendor lines** are how the world produces a wandering trader: a search of an
apartment block turns up a barricaded unit with someone inside willing to deal.
The line rolls like any other; on a hit, the consumer spawns that vendor's
instance (§3.10.2).

### 3.13 Carry weight

Enabled by `system.carry`. Every item has a `weight` per unit (default `0`), and
every party sheet has a `carry.max`.

- **Load** is the sum of `weight × qty` over the sheet's inventory **and**
  equipment. The rifle on the sling and the magazine in it count the same as
  what's in the pack.
- **The limit is hard.** Load never exceeds `carry.max`. Gaining an item that
  would push it over fails. The loot stays on the floor, and a purchase is
  refused before any money changes hands (`OUTCOME_AUTHORITY.md` §4.1a). The
  player chooses what to drop or hand to a companion. The fork never drops
  anything on its own.
- **Encumbrance tiers.** `system.carry.tiers` are ordered by `atPct`. The
  highest tier whose `atPct` the load has reached applies, and its `state` and
  `note` go into the state block (§4.5). An operator at 44 of 50 kg is
  `burdened` and the model writes them slower and tiring faster. What a tier
  does mechanically (movement, initiative, stamina drain, a failed escape) is
  deferred with combat resolution (§7). In v0 a tier is authoritative fact the
  model narrates from.
- **The limit is part of the build.** `carry.max` is authored with the rest of
  the sheet and explained in `buildNote` when it's unusual. A trained operator
  who carries 50 kg; a nurse who manages 30. A starting load above the limit is
  invalid.
- **Party members carry separately.** Handing an item to a companion moves it
  between sheets and is a commit. Bestiary instances and vendors don't track
  weight.

---

## 4. Consumer lifecycle — designed, not implemented

Normative for the consumer once it is built. Recorded here so both sides share
the same picture of what the starting values are *for*.

### 4.1 Bootstrap

On the first RPG action in a chat with no campaign state (pristine), the consumer
reads the carrier and **snapshots the whole payload** into the chat's campaign
state: `system`, `items`, and `bestiary` as the campaign's rules, and `sheets`
and fixed-vendor `stock` as its starting state. Stateful inventory lines are
expanded into individual copies with consumer-assigned ids (§3.11). Fixed vendors'
`funds` roll on their first refresh (§3.10.2). It records a content hash of the
carrier alongside the snapshot.

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

Rounds fired, magazines swapped, fire-mode switches, refills, and wear during
the fight all go to the working copy too. A live HUD shows the working copy.

When the encounter ends, the sheets' changes from the working copy are committed
(§4.4), recovery rolls for spent `direct`-feed ammunition resolve (§3.8.3), loot
rolls resolve into inventory, and the instances are discarded. Loot that would
push a sheet over its carry limit (§3.13) stays on the ground for the player to
pick through.

A **wandering vendor** instance (§3.10.2) is temporary in the same way, without
a working copy. Trades with it commit normally, and the instance itself (funds,
remaining stock) is discarded when the party leaves.

### 4.4 Commits and rewind

Campaign state changes only at **commits**:

- an encounter ends;
- an item is used, gained, or lost (loot, a consumable, a trade);
- outside an encounter: rounds are fired, a weapon is reloaded or refilled, or a
  copy wears (§3.8–§3.9);
- a purchase or sale with a vendor (the party's inventory, the vendor's stock,
  and the vendor's funds all change, §3.10);
- a fixed vendor's funds refresh, or a wandering vendor spawns (§3.10.2);
- a search resolves, including depleting the place (§3.12);
- an item moves between party sheets (§3.13);
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
and `buildNote`. For weapons: the equipped weapon's mode, rounds in the inserted
magazine (or loaded, for `internal` feed), how many loaded magazines remain, and
any copy that is `broken`. "Last magazine" and "no loaded magazines, 45 loose
rounds" are exactly the facts the model must not drift from. Money is shown with
the currency `symbol`. With `system.carry`: each party member's load against
their limit and the encumbrance tier in force, with its `note`. While the party
is trading: the vendor's funds and stock with current values. After a search:
what it turned up. During combat it adds the encounter: each instance's name,
rough condition, and `note`, plus any boss `phases` note that has fired. Exact
numbers versus descriptive condition ("badly hurt") is a consumer presentation
choice. The block is authoritative fact, the same standing as the dice oracle's
injected facts (`DICE_ORACLE.md` §1).

### 4.6 Rolls and observations

Every roll is made by the consumer and logged against its message id: spawn
ranges, loot, and whatever later combat resolution needs. The model's part is
observational, the same split as `BODY_CYCLES.md` §1.2. It can report that
`{{user}}` drank a dressing or took a bite. The consumer turns that into a change,
and the user can confirm or correct it.

**Shots are observed, rounds are counted.** The model reports trigger pulls
("fires twice"); the consumer multiplies by the current fire mode's `rounds` and
decrements the inserted magazine. The model never reports a remaining-rounds
figure, the same way it never reports an HP total.

**Narration never mints catalog items.** A catalog item enters the campaign only
through a fork roll (bestiary loot, a scavenge table, a wandering vendor's
stock), a trade, or the authored starting state. If the model narrates "a box of
9mm under the counter" that no roll produced, the consumer doesn't commit it.
Otherwise the model becomes the loot table, and a model that wants to please
hands out ammunition whenever things get tense (producer `CLAUDE.md`
principle #13). Ordinary uncatalogued objects the scene supports stay free to
pick up and carry no stats (`OUTCOME_AUTHORITY.md` §3.2).

How the model reports changes (a tag, a scan, a UI action) is a consumer design
question, out of scope for v0.

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
- A weapon whose `ammo` names no known item (an unknown magazine or round id)
  seeds, but can't be loaded; warning. A magazine with no `accepts` or no
  `capacity` is treated as a non-stateful item.
- An unknown `feed` value ⇒ the `ammo` block is ignored and the weapon is treated
  as melee; warning. An unknown `mode` falls back to the first fire mode.
- `loaded` above `capacity` or `durability` above `max` is clamped, with a
  warning.
- `price` or `vendors` present with no valid `system.currency` ⇒ prices are
  ignored and vendors don't load; logged once.
- A vendor line in a scavenge table that names no `wandering` vendor is dropped;
  warning. An unknown `kind` loads as `"fixed"`; an unknown `fundsRefresh` as
  `"visit"`.
- More than one `fallback` scavenge table ⇒ the first wins; warning.
- `system.carry` declared but a party sheet has no `carry.max` ⇒ that sheet has no
  limit; warning. A starting load above the limit seeds anyway, with a warning;
  nothing more can be picked up until it's under.
- No Scene Tracker location ⇒ depletion is skipped, and trade with fixed vendors
  goes through an explicit trade action (§3.10.3, §3.12).
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
   item catalog with weapons, ammunition, and weights, bestiary, currency,
   settlement vendors and wandering vendor types, scavenge tables, carry tiers),
   plus a *Starting Build* field in §3 (protagonist) and in §4 (each statted NPC),
   including carry limit.
2. **Interviewer** — elicits the stat system for the world's genre (proposing
   the main / secondary / ranged slot default, §3.2, and asking what the world
   uses as money, which settlements trade, and what kinds of place are worth
   searching), then
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
- [ ] Every weapon, magazine, ammunition item, and the currency item has a
      `type` from the shared vocabulary (`OUTCOME_AUTHORITY.md` §4.5).
- [ ] Every `ammo` block has a valid `feed` and its references resolve: a
      `magazine` feed's `magazines` are items with a `magazine` block; an
      `internal` feed has `accepts` and `capacity`; every `accepts` id is a
      catalog item. Every magazine's `accepts` resolves to round items.
- [ ] `fireModes` keys are unique per weapon; every `rounds` is ≥ 1 (a range's
      floor included). Starting `mode` values name a declared mode.
- [ ] Starting `loaded` ≤ capacity and `durability` ≤ `max`. Any non-pristine
      starting copy is explained in the sheet's `buildNote` (§3.11).
- [ ] If any `price` or `vendors` exists, `system.currency` names a catalog
      item, and that item has no `price`. Every vendor `npc` is a manifest slug.
      Every `buys` entry is a vocabulary type or `class.*` pattern.
- [ ] Every `fixed` vendor has `stock`; every `wandering` vendor has `stock` or
      `stockTable` and no `npc` or `location`. `funds` ranges stay ≥ 0.
- [ ] Every scavenge `vendor` line names a `wandering` vendor. At most one
      `fallback` table. Scavenge and stock-table lines resolve to catalog items.
- [ ] With `system.carry`: every party sheet has `carry.max`, its starting load
      (inventory + equipment) is within it, and tiers are in ascending `atPct`
      with unique `state` names. An unusual limit is explained in `buildNote`.
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

Deliberately absent from v0. Each one is a later, additive version. The
mechanics among them (combat, refill time, encumbrance effects, repair checks,
restocking) are specified in [`RESOLUTION.md`](./RESOLUTION.md), written from
the fork side. Any new authored data they need is added here.

- **Combat resolution** — damage, hit chance, initiative, turn order. Needs the
  reserved item `combat` field and, per `DICE_ORACLE.md` §7.3, likely
  server-authoritative rolls.
- **Statuses** — bleeding, infected, stunned. The `statuses` field is reserved.
- **Levels, XP, and growth** — how `max` and ranks rise. v0 already allows `max`
  to change through `target: "max"` effects; systematic growth is later.
- **Regeneration and rest** — how `current` recovers between fights.
- **Weapon combat numbers** — damage, range, accuracy, what a fire mode does to a
  hit, reach (knife vs. katana). All in the reserved `combat` field.
- **Refill duration in turns** and the roll scheme behind `system.refill`
  checks; both wait on initiative and turn order.
- **Repair** — restoring durability (a repair kit item, a vendor service, a
  proficiency). Until then a `broken` copy stays broken.
- **Ammunition realism** — a chambered round (+1), dropping magazines on a speed
  reload, mixed round types in one magazine, ammunition variants with different
  effects.
- **Encumbrance mechanics** — what a carry tier does to movement, initiative,
  stamina, or an escape. v0 tiers are narrated fact only.
- **Carry bonuses** — a bigger backpack or a cart raising `carry.max` (an item
  field plus a slot for it).
- **Two-handed and dual-wield rules.**
- **Economy depth** — fixed-vendor restocking (the reserved `stockTable`),
  haggling and reputation pricing, more than one currency, exchange rates.
- **Scavenge respawn** — depleted places refilling over time.
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
ex-SAS operator who woke from a coma into the outbreak and took a pistol off a
dead officer on the way out of the hospital. Maya Okafor is a nurse companion. A
full world would declare all its zombie types; three are shown, plus a human
elite and a named boss. Dollars are the currency here only because this world
kept them; caps, euros, or ration chits work the same way.

The economy loop is visible end to end. Scavenge tables (a pharmacy, a police
cruiser, an apartment block) turn up worn guns, magazines with a few rounds in
them, and sometimes a squatter willing to trade. Two settlement vendors buy
what's found at a fraction of its condition-adjusted value. One of them, a
gunsmith in Northgate, has a single pristine Beretta M9 priced well above base:
the reward for a lot of scavenging. Carry limits make each trip back a choice
about what to leave.

The opening state is built for tension on purpose: `{{user}}` has a Glock with
9 rounds in the magazine, one empty spare, and 11 loose rounds in a pocket. Two
reloads' worth of ammunition, and the second one has to be refilled first.

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
      { "key": "shotguns", "label": "Shotguns", "maxRank": 5 },
      { "key": "archery", "label": "Archery", "maxRank": 5 },
      { "key": "melee", "label": "Melee weapons", "maxRank": 5 },
      { "key": "hand_to_hand", "label": "Hand-to-hand", "maxRank": 5 },
      { "key": "first_aid", "label": "First aid", "maxRank": 5 }
    ],
    "equipmentSlots": [
      { "key": "main", "label": "Main weapon" },
      { "key": "secondary", "label": "Secondary" },
      { "key": "ranged", "label": "Ranged" },
      { "key": "armor", "label": "Body armor" }
    ],
    "currency": { "item": "dollar", "symbol": "$" },
    "refill": {
      "outOfCombat": "free",
      "inCombat": { "outcomes": { "success": "full", "partial": "half", "fail": "none" } }
    },
    "pricing": { "condition": { "floor": 0.2, "broken": 0.05 } },
    "carry": {
      "unit": "kg",
      "tiers": [
        { "atPct": 60, "state": "burdened", "note": "Slower on foot; tires faster; climbing is hard work." },
        { "atPct": 90, "state": "overloaded", "note": "Can't run. Every stair and fence is a struggle." }
      ]
    }
  },
  "items": [
    { "id": "c8_carbine", "name": "C8 Carbine", "type": "firearm.rifle", "weight": 3.4, "slot": "main",
      "requires": { "proficiency": "rifles", "rank": 2 }, "price": 900,
      "ammo": { "feed": "magazine", "magazines": ["stanag_30"] },
      "fireModes": [ { "key": "single", "label": "Semi", "rounds": 1 },
                     { "key": "burst", "label": "Burst", "rounds": 3 },
                     { "key": "auto", "label": "Auto", "rounds": { "base": 8, "spread": 3 } } ],
      "durability": { "max": 300, "atZero": "broken" } },
    { "id": "stanag_30", "name": "STANAG Magazine", "type": "ammo.magazine", "weight": 0.5, "price": 30,
      "magazine": { "accepts": ["round_556"], "capacity": 30 } },
    { "id": "round_556", "name": "5.56mm Round", "type": "ammo.round", "weight": 0.012, "price": 2 },
    { "id": "glock_17", "name": "Glock 17", "type": "firearm.handgun", "weight": 0.7, "slot": "secondary",
      "requires": { "proficiency": "handguns", "rank": 1 }, "price": 350,
      "ammo": { "feed": "magazine", "magazines": ["glock_mag_17"] } },
    { "id": "glock_mag_17", "name": "Glock Magazine", "type": "ammo.magazine", "weight": 0.1, "price": 20,
      "magazine": { "accepts": ["round_9mm"], "capacity": 17 } },
    { "id": "round_9mm", "name": "9mm Round", "type": "ammo.round", "weight": 0.008, "price": 1 },
    { "id": "beretta_m9", "name": "Beretta M9", "type": "firearm.handgun", "weight": 0.95, "slot": "secondary",
      "requires": { "proficiency": "handguns", "rank": 1 }, "price": 500,
      "description": "Military-issue 9mm. Clean ones haven't been seen since the first month.",
      "ammo": { "feed": "magazine", "magazines": ["beretta_mag_15"] },
      "durability": { "max": 250, "atZero": "broken" } },
    { "id": "beretta_mag_15", "name": "Beretta Magazine", "type": "ammo.magazine", "weight": 0.1, "price": 20,
      "magazine": { "accepts": ["round_9mm"], "capacity": 15 } },
    { "id": "remington_870", "name": "Remington 870", "type": "firearm.shotgun", "weight": 3.6, "slot": "main",
      "requires": { "proficiency": "shotguns", "rank": 1 }, "price": 450,
      "ammo": { "feed": "internal", "accepts": ["shell_12g"], "capacity": 6 } },
    { "id": "shell_12g", "name": "12-Gauge Shell", "type": "ammo.shell", "weight": 0.04, "price": 3 },
    { "id": "recurve_bow", "name": "Recurve Bow", "type": "ranged.bow", "weight": 1.2, "slot": "ranged",
      "requires": { "proficiency": "archery", "rank": 1 }, "price": 250,
      "description": "Quiet. The only thing that doesn't bring more of them.",
      "ammo": { "feed": "direct", "accepts": ["arrow"] } },
    { "id": "arrow", "name": "Arrow", "type": "ammo.arrow", "weight": 0.03, "price": 4, "recover": 0.5 },
    { "id": "fire_axe", "name": "Fire Axe", "type": "melee.blade", "weight": 2.7, "slot": "main", "price": 60,
      "durability": { "max": 120, "atZero": "broken" } },
    { "id": "combat_knife", "name": "Combat Knife", "type": "melee.blade", "weight": 0.3, "slot": "secondary",
      "price": 40, "durability": { "max": 150, "atZero": "broken" } },
    { "id": "stab_vest", "name": "Police Stab Vest", "type": "armor.light", "weight": 2.5, "slot": "armor",
      "price": 200, "durability": { "max": 80, "atZero": "destroyed" } },
    { "id": "field_dressing", "name": "Field Dressing", "type": "consumable.medical", "weight": 0.1,
      "consumable": true, "price": 35,
      "description": "Gauze, tape, a sachet of clotting powder.",
      "effects": [ { "resource": "hp", "delta": 20 } ], "tags": ["medical"] },
    { "id": "military_stim", "name": "Experimental Military Stim", "type": "consumable.drug", "weight": 0.05,
      "consumable": true,
      "description": "Unlabelled auto-injector from a quarantine lab.",
      "effects": [ { "resource": "hp", "target": "max", "delta": 10 } ],
      "tags": ["medical", "rare"] },
    { "id": "dollar", "name": "Dollar", "type": "currency.note" }
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
      "inventory": [
        { "item": "field_dressing", "qty": 1 },
        { "item": "glock_mag_17", "qty": 1, "loaded": 0 },
        { "item": "round_9mm", "qty": 11 },
        { "item": "dollar", "qty": 35 }
      ],
      "carry": { "max": 50 },
      "equipment": {
        "main": null,
        "secondary": { "item": "glock_17", "magazine": { "item": "glock_mag_17", "loaded": 9 } },
        "ranged": null,
        "armor": null
      },
      "buildNote": "Ex-SAS operator, home on leave when the coma took them; woke weeks later into the outbreak. Training and reflexes intact, body not: HP and stamina well below max until they recover. Took a Glock off a dead officer in the hospital stairwell: the magazine in it is half spent, the spare is empty, and the rest is a pocketful of loose rounds. Used to carrying a full combat load, about 50 kg, and feels every kilo of it now."
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
      "inventory": [ { "item": "field_dressing", "qty": 4 }, { "item": "dollar", "qty": 120 } ],
      "equipment": { "main": { "item": "fire_axe", "durability": 70 } },
      "carry": { "max": 30 },
      "buildNote": "ICU nurse who kept the ward running through the first week. Expert medic, untrained fighter: she swings the axe because she has to. It came off the corridor wall and has already been through a door and two of them; the edge is chipped."
    }
  ],
  "bestiary": [
    { "id": "shambler", "name": "Shambler", "tier": "common",
      "resources": { "hp": { "base": 40, "spread": 10 } },
      "note": "Slow, relentless, dangerous when it gets hands on you. Comes in numbers.",
      "loot": [ { "item": "field_dressing", "chance": 0.1 },
                { "item": "dollar", "chance": 0.3, "qty": { "base": 10, "spread": 8 } } ] },
    { "id": "runner", "name": "Runner", "tier": "common",
      "resources": { "hp": { "base": 30, "spread": 8 } },
      "note": "Recently turned. Fast, closes distance before you can aim." },
    { "id": "bloated", "name": "Bloated", "tier": "elite",
      "resources": { "hp": { "base": 110, "spread": 20 } },
      "note": "Swollen and slow. Bursts when it drops, and anyone close gets sprayed." },
    { "id": "rogue_operator", "name": "Rogue Operator", "tier": "elite",
      "resources": { "hp": { "base": 120, "spread": 15 } },
      "proficiencies": { "rifles": { "base": 3, "spread": 1 }, "hand_to_hand": 3 },
      "equipment": { "main": "c8_carbine", "secondary": "glock_17", "armor": "stab_vest" },
      "note": "Trained, works in pairs, uses cover and flanks.",
      "loot": [ { "item": "c8_carbine", "chance": 0.4, "durability": { "base": 180, "spread": 80 } },
                { "item": "stanag_30", "chance": 0.7, "qty": { "base": 2, "spread": 1 },
                  "loaded": { "base": 15, "spread": 15 } },
                { "item": "round_556", "chance": 0.5, "qty": { "base": 20, "spread": 10 } },
                { "item": "field_dressing", "chance": 0.6, "qty": { "base": 2, "spread": 1 } },
                { "item": "dollar", "chance": 0.8, "qty": { "base": 60, "spread": 40 } } ] },
    { "id": "colonel_hale", "name": "Colonel Hale", "tier": "boss", "unique": true,
      "npc": "colonel_hale",
      "resources": { "hp": { "base": 300, "spread": 0 } },
      "proficiencies": { "rifles": 5, "hand_to_hand": 4 },
      "equipment": { "main": "c8_carbine", "secondary": "glock_17", "armor": "stab_vest" },
      "note": "Fights from behind his men until there are none left.",
      "phases": [ { "atHpPct": 50, "note": "His last guards are down; he stops giving orders and fights himself." } ],
      "loot": [ { "item": "military_stim", "chance": 1.0 },
                { "item": "stanag_30", "chance": 1.0, "qty": 3 } ] }
  ],
  "vendors": [
    { "id": "junction_trader", "kind": "fixed", "name": "The Junction Trader", "npc": "sal_moreno",
      "location": "Junction Market",
      "funds": { "base": 300, "spread": 150 }, "fundsRefresh": "visit",
      "stock": [
        { "item": "round_9mm", "qty": 120 },
        { "item": "round_556", "qty": 200 },
        { "item": "shell_12g", "qty": 40 },
        { "item": "glock_mag_17", "qty": 4 },
        { "item": "stanag_30", "qty": 2, "price": 45 },
        { "item": "remington_870", "qty": 1 },
        { "item": "recurve_bow", "qty": 1 },
        { "item": "arrow", "qty": 30 },
        { "item": "field_dressing", "qty": 6, "price": 50 }
      ],
      "buyRate": 0.4,
      "buys": ["firearm.*", "ammo.*", "consumable.*"],
      "note": "Cash only. Won't touch anything that's been bitten." },
    { "id": "okoro_gunsmith", "kind": "fixed", "name": "Okoro Gunsmithing", "npc": "daniel_okoro",
      "location": "Northgate Settlement",
      "funds": { "base": 600, "spread": 300 }, "fundsRefresh": "day",
      "stock": [
        { "item": "beretta_m9", "qty": 1, "price": 1400 },
        { "item": "beretta_mag_15", "qty": 3 },
        { "item": "c8_carbine", "qty": 1, "durability": 150 },
        { "item": "stanag_30", "qty": 4, "loaded": 0 }
      ],
      "buyRate": 0.5,
      "buys": ["firearm.*", "ammo.*", "armor.*"],
      "note": "Strips every gun you sell him on the bench before he names a price." },
    { "id": "squatter_trader", "kind": "wandering", "name": "Squatter Trader",
      "funds": { "base": 120, "spread": 80 },
      "stockTable": [
        { "item": "field_dressing", "chance": 0.6, "qty": { "base": 2, "spread": 1 } },
        { "item": "round_9mm", "chance": 0.5, "qty": { "base": 15, "spread": 10 } },
        { "item": "glock_mag_17", "chance": 0.3, "loaded": { "base": 8, "spread": 8 } },
        { "item": "combat_knife", "chance": 0.3, "durability": { "base": 90, "spread": 40 } },
        { "item": "shell_12g", "chance": 0.25, "qty": { "base": 6, "spread": 4 } },
        { "item": "military_stim", "chance": 0.03, "price": 900 }
      ],
      "buyRate": 0.3,
      "buys": ["consumable.*", "ammo.*"],
      "note": "Talks through a door chain. Wants medicine more than money." }
  ],
  "scavenge": [
    { "id": "pharmacy", "name": "Pharmacy", "aliases": ["chemist", "drugstore", "clinic"],
      "loot": [ { "item": "field_dressing", "chance": 0.6, "qty": { "base": 2, "spread": 2 } },
                { "item": "military_stim", "chance": 0.02 },
                { "item": "dollar", "chance": 0.4, "qty": { "base": 30, "spread": 25 } } ],
      "note": "Usually hit early. Look behind the counter and in the back room." },
    { "id": "police_cruiser", "name": "Police cruiser", "aliases": ["cop car", "patrol car"],
      "loot": [ { "item": "glock_17", "chance": 0.3 },
                { "item": "glock_mag_17", "chance": 0.5, "qty": { "base": 1, "spread": 1 },
                  "loaded": { "base": 8, "spread": 8 } },
                { "item": "round_9mm", "chance": 0.4, "qty": { "base": 12, "spread": 8 } },
                { "item": "stab_vest", "chance": 0.1, "durability": { "base": 40, "spread": 25 } } ] },
    { "id": "apartment_block", "name": "Apartment block", "aliases": ["flats", "apartments", "tenement"],
      "loot": [ { "item": "dollar", "chance": 0.5, "qty": { "base": 20, "spread": 15 } },
                { "item": "field_dressing", "chance": 0.2 },
                { "item": "round_9mm", "chance": 0.15, "qty": { "base": 8, "spread": 6 } },
                { "item": "fire_axe", "chance": 0.05, "durability": { "base": 80, "spread": 30 } },
                { "vendor": "squatter_trader", "chance": 0.08 } ],
      "note": "Most doors are open. The ones that aren't, someone is behind." },
    { "id": "anywhere_else", "name": "Anywhere else", "fallback": true, "depletes": false,
      "loot": [ { "item": "dollar", "chance": 0.15, "qty": { "base": 5, "spread": 4 } } ] }
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
| `[[RPG_STATS]]` carrier, stat system, item catalog (weapons, magazines, ammunition), starting sheets, bestiary, currency and vendors | this document |
| Item `type` / `nature` vocabulary, possession and legality checks on weapons and money | `OUTCOME_AUTHORITY.md` (Draft) |
| Dice, math, modifiers, time, combat, attempt parsing — how the engine uses this payload | `RESOLUTION.md` (Placeholder, fork-authored) |
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
  consumer but heavy to hand-edit, and weapons, magazines, rounds, and vendors
  make the catalog grow fastest. Splitting into several carriers is possible
  but costs the single-read simplicity.
- **How mode switches and reloads are reported** — narration observation, a HUD
  control, or both. A HUD control is the cleaner fit for out-of-fiction
  bookkeeping like a fire-mode toggle; a reload under fire is an in-fiction
  attempt and probably belongs to narration.
- **Location identity.** Scavenge depletion and fixed-vendor trade both key off
  the Scene Tracker's current location as a free-text string. Two names for the
  same pharmacy deplete separately, and a vendor's `location` must match
  verbatim. A stable location id (the way `MEMORY_CONTRACT.md` gives NPCs one)
  may be needed before v1.
- **Matching a search to a table.** Name and alias matching is brittle against
  free prose ("I check the chemist's on the corner"). The small-model
  classification pass is a candidate helper, or the HUD could offer the matching
  tables as a choice.
