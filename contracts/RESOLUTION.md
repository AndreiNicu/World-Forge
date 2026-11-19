# Resolution Contract — how attempts become outcomes

**Status:** Placeholder, with §2 (attempt interpretation), §3 (combat: the exchange, its budget, the enemy side, escape, and death), and §4 (the core roll) in Draft · **Version:** 0 · **Last updated:** 2026-11-19

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
> fork's to define. §2 (attempt interpretation), §3 (combat: how an exchange
> is budgeted, how the enemy side resolves, how a party gets away, and how characters die), and §4 (the core roll) were drafted early so the rest of the engine has a
> shape to build against. They are Drafts: nothing reads them, and the fork may
> revise them here as it builds. The other sections have no content yet. No
> agent spec references this document and nothing in this repo depends on it.

---

## 1. What will live here

The engine half of the RPG layer: everything between "`{{user}}` attempts
something" and "the fork commits a result."

- **The core roll** — the dice system, and how a roll maps onto the three
  outcome bands (success / partial / fail) that `RPG_STATS.md` and
  `OUTCOME_AUTHORITY.md` already use: **§4, Draft.**
- **The math** — how proficiency ranks and modifiers turn into odds;
  difficulty and who sets it: **§4.2, Draft**, calibrated in §4.6.
- **The modifier stack** — named sources (rank, weapon accuracy and condition,
  aim, stance, cover, range, stress, encumbrance tier), so the HUD can show why
  the odds are what they are: **§4.2, Draft.** Statuses beyond stress join it
  later.
- **Time** — what a beat or round is in chat play; initiative and turn order.
  *Placeholder.* What fits in one exchange, reload and refill included, is the
  budget (§3.2a); ambush and unaware enemies are awareness (§3.3a).
- **Combat** — the exchange and its budget, range bands, overwatch, and how
  enemies act and are narrated; awareness and ambush, suppression, standing
  orders, breaking contact, chases, terrain, stamina, and death: **§3,
  Draft.** Attack math, damage, and armor
  are in the core roll (§4.2–§4.3). What a fire mode does to a hit is still a
  placeholder.
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

