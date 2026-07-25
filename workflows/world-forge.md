---
description: A workflow to build worlds for player to roleplay in.
---

# THE WORLD FORGE PIPELINE
*Orchestrator v7 — Universal Roleplay World Building & SillyTavern Export*

**Produces:** Character Cards + World Lorebook (Tier 1, permanent) + Character & NPC Lorebooks (Tier 2, permanent) + Character/NPC Intimacy Profiles (Tier 2, permanent, where applicable) + Tier 3 lorebook (arc mode: Arc Lorebooks, one active at a time; sandbox mode: a single always-active Sandbox Lorebook) + Intimacy Registers (Tier 3: per-arc in arc mode, a single standing register in sandbox mode, where applicable) + Chat Completion Preset. Works for any world — arc or sandbox, any number of arcs, characters, or NPCs.

---

## PIPELINE OVERVIEW

```
[User intent — start a new world]
      |
      v
 PHASE 0: THE INTERVIEWER
 Walks user through the World Seed Template interactively, including the Section 8
 Intimacy specification when relevant. Pushes back on weak material. Captures test scenarios.
      |
      v
 World_Seed.md
      |
      v
 PHASE 1: THE REFINER
 Classifies World Seed into Tiers 1/2/3. Identifies gaps. Builds Master Design.
      |
      |-- [Gaps?] --> UNRESOLVED_QUESTIONS.md → ⏸ PAUSE → /worldforge resume phase1
      v
 Master_Design.md [LOCKED]
      |
      v
 PHASE 2: THE ARCHITECT
 Authors all draft content: Character Cards, Protagonist Lorebook,
 Tier 1/2/3 entry files, LLM Instruction drafts.
      |
      v
 PHASE 2.5: THE INTIMACY ARCHITECT (conditional — runs if Section 8 has material)
 Authors Tier 2 Intimacy Profiles (permanent substrate per character) and
 Tier 3 Intimacy Registers (arc-specific delta). Cross-references existing drafts.
      |
      |-- [Section 8 missing material?] → UNRESOLVED_INTIMACY.md → ⏸ PAUSE → /worldforge resume phase2.5
      v
 PHASE 3: THE EDITOR (ITERATIVE LOOP)
 Validates prose + tier integrity + lorebook quality + LLM instructions + intimacy entries.
      |
      |-- [Missing/failed?] → Return to Architect or Intimacy Architect
      |-- [3+ rounds, no improvement?] → ⏸ PAUSE → escalate to user
      v (Editor Sign-Off)
      |
      v
 PHASE 3.5 + 3.6 + 3.7 (parallel)
 ─ 3.5 VOICE AUDITOR — behavioral fidelity in regular dialogue
 ─ 3.6 ARC TRANSITION AUDITOR — continuity across arc seams
 ─ 3.7 INTIMACY AUDITOR — voice fidelity + thematic register in intimate scenes (conditional)
      |
      |-- [Failures from any auditor?] → Return to relevant Architect → re-Editor → re-audit
      v (All three sign-offs received)
      |
      v
 PHASE 4: THE COMPILER
 Translates Markdown → SillyTavern JSON. Reads Notes_On_functionality.md first.
      |
      |-- [Templates missing?] → ⏸ PAUSE → /worldforge resume phase4
      v
 Export/ [JSON package]
      |
      v
 PHASE 5: THE PROMPT ENGINEER
 Audits runtime correctness (read-only on Export/) + authors Chat Completion Preset JSON.
 Recommends corrections for any conflicts found — manual user application required.
      |
      |-- [Recommendations in Sections 7/8?] --> PHASE 5.5: MANUAL APPLY
      v
 ✅ PIPELINE COMPLETE
```

---

## WORLD MODE: ARC vs. SANDBOX

Every world is built in one of two modes, declared in World Seed Section 1 (`World Mode: arc | sandbox`) and recorded by the Refiner at the top of `Master_Design.md`. **`arc` is the default and the legacy behavior** — every existing world is an arc world, and arc-world behavior is unchanged. **`sandbox`** is for open-ended worlds with no narrative arc: power-fantasy, world-director, and life-sim worlds anchored by a standing world-state rather than a progression of arcs.

Sandbox mode is a **branch through this same pipeline, not a separate fork.** The same phases and agents run; sandbox mode changes only the Tier 3 spine and the large-cast NPC format. `/worldforge start --sandbox` pre-sets the World Seed field; the field itself is the source of truth, so a hand-written seed or a `skip phase0` run carries the signal.

**What sandbox mode changes, phase by phase:**

| Phase | Arc mode | Sandbox mode |
|---|---|---|
| 0 Interviewer | Section 5 walks the arcs | Section 5 becomes the **Sandbox Charter** (standing situation, tonal mandate + aliveness contract, world pulse, live scene types, NPC roster split) |
| 1 Refiner | Master Design §9 = Narrative Arc Structure | Master Design §9 = **Sandbox Charter (9B)**; NPCs classified principal vs. roster |
| 2 Architect | One Arc Lorebook per arc (§8); full NPC profiles (§7.D) | One always-active **Sandbox Lorebook** `Tier3_Sandbox_Entries.md` (§8S: `SANDBOX_STATE` + `WORLD_PULSE`); principals §7.D + roster §7.E |
| 3 Editor | ARC_STATE validation, ≥8 entries/arc, cross-arc qualifiers | **SANDBOX_STATE validation (Step 4a-S)**; no 8-entry floor; no cross-arc qualifiers; roster fingerprint check |
| 3.5 Voice Auditor | Arc register checks | Standing register vs. SANDBOX_STATE + **Distinctiveness Matrix (Step 3I)** across the roster |
| 3.6 Arc Transition Auditor | Runs | **Skipped** (no arc seams) |
| 2.5 Intimacy Architect | Per-character profiles + per-arc registers; **`{{user}}` intimate embodiment (§6.6)**; stock-register prohibitions in the hard rules (§6.7) | Profiles **+ NPC intimacy** (principal full / roster compact §6.5); a single standing `Sandbox_Intimacy_Register` (no per-arc) |
| 3.7 Intimacy Auditor | Conditional on Section 8 | Conditional on Section 8; audits the standing `INTIMACY_FUNCTION` + **NPC intimate coverage & distinctiveness** (Step 3H) across the sexual NPC cast |
| 4 Compiler | One `[WorldName]_Arc[N]_Lorebook.json` per arc | One `[WorldName]_Sandbox_Lorebook.json` (always active; SANDBOX_STATE constant + ignoreBudget, WORLD_PULSE at position 4) |
| 5 Prompt Engineer | Arc Guardian / Deep Think name the arcs | Blocks reference the standing sandbox state rather than arcs; defaults to **Multi-Character Dynamics** + the optional **NPC Ensemble & Enrichment** block (NPC-to-NPC dialogue, ensemble prose scaling, organic NPC enrichment) + **high-weighted Sensory Embodiment** |

**The aliveness contract** is the load-bearing idea of sandbox mode: with no arc carrying tone and momentum, the `SANDBOX_STATE` Tonal Mandate and the `WORLD_PULSE` entry are what keep the world feeling alive — NPCs pursuing their own agendas and initiating, the world reacting to and remembering `{{user}}`, the cast rotating in and out rather than sitting inert until summoned. It is made concrete by per-NPC **Standing Goals** (Architect §7.D): each principal carries an active objective, and the directive has an NPC advance its goal when a scene lulls. A subplot-shaped goal can optionally be staged as an **Escalation Ladder** (§7.D): 2–4 ordered stages with in-fiction advance conditions, an endpoint, and a stated collision with `{{user}}` — the directive then names the current stage and binds the progression discipline (advance only on stated condition, never skip, never self-resolve), so the model *executes* an authored subplot rather than inventing one. The Voice Auditor's **Step 3J** tests that NPCs actually take that initiative (and that laddered NPCs hold their current stage). The **roster NPC format** (§7.E) with its uniqueness rule, plus the Voice Auditor's **Distinctiveness Matrix**, are what keep a large cast from collapsing into one generic voice. The same NPC-agency mechanic runs in **arc mode** through the ARC_STATE activity-cadence directive — NPCs exist in both modes, so the goal/cadence pair is mode-agnostic.

