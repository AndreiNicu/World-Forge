# Outcome Authority Contract — who decides what happened

**Status:** Draft · **Version:** 0 · **Last updated:** 2026-11-05

> **Shared contract — canonical source of truth:**
> [`AndreiNicu/World-Forge`](https://github.com/AndreiNicu/World-Forge) → `contracts/OUTCOME_AUTHORITY.md`.
> Copies in other repositories (including the SillyTavern fork) are mirrored
> **read-only**. Do not edit a copy — edit the canonical file, then run the
> contract sync (`scripts/sync-contracts.sh`). A CI drift check keeps every copy
> byte-identical to this canonical version.
>
> **Draft — exploration, neither side exists.** This document has no carrier and
> emits nothing. No agent spec references it, no preset block implements it, and
> nothing in the fork enforces it. It records the rules the RPG layer
> (`RPG_STATS.md`) and the preset are meant to converge on, so they can be
> prototyped against one design. Sections marked **sketch** are deliberately
> loose and expected to move.

This document specifies **who has authority over outcomes** in a world with
tracked state: rolls, stats, inventory, and the conditions characters are in.
It is the rule the stat layer stands on. A tracked HP figure is worth nothing if
the player can type it away.

---

## 1. Purpose and scope

### 1.1 The problem

The model was trained to satisfy the person typing (producer `CLAUDE.md`
principle #13). In a world with tracked state, that habit shows up in a specific
form: **the model treats `{{user}}`'s message as a state change rather than an
attempt.** Two examples:

- **Claiming what isn't there.** "I pull Excalibur out of my pack" in a zombie
  survival world. Or, more quietly, "I grab my carbine" when `{{user}}` has no
  carbine. The model goes along with it, and the sword or the carbine now exists.
- **Undoing what happened.** `{{user}}` is downed by a roll. The next message:
  "but I wasn't, I roll aside at the last second." Or: "Maya shakes it off and
  gets up." The model goes along with it, and the roll stops meaning anything.

Both are the posture contract's **auto-success** and **rescue from
consequence**, aimed at mechanical state instead of at an NPC's will. The
`protagonist_jeopardy` block (`agent_roles/05a_Block_Library.md`) addresses the
disposition. It doesn't reach these cases, because it has no state to point at.
This contract supplies that state's authority.

### 1.2 Scope: the in-fiction path only

This contract makes outcomes immutable **from inside the fiction**. Typing a
denial, a claim, or a retcon into the chat does nothing to the state.

It does **not** defend the out-of-fiction path. The chat file belongs to the
player. Editing a message, deleting one, editing JSON, branching a chat from an
earlier point: these are the player's tools, and a player who uses them to cheat
is choosing to spend their own fun. No ironman mode, tamper detection, or
rewind lock is planned (§8).

### 1.3 Relationship to v0 stats

`RPG_STATS.md` v0 prototypes the stat shape: what a character *has*. Combat
resolution, statuses, and recovery are deferred there. This document is where
the authority rules for those later pieces are explored ahead of time, so v0's
shape doesn't harden in a way that contradicts them. §9 lists the passages in
`RPG_STATS.md` that this document expects to change when it settles.

---

## 2. The rule

> **`{{user}}`'s message is an attempt. It is never a state write.**

The player owns `{{user}}`'s **choices**: what they try, what they say, what
they want, how they feel. The world owns `{{user}}`'s **body, pockets, and
outcomes**: whether the legs work, what is in the pack, whether the swing lands.

This is the line that keeps the rule compatible with the Main Prompt's
protagonist-agency rule. "I leap up" is a choice and the player is entitled to
make it. "Your legs don't answer" is the world responding to it, not the model
taking over `{{user}}`'s turn.

### 2.1 Order of authority

When sources disagree about what is true, the higher one wins:

| Rank | Source | Example |
| --- | --- | --- |
| 1 | **Committed campaign state and pinned rolls** (fork) | HP 0, `downed`; inventory has no carbine; roll result: miss. |
| 2 | **World facts** (lorebooks, item catalog, dice-oracle facts) | Swords of legend do not exist here. The carbine is a catalog item. |
| 3 | **The model's narration** | "The Shambler's teeth find your forearm." |
| 4 | **`{{user}}`'s message** | "I dodge and I'm fine." — intent only. |

Rank 4 never overrides ranks 1–3. Rank 3 never overrides 1–2: the model may not
narrate a revival the state doesn't show, any more than the player may declare
one.

### 2.2 The closed list of state writers

Campaign state changes **only** through:

1. **Rolls the fork makes**, logged and pinned (§4.2).
2. **Commits from defined events** (`RPG_STATS.md` §4.4: encounter end, item
   used/gained/lost, equipment change, permanent effect, death, party change).
3. **The model's report of the world's response**, parsed by the fork. The model
   reports what the world did to `{{user}}` ("took a bite"). It never relays
   what `{{user}}` claimed ("wasn't hurt").

`{{user}}`'s message text is not on this list. It can *propose* an action the
fork then resolves (drink a dressing → the fork checks inventory → commit). It
cannot write a result.

---

## 3. Four kinds of claim

### 3.1 Possession claims — the thing exists, `{{user}}` doesn't have it

"I draw my Glock" with no Glock in inventory or equipment. "I use a field
dressing" with zero dressings.

- **Resolution:** the action fails inside the fiction. The hand finds an empty
  holster; the pouch is empty.
- **Who catches it:** the fork, deterministically, when the message names a
  catalog item (§4.1a). For an object the catalog doesn't list, the small-model
  classification (§4.1b) first decides whether it can exist here at all. If it
  can, the on-person rule applies: an uncatalogued object `{{user}}` produces
  from their own pack or pocket isn't there, because the inventory is the record
  of what they carry. The model catches the rest, from the state block.
- **Possession is matched by type, not by brand** (decided 2026-11-09). If the
  sheet holds `glock_17` and the player writes "I draw my Beretta," both are
  `firearm.handgun` (§4.5), so the fork treats it as the handgun they carry.
  The player isn't refused for misremembering the model on their sheet. A claim
  fails only when the inventory holds nothing of that type.

### 3.2 Premise claims — the thing cannot exist in this world

"I pull out Excalibur" in a zombie survival world. A plasma rifle in a medieval
world. A spell in a world with no magic.

- **Resolution:** the premise is declined, not the attempt resolved. There is no
  sword to fail to swing.
- **Who catches it:** the fork first. A small model classifies the object by
  **type** and **nature** (§4.1b, §4.5), and the fork looks the result up
  against the world's **absent list**. Excalibur classifies as `melee.blade`
  (an ordinary type in a zombie world) with nature `magical` and `legendary`
  (both absent), so it cannot exist here. A Glock in a samurai RPG is a
  mundane object, but its type `firearm.*` is absent there. The main model,
  through the engine block (§5), catches whatever the check misses. This is
  the "world-integrity enforcement against `{{user}}`'s inputs" that
  principle #13 lists as not yet built.
- **The target is the big red flags, not every edge** (decided 2026-11-09).
  Magic in a zombie world, energy weapons in a modern one, firearms in a
  medieval one. Borderline and unknown objects are allowed. A player who games
  the fine edges is spending their own fun (§1.2), and anything that slips
  through still carries no stats (next bullet).
- **Always refused inside the story** (decided 2026-11-05). No out-of-character
  note: "There's no sword. Your hand is still wrapped around the rebar."
- **The catalog is closed for mechanics, not for objects.** Any ordinary object
  the scene supports can be picked up and used: a brick, a kitchen knife, a
  chair. An object without a catalog entry simply carries no stats, so
  improvisation stays free and a premise claim can't buy a mechanical edge even
  when it slips past the model.

### 3.3 Outcome denial — undoing what was resolved

"I wasn't downed." "The bite missed after all." "Maya gets back up."

- **Resolution:** the outcome stands. A downed character stays downed until a
  defined recovery happens (§6). The message is read as what `{{user}}` tries
  next, and the world answers that try from the current state.
- **Refused inside the story, and an attempt against the state can cost**
  (decided 2026-11-05). An action the state forbids is not a no-op. It is
  attempted, it fails, and the world answers it the way the state says it
  would. With a broken leg on the sheet, "I jump up" becomes: `{{user}}` tries
  to jump, the broken leg grinds bone on bone, the pain whites out the room, and
  HP drops further. The cost is derived from the state (the break), never
  invented to punish the try (§5 counter-guardrail). The model narrates the
  damage as the world's response; the fork picks it up as an observation and
  commits it (§2.2 writer 3).
- **Who catches it:** the fork, by injecting the status as authoritative fact
  every turn while it holds (§4.4). The model, by never narrating a recovery
  the state doesn't show.

### 3.4 Result declarations — stating the outcome of one's own attempt

"I shoot him in the head and he drops dead." "I talk the guard into letting me
through."

- **Resolution:** the first half is the attempt; the second half is ignored.
  The world decides the result.
- **Who catches it:** while combat resolution is deferred (`RPG_STATS.md` §7),
  the model judges the result, governed by `protagonist_jeopardy`'s
  "a stated attempt is an attempt." When pre-generation resolution exists, the
  fork rolls first and injects the result (fail / partial / success), the same
  what/how split as the dice oracle.

---

## 4. Consumer mechanisms — sketch, not implemented

### 4.1 Legality check before generation

Two passes, cheapest first. Both run before the request goes to the main model.

#### 4.1a Deterministic pass

The fork checks the parts of `{{user}}`'s message it can check **for certain**:

- a named catalog item (by `name`) when nothing of its **type** is in
  inventory or equipment (§3.1);
- an action while `{{user}}`'s status forbids it (`downed`, `dead`);
- an ability whose `cost` exceeds the current resource.

On a hit, the fork **injects an authoritative fact** ("`{{user}}` has no
carbine."; "`{{user}}` is downed: can speak and crawl, cannot fight.") so the
model writes the failure inside the fiction. The refusal lives in the story,
not in a UI notice (§10.1). The fork never rewrites or blocks the player's
message.

This pass is deliberately narrow: a false positive refuses a legal action,
which is worse than a miss the later layers will usually catch.

#### 4.1b Small-model classification pass (decided 2026-11-05, narrowed 2026-11-09)

For an object the message names that is **not in the catalog**, a small, cheap
model call **classifies** it. It never decides whether the object may exist;
the fork does that by lookup.

- **Input:** the object as named, the sentence it appears in, and the shared
  classification vocabulary (§4.5).
- **Output:** a type and a set of natures, or `unknown`:

  ```jsonc
  { "object": "Excalibur", "type": "melee.blade", "nature": ["magical", "legendary"] }
  { "object": "Beretta",   "type": "firearm.handgun", "nature": ["mundane"] }
  { "object": "the thing from my dream", "type": "unknown" }
  ```

  Nothing else. The pass does not judge whether `{{user}}` *has* the object,
  whether the action succeeds, or anything about the scene. Small models
  classify well-known real-world objects reliably (Beretta → handgun, AK-47 →
  rifle, RPG-7 → launcher). That is the reason the question is narrowed to
  classification rather than open-ended plausibility.
- **The fork's lookup:** if the type or any nature appears in the world's
  absent list (§4.5), the fork injects an authoritative fact ("No such object
  exists in this world.") and the main model refuses the premise in-story
  (§3.2).
- **Otherwise, and always on `unknown`:** no injection. The object is an
  ordinary, uncatalogued object: usable if the scene supplies it, absent if
  `{{user}}` claims it from their own person (§3.1), and mechanically
  weightless either way.
- **World-invented names** ("a Halvorsen M9," "a Veilstone blade") mean nothing
  to a small model. They must be catalog items with their `type` and `nature`
  authored, which is natural: a world that invents the name is already defining
  the item.

Result declarations and other fuzzy claims stay with the main model and the
engine block.

**Not yet scoped: creating items during play.** Gameplay may need to build new
items and weapons that the pipeline never authored (crafting, a found prototype,
a modified weapon). That would let a plausible uncatalogued object gain stats
and enter the campaign's catalog, which is outside the pipeline's scope and
needs its own investigation. If it's built, the classification pass is its natural
first gate: an object whose type or nature is absent here can't be crafted
either, and crafted outputs would be catalog items with an authored type.

### 4.2 Rolls are pinned to the user's message

A roll that resolves `{{user}}`'s attempt is keyed to **the user message that
made the attempt**, not to the reply that narrates it.

- **A swipe or regeneration replays the same roll.** A swipe asks for different
  prose, not a different fate. The new reply narrates the same miss.
- **Editing or deleting the user message** is out-of-fiction (§1.2). The fork
  treats an edited message as a new attempt and rolls again. A player can
  re-roll that way; that is their choice to make.

This replaces the current wording of `RPG_STATS.md` §4.3, which lets swipes
inside a fight discard working-copy changes "so a re-roll can't permanently cost
anything." Under that wording, swiping until a roll succeeds is free.

### 4.3 Corrections fix parsing, never outcomes

`RPG_STATS.md` §4.6 lets the player confirm or correct a change the fork picked
up from narration. That stays, narrowed:

- A correction fixes a **parse error**: the fork misread the narration (logged
  20 damage when the reply said the vest stopped it).
- It is a **UI action**. Chat text never counts as a correction.
- It can never change a **roll result** or a status a roll produced.

### 4.4 Status is restated every turn it holds

While a sheet is `downed` (or any later status), the state block (`RPG_STATS.md`
§4.5) states it each turn with what the character can and cannot do. Restating
it is what stops the model drifting out of it three messages later, the same
reason `ARC_STATE` fires constantly.

### 4.5 Classification vocabulary and the absent list — sketch

**One shared vocabulary, owned by the fork, the same in every world.** Worlds
don't invent categories; they mark which ones are absent. One vocabulary keeps
the small model consistent across worlds and gives a validator something to
check.

**Axis 1 — type**, two levels (class → type):

| Class | Types |
| --- | --- |
| `firearm` | `handgun`, `smg`, `rifle`, `shotgun`, `heavy` |
| `melee` | `blade`, `blunt`, `polearm` |
| `ranged` | `bow`, `crossbow`, `thrown` |
| `explosive` | `thrown`, `launcher`, `placed` |
| `energy` | `handheld`, `heavy` |
| `focus` | `staff`, `wand`, `talisman` (magical implements) |
| `consumable` | `medical`, `food`, `drug` |
| `armor` | `light`, `heavy`, `shield` |
| `tool` | `general` |

A knife and a katana are both `melee.blade`; a Beretta is `firearm.handgun`; an
AK-47 is `firearm.rifle`; an RPG launcher is `explosive.launcher`. The table is
a starting point and expected to grow.

**Axis 2 — nature**, a set: `mundane`, `magical`, `futuristic`, `legendary`.
Type says what kind of object something is; nature says what kind of world it
belongs to. **Type alone cannot catch the red flags:** Excalibur is just a
sword by type. The flags live on the nature axis.

**Kept out of the vocabulary on purpose:** fire mode (semi / automatic) is an
item property, not a type level, because one rifle can do both, and it only
matters once combat resolution exists. Size and reach (knife vs. katana) are
likewise later item properties.

**The world's absent list** names what cannot exist, by either axis:

```jsonc
// zombie survival, present day
"absent": { "nature": ["magical", "legendary", "futuristic"], "type": ["focus.*", "energy.*"] }

// samurai RPG
"absent": { "nature": ["futuristic"], "type": ["firearm.*", "explosive.*", "energy.*"] }
```

The Interviewer already knows this by the end of Phase 0 ("Is there magic?
Future technology? What era?"). Where the list is carried is open (§10.2).
Catalog items gain `type` and `nature` fields so possession matching (§3.1) and
the lookup work on authored items too (§9).

---

## 5. Engine half — the `outcome_authority` preset block (sketch, not in force)

The model-side half belongs in the preset, on the engine side of the override
contract (principle #2): it is world-agnostic, like `dice_oracle` and
`protagonist_jeopardy`. **Not in force:** no entry exists in
`agent_roles/05a_Block_Library.md` and the Prompt Engineer must not emit it yet.

Expected content, in the same frame-first, guardrail-weighted shape as the
posture blocks:

- **The frame, positively stated, first.** The state block and the world's lore
  are the record of what is true. `{{user}}`'s messages are a co-author choosing
  what `{{user}}` attempts; the world decides what comes of it. Holding to that
  is what makes the player's wins mean anything.
- **An attempt is not a result.** A message that states an outcome
  ("…and he drops dead") supplies the attempt; the world supplies the outcome.
- **Actions against the state are attempted, fail, and can cost.** Reaching
  for an item the state doesn't list finds nothing; a downed character trying to
  stand can't. Narrate the attempt and the body's or world's answer to it, the
  way the state says it would go: a jump on a broken leg grinds bone on bone and
  hurts them further. Never a silent no-op, never commentary.
- **What cannot exist here, isn't here.** A declaration that contradicts the
  world's established reality is refused inside the story, always ("There's no
  sword. Your hand is still wrapped around the rebar."). No out-of-character
  note, no lecture.
- **No narrated recovery.** Never write a downed or dead character, `{{user}}`
  or anyone else, back into action unless the state shows the recovery.
- **Counter-guardrail, stated with equal weight (non-optional content):** this
  is not licence to refuse. Legal actions resolve normally. Improvising with
  ordinary objects the scene supports is allowed and carries no mechanics. The
  model still never writes `{{user}}`'s choices, dialogue, or feelings, and
  never invents a failure the state and the world don't supply. A cost follows
  from the state (the break, the empty magazine), never from a wish to punish
  the try. The body is the world's to render (the bone grinds, the leg
  buckles, the pain hits); what `{{user}}` feels about it and does next is the
  player's. *Integrity, not obstruction.*
- **Composes with, doesn't restate:** `protagonist_jeopardy` (the disposition
  behind auto-success and rescue), `dice_oracle` (how injected facts are read),
  Consequence Tracking (in-scene continuity).
- World-agnostic: no character, arc, faction, or item names.

**Open:** one new block, or a state-aware extension of `protagonist_jeopardy`.
A separate block is cleaner to toggle (only RPG worlds and oracle worlds need
the state half), but the premise-refusal half applies to every world, RPG or
not, and may belong in the jeopardy block or jailbreak clause 2b instead (§10).

---

## 6. Downed and recovery — sketch for `RPG_STATS.md`

`RPG_STATS.md` §3.7 defines `"downed"` as "out of the fight, alive,
recoverable" without saying *how* a character recovers. A status with no
recovery rule gets recovered by narration, which is the outcome-denial hole
(§3.3). The proposed extension, shape not settled:

```jsonc
"atZero": {
  "default": "dead",
  "persona": {
    "state": "downed",
    "allows": ["speak", "crawl"],          // what a downed character can still do
    "recovery": [                           // the ONLY ways out of downed
      { "by": "ability", "tag": "revive" }, // an ability tagged revive (Maya's Triage)
      { "by": "item",    "tag": "revive" }, // an item tagged revive
      { "by": "encounterEnd", "requires": "allyStanding", "restoreTo": 1 }
    ],
    "allDown": "captured"                   // what happens when the whole party is downed
  }
}
```

- **`allows`** feeds the legality check (§4.1) and the state block (§4.4).
- **`recovery`** is closed: nothing outside the list ends the status. A revive
  ability is itself an attempt the fork resolves.
- **`allDown`** is authored from Master Design Section 6's permitted shapes of a
  lost scene (captured, left for dead, wakes somewhere worse), never defaulted.
  It is the posture contract's boundary turned into a rule, the same way
  `atZero` already ties to it.

A plain string `"downed"` keeps working and means "recovers at encounter end if
any ally stands" until the field is settled.

---

## 7. Graceful degradation

- A world with no `[[RPG_STATS]]` carrier has no state to enforce. Only the
  premise-refusal rule and `protagonist_jeopardy` apply.
- With no legality check implemented, the state block alone carries authority
  and the model enforces it. Weaker, still correct in direction.
- With no small model configured, §4.1b is skipped and the main model alone
  handles premise refusal through the engine block.
- With no `recovery` field, the default in §6 applies.

---

## 8. Non-goals

- **Out-of-fiction cheating.** Editing JSON, editing or deleting messages,
  branching a chat. Not detected, not prevented. The player owns the chat.
- **Ironman / rewind locks.** Not planned; same reason.
- **Combat resolution.** Belongs to `RPG_STATS.md` when it lands. This document
  only fixes the rule that a resolution, once made, holds.
- **Narrowing creativity.** Uncatalogued objects, clever plans, and legal
  actions the author didn't foresee are all fine. The rule is about results,
  not about what may be tried.

---

## 9. Expected changes to `RPG_STATS.md` when this settles

| Passage | Change |
| --- | --- |
| §4.3 working copy | Swipes replay pinned rolls (§4.2); only out-of-fiction edits re-roll. |
| §4.6 rolls and observations | Corrections are parse-only, UI-only, never against a roll (§4.3). |
| §3.7 `atZero` | `downed` gains `allows`, `recovery`, `allDown` (§6). |
| §4.5 what the model sees | Status lines with allowed actions are restated each turn (§4.4). |
| §1.2 who owns what | Points here for the authority order (§2.1). |
| §3.3 `items[]` | Items gain `type` (from the §4.5 vocabulary) and `nature`; possession is matched by type (§3.1). |

---

## 10. Decisions and open questions

### 10.1 Decided (2026-11-05)

- **Plausibility is a small-model check** (§4.1b), not name-matching alone. (Narrowed on 2026-11-09 to classification; see 10.1b.)
  Catalog matching stays as the deterministic first pass (§4.1a); the small
  model answers only "would this object make sense within this roleplay's
  boundaries?" for objects the catalog doesn't list.
- **Refusals are always in-story** (§3.2, §3.3, §5). No out-of-character
  fallback. An attempt the state forbids is narrated as attempted and failed,
  and can cost the character what the state says it would.

### 10.1b Decided (2026-11-09)

- **Big red flags only** (§3.2). The goal is catching magic in a zombie world,
  not policing every edge. Borderline and unknown objects are allowed.
- **The small model classifies; the fork decides** (§4.1b). The open-ended
  plausibility question is replaced by classification on two axes, type and
  nature (§4.5), looked up against the world's absent list.
- **Types, not brand aliases** (§4.5). A Beretta is a handgun, an AK-47 a
  rifle, a katana a blade. Possession is matched by type (§3.1).
- **Deferred:** rarity tiers (they belong to loot: drop rates and one-per-campaign
  `unique` items, not to existence), fire mode and size as item properties
  (they matter once combat resolution exists), and improvised-weapon catalog
  entries (same reason).

### 10.2 Open

- **Where premise refusal lives.** It applies to every world, with or without
  stats. Candidates: the new `outcome_authority` block, `protagonist_jeopardy`,
  or jailbreak clause 2b. Undecided.
- **Where the absent list is carried** (§4.5). It applies to every world,
  with or without stats, so it may not belong in the `[[RPG_STATS]]` carrier.
  Leading candidate: its own small enabled-but-inert carrier (working name
  `[[WORLD_BOUNDS]]`), authored by the pipeline from Phase 0, with the usual
  seed → Interviewer → Refiner → Architect → Editor → Compiler → validator
  wiring. With no list present, §4.1b is skipped.
- **Growing the vocabulary** (§4.5). Who adds a class or nature, and how a
  consumer treats a type it doesn't recognize (proposed: as `unknown`, so
  allowed).
- **Creating items during play** (§4.1b). Crafting, modifying, or finding items
  the pipeline never authored, so a plausible uncatalogued object can gain
  stats. Outside the pipeline's scope; needs its own investigation.
- **The `allows` vocabulary.** Free strings, or a small fixed set the legality
  check can act on.
- **Statuses beyond downed.** Broken limbs, bleeding, restrained, blinded, each
  with its own `allows` and the cost of acting against it. The broken-leg case
  in §3.3 needs these, so `RPG_STATS.md`'s reserved `statuses` field is
  probably needed before combat resolution is. This document's §6 shape is meant
  to generalize to them.
- **Oracle facts.** Dice-oracle rolls are manual and already fixed once rolled;
  confirm a swipe never re-rolls them either.

---

## 11. Relationship to the other contracts

| Concern | Governed by |
| --- | --- |
| Stat system, sheets, items, bestiary, campaign state | `RPG_STATS.md` |
| Rolled facts injected as authoritative context | `DICE_ORACLE.md` |
| Who decides outcomes, and what `{{user}}`'s message can and cannot change | this document |
| The disposition (yield, auto-success, rescue) | producer `CLAUDE.md` principle #13, `protagonist_jeopardy` |
| `{{user}}` as reference data, never impersonation | producer `CLAUDE.md` principle #14 |
