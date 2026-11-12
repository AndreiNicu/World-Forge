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
  which beats roll, which bring up HUD actions, what the player may and may not
  declare, and how the message is displayed and sent. **§2, Draft.** How the main
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
state, rolls, or brings up a HUD action. A clause that describes the world
rather than something `{{user}}` does ("There were 4 apartments", "The apartment
was empty") is a `claim` beat (§2.4a).

A clause that restates or emphasizes the previous beat is part of that beat, not
a new one. "I stabbed the zombie. Stabbed him good." is one stab and one roll.

Only `{{user}}` makes beats. A clause about another character's action depends
on who they are:

- **A party member** (a sheet with `party: true`, `RPG_STATS.md` §3.4). Directing
  companions is ordinary play, so "Maya, cover the stairs", "Maya searches the
  kitchen", and "We split up" are all **instructions** from `{{user}}`: a
  `speech` beat with `instruction: true`, whether spoken or narrated. It stays
  in the model's copy. Whether the ally does it is the world's response, and if
  she does something a roll owns (a search), it goes through the same action
  `{{user}}`'s would.
- **Anyone else.** "Sal agrees to the price" is a `claim` about another
  character (`npc`, §2.4a), and the world decides what they do.

**Not every clause that names an action is one.**

- **Negated actions** ("I don't go in yet", "I hold my fire") are `flavor`. A
  pass that keys on the verb would roll arrival for a door the player chose not
  to open.
- **Conditionals** ("If anything moves in there, I shoot it") describe a plan:
  `intent`. One that describes readiness also sets stance `ready` (§2.7).
  Whether the fork fires it when the condition happens is open (§2.13).
- **Questions to the narrator** ("Is there anything useful in the room?") are
  perception: `flavor`. The answer comes from the state
  (`OUTCOME_AUTHORITY.md` §5): what's in plain sight, and for a place not yet
  searched, the search action rather than a list of contents.

**Roleplay formatting.** The pass reads the three common conventions:

- `"Quoted text"` is what `{{user}}` says: `speech`. Its content is never
  checked for claims (§2.4a). `{{user}}` can lie or be wrong, and it is the
  world that answers that, not the parse.
- `*Asterisk text*` is action or narration, read like any other prose.
- Out-of-character text (`(OOC: …)`, `((…))`, `[OOC]`) is not part of the
  fiction. The pass skips it: no beats, never marked or folded. It reaches the
  model unchanged, as a note to the narrator (`OUTCOME_AUTHORITY.md` §1.2).

### 2.3 The vocabulary

| Kind | What it is | Example | Rolls? | What the fork does |
| --- | --- | --- | --- | --- |
| `flavor` | Pausing, looking around or looking for something, breathing, thinking, feeling; negated actions and questions to the narrator (§2.2). No change to the world. What `{{user}}` perceives *in* the world is a `claim` (§2.4a). | "I paused a bit to look around", "looking if there was anything to loot", "I don't go in yet" | no | Nothing. The model narrates it. |
| `intent` | A plan or decision about later: *will*, *going to*, *decide to*, *want to*; and conditionals (§2.2). | "I decided that I will search them", "If anything moves, I shoot it" | no | Nothing in v0. A plan is not an action. A conditional that describes readiness sets stance `ready`. |
| `stance` | A change to `{{user}}`'s own readiness or posture. | "Raising my rifle" | no | A free action (§2.7). Checks it's possible, then records the stance and shows it on the HUD. |
| `move` | Entering or leaving a distinct place: a room, a building, a street, an area. | "I entered apartment 202" | **yes** | Commits the new location, makes the **arrival roll** (§2.5), and offers the place's HUD actions (search, trade). |
| `attempt` | An action whose outcome is uncertain and matters: against resistance, risk, or opposition. | "I force the door", "I sneak past", "I fire three shots" | **yes** | Rolls. How the check is chosen and resolved is the core roll and math (§1, placeholder). A repeated action carries a `count` (§2.9). |
| `use` | A deterministic action with an item or the party's own gear, including taking something a roll placed and searching a defeated enemy. | "I drink a dressing", "I swap magazines", "I take the shotgun it dropped", "I go through his pockets" | usually no | Runs the legality check (`OUTCOME_AUTHORITY.md` §4.1a), then commits. Rolls only where the contract already asks for a check (refill, `RPG_STATS.md` §3.8.4). Taking an item no roll placed becomes a `search`; searching a body takes the loot its defeat rolled (§2.4a). |
| `search` | A committed search of a **place**: search, rummage, go through, check. | "I search the kitchen", "I check the cruiser" | no, by itself | Brings up the matching search action (`RPG_STATS.md` §3.12) and ends the turn there (§2.6). The table rolls only when the player chooses it. Looking around is `flavor`; searching a body is a `use`. |
| `speech` | Words `{{user}}` says, quoted or reported, and gestures to someone; instructions to party members, spoken or narrated (§2.2); offers to trade. | "Anyone in here?", "Maya, cover the stairs", "I wave her over" | no | Nothing by default; quoted words are never checked for claims. A line meant to make someone do something they otherwise wouldn't (persuade, lie, intimidate) is an `attempt`. A trade offer brings up the trade action with the offer filled in and commits only when confirmed (§2.8). Haggling stays `speech` until haggling exists (`RPG_STATS.md` §7). |
| `claim` | A statement about the world rather than something `{{user}}` does: who's there, what a place holds, how something turned out, what someone else decided, or plain scenery. | "There were 4 apartments", "The apartment was empty" | no | Scenery passes through. Anything else is ignored, marked *Not confirmed*, and left out of what the model is sent (§2.4a, §2.10). |
| `wait` | Time passing: resting, sleeping, waiting, holing up. | "We hole up for the night", "I wait an hour" | **yes**, once encounter data exists | Makes the **time roll** for something finding the party (§2.5), and advances time once time exists (§1). A cut point when the roll interrupts (§2.6). |

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
a flag saying a result was declared, so the engine block can hold the line, and
the declared half is marked and left out of the model's copy exactly like a
claim (§2.10). That includes results stated in a separate sentence ("It went
down in a blink") and results folded into the action's wording ("three shots
*into* the zombie").

### 2.4a Claims — decorate, don't decide

Players co-author, and the scenery they add makes play better: the layout, the
dust, the smell, "there were 4 apartments." But a player can also write the
world's side of the turn: what's in a room, how something turned out, what
someone else decided. One rule covers it (`OUTCOME_AUTHORITY.md` §3.5):

> **If the fork rolls it or tracks it, the player can't declare it.**

A clause that says something about the world, rather than something `{{user}}`
does, is a `claim` beat, tagged with what it's about:

| `about` | The player declares… | Example | What the fork does |
| --- | --- | --- | --- |
| `presence` | Who or what is in a place, or that nothing is | "There was nothing in the apartment" | Ignored. The arrival roll decides. |
| `contents` | What a place holds, when the catalog covers it | "…but a box of 9mm ammo" | Ignored. Only a roll places catalog items. |
| `outcome` | How something already in motion turns out, or a detail that would decide an outcome | "The Shambler collapsed", "There's a back door" | Ignored. State and rolls decide; until resolution covers it, the main model judges. |
| `npc` | What a character outside the party decides, does, or feels (a party member's action is an instruction, §2.2) | "Sal agrees to the price", "The survivor believes me" | Ignored. The world answers. |
| `state` | A number or possession the fork tracks for `{{user}}` or the party: rounds, HP, what's in the pack | "…and it clicked empty", "I'm barely scratched", "I still had two mags" | Ignored. The fork's numbers win (`OUTCOME_AUTHORITY.md` §3.1, §3.3). |
| `scenery` | Detail nothing rides on | "There were 4 apartments", "Dust everywhere" | Passed through, like `flavor`. |

Ignored claims are marked *Not confirmed* in the chat and left out of the copy
of the message sent to the model (§2.10). A player stating the result of
`{{user}}`'s own attempt is not a `claim`; it is the `declaresResult` flag on
that `attempt` (§2.4).

**Quoted speech is exempt.** `"It's clear, nothing in here!"` is `{{user}}`'s
line, not a claim about the room. It is never marked or left out. If it's wrong
or a lie, the world answers that in the fiction.

**The gray case.** "There's a back door; I slip out." No roll owns exits, but the
detail would decide whether `{{user}}` gets away. A declared detail that would
change an outcome (an exit, a weapon to hand, a hiding place while something is
hunting `{{user}}`) is tagged `outcome`, not `scenery`. When the pass genuinely
can't tell, `scenery` is the safe failure: the model still treats the clause as
a proposal only (`OUTCOME_AUTHORITY.md` §5), and nothing it narrates can mint a
catalog item or override state.

**Perception counts as a claim.** "I thought I heard noises upstairs" describes
the world through `{{user}}`'s senses. `{{user}}`'s thoughts and feelings are
the player's, but what is actually upstairs is the world's, and a model handed
"noises upstairs" will put something there: the model as encounter table again.
A perception of something in the world is a `claim` (usually `presence`),
hedged or not. Acting on it stays the player's choice: "I went to investigate"
is a `move` that rolls arrival upstairs like any other, and that roll decides
whether anything made a noise.

**Beats that depend on a claim resolve against the state.** "I picked it up,"
where "it" is a box only the player declared, is a take of something no roll
placed. A take is a `use`. The fork checks whether a roll placed that item here:
a search result, loot from a body, something a vendor or an ally handed over.
If the catalog covers the item (by name, or by type as in
`OUTCOME_AUTHORITY.md` §3.1) and no roll placed one, the beat becomes a
`search`: nothing is committed, the place's search action is offered, and the
turn ends there (§2.6). Picking up uncatalogued scenery (a brick, a chair leg)
is fine and carries no stats (`OUTCOME_AUTHORITY.md` §3.2).

**Searching a body takes what the defeat rolled.** Bestiary loot rolls when an
instance is defeated (`RPG_STATS.md` §3.5), so a body already holds whatever it
holds. "I search him", aimed at a defeated enemy, is a `use` that takes that
loot: no new roll, no search action, no cut. Carry limits apply as to any take.
Aimed at an enemy that isn't defeated, the legality check catches it ("it's
still moving"). `search` is for places.

### 2.5 When a roll happens

**A beat rolls only when its outcome is uncertain and something rides on it.**
That leaves exactly two sources of rolls:

1. **The player's `attempt`.** `{{user}}` tries something that could go either
   way.
2. **The world's response to `{{user}}` being somewhere.** Arriving raises the
   question of what's there: nothing, a Shambler behind the door, a frightened
   survivor. That is the **arrival roll** on a `move`. Staying raises the
   question of what comes: the **time roll** on a `wait` ("we hole up for the
   night"), its chance growing with the duration. The fork rolls both
   automatically.

Everything else is free. Looking around never rolls, because what there is to
see was set by the last arrival roll; looking is how the player finds out.

**Both need authored data that doesn't exist yet.** The fork can only roll
what's in a place, or what finds the party there, if the world says so: an
encounter chance per kind of place (and, for waiting, per span of time), most
likely as lines on the scavenge tables (`RPG_STATS.md` §3.12), referencing
bestiary entries. That field belongs in `RPG_STATS.md` and is not specified
there yet (§2.13). Until it is, a `move` commits the location and offers the
place's actions with no arrival roll, and a `wait` passes without one.

### 2.6 Order and cut points

Beats resolve in the order the player wrote them, all before the main model
generates.

- Free beats (`flavor`, `intent`, `stance`, `use`, `speech`, `claim`) resolve
  immediately and in order.
- **A rolled beat (`move`, `attempt`, `wait`) is a cut point.** If the roll
  leaves the rest of the message's premise intact — an `attempt` that succeeds,
  an arrival that turns up nothing, a night that passes quietly — the fork
  carries on to the next beat. On anything else (a partial, a fail, an
  encounter), **the turn ends at that beat.** The
  later beats are not carried out and are not queued; the player decides again
  once they see what happened.
- **Inside an encounter, a failed `attempt` doesn't cut.** Missing a shot
  doesn't stop `{{user}}` reloading. The beats resolve in order, and a beat that
  depended on the failed one is caught by the legality check instead: searching
  a Shambler that didn't go down fails because it isn't defeated. How many
  actions fit in one turn of a fight is a question of time and combat (§1,
  placeholder); until that exists, the fork resolves the beats in order and the
  model narrates the enemy's response after them. An arrival roll that starts an
  encounter still cuts: the fight begins at that beat.
- **A `search` beat is always a cut point.** Its roll waits for the player to
  choose the search action (§2.8), so the turn ends as `{{user}}` starts to
  look. "I search the kitchen and head back out" searches nothing yet and
  doesn't leave; the search action is offered and the player picks up from
  there.
- Beats past a cut are marked *Not reached* and left out of the copy of the
  message the model is sent (§2.10).
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

- **Trades wait for the player too.** A trade offered in prose ("I offer him
  my Glock and 200 bucks") brings up the trade action with the offer filled in,
  and commits only when the player confirms it there (`RPG_STATS.md` §3.10.3).
  A trade is a benefit claimed, and prose can't settle a price.

The same line applies to anything later: rolls that are the **world's
response** are automatic (arrival, time), and anything that is the **player
claiming a benefit** goes through an explicit HUD action (searches, trades).

### 2.9 The beat pass

Splitting and labeling is a small, cheap model call made before generation: the
**beat pass**. It is a second small-model job, separate from the object
classification pass (`OUTCOME_AUTHORITY.md` §4.1b), with the same discipline:
**it labels, it never decides.** It does not judge whether `{{user}}` can do
something, whether it succeeds, or what is in a place. The fork does all of that
deterministically.

- **Input:** `{{user}}`'s message, the current location, `{{user}}`'s equipped
  items by name and type, the names of characters present and which of them are
  party members, and this vocabulary.
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
  `move` carries `to`; `attempt` carries `target` if there is one, `count`
  when the clause repeats the action ("three shots" is three trigger pulls),
  and `declaresResult: true` when the clause stated its own outcome (§2.4);
  `use` carries `item`; `search` carries `place`; `speech` carries `to` if it
  addresses someone, `quoted: true` for quoted words, and `instruction: true`
  for a direction to a party member (§2.2); `wait` carries `duration` as
  written ("for the night", "an hour"); `claim` carries `about` (§2.4a), and for `about: state`
  the quantity it contradicts where it can (`"rounds"`, `"hp"`). The pass
  labels a take as `use` either way. Whether a roll placed the item, and so
  whether the take becomes a `search`, is the fork's lookup, not the pass's
  judgment. Objects are matched to the inventory by type, as in
  `OUTCOME_AUTHORITY.md` §3.1, and unknown objects go to the §4.1b classifier.
- **The fork counts what it resolved, once.** Trigger pulls in the player's
  message are resolved and deducted before generation: `count` × the fire
  mode's `rounds`, stopping when the inserted magazine runs dry, so a third
  pull on two rounds clicks. The model's narration of those same shots is not
  counted again (`RPG_STATS.md` §4.6). Otherwise "I fire three times" followed by
  "she fires three times" takes six rounds.
- **Output that doesn't parse, or a kind outside the vocabulary,** makes that
  beat `flavor`.

### 2.10 Display, prompt, and corrections

**The stored message is never edited** (`OUTCOME_AUTHORITY.md` §4.1a). What the
player sees and what the model is sent are both derived from it:

| | Applied | Not reached | Not confirmed |
| --- | --- | --- | --- |
| **What** | Beats the turn resolved, and `scenery` claims | Everything after a cut point (§2.6) | `claim` beats other than `scenery`, declared results of `{{user}}`'s own attempts (§2.4), and takes turned into a search (§2.4a), before the cut |
| **Chat display** | Normal text | Folded under one faint line: *✂ Not reached — the turn ended at "I entered Apartment 202."* Expanding shows the original, with **Use as my next message** | Faintly marked in place, with the matching action beside it where there is one ([Search Apartment]) |
| **Sent to the model** | As written | Left out | Left out |

- **On every later turn too.** The cut and the omissions stay with the message,
  so history never shows the model a declared find or a declared empty room,
  and it can't drift toward them later.
- **Use as my next message** copies the folded text into the input box. What was
  cut is often still the plan once the danger is dealt with.
- **Labels describe, never judge.** *Not reached* and *Not confirmed*, never
  "illegal," "invalid," or anything that reads as an accusation. The dice
  getting there first is ordinary play.
- **The exact visuals are the fork's** (icons, wording, fading). The contract
  requires only that the original is kept, the two states are labeled
  distinctly, and the copy sent to the model leaves both out.
- **The HUD shows the parse** beside the message: a stance as a badge, each
  rolled beat with its result, the cut marker.

**Corrections.** The player can correct a beat the pass misread ("I only looked
in, I didn't enter"). That is a correction of parsing, not of outcome
(`OUTCOME_AUTHORITY.md` §4.3):

- A correction that changes a rolled beat's kind or target voids its roll, and
  the corrected beat resolves fresh.
- A correction that leaves the kind and target the same keeps the pinned roll.
  Relabeling a beat is not a way to re-roll it.
- A correction recomputes what is folded, marked, and sent. Because nothing was
  deleted, a misparse costs one click, not the player's prose.

### 2.11 Worked examples

**A. The message from §2.1,** in the `RPG_STATS.md` §8 zombie world. `{{user}}` starts
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

**B. The player writes the world's side.** The same message, with two sentences
added:

> "…Raising my rifle, I entered one of the apartments. Apartment 202. There was
> nothing in the apartment but a box of 9mm ammo. I picked it up for my M9
> Beretta."

Beats 1–4 as in A, then:

| # | Beat | Kind | Fork action |
| --- | --- | --- | --- |
| 5 | "There was nothing in the apartment" | `claim: presence` | Ignored; the arrival roll decides |
| 6 | "but a box of 9mm ammo" | `claim: contents` | Ignored; no roll placed it |
| 7 | "I picked it up for my M9 Beretta" | `use` → `search` | No roll placed 9mm here, so the take becomes a search and a cut point. "My M9 Beretta" matches the Glock by type (`OUTCOME_AUTHORITY.md` §3.1), so there is nothing to refuse, and the state block keeps calling it a Glock. |

- **Arrival: a Shambler.** Beat 4 is the cut. Beats 5–7 are folded as *Not
  reached*, and the model is sent the message up to "Apartment 202." It
  narrates the entry and the Shambler, and stops. The chat reads "…I entered
  one of the apartments. Apartment 202." followed by the Shambler, with the
  folded line underneath. The claims never come into play; the cut removed
  them. A claim placed before the `move` ("202 was empty, so I walked in")
  would be ignored anyway, and the roll would still produce the Shambler.
- **Arrival: nothing.** The turn continues past beat 4. Beats 5 and 6 are marked
  *Not confirmed*. Beat 7 becomes a search and ends the turn, so [Search
  Apartment] appears beside the marked clauses. The model is sent the message
  up to "Apartment 202," plus the arrival fact that the unit is empty and not
  yet searched. It narrates the empty unit, rifle up, `{{user}}` starting to
  look around, and stops. It neither confirms nor denies the box, because no
  search has been rolled. If the player taps [Search Apartment] and the table
  turns up 9mm, they have it then.

**C. Perception and a second move.**

> "I stepped into the house, looking if there was anything around to loot. I
> thought I heard noises upstairs and I went to investigate."

| # | Beat | Kind | Fork action |
| --- | --- | --- | --- |
| 1 | "I stepped into the house" | `move` | Location → the house; arrival roll; [Search House] offered |
| 2 | "looking if there was anything around to loot" | `flavor` | None. Looking isn't searching, and beat 1 already offered the search action. |
| 3 | "I thought I heard noises upstairs" | `claim: presence` | *Not confirmed*; nothing is upstairs until a roll says so |
| 4 | "I went to investigate" | `move` | Location → upstairs; arrival roll |

- **The house holds something:** the turn ends at the door; beats 2–4 are
  folded as *Not reached*.
- **The house is empty:** the turn continues. Beat 3 is marked, and beat 4 rolls
  arrival upstairs. Whatever that roll finds is what made the noise; if it finds
  nothing, there was no noise. The model never reads "noises upstairs," so it
  can't put something there itself. Two arrival rolls in one turn, for a place
  inside a place, are open questions (§2.13).

**D. Shots, a click, and a reload, in a fight.** `{{user}}` holds the §8 Glock
with **2 rounds** in the inserted magazine, an **empty** spare magazine, and 11
loose 9mm, and is fighting a Shambler.

> "I fired 3 more shots into the zombie and clicked on quickly tried to reload."

| # | Beat | Kind | Fork action |
| --- | --- | --- | --- |
| 1 | "I fired 3 more shots into the zombie" | `attempt`, `count: 3`, `declaresResult` | Three pulls; the Glock has no `fireModes`, so one round each (`RPG_STATS.md` §3.8.2). Two rounds fire, the third pull clicks. The fork deducts the two rounds now. "Into the zombie" is marked; the roll decides the hits. |
| 2 | "clicked" | `claim: state` | *Not confirmed*. It happens to match here; the fork's count is what's true either way. |
| 3 | "quickly tried to reload" | `use` (reload) | The legality check fails: no magazine in inventory holds a round. Fact injected: no loaded magazine, 11 loose rounds. |

A miss on beat 1 doesn't cut (§2.6, inside an encounter). The model narrates two
shots, the dry click, a hand finding only the empty spare, and the Shambler's
response. Its narration of the shots isn't counted again (§2.9). Refilling the
spare is its own action next turn, with its check (`RPG_STATS.md` §3.8.4). The
garbled "clicked on quickly" is the player's text; the pass labels what it can
and the rest falls to `flavor`.

**E. A kill, a body, and money the player found themselves.**

> "I stabbed the fucking zombie. Stabbed him good. It went down in a blink and I
> began searching him. I already found 50 bucks on him. He must've been someone
> before all of this."

| # | Beat | Kind | Fork action |
| --- | --- | --- | --- |
| 1 | "I stabbed the fucking zombie. Stabbed him good." | `attempt`, `declaresResult` | One stab, one roll. "Stabbed him good" restates beat 1 and merges into it (§2.2); "good" is a declared result, marked. |
| 2 | "It went down in a blink" | declared result of beat 1 | *Not confirmed*; the roll decides |
| 3 | "I began searching him" | `use` (search a body) | If the Shambler is defeated, takes the loot its defeat rolled; if not, fails the legality check |
| 4 | "I already found 50 bucks on him" | `claim: contents` | *Not confirmed*. The §8 Shambler's dollar line is a 30% chance of $2–18, so it could never have carried $50; and what it did carry was rolled at defeat, not declared. |
| 5 | "He must've been someone before all of this" | `flavor` | None |

- **The stab kills:** the body's rolled loot is taken: a field dressing on a 10%
  line, a few dollars on a 30% line, both, or nothing. The model narrates what
  was actually found, not $50, and the reflection reaches it in the player's
  own voice.
- **The stab fails:** no cut, because it's an encounter. The search fails the
  legality check because the Shambler is still moving, the $50 stays *Not
  confirmed*, and the reflection still applies; it never depended on the kill.

Examples F–K use the §8 starting state: the Glock with 9 rounds, an empty spare
magazine, 11 loose rounds, $35, no stim, no axe. Maya is in the party.

**F. A line that might be wrong.**

> `I shout to Maya, "It's clear, nothing in here!" and wave her over.`

| # | Beat | Kind | Fork action |
| --- | --- | --- | --- |
| 1 | `I shout to Maya, "It's clear, nothing in here!"` | `speech`, `to: Maya`, `quoted` | Sent as written. The words are never checked for claims. |
| 2 | "and wave her over" | `speech` (gesture), `instruction` | Sent. Whether Maya comes is the world's response. |

If `{{user}}` is wrong, it is the state that says so, not the parse. If they are
lying to her, Maya reacts to the lie.

**G. A door not opened, and a condition.**

> "I don't go in yet. If anything moves in there, I shoot it."

| # | Beat | Kind | Fork action |
| --- | --- | --- | --- |
| 1 | "I don't go in yet" | `flavor` (negated) | None: no `move`, no arrival roll |
| 2 | "If anything moves in there, I shoot it" | `intent` (conditional) | Stance `ready`. No shot is fired this turn. |

The model narrates `{{user}}` holding at the threshold, weapon up. Nothing inside
is decided until `{{user}}` goes in.

**H. Orders to the party and an offer to a trader.** At Okoro Gunsmithing in
Northgate (`RPG_STATS.md` §8), where the Beretta is $1,400.

> "We split up. Maya searches the kitchen while I haggle with the trader for the
> Beretta. I offer him my Glock and 200 bucks."

| # | Beat | Kind | Fork action |
| --- | --- | --- | --- |
| 1 | "We split up" | `speech`, `instruction` | Sent. Split parties are open (§2.13). |
| 2 | "Maya searches the kitchen" | `speech`, `instruction`, `to: Maya` | Sent. If she goes, her search is the kitchen's search action, chosen like any other. |
| 3 | "while I haggle with the trader for the Beretta" | `speech`, `to: Okoro` | Brings up the trade action. No price change: haggling isn't in v0. |
| 4 | "I offer him my Glock and 200 bucks" | `speech` (trade offer) | The legality check finds $35, not $200; the fact is injected. The trade action opens with the Glock offered. Nothing commits until confirmed. |

The model plays the haggle as conversation, with Okoro answering from his own
position. The $200 isn't there, and the HUD shows the offer can't reach $1,400.

**I. Downed, and reaching for things that aren't there.** `{{user}}` is downed
in a fight.

> "*Ignoring the pain* I get up, jab the military stim into my thigh and grab my
> axe."

| # | Beat | Kind | Fork action |
| --- | --- | --- | --- |
| 1 | "*Ignoring the pain*" | `flavor` | The player's feeling. It changes nothing the body can do. |
| 2 | "I get up" | `stance` (posture) | Fails: `downed` allows speaking and crawling only (`OUTCOME_AUTHORITY.md` §6). Attempted, and it fails. |
| 3 | "jab the military stim into my thigh" | `use` | Fails possession: there is no stim in inventory. It would not help anyway, because the stim raises max HP and is not a revive. |
| 4 | "grab my axe" | `use` | Fails possession: `{{user}}` has no axe. The fire axe is Maya's. |

Inside an encounter nothing cuts. The model narrates the try to rise and the
body refusing, a hand finding no injector and no axe in reach. Any cost comes
from the state, never from the number of failures.

**J. A night, then something that can't exist.**

> "We hole up in the apartment for the night. In the morning I pull out my
> lightsaber and cut through the barricade."

| # | Beat | Kind | Fork action |
| --- | --- | --- | --- |
| 1 | "We hole up in the apartment for the night" | `wait`, `duration: for the night` | Time roll, once encounter data exists. If something finds them, the turn ends in the night. |
| 2 | "In the morning I pull out my lightsaber" | `use` | Premise claim: the §4.1b classifier marks an energy weapon absent from this world, so it is refused in-story. Producing an uncatalogued object from `{{user}}`'s own pack fails anyway (`OUTCOME_AUTHORITY.md` §3.1). |
| 3 | "and cut through the barricade" | `attempt` | Depends on a tool that isn't there. The legality check fails it, and the barricade stands. |

If the night passes quietly, the model narrates the morning, a hand reaching for
something that was never there, and the barricade still standing.

**K. A note to the narrator, and a question.**

> "(OOC: can we skip ahead to the settlement?) Is there anything useful in the
> room?"

| # | Beat | Kind | Fork action |
| --- | --- | --- | --- |
| — | "(OOC: can we skip ahead to the settlement?)" | not a beat | Skipped. Reaches the model unchanged, as a note to the narrator. |
| 1 | "Is there anything useful in the room?" | `flavor` (question) | None. Answered from the state, with the room's search action offered. |

The model can describe what's in plain sight (a stripped bed, a cabinet hanging
open) and point at the search. It never answers "yes, a box of ammo." Whether a
skipped journey still rolls for encounters on the way is open (§2.13).

### 2.12 Graceful degradation

- **No beat pass** (disabled, or the small model is unavailable): no automatic
  rolls, and nothing is folded or marked; the message is sent as written. The
  main model handles it under the existing rules (`protagonist_jeopardy`'s "a
  stated attempt is an attempt", and the engine block's "the player's
  description of the world is a proposal", `OUTCOME_AUTHORITY.md` §5). HUD
  actions still work when chosen by hand.
- **No location signal:** a `move` can't commit a location. No arrival roll,
  no place actions; the manual "Search as…" choice still works.
- **No encounter data** for the place: the location commits and actions are
  offered, with no arrival roll (§2.5).
- **No `[[RPG_STATS]]` carrier:** no beat pass at all. Nothing in this section
  applies to a world without stats.

### 2.13 Open questions

- **Encounter data.** The shape of the per-place encounter chance that the
  arrival roll needs, the per-span-of-time chance the time roll needs, and
  whether they live on the scavenge tables or on their own. An `RPG_STATS.md`
  field; its own PR.
- **Re-entry.** Does going back into a place already visited roll arrival again
  (the world moved on) or not (it was cleared)? Possibly a per-table setting,
  like `depletes`.
- **Rolls per turn.** Whether a message can trigger any number of rolls, as
  long as each one leaves the premise intact, or whether there is a cap.
  Example C already rolls arrival twice in one turn.
- **Places inside places.** Upstairs in a house, the back room of a store:
  whether each is its own location with its own encounter chance and
  depletion, or shares its parent's. Tied to location identity
  (`RPG_STATS.md` §10).
- **World-authored stances.** Whether `system` in `RPG_STATS.md` may add
  stances to the v0 four, and how a stance's modifier is declared.
- **Intent with mechanics.** Whether a stated plan ("search all four") should
  queue HUD actions or stay narrative only.
- **Time in free beats.** Whether "I paused a bit" should advance time once
  time exists (§1). Longer spans ("I wait an hour") are a `wait` (§2.3).
- **Conditionals that fire.** Whether "If anything moves, I shoot it" should
  resolve automatically when the condition happens (overwatch), or stay a
  stance until the player acts. A question for combat (§1).
- **Split parties.** "We split up" puts party members in different places. The
  party currently has one location, so where Maya's search happens, and which
  place an arrival roll belongs to, needs a shape.
- **Skipped travel.** "Can we skip ahead to the settlement?" Whether a journey
  between known places rolls for encounters on the way, so that skipping isn't
  a free way past danger.
- **Claims the state agrees with.** "There was nothing in the apartment" is
  marked *Not confirmed* even when the arrival roll comes back empty. Whether
  the fork should unmark a claim the state happens to confirm, and how it
  would tell reliably, is open.
- **Improvised objects that share a catalog type.** A kitchen knife is
  `melee.blade`, like the catalog's combat knife. Whether taking one is free
  scenery or becomes a search prompt (§2.4a) is open. It matters once
  improvised weapons carry stats (`OUTCOME_AUTHORITY.md` §10.1b).

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