> **Revise pipeline:** `workflows/world-forge-revise.md` **is sandbox-aware.** Surgical edits to a shipped sandbox world — `SANDBOX_STATE` / aliveness recalibration, `WORLD_PULSE` and location tweaks, adding or recalibrating roster NPCs, sandbox intimacy — run through the same minis via the `sandbox_*` scope types and the mode-aware NPC/intimacy scopes (the Arc Transition Auditor never fires). *Flipping* a world between arc and sandbox is a Section 1 `World Mode` change and still bounces to a full rebuild (`skip phase0`); an automated arc→sandbox converter remains deferred.

---

## PIPELINE STATE LEDGER

Loop state — which phase is live, what round it is on, which sign-offs are in — must survive a context summary or a session restart, not live only in the runtime agent's memory. The **Pipeline State Ledger** is a machine-managed block the Refiner writes at the top of `Master_Design.md` (directly under the `World Mode` line, alongside the Revision Log) and that the orchestrator updates at every phase boundary and loop return. It is the single on-disk source of truth for `/worldforge status` and for every `round > N → escalate` gate. The sign-off blocks remain the detailed certification record; the ledger is the index over them.

**Schema** (the Refiner initializes it; the orchestrator advances it):

```
<!-- PIPELINE STATE LEDGER — machine-managed. Do not hand-edit mid-run. -->
## 🔧 PIPELINE STATE LEDGER
- world_mode: arc            # validated ∈ {arc, sandbox} by the Refiner; never silently defaulted on a typo
- intimacy_in_scope: true    # World Seed Section 8 has material → Phases 2.5 / 3.7 run
- current_phase: 3.5
- status: IN_PROGRESS         # IN_PROGRESS | PAUSED | BLOCKED | COMPLETE

| Phase | Status | Round | Sign-off anchor |
|---|---|---|---|
| 1 Refiner            | COMPLETE | —  | REFINER SIGN-OFF |
| 2 Architect          | PENDING  | —  | PRE-SUBMISSION CHECKLIST |
| 2.5 Intimacy Arch.   | PENDING  | —  | (SKIPPED when intimacy_in_scope: false) |
| 3 Editor             | PENDING  | 0  | EDITOR SIGN-OFF |
| 3.5 Voice Auditor    | PENDING  | 0  | VOICE AUDITOR SIGN-OFF |
| 3.6 Arc Transition   | PENDING  | 0  | ARC TRANSITION AUDITOR SIGN-OFF (SKIPPED in sandbox mode) |
| 3.7 Intimacy Auditor | PENDING  | 0  | INTIMACY AUDITOR SIGN-OFF (SKIPPED when intimacy_in_scope: false) |
| 4 Compiler           | PENDING  | —  | COMPILER SIGN-OFF |
| 5 Prompt Engineer    | PENDING  | —  | PROMPT ENGINEER SIGN-OFF |
```

**Per-phase status values:** `PENDING` (not started), `IN_PROGRESS` (running or mid-loop), `COMPLETE` (signed off), `SKIPPED` (conditional phase that did not run — record why in the anchor cell), `BLOCKED` (a pause/blocker file was generated), `ESCALATED` (round ceiling hit — awaiting user).

**Contract:**
- **The Refiner initializes the ledger** at Phase 1 sign-off: `world_mode` validated, `intimacy_in_scope` set from World Seed Section 8, the `1 Refiner` row `COMPLETE`, every later row `PENDING`, loop-phase `Round` at `0`, and the conditional rows pre-marked `SKIPPED` where they will not run (3.6 in sandbox mode; 2.5 and 3.7 when intimacy is out of scope).
- **The orchestrator advances the ledger** — on entering a phase it sets that row `IN_PROGRESS` and updates top-level `current_phase`; on a sign-off it sets the row `COMPLETE`; on a loop return it increments that phase's `Round`; on a pause it sets `BLOCKED`; on a round-ceiling escalation it sets `ESCALATED`. These are file writes, not memory.
- **`round > N` gates read the ledger**, not the conversation. The ceiling is `3` for every loop phase (Editor 3, and auditors 3.5 / 3.6 / 3.7).
- **`/worldforge status` and every `resume` command read the ledger** to report and to re-enter the correct phase and round.
- **The Compiler verifies the ledger** before compiling: every required phase `COMPLETE` (conditional phases `COMPLETE` or `SKIPPED`), `world_mode` consistent with Master Design Section 1, and `status` not `BLOCKED`/`ESCALATED`.

---

## 💾 CHECKPOINT DISCIPLINE (write-as-you-go)

Every phase agent that writes a pipeline artifact follows three rules. They exist because long phases otherwise accumulate hours of settled work in conversation memory, and because a failed or silently-empty tool write otherwise goes unnoticed until a later phase reads the file. Both failure modes are documented from live runs: a Phase 0 interview held ~6 hours of seed content in memory before its first write, and a Phase 2 run shipped a zero-byte `Instructions_[CardName].md` that nobody caught until the user checked.

1. **Commit each unit as it locks.** A unit is the phase's natural grain: a World Seed section (Interviewer), a Master Design section (Refiner), a draft file — or, within the large entry files, a complete lorebook entry (Architect / Intimacy Architect) — an Export file (Compiler), a report file (Editor / auditors / Prompt Engineer). Write the unit to disk as soon as it is settled; never hold more than one locked-but-unwritten unit in memory. Do not batch multiple units into one oversized write. Do not degrade below the unit grain either — line-at-a-time writing multiplies the failure surface and burns the session; one complete section or entry per write is the floor.
2. **Verify the write landed.** After each write, re-read or stat the target: it exists, is non-empty, and ends with the content just written. A write that failed, timed out, or produced an empty or truncated file halts that unit — rewrite the *same* unit until it verifies. Never build unit N+1 on an unverified unit N.
3. **Resume from disk, not memory.** Every `resume phase[N]` — and any mid-phase recovery after an error — starts by inventorying the phase's output files against the phase's mandatory-output list: which units exist, which are missing, empty, or truncated. Continue from the first incomplete unit. Do not rewrite units that verify intact, and do not reconstruct from conversation memory what is already on disk — the file is the source of truth.

Checkpoint state is inferred from disk; it is not tracked in the Pipeline State Ledger (the ledger tracks phases, checkpoints track units within one). Fallback writes under a failing tool obey the Compiler's FILE-WRITING & ENCODING guard: UTF-8 via the file-write tool or a Python/Node script — never PowerShell `Set-Content`/`Add-Content`/`>` redirection, which mojibakes em-dashes and curly quotes in Drafts markdown exactly as it does in Export JSON.

---

## BRAINSTORM (optional ideation, upstream of Phase 0)

Some users arrive with a fully-formed concept; the Interviewer is built for them. Others arrive with only a vibe — an image, a mood, a single character, a "what if" — and nothing solid enough for the Interviewer's structured, specificity-demanding questions to land. `/worldforge brainstorm` is the optional front porch for that state.

It invokes the **Brainstormer** (`agent_roles/Brainstormer/00_The_Brainstormer.md`) as a single standalone step (Phase 0-pre). Where the Interviewer is **convergent** (walks the template, pushes for depth, refuses weak material), the Brainstormer is **divergent**: it generates multiple premise directions, yes-ands the user's instincts, follows the spark, and helps an idea find its shape. When a premise has a pulse — a central tension, a feel, and at least one anchor the user is excited about — it reflects that back and hands off.

