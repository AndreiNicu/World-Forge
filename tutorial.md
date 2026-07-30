# World Forge Pipeline: A Step-by-Step Tutorial

This tutorial walks through the World Forge pipeline using the **Lucifer** project as a worked example. You can follow along by reading the actual artifacts in `Samples/Drafts/` and `Samples/Export/` as they are referenced — every claim in this tutorial maps to a real file you can open.

The Lucifer world was authored by skipping Phase 0 (the user wrote `World_Seed_Lucifer.md` directly). The remaining phases ran in full, including iterative Editor and auditor loops. By the time you finish reading this tutorial, you will know how to read any pipeline output, how to interpret each agent's role, and where to look when something is wrong.

---

## 1. Prerequisites and Setup

You need:

- **VS Code** with an agentic extension — [Kilo Code](https://github.com/Kilo-Org/kilocode) (recommended) or [Cline](https://github.com/cline/cline) — configured with an LLM API key. For tool-by-tool guidance see [`wiki/Agentic-Tools-and-Models.md`](./wiki/Agentic-Tools-and-Models.md); Kilo Code users have a dedicated setup walkthrough at [`wiki/Kilo-Code-Setup.md`](./wiki/Kilo-Code-Setup.md).
- A clone of this repository, opened as a VS Code workspace.

That is the entire setup. The pipeline is markdown specifications — there is nothing to build or install.

**Two settings worth getting right before a long run:** which model runs which phase ([`wiki/Agentic-Tools-and-Models.md` §3.3](./wiki/Agentic-Tools-and-Models.md#33-mixing-models-across-phases) — spend the most on the Editor and Auditors), and sampling temperature per phase ([§3.5](./wiki/Agentic-Tools-and-Models.md#35-sampling-temperature-by-phase) — creative seats hot, the Compiler near zero). Kilo Code users get both preconfigured: the repo ships a `.kilo/kilo.jsonc` with per-phase agents, and [`wiki/Kilo-Code-Setup.md` §5.4](./wiki/Kilo-Code-Setup.md#54-per-phase-temperature) covers the temperature settings (already baked into the shipped `.kilo/kilo.jsonc`).

### Repository structure (what you cloned)

```text
World-Forge/
├── README.md                     ← Entry-point overview
├── tutorial.md                   ← This file
├── CLAUDE.md                     ← Standing context for AI coding agents
├── Notes_On_functionality.md     ← Authoritative SillyTavern runtime reference
├── agent_roles/                  ← Per-phase agent specifications
├── templates/                    ← Structural references (World Seed, card, lorebook, preset)
├── workflows/world-forge.md      ← The pipeline router (+ four stage files world-forge-*.md)
└── Samples/                      ← Worked example: the Lucifer world (full pipeline output)
```

### Project folder structure (what gets generated when you run)

When you start a new world, your project folder evolves through these files:

```text
[project-name]/
├── World_Seed.md                                  ← Phase 0 (or hand-written)
├── UNRESOLVED_QUESTIONS.md                        ← Phase 1 (conditional)
├── UNRESOLVED_INTIMACY.md                         ← Phase 2.5 (conditional)
├── Drafts/                                        ← Phases 1–3.7 outputs
└── Export/                                        ← Phase 4–5 final JSON package
```

The `templates/`, `agent_roles/`, `workflows/`, and `Notes_On_functionality.md` files travel with the repo and are read by the agents at runtime; you do not need to copy them per project.

---

## 2. Pipeline Overview

Each phase is run by a specialized agent. Some phases are conditional, some loop, and Phase 3.5/3.6/3.7 run in parallel.

```
[user intent]
      |
      v
 PHASE 0 — The Interviewer        (skip with /worldforge skip phase0)
      v
 World_Seed.md
      v
 PHASE 1 — The Refiner            → Master_Design.md
      v
 PHASE 2 — The Architect          → all Drafts/
      v
 PHASE 2.5 — Intimacy Architect   (conditional on World Seed Section 8)
      v
 PHASE 3 — The Editor             [loops until quality gate passes]
      v
 PHASE 3.5 + 3.6 + 3.7            (parallel auditors)
      v
 PHASE 4 — The Compiler           → Export/*.json
      v
 PHASE 5 — The Prompt Engineer    → ChatPreset + audit report
      v
 PHASE 5.5 — Manual application   (conditional on audit recommendations)
      v
 ✅ READY FOR SILLYTAVERN
```

### Trigger commands

| Command | Action |
|---|---|
| `/worldforge brainstorm` | Optional, upstream of Phase 0: divergent ideation when you have only a vibe — generates premise directions, writes informal `Brainstorm_Notes.md`, no World Seed (the Interviewer reads the notes on the next `start`) |
| `/worldforge brainstorm --adapt <document>` | Optional, upstream of Phase 0: turn an existing story, fanfiction, or roleplay log into a precursor — extracts its world and helps you decide who `{{user}}` is, then writes an `adaptation`-stamped `Brainstorm_Notes.md` (no World Seed) |
| `/worldforge brainstorm --improve` | Any time a world already exists (seed-only or shipped): ping-pong improvement ideas against it with no commitment — the Brainstormer reads the world read-only, riffs on fit / additions / reworks, and parks the results in the standing `Big_Brain_Storm.md`; nothing runs afterward — a later `revise --brainstorm` or a rebaseline `--then-brainstorm` chain offers to pick a parked idea up (see Section 9) |
| `/worldforge start` | Begin from Phase 0 (arc mode by default) |
| `/worldforge start --sandbox` | Begin from Phase 0 in **sandbox mode** — an open-ended world with no narrative arc (see Section 7) |
| `/worldforge skip phase0` | Begin from Phase 1 (you authored the World Seed manually — Lucifer's path) |
| `/worldforge resume phase[N]` | Resume from a specific phase after a pause gate |
| `/worldforge status` | Report current phase, round, and open blockers |
| `/worldforge skip phase2.5` | Skip Intimacy Architect (no intimate content) |
| `/worldforge skip phase3.6` | Skip Arc Transition Auditor (auto-skipped in sandbox mode — no arc seams) |
| `/worldforge skip phase3.7` | Skip Intimacy Auditor (no intimate content) |
| `/worldforge revise` | Post-launch surgical edits to a shipped world (UID-preserving, scope-locked) |
| `/worldforge revise --brainstorm` | Post-launch diagnostic: when something feels off but you can't name what to revise — runs the Brainstormer to locate the concern first, then the Reviser scopes it (see Section 9) |
| `/worldforge resync-preset` | Post-launch: refresh a shipped world's Chat Completion Preset against the current template + block library |
| `/worldforge audition` | Post-launch, read-only: probe how one character would behave in one scene under named conditions — returns YES / NO / IT DEPENDS with a trace, changes nothing (see Section 10.6) |
| `/worldforge audition --save` | Same as above, but also writes the result to `Drafts/Audition_[Char]_[slug].md` as a durable record |
| `/worldforge convert <source> <target>` | Post-launch: reframe a shipped world into a new build — different protagonist, World Mode, Style Contract, or Core Concept (see Section 8) |
| `/worldforge convert <source> <target> --rebaseline` | Post-launch: consolidate a revised world into a clean rebuild — same protagonist, revisions carried, markers dropped (see Section 8) |
| `/worldforge convert <source> <target> --rebaseline --then-interview` | Same, then go directly into the Interviewer to make major changes against the clean seed before the rebuild (see Section 8) |
| `/worldforge convert <source> <target> --rebaseline --then-brainstorm` | Same, but brainstorm *what* to change first (Brainstormer improvement posture), then the Interviewer reads those notes as proposals (see Section 8) |

> This table is a quick subset. **Section 10** is the full command reference — every trigger and flag with an example invocation and the *why* behind it.

> The Lucifer case study below is an **arc world** — it progresses through four arcs. If you are building an open-ended, NPC-populated world with no narrative arc (a power-fantasy, world-director, or life-sim world), read this case study first to learn the pipeline, then see **Section 7 — Sandbox worlds** for what changes.

---

## 3. The Lucifer Case Study

The Lucifer world is a four-arc grimdark narrative: a recovering addict named Anna meets Andrei (the user's protagonist, secretly the Devil), navigates a celestial conflict, and ends in cosmic tragedy and reconstruction. The world has two AI character cards (Anna and a World Director managing NPCs), full intimacy specification across all four arcs, and a multi-faction setting (the Black Hand of God, the Heavenly Host, Jack's prostitution ring).

### Phase 0: The Interviewer — *skipped*

For Lucifer, Phase 0 was skipped. The user authored `Samples/World_Seed_Lucifer.md` manually using `templates/World_Seed_Template.md` as the structural reference. To replicate this pattern:

```
/worldforge skip phase0
```

This is a valid path when you already have a fully-formed concept and want to write the World Seed yourself. The Interviewer is most useful for users whose ideas are still forming or who need pushback on thin material — for a fully-developed world like Lucifer, the manual path is faster.

If your idea is *less* than forming — just a vibe, an image, a single character with no world around them yet — there is an optional step further upstream: `/worldforge brainstorm`. The Brainstormer is the Interviewer's divergent counterpart. Instead of walking the template and pushing for specificity, it generates premise directions, follows whatever you light up on, and helps a concept find its shape. When something has a pulse, it writes informal `Brainstorm_Notes.md` (explicitly *not* a World Seed) and hands you to `/worldforge start`, where the Interviewer reads those notes as a warm start and runs the full interview. Brainstorm is entirely optional — skip it whenever you already know what you're building. **Section 9** covers the Brainstormer in full: its proactive suggestion style, the six domain lenses, and its use as a revision diagnostic.

The completed World Seed contains nine sections: core concept and tone (Section 1), the world (Section 2 — sensory signature, rules, factions, locations, species, concepts), the protagonist (Section 3), characters and their lorebook material (Section 4), narrative arcs (Section 5), technical specifications (Section 6), test scenarios (Section 7b), and the conditional intimacy specification (Section 8). The current pipeline also includes a Section 1.5 Style Contract (perspective, tense, formatting markers); Lucifer's seed predates this section and runs cleanly under the pipeline's defaults pathway. For how to fill the Style Contract in — what `DEFAULTS` gives you, and worked examples from the literary default to a leaner "typical roleplay" register — see **Section 11 — Setting your prose style**.

### Phase 1: The Refiner — `Drafts/Master_Design.md`

The Refiner reads the World Seed and produces a structured Master Design that classifies every piece of content into Tier 1 (world), Tier 2 (character), or Tier 3 (arc). For Lucifer, this produces a 9-section document:

```
SECTION 1: WORLD LAWS & MECHANICS (Tier 1 Source)
  1.1 Core Concept & Tone
  1.2 Tonal Hard Rules
  1.3 Rules of Reality
  1.4 What the World Forbids (Narrative Hard Limits)
  1.5 Sensory Signature of the World
SECTION 2: FACTIONS & POWER STRUCTURES (Tier 1 Source)
  2.1 The Black Hand of God
  2.2 The Heavenly Host
  2.3 Jack's Prostitution Ring & Street Gangs
SECTION 3: STANDING LOCATIONS — Andrei's Penthouse, Anna's Apartment, Ingrid's House, the Streets
SECTION 4: SPECIES & CATEGORIES — Demons, Angels, Nephilim
SECTION 5: WORLD CONCEPTS & LORE — The Veil, The Fall, Heroin Addiction & Withdrawal
SECTION 6: PROTAGONIST SPECIFICATION ({{user}})
SECTION 7: CHARACTER FOUNDATIONS (Tier 2 Source)
SECTION 8: NPC ROSTER (Tier 2 Source — secondary characters)
SECTION 9: NARRATIVE ARC STRUCTURE (Tier 3 Source)
```

If the Refiner finds gaps (a faction with no trigger keywords, an arc without an exit trigger, a character with no central wound), it produces `UNRESOLVED_QUESTIONS.md` and halts. You answer the questions, then resume with `/worldforge resume phase1`. For Lucifer, no gaps were found — the World Seed was complete enough to proceed.

### Phase 2: The Architect — drafts every source file

The Architect takes the locked Master Design and authors every Markdown source the Compiler will need. For Lucifer, Phase 2 produces:

| File | What it contains |
|---|---|
| `Card_Anna.md` | Anna's character card content: description, personality, scenario, first message, example exchanges |
| `Card_World_Director.md` | The World Director card: omniscient narrator content, NPC voice patterns |
| `User.md` | The `{{user}}` Persona Description text (paste-ready, ≤150 words). Pairs with the Tier 2 Protagonist Lorebook to give `{{user}}` parity with `{{char}}` despite ST's missing persona import format. Voice and personality intentionally excluded — the human plays `{{user}}`. |
| `Tier1_World_Entries.md` | All Tier 1 lorebook entries — world rules, factions, standing locations, species, concepts |
| `Tier2_Anna_Entries.md` | Anna's permanent character lorebook: physical baseline, psychological core, relationships |
| `Tier2_Andrei_Entries.md` | Protagonist lorebook for Andrei (`{{user}}`) |
| `Tier2_NPC_Entries.md` | NPC reference data (Mr. Black, Michael, Jack, etc.) |
| `Tier3_Arc[1-4]_Entries.md` | Per-arc state, NPC shifts, dramatic beats, tension |
| `Instructions_Anna.md` | Anna's `system_prompt` and `post_history_instructions` |
| `Instructions_World_Director.md` | The World Director's `system_prompt` and `post_history_instructions` |

Each Tier 1 entry follows a strict structure. From `Samples/Drafts/Tier1_World_Entries.md`:

```text
### ENTRY: World Rule — Demonic Disguises
**Category:** RULE
**Trigger Keys:** demon disguise, red eyes, sunglasses, disguise fracture, human form demon
**Secondary Keys:** shadow wrong, temperature drop, demonic tell
**Selective Logic:** 0
**Constant:** No
**Injection Position:** 0
**Order Priority:** 100
**Position Rationale:** DEFAULT

**Content:**
All demons operating on Earth must maintain a complete human form. The disguise
requires continuous will — it is not automatic. Under extreme emotional or
physical duress, the disguise fractures: ambient temperature drops sharply,
shadows lengthen and move incorrectly, and red bleeds around the edges of their
sunglasses. The sole tell is their eyes — glowing red...
```

Note the **Position Rationale** field. Every entry must include it. "DEFAULT" means the entry uses the documented default position for its tier (Tier 1 → position 0). Any non-default choice requires a one-sentence justification referencing `Notes_On_functionality.md`. The Editor will hard-fail entries with missing or shallow rationales.

### Phase 2.5: The Intimacy Architect — *conditional*

For worlds with intimate content (Section 8 of the World Seed populated), the Intimacy Architect runs after Phase 2 and drafts two additional file types:

- `Tier2_[CharName]_Intimacy_Profile.md` — permanent intimate substrate per character: trauma map, body reactions, vulnerability shape, voice in intimacy, hard limits and hard yeses.
- `Tier3_Arc[N]_Intimacy_Register.md` — arc-specific delta: thematic function, prose register, live scene types, arc-specific hard rules.

For Lucifer, intimacy is a thematic pillar, so Phase 2.5 ran. The world's intimacy posture was specified as oppressive and transactional (Arc 1) shifting to communion (Arc 4). The per-arc functions were:

- Arc 1: Transaction and Survival — vigilant prose, intimacy as commodity
- Arc 2: Communion and Comfort — frightened discovery; trauma map highly active
- Arc 3: Claim and Play — confidence and ownership
- Arc 4: Ritual — weight and consequence

By specifying Arc 1's function as *transaction* explicitly, the Intimacy Architect ensures the model never writes Anna as enthusiastically initiating sex in Arc 1 — preserving the world's psychological realism. This is the leverage of the function-based approach: the prose register flows from the declared purpose, not from generic erotica defaults.

If your world has no intimate content, leave Section 8 of the World Seed empty and the pipeline will skip Phase 2.5 and Phase 3.7 entirely. Use `/worldforge skip phase2.5` if invoking the orchestrator manually.

### Phase 3: The Editor — iterative quality validation

The Editor validates the Architect's drafts across three layers: prose quality (sensory completeness, show-don't-tell, voice distinctiveness), tier integrity (no arc-specific content in Tier 1 or Tier 2), and LLM instruction quality (system_prompt structure, override architecture compliance, no engine-instruction contamination in cards).

The Editor loops until everything passes. Lucifer required **three rounds**:

- **`Editor_Critique_Round1.md`** — One blocking hard fail: the World Director's `system_prompt` contained the diagnostic phrase `"{{user}} controls their own"`, which is engine-instruction contamination per Editor §5b. The phrase belongs in the preset Main Prompt, spliced via `{{original}}`, not in the card itself. Multiple quality directives also flagged.
- **`Editor_Critique_Round2.md`** — Hard fail resolved. Quality directives addressed. New observations on Tier 2 Intimacy Profile depth and dissociation-snapshot specificity.
- **`Editor_Critique_Round3.md`** — Final clean pass. All 15 directives PASS. All 7 hard rules PASS. No regression. Sign-off issued.

The Editor's sign-off block is the gate to the auditors. Without it, the auditors halt — there is no point validating runtime behavior on material that has structural failures.

If the Editor stalls (three rounds of the same files without improvement), the pipeline pauses and escalates to the user. The problem is usually in the Master Design, not the Architect's execution.

### Phases 3.5 / 3.6 / 3.7: The Auditors — runtime fidelity

The Editor verifies that the drafts are structurally correct. The auditors verify that the drafts will *behave correctly* at runtime. They generate sample dialogue or scenes using the drafts as if the model were running on them, and audit the result against the spec.

#### Phase 3.5: Voice Auditor — `Voice_Audit_Report_Round[N].md`

Builds a test matrix: every AI-played character × every arc × at least three scenarios per character per arc. For Lucifer's Anna:

| # | Test Scenario | Active Arc | Expected Register | Trigger to Verify |
|---|---|---|---|---|
| A1a | Arrival at penthouse; {{user}} offers food without taking anything | Arc 1 | The Wreckage | Sincere unprompted kindness; transactional reflex |
| A1b | {{user}} asks about Timmy during withdrawal | Arc 1 | The Wreckage | Timmy trigger — sarcasm drop; fragmented speech |
| A2a | Anna clean, pre-revelation; {{user}} offers gentle touch unexpectedly | Arc 2 pre-rev | The Becoming | Unexpected gentle touch; warmth-then-deflect |
| ... | (eight more scenarios) | | | |

For each scenario, the auditor generates a 4–6 exchange dialogue sample as if it were the model running on Anna's drafted material, then checks: does the dialogue match the active arc's CHARACTER_STATE (including the trauma-trajectory line — a faded trigger must not fire at full intensity)? Do triggers fire correctly? Is voice distinct? Does behavior bleed across arcs? And in a lull, do NPCs act on their own standing goals rather than the scene freezing to wait on `{{user}}` (Step 3J)?

For Lucifer, Round 1 flagged behavioral fidelity issues that traced back to specific draft files. Round 2 verified the fixes. Sign-off issued.

#### Phase 3.6: Arc Transition Auditor — `Arc_Transition_Audit_Round[N].md`

Verifies continuity across consecutive arc seams. For each arc pair, checks: trigger continuity, CHARACTER_STATE continuity (including trauma de-escalation — fades are shown, never sudden vanishings), NPC behavioral shift continuity, relationship & belief continuity (bonds and beliefs drift only through earned beats — no teleporting bonds, un-caused belief flips, or silent memory resets), world state continuity, hidden-information rule continuity, dramatic-beat sequence, tone-register continuity.

For Lucifer, Round 1 found Critical failures at the Arc 1 → Arc 2 seam: the Arc 1 exit trigger (Jack's forces making first contact with the Black Hand) did not causally connect to the Arc 2 entry trigger (Anna's first night sleeping through without withdrawal). The structural bridge — Black Hand's response, the cooling-off period, Anna's recovery process — was missing from the Tier 3 Arc 1 file. The Architect drafted the missing bridge content; Round 2 verified.

#### Phase 3.7: Intimacy Auditor — `Intimacy_Audit_Report_Round[N].md` *(conditional)*

Generates sample intimate scenes and audits them under two lenses:

- **Voice fidelity (primary)**: does each character behave like themselves during sex? Substrate fidelity, trauma map fidelity, voice continuity, hard-limit integrity.
- **Thematic register match (secondary)**: does the scene serve its declared function? Function fidelity, prose-register match, direction fidelity.

When the lenses conflict, voice fidelity wins. Function/substrate contradictions at the Master Design level are escalated to the user, not patched at the draft level.

For Lucifer, Round 1 found behavioral fidelity issues in Arc 2 intimate scenes (trauma map flinch fidelity); Round 2 verified after the Architect tightened the relevant Intimacy Profile and Arc 2 Register entries.

The three auditors run in parallel after Editor sign-off. Failures from any auditor return the affected files to the relevant Architect, then back through the Editor, then back to the auditor.

### Phase 4: The Compiler — `Export/*.json` and `Compiler_Log.md`

The Compiler translates approved Markdown drafts into SillyTavern-ready JSON. Before doing anything, it verifies sign-off from all four prior phases:

```text
| Phase | Report                                | Sign-Off    |
|-------|---------------------------------------|-------------|
| 3.0   | Editor_Critique_Round3.md             | ✅ APPROVED |
| 3.5   | Voice_Audit_Report_Round2.md          | ✅ SIGN-OFF |
| 3.6   | Arc_Transition_Audit_Round2.md        | ✅ SIGN-OFF |
| 3.7   | Intimacy_Audit_Report_Round2.md       | ✅ SIGN-OFF |
```

Without all four sign-offs, the Compiler halts. This is the audit-vs-apply discipline of the pipeline: nothing reaches Export/ that has not passed every quality gate.

For Lucifer, the Compiler produced 17 JSON files plus the log:

- 2 character cards (`Anna_Card.json`, `World_Director_Card.json`)
- 1 World Lorebook (Tier 1, 22 entries)
- 1 Andrei (Protagonist) Lorebook (Tier 2)
- 1 Anna Lorebook (Tier 2)
- 1 NPC Lorebook (Tier 2)
- 1 Anna Intimacy Profile (Tier 2)
- 4 Arc Lorebooks (Tier 3)
- 4 Arc Intimacy Registers (Tier 3)

The Compiler Log includes a **Persona Linkage Instruction** because the Protagonist Lorebook needs to be manually linked to the active SillyTavern Persona after import — this is documented inline in `Samples/Export/Compiler_Log.md`.

### Phase 5: The Prompt Engineer — `Prompt_Engineer_Audit.md` and `[WorldName]_ChatPreset.json`

The Prompt Engineer does two things in parallel:

1. **Audits the Compiler's output** (read-only on `Export/`). Reviews every lorebook entry for position correctness, injection order, keyword coverage, and budget risk. Reviews every character card for system_prompt, post_history_instructions, and depth_prompt correctness. Cross-checks card behavioral mandates against arc CHARACTER_STATE entries to prevent drift.
2. **Authors the Chat Completion Preset** — the file SillyTavern loads as the model's runtime prompt configuration. For each block (Main Prompt, Deep Think, Arc Guardian, Lore Integration, Spatial Awareness, Sensory Embodiment, Formatting, Jailbreak, plus optional/conditional blocks), the agent writes world-specific content per a Block Selection Rationale that names the world's likely runtime failure modes.

The audit report is structured as numbered sections — for Lucifer, position logic review (table of all 22 World Lorebook entries verified), keyword coverage audit, card-lorebook consistency audit, Block Selection Rationale, and a sign-off. If the audit finds runtime risks, the recommendations land in **Sections 7 and 8** of the report as plain-text instructions for manual application — the Prompt Engineer never modifies its own audit subject.

### Phase 5.5: Manual application — *conditional*

If the Prompt Engineer's audit produced recommendations in Sections 7 or 8, the user opens each named file, applies the corrections, and saves. The pipeline is complete only after this step.

For Lucifer, the audit ended `Status: COMPLETE`, so no Phase 5.5 was needed. The Export/ directory was ready for SillyTavern import as-is.

---

## 4. Reading the artifacts

`Samples/` is structured to be navigable. If you want to understand a specific aspect of the pipeline, here is where to look:

| Question | File to read |
|---|---|
| How does a World Seed actually look when complete? | `Samples/World_Seed_Lucifer.md` |
| How does the Refiner organize a world into tiers? | `Samples/Drafts/Master_Design.md` |
| What does a fully-drafted character card look like? | `Samples/Drafts/Card_Anna.md`, `Samples/Drafts/Card_World_Director.md` |
| What does a `User.md` persona description look like? | `Samples/Drafts/User.md` (Architect draft) → `Samples/Export/User.md` (final, paste-ready) |
| How are Tier 1/2/3 lorebook entries structured? | `Samples/Drafts/Tier1_World_Entries.md`, `Samples/Drafts/Tier2_Anna_Entries.md`, `Samples/Drafts/Tier3_Arc1_Entries.md` |
| What is the difference between Tier 2 Intimacy Profile and Tier 3 Intimacy Register? | `Samples/Drafts/Tier2_Anna_Intimacy_Profile.md` vs. `Samples/Drafts/Tier3_Arc1_Intimacy_Register.md` |
| How does the Editor flag and resolve issues? | `Samples/Drafts/Editor_Critique_Round1.md` (failures) → `Round3.md` (clean sign-off) |
| What does an auditor's test matrix and dialogue audit look like? | `Samples/Drafts/Voice_Audit_Report_Round1.md` |
| How does the Compiler verify the pipeline's chain of sign-offs? | `Samples/Export/Compiler_Log.md` |
| What does the final Chat Completion Preset look like? | `Samples/Export/Lucifer_ChatPreset.json` |
| How thorough is the runtime audit? | `Samples/Export/Prompt_Engineer_Audit.md` |

---

## 5. After SillyTavern import

Once your `Export/` directory is ready:

1. Import each `*.json` lorebook through SillyTavern's **World Info** panel. Import each character card through the **Character Management** panel. Import the chat preset through **API settings → Chat Completion Presets → Import**.
2. In the World Info panel, enable the **World Lorebook** group and all **Character Lorebook** groups permanently. **Arc lorebooks** are swap-in: enable Arc 1 to start; switch to Arc 2 when the story's exit trigger fires (e.g., for Lucifer, when Anna sleeps through her first night without withdrawal); and so on. **Only one arc lorebook should be active at a time.** The same applies to Arc Intimacy Registers when present.
3. Wire up the `{{user}}` persona. SillyTavern provides no structured import for personas, so this step is manual but quick:
   - Open **User Settings → Persona Management** and create (or select) the persona for this world. Use the in-world name from the top of `Export/User.md` (for Lucifer, `Andrei Petrov`).
   - Open `Export/User.md`. Copy the text between `--- BEGIN PERSONA DESCRIPTION ---` and `--- END PERSONA DESCRIPTION ---` and paste it into the persona's **Description** field.
   - In the same persona editor, link `[WorldName]_[ProtagonistName]_Lorebook.json` (for Lucifer, `Lucifer_Andrei_Lorebook.json`) in the persona's **Lorebook** field. The persona description is the always-on identity floor (≤150 words, injected every turn); the lorebook fires on keys for fuller detail.
   - Activate this persona before starting the chat.
4. Select the world's Chat Completion Preset (e.g., `Lucifer_ChatPreset.json`) in the API settings panel.

You are ready to roleplay.

> Note: `User.md` deliberately does **not** contain voice, personality, or speech patterns for `{{user}}`. The human plays `{{user}}` and writes their own dialogue and actions — those are the human's domain, not the LLM's. `User.md` is reference data the LLM uses to react *to* `{{user}}` correctly.

---

## 6. Common gotchas

- **Phase 1 paused with UNRESOLVED_QUESTIONS.md.** This is the Refiner finding gaps. Read the file, answer the questions in your World Seed, then `/worldforge resume phase1`. Do not skip — gaps propagate forward and produce broken cards.
- **Phase 3 looped three times without improvement.** The Editor escalates to you. The problem is usually in the Master Design, not the Architect's execution. Re-examine the Master Design's relevant section.
- **Auditor flagged a Critical failure that ties to the Master Design itself.** Sometimes the bug is structural — an arc's exit trigger doesn't causally connect to the next arc's entry; a character's substrate forbids a behavior the world wants in scene. The fix is to update the Master Design and re-run from Phase 2, not to patch the symptom in the drafts.
- **Phase 5 audit ended "AUDIT COMPLETE — N manual corrections required."** Phase 5.5 is not optional in this case. Open each Export/ file named in the audit, apply the recommended corrections, save. Only then is the world ready.
- **Forgot to paste `User.md` into the persona Description field.** SillyTavern will run the world without it, but NPCs will react oddly to `{{user}}` in opening turns until a Tier 2 keyword fires. Always paste the persona description before starting a chat.
- **Unfamiliar files in Samples/.** Lucifer's Drafts/ has 27 files because the world has four arcs, two character cards, full intimacy specification, and went through three Editor rounds and two rounds for each auditor. A simpler world produces fewer files. The structure is the same; the volume scales with the world.

---

## 7. Sandbox worlds (an alternative World Mode)

Lucifer is an **arc world**: it moves through a fixed progression of arcs, each with entry/exit triggers, dramatic beats, and per-character evolution. Some worlds have no arc at all — open-ended power-fantasy, world-director, and life-sim worlds where the experience is "live in this world and do things," not "move through a story." Those run in **sandbox mode**.

Sandbox mode is **not a separate pipeline** — it is a branch *through* the same phases you just read. The same Interviewer, Refiner, Architect, Editor, Voice Auditor, Compiler, and Prompt Engineer run. Only the Tier 3 spine and the large-cast NPC format change.

### Declaring sandbox mode

Mode is declared in **World Seed Section 1** (`World Mode: arc | sandbox`). `arc` is the default; every existing world is an arc world. To build a sandbox world:

```
/worldforge start --sandbox
```

This pre-sets the Interviewer, but the World Seed field is the source of truth — a hand-written seed or a `skip phase0` run carries the signal too. When sandbox mode is set, the Interviewer walks a **Sandbox Charter** (World Seed Section 5B) instead of the arc questions.

### What changes vs. an arc world

| Aspect | Arc world (Lucifer) | Sandbox world |
|---|---|---|
| **Tier 3** | One Arc Lorebook per arc, swapped in/out | **One always-active Sandbox Lorebook** — never swapped |
| **Standing anchor** | `ARC_STATE` per arc (Dramatic Situation + Tonal Mandate) | `SANDBOX_STATE` (Standing Situation + Tonal Mandate, with an **aliveness contract**) + a `WORLD_PULSE` entry |
| **Per-arc entries** | `CHARACTER_STATE`, `NPC_SHIFT`, `DRAMATIC_BEAT`, arc triggers | none — there is no arc |
| **NPC cast** | Full profiles per NPC | **Principal/roster split** — a few deep principals, the rest as compact roster stat blocks with unique voice fingerprints |
| **Phase 3.6** | Arc Transition Auditor runs | Skipped (no arc seams) |
| **Phase 3.5** | Arc-register checks | Standing-register checks **+ NPC Distinctiveness Matrix** (a blind-line test across the roster) |
| **Preset** | Standard blocks | Adds the **NPC Ensemble & Enrichment** block and weights Sensory Embodiment high |

### The aliveness contract

The single most important thing a sandbox world needs is the thing an arc carries for free: momentum and tone. With no arc driving the experience, the `SANDBOX_STATE` Tonal Mandate and the `WORLD_PULSE` entry carry an **aliveness contract** — NPCs pursue their own agendas and initiate scenes, the world reacts to and remembers `{{user}}`'s actions and reputation, off-screen life continues, and the world never freezes waiting for `{{user}}`. This is what keeps a sandbox from playing like an inert menu of NPCs that only exist when summoned.

The contract is made concrete by **per-NPC standing goals**: each principal NPC carries an active objective and the moves that advance it (Architect §7.D), and the cadence directive tells the model to have a present or off-screen NPC advance its goal when a scene lulls. The Voice Auditor's Step 3J tests exactly this — that NPCs take initiative and that each move traces to a stated goal. (The same goal/cadence mechanic runs in arc worlds through the `ARC_STATE` activity-cadence directive; NPCs exist in both modes, so it is mode-agnostic.)

### Keeping a large NPC cast distinct

A sandbox usually runs on a big cast voiced by a World Director card. The failure mode at that scale is not per-NPC infidelity — it is **homogenization**: thirty NPCs collapsing into two or three generic voices. Two mechanisms defend against it:

- **Roster NPC stat blocks** (Architect §7.E) — each roster NPC gets a compact block whose load-bearing field is a **voice fingerprint**: three concrete, unique speech markers no other NPC shares. The binding rule is that no two roster NPCs are confusable from a single line of dialogue.
- **The NPC Ensemble & Enrichment preset block** (`npc_ensemble`) — encourages NPC-to-NPC dialogue (not just hub-and-spoke around `{{user}}`), scales prose up when several NPCs share a scene, and lets NPCs grow organic detail *not* in the lorebook, within guardrails (consistent with their established voice, never contradicting the lorebook, treated as canon once established).

### Intimacy in a sandbox

Sandbox worlds usually carry sexual material across the NPC cast. The intimacy infrastructure threads the same way:

- The Tier 3 intimacy register folds into a single standing **`Sandbox_Intimacy_Register`** (a standing `INTIMACY_FUNCTION`, not per-arc).
- **NPC intimacy follows the principal/roster split** — principal NPCs get full Tier 2 Intimacy Profiles; roster NPCs get compact §6.5 intimate stat blocks (intimate essence, body & sound signature, voice in intimacy, a limit/yes, stance), with the same uniqueness rule: no two NPCs interchangeable in an intimate scene.
- The Intimacy Auditor adds an **NPC intimate coverage & distinctiveness check** (Step 3H): every sexual NPC has substrate, and no two read as the same in bed.

### After SillyTavern import (sandbox)

The import flow is the same as Section 5, with one difference: there are no arc lorebooks to swap. Enable the **World Lorebook**, all **Character/NPC Lorebook** groups, and the single **Sandbox Lorebook** group permanently — and leave them on. The `SANDBOX_STATE` entry is constant and `ignoreBudget`, so it fires every turn. If the world has intimate content, enable the **Sandbox Intimacy Register** group the same way.

### Note on retrofitting

Flipping World Mode is a Section 1 change, which the revise pipeline bounces. There are two paths: a from-scratch rebuild via hand-editing the World Seed (`World Mode: sandbox`, rewrite Section 5 as a Sandbox Charter, reclassify NPCs into principal/roster) and running `/worldforge skip phase0`; or the **Convert pipeline** (Section 8 below), which is the structured path for arc↔sandbox flips and other big reframings — it reads the source world's `Master_Design.md` read-only, walks you through what to keep and what to regenerate, and writes a new seed in a fresh project folder. Convert is usually the right choice for a mode flip because it preserves the Tier 1 work (rules, factions, locations) and most of Tier 2 (characters) — `start --sandbox` from scratch would make you rebuild all of that. Surgical edits to a shipped sandbox world — recalibrating `SANDBOX_STATE`, tweaking `WORLD_PULSE`, adding roster NPCs, adjusting sandbox intimacy — *are* handled by the revise pipeline (`/worldforge revise`), which is sandbox-aware via the `sandbox_*` scope types.

---

## 8. Converting a shipped world (`/worldforge convert`)

Sometimes a shipped world's world-building is worth reusing under a different angle. The Lucifer world (Section 3) is a four-arc grimdark story with a mortal `{{user}}` who becomes Lucifer's confessional foil. Suppose you've finished Anna's story and you want to play through the same world — same modern Stockholm, same Black Hand of God, same cosmology, same Lucifer — but as God instead, doing field work on Earth and running into Lucifer's syndicate from the other side. Or suppose you want the same world but as a sandbox: drop into Lucifer's Stockholm with no fixed arc, just live the city's pressures.

Both are exactly what the **Convert pipeline** is for. It is the third post-launch operation alongside revise and resync-preset, and it is the legitimate path for the change-categories the revise pipeline bounces: a different protagonist, a `World Mode` flip (arc ↔ sandbox), a different Style Contract at the world level, or a different Core Concept & Tone (Master Design Section 1).

### What Convert does and does not do

| What it does | What it doesn't do |
|---|---|
| Reads the source world's `Master_Design.md` read-only | Modifies the source project (never) |
| Walks a preservation matrix with you (keep / modify / drop / regenerate per source section) | Writes anything other than the new `World_Seed.md` |
| Surfaces role reassignments explicitly (old protagonist → NPC, source NPC → new `{{user}}`, power-tier shifts) | Replace `/worldforge start` for fully fresh worlds |
| Writes a new `World_Seed.md` in your target folder | Replace `/worldforge revise` for surgical edits |
| Hands off to `/worldforge skip phase0` for the standard build | Merge two source worlds (single source only) |

The Converter is one phase (C0). After it finishes, you run the standard pipeline (Phase 1 onward) against the target folder, exactly as if you had hand-written the new seed.

### Invocation

```
# Interactive: the Converter interviews you through the preservation matrix
/worldforge convert path/to/lucifer-project path/to/lucifer-as-god

# Brief-driven: fill in templates/Convert_Brief_Template.md first, then
/worldforge convert path/to/lucifer-project path/to/lucifer-as-god --brief path/to/Convert_Brief.md
```

The Brief is recommended for non-trivial conversions because it is version-controllable and reviewable. The brief-driven mode still interviews you — but only on gaps and ambiguities in the brief.

### The overlap floor refusal

Convert is **reframe or rebaseline, never reskin**. If you are replacing setting + protagonist + factions + tone all at once, the Converter refuses with an explicit bounce to `/worldforge start`. At that scale, the source is creative reference, not a structural source — pretending otherwise produces a Frankenstein seed that the downstream pipeline cannot build cleanly. The Converter classifies your intent against four axes (setting, protagonist, factions, tone), counts how many are being replaced, and:

- **0 or 1 replaced** — well-shaped conversion; proceed
- **2 replaced** — borderline ("half a new world"); surface to you, proceed on explicit confirm
- **3 or 4 replaced** — refuse; run `/worldforge start` against the target folder, use the source's `Master_Design.md` as creative reference during Phase 0

This refusal is intentional and not configurable. "I'm building a Greek mythology version of the Lucifer world" is usually a four-axes-replaced ask: new setting, new protagonist, new factions, new tone. That's a new world inspired by Lucifer, not Lucifer converted.

### The Lucifer → God worked example

Suppose you want to reframe the Lucifer world to play as God. You'd run:

```
/worldforge convert path/to/Lucifer path/to/Lucifer-as-God
```

The Converter reads `path/to/Lucifer/Drafts/Master_Design.md` and walks you through:

- **Overlap floor.** Setting (modern Stockholm with grimdark cosmology) — *kept*. Factions (Black Hand of God, etc.) — *kept*. Tone (grimdark, morally weighted) — *kept* or possibly modified (playing God may shift the moral lens). Protagonist (mortal → deity) — *replaced*. Result: 1 axis replaced — well-shaped. Proceed.
- **Tier 1.** Most of Section 2 carries forward verbatim — the supernatural rules, the location descriptions, the species/cosmology entries. The factions carry forward by name and capability, but **their relationship to `{{user}}` will be reauthored downstream** — the new protagonist is God, not Anna's POV, so the Black Hand's framing shifts from "Lucifer's syndicate on Earth seen from the outside" to "Lucifer's earthly operation that you, God, are observing or intervening in." The Converter flags this; the Architect rewrites the relationship at Phase 2.
- **Tier 2.** Anna stays as a Tier 2 character (she's not a protagonist in the new world; she's a person God interacts with). Lucifer stays as a Tier 2 character. The source `{{user}}` (the original protagonist) is dropped — there was no separate Tier 2 entry for them; they were the protagonist. The new `{{user}}` (God) does not exist as a source Tier 2 entry, so they are authored fresh in Section 3.
- **Section 4 fields the Converter handles automatically.** Anna's `Standing Goal` carries across if it's protagonist-agnostic (e.g., "stay clean and get her brother out of the syndicate") or is stripped + marked for reauthoring if it cites the old protagonist. Every relationship's `How it drifts (arc worlds)` line is stripped — the arcs are being regenerated, so the drift trajectory will be authored fresh downstream. `Operative belief` lines carry across only between two preserved characters and only when they don't mention `{{user}}` — beliefs about `{{user}}` (the most common case) get stripped because `{{user}}` has changed. `Trauma trajectory` per intimate character is stripped for the same arc-coupled reason; the base `Trauma map` (the trigger + response substrate) carries through. You don't declare any of this in the Convert Brief — it happens inside the Converter's Section 4 carry-across pass.
- **Section 3 (new protagonist).** This is always new. The Converter runs Interviewer-grade Section 3 questioning on God — wound (an ancient one, possibly), hidden layer, contradiction, power and limits (this is critical — a deity protagonist has a different power tier than Anna's mortal `{{user}}`, and the world's hard rules must be examined for whether they still constrain or whether God transcends them), physical description (incarnate? voice-only? both?), voice and manner.
- **Section 5 (arcs).** Regenerated. The arc spine is protagonist-shaped, and the protagonist has changed. The Converter leaves Section 5 as a structured stub; the Refiner surfaces it as a Phase 1 gap. You answer (probably: "field-work arcs investigating Lucifer's operations, culminating in a confrontation"), Phase 1 proceeds.
- **Section 7b (test scenarios).** New. Three to five scenes you intend to play as God — say, a first meeting with Lucifer where the power asymmetry is the entire scene; a quiet moment observing the city's suffering and choosing not to intervene; a confrontation with the Black Hand in a public setting.
- **Section 8 (intimacy).** If the source had intimacy and the new world will too, world-level posture and hard rules carry across. Per-character substrate carries across for preserved characters. Per-arc intimate functions are regenerated downstream because the arcs are regenerated.

After Step 6 (write the seed) and Step 7 (sign-off), the Converter outputs the hand-off instruction. You run `/worldforge skip phase0 path/to/Lucifer-as-God` and the standard pipeline builds the new world.

### What survives, what doesn't (rule of thumb)

- **Survives:** world rules, factions (without the relationship to `{{user}}`), locations, species, concepts, preserved Tier 2 characters' wounds/voices/physical descriptions, Style Contract world defaults (if kept), world-level intimacy posture (if kept).
- **Reauthored downstream:** every preserved character's *relationship to `{{user}}`*, behavioral mandates that depended on the old protagonist, per-card style overrides, faction-to-`{{user}}` relationships.
- **Always regenerated:** Section 3 (new `{{user}}`), Section 5 (arcs or Sandbox Charter — protagonist-shaped), Section 7b (test scenarios), per-arc / standing intimate functions.

The Converter's job is to **surface every transition explicitly** in the Conversion Manifest at the top of the new seed and in HTML-comment markers throughout. The downstream pipeline treats the seed as a normal Phase 0 output and builds against it.

### Rebaseline: consolidating a revised world (`--rebaseline`)

There is one conversion where *nothing* is replaced: your world has been through enough revisions (R1…R6, say) that the Master Design and drafts are layered with `<!-- REVISED IN R[N] -->` markers, the original `World_Seed.md` is six revisions stale, and the next thing you want to add is structural enough that another surgical revision feels wrong. That is **Rebaseline mode**:

```
/worldforge convert path/to/Lucifer path/to/Lucifer-clean --rebaseline
```

Same world, same protagonist. The Converter takes your original `World_Seed.md` as the base — everything a revision never touched carries **1:1, in your own words**, never paraphrased — then reads every `Revision_R*.md` report against the *post-revision* `Master_Design.md` and writes each revision's effect into the affected seed passage in place. Everything a regular conversion always regenerates — Section 3 (protagonist), Section 5 (arcs), the test scenarios — carries forward the same way. Anything the build added after Phase 0 that no revision explains (answers you gave the Refiner, arcs that grew past the seed's sketch) gets *surfaced*, and you decide per item whether it folds into the seed or gets re-elicited in the rebuild — nothing is silently kept or silently lost. (If you'd rather have the seed re-derived from the post-revision Master Design — say your original seed was thin, or the world has long outgrown its wording — pass `--distill`; a source with no `World_Seed.md` falls back to the same distillation with your confirmation, announced up front.) Revision *content* carries; revision *markers* don't. New mechanics you're introducing go in at seed level, marked `<!-- NEW IN REBASELINE -->`. Then `/worldforge skip phase0` rebuilds the world clean, and the new project's revision counter starts over at R1.

**The one real cost:** the rebuild compiles fresh UIDs, so running SillyTavern chats against the old package don't migrate — the old Export/ stays playable as-is, but the rebuilt world is a fresh import with fresh chat state. If you want running chats to survive, stay with `/worldforge revise`. Full mode spec: `agent_roles/Converter/00_The_Converter.md` Section 9.

**If the rebaseline is a staging step** — you're consolidating *because* something bigger is coming — add `--then-interview`:

```
/worldforge convert path/to/Lucifer path/to/Lucifer-clean --rebaseline --then-interview
```

After writing the consolidated seed, the Converter hands off into the **Interviewer in seed-revision posture** instead of `skip phase0`: it plays the world back to you, asks what you want to change, and interviews just those changes at full Phase 0 depth — including the cascade (rework an arc and it will re-elicit that arc's relationship drift, trauma trajectory, and intimate function lines). Changed sections get marked, the Interviewer signs off below the Converter, and the standard pipeline proceeds from Phase 1.

**If you know you want to change the world but not yet *what*,** use `--then-brainstorm` instead:

```
/worldforge convert path/to/Lucifer path/to/Lucifer-clean --rebaseline --then-brainstorm
```

This inserts the **Brainstormer in improvement posture** ahead of the Interviewer. It reads the consolidated seed, plays the world back, and brainstorms improvement directions *with* you — a new mechanic, an arc rework, a character to deepen, a tonal turn — generating options the way it does for a fresh world, but pointed at the world you already have. And if you have a standing `Big_Brain_Storm.md` from earlier `brainstorm --improve` sessions (Section 9), this is when those parked ideas come due: the Brainstormer notices the file in the source project and *asks* whether to fold them in — endorsed ideas land in the notes with attribution, and the curated file is carried forward to the new project folder so your idea pool follows the world (the source copy stays untouched; even without either `--then-` flag, a plain `--rebaseline` will surface the file and offer the same routing). It writes informal `Brainstorm_Notes.md` (never the seed), and the chain continues into the seed-revision Interviewer, which reads those notes as *proposals*: it leads with them, you refine them in discussion, and the endorsed ones get interviewed into seed edits at full depth. The Brainstormer keeps you honest about scope — an idea that would flip the World Mode, swap the protagonist, or overturn the core concept is a *reframe* (a regular `/worldforge convert`), not a rebaseline improvement, and it'll say so. `--then-brainstorm` requires `--rebaseline` and supersedes `--then-interview` (the interview always follows the brainstorm). And if you just want to explore ideas against a world *without* consolidating or committing to anything, the same improvement posture runs standalone as `/worldforge brainstorm --improve` — see Section 9.

---

## 9. Brainstorming a world (`/worldforge brainstorm`)

Everything so far assumes you arrive with a concept solid enough for the Interviewer to interrogate. Sometimes you don't — you have a vibe, an image, a single character, a "what if," and nothing with a shape yet. The **Brainstormer** is the optional front porch for that state. It is the Interviewer's divergent counterpart: where the Interviewer converges (walks the template, pushes for specificity, refuses thin material), the Brainstormer diverges (throws out options, follows whatever you light up on, helps an idea find its own shape). It writes informal `Brainstorm_Notes.md` — explicitly *not* a World Seed — and hands you to `/worldforge start`, where the Interviewer reads those notes as a warm start and still runs the full interview.

```
/worldforge brainstorm
```

It is entirely optional and skippable — if you already know what you're building, go straight to `/worldforge start`.

### It makes suggestions, not just prompts

The Brainstormer is built to be *proactive*. Rather than only asking questions, it offers material:

- **Touchstones, not just adjectives.** Hand it a genre or mood and it reaches for the works that own that territory: "a horror sandbox in a small neighborhood" is Stephen King country — ordinary streets with something wrong humming underneath. It names the touchstone *and* describes its texture, so it lands whether or not you know the work, and it offers two or three so you can feel which direction has heat.
- **Excerpt sketches.** When a register is hard to describe, it writes a few lines of the world's prose in the tone it's proposing and asks if that's warmer or colder than what you meant.
- **Cast on request.** Ask "who else is in here?" and it generates a handful of distinct candidates with a hook each, rather than handing the question back.
- **Clichés, dodged but offered.** It steers toward the fresher angle by default, but tropes are tools — when it steers around one it says so and offers the familiar version too, because the well-worn path is often the easier build. You choose.
- **"Where does it sag?"** It will play a premise forward and name where it tends to go flat (a sandbox with no internal pressure becomes a diorama; a one-note antagonist gets boring by the third scene), then offer ways to firm it up. This is a sounding board, not a verdict — it never scores your idea.

### The six domain lenses

When a brainstorm turns toward a domain where ideas reliably go generic, the Brainstormer pulls in a matching **lens** — craft grounding that sharpens its suggestions away from cliché. The lenses produce *leanings for the notes*, never locked content; the downstream agents still do all the authoring.

| Lens | Guards against | Example nudge |
|---|---|---|
| **Intimacy & Dynamics** | interchangeable, generic sex scenes | make a scene fit the *specific pair* — a shorter man and a taller woman reshapes the staging and the power play |
| **Appearance & Style** | the default body-type cliché | "a curvy distance runner" is in tension — distance running builds a lean frame; want yoga instead, or keep the body and call it genetics? |
| **Realism** | hand-wavy mechanics | a team chasing the World Cup can't train 24/7 — injuries, recovery, and politics are where the stakes live. (Genre-aware: it steps aside for power-fantasy, where "realism" becomes internal consistency.) |
| **Character Psychology** | the flat archetype | a "cold crime boss" is a costume — what does he *want* underneath, and what's the one line he won't cross, or already crossed? |
| **World & Factions** | the world as generic backdrop | a faction is an agenda, not a hat — what is the Merchant Guild *doing this month*, and whose plans does it wreck? A tension that resolves in one session isn't an engine; scarcity, rivalry, or occupation regenerate forever |
| **Cast & Voice** | interchangeable NPCs orbiting `{{user}}` | if two characters would react identically to the same event, one is redundant — and strip the names off three lines of dialogue: can you tell who said what? |

The appearance/realism nudge is a coherence check, not a rule: it surfaces the tension once, offers the resolutions, and drops it the moment you choose — "curvy and genetically gifted" is a complete answer.

### Four postures

The Brainstormer runs in one of four modes depending on how it's invoked:

1. **Fresh start** (`/worldforge brainstorm`) — the default above: a blank page and a vibe.
2. **Improvement** — brainstorming *changes* to a world you already have. Two doors: chained after a rebaseline (`/worldforge convert ... --rebaseline --then-brainstorm`, covered in [Section 8](#8-converting-a-shipped-world-worldforge-convert)) or standalone (`/worldforge brainstorm --improve`) — the no-commitment sounding board, two subsections down.
3. **Revision diagnostic** (`/worldforge revise --brainstorm`) — the subsection after next.
4. **Adaptation** (`/worldforge brainstorm --adapt <document>`) — turning an existing story, fanfiction, or roleplay log into a precursor for a world. The next subsection.

### Turning a story into a world (`/worldforge brainstorm --adapt`)

Sometimes you don't arrive with a vibe — you arrive with a *document*. A short story you wrote, a fanfiction you love, a transcript of a roleplay that went somewhere good. It already has a world in it: characters, a setting, a tone. What it doesn't have is a *you* — it was written as a story to read, not a world to play in.

```
/worldforge brainstorm --adapt ./my_story.md
```

This runs the Brainstormer in its **adaptation posture**. It reads the document once, plays the world back to you (setting, tone, cast, the central tension), and then goes straight to the question the document can't answer for you: **who do you want to *be* in this world?** A story has a fixed protagonist; a roleplay world needs a player slot. It reads the document's POV and *recommends the natural fit* — tight first-person from one character → play as them; an ensemble with no single anchor → drop in as someone new and let the old protagonist become an NPC (often the richest option, since they're already deeply drawn) — explains the cascade the choice triggers, and confirms with you. You can always override; the recommendation just removes the cold-start guesswork. From there it diverges on everything else the document left open: World Mode, the arc or sandbox shape, NPC agency, and anywhere the source is too thin to live in.

Because the document is a *finished sample*, it also extracts the things you most likely want replicated: the **prose style** (perspective, tense, register, rhythm, and pacing — raw material for your Style Contract), **how each character speaks** (a voice fingerprint plus a verbatim sample line or two lifted straight from the text), and, if the source has sex, the **intimate register** (the dynamics, explicitness, and any kinks or fetishes the page actually shows — raw material for the Intimacy Architect in Phase 2.5). It extracts only what's on the page and *attributes it to the source* — it won't invent a hidden wound, or a kink, the story never showed; it flags those as gaps for the Interviewer to dig on instead. The output is an `adaptation`-stamped `Brainstorm_Notes.md`: the extracted world, the prose sample, the intimate register, your `{{user}}`-slot decision, and the list of gaps to fill. Hand it to `/worldforge start` exactly like any other brainstorm — the Interviewer reads it as a (richly furnished) warm start and still runs the full interview, leaning on the prose and intimate samples as confirmed starting points and pushing hardest on the interiority and stakes the document didn't supply. As always, it writes only notes, never a seed, and never edits or continues your document.

### Testing ideas against an existing world (`/worldforge brainstorm --improve`)

Revision assumes you've already decided something should change; `revise --brainstorm` (next subsection) assumes something already feels *wrong*. But sometimes you're just carrying ideas with no commitment behind them — "would a rival faction fit this world?", "should Anna's arc go deeper?", "could the market district be made better?" — and what you want is a sounding board, not a pipeline.

```
/worldforge brainstorm --improve
```

This runs the Brainstormer's **improvement posture standalone** — the same conversation `--then-brainstorm` chains after a rebaseline (Section 8), but with no conversion in front of it and nothing dispatched after it. It reads your world's current state read-only (`Master_Design.md` with its Revision Log if the world is built; the `World_Seed.md` if not), plays it back, and then ping-pongs: pitch it your ideas and it yes-ands, expands, pressure-tests ("where does it sag?"), and offers alternatives; arrive empty-handed and it asks what's pulling at you and generates directions. It respects the world's spine — an idea that would flip the World Mode, replace the protagonist, or overturn the core concept gets named plainly as `/worldforge convert` territory rather than dressed up as an improvement.

It ends by parking everything in **`Big_Brain_Storm.md`** — a *standing* idea file, separate from the run-scoped `Brainstorm_Notes.md`, so it survives between sessions: run `--improve` again later and the Brainstormer plays your still-open ideas back and curates the file forward instead of starting from amnesia. And the parked ideas flow organically into the pipeline when you're ready: the next time you run `/worldforge revise --brainstorm`, the Brainstormer notices the file and *asks* whether to fold those ideas into the diagnosis — if one of them is the change you want, it adapts it into the notes the Reviser scopes. The same pickup fires on a rebaseline (Section 8): a `--rebaseline --then-brainstorm` chain offers the parked ideas and carries the curated file forward to the new project, and even a plain `--rebaseline` surfaces the file's existence and lets you route it. You can equally take an idea straight through a door yourself — `/worldforge revise` for a surgical change to a built world (state the change as your intent; the Reviser never reads `Big_Brain_Storm.md` directly), seed edits or the seed-revision interview for a world not yet built, `/worldforge convert` for the structural stuff. And if nothing lands, the ideas just stay parked — exploration is the point.

### "Something feels off but I can't name it" (`/worldforge revise --brainstorm`)

The revision pipeline (`/worldforge revise`, Section 7's retrofitting note) assumes you can name what to change — "Anna's voice is too snarky in Arc 2," "add an NPC to the market district." But sometimes a shipped world just feels *off* in play and you can't point at why. That's the pre-articulation case, and grinding through the Reviser's narrowing questions doesn't help when you have no starting noun.

```
/worldforge revise --brainstorm
```

This runs the Brainstormer in its **revision-diagnostic posture** *before* the Reviser. It reads your `Master_Design.md` read-only, plays the world back, and asks what bugged you in the last session — and if you have a standing `Big_Brain_Storm.md` from earlier `brainstorm --improve` sessions, it asks whether to fold those parked ideas into the diagnosis (a felt concern and a parked idea are often the same thing seen from two sides). Then it diagnoses divergently, using the six lenses in reverse as a diagnostic vocabulary (a scene that fell flat → the psychology lens; samey intimate beats → the intimacy lens; an arc with no pressure → the "where does it sag" move; a world that plays like a backdrop → the world & factions lens; NPCs who all sound the same → the cast & voice lens). It converges on **one primary concern**, phrased as a revision intent, plus a few candidate future concerns, and writes them to `Brainstorm_Notes.md`. The Reviser then reads that file, captures the primary concern as your verbatim intent, and classifies and scopes the revision as normal.

It respects the same bright line as the Reviser: if the thing that's "off" turns out to be the world's core concept, tone, Style Contract, or World Mode, it says so and points you to a full re-run or a `/worldforge convert` rather than dressing a structural change up as a surgical one. And like every Brainstormer posture, it writes only informal notes — it never classifies tiers or scopes the revision itself. That stays the Reviser's job.

---

## 10. Command reference — every trigger, by example

This section collects every `/worldforge` command in one place, each with an example invocation, what it does, and *why* you would reach for it. The examples reuse the Lucifer project (Section 3) for continuity. Two conventions throughout:

- **Paths point at project folders** — the directory that holds `World_Seed.md`, `Drafts/`, and `Export/` — not at individual files, except where a flag explicitly takes a file (`--brief`, `--target`).
- **You type these in your agentic extension's chat** (the **Code** agent in Kilo Code, or the default agent in Cline), with the World-Forge repo open as the workspace.

A run moves left-to-right through a lifecycle: *(optional) brainstorm → start/skip → resume/skip while building → ship → revise / resync-preset / convert / audition after launch.*

### 10.1 Starting a build

**`/worldforge brainstorm`** — *optional, before everything*
```
/worldforge brainstorm
```
Divergent ideation for when you have only a vibe. Generates premise directions, reaches for touchstones, sketches excerpts, and pulls in the six domain lenses (Section 9). Writes informal `Brainstorm_Notes.md` and stops — it never writes a World Seed.
**Why:** use it when you can't yet answer the Interviewer's "what's the central wound?" because the idea has no shape. Skip it when you already know what you're building.

**`/worldforge brainstorm --adapt <document>`** — *optional, before everything; you have a story, not a vibe*
```
/worldforge brainstorm --adapt ./my_story.md
```
Reads an existing narrative document (a story, fanfiction, or roleplay log), extracts the world latent in it (cast, setting, tone), and diverges on the gap to a playable world — above all the `{{user}}` slot the document's fixed POV can't supply. Writes an `adaptation`-stamped `Brainstorm_Notes.md` the next `start` reads as a warm start; never writes a World Seed and never edits your document.
**Why:** use it when the world you want already exists in something you've read or written, and you want to *play in* it rather than build from a blank page. See Section 9.

**`/worldforge brainstorm --improve`** — *any time a world exists; ideas, not yet changes*
```
/worldforge brainstorm --improve
```
Runs the Brainstormer's improvement posture standalone against a world you already have (seed-only or shipped): reads its current state read-only (`Master_Design.md` if built, else `World_Seed.md`), ping-pongs your ideas — fit, additions, reworks — pressure-tests them, and parks the results in the standing `Big_Brain_Storm.md` (curated forward across sessions, separate from `Brainstorm_Notes.md`). Commits you to nothing; a later `revise --brainstorm` or a rebaseline `--then-brainstorm` chain offers to pick a parked idea up, or take one through `revise` / `convert` yourself.
**Why:** you want a sounding board against an existing world without opening a revision or a conversion. If something already feels *wrong* and you can't name it, that's `revise --brainstorm` instead (Section 10.3).

**`/worldforge start`** — *the normal entry*
```
/worldforge start
```
Begins at Phase 0 (the Interviewer) in **arc mode** — the default. The Interviewer walks the World Seed Template, pushes back on thin material, and produces `World_Seed.md`. If `Brainstorm_Notes.md` is present it's read as a warm start.
**Why:** the standard path for nearly every new world.

**`/worldforge start --sandbox`** — *open-ended worlds*
```
/worldforge start --sandbox
```
Same as `start`, but pre-sets **sandbox mode** (Section 7): no narrative arcs, a single always-active Sandbox Lorebook, and a large principal/roster NPC cast. The `World Mode: sandbox` field in the seed is the real source of truth, so this flag just pre-seeds it for the Interviewer.
**Why:** power-fantasy, world-director, and life-sim worlds where you "live in" the world rather than move through a story.

**`/worldforge skip phase0`** — *you wrote the seed yourself*
```
/worldforge skip phase0
```
Begins at Phase 1 (the Refiner), assuming you authored `World_Seed.md` by hand against `templates/World_Seed_Template.md` — the way the Lucifer sample was built.
**Why:** you have a fully-formed concept and prefer writing the seed directly to being interviewed — or you're resuming after a Section 1 / 11a revision bounced out of the revise pipeline.

### 10.2 Controlling a run in flight

**`/worldforge status`**
```
/worldforge status
```
Reports the current phase, round, and any open blockers, read from the Pipeline State Ledger at the top of `Master_Design.md` (not reconstructed from memory).
**Why:** any time you're unsure where a paused run actually stands.

**`/worldforge resume phase[N]`**
```
/worldforge resume phase1      # after answering UNRESOLVED_QUESTIONS.md
/worldforge resume phase2.5    # after filling in Section 8 intimacy detail
/worldforge resume phase3      # re-enter the Editor loop
/worldforge resume phase5      # re-run the Prompt Engineer audit
```
Resumes from a specific phase after a pause gate. Valid phases: `phase0, phase1, phase2, phase2.5, phase3, phase3.5, phase3.6, phase3.7, phase4, phase5`.
**Why:** continue after you've resolved whatever caused a pause — a Refiner gap, an Editor stall, an intimacy blocker.

**`/worldforge skip phase2.5` · `skip phase3.6` · `skip phase3.7`**
```
/worldforge skip phase2.5   # no intimate content — skip the Intimacy Architect
/worldforge skip phase3.7   # no intimate content — skip the Intimacy Auditor
/worldforge skip phase3.6   # arc-seam auditor; auto-skipped in sandbox mode anyway
```
Tells the orchestrator a conditional phase doesn't apply, instead of letting it ask. The two intimacy phases (2.5 and 3.7) are skipped together for worlds with no intimate content; the Arc Transition Auditor (3.6) is auto-skipped in sandbox mode.
**Why:** declare up front that a conditional phase is irrelevant to this world.

### 10.3 Post-launch: surgical edits (`/worldforge revise`)

Once a world has shipped (Export/ exists), the revision pipeline makes small, scope-locked changes. It preserves UIDs, so running SillyTavern chats survive the edit. The bright line: anything touching the world's Core Concept / tone (Master Design Section 1) or Style Contract world defaults (Section 11a) — including an arc↔sandbox flip — bounces to a full re-run or a `convert`.

**`/worldforge revise`** — *interview mode (default)*
```
/worldforge revise
```
The Reviser asks what feels off, narrows it to one concern, classifies the scope, runs the bright-line check, and writes a Revision Log entry.
**Why:** you know roughly what's wrong and want to be walked through pinning it down.

**`/worldforge revise --freeform`** — *you'll describe it yourself*
```
/worldforge revise --freeform
```
You paste a description of the change; the Reviser structures and classifies it, then echoes its interpretation back for confirmation.
**Why:** you can state the change in a sentence or two and don't need the interview.

**`/worldforge revise --target [path]`** — *you know the file*
```
/worldforge revise --target Drafts/Tier2_Anna_Entries.md
```
Skips diagnostic narrowing and goes straight to "what's wrong with this file, and what should it become?"
**Why:** you've already located the exact draft entry to change.

**`/worldforge revise --brainstorm`** — *something feels off, but you can't name it*
```
/worldforge revise --brainstorm
```
Runs the Brainstormer's revision-diagnostic posture (Section 9) first: it reads `Master_Design.md` read-only, plays the world back, offers to fold in parked ideas from a standing `Big_Brain_Storm.md` if you have one, diagnoses divergently with the lenses, and writes one primary concern to `Brainstorm_Notes.md` — which the Reviser then picks up and scopes.
**Why:** play feels wrong but you have no starting noun to hand the interview. (If you're carrying *ideas* rather than a symptom — "would X fit?" — use `/worldforge brainstorm --improve` instead; it commits you to nothing and this command will offer to pick its parked ideas up later.)

**`/worldforge revise status` · `resume R[N]` · `cancel R[N]`**
```
/worldforge revise status        # list all revisions and their statuses
/worldforge revise resume R3     # continue pending revision R3 from its last phase
/worldforge revise cancel R3     # cancel R3, roll back its draft edits, mark CANCELLED
```
Manage in-flight or past revisions. `R[N]` is the revision id from the Revision Log (R1 is the first revision; the initial build is unnumbered).
**Why:** `status` checks for a pending revision (only one runs at a time); `resume` continues after a pause; `cancel` abandons one cleanly.

### 10.4 Post-launch: refresh the preset (`/worldforge resync-preset`)

```
/worldforge resync-preset
```
Regenerates a shipped world's `Export/[WorldName]_ChatPreset.json` against the current preset template and block library, picking up pipeline improvements and any content changes that surface inside preset blocks. It makes **no content changes** and touches only the preset — re-importing it does not disturb running chats, because a preset is a global settings profile, not UID-bearing world info.
**Why:** the pipeline's preset spec has evolved since you built the world, or revisions changed content that should reflect in preset blocks. This is *not* `resume phase5` — that re-runs the full Phase-5 audit during an in-progress build; resync is a maintenance op on an already-shipped world.

### 10.5 Post-launch: reframe or consolidate (`/worldforge convert`)

Convert reads a shipped world read-only and writes a *new* `World_Seed.md` to a target folder — the legitimate path for the big changes the revise pipeline bounces (different protagonist, World Mode flip, Style Contract or Core Concept change). The full walkthrough is Section 8; here are the invocations side by side.

**`/worldforge convert <source> <target>`** — *reframe (interactive)*
```
/worldforge convert path/to/Lucifer path/to/Lucifer-as-God
```
Interviews you through the preservation matrix (keep / modify / drop / regenerate per source section), surfaces role reassignments, and writes the new seed. You then run `/worldforge skip phase0` against the target.
**Why:** play the same world from a different angle — e.g., Lucifer's world as God instead of Anna's foil. (Replacing setting + protagonist + factions + tone all at once is refused — that's a new world, use `start`.)

**`--brief <path>`** — *reframe (brief-driven)*
```
/worldforge convert path/to/Lucifer path/to/Lucifer-as-God --brief path/to/Convert_Brief.md
```
Drives the conversion from a pre-filled `templates/Convert_Brief_Template.md` instead of a live interview; it still interviews you on gaps and ambiguities.
**Why:** non-trivial conversions you want version-controlled and reviewable.

**`--rebaseline`** — *consolidate a revised world*
```
/worldforge convert path/to/Lucifer path/to/Lucifer-clean --rebaseline
```
Same world, same protagonist: rebuilds a clean seed when accumulated revisions have made surgical editing unwieldy — your original `World_Seed.md` carries 1:1, with each revision's effect applied in place and post-seed drift surfaced for your decision. Revision content carries; revision markers don't. Combines with `--brief`.
**Why:** a world is layered with `<!-- REVISED IN R[N] -->` markers and the next change feels too big for another surgical revision. **Trade-off:** the rebuild compiles fresh UIDs, so running chats don't migrate — that's the price of a clean baseline; `revise` is the UID-preserving alternative.

**`--rebaseline --distill`** — *consolidate, but re-derive the seed*
```
/worldforge convert path/to/Lucifer path/to/Lucifer-clean --rebaseline --distill
```
Skips the 1:1 carry and distills the seed fresh from the *post-revision* Master Design instead. Requires `--rebaseline`.
**Why:** your original seed was thin, or the world has outgrown its wording so far that you'd rather keep the Master Design's developed articulation than your Phase 0 text. **Trade-off:** every section gets re-worded through summarization — the 1:1 fidelity of a normal rebaseline is exactly what you're opting out of.

**`--rebaseline --then-interview`** — *consolidate, then change a lot*
```
/worldforge convert path/to/Lucifer path/to/Lucifer-clean --rebaseline --then-interview
```
After writing the consolidated seed, hands straight into the Interviewer (seed-revision posture) to interview your changes at full depth before Phase 1, instead of `skip phase0`. Requires `--rebaseline`.
**Why:** the consolidation is a staging step and you already know what you want to change.

**`--rebaseline --then-brainstorm`** — *consolidate, then decide what to change*
```
/worldforge convert path/to/Lucifer path/to/Lucifer-clean --rebaseline --then-brainstorm
```
Inserts the Brainstormer (improvement posture) ahead of that Interviewer: it brainstorms *what* to change against the consolidated world — offering parked ideas from a standing `Big_Brain_Storm.md` if you have one, and carrying the curated file forward to the new project — writes `Brainstorm_Notes.md`, and the seed-revision Interviewer reads those as proposals. Requires `--rebaseline`; supersedes `--then-interview`.
**Why:** you want to evolve the world but haven't decided how.

### 10.6 Post-launch: probe a character (`/worldforge audition`)

You're mid-session in a shipped world and a question comes up that's too subtle to answer from memory: would this character actually *do* that, right now, given everything currently true about them? `/worldforge audition` answers it cheaply, without gambling a real scene to find out.

```
/worldforge audition
```

Invokes **the Auditioner** (`agent_roles/Auditioner/00_The_Auditioner.md`) — not a numbered pipeline phase, a standalone probe you can run any time after launch. You hand it one character, one scene, and the active conditions (which arc is live, or the standing sandbox state — plus the named ladder stage, if the NPC has one); it simulates the scene as the model would actually run it and returns one of three verdicts:

- **YES** — the spec reliably produces the behavior you expected.
- **NO** — the spec is fine, it just drives a *different* behavior than you expected.
- **IT DEPENDS** — the spec is silent or self-conflicting here, so the outcome isn't determined. This is a coverage gap surfacing on demand.

It is read-only end to end — it never touches `Drafts/`, `Export/`, or `Master_Design.md`. If it finds a real gap, it hands you a **revise handle** (the file, the element, the kind of change) rather than applying anything itself; you decide, and `/worldforge revise` is what actually makes the edit.

```
/worldforge audition --save
```

Same probe, but also writes the result to `Drafts/Audition_[Char]_[slug].md` as an informal, durable log — read by nothing downstream, safe to delete any time.

**Why:** it's the single-scenario, on-demand cousin of the Voice Auditor (Phase 3.5) — same simulation discipline and check vocabulary, applied to exactly the one situation you're curious about instead of a systematic build-time matrix across the whole cast. Reach for it whenever play raises a "would they really..." question you don't want to answer by trial and error.

---

## 11. Setting your prose style (the Style Contract)

World Forge has no house voice. It does not decide what good prose is, and it does **not** strip "slop" — what reads as overwrought to one person is another's register. Instead, **you declare the world's prose conventions once**, in World Seed **Section 1.5 (the Style Contract)**, and every card in the world inherits them. (A Director/Narrator card can override perspective — Section 1.5c — but most worlds set the contract once and never override.)

The Style Contract has six enum fields plus one free-text field:

| Field | What it controls |
|---|---|
| **Perspective** | `first` / `second` / `third_limited` / `third_omniscient` |
| **Tense** | `past` / `present` |
| **Narration Marker** | what `*asterisks*` mean: narration+action, thoughts-only, or none |
| **Dialogue Marker** | `double_quotes` / `single_quotes` / `em_dash` / `unmarked` |
| **Emphasis Marker** | `double_asterisks` / `italics_underscore` / `none` |
| **Paragraph Register** | `terse` / `standard` / `dwelling` |
| **Style Notes** (free text) | anything the enums don't capture |

The six enums pick the *mechanics* (POV, tense, what the markup means). The seventh — **Style Notes** — is where you steer the *feel*: contractions or not, modern idiom or not, and what you do or don't want the prose to do.

### What `DEFAULTS` does

If you don't care about prose style, write `DEFAULTS` for each field and the Refiner fills in the pipeline's legacy convention:

```text
Perspective:        third_limited      (only {{char}}'s interior is visible)
Tense:              past
Narration Marker:   asterisks_for_narration   (*asterisks* wrap narration + action)
Dialogue Marker:    double_quotes      ("Like this.")
Emphasis Marker:    double_asterisks   (**like this**)
Paragraph Register: standard
Style Notes:        (none)
```

This is the classic novelistic register — third-person limited, past tense, action and narration inside asterisks, dialogue in quotes. It's a safe default for most worlds and it's what the Lucifer sample runs under. A turn under this contract reads like:

> *She set the cup down without looking at him, her shoulders held too still.* "I wasn't expecting you tonight."

### Example: a more direct, "typical roleplay" register

If you want prose that reads less like a literary novel and more like how chat roleplay usually looks — tighter, present-tense, less ornament — set the contract explicitly instead of taking `DEFAULTS`:

```text
Perspective:        second             (addresses you as "you" in the prose)
Tense:              present
Narration Marker:   asterisks_for_narration
Dialogue Marker:    double_quotes
Emphasis Marker:    double_asterisks
Paragraph Register: terse              (short paragraphs, dense, fast)
Style Notes:        Keep the prose direct and concrete. Prefer plain statements
                    over poetic phrasing — "his hand is shaking" rather than "a
                    tremor betrays the weight he carries." Avoid antithetical
                    "X, not Y" / "not X but Y" constructions. No purple metaphor;
                    one sensory detail per beat is enough.
```

That produces the punchy, second-person-present, action-in-asterisks style most roleplay uses, and the Style Notes steer it away from the literary tropes the enums can't express on their own:

> *She sets the cup down and meets your eyes.* "You're early." *A beat. Her jaw tightens.* "What do you want?"

### Tuning the feel with Style Notes

The six enums can't capture everything about *voice*. **Style Notes is free text that flows into the world's Main Prompt**, so it's where you put preferences the enums miss:

- **Plainness / anti-"slop":** *"Prefer concrete, factual phrasing over poetic abstraction; avoid 'X rather than Y' and 'with the X of someone who Y' constructions."*
- **Register quirks:** *"The narrator never uses contractions."* · *"Prose avoids modern idiom in the pre-modern arcs."*
- **Mixed markup:** *"Internal monologue uses `_italics-underscore_` even though dialogue uses `double_quotes`."*

Two things worth knowing:

- **This is the supported way to control "slop."** World Forge carries no opinion about tropes or clichés. If you want them avoided, *name them here* — the more concrete your examples, the better the model holds the line. There is no separate trope-removal pass by design; the contract is the lever.
- **Style Notes governs runtime narration** — the prose the model generates as it plays. It's the knob for how your *sessions* read, not a cleanup pass over the lorebook text.

### Where this gets applied

You set the contract in Section 1.5 of the World Seed — the Interviewer asks for it in Phase 0, or you fill it in directly on a `skip phase0` build. From there the Refiner validates the enum values and records them in the Master Design, the Prompt Engineer parameterizes the preset's Main Prompt from them, and the Architect emits per-card overrides for any Director/Narrator card that declares one. By the time you import into SillyTavern, your style choices are baked into the preset that drives every turn.

---

## 12. Where to learn more

- `README.md` — high-level overview of what the pipeline produces and how the architecture is organized
- `workflows/world-forge.md` — the pipeline router: dispatch protocol, state ledger, pause gates, and trigger commands; the phase-by-phase definitions live in the four stage files (`workflows/world-forge-discovery.md`, `-drafting.md`, `-validation.md`, `-construction.md`) and the post-launch operations in `workflows/world-forge-postlaunch.md`
- `workflows/world-forge-revise.md` — the revise pipeline (surgical post-launch edits, R0–R5.5)
- `workflows/world-forge-convert.md` — the convert pipeline (reframe a shipped world into a new build, C0)
- `agent_roles/*.md` — the actual specification each agent runs against (read these if you want to know what an agent will or will not do)
- `Notes_On_functionality.md` — authoritative reference for SillyTavern's runtime behavior (position values, lorebook scanning, prompt assembly, override mechanics)
- `CLAUDE.md` — standing context for AI agents working on the repo itself; useful if you want to extend or modify the pipeline
- `templates/World_Seed_Template.md` — the blank template you fill in for a new world (or that the Interviewer fills in for you)
- `templates/User_Persona_template.md` — the structural reference for `User.md`
- `templates/Convert_Brief_Template.md` — the preservation matrix as a fillable brief, for brief-driven conversions
- `agent_roles/Auditioner/00_The_Auditioner.md` — the on-demand behavioral probe invoked by `/worldforge audition` (Section 10.6)
