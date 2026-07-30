---
description: World Forge build Stage 3 — Validation (Phase 3 Editor loop, Phases 3.5/3.6/3.7 auditors). Dispatched by workflows/world-forge.md.
---

# WORLD FORGE — STAGE 3: VALIDATION
*Stage file 3 of 4 — dispatched by the router (`workflows/world-forge.md`). Not a standalone entry point.*

**Phases:** Phase 3 (the Editor, iterative loop) · Phase 3.5 (the Voice Auditor) · Phase 3.6 (the Arc Transition Auditor, arc mode only) · Phase 3.7 (the Intimacy Auditor, conditional)

**Entry conditions (read from the Pipeline State Ledger; halt if unmet):** ledger rows `2` (and `2.5`, or `SKIPPED`) are `COMPLETE` and the Stage 2 exit gates verified the draft inventory on disk. Resumes (`resume phase3` / `3.5` / `3.6` / `3.7`) re-enter here at the recorded phase and round.

**Exit conditions (verify on disk before handing back):** ledger rows `3`, `3.5`, `3.6` (or `SKIPPED` in sandbox mode), and `3.7` (or `SKIPPED` without intimacy) are `COMPLETE`, each with its report file and sign-off anchor verified on disk per the router's artifact-gate table. Then hand back to the router → Stage 4 (`workflows/world-forge-construction.md`).

**Governing router sections (not restated here):** PIPELINE STATE LEDGER, CHECKPOINT DISCIPLINE, DISPATCH PROTOCOL — all in `workflows/world-forge.md`. Every phase below runs by dispatching its agent; never inline.

**The loop lives in this stage.** The Editor and the three auditors are **read-only on drafts** (audit/apply separation). When a check fails, this stage dispatches the relevant *drafting agent* — `@agent_roles/02_The_Architect.md` or `@agent_roles/06_The_Intimacy_Architect.md` — directly with the critique/audit report's directives, then re-dispatches the Editor, then the auditors. Do not re-enter the Stage 2 file for loop returns (it orchestrates initial authoring, not rework), and never let an auditor "just fix" what it flagged — an auditor-applied fix is a self-validating correction and a pipeline violation. Every loop return increments the phase's `Round` in the ledger; every round's report is a new file (`[Round N]`), never an overwrite of the previous round.

**No audit phase is skippable by judgment.** 3.6 is skipped only by `world_mode: sandbox`; 3.7 (and 2.5 upstream) only by `intimacy_in_scope: false`. "The drafts look fine" is not a skip condition — a completed build with no audit reports on disk is a failed build (DISPATCH PROTOCOL rule 2; `tools/validate_pipeline_state.py` flags it deterministically).

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

**Artifact gate (Phase 3):** `Drafts/Editor_Critique_[Round N].md` exists for the current round; the row goes `COMPLETE` only when the latest round's file contains `EDITOR SIGN-OFF`.

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

**Artifact gate (Phase 3.5):** `Drafts/Voice_Audit_Report_[Round N].md` exists for the current round; the row goes `COMPLETE` only when the latest round's report contains `VOICE AUDITOR SIGN-OFF`.

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

**Artifact gate (Phase 3.6, arc mode):** `Drafts/Arc_Transition_Audit_[Round N].md` exists for the current round; the row goes `COMPLETE` only when the latest round's report contains `ARC TRANSITION AUDITOR SIGN-OFF`. In sandbox mode the row reads `SKIPPED` — never silently absent.

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

**Artifact gate (Phase 3.7, when in scope):** `Drafts/Intimacy_Audit_Report_[Round N].md` exists for the current round; the row goes `COMPLETE` only when the latest round's report contains `INTIMACY AUDITOR SIGN-OFF`. When intimacy is out of scope the row reads `SKIPPED` — never silently absent.

---

**Phases 3.5, 3.6, and 3.7 run in parallel.** All three (or all that ran, where 3.7 is conditional) must sign off before Phase 4 begins. Failures from any phase trigger a return to the relevant Architect, then re-Editor, then re-audit.

---

## STAGE EXIT

1. Verify every audit phase's artifact gate above — the report files and their sign-off anchors, read from disk. A missing audit report means the audit did not happen, whatever the conversation says; re-dispatch it.
2. If a Python runtime is available: `python tools/validate_pipeline_state.py <project folder>` (read-only). Resolve any reported mismatch before proceeding.
3. Hand back to the router → dispatch Stage 4 (`workflows/world-forge-construction.md`).
