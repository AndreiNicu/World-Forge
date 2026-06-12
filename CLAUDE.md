# CLAUDE.md

> Standing context for AI coding agents (Claude Code, Antigravity, similar) working on this repository. This file is read first on every session start. It tells you what this project is, what the load-bearing architectural decisions are, and what rules govern safe modification of the pipeline files.

---

## What this repository is

World Forge is a **multi-agent pipeline for building immersive roleplay worlds for SillyTavern**. It is not application code in the traditional sense — it is a curated collection of agent specifications (markdown), templates (markdown and JSON), and orchestration logic (markdown) that together define a structured creative writing pipeline.

The pipeline is designed to run inside an agentic VS Code extension (typically Kilo Code; the formerly-recommended Roo Code was retired May 15, 2026). When invoked, it walks a user from a raw idea through 5+ phases of structured drafting and validation, producing a complete SillyTavern-ready world package.

**The repository is the pipeline itself.** Editing files here changes how the pipeline behaves on its next run. There is no compilation step, no test suite, no deployment — files are read directly by the runtime agent.

---

## What this repository is NOT

- **Not a SillyTavern fork or extension.** SillyTavern is the runtime environment that consumes the pipeline's outputs. This repo produces files for SillyTavern; it does not modify SillyTavern itself.
- **Not a runtime engine.** The pipeline does not execute — it is consumed by an agentic IDE extension (Kilo Code) that orchestrates LLM calls. Do not add execution logic, build steps, or deployment configuration.
- **Not a code project.** The "code" here is markdown agent specifications. Treat them as you would treat carefully-versioned prose documents, not as source code.
- **Not for editing during pipeline runs.** When a user is actively running `/worldforge start`, the pipeline files are being read by the runtime agent. Editing them mid-run produces undefined behavior.

---

## Repository structure (authoritative)

```
World-Forge/
├── README.md                         ← Human-facing project description
├── tutorial.md                       ← Usage tutorial
├── AGENTS.md                         ← Standing instructions for agentic tools (Kilo/Cline); routes run-vs-maintenance sessions
├── Notes_On_functionality.md         ← Authoritative reference: how SillyTavern works internally
├── Notes_Quick_Reference.md          ← DERIVED ~5KB distillation of Notes (position enum, flags, assembly); agents consult it first
├── LICENSE
├── .gitignore
├── .kilocodeignore                   ← Keeps Samples/ + maintenance docs out of runtime agent context
├── .kilo/
│   └── kilo.jsonc                    ← Preconfigured Kilo Code per-phase agents (OpenRouter DeepSeek flavor; auto-loaded)
├── tools/
│   └── validate_export.py            ← Read-only Export/ JSON validator (explicit exception to the no-code rule; see Out of scope)
├── agent_roles/                      ← Phase-specific agent specifications (each opens with a 📂 CONTEXT MANIFEST)
│   ├── 00_The_Interviewer.md
│   ├── 01_The_Refiner.md
│   ├── 02_The_Architect.md
│   ├── 03_The_Editor.md
│   ├── 03b_The_Voice_Auditor.md
│   ├── 03c_The_Arc_Transition_Auditor.md
│   ├── 03d_The_Intimacy_Auditor.md
│   ├── 04_The_Compiler.md
│   ├── 05_The_Prompt_Engineer.md
│   ├── 05a_Block_Library.md          ← Preset block library (split from 05; loaded only for preset authoring/resync)
│   ├── 06_The_Intimacy_Architect.md
│   ├── SHARED_Style_Contract_Reference.md
│   ├── Converter/                    ← Convert-pipeline agent (reframe a shipped world into a new build)
│   │   └── 00_The_Converter.md
│   └── revise/                       ← Revision-pipeline mini-agents (surgical post-launch edits)
│       ├── 00_The_Reviser.md
│       ├── 01_The_Refiner_mini.md
│       ├── 02_The_Architect_mini.md
│       ├── 02b_The_Intimacy_Architect_mini.md
│       ├── 03_The_Editor_mini.md
│       ├── 03b_The_Voice_Auditor_mini.md
│       ├── 03c_The_Arc_Transition_Auditor_mini.md
│       ├── 03d_The_Intimacy_Auditor_mini.md
│       ├── 04_The_Compiler_mini.md
│       └── 05_The_Prompt_Engineer_mini.md
├── templates/                        ← Structural references the pipeline produces output against
│   ├── World_Seed_Template.md        ← Phase 0 authoring guide
│   ├── Char_Card_creation.md         ← Card field-by-field authoring guide
│   ├── Lorebook_creation.md          ← Lorebook entry authoring guide
│   ├── Group_lorebook_template.md    ← Group lorebook authoring guide
│   ├── User_Persona_template.md      ← {{user}} persona description (User.md) authoring guide
│   ├── Convert_Brief_Template.md     ← Convert pipeline input (preservation matrix as a fillable brief)
│   ├── char_template.json            ← Raw V3 character-card JSON schema exemplar
│   ├── Lorebook_Template.json        ← Raw lorebook JSON schema exemplar
│   ├── Group_lorebook_template.json  ← Raw group lorebook JSON schema exemplar
│   └── Chat_Completion_Preset_template.json   ← Preset JSON structure (Prompt Engineer target)
├── workflows/                        ← Pipeline orchestration
│   ├── world-forge.md                ← Main pipeline (initial build, Phase 0–5.5; also PRESET RESYNC and CONVERT pointers)
│   ├── world-forge-revise.md         ← Revision fork (surgical post-launch edits, Phase R0–R5.5)
│   └── world-forge-convert.md        ← Convert fork (reframe a shipped world into a new build, Phase C0)
├── wiki/                             ← Setup & tooling guides (linked from README/tutorial)
│   ├── README.md                     ← Wiki index
│   ├── Agentic-Tools-and-Models.md   ← Kilo/Cline + model comparison (incl. Roo Code retirement note)
│   └── Kilo-Code-Setup.md            ← Dedicated Kilo Code setup walkthrough
└── Samples/                          ← Example world outputs for reference
```