**Load-bearing properties:**
- **Writes only its notes files.** Informal, unstructured ideation notes in the project folder — explicitly *not* a World Seed. The Brainstormer never authors or edits `World_Seed.md`, never writes `Drafts/` or `Export/`, and never touches structural pipeline material. Seed authorship belongs to the Interviewer alone. Its run-scoped output is `Brainstorm_Notes.md`: **exactly one per project, written fresh every run** — each invocation overwrites any prior `Brainstorm_Notes.md` in full and stamps it with its `Posture:` (fresh-start | improvement | revision-diagnostic | adaptation) + date, so a stale file from an earlier run never has to be deleted by hand and consumers can confirm which run produced it. The one exception is the standalone improvement door (`brainstorm --improve`), which instead writes the standing **`Big_Brain_Storm.md`** — a living idea file rewritten fresh each standalone session with still-open ideas carried forward; no agent consumes it silently (`revise --brainstorm` and the rebaseline `--then-brainstorm` chain *offer* to adapt from it; a plain `--rebaseline` surfaces its existence and routes), and it leaves `Brainstorm_Notes.md` untouched.
- **Upstream of the pipeline, not a phase of it.** It does not classify tiers, advance the Pipeline State Ledger, or invoke any downstream agent. It is a standalone optional entry point, like a pre-`start`.
- **Hands off to `/worldforge start`.** The Interviewer reads `Brainstorm_Notes.md` if present (its Context Manifest lists it under "Load if present") as raw starting material, then runs the full interview — pushing for exactly the specificity the Brainstormer deliberately left open, and confirming (not inheriting) the notes' non-binding World Mode leaning.
- **Optional and skippable.** A user with a developed concept skips brainstorm entirely and goes straight to `/worldforge start` or `/worldforge skip phase0`. Nothing downstream depends on a brainstorm having happened.
- **Four postures.** The default (Brainstormer Sections 1–7) is the fresh start above. The **improvement posture** (Section 8) brainstorms *changes to an existing world* — it reads the world's current state and diverges on what to add, rework, or deepen, respecting the world's spine (an idea that flips World Mode, swaps the protagonist, or overturns the core concept is named as convert territory). It has two doors. **Chained:** `/worldforge convert --rebaseline --then-brainstorm` — after a rebaseline consolidates a revised world, the Brainstormer reads the consolidated `World_Seed.md`, explores improvements — offering parked ideas from the source's standing `Big_Brain_Storm.md` if one exists (ask-first), and carrying the curated file forward to the target when brought in — writes `Brainstorm_Notes.md`, and the chain continues into the Interviewer in seed-revision posture (which reads those notes as proposals). **Standalone:** `/worldforge brainstorm --improve` — no-commitment idea ping-pong against any existing world (reads `Drafts/Master_Design.md` read-only when the world is built, `World_Seed.md` otherwise), recorded in the standing **`Big_Brain_Storm.md`** rather than `Brainstorm_Notes.md`; nothing is dispatched afterward — a later `revise --brainstorm` or rebaseline `--then-brainstorm` chain offers to adapt a parked idea from the file, or the user takes a landed change through its normal door (`/worldforge revise`, seed edits before `skip phase0`, or `/worldforge convert`), or the ideas just stay parked. A bare `/worldforge brainstorm` invoked against a project that already contains a world is usually a mistake for `--improve` — confirm intent before running the fresh-start posture there. The **revision-diagnostic posture** (Section 9) serves the post-launch *pre-articulation* case — something feels off in a shipped world but the user can't name what to revise. Invoked by `/worldforge revise --brainstorm`, it reads `Drafts/Master_Design.md` read-only, diagnoses divergently (the domain lenses as diagnostic vocabulary), and writes a primary concern to `Brainstorm_Notes.md` that the Reviser then classifies. The **adaptation posture** (Section 10) serves the user who arrives with an *existing narrative document* — a story, a fanfiction, a roleplay log — rather than a blank-page vibe. Invoked by `/worldforge brainstorm --adapt <document_path>`, it reads the document read-only, extracts the world latent in it (cast, setting, tone, the prose style as a Style Contract sample, and any intimate register the source shows for Phase 2.5), and diverges on the gap between a story-to-read and a world-to-play-in — above all the `{{user}}` slot the document's fixed POV can't supply, which it recommends from the document's POV and confirms — then writes an `adaptation`-stamped `Brainstorm_Notes.md` the Interviewer reads exactly like a `fresh-start` file. See the CONVERT section, `workflows/world-forge-convert.md`, and `workflows/world-forge-revise.md`.

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
4. The protagonist ({{user}}) — wound, hidden layer, contradiction, power and limits, arc trajectory, physical, voice, **and the Posture Toward {{user}} block** (declared posture `adversarial` / `indifferent` / `mixed` / `deferential`, a named force that does not defer, concrete losable things, the permitted shapes of a lost scene and the off-the-table boundary). Required in every world, `deferential` power fantasies included — an unstated posture is not a neutral world, it is the model's trained deference filling the gap
5. Characters — central wound, shield, crack, voice with sample lines, physical in anatomical order, relationships, NPCs with sample lines, plus the per-card style override declaration (only for cards flagged in Section 1.5)
6. Arcs — hidden information rules, dramatic beats, NPC shifts, entry and exit triggers, tone and pacing
7. Technical specifications — cards, lorebooks, depth_prompt assessment per character
8. Test scenarios (Section 7b) — three to five specific roleplay moments the user intends to play through
9. **Intimacy & Sexuality (Section 8)** — world-level posture toward sex, per-character intimacy substrate, per-arc thematic functions and scene types, tonal hard rules for intimate content. Conditional on the world containing intimate scenes.
10. **Runtime Directives (Section 9)** — optional engine-steering asks about how the model must behave turn-by-turn (e.g., "combat must feel slow and costly"), each with a wrong-response example and a scope. The Prompt Engineer must address every one in the Chat Completion Preset. Most worlds leave this empty; misplaced answers (world facts, single-character behavior, style) are routed to their proper sections instead.

If the user resists developing a section, the Interviewer adds an explicit note in the document marking it for Refiner review rather than silently filling gaps.

**This phase exists because the World Seed is hardest to write well the first time.** A weak World Seed propagates through every subsequent phase. Five minutes of pushback at this stage saves an hour of debugging at the runtime stage.

**Optional upstream step.** Users who arrive with only a vibe — no premise solid enough to interview against — can run `/worldforge brainstorm` first (see BRAINSTORM below). It is a divergent ideation partner that produces informal `Brainstorm_Notes.md`, which the Interviewer then reads as starting material. The Interviewer still runs the full interview; the notes are a warm start, not a substitute.

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

---

## PHASE 2: DRAFTING — THE ARCHITECT

**Invoke:** `@agent_roles/02_The_Architect.md`
**Input:** `Drafts/Master_Design.md` with REFINER SIGN-OFF
**Output:** All draft files in `Drafts/`

**Mandatory outputs (all seven required):**
1. `Card_[CharName].md` — character card content per card
2. `User.md` — `{{user}}` Persona Description text (paste-ready for ST → User Settings → Persona Management; paired with the Tier 2 Protagonist Lorebook)
3. `Tier2_[ProtagonistName]_Entries.md` — Protagonist Lorebook ({{user}} identity reference)
4. `Tier1_World_Entries.md` — all Tier 1 entries
5. `Tier2_[CharName]_Entries.md` — Tier 2 entries per character/NPC (principals as full profiles, roster NPCs as compact stat blocks for large casts)
6. Tier 3 lorebook — *arc mode:* `Tier3_Arc[N]_[Title]_Entries.md` per arc; *sandbox mode:* a single `Tier3_Sandbox_Entries.md` (`SANDBOX_STATE` + `WORLD_PULSE`)
7. `Instructions_[CardName].md` — system_prompt + post_history_instructions + depth_prompt per card

If the PRE-SUBMISSION CHECKLIST shows any of these unchecked, return to Architect before proceeding.

---

## PHASE 2.5: INTIMACY DRAFTING — THE INTIMACY ARCHITECT

**Invoke:** `@agent_roles/06_The_Intimacy_Architect.md`
**Input:** Architect's complete drafts + `Drafts/Master_Design.md` + `World_Seed.md` Section 8
**Output:** Intimacy drafts added to `Drafts/`

**Conditional phase.** Runs if and only if the World Seed Section 8 contains material — i.e., the world includes intimate scenes meaningful enough to warrant craft fidelity. For wholesome or low-intimacy worlds where Section 8 was deliberately left empty by the user, this phase is skipped and the pipeline proceeds directly from Phase 2 to Phase 3.

