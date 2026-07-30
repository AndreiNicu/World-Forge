---
description: World Forge build Stage 2 — Drafting (Phase 2 Architect, Phase 2.5 Intimacy Architect). Dispatched by workflows/world-forge.md.
---

# WORLD FORGE — STAGE 2: DRAFTING
*Stage file 2 of 4 — dispatched by the router (`workflows/world-forge.md`). Not a standalone entry point.*

**Phases:** Phase 2 (the Architect) · Phase 2.5 (the Intimacy Architect, conditional)

**Entry conditions (read from the Pipeline State Ledger; halt if unmet):** the `1 Refiner` row is `COMPLETE` and `Drafts/Master_Design.md` verifies on disk with its `REFINER SIGN-OFF` (Stage 1 exit gate). Resumes (`resume phase2` / `resume phase2.5`) re-enter here per the checkpoint discipline's resume-from-disk rule.

**Exit conditions (verify on disk before handing back):** the seven mandatory Phase 2 outputs exist and are non-empty; when `intimacy_in_scope: true`, the Phase 2.5 outputs exist with the `INTIMACY ARCHITECT SIGN-OFF` appended to the final output file. Ledger rows `2` (and `2.5`, or `SKIPPED`) `COMPLETE`. Then hand back to the router → Stage 3 (`workflows/world-forge-validation.md`). If Phase 2.5 produced `UNRESOLVED_INTIMACY.md`, the ledger is `BLOCKED` and the run pauses for the user.

**Governing router sections (not restated here):** PIPELINE STATE LEDGER, CHECKPOINT DISCIPLINE, DISPATCH PROTOCOL — all in `workflows/world-forge.md`. Every phase below runs by dispatching its agent; never inline.

**Write authority note:** this stage holds the pipeline's only draft-write authority (the Architect and the Intimacy Architect). The validation stage that follows is read-only on drafts; when its audits fail, the *agents of this stage* are re-dispatched with the auditors' directives — but those loop returns are orchestrated by Stage 3, not by re-entering this file.

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

**Artifact gate (Phase 2):** all seven output classes exist on disk and are non-empty — inventory `Drafts/` against the list above (the PRE-SUBMISSION CHECKLIST arrives in the submission note; the on-disk file inventory is the gate). A missing or zero-byte file means the phase is not complete, whatever the checklist says.

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

**Artifact gate (Phase 2.5, when it runs):** the profile and register files above exist and are non-empty, and the `INTIMACY ARCHITECT SIGN-OFF` block is present at the end of the final output file. When the phase does not run, the ledger row reads `SKIPPED` with the reason in the anchor cell — never silently absent.

---

## STAGE EXIT

1. Verify the Phase 2 (and, when in scope, Phase 2.5) artifact gates above by inventorying `Drafts/` — read the files; conversation memory does not count.
2. If a Python runtime is available: `python tools/validate_pipeline_state.py <project folder>` (read-only). Resolve any reported mismatch before proceeding.
3. Hand back to the router → dispatch Stage 3 (`workflows/world-forge-validation.md`).