**File authority levels:**
- **READ-ONLY for the user's project work** but writable here in the pipeline repo: all `agent_roles/`, `templates/`, `workflows/`, `tools/`, `Notes_On_functionality.md`, and `Notes_Quick_Reference.md`. These are the pipeline definition.
- **Generated at runtime** in the user's project folder (NOT in this repo): `Drafts/`, `Export/`, `World_Seed.md`, audit reports. These never appear in this repo unless they are explicit samples in `Samples/`.

---

## Core architectural principles (load-bearing — DO NOT VIOLATE without explicit instruction)

These principles took multiple iterations to converge on. Each one has a specific failure mode it prevents. Changes that violate them will produce subtle bugs that surface only at runtime in roleplay sessions.

### 1. The Three-Tier Lorebook Architecture

Every piece of world information belongs to exactly one tier:

- **Tier 1 — World Lorebook** (permanent, arc-agnostic): world rules, factions, species, mechanics, standing locations. Position 0 (Before Char Def). Never replaced or disabled.
- **Tier 2 — Character Lorebooks** (permanent, arc-agnostic, one per major character): physical description, psychological dimensions, relationships, history. Position 1 (After Char Def). Never replaced.
- **Tier 3 — Arc Lorebooks** (modular, one per arc, swapped in/out): ARC_STATE, CHARACTER_STATE, NPC_SHIFT, DRAMATIC_BEAT, TENSION, hidden information rules. Only one arc lorebook active at a time.