**Mandatory outputs when phase runs:**
1. `Tier2_[CharName]_Intimacy_Profile.md` — one per character with intimate scene presence. Permanent substrate: trauma map, body reactions (**embodied baseline + reaction set**), vulnerability shape, voice in intimacy, hard limits and hard yeses, and the **physical dyad** per pairing with a real differential. **Extends to NPCs:** principal NPCs get full profiles; roster NPCs get compact intimate stat blocks (Intimacy Architect §6.5) — load-bearing for sandbox worlds, which usually carry sexual material across a large NPC cast.
1b. `Tier2_[ProtagonistName]_Intimacy_Profile.md` — `{{user}}`'s intimate embodiment (Intimacy Architect §6.6), authored whenever World Seed Section 3 carries the field. **Reference data other characters react to, never an instruction to play `{{user}}`.** Without it, every intimate scene in the world renders other characters reacting to a stock default body.
2. Tier 3 register — *arc mode:* `Tier3_Arc[N]_Intimacy_Register.md` per arc (delta only: arc thematic function, per-character notes, live scene types, arc hard rules). *Sandbox mode:* a single `Tier3_Sandbox_Intimacy_Register.md` (standing `INTIMACY_FUNCTION`, `INTIMATE_SCENE_TYPES`, `INTIMATE_HARD_RULES`; no arc deltas).

