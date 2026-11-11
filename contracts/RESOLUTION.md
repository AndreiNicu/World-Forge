# Resolution Contract — how attempts become outcomes

**Status:** Placeholder, with §2 (attempt interpretation) in Draft · **Version:** 0 · **Last updated:** 2026-11-11

> **Shared contract — canonical source of truth:**
> [`AndreiNicu/World-Forge`](https://github.com/AndreiNicu/World-Forge) → `contracts/RESOLUTION.md`.
> Copies in other repositories (including the SillyTavern fork) are mirrored
> **read-only**. Do not edit a copy — edit the canonical file, then run the
> contract sync (`scripts/sync-contracts.sh`). A CI drift check keeps every copy
> byte-identical to this canonical version.
>
> **Mostly placeholder — authored from the consumer side.** This contract
> belongs to the SillyTavern fork's side, which owns the runtime internals it
> describes. World Forge only produces the data the engine consumes
> (`RPG_STATS.md`, `DICE_ORACLE.md`); how that data is handled at runtime is the
> fork's to define. §2 (attempt interpretation) was drafted early so the rest of
> the engine has a shape to build against. It is a Draft: nothing reads it, and
> the fork may revise it here as it builds. The other sections have no content
> yet. No agent spec references this document and nothing in this repo depends
> on it.

---

## 1. What will live here

The engine half of the RPG layer: everything between "`{{user}}` attempts
something" and "the fork commits a result."

- **The core roll** — the dice system, and how a roll maps onto the three
  outcome bands (success / partial / fail) that `RPG_STATS.md` and
  `OUTCOME_AUTHORITY.md` already use. *Placeholder.*
- **The math** — how proficiency ranks, attributes, and modifiers turn into
  odds; difficulty and who sets it. *Placeholder.*
- **The modifier stack** — named sources (rank, attribute, weapon condition,
  encumbrance tier, statuses, stance, cover, range, fire mode), so the HUD can
  show why the odds are what they are. *Placeholder.*
- **Time** — what a beat or round is in chat play; refill and reload duration;
  initiative and turn order. *Placeholder.*
- **Combat** — attack, damage, armor, what a fire mode does to a hit (the
  reserved `combat` field in `RPG_STATS.md` §3.3). *Placeholder.*
- **Dice grammar** — dice notation and roll syntax, shared with the dice oracle
  where it can be. *Placeholder.*
- **Attempt interpretation** — how `{{user}}`'s message is split into beats,
  which beats roll, and which bring up HUD actions. **§2, Draft.** How the main
  model's reply is parsed into observations afterward is still a placeholder.
- **The deferred mechanics built on the core** — what carry tiers do, repair
  checks, vendor restocking, and the other items `RPG_STATS.md` §7 defers to
  resolution. *Placeholder.*

---

## 2. Attempt interpretation — Draft

### 2.1 The problem

A player's message is prose, and most of it isn't an attempt. Take:

> "I paused a bit to look around. There were 4 apartments and I decided that I
> will search them for supplies. Raising my rifle, I entered one of the
> apartments. Apartment 202."

Only one clause in it should roll anything: entering apartment 202. Pausing is
color, deciding is a plan, and raising the rifle is a change of readiness with
no uncertainty in it. A fork that rolls on every verb buries the player in
pointless checks; a fork that rolls on none leaves the model to decide what's
behind every door, which makes the model the encounter table
(`OUTCOME_AUTHORITY.md` §2.2). The vocabulary below is the closed list of things
a clause can be, and what the fork does with each.

### 2.2 Beats

The fork splits `{{user}}`'s message into **beats**: one clause, one thing
`{{user}}` does, says, or decides. Each beat gets exactly one **kind** from the
vocabulary (§2.3). The kind decides whether the fork does nothing, commits
state, rolls, or brings up a HUD action. Narration around the beats (scene
description the player wrote, "There were 4 apartments") is not a beat.

Only `{{user}}` makes beats. A clause that acts for another character ("Maya
covers the stairs") is not `{{user}}`'s action. When it's an instruction to an
ally, it is `speech`, and what the ally does is the world's response. When it
narrates the ally acting on their own, it is ignored as a claim on someone
else's turn.

### 2.3 The vocabulary

| Kind | What it is | Example | Rolls? | What the fork does |
| --- | --- | --- | --- | --- |
| `flavor` | Pausing, looking, breathing, thinking, feeling. No change to the world. | "I paused a bit to look around" | no | Nothing. The model narrates it. |
| `intent` | A plan or decision about later: *will*, *going to*, *decide to*, *want to*. | "I decided that I will search them" | no | Nothing in v0. A plan is not an action. |
| `stance` | A change to `{{user}}`'s own readiness or posture. | "Raising my rifle" | no | A free action (§2.7). Checks it's possible, then records the stance and shows it on the HUD. |
| `move` | Entering or leaving a distinct place: a room, a building, a street, an area. | "I entered apartment 202" | **yes** | Commits the new location, makes the **arrival roll** (§2.5), and offers the place's HUD actions (search, trade). |
| `attempt` | An action whose outcome is uncertain and matters: against resistance, risk, or opposition. | "I force the door", "I sneak past", "I shoot it" | **yes** | Rolls. How the check is chosen and resolved is the core roll and math (§1, placeholder). |
| `use` | A deterministic action with an item or the party's own gear. | "I drink a dressing", "I swap magazines", "I equip the axe" | usually no | Runs the legality check (`OUTCOME_AUTHORITY.md` §4.1a), then commits. Rolls only where the contract already asks for a check (refill, `RPG_STATS.md` §3.8.4). |
| `search` | Searching a place for things. | "I search the kitchen" | no, by itself | Brings up the matching search action (`RPG_STATS.md` §3.12). The table rolls only when the player chooses it. |
| `speech` | Words `{{user}}` says, including instructions to allies and requests to trade. | "Anyone in here?", "Maya, cover the stairs" | no | Nothing by default. A line meant to make someone do something they otherwise wouldn't (persuade, lie, intimidate) is an `attempt`. A trade request to a vendor brings up the trade action (`RPG_STATS.md` §3.10.3). |

A beat that fits no kind is `flavor`. The safe failure is "nothing happens
mechanically", never a spurious roll.

### 2.4 Mood decides the kind, tense doesn't

Players write in whatever tense they like, most often the past. **Tense never
changes the kind.** "I entered", "I enter", and "Entering," are all a `move`
happening now. **Grammatical mood does:** "I will search them", "I decided to
search them", "I'm going to check the bedroom" are `intent`, while "I searched
the kitchen" is a `search`.

A clause that states its own result ("I shoot him and he drops dead") is an
`attempt` for the first half. The declared result is not a beat. The fork
ignores it and the roll decides (`OUTCOME_AUTHORITY.md` §3.4). The beat carries
a flag saying a result was declared, so the engine block can hold the line.

### 2.5 When a roll happens

**A beat rolls only when its outcome is uncertain and something rides on it.**
That leaves exactly two sources of rolls:

1. **The player's `attempt`.** `{{user}}` tries something that could go either
   way.
2. **The world's response to a `move`: the arrival roll.** Arriving somewhere
   new raises the question of what's there: nothing, a Shambler behind the
   door, a frightened survivor. The fork rolls it on entry.

Everything else is free. Looking around never rolls, because what there is to
see was set by the last arrival roll; looking is how the player finds out.

**Arrival needs authored data that doesn't exist yet.** The fork can only roll
what's in a place if the world says what places hold: an encounter chance per
kind of place, most likely as lines on the scavenge tables (`RPG_STATS.md`
§3.12), referencing bestiary entries. That field belongs in `RPG_STATS.md` and
is not specified there yet (§2.13). Until it is, a `move` commits the location
and offers the place's actions, and makes no arrival roll.

### 2.6 Order and cut points

Beats resolve in the order the player wrote them, all before the main model
generates.

- Free beats (`flavor`, `intent`, `stance`, `use`, `search`, `speech`) resolve
  immediately and in order.
- **A rolled beat (`move`, `attempt`) is a cut point.** If the roll leaves the
  rest of the message's premise intact — an `attempt` that succeeds, an arrival
  that turns up nothing — the fork carries on to the next beat. On anything
  else (a partial, a fail, an encounter), **the turn ends at that beat.** The
  later beats are not carried out and are not queued; the player decides again
  once they see what happened.
- The fork tells the model where the turn ends. The model narrates the beats up
  to the cut and its outcome, then stops. It does not narrate the beats past
  the cut as if they happened.

"I enter 202 and check the bedroom" checks the bedroom only if 202 is quiet. If
a Shambler is behind the door, the turn ends in the doorway.

### 2.7 Free actions and stance

`stance` and `use` are **free actions**: no roll, because nothing about them is
uncertain. A free action is still an attempt, not a state write
(`OUTCOME_AUTHORITY.md` §2). The fork checks it can happen, then commits it. "I
raise my rifle" with no rifle equipped is caught by the legality check like any
other possession claim, and the model is given the fact to write around.

Free applies **outside an encounter.** During one, how long an action takes and
whether it can be interrupted is a question of time and combat (§1,
placeholder), and the fork may resolve a free action as an `attempt` there.

**Stance** is short-lived state the fork tracks for `{{user}}`. v0 vocabulary:

| Stance | Means | Example |
| --- | --- | --- |
| `ready` | Weapon raised, alert, braced for trouble. | "Raising my rifle" |
| `quiet` | Moving carefully, keeping noise down. | "I slip in quietly" |
| `hidden` | In cover or concealment, trying not to be seen. | "I duck behind the counter" |
| `at_ease` | Clears the stance: weapon lowered, guard down. | "I lower the rifle" |

A stance lasts until it's changed, the location changes, or an encounter ends.
It shows on the HUD as a badge. What it does to a roll — `ready` helping the
first shot, `quiet` helping an arrival roll go unnoticed — is a modifier (§1,
placeholder). A stance word in a `move` beat ("I slip into 202 quietly") sets
the stance first, then moves, so it applies to the arrival roll.

An unrecognised stance is ignored. Whether a world may author its own stances
(`warded`, `in formation`) is open (§2.13).

### 2.8 Automatic rolls and explicit actions

Two rules sit side by side and are deliberately different:

- **The arrival roll is automatic.** It is the world reacting to a `move`. If it
  waited for the player to press something, the model would fill the gap by
  deciding what's behind the door itself.
- **The search roll waits for the player** (`RPG_STATS.md` §3.12). A search is
  the player claiming a reward, and which table applies is a choice. Prose only
  surfaces the action.

The same line applies to anything later: rolls that are the **world's
response** are automatic, rolls that are the **player claiming a benefit** go
through an explicit HUD action.

### 2.9 The beat pass

Splitting and labeling is a small, cheap model call made before generation: the
**beat pass**. It is a second small-model job, separate from the object
classification pass (`OUTCOME_AUTHORITY.md` §4.1b), with the same discipline:
**it labels, it never decides.** It does not judge whether `{{user}}` can do
something, whether it succeeds, or what is in a place. The fork does all of that
deterministically.

- **Input:** `{{user}}`'s message, the current location, `{{user}}`'s equipped
  items by name and type, the names of characters present, and this vocabulary.
- **Output:** the beats in order, each with its kind and only the fields that
  kind needs:

  ```jsonc
  { "beats": [
    { "text": "I paused a bit to look around",                  "kind": "flavor" },
    { "text": "I decided that I will search them for supplies", "kind": "intent" },
    { "text": "Raising my rifle",                               "kind": "stance", "stance": "ready", "object": "rifle" },
    { "text": "I entered one of the apartments. Apartment 202", "kind": "move",   "to": "Apartment 202" }
  ] }
  ```

  Per kind: `stance` carries `stance` and, if a weapon is named, `object`;
  `move` carries `to`; `attempt` carries `target` if there is one and
  `declaresResult: true` when the clause stated its own outcome (§2.4); `use`
  carries `item`; `search` carries `place`; `speech` carries `to` if it
  addresses someone. Objects are matched to the inventory by type, as in
  `OUTCOME_AUTHORITY.md` §3.1, and unknown objects go to the §4.1b classifier.
- **Output that doesn't parse, or a kind outside the vocabulary,** makes that
  beat `flavor`.

### 2.10 Showing and correcting the parse

The HUD shows the parse next to the message: free beats greyed, a stance as a
badge, each rolled beat with its result. The player can correct a beat the pass
misread ("I only looked in, I didn't enter"). That is a correction of parsing,
not of outcome (`OUTCOME_AUTHORITY.md` §4.3):

- A correction that changes a rolled beat's kind or target voids its roll, and
  the corrected beat resolves fresh.
- A correction that leaves the kind and target the same keeps the pinned roll.
  Relabeling a beat is not a way to re-roll it.

### 2.11 Worked example

The message from §2.1, in the `RPG_STATS.md` §8 zombie world. `{{user}}` starts
there with a Glock; assume they have since picked up the C8 carbine
(`c8_carbine`, type `firearm.rifle`), have it equipped, and are standing in a hallway:

| # | Beat | Kind | Fork action |
| --- | --- | --- | --- |
| 1 | "I paused a bit to look around" | `flavor` | none |
| 2 | "I decided that I will search them for supplies" | `intent` | none |
| 3 | "Raising my rifle" | `stance: ready` | "rifle" matches the equipped `firearm.rifle` → stance `ready`, HUD badge |
| 4 | "I entered … Apartment 202" | `move` | Location → "Apartment 202"; arrival roll; [Search Apartment] offered |

Two possible results for beat 4:

- **Arrival: nothing.** The model narrates an empty unit, rifle up, and the HUD
  shows [Search Apartment]. The player taps it next turn or writes something
  else.
- **Arrival: one Shambler, inside, alerted.** The turn ends at the doorway. The
  model narrates the Shambler and stops. The `ready` stance applies to whatever
  the player does next. No search is offered while the encounter runs.

### 2.12 Graceful degradation

- **No beat pass** (disabled, or the small model is unavailable): no automatic
  rolls. The main model handles the message under the existing rules
  (`protagonist_jeopardy`'s "a stated attempt is an attempt"), and HUD actions
  still work when chosen by hand.
- **No location signal:** a `move` can't commit a location. No arrival roll,
  no place actions; the manual "Search as…" choice still works.
- **No encounter data** for the place: the location commits and actions are
  offered, with no arrival roll (§2.5).
- **No `[[RPG_STATS]]` carrier:** no beat pass at all. Nothing in this section
  applies to a world without stats.

### 2.13 Open questions

- **Encounter data.** The shape of the per-place encounter chance that the
  arrival roll needs, and whether it lives on the scavenge tables or on its own.
  An `RPG_STATS.md` field; its own PR.
- **Re-entry.** Does going back into a place already visited roll arrival again
  (the world moved on) or not (it was cleared)? Possibly a per-table setting,
  like `depletes`.
- **Rolls per turn.** Whether a message can trigger any number of rolls, as
  long as each one leaves the premise intact, or whether there is a cap.
- **World-authored stances.** Whether `system` in `RPG_STATS.md` may add
  stances to the v0 four, and how a stance's modifier is declared.
- **Intent with mechanics.** Whether a stated plan ("search all four") should
  queue HUD actions or stay narrative only.
- **Time in free beats.** Whether "I paused a bit" or "I wait an hour" should
  advance time, once time exists (§1).

---

## 3. Boundary with the producer

World Forge authors **starting values and world data** (stats, items, sheets,
bestiary, vendors, scavenge tables). It never authors resolution rules, never
emits roll logic, and carries no carrier for this contract. If resolution needs
a new piece of authored world data (a difficulty table, a weapon's damage
range, an encounter chance per kind of place), that field is added to
`RPG_STATS.md` and produced there; this document defines only how the engine
uses it.

## 4. Relationship to the other contracts

| Concern | Governed by |
| --- | --- |
| What exists: stats, items, sheets, bestiary, economy | `RPG_STATS.md` (Draft) |
| Who decides: attempts vs. results, pinned rolls, legality | `OUTCOME_AUTHORITY.md` (Draft) |
| How an attempt resolves: beats, dice, math, modifiers, parsing | this document (§2 Draft, rest Placeholder) |
| Stateless narrative roll tables | `DICE_ORACLE.md` |
