---
description: World Forge build Stage 4 — Construction (Phase 4 Compiler, Phase 5 Prompt Engineer, Phase 5.5 Manual Apply). Dispatched by workflows/world-forge.md.
---

# WORLD FORGE — STAGE 4: CONSTRUCTION
*Stage file 4 of 4 — dispatched by the router (`workflows/world-forge.md`). Not a standalone entry point.*

**Phases:** Phase 4 (the Compiler) · Phase 5 (the Prompt Engineer) · Phase 5.5 (Manual Correction Application, conditional)

**Entry conditions (read from the Pipeline State Ledger; halt if unmet):** ledger rows `3`, `3.5`, `3.6`, `3.7` are each `COMPLETE` or legitimately `SKIPPED`, with their report files and sign-off anchors verified on disk (Stage 3 exit gate). The Compiler additionally re-verifies the ledger itself before compiling (router → PIPELINE STATE LEDGER contract). Resumes (`resume phase4` / `resume phase5`) re-enter here per the checkpoint discipline's resume-from-disk rule.

**Exit conditions:** `Export/` verified (including `tools/validate_export.py` when a Python runtime is available), `Export/Prompt_Engineer_Audit.md` signed off, Phase 5.5 recommendations applied where present → ledger `status: COMPLETE` → **PIPELINE COMPLETE**.

**Governing router sections (not restated here):** PIPELINE STATE LEDGER, CHECKPOINT DISCIPLINE, DISPATCH PROTOCOL — all in `workflows/world-forge.md`. Every phase below runs by dispatching its agent; never inline.

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

**Artifact gate (Phase 4):** `Export/` populated per the build list above and `Export/Compiler_Log.md` contains `COMPILER SIGN-OFF`.

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

**Artifact gate (Phase 5):** `Export/Prompt_Engineer_Audit.md` contains `PROMPT ENGINEER SIGN-OFF` and `Export/[WorldName]_ChatPreset.json` exists and parses.

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

## STAGE EXIT (PIPELINE COMPLETE)

1. Verify the Phase 4 and Phase 5 artifact gates above on disk; confirm Phase 5.5 recommendations (if any) are applied.
2. If a Python runtime is available: `python tools/validate_export.py Export/` and `python tools/validate_pipeline_state.py <project folder>` (both read-only). Resolve any reported failure before declaring completion.
3. Set the ledger `status: COMPLETE`. The world is ready for SillyTavern import. Post-launch changes go through the operations in `workflows/world-forge-postlaunch.md` — never through re-editing `Drafts/` or `Export/` by hand.
