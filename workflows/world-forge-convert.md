---
description: A workflow to reframe an existing shipped world into a new build — different protagonist, different World Mode, different Style Contract, different Core Concept — or, in Rebaseline mode, to consolidate a revised world into a clean rebuild of itself. Produces a new World Seed; the standard pipeline runs from Phase 1 onward.
---

# THE WORLD FORGE CONVERSION PIPELINE
*Orchestrator (convert fork) — Reframing Shipped Worlds Into New Builds*

**When to use:** an existing shipped world (Phases 0–5.5 complete, Export/ ready, in play or post-launch) has structural content — world rules, factions, cosmology, NPCs — worth reusing under a new protagonist, a new World Mode, a new tonal register, or a new Style Contract. The Converter reads the source's `Master_Design.md`, captures the user's keep/modify/regenerate decisions, and authors a new `World_Seed.md` in a fresh target project folder. The regular pipeline (`/worldforge skip phase0`) then builds the new world end-to-end.

**Also use for consolidation:** a world that has accumulated enough revisions (R1…R[N]) that rebuilding clean beats another surgical edit — especially when new mechanics are coming. That is **Rebaseline mode** (`--rebaseline`, see REBASELINE MODE below): same world, same protagonist, rebuilt fresh from its post-revision state.

**When NOT to use:**
- **Pure reskin** — if the user is replacing setting + protagonist + factions + tone all at once, the Converter refuses (see Phase C1 overlap floor below). That's a new world inspired by the source; run `/worldforge start` fresh and use the source as creative reference.
- **Surgical changes to a shipped world** — use `/worldforge revise` instead. Convert is for "reframe and rebuild," not "fix a voice."
- **In-build worlds** — the source world must have shipped (REFINER SIGN-OFF + Export/ present). For worlds still in Phase 0–5, finish the original pipeline first.
- **Mashups** — single source only. Cannot convert from two source worlds simultaneously.

**The bright lines the Converter is the legitimate path for.** Three categories of change explicitly bounce out of the revise pipeline (`workflows/world-forge-revise.md`):
- **Master Design Section 1 (Core Concept & Tone)** changes — a fundamentally different story.
- **Master Design Section 1.5 / Section 11a (Style Contract world defaults)** changes — different perspective / tense / markers / paragraph register at the world level.
- **`World Mode` flips (arc ↔ sandbox)** — arc world becoming a sandbox, or vice versa.

Today the revise pipeline tells users to run a full rebuild for any of these. The Converter is that full rebuild made coherent: it preserves the structural world-building work (Tier 1 + most of Tier 2) and re-runs everything that depends on the protagonist (Section 3 + Tier 3 + intimacy manifestations + test scenarios).

---

## CONVERT PIPELINE OVERVIEW

```
[User runs /worldforge convert <source> <target>]
      |
      v
 PHASE C0: THE CONVERTER
 Reads source Master_Design.md (read-only). Captures intent (Convert Brief or interview).
 Builds preservation matrix decisions with user. Surfaces role reassignments explicitly.
      |
      |-- [Overlap floor: 3+ axes replaced?] --> REFUSE. Bounce to /worldforge start fresh.
      |-- [Overlap floor: 2 axes replaced?] --> Surface borderline; user confirms.
      |-- [User cancels?] --> Halt with no output.
      v
 New <target>/World_Seed.md written with:
   - Conversion Manifest block at top
   - Preserved Section 2 (Tier 1) content, marked
   - New Section 3 (protagonist)
   - Preserved Section 4 (Tier 2) characters with relationship-to-{{user}} flagged for reauthoring
   - Section 5 left as structured stub for downstream
   - New Section 7b (test scenarios)
   - Preserved or regenerated Section 8 (intimacy) per user decision
   - CONVERTER SIGN-OFF block at bottom
      |
      v
 ✅ CONVERTER COMPLETE. Output the hand-off instruction.
      |
      v
 [User runs /worldforge skip phase0 against <target>]
      |
      v
 Standard pipeline (Phases 1 → 5.5) builds the new world end-to-end.
 The Refiner reads the Conversion Manifest, treats preserved sections as
 confirmed Phase 0 content, and surfaces regeneration stubs as normal gaps.
```

