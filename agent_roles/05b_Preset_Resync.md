# PRESET RESYNC MODE (companion to The Prompt Engineer)

*Companion to `agent_roles/05_The_Prompt_Engineer.md` (Phase 5). Split out so Build mode — the dominant path — never carries the resync procedure in context.*

> **Who loads this file, and when:** the Prompt Engineer, **only** when invoked via `/worldforge resync-preset` on an already-shipped world. Build mode (`/worldforge start`, `/worldforge resume phase5`) and the revise pipeline never load it. When you do load it, also keep `05_The_Prompt_Engineer.md` open: the foundational hard-fail rules at the top of that file and its Section 5f Pass 1 + Pass 2 self-validation still govern whatever preset you write, and §5/§5a remain your authoring references. The block library (`agent_roles/05a_Block_Library.md`) and `templates/Chat_Completion_Preset_template.json` are your other inputs, exactly as in Workstream B.

---

## PRESET RESYNC MODE (maintenance entry — upgrade a shipped world's preset)

This mode runs when you are invoked via `/worldforge resync-preset`. The world has already shipped: `Export/` exists and contains `[WorldName]_ChatPreset.json`. The preset may have fallen behind in two independent ways since it was authored: the **pipeline's preset spec** has evolved (a reframed block, a new block type), and/or the **world's content** has changed through the revision pipeline (a revised or added arc, a new character) in ways the revise mini-Prompt-Engineer does not write into the preset (it only toggles Multi-Character Dynamics, NSFW, and the ACTIVE-SPEAKER RULE). Your job is to bring this one file current on both — and nothing else.

**This is not Build mode and not `resume phase5`.** You do not re-audit lorebooks or cards. You do not produce or update `Prompt_Engineer_Audit.md`. You do not emit Section 7/8 recommendations. You touch exactly two files: you rewrite `Export/[WorldName]_ChatPreset.json` in place, and you write `Export/Preset_Resync_Report.md`.

### 1 — Preconditions

Halt and report the specific gap if any fails:
- `Export/[WorldName]_ChatPreset.json` exists (the world has been built and a preset authored).
- `templates/Chat_Completion_Preset_template.json` exists (your structural reference for current spec).
- `Drafts/Master_Design.md` exists (source for the Block Selection Rationale and `<style_contract>` parameters).

### 2 — Inputs

- `Export/[WorldName]_ChatPreset.json` — the existing preset (what you are upgrading).
- `templates/Chat_Completion_Preset_template.json` — current canonical structure and core-block placeholder/canonical content.
- `agent_roles/05a_Block_Library.md` (Sections 5a + 5a-detail) — current block library and per-block content requirements.
- `Drafts/Master_Design.md` — the **post-revision source of truth**. If the world was changed through the revision pipeline, the mini-Refiner has merged those deltas into its canonical sections (and inline `<!-- REVISED IN R[N] -->` / `<!-- CREATED IN R[N] -->` markers flag the change sites). You re-derive all world-specific block content from this file, plus it drives the Block Selection Rationale (`05_The_Prompt_Engineer.md` Section 5.0b) and the `<style_contract>` enums (Section 11a/c).
- `Notes_On_functionality.md` — runtime reference, as in Build mode.

### 3 — Process

**Step 1 — Load and parse.** Load the existing preset, the current template, and Master Design. Build a map of the existing preset's blocks (identifier → content, enabled flag, position in `prompt_order`) and its top-level field set.

**Step 2 — Re-derive and diff.** `Drafts/Master_Design.md` is the post-revision source of truth. For each block, determine its current correct content, then diff against the existing preset on these axes:

- **Block content (spec + world-content sync).** For each core block and each present optional block, re-derive its correct content from BOTH the current 5a-detail requirement (framing/spec) AND the current Master Design (world facts: arc names, characters, CHARACTER_STATE, heights, sensory anchors, the multi-character lattice). **Never copy a block's world content forward from the existing preset — derive it from Master Design.** This is what makes resync pick up revision-pipeline content changes the revise mini-PE never writes into the preset. A block whose re-derived content substantively differs from the existing content is **CHANGED** (record the cause: spec reframe, revised world content, or both); a block whose re-derived content is semantically equivalent to the existing content is **UNCHANGED** — preserve the existing content verbatim to avoid cosmetic churn.
- **Newly-warranted optional blocks.** Re-run the Section 5.0b Block Selection Rationale against the current Master Design. Any optional block the rationale now warrants but the preset lacks is **ADDED** (e.g., Opening Variation, Perception Boundary, or — for a world now in or converted to sandbox mode — NPC Ensemble & Enrichment). An optional block already present is evaluated under "Block content" above. An optional block neither present nor warranted is **SKIPPED** — do not add speculative blocks. *(Note: the Section 5.0b sandbox-mode block guidance applies here too — resyncing a sandbox world should surface `npc_ensemble` and the sandbox Sensory Embodiment weighting if the live preset predates them.)*
- **Template field drift.** Compare top-level fields. You may adopt a template field change ONLY when a foundational hard-fail rule requires it (e.g., `forbid_overrides: false` on `main`/`jailbreak`). You do NOT overwrite the user's sampling parameters, format strings, or provider fields — those are the user's customizations and survive resync untouched.

**Step 3 — Regenerate in place.** Apply the diff under these preservation rules (load-bearing):

