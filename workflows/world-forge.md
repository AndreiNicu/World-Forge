---
description: A workflow to build worlds for player to roleplay in.
---

# THE WORLD FORGE PIPELINE
*Orchestrator v8 (router) — Universal Roleplay World Building & SillyTavern Export*

**Produces:** Character Cards + World Lorebook (Tier 1, permanent) + Character & NPC Lorebooks (Tier 2, permanent) + Character/NPC Intimacy Profiles (Tier 2, permanent, where applicable) + Tier 3 lorebook (arc mode: Arc Lorebooks, one active at a time; sandbox mode: a single always-active Sandbox Lorebook) + Intimacy Registers (Tier 3: per-arc in arc mode, a single standing register in sandbox mode, where applicable) + Chat Completion Preset. Works for any world — arc or sandbox, any number of arcs, characters, or NPCs.

---

## ROUTER & STAGE FILES

This file is the **router**. It owns the map — pipeline overview, world mode, the Pipeline State Ledger, checkpoint discipline, the dispatch protocol, trigger commands, pause gates, file structure — and dispatches execution to four **stage files**, each carrying the full phase-by-phase orchestration for its slice of the build:

| Stage | File | Phases |
|---|---|---|
| 1. Discovery & Planning | `workflows/world-forge-discovery.md` | Brainstorm (optional pre-phase) · 0 Interviewer · 1 Refiner |
| 2. Drafting | `workflows/world-forge-drafting.md` | 2 Architect · 2.5 Intimacy Architect |
| 3. Validation | `workflows/world-forge-validation.md` | 3 Editor · 3.5 Voice Auditor · 3.6 Arc Transition Auditor · 3.7 Intimacy Auditor (iterative loop) |
| 4. Construction | `workflows/world-forge-construction.md` | 4 Compiler · 5 Prompt Engineer · 5.5 Manual Apply |

Post-launch operations on shipped worlds are **not build stages** and live in their own workflow files: revise in `workflows/world-forge-revise.md`, convert in `workflows/world-forge-convert.md`, and preset resync + audition + the post-launch routing rules in `workflows/world-forge-postlaunch.md`.

**Load discipline:** hold this router plus the **active stage file only**. Never preload all stage files — the split exists so that each slice of the run carries only its own orchestration. The stage files do not restate the sections of this router; the router's PIPELINE STATE LEDGER, CHECKPOINT DISCIPLINE, and DISPATCH PROTOCOL sections govern every stage.

---

## DISPATCH PROTOCOL (hard rules — read before running anything)

These rules exist because both failure modes below are documented from live runs: a failed model call led the orchestrator to perform an agent's phase inline without the agent's spec loaded, and a completed run shipped with the Phase 3.5–3.7 audit reports never written while the run reported success.