---

## PHASE C0: THE CONVERTER

**Invoke:** `@agent_roles/Converter/00_The_Converter.md`
**Input:**
- `<source_path>/Drafts/Master_Design.md` (required; must have REFINER SIGN-OFF)
- `<source_path>/World_Seed.md` (optional in reframe mode — secondary context; **rebaseline mode: the 1:1 consolidation base, required reading when present**)
- `<source_path>/Export/` directory (required; confirms source shipped)
- `<brief_path>` if `--brief` mode (optional; user-authored against `templates/Convert_Brief_Template.md`)

**Output:**
- `<target_path>/World_Seed.md` — new seed with Conversion Manifest at top, Converter Sign-Off at bottom, formatted against `templates/World_Seed_Template.md`

**Authority:**
- **Read-only on `<source_path>`.** Hard rule. The Converter never modifies any file in the source project.
- **Write-only on `<target_path>/World_Seed.md`.** Does not write `Drafts/`, `Export/`, `Master_Design.md`, or any other file in the target project. The standard pipeline produces those.

**Single phase.** The Converter is one phase, not a multi-phase mini-pipeline. It produces the seed; everything downstream is the regular pipeline. This is unlike `/worldforge revise`, which orchestrates eight mini-phases.

### Operating modes (invocation)

| Mode | Invocation | When to use |
|---|---|---|
| **Interview** | `/worldforge convert <source> <target>` | First-time conversion, complex preservation decisions, user wants creative-partner pushback |
| **Brief-driven** | `/worldforge convert <source> <target> --brief <path>` | User has written a Convert Brief; Converter validates + asks clarifying questions only |
| **Brief + interview** | (automatic; same as brief-driven when the Brief has gaps) | The brief-driven path automatically interviews on missing or ambiguous fields |
| **Rebaseline** | `/worldforge convert <source> <target> --rebaseline` (combines with `--brief`) | Same world, same protagonist — consolidate accumulated revisions into a clean rebuild, optionally folding in new mechanics. See REBASELINE MODE below |
| **Rebaseline (distilled)** | `/worldforge convert <source> <target> --rebaseline --distill` | Same, but the seed is re-derived from the post-revision Master Design instead of carried 1:1 from the source seed — for when the original seed was thin or the world has outgrown its wording. Requires `--rebaseline` |
| **Rebaseline + interview** | `/worldforge convert <source> <target> --rebaseline --then-interview` | Consolidate first, then go straight into the Interviewer (seed-revision posture) to make major changes against the clean seed before Phase 1. Requires `--rebaseline` |
| **Rebaseline + brainstorm + interview** | `/worldforge convert <source> <target> --rebaseline --then-brainstorm` | Consolidate, then brainstorm *what* to change (Brainstormer improvement posture) before the Interviewer reads those notes as proposals and makes the edits. Offers parked ideas from the source's standing `Big_Brain_Storm.md`, if one exists, and carries the curated file forward to the target. For when changes are wanted but undecided. Requires `--rebaseline`; supersedes `--then-interview` |

The Brief is recommended for non-trivial conversions because it is version-controllable and reviewable. The Converter spec (`agent_roles/Converter/00_The_Converter.md` Section 2) explains both modes in detail.

### What the Converter writes (the seed)

The new `World_Seed.md` follows `templates/World_Seed_Template.md` exactly — same section numbering, same required fields, same conventions. The Refiner reads it as if a user wrote it at Phase 0. What is distinctive about a Converter-authored seed:

- **Conversion Manifest at top.** Records source path, intent, overlap floor result, preservation decisions, role reassignments, cross-references the user should be aware of. Block format defined in `agent_roles/Converter/00_The_Converter.md` Section 7.
- **HTML comments marking provenance.** Every preserved section carries a `<!-- CONVERTED FROM ... -->` comment so downstream agents (and human readers) can trace what came from the source.
- **CONVERTER NOTE blocks for regenerated sections.** Section 5 (arcs or Sandbox Charter) and any other always-regenerated section gets an explicit note explaining what the downstream pipeline will fill in. The Refiner surfaces these as Phase 1 gaps in `UNRESOLVED_QUESTIONS.md`.
- **Relationship-to-`{{user}}` flagged everywhere.** Every preserved Tier 2 character's source content carries through *except* relationship-to-`{{user}}` content — that gets a `<!-- RELATIONSHIP TO {{user}} TO BE REAUTHORED FOR NEW PROTAGONIST -->` marker. The Architect handles the reauthoring in Phase 2.
- **CONVERTER SIGN-OFF at bottom.** The structural equivalent of INTERVIEWER SIGN-OFF — confirms the seed is complete enough to proceed to Phase 1.

### The overlap floor (Phase C1 in spec terms, but a check inside Phase C0)

Before doing any authoring, the Converter classifies the conversion intent across four axes — **setting, protagonist, factions, tone** — and counts how many are being **replaced** vs. **kept**.

| Axes replaced | Result |
|---|---|
| 0 or 1 | Well-shaped conversion; proceed |
| 2 | Borderline ("half a new world"); surface to user, proceed only on explicit confirm |
| 3 or 4 | Refuse; this is a fresh build inspired by the source, not a conversion |

The refusal output (Phase C0 Step 2 in the agent spec) explicitly bounces the user to `/worldforge start` with the source as creative reference. **The Converter does not soften this** — a four-axes-replaced "conversion" produces a Frankenstein seed and undermines the pipeline downstream.

---

## ROLE REASSIGNMENT SURFACING

The single most consequential operation in a conversion is **role reassignment**: a character whose role changes between the source and the new build. The Converter handles five canonical cases explicitly:

1. **Old protagonist → NPC or supporting Tier 2 character.** The most common case. Source `{{user}}` content (wound, voice, physical) becomes Tier 2 starting material; the internal monologue and trajectory drop (those were protagonist-shaped). The Converter writes a Tier 2 block in Section 4 using the source's `{{user}}` content, flagged with `<!-- WAS SOURCE PROTAGONIST — TIER 2 BLOCK REAUTHORED FROM PROTAGONIST CONTENT; REFINER WILL VERIFY TIER DISCIPLINE -->`. The Refiner does the final tier-discipline check at Phase 1.