A player's message is prose, and most of it needs no roll. Take:

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
state, rolls, or brings up a HUD action. **A kind is a route, and a beat never
changes kind once labeled.** What varies inside a kind (which item operation,
which stance axis, what a claim is about) is a field on the beat. A clause that
describes the world rather than something `{{user}}` does ("There were 4
apartments", "The apartment was empty") is a `claim` beat (§2.4a).

A clause that restates or emphasizes the previous beat is part of that beat, not
a new one. "I stabbed the zombie. Stabbed him good." is one stab and one roll.
Two kinds of clause attach the same way:

- **A speaker tag** ("I yelled at Jack", "I told the seller") is part of the
  quote it attributes.
- **A lead-in** that only introduces the next clause ("But then, it happened.",
  "Suddenly—") is part of the next beat and shares its fate: sent, marked, or
  folded with it. Sent on its own, a lead-in to an omitted clause is a
  cliffhanger, and the model fills it in itself.
- **Consecutive trade clauses to the same vendor** ("I haggle with the trader
  for the Beretta. I offer him my Glock and 200 bucks") are one `trade` beat
  and one offer.

Only `{{user}}` makes beats. A clause about another character's action depends
on who they are:

- **A party member** (a sheet with `party: true`, `RPG_STATS.md` §3.4). Directing
  companions is ordinary play, so "Maya, cover the stairs", "Maya searches the
  kitchen", and "We split up" are all **instructions** from `{{user}}`: a
  `speech` beat with `instruction: true`, whether spoken or narrated. It carries
  `asks`, the kind of beat the instruction would be if the ally did it
  (`search`, `move`, `check`, `stance`, `gear`). It stays in the model's copy.
  Whether the ally does it is the world's response, and if she does something a
  roll owns (a search), it goes through the same action `{{user}}`'s would. In
  a fight, the fork resolves it before generation (§3.5).
  **An instruction can't ask for what the ally's state forbids.** The fork runs
  the legality check for the asked kind against the ally's own sheet
  (`OUTCOME_AUTHORITY.md` §4.1a). "Maya shakes it off and gets up", with Maya
  downed, is an instruction asking for a `stance` her status rules out: the
  fact is injected and she stays down (`OUTCOME_AUTHORITY.md` §3.3).
- **Anyone else.** "Sal agrees to the price" is a `claim` about another
  character (`npc`, §2.4a), and the world decides what they do.

**Not every clause that names an action is one.**

- **Negated actions** ("I don't go in yet", "I hold my fire") are `flavor`. A
  pass that keys on the verb would roll arrival for a door the player chose not
  to open.
- **Conditionals** never carry out their action now. One that describes
  readiness ("If anything moves in there, I shoot it") is a `stance` beat:
  weapon `ready`, with the condition kept in `when` (§2.7). Any other ("If he
  agrees, I'll buy two") is a plan: `intent`. Whether the fork fires a
  readiness conditional when the condition happens is open (§2.13).
- **Travel along the way** ("I took a turn on the road", "we pass the gas
  station") is `flavor`. A `move` is arriving at a place, leaving one, or
  setting out for one. The road between two places is one journey (§2.5), not a
  new place at every bend. Changing distance to an enemy inside a fight ("I
  back away", "I rush him") is a `position` beat (§2.3).
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

Twelve kinds, grouped by the route each one takes.

| Kind | What it is | Example | Rolls? | What the fork does |
| --- | --- | --- | --- | --- |
| **Passed through** | | | | |
| `flavor` | Pausing, looking around or looking for something, breathing, thinking, feeling; negated actions, questions to the narrator, and travel along the way (§2.2). No change to the world. What `{{user}}` perceives *in* the world, or expects someone else to do, is a `claim` (§2.4a). | "I paused a bit to look around", "looking if there was anything to loot", "I don't go in yet" | no | Nothing. The model narrates it. A question to the narrator carries `question: true`, and the fork offers the place's search action beside the answer. |
| `intent` | A plan or decision about later: *will*, *going to*, *decide to*, *want to*; and conditionals that aren't about readiness (§2.2). | "I decided that I will search them", "If he agrees, I'll buy two" | no | Nothing in v0. A plan is not an action. |
| `speech` | Words `{{user}}` says, quoted or reported, and gestures to someone; instructions to party members, spoken or narrated (§2.2). | "Anyone in here?", "Maya, cover the stairs", "I wave her over" | no | Nothing by default; quoted words are never checked for claims. An instruction carries `asks`, and the fork checks it against the ally's own state (§2.2). A line meant to make someone do something they otherwise wouldn't (persuade, lie, intimidate) is labeled `check`, not `speech`; a line about buying, selling, or a price is labeled `trade`. |
| **Checked, then committed** | | | | |
| `stance` | A change to `{{user}}`'s own readiness or posture, on one of five axes (§2.7); and a conditional that describes readiness (§2.2). | "Raising my rifle", "I slip in quietly", "I get up", "If anything moves, I shoot it" | no | A free action (§2.7). Checks it's possible, then records the axis it names, leaves the others as they were, and shows it on the HUD. Readying a named weapon puts it in hand (`RPG_STATS.md` §3.11). |
| `gear` | A deterministic action with an item or the party's own gear. The beat names the operation in `op` (below). | "I drink a dressing", "I swap magazines", "I take the shotgun it dropped", "I go through his pockets", "I hand Maya the dressing" | only `refill` in an encounter | Runs the legality check for that `op` (`OUTCOME_AUTHORITY.md` §4.1a), then makes the matching commit (`RPG_STATS.md` §4.4). A `refill` inside an encounter makes the check `RPG_STATS.md` §3.8.4 asks for. A `take` of a catalog item no roll placed commits nothing and brings up the place's search action (§2.4a). |
| `position` | Inside an encounter, changing distance to an enemy without leaving the place: closing in, backing off, falling back across the room. | "I back away from it", "I rush him", "I fall back to the stairs" | only to disengage | Checks it's possible, then moves one range band toward the target or away, two with `dash` (§3.3). Backing away from an enemy engaged with you is disengaging, which is a check. Outside an encounter there are no bands, and the beat is `flavor`. |
| **The world's roll** | | | | |
| `move` | Entering or leaving a distinct place: a room, a building, a street, an area; or setting out for one it doesn't reach in the same beat, which starts a journey (§2.5). | "I entered apartment 202", "We drive back to camp" | **yes** | Commits the new location, makes the **arrival roll** (§2.5), and offers the place's HUD actions (search, trade). A journey makes the **journey roll** instead; arriving is its own `move`. |
| `wait` | Time passing: resting, sleeping, waiting, holing up. | "We hole up for the night", "I wait an hour" | **yes**, once encounter data exists | Makes the **time roll** for something finding the party (§2.5), and advances time once time exists (§1). A cut point when the roll interrupts (§2.6). |
| **The player's roll** | | | | |
| `check` | An action whose outcome is uncertain and matters: against resistance, risk, or opposition. Includes firing a weapon, using an ability, and talking someone into something. | "I force the door", "I sneak past", "I fire three shots", "I use Triage on Maya", "I talk the guard into letting me through" | **yes** | Runs the legality check (a loaded weapon, an ability's `cost`), then rolls. `with` names the item or ability the action uses; without one, the weapon in hand (§2.7). How the check is chosen and resolved is the core roll (§4). A repeated action carries a `count` (§2.9). |
| **An explicit action** | | | | |
| `search` | A committed search of a **place**: search, rummage, go through, check. | "I search the kitchen", "I check the cruiser" | no, by itself | Brings up the matching search action (`RPG_STATS.md` §3.12) and ends the turn there (§2.6). The table rolls only when the player chooses it. Looking around is `flavor`; searching a body is a `gear` beat (`op: loot`). |
| `trade` | An offer to buy, sell, or swap, and any argument about a price, spoken or narrated. | "I offer him my Glock and 200 bucks", "How about you drop the 50?" | no | Runs the legality check on what's offered, brings up the trade action with the offer filled in, and ends the turn there (§2.6). Nothing commits until the player confirms it (§2.8). The words stay in the model's copy as written. Haggling has no roll until it exists (`RPG_STATS.md` §7); the model is told the price stands (§2.8). |
| **Withheld, or answered by a roll** | | | | |
| `claim` | A statement about the world rather than something `{{user}}` does: who's there, what a place holds, how something turned out (the result of `{{user}}`'s own action included), what someone else decided, or plain scenery. | "There were 4 apartments", "The apartment was empty", "I heard a noise", "…and he drops dead" | only a perceived presence, which asks for the world's roll | Scenery passes through. A perceived presence asks for the roll that answers it. An opening is sent to the model as a proposal and ends the turn. Anything else is ignored, marked *Not confirmed*, and left out of what the model is sent (§2.4a, §2.10). |

A beat that fits no kind is `flavor`. The safe failure is "nothing happens
mechanically", never a spurious roll.

**`gear` operations.** `op` is a closed list, one per commit `RPG_STATS.md`
§4.4 defines:

| `op` | What it is | Example | Legality check |
| --- | --- | --- | --- |
| `consume` | Using up a consumable for its effects. | "I drink a dressing", "I take a bite of the biscuit" | Has one. |
| `equip` | Moving an item into or out of an equipment slot. | "I sling the shotgun", "I grab my axe" | Has one; meets its `requires`. |
| `reload` | Swapping the inserted magazine for a fuller one (`RPG_STATS.md` §3.8.4). | "I swap magazines" | A magazine in inventory holds a round. |
| `refill` | Pressing loose rounds into magazines, or into an `internal`-feed weapon. | "I thumb rounds into the spare" | Has loose rounds that fit. |
| `mode` | Switching fire mode (`RPG_STATS.md` §3.8.2). | "I flick it to burst" | The weapon has that mode. |
| `take` | Picking up something that's here. | "I take the shotgun it dropped" | A roll placed it here, or it's uncatalogued scenery; carry limit. |
| `loot` | Searching a defeated enemy. | "I go through his pockets" | The enemy is defeated; carry limit. |
| `drop` | Putting an item down. | "I leave the vest behind" | Has one. |
| `give` | Handing an item to a party member (`RPG_STATS.md` §3.13). | "I hand Maya the dressing" | Has one; she's here; her carry limit. |

An `op` outside the list makes the beat `flavor`. Readying a weapon that is
already in a slot ("I pull my gun") is a `stance`, not an `equip`: the beat pass
is given the equipped items, so it can tell the two apart (§2.9).

### 2.4 Mood decides the kind, tense doesn't

Players write in whatever tense they like, most often the past. **Tense never
changes the kind.** "I entered", "I enter", and "Entering," are all a `move`
happening now. **Grammatical mood does:** "I will search them", "I decided to
search them", "I'm going to check the bedroom" are `intent`, while "I searched
the kitchen" is a `search`.

A clause that states its own result ("I shoot him and he drops dead") is two
beats. The first half is a `check`. The declared result is a `claim` beat of
its own (`about: outcome`, `own: true`, §2.4a): the fork ignores it and the
roll decides (`OUTCOME_AUTHORITY.md` §3.4). The `check` also carries
`declaresResult: true`, so the engine block can hold the line. That covers
results stated in a separate sentence ("It went down in a blink") and results
folded into the action's wording: "three shots *into* the zombie" splits into
the shots and "into the zombie". Because the declared half is its own beat, it
is marked and left out by the same rule as every other claim (§2.10), and no
beat is ever partly sent.

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
| `presence` | Who or what is in a place, or that nothing is | "There was nothing in the apartment" | Ignored. The arrival roll decides. A presence `{{user}}` perceives asks for that roll (below). |
| `contents` | What a place holds, when the catalog covers it | "…but a box of 9mm ammo" | Ignored. Only a roll places catalog items. |
| `outcome` | How something already in motion turns out. With `own: true`, the result of `{{user}}`'s own `check` (§2.4) | "The Shambler collapsed", "…and he drops dead" | Ignored. State and rolls decide. |
| `opening` | A detail no roll or state owns that would get `{{user}}` past something: an exit, a weapon to hand, a hiding place | "There's a back door" | Sent to the model as a proposal for it to judge; the turn ends there (below). |
| `npc` | What a character outside the party decides, does, or feels (a party member's action is an instruction, §2.2) | "Sal agrees to the price", "The survivor believes me" | Ignored. The world answers. |
| `state` | A number or possession the fork tracks for `{{user}}` or the party: rounds, HP, what's in the pack | "…and it clicked empty", "I'm barely scratched", "I still had two mags" | Ignored. The fork's numbers win (`OUTCOME_AUTHORITY.md` §3.1, §3.3). |
| `scenery` | Detail nothing rides on | "There were 4 apartments", "Dust everywhere" | Passed through, like `flavor`. |

Ignored claims are marked *Not confirmed* in the chat and left out of the copy
of the message sent to the model (§2.10). The result of `{{user}}`'s own
action is a claim like any other: `about: outcome` with `own: true` (§2.4).

These are the world declarations and result declarations of
`OUTCOME_AUTHORITY.md` §3.4–§3.5. Its other claims aren't `claim` beats:
possession and premise claims are caught by the legality check on whatever
beat names the object, and its §3 table maps all five.

**Quoted speech is exempt.** `"It's clear, nothing in here!"` is `{{user}}`'s
line, not a claim about the room. It is never marked or left out. If it's wrong
or a lie, the world answers that in the fiction.

**The gray case: an opening.** "There's a back door; I slip out." No roll owns
exits, but the detail would decide whether `{{user}}` gets away. A declared
detail that would get `{{user}}` past something (an exit, a weapon to hand, a
hiding place while something is hunting them) is tagged `opening`, not
`scenery`. Nothing in the fork can answer it, so the main model judges
(`OUTCOME_AUTHORITY.md` §3.5), and it can only judge what it is shown:

- The claim **stays in the model's copy**, with a fact beside it saying the
  detail is the player's proposal and not established.
- It is a **cut point** (§2.6). "I slip out" is *Not reached*: the fork won't
  commit a location through a door that may not exist. The model narrates
  whether the door is there, and the player acts on what they find.
- When the pass genuinely can't tell an opening from scenery, `scenery` is the
  safe failure: the model still treats the clause as a proposal only
  (`OUTCOME_AUTHORITY.md` §5), and nothing it narrates can mint a catalog item
  or override state.

**Complications are scenery.** A handicap the player puts on `{{user}}`, about
something nothing tracks ("in the dark", "blindly", "my hands were shaking"),
decides nothing in their favor. It is `scenery` and passes through. Dropping it
would delete a difficulty the player chose.

**Perception counts as a claim.** "I thought I heard noises upstairs" describes
the world through `{{user}}`'s senses. `{{user}}`'s thoughts and feelings are
the player's, but what is actually upstairs is the world's, and a model handed
"noises upstairs" will put something there: the model as encounter table again.
A perception of something in the world is a `claim` (usually `presence`),
hedged or not.

**A perceived presence asks; it doesn't decide.** A noise, a grunt, movement in
the dark: the player is inviting the world in, and the world answers with a
roll it would make anyway (§2.5).

- **Here.** A presence perceived in the current place makes a short time roll,
  as for a brief `wait`. A roll that finds something starts an encounter, and
  the turn ends there (§2.6).
- **Somewhere else.** A presence perceived in a place `{{user}}` isn't in
  ("upstairs", "next door") makes that place's arrival roll now. The result is
  pinned to the place and used when `{{user}}` enters, so going to investigate
  doesn't roll again. Nothing has met `{{user}}` yet, so it doesn't cut.
- **The roll decides what; the player only prompted whether.** If it turns up
  something, that is what the player heard. The fork's own roll confirms the
  claim, so it stays in the model's copy as written. If it turns up nothing,
  the claim is marked *Not confirmed* and the model is told the place is quiet,
  so it can narrate the noise as nothing (the building settling).
- **Absence never asks.** "It was empty" and "nothing followed us" would shut
  the world out, and they stay ignored. A noise invites danger in; an absence
  claim tries to keep it out.
- **No new lever.** "I wait an hour" already calls a roll on demand, so hearing
  noises gets the player nothing the world wasn't already offering.
- **A place already rolled this turn** doesn't roll again. "There's movement in
  here," right after an arrival roll, is checked against that roll.
- **Without encounter data** (§2.5) there is no roll to ask for, so a perceived
  presence passes through to the model as a proposal, as it does today
  (`OUTCOME_AUTHORITY.md` §5). Leaving it out would only take away the
  player's co-authoring.

Acting on a perception stays the player's choice: "I went to investigate" is a
`move`, and it uses the pinned roll.

**So does expecting what someone else will do.** "Knowing he would be
sympathetic and give me the knives for 100" is `{{user}}`'s thought, but its
content is the vendor's decision. A thought, expectation, or hope about what a
character outside the party will decide or feel ("knowing he would", "sure
she'll", "hoping he'd agree") is a `claim: npc`, hedged or not. A model handed
the expectation reads it as the answer the player wants, which is the yield
reflex the posture contract exists to stop (producer `CLAUDE.md` principle
#13). A feeling with no one else's decision in it ("I was desperate", "I hated
asking") stays `flavor`.

**Beats that depend on a claim resolve against the state.** "I picked it up,"
where "it" is a box only the player declared, is a take of something no roll
placed. A take is a `gear` beat (`op: take`). The fork checks whether a roll
placed that item here: a search result, loot from a body, something a vendor or
an ally handed over. If the catalog covers the item (by name, or by type as in
`OUTCOME_AUTHORITY.md` §3.1) and no roll placed one, the take fails that
lookup: nothing is committed, the place's search action is offered, and the
turn ends there (§2.6). The beat is still a `gear` beat; it is the lookup that
failed, not the label that changed. Picking up uncatalogued scenery (a brick, a
chair leg) is fine and carries no stats (`OUTCOME_AUTHORITY.md` §3.2).

**Searching a body takes what the defeat rolled.** Bestiary loot rolls when an
instance is defeated (`RPG_STATS.md` §3.5), so a body already holds whatever it
holds. "I search him", aimed at a defeated enemy, is a `gear` beat (`op: loot`)
that takes that loot: no new roll, no search action, no cut. Carry limits apply
as to any take.
Aimed at an enemy that isn't defeated, the legality check catches it ("it's
still moving"). `search` is for places.

### 2.5 When a roll happens

**A beat rolls only when its outcome is uncertain and something rides on it.**
That leaves exactly two sources of rolls:

1. **The player's `check`.** `{{user}}` tries something that could go either
   way.
2. **The world's response to `{{user}}` being somewhere.** Arriving raises the
   question of what's there: nothing, a Shambler behind the door, a frightened
   survivor. That is the **arrival roll** on a `move`. Staying raises the
   question of what comes: the **time roll** on a `wait` ("we hole up for the
   night"), its chance growing with the duration. Travelling raises it too: the
   **journey roll** (below). The fork rolls all three automatically, along with
   the roll a perceived presence asks for (§2.4a).

Everything else is free. Looking around never rolls, because what there is to
see was set by the last arrival roll; looking is how the player finds out.

**Journeys.** The road between two places is neither arriving nor staying, and
a turn of the wheel isn't a place. So a journey rolls once, as a whole:

- A `move` toward a place it doesn't reach in the same beat ("we drive back to
  camp", "I head north to Northgate") starts a journey. The fork makes the
  journey roll there, using the time roll's mechanism, and commits the
  location as en route.
- Travel narrated along the way ("I took a turn on the road", "only 3 km more")
  is `flavor` or `scenery` and rolls nothing. The journey roll already covered
  the road.
- If the journey roll finds something, the turn ends on the road (§2.6). If not,
  the journey is quiet, however many messages the player spends on it.
- Arriving is its own `move`, with its own arrival roll.
- A skip the fork carries out ("(OOC: skip ahead to the settlement)") makes the
  journey roll first, then jumps to the arrival. A skip passes over the
  narration, never the road (`OUTCOME_AUTHORITY.md` §1.2).
- A journey already under way before any beat pass ran (a chat that opens on the
  road) has no journey roll. The next arrival rolls as usual.

How the chance scales (distance, duration, kind of route) is encounter data.
Distance isn't tracked in v0; once it is, a player's "only 3 km more" becomes
a `state` claim rather than `scenery`.

**All three need authored data that doesn't exist yet.** The fork can only roll
what's in a place, or what finds the party there or on the way, if the world
says so: an encounter chance per kind of place (and, for waiting and journeys,
per span of time or route), most likely as lines on the scavenge tables
(`RPG_STATS.md` §3.12), referencing bestiary entries. That field belongs in
`RPG_STATS.md` and is not specified there yet (`RPG_STATS.md` §10). Until it
is, a `move` commits the location and offers the place's actions with no
arrival roll, a `wait` passes without one, and a journey is quiet.

### 2.6 Order and cut points

Beats resolve in the order the player wrote them, all before the main model
generates.

- Free beats (`flavor`, `intent`, `speech`, `stance`, `gear`, `claim`) resolve
  immediately and in order. So does `position`, which rolls only to disengage
  (§3.3).
- **A rolled beat (`move`, `wait`, `check`) is a cut point.** If the roll
  leaves the rest of the message's premise intact — a `check` that succeeds,
  an arrival that turns up nothing, a night or a journey that passes quietly —
  the fork carries on to the next beat. On anything else (a partial, a fail, an
  encounter), **the turn ends at that beat.** The later beats are not carried
  out and are not queued; the player decides again once they see what
  happened.
- **Inside an encounter, a failed `check` doesn't cut.** Missing a shot
  doesn't stop `{{user}}` reloading. The beats resolve in order, and a beat that
  depended on the failed one is caught by the legality check instead: searching
  a Shambler that didn't go down fails because it isn't defeated. The fork then
  resolves the enemy side (§3.2), and the model narrates both. What does cut
  inside an encounter is the **exchange budget** (§3.2a): the first beat that
  doesn't fit ends the exchange, and it and everything after it are *Not
  reached*. An arrival roll that starts an encounter still cuts: the fight
  begins at that beat.
- **A perceived presence that rolls** (§2.4a) is a cut point when it's here and
  finds something: the encounter starts at that beat. One about somewhere else
  never cuts, because what it found is waiting there.
- **A `search` beat is always a cut point.** Its roll waits for the player to
  choose the search action (§2.8), so the turn ends as `{{user}}` starts to
  look. "I search the kitchen and head back out" searches nothing yet and
  doesn't leave; the search action is offered and the player picks up from
  there. A `gear` take of something no roll placed cuts the same way (§2.4a).
- **A `trade` beat is always a cut point**, for the same reason. The trade
  commits only when the player confirms it (§2.8), so "I buy the knives and
  head out" buys nothing yet and doesn't leave.
- **An `opening` claim is a cut point** (§2.4a). The model judges whether the
  detail is there, and the player acts on the answer.
- Beats past a cut are marked *Not reached* and left out of the copy of the
  message the model is sent (§2.10).
- The fork tells the model where the turn ends. The model narrates the beats up
  to the cut and its outcome, then stops. It does not narrate the beats past
  the cut as if they happened.

"I enter 202 and check the bedroom" checks the bedroom only if 202 is quiet. If
a Shambler is behind the door, the turn ends in the doorway.

### 2.7 Free actions and stance

`stance` and `gear` are **free actions**: no roll, because nothing about them is
uncertain. A free action is still an attempt in the sense of
`OUTCOME_AUTHORITY.md` §2, not a state write. The fork checks it can happen,
then commits it. "I raise my rifle" with no rifle equipped is caught by the
legality check like any other possession claim, and the model is given the fact
to write around.

Free applies **outside an encounter.** During one, every beat has a cost in the
exchange budget (§3.2a): readying the weapon already in hand is still free,
drawing a different one costs the move, and a refill costs the action and makes
its check. The beat's kind doesn't change.

**Stance** is short-lived state the fork tracks for `{{user}}`, on five
independent axes. A beat sets the axis it names and leaves the others alone:
"Raising my rifle, I slip quietly into 202" is weapon `ready` *and* noise
`quiet`.

| Axis | Values (default first) | Set by | Example |
| --- | --- | --- | --- |
| `weapon` | `lowered`, `ready`, `aimed` | Raising, drawing, or lowering a weapon; bracing for trouble; taking aim. `aimed` lasts until the next attack or the end of the exchange, then returns to `ready`. | "Raising my rifle", "I lower the rifle", "I take careful aim" |
| `noise` | `normal`, `quiet` | Moving carefully, keeping noise down. | "I slip in quietly" |
| `cover` | `exposed`, `hidden` | Getting into or out of cover or concealment. | "I duck behind the counter" |
| `posture` | `standing`, `prone` | Getting up, dropping down. | "I get up", "I drop flat" |
| `carrying` | `nobody`, a party member | Lifting a downed party member to carry them; putting them down (§3.7e). | "I haul Maya over my shoulder", "I set her down" |

- **`at_ease`** on the beat resets `weapon`, `noise`, and `cover` to their
  defaults ("I relax", "I let my guard down"). It doesn't change `posture`.
- **`weapon`, `noise`, and `cover` last** until they're changed, the location
  changes, or an encounter ends. **`posture` lasts** until it's changed.
  **`carrying` lasts** until the carried character is put down, gets up, or
  dies. A
  status can pin it: `downed` holds `posture` at `prone`
  (`OUTCOME_AUTHORITY.md` §6), so "I get up" while downed is a `stance` beat
  that fails the legality check. It is attempted, and it fails.
- **The weapon in hand.** A `stance` beat that readies a named weapon carries it
  in `object`. The fork matches it to an equipped item by type and records that
  slot as the weapon in hand (`RPG_STATS.md` §3.11). A `check` that fires or
  strikes without naming a weapon uses the one in hand; with nothing in hand,
  the only equipped weapon that fits, if there is exactly one.
- **A conditional** ("If anything moves in there, I shoot it") sets weapon
  `ready` and keeps the condition in `when`. No shot is fired (§2.13).
- Each non-default axis shows on the HUD as a badge. What it does to a roll —
  `ready` helping the first shot, `quiet` helping an arrival roll go unnoticed —
  is a modifier (§4.2). A stance word in a `move` beat ("I slip into
  202 quietly") sets the stance first, then moves, so it applies to the arrival
  roll.

An unrecognised axis or value is ignored. Whether a world may author its own
axes or values (`warded`, `in formation`) is open (`RPG_STATS.md` §10).

### 2.8 Automatic rolls and explicit actions

Two rules sit side by side and are deliberately different:

- **The arrival roll is automatic.** It is the world reacting to a `move`. If it
  waited for the player to press something, the model would fill the gap by
  deciding what's behind the door itself.
- **The search roll waits for the player** (`RPG_STATS.md` §3.12). A search is
  the player claiming a reward, and which table applies is a choice. Prose only
  surfaces the action.

- **Trades wait for the player too.** A `trade` beat ("I offer him my Glock and
  200 bucks") brings up the trade action with the offer filled in, and commits
  only when the player confirms it there (`RPG_STATS.md` §3.10.3). A trade is a
  benefit claimed, and prose can't settle a price.
- **The price stands.** An offer below the price, however it's argued, is
  haggling: no roll in v0, and the model is told the price stands. The vendor
  answers in their own voice (`note`), and can be sympathetic and still say no.
  Without the fact, the fiction can agree to a price the trade action won't
  honour.

The same line applies to anything later: rolls that are the **world's
response** are automatic (arrival, time, journey, and the roll a perceived
presence asks for), and anything that is the **player
claiming a benefit** goes through an explicit HUD action (searches, trades).

### 2.9 The beat pass

Splitting and labeling is a small, cheap model call made before generation: the
**beat pass**. It is a second small-model job, separate from the object
classification pass (`OUTCOME_AUTHORITY.md` §4.1b), with the same discipline:
**it labels, it never decides.** It does not judge whether `{{user}}` can do
something, whether it succeeds, or what is in a place. The fork does all of that
deterministically.

- **Input:** `{{user}}`'s message, the current location, `{{user}}`'s equipped
  items by name and type, their abilities by name, the names of characters
  present and which of them are party members, and this vocabulary.
- **Output:** the beats in order, each with its kind and only the fields that
  kind needs:

  ```jsonc
  { "beats": [
    { "text": "I paused a bit to look around",                  "kind": "flavor" },
    { "text": "I decided that I will search them for supplies", "kind": "intent" },
    { "text": "Raising my rifle",                               "kind": "stance", "weapon": "ready", "object": "rifle" },
    { "text": "I entered one of the apartments. Apartment 202", "kind": "move",   "to": "Apartment 202" }
  ] }
  ```

  Fields per kind:

  | Kind | Fields |
  | --- | --- |
  | `flavor` | `question: true` for a question to the narrator. |
  | `intent` | None. |
  | `speech` | `to` if it addresses someone; `quoted: true` for quoted words; `instruction: true` for a direction to a party member, with `asks` (the kind it would be if they did it) and the fields that kind takes ("Maya, shoot the big one" carries `asks: check` and its `target`) (§2.2). An instruction meant to last ("keep their heads down", "stay close") adds `standing: true` and an `order` (`follow`, `attack`, `hold`, `suppress`, `cover`) (§3.5). |
  | `stance` | The axis it sets (`weapon`, `noise`, `cover`, `posture`, `carrying`) with its value, or `at_ease: true`; `object` if a weapon is named; `when` for a conditional (§2.7). |
  | `position` | `toward` (the enemy it closes on) or `away: true`; `dash: true` when it moves fast or far ("I sprint at him", "I run for the back of the store") (§3.3); `leaves`, the party members the movement deliberately leaves behind ("I run, leaving Maya") (§3.7e). |
  | `gear` | `op` (§2.3); `item`; for `give`, `to`; for `mode`, `mode`; for `loot`, `target`. |
  | `move` | `to`; `journey: true` when it sets out for a place it doesn't reach in the same beat; `leaves`, as for `position`. |
  | `wait` | `duration` as written ("for the night", "an hour"). |
  | `check` | `target` if there is one; `with` when the clause names the item or ability it uses; `count` when the clause repeats the action ("three shots" is three trigger pulls); `declaresResult: true` when the clause stated its own outcome (§2.4); `skill`, a proficiency key from the world's declared list, when the check isn't an attack or an ability and one fits (§4.2); `steady: true` when the clause steadies `{{user}}`'s own nerves (§4.4); `suppress: true` for fire meant to pin rather than hit ("I keep their heads down") (§3.4b); `called: legs` for a shot at the legs (§3.4c). |
  | `search` | `place`. |
  | `trade` | `vendor` if named; `gives` and `wants` as written (items, amounts); `quoted: true` for a quoted offer. |
  | `claim` | `about` (§2.4a). For `outcome`, `own: true` when it's the result of `{{user}}`'s own `check`. For `state`, the quantity it contradicts where it can (`"rounds"`, `"hp"`). For `presence`, `perceived: true` when it's something `{{user}}` senses, `absent: true` when it says nothing is there, and `place` when it names somewhere other than here. |

  The pass labels a take as `gear` with `op: take` either way. Whether a roll
  placed the item is the fork's lookup, not the pass's judgment. Objects are
  matched to the inventory by type, as in `OUTCOME_AUTHORITY.md` §3.1, and
  unknown objects go to the §4.1b classifier.
- **The fork counts what it resolved, once.** Trigger pulls in the player's
  message are resolved and deducted before generation: `count` × the fire
  mode's `rounds`, stopping when the inserted magazine runs dry, so a third
  pull on two rounds clicks. A pull that clicks fires nothing and rolls
  nothing. The model's narration of those same shots is not
  counted again (`RPG_STATS.md` §4.6). Otherwise "I fire three times" followed by
  "she fires three times" takes six rounds.
- **Output that doesn't parse, a kind outside the vocabulary, or a `gear` beat
  with an `op` outside its list,** makes that beat `flavor`.

### 2.10 Display, prompt, and corrections

**The stored message is never edited** (`OUTCOME_AUTHORITY.md` §4.1a). What the
player sees and what the model is sent are both derived from it:

| | Applied | Not reached | Not confirmed |
| --- | --- | --- | --- |
| **What** | Beats the turn resolved, `scenery` claims, perceived presences the roll confirmed, and `opening` claims, which go with a fact marking them as a proposal (§2.4a) | Everything after a cut point (§2.6) | Other `claim` beats, declared results included (§2.4), and takes of something no roll placed (§2.4a), before the cut |
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
| 3 | "Raising my rifle" | `stance`, `weapon: ready`, `object: rifle` | "rifle" matches the equipped `firearm.rifle` → weapon `ready`, the carbine in hand, HUD badge |
| 4 | "I entered … Apartment 202" | `move` | Location → "Apartment 202"; arrival roll; [Search Apartment] offered |

Two possible results for beat 4:

- **Arrival: nothing.** The model narrates an empty unit, rifle up, and the HUD
  shows [Search Apartment]. The player taps it next turn or writes something
  else.
- **Arrival: one Shambler, inside, alerted.** The turn ends at the doorway. The
  model narrates the Shambler and stops. The `ready` weapon applies to whatever
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
| 7 | "I picked it up for my M9 Beretta" | `gear`, `op: take` | No roll placed 9mm here, so the take fails its lookup: nothing is committed, the search action is offered, and the turn ends there. "My M9 Beretta" matches the Glock by type (`OUTCOME_AUTHORITY.md` §3.1), so there is nothing to refuse, and the state block keeps calling it a Glock. |

- **Arrival: a Shambler.** Beat 4 is the cut. Beats 5–7 are folded as *Not
  reached*, and the model is sent the message up to "Apartment 202." It
  narrates the entry and the Shambler, and stops. The chat reads "…I entered
  one of the apartments. Apartment 202." followed by the Shambler, with the
  folded line underneath. The claims never come into play; the cut removed
  them. A claim placed before the `move` ("202 was empty, so I walked in")
  would be ignored anyway, and the roll would still produce the Shambler.
- **Arrival: nothing.** The turn continues past beat 4. Beats 5 and 6 are marked
  *Not confirmed*. Beat 7 takes nothing and ends the turn, so [Search
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
| 3 | "I thought I heard noises upstairs" | `claim: presence`, `perceived`, `place: upstairs` | Asks for upstairs' arrival roll now; the result is pinned to upstairs |
| 4 | "I went to investigate" | `move` | Location → upstairs; uses the pinned roll |

- **The house holds something:** the turn ends at the door; beats 2–4 are
  folded as *Not reached*, and upstairs isn't rolled.
- **The house is empty:** the turn continues, and beat 3 rolls upstairs. If the
  roll finds something, that is what made the noise: beat 3 stays in the
  model's copy, and beat 4 walks into it, which ends the turn. If it finds
  nothing, beat 3 is marked, the model is told upstairs is quiet, and beat 4
  finds an empty floor. Either way upstairs is rolled once, and the model never
  decides what made the noise. Two arrival rolls in one turn, for a place
  inside a place, are open questions (§2.13; `RPG_STATS.md` §10).

**D. Shots, a click, and a reload, in a fight.** `{{user}}` holds the §8 Glock
with **2 rounds** in the inserted magazine, an **empty** spare magazine, and 11
loose 9mm, and is fighting a Shambler.

> "I fired 3 more shots into the zombie and clicked on quickly tried to reload."

| # | Beat | Kind | Fork action |
| --- | --- | --- | --- |
| 1 | "I fired 3 more shots" | `check`, `count: 3`, `declaresResult` | No weapon is named and nothing is in hand, so the only equipped firearm is used (§2.7). Three pulls; the Glock has no `fireModes`, so one round each (`RPG_STATS.md` §3.8.2). Two rounds fire, the third pull clicks. The fork deducts the two rounds now. |
| 2 | "into the zombie" | `claim: outcome`, `own` | *Not confirmed*. The roll decides the hits. |
| 3 | "clicked" | `claim: state` | *Not confirmed*. It happens to match here; the fork's count is what's true either way. |
| 4 | "quickly tried to reload" | `gear`, `op: reload` | The legality check fails: no magazine in inventory holds a round. Fact injected: no loaded magazine, 11 loose rounds. |

The message fits the exchange budget (§3.2a): three pulls are one attack
action, at the default cap, and the reload is the move. The failed reload still
spends it. The two shots that fire are one roll (§4.3): with the Shambler at
`near` and `{{user}}` `steady`, the chance is 35 base + 40 handguns + 0 for a
pistol at near = 75% (§4.6), and a partial lands both
rounds at half damage. A miss on beat 1 doesn't cut (§2.6, inside an encounter). The model narrates two
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
| 1 | "I stabbed the fucking zombie. Stabbed him good." | `check`, `declaresResult` | One stab, one roll. "Stabbed him good" restates beat 1 and merges into it (§2.2). "Good" leans toward a result; the flag covers it, and the beat is sent whole. |
| 2 | "It went down in a blink" | `claim: outcome`, `own` | *Not confirmed*; the roll decides |
| 3 | "I began searching him" | `gear`, `op: loot` | If the Shambler is defeated, takes the loot its defeat rolled; if not, fails the legality check |
| 4 | "I already found 50 bucks on him" | `claim: contents` | *Not confirmed*. The §8 Shambler's dollar line is a 30% chance of $2–18, so it could never have carried $50; and what it did carry was rolled at defeat, not declared. |
| 5 | "He must've been someone before all of this" | `flavor` | None |

- **The stab kills, and it was the only enemy:** the encounter ends at beat 1,
  and the rest of the message resolves outside it, with no budget (§3.2a). The
  body's rolled loot is taken: a field dressing on a 10% line, a few dollars
  on a 30% line, both, or nothing. The model narrates what was actually found,
  not $50, and the reflection reaches it in the player's own voice.
- **The stab fails:** the stab spent the exchange's action, and searching a
  body costs an action too, so beat 3 doesn't fit the budget. Beats 3–5 are
  *Not reached*, the $50 and the reflection with them, and the Shambler acts.
  Had the action been free, the search would still have failed the legality
  check: the Shambler is still moving.

Examples F–K use the §8 starting state: the Glock with 9 rounds, an empty spare
magazine, 11 loose rounds, $35, no stim, no axe. Maya is in the party.

**F. A line that might be wrong.**

> `I shout to Maya, "It's clear, nothing in here!" and wave her over.`

| # | Beat | Kind | Fork action |
| --- | --- | --- | --- |
| 1 | `I shout to Maya, "It's clear, nothing in here!"` | `speech`, `to: Maya`, `quoted` | Sent as written. The words are never checked for claims. |
| 2 | "and wave her over" | `speech` (gesture), `instruction`, `asks: move` | Sent. Nothing in Maya's state forbids it. Whether she comes is the world's response. |

If `{{user}}` is wrong, it is the state that says so, not the parse. If they are
lying to her, Maya reacts to the lie.

**G. A door not opened, and a condition.**

> "I don't go in yet. If anything moves in there, I shoot it."

| # | Beat | Kind | Fork action |
| --- | --- | --- | --- |
| 1 | "I don't go in yet" | `flavor` (negated) | None: no `move`, no arrival roll |
| 2 | "If anything moves in there, I shoot it" | `stance`, `weapon: ready`, `when` | Weapon `ready`, the condition kept. No shot is fired this turn. |

The model narrates `{{user}}` holding at the threshold, weapon up. Nothing inside
is decided until `{{user}}` goes in.

**H. Orders to the party and an offer to a trader.** At Okoro Gunsmithing in
Northgate (`RPG_STATS.md` §8), where the Beretta is $1,400.

> "We split up. Maya searches the kitchen while I haggle with the trader for the
> Beretta. I offer him my Glock and 200 bucks."

| # | Beat | Kind | Fork action |
| --- | --- | --- | --- |
| 1 | "We split up" | `speech`, `instruction`, `asks: move` | Sent. Split parties are open (`RPG_STATS.md` §10). |
| 2 | "Maya searches the kitchen" | `speech`, `instruction`, `to: Maya`, `asks: search` | Sent. If she goes, her search is the kitchen's search action, chosen like any other. |
| 3 | "while I haggle with the trader for the Beretta. I offer him my Glock and 200 bucks" | `trade`, `vendor: Okoro`, `gives`: Glock, $200, `wants`: Beretta | Two trade clauses to one vendor, so one beat and one offer (§2.2). The legality check finds $35, not $200; the fact is injected. The trade action opens with the Glock offered. Nothing commits until confirmed, and the turn ends there. No price change: haggling isn't in v0. |

The model plays the haggle as conversation, with Okoro answering from his own
position. The $200 isn't there, and the HUD shows the offer can't reach $1,400.

**I. Downed, and reaching for things that aren't there.** `{{user}}` is downed
in a fight.

> "*Ignoring the pain* I get up, jab the military stim into my thigh and grab my
> axe."

| # | Beat | Kind | Fork action |
| --- | --- | --- | --- |
| 1 | "*Ignoring the pain*" | `flavor` | The player's feeling. It changes nothing the body can do. |
| 2 | "I get up" | `stance`, `posture: standing` | Fails: `downed` pins posture at `prone` (`OUTCOME_AUTHORITY.md` §6). Attempted, and it fails. |
| 3 | "jab the military stim into my thigh" | `gear`, `op: consume` | `downed` allows `gear.consume`, so the status doesn't stop it. Fails possession: there is no stim in inventory. It would not help anyway, because the stim raises max HP and is not a revive. |
| 4 | "grab my axe" | `gear`, `op: equip` | No axe is in a slot, so this is an `equip`, not a `stance` (§2.3). It doesn't fit the budget, so it is *Not reached* (below). Reached, it would fail twice: `downed` doesn't allow `gear.equip`, and `{{user}}` has no axe. The fire axe is Maya's. |

Inside an encounter a failed beat doesn't cut, but the budget does (§3.2a). The
attempt to get up spends the move and the stim spends the action, even though
both fail, so beat 4 doesn't fit: "grab my axe" is *Not reached*. The model
narrates the try to rise and the body refusing, and a hand finding no
injector. Any cost comes from the state, never from the number of failures.

**J. A night, then something that can't exist.**

> "We hole up in the apartment for the night. In the morning I pull out my
> lightsaber and cut through the barricade."

| # | Beat | Kind | Fork action |
| --- | --- | --- | --- |
| 1 | "We hole up in the apartment for the night" | `wait`, `duration: for the night` | Time roll, once encounter data exists. If something finds them, the turn ends in the night. |
| 2 | "In the morning I pull out my lightsaber" | `gear`, `op: equip` | Premise claim: the §4.1b classifier marks an energy weapon absent from this world, so it is refused in-story. Producing an uncatalogued object from `{{user}}`'s own pack fails anyway (`OUTCOME_AUTHORITY.md` §3.1). |
| 3 | "and cut through the barricade" | `check`, `with: lightsaber` | Depends on a tool that isn't there. The legality check fails it, nothing rolls, and the barricade stands. |

If the night passes quietly, the model narrates the morning, a hand reaching for
something that was never there, and the barricade still standing.

**K. A note to the narrator, and a question.**

> "(OOC: can we skip ahead to the settlement?) Is there anything useful in the
> room?"

| # | Beat | Kind | Fork action |
| --- | --- | --- | --- |
| — | "(OOC: can we skip ahead to the settlement?)" | not a beat | Skipped. Reaches the model unchanged, as a note to the narrator. |
| 1 | "Is there anything useful in the room?" | `flavor`, `question` | Nothing resolves. Answered from the state, with the room's search action offered. |

The model can describe what's in plain sight (a stripped bed, a cabinet hanging
open) and point at the search. It never answers "yes, a box of ammo." If the
fork carries out the skip, it makes the journey roll first (§2.5).

**L. Arguing on the drive back.** `{{user}}` is driving back to camp from a
supply run, with Jack, a party member, in the passenger seat. The journey began
when they left the pharmacy.

> `"God damn it Jack! You should never run into a pharmacy, without backup. You
> could have died or worse, gotten bitten." I yelled at Jack, as I took a turn
> on the road. Only 3 KM more until camp.`

| # | Beat | Kind | Fork action |
| --- | --- | --- | --- |
| 1 | The quote, with "I yelled at Jack" | `speech`, `to: Jack`, `quoted` | Sent as written. The speaker tag is part of the quote (§2.2). "Died" and "bitten" are inside it and never checked. Scolding isn't an instruction, so Jack's answer is the world's. |
| 2 | "as I took a turn on the road" | `flavor` (travel along the way) | None. Not a `move`: the journey roll made when they left already covered the road. |
| 3 | "Only 3 KM more until camp" | `claim: scenery` | Passes through. Distance isn't tracked in v0. |

Nothing rolls this turn. Had the journey roll found something, the turn that
made it would have ended on the road. This is a quiet stretch, and the model
plays the argument. "We pull into camp" is a `move` with its own arrival roll.

**M. A noise, then an empty gun.** `{{user}}` is in an apartment whose search
turned up a dried biscuit. They hold the §8 Glock with an **empty** inserted
magazine and have loose 9mm in a pocket.

> "I managed to take a bite from the dried biscuit I found. But then, it
> happened. I heard a noise and a grunt."

| # | Beat | Kind | Fork action |
| --- | --- | --- | --- |
| 1 | "I managed to take a bite from the dried biscuit I found" | `gear`, `op: consume` | The search placed it, so it's eaten. Had `{{user}}` not had one, it would fail possession. |
| 2 | "But then, it happened. I heard a noise and a grunt." | `claim: presence`, `perceived` | The lead-in joins the perception (§2.2). Asks for a short time roll here. |

- **The roll finds a Shambler.** The noise was real: beat 2 stays in the
  model's copy, the encounter starts, and the turn ends there. The model
  narrates the grunt becoming a Shambler in the doorway, and stops.
- **The roll finds nothing.** Beat 2 is marked *Not confirmed*, lead-in and all,
  and the model is told the apartment is quiet. It isn't handed a cliffhanger
  to fill.

With the Shambler there:

> "Biscuit still in mouth, I pulled my gun and just fired blindly fired in the
> dark, at the source of the noise."

| # | Beat | Kind | Fork action |
| --- | --- | --- | --- |
| 1 | "Biscuit still in mouth" | `flavor` | None |
| 2 | "I pulled my gun" | `stance`, `weapon: ready`, `object: gun` | Matches the equipped Glock, which is now in hand. In an encounter the fork may put a check on it (§2.7). |
| 3 | "fired blindly in the dark, at the source of the noise" | `check`, `target`: the Shambler | Uses the Glock in hand. The magazine is empty, so the pull clicks: nothing fires and nothing rolls (§2.9). Fact injected: empty magazine, loose rounds in the pocket. "Blindly" and "in the dark" are handicaps the player chose: `scenery` (§2.4a). |

There's no cut, because it's an encounter, and the message fits the budget
(§3.2a): drawing the gun is the move and firing is the action. The model narrates the dry click and
the Shambler's response. Nothing warns the player beforehand or reloads for
them. The HUD showed the count, and the click is what forgetting it costs (the
no-rescue rule, producer `CLAUDE.md` principle #13).

**N. A plea for a discount.** A vendor sells a set of throwing knives for $150.
`{{user}}` has $100.

> `"Listen buddy, I really need those knives but I only got 100 bucks. How about
> you drop the 50 and let me have them? It's a shit world out there and I want
> to live." I told the seller, knowing he would be sympathetic and give me the
> knives for 100.`

| # | Beat | Kind | Fork action |
| --- | --- | --- | --- |
| 1 | The quote, with "I told the seller" | `trade`, `vendor`: the seller, `quoted`, `gives`: $100, `wants`: the knives | Persuasion about a price is haggling: a `trade` beat with no roll, not a `check` (§2.3). The trade action opens with the knives offered for $100, the legality check finds the $100 is there, and the turn ends there. The quote reaches the model as written and isn't checked for claims: had `{{user}}` lied about the money, the seller would react to the lie. |
| 2 | "knowing he would be sympathetic and give me the knives for 100" | `claim: npc` | Past the cut, so *Not reached*. Before one it would be *Not confirmed*. Left out of the model's copy either way: the seller decides (§2.4a). |

The model is told the price stands at $150 and plays the seller's answer from
his own position and `note`. He can be sympathetic and still say no. The HUD
shows the offer $50 short, and nothing changes hands.

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
  offered, with no arrival roll. A journey is quiet, and a perceived presence
  passes through to the model as a proposal (§2.4a, §2.5).
- **No `[[RPG_STATS]]` carrier:** no beat pass at all. Nothing in this section
  applies to a world without stats.

### 2.13 Open questions

Questions about how the engine reads and resolves a turn live here. Questions
about authored data or state shape live in `RPG_STATS.md` §10, and questions
about what the player may claim or bypass live in `OUTCOME_AUTHORITY.md` §10.2.
Each is recorded once, in the file that will settle it.

- **Rolls per turn.** Whether a message can trigger any number of rolls, as
  long as each one leaves the premise intact, or whether there is a cap.
  Example C already rolls arrival twice in one turn.
- **Intent with mechanics.** Whether a stated plan ("search all four") should
  queue HUD actions or stay narrative only.
- **Time in free beats.** Whether "I paused a bit" should advance time once
  time exists (§1). Longer spans ("I wait an hour") are a `wait` (§2.3).
- ~~**Conditionals that fire.**~~ Resolved 2026-11-18 for fights: inside an
  encounter, a readiness conditional holds the action and fires on a
  mechanical trigger (overwatch, §3.4a). Outside one it stays a stance; one
  held when the party is ambushed fires in the ambush's enemy step (§3.3a).

**Tracked in the owning contract:**

| Question | Where |
| --- | --- |
| Encounter data for the arrival, time, and journey rolls | `RPG_STATS.md` §10 |
| Re-entry: does a revisited place roll arrival again | `RPG_STATS.md` §10 |
| Places inside places (upstairs, a back room) | `RPG_STATS.md` §10, under location identity |
| World-authored stances | `RPG_STATS.md` §10 |
| Split parties | `RPG_STATS.md` §10 |
| The weapon in hand, as fork state | `RPG_STATS.md` §3.11 |
| Claims the state agrees with | `OUTCOME_AUTHORITY.md` §10.2 |
| Improvised objects that share a catalog type | `OUTCOME_AUTHORITY.md` §10.2 |

---

## 3. Combat — Draft

The enemy side was decided 2026-11-13; the exchange budget, movement within a
fight, and overwatch on 2026-11-18; escape and avoidance, awareness, terrain,
stamina, standing orders, and death on 2026-11-19. This section covers how an
exchange is ordered and how much fits in it, where the party and the enemies
are, what the enemies do, who they do it to, how the result reaches the model,
how a party gets away, and how characters die. The numbers behind it — the attack roll, what defense is made of, damage,
armor — are the core roll (§4).

### 3.1 The problem

§2 resolves the player's side of a fight before generation. If the enemy's side
were left to the narration, the model would decide whether the Shambler's bite
lands, and the fork would only read the damage back (`OUTCOME_AUTHORITY.md`
§2.2, writer 3). That makes the model the jeopardy dial: the same habit that
yields to `{{user}}` would decide how often the enemy hits them (producer
`CLAUDE.md` principle #13). The player's side would be mechanical and the
enemy's would be a mood.

So **the fork resolves both sides before generation**: what each enemy does,
to whom, whether it lands, and for how much. The model writes how it happens.
It is the dice oracle's split applied to a fight, "roll the shape, not the
choreography" (`DICE_ORACLE.md` §6.1).

### 3.2 The exchange

Inside an encounter, **one user message and the reply to it are one
exchange.** Before generation, the fork resolves it in this order:

1. **`{{user}}`'s beats**, in the order written (§2.6). An enemy they defeat
   doesn't act.
2. **Party members acting on an instruction** in this message (§3.5), in the
   order the instructions were written.
3. **Each enemy instance still able to act** takes one action (§3.4), in
   instance order (`Shambler 1` before `Shambler 2`). An earlier action's
   result applies to later ones.
4. **The results commit to the working copy** (`RPG_STATS.md` §4.3) and reach
   the model as one block of facts (§3.6).

- **Both sides are pinned to the user's message** (`OUTCOME_AUTHORITY.md`
  §4.2). A swipe replays the whole exchange, the enemy's rolls included, and
  asks only for different prose.
- **Enemies act even when the player rolls nothing.** A message that only talks,
  reloads, or hesitates still gives every enemy its action. Spending an
  exchange on something else is a choice, and the enemy answers it.
- **The party acts first.** The player's message is the party's move and the
  world answers it. The exchange whose arrival roll starts an encounter has no
  enemy actions: the turn ends at that beat (§2.6), and the first full exchange
  is the player's next message. Awareness makes the two exceptions (§3.3a):
  enemies that ambush the party act in that arriving exchange, and `unaware`
  enemies don't act at all until something alerts them.
- **How much fits in one exchange** — three shots, a reload, and a dive for
  cover in one message — is the exchange budget (§3.2a).

### 3.2a The exchange budget

Decided 2026-11-18. Each exchange gives `{{user}}` one **action**, one
**move**, and any number of **free** beats. The action can be spent as a second
move. A party member acting on an instruction has her own action and move
(§3.5).

| Cost | Beats |
| --- | --- |
| **Free** | `flavor`, `intent`, `claim`; `speech`, orders to companions included; `stance` changes to `weapon` (readying or lowering the weapon already in hand), `noise`, or `posture` → `prone`; `gear` `mode` and `drop`; `wait`, which spends nothing and lets the enemies act |
| **Move** | `position`, one band (§3.3); `stance` changes to `cover` (in or out) or `posture` → `standing`; `stance` readying a weapon that isn't in hand (drawing or switching, §2.7); `stance` taking aim (`weapon: aimed`, §4.2); `gear` `reload`, `take`, `give`, `equip`; steadying (a `check` with `steady: true`, §4.4) |
| **Action** | `check`: an attack (suppressive fire included, §3.4b), an ability, forcing something, disengaging (§3.3); `position` with `dash`; `move` through an exit, which is a dash (§3.7c); `gear` `refill` (with its check, `RPG_STATS.md` §3.8.4), `consume`, `loot`; holding an attack (overwatch, §3.4a); `stance` lifting a party member to carry, and every exchange of carrying after it (§3.7e); shutting a door behind the party (§3.7c) |
| **Not in a fight** | `search` and `trade`: their actions aren't offered during an encounter, so the beat commits nothing and the fact is injected. |

- **Beats spend in order.** The first beat that costs more than what's left
  ends the exchange: it and every beat after it, free ones included, are *Not
  reached* (§2.6, §2.10), folded with **Use as my next message**. The fold's
  line says where the exchange ran out.
- **An attempt spends its cost whether or not it works.** A refill that loads
  nothing, a reach for an axe that isn't there, and a stand that a status
  refuses each use the moment they took (`OUTCOME_AUTHORITY.md` §3.3).
- **Trigger pulls per action.** One attack action covers up to **3** trigger
  pulls; a weapon's `pullsPerAction` overrides it (`RPG_STATS.md` §3.3). A
  burst or automatic pull counts as one pull; how many of its rounds can hit
  is §4.3. A `count` above the cap fires only the cap, the beat stays whole in the model's copy (§2.4), and a fact says how
  many pulls fired.
- **An implied close.** A melee attack on an enemy at `near` spends the move to
  close first, when the move is still unspent (§3.3). Without it, the attack
  fails for reach and the fact is injected.
- **The fight can end mid-message.** When the party's beats leave no enemy able
  to act (§3.7), the encounter ends at that beat, and the rest of the message
  resolves as it would outside a fight, with no budget.
- **Leaving the place** (a `move` during an encounter) is a dash through one
  of the place's exits (§3.7c). It costs the action, and the encounter comes
  along: distances carry through the doorway. A fight ends by breaking contact
  (§3.7a), never by walking into the next room.
- **Stamina.** With `system.exertion` (`RPG_STATS.md` §3.2), a dash and a
  disengage also cost stamina, and at zero neither is possible (§3.7d).
- **The HUD shows the budget** beside the parse: action and move, spent or
  open.

### 3.3 Range bands

Each enemy instance is in one of three **range bands**, relative to the party:

| Band | Meaning |
| --- | --- |
| `engaged` | Within arm's reach of one party member. Melee range. The instance records **which** party member it is engaged with. |
| `near` | Across a room or a yard: a few seconds' rush. |
| `far` | Across a street or a field: ranged weapons only. |

- **Distance past `far`.** The fork counts distance as a number: `engaged` 0,
  `near` 1, `far` 2. Three or more is out of reach and out of sight, which is
  how a party breaks contact (§3.7a). The state block shows only the band.
- **The party shares one position.** Bands are per enemy instance, not per
  party member, except that an `engaged` instance names the member it's
  engaged with. Distances per party member wait on split parties
  (`RPG_STATS.md` §10).
- **Starting band.** Instances start at `near` until encounter data sets the
  band (`RPG_STATS.md` §10). The arrival roll is the expected place to set it,
  along with whether the enemy is alerted (§3.3a).
- **Enemies change band** through their own actions: `close` takes `speed`
  off the distance, `withdraw` moves one band away (§3.4).
- **The party changes band** through `position` beats (§2.3), decided
  2026-11-18:
  - **`toward`** an enemy moves one band closer to it, costing the move;
    reaching `engaged` engages it with whoever moved. A `dash` moves two bands
    and costs the action instead (`far` to `engaged` in one exchange).
  - **`away`** moves one band farther from every instance that isn't engaged
    with the mover; a `dash` away moves two. Past `far` an instance is out of
    reach (§3.7a).
  - **Disengaging.** A `position` away from an enemy engaged with the mover is
    a check, and costs the action. On a success the mover gets clear and the
    enemy drops to `near`. On a partial the mover gets clear, but the enemy
    attacks first; that attack is its action this exchange. On a fail the
    mover stays engaged. Without this, backing off one band each exchange would
    keep a slow enemy closing forever and never attacking. With
    `system.exertion` it costs stamina too (§3.7d).
  - **Only `{{user}}`'s `position` moves the party's bands.** A companion's
    instructed `position` changes only her own engagement: toward a `near`
    enemy engages her with it, and away disengages her, with her own check.
- **Fire on the move.** A ranged attack on a party member who moved this
  exchange uses the weapon's accuracy for the band they **started** the
  exchange in. Getting away from guns takes an exchange under fire.
- **Reach.** A `melee` attack reaches only the party member the instance is
  engaged with. A `ranged` attack reaches any band. What range does to the
  odds is the weapon's accuracy for that band (§4.2). The same holds for the party: a melee
  attack on an enemy at `near` makes an implied close first, if the move is
  unspent (§3.2a), and one at `far` can't reach.
- Each instance's band shows in the state block (`RPG_STATS.md` §4.5) and on
  the HUD.

### 3.3a Awareness, stealth, and ambush

Decided 2026-11-19. Each enemy instance is **`unaware`** or **`alerted`**.

- **Arriving.** The arrival roll that spawns enemies decides it (§2.5). If the
  party arrived in `quiet` stance (§2.7), the fork rolls the world's stealth
  check (`system.stealth`, `RPG_STATS.md` §3.2) for the party, at the lowest
  rank among its standing members: on a success the instances start
  `unaware`. Otherwise, and whenever the party wasn't quiet, they start
  `alerted`. Encounter data may set awareness instead (`RPG_STATS.md` §10).
  With no encounter data, every instance starts `alerted`.
- **Unaware enemies take no action.** They stay where they are and roll no
  intent.
- **Leaving unaware enemies** in `quiet` stance is free: a `position` away or
  a `move` out commits with no check. Moving at `normal` noise within `near` of
  one makes a stealth check, and a fail alerts every instance. A `dash` is
  always loud and alerts them.
- **Ambush.** The first attack on an `unaware` instance gets **+20** (§4.2).
  Then:
  - a `loud` attack (`RPG_STATS.md` §3.3 `noise`; firearms by default) alerts
    every instance, and they **lose that exchange**: no enemy acts in it;
  - a `quiet` attack (bows, blades, fists by default) alerts only its target,
    and only if it survives. A quiet kill leaves the rest unaware.
- **Being ambushed.** Enemies that ambush the party (encounter data) take an
  enemy step in the arriving exchange, and the `surprised` stress trigger fires
  (§4.4). A readiness conditional held as the party arrived (§3.4a) fires in
  that step.
- **Gunfire is noise.** An exchange with any loud attack in it makes one short
  time roll at its end (§2.5), the same roll a partial's noise asks for
  (§4.3). It can start a second encounter in the same place: the rest of the
  street heard the shots. Without encounter data, nothing comes.
- Each instance's awareness shows in the state block and on the HUD.

### 3.4 An enemy's action

Each enemy instance that can act takes one action. The fork picks it in four
steps: **intent, target, roll, damage.** None of them is the model's.

**Intent.** What the enemy does this exchange, from a closed list:

| Intent | Applies when | What happens |
| --- | --- | --- |
| `attack` | One of its attacks reaches a party member (§3.3) | The attack resolves (below). |
| `close` | It isn't engaged and no attack reaches | It moves `speed` bands toward the party. Reaching `engaged`, it engages its target. |
| `cover` | It isn't in cover | It is in cover until it moves, and attacks against it take the cover modifier (§4.2). |
| `withdraw` | It's engaged and has a `ranged` attack | It moves to `near`. |
| `flee` | Its HP is at or below its `fleeAtHpPct` | It leaves the encounter. It isn't defeated, so it drops no loot. |
| `feed` | It `feeds` and is engaged with a downed or left-behind party member | It feeds. If `fedOn` is in that character's death path, they die (§3.7e). It stays with the body and drops out of the encounter and any chase. |
| `suppress` | It has a ranged attack, its target is in cover, another able instance can attack that target, and no other instance is suppressing it this exchange | No damage. The target is **suppressed** until the end of their next exchange: −20 to their attacks (§4.2), and leaving cover while suppressed exposes them (+10 to the next attack against them). |
| `flank` | Its target is in cover and the cover still counts against it, it isn't engaged, and no other instance is flanking that target this exchange | It moves for an angle. From then on the target's cover doesn't count against **this** instance's attacks, until the target changes position or cover. |

The bestiary entry's **`tactics`** is an ordered list of these intents, and
**the first one that applies is taken** (`RPG_STATS.md` §3.5). Authors set the
priority; the fork judges only the fixed conditions in the table. Nothing is
model-chosen and no condition language is authored.

- **Default `["attack", "close"]`** when `tactics` is absent: hit what's in
  reach, otherwise come closer. That is every Shambler.
- A trained enemy might be `["cover", "attack", "close"]`: it gets into cover
  first, then shoots from it.
- `flee` applies only to an entry with `fleeAtHpPct`, and only where it is
  listed in `tactics`.
- **`feed` comes first** for an entry with `feeds` (`RPG_STATS.md` §3.5): the
  fork puts it at the front of the list. A feeder doesn't choose a meal over a
  fight; it can't help it.
- **Coordinated intents.** `suppress` and `flank` go to one instance per target
  per exchange, in instance order. A trained pair that lists
  `["cover", "suppress", "flank", "attack", "close"]` gets one man pinning
  `{{user}}` behind the counter while the other works around it, and a lone
  operator, with nobody to cover for, just shoots.
- **Boss phases switch tactics.** A phase with its own `tactics` replaces the
  entry's list from the moment it fires. "Fights from behind his men until
  there are none left" becomes a list, not a hope.
- **If no intent applies, the instance holds** and does nothing this exchange.

**Target.** The party member an `attack` (or the engagement at the end of a
`close`) is aimed at. The fork picks:

1. the party member the instance is engaged with;
2. otherwise the one who damaged it most recently this exchange;
3. otherwise one at random among the party members its attack can reach.

**The model never picks the target.** A fact that says "someone takes 9" ends
up on whoever the model would rather hurt, which is never `{{user}}`.

**The downed.** A downed party member is targeted only by an instance that
`feeds`, which goes to downed and left-behind bodies before anyone standing, or
when no standing party member is in reach. What a hit on them does is that
character's death path (§3.7e), authored from the world's posture boundary
(`RPG_STATS.md` §3.7).

**Which attack.** When several of an instance's attacks reach, the fork picks
one at random, weighted by each attack's `weight` (default `1`).

**Roll.** The attack is a core roll (§4.1): its chance is the instance's rank
and its weapon's accuracy, adjusted by the target's cover, posture, and band
(§4.2), and it lands in one of the three bands.

**Damage.** A hit rolls the attack's `damage` (a number or a range,
`RPG_STATS.md` §3.6), halved on a partial, reduced by the target's armor less
the attack's pierce (§4.3), and commits to the target's working copy. `atZero`
applies as usual.

**One attack formula for both sides.** An enemy with `equipment` attacks with
its equipped weapon exactly as `{{user}}` would: the weapon's `combat` numbers
(reserved, `RPG_STATS.md` §3.3) and the instance's own proficiency. Its weapon
never runs dry or wears (`RPG_STATS.md` §3.5). Creatures without weapons have
natural `attacks`. An instance with neither a natural attack nor a weapon with
`combat` numbers has nothing to attack with, and `attack` never applies to it.

**Named enemies.** A bestiary entry with `npc` is portrayed from that
character's own material (`RPG_STATS.md` §3.5), but the fork still picks its
intent and resolves its results. Its `tactics` and `phases` are the authored
frame the portrayal stands on, the same way a card is.

### 3.4a Overwatch

Decided 2026-11-18. Inside an encounter, a readiness conditional ("If anything
comes through that door, I shoot it", §2.7) **holds the exchange's action**:
weapon `ready`, plus a held attack.

- **It fires in the enemy step,** the first time any enemy instance `close`s
  into the held weapon's reach or `attack`s a party member. The held attack
  resolves first, against that enemy, as an ordinary attack action (pull cap
  included, §3.2a). If it defeats the enemy, the enemy's action doesn't happen.
- **The trigger is mechanical, not the `when` text.** The fork doesn't judge
  whether "comes through that door" matched. `when` stays in the model's copy
  so the narration can honor it.
- **Reach still applies.** A held melee attack fires only on an enemy that
  closes to `engaged` with the holder or attacks them. A held ranged attack
  fires on any band.
- **Unfired, it lapses** at the end of the exchange. The weapon stays `ready`.
- **A companion can be told to hold** ("Maya, cover the door"): an instruction
  asking for a `stance` with `when` holds her action the same way (§3.5), and
  a standing `hold` order holds it every exchange.
- Outside an encounter the conditional stays a stance (§2.7). One held as the
  party arrives fires in an ambush's enemy step (§3.3a); otherwise the arriving
  exchange has no enemy step for it to fire in.

### 3.4b Suppressive fire

Decided 2026-11-19. An attack action can be fired to pin rather than to hit
("I put rounds over their heads", "keep them down"): a `check` with
`suppress: true`.

- **It needs volume:** at least 3 rounds in the action, from three single
  pulls, a burst, or automatic fire. With fewer, it's an ordinary attack.
- **It does no damage.** It rolls like an attack on an instance in the target
  band, with no aim and no recoil.
- **Success** pins up to 3 instances in that band; automatic fire pins every
  instance in it. **Partial** pins one. **Fail** pins none. Every round is
  spent either way.
- **A pinned instance** can't `close` or `attack` this exchange. It can still
  take cover, withdraw, or flee. Pinning happens in the party's steps, before
  the enemy step.
- **`fearless` enemies can't be pinned** (`RPG_STATS.md` §3.5). Covering fire
  buys time against people, not against the dead.
- A companion with a `suppress` order does this every exchange her weapon can
  (§3.5). Loud suppression is gunfire like any other (§3.3a).

### 3.4c Called shots: the legs

An aimed attack (§4.2) can be called at the legs: a `check` with
`called: legs`. It keeps the aim bonus to the chance, and a success trades the
×1.5 damage for the **`hobbled`** status. A partial does half damage with no
status.

- **Hobbled** means no dashing. A hobbled enemy's `speed` drops by 1, to a
  minimum of 1: a hobbled Runner moves like a Shambler, and can be outrun.
- **It is the first status an attack inflicts.** On an instance it lasts the
  encounter. On a party sheet it lasts until a consumable tagged `medical` is
  used on them (`RPG_STATS.md` §3.3), until statuses and rest are designed
  (`RPG_STATS.md` §7).
- **Party members can be shot.** An attack on a party member is an attempt like
  any other, at the `engaged` accuracy: she's beside you. Shooting Maya in the
  leg so the Runners take her instead is legal, and the fork resolves it. What
  follows in the fiction is the cast's, under the posture contract (producer
  `CLAUDE.md` principle #13): it is moral and relational harm, the world
  doesn't soften it, and she doesn't forgive by default. That would be the
  yield reflex.

### 3.5 Party members in a fight

- **`{{user}}`** acts through their beats (§2).
- **A one-off instruction** this exchange ("Maya, shoot the big one") acts in
  step 2 of the exchange (§3.2). The fork checks the asked kind against her
  own sheet (§2.2) and resolves it as it would `{{user}}`'s: her proficiency,
  her weapon, her rounds, and her own action and move (§3.2a). Until refusal is
  settled (§3.9), an instruction her state allows is carried out, and the
  model voices how she does it. It overrides her standing order for that
  exchange only.
- **Standing orders**, decided 2026-11-19. An instruction meant to last
  ("keep their heads down", "cover the door", "stay close") carries
  `standing: true` and becomes her **order**, kept until another replaces it.
  Orders are a closed set:

  | Order | Each exchange |
  | --- | --- |
  | `follow` | **The default.** She attacks whatever is engaged with her. With nothing engaged, no attack. |
  | `attack` | She attacks the instance named, or the nearest, using her move to close on it when she has to. |
  | `hold` | She holds her action as overwatch (§3.4a). |
  | `suppress` | She fires suppression at the named band (§3.4b), while her weapon can. |
  | `cover` | She gets into cover and stays there. No attacks. |

  The state block shows each companion's order on one line
  (`Maya — order: covering the door`), so the model never has to infer what
  three companions are doing. One line each keeps the prompt small.
- **She moves with the party.** The party shares one position (§3.3) and moves
  at its slowest member: nobody dashes unless every standing member can
  (stamina, carry tier, hobbled; §3.7d). An engaged companion disengages only
  when told, with her own check, and breaking contact needs every standing
  member clear (§3.7a).
- **Leaving her behind** is an explicit choice: a `position` or `move` beat
  with `leaves` (§3.7e).
- **Every party member can be targeted** (§3.4). Damage to a companion commits
  to her sheet like damage to `{{user}}`.

### 3.6 The exchange reaches the model: no more harm, no less

The fork injects each exchange's results as one block of authoritative fact,
with the standing of the state block (`RPG_STATS.md` §4.5). It lists, in the
order resolved:

- each party roll and its result;
- each enemy's action: its intent, its target, the band, the damage, and the
  **severity** the target is left at;
- band changes, defeats, flights, and any boss phase that fired;
- awareness changes, pins, suppression, and flanks;
- in a chase, the evasion result and where each pursuer ended up;
- downed characters with their bleed-out clock, and deaths with their cause.

**Severity** is a short descriptive band derived from `current / max`
(unhurt, lightly hurt, badly hurt, barely standing, downed), given beside the
number so the prose and the HP stay in step. The exact bands and wording are
the consumer's (`RPG_STATS.md` §10). One possible form:

> `[Exchange — Shot 1 hits Shambler 1 (badly hurt). Shot 2 misses. Shambler 1 claws {{user}}: hit, 9 damage — {{user}} lightly hurt. Shambler 2 closes to arm's reach of Maya.]`

The model narrates **exactly** the block:

- **No less.** A rolled hit lands, at its severity. Writing nine damage as
  "barely a scratch" is rescue from consequence. A miss is a miss.
- **No more.** No hits, wounds, or effects the block doesn't list, and no
  enemy acts beyond its injected action. That is sourceless adversity,
  which `protagonist_jeopardy` already rules out.
- **The model owns the choreography:** how the lunge looks, what the Colonel
  shouts, what the cover is, the sound and the blood. Never whether, who, or
  how much.

The engine block that carries this rule is `outcome_authority`
(`OUTCOME_AUTHORITY.md` §5), still a sketch.

**The fight isn't read back for damage.** Inside an encounter the enemy side is
already resolved, so the model's narration of it is not parsed for damage or
hits (`OUTCOME_AUTHORITY.md` §2.2, writer 3). Outside encounters, observation
works as `RPG_STATS.md` §4.6 describes: a fall, a fire, a hazard.

### 3.7 Encounter end

An encounter ends when no enemy instance is left able to act (each one
defeated, fled, or feeding on a body the party left), when the party breaks
contact or loses a chase (§3.7a–§3.7b), or when nobody in the party is left
standing (§3.7e). The working copy then commits (`RPG_STATS.md` §4.3).
Instances the party got away from are discarded with no loot.

### 3.7a Breaking contact

Decided 2026-11-19. Replaces the interim leave rule.

- **The party breaks contact** when, after the enemy step, no instance that can
  act is within `far` (every one at distance 3 or more, §3.3) and every
  standing party member moved with the party. The encounter ends for the party.
- **Distance is the whole mechanism.** A `position` away adds one band to every
  instance not engaged with the mover, and a `dash` adds two for the action.
  An instance's `close` takes back its `speed`. From `near`, a party that
  dashes is clear of Shamblers (speed 1) in about two exchanges, and never of
  Runners (speed 2) by distance alone: those take a chase (§3.7b).
- **Running from guns costs HP.** Ranged enemies shoot at the band the party
  started in (§3.3). Suppression (§3.4b) is how that price comes down.
- **Pinned instances don't close,** so the gap opens on them.
- **Unaware enemies** are left as §3.3a says.
- **Pursuers don't drop out past `far`** (`pursues`, `RPG_STATS.md` §3.5). They
  stay at `far`, and when they are the only instances left within reach, the
  encounter becomes a chase.

### 3.7b Chases

When the party dashes away and the only instances left within reach are
pursuers, the encounter becomes a **chase**. Each chase exchange:

1. **The party runs.** Every standing party member dashes and pays its stamina
   (§3.7d). A member who can't dash ends the chase for everyone, unless they
   are left behind (§3.7e).
2. **The party rolls to evade:** the world's stealth check (`system.stealth`)
   at the lowest rank among its standing members, with stress and encumbrance
   (§4.2). A companion who can't move quietly is the one who gets you found.
3. **Each pursuer moves by the result:**

   | Evasion | Pursuer at `speed` 2+ | Pursuer at `speed` 1 |
   | --- | --- | --- |
   | Success | falls back one band | falls back two |
   | Partial | holds its band | falls back one |
   | Fail | gains one band | holds its band |

   A pursuer that falls back past `far` has lost the party. When none is left,
   the chase and the encounter end.
4. **The enemy step** runs as usual: a pursuer that reached `engaged` attacks,
   and ranged pursuers shoot from their band.

- **Stopping ends the chase.** An exchange without a dash (turning to fight,
  disengaging, ducking into cover) goes back to ordinary distances from where
  the pursuers stand. One engaged with a party member has to be disengaged from
  (§3.3) before the party can run again.
- **The chase has a clock.** Runners don't tire and the party does. When
  stamina runs out (§3.7d), it's a fight. That is the decision the chase
  forces: keep rolling, or turn while there is still HP and stamina to fight
  with.
- **Breaking off.** A pursuer that isn't `fearless` abandons the chase when an
  encounter with `fearless` enemies starts, from gunfire noise (§3.3a) or an
  arrival roll on the way. Operators don't follow anyone into the dead. Fights
  between enemy groups are open (§3.9); for now they just leave.
- **Feeders stop** at a downed or left-behind body (§3.7e).
- **Chases cross places.** A dash through an exit is a chase exchange like any
  other, and the new place's arrival roll applies (§3.7c).

### 3.7c Places, exits, and terrain

Decided 2026-11-19.

- **The encounter moves with the party.** A `move` during an encounter is a
  dash through one of the place's exits (§3.2a). Distances carry through the
  doorway: Shamblers at `near` in the basement are at `near` on the stairs, and
  follow the party up until it breaks contact. The new place's arrival roll
  still applies (§2.5), so running can find more trouble.
- **Terrain is data, never narration.** Each kind of place may author
  `terrain` (`RPG_STATS.md` §3.12): its exits, whether it has a chokepoint, and
  whether it has cover. The fork records a place's terrain when the party
  enters it, matched the way a search is (`RPG_STATS.md` §3.12), and the state
  block lists the exits. An unauthored place has two exits, cover, and no
  chokepoint.
- **An exit the record doesn't have isn't there.** A `move` through it fails,
  and the attempt spends the action (§3.2a). The model narrates the exits the
  state lists. This is what keeps a dead end from being sourceless adversity
  (`protagonist_jeopardy`): the model can't invent a locked door mid-chase, and
  the player can see that a place is a dead end before running into it.
- **A dead end** is a place whose only exit is the one the enemies are coming
  through. The way out is gone, and the fight is a consequence of where the
  party chose to run.
- **Chokepoints make a last stand possible.** In a place with
  `chokepoint: "narrow"`, at most one instance can be engaged with each party
  member; with `"tight"`, two. The rest wait at `near`. Ranged attacks aren't
  limited. Holding the basement stairs against eight Shamblers is a fight only
  if two reach you at a time.
- **No cover.** In a place with `cover: false`, a `stance` into cover fails:
  there is nothing to get behind.
- **Doors.** An exit with `door: true` can be shut behind the party. It costs
  the action, and every pursuer coming through it spends its next action
  getting through. Barricading and holding a door are open (§3.9).

### 3.7d Stamina

Opt-in per world (`system.exertion`, `RPG_STATS.md` §3.2). Movement has weight:
like the bars in a tactics game, stamina is a number the player learns to
watch.

- **A dash** costs `costs.dash` from every party member who makes it (10 in the
  §8 world), and every chase exchange is a dash. **A disengage** costs
  `costs.disengage` (5).
- **At zero** a character can't dash or disengage. They walk, or they fight.
  A carry tier with `dash: false` forbids dashing the same way (`RPG_STATS.md`
  §3.13).
- **Recovery.** Each exchange a character doesn't dash, they recover
  `recoverPerExchange` (3). Outside an encounter, a `wait` of an hour or more
  brings stamina back to where it stood before the fighting started.
  Recovering past that (the post-coma body getting stronger) is regeneration
  and rest (`RPG_STATS.md` §7).
- The HUD and the state block show stamina beside HP.

### 3.7e Downed, dead, and left behind

Decided 2026-11-19. A character at 0 HP takes their `atZero` (`RPG_STATS.md`
§3.7). Where that is `downed`, the character's **death path** (`diesWhen`)
says what turns downed into dead:

| Entry | Kills when |
| --- | --- |
| `bleedOut` | `bleedOut` exchanges pass (3 by default) and nothing on their `recovery` list has got them up. The clock counts the encounter's exchanges, and the HUD shows it. |
| `harmWhileDowned` | Any hit lands on them while they're down. |
| `fedOn` | An instance that `feeds` reaches the body (§3.4). |

A world that rules a character's death out leaves the list empty, and
`allDown` names the lost scene instead.

- **Nobody standing.** When no party member is left standing, the party gets
  one more exchange: the downed still do what their status `allows` (speak,
  crawl, use a consumable). At its end, if nobody stands, `allDown` applies
  (`OUTCOME_AUTHORITY.md` §6): captured, left for dead, wakes somewhere worse,
  or `dead` where the world rules death in. The death path can end it sooner.
- **Carrying.** A standing party member can lift a downed one (`stance`,
  `carrying`, §2.7). Lifting costs the action, and so does every exchange of
  carrying after it. While anyone carries, the party can't dash. Putting them
  down is free.
- **Left behind.** A `position` or `move` beat with `leaves` deliberately
  leaves the named party members: they leave the party and stay where they are,
  with the enemies. A downed member nobody is carrying is left behind by any
  movement away, and the HUD flags it on the parse before the message is sent,
  so it is never an accident. An instance that `feeds` goes for a downed or
  left-behind body first and, once it reaches it, stays there: it drops out of
  the encounter and out of any chase. That is the trade.
- **Dead** is HP 0 with the status `dead` and a cause, shown in the state block
  every turn (`Maya — dead (eaten, exchange 14)`). It is permanent campaign
  state (`RPG_STATS.md` §4.4), and nothing on a `recovery` list applies to it,
  which is what stops the model writing the character back in. A dead
  companion leaves the party and her order is cleared. Her gear stays with the
  body; taking it is a `gear` `loot` on the body.
- **What being fed on does is the world's.** Whether `fedOn`, or any entry, is
  in a character's death path is authored from the world's boundary (Master
  Design Section 6, producer `CLAUDE.md` principle #13), separately for
  `{{user}}` and for companions, like the rest of `atZero`. A world that rules
  `{{user}}`'s death out never puts an entry in theirs.

### 3.7f When `{{user}}` dies

- **The fork decides it, never the model:** an HP total and a death path, both
  in the state.
- **The death exchange's reply is the last one.** The fork injects the death as
  fact, with the instruction that this reply ends the story. After it the chat
  is ended: the input is replaced with **Start a new chat**. Swiping the final
  reply gives different prose of the same death, because the rolls are pinned
  (`OUTCOME_AUTHORITY.md` §4.2).
- **The model narrates the death in full and as final.** No last-second
  rescue, no ambiguity, no fade to black that leaves it open. It describes the
  body and the world: what hits, what falls, what the enemies do next, what is
  left in the room.
- **It never writes `{{user}}`'s thoughts, feelings, or last words.** The
  player owns those (`OUTCOME_AUTHORITY.md` §2). What the player wrote in the
  last message, the words said and the last act attempted, is rendered as
  written.
- **The ending is not anti-cheat.** Editing or deleting the fatal message, or
  branching from earlier, stays the player's business (`OUTCOME_AUTHORITY.md`
  §8). The lock ends the story; it doesn't police the save file.
- **Narrating a decided death is not narrating defeat on the player's behalf.**
  `protagonist_jeopardy`'s guardrail stops the model from deciding that
  `{{user}}` lost. A death the fork resolved is the opposite case, and the
  block's wording has to say so when it is built (`OUTCOME_AUTHORITY.md` §5).

### 3.8 Graceful degradation

- **No instance in the encounter can attack** (no natural `attacks`, no weapon
  with `combat` numbers): the enemy side falls back to the behavior before this
  section. The model narrates the enemy's response, and its harm is read back
  as an observation (`RPG_STATS.md` §4.6).
- **No core roll implemented:** no enemy side. Same fallback.
- **No beat pass** (§2.12): no exchange is resolved. The model handles the fight
  under `protagonist_jeopardy`.
- **No `tactics`:** the default `["attack", "close"]`. No `speed`: `1`.
- **No encounter data:** every instance starts `alerted`, nobody ambushes, and
  gunfire's time roll finds nothing.
- **No `system.stealth`:** stealth and evasion checks read no proficiency
  (rank 0, §4.2).
- **No `system.exertion`:** dashes and disengages cost nothing but the action.
- **No `terrain`:** every place has two exits, cover, and no chokepoint.
- **No `pursues` anywhere:** nobody chases, and distance alone decides every
  escape.
- **No `diesWhen`:** downed holds until recovery or `allDown`, as before.

### 3.9 Open questions

- ~~**Escape and avoidance.**~~ Resolved 2026-11-19: awareness (§3.3a),
  suppression (§3.4b), breaking contact and chases (§3.7a–§3.7b), terrain
  (§3.7c), stamina (§3.7d).
- **Initiative and surprise.** Settled in part by awareness (§3.3a): unaware
  enemies, ambush both ways, and a held conditional firing in an ambush step.
  Still open: the encounter data that sets awareness, starting band, and
  ambush (`RPG_STATS.md` §10).
- **Companions.** Settled in part by standing orders (§3.5). Still open:
  whether one may refuse an order mid-fight.
- ~~**Attacks on downed characters.**~~ Resolved 2026-11-19: feeders first,
  others only with nobody standing in reach, and the death path decides what a
  hit does (§3.4, §3.7e).
- **Fights between enemy groups.** Zombies attacking the operators who were
  chasing the party: a three-way fight needs hostility between bestiary
  entries. Deferred on purpose to keep this round small; non-`fearless`
  pursuers just break off (§3.7b).
- **Barricades and holding a door** (§3.7c): nailing it shut, bracing it while
  something pushes.
- **What a pursuer does after losing the party.** Whether it searches, and
  whether it can turn up again later.
- **Talking an enemy down.** A successful intimidation or plea that switches an
  enemy's intent to `withdraw` or `flee`.
- **Statuses from attacks.** `hobbled` is the first (§3.4c). A grab that
  holds, a bite that infects wait on statuses (`OUTCOME_AUTHORITY.md` §10.2).
- **Morale** beyond `fleeAtHpPct`: fleeing when the others fall, or when the
  leader does.
- ~~**Leaving a fight.**~~ Resolved 2026-11-19 (§3.7a–§3.7c).
- **A fleeing `unique` enemy.** Its HP doesn't persist yet (`RPG_STATS.md`
  §7), so it comes back whole.

---

## 4. The core roll — Draft

Decided 2026-11-19. One roll serves every `check`, both sides of a fight, and
every authored check object (`RPG_STATS.md` §3.2). The dice, the bands, how
modifiers combine, and what a band does are decided; the numbers were
calibrated by simulation against stated target curves (§4.6), and play-testing
has the last word.

### 4.1 The roll

**d100 against a chance.** The fork computes a **chance** from a base and
named modifiers (§4.2), clamps it to **5–95**, and rolls d100:

| Roll | Band |
| --- | --- |
| 01–05 | **Success**, always |
| at or under the chance | **Success** |
| up to 20 over the chance, and at most 95 | **Partial** |
| anything higher, and 96–00 always | **Fail** |

At chance 70: 01–70 success, 71–90 partial, 91–00 fail. At chance 5: 01–05
success, 06–25 partial, the rest fail.

- **Nothing is certain and nothing is impossible.** The clamp and the fixed
  ends keep at least a 5% chance of failing and at least a 5% chance of
  succeeding. That is the dice-side form of two `protagonist_jeopardy` rules:
  no auto-success, no no-win scene.
- **Additive, never multiplied.** Every modifier is a number of points added
  to or taken from the chance. Multipliers compound across sources: three
  favourable ones make any roll succeed, and one bad one halves everything,
  which can't be calibrated or shown. Damage is where multiplication belongs
  (§4.3).
- **The roll is pinned** to the user message that made the attempt
  (`OUTCOME_AUTHORITY.md` §4.2), like every other roll.
- **Why d100.** Many small factors each move the odds a little. A percentile
  scale has room for all of them without saturating, and the HUD can show the
  chance as a number the player reads at a glance.

### 4.2 The chance

**Chance = base + every modifier that applies**, then clamped. Each modifier is
a named source, so the HUD can show exactly why the odds are what they are.

| Source | Applies when | Value (§4.6) |
| --- | --- | --- |
| **Base** | always | 35 |
| **Proficiency** | the check reads a proficiency (below) | +10 per rank, scaled to five ranks when the world's `maxRank` differs |
| **Untrained** | a fitting proficiency exists and the actor has none | −10 |
| **Weapon at range** | an attack with a weapon | the weapon's `combat.accuracy` for the target's band (`RPG_STATS.md` §3.3) |
| **Weapon condition** | the copy is below half its durability `max` | −10. A `broken` copy can't be used at all. |
| **Aimed** | weapon `aimed` (§2.7), on an attack of one round | +15, and a success does ×1.5 damage (§4.3), or inflicts `hobbled` when called at the legs (§3.4c). Volume fire, suppression, and overwatch shots get none. |
| **Recoil** | an action fires more than one round that can hit (§4.3) | −10 per round past the first |
| **Ready** | weapon `ready`, the first attack the actor makes in an encounter | +10 |
| **Target in cover** | the target's `cover` is `hidden`, and the attacker hasn't flanked them (§3.4) | −15 |
| **Target unaware** | the first attack on an `unaware` instance (§3.3a) | +20 |
| **Suppressed** | the actor is suppressed (§3.4), on their attacks | −20 |
| **Target prone** | the target's `posture` is `prone` | −10 against ranged, +10 against melee |
| **Exposed** | the target took a partial on a non-attack check this exchange (§4.3), or left cover while suppressed (§3.4) | +10 to the next attack against them |
| **Stress** | the actor isn't `steady` (§4.4) | the level's `mod` |
| **Encumbrance** | a carry tier is in force | the tier's `mod` (`RPG_STATS.md` §3.13) |
| **Authored difficulty** | a check object carries `mod` (`RPG_STATS.md` §3.2) | as authored |

**Which proficiency a check reads.** An attack reads its weapon's
`requires.proficiency`. An ability reads its `uses`. Any other `check` reads
the proficiency the beat pass tags in `skill`, chosen from the world's declared
keys (§2.9): a label, the same kind of classification as an object's type.
With no tag, no proficiency fits: rank counts as 0 and **untrained** doesn't
apply. A bare climb in a world with no climbing skill is a +0 check, not a
penalty.

**Difficulty is never judged from prose.** A check with no authored `mod` is at
standard difficulty. Neither the fork nor the beat pass decides that "this door
looks hard." Where a world wants a harder search or a harder refill, it authors
the `mod` on that check object.

**Defense is the modifiers.** There is no defense stat and no attribute in the
formula. A target is harder to hit because it is in cover, prone, or far away;
it is harder to **hurt** because of armor, which is damage, not chance (§4.3).

**Enemies roll the same way.** An instance's proficiency comes from its
bestiary values (`RPG_STATS.md` §3.5). A natural attack reads its own `rank`,
which defaults by tier: common 1, elite 2, boss 3. Its weapon, if it has one,
brings its `combat.accuracy`. Stress doesn't apply to enemies (§4.8).

### 4.3 What a band does

**One roll per action.** An attack action rolls once, however many trigger
pulls it covers (§3.2a). **Up to 3 rounds can hit:** each pull of a single-round
mode, or each round of a burst. Every round past the first costs recoil
(§4.2). Automatic fire spends more rounds than can hit; the extra rounds do
nothing more to the target, and fired as suppression they pin every instance
in the band (§3.4b). The band decides what the whole action did:

| Band | An attack | A check that isn't an attack |
| --- | --- | --- |
| **Success** | Every round that can hit does, at full damage (×1.5 if aimed). | It works. |
| **Partial** | Every round that can hit does, at half damage (rounded down, minimum 1). | It works, with a cost (below). |
| **Fail** | Nothing hits. The rounds are still spent. | It doesn't work. The cost of trying is still spent (§3.2a). |

**Damage, per hit:** roll the weapon's `combat.damage` (or the natural attack's
`damage`), multiply it by 1.5 on an aimed success or halve it on a partial,
then subtract the target's **armor** reduced
by the weapon's **pierce**, to a minimum of 0. Each hit the armor takes costs
it one use of durability (`RPG_STATS.md` §3.9); a `broken` or `destroyed` piece
absorbs nothing. This is where "the rifle goes through the vest and the Glock
doesn't" lives.

**The cost of a partial, on a check that isn't an attack,** is fixed, so the
model never picks it:

- **Outside a fight: noise.** It works, but loudly. The fork makes a short time
  roll here, the same one a perceived presence asks for (§2.4a). Without
  encounter data, the cost falls away and it is a plain success.
- **Inside a fight: exposure.** It works, and the next attack against the
  actor this exchange gets +10 (§4.2).

**Authored outcomes win.** A check with its own outcomes uses them instead of
this table: a refill under fire loads `full` / `half` / `none`
(`RPG_STATS.md` §3.8.4), a scavenge check halves the table's chances, and
disengaging has its own three results (§3.3).

### 4.4 Stress

Stress is the body's response to danger, tracked per party sheet: hands that
shake, breathing that won't slow, vision narrowing to the threat. It is opt-in
per world (`system.stress`, `RPG_STATS.md` §3.2) and is the first tracked
status after `downed`.

**Three levels.** `steady` (no modifier), `shaken`, `overwhelmed`, each with
an authored `mod` (−10 and −25 in the calibration, §4.6) and a `note` in observable
register.

**It is the body, never the feeling.** The player owns what `{{user}}` feels;
the world owns `{{user}}`'s body (`OUTCOME_AUTHORITY.md` §2). The state block
shows the level and its `note` ("shaken: hands unsteady, breathing fast"), and
the model renders exactly that: the tremor, the breath, the tunnel vision. It
never writes that `{{user}}` is afraid, panicking, or calm. A player who writes
`{{user}}` as cold and composed while their hands shake is characterizing, not
contradicting the state.

**What raises it.** The fork checks these deterministically, from the state:

- **Outnumbered.** When able enemies outnumber standing party members by the
  authored ratios (3:1 for `shaken`, 6:1 for `overwhelmed`, §4.6), each party
  member is raised to at least that level. The count is **threat-weighted**:
  a common enemy counts 1, an elite 2, a boss 4. Fifteen Shamblers against two
  people is 7.5:1; two Rogue Operators against `{{user}}` alone is 4:1.
- **Badly hurt.** A hit that leaves the character at `badly hurt` severity or
  worse (§3.6) raises them one level.
- **An ally goes down.** Every standing party member rises one level.
- **Surprised.** An encounter that starts with an alerted enemy raises the
  party one level.

**Nerve resists it.** When a trigger fires on a character with a rank in the
world's nerve proficiency (`system.stress.check`), the fork rolls nerve for
them: a success resists that trigger, anything else takes it. A character with
no rank simply takes it. This is the world's response, so it rolls
automatically, like an arrival roll. The rank is part of the authored build and
explained in `buildNote`: an ex-soldier is steadier than a nurse.

**What lowers it.**

- **Steadying** ("I take a breath and steady myself") is a `check` with
  `steady: true` that reads nerve and **costs the move** (§3.2a). A success
  lowers the level by one. A partial lowers it by one and exposes the actor.
  A fail changes nothing.
- **The odds improving.** When the enemy-to-party ratio drops below the
  threshold that raised a character, the level drops by one.
- **The encounter ending** resets every party member to `steady`.

**It can't be declared away.** "I'm calm" and "I'm not scared" are feelings:
`flavor`, and they change nothing. "My hands are steady" is a `claim` about
tracked state (`about: state`) and is marked *Not confirmed*. Only steadying,
which is an attempt, moves the gauge.

Party members other than `{{user}}` have their own stress, from their own
sheets. Enemies have none; human enemies breaking is morale, which is open
(§3.9).

### 4.5 What the HUD shows

For every roll: the chance with each source and its points ("Glock at near:
35 base, +40 handguns, +0 range, −10 shaken = 65%"), the d100 result, and the
band. For an attack, the damage per hit and what armor took off. For stress,
each party member's level and what raised it. The exact layout is the fork's.

### 4.6 Calibration

Calibrated 2026-11-19 by simulation: a Monte Carlo of the `RPG_STATS.md` §8
zombie world, 12,000–20,000 fights per case, against the target curves below.
The curves are the design intent; the numbers are what hits them. Play-testing
has the last word.

**Engine constants** (the fork's, the same in every world):

| Constant | Value |
| --- | --- |
| Base chance | 35 |
| Per proficiency rank | +10 (untrained −10; no fitting proficiency 0) |
| Aimed | +15, and a success does ×1.5 damage. One round only. |
| Ready, first attack of the encounter | +10 |
| Recoil | −10 per round past the first that can hit |
| Rounds that can hit, per action | at most 3 |
| Target in cover / prone | −15 / −10 against ranged, +10 against melee |
| Exposed | +10 |
| Partial band | 20 points over the chance |
| Clamp | 5–95, with 01–05 and 96–00 fixed |
| Stress | `shaken` −10, `overwhelmed` −25; outnumbered at 3:1 and 6:1, threat-weighted (§4.4) |
| Natural attack rank by tier | common 1, elite 2, boss 3 |
| Target unaware / actor suppressed | +20 / −20 |
| Suppression pins | success 3 (automatic fire: the whole band), partial 1 |
| Bleed-out, when a world doesn't set it | 3 exchanges |

**Target curves.** What a fight should feel like, with the measured result for
the §8 world. `{{user}}` fights alone at 100 HP, shooting first unless noted.

*A common enemy (a Shambler, 40 ± 10 HP), `{{user}}` with a Glock:*

| Shamblers | Target | Single shots | Aimed | Three pulls |
| --- | --- | --- | --- | --- |
| 1 | trivial | loses ~9 HP | ~3 HP | ~2 HP |
| 3 | dangerous to careless play | downed 26% | 1% | 0.5% |
| 5 | lethal standing your ground: run | downed 100% | 91% | 41% |

*Trained human enemies (the Rogue Operator: rifles 2 ± 1, 80 ± 10 HP, a
vest, a C8), downed rate in the open / from cover, stress included:*

| Operators | Target | `{{user}}` with a C8 | `{{user}}` with a Glock |
| --- | --- | --- | --- |
| 1 | the adrenaline fight: winnable, costly | 0% / 0%, ends near 65 HP (47 if the operator shoots first) | 22% / 10% (47% / 23% if the operator shoots first) |
| 2 | very bad odds | 77% / 48% | ~100% / 99% |
| 3 | nearly hopeless | 100% / 99% | 100% |
| 4 or more, in the open | game over | 100% | 100% |

**The curve moves with the protagonist's weapon.** A rifle-armed protagonist
sits on the curve as written; a sidearm moves every row one step worse. That is
deliberate: the weapon gap is what makes finding a rifle matter.

**The action trade-off.** Against one Shambler with the Glock: three pulls kill
fastest (2.1 exchanges) at the most ammunition (6.3 rounds); an aimed shot is
nearly as fast (2.6) at the least (2.6) but costs the move; a plain single shot
is slowest (3.9) and leaves the move free. No option dominates.

**World authoring targets.** World data is authored, not engine-fixed, and is
checked against these (`RPG_STATS.md` §6):

- **A common enemy** dies in about 3 hits from the world's standard sidearm,
  or 2 from a rifle.
- **Human enemies** have 60–90 HP. Armor, not HP, makes them tough.
- **An elite** takes 4–6 exchanges for a trained, properly armed character.
  **A boss** takes 10–15, with phases.
- **A common enemy's hit** costs about 5–10% of a protagonist's max HP; **an
  armed elite's** about 15–25%.
- **Danger scales with numbers.** One common enemy is trivial, three are
  dangerous to careless play, five or more mean run. One trained human is a
  fight; two or three are very bad odds; four or more in the open are game
  over.

**What the simulation assumed.** `{{user}}` always aims (when aiming), stands
still, and acts first unless noted. Maya isn't fighting. Suppression, flanking,
fleeing, and stealth aren't in the curves above. Flanking makes groups worse;
fleeing and stealth are what make them avoidable, measured below.

**Lethal is not no-win.** These curves make groups lethal by design. A lethal
fight stays inside the `protagonist_jeopardy` guardrail only while there is a
way out of it: running, hiding, or never being seen (§3.3a, §3.7a–§3.7c).
Measured 2026-11-19 under those rules, `{{user}}` alone at 100 HP and 60
stamina:

| Situation | Got away | Cost |
| --- | --- | --- |
| 5 Shamblers at `near`, `{{user}}` runs | 100% | 0 HP, about 2 exchanges (1–3 HP with one or two already engaged) |
| 4 Rogue Operators at `near`, `{{user}}` in cover, just runs | 95% | ~72 HP |
| … laying Glock covering fire (3 pulls) while running | 91% | ~54 HP |
| … laying C8 automatic suppression while running | 95% | ~27 HP |
| 2 Rogue Operators, Glock covering fire | 100% | ~11 HP (36 just running) |
| 3 Runners chase, stealth 3 | 90% | ~4 HP; otherwise stamina runs out and it's a fight |
| … `{{user}}` shaken | 76% | ~8 HP |
| … with Maya (her stealth 1 sets the roll) | 59% | ~13 HP |
| … the same Runners, hobbled | ~100% | ~0 HP |
| 1 / 2 / 4 Rogue Operators chase | 100% / 96% / 83% | ~12 / 23 / 36 HP |

Getting away from the dead costs stamina; getting away from guns costs blood,
and suppression is what brings that price down. Runners are the gamble the
design wants: keep rolling, cut someone loose, or turn and fight. The
breaking-contact rows count the fight up to the moment of escape; operators
who pursue then start a chase, priced in the last row.

### 4.7 Graceful degradation

- **No `combat` numbers on a weapon:** it has no accuracy modifier and no
  damage; an attack with it can't hurt anything, and the fallback in §3.8
  applies.
- **No `system.stress`:** no stress, no nerve rolls, no steadying. A
  `steady: true` check becomes an ordinary check with no effect on the state.
- **No carry tier `mod`:** encumbrance adds no modifier, as before.
- **An unknown `skill` tag** counts as no tag: rank 0, no untrained penalty.

### 4.8 Open questions

- **Play-testing the calibration** (§4.6), especially with cover, companions,
  and flanking in play, which the simulations modeled only in part.
- **Vision.** Darkness and visibility should come from the world, not the
  player: the Scene Tracker's time of day, or a place's lighting. No signal is
  chosen.
- **Social checks.** Persuading, lying, and intimidating need something on the
  NPC side to roll against, and the posture contract governs what a success
  may mean. A round of its own, together with talking an enemy down (§3.9).
- **Critical results.** None in v0.
- ~~**Suppression.**~~ Resolved 2026-11-19 (§3.4b).
- **Attributes.** Not part of the formula in v0 (`RPG_STATS.md` §10).
- **Morale** for enemies, as stress's counterpart (§3.9).
- **Dice grammar** shared with the dice oracle (§1).

---

## 5. Boundary with the producer

World Forge authors **starting values and world data** (stats, items, sheets,
bestiary, vendors, scavenge tables). It never authors resolution rules, never
emits roll logic, and carries no carrier for this contract. If resolution needs
a new piece of authored world data (a difficulty table, a weapon's damage
range, an encounter chance per kind of place), that field is added to
`RPG_STATS.md` and produced there; this document defines only how the engine
uses it.

## 6. Relationship to the other contracts

| Concern | Governed by |
| --- | --- |
| What exists: stats, items, sheets, bestiary (including attacks, speed, tactics, pursuit and feeding), stamina, terrain, death paths, economy | `RPG_STATS.md` (Draft) |
| Who decides: attempts vs. results, pinned rolls, legality | `OUTCOME_AUTHORITY.md` (Draft) |
| How an attempt resolves: beats, the exchange budget and the enemy side of a fight, escape, chases, death, the core roll, modifiers, stress, parsing | this document (§2–§4 Draft, rest Placeholder) |
| Stateless narrative roll tables | `DICE_ORACLE.md` |
