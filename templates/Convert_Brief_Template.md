# 🔄 CONVERT BRIEF: [SOURCE WORLD NAME] → [NEW WORLD NAME]
*Input document for the World Forge **Converter** (Phase C0). Optional — the Converter can also run interactively, but a Brief is recommended for non-trivial conversions because it is version-controllable and reviewable.*

---

## HOW TO USE THIS TEMPLATE

This Brief tells the Converter what to **keep**, what to **modify**, and what to **regenerate** when reframing an existing shipped world into a new build. The Converter reads it, validates it against the source world's `Master_Design.md`, asks clarifying questions where the Brief is silent or ambiguous, and writes a new `World_Seed.md` that goes through the standard pipeline via `/worldforge skip phase0`.

Fill in every section below. Delete instructional text in brackets before submitting. Leave section headers intact — the Converter uses them as navigation anchors.

**Important:** This Brief is *not* a World Seed. It is a delta description. The new World Seed is produced by the Converter from this Brief plus the source world's content. Do not author Tier 1, Tier 2, or Tier 3 content here; declare what you want done with the *source's* content and provide the new protagonist's psychological frame.

**When NOT to use the Converter:** if you are changing **setting + protagonist + factions + tone** all at once, you are not converting — you are building a new world that takes inspiration from the source. Use `/worldforge start` against a fresh project folder instead. The Converter will refuse a four-axes-replaced Brief.

**Rebaseline mode:** if you are changing *nothing structural* — same protagonist, same World Mode, same tone — and want to consolidate accumulated revisions into a clean rebuild (optionally adding new mechanics), declare `Operating mode: rebaseline` in Section 1 and invoke with `--rebaseline`. Rebaseline flips this Brief's defaults: Sections 5 and 6 are *kept from the source* instead of authored fresh, and the Section 4e auto-strip reminders invert to carry. The consolidation is **seed-anchored**: your original `World_Seed.md` carries 1:1 — sections no revision touched keep your exact wording — with each applied revision written into the affected passage in place, and any post-seed drift surfaced for your ask-first decision. If you'd rather have the seed re-derived from the post-revision Master Design (your original seed was thin, or the world has outgrown its wording), pass `--distill` and declare `Rebaseline consolidation: distill` in Section 1; the Converter also falls back to distillation, with your confirmation, if the source has no seed file. See `agent_roles/Converter/00_The_Converter.md` Section 9. The per-section notes below say "*Rebaseline:*" where the rules differ.

---

## 1. SOURCE & TARGET **[REQUIRED]**