If you find content that would fit in multiple tiers, this is a design smell. Surface it for review — the right home is usually the most modular tier (Tier 3 if it changes per-arc, Tier 2 if it changes per-character, Tier 1 only if it's truly universal).

### 2. The Override Architecture (paired contract)

Character cards' `system_prompt` and `post_history_instructions` fields override the SillyTavern Chat Completion Preset's Main Prompt and Jailbreak blocks at runtime, UNLESS the card uses the `{{original}}` macro to splice the preset's content back in.

**Mandate:** Every character card's `system_prompt` and `post_history_instructions` MUST begin with `{{original}}` on its own line, followed by character-specific content.

**The division of labor:**
- **Preset Main Prompt** = engine-only (world-agnostic, character-agnostic): prose style, narration discipline, perspective rules, formatting rules, generic creative framework
- **Card `system_prompt`** = character-specific only: identity, behavioral mandates, prohibitions, trigger-response pairs

**Forbidden in cards (Editor will hard-fail):** narration rules, formatting rules, perspective rules, style guidelines, generic creative framework statements, generic character embodiment principles. These are engine-level and live in the preset.

**Forbidden in preset Main Prompt (Prompt Engineer Pass 1 will hard-fail):** character names, arc names, faction names, location names, character-specific psychology language. These are character/world-specific and live in cards/lorebooks.

If you find yourself moving content between cards and preset, verify which side of the contract it belongs on first.

### 3. Audit-vs-Apply Separation

The Editor (Phase 3), Voice Auditor (3.5), Arc Transition Auditor (3.6), Intimacy Auditor (3.7), and Prompt Engineer (5) are **read-only on draft and export files**. They produce critique reports, audit reports, and recommendations — they do not modify the files they audit.

The Architect (Phase 2) and Intimacy Architect (Phase 2.5) are the **only agents with write authority on drafts**. The Compiler (Phase 4) is the only agent with write authority on `Export/` JSON files — with one narrow, post-launch exception: the Prompt Engineer gains write authority on the single `Export/[WorldName]_ChatPreset.json` file (and only that file) under Preset Resync Mode, and the mini-Prompt-Engineer may toggle three preset blocks under the revise pipeline. See principle #8. Both exceptions are preset-only; neither touches lorebook or card JSON.

The Prompt Engineer's audit recommendations (Sections 7 and 8 of `Prompt_Engineer_Audit.md`) require **manual user application** — see Phase 5.5 in `workflows/world-forge.md`. This is intentional: it preserves audit reviewability and prevents self-validating corrections.

When modifying any agent spec, do not change its read/write authority without explicit instruction. The asymmetry is load-bearing.

### 4. Position Rationale Requirement

Every lorebook entry produced by the pipeline must include a `Position Rationale:` field. Default positions (per tier and entry type, documented in `agent_roles/02_The_Architect.md` Section 6) get the literal value "DEFAULT". Non-default positions require a one-sentence justification referencing `Notes_On_functionality.md` and explaining why the default fails.

The Editor (Step 4.5) hard-fails entries with missing or shallow rationales. When editing entry templates, preserve the Position Rationale field.

### 5. ARC_STATE Two-Subsection Structure

ARC_STATE entries (one per arc, fires constantly during the active arc) MUST contain two clearly-labeled subsections:

- `**Dramatic Situation:**` — descriptive scene-setting, world-fact register
- `**Tonal Mandate (binding behavioral directive — applies to every response in this arc):**` — directive bullets using imperative language (resist, dominates, never default to, dwells on, elides, do not, must, never, always)

The Tonal Mandate must contain 4-8 bullets covering active register, prose dwells on, prose elides, live scene types, activity cadence (when the arc has active principal NPCs), and hard prohibitions (where relevant). The Editor (Step 4a) hard-fails entries missing the structure or with insufficient directive language. The **activity cadence** directive (Editor Step 4a-3b) is what mechanizes NPC agency: principal NPCs have a Tier 2 §7.D **Standing Goal** (an active objective + pursuit moves), and the cadence directive instructs the model to have a present or off-screen NPC advance its goal when a scene lulls rather than freezing to wait on `{{user}}`. The Voice Auditor's Step 3J tests that NPCs actually take that initiative and that their moves trace to a stated goal. This is the arc-mode counterpart of the sandbox aliveness contract (#9); the generic engine half lives preset-side in the `npc_ensemble` block, the world-specific goals in Tier 3.

This structure exists because un-split ARC_STATE entries get interpreted as world-description rather than as binding directives, causing the model to default to its own tonal disposition rather than the arc's specified register.

### 6. Revision Pipeline (Post-Launch Surgical Edits)

Once a world has shipped (Phase 5.5 complete), surgical changes use the **revision pipeline** in `workflows/world-forge-revise.md` — a parallel fork running mini-agents under `agent_roles/revise/`. The minis are smaller, scope-locked counterparts of their initial-build parents.

**The bright line:** any revision that requires changes to Master Design Section 1 (Core Concept & Tone) or Section 11a (Style Contract world defaults) is **out of scope for the revision pipeline**. The Reviser (Phase R0) classifies and bounces these to a full pipeline re-run via `/worldforge skip phase0`, reusing the existing `World_Seed.md`. Per-card overrides in Section 11b stay in revision scope; only world-default changes bounce. **`World Mode` (arc | sandbox) lives in Section 1, so flipping it is a bright-line bounce** — the revise pipeline edits a world *within* its mode; converting arc↔sandbox is a full rebuild. When a world's *accumulated* revisions outgrow surgical editing (markers everywhere, seed badly stale, structural changes coming), the consolidation path is the Convert pipeline's **Rebaseline mode** (#10), not another revision.

**Sandbox-aware.** The revise pipeline handles `World Mode: sandbox` worlds through the same minis. The Reviser reads `World Mode` and uses three `sandbox_*` scope types (`sandbox_state_recalibration`, `sandbox_entry_modify`, `sandbox_entry_add`) in place of the `tier3_arc_*` types; the NPC and intimacy scopes are mode-aware (principal/roster NPCs, the single standing `Sandbox_Intimacy_Register`). The Arc Transition Auditor (R3.6) never fires on a sandbox world. Because every parent agent is already sandbox-aware (#9), the minis inherit it — they document only thin sandbox deltas.

**Load-bearing properties of the revise pipeline:**
- **Cascade scope.** Mini-agents touch only files listed in the Revision Log entry's confirmed cascade. Silent scope expansion is forbidden — cross-references the user did not flag are surfaced for confirmation, not silently widened.
- **UID preservation.** The mini-Compiler reads existing Export/ JSON before rewriting, preserves UIDs on unchanged entries, assigns next-free UIDs to new entries, and never deletes unless cascade explicitly says so. This keeps running SillyTavern chat states viable across revisions.
- **Inline revision markers.** Every change site in Master_Design.md and Drafts/ gets a `<!-- REVISED IN R[N] -->` or `<!-- CREATED IN R[N] -->` marker. These are the canonical audit trail at the change site; the per-revision report in `Drafts/Revision_R[N]_Report.md` is the durable detail. On the Export/ side, where filenames can't be renamed and JSON can't carry extra fields, the mini-Compiler maintains `Export/REVISED_FILES.md` — a cumulative manifest of every export file ever touched by a revision (file, latest revision, date, summary). It is the sole revision marker on the Export side.
- **Audit/apply separation preserved.** The mini-Editor and mini-auditors are read-only on drafts; the mini-Prompt-Engineer is read-only on Export/ JSON except for the Chat Completion Preset, which it may modify only under narrow triggers (Multi-Character Dynamics block toggle, NSFW block toggle, Style Contract ACTIVE-SPEAKER RULE toggle).
- **Single revision at a time.** A revise invocation captures one logical concern. Multiple unrelated changes run as separate sequential revisions; overlapping PENDING entries are forbidden.

When editing any `agent_roles/revise/*` file, the parent agent's foundational rules still apply — the mini documents only the deltas. Cross-reference the parent before adding rules that should already inherit.

### 7. Notes_On_functionality.md is the SillyTavern source of truth

This file is the authoritative reference for SillyTavern's runtime behavior — prompt assembly, world info scanning, position values, lorebook flag effects, group chat field combination. When editing pipeline files, if you need to reference SillyTavern behavior, consult this file. If a position value, flag effect, or runtime mechanic appears to be wrong in this file, verify against the official SillyTavern source (https://github.com/SillyTavern/SillyTavern) before editing — this file has been corrected before for outdated content, and getting it right matters because every agent consults it.

**Authoritative position enum (line ~661 of Notes_On_functionality.md):**
- 0: before (Before Char)
- 1: after (After Char)
- 2: ANTop (Author's Note Top)
- 3: ANBottom (Author's Note Bottom)
- 4: atDepth
- 5: EMTop (Example Messages Top — prepended to dialogueExamples)
- 6: EMBottom (Example Messages Bottom — appended to dialogueExamples)
- 7: outlet

### 8. Preset Resync (Post-Launch Preset Refresh)

There are three distinct operating modes, not two: the **initial build** (`/worldforge start`, Phases 0–5.5), the **revision pipeline** (`/worldforge revise`, principle #6), and **preset resync** (`/worldforge resync-preset`). Resync exists because a shipped world's `Export/[WorldName]_ChatPreset.json` can fall behind in two independent ways: the pipeline's preset spec evolves (a reframed core block, a new optional block, a changed template flag), and/or the world's content changes through the revise pipeline in ways that surface inside preset blocks (Deep Think names the arcs, the multi-character lattice names characters) but that the revise mini-Prompt-Engineer never writes.

It invokes the Prompt Engineer in **Preset Resync Mode** (`agent_roles/05_The_Prompt_Engineer.md` Section 8). The agent re-derives each block's content from the current `templates/Chat_Completion_Preset_template.json` + block library (`agent_roles/05a_Block_Library.md`) + the post-revision `Drafts/Master_Design.md`; writes only the blocks whose content has drifted and adds newly-warranted optional blocks; **preserves** block identifiers, `prompt_order`, revision-applied toggles, and the user's field-level customizations; re-runs the Section 5f Pass 1 + Pass 2 self-validation; and writes `Export/Preset_Resync_Report.md`.

**Load-bearing properties:**
- **Preset-only write authority.** This is the one place the Prompt Engineer writes to `Export/` (see principle #3). It touches the Chat Completion Preset and nothing else — no lorebook or card JSON.
- **Makes no content changes.** Resync reflects already-applied content and spec changes into the preset. The revise pipeline *makes* surgical content changes; resync makes none. A world can be resynced without ever entering revise, and revised worlds can be resynced afterward.
- **Distinct from `resume phase5`.** `resume phase5` re-runs the full Phase-5 audit during an in-progress build; resync is a maintenance op on an already-shipped world that only refreshes the preset.
- **Low risk.** A Chat Completion Preset is a global SillyTavern settings profile, not UID-bearing world info, so re-importing a resynced preset does not disturb running chat states. Git is the rollback path.

See the **PRESET RESYNC** section of `workflows/world-forge.md` for the full operation.

### 9. World Mode: Arc vs. Sandbox

A world is built in one of two **modes**, declared in World Seed Section 1 (`World Mode: arc | sandbox`) and recorded by the Refiner. `arc` is the default and the legacy behavior — every existing world is an arc world, and nothing about arc worlds changes. `sandbox` exists for worlds that have **no narrative arc**: open-ended power-fantasy / world-director / life-sim worlds where the experience is anchored by a standing world-state rather than a progression of arcs with entry/exit triggers and dramatic beats.

The mode is a branch *through* the existing pipeline, **not a parallel fork.** The same Interviewer, Refiner, Architect, Editor, Voice Auditor, Compiler, and Prompt Engineer run; sandbox mode swaps the Tier 3 spine and the large-cast NPC format. `/worldforge start --sandbox` is a convenience that pre-sets the Interviewer; the World Seed field is the source of truth (so a hand-written seed or a `skip phase0` run carries the signal).

**What sandbox mode changes (load-bearing):**
- **Tier 3 becomes one always-active Sandbox lorebook**, not *N* swappable arc lorebooks. It contains a `SANDBOX_STATE` entry (the `ARC_STATE` analog — same constant / `ignoreBudget` / position-1 mechanics and the same mandatory two-subsection structure from principle #5, with `**Standing Situation:**` replacing `**Dramatic Situation:**`) and at least one `WORLD_PULSE` entry (the `TENSION` analog at position 4 — a sustained "the world is alive and reactive" directive rather than a stakes countdown). Standing `LOCATION` entries as needed. There are no `CHARACTER_STATE`, `NPC_SHIFT`, `DRAMATIC_BEAT`, or arc-trigger entries, because there is no arc.
- **The SANDBOX_STATE Tonal Mandate carries the aliveness contract**: NPCs pursue their own agendas, initiate scenes, and carry off-screen continuity; the world reacts to and remembers `{{user}}`'s actions; it never freezes waiting for `{{user}}`. This is what anchors tone when no arc is carrying it. The contract is made concrete by per-NPC **Standing Goals** (Architect §7.D): each principal NPC carries an active objective + pursuit moves, and the aliveness directive instructs the model to have an NPC advance its goal when a scene lulls. The Voice Auditor's Step 3J tests this (initiative + goal-trace) in both modes. The same mechanic runs in arc mode via the ARC_STATE activity-cadence directive (#5) — it is mode-agnostic because NPCs exist in both modes.
- **Large casts use a two-tier NPC model** (Architect §7): a few **principal NPCs** keep the full §7.D profile; the rest are **roster NPCs** authored as a compact, fixed-schema stat block engineered for differentiation at scale. The binding rule: every roster NPC's **voice fingerprint must be unique across the roster.** This is the structural defense against the homogenization that swallows large NPC casts in sandbox play.
- **The Voice Auditor adds a distinctiveness lens** (sandbox-only Step 3I): a blind-line test across the roster that flags any two NPCs whose voices could be swapped. The arc-register checks reframe to "standing register vs. `SANDBOX_STATE`."
- **Phase 3.6 (Arc Transition Auditor) is skipped** in sandbox mode — there are no arc seams to audit, exactly as Phase 3.7 is skipped without intimacy. Cross-arc consistency qualifiers and the ≥8-entries-per-arc floor do not apply.
- **The Prompt Engineer defaults sandbox presets** to enabling Multi-Character Dynamics, including the optional **NPC Ensemble & Enrichment** block (`npc_ensemble`: NPC-to-NPC dialogue, ensemble prose scaling, and organic NPC enrichment within guardrails — the NPC-roster analogue of the `enhanceDefinitions` enhancer), and weighting Sensory Embodiment high. These are runtime engine directives in the preset, so they live on the preset side of the override contract (#2) — never in cards.

**Boundaries:** Sandbox mode does not touch SillyTavern, the override architecture (#2), audit/apply separation (#3), Position Rationale (#4), or the preset contract — it only repoints what Tier 3 contains and how a large NPC cast is authored. Intimacy (Section 8) stays orthogonal but is mode- and cast-aware: a sandbox world folds its `INTIMACY_FUNCTION` register into a single standing `Sandbox_Intimacy_Register` (no per-arc registers), and **NPC intimacy follows the principal/roster split** — principal NPCs get full Tier 2 Intimacy Profiles, roster NPCs get compact §6.5 intimate stat blocks with the same uniqueness rule (no two NPCs interchangeable in an intimate scene). The Intimacy Auditor checks NPC intimate coverage and distinctiveness (Step 3H). The **revise pipeline is sandbox-aware** (see #6): sandbox worlds are revised through the same minis using the `sandbox_*` scope types, with R3.6 never firing. *Flipping* a world between arc and sandbox is a Section 1 `World Mode` change and bounces out of the revise pipeline — but this is one of the canonical cases the **Convert pipeline** (#10) is built for, alongside protagonist swaps and Style Contract changes.

See the **SANDBOX MODE** section of `workflows/world-forge.md` for the full operation.

### 10. Convert Pipeline (Reframe + Rebaseline)

There is a fourth operating mode alongside initial-build / revise / preset-resync: **`/worldforge convert`** (`workflows/world-forge-convert.md`). It reframes a shipped world into a new build with a different protagonist, World Mode, Core Concept, or Style Contract world defaults — exactly the change-categories principle #6 explicitly bounces out of revise. The Converter (`agent_roles/Converter/00_The_Converter.md`) is a single phase (C0): it reads the source's `Master_Design.md` (read-only), captures the user's keep/modify/regenerate decisions per source section (interview or pre-authored Convert Brief), and writes a new `World_Seed.md` to a target project folder. The user then runs `/worldforge skip phase0` against the target; the standard pipeline (Phases 1–5.5) builds the new world end-to-end.

The Converter has two operating modes. **Reframe** (default) is the above — something structural changes. **Rebaseline** (`--rebaseline`; Converter spec Section 9) is the zero-axes-replaced conversion: same world, same protagonist, rebuilt clean from its *post-revision* Master Design — the consolidation path for a world whose accumulated revisions (#6) have outgrown surgical editing, optionally folding in new mechanics at seed level. Rebaseline inverts the always-regenerate rules below (their premise — a changed protagonist — is absent): Sections 3 / 5 / 7b, intimate functions, per-card overrides, relationship-to-`{{user}}` content, and the four Section 4 strip rules all flip to keep/carry, distilled at seed grade. Revision content carries; `<!-- REVISED IN R[N] -->` markers do not (provenance moves to `<!-- REBASELINED FROM ... -->` comments + a manifest high-water mark). `Drafts/Revision_R*.md` + `Export/REVISED_FILES.md` become required reading with a source-integrity check (every reported revision must be visible in the Master Design — halt on drift). The honest cost is stated explicitly: the rebuild compiles **fresh UIDs, so running SillyTavern chats do not migrate** — revise preserves UIDs precisely to avoid this; rebaseline trades it for cleanliness. When the consolidation is a staging step for bigger changes, **`--then-interview`** (Converter Section 9 Step H) chains the hand-off into Phase 0 instead of `skip phase0`: the Interviewer's **seed-revision posture** (`agent_roles/00_The_Interviewer.md` Section 9) interviews only the user's changes against the consolidated seed — full Phase 0 depth on the delta, cascade re-elicited on coupled fields, untouched sections left alone — then signs off and hands to Phase 1 as normal.

**Load-bearing properties:**
- **Read-only on the source project.** The Converter never modifies any file in the source folder. Period.
- **Write-only on the target's `World_Seed.md`.** Does not write `Drafts/`, `Export/`, `Master_Design.md`, or any other target file. The standard pipeline produces those. Convert is upstream of the standard pipeline, not parallel to it — no downstream agent needs special handling for a converted world; the new seed and Master Design are first-class Phase 0/1 outputs.
- **Overlap floor refusal (the reskin refusal).** If the conversion replaces three or four of (setting, protagonist, factions, tone), the Converter refuses with an explicit bounce to `/worldforge start`. Borderline (two replaced) gets surfaced for explicit user confirmation. **Pure reskin is intentionally out of scope** — at three-axes-replaced, the source is creative reference, not a structural source. In Rebaseline mode the floor inverts into the **zero-axes gate**: any replaced axis reclassifies the run as a reframe conversion (announced, not refused).
- **Always-regenerated content (reframe mode).** Section 3 (`{{user}}`), Section 5 (arcs / Sandbox Charter), Section 7b (test scenarios), per-arc / standing intimate functions, and per-card style overrides are always regenerated downstream — they are protagonist-shaped or downstream-derived. The Converter does not let the user mark them `keep` — except in Rebaseline mode, where they default to keep.
- **Role reassignment surfacing.** Five canonical cases (old protagonist → NPC; source NPC → new protagonist; power-tier shift on `{{user}}`; character dropped; role shift not involving the protagonist) are surfaced explicitly to the user and confirmed before the seed is written. Source content carries forward where it can; relationship-to-`{{user}}` content is always reauthored downstream and gets a marker comment in the seed.
- **Single source.** No mashups. The Converter accepts exactly one source world per conversion.
- **Conversion Manifest at top of seed.** Records source, intent (verbatim), overlap floor classification, per-section preservation decisions, role reassignments, and cross-references the user should be aware of. The Refiner reads this at Phase 1 to route accordingly.

**Boundaries:** Convert does not touch SillyTavern, the override architecture (#2), audit/apply separation (#3), Position Rationale (#4), or any other architectural principle. It is purely an upstream seed-production operation. It is *the* legitimate path for the change-categories revise bounces (Section 1, Section 11a, World Mode flips), preserving structural world-building that `/worldforge start` from scratch would discard.

See the **CONVERT** section of `workflows/world-forge.md` and the full operation in `workflows/world-forge-convert.md`.

---

## Cross-file consistency requirements

These pairs of files must stay in sync. When editing one, check the other.

| If you edit | Also check |
|---|---|
| `agent_roles/02_The_Architect.md` (entry templates) | `agent_roles/03_The_Editor.md` (validation rules) — they validate what the Architect produces |
| `agent_roles/02_The_Architect.md` (card structure) | `templates/Char_Card_creation.md` — both define card field requirements |
| `agent_roles/02_The_Architect.md` / `agent_roles/03_The_Editor.md` (User.md persona) | `templates/User_Persona_template.md` — both define the `{{user}}` persona-description structure |
| `agent_roles/05a_Block_Library.md` (block library, split from 05) | `agent_roles/05_The_Prompt_Engineer.md` (Sections 5b–5f reference §5a/§5a-detail; Resync Mode re-derives from it) and `templates/Chat_Completion_Preset_template.json` — agent must produce against template structure |
| `Notes_On_functionality.md` (any correction or content change) | `Notes_Quick_Reference.md` — it is a DERIVED distillation (position enum, flags, assembly order, gotchas); regenerate the affected fact, never let the two disagree |
| `agent_roles/04_The_Compiler.md` (pre-save guards) | `tools/validate_export.py` — the validator deterministically re-checks the same failure modes (UTF-8/mojibake, parse, `{{original}}`, position enum, UID uniqueness, entry-key/UID parity, snake_case alias fields); changing a guard may require updating the script and vice versa |
| Any agent spec's INPUT section | The same spec's `📂 CONTEXT MANIFEST` block at the top — the manifest is the load-discipline restatement of the inputs; they must list the same files |
| `agent_roles/05_The_Prompt_Engineer.md` Section 8 (Preset Resync Mode) | `workflows/world-forge.md` PRESET RESYNC section — both define the `/worldforge resync-preset` operation |
| `Notes_On_functionality.md` (position table) | All agent files referencing positions — they cite this table |
| Any agent spec (sign-off block) | `workflows/world-forge.md` (phase descriptions) — phase outputs feed handoffs |
| `agent_roles/06_The_Intimacy_Architect.md` | `agent_roles/03d_The_Intimacy_Auditor.md` — auditor validates what architect produces |
| Any parent agent in `agent_roles/*.md` | Its mini counterpart in `agent_roles/revise/*_mini.md` — the mini inherits parent's foundational rules, so changing the parent may require updating the mini's delta list |
| `workflows/world-forge-revise.md` (routing matrix) | `agent_roles/revise/00_The_Reviser.md` (scope types) — both must enumerate the same fourteen scope types (incl. the three `sandbox_*` types) |
| `agent_roles/02_The_Architect.md` (sandbox lorebook + Roster NPC §7.E) | `agent_roles/03_The_Editor.md` (sandbox validation) and `agent_roles/03b_The_Voice_Auditor.md` (distinctiveness lens) — Editor validates `SANDBOX_STATE`/`WORLD_PULSE`/roster format; Voice Auditor tests roster fingerprint uniqueness |
| NPC agency: Architect §7.D principal **Standing Goal** + ARC_STATE/SANDBOX_STATE **activity cadence** directive | `agent_roles/03_The_Editor.md` (Step 4a-3b cadence + goal-coverage hard checks), `agent_roles/03b_The_Voice_Auditor.md` (Step 3J initiative + goal-trace), `agent_roles/00_The_Interviewer.md` + `01_The_Refiner.md` (elicit/record the goal), `templates/World_Seed_Template.md` (NPC Standing Goal field) — the goal is authored once and pointed at by the cadence directive; all must stay in sync across arc and sandbox |
| Relationship/belief state: Architect CHARACTER_STATE item 6 + NPC_SHIFT relational-stance delta (arc); standing accumulation via SANDBOX_STATE aliveness (sandbox) | `agent_roles/03c_The_Arc_Transition_Auditor.md` (Check 3b — continuity teeth: no teleporting bonds, un-caused belief flips, or silent memory resets), `agent_roles/03_The_Editor.md` (relational-stance delta-integrity + coverage soft-flag), `agent_roles/00_The_Interviewer.md` + `01_The_Refiner.md` (elicit/record the drift trajectory + operative belief), `templates/World_Seed_Template.md` (§4 "How it drifts"/"Operative belief" + arc "Relationship shifts this arc") — drift is authored per-arc as delta only, and Check 3b verifies it is earned; arc-mode only (sandbox has no seam) |
| Trauma de-escalation: Architect CHARACTER_STATE item 7 (trauma trajectory delta, arc) | `agent_roles/03c_The_Arc_Transition_Auditor.md` (Check 2 trauma-response continuity — fades shown, never sudden vanishings/un-caused re-activations), `agent_roles/03b_The_Voice_Auditor.md` (Step 3A active-vs-dormant match against item 7), `agent_roles/03_The_Editor.md` (trauma-trajectory delta-integrity + coverage soft-flag), `agent_roles/00_The_Interviewer.md` + `01_The_Refiner.md` (elicit/record which trigger fades in which arc), `templates/World_Seed_Template.md` (§4 "Trauma trajectory" + arc "Trauma shifts this arc") — authored per-arc as delta; intimate-context trauma rides the per-arc Intimacy Register instead; arc-mode only (sandbox trauma is static Tier 2 substrate) |
| World Mode handling in any one of Interviewer / Refiner / Architect / Editor / Voice Auditor / Intimacy Architect / Intimacy Auditor / Compiler / Prompt Engineer | The others + `workflows/world-forge.md` SANDBOX MODE section + `templates/World_Seed_Template.md` (§1 `World Mode`, §5 conditional, §4 NPC intimacy) — the arc/sandbox branch (incl. the standing Sandbox Intimacy Register and NPC principal/roster intimacy) must read consistently end-to-end |
| `agent_roles/Converter/00_The_Converter.md` (preservation matrix, Conversion Manifest format, Section 9 Rebaseline mode) | `templates/Convert_Brief_Template.md` (Sections 4a–4h mirror the matrix row-for-row; *Rebaseline:* notes mirror the Section 9 inversions) + `workflows/world-forge-convert.md` (operating modes incl. REBASELINE MODE, overlap floor / zero-axes gate, role reassignment cases) + `templates/World_Seed_Template.md` (the seed structure the Converter writes against — section numbering, required fields, conventions) — Convert is a three-file contract; changing any one requires checking the others |
| NPC agency / relationship-belief state / trauma-trajectory machinery (Architect §7.D `Standing Goal`, World Seed §4 `How it drifts` + `Operative belief` + `Trauma trajectory`, Refiner/Architect/Editor/Voice-Auditor/Arc-Transition-Auditor rules) | `agent_roles/Converter/00_The_Converter.md` (Section 4 carry-across rules + preservation matrix) and `templates/Convert_Brief_Template.md` (Section 4e reminders) — these four Section 4 fields couple to the regenerated parts of a converted seed (Section 3 protagonist + Section 5 arcs). The Converter's carry-across rules (preserve / strip / mark-for-reauthor) must stay consistent with how the parents author the fields; if the field set changes, update the Converter's Section 4 handling at the same time |
| `agent_roles/00_The_Interviewer.md` (Section 3 protagonist questioning; Section 9 seed-revision posture) | `agent_roles/Converter/00_The_Converter.md` (Step 4 question 7 reuses the Interviewer's Section 3 depth standard; Section 9 Step H dispatches the Interviewer's seed-revision posture for `--then-interview`) — Convert authors a new protagonist with Interviewer-grade depth and chains rebaseline into the posture; if either side's contract evolves, the other inherits |

---

## Editing protocol

When making changes to pipeline files, follow this order:

1. **Read the file you're about to edit completely.** Pipeline files have load-bearing structural conventions (sign-off blocks, step numbering, sub-section headers). Don't edit blindly.
2. **Check the cross-file consistency table above.** If your change touches a paired file, plan the edit for both at once.
3. **Preserve sign-off blocks.** Each agent ends with a `## ✅ [AGENT] SIGN-OFF` block listing certification items. When adding new validation requirements, add corresponding sign-off items.
4. **Preserve step numbering.** The Editor uses step numbers like 1, 2, 3, 4, 4a, 4.5, 5, 6, 7. New steps insert with sub-numbering (e.g., 4a) rather than renumbering existing steps.
5. **For markdown documents, validate code fence balance after editing** (every ``` must have a closing ```).
6. **Keep each agent's `📂 CONTEXT MANIFEST` in sync with its INPUT section.** Every main agent spec opens with a manifest telling the runtime agent exactly what to load (small-context models depend on it). If your edit changes what an agent reads — a new input file, a new template, a section moved to another file — update the manifest in the same edit.
7. **Use git aggressively.** Commit before architectural changes. Branch for experiments. The pipeline has gotten complex enough that "what did we decide three weeks ago and why" is a real question; git history is the answer.

---

## Common failure modes to avoid

These are mistakes that have been made before and produce subtle bugs:

- **Adding engine instructions to a card template.** The override architecture forbids this. Engine instructions live in the preset Main Prompt.
- **Adding character/world specifics to the preset Main Prompt.** Same architecture, inverse direction. Specifics live in cards and lorebooks.
- **Using lorebook position values without consulting Notes_On_functionality.md.** Position 5 is EMTop (prepended), not "Before Example Messages" or "After Example Dialogue" — verify before writing.
- **Marking an entry "DEFAULT" in Position Rationale when it isn't actually using defaults.** The Editor's 4.5b check catches this; produce honest rationales.
- **Writing audit/recommendation content as if the auditor will apply it.** Auditor agents are read-only on the files they audit. Use "recommend" language consistently.
- **Conflating ARC_STATE descriptive content with directive content.** Use the two-subsection structure; don't merge them. The sandbox `SANDBOX_STATE` entry inherits the same rule (`**Standing Situation:**` descriptive, `**Tonal Mandate:**` directive).
- **Authoring a sandbox NPC roster with overlapping voice fingerprints.** At sandbox scale the failure mode is cross-NPC homogenization, not per-NPC infidelity. Every roster NPC's voice fingerprint must be distinct enough that the Voice Auditor's blind-line test (Step 3I) can tell them apart.
- **Forcing a sandbox world through arc machinery.** Don't author `CHARACTER_STATE`/`NPC_SHIFT`/`DRAMATIC_BEAT`/arc triggers for a `World Mode: sandbox` world — Tier 3 is the single Sandbox lorebook (`SANDBOX_STATE` + `WORLD_PULSE`). Conversely, don't apply the sandbox format to an arc world.
- **Keying lorebook entries by sequential position instead of by UID.** ST stores and looks up world-info entries as `entries[uid]`; an entry keyed `"1"` with `"uid": 20` imports without error and then never renders in the World Info editor (GitHub issue #31). Every entry's object key must equal `String(uid)` — Compiler Foundational Rule 9, deterministically re-checked by `tools/validate_export.py`. The same issue covered the snake_case alias fields (`case_sensitive`, `match_whole_words`, `use_regex`, `characterFilterNames`/`characterFilterExclude`) — those belong to the embedded `character_book` card format, not standalone lorebooks (Rule 10).
- **Editing `Notes_On_functionality.md` based on memory of how SillyTavern works.** Always verify against the official ST source if changing this file.
- **Adding a new pipeline phase or agent without updating `workflows/world-forge.md`.** Orchestration is the source of truth for what runs when.
- **Writing Export JSON through PowerShell (Compiler / mini-Compiler).** Windows PowerShell `Out-File` / `Set-Content` / `>` re-encode to UTF-16 / Windows-1252 and corrupt the em-dashes (—), curly quotes, and accented names that fill lorebook and card content into mojibake (`—` → `â€"`). The mangled file still passes `JSON.parse`, so the "JSON parses" guard never catches it. Write JSON as UTF-8 via the file-write tool directly or a **Python / Node** script, and after writing grep for `â€` / `Ã` (expect zero). See the Compiler's FILE-WRITING & ENCODING guard. `python tools/validate_export.py Export/` checks for exactly this corruption (plus parse, `{{original}}`, and position-enum failures) read-only — run it after every compile.

---

## Working style notes for AI agents

The project owner (Andrei) has a specific working style that produces good outcomes:

- **Decisions before implementation.** When proposing changes, present options with tradeoffs and wait for explicit approval before writing patches. Multi-file changes especially benefit from a "final scope confirmed?" gate.
- **Push back honestly.** When a proposed change would harm the architecture or solve a non-existent problem, say so directly. Several improvements to this pipeline came from agents pushing back on requests that would have introduced complexity without value.
- **Solve actual problems, not anticipated ones.** "Build one manually first, then come back if I find friction points" is the preferred pattern over speculative documentation.
- **Surface latent bugs you notice during other work.** When fixing one thing, if you notice another thing that's wrong, flag it separately rather than fixing it silently or ignoring it.
- **Verify against authoritative sources.** Memory of how SillyTavern works is unreliable; the official source and `Notes_On_functionality.md` are the references.

---

## Out of scope for this repo

Do not, without explicit instruction:

- Modify SillyTavern itself (this repo produces inputs for ST, not changes to ST)
- Add language-specific code (Python, JavaScript, etc.) — the pipeline is pure markdown/JSON. **One standing exception, explicitly approved 2026-06-10:** `tools/validate_export.py`, a stdlib-only, strictly read-only validator for Export/ JSON (UTF-8/mojibake, parse, `{{original}}`, position enum, UID uniqueness, entry-key/UID parity, snake_case alias fields). It is a deterministic backstop for the Compiler's guards, not a replacement for them. Do not extend it into anything that modifies files, and do not add further scripts without the same explicit approval.
- Add CI/CD, test frameworks, or build configuration — there is nothing to compile or deploy
- Add dependencies of any kind
- Refactor file paths or folder structure (every agent references specific paths)
- Generate world content (worlds are produced by running the pipeline against a user's World Seed; this repo defines the pipeline, not specific worlds — except for `Samples/`)
- Add automated linting that modifies files (validation logic belongs in agent specs, not as separate tooling; the read-only `tools/validate_export.py` is the one sanctioned exception precisely because it modifies nothing)

---

## Where to learn more

- **Pipeline overview:** `README.md` (human-facing) and `workflows/world-forge.md` (agent-facing orchestrator)
- **SillyTavern runtime mechanics:** `Notes_On_functionality.md`
- **Per-phase agent specs:** `agent_roles/*.md`
- **Output structural targets:** `templates/*.md` and `templates/*.json`
- **Sample world outputs:** `Samples/`