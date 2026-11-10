# Resolution Contract — how attempts become outcomes

**Status:** Placeholder · **Version:** 0 · **Last updated:** 2026-11-09

> **Shared contract — canonical source of truth:**
> [`AndreiNicu/World-Forge`](https://github.com/AndreiNicu/World-Forge) → `contracts/RESOLUTION.md`.
> Copies in other repositories (including the SillyTavern fork) are mirrored
> **read-only**. Do not edit a copy — edit the canonical file, then run the
> contract sync (`scripts/sync-contracts.sh`). A CI drift check keeps every copy
> byte-identical to this canonical version.
>
> **Placeholder — authored from the consumer side.** This file has no content
> yet. It will be written by the SillyTavern fork's side, which owns the
> runtime internals this contract describes. World Forge only produces the data
> the engine consumes (`RPG_STATS.md`, `DICE_ORACLE.md`); how that data is
> handled at runtime is the fork's to define. No agent spec references this
> document and nothing in this repo depends on it.

---

## What will live here

The engine half of the RPG layer: everything between "`{{user}}` attempts
something" and "the fork commits a result."

- **The core roll** — the dice system, and how a roll maps onto the three
  outcome bands (success / partial / fail) that `RPG_STATS.md` and
  `OUTCOME_AUTHORITY.md` already use.
- **The math** — how proficiency ranks, attributes, and modifiers turn into
  odds; difficulty and who sets it.
- **The modifier stack** — named sources (rank, attribute, weapon condition,
  encumbrance tier, statuses, cover, range, fire mode), so the HUD can show why
  the odds are what they are.
- **Time** — what a beat or round is in chat play; refill and reload duration;
  initiative and turn order.
- **Combat** — attack, damage, armor, what a fire mode does to a hit (the
  reserved `combat` field in `RPG_STATS.md` §3.3).
- **Dice grammar** — dice notation and roll syntax, shared with the dice oracle
  where it can be.
- **Attempt interpretation** — how the small model parses `{{user}}`'s message
  into structured attempts before generation, and how the main model's reply is
  parsed into observations after it.
- **The deferred mechanics built on the core** — what carry tiers do, repair
  checks, vendor restocking, and the other items `RPG_STATS.md` §7 defers to
  resolution.

## Boundary with the producer

World Forge authors **starting values and world data** (stats, items, sheets,
bestiary, vendors, scavenge tables). It never authors resolution rules, never
emits roll logic, and carries no carrier for this contract. If resolution needs
a new piece of authored world data (a difficulty table, a weapon's damage
range), that field is added to `RPG_STATS.md` and produced there; this document
defines only how the engine uses it.

## Relationship to the other contracts

| Concern | Governed by |
| --- | --- |
| What exists: stats, items, sheets, bestiary, economy | `RPG_STATS.md` (Draft) |
| Who decides: attempts vs. results, pinned rolls, legality | `OUTCOME_AUTHORITY.md` (Draft) |
| How an attempt resolves: dice, math, modifiers, parsing | this document (Placeholder) |
| Stateless narrative roll tables | `DICE_ORACLE.md` |
