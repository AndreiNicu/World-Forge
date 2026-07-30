---
description: World Forge build Stage 1 — Discovery & Planning (Brainstorm pre-phase, Phase 0 Interviewer, Phase 1 Refiner). Dispatched by workflows/world-forge.md.
---

# WORLD FORGE — STAGE 1: DISCOVERY & PLANNING
*Stage file 1 of 4 — dispatched by the router (`workflows/world-forge.md`). Not a standalone entry point.*

**Phases:** Brainstorm (optional, upstream) · Phase 0 (the Interviewer) · Phase 1 (the Refiner)

**Entry conditions:** a fresh run (`/worldforge start`, `/worldforge start --sandbox`, `/worldforge brainstorm`), a seed-first run (`/worldforge skip phase0` — begin directly at Phase 1 against an existing `World_Seed.md`), or a resume (`resume phase0` / `resume phase1` — re-enter per the Pipeline State Ledger and the checkpoint discipline's resume-from-disk rule).

**Exit conditions (verify on disk before handing back):** `Drafts/Master_Design.md` exists, is non-empty, contains `REFINER SIGN-OFF`, and carries an initialized Pipeline State Ledger with the `1 Refiner` row `COMPLETE`. Then hand back to the router → Stage 2 (`workflows/world-forge-drafting.md`). If Phase 1 produced `UNRESOLVED_QUESTIONS.md` instead, the ledger is `BLOCKED` and the run pauses for the user.

**Governing router sections (not restated here):** PIPELINE STATE LEDGER, CHECKPOINT DISCIPLINE, DISPATCH PROTOCOL — all in `workflows/world-forge.md`. Every phase below runs by dispatching its agent; never inline.

---

## BRAINSTORM (optional ideation, upstream of Phase 0)

Some users arrive with a fully-formed concept; the Interviewer is built for them. Others arrive with only a vibe — an image, a mood, a single character, a "what if" — and nothing solid enough for the Interviewer's structured, specificity-demanding questions to land. `/worldforge brainstorm` is the optional front porch for that state.

It invokes the **Brainstormer** (`agent_roles/Brainstormer/00_The_Brainstormer.md`) as a single standalone step (Phase 0-pre). Where the Interviewer is **convergent** (walks the template, pushes for depth, refuses weak material), the Brainstormer is **divergent**: it generates multiple premise directions, yes-ands the user's instincts, follows the spark, and helps an idea find its shape. When a premise has a pulse — a central tension, a feel, and at least one anchor the user is excited about — it reflects that back and hands off.

**Load-bearing properties:**
- **Writes only its notes files.** Informal, unstructured ideation notes in the project folder — explicitly *not* a World Seed. The Brainstormer never authors or edits `World_Seed.md`, never writes `Drafts/` or `Export/`, and never touches structural pipeline material. Seed authorship belongs to the Interviewer alone. Its run-scoped output is `Brainstorm_Notes.md`: **exactly one per project, written fresh every run** — each invocation overwrites any prior `Brainstorm_Notes.md` in full and stamps it with its `Posture:` (fresh-start | improvement | revision-diagnostic | adaptation) + date, so a stale file from an earlier run never has to be deleted by hand and consumers can confirm which run produced it. The one exception is the standalone improvement door (`brainstorm --improve`), which instead writes the standing **`Big_Brain_Storm.md`** — a living idea file rewritten fresh each standalone session with still-open ideas carried forward; no agent consumes it silently (`revise --brainstorm` and the rebaseline `--then-brainstorm` chain *offer* to adapt from it; a plain `--rebaseline` surfaces its existence and routes), and it leaves `Brainstorm_Notes.md` untouched.
- **Upstream of the pipeline, not a phase of it.** It does not classify tiers, advance the Pipeline State Ledger, or invoke any downstream agent. It is a standalone optional entry point, like a pre-`start`.
- **Hands off to `/worldforge start`.** The Interviewer reads `Brainstorm_Notes.md` if present (its Context Manifest lists it under "Load if present") as raw starting material, then runs the full interview — pushing for exactly the specificity the Brainstormer deliberately left open, and confirming (not inheriting) the notes' non-binding World Mode leaning.
- **Optional and skippable.** A user with a developed concept skips brainstorm entirely and goes straight to `/worldforge start` or `/worldforge skip phase0`. Nothing downstream depends on a brainstorm having happened.
- **Four postures.** The default (Brainstormer Sections 1–7) is the fresh start above. The **improvement posture** (Section 8) brainstorms *changes to an existing world* — it reads the world's current state and diverges on what to add, rework, or deepen, respecting the world's spine (an idea that flips World Mode, swaps the protagonist, or overturns the core concept is named as convert territory). It has two doors. **Chained:** `/worldforge convert --rebaseline --then-brainstorm` — after a rebaseline consolidates a revised world, the Brainstormer reads the consolidated `World_Seed.md`, explores improvements — offering parked ideas from the source's standing `Big_Brain_Storm.md` if one exists (ask-first), and carrying the curated file forward to the target when brought in — writes `Brainstorm_Notes.md`, and the chain continues into the Interviewer in seed-revision posture (which reads those notes as proposals). **Standalone:** `/worldforge brainstorm --improve` — no-commitment idea ping-pong against any existing world (reads `Drafts/Master_Design.md` read-only when the world is built, `World_Seed.md` otherwise), recorded in the standing **`Big_Brain_Storm.md`** rather than `Brainstorm_Notes.md`; nothing is dispatched afterward — a later `revise --brainstorm` or rebaseline `--then-brainstorm` chain offers to adapt a parked idea from the file, or the user takes a landed change through its normal door (`/worldforge revise`, seed edits before `skip phase0`, or `/worldforge convert`), or the ideas just stay parked. A bare `/worldforge brainstorm` invoked against a project that already contains a world is usually a mistake for `--improve` — confirm intent before running the fresh-start posture there. The **revision-diagnostic posture** (Section 9) serves the post-launch *pre-articulation* case — something feels off in a shipped world but the user can't name what to revise. Invoked by `/worldforge revise --brainstorm`, it reads `Drafts/Master_Design.md` read-only, diagnoses divergently (the domain lenses as diagnostic vocabulary), and writes a primary concern to `Brainstorm_Notes.md` that the Reviser then classifies. The **adaptation posture** (Section 10) serves the user who arrives with an *existing narrative document* — a story, a fanfiction, a roleplay log — rather than a blank-page vibe. Invoked by `/worldforge brainstorm --adapt <document_path>`, it reads the document read-only, extracts the world latent in it (cast, setting, tone, the prose style as a Style Contract sample, and any intimate register the source shows for Phase 2.5), and diverges on the gap between a story-to-read and a world-to-play-in — above all the `{{user}}` slot the document's fixed POV can't supply, which it recommends from the document's POV and confirms — then writes an `adaptation`-stamped `Brainstorm_Notes.md` the Interviewer reads exactly like a `fresh-start` file. See the POST-LAUNCH OPERATIONS pointers in `workflows/world-forge.md`, `workflows/world-forge-convert.md`, and `workflows/world-forge-revise.md`.

---

## PHASE 0: DISCOVERY — THE INTERVIEWER

**Invoke:** `@agent_roles/00_The_Interviewer.md`
**Input:** User intent to build a new world
**Output:** `World_Seed.md` ready for Phase 1

The Interviewer walks the user through the World Seed Template interactively. Asks the right questions in the right order. Pushes back on thin or inconsistent answers. Will not let the document be weak.

The Interviewer asks about:
1. Core concept and tone — logline, emotional payoff, tonal hard rules
2. **Style Contract (Section 1.5)** — perspective, tense, narration marker, dialogue marker, emphasis marker, paragraph register, plus per-card overrides for cards structurally incompatible with the world default (typically Director/Narrator cards). Defaults pathway short-circuits the section for users who want pipeline-legacy prose conventions.
3. The world — sensory signature, rules with costs, factions, locations, species, concepts
4. The protagonist ({{user}}) — wound, hidden layer, contradiction, power and limits, arc trajectory, physical, voice, **and the Posture Toward {{user}} block** (declared posture `adversarial` / `indifferent` / `mixed` / `deferential` / `predatory`, a force that does not defer, concrete losable things with their harm class, the permitted shapes of a lost scene and the boundary in whichever direction the world needs it, plus the manipulation vectors and tell rule wherever the cast works *through* {{user}}). Required in every world, power fantasies included — an unstated posture is not a neutral world, it is the model's trained deference filling the gap. Note that **compliance and intent are different questions**: `deferential` and `predatory` both yield to {{user}} constantly and are opposite worlds
5. Characters — central wound, shield, crack, voice with sample lines, physical in anatomical order, relationships, NPCs with sample lines, plus the per-card style override declaration (only for cards flagged in Section 1.5)
6. Arcs — hidden information rules, dramatic beats, NPC shifts, entry and exit triggers, tone and pacing
7. Technical specifications — cards, lorebooks, depth_prompt assessment per character
8. Test scenarios (Section 7b) — three to five specific roleplay moments the user intends to play through
9. **Intimacy & Sexuality (Section 8)** — world-level posture toward sex, per-character intimacy substrate, per-arc thematic functions and scene types, tonal hard rules for intimate content. Conditional on the world containing intimate scenes.
10. **Runtime Directives (Section 9)** — optional engine-steering asks about how the model must behave turn-by-turn (e.g., "combat must feel slow and costly"), each with a wrong-response example and a scope. The Prompt Engineer must address every one in the Chat Completion Preset. Most worlds leave this empty; misplaced answers (world facts, single-character behavior, style) are routed to their proper sections instead.

If the user resists developing a section, the Interviewer adds an explicit note in the document marking it for Refiner review rather than silently filling gaps.

**This phase exists because the World Seed is hardest to write well the first time.** A weak World Seed propagates through every subsequent phase. Five minutes of pushback at this stage saves an hour of debugging at the runtime stage.

**Optional upstream step.** Users who arrive with only a vibe — no premise solid enough to interview against — can run `/worldforge brainstorm` first (see BRAINSTORM above). It is a divergent ideation partner that produces informal `Brainstorm_Notes.md`, which the Interviewer then reads as starting material. The Interviewer still runs the full interview; the notes are a warm start, not a substitute.

**Artifact gate (Phase 0):** `World_Seed.md` exists, is non-empty, and ends with the `INTERVIEWER SIGN-OFF` block before Phase 1 is dispatched.

---

## PHASE 1: PLANNING — THE REFINER

**Invoke:** `@agent_roles/01_The_Refiner.md`
**Input:** `World_Seed.md` (+ `UNRESOLVED_QUESTIONS.md` if resuming)
**Output:** `Drafts/Master_Design.md`

1. Classifies all World Seed content into Tier 1 / Tier 2 / Tier 3 material.
2. Identifies gaps in each tier and flags questions requiring user input.
3. **No blockers:** produces `Master_Design.md` with REFINER SIGN-OFF → Phase 2.
4. **Blockers found:** produces `UNRESOLVED_QUESTIONS.md` → **PAUSE.** Await user answers.

A complete Master Design contains: world laws/factions/locations/species/concepts (Tier 1), character foundations + physical descriptions in anatomical order + protagonist spec (Tier 2), all arcs with hidden information rules + dramatic beats (Tier 3), LLM behavioral requirements per card including depth_prompt assessment, intimacy specifications routed from Section 8 to the appropriate tier source for the Intimacy Architect, the `Posture Toward {{user}}` block in Section 6 (routed to **Tier 3**, not Tier 2 — it is world-and-cast property and the Editor hard-fails it in the protagonist lorebook), and runtime directives from World Seed Section 9 recorded in Section 12 (validated, rerouted where misplaced, or `No runtime directives declared.`) for the Prompt Engineer.

**Artifact gate (Phase 1):** `Drafts/Master_Design.md` exists, is non-empty, contains `REFINER SIGN-OFF`, and carries the initialized Pipeline State Ledger (router → PIPELINE STATE LEDGER). Only then is the `1 Refiner` row `COMPLETE`.

---

## STAGE EXIT

1. Verify the Phase 0 and Phase 1 artifact gates above (read the files — conversation memory does not count).
2. If a Python runtime is available: `python tools/validate_pipeline_state.py <project folder>` (read-only). Resolve any reported mismatch before proceeding.
3. Hand back to the router → dispatch Stage 2 (`workflows/world-forge-drafting.md`).