2. **Source NPC → new protagonist.** A character who was Tier 2 in the source becomes `{{user}}` in the new build. Source Tier 2 entries are *starting material* for Section 3 but get reauthored as protagonist-shaped content downstream. The Converter does not copy-paste; it captures the new psychological frame in Section 3 (with the user's input via interview or Brief Section 5), and surfaces the connection in the Conversion Manifest's "Role reassignments" block.

3. **Power tier shift on `{{user}}` (mortal → deity, or vice versa).** Faction relationships, hard rules, intimate dynamics, and the entire stakes register reshape. The Converter walks the user through which downstream content is implicated (typically: every preserved faction needs its relationship-to-`{{user}}` reauthored regardless; intimate dynamics may need re-thinking even if intimacy is preserved at the world level).

4. **A Tier 2 character is dropped.** Cleanest case. Their Tier 2 entries do not transfer. Any source content that referenced them (Tier 1 entries naming them, arc state mentioning them) is *not* written into the new seed; if those Tier 1 entries are otherwise preserved, the Converter strips the reference and marks the location `<!-- REFERENCE TO [dropped character name] REMOVED IN CONVERSION -->`.

5. **Tier 2 character role shift not involving `{{user}}`.** Antagonist becomes ally (because the protagonist changed) — wound, voice, physical carry; behavioral mandates and relationship-to-`{{user}}` get reauthored downstream. Same marker pattern as case 1, but the character stays in Tier 2 throughout.

All reassignments are confirmed with the user before the seed is written. The Converter surfaces them as a list in Step 5 and requires explicit `y/edit/cancel`.

---

## REBASELINE MODE (consolidating a revised world into a clean rebuild)

`/worldforge convert <source> <target> --rebaseline` is the **zero-axes-replaced conversion, formalized**: same protagonist, same World Mode, same tone, same factions. It exists for the world whose accumulated revisions (R1…R[N]) have layered `Master_Design.md` and `Drafts/` with revision markers and left `World_Seed.md` N revisions stale — and whose next change is structural enough (new mechanics, say) that another surgical revision feels wrong. The full mode spec is `agent_roles/Converter/00_The_Converter.md` Section 9; the load-bearing deltas from a regular (reframe) conversion:

- **The always-regenerate rules invert.** Every "regenerate (always)" disposition derives from the protagonist or arc spine changing; in rebaseline neither changes, so Section 3 (protagonist), Section 5 (arcs / Sandbox Charter), Section 7b (test scenarios), per-arc/standing intimate functions, per-card style overrides, and relationship-to-`{{user}}` content all **keep** at their post-revision state. The four Section 4 strip rules (Standing Goal / drift / belief / trauma trajectory) invert to carry.
- **Zero-axes gate instead of the overlap floor.** Replacing any axis reclassifies the run as a regular conversion (announced, not refused). A rebaseline with no applied revisions and no new mechanics is flagged as a no-op copy and proceeds only on explicit confirmation (a seed that drifted from what Phases 1–5 built is one legitimate answer — the divergence scan covers it).
- **Revision reports become required reading.** `Drafts/Revision_R*.md` + `Export/REVISED_FILES.md` are read in full; the revision high-water mark is recorded in the Conversion Manifest; and an integrity check verifies every reported revision is visible in the current Master Design (halt and flag if not — a drifted source would silently lose a revision). The source `World_Seed.md` joins the required-reading list when it exists.
- **Seed-anchored, 1:1** (Converter Section 9 Step D). The source `World_Seed.md` carries **verbatim** as the consolidation base — sections no revision touched keep the user's original wording, never paraphrased or re-summarized. Each applied revision is then written into the affected seed passage in place (replace-not-stack, at seed grade), and a **divergence scan** surfaces post-seed content that no revision explains (Phase 1+ elicitations, developed arcs) for ask-first fold-in — nothing folds in or drops silently. The structure upgrades to the current `World_Seed_Template.md` without re-wording carried content. Distillation from the post-revision Master Design runs only on the explicit **`--distill`** flag (a deliberate opt-out — the original seed was thin, or the world has outgrown its wording) or as the announced fallback when the source has no `World_Seed.md` (confirming that announcement counts as passing the flag). The route is recorded in the manifest's `Seed base:` line.
- **Distill only on the distillation path — and never dump.** Master Design content is design-grade; a distillation targets seed grade. In every mode, no entry-level (`CHARACTER_STATE`/`NPC_SHIFT`) content in the seed.
- **Clean means marker-free.** Revision *content* carries; `<!-- REVISED IN R[N] -->` markers do not. Passages carried 1:1 stay unmarked; change sites (revision deltas, confirmed fold-ins, structure upgrades) get `<!-- REBASELINED FROM ... -->` comments, inventoried in the manifest. The new project's revision counter restarts at R1.
- **New mechanics enter at seed level**, marked `<!-- NEW IN REBASELINE -->`, with couplings surfaced under the no-silent-expansion rule. As part of the same intake (Converter Section 9 Step F), the Converter checks the source project for a standing **`Big_Brain_Storm.md`** (parked ideas from `brainstorm --improve` sessions) — it never reads the file itself, but surfaces its existence and routes: fold the ideas via the `--then-brainstorm` chain (upgrading the run if the flag wasn't passed), state an idea directly as new mechanics, or leave the file parked in the source. The disposition is recorded in the manifest.
- **The honest cost: chat states.** The rebuild compiles fresh UIDs — running SillyTavern chats against the source do **not** migrate. Revise preserves UIDs precisely to avoid this; rebaseline trades it for cleanliness. The Converter states this at hand-off and records the acknowledgment in the manifest. The source package stays playable as-is.

- **`--then-interview` chains consolidation into redesign.** With the flag, the C0 hand-off dispatches **Phase 0 — the Interviewer in seed-revision posture** (`agent_roles/00_The_Interviewer.md` Section 9) against the consolidated seed instead of `skip phase0`. The Interviewer plays the world back, interviews only the user's changes at full Phase 0 depth (cascading through coupled fields — changed arcs drag drift/trauma/intimacy lines, a changed protagonist drags relationship-to-`{{user}}` content), marks changed sections `<!-- CHANGED IN SEED-REVISION INTERVIEW -->`, appends a dated note to the Conversion Manifest, signs off, and hands to Phase 1. Use it when the rebaseline is a staging step for something bigger. Without the flag, you can still get the same flow later by dispatching the Interviewer in seed-revision posture against the target before running `skip phase0`. The flag requires `--rebaseline` — in reframe mode the C0 interview already authors the new material.
- **`--then-brainstorm` adds an ideation step ahead of the interview.** Same chain, with the **Brainstormer in improvement posture** (`agent_roles/Brainstormer/00_The_Brainstormer.md` Section 8) inserted first — for when the user wants to change the consolidated world but hasn't settled on *what*. The Brainstormer reads the clean seed + Conversion Manifest, diverges on improvement directions (a new mechanic, an arc rework, a deeper character, a tonal turn), and writes informal `Brainstorm_Notes.md` — it never edits the seed. If the source project carries a standing `Big_Brain_Storm.md` (parked ideas from earlier `brainstorm --improve` sessions), the Brainstormer asks whether to fold those ideas in (its Section 8 step 1a — never silently); endorsed ideas land in the notes with attribution, and the curated standing file is carried forward to the target project so the parked pool follows the world — the source copy is never modified. The chain then continues into the Interviewer in seed-revision posture exactly as `--then-interview` does; the Interviewer reads the notes as *proposals*, leads with them, and interviews the endorsed ones at full depth. The Brainstormer respects the world's spine: an idea that would flip World Mode, swap the protagonist, or overturn the core concept is flagged as reframe-conversion territory, not a rebaseline improvement. The flag requires `--rebaseline` and **supersedes `--then-interview`** (the interview always follows the brainstorm). (The same improvement posture is also available *standalone*, outside any conversion, as `/worldforge brainstorm --improve` — no-commitment idea ping-pong against an existing world, nothing dispatched afterward; see the BRAINSTORM section of `workflows/world-forge-discovery.md`.)

**Choosing between revise and rebaseline:** if the change is surgical and you want running chats to survive, revise. If the world needs consolidation, the seed is badly stale, or the next change is structural — rebaseline, and accept the fresh start. If you know changes are coming right after the consolidation, add `--then-interview`. Flipping protagonist / World Mode / tone on the way out is regular convert, not rebaseline.

---

## HAND-OFF TO THE STANDARD PIPELINE

After the Converter writes the seed and outputs its sign-off message, the user runs:

```
/worldforge skip phase0
```

…against the target project folder. (Exception: a `--rebaseline --then-interview` run inserts Phase 0 first — the Interviewer in seed-revision posture captures the user's post-consolidation changes, signs off, and *then* the flow below proceeds from Phase 1 unchanged. A `--rebaseline --then-brainstorm` run inserts the Brainstormer (improvement posture) ahead of that Interviewer — it writes `Brainstorm_Notes.md`, which the Interviewer then reads as proposals — before the same Phase 1 hand-off.) From the standard pipeline's perspective (`workflows/world-forge.md`), this is the normal `skip phase0` flow — the user wrote a `World_Seed.md` and wants Phase 1 to pick it up. The Refiner reads the Conversion Manifest at the top and routes accordingly:

- **Preserved sections** (marked with `<!-- CONVERTED FROM ... -->` comments): the Refiner treats these as confirmed Phase 0 content. No gap surfaced.
- **Reauthored content markers** (relationship-to-`{{user}}`, role-shift Tier 2 blocks): the Refiner notes them. The Architect handles the reauthoring at Phase 2.
- **Regeneration stubs** (Section 5 arcs / Sandbox Charter, often Section 8 per-arc functions): the Refiner surfaces these as gaps in `UNRESOLVED_QUESTIONS.md` exactly as it would for any thin Phase 0 section. The user answers the gaps; `/worldforge resume phase1` proceeds.

From Phase 2 onward, the conversion is invisible to the rest of the pipeline. The Architect builds drafts from the Master Design; the Editor validates them; the auditors run; the Compiler produces Export/; the Prompt Engineer authors the preset. No agent downstream needs special handling for a converted world — the new seed and Master Design are first-class Phase 0/1 outputs.

**This is by design.** Convert is upstream of the standard pipeline, not parallel to it. There is no "Convert mode" the downstream agents need to know about; they read the seed and Master Design exactly as they would for a hand-written world.

---

## HUMAN PAUSE GATES (convert pipeline)

| Gate | Trigger | Action |
|---|---|---|
| **C0 Precondition Fail** | Source missing REFINER SIGN-OFF, source Export/ missing, or target World_Seed.md already exists | Converter halts and reports the gap. User fixes the input (e.g., confirms source has shipped) or moves/renames the target seed. |
| **C0 Overlap Refusal** | Phase C0 Step 2 classifies 3 or 4 axes as Replaced | Converter refuses; user runs `/worldforge start` against the target instead, using the source as creative reference. |
| **C0 Borderline Confirm** | Phase C0 Step 2 classifies exactly 2 axes as Replaced | Converter surfaces the borderline; user confirms convert anyway or cancels and runs fresh. |
| **C0 Brief Validation** | `--brief` mode and the brief's preservation decisions don't match the source (e.g., names a faction that doesn't exist) | Converter halts and flags the discrepancy. User edits the brief and re-invokes. |
| **C0 Role Reassignment Confirm** | Before writing the seed | Converter echoes role reassignments; user confirms `y/edit/cancel`. |
| **C0 Target Overwrite** | `<target_path>/World_Seed.md` already exists | Converter halts and asks for explicit confirmation. Never overwrites silently. |
| **C0 Rebaseline Reclassify** | `--rebaseline` and any axis classifies as Replaced | Converter announces the reclassification to a regular (reframe) conversion; user confirms reframe or narrows back to rebaseline. |
| **C0 Rebaseline No-Op** | `--rebaseline`, source has no applied revisions, and no new mechanics named | Converter flags the no-op copy; proceeds only on explicit confirmation. |
| **C0 Rebaseline Source Integrity** | A `Revision_R*.md` report records a change not visible in the current Master Design | Converter halts and flags; user reconciles the source (usually re-running that revision's R1 merge) and re-invokes. |
| **C0 Rebaseline No Source Seed** | `--rebaseline` without `--distill` and `<source_path>/World_Seed.md` does not exist | Converter announces that only the distillation path is available (the seed will be distilled from the post-revision Master Design instead of carried 1:1); user confirms or cancels. **Confirmation counts as passing `--distill`.** Recorded in the manifest's `Seed base:` line. (With `--distill` passed, this gate never fires — the flag is the consent; the Converter announces the re-wording cost once and proceeds.) |
| **C0 Rebaseline Divergence Fold-In** | The Step D divergence scan finds seed-grade content in the Master Design that no revision explains | Converter surfaces each finding; user decides fold-in vs. leave-for-rebuild per item. No silent fold-ins, no silent drops; dispositions recorded in the manifest. |

After Phase C0 completes, all subsequent pause gates are the standard pipeline's (Phase 1 blocker → `UNRESOLVED_QUESTIONS.md`, etc.).

---

## FILE STRUCTURE (convert pipeline)

The Converter writes a single file. After Phase C0:

```
<source_path>/                              ← never modified
└── (unchanged)

<target_path>/                              ← new project folder
└── World_Seed.md                           ⭐ written by Converter (Phase C0)
    │   ├── ## Conversion Manifest (top)
    │   ├── ## 1. CORE CONCEPT & TONE
    │   ├── ## 1.5. STYLE CONTRACT
    │   ├── ## 2. THE WORLD
    │   ├── ## 3. THE PROTAGONIST
    │   ├── ## 4. CHARACTERS
    │   ├── ## 5. NARRATIVE ARCS or SANDBOX CHARTER (stub)
    │   ├── ## 6. TECHNICAL SPECIFICATIONS
    │   ├── ## 7. TEST SCENARIOS (Section 7b)
    │   ├── ## 8. INTIMACY (conditional)
    │   └── ## ✅ CONVERTER SIGN-OFF (bottom)
```

After the user runs `/worldforge skip phase0` against the target, the standard pipeline takes over and the target folder evolves through the normal structure (`Drafts/`, `Export/`, etc.) documented in `workflows/world-forge.md`.

---

## TRIGGER COMMANDS

| Command | Action |
|---|---|
| `/worldforge convert <source> <target>` | Begin from C0 in interview mode |
| `/worldforge convert <source> <target> --brief <path>` | Begin from C0 in brief-driven mode (the Convert Brief is validated against the source; the Converter interviews on gaps and ambiguities) |
| `/worldforge convert <source> <target> --rebaseline` | Begin from C0 in **Rebaseline mode** — same world, same protagonist; consolidate accumulated revisions into a clean rebuild. Combines with `--brief` (the Brief must declare `Operating mode: rebaseline`) |
| `/worldforge convert <source> <target> --rebaseline --distill` | Rebaseline with **distilled consolidation** — re-derive the seed from the post-revision Master Design instead of carrying the source seed 1:1. Requires `--rebaseline`; combines with `--brief` and the `--then-*` flags |
| `/worldforge convert <source> <target> --rebaseline --then-interview` | Rebaseline, then hand off into **Phase 0 (Interviewer, seed-revision posture)** to make major changes against the consolidated seed before Phase 1. Requires `--rebaseline` |
| `/worldforge convert <source> <target> --rebaseline --then-brainstorm` | Rebaseline, then hand off into the **Brainstormer (improvement posture)** to brainstorm *what* to change, then the Interviewer (seed-revision posture) reads those notes as proposals. Requires `--rebaseline`; supersedes `--then-interview` |

After Converter completes, switch to the standard pipeline's commands against the target folder (`/worldforge skip phase0`, `/worldforge resume phase1`, etc.).

---

## RELATIONSHIP TO OTHER PIPELINE OPERATIONS

| Operation | What it does | Source artifact | Output artifact | Touches downstream pipeline? |
|---|---|---|---|---|
| `/worldforge start` | Build a new world from scratch | none | full project | yes — runs Phases 0–5.5 |
| `/worldforge start --sandbox` | Same, but pre-sets `World Mode: sandbox` in the seed | none | full project | yes |
| `/worldforge skip phase0` | Resume from Phase 1 against an existing World_Seed.md | World_Seed.md | full project | yes — runs Phases 1–5.5 |
| `/worldforge revise` | Surgical edit to a shipped world | shipped project | modified files in same project | partial — mini-pipeline runs |
| `/worldforge resync-preset` | Refresh a shipped world's Chat Completion Preset | shipped project | one updated JSON in same project | preset only |
| `/worldforge convert <source> <target>` | **Reframe a shipped world into a new build** | **shipped project (read-only)** | **new World_Seed.md in target project** | **upstream — produces seed, then hands off to `skip phase0`** |
| `/worldforge convert <source> <target> --rebaseline` | **Consolidate a revised world into a clean rebuild** (same protagonist; source seed carried 1:1 with revisions applied in place, markers dropped; fresh UIDs — running chats do not migrate) | **shipped project (read-only)** | **new World_Seed.md in target project** | **upstream — produces seed, then hands off to `skip phase0`** |

The Converter is positioned **upstream** of the standard pipeline. It does not replace any phase; it produces the input to Phase 1.