**Failure conditions:**
- Section 8 is missing material the agent needs → produces `UNRESOLVED_INTIMACY.md`, halts pipeline.
- Cross-reference inconsistency with existing drafts (card description contradicts Tier 2 profile, arc state contradicts intimate register, etc.) → flagged in output for resolution.
- Function/substrate contradiction at the Master Design level (an arc requires intimate behavior the character's substrate forbids) → halts and escalates to user. The Intimacy Architect does not paper over these.

The Intimacy Architect does not author or modify character cards. Card-level content is the original Architect's domain. Intimacy lives in the lorebook.

---

## PHASE 3: STRUCTURAL VALIDATION — THE EDITOR (ITERATIVE LOOP)

**Invoke:** `@agent_roles/03_The_Editor.md`
**Input:** All `Drafts/` files + `Drafts/Master_Design.md`

Validates four layers: prose quality, tier integrity + lorebook entry quality, LLM instruction quality, and intimacy entry quality (when intimacy drafts are present).

**Hard rules:**
- Arc-specific content in Tier 1 or Tier 2 = immediate rejection
- ARC_STATE entry missing hidden information rules = immediate rejection
- system_prompt applicable to any character in any world = immediate rejection
- Arc lorebook with fewer than 8 entries = rejection
- Tier 2 Intimacy Profile containing arc-specific content = immediate rejection
- Tier 3 Intimacy Register restating substrate already in Tier 2 = immediate rejection
- INTIMACY_FUNCTION entry (per-arc `INTIMACY_FUNCTION_Arc[N]` in arc mode, or the standing `INTIMACY_FUNCTION` in sandbox mode) missing thematic function name or prose register specification = rejection
- Sexual NPC with no intimate substrate (no full profile and no §6.5 compact stat block) = rejection (coverage gap)

```
LOOP:  (each return increments the ledger's `3 Editor` Round)
  IF files missing → return to relevant Architect (Architect or Intimacy Architect)
  IF hard failures → return affected files to relevant Architect
  IF quality below threshold → return with directives
  IF round > 3 (per ledger), no improvement → ⏸ PAUSE, escalate to user (ledger → ESCALATED)
  IF all pass → EDITOR SIGN-OFF → Phase 3.5 + 3.6 + 3.7
```

---

## PHASE 3.5: BEHAVIORAL FIDELITY — THE VOICE AUDITOR

**Invoke:** `@agent_roles/03b_The_Voice_Auditor.md`
**Input:** All Editor-approved `Drafts/` + `Drafts/Master_Design.md` + `World_Seed.md` Section 7b
**Output:** `Drafts/Voice_Audit_Report_[Round N].md`

Generates sample regular dialogue using the drafts as runtime context — as a **cold read** (plausible failure pre-committed per scenario, expected outcome out of view during generation, every PASS evidence-cited and counterfactual-probed), over a test matrix whose scenario classes go beyond the happy path (trigger-collision, near-miss/false-trigger, off-script pressure, coverage-void probes, and a **bid** scenario in every arc) — and audits against character spec for trigger-response fidelity, voice distinctiveness, arc register integrity, reflex misfires, NPC voice drift, and — where the world has principal NPCs — NPC agency and goal-following in a lull (Step 3J: do NPCs take initiative toward a stated Standing Goal rather than the scene freezing? for laddered NPCs, do moves trace to the named active stage, and does the model hold the stage under a temptation scenario rather than jumping to the endgame?).

**Step 3K — protagonist jeopardy — runs on every world and every arc, with no exemptions.** Every other check asks whether a character is faithfully itself; this one asks whether the world is *not on the player's side*. Against the bid scenario it tests the three trained reflexes — an NPC conceding because `{{user}}` asked, a stated attempt rendered as an accomplished fact, a convenient rescue with no antecedent — and, with equal weight, the over-correction: agency seizure, narrating `{{user}}`'s defeat for them, no-win scenes, adversity with no source. Findings split by breadth: isolated to one arc or NPC = world-side (Architect, the ARC_STATE / SANDBOX_STATE stance directive); uniform across the whole matrix = engine-side (Prompt Engineer — the `protagonist_jeopardy` preset block or the jailbreak's role-separation clause).

```
IF Critical or High failures → return to Architect with rewrite directives (increment ledger `3.5` Round)
IF round > 3 (per ledger), no improvement → ⏸ PAUSE, escalate to user (ledger → ESCALATED)
IF only Medium failures → may sign off with notes
IF no failures → VOICE AUDITOR SIGN-OFF
```

---

## PHASE 3.6: ARC CONTINUITY — THE ARC TRANSITION AUDITOR

**Invoke:** `@agent_roles/03c_The_Arc_Transition_Auditor.md`
**Input:** All Editor-approved `Drafts/Tier3_*` files + `Drafts/Tier2_*` files + `Drafts/Master_Design.md`
**Output:** `Drafts/Arc_Transition_Audit_[Round N].md`

**Conditional phase.** Runs only in **arc** mode. In **sandbox** mode there are no consecutive arcs and no arc seams to audit — this phase is skipped (exactly as Phase 3.7 is skipped without intimacy), and Phases 3.5 + 3.7 (if applicable) proceed without it.

Verifies continuity across every consecutive arc pair: trigger continuity, CHARACTER_STATE continuity, NPC behavioral shift continuity, relationship & belief continuity (Check 3b — bonds and beliefs drift only through earned beats, never teleporting or silently resetting), world state continuity, hidden information rule continuity, dramatic beat sequence, tone register continuity.

```
IF Critical failures → return to Architect (increment ledger `3.6` Round)
IF round > 3 (per ledger), no improvement → ⏸ PAUSE, escalate to user (ledger → ESCALATED)
IF only Medium failures → may sign off with notes
IF no failures → ARC TRANSITION AUDITOR SIGN-OFF
```

---

## PHASE 3.7: INTIMATE SCENE FIDELITY — THE INTIMACY AUDITOR

**Invoke:** `@agent_roles/03d_The_Intimacy_Auditor.md`
**Input:** All Editor-approved `Drafts/` (including Intimacy Architect's outputs) + `Drafts/Master_Design.md` + `World_Seed.md` Section 7b/8
**Output:** `Drafts/Intimacy_Audit_Report_[Round N].md`

**Conditional phase.** Runs if and only if Phase 2.5 ran and produced intimacy drafts. If Phase 2.5 was skipped, this phase is also skipped.

Generates sample intimate scenes using the drafts as runtime context — as a **cold read** (plausible failure pre-committed per scenario, expected outcome out of view during generation, every PASS evidence-cited and counterfactual-probed), over a test matrix whose scenario classes go beyond the canonical intimate beats (trigger-collision, function-shift, boundary, hard-limit probe, substrate near-miss) — and audits against two lenses:
- **Primary lens — voice fidelity:** does the character behave like themselves during sex? Substrate fidelity, trauma map fidelity, voice continuity, hard limit integrity.
- **Secondary lens — thematic register match:** does the scene serve its declared function? Function fidelity, prose register match, direction fidelity, arc atmosphere preservation.

When the lenses conflict, voice fidelity wins. Function/substrate contradictions at the Master Design level are escalated to the user, not patched at the draft level.

```
IF Critical or High failures → return to relevant Architect (Architect for cards, Intimacy Architect for intimacy entries) (increment ledger `3.7` Round)
IF function/substrate conflicts found → escalate to user
IF round > 3 (per ledger), no improvement → ⏸ PAUSE, escalate to user (ledger → ESCALATED)
IF only Medium failures → may sign off with notes
IF no failures → INTIMACY AUDITOR SIGN-OFF
```

**Phases 3.5, 3.6, and 3.7 run in parallel.** All three (or all that ran, where 3.7 is conditional) must sign off before Phase 4 begins. Failures from any phase trigger a return to the relevant Architect, then re-Editor, then re-audit.

---

## PHASE 4: IMPLEMENTATION — THE COMPILER

**Invoke:** `@agent_roles/04_The_Compiler.md`
**Input:** Approved `Drafts/` (with Voice + Arc Transition + Intimacy sign-offs as applicable) + `templates/` + `Notes_Quick_Reference.md` (+ `Notes_On_functionality.md` schema sections on demand)
**Output:** `Export/` directory

**Read `Notes_Quick_Reference.md` first**, then the `Notes_On_functionality.md` schema sections the Compiler spec's Context Manifest names (§5.1b V3 card, §5.2 World Info file, §6 gotchas). `Notes_On_functionality.md` is the authoritative ST runtime reference — where it contradicts the quick reference, templates, or this document, it takes precedence.

**Builds:**
- Character Card JSON per card (`system_prompt`, `post_history_instructions`, and `data.extensions.depth_prompt` mandatory fields, never empty)
- `User.md` — `{{user}}` Persona Description text (passed through from `Drafts/User.md` unchanged; paste-ready for ST persona)
- All lorebook/register files are prefixed with `[WorldName]_` (the world-name token, as in `[WorldName]_ChatPreset.json`) so a world's whole lorebook set groups together in ST's filename-sorted World Info list (Compiler file-naming convention before Step 5). Cards and `User.md` are not prefixed.
- `[WorldName]_[ProtagonistName]_Lorebook.json` — Tier 2, {{user}} identity reference
- `[WorldName]_World_Lorebook.json` — Tier 1, all entries at `position: 0`
- `[WorldName]_[CharName]_Lorebook.json` — Tier 2, one per character/NPC, all entries at `position: 1`
- `[WorldName]_[CharName]_Intimacy_Profile.json` — Tier 2, one per character/NPC with intimate presence (principal full profiles; roster NPC compact stat blocks may share `[WorldName]_NPC_Intimacy_Roster.json`), all entries at `position: 1`. Compiled from Phase 2.5 drafts when present.
- `[WorldName]_Arc[N]_Lorebook.json` — Tier 3, one per arc (min 8 entries each, ARC_STATE at `position: 1` with `ignoreBudget: true`, TENSION at `position: 4`) — *arc mode*
- Tier 3 intimacy register — *arc mode:* `[WorldName]_Arc[N]_Intimacy_Register.json` per arc with intimate beats; *sandbox mode:* a single `[WorldName]_Sandbox_Intimacy_Register.json` (standing INTIMACY_FUNCTION CONSTANT with `ignoreBudget: true`). Compiled from Phase 2.5 drafts when present.
- An inert `[[NPC_MANIFEST]]` entry embedded in each NPC/scene-bearing lorebook — the NPC Memory Contract index consumed by the `npc-memory` ST extension (Compiler Step 7.7; CLAUDE.md principle #12). Additive; not a separate file.

**Golden Rule:** One draft entry = one JSON entry. Never merge.

**Post-compile check (read-only):** if a Python runtime is available, run `python tools/validate_export.py Export/` after the last file is written. It verifies UTF-8 integrity (mojibake markers), strict JSON parse, `{{original}}` presence on both card override fields, position enum range, and UID uniqueness — the exact failure modes of the Compiler's pre-save guards, checked deterministically. It never modifies files. Failures mean the source is wrong: fix and re-compile; do not hand-edit Export/ JSON.

In SillyTavern: import the individual lorebooks — `[WorldName]_World_Lorebook.json` and the per-character lorebooks (plus character intimacy profiles) stay enabled permanently; swap the arc lorebooks (including arc intimacy registers) in and out as the story advances. In **User Settings → Persona Management**, create the persona for this world, paste the Persona Description block from `Export/User.md` into the Description field, and link `[WorldName]_[ProtagonistName]_Lorebook.json` in the Lorebook field.

---

## PHASE 5: RUNTIME VALIDATION — THE PROMPT ENGINEER

**Invoke:** `@agent_roles/05_The_Prompt_Engineer.md`
**Input:** All `Export/` files + `Notes_Quick_Reference.md` + `Notes_On_functionality.md` (§5.2, §5.10, §8 mandatory) + `templates/Chat_Completion_Preset_template.json` + `agent_roles/05a_Block_Library.md` (Workstream B only) + `Drafts/Master_Design.md`
**Output:** `Export/Prompt_Engineer_Audit.md` + `Export/[WorldName]_ChatPreset.json` + `Export/Authors_Note_Suggestions.md`

**Read `Notes_Quick_Reference.md` plus `Notes_On_functionality.md` §5.2 / §5.10 / §8 completely before beginning (rest of the file on demand). For Workstream B, load `templates/Chat_Completion_Preset_template.json` as the structural reference and `agent_roles/05a_Block_Library.md` as the block library — do not author the preset from scratch.**

**Workstream A — Audit (read-only against Export/):** Reviews every lorebook entry (including intimacy profiles and registers) for position correctness, injection order, keyword coverage, token budget risk. Reviews every character card for `system_prompt`, `post_history_instructions`, and `depth_prompt`. Produces audit report with **recommended corrections** for any issues found. The Prompt Engineer does NOT modify Export/ JSON files — recommendations are surfaced in Sections 7 and 8 of the audit report as plain-text instructions for the user to apply manually. The audit report's status line distinguishes "COMPLETE — pipeline ready" (no recommendations generated) from "AUDIT COMPLETE — N manual corrections required" (recommendations outstanding).

**Workstream B — Chat Preset:** Begins with the Section 5.0b Block Selection Rationale — an analytical write-up that names this world's archetype, predicts 4-8 specific runtime failure modes, and maps each failure mode to the block(s) that address it. Block selection is the *outcome* of this analysis, not a checklist. **User-stated runtime directives (Master Design Section 12, from World Seed Section 9) enter the analysis as requirements, not suggestions:** every directive must be implemented in a world-tunable block — an extended world-specific core block, an adapted optional block, or a custom block — with the mapping shown in a Runtime Directive Coverage table; directives never land in the Main Prompt, Jailbreak, or Formatting blocks or inside `<style_contract>` (the world-agnostic engine surfaces of the override architecture). The agent then starts from `templates/Chat_Completion_Preset_template.json` and authors content for the 8 core blocks (Main, Deep Think, Arc Guardian, Lore Integration, Spatial Awareness, Sensory Embodiment, Formatting, Jailbreak), enables/disables the 2 conditional core blocks (Multi-Character Dynamics for 2+ AI cards or Director NPC; NSFW for Section 8 in scope), and adds optional blocks from the menu (Subtext, Consequence Tracking, Power Asymmetry, Atmosphere & Dread, Internal Monologue Discipline, Time & Continuity Anchors, Cultural Voice & Diction, Opening Variation, Perception Boundary, NPC Ensemble & Enrichment) or custom blocks as the Rationale warrants. **Sandbox worlds** default to enabling Multi-Character Dynamics, including NPC Ensemble & Enrichment (NPC-to-NPC dialogue, ensemble prose scaling, organic NPC enrichment within guardrails), and weighting Sensory Embodiment high — see the Section 5.0b sandbox-mode block guidance. **The Main Prompt's `<style_contract>` block is parameterized from Master Design Section 11a (perspective, tense, marker enums); the active-speaker rule is included only when Section 11c reports `is_multi_perspective: true`; the DIRECTOR-CARD RULE line (SHARED §3d) is included only when Section 11c reports `has_director_card: true` — it keeps Director-card turns coherent when the perspective line's `{{char}}` macro resolves to the Director card's name; the Formatting block is the slim deferral form referencing both `<style_contract>` and `<style_override>` by name.** NSFW when enabled covers thematic function discipline, voice & sound register (onomatopoeia mapped to body reactions, slurred speech mechanics, voice register shifts), body coordination (pre-scene retrieval of physical facts, multi-body geometry mapping, narrated adaptation when geometry doesn't work natively), hard limits, and world hard rules. Verifies `forbid_overrides: false` on `main` and `jailbreak`. Runs the Section 5f Pass 1 + Pass 2 self-validation before saving. Produces `[WorldName]_ChatPreset.json` ready for ST import.

**Author's Note suggestions (Build mode only):** alongside the audit and preset, the Prompt Engineer writes `Export/Authors_Note_Suggestions.md` — a small player-facing file with a primer on SillyTavern's Author's Note plus 3–5 world-tuned example notes the player can paste in to steer a scene transiently. Suggestions only; it modifies no other file (see agent Section 4c).

Appends SIGN-OFF to audit file.

---

## PHASE 5.5: MANUAL CORRECTION APPLICATION (conditional)

**Invoke:** Manual user action — no agent runs this phase
**Input:** `Export/Prompt_Engineer_Audit.md` Sections 7 and 8
**Output:** Modified `Export/[CharName]_Card.json` and `Export/[LorebookName].json` files

**Conditional phase.** Runs only if the Prompt Engineer's audit report contains recommendations in Sections 7 or 8. If the audit report's status is "COMPLETE — pipeline ready" with no recommendations, this phase is skipped.

The user opens each file named in the audit's "Files With Recommended Corrections" sign-off block, locates the entry or field referenced by the recommendation, replaces the current value with the recommended value, and saves. After all recommendations have been applied, the world is ready for SillyTavern import.

This phase exists because the Prompt Engineer operates with read-only authority on Export/ JSON files (audit/apply separation). Direct modification by the auditor would produce self-validating corrections with no review gate. Manual application by the user keeps the audit reviewable: corrections can be inspected, modified, or rejected before they reach the final files.

For users who find manual application onerous on large worlds, a future pipeline iteration may add an automated apply step. As of this version, application is manual.

→ **PIPELINE COMPLETE.**

---

## HUMAN PAUSE GATES

| Gate | Trigger | Action |
|---|---|---|
| **Phase 0 Pause** | User wants time to think on a section | Save partial seed, resume with `/worldforge resume phase0` |
| **Phase 1 Blocker** | `UNRESOLVED_QUESTIONS.md` generated | Answer questions, then `/worldforge resume phase1` |
| **Phase 2.5 Blocker** | `UNRESOLVED_INTIMACY.md` generated | Populate Section 8 material, then `/worldforge resume phase2.5` |
| **Phase 3 Stall** | Ledger `3 Editor` Round > 3 without improvement | Review flagged files and advise |
| **Phase 3.5 Critical / Stall** | Voice Auditor flags Critical failures, or ledger `3.5` Round > 3 | Architect revises, re-runs through Editor and Voice Auditor |
| **Phase 3.6 Critical / Stall** | Arc Transition Auditor flags Critical failures, or ledger `3.6` Round > 3 | Architect revises, re-runs through Editor and Arc Transition Auditor |
| **Phase 3.7 Critical / Stall** | Intimacy Auditor flags Critical failures, or ledger `3.7` Round > 3 | Relevant Architect revises, re-runs through Editor and Intimacy Auditor |
| **Phase 3.7 Conflict** | Function/substrate contradiction found | User decides: change substrate, change function, or accept the failure |
| **Phase 4 Missing Templates** | Template file not found | Add to `templates/`, then `/worldforge resume phase4` |
| **Phase 5 Audit Recommendations** | Sections 7/8 of `Prompt_Engineer_Audit.md` contain corrections | Open named Export/ files, apply each recommendation manually, save. Pipeline is COMPLETE only after all recommendations are applied. |

---

## FILE STRUCTURE

```
[project-name]/
├── Brainstorm_Notes.md                            ← Optional (the Brainstormer, upstream of Phase 0)
├── Big_Brain_Storm.md                             ← Optional (standing idea file — standalone `brainstorm --improve` sessions)
├── World_Seed.md                                  ← Produced by Phase 0
├── UNRESOLVED_QUESTIONS.md                        ← Conditional (Phase 1)
├── UNRESOLVED_INTIMACY.md                         ← Conditional (Phase 2.5)
├── Notes_On_functionality.md                      ← ST docs (Phase 4 + 5)
├── Drafts/
│   ├── Master_Design.md
│   ├── Card_[CharName].md
│   ├── User.md                                     ⭐ {{user}} Persona Description (Phase 2)
│   ├── Tier1_World_Entries.md
│   ├── Tier2_[ProtagonistName]_Entries.md
│   ├── Tier2_[CharName]_Entries.md
│   ├── Tier2_[CharName]_Intimacy_Profile.md       ⭐ new (Phase 2.5)
│   ├── Tier2_NPC_Intimacy_Roster.md                ← roster NPC compact intimacy (Phase 2.5, sexual NPC cast)
│   ├── Tier3_Arc[N]_[Title]_Entries.md             ← arc mode
│   ├── Tier3_Sandbox_Entries.md                    ← sandbox mode (single, replaces arc files)
│   ├── Tier3_Arc[N]_Intimacy_Register.md          ⭐ arc mode (Phase 2.5)
│   ├── Tier3_Sandbox_Intimacy_Register.md          ← sandbox mode (single, Phase 2.5)
│   ├── Instructions_[CardName].md
│   ├── Editor_Critique_[Round N].md
│   ├── Voice_Audit_Report_[Round N].md
│   ├── Arc_Transition_Audit_[Round N].md
│   └── Intimacy_Audit_Report_[Round N].md         ⭐ new (Phase 3.7)
├── templates/
│   ├── Char_Card_creation.md
│   ├── Lorebook_creation.md
│   ├── User_Persona_template.md                   ⭐ {{user}} Persona structural reference
│   └── Chat_Completion_Preset_template.json   ⭐ new (Phase 5 structural reference)
└── Export/
    ├── [CharName]_Card.json
    ├── User.md                                     ⭐ {{user}} Persona Description (Phase 4 passthrough)
    ├── [ProtagonistName]_Lorebook.json
    ├── World_Lorebook.json
    ├── [CharName]_Lorebook.json
    ├── [CharName]_Intimacy_Profile.json           ⭐ new (Phase 4, conditional)
    ├── NPC_Intimacy_Roster.json                    ← roster NPC compact intimacy (Phase 4, conditional)
    ├── Arc[N]_Lorebook.json                        ← arc mode
    ├── Sandbox_Lorebook.json                       ← sandbox mode (single, always active)
    ├── Arc[N]_Intimacy_Register.json              ⭐ arc mode (Phase 4, conditional)
    ├── Sandbox_Intimacy_Register.json              ← sandbox mode (single, Phase 4, conditional)
    ├── Compiler_Log.md
    ├── Prompt_Engineer_Audit.md
    ├── [WorldName]_ChatPreset.json
    └── Authors_Note_Suggestions.md
```

---

## TRIGGER COMMANDS

| Command | Action |
|---|---|
| `/worldforge brainstorm` | **Optional, upstream of Phase 0.** Divergent ideation with the Brainstormer for users who arrive with only a vibe — generates premise directions, then writes informal `Brainstorm_Notes.md`. Produces no World Seed; hand off to `/worldforge start`. See BRAINSTORM below. |
| `/worldforge brainstorm --adapt <document>` | **Optional, upstream of Phase 0.** Brainstormer **adaptation posture** (`agent_roles/Brainstormer/00_The_Brainstormer.md` Section 10) — reads an existing narrative document (story, fanfiction, roleplay log) read-only, extracts the world latent in it, and diverges on the gap to a playable world (above all the `{{user}}` slot). Writes an `adaptation`-stamped `Brainstorm_Notes.md`; produces no World Seed; hand off to `/worldforge start`. See BRAINSTORM below. |
| `/worldforge brainstorm --improve` | **Optional, any time a world already exists (seed-only or shipped).** Brainstormer **improvement posture, standalone** (`agent_roles/Brainstormer/00_The_Brainstormer.md` Section 8) — pure idea ping-pong against an existing world ("would this fit? should something be added?") with no chain into revise or convert. Reads the world's current state read-only (`Drafts/Master_Design.md` if built, else `World_Seed.md`) plus any prior `Big_Brain_Storm.md`, and writes/refreshes **`Big_Brain_Storm.md`** — a standing idea file, distinct from the run-scoped `Brainstorm_Notes.md` — then stops. A later `/worldforge revise --brainstorm` or a rebaseline `--then-brainstorm` chain offers to adapt a parked idea from it (a plain `--rebaseline` surfaces its existence and routes); the user can equally take a landed change through its normal door (`/worldforge revise`, seed edits before `skip phase0`, or `/worldforge convert`), or leave it parked. See BRAINSTORM below. |
| `/worldforge start` | Begin from Phase 0 (the Interviewer) — arc mode by default. If `Brainstorm_Notes.md` is present, the Interviewer reads it as starting material. |
| `/worldforge start --sandbox` | Begin from Phase 0 in **sandbox mode** (no narrative arcs; standing world-state + large NPC roster). Pre-sets the World Seed `World Mode` field; see SANDBOX MODE below |
| `/worldforge resume phase0` | Resume the interview from the last completed section |
| `/worldforge resume phase1` | Re-run Refiner with answered questions |
| `/worldforge resume phase2` | Re-run Architect |
| `/worldforge resume phase2.5` | Re-run Intimacy Architect (after populating Section 8) |
| `/worldforge resume phase3` | Re-enter Editor loop |
| `/worldforge resume phase3.5` | Re-run Voice Auditor |
| `/worldforge resume phase3.6` | Re-run Arc Transition Auditor |
| `/worldforge resume phase3.7` | Re-run Intimacy Auditor |
| `/worldforge resume phase4` | Re-run Compiler |
| `/worldforge resume phase5` | Re-run Prompt Engineer |
| `/worldforge status` | Report current phase, round, open blockers — read from the Pipeline State Ledger at the top of `Master_Design.md`, not reconstructed from memory |
| `/worldforge skip phase0` | Begin from Phase 1 (user has written World_Seed.md manually, OR resuming after a Section 1/11 revision bounced from the revise pipeline) |
| `/worldforge skip phase2.5` | Skip Intimacy Architect (no intimate content in this world) |
| `/worldforge skip phase3.6` | Skip Arc Transition Auditor (auto-skipped in sandbox mode — no arc seams to audit) |
| `/worldforge skip phase3.7` | Skip Intimacy Auditor (no intimate content in this world) |
| `/worldforge revise` | Begin the revision pipeline for surgical changes to an already-built world (see `workflows/world-forge-revise.md`) |
| `/worldforge revise --freeform` | Revision pipeline with freeform intent input (paste a description, Reviser structures) |
| `/worldforge revise --target [path]` | Revision pipeline with known target file/entry (skips diagnostic narrowing) |
| `/worldforge revise --brainstorm` | Revision pipeline **diagnostic mode** — for when something feels off but you can't name it. Runs the Brainstormer (revision-diagnostic posture, `agent_roles/Brainstormer/00_The_Brainstormer.md` Section 9) to locate the concern — if a standing `Big_Brain_Storm.md` exists (from standalone `brainstorm --improve` sessions), it asks the user whether to fold those parked ideas into the diagnosis and adapts a chosen one into its notes — then the Reviser reads its `Brainstorm_Notes.md` and classifies as normal |
| `/worldforge revise status` | Show all Revision Log entries and their statuses |
| `/worldforge revise resume R[N]` | Resume a pending revision from its last completed phase |
| `/worldforge revise cancel R[N]` | Cancel a pending revision and mark CANCELLED |
| `/worldforge resync-preset` | Regenerate a shipped world's Chat Completion Preset against the current template + block library, picking up pipeline changes made since the world was built (see PRESET RESYNC below). Preset-only; does not re-audit lorebooks or cards. |
| `/worldforge audition` | **On-demand behavioral probe (post-launch), read-only.** Hand the Auditioner one character, one scene, and the active conditions; it simulates how the character would behave and returns YES / NO / IT DEPENDS against your expectation, with a trace to the spec and (on a gap) a revise handle. Changes nothing. See AUDITION below. |
| `/worldforge audition --save` | Same as above, but also writes the audition to `Drafts/Audition_[Char]_[slug].md` as a durable record. |
| `/worldforge convert <source> <target>` | Reframe a shipped world into a new build (different protagonist, different World Mode, different Style Contract, different Core Concept). Produces a new `World_Seed.md` in `<target>`, then hands off to `/worldforge skip phase0`. See `workflows/world-forge-convert.md`. Read-only on `<source>`. |
| `/worldforge convert <source> <target> --brief <path>` | Same as above, but driven by a pre-authored Convert Brief (`templates/Convert_Brief_Template.md`). Converter validates the brief against the source and interviews only on gaps. |
| `/worldforge convert <source> <target> --rebaseline` | **Rebaseline mode** — same world, same protagonist: consolidate a world's accumulated revisions into a clean rebuild, optionally folding in new mechanics. Inverts the Converter's always-regenerate rules (Section 3/5/7b carry from the post-revision Master Design). Fresh UIDs — running chats do not migrate. Combines with `--brief`. See `agent_roles/Converter/00_The_Converter.md` Section 9. |
| `/worldforge convert <source> <target> --rebaseline --then-interview` | Rebaseline, then go directly into **Phase 0 (the Interviewer, seed-revision posture** — `agent_roles/00_The_Interviewer.md` Section 9**)** to make major changes against the consolidated seed before Phase 1 runs. Requires `--rebaseline`. |
| `/worldforge convert <source> <target> --rebaseline --then-brainstorm` | Rebaseline, then go into the **Brainstormer (improvement posture** — `agent_roles/Brainstormer/00_The_Brainstormer.md` Section 8**)** to brainstorm *what* to change against the consolidated seed, **then** the Interviewer (seed-revision posture) reads those notes as proposals. For when changes are wanted but undecided. Requires `--rebaseline`; supersedes `--then-interview`. |

---

## POST-LAUNCH REVISIONS

Once a world has completed Phase 5.5 (pipeline complete, Export/ ready, world in play), surgical changes use the **revision pipeline** — a parallel fork that runs mini-versions of the agents above with read-mostly authority and UID-preserving compilation. See `workflows/world-forge-revise.md` for the full revise pipeline.

The bright line is **Master Design Section 1 (Core Concept & Tone) and Section 11a (Style Contract world defaults)**. Revisions that don't touch these stay in the revision pipeline (faster, surgical, preserves running ST chat states). Revisions that touch them require a full re-run from Phase 1 via `/worldforge skip phase0` — the existing `World_Seed.md` is reused, the Interviewer is skipped, and Phases 1–5 rebuild from scratch. The Reviser performs this classification and bounces out-of-scope revisions automatically.

**When the rebuild is also a reframe — different protagonist, different World Mode, different tonal register — use `/worldforge convert` instead** (see CONVERT below). Convert is the legitimate path for the exact change-categories the revise pipeline bounces: it reads the shipped world's `Master_Design.md` (read-only), captures keep/modify/regenerate decisions, and produces a new `World_Seed.md` in a fresh target folder, then hands off to `/worldforge skip phase0`. Convert preserves the structural world-building work that a from-scratch `/worldforge start` would discard.

---

## CONVERT (reframe a shipped world into a new build)

A shipped world's `Master_Design.md` carries substantial structural work — world rules, factions, cosmology, NPCs — that survives a protagonist swap, a World Mode flip, or a Style Contract change even though the revise pipeline cannot. `/worldforge convert` is the operation that captures the reuse: it reads the source's `Master_Design.md` (read-only), walks the user through a preservation matrix (keep / modify / drop / regenerate, per source section), surfaces role reassignments explicitly (the old protagonist becoming an NPC, a source NPC becoming the new `{{user}}`, power-tier shifts), and authors a new `World_Seed.md` in a target project folder.

It invokes the Converter (`agent_roles/Converter/00_The_Converter.md`) as a single phase (C0). The Converter does not replace any pipeline phase; it produces the input to Phase 1. After C0 completes, the user runs `/worldforge skip phase0` against the target folder and the standard pipeline (Phases 1–5.5) builds the new world end-to-end.

**Load-bearing properties:**
- **Read-only on source.** The Converter never modifies any file in the source project. Hard rule.
- **Write-only on target's `World_Seed.md`.** Does not write `Drafts/`, `Export/`, or any other file in the target project — those are the standard pipeline's job.
- **Overlap floor refusal.** If the conversion replaces 3 or 4 of (setting, protagonist, factions, tone), the Converter refuses. That's a fresh build inspired by the source — `/worldforge start` is the right path. Borderline (2 axes replaced) gets surfaced for explicit user confirmation.
- **Single source.** No mashups. Mashing two worlds together is out of scope; run Convert once, use revise later if you want to splice content from a third source.
- **Always-regenerated content (reframe mode).** Section 3 (`{{user}}`), Section 5 (arcs / Sandbox Charter), Section 7b (test scenarios), per-arc/standing intimate functions, and per-card style overrides are always regenerated downstream. These are protagonist-shaped or downstream-derived, so they cannot transfer mechanically. The Converter does not let the user mark them `keep` — except in Rebaseline mode, where the premise (a changed protagonist) is absent and they flip to keep-by-default.
- **Rebaseline mode (`--rebaseline`).** The zero-axes-replaced conversion: same world, same protagonist, rebuilt clean from its *post-revision* Master Design — the consolidation path for a world whose accumulated revisions (R1…R[N]) have outgrown surgical editing, especially when new mechanics are coming. Revision content carries; revision markers do not; the rebuild gets fresh UIDs (running chats do not migrate — the Converter states this cost explicitly). Spec: `agent_roles/Converter/00_The_Converter.md` Section 9; operation: REBASELINE MODE section of `workflows/world-forge-convert.md`.
- **Convert Brief support.** Users can pre-author the keep/modify/regenerate decisions in a `Convert_Brief.md` (against `templates/Convert_Brief_Template.md`) for version-controllable, reviewable conversions. The Converter validates the brief against the source and interviews only on gaps. Pure interview mode also works for ad-hoc conversions. Briefs declare `Operating mode: reframe | rebaseline` in their Section 1.

See the **CONVERT** workflow at `workflows/world-forge-convert.md` for the full operation, the Conversion Manifest format, and the role-reassignment cases.

---

## PRESET RESYNC (post-launch preset upgrade)

A shipped world's `Export/[WorldName]_ChatPreset.json` can fall behind in two independent ways: the **pipeline's preset spec** evolves (a reframed core block, a new optional block, a changed template flag), and/or the **world's content** changes through the revision pipeline (a revised or added arc, a new character) in ways that surface inside preset blocks (Deep Think names the arcs, Arc Guardian references them, the multi-character lattice names characters) but that the revise mini-Prompt-Engineer never writes — it only toggles Multi-Character Dynamics, NSFW, and the Style Contract's conditional ACTIVE-SPEAKER RULE / DIRECTOR-CARD RULE lines. `/worldforge resync-preset` brings the preset current on both, without touching world content.

It invokes the Prompt Engineer in **Preset Resync Mode** (`agent_roles/05_The_Prompt_Engineer.md` Section 8). The agent re-derives each block's content from the current `templates/Chat_Completion_Preset_template.json` + block library (`agent_roles/05a_Block_Library.md`) + the post-revision `Drafts/Master_Design.md`, writes the blocks whose content has drifted (from a spec change, a revision content change, or both) and adds newly-warranted optional blocks, preserves block identifiers + `prompt_order` + revision-applied toggles + the user's field-level customizations, re-runs the Section 5f Pass 1 + Pass 2 self-validation, and writes `Export/Preset_Resync_Report.md` documenting every block changed (with cause), added, or preserved.

**Scope and boundaries:**
- **Preset only.** Resync regenerates the Chat Completion Preset — the one Export/ file the Prompt Engineer authors. It does NOT re-audit lorebooks or cards and does NOT emit Section 7/8 manual-apply recommendations. World content (lorebooks, cards, drafts) is untouched.
- **Reads the post-revision world.** Because it re-derives block content from the current `Master_Design.md`, resync picks up content changes made through the revision pipeline that the revise mini-PE leaves out of the preset. It preserves the toggles the revise mini-PE *does* apply (Multi-Character Dynamics, NSFW, ACTIVE-SPEAKER RULE, DIRECTOR-CARD RULE) — while a *missing-but-warranted* DIRECTOR-CARD RULE line (a Director-card world whose preset predates SHARED §3d) counts as ordinary spec drift that resync adds.
- **Distinct from `resume phase5`.** `resume phase5` re-runs the full Phase-5 audit during an in-progress build. `resync-preset` is a maintenance op on an already-shipped world that only refreshes the preset.
- **Distinct from the revise pipeline.** The revise pipeline *makes* surgical content changes. Resync makes none — it reflects already-applied content and spec changes into the preset. A world can be resynced without ever entering revise, and revised worlds can be resynced afterward to bring the preset fully current.
- **Low risk.** A Chat Completion Preset is a global SillyTavern settings profile, not UID-bearing world info, so re-importing a resynced preset does not disturb running chat states. Git is the rollback path if the user wants the prior preset back.

---

## AUDITION (on-demand behavioral probe, post-launch)

You are deep into playing a shipped world and a question surfaces that the personality is too complex to answer from memory: *would this character actually do this, in this moment, under these conditions?* Gambling a real scene to find out is expensive. `/worldforge audition` is the cheap, read-only way to find out first.

It invokes **The Auditioner** (`agent_roles/Auditioner/00_The_Auditioner.md`) as a single standalone post-launch operation — **not** a numbered pipeline phase. The user hands it one focal character, one scene, the active conditions (which arc, or the standing sandbox state), and optionally the behavior they expect; the Auditioner loads that character's spec as runtime context, simulates the scene **as the model would run it**, and returns a verdict with a trace.

It is the **single-scenario, user-driven cousin of the Voice Auditor** (Phase 3.5). Where the Voice Auditor runs at build time, generates its own systematic matrix across the whole cast and every arc, and feeds rewrite directives back to the Architect, the Auditioner runs whenever the user is curious mid-play, tests exactly the one situation the user names, and changes nothing. It reuses the Voice Auditor's simulation discipline and check vocabulary (Step 3) rather than re-deriving them, and applies the Intimacy Auditor's lens when the probed scene is intimate.

**Load-bearing properties:**
- **Read-only on the whole project.** The Auditioner modifies nothing — not `Drafts/`, not `Export/`, not `Master_Design.md`. It answers a question (audit/apply separation, CLAUDE.md principle #3). When it finds a real gap, it hands the user a **revise handle** (the file + element + kind of change) — it does not apply the change. The user decides; the revise pipeline applies.
- **Three honest verdicts.** Every run resolves to **YES** (the spec reliably produces the expected behavior), **NO** (the spec drives a *different* behavior — the character is correct per spec, the spec just doesn't match the expectation), or **IT DEPENDS** (the spec is silent or self-conflicting here, so the outcome isn't determined — a latent coverage gap surfaced on demand). "Probably" is not a verdict.
- **Mode- and intimacy-aware by inheritance.** Arc worlds load the user-named active arc's CHARACTER_STATE/NPC_SHIFT; sandbox worlds use the standing SANDBOX_STATE (and the user-named ladder stage where one exists). Intimate scenarios additionally pull the Intimacy Profile + active register and apply the intimacy lens. No new machinery — it reuses what the build-time auditors already define.
- **World layer, not engine layer.** It simulates from the Drafts (the content spec the Voice Auditor reads), not the Chat Completion Preset (the engine layer). When real play diverges from a YES verdict, the cause may be the preset, and `/worldforge resync-preset` may be the fix — the Auditioner flags this rather than pretending to have simulated the engine.
- **Not a phase.** It does not advance the Pipeline State Ledger, does not invoke any downstream agent, and produces no first-class pipeline artifact. The optional `--save` record (`Drafts/Audition_[Char]_[slug].md`) is an informal log, read by nothing downstream and deletable freely.
- **Shipped-world precondition, detected from the world — not the ledger.** It is a post-launch tool. It confirms shipped-status from the direct signal (a populated `Export/` + Refiner sign-off, with a Revision Log / `REVISED_FILES.md` as conclusive proof), **not** from the Pipeline State Ledger — which on a shipped-and-revised world is routinely stale or absent and must not be read as "mid-build." Likewise it reads **World Mode from Master Design Section 1**, so a sandbox world is never mistaken for an unfinished arc world. Only a world that never reached the Compiler is declined, with a pointer to the Voice Auditor (Phase 3.5).

See the full operation in `agent_roles/Auditioner/00_The_Auditioner.md`.