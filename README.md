# World-Forge

*A multi-agent pipeline for building immersive roleplay worlds for [SillyTavern](https://github.com/SillyTavern/SillyTavern).*

World-Forge takes you from a raw idea to a complete, runtime-ready world package: character cards, a tiered lorebook system, a chat completion preset, and audit reports — all aligned with how SillyTavern actually assembles prompts at runtime. The pipeline is a sequence of specialized agents, each with a defined role, that walks you through five-plus phases of structured drafting, validation, and export.

The repository **is** the pipeline. There is no application code to compile, no service to deploy, no dependencies. The agents are markdown specifications consumed at runtime by an agentic IDE extension — [Kilo Code](https://github.com/Kilo-Org/kilocode) (recommended; the repo ships a preconfigured `.kilo/kilo.jsonc`) or [Cline](https://github.com/cline/cline) — running inside VS Code. When you invoke `/worldforge start`, the orchestrator reads these specifications and dispatches each phase. See [`wiki/Agentic-Tools-and-Models.md`](./wiki/Agentic-Tools-and-Models.md) for the tool comparison, and [`wiki/Kilo-Code-Setup.md`](./wiki/Kilo-Code-Setup.md) for a dedicated Kilo Code setup walkthrough. (Roo Code, the tool the pipeline was originally authored against, was retired on May 15, 2026 — see the wiki's migration note.)

A companion SillyTavern fork — [AndreiNicu/SillyTavern](https://github.com/AndreiNicu/SillyTavern) — is maintained alongside this repository. It is optional but recommended when running World-Forge worlds at scale: it relaxes some of stock SillyTavern's constraints that World-Forge outputs would otherwise bump into (notably allowing more than one matching lorebook entry to fire in a scene, which World Director cards rely on) and ships a small `world-forge` ST extension that wires style-override runtime support. See [Companion SillyTavern fork](#companion-sillytavern-fork-optional) below.

## What this is NOT

- **Not a SillyTavern fork.** SillyTavern is the runtime that consumes World-Forge's outputs. World-Forge does not modify SillyTavern.
- **Not a runtime engine.** The pipeline does not execute on its own — it is consumed by an agentic IDE extension that orchestrates LLM calls.
- **Not application code.** Editing files here is editing markdown specs, not source code. There is nothing to build or deploy.

## What it produces

A complete SillyTavern-ready package per world:

- **One Character Card per AI-played character** (V3 spec JSON) — psychology, voice, and behavioral mandates wired against the override architecture, with optional `depth_prompt` for mid-context reinforcement.
- **One World Lorebook (Tier 1)** — permanent arc-agnostic world truths: rules, factions, locations, species, concepts.
- **One Character Lorebook per character (Tier 2)** — permanent reference data: physical baseline, psychological dimensions, relationships.
- **One Protagonist Lorebook (Tier 2)** — `{{user}}` identity reference, linked to your active SillyTavern Persona after import.
- **One `User.md` Persona Description** — paste-ready text block for SillyTavern's Persona Description field. Pairs with the Protagonist Lorebook to give `{{user}}` parity with `{{char}}` despite ST's missing persona import format. Voice and personality intentionally excluded — the human plays `{{user}}`.
- **One Intimacy Profile per character with intimate scenes (Tier 2, conditional)** — permanent intimate substrate.
- **Tier 3, by World Mode:** *arc worlds* get **one Arc Lorebook per arc** — modular and swap-in: ARC_STATE, CHARACTER_STATE, NPC behavioral shifts, dramatic beats, tension entries. *Sandbox worlds* (open-ended power-fantasy / world-director worlds, run with `/worldforge start --sandbox`) get **one always-active Sandbox Lorebook** instead — SANDBOX_STATE (standing situation + tonal mandate + an aliveness contract) plus a WORLD_PULSE entry — and author large NPC casts as a principal/roster split with a per-NPC voice-fingerprint uniqueness rule.
- **One Arc Intimacy Register per arc with intimate beats (Tier 3, conditional)** — arc-specific intimate function and per-character delta.
- **One Group Lorebook** — all tiers combined and group-tagged for ST's lorebook editor.
- **One Chat Completion Preset** — the model's prompt blocks, injection order, and behavioral framework, parameterized for this world's prose conventions.
- **One audit report** — runtime risks identified by the Prompt Engineer, with recommended corrections for the user to apply manually.

## Core architectural ideas

Three architectural decisions are load-bearing across the pipeline. Understanding them helps you read the agent specs and anticipate how the pipeline behaves.

**The three-tier lorebook architecture.** Every piece of world information belongs to exactly one tier. Tier 1 is permanent and arc-agnostic (the world). Tier 2 is permanent and per-character (who the characters are). Tier 3 is modular and per-arc (what is happening right now), with only one arc lorebook active at a time. This separation is what allows long, multi-arc roleplay to maintain coherence — character state evolves through Tier 3 swaps without rewriting Tier 2. In **sandbox mode**, Tier 3 collapses to a single always-active Sandbox Lorebook that anchors the standing world-state instead of a progression of arcs — the same tier mechanics, no swapping.

**The override architecture.** A character card's `system_prompt` and `post_history_instructions` fields override the preset's Main Prompt and Jailbreak blocks at runtime. Every card uses the `{{original}}` macro to splice the preset's content back in, then layers character-specific content on top. The preset holds engine-level instructions (creative framework, narration discipline, formatting conventions); cards hold character identity and behavior. The Editor enforces this contract on both sides: engine instructions in cards are a hard fail; character names in the preset's Main Prompt are a hard fail.

**The Style Contract.** Each world declares its prose conventions — perspective, tense, formatting markers, paragraph register — once, in World Seed Section 1.5. The Prompt Engineer parameterizes the preset's Main Prompt from this contract. Individual cards may declare a per-card style override (typically Director or Narrator cards in single-character-perspective worlds), which the Architect emits as a structured `<style_override>` block. The Editor validates the coupling between the structured field and the block content. Worlds with no overrides produce no overrides; the mechanism scales from zero overrides to many per world.

## Pipeline phases

Each phase is run by a specialized agent. The orchestrator dispatches them in order; some are conditional, some run in parallel, and some loop until quality thresholds are met.

| Phase | Agent | What it does |
|---|---|---|
| 0 | The Interviewer | Walks you through the World Seed Template interactively. Pushes back on thin or inconsistent material. Captures the Style Contract and test scenarios. |
| 1 | The Refiner | Classifies World Seed content into Tiers 1/2/3 plus the Style Contract. Identifies gaps. Produces a locked Master Design. Halts on unresolved questions. |
| 2 | The Architect | Drafts every Markdown source: character cards, all lorebook entries, system_prompt and post_history_instructions per card, optional depth prompts. Emits `<style_override>` blocks for cards with declared overrides. |
| 2.5 | The Intimacy Architect *(conditional)* | Drafts Tier 2 Intimacy Profiles and Tier 3 Intimacy Registers from Section 8 of the World Seed. Skipped if Section 8 is empty. |
| 3 | The Editor | Iteratively validates prose quality, tier integrity, lorebook entry quality, the override architecture, and the style override coupling. Returns directives until all checks pass. |
| 3.5 | The Voice Auditor | Generates sample dialogue from the drafts and audits behavioral fidelity, voice distinctiveness, trigger-response correctness, NPC agency (in a lull, do NPCs act on their own standing goals?), and (in multi-perspective worlds) cross-card perspective bleed. |
| 3.6 | The Arc Transition Auditor | Verifies continuity across consecutive arc seams: character state, trauma de-escalation, NPC behavior, relationship & belief drift, world conditions, hidden-information rules. |
| 3.7 | The Intimacy Auditor *(conditional)* | Generates sample intimate scenes and audits them for voice fidelity (does each character behave like themselves during sex?) and thematic register match (does the scene serve its declared function?). |
| 4 | The Compiler | Translates the approved Markdown drafts into SillyTavern-ready JSON files. |
| 5 | The Prompt Engineer | Audits Phase 4's output for runtime risks (read-only on `Export/`) and authors the Chat Completion Preset. Recommendations for any conflicts found are surfaced as plain-text instructions for manual application. |
| 5.5 | *(manual)* | If Phase 5 produced recommended corrections, you open each named file, apply the corrections, and save. The pipeline is complete only after this step. |

Phases 3.5 / 3.6 / 3.7 run in parallel after Phase 3 sign-off. Failures from any auditor return the affected files to the relevant Architect, then back through the Editor, then back to the auditor.

The audit/apply separation in Phase 5 is deliberate: the Prompt Engineer never modifies its own audit subject. This produces correctable mistakes rather than silent miscorrections. If you find this onerous on large worlds, the recommendations are short and structured — most apply in seconds.

## Pause gates

The pipeline pauses for user input under specific conditions:

- **Phase 1 blocker** — the Refiner found gaps requiring user answers. Logged in `UNRESOLVED_QUESTIONS.md`. Resume with `/worldforge resume phase1`.
- **Phase 2.5 blocker** — the Intimacy Architect needs Section 8 detail. Logged in `UNRESOLVED_INTIMACY.md`. Resume with `/worldforge resume phase2.5`.
- **Phase 3 stall** — the Editor returned the same files three rounds without improvement. Escalates to user; the problem is usually in the Master Design, not the Architect's execution.
- **Phase 3.7 conflict** — the Intimacy Auditor found a function/substrate contradiction at the Master Design level. You decide which side to change.
- **Phase 5 recommendations** — the Prompt Engineer found runtime risks. You apply manually before the world is ready for SillyTavern.

## Quick start

You need: VS Code with an agentic extension — [Kilo Code](https://github.com/Kilo-Org/kilocode) (recommended) or [Cline](https://github.com/cline/cline) — configured with an LLM API key. For the Kilo Code path specifically, follow [`wiki/Kilo-Code-Setup.md`](./wiki/Kilo-Code-Setup.md); for the tool/model comparison, see [`wiki/Agentic-Tools-and-Models.md`](./wiki/Agentic-Tools-and-Models.md).

**A note on model choice.** The agent specs in `agent_roles/` and the orchestrator in `workflows/world-forge.md` are deliberately long and prescriptive — each phase loads several thousand tokens of structural rules, validation checks, hard-fail conditions, and cross-references. To get the full benefit of the pipeline (and not silent skipping of validation steps or drift in tier discipline), use a model with strong long-context attention and a high tolerance for following dense, multi-step instructions. From the testing done so far, **DeepSeek 4 Pro** has held up well across the full pipeline. **Grok** failed during a run, though it is not yet clear whether the failure was the model itself or the way the agentic tool (Roo Code, since retired) drove it — treat this as a caveat, not a verdict. If you run the pipeline against a model not listed here and it succeeds (or fails in an interesting way), reports are welcome.

1. Clone this repository and open it as a VS Code workspace.
2. Open your agentic extension and select the orchestrator-class entry point: the **Code** agent in Kilo Code, or the default agent in Cline.
3. In the chat, type:
   ```
   /worldforge start
   ```
4. The Interviewer takes over. Answer its questions; it will push back when material is thin. Five minutes of friction here saves an hour of debugging at the runtime stage.
5. Subsequent phases run automatically, pausing only at the gates listed above.
6. When Phase 5 finishes, your `Export/` directory contains SillyTavern-importable JSON. If `Prompt_Engineer_Audit.md` lists recommendations, apply them manually before importing.

## A worked example

`Samples/` contains a complete pipeline output for the "Lucifer" world: a four-arc grimdark narrative with a protagonist, a primary character (Anna), a World Director card managing NPCs, intimacy across multiple arcs, and the full lorebook system. Inspect `Samples/Drafts/` to see what each agent produces; inspect `Samples/Export/` to see the resulting SillyTavern-ready JSON. `Samples/World_Seed_Lucifer.md` is the starting point — the document you would hand to the Refiner.

## Repository structure

What you get when you clone:

```text
World-Forge/
├── README.md                     ← This file
├── tutorial.md                   ← Extended usage walkthrough
├── AGENTS.md                     ← Standing instructions for agentic tools (Kilo/Cline)
├── CLAUDE.md                     ← Standing context for AI coding agents working on the repo
├── Notes_On_functionality.md     ← Authoritative reference for SillyTavern's runtime behavior
├── Notes_Quick_Reference.md      ← Compact distillation of the above (agents consult it first)
├── .kilocodeignore               ← Keeps samples + maintenance docs out of runtime agent context
├── .kilo/kilo.jsonc              ← Preconfigured Kilo Code per-phase agents (auto-loaded; OpenRouter flavor)
├── tools/
│   └── validate_export.py        ← Read-only validator for Export/ JSON (run after Phase 4)
├── agent_roles/                  ← Per-phase agent specifications (one .md per agent)
├── templates/                    ← Structural references (World Seed, character card, lorebook, preset)
├── workflows/
│   └── world-forge.md            ← The pipeline orchestrator
└── Samples/                      ← Worked example: a complete world output (Lucifer)
```

## Project folder structure (when running)

A new project folder evolves through these files as the pipeline progresses:

```text
[project-name]/
├── World_Seed.md                                  ← Phase 0
├── UNRESOLVED_QUESTIONS.md                        ← Phase 1 (conditional)
├── UNRESOLVED_INTIMACY.md                         ← Phase 2.5 (conditional)
├── Drafts/
│   ├── Master_Design.md                           ← Phase 1
│   ├── Card_[CharName].md                         ← Phase 2
│   ├── User.md                                    ← Phase 2 ({{user}} Persona Description text)
│   ├── Tier1_World_Entries.md                     ← Phase 2
│   ├── Tier2_[ProtagonistName]_Entries.md         ← Phase 2
│   ├── Tier2_[CharName]_Entries.md                ← Phase 2
│   ├── Tier2_[CharName]_Intimacy_Profile.md       ← Phase 2.5 (conditional)
│   ├── Tier3_Arc[N]_[Title]_Entries.md            ← Phase 2
│   ├── Tier3_Arc[N]_Intimacy_Register.md          ← Phase 2.5 (conditional)
│   ├── Instructions_[CardName].md                 ← Phase 2
│   ├── Editor_Critique_[Round N].md               ← Phase 3
│   ├── Voice_Audit_Report_[Round N].md            ← Phase 3.5
│   ├── Arc_Transition_Audit_[Round N].md          ← Phase 3.6
│   └── Intimacy_Audit_Report_[Round N].md         ← Phase 3.7 (conditional)
└── Export/
    ├── [CharName]_Card.json                       ← Phase 4
    ├── User.md                                    ← Phase 4 (paste into ST persona)
    ├── [ProtagonistName]_Lorebook.json            ← Phase 4
    ├── World_Lorebook.json                        ← Phase 4
    ├── [CharName]_Lorebook.json                   ← Phase 4
    ├── [CharName]_Intimacy_Profile.json           ← Phase 4 (conditional)
    ├── Arc[N]_Lorebook.json                       ← Phase 4
    ├── Arc[N]_Intimacy_Register.json              ← Phase 4 (conditional)
    ├── Group_Lorebook.json                        ← Phase 4
    ├── Compiler_Log.md                            ← Phase 4
    ├── Prompt_Engineer_Audit.md                   ← Phase 5
    └── [WorldName]_ChatPreset.json                ← Phase 5
```

`User.md` is the persona-description counterpart to the Tier 2 Protagonist Lorebook. SillyTavern provides no structured import for `{{user}}` personas (unlike V3 character cards for `{{char}}`), so the pipeline produces a paste-ready text block in `Export/User.md` alongside the Tier 2 Protagonist Lorebook. The persona description is the always-on identity floor injected every turn; the lorebook fires on keys for fuller detail. Voice / personality / manner are intentionally excluded from `User.md` — the human plays `{{user}}` and writes their own dialogue.

## Trigger commands

| Command | Action |
|---|---|
| `/worldforge start` | Begin from Phase 0 |
| `/worldforge resume phase[N]` | Resume from a specific phase (`phase0`, `phase1`, `phase2`, `phase2.5`, `phase3`, `phase3.5`, `phase3.6`, `phase3.7`, `phase4`, `phase5`) |
| `/worldforge status` | Report the current phase, round, and open blockers |
| `/worldforge skip phase0` | Begin from Phase 1 (you wrote the World Seed manually) |
| `/worldforge skip phase2.5` | Skip Intimacy Architect (no intimate content) |
| `/worldforge skip phase3.7` | Skip Intimacy Auditor (no intimate content) |
| `/worldforge revise` | Post-launch: make a surgical change to a shipped world through the revision pipeline (UID-preserving, scope-locked) |
| `/worldforge resync-preset` | Post-launch: regenerate a shipped world's Chat Completion Preset against the current template and block library — preset only, no content changes |
| `/worldforge convert <source> <target>` | Post-launch: reframe a shipped world into a new build (different protagonist, World Mode, Style Contract, or Core Concept). Produces a new `World_Seed.md` in `<target>`; hand off to `/worldforge skip phase0`. Read-only on `<source>`. |

## After SillyTavern import

1. Import each `Export/*.json` lorebook through SillyTavern's **World Info** panel; import each character card through the **Character Management** panel; place the chat preset through **API settings → Chat Completion Presets → Import**.
2. In the World Info panel, enable the **World Lorebook** group and all **Character Lorebook** groups permanently. **Arc lorebooks** are swap-in: enable Arc 1 to start; switch to Arc 2 when the story's exit trigger fires; and so on. **Only one arc lorebook should be active at a time.** The same applies to Arc Intimacy Registers when present.
3. Open **User Settings → Persona Management** and create (or select) the persona for this world. Open `Export/User.md`, copy the text between `--- BEGIN PERSONA DESCRIPTION ---` and `--- END PERSONA DESCRIPTION ---`, and paste it into the persona's **Description** field. Link the **Protagonist Lorebook** in the same persona's **Lorebook** field so it scans only when that persona is active.
4. Select the world's Chat Completion Preset in the API settings panel.

## Post-launch: revising and resyncing

A shipped world is not frozen. Two maintenance paths keep a world current without rebuilding it from scratch:

- **`/worldforge revise`** runs the revision pipeline — a parallel fork that makes surgical, scope-locked content changes (revise an arc, add a character, adjust a relationship) through mini-versions of the build agents. It preserves the UIDs on your existing lorebook entries, so running SillyTavern chat states survive the change. The one bright line: revisions that touch the world's core concept/tone or its Style Contract world defaults are bounced to a full re-run (reusing your existing `World_Seed.md`). See [`workflows/world-forge-revise.md`](./workflows/world-forge-revise.md).
- **`/worldforge resync-preset`** refreshes only the Chat Completion Preset, bringing it current with pipeline improvements and any content changes that surface inside preset blocks. It makes no content changes and, because a preset is a global settings profile rather than UID-bearing world info, re-importing it does not disturb running chats.
- **`/worldforge convert <source> <target>`** reframes a shipped world into a new build — different protagonist, different World Mode (arc ↔ sandbox), different tonal register, or different Style Contract world defaults — while preserving the structural work (world rules, factions, cosmology, NPCs) that would otherwise be discarded by a from-scratch `/worldforge start`. The Converter reads the source's `Master_Design.md` read-only, walks you through a preservation matrix (keep / modify / drop / regenerate, per source section), surfaces role reassignments explicitly (the old protagonist becoming an NPC, a source NPC becoming the new `{{user}}`, power-tier shifts), and writes a new `World_Seed.md` to your target folder. You then run `/worldforge skip phase0` against the target and the standard pipeline builds the new world end-to-end. Pure reskins (replacing setting + protagonist + factions + tone all at once) are refused — at that scale you're building a new world inspired by the source, not converting it; use `/worldforge start` fresh. See [`workflows/world-forge-convert.md`](./workflows/world-forge-convert.md).

## Companion SillyTavern fork (optional)

World-Forge produces world packages that target stock SillyTavern. Worlds will run on upstream ST without modification. That said, a few World-Forge patterns push against stock-ST defaults, and a companion fork — **[AndreiNicu/SillyTavern](https://github.com/AndreiNicu/SillyTavern)** — exists to smooth those edges. It is a separate project from this repository (this repository is **not** a fork; see [What this is NOT](#what-this-is-not) above), maintained alongside the pipeline so that the runtime keeps pace with patterns the pipeline produces.

What the fork changes, relative to stock SillyTavern:

- **Multi-entry lorebook firing per scene.** Stock SillyTavern's world-info scanner tends to converge on a single matching entry per group when keys overlap. World-Forge's Tier 3 design — ARC_STATE plus CHARACTER_STATE plus NPC_SHIFT plus DRAMATIC_BEAT all potentially firing in the same response — and World Director cards (which route off-roster NPC dialogue through a dedicated card) both assume that multiple matching entries can land in a single turn. The fork relaxes this so the full set of relevant entries is injected when their keys match, rather than collapsing to one.
- **Group chat routing for World Director cards.** Adjustments to the group reply strategy so a Director card handles off-roster NPC names cleanly and stops monologuing past the main cast. This pairs with the pipeline's World Director card pattern.
- **`world-forge` ST extension.** Ships in `public/scripts/extensions/world-forge/` in the fork. Provides runtime support for the structured `<style_override>` blocks that the Architect emits — macro substitution and a v2 directives array — so per-card style overrides resolve correctly at prompt-assembly time.
- **`prompt-viewer` ST extension (debugging).** Wand-menu extension for inspecting the outgoing prompt and, optionally, dumping it server-side. Useful when diagnosing whether a Tier 3 entry actually fired, whether `{{original}}` spliced as expected, or whether a style override resolved.

**You do not need the fork to use World-Forge.** Stock SillyTavern will run a World-Forge world; you may just notice that Tier 3 layering is less rich than designed when multiple ARC_STATE-adjacent entries are competing for a single slot, and that any `<style_override>` blocks are inert without the extension. If you find yourself running multi-arc worlds with Director cards or per-card style overrides, the fork is the smoother path.

Installation, branch policy, and update cadence are documented in the fork's own README.

## Where to learn more

- `tutorial.md` — extended usage walkthrough with worked examples
- `workflows/world-forge.md` — the orchestrator's full phase definitions
- `agent_roles/*.md` — per-phase agent specifications
- `Notes_On_functionality.md` — authoritative reference for SillyTavern's runtime behavior
- `CLAUDE.md` — standing context for AI agents working on the repository

---

*Issues, contributions, and pipeline improvements welcome. Pipeline architecture decisions are documented in `CLAUDE.md` and the agent specs themselves; consult those before proposing structural changes.*