1. **Dispatch, never inline.** Every phase runs by dispatching its agent (`@agent_roles/...`, or the tool's per-phase custom agent/subagent mechanism) with that agent's spec and Context Manifest loaded. If a dispatch or model call fails, retry the dispatch. If dispatch remains unavailable, set the ledger `status` to `BLOCKED`, halt, and report to the user. **Performing a phase's work inline — without the agent's spec loaded — is a pipeline violation, not a fallback.** An inline-produced phase has no Context Manifest, no persona isolation, and no valid sign-off; treat any inline-produced artifact as if the phase never ran.

2. **Artifact-existence gate.** A ledger row may be set `COMPLETE` only after **reading the phase's primary artifact from disk** and verifying all three: the file exists, it is non-empty, and it contains that row's sign-off anchor. Conversation memory, an agent's verbal report, or the orchestrator's recollection do not count — the file is the proof. If the artifact is missing, the phase did not happen, whatever the conversation says; re-dispatch the phase.

   | Phase | Primary artifact(s) on disk | Sign-off anchor |
   |---|---|---|
   | 0 Interviewer | `World_Seed.md` | `INTERVIEWER SIGN-OFF` |
   | 1 Refiner | `Drafts/Master_Design.md` | `REFINER SIGN-OFF` |
   | 2 Architect | The seven mandatory `Drafts/` outputs (stage file 2 lists them) — all present, all non-empty — plus `Drafts/Architect_Checklist.md` | `ARCHITECT PRE-SUBMISSION CHECK` (in `Drafts/Architect_Checklist.md`; also repeated in the submission note) |
   | 2.5 Intimacy Architect | `Drafts/Tier2_*_Intimacy_Profile.md` + the mode-appropriate Tier 3 register file(s) | `INTIMACY ARCHITECT SIGN-OFF` (appended to the final output file) |
   | 3 Editor | `Drafts/Editor_Critique_[Round N].md` (latest round) | `EDITOR SIGN-OFF` |
   | 3.5 Voice Auditor | `Drafts/Voice_Audit_Report_[Round N].md` (latest round) | `VOICE AUDITOR SIGN-OFF` |
   | 3.6 Arc Transition Auditor | `Drafts/Arc_Transition_Audit_[Round N].md` (latest round) | `ARC TRANSITION AUDITOR SIGN-OFF` |
   | 3.7 Intimacy Auditor | `Drafts/Intimacy_Audit_Report_[Round N].md` (latest round) | `INTIMACY AUDITOR SIGN-OFF` |
   | 4 Compiler | `Export/` populated + `Export/Compiler_Log.md` | `COMPILER SIGN-OFF` |
   | 5 Prompt Engineer | `Export/Prompt_Engineer_Audit.md` + `Export/[WorldName]_ChatPreset.json` | `PROMPT ENGINEER SIGN-OFF` |

   This table must stay in sync with the ledger schema's anchor column and with `tools/validate_pipeline_state.py`, which re-checks the same mapping deterministically.

3. **Stage entry check.** Each stage file opens with entry conditions read from the Pipeline State Ledger. A stage entered out of order — its entry conditions unmet, or a prior stage's rows not `COMPLETE`/`SKIPPED` — halts with a report instead of running. Never skip a stage or a phase because "the content is probably fine"; conditional phases are skipped only by their declared conditions (`world_mode`, `intimacy_in_scope`), recorded as `SKIPPED` in the ledger.

4. **Deterministic backstop.** If a Python runtime is available, run `python tools/validate_pipeline_state.py <project folder>` (read-only) at every stage boundary and at pipeline completion. It re-checks the ledger against the artifacts on disk — missing reports, absent sign-off anchors, incoherent conditional skips, order violations — exactly the failure modes the gates above guard, checked without asking the model anything. Failures mean a phase must be re-dispatched; the script never modifies files.

---

## PIPELINE OVERVIEW

```
[User intent — start a new world]
      |
      v
 ────────── STAGE 1: DISCOVERY & PLANNING (world-forge-discovery.md) ──────────
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
 ────────── STAGE 2: DRAFTING (world-forge-drafting.md) ──────────
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
      |
 ────────── STAGE 3: VALIDATION (world-forge-validation.md) ──────────
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
 ────────── STAGE 4: CONSTRUCTION (world-forge-construction.md) ──────────
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
| 2 Architect          | PENDING  | —  | ARCHITECT PRE-SUBMISSION CHECK |
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
- **The orchestrator advances the ledger** — on entering a phase it sets that row `IN_PROGRESS` and updates top-level `current_phase`; on a sign-off it sets the row `COMPLETE` **after passing the artifact-existence gate (DISPATCH PROTOCOL rule 2)**; on a loop return it increments that phase's `Round`; on a pause it sets `BLOCKED`; on a round-ceiling escalation it sets `ESCALATED`. These are file writes, not memory.
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

## TRIGGER COMMANDS

| Command | Action |
|---|---|
| `/worldforge brainstorm` | **Optional, upstream of Phase 0.** Divergent ideation with the Brainstormer for users who arrive with only a vibe — generates premise directions, then writes informal `Brainstorm_Notes.md`. Produces no World Seed; hand off to `/worldforge start`. See the BRAINSTORM section of `workflows/world-forge-discovery.md`. |
| `/worldforge brainstorm --adapt <document>` | **Optional, upstream of Phase 0.** Brainstormer **adaptation posture** (`agent_roles/Brainstormer/00_The_Brainstormer.md` Section 10) — reads an existing narrative document (story, fanfiction, roleplay log) read-only, extracts the world latent in it, and diverges on the gap to a playable world (above all the `{{user}}` slot). Writes an `adaptation`-stamped `Brainstorm_Notes.md`; produces no World Seed; hand off to `/worldforge start`. See the BRAINSTORM section of `workflows/world-forge-discovery.md`. |
| `/worldforge brainstorm --improve` | **Optional, any time a world already exists (seed-only or shipped).** Brainstormer **improvement posture, standalone** (`agent_roles/Brainstormer/00_The_Brainstormer.md` Section 8) — pure idea ping-pong against an existing world ("would this fit? should something be added?") with no chain into revise or convert. Reads the world's current state read-only (`Drafts/Master_Design.md` if built, else `World_Seed.md`) plus any prior `Big_Brain_Storm.md`, and writes/refreshes **`Big_Brain_Storm.md`** — a standing idea file, distinct from the run-scoped `Brainstorm_Notes.md` — then stops. A later `/worldforge revise --brainstorm` or a rebaseline `--then-brainstorm` chain offers to adapt a parked idea from it (a plain `--rebaseline` surfaces its existence and routes); the user can equally take a landed change through its normal door (`/worldforge revise`, seed edits before `skip phase0`, or `/worldforge convert`), or leave it parked. See the BRAINSTORM section of `workflows/world-forge-discovery.md`. |
| `/worldforge start` | Begin from Phase 0 (the Interviewer) — arc mode by default. Dispatch Stage 1 (`workflows/world-forge-discovery.md`). If `Brainstorm_Notes.md` is present, the Interviewer reads it as starting material. |
| `/worldforge start --sandbox` | Begin from Phase 0 in **sandbox mode** (no narrative arcs; standing world-state + large NPC roster). Pre-sets the World Seed `World Mode` field; see WORLD MODE above. Dispatch Stage 1 (`workflows/world-forge-discovery.md`). |
| `/worldforge resume phase0` | Resume the interview from the last completed section — Stage 1 (`workflows/world-forge-discovery.md`) |
| `/worldforge resume phase1` | Re-run Refiner with answered questions — Stage 1 (`workflows/world-forge-discovery.md`) |
| `/worldforge resume phase2` | Re-run Architect — Stage 2 (`workflows/world-forge-drafting.md`) |
| `/worldforge resume phase2.5` | Re-run Intimacy Architect (after populating Section 8) — Stage 2 (`workflows/world-forge-drafting.md`) |
| `/worldforge resume phase3` | Re-enter Editor loop — Stage 3 (`workflows/world-forge-validation.md`) |
| `/worldforge resume phase3.5` | Re-run Voice Auditor — Stage 3 (`workflows/world-forge-validation.md`) |
| `/worldforge resume phase3.6` | Re-run Arc Transition Auditor — Stage 3 (`workflows/world-forge-validation.md`) |
| `/worldforge resume phase3.7` | Re-run Intimacy Auditor — Stage 3 (`workflows/world-forge-validation.md`) |
| `/worldforge resume phase4` | Re-run Compiler — Stage 4 (`workflows/world-forge-construction.md`) |
| `/worldforge resume phase5` | Re-run Prompt Engineer — Stage 4 (`workflows/world-forge-construction.md`) |
| `/worldforge status` | Report current phase, round, open blockers — read from the Pipeline State Ledger at the top of `Master_Design.md`, not reconstructed from memory. If a Python runtime is available, also run `python tools/validate_pipeline_state.py <project folder>` and report any ledger/artifact mismatches. |
| `/worldforge skip phase0` | Begin from Phase 1 (user has written World_Seed.md manually, OR resuming after a Section 1/11 revision bounced from the revise pipeline) — Stage 1 (`workflows/world-forge-discovery.md`) |
| `/worldforge skip phase2.5` | Skip Intimacy Architect (no intimate content in this world) — recorded as `SKIPPED` in the ledger |
| `/worldforge skip phase3.6` | Skip Arc Transition Auditor (auto-skipped in sandbox mode — no arc seams to audit) — recorded as `SKIPPED` in the ledger |
| `/worldforge skip phase3.7` | Skip Intimacy Auditor (no intimate content in this world) — recorded as `SKIPPED` in the ledger |
| `/worldforge revise` | Begin the revision pipeline for surgical changes to an already-built world (see `workflows/world-forge-revise.md`) |
| `/worldforge revise --freeform` | Revision pipeline with freeform intent input (paste a description, Reviser structures) |
| `/worldforge revise --target [path]` | Revision pipeline with known target file/entry (skips diagnostic narrowing) |
| `/worldforge revise --brainstorm` | Revision pipeline **diagnostic mode** — for when something feels off but you can't name it. Runs the Brainstormer (revision-diagnostic posture, `agent_roles/Brainstormer/00_The_Brainstormer.md` Section 9) to locate the concern — if a standing `Big_Brain_Storm.md` exists (from standalone `brainstorm --improve` sessions), it asks the user whether to fold those parked ideas into the diagnosis and adapts a chosen one into its notes — then the Reviser reads its `Brainstorm_Notes.md` and classifies as normal |
| `/worldforge revise status` | Show all Revision Log entries and their statuses |
| `/worldforge revise resume R[N]` | Resume a pending revision from its last completed phase |
| `/worldforge revise cancel R[N]` | Cancel a pending revision and mark CANCELLED |
| `/worldforge resync-preset` | Regenerate a shipped world's Chat Completion Preset against the current template + block library, picking up pipeline changes made since the world was built (see the PRESET RESYNC section of `workflows/world-forge-postlaunch.md`). Preset-only; does not re-audit lorebooks or cards. |
| `/worldforge audition` | **On-demand behavioral probe (post-launch), read-only.** Hand the Auditioner one character, one scene, and the active conditions; it simulates how the character would behave and returns YES / NO / IT DEPENDS against your expectation, with a trace to the spec and (on a gap) a revise handle. Changes nothing. See the AUDITION section of `workflows/world-forge-postlaunch.md`. |
| `/worldforge audition --save` | Same as above, but also writes the audition to `Drafts/Audition_[Char]_[slug].md` as a durable record. |
| `/worldforge convert <source> <target>` | Reframe a shipped world into a new build (different protagonist, different World Mode, different Style Contract, different Core Concept). Produces a new `World_Seed.md` in `<target>`, then hands off to `/worldforge skip phase0`. See `workflows/world-forge-convert.md`. Read-only on `<source>`. |
| `/worldforge convert <source> <target> --brief <path>` | Same as above, but driven by a pre-authored Convert Brief (`templates/Convert_Brief_Template.md`). Converter validates the brief against the source and interviews only on gaps. |
| `/worldforge convert <source> <target> --rebaseline` | **Rebaseline mode** — same world, same protagonist: consolidate a world's accumulated revisions into a clean rebuild, optionally folding in new mechanics. Inverts the Converter's always-regenerate rules (Section 3/5/7b carry from the post-revision Master Design). Fresh UIDs — running chats do not migrate. Combines with `--brief`. See `agent_roles/Converter/00_The_Converter.md` Section 9. |
| `/worldforge convert <source> <target> --rebaseline --then-interview` | Rebaseline, then go directly into **Phase 0 (the Interviewer, seed-revision posture** — `agent_roles/00_The_Interviewer.md` Section 9**)** to make major changes against the consolidated seed before Phase 1 runs. Requires `--rebaseline`. |
| `/worldforge convert <source> <target> --rebaseline --then-brainstorm` | Rebaseline, then go into the **Brainstormer (improvement posture** — `agent_roles/Brainstormer/00_The_Brainstormer.md` Section 8**)** to brainstorm *what* to change against the consolidated seed, **then** the Interviewer (seed-revision posture) reads those notes as proposals. For when changes are wanted but undecided. Requires `--rebaseline`; supersedes `--then-interview`. |

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
| **Dispatch failure** | An agent dispatch/model call fails and retries do not recover it | Ledger `status` → `BLOCKED`; orchestrator halts and reports. Never performed inline (DISPATCH PROTOCOL rule 1). |

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
│   ├── Architect_Checklist.md                      ← Phase 2 durable pre-submission checklist (sign-off artifact)
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

## POST-LAUNCH OPERATIONS (pointers — not build stages)

Once a world has completed Phase 5.5 (pipeline complete, Export/ ready, world in play), four operating modes exist alongside the initial build. Their routing rules and full operations live in `workflows/world-forge-postlaunch.md`; only the map is here:

- **Revise** (`/worldforge revise`) — surgical, UID-preserving changes to a shipped world through the mini-agents. Full pipeline: `workflows/world-forge-revise.md`. The bright line (Master Design Section 1 / Section 11a / `World Mode` changes bounce to a rebuild) is documented in the POST-LAUNCH REVISIONS section of `workflows/world-forge-postlaunch.md`.
- **Convert** (`/worldforge convert`) — reframe a shipped world into a new build (protagonist swap, World Mode flip, Style Contract change), or **rebaseline** (consolidate accumulated revisions). Full pipeline: `workflows/world-forge-convert.md`; summary and load-bearing properties: the CONVERT section of `workflows/world-forge-postlaunch.md`.
- **Preset Resync** (`/worldforge resync-preset`) — refresh a shipped world's Chat Completion Preset against the current spec + post-revision content. Preset-only. Full operation: the PRESET RESYNC section of `workflows/world-forge-postlaunch.md`.
- **Audition** (`/worldforge audition`) — on-demand, read-only behavioral probe of one character in one scene. Full operation: the AUDITION section of `workflows/world-forge-postlaunch.md`.