**Source project path:** [Absolute or workspace-relative path to the source world's project folder. Must contain `Drafts/Master_Design.md` with REFINER SIGN-OFF and an `Export/` directory.]

**Source world name:** [The name from the source's Master Design Section 1, for clarity.]

**Source World Mode:** [`arc` | `sandbox` — read from the source's Section 1 / Section 9 title]

**Target project path:** [Absolute or workspace-relative path to the new project folder. Should be empty or non-existent; if it contains a `World_Seed.md` already, the Converter will refuse to overwrite without explicit confirmation.]

**Target World Mode:** [`arc` | `sandbox` | `unchanged` — flipping is one of the load-bearing cases the Converter exists for. If flipping, read the SANDBOX MODE section of `workflows/world-forge.md` to understand what that means. *Rebaseline:* must be `unchanged`.]

**Operating mode:** [`reframe` (default) | `rebaseline` — must match the invocation flag. `rebaseline` requires zero axes replaced in Section 3, protagonist included.]

**Rebaseline consolidation:** [`seed-anchored` (default — the source `World_Seed.md` carries 1:1 with revision deltas applied) | `distill` (re-derive the seed from the post-revision Master Design; must match the `--distill` flag) | omit this line in reframe mode]

---

## 2. CONVERSION INTENT **[REQUIRED]**

**In one or two sentences, what is this conversion?** [Example: "Same Lucifer world, but I want to play as God instead of a mortal — same factions, same cosmology, but the moral lens flips." Example: "Keep the modern-Stockholm syndicate world, but rebuild it as a sandbox instead of a four-arc narrative — same cast, same setting, no progression." Rebaseline example: "Six revisions in, the world has drifted from its seed — consolidate everything into a clean rebuild and add the new corruption-economy mechanic." Capture verbatim what you want; the Converter does not paraphrase.]

> [Your intent statement here.]

**New mechanics (rebaseline only):** [What new mechanics or structural content are you introducing in the rebuild — or write `none — pure consolidation`. New material is authored into the seed marked `<!-- NEW IN REBASELINE -->`; the Converter will surface any couplings to existing arcs, characters, or factions. If the new mechanics are big enough to replace an axis, this is a reframe conversion, not a rebaseline. Note: if the source project carries a standing `Big_Brain_Storm.md` (parked ideas from `brainstorm --improve` sessions), the Converter will surface it at this intake regardless of what you write here and offer routing — fold via the `--then-brainstorm` chain, state an idea here directly, or leave it parked.]

---

## 3. OVERLAP FLOOR CHECK **[REQUIRED]**

*The Converter refuses conversions where three or four of these axes are replaced. That isn't a conversion — it's a new world inspired by the source. Mark each axis honestly.*

| Axis | What is the source's value? | What is the new value? | Kept or Replaced? |
|---|---|---|---|
| **Setting** (genre, time period, physical world, cosmology) | [...] | [...] | [`kept` | `replaced`] |
| **Protagonist** (who `{{user}}` is) | [...] | [...] | [`kept` | `replaced`] |
| **Factions** (the named power structures) | [...] | [...] | [`kept` | `replaced`] |
| **Tone** (grimdark / noir / lighthearted / etc.) | [...] | [...] | [`kept` | `replaced`] |

**Axes replaced (count):** [0 | 1 | 2]

*If you wrote 3 or 4: do not run the Converter. Run `/worldforge start` against the target folder fresh and use the source as creative reference during the Interviewer session.*

*If you wrote 2: this is borderline. The Converter will flag it and ask you to confirm before proceeding.*

*Rebaseline: the count must be 0 — protagonist included. Any replaced axis reclassifies the run as a regular (reframe) conversion; the Converter will announce it and ask.*

---

## 4. PRESERVATION DECISIONS **[REQUIRED]**

*For each row, declare what you want done with the source's content. Refer to the source's `Master_Design.md` if you need to remember what's there. The Converter validates your decisions against the source before writing the seed.*

### 4a. World rules / cosmology / mechanics (Section 2 — Tier 1)

[`keep` | `modify` | `regenerate`]

[If `modify`: list which specific rules change and how. Example: "Keep all rules except Rule 3 (magic interacts with iron) — replace with: Rule 3 (magic interacts with prayer). Keep everything else verbatim."]

### 4b. Factions (Section 2c)

[Per-faction disposition. List every faction from the source Master Design and mark each:]

- **[Faction name 1]:** [`keep` | `modify: <description>` | `drop`]
- **[Faction name 2]:** [`keep` | `modify: <description>` | `drop`]
- [...]

**Reminder:** Even on factions you mark `keep`, the **relationship to `{{user}}`** will be reauthored downstream — the protagonist has changed, so that relationship cannot transfer mechanically. The Converter handles this automatically; you don't need to mark it here.

### 4c. Standing locations (Section 2d)

[Per-location disposition. Often these all stay; flag any that don't make sense under the new protagonist.]

- **[Location name 1]:** [`keep` | `modify: <description>` | `drop`]
- **[Location name 2]:** [`keep` | `modify: <description>` | `drop`]
- [...]

### 4d. Species, types, categories, concepts (Sections 2e, 2f)

[Usually carry across as-is. Flag any that don't fit the new world.]

- [`keep all` | per-entry disposition as above]

**World Calendar (Section 2g) — optional:** [`keep` | `modify: <new start / end / weekday>` | `regenerate` | `drop` | `n/a — source has none`]

[The Scene Tracker date seed (`contracts/WORLD_FORGE_SYNC.md` §5). Keep it if the era is unchanged; regenerate or drop if the new setting's time period differs. *Rebaseline:* keeps by default — it is not protagonist-coupled.]

**Dice Oracle Tables (Section 2h) — optional:** [`keep` | `modify: <which pools / procedures change>` | `regenerate` | `drop` | `n/a — source has none`]

[The Scene Tracker dice-oracle seed (`contracts/DICE_ORACLE.md`; pools, procedures, `mode`/`turns`). Keep it if the conjured-fact situations still apply to the new world; regenerate or drop if the protagonist/setting change makes them irrelevant (a recount pool tied to the old protagonist gets reauthored). *Rebaseline:* keeps by default — it is not tier-coupled.]

### 4e. Major characters (Section 4 — Tier 2)

[For each named character / NPC in the source, declare disposition. The most consequential row in the Brief — the role reassignments live here.]

- **[Character name 1]:** [`keep as-is (same role)` | `role change: was <old role>, now <new role>` | `drop` | `regenerate as someone new`]
- **[Character name 2]:** [...]
- [...]

**If the old protagonist becomes a Tier 2 character**, name the new role explicitly. Example: "Lucifer: role change — was `{{user}}` (protagonist), now principal NPC and primary antagonist." The Converter will surface this as a role reassignment and confirm with you.

**If a source NPC becomes the new protagonist**, mark them `drop from Tier 2` and write the new protagonist's full psychological frame in Section 5 below. The source character's Tier 2 entries will be starting material for the new Section 3 but get reauthored as protagonist-shaped content downstream.

**Reminders for what gets handled automatically inside Section 4 (you do not declare these here):**
- **`Standing Goal`** per principal NPC carries across **only if** the goal doesn't cite the old protagonist or depend on the old protagonist's role / power tier. Protagonist-coupled goals (e.g., "to corrupt {{user}}") get stripped with a reauthor marker; the new build will populate them once the new protagonist's Section 3 lands.
- **`Escalation Ladder`** per laddered principal rides the Standing Goal rule. When the goal carries, protagonist-coupled stages and the collision line (it names `{{user}}` by definition) still get stripped with reauthor markers; protagonist-agnostic stages carry. The *active stage* never carries — it is Tier 3 state and the new build re-places it.
- **`How it drifts (arc worlds)`** per relationship is arc-coupled and always stripped — arcs are being regenerated downstream, so the drift trajectory will be authored fresh.
- **`Operative belief`** per relationship carries across **only** when it's between two preserved characters AND doesn't reference `{{user}}`. Beliefs about `{{user}}` get stripped (`{{user}}` has changed); beliefs between preserved characters whose dynamic shifted because the protagonist changed get surfaced for your decision during the Converter's interview.
- **`Trauma trajectory (arc worlds)`** per intimate character is arc-coupled and always stripped. The base `Trauma map` (trigger + response, no trajectory) carries across normally. Sandbox sources never had a trajectory authored, so this rule is a no-op for sandbox preservation.
- **`Embodied baseline`** per intimate character carries across unchanged — age and body history, build and scale, arousal and recovery mechanics. It describes that character's own body, which a protagonist swap does not alter, so it transfers verbatim including its observable register and its both-directions framing.
- **`Physical dyad`** is a *pairing* property, not a character property, so it splits. Dyads computed against `{{user}}` (height, build, stamina, age gap, experience) are **always stripped with a reauthor marker** — the other half of the pairing has been replaced, which voids every differential. Dyads between two preserved characters carry across unchanged, and are dropped only if a partner is dropped or role-shifted out of the pairing.

***Rebaseline:* the auto-strip rules above invert to carry** — the protagonist and arc spine are unchanged, so Standing Goals, Escalation Ladders (stages, endpoint, collision — with the rebuild starting from the post-revision high-water stage), drift trajectories, operative beliefs, trauma trajectories, and `{{user}}` physical dyads transfer verbatim at their post-revision state (carried from the source seed, with revision deltas applied in place — the Converter's Step D). Relationship-to-`{{user}}` content also carries (same `{{user}}`). The only strip: drift/trauma/ladder lines referencing an arc you are dropping or restructuring via new mechanics.

### 4f. Section 1 — Core Concept & Tone

- **Logline:** [almost always new — the protagonist usually drives the logline. Write the new logline here, or write `new — to be authored in interview` if you'd rather discuss it with the Converter interactively.]
- **Emotional payoff:** [`keep` | `modify: <new payoff>` | `regenerate`]
- **Hard tonal rules:** [`keep` | `modify: which rules change and how` | `regenerate`]

### 4g. Section 1.5a — Style Contract (world defaults)

[Six fields. For each: `keep` or the new enum value. The Converter will validate against the source.]

- **Perspective:** [`keep` | `first` | `second` | `third_limited` | `third_omniscient`]
- **Tense:** [`keep` | `past` | `present`]
- **Narration marker:** [`keep` | `asterisks_for_narration` | `asterisks_for_thoughts_only` | `plain_prose`]
- **Dialogue marker:** [`keep` | `double_quotes` | `single_quotes` | `em_dash` | `unmarked`]
- **Emphasis marker:** [`keep` | `double_asterisks` | `italics_underscore` | `none`]
- **Paragraph register:** [`keep` | `terse` | `standard` | `dwelling`]

[Per-card style overrides (Section 1.5c) are not declared here — they regenerate with the cards they belong to.]

### 4h. Section 8 — Intimacy (world-level)

[`n/a (no intimacy in source or new world)` | `preserve world-level posture and hard rules` | `regenerate world-level posture and hard rules` | `add intimacy where source had none` | `drop intimacy where source had it`]

[If `preserve`: the source's world-level posture and hard rules transfer. Per-character substrate transfers via Section 4e for preserved characters. Per-arc / standing intimate function is always regenerated downstream — those are arc/sandbox-shaped, and the arc/sandbox spine is being regenerated.]

[If `add`: you'll write the world-level intimacy spec during the Converter's interview, or sketch it in Section 6 below.]

[If `drop`: the new seed omits Section 8 entirely. Phase 2.5 and Phase 3.7 will be skipped downstream.]

### 4i. Section 9 — Runtime Directives

[`n/a (source has none)` | `keep` | `modify: which directives change and how` | `drop` | `regenerate`]

[Runtime directives are engine-steering asks recorded in the source's Master Design Section 12 — world-behavior-shaped, so they carry by default. The Converter strips any directive that cites the old protagonist, depends on their power tier, or is scoped `Arc N only` (the arcs regenerate), and marks it for restating. *Rebaseline:* keeps by default.]

---

## 5. THE NEW PROTAGONIST (`{{user}}`) **[REQUIRED — reframe mode]**

*Rebaseline: skip this section — write `rebaseline — protagonist unchanged, carried at post-revision state` and leave the fields blank. The Converter carries Section 3 over 1:1 from the source seed with any revision deltas applied (distilling from the post-revision Master Design only on the `--distill` path or when the source has no seed file).*

*Reframe mode: this section is always new. The Converter will not transfer protagonist content from the source. Even if you are "playing as the source's antagonist" or "playing as a previously-minor character," the protagonist frame must be authored fresh — the Refiner will treat it as Phase 0 Section 3 material.*

*Walk through these with at least one or two sentences each. The Converter will ask follow-up questions in interview mode for any you leave thin; in pure brief mode, thin answers become Refiner gaps in `UNRESOLVED_QUESTIONS.md` downstream.*

**Identity and role:** [Who is the new `{{user}}` in this world? Not their backstory — what is their position, function, what do people see when they look at them?]

**The wound (foundational):** [What happened to this person that shaped everything? The thing they are still inside, not the thing they have processed.]

**The hidden layer:** [What does the new `{{user}}` want that they will not admit to themselves? What are they running from?]

**The contradiction:** [What do they do that contradicts who they claim to be? The gap between self-image and behavior.]

**Power and limits:** [What can the new `{{user}}` do in this world? **And** — equally important — what can they absolutely not do, even if they wanted to?]

**Arc trajectory (arc mode) or standing posture (sandbox mode):** [Arc mode: one sentence per intended arc — what is the protagonist's internal journey across the new story? Sandbox mode: what is the protagonist's standing position in the world, and what kind of life are they living turn-by-turn?]

**Physical description (anatomical order):** [Face and lips, hair, eyes, body, movement and posture, sensory signature.]

**Voice and manner:** [Sentence length, vocabulary, accent if any, what they never say directly. A sample line in their actual voice if you can.]

---

## 6. TEST SCENARIOS (Section 7b) **[REQUIRED — reframe mode]**

*Rebaseline: the source's scenarios carry by default — write `keep` here, or list replacement scenes if the new mechanics warrant them (the Converter will offer a refresh either way).*

*Reframe mode: always new — even if the source had test scenarios, those were for the source's protagonist. Write three to five specific roleplay scenes you intend to play through in the **new** world.*

1. [Scene 1 — be specific. "Tense first meeting with [preserved NPC] in the new protagonist's role" is more useful than "first meeting."]
2. [Scene 2]
3. [Scene 3]
4. [Scene 4, optional]
5. [Scene 5, optional]

[At least one intimate scenario if the new world contains intimate content.]

---

## 7. NOTES FOR THE CONVERTER **[OPTIONAL]**

[Free text. Anything that doesn't fit the structured fields above. Examples:]
- ["The arc 2 mood in the source was too heavy; please thin it out for the new build's arc 2."]
- ["I want the World Pulse in sandbox mode to lean toward political intrigue rather than the source's transactional crime."]
- ["The source's intimate scenes leaned grimdark; I want the new world's intimate scenes to carry the same craft fidelity but with a different thematic weight — communion instead of corruption."]
- ["I noticed [character] in the source had a relationship to the protagonist that drove a lot of the arc 3 beats — be aware that with the protagonist changing, that relationship is gone and arc 3 will need a different driver."]

[Or leave blank.]

---

## 8. SIGN-OFF (you fill this in)

- [ ] Source path verified to contain a shipped world (Master Design with REFINER SIGN-OFF, Export/ present)
- [ ] Target path verified to be empty (no World_Seed.md to overwrite)
- [ ] Overlap floor check filled in honestly (count of replaced axes recorded; rebaseline: 0)
- [ ] Preservation decisions made for every Section 4a–4h row
- [ ] Major characters: each one's disposition decided (no "TBD" entries)
- [ ] New protagonist (Section 5) authored with at least one sentence per field — *or marked `rebaseline — protagonist unchanged`*
- [ ] Test scenarios (Section 6) — three to five written, *or `keep` in rebaseline mode*
- [ ] Rebaseline only: Operating mode declared in Section 1; consolidation declared (`seed-anchored` default, or `distill` matching the `--distill` flag); new mechanics declared in Section 2 (or `none — pure consolidation`); fresh-UID cost understood (running ST chats do not migrate to the rebuild)
- [ ] Notes for the Converter (Section 7) — filled in or explicitly left blank

**When ready, invoke:**

```
/worldforge convert <source_path> <target_path> --brief <path_to_this_brief>
```

The Converter will read this Brief, validate it against the source, ask clarifying questions where the Brief is silent or ambiguous, write the new `World_Seed.md`, and hand off to `/worldforge skip phase0`.