- **Preserve block structure, including revision-applied toggles.** Every block retains its identifier, enabled flag, and position in `prompt_order`. Resync changes block *content*, never block identity, order, or enabled state. In particular, blocks the revision pipeline toggled on (Multi-Character Dynamics, NSFW) and the current ACTIVE-SPEAKER RULE state stay exactly as the live preset has them.
- **Write CHANGED blocks; preserve UNCHANGED blocks verbatim.** For a CHANGED block, write the re-derived content (current framing + current world facts). For an UNCHANGED block, keep the existing content byte-for-byte — do not rewrite for cosmetic reasons.
- **Derive world content from Master Design, not the old preset.** When re-deriving any block, pull arc names, character names, CHARACTER_STATE references, heights, the multi-character lattice, and sensory anchors from the current Master Design — never forward-copy them from the stale preset.
- **Insert ADDED blocks without disturbing existing ones.** Append new optional blocks to the `prompts` array and add them to `prompt_order` in a sensible position; do not shift the relative order of existing blocks.
- **Never delete a block; leave disabled blocks disabled.** A disabled block's content is left as-is (matches Build mode handling of disabled conditional blocks). Resync only changes content, adds blocks, or leaves blocks alone.
- **Preserve user field-level customizations.** Keep every top-level field as the existing preset has it, except the minimal set Step 2 flagged as hard-fail-required.
- **Flag hand-customized content.** If a CHANGED block's existing content appears hand-edited beyond the pipeline's canonical form, still write the re-derived content, but call it out in the report ("prior content may have been hand-customized; review against git") so the user can reconcile. Do not silently discard authorial edits without surfacing them.

**Step 4 — Validate.** Run the `05_The_Prompt_Engineer.md` Section 5f Pass 1 (structural) + Pass 2 (content) self-validation on the regenerated preset, and confirm the foundational hard-fail rules at the top of that document. Do not write the file if any check fails — diagnose and fix first.

**Step 5 — Report.** Write `Export/Preset_Resync_Report.md` (Report format below). If Step 2 found no drift on any axis, do not rewrite the preset; write a report whose status is "ALREADY CURRENT — no changes."

### 4 — Report format

`Export/Preset_Resync_Report.md`:

```
# PRESET RESYNC REPORT — [WorldName]

**Resynced against:** templates/Chat_Completion_Preset_template.json + block library (agent_roles/05a_Block_Library.md) + Drafts/Master_Design.md, [date]
**Preset file:** Export/[WorldName]_ChatPreset.json

## Block changes

| Block (identifier) | Status | Cause | Change (before → after) |
|---|---|---|---|
| jailbreak | CHANGED | spec reframe | ethics-exception boilerplate → constitutive-fictional metaverse frame |
| deep_think | CHANGED | spec reframe + revised content | numbered procedure → considerations checklist; now names Arc 5 (created in R3) |
| arc_guardian | CHANGED | revised content | added behavioral rules for Arc 5 (created in R3) |
| opening_variation | ADDED | newly warranted | warranted by failure mode: [name] |
| main | UNCHANGED | — | — |
| ... | ... | ... | ... |

## Template field changes adopted
- [field]: [old] → [new] — required by foundational rule [N]
- (or: none)

## Blocks flagged for user review
- [identifier] — prior content may have been hand-customized; compare against git history.
- (or: none)

## Validation
- Pass 1 (structural): [PASS/FAIL]
- Pass 2 (content): [PASS/FAIL]
- Foundational hard-fail rules: [PASS/FAIL]

## Status
[Status line — see Completion status below]
```

### 5 — Completion status

- No drift found → `Status: ALREADY CURRENT — preset matches the current pipeline spec and world content. No changes written.`
- Changes found and resynced → `Status: RESYNC COMPLETE — preset synced to current spec + world content. [N] blocks changed, [M] blocks added. Re-import [WorldName]_ChatPreset.json in SillyTavern (API settings → Chat Completion presets).`
- Validation failed → do not write the preset; report the failing checks and halt.

### ✅ PRESET RESYNC SIGN-OFF

Append to `Export/Preset_Resync_Report.md`:

```
---
## ✅ PRESET RESYNC SIGN-OFF

- [ ] Scope respected: only Export/[WorldName]_ChatPreset.json and Export/Preset_Resync_Report.md written; no lorebook/card audit run; no Section 7/8 recommendations emitted
- [ ] Block content re-derived from the current (post-revision) Master Design, not copied forward from the existing preset
- [ ] Diff run on all axes (per-block content sync, newly-warranted optional blocks, template field drift)
- [ ] Every block retains its identifier, enabled flag, and prompt_order position — including revision-applied toggles (Multi-Character Dynamics, NSFW, ACTIVE-SPEAKER RULE)
- [ ] CHANGED blocks carry current framing AND current world facts (arc names, characters, heights, lattice); UNCHANGED blocks preserved verbatim
- [ ] ADDED blocks present in both prompts and prompt_order; existing block order undisturbed
- [ ] No block deleted; disabled blocks left disabled
- [ ] User field-level customizations preserved; only hard-fail-required top-level fields changed
- [ ] Hand-customized content (if any) flagged for review, not silently discarded
- [ ] Section 5f Pass 1 + Pass 2 and foundational hard-fail rules pass on the regenerated preset
- [ ] Resync report written with block-change table (status + cause) and accurate status line
```
