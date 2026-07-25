# Changelog

All notable changes to the **World Forge** pipeline.

World Forge is a multi-agent pipeline that turns a world idea into a complete
SillyTavern-ready roleplay package — character cards, layered (three-tier)
lorebooks, a `{{user}}` persona, and a tuned Chat Completion Preset — through
staged drafting and auditing for voice, tier integrity, and runtime fidelity.

The pipeline ships as living markdown specifications rather than versioned
software, so entries are grouped by date and pull request rather than release
numbers. Newest first.

---

## 2026-07-25 — `contracts/BODY_CYCLES.md` draft (no pipeline behavior change)

Records a design agreement for a seam that does not exist yet: recurring body
states (a menstrual cycle, a species' estrus, a lunar turn) tracked by the
Scene Tracker as **supplementary per-chat state**, seeded once from the world.

Ownership was the whole design question, and two candidate owners were
rejected. The **model** cannot own it: the cheap version states the parameters
in a lorebook and lets the model compute the phase from an injected day, but
models are unreliable at sustained modular arithmetic over a running counter,
and the failure is silent and self-compounding. A world that tracks nothing is
coherent; one that tracks wrongly is not. The **producer** cannot own it
either: a world file is authored once and played for months across many chats,
so anything that advances per-chat is chat state with no coherent value to
write at build time.

That leaves the Scene Tracker, alongside the state it already tracks by
default (health, location, clothing, mood) — which makes this carrier a
**seed**, read once onto a pristine scene record exactly like
`[[WORLD_CALENDAR]]`, not a payload re-derived every turn. The producer
supplies only two things: the phase shape plus where the character starts, and
a terse one-line behavioral index per phase.

Specified generically (author-defined phases, not a fixed
follicular/ovulatory/luteal vocabulary) so fantasy and non-human biologies fit
the same mechanism and the consumer needs no domain knowledge. Phases carry
**durations rather than day ranges**, which makes gaps and overlaps
structurally impossible — no tiling to validate, no day that can fall outside
a phase.

**Nothing in the pipeline changes.** No agent spec references the document, and
producers must not emit the carrier. Suppression (pregnancy, contraception,
illness, magic), irregularity, and `{{user}}` cycles are deferred to the
tracker by design, with the path to a later producer-declared suppression
vocabulary noted so it reuses this seed rather than inventing a parallel
mechanism.

### Added
- `contracts/BODY_CYCLES.md` — draft contract: carrier flags and pristine-record
  seeding semantics (both reusing the `[[WORLD_CALENDAR]]` convention),
  per-character payload with stable slug ids (reusing the `MEMORY_CONTRACT.md`
  §4 id space), duration-based phases with per-phase behavioral indices,
  graceful degradation, a not-yet-in-force producer checklist, the deferred
  list, and one open design question (whether a second supplementary state
  should collapse this into a generic `[[TRACKED_STATE]]` carrier).

### Changed
- `contracts/README.md` — index row for the draft, plus a note defining what
  draft status means: no consumer, no agent reference, producers do not emit.
---

## 2026-07-25 — The posture contract: `{{user}}` is a character, not the customer

Three related problems with `{{user}}`, fixed together because they turn out
to be the same bright line seen from different sides.

The first is the model's disposition. It was optimized to satisfy the person
typing, and that does not switch off inside a fiction — it reads `{{user}}`'s
message as a request from someone it should please rather than as a
character's move in a story. Three symptoms, all ordinary and all easy to miss
because they read as *cooperative*: an NPC concedes because `{{user}}` asked
rather than because its own interests say yes; a stated attempt ("`{{user}}`
reaches for the ledger") is rendered as an accomplished fact; and a convenient
interruption dissolves an outcome the scene had earned.

The jailbreak already said `{{user}}` was "a character played by the human at
the keyboard, equally subject to the story's logic." That is a *permission* —
it licenses harm — and it leaves the disposition completely intact, which is
how a world ends up with the permission granted and never exercised. What was
missing was the **role separation** that follows from it: the human *authors*
`{{user}}`'s moves, they are not the recipient of the model's service.

Following the embodied-specificity pattern, the correction is a triad, since
none of the three parts works alone. An engine prohibition with no world
substrate is gestural and the model nods at it; substrate with no prohibition
gets authored and never reached; and both without an audit check pass silently,
because a scene where `{{user}}` asks and receives looks like good prose. So:
a declared posture in the seed, a mandatory Tier 3 stance directive that names
*this arc's* concrete instance, an engine block for the disposition itself, and
a Voice Auditor probe that judges by counterfactual rather than by how smoothly
the scene read.

Two things this deliberately is **not**. It is not an argument that worlds
should be dark — the posture is *declared*, and `deferential` is a legitimate
answer that the pipeline supports; the point is that an unstated posture is not
a neutral world, it is whichever default the model was trained into. (Same trap
as the intimacy valence field.) And it is not licence to railroad: the
`protagonist_jeopardy` block carries a counter-guardrail with equal weight to
its prohibitions, because a model that seizes `{{user}}`'s turns and narrates
their defeats is a worse bug than the one being fixed. *Opposition, not
punishment.*

The second problem is that **compliance and intent are different questions**,
and the first pass of this work conflated them. A four-value posture enum asked
only "does the world give `{{user}}` what they want," which classifies a
compulsion-premise world — everyone must obey the protagonist, and every one of
them is using that obedience to route him into their own ends — as
`deferential`, the gentlest setting. It is the darkest kind of world the
pipeline can build. So the enum gains a fifth value, `predatory`: the world
gives `{{user}}` what they want, *and that is the mechanism of harm*.

Three consequences fell out of that, and each was a real hole:

**Harm classes.** "What can `{{user}}` lose" reads as a question about
possessions, and a protagonist who is invulnerable or omnipotent answers
"nothing." But such a world has stakes — they are **moral** (complicity,
self-image, a line that can't be uncrossed) and **epistemic** (being deceived
and acting on it), the two classes the model never reaches for unprompted and
the only ones available when the first three don't apply.

**The fourth reflex.** Yield, auto-success, and rescue all *correctly pass* in a
world that defers by design. What fires there is **rescue from consequence**:
the ask gets softened before it's made, the target turns out to have deserved
it, an NPC breaks frame to check that `{{user}}` is all right, the deed quietly
doesn't take, or the next scene opens on word that it worked out fine.

**The tell rule.** The model warns the player. It marks an insincere line with a
narration tell — *her smile didn't quite reach her eyes* — because it treats the
reader as owed a heads-up. In a world whose mechanic is manipulation that tell
is the bug: every appeal lands as a visible trap instead of as warmth, and the
choice the world was built around stops being a choice.

The cast-side sibling of all this is that **the model warms villains**, supplying
doubt, hesitation, and redemptive interiority the drafts never authored. Not an
argument for flat antagonists — a villain with real interiority is better
writing — but the mitigation has to be *authored* rather than supplied because
the model is uncomfortable. Two configurations it will not hold unaided, and
both are usually the point of the character: *feels nothing about what they do*,
and *loves them and does it anyway*.

The third problem is the mirror image, and it is issue #82. The pipeline's
"the human plays `{{user}}`, the model never impersonates them" rule was stated
upstream in three places but enforced by the Editor on `Drafts/User.md` alone.
The Tier 2 Protagonist Lorebook — unbounded, holding the content nearest the
line, and the file Step 5.5d actively routes `User.md` overflow *into* — had no
gate at all. The gated file was capped at 150 words; the ungated one was where
the violation would actually happen.

### Added
- `templates/World_Seed_Template.md`: **§3 `POSTURE TOWARD {{user}}`**
  (required) — declared `Default posture` enum
  (`adversarial`/`indifferent`/`mixed`/`deferential`), the named force that does
  not defer and what it wants instead, concrete losable things, the permitted
  shapes of a lost scene plus the off-the-table boundary, and an optional
  sharpest-specific field. Plus the §3 checklist items and a §5B.1 agreement
  note against the sandbox experience contract.
- `agent_roles/02_The_Architect.md`: **§8.A "THE STANCE-TOWARD-`{{user}}`
  DIRECTIVE"** — a new mandatory ARC_STATE Tonal Mandate category (every arc,
  no exemptions, `deferential` inverted rather than omitted), with two worked
  bullets; and the §8S.A sandbox counterpart on the power-fantasy contract
  bullet.
- `agent_roles/02_The_Architect.md`: **§7 "THE TIER 2 PROTAGONIST LOREBOOK —
  REFERENCE DATA, NEVER IMPERSONATION GUIDANCE"** — the authoring rule the new
  Editor gate validates against, with the descriptive-for-reaction vs.
  directive-for-behavior table, the reframing rule, and an explicit
  not-forbidden list so the gate does not get over-applied.
- `agent_roles/03_The_Editor.md`: **Step 5.7** — the protagonist-lorebook
  impersonation gate (5.7a directive scan, 5.7b mandatory reframe suggestion,
  5.7c ambiguous-mood soft flag, 5.7d posture-misrouting hard fail). Closes
  issue #82.
- `agent_roles/03_The_Editor.md`: **Step 4a-3d** — unconditional stance-directive
  hard fail, plus the sandbox line in 4a-S.
- `agent_roles/05a_Block_Library.md`: jailbreak **clause 2b (role separation)**,
  making it a five-clause block; and the **Protagonist Jeopardy**
  (`protagonist_jeopardy`) optional block with its §5a-detail content
  requirements including the non-optional counter-guardrail.
- `agent_roles/05_The_Prompt_Engineer.md`: the **protagonist-jeopardy block
  hint** (5.0b), which is explicitly *not* genre-keyed — it addresses a failure
  the model brings, not one the world introduces.
- `agent_roles/03b_The_Voice_Auditor.md`: the **bid** scenario class (mandatory
  every arc, both modes) and **Step 3K — Protagonist Jeopardy**, testing the
  three reflexes and the over-correction, with the world-side vs. engine-side
  diagnosis split by breadth.
- `agent_roles/revise/05_The_Prompt_Engineer_mini.md`: **Trigger G** —
  `protagonist_jeopardy` block toggle on a posture-change revision.
- `agent_roles/Auditioner/00_The_Auditioner.md`: check **K** in the reused
  Voice Auditor vocabulary.
- `templates/World_Seed_Template.md`: fifth posture value **`predatory`**; the
  **five harm classes** on the losables field (material / relational / physical
  / **moral** / **epistemic**); the boundary field made bidirectional so
  souls-like worlds can declare death, defeat, and game-over explicitly **on**
  the table; and **"How the world works on {{user}}"** — manipulation vectors
  with voiced phrasings plus the **tell rule** (`opaque` /
  `visible-but-tempting` / `mixed by character`).
- `agent_roles/02_The_Architect.md`: **§8.A "THE TELL RULE"** block (concrete
  prose-habit prohibitions, since the model doesn't recognize itself performing
  them from an abstraction), `predatory` shaping for the stance directive
  (*use*, not opposition), a worked `predatory` + tell-rule example, and
  **§5 "ANTAGONIST FIDELITY"** — author the interiority, including its absence.
- `agent_roles/03_The_Editor.md`: Step 4a-3d gains the fourth reflex, the
  bidirectional boundary, `predatory` shaping (verbatim voiced phrasings; a
  paraphrase is a hard fail), and the tell-rule check; Step 3 gains the
  antagonist-interiority soft flag.
- `agent_roles/03b_The_Voice_Auditor.md`: **Step 3L — Antagonist Fidelity** with
  its cruelty scenario class; Step 3K gains rescue-from-consequence, tell-rule
  integrity, and a **posture-weighting table** (running the four reflexes flat on
  a `deferential`/`predatory` world reports three meaningless passes and misses
  the real failure); the bid scenario is now shaped to the posture.
- `agent_roles/05a_Block_Library.md`: **Antagonist Integrity**
  (`antagonist_integrity`) optional block with its §5a-detail requirements and
  its own non-optional counter-guardrail (*no flat villains*); the fourth
  prohibition added to `protagonist_jeopardy`.
- `agent_roles/revise/05_The_Prompt_Engineer_mini.md`: **Trigger H**
  (`antagonist_integrity` toggle); Trigger G now also fires as a content
  re-weighting when a posture changes into `predatory`/`deferential`.
- `agent_roles/revise/03b_The_Voice_Auditor_mini.md`: delta 10 — Step 3L on
  character scopes touching a harm-function character.
- `CLAUDE.md`: architectural principles **#13 (The Posture Contract)** and
  **#14 (`{{user}}` is reference data, never impersonation guidance)**, plus
  five cross-file consistency rows. #13 records the compliance-vs-intent
  distinction, the five harm classes, the bidirectional boundary, and a note on
  the adjacent-and-not-yet-built piece: world-integrity enforcement against
  `{{user}}`'s *inputs* (declining an impossible premise — a firearm in a
  medieval setting — rather than resolving the attempt).

### Changed
- `agent_roles/00_The_Interviewer.md`: Section 3 gains the posture elicitation
  with its framing preamble (the reflex is explained to the user before the
  questions, or they read as asking permission to be cruel), the four questions
  with their push-standards, and the sign-off coverage line.
- `agent_roles/01_The_Refiner.md`: Master Design **Section 6** gains the
  `Posture Toward {{user}}` record block with an explicit **Tier 3** routing
  statement (the surrounding Section 6 material all flows to Tier 2; this does
  not), gap routing that names the stake, a sandbox charter cross-check, and a
  sign-off line. The existing `{{user}}`-reference-data note now states that the
  rule binds grammatical mood, not topic.
- `agent_roles/05_The_Prompt_Engineer.md`: Pass 1 jailbreak check is now
  five clauses; Pass 2 gains the jeopardy block-content and inclusion checks;
  two sign-off lines; Section 8 resync adds `protagonist_jeopardy` and treats a
  missing clause 2b as reportable spec drift.
- `agent_roles/revise/00_The_Reviser.md`: `tier3_arc_tonal_recalibration` and
  `sandbox_state_recalibration` now name the posture-change case, with the
  every-arc cascade warning (a half-updated world plays as neither posture).
- `agent_roles/revise/02_The_Architect_mini.md`,
  `agent_roles/revise/03_The_Editor_mini.md`,
  `agent_roles/revise/03b_The_Voice_Auditor_mini.md`: stance-bullet survival on
  recalibration, the all-arcs-or-none check, the protagonist-lorebook gate on
  touched entries, and a bid scenario on state/posture scopes with the
  over-correction weighted (the revision most likely to introduce it).
- `agent_roles/Converter/00_The_Converter.md` + `templates/Convert_Brief_Template.md`:
  `Section 3 — Posture Toward {{user}}` is **regenerate-always** in reframe
  (every field is computed against a specific protagonist; a carried posture
  aims the world's opposition at someone no longer in the story), with the
  `Default posture` enum offerable as a starting suggestion and a power-tier-shift
  warning; **keep** in rebaseline, with a prompt for source worlds that predate
  the contract entirely.
- `workflows/world-forge.md`: Phase 0, Phase 1, and Phase 3.5 descriptions.

## 2026-07-25 — Intimate aftermath: scenes that don't end at climax

A third failure of the same family as the two entries below, but a different
kind: not a wrong body, a **missing scope**. Erotic prose is trained to
terminate at orgasm, so the ordinary ten minutes afterward — getting up,
cleanup, needing to urinate, the towel, staying or leaving, what gets said —
simply never gets written. Intimate scenes read as ending in a fade rather
than in a bed with two real people in it.

The aftermath is also disproportionately characterizing. Two people can be
identical during sex and completely different afterward, and the afterward is
usually the more revealing half — the character who showers immediately versus
the one who doesn't care, the one who stays versus the one who dresses and
goes. None of that had a home in the profile.

It needed both halves, for the reason the previous entry established: a new
substrate entry alone would be authored and never reached, because the model
stops writing before it becomes relevant. So the aftermath joins the §6.7
trained reflexes with its own prohibition, and the Auditor's scene generation
now requires at least one scenario per character to run past climax — without
that, a test matrix passes while the substrate is never exercised.

### Added
- `agent_roles/06_The_Intimacy_Architect.md`: **Entry 6b — `[CHAR]_AFTERMATH`**
  (required), covering both registers — the ordinary bodily business and what
  they do with the other person — plus the change-of-state tell: the one
  aftermath behavior that signals something has shifted, the extension of
  `VULNERABILITY_SHAPE`'s job past the end of the scene. Inserted with
  sub-numbering per the editing protocol; Entries 7 and 8 keep their numbers.
  **Termination at climax** added as the fourth trained reflex in §6.7 with its
  own prohibition. §6.5 roster stat block gains an `Afterward` line. Three
  sign-off items.
- `agent_roles/03d_The_Intimacy_Auditor.md`: aftermath check in Step 3A
  (substrate fidelity, both registers + correct use of the tell); scene
  termination added to the Step 3I stock-register override; **Step 2 now
  requires at least one scenario per character to run past climax**; two
  diagnosis rows (no aftermath rendered / aftermath rendered but generic);
  report section and sign-off item.
- `templates/World_Seed_Template.md`: §4 `Afterward` field for characters and
  both NPC intimacy fields; the aftermath rule added to §8a's recommended
  stock-register rules; §4 checklist updated.
- `agent_roles/00_The_Interviewer.md`: Section 4 aftermath question with the
  change-of-state follow-up and the mechanical reason stated; roster NPC line.
- `agent_roles/01_The_Refiner.md`: Section 7 `Afterward` recording bullet
  noting why it is substrate rather than prose texture; NPC routing line.

### Changed
- `agent_roles/revise/02b_The_Intimacy_Architect_mini.md`: aftermath added to
  the new-profile draft list; delta 3a-i covers the aftermath prohibition.
- `agent_roles/revise/03d_The_Intimacy_Auditor_mini.md`: delta 3c runs the
  aftermath sub-check and requires a past-climax scenario when an `AFTERMATH`
  entry is touched.
- `CLAUDE.md`: cross-file row extended.

---

## 2026-07-25 — `{{user}}` embodiment, the stock-register prohibition, act cost, and valence

Follow-up to the entry below, closing the gaps it left. Testing the embodied
baseline against a concrete case — a short, slightly-built `{{user}}` paired
with a taller partner — exposed four things the first pass did not handle.

**`{{user}}` had no intimate substrate anywhere in the pipeline.** The Intimacy
Architect authors profiles for the cast the model *plays*; the protagonist was
never in scope, and the only place `{{user}}`'s body appeared in an intimate
context was the physical dyad, authored from the character's side. So every
intimate scene in every world had the model writing characters' reactions to a
stock default body regardless of what Section 3 said. The Tier 2 Protagonist
Lorebook was always the right home — nothing had ever been routed to it.

**Facts alone do not displace trained reflexes.** This is the load-bearing
insight of this pass. Erotic prose carries reflexes that fire *independently of
stated anatomy*: scale language ("filling her," "stretched around him," "she
could barely take him"), anal written as uniformly punishing regardless of the
anatomy authored, and a stock early-twenties body for everyone. A profile can
state a short, slight partner perfectly and the prose will still reach for the
stock phrase. These are the intimate equivalent of "moaned softly," and like it
they need a *prohibition*, not a description — which is exactly what the
Auditor's own counterfactual probe would have said about the previous pass.

**Size changes what acts cost**, and the dyad field enumerated positioning,
pacing, and noticing without ever signalling act cost as a consequence to
author — leaving the highest-value inference to a model whose default prices
every act identically.

**And loaded attributes have two competing defaults, not one.** The previous
difference-not-deficit rule was shaped by the older-woman case, where the
failure runs one way. For size the two defaults are *overwhelming* and
*inadequate*; for age, *idealised* and *diminished*. Both are wrong unless
chosen, so the author now declares the valence — neutral fact, advantage, or
charged. Charged is legitimate craft; unstated is a coin flip resolved
differently in every scene.

### Added
- `agent_roles/06_The_Intimacy_Architect.md`: **Section 6.6 — `{{user}}`
  intimate embodiment**, a Tier 2 protagonist intimacy profile pairing with the
  Protagonist Lorebook, carrying the bright line that it is reference data for
  other characters' reactions and never an instruction to play `{{user}}`.
  **Section 6.7 — the stock-register prohibition**, stating why descriptive
  substrate loses to a trained reflex and requiring the prohibitions in
  `INTIMATE_HARD_RULES` (authored from §8a defaults if the seed omitted them).
  Entry 3 Half A gains a fourth rule (valence declaration); Entry 7 Half B
  gains the anatomical-fit bullet; draft order, objective, arc and sandbox
  hard-rule entries, and four sign-off items updated.
- `agent_roles/03d_The_Intimacy_Auditor.md`: four new Step 3I sub-checks —
  stock-register override, `{{user}}` embodiment, valence integrity, and (in
  Step 1) an **embodiment probe** scenario class that invites the stock
  register so the check has material. Six diagnosis rows, severity guidance
  (stock-register override and defaulted `{{user}}` body are Critical), input
  list, report section, and three sign-off items.
- `templates/World_Seed_Template.md`: §3 **Protagonist Intimate Embodiment**
  block (stature and proportion, anatomy, what it changes act by act, stamina
  and recovery, valence); §8a **recommended stock-register rules** with three
  drop-in prohibitions; anatomical-fit clause on the §4 physical dyad; valence
  clause on the §4 embodied baseline.
- `agent_roles/00_The_Interviewer.md`: Section 3 intimate-embodiment
  elicitation with its framing preamble and the valence question; Section 8
  stock-register rule proposed by default with the mechanic explained;
  anatomical-fit and valence added to the Section 4 dyad and baseline questions.
- `agent_roles/01_The_Refiner.md`: Section 6 `{{user}}` intimate embodiment
  recording with the reference-data framing and gap routing; anatomical fit and
  valence added to the dyad and baseline bullets.

### Changed
- `workflows/world-forge.md`: Phase 2.5 output list gains the protagonist
  intimacy profile; phase table row names §6.6 and §6.7.
- `agent_roles/03_The_Editor.md`: protagonist intimacy profile added to the
  per-entry validation file list.
- `agent_roles/revise/02b_The_Intimacy_Architect_mini.md`: delta 3a-i
  (`{{user}}` embodiment in scope under `intimacy_substrate_modify`, bright
  line binding, stock-register rules preserved or authored); a `{{user}}` body
  change as the widest cross-cascade in the intimacy set; two sign-off items.
- `agent_roles/revise/03d_The_Intimacy_Auditor_mini.md`: delta 3c extended with
  the stock-register, `{{user}}` embodiment, and valence sub-checks.
- `agent_roles/Converter/00_The_Converter.md` +
  `templates/Convert_Brief_Template.md`: matrix rows for the protagonist
  embodiment (regenerates with Section 3; kept in rebaseline) and the
  stock-register hard rules (preserve — they bind whatever bodies exist).
- `CLAUDE.md`: cross-file row extended to cover the four additions.

---

## 2026-07-25 — Embodied specificity: the generic-body defense for intimate scenes

The pipeline's founding observation is that the model collapses characters to
a default unless something compels otherwise — hence voice entries, voice
fingerprints, and the Voice Auditor. That collapse applies to *bodies* just as
much as to voices, and nothing in the pipeline addressed it: absent a
compelling substrate, every character in an intimate scene gets rendered on a
stock body in its early twenties, with stock stamina and stock mechanics, no
matter what the card's physical description says. A woman in her forties who
has carried two children reads identically to a twenty-year-old.

The fix is not a physiology reference — the model already knows what age,
childbirth, injury, and build do to a body. The fix is removing its license to
ignore that knowledge, which is an elicitation-and-directive problem, the same
shape as every other collapse this pipeline defends against.

The change also closes a structural gap: half of what makes an intimate
pairing specific is not a property of either character. Height differential,
stamina asymmetry, and age-gap embodiment are properties of a *dyad*, and no
per-character field can hold them. `[CHAR]_INTIMACY_RELATIONSHIP_DELTAS`
(previously optional and purely psychological) becomes the home for them and
is now required wherever a real differential exists.

Three rules ship with it, because the naive version of this feature makes
output worse: substrate is authored in **observable register, not clinical
vocabulary** (the entry reaches the model's context and the model echoes it —
clinical input produces anatomy-lecture prose); embodiment is authored as
**difference, not deficit**, in both directions and for both partners (a
non-default body is different, not a degraded copy — and the younger partner's
inexperience is an asymmetry running the other way); and **every** intimate
character gets a baseline, including unremarkable default-bodied ones, or the
field becomes "the aging field" and the stock default silently reasserts
itself for everyone else.

### Added
- `agent_roles/06_The_Intimacy_Architect.md`: Entry 3 (`BODY_REACTIONS`) split
  into two mandatory halves — **Half A embodied baseline** (age and what the
  body has lived through, build and scale, arousal and recovery mechanics, the
  particulars of the world's live acts, trajectory) and **Half B reaction
  set** (the previous content), with the three governing rules stated inline.
  Entry 7 gains **Half B physical dyad** and moves from "Optional entries" to
  "Conditional entries" — required wherever a height, age, build, stamina,
  experience, or world-specific differential exists. §6.5 roster stat block
  gains an `Embodied baseline` line. Four craft notes and two
  never-goes-in-a-profile rules added; §8 gains an embodied-consistency
  cross-check; sign-off gains three items.
- `agent_roles/03d_The_Intimacy_Auditor.md`: new **Step 3I — Embodied
  specificity**, the generic-body counterpart to Step 3E's generic-voice
  check, with four sub-checks (body specificity, dyad materiality, clinical
  intrusion, deficit framing) and severity guidance. Six diagnosis-table rows,
  a report section, a sign-off item, and a §8 note on not supplying the body
  the drafts failed to.
- `templates/World_Seed_Template.md`: §4 `Embodied baseline` and
  `Physical dyad` fields; embodied/dyad content added to both NPC intimacy
  fields (principal and roster); three §4 checklist items.
- `agent_roles/00_The_Interviewer.md`: two new Section 4 elicitation questions
  (embodied baseline asked *before* the reaction questions; the physical dyad
  as an explicitly pairing-level question), each with register and direction
  pushback; NPC intimacy paragraph notes age/build/history as the cheapest
  differentiators on a large roster.
- `agent_roles/01_The_Refiner.md`: Section 7 `Embodied baseline` and
  `Physical dyad` recording bullets with `UNRESOLVED_QUESTIONS.md` routing for
  gaps, deficit-only entries, and consequence-free dyads; three sign-off items;
  homogenised-sexual-roster flag in the NPC intimacy routing paragraph.

### Changed
- `agent_roles/revise/02b_The_Intimacy_Architect_mini.md`: new foundational
  delta 3a (embodiment is substrate; the parent's three rules bind); both
  halves added to the new-profile draft list plus a physical-dyad line; two new
  cross-cascade cases — a changed age/history/build makes every dyad involving
  that character **stale**, and a new or replaced partner leaves a pairing with
  no dyad at all; two sign-off items.
- `agent_roles/revise/03d_The_Intimacy_Auditor_mini.md`: new foundational
  delta 3c running the parent's Step 3I on the affected slice, with stale
  dyads called out as the revision-specific failure; audit and sign-off lines.
- `agent_roles/Converter/00_The_Converter.md`: three preservation-matrix rows
  separating the two — `Embodied baseline` **preserves** (a body survives a
  protagonist swap), `Physical dyad` against `{{user}}` **strips + marks**
  (the pairing's other half was replaced), dyads between preserved characters
  preserve; Step 6 Section 4 authoring rule and marker; Step 4 question 5 note;
  Section 9 rebaseline inversion row (`{{user}}` dyads carry — same person).
- `templates/Convert_Brief_Template.md`: §4e reminder bullets mirroring the
  matrix split, and the rebaseline inversion paragraph.
- `CLAUDE.md`: cross-file consistency row for the embodied-specificity seam.

---

## 2026-07-18 — Three new optional preset blocks: action choreography, fair-play mystery, register blending (#81)

The genre-lens table (entry below) made the optional block menu's coverage
gaps visible. Three families had a named runtime failure with no menu block:
action-heavy worlds (fights summarized into a sentence, physical incoherence,
the model ending fights unilaterally), played mysteries (solution drift,
NPCs volunteering the answer, theories confirmed out-of-fiction), and worlds
whose tone is a deliberate register blend, action-comedy à la Rush Hour
(mode collapse — the humor evaporates the moment stakes rise; register
segregation — alternating single-register scenes instead of banter-during-
the-fight; mutual defusal — a joke resets the tension). Blends are the case
the table's union-of-rows rule cannot fix: the blend itself fails at runtime
in ways neither family's blocks address. All three blocks are engine-level;
Register Blending carries one world-adapted element (the declared blend axes
in Master Design tone vocabulary) and defers register authority to the
active ARC_STATE / SANDBOX_STATE Tonal Mandate. Preset Resync picks all
three up automatically via its newly-warranted-optional-blocks axis.

### Added
- **`agent_roles/05a_Block_Library.md`** — three new §5a optional menu
  entries with matching §5a-detail content requirements: **Action & Combat
  Choreography** (`action_choreography`: beat discipline of 1–3 exchanges
  per reply, choreography grounding composing with Spatial Awareness,
  opposition integrity, accruing in-fight cost composing with Consequence
  Tracking, resolution authority), **Mystery / Fair-Play Investigation**
  (`fair_play_mystery`: fixed solution, clues earned through investigative
  action, fair-play discipline, withholding-is-not-stonewalling, {{user}}
  does the solving; generic protocol deferring the world's specific
  hidden-information content to Arc Guardian / Tier 3), and **Register
  Blending** (`register_blending`: simultaneity rule, no-cancellation in
  both directions, register carriers, escalation drift check, Tonal-Mandate-
  wins authority clause).

### Changed
- **`agent_roles/05_The_Prompt_Engineer.md`** — genre-lens table updated in
  the same edit per the CLAUDE.md coupling rule: new "Action-forward /
  combat-heavy" and "Deliberate register blend" rows, Mystery / Fair-Play
  added to the intrigue/mystery row, Step 1 family list gains "action" and
  the name-the-blend instruction, closing paragraph routes blends to the
  blend row. Pass 1 optional-block enumeration, Pass 2 per-block content
  checks, and the sign-off optional-blocks line extended for the three new
  blocks.

---

## 2026-07-18 — Genre-lens hint in the Block Selection Rationale (#81)

The Prompt Engineer's optional block menu (§5a) is genre-keyed — Subtext for
intrigue, Consequence Tracking for grimdark, Atmosphere & Dread for horror,
and so on — but block selection is driven by the predicted-failure-mode
analysis, and nothing forced that analysis to actually sweep the menu against
the world's genre. A fitting block could be omitted by oversight rather than
judgment, leaving no trace in the Step 4 omissions list. This adds a genre-lens
completeness check following the same "hint feeding the analysis, not a
mandate" pattern as the existing sandbox / ladder / dice-oracle hints: the
genre label never auto-includes a block, but every menu block mapped to a
named genre family must now be explicitly included or explicitly omitted
with a reason. Preset Resync inherits the hint automatically (its Step 2
re-runs the Section 5.0b rationale).

### Added
- **`agent_roles/05_The_Prompt_Engineer.md`** — new **genre-lens hint**
  subsection in Section 5.0b (after the dice-oracle hint): a genre-family →
  menu-block mapping table with the evaluate-or-justify rule, covering ten
  families (grimdark, horror, intrigue/mystery, thriller, strict-hierarchy,
  historical/jargon, romance, comedy, slice-of-life, large-ensemble). The
  comedy row is honest about the one menu gap: the comedic-register failure
  ("humor drifts toward earnest drama") has no dedicated menu block, so the
  row routes it to the §5c custom-block path rather than leaving it silently
  unaddressed. Step 1 (World Archetype) now names the world's dominant genre
  family/families explicitly;
  the Block-to-Failure-Mode Coverage Check (both the 5.0b format and the
  Section 6 report template) gains a genre-coverage checkbox; the sign-off
  gains a genre-lens line alongside the sandbox/ladder/dice lines.

### Changed
- **`CLAUDE.md`** — the `05a_Block_Library.md` cross-file consistency row now
  records the new coupling: the 5.0b genre-lens table enumerates the §5a
  optional menu, so adding or renaming an optional block updates the table in
  the same edit.

---

## 2026-07-11 — Checkpoint discipline (write-as-you-go)

A field run surfaced two related failure modes: a ~6-hour Phase 0 interview
held every settled seed section in conversation memory until a single
end-of-interview write (context rot + one oversized write as the single point
of failure), and a Phase 2 run shipped a zero-byte `Instructions_[CardName].md`
that no agent caught because nothing verified that writes actually landed. Both
were amplified by a provider whose tool calls degraded on long outputs — the
user's own workaround (line-at-a-time PowerShell `Add-Content`) then burned the
session and risked mojibake in Drafts markdown. This change makes incremental
committing, write verification, and disk-first resume an explicit pipeline-wide
contract.

### Added
- **`workflows/world-forge.md`** — new **CHECKPOINT DISCIPLINE** section (after
  PIPELINE STATE LEDGER): three rules — commit each unit as it locks (with a
  one-entry/one-section grain floor; no line-at-a-time writes), verify every
  write landed (non-empty, ends with the content just written), and resume from
  disk, not memory. Checkpoint state is inferred from disk, not tracked in the
  ledger; fallback writes obey the Compiler's FILE-WRITING & ENCODING guard
  (never PowerShell).
- **`agent_roles/00_The_Interviewer.md`** — Section 3 gains a "commit each
  section to disk as it locks" working-approach paragraph (explicitly *not*
  softening the never-draft-ahead rule); Section 7 notes the seed is authored
  incrementally across the interview.
- **`agent_roles/01_The_Refiner.md`** — Step 3 writes the Master Design
  checkpointed section by section, with the Pipeline State Ledger still
  authored once at sign-off per its existing contract.
- **`agent_roles/02_The_Architect.md`** — Section 4 (Draft Order) gains the
  checkpoint rule (per-file writes, optional per-entry appends within the large
  entry files, resume-from-inventory); the pre-submission checklist gains a
  **File Integrity** block (no zero-byte, truncated, or mojibake-corrupted
  drafts).
- **`agent_roles/06_The_Intimacy_Architect.md`** — Section 5 (Draft Order)
  gains the same rule for profiles and registers.
- **`agent_roles/04_The_Compiler.md`** — the FILE-WRITING & ENCODING guard
  gains a write-verification & resume note (`resume phase4` re-verifies
  existing Export files and recompiles only what fails; UIDs resolve per-file,
  so single-file recompiles are safe).
- **`CLAUDE.md`** — cross-file consistency row for the checkpoint set-piece.
  The Editor, auditors, and Prompt Engineer are covered generically by the
  workflow section (their unit is one report file); revise minis inherit the
  parents' checkpoint rules with no delta text.

---

## 2026-07-07 — Brainstormer: dice-oracle awareness (leaning-only, all postures)

The Brainstormer had zero awareness of the dice oracle, so it never proposed it
even when a premise was exactly what it's for (a character who overshares random
off-screen pasts, a conjured temp cast, recurring random events). Adds light,
boundary-respecting awareness: the Brainstormer *names* the dice oracle as a
leaning when the premise fits — the same way it floats Arc-vs-sandbox and the
intimate register — and never authors tables (bright line #11 intact; the
Interviewer elicits, the Architect authors).

### Changed
- **`agent_roles/Brainstormer/00_The_Brainstormer.md`** — Section 4 gains a
  "Randomized off-screen facts? (surface, don't author)" divergence axis; the
  Section 6 notes template gains a dice-oracle Leaning line; the
  revision-diagnostic posture (Section 9 step 2) gains a diagnostic hook (model
  keeps inventing off-screen facts wrong/repetitively → wants a dice oracle it
  lacks, or its `[[DICE_TABLES]]` is serializing/over-rolling — both in-scope
  `tier1_world_rule_*` revise concerns); the adaptation posture (Section 10 step
  4) floats it when the source shows an oversharer / conjured temp cast.
- **`agent_roles/Brainstormer/lenses/Cast_and_Voice_Lens.md`** — a leaning-only
  note tying an oversharing / temp-cast character to the dice oracle.
- **`CLAUDE.md`** — the dice-oracle seam row lists the Brainstormer as an
  upstream leaning-only touchpoint.

## 2026-07-07 — Dice Oracle: complexity roadmap in contract §7 (tiered)

Captures where "more complex dice / RPG mechanics" should go, so producer and
consumer evolve toward the same place without accreting a half-RPG engine onto
the ephemeral oracle. No behavior or schema change — documentation only.

### Changed
- **`contracts/DICE_ORACLE.md`** §7 rewritten into three tiers: **7.1 richer
  randomness** (weighted pools, pick-N, advantage/keep-drop/exploding grammar,
  derived modifiers — additive, stays in the oracle), **7.2 resolution
  mechanics** (skill-check-vs-DC / success counting — fits until it needs a stat
  modifier or persistence), **7.3 stateful RPG** (sheets/HP/consequences — a
  separate subsystem via server-authoritative rolls + a state channel, never
  bolted onto the ephemeral oracle). `Last updated` bumped; version unchanged.
  **Cross-repo: needs contract sync to the ST fork.**

## 2026-07-07 — Dice Oracle: `dice_oracle` block handles established-character references

Supports a consumer-side feature (ST fork `world-forge` extension): pinning an
**existing cast member** into a dice roll as a participant, so a rolled scene is
part-authored (the named NPC) and part-rolled (the situation). The pipeline's
only obligation is one interpretation clause; the roll/UI is consumer-side and
needs no schema or contract change (the NPC is referenced by name at roll time,
resolved from the `[[NPC_MANIFEST]]`, and stays ephemeral like every dice fact).

### Changed
- **`agent_roles/05a_Block_Library.md`** — the `dice_oracle` block's §5a-detail
  content requirements gain an **Established-character references** clause: when
  a `<dice_oracle>` result names an existing cast member, portray them from their
  own lorebook/card (voice, body, psychology, intimacy profile), never from the
  rolled facts — the dice fix the *situation*, the character is authored, not
  rolled; the involvement is ephemeral recount/event fiction, not a canon update.

## 2026-07-07 — Dice Oracle: `dice_oracle` preset block (runtime interpretation)

The pipeline fixes the *authoring* of dice tables, but nothing told the model
how to *read* the `<dice_oracle>` facts at runtime — so a well-shaped payload
could still be recited as a list or serialized participant-by-participant. This
adds the engine-side half of the dice oracle's what/how split as an optional
preset block: the world's `framing` + the facts fix *what is true*; the block
fixes *how to consume the injection channel*. It sits on the preset (engine)
side of the override contract (#2) — world-agnostic, never in cards — and is the
`<dice_oracle>`-channel sibling of Block 4 (Lore Integration)'s anti-recitation
rule.

### Added
- **`agent_roles/05a_Block_Library.md`** — new optional block **Dice Oracle
  Interpretation** (`identifier: "dice_oracle"`): menu entry + §5a-detail content
  requirements. Facts are the skeleton/constraints of a recount (past) or event
  (present) to **interweave into one coherent scene**, never recited as a list;
  a multi-participant result is one continuous scene, never one-after-another;
  honor the framed tense; defer voice/tone/explicitness to the world.
- **`agent_roles/05_The_Prompt_Engineer.md`** — 5.0b **dice-oracle block hint**
  (default-include iff the world declares a `[[DICE_TABLES]]` oracle, either
  mode), a Pass 1 presence-iff-oracle + no-specifics check, a sign-off checklist
  line, and inclusion in the optional-block list + resync ADD examples.
- **`agent_roles/revise/05_The_Prompt_Engineer_mini.md`** — **Trigger F**: when a
  revision adds a world's first dice oracle (`tier1_world_rule_add` creating the
  carrier), add + enable the `dice_oracle` block (editing existing tables needs
  no preset change).
- **`CLAUDE.md`** — Dice Oracle seam row records the runtime-interpretation block
  and its selection/toggle touchpoints.

No template JSON change: `dice_oracle` is an *optional* block (added when
warranted), not a conditional core block, matching the `npc_ensemble` precedent.

## 2026-07-06 — Dice Oracle: "roll the shape, not the choreography" authoring guidance

A dice world built through the pipeline serialized multi-man recounts (the
model narrated "one man, then the next appears") and read the rolled facts back
like a checklist. Root cause was authoring, not schema: procedures rolled the
per-participant blow-by-blow (positions, hole-switching, a per-man finish) and
split one encounter across per-participant records, which the consumer injects
as separate blocks. The dice were doing the model's job (choreography) badly,
and the model was doing the dice's job (reciting the list). This threads the
what/how line through the *authoring* step so future worlds don't reproduce it.

### Added
- **Architect** §6 — a "Roll the shape, not the choreography" block: fix
  setting / cast-as-traits / configuration / valence / one signature detail;
  never roll positions, act-by-act sequence, per-participant acts, or a
  per-participant finish; one situation = one procedure (participants are gated
  trait steps, never per-participant procedures/rolls); count > 1 states
  simultaneity in `text` + one encounter-level configuration + one joint
  outcome; framing fixes register, never invites a sequence.
- **Editor** Step 4.8 — soft-flags for the same anti-patterns (per-participant
  procedure/duplication, rolled choreography / per-person finish, count outcome
  missing simultaneity, serializing framing).
- **`contracts/DICE_ORACLE.md`** §6.1 — informative authoring guidance mirroring
  the above (no schema change; **needs contract sync to the ST fork**).
- **Revise cascade — remediation path for an already-shipped world.** Correcting
  a dice oracle that serializes / over-rolls is a `tier1_world_rule_modify`:
  `agent_roles/revise/00_The_Reviser.md` names the dice-carrier target (+ a
  possible paired `intimacy_register_modify` for the standing "tell it, don't
  recite" instruction); `agent_roles/revise/02_The_Architect_mini.md` Step R2.5
  rewrites the carrier payload **in place** applying the parent's shape-not-
  choreography rules (collapse per-participant procedures, strip choreography /
  per-person finishes, add simultaneity + configuration + one joint outcome,
  de-serialize framing); `agent_roles/revise/03_The_Editor_mini.md` Step R3.1
  revalidates per parent Step 4.8 + the soft-flags. The mini-Compiler already
  preserves the carrier UID, so running SillyTavern chats keep world-info state.

### Changed
- **Interviewer** dice elicitation — steers authors to roll shape/flavor + one
  signature detail (not choreography), keeps one situation as one procedure, and
  draws out multi-participant configuration + simultaneity instead of "extra
  positions"; reflect-back and §2h record note updated.
- **World Seed** template §2h — author-facing "roll the shape, not the
  choreography" + "one situation = one procedure" callouts; examples de-
  choreographed (dropped "the act" / "extra-positions pool").
- **`CLAUDE.md`** — Dice Oracle seam row notes the authoring-guidance set-piece
  that must read consistently across seed / Interviewer / Architect / Editor /
  contract §6.1.

## 2026-07-06 — Dice Oracle: producer caught up to schema 2 + Editor validation gate

The dice oracle producer chain was still authoring **schema 1** payloads while
`contracts/DICE_ORACLE.md` had moved to **v2 / schema 2** (procedure `mode` —
recount vs. event tense — and `turns` injection duration, both additive). The
Architect hard-coded `schema: 1` and knew nothing about `mode`/`turns`, so the
pipeline could not author either v2 feature. Separately, the Architect deferred
malformed-payload rejection to the Editor, but the Editor had no dice-carrier
validation step (only the WARN-only compile-time backstop caught it). This
closes both gaps and threads the seam through the revise/convert cascades.

### Changed
- **`contracts/DICE_ORACLE.md`** status flipped **Draft → Established** — the v2
  seam is settled end to end (producer + consumer).
- **World Seed** template §2h — adds per-situation **tense** (recount default /
  event) and **duration** (replies to keep facts armed) author fields.
- **Interviewer** (Section 2 dice elicitation) — now draws out recount-vs-event
  and duration per procedure, and records them into §2h.
- **Refiner** — the `**Dice Oracle Tables (Scene Tracker seed):**` line carries
  tense + duration; points the Architect at schema 2.
- **Architect** §6 — emits `schema: 2` with optional payload-level `turns` and
  per-procedure `mode`/`turns`; payload example updated.
- **Compiler** Step 7.9 — carries `mode`/`turns` verbatim; guard + checklist
  updated to schema 2.
- **`tools/validate_export.py`** — `check_dice_tables` gains WARN checks for a
  bad `mode` (not recount/event) and a bad `turns` (payload or procedure, not a
  positive int); docstring/header note schema 2.

### Added
- **Editor** Step 4.8 — Dice Oracle Carrier Validation (hard-fail on disabled
  carrier, unparseable payload, missing/wrong `schema`, no valid procedures,
  malformed step, uncovered roll range, forward/dangling `when`, bad
  `mode`/`turns`; soft-flags), plus a sign-off item. Mirrors the calendar Step
  4.7 and is the pipeline's audit gate the Architect defers to.
- **Cross-file consistency:** `CLAUDE.md` gains a Dice Oracle seam row; the
  revise **mini-Compiler** preserves an existing `[[DICE_TABLES]]` carrier
  through a World-lorebook rewrite (rule + sign-off items); the **Converter**
  preservation matrix and **Convert Brief** template gain a §2h dice row.

## 2026-07-06 — Dice Oracle: producer emits `[[DICE_TABLES]]` for the Scene Tracker

New optional seam, adopted canonically from the SillyTavern fork (where the
consumer — a manual **Dice** tab in the `world-forge` Scene Tracker — was built
first). Before the narrating model invents facts it has no basis for — a
character recounting an off-screen past that lives in no lorebook, or a
temporary, unnamed NPC conjured for one scene — the player rolls world-authored
tables and the resolved facts inject as authoritative context. The dice fix
*what* is true; the model narrates *how*.

- **New contract** `contracts/DICE_ORACLE.md` (schema 1): the `[[DICE_TABLES]]`
  carrier (same enabled-but-inert convention as `[[WORLD_CALENDAR]]`), the
  roll-table payload (pools, procedures, `roll`/`pick` steps, conditional
  `when` gates, optional `framing` lead-in), and graceful degradation.
- **Authoring chain**, mirroring the World Calendar seam end to end:
  - **World Seed** template §2h — optional author-facing declaration (what to
    randomize, pools, outcome scales, lead-in).
  - **Refiner** records a `**Dice Oracle Tables (Scene Tracker seed):**` line
    in Master Design Section 1 when §2h is filled.
  - **Architect** compiles it into a `### CARRIER: [[DICE_TABLES]]` block
    (pools/procedures/gated steps; likelihoods → dice ranges).
  - **Compiler** Step 7.9 transcribes the carrier into the World Lorebook JSON
    verbatim (enabled, inert), with a pre-save guard + release-checklist items.
- **`tools/validate_export.py`**: WARN-only `check_dice_tables` — at most one
  carrier per lorebook; enabled so the Dice tab sees it; JSON object with an
  integer schema; each procedure a slug id + ≥1 step; each step a pick xor
  roll+outcomes; named pools resolve; `when` references only earlier steps.

Optional and backward-compatible: a world that declares nothing emits no
carrier, and the Scene Tracker's Dice tab falls back to a built-in demo set.

---

## 2026-07-05 — Rebaseline consolidates seed-anchored: 1:1 source seed + applied revisions

Rebaseline mode previously *distilled* the entire seed from the post-revision
`Master_Design.md` (old Step D, "Distillation, not transcription"), which
paraphrased the user's original seed wording even in sections no revision
ever touched. The consolidation is now **seed-anchored**: the source
`World_Seed.md` — already seed-grade by definition — carries **1:1** as the
base, each applied revision (from the required `Revision_R*.md` reading) is
written into the affected seed passage in place (replace-not-stack, at seed
grade), and a new **divergence scan** surfaces post-seed content that no
revision explains (Refiner gap answers, arcs developed past the seed's
sketch) for ask-first fold-in — nothing folds in or drops silently. The
structure upgrades to the current `World_Seed_Template.md` without
re-wording carried content. Distillation from the Master Design remains
available, but never as a silent default while a source seed exists: the
new **`--distill`** flag opts out of the 1:1 carry deliberately (for a
seed that was thin at Phase 0, or a world that has outgrown its wording),
and a seedless source is announced and confirmed — the confirmation
counting as passing the flag, the same treat-confirmation-as-the-flag
pattern as Step F's `--then-brainstorm` upgrade. Sub-seed-grade revisions
(entry-level tweaks) make no seed edit and are recorded in the manifest
as re-deriving downstream — the same outcome the old distillation gave
them. Everything else about rebaseline (zero-axes gate, source-integrity
check, marker-free cleanliness, fresh-UID cost,
`--then-interview`/`--then-brainstorm` chains) is unchanged.

### Added
- **`--rebaseline --distill`** — distilled consolidation as an explicit
  opt-in: the seed is re-derived from the post-revision Master Design
  instead of carried 1:1 from the source seed. Requires `--rebaseline`
  (halts in reframe mode); combines with `--brief` (new Section 1
  `Rebaseline consolidation:` field must agree) and the `--then-*` flags.
  The flag is the consent — the Converter announces the re-wording cost
  once and proceeds without a further confirm. Documented across the
  Converter spec (invocation, Step B routing, Step D distillation path,
  manifest `Seed base:` values, sign-off), the convert workflow (mode +
  command tables, pause gate), the Convert Brief template, `CLAUDE.md`
  principle #10, and the tutorial's flag reference.

### Changed
- `agent_roles/Converter/00_The_Converter.md`: Section 9 Step D rewritten
  from "Distillation, not transcription" to **"Seed-anchored
  consolidation"** — carry the seed 1:1, apply revision deltas in place,
  divergence scan (ask-first), upgrade structure not words, with the
  distillation path reserved for `--distill` and seedless sources. Step B makes the source
  `World_Seed.md` required reading (announcing the fallback when absent);
  Step C's disposition table defines rebaseline `keep` as carried per
  Step D; Step E scopes `<!-- REBASELINED FROM ... -->` comments to change
  sites (1:1 passages stay unmarked — unmarked *is* the 1:1 contract);
  Step A's no-op flag names seed drift as a legitimate revision-free
  rebaseline reason. Manifest gains a Consolidation block (`Seed base:`
  line + carried-1:1 / deltas-applied / divergence-dispositions /
  structure-upgrades inventory); Context Manifest, Step 3 intake, and the
  rebaseline sign-off checklist updated to match.
- `workflows/world-forge-convert.md`: REBASELINE MODE bullets describe the
  seed-anchored consolidation and route distillation through the explicit
  `--distill` path; the C0 input list marks the source seed required in
  rebaseline mode; two new pause gates (**C0 Rebaseline No Source Seed**,
  **C0 Rebaseline Divergence Fold-In**); operations-table row updated.
- `templates/Convert_Brief_Template.md`: rebaseline intro note and the
  Section 4e / Section 5 *Rebaseline:* notes now describe the 1:1
  seed-anchored carry instead of "distills from the source".
- `CLAUDE.md`: principle #10 rebaseline description updated (seed-anchored
  Step D, divergence scan, fallback).
- `tutorial.md`: Section 8 rebaseline walkthrough rewritten around the 1:1
  carry + divergence surfacing.

---

## 2026-07-05 — Rebaseline picks up the standing Big_Brain_Storm.md idea file

The standing `Big_Brain_Storm.md` idea file (written by standalone
`/worldforge brainstorm --improve` sessions) previously had exactly one
pickup point: `revise --brainstorm` (revision-diagnostic posture, step 1a).
A rebaseline — the moment parked ideas most naturally come due — ignored it
entirely: the `--then-brainstorm` chained Brainstormer read only the
consolidated seed + Conversion Manifest, and nothing carried the standing
file to the target project, stranding the idea pool in the source folder.
This change gives the convert side the same ask-first pickup contract and
makes the parked pool follow the world. The "no agent reads it silently"
line holds: the Brainstormer remains the only agent that reads or writes
the file (now through both improvement doors plus revision-diagnostic);
the Converter only checks for its existence; the Reviser and Interviewer
still never touch it — endorsed ideas reach the pipeline through
`Brainstorm_Notes.md`, as before.

### Added
- `agent_roles/Brainstormer/00_The_Brainstormer.md`: improvement-posture
  step 1a — in a `--then-brainstorm` chain, check the **source** project
  (path from the Conversion Manifest) for `Big_Brain_Storm.md`, ask before
  folding its still-open ideas in, attribute endorsed ideas in
  `Brainstorm_Notes.md` ("from `Big_Brain_Storm.md`"), and at write time
  carry the curated standing file forward to the **target** project
  (pursued ideas retired as "picked up in rebaseline chain", still-open
  ideas carried, source copy never modified). Context Manifest, Section 8
  step 4 (chained bullet), the standing file's stamped header, and the
  improvement-posture sign-off updated to match.
- `agent_roles/Converter/00_The_Converter.md`: Section 9 Step F standing
  idea file check — every rebaseline checks the source for
  `Big_Brain_Storm.md` (presence only; the Converter never reads it) and
  routes: fold via the `--then-brainstorm` chain (upgrading the run on
  user confirmation if the flag wasn't passed), state an idea directly as
  new mechanics, or leave it parked. Disposition recorded via a new
  `Standing idea file:` line in the manifest's "New in rebaseline" block;
  Context Manifest and rebaseline sign-off checklist updated.

### Changed
- `workflows/world-forge-convert.md`: rebaseline mode bullets, the
  `--then-brainstorm` command-table row, and the chain description now
  document the pickup + carry-forward.
- `workflows/world-forge.md`: BRAINSTORM section and command-table rows
  name both pickup points (`revise --brainstorm` and the rebaseline
  `--then-brainstorm` chain; plain `--rebaseline` surfaces and routes).
- `CLAUDE.md`: principles #10 and #11 and the Brainstormer
  cross-file-consistency row updated to the two-point pickup contract.
- `templates/Convert_Brief_Template.md`: the "New mechanics (rebaseline
  only)" field notes that the Converter surfaces a standing
  `Big_Brain_Storm.md` at this intake regardless of the brief (three-file
  contract kept in sync).
- `tutorial.md` (Sections 8, 9, 10.1 / 10.5) and `README.md` (command
  table): pickup wording updated to match.

---

## 2026-07-05 — Kilo config: OpenRouter per-model provider routing + GLM 5.2 / Kimi K2.5 alternates (#72)

A user report of GLM 5.2 runs failing and stopping mid-task through OpenRouter
traced to the upstream-routing layer, not the pipeline: OpenRouter serves each
model through several third-party hosts, and which host a request lands on
determines stream reliability, effective context handling, and — for
DeepSeek — whether the automatic prefix caching that makes per-phase spec
reloads cheap applies at all. Kilo forwards everything under
`provider.openrouter.models.<id>.options` in `kilo.jsonc` verbatim to
OpenRouter, so routing is pinnable per model from the shipped config. The
shipped `kilo.jsonc` now pins the DeepSeek seats to DeepSeek's first-party
upstream (`order: ["DeepSeek"]`, fallbacks allowed) and carries commented-out,
ready-to-swap routing entries for GLM 5.2 (`z-ai/glm-5.2`, hard-pinned
`only: ["Z.AI"]` because the reported mid-task stream failures live on the
third-party upstreams, plus `reasoning: { effort }` on the same passthrough)
and Kimi K2.5 (`moonshotai/kimi-k2.5`, the general-line chat-tuned Kimi —
preferred over the coding-tuned K2.7 Code for creative seats, no output-cap
problem, and it keeps the per-phase temperatures, unlike GLM).

### Added
- `Kilo_Variants/`: drop-in all-seats alternates for the shipped config —
  `kilo.glm-5.2.jsonc` (every seat on `openrouter/z-ai/glm-5.2`, reasoning
  effort high, Z.AI upstream hard-pinned, no `temperature` fields since
  reasoning-class endpoints ignore sampling) and `kilo.kimi-k2.5.jsonc`
  (every seat on `openrouter/moonshotai/kimi-k2.5`, the general-line
  chat-tuned Kimi — per-phase temperatures kept, Moonshot AI upstream
  preferred). Both are generated from the shipped agent set, so the 23
  seats and `{file:...}` prompt pins are identical. Not auto-loaded:
  activated by copying over `.kilo/kilo.jsonc` per the folder README.
  Added to `.kilocodeignore` (maintenance material, not runtime context)
  and to the `CLAUDE.md` repository tree. (An all-seats coding-tuned
  Kimi K2.7 Code variant existed briefly during this PR and was replaced
  by the K2.5 one before merge.)

### Changed
- `.kilo/kilo.jsonc`: new top-level `provider.openrouter.models` routing
  block (DeepSeek pinned; GLM 5.2 and Kimi K2.5 as commented
  alternates); header comment documents the passthrough and its two sharp
  edges (per-model-only placement, unvalidated fields); the `agent` section
  opens with a per-seat swap guide (exact `"model"` strings for the two
  alternates, the uncomment-the-routing-entry step, the per-alternate
  temperature rule — GLM 5.2 seats drop `temperature` because reasoning
  endpoints ignore sampling, Kimi K2.5 seats keep it — and seat guidance,
  including watching the Editor for round-1 sycophancy on budget models).
- `wiki/Kilo-Code-Setup.md`: §3.2 gains item 6 (per-model provider routing
  from `kilo.jsonc`, sharp edges, how to activate the alternates); §10
  troubleshooting gains a row for GLM-family mid-task stops / "did not
  provide any assistant messages" with the routing pin as the fix.
- `wiki/Agentic-Tools-and-Models.md`: §3.3 aggregator note and the §3.4
  DeepSeek-caching bullet now state that caching depends on landing on the
  first-party upstream and point at the routing block.

### Fixed
- `wiki/Kilo-Code-Setup.md` §5.1/§5.2: stale claim that the shipped config
  runs `deepseek-r1` on the Editor + Auditor seats — those seats have run
  DeepSeek 4 Pro with per-phase temperatures (0.3 / 0.6) since the config
  was last revised; the wiki now matches the file.

---

## 2026-07-05 — Voice + Intimacy Auditors: adversarial scenario classes + cold-read generation discipline

The Voice Auditor's simulation pass had a structural blind spot, visible in
the sample audit reports: nearly every check passed on every scenario. Two
causes. First, the test matrix contained only on-script scenarios — canonical
arc beats where `{{user}}` does what the scene expects — which is the one
case that almost never fails; trigger collisions, near-miss false triggers
(the offering-as-reflex bug class Step 3E exists for), off-script user
behavior, and deliberate probes into spec-silent territory (Step 3G's
material) were aspirations in Section 7, never matrix requirements. Second,
the auditor authored each dialogue while looking at the row's expected
register and trigger-to-verify, "with the specific intent of exercising the
mandate" — an author who knows the pass criteria produces conforming
dialogue every time, so the audit graded its own homework. This change
mandates adversarial scenario classes in Step 1 and splits author from
grader in Step 2: pre-commit the most plausible failure before writing,
generate from runtime context only with the expected columns out of view,
then audit. Every PASS now requires cited evidence (the dialogue line + the
draft line that compelled it) and must survive a counterfactual probe —
if the same drafts equally permit the failing version, the verdict is
⚠️ NOT BINDING (flagged Medium), the present-but-not-binding mandate being
precisely the bug class that otherwise surfaces only in long real sessions.
The Intimacy Auditor shared the identical structure (scenes generated with
the expected-substrate columns in view; "stress the spec" aspirational in
Section 8, never mandated in Step 1), so the same fix is ported there with
intimacy-specific scenario classes: a **hard-limit probe** (a scene that
invites crossing a declared hard limit, making "hard limits stress-tested"
a generated scenario rather than an entry inspection, and catching
function/substrate conflicts before the user's session) and a **substrate
near-miss** (a scene resembling a trauma-map trigger context with the
trigger absent — a spurious fire is as damaging in play as a missed one).
Check taxonomies are unchanged in both auditors, so the Auditioner's
by-reference reuse of those checks is untouched; the Arc Transition
Auditor is purely analytical (generates nothing) and does not share the
weakness.

### Changed
- `agent_roles/03b_The_Voice_Auditor.md`: new Foundational Rule 7
  (author/grader separation); Step 1 matrix gains Class and Plausible
  Failure columns plus four mandatory scenario classes per AI-played
  character (trigger-collision, near-miss/false-trigger, off-script
  pressure, coverage-void probe — counting toward the existing
  three-per-character-per-arc floor); Step 2 becomes a cold read
  (pre-commit → generate blind → audit); Step 3 gains the evidence rule and
  counterfactual probe governing every verdict; Step 4 diagnosis table gains
  the NOT BINDING row; report template carries class, plausible failure, and
  NOT BINDING findings under Medium; sign-off checklist gains
  scenario-class-coverage and cold-read-discipline items; Section 7
  reframed around the mandated classes and the do-not-write-toward-the-rubric
  discipline.
- `agent_roles/revise/03b_The_Voice_Auditor_mini.md`: new Foundational Delta
  7 — the parent's cold read, evidence rule, and counterfactual probe apply
  to all slice sampling; every touched trigger-response pair gets a
  near-miss scenario, collision scenarios when other triggers bear on the
  same scene type; evidence reproduction (R3.5.2) exempt from the
  out-of-view rule but not from the probe. Old delta 7 (Step 3J) renumbered
  to 8.
- `agent_roles/03d_The_Intimacy_Auditor.md`: Step 1 matrix gains Class and
  Plausible Failure columns; the "difficult intersections" list becomes five
  mandatory scenario classes per character with intimate presence
  (trigger-collision, function-shift, boundary, hard-limit probe, substrate
  near-miss — counting toward the existing floor); Step 2 becomes a cold
  read with intimacy-specific plausible-failure suspects (generic-erotica
  collapse, vanishing shield, skipped/spurious trauma trigger, function
  drifting to titillation); Step 3 gains the evidence rule and
  counterfactual probe; Step 4 diagnosis table gains the NOT BINDING row;
  report template and sign-off checklist updated (hard-limit stress-testing
  now explicitly via probe scenarios); Section 8 gains the
  do-not-write-toward-the-rubric discipline.
- `agent_roles/revise/03d_The_Intimacy_Auditor_mini.md`: new Foundational
  Delta 6 — parent cold read, evidence rule, and counterfactual probe apply
  to slice sampling; `intimacy_substrate_modify` revisions get a near-miss +
  hard-limit probe, register revisions get a function-shift/boundary
  scenario; evidence reproduction (R3.7.2) exempt from the out-of-view rule
  but not from the probe.
- `workflows/world-forge.md`: Phase 3.5 and 3.7 descriptions reflect the
  cold read and scenario classes.

---

## 2026-07-04 — Standalone improvement brainstorm: `/worldforge brainstorm --improve` + `Big_Brain_Storm.md`

The Brainstormer's improvement posture (Section 8) existed but was reachable
only chained behind a rebaseline conversion (`--then-brainstorm`), and the
only post-launch brainstorm door (`revise --brainstorm`) presumes something
already feels *wrong* and feeds the Reviser. A user carrying undecided
*ideas* — "would this fit? should something be added? can this be made
better?" — had no way to just ping-pong them against an existing world
without opening a revision or a conversion. `--improve` runs the improvement
posture standalone: read-only on the world's current state
(`Drafts/Master_Design.md` + Revision Log when built, `World_Seed.md`
otherwise), with nothing dispatched downstream. Its record is a new,
*standing* idea file — **`Big_Brain_Storm.md`** — distinct from the
run-scoped `Brainstorm_Notes.md`: rewritten fresh each standalone session
with still-open ideas curated forward, never consumed silently by any agent.
The organic pickup: a later `revise --brainstorm` run detects the file, asks
the user whether to fold its parked ideas into the diagnosis, and adapts a
chosen one into the revision-diagnostic `Brainstorm_Notes.md` the Reviser
scopes as normal (the Reviser itself never reads `Big_Brain_Storm.md`).
Ending a standalone session with parked ideas and no action is a legitimate
outcome.

### Added
- `agent_roles/Brainstormer/00_The_Brainstormer.md`: the standalone
  `--improve` door in Section 8 (per-door input rule, arrive-with-ideas
  opening, `Big_Brain_Storm.md` output with its own stamped header and
  curate-not-clobber discipline, per-door sign-off status lines) and Section
  9 step 1a (ask-first `Big_Brain_Storm.md` pickup, read-only in that
  posture, adapt-with-attribution into the diagnostic notes). Context
  Manifest lists the new inputs; `Big_Brain_Storm.md` is documented as the
  one deliberate exception to the "prior notes are never an input" rule.
- `workflows/world-forge.md`: `/worldforge brainstorm --improve` trigger row,
  the two-door improvement posture + `Big_Brain_Storm.md` contract in the
  BRAINSTORM section (incl. confirming intent when a bare `brainstorm` is
  invoked against a project that already has a world), and the project-tree
  entry for the standing file.
- `tutorial.md`: command-table row, "Testing ideas against an existing world"
  subsection in §9, §10.1 command entry, and pickup/contrast notes on the
  `revise --brainstorm` subsection and entries and the §8 `--then-brainstorm`
  walkthrough.
- `README.md`: trigger-command row + post-launch note.

### Changed
- `agent_roles/revise/00_The_Reviser.md`: `--brainstorm` invocation notes the
  upstream `Big_Brain_Storm.md` offer; the stale-notes gloss states the
  standing file is never the Reviser's input; Step 2 off-ramp gained the
  inverse pointer (undecided idea → `brainstorm --improve`, decided intent →
  Reviser).
- `workflows/world-forge-revise.md`: `--brainstorm` trigger row notes the
  `Big_Brain_Storm.md` offer.
- `workflows/world-forge-convert.md`: `--then-brainstorm` description points
  at the standalone door.
- `.kilo/kilo.jsonc`: `WorldForge-Brainstormer` seat description mentions the
  standalone improvement door and its standing file.
- `CLAUDE.md`: principles #6 and #11 and the Brainstormer cross-file row
  updated for the two-door improvement posture and the `Big_Brain_Storm.md`
  pickup contract.

---

## 2026-07-04 — Two new Brainstormer lenses: World & Factions, Cast & Voice

A coverage review of the Brainstormer's domain lenses found the four existing
ones (intimacy, appearance, realism, psychology) all character-shaped or
plausibility-shaped, leaving two suggestion domains without craft grounding:
the **world itself** (the improvement posture's own "this faction is the
flattest" example had no lens behind it, and the revision-diagnostic
vocabulary had no entry for "the world plays like a backdrop") and the
**cast as an ensemble plus per-character dialogue voice** (Section 3's
"generate the cast when asked" move had no lens, even though voice
distinctiveness is load-bearing downstream — the Voice Auditor's blind-line
test and the sandbox roster's fingerprint-uniqueness rule). A third candidate
(Systems & Powers, for heightened-world mechanics the Realism lens steps
aside from) was deliberately deferred until real friction shows.

### Added
- `agent_roles/Brainstormer/lenses/World_and_Factions_Lens.md`: factions as
  agendas (not hats), power with a named price, the renewable conflict
  engine, locations that provoke, lived-in texture, and what the world wants
  from `{{user}}` — with the premise-leads / genre-sets-the-pressure bright
  line.
- `agent_roles/Brainstormer/lenses/Cast_and_Voice_Lens.md`: cast built from
  friction rather than role-slots, relationship geometry beyond
  spokes-to-`{{user}}`, contrast pairs, right-sizing, and a distinct voice
  fingerprint per character (diction / rhythm / tics, the blind-line test) —
  the ensemble-level companion to the psychology lens.

### Changed
- `agent_roles/Brainstormer/00_The_Brainstormer.md`: Context Manifest lists
  the two new lenses; Section 3's lens paragraph counts six and adds the
  faction-fronting-NPC interlock example; the "generate the cast" move points
  at the Cast & Voice lens; Section 9's diagnostic vocabulary adds the two
  new symptom mappings (world-as-backdrop, NPCs who blur together).
- `agent_roles/Brainstormer/lenses/Character_Psychology_and_Motivation_Lens.md`,
  `Realism_Lens.md`, `Appearance_and_Style_Lens.md`: "Works with"
  cross-references to the new lenses.
- `CLAUDE.md` (principle #11), `workflows/world-forge-revise.md` (diagnostic
  front door), `tutorial.md` (Section 9 lens table + command reference):
  lens count four → six; tutorial table gains the two new rows.

---

## 2026-07-02 — Director-card style coherence: stop models treating the World Director as a character

Field report: on Director / NPC-host cards, some models (e.g. Kimi 2.7) burn
reasoning on — or act out — a contradiction the pipeline itself ships. The
style contract's `NARRATIVE PERSPECTIVE` templates anchor their focal clause
on `{{char}}`, and at runtime SillyTavern resolves `{{char}}` to the active
card's **name**: a Director turn in a `third_limited` world reads *"focal on
[Director card name] this turn… the narrator sees [Director card name]'s
interior"* while the card itself declares it is not a character. Three gaps
compounded: the Refiner's Director scan only fired for `first`/`second` world
defaults (so `third_limited` Director worlds shipped no override), the
omniscient override template still framed the Director as *"the focal
narrator"*, and on stock SillyTavern (no `world_forge` extension) per-card
override metadata is inert, leaving the world contract as the only style
authority on Director turns with no correction at all.

### Added
- `agent_roles/SHARED_Style_Contract_Reference.md`: **§3a-D Director-card
  variant** of the `NARRATIVE PERSPECTIVE` templates (`third_omniscient` /
  `third_limited` × tense) — states outright that `{{char}}` is not a
  character in the scene but the world's narrating voice and NPC host, focal
  on whichever scene character is being rendered; **§3d `DIRECTOR-CARD RULE`**
  — a conditional, world-agnostic line in the world `<style_contract>`
  (trigger: Master Design Section 11c `has_director_card: true`) that corrects
  the reading of any focal-on-`{{char}}` directive on Director turns, covering
  stock SillyTavern where overrides never splice; a §6 anti-pattern bullet
  (never emit character-shaped §3a prose for a Director-flagged card, or
  §3a-D prose for a character card).
- `agent_roles/01_The_Refiner.md`: Section 11c `has_director_card` flag +
  Director-flagged card list; sign-off items for the flag and the widened
  advisory.
- `agent_roles/05_The_Prompt_Engineer.md` + `agent_roles/05a_Block_Library.md`:
  the conditional `DIRECTOR-CARD RULE` line in the Main Prompt's
  `<style_contract>` (now two to four lines), Pass 1 presence/absence hard
  checks (with a fallback derivation from the Director criteria for Master
  Designs predating the flag), sign-off items, and resync handling (a
  missing-but-warranted line is ordinary spec drift resync adds).
- `templates/Char_Card_creation.md`: Director-card bullet pointing at the
  §3a-D variant and the runtime `{{char}}`-resolves-to-name failure mode.
- `CLAUDE.md`: cross-file consistency row for the Director-card style seam.

### Changed
- `agent_roles/01_The_Refiner.md`: Step 1.5 Pass 4 Director scan now runs
  regardless of the world default perspective, and the Section 11d POV
  ambiguity advisory triggers on every focal-anchored *effective* perspective
  (`first`, `second`, **and `third_limited`**) on a Director-flagged card —
  advisory text rewritten around the `{{char}}`-resolves-to-name mechanism.
- `agent_roles/02_The_Architect.md`: Director-flagged cards' override
  directives select SHARED §3a-D instead of §3a; worked example 3 updated to
  the Director-variant prose; pre-submission checklist item added.
- `agent_roles/03_The_Editor.md`: Step 5.6 Pass 2 makes template selection a
  hard check — §3a prose on a Director-flagged card (or §3a-D prose on a
  non-Director card) is a hard reject; sign-off updated.
- `agent_roles/revise/05_The_Prompt_Engineer_mini.md`: Trigger C widened from
  "multi-axis flag flip" to "Style Contract conditional-line flag flip" — a
  revision that adds/removes a Director card and flips `has_director_card`
  toggles the `DIRECTOR-CARD RULE` line, parallel to the ACTIVE-SPEAKER RULE.
- `workflows/world-forge.md` (Phase 5 Workstream B, revise/resync notes) +
  `workflows/world-forge-revise.md` (R5 preset triggers) + `CLAUDE.md`
  (principles #3 and #6 mini-PE toggle wording): mirrored the new conditional
  line end-to-end.

`Samples/` intentionally not regenerated in this change (pipeline specs only).

---

## 2026-07-02 — Runtime Directives: a seed-level channel for world-tuned preset blocks

The Chat Completion Preset's world-tuning was entirely inferred: the Prompt
Engineer predicted a world's runtime failure modes from the Master Design at
Phase 5, with no way for the *user* to state a runtime behavior they already
knew they wanted ("combat must feel slow and costly", "NPCs bargain — never
volunteer information for free"). If the analysis didn't predict the need, no
block carried it. This adds **Runtime Directives** — an optional World Seed
Section 9 that flows through Master Design Section 12 into the Block Selection
Rationale, where every directive must be implemented in a world-tunable block
(an extended world-specific core block, an adapted optional block, or a custom
block) and shown in a new Runtime Directive Coverage table. Directives are
explicitly forbidden from the world-agnostic engine surfaces (Main Prompt,
Jailbreak, Formatting, `<style_contract>` interior) — the override architecture
is untouched. The channel is fully optional: an empty or absent Section 9/12
changes nothing, and existing worlds are unaffected.

### Added
- `templates/World_Seed_Template.md`: Section 9 (RUNTIME DIRECTIVES, optional)
  — per-directive format (imperative behavior + "wrong response looks like"
  example + scope), routing guardrails (world facts → §2, character behavior →
  §4, style → §1.5, arc tone → §5), the forbidden-target boundary note, and a
  submission-checklist block.
- `agent_roles/00_The_Interviewer.md`: interview SECTION 9 — optional late-
  interview elicitation, push-to-observable-behavior guidance, reroute rules,
  sign-off coverage line.
- `agent_roles/01_The_Refiner.md`: Step 1.6 (Runtime Directive Classification:
  shape validation, reroute of misplaced content, `UNRESOLVED_QUESTIONS.md` for
  untestable directives), Master Design SECTION 12 (`RD-N` record format), Step
  1 classification bullet, sign-off section.
- `agent_roles/05_The_Prompt_Engineer.md`: Section 5.0b Step 2b (directive
  intake as requirements, legitimate vs. forbidden block targets), Runtime
  Directive Coverage table in the Rationale format and audit-report Section 9,
  Pass 2 content check, sign-off lines, and Preset Resync Step 2 re-derivation
  (a directive the live preset doesn't implement surfaces as CHANGED/ADDED).
- `templates/Convert_Brief_Template.md`: Section 4i (Runtime Directives
  preservation decision).

### Changed
- `agent_roles/05a_Block_Library.md`: custom-block guidance names Master Design
  Section 12 directives as a primary custom-block source (behavior → imperative
  content, wrong_response → anti-failure-mode statement, scope → placement).
- `workflows/world-forge.md`: Phase 0 interview list (item 10), Phase 1 Master
  Design contents, Phase 5 Workstream B description.
- `agent_roles/Converter/00_The_Converter.md`: preservation matrix row for
  Section 9 (keep by default; protagonist- and arc-coupled directives strip +
  mark), Step 6 seed-writing rule, sign-off coverage line.
- `CLAUDE.md`: cross-file consistency table row for the Runtime Directives
  channel.

---

## 2026-07-01 — Tutorial: document `/worldforge audition`

`tutorial.md` never referenced the Auditioner (`/worldforge audition`), even
though it's documented in `workflows/world-forge.md` and `CLAUDE.md`. No
pipeline behavior changed; this closes the documentation gap.

### Added
- `tutorial.md`: `/worldforge audition` and `--save` rows in the Section 2
  trigger-commands table; the audition step in the Section 10 lifecycle
  sentence; a new **Section 10.6** walkthrough (verdicts, read-only scope,
  the revise-handle hand-off, relation to the Voice Auditor); a pointer to
  `agent_roles/Auditioner/00_The_Auditioner.md` in Section 12.

---

## 2026-06-30 — World Calendar seam: producer support for the Scene Tracker date seed

The fork's `world-forge` Scene Tracker extension gained an in-world calendar
(weekday tied to a day counter, anchored month/year, a `Day X of N` horizon, and
open-ended mode) and can **seed** it on a fresh chat from an optional world-level
`[[WORLD_CALENDAR]]` lorebook entry (ST PR #42). This adds the **producer** half:
a new runtime seam in the canonical contract and end-to-end pipeline support so a
World Seed that fixes an in-world start date emits the carrier. The seam is fully
optional — absent ⇒ the Scene Tracker keeps its manual per-chat behavior and
existing worlds are unaffected.

The carrier's one load-bearing subtlety: unlike the `[[NPC_MANIFEST]]` carrier
(emitted `disable: true`), the calendar carrier MUST be **enabled**
(`disable: false`) because the Scene Tracker reads candidates from
`getSortedEntries()` with a `!disable` filter and silently skips disabled ones;
it stays inert via `key: []` + `constant: false`. Months are **0-indexed**
(0 = January), matching the consumer.

### Added
- `contracts/WORLD_FORGE_SYNC.md` **§5 World calendar (Scene Tracker date seed)**;
  document bumped **Version 1 → 2**. New §5 specifies the `[[WORLD_CALENDAR]]`
  carrier (marker, the enabled-not-disabled flag, the JSON payload, 0-indexed
  months, open-ended semantics) and the producer ask; §7 checklist and §8 table
  updated; the consumer-direction / checklist / relationship sections renumbered
  §5→§6, §6→§7, §7→§8.
- `templates/World_Seed_Template.md` **§2g World Calendar** (optional): start
  date, end/horizon-or-open-ended, Day 1 weekday; submission-checklist line added.
- `tools/validate_export.py`: `check_world_calendar()` — **WARN-only** backstop
  (the seam is optional and degrades gracefully) for >1 carrier, non-JSON content,
  `start`/`end` month not 0–11, `weekdayOfDay1` not 0–6, bad `end` shape, and a
  `disable: true` carrier the Scene Tracker would skip. Warnings never change exit
  status; the summary line now reports a warning count. Still read-only, stdlib-only.

### Changed
- `agent_roles/00_The_Interviewer.md` (Section 2): asks *when* the world is set
  (era/period/year) and its *horizon* (deadline-or-open-ended) as a setting +
  intent question — era routes to the Setting lore (Section 2a), a concrete date +
  horizon routes to the §2g calendar carrier.
- `agent_roles/01_The_Refiner.md` (Master Design Section 1): records a
  `World Calendar (Scene Tracker seed)` line with 0-indexed months / 0–6 weekday
  when World Seed §2g is filled.
- `agent_roles/02_The_Architect.md` (§6 + sign-off): authors the
  `### CARRIER: [[WORLD_CALENDAR]]` block in the Tier 1 World draft (enabled +
  inert, payload from the seed) when the Master Design has a calendar.
- `agent_roles/03_The_Editor.md` (new **Step 4.7** + sign-off): validates the
  carrier when present (enabled-not-disabled, parseable payload, months 0–11,
  weekday 0–6, `end` object/omitted/`"infinite"`, no null placeholders).
- `agent_roles/04_The_Compiler.md` (new **Step 7.8** + Step 5 note, validation
  pass, output-manifest sign-off): transcribes the carrier verbatim into the
  World Lorebook JSON with the enabled-but-inert flags.
- `agent_roles/revise/04_The_Compiler_mini.md`: **preserves** an existing
  `[[WORLD_CALENDAR]]` carrier through a World-lorebook rewrite (UID + flags +
  payload), the same way it regenerates the NPC manifest; never drops it and never
  adds one to a lorebook that lacked it. Editing the calendar is an ordinary
  `tier1_world_rule_modify` — the mini-Architect/mini-Editor inherit the parent's
  §6 authoring / Step 4.7 validation, so no new revise scope type.
- Convert pipeline carries the seam: `agent_roles/Converter/00_The_Converter.md`
  (preservation matrix row + Section 2 seed-writing) and
  `templates/Convert_Brief_Template.md` (§4d) carry the calendar across a reframe
  when the era is unchanged, regenerate/drop it when the setting's time period
  differs, and keep it by default in rebaseline (it is not protagonist-coupled).
- `CLAUDE.md`: contract description line + a new cross-file-consistency row for
  the calendar seam (incl. the revise + convert cascade touchpoints).

---

## 2026-06-28 — Shared design contracts made canonical; pipeline now guarantees the runtime seams

World Forge is the **producer** in a contract it shares with the fork's
`world-forge` + `npc-memory` SillyTavern extensions. Those contracts now live in
this repo as the **canonical source of truth** (the fork mirrors them read-only
and CI-checks byte-equality), and the pipeline is tightened so it *guarantees*
the runtime seams `WORLD_FORGE_SYNC.md` §2–§4 describe instead of only happening
to satisfy them in the hand-built `Samples/` world.

### Added
- `contracts/` directory: `MEMORY_CONTRACT.md` and `WORLD_FORGE_SYNC.md` (the
  canonical copies, kept byte-identical to the fork's mirror) plus `README.md`
  describing the canonical/mirror relationship.
- `tools/validate_export.py`: deterministic backstops for the new seams —
  manifest `lorebook.kind` enum check; per-npc **bare-first-name alias** check
  (`WORLD_FORGE_SYNC` §3); and an export-set check that a `kind:"director"`
  manifest is accompanied by a card carrying a recognized director tag
  (`WORLD_FORGE_SYNC` §2, directory runs only). No new files written; still
  read-only and stdlib-only.

### Changed
- `agent_roles/02_The_Architect.md` + `templates/Char_Card_creation.md` (§2):
  a Director / NPC-host card MUST carry a recognized director tag
  (`world-director` / `world director` / `npc-controller` / `npc controller` /
  `director` / `npc`), declared in the card draft so it survives export and
  agrees with the roster manifest's `kind:"director"`.
- `agent_roles/04_The_Compiler.md`: Step 4 now carries the director tag through
  to `data.tags` (§2); Step 7.7i now **requires** the bare first name + prose
  nicknames in every multi-word npc's `aliases` (§3, previously only
  recommended), because the Scene Tracker → npc-memory name round-trip depends
  on it. Manifest sign-off checklist updated.
- `agent_roles/05_The_Prompt_Engineer.md` + `agent_roles/05a_Block_Library.md`
  (§4): the closing `</style_contract>` marker is pinned as a verbatim literal
  (no attributes, exact casing) — the `world_forge` extension splices per-card
  `<style_override>` by a plain substring search for it, so any deviation drops
  the override silently. Added a Pass-1 hard-fail.
- `CLAUDE.md`: `contracts/` added to the authoritative repository structure.

## 2026-06-28 — Author's Note suggestions: teach the player SillyTavern's transient steering lever (#61)

The world package carries all *persistent* steering (cards, lorebooks, preset),
but SillyTavern's **Author's Note** — a per-chat, ephemeral nudge the player
sets by hand and that injects near the end of context — is the player's
*transient* lever, and most players never learn to use it well. A true Author's
Note is not shippable (it lives in per-chat metadata / global settings, not the
card JSON), so the right move is not to bake one into the package but to hand
the player a few ready-to-paste, world-tuned examples plus a short primer. The
Prompt Engineer already had the right context (it has read the Master Design and
reasons about runtime injection), so it gains one small player-facing output.
This touches none of the load-bearing architecture: it is suggestions only, it
writes a brand-new standalone file and modifies nothing else, so audit/apply
separation (principle #3) is untouched.

### Added
- **`agent_roles/05_The_Prompt_Engineer.md`** — new **Section 4c, Author's Note
  Suggestions**, a Build-mode-only deliverable. The Prompt Engineer writes a
  standalone `Export/Authors_Note_Suggestions.md` containing: a mechanics primer
  (the Author's Note is per-chat/ephemeral; recommended In-chat @ Depth 4, role
  System); 3–5 world-tuned example notes across pace/scene-hold, tonal-register
  dial, NPC-agency push, refocus, and (when intimate content is in scope)
  intimacy-pacing categories; and a "transient steering only — permanent
  steering belongs in the package" boundary note. Added a Tertiary Output entry
  (Section 6) and sign-off items for it.

### Changed
- **`workflows/world-forge.md`** — Phase 5 output line, a Workstream note, and
  the `Export/` deliverables tree now list `Authors_Note_Suggestions.md`.

---

## 2026-06-28 — Adaptation posture: turn an existing story/fanfiction/RP into a world precursor (#62)

World Forge had three upstream-of-Phase-0 entry points — the Brainstormer (from a
fragment), the Converter (from a shipped World Forge world), and the Interviewer
(cold) — but no way to start from an **existing narrative document** a user
already had. This adds a fourth Brainstormer posture for exactly that: read a
story, fanfiction, or roleplay log and extract the playable world latent in it,
landing a precursor the Interviewer builds a seed from. It stays behind the
load-bearing bright line (principle #11) — it writes only informal
`Brainstorm_Notes.md`, never a World Seed, and it extracts what is on the page
rather than inventing over the document's silences.

### Added
- **`agent_roles/Brainstormer/00_The_Brainstormer.md`** — new **Section 10,
  the adaptation posture**, invoked by `/worldforge brainstorm --adapt
  <document_path>`. It reads the document read-only and:
  - extracts the **world** (cast, setting, tone, factions, locations,
    relationships), attributed to the source;
  - extracts the **prose style as a finished sample** for the Style Contract
    (perspective, tense, register, rhythm, **pacing**, distinctive markers);
  - extracts **per-character dialogue voice** — a voice fingerprint plus 1–2
    *verbatim* sample lines lifted from the text (the anchor that seeds cards
    and the Voice Auditor);
  - extracts any **intimate register** the source shows (dynamics, explicitness,
    kinks/fetishes/acts) as raw material for the Intimacy Architect (Phase 2.5);
  - **recommends the `{{user}}` slot from the document's POV and confirms** —
    play as the source's protagonist / a new insert / a promoted side character —
    rather than presenting a cold menu or deciding silently;
  - **flags what the document doesn't supply** (interior wounds, rule costs,
    stakes, NPC goals) as gaps for the Interviewer, never inventing over them.

  Writes an `adaptation`-stamped `Brainstorm_Notes.md` with dedicated slots for
  the extracted world, prose/style sample, per-character voice, intimate register,
  the `{{user}}` decision, and the gap list. Objective (four entry modes),
  Context Manifest (the `--adapt` source input), and sign-off all updated.

### Changed
- **`agent_roles/00_The_Interviewer.md`** — accepts the `adaptation` stamp as a
  `fresh-start`-equivalent for `/worldforge start`; reads the extracted prose
  sample, per-character voice (with sample lines), and intimate register as
  confirmed starting points feeding Section 1.5 / Section 5 / Section 8, while
  still running the full interview and pushing hardest on the flagged gaps.
- **`workflows/world-forge.md`** — BRAINSTORM section now documents four postures
  and the `--adapt` invocation; new trigger-table row.
- **`.kilo/kilo.jsonc`** — `WorldForge-Brainstormer` seat description notes the
  adaptation posture.
- **`CLAUDE.md`** — principle #11 and the Brainstormer cross-file-consistency
  row updated to four postures incl. adaptation.
- **`tutorial.md`** — Section 9 now lists four postures, adds a "Turning a story
  into a world" walkthrough, and a command-reference entry for `--adapt`.

## 2026-06-26 — Brainstormer overwrites a stale `Brainstorm_Notes.md` instead of requiring manual deletion

`/worldforge revise --brainstorm` (and the other brainstorm entry points) left a
single shared `Brainstorm_Notes.md` per project folder with no defined behavior
when one already existed. A world in active play almost always still has the
notes file from when it was first built, so running the revision-diagnostic
brainstorm against it produced ambiguous/append behavior and the user had to
delete the file by hand before each run. The consumers (Reviser, Interviewer)
also read the file "if present" without checking which run produced it, so a
stale wrong-posture file could be mistaken for the current one.

### Changed
- **`agent_roles/Brainstormer/00_The_Brainstormer.md`** — the notes file now
  carries a stamped header (`Posture: fresh-start | improvement |
  revision-diagnostic` + `Written:` date) and an explicit **overwrite-on-write**
  rule: there is exactly one `Brainstorm_Notes.md` per project and every run
  writes it fresh, replacing any prior file in full (never append/merge). The
  Context Manifest notes a pre-existing notes file is a stale output to
  overwrite, never an input. All three output sections (6, 8, 9) and the
  sign-off checklist enforce the stamp + fresh-write discipline.
- **`agent_roles/revise/00_The_Reviser.md`** — consumes `Brainstorm_Notes.md`
  only on a `--brainstorm` run *and* only when its header reads
  `Posture: revision-diagnostic`; a stale or wrong-posture file is ignored and
  intent is discovered normally (INPUT + Step 2).
- **`agent_roles/00_The_Interviewer.md`** — reads the notes as starting material
  only when the `Posture:` stamp matches the entry point (`fresh-start` for
  `/worldforge start`, `improvement` for a `--then-brainstorm` chain); a
  mismatched/stale file is ignored (Context Manifest + Section 4 + Section 9).

## 2026-06-24 — Document how to set prose style via the Style Contract (#43)

Issue #43 asked for a post-Phase-3 agent that hunts and removes "common tropes"
(antithetical "X, not Y" constructions, poetic-over-factual phrasing) from the
lore. The pipeline deliberately has no house voice and does no "slop removal"
(README, *On prose quality and "slop"*); the supported lever already exists —
the World Seed **Section 1.5 Style Contract**, whose free-text **Style Notes**
field flows into the preset's Main Prompt and governs every turn. The gap was
discoverability, not capability, so this adds a tutorial section showing how to
use it rather than a new agent.

### Added
- **`tutorial.md`** — new **Section 11, "Setting your prose style (the Style
  Contract)"**: the six enum fields plus Style Notes, what `DEFAULTS` expands to
  (with a sample turn), a leaner "typical roleplay" register example (second-
  person present, terse) including Style Notes that steer away from literary
  tropes, a Style-Notes tuning guide that names the anti-"slop" use explicitly,
  and where the contract gets applied across the pipeline.

### Changed
- **`tutorial.md`** — the Phase 0 case-study mention of Section 1.5 now points
  forward to the new Section 11; the trailing **"Where to learn more"** section
  renumbered from 11 to 12 (no inbound anchor links).

The Compiler now prefixes **every exported lorebook/register filename** with
`[WorldName]_` — the same world-name token already used for
`[WorldName]_ChatPreset.json`. So a world named *Crimson Harbor* now ships
`CrimsonHarbor_World_Lorebook.json`, `CrimsonHarbor_Anna_Lorebook.json`,
`CrimsonHarbor_Arc1_Lorebook.json`, and so on. SillyTavern names a standalone
World Info world by its **imported filename** (not the internal `name` field),
so the prefix makes a world's entire lorebook set sort and group together as one
block in ST's alphabetical World Info list — the request in #42. Character cards
and `User.md` are not prefixed. This is a filename-only change: no entry content,
UID, position, or flag changes, so it does not disturb running chat state.

### Changed
- **`agent_roles/04_The_Compiler.md`** — new file-naming convention before Step 5;
  Steps 5/6/7A/7B, the intimacy registers, the output manifest, the sign-off
  checklist, and the persona-link instruction all carry the `[WorldName]_` prefix;
  the lorebook `name` field is set to match the filename.
- **`agent_roles/02_The_Architect.md`, `agent_roles/03_The_Editor.md`,
  `templates/User_Persona_template.md`** — the protagonist-lorebook filename in the
  persona Setup Instructions (authored by the Architect, validated by the Editor)
  carries the prefix.
- **`workflows/world-forge.md`, `agent_roles/01_The_Refiner.md`,
  `agent_roles/05_The_Prompt_Engineer.md`, `templates/World_Seed_Template.md`** —
  output descriptions updated to the prefixed convention.

### Revision-pipeline safety
- **`agent_roles/revise/04_The_Compiler_mini.md`** (+ Reviser and Refiner-mini
  cascade notes) — the prefix is a **new-build** convention. The revise pipeline
  never retro-renames a shipped world's Export files (renaming changes the ST world
  name and orphans the user's links, exactly what UID preservation exists to avoid);
  it matches the world's existing on-disk naming. Migrating an old world onto the
  prefix is a Convert/Rebaseline concern, not a surgical revision.

---

## 2026-06-22 — Remove the consolidated Group lorebook (#40)

The consolidated **Group lorebook** (`Export/Group_Lorebook.json`) — the single
file the Compiler built by merging every Tier 1/2/3 entry with re-sequenced UIDs
— is **removed**. Per-character and per-tier lorebooks are the supported delivery
format; SillyTavern group chats load those (plus the protagonist persona
lorebook) directly, so the merged-everything artifact was redundant at runtime.
It also re-sequenced every UID from 0, which forced a bug-prone parallel set of
rules — most acutely the NPC Memory Manifest re-derivation against the new UIDs.
Removing it simplifies the manifest to **per-file carriers only**. This follows
the deprecation tracked in #40.

### Removed
- **`agent_roles/04_The_Compiler.md`** — Step 8 (Build Group Lorebook) and Step
  7.7i (Group combined-manifest re-derivation); the subsequent sub-steps and the
  Validation Pass renumber/shed their Group lines; OUTPUT MANIFEST and sign-off
  Group entries dropped; the two Group template references removed from the
  Context Manifest and Schema Sources.
- **`templates/Group_lorebook_template.md`** and
  **`templates/Group_lorebook_template.json`** — retired.
- **`agent_roles/05_The_Prompt_Engineer.md`** — the Group Lorebook Structural
  Audit (§3e), its report section, and its sign-off line.

### Changed
- **`agent_roles/revise/04_The_Compiler_mini.md`** — drops the "regenerate
  Group_Lorebook" operational model; the mini now recompiles only the touched
  individual lorebooks. The "what changes when" report and `REVISED_FILES.md`
  manifest no longer reference the Group file.
- **`agent_roles/revise/01_The_Refiner_mini.md`**,
  **`agent_roles/revise/00_The_Reviser.md`** — cascade rows no longer flag
  Group_Lorebook regeneration; the Revision Log entry drops its Group regen field.
- **`agent_roles/00_The_Interviewer.md`**, **`workflows/world-forge.md`**,
  **`workflows/world-forge-revise.md`**, **`templates/World_Seed_Template.md`**,
  **`README.md`**, **`tutorial.md`** — output lists, repo trees, and ST import
  instructions updated; users now import the individual lorebooks (re-importing
  only the lorebooks a revision touched).
- **`CLAUDE.md`** — repo-structure listing, principle #12 manifest notes, the
  failure-mode bullet, and the NPC-manifest cross-file consistency row updated to
  the per-file-only model.
- **`tools/validate_export.py`** — `check_manifest` docstring updated (no Group
  re-derivation); logic unchanged (it validates whatever lorebook files exist).

### Notes
- The Lucifer sample (`Samples/`) retains its historical
  `Lucifer-Group_Lorebook.json` and references as a dated snapshot of the prior
  pipeline output; it is intentionally left unregenerated.

## 2026-06-22 — Brainstormer: domain lenses + revision-diagnostic posture (#46)

The Brainstormer (introduced #37, below) gains craft grounding and a third
entry mode. Four on-demand **domain lenses** load only when a brainstorm turns
toward their domain, and a new **revision-diagnostic posture** serves the
post-launch "something feels off but I can't name what to revise" case. All of
it stays non-prescriptive — reference shelves for the Brainstormer's own
riffing, never separate voices, never scorers or feasibility-checkers.

### Added
- **Four domain lenses** (`agent_roles/Brainstormer/lenses/`), loaded on demand
  to preserve context budget: **Intimacy & Dynamics** (kink-as-character, not
  bolt-on), **Appearance & Style** (looks derived from role / activity / genre
  rather than reflexive defaults), **Realism** (consequence / constraint /
  expertise as a tool, deferring to genre register), and **Character Psychology
  & Motivation** (want / need / fear, humanizing contradictions, lines a
  character won't cross). Each carries a "bright line" section restating what the
  Brainstormer does NOT do (author, classify tiers, impose constraints).
- **Revision-diagnostic posture** (third entry mode) — `/worldforge revise
  --brainstorm` runs the Brainstormer against a shipped world's
  `Drafts/Master_Design.md` (read-only), diagnoses the primary concern
  divergently, and writes it to `Brainstorm_Notes.md`; the Reviser then reads
  that as captured intent. Enforces the same Section 1 / 11a / World Mode bright
  line and bounces an out-of-scope diagnosis rather than dressing it as a
  revision.
- **Expanded technique guidance** — sketching register via short prose excerpts,
  creative touchstones to anchor tone, generating a cast when asked (not
  deflecting), dodging clichés while still offering them as valid choices, and
  the "where does it sag?" soft-spot move.

### Changed
- **`agent_roles/revise/00_The_Reviser.md`**, **`workflows/world-forge-revise.md`**
  — the `--brainstorm` front door and the Reviser's read of a
  revision-diagnostic `Brainstorm_Notes.md`.
- **`CLAUDE.md`** — clarified that a `World Mode` (arc | sandbox) flip is out of
  revise scope (full rebuild).
- **Docs (#48):** `tutorial.md` Section 9 (the three postures, the four lenses
  with example nudges, the `revise --brainstorm` flow) and `README.md` (the
  `/worldforge revise --brainstorm` trigger row + a post-launch note).

---

## 2026-06-22 — Tutorial command reference (#49)

### Added
- **`tutorial.md` Section 10** — a single example-driven reference for every
  `/worldforge` command and flag, organized by lifecycle (start, in-flight
  control, revise, resync-preset, convert), each pairing an example invocation
  with what it does and why you'd reach for it, using the Lucifer project for
  continuity. "Where to learn more" renumbered to Section 11; a pointer added
  from the Section 2 trigger table. Docs only.

---

## 2026-06-18 — NPC Memory Manifest: producer side of the npc-memory contract

World Forge becomes the **producer** side of the **NPC Memory Contract**
(`schema 1`), a spec shared with the `npc-memory` SillyTavern extension (which
lives in the ST fork, not this repo). The extension attaches per-NPC memory
keyed by a **stable slug id** instead of a volatile UID; World Forge's
obligation is to emit a machine-readable index — the **manifest** — as an inert
World Info entry embedded in the lorebooks the Compiler already builds. The
feature is purely additive: it changes no existing entry, emits no new file, and
a world without it still works via the extension's prose fallback.

### Added
- **`agent_roles/04_The_Compiler.md`** — **Step 7.7** (Emit NPC Memory Manifest
  entries): carrier format (`comment` begins `[[NPC_MANIFEST]]`, `disable: true`,
  `key: []`), JSON payload shape, the slug-id rule (`Anna Larsson` →
  `anna_larsson`, derived from the canonical name, never the UID), persona-vs-npc
  split, facet typing (normalizing both the `NPC — Name (Facet)` and
  `Name — Aspect` comment conventions to one npc per character), `relationships[]`
  edges, arc `scenes[]` from `BEAT —` entries, per-file vs. Group placement, and
  the Group re-derivation against re-sequenced UIDs. Step 9 validation lines and a
  sign-off subsection added.
- **`agent_roles/revise/04_The_Compiler_mini.md`** — foundational delta: regenerate
  a touched lorebook's manifest against preserved + new UIDs (slug ids stay
  stable, so a running memory store stays attached across revisions); Group
  re-derivation; sign-off lines.
- **`tools/validate_export.py`** — read-only `check_manifest` backstop: at most one
  `[[NPC_MANIFEST]]` per file, carrier flags, JSON-parse, slug validity, and
  facet/scene uid resolution within the same file.
- **`NPC_Memory_Seed_Proposal.md`** (new; `.kilocodeignore`'d as maintenance doc) —
  a coordination draft proposing a `schema 2` per-NPC starting-memory `seed` field
  (the "NPC was just finishing the laundry" warm-start), with seed-once/no-clobber
  semantics and open questions for the extension maintainer. Not implemented;
  awaiting consumer-side agreement.

### Changed
- **`CLAUDE.md`** — new architectural **principle #12** (NPC Memory Manifest),
  a cross-file consistency row (Compiler Step 7.7 ↔ mini-Compiler ↔ validator), and
  a common-failure bullet (never key memory by UID; never copy per-file manifest
  uids into the Group lorebook).
- **`workflows/world-forge.md`** — Phase 4 build list notes the embedded manifest.

### Deferred
- The contract's optional per-message **turn tag** (`<!--npcmem:{...}-->`, runtime
  lever) is not implemented on the producer side — a separate preset/card-level
  change if pursued.

---

## 2026-06-18 — validate_export: clean exit on SIGPIPE (#39)

### Fixed
- **`tools/validate_export.py`** — piping the validator into a reader that closes
  early (e.g. `head`) ended a clean run with a `BrokenPipeError` traceback,
  making a working diagnostic look like a crash and distorting the exit status
  the shell sees. The `__main__` guard now catches `BrokenPipeError` and exits
  quietly like other Unix CLIs. Output plumbing only — no validation behavior or
  exit-code change for complete runs; stays within the file's stdlib-only,
  read-only standing exception. Closes #32. (Reported and fixed by @SAY-5.)

---

## 2026-06-17 — Convert flags surfaced in the README (#38)

### Changed
- **`README.md`** — the `/worldforge convert` command-table entry now lists the
  `--brief`, `--rebaseline`, and `--then-interview` / `--then-brainstorm` modes
  (already supported in the pipeline) and links to tutorial §8 for the detailed
  guidance. Docs only.

---

## 2026-06-14 — The Brainstormer: optional divergent ideation upstream of Phase 0 (#37)

A new optional entry point for users who arrive with only a vibe or a fragment
and nothing solid enough for the Interviewer's structured, specificity-demanding
questions to land. The Brainstormer is the **divergent** counterpart to the
convergent Interviewer — it generates premise directions, yes-ands instincts,
and converges only when an idea has a pulse, then hands off to `/worldforge
start`.

### Added
- **`agent_roles/Brainstormer/00_The_Brainstormer.md`** — generates multiple
  directions and follows sparks; converges on a premise with a pulse (central
  tension + feel + at least one anchor). Two entry modes at introduction:
  fresh-start ideation and an improvement posture for brainstorming changes to an
  already-consolidated world. **Load-bearing bright line:** it writes only
  informal `Brainstorm_Notes.md`, never a `World_Seed.md` — seed authorship
  belongs to the Interviewer alone. It advances no pipeline state and invokes no
  downstream agent; it is a skippable front porch.
- **`.kilo/kilo.jsonc`** — a `WorldForge-Brainstormer` seat (DeepSeek v4 Pro,
  temperature 0.9 for divergent ideation).

### Changed
- **`agent_roles/00_The_Interviewer.md`** — Context Manifest loads
  `Brainstorm_Notes.md` if present as raw starting material (not as answers; the
  full interview still runs).
- **`agent_roles/Converter/00_The_Converter.md`** — `--then-brainstorm` flag for
  rebaseline chains (consolidate, brainstorm improvements, then the Interviewer
  reworks the seed; Section 9 Step H).
- **`workflows/world-forge.md`** (new BRAINSTORM section),
  **`workflows/world-forge-convert.md`** (`--then-brainstorm` chaining),
  **`tutorial.md`**, **`AGENTS.md`**, and **`CLAUDE.md`** (the new
  `agent_roles/Brainstormer/` folder; role documented as upstream ideation, not a
  pipeline phase).

---

## 2026-06-12 — Roo Code retirement: Kilo Code becomes the reference tool

Roo Code — the agentic extension the pipeline was originally authored against —
shut down all its products on May 15, 2026 (extension archived, repository
read-only, no further updates). Documentation-only change (#29, reported by
mrzando-lastone): nothing in the pipeline itself was Roo-specific, and the only
shipped tool configuration was already Kilo Code's (`.kilo/kilo.jsonc`,
`.kilocodeignore`).

### Changed
- **`wiki/Agentic-Tools-and-Models.md`** — Kilo Code promoted to §2.1
  (recommended — reference tool), absorbing the orchestration rationale from
  the old Roo section; Roo Code demoted to §2.3 as a retired entry with
  migration guidance (Kilo Code as the fork with shared history, Cline as Roo's
  own parting recommendation); compatibility table, troubleshooting rows,
  model-section asides, and summary updated accordingly.
- **`README.md`, `tutorial.md`** — Roo Code removed from the prerequisites and
  quick-start tool lists; Kilo Code listed as recommended. The Grok
  model-caveat note keeps its historical Roo reference, marked as retired.
- **`CLAUDE.md`, `AGENTS.md`, `wiki/README.md`, `wiki/Kilo-Code-Setup.md`,
  `.kilocodeignore`** — remaining "typically Roo Code" / "Kilo/Roo/Cline" /
  "rather than Roo Code" phrasings updated; purely historical mentions
  (lineage, changelog) retained.

### Unchanged
- No agent spec, template, or workflow file referenced Roo Code; none were
  touched. Earlier CHANGELOG entries keep their historical Roo mentions.

---

## 2026-06-12 — Lorebook export schema: entry key/UID parity + camelCase entry fields

Both fixes verified against the official SillyTavern source (`world-info.js`,
release branch, 2026-06-12) before any file was edited, per the
`Notes_On_functionality.md` editing rule.

### Fixed
- **Lorebook entries invisible after import — entry object key must equal
  `String(uid)`** (#31, reported by mrzando-lastone). SillyTavern stores and
  looks up world-info entries as `entries[uid]` (`createWorldInfoEntry` /
  `getFreeWorldEntryUid`, and every editor read/write), so an entry keyed `"1"`
  with `"uid": 20` imports without error and then **never renders in the World
  Info editor**. The spec previously said only "sequential string keys starting
  from `"0"`", which is safe when UIDs are sequential but left the door open for
  exactly this drift. The **Compiler** gains **Foundational Rule 9** (key ==
  `String(uid)`, hard-fail), a Group-Lorebook re-key note (re-sequenced UIDs get
  re-keyed), Step 9 validation checks, and sign-off items; the **mini-Compiler**
  inherits it with the preserved-UID case called out (a preserved UID 20 keeps
  key `"20"` — never re-key survivors to sequential positions).
- **snake_case alias fields in the lorebook templates.**
  `templates/Lorebook_Template.json`, `templates/Group_lorebook_template.json`,
  and both authoring guides carried `case_sensitive` / `match_whole_words` /
  `use_regex` and the legacy `characterFilterNames` / `characterFilterExclude`
  pair. Those names belong to the embedded `character_book` card format
  (Notes §5.1b) — in a standalone World Info file ST stores them but the GUI
  reads only the camelCase fields, so the values were silently dead. Replaced
  with the canonical nullable overrides (`scanDepth`, `caseSensitive`,
  `matchWholeWords`, `useGroupScoring`) plus `displayIndex`, and enforced as
  Compiler **Foundational Rule 10** (no snake_case aliases, hard-fail).

### Changed
- **`agent_roles/04_The_Compiler.md`** — Foundational Rules 9 + 10 (ten guards
  total), entry field-table rows for the new fields, lorebook-level `entries`
  description rewritten around the key==uid invariant, Step 8 re-key note,
  Step 9 checks, sign-off items.
- **`agent_roles/revise/04_The_Compiler_mini.md`** — guard count 8 → 10, key
  parity in the UID-continuity step, sign-off items.
- **`tools/validate_export.py`** — deterministically re-checks both failure
  modes (key/UID parity, snake_case alias fields); still strictly read-only.
- **`Notes_On_functionality.md`** — key==uid mechanics in §3.2 / §5.2 / §6
  gotchas, camelCase-vs-`character_book` field-name note, `displayIndex` added
  to the §5.2 exemplar, `characterFilter` quick-reference row.
- **`Notes_Quick_Reference.md`** — affected facts regenerated (key parity,
  camelCase field names, `displayIndex` fallback).
- **`agent_roles/05_The_Prompt_Engineer.md`** (+ mini) — stale
  `match_whole_words` reference → `matchWholeWords`; mini's "eight pre-save
  gates" pointer updated.
- **`CLAUDE.md`** — validator check lists updated; new common-failure-mode
  bullet (keying entries by sequential position instead of by UID).
- **`agent_roles/04_The_Compiler.md` Step 9** — the "No Markdown syntax leaked
  into JSON string values" check clarified to target structural leakage
  (unescaped quotes/newlines, code fences, headers wrapping the JSON), with an
  explicit mandate that draft content transfers **verbatim including markdown
  emphasis** — never strip `**bold**` markers from entry content, since
  ARC_STATE / SANDBOX_STATE depend on their literal `**Dramatic Situation:**` /
  `**Tonal Mandate:**` labels. Found via a cold-context compliance test of the
  rewritten spec (a fresh small-model Compiler run passed Rules 9/10 on its
  first write but read the old wording as license to strip bold markers from
  ARC_STATE content).

### Notes
- Two corrections to the fix proposed in #31, both from the ST source:
  `characterFilter` is **optional** (ST's own editor deletes the empty object —
  the templates omit it rather than mandating it), and `displayIndex` falls
  back to `uid` when missing (the pipeline sets it equal to `uid`, resolving
  the proposal's "sequential 0-based" vs "matching uid" ambiguity).
- `Samples/Export/*.json` still carry the inert snake_case alias fields from
  the old template (their keys/UIDs are consistent, so they render fine in ST);
  left untouched, flagged for a separate migration pass.

---

## 2026-06-12 — LICENSE: CC0 text removed (#35)

### Removed
- **`LICENSE`** — the Creative Commons CC0 1.0 Universal license text was deleted
  from the file.

---

## 2026-06-11 — Escalation Ladders: NPC-driven subplots from wants, desires, and goals

The pipeline mechanized NPC *initiative* (§7.D Standing Goals + the activity-cadence
directive) but not *progression* — a Standing Goal is a flat drive with no stages,
complications, or resolution. Mid-tier runtime models (DeepSeek/GLM class) won't
invent coherent multi-session subplots, but they reliably *execute* authored plans.
The Escalation Ladder closes the gap on that division of labor: the author stages
the subplot; the model recognizes stated conditions and runs the next authored stage.

### Added
- **Escalation Ladder** — optional extension of the §7.D Standing Goal
  (`agent_roles/02_The_Architect.md`): 2–4 ordered stages (on-screen moves,
  off-screen moves with surfaceable evidence, an in-fiction observable advance
  condition each), a stated **endpoint** (ladders resolve; standing pressure stays
  TENSION/WORLD_PULSE's job), and a stated **collision** with `{{user}}` or the
  main spine (missing collision = Editor hard fail). Opt-in per NPC; >3 laddered
  NPCs per world is a soft flag. Seed field in `templates/World_Seed_Template.md`;
  elicitation in the Interviewer; recording + integrity pre-check in the Refiner.
- **Stage state, per mode.** Arc mode gets hard state: an optional
  `Active ladder stage this arc` delta line in NPC_SHIFT, named by the ARC_STATE
  cadence bullet, with stage transitions as optional keyed DRAMATIC_BEATs.
  Sandbox mode gets soft state: the stage is named in the SANDBOX_STATE aliveness
  bullet and anchored by WORLD_PULSE's depth-2–4 recency injection, with the
  revise pipeline's `sandbox_state_recalibration` as the manual ratchet when play
  moves past the named stage.
- **Progression discipline** in the cadence/aliveness directive: named current
  stage, advance only when the stated condition occurs in-fiction, never skip a
  stage, never resolve the endpoint without `{{user}}` having had the chance to
  interfere.
- **Audit teeth.** Editor Step 4a-3c (ladder format integrity, stage-named
  cadence, dangling-stage extension — hard fails; >3 ladders + unchoreographed
  collisions — soft flags). Voice Auditor Step 3J extensions (stage-trace: lull
  moves belong to the *active* stage; a "temptation" scenario probes that the
  model holds the stage instead of jumping to the endgame). Arc Transition
  Auditor Check 3b extension (stages monotonic across seams, advancement
  satisfies the authored condition via a beat or stated off-screen event, no
  off-page endpoint resolution).

### Changed
- `agent_roles/05a_Block_Library.md` — one clarifying sentence in the
  `npc_ensemble` enrichment guardrail: executing an authored ladder (including
  surfacing its stated off-screen evidence) is goal-following, not
  enrichment-invention; inventing stages/conditions/resolutions remains forbidden.
- `agent_roles/Converter/00_The_Converter.md` + `templates/Convert_Brief_Template.md`
  — the ladder rides the Standing Goal carry-across rule, with per-stage and
  collision audits (protagonist-coupled parts strip + mark); active stage never
  carries (it is Tier 3 state). Rebaseline carries the ladder verbatim with the
  rebuild starting at the post-revision high-water stage.
- `agent_roles/revise/00_The_Reviser.md` — no new scope types; stage bumps route
  through `tier3_arc_entry_modify` (arc) / `sandbox_state_recalibration`
  (sandbox); examples added.
- `agent_roles/05_The_Prompt_Engineer.md` — ladder-aware block hint in the
  Section 5.0b selection analysis: arc worlds with Escalation Ladders weight
  `npc_ensemble` for inclusion (laddered subplots render through NPC-to-NPC
  dialogue and off-screen evidence surfacing; predicted failure mode: "subplot
  starves because all dialogue routes through {{user}}"), with a matching
  self-validation checklist line. A hint feeding the analysis, not a mandate —
  omission stays legitimate with a Step 4 justification.

### Unchanged on purpose
- No new entry types, positions, flags, phases, or scope types; no Compiler or
  `tools/validate_export.py` changes; no preset content changes. Flat Standing
  Goals remain the default and fully valid — every new check is conditional on a
  ladder existing, so existing worlds are unaffected.

---

## 2026-06-11 — Convert Rebaseline mode: consolidate a revised world into a clean rebuild

A world that has been through several revisions (R1…R[N]) accumulates `<!-- REVISED
IN R[N] -->` markers across `Master_Design.md` and `Drafts/`, while its
`World_Seed.md` stays frozen at Phase 0 — revisions never back-propagate to the
seed. Until now there was no consolidation path: `skip phase0` rebuilds from the
stale seed (losing every revision), and regular Convert always regenerates the
protagonist and arc spine (losing them too). Rebaseline closes the gap.

### Added
- **Rebaseline mode** (`/worldforge convert <source> <target> --rebaseline`;
  combines with `--brief`) — the zero-axes-replaced conversion, formalized: same
  world, same protagonist, rebuilt clean from the *post-revision* Master Design,
  optionally folding in new mechanics at seed level. Spec lives in
  `agent_roles/Converter/00_The_Converter.md` **Section 9**; operation in the
  new **REBASELINE MODE** section of `workflows/world-forge-convert.md`.
  Load-bearing properties:
  - **The always-regenerate rules invert.** Foundational rule 8's premise ("the
    protagonist has changed by definition") is absent, so Sections 3 / 5 / 7b,
    per-arc/standing intimate functions, per-card style overrides,
    relationship-to-`{{user}}` content, and the four Section 4 strip rules
    (Standing Goal / drift / operative belief / trauma trajectory) all flip to
    keep/carry — distilled from the post-revision Master Design at **seed grade**
    (distill, never dump; no entry-level content in the seed).
  - **Zero-axes gate** replaces the overlap floor: any replaced axis reclassifies
    the run as a regular (reframe) conversion — announced, not refused. A
    rebaseline with no revisions and no new mechanics is flagged as a no-op copy.
  - **Revision reports become required reading** (`Drafts/Revision_R*.md` +
    `Export/REVISED_FILES.md`), with a source-integrity check: every reported
    change must be visible in the current Master Design, else halt — a drifted
    source would silently lose a revision. The revision high-water mark is
    recorded in the Conversion Manifest.
  - **Clean means marker-free.** Revision content carries; `REVISED IN R[N]`
    markers do not. Provenance moves to `<!-- REBASELINED FROM ... -->` comments
    + the manifest. The new project's revision counter restarts at R1.
  - **The honest cost is stated, not implied:** the rebuild compiles fresh UIDs,
    so running SillyTavern chats do not migrate (revise preserves UIDs precisely
    to avoid this; rebaseline trades it for cleanliness). The Converter prints
    this at hand-off and records the acknowledgment in the manifest.
- **`--then-interview` hand-off + the Interviewer's seed-revision posture.**
  `/worldforge convert <source> <target> --rebaseline --then-interview` chains
  the consolidation directly into **Phase 0** for when the rebaseline is a
  staging step for major changes: instead of `skip phase0`, the C0 hand-off
  dispatches the Interviewer in the new **seed-revision posture**
  (`agent_roles/00_The_Interviewer.md` Section 9) — read the complete
  consolidated seed + Conversion Manifest, play the world back, interview *only
  the user's changes* at full Phase 0 depth, re-elicit the cascade on coupled
  fields (changed arcs drag drift / trauma-trajectory / intimate-function lines;
  a changed protagonist drags relationship-to-`{{user}}` content, with an honest
  pointer that reframe conversion automates those strips), mark changed sections
  `<!-- CHANGED IN SEED-REVISION INTERVIEW -->`, append a dated note to the
  Conversion Manifest, sign off, and hand to Phase 1. The flag requires
  `--rebaseline`; in reframe mode the C0 interview already does this work. The
  posture is also dispatchable standalone against any complete pre-build seed.

### Changed
- **`agent_roles/Converter/00_The_Converter.md`** — header + rule 8 carve-out,
  `--rebaseline` / `--then-interview` invocations, Step 2 / Step 3 / matrix
  touch-points, manifest fields (`Operating mode`, revision high-water mark,
  rebaseline manifest variant), Section 9 Step H hand-off variant, sign-off
  gains a rebaseline checklist + Operating Mode block, context manifest notes
  the rebaseline-required reads.
- **`agent_roles/00_The_Interviewer.md`** — new Section 9 (seed-revision
  posture); context manifest now loads the existing `World_Seed.md` in that
  posture as well as on resume.
- **`templates/Convert_Brief_Template.md`** — Section 1 gains `Operating mode:
  reframe | rebaseline`; Section 2 gains the new-mechanics field; per-section
  *Rebaseline:* notes mirror the Section 9 inversions (Sections 5/6 become
  keep-from-source); sign-off updated. The Brief remains row-for-row consistent
  with the preservation matrix.
- **`workflows/world-forge-convert.md`** — operating-modes table, REBASELINE MODE
  section, three new pause gates (Reclassify / No-Op / Source Integrity), trigger
  commands, and the operations-comparison table.
- **`workflows/world-forge.md`** — CONVERT section and trigger commands document
  the mode; the "always-regenerated content" property is now reframe-scoped.
- **`CLAUDE.md`** — principle #10 retitled "Convert Pipeline (Reframe +
  Rebaseline)" with the mode's load-bearing properties; principle #6 points
  accumulated-revision consolidation at Rebaseline; cross-file consistency row
  updated. `tutorial.md` §8 gains a Rebaseline subsection + trigger-table row;
  the Converter's `kilo.jsonc` description mentions the mode.

No downstream agent changes: a rebaselined seed is a maximally-preserved
converted seed with Section 5 populated — the normal hand-written-seed path the
Refiner already handles.

---

## 2026-06-11 — Kilo config: DeepSeek 4 Pro on every seat; revise minis as subagents

Catch-up entry for two config changes shipped without changelog entries, plus
the documentation drift they left behind.

### Changed
- **`.kilo/kilo.jsonc` — all seats now run `deepseek/deepseek-v4-pro`** (via
  OpenRouter). The Editor and the three Auditors previously ran `deepseek-r1`
  with no temperature (reasoner endpoints ignore sampling parameters); as
  chat-tuned seats they now carry explicit temperatures — Editor 0.3, Auditors
  0.6 — alongside the existing per-phase values (creative seats 0.8, Refiner 0.4,
  Compiler 0.1, Prompt Engineer 0.3, Reviser 0.5, Converter 0.6). All 21 agents
  verified against the models wiki §3.5 ranges. The header comment documents the
  optional upgrade path back to a reasoning model for the strongest audits.
- **`.kilo/kilo.jsonc` — the nine revise minis (`agent_roles/revise/*`) are now
  defined as agents**, so the top-level Code agent can dispatch them as subagents
  per `AGENTS.md`'s delegation instructions. Temperatures mirror their parents.

### Fixed
- **Stale reasoner references in the wikis.** `Agentic-Tools-and-Models.md` §3.5
  claimed the shipped `kilo.jsonc` runs audit seats on a reasoner ("they need no
  temperature profile"), and `Kilo-Code-Setup.md` §5.4 still said "the Editor and
  the three Auditors run `deepseek-r1`" with no temperature set. Both rewritten
  to match the shipped config (chat-tuned DeepSeek 4 Pro with temperatures
  everywhere; drop the `temperature` field only if you upgrade a seat to a
  reasoner-class model).

---

## 2026-06-10 — Preconfigured Kilo Code project config

### Added
- **`.kilo/kilo.jsonc`** — project-scoped Kilo Code agent definitions, auto-loaded
  when the workspace opens (takes precedence over the global config). Twelve
  agents: the ten initial-build phases plus the Reviser and Converter entry
  points. Schema verified against the official Kilo docs
  (kilo.ai/docs/customize/custom-subagents): each agent uses `prompt:
  "{file:../agent_roles/...}"` to pin its phase spec as the system prompt
  (paths resolve relative to the config file), `mode: "all"` (user-selectable
  and Task-dispatchable), a provider-prefixed `model`, and a per-agent
  `temperature` from the models wiki §3.5 table. Models route through
  OpenRouter — DeepSeek 4 Pro on drafting/utility seats, `deepseek-reasoner`
  on the Editor + Auditor seats (no temperature set — reasoner endpoints
  ignore sampling parameters). API keys are never read from this file;
  non-OpenRouter users edit the `"model"` prefixes per the header comment.
  Wiki §5 rewritten against the verified schema (incl. the `.kilo/agents/`
  markdown-agent alternative and the per-agent `permission` field); the
  hand-written walkthrough remains as reference for alternative flavors.
- **Sampling-temperature guidance for the pipeline agents.** Models wiki gains
  §3.5 — a per-phase temperature table (creative seats 0.7–0.9, auditors mid,
  Editor low, Compiler ~0) with the two-temperatures scope note (agent sampling
  vs. the runtime preset's `temperature` field) and the reasoner caveat. The
  values are baked into the shipped `.kilo/kilo.jsonc` as per-agent
  `temperature` fields; Kilo setup §5.4 documents adjusting them. Tutorial §1
  points at both.

---

## 2026-06-10 — Agentic-friendliness: context discipline for small-context models

The pipeline was sized against 200K-context frontier models; this change makes it run
well on non-frontier models (DeepSeek 4, GLM 5) under Kilo Code / Roo Code by controlling
*what gets loaded per phase* rather than shrinking any spec content. The discipline is
framed as quality-and-cost engineering, not a hard window ceiling — nominal windows vary
(DeepSeek 4 Pro 1M, GLM 5 200K), but effective recall degrades well before nominal
limits on every model. No behavioral rule of any agent changed except where reading
mandates were scoped (see Changed).

### Added
- **`AGENTS.md`** — standing instructions for agentic tools (Kilo reads this, not
  `CLAUDE.md`). Routes sessions by type: pipeline *runs* go to `workflows/world-forge.md`
  with the runtime read-only rules; pipeline *maintenance* goes to `CLAUDE.md`. Carries
  the hard invariants compressed to one line each.
- **`.kilocodeignore`** — shipped denylist keeping `Samples/` (>1 MB), `wiki/`,
  `CLAUDE.md`, `CHANGELOG.md`, and `tutorial.md` out of auto-included runtime context.
- **`📂 CONTEXT MANIFEST` blocks** at the top of all eleven main agent specs — an
  explicit "load now / load on demand / do NOT load" read-set per phase, derived from
  each spec's INPUT section. Smaller models over-read or under-read without this; the
  manifests also document each spec's true dependencies. New editing-protocol rule:
  manifests must stay in sync with INPUT sections.
- **`Notes_Quick_Reference.md`** — a ~5 KB DERIVED distillation of
  `Notes_On_functionality.md` (position enum + routing, `{{original}}` override
  mechanics, prompt assembly order, behavior-bearing lorebook flags, strictness/provider
  gotchas). Agents consult it first; the full Notes file remains the sole authority and
  the quick reference must be regenerated when it changes (new cross-file consistency
  row).
- **`agent_roles/05a_Block_Library.md`** — the Prompt Engineer's Section 5a block
  library (~37 KB, half the spec) split into its own file. The audit workstream never
  needed it; now it loads only for preset authoring and Preset Resync. Section numbering
  (5a / 5a-detail) preserved so existing cross-references resolve. Parent spec drops
  from 114 KB to 78 KB.
- **`tools/validate_export.py`** — a stdlib-only, strictly **read-only** validator for
  `Export/` JSON: strict UTF-8 decode, mojibake markers (the PowerShell re-encode
  signature that passes `JSON.parse`), parse validity, `{{original}}` at the top of both
  card override fields, `depth_prompt` / `style_override` structure, position enum 0–7,
  UID uniqueness, and preset `prompts`/`prompt_order` resolution. An explicit, documented
  exception to the repo's no-code rule (approved 2026-06-10); it modifies nothing and
  exists as a deterministic backstop for the Compiler's pre-save guards.
- **Wiki: models page §3.4** — context discipline on DeepSeek/GLM: per-phase agents
  strongly recommended everywhere and effectively mandatory on 200K-and-below windows
  for large worlds, where to spend a frontier seat (Editor/Auditors — sycophancy under
  audit is these models' weak spot, not prose), DeepSeek automatic prefix caching,
  GLM 5 added to the recommended tiers. **Kilo setup page** — DeepSeek/GLM `kilo.jsonc`
  flavor, shipped `AGENTS.md`/`.kilocodeignore` documentation, validator allowlisting
  note, updated troubleshooting rows.

### Changed
- **Prompt Engineer reading mandate scoped.** "Read `Notes_On_functionality.md`
  completely before any audit" became: quick reference in full + Notes §5.2 / §5.10 / §8
  completely (the sections runtime judgments rest on), rest on demand. The Compiler's
  "read Notes first" similarly routes through the quick reference + targeted schema
  sections. No validation rule weakened — only the reading path to the same facts.
- **Phase 4 post-compile check** added to the orchestrator: run
  `python tools/validate_export.py Export/` (read-only) when a Python runtime is
  available; failures mean fix the source and re-compile, never hand-edit Export/ JSON.
- `CLAUDE.md` — repository tree, file authority levels, cross-file consistency table
  (four new/updated rows), editing protocol (manifest-sync rule), and the out-of-scope
  exceptions updated to match all of the above.

---

## 2026-06-09 — Convert pipeline (reframe a shipped world into a new build)

A fourth operating mode alongside initial-build / revise / preset-resync,
landing the "deferred arc→sandbox converter" called out in the Sandbox Mode
entries below — and broader in scope than just mode flips. The Convert pipeline
is the legitimate path for the change-categories the revise pipeline explicitly
bounces: a different protagonist, a `World Mode` flip (arc ↔ sandbox), a
different Style Contract at the world level, or a different Core Concept &
Tone (Master Design Section 1). It preserves the structural world-building
work (Tier 1 rules / factions / locations / cosmology, most of Tier 2
characters) that a from-scratch `/worldforge start` would discard (#24).

### Added
- **`/worldforge convert <source> <target>`** — a single-phase pipeline (C0)
  driven by the new **Converter** agent (`agent_roles/Converter/00_The_Converter.md`).
  Reads the source world's `Drafts/Master_Design.md` **read-only**, walks the
  user through a preservation matrix (keep / modify / drop / regenerate per
  source section), surfaces role reassignments explicitly (old protagonist
  becoming an NPC, source NPC becoming the new `{{user}}`, power-tier shifts),
  and writes a new `World_Seed.md` to the target project folder. The user then
  runs `/worldforge skip phase0` against the target and the standard pipeline
  (Phases 1–5.5) builds the new world end-to-end. Convert is **upstream** of
  the standard pipeline, not parallel to it — no downstream agent needs special
  handling for a converted world.
- **Overlap floor refusal (the reskin refusal).** The Converter classifies
  conversion intent against four axes — setting, protagonist, factions, tone —
  and refuses outright if three or four are replaced. At that scale the source
  is creative reference, not a structural source; the user is bounced to
  `/worldforge start` fresh. Borderline (two axes replaced) is surfaced for
  explicit user confirmation. Single source only — no mashups.
- **Convert Brief** (`templates/Convert_Brief_Template.md`) — an optional
  pre-authored brief mirroring the preservation matrix row-for-row. The
  brief-driven mode (`--brief <path>`) validates the brief against the source
  and interviews only on gaps / ambiguities, making non-trivial conversions
  version-controllable and reviewable.
- **Conversion Manifest** at the top of every converted seed — records source
  path, intent verbatim, overlap floor classification, per-section preservation
  decisions, role reassignments, and cross-references the user should be aware
  of. The Refiner reads it at Phase 1 to route accordingly. HTML-comment
  markers throughout the seed (`<!-- CONVERTED FROM ... -->`,
  `<!-- RELATIONSHIP TO {{user}} TO BE REAUTHORED FOR NEW PROTAGONIST -->`,
  `<!-- WAS SOURCE PROTAGONIST — TIER 2 BLOCK REAUTHORED ... -->`) make
  provenance traceable for both downstream agents and human readers.
- **Section 4 carry-across rules** for the four mechanics added in PR #23
  (NPC `Standing Goal`, relationship `How it drifts (arc worlds)`,
  `Operative belief`, intimacy `Trauma trajectory (arc worlds)`). Each field
  couples to the regenerated parts of a converted seed (Section 3 protagonist
  + Section 5 arcs), so carrying them naively produces a seed that mentions
  arcs that don't exist yet and a protagonist who doesn't exist yet. Rules:
  Standing Goal preserves if protagonist-agnostic else strips with a reauthor
  marker; drift always strips (arcs regenerate); Operative belief preserves
  only between two preserved characters AND not about `{{user}}`; Trauma
  trajectory always strips (arc-coupled). The base Trauma map (trigger +
  response, no trajectory) carries through normally.
- **CLAUDE.md principle #10 (Convert Pipeline)**, repo-structure tree updates,
  and three new cross-file consistency rows (Convert three-file contract;
  Interviewer Section 3 ↔ Converter Step 4 protagonist authoring; NPC agency
  / relationship-belief / trauma-trajectory machinery ↔ Converter Section 4
  carry-across).
- **`workflows/world-forge-convert.md`** — the convert orchestrator (phase
  outline, role reassignment surfacing for the five canonical cases, handoff
  semantics, pause gates, file structure, trigger commands, relationship to
  other pipeline operations).
- **Tutorial Section 8** — worked example (Lucifer → God): how the Converter
  walks the preservation matrix, what carries forward verbatim, what gets
  reauthored downstream, and how the four new Section 4 fields are handled
  automatically.

### Notes
- **Always-regenerated content** is not user-overridable: Section 3 (`{{user}}`),
  Section 5 (arcs / Sandbox Charter), Section 7b (test scenarios), per-arc /
  standing intimate functions, per-card style overrides, and every preserved
  Tier 2 character's relationship-to-`{{user}}`. These are protagonist-shaped
  or downstream-derived and cannot transfer mechanically; the downstream
  Refiner / Architect produces them in the new build.
- **Boundaries.** Convert does not touch SillyTavern, the override architecture
  (CLAUDE.md #2), audit/apply separation (#3), Position Rationale (#4), or any
  other architectural principle. It is purely an upstream seed-production
  operation. The Pipeline State Ledger (this same date, below) is unaffected —
  it lives at the top of `Master_Design.md`, written by the Refiner; the
  Converter writes only `World_Seed.md`.
- Older changelog entries that reference "an automated arc→sandbox converter
  remains deferred" (Sandbox Mode and Sandbox-aware revise pipeline entries
  below) describe the gap that this change closes. The remaining out-of-scope
  case is **pure reskin** (replacing setting + protagonist + factions + tone
  at once); that is intentionally bounced to `/worldforge start` fresh and
  will not be added as a Convert mode.

---

## 2026-06-08 — Compiler encoding guard (PowerShell mojibake)

### Fixed
- **Em-dash / non-ASCII corruption in Export JSON** (#23). Agents running on
  Windows (notably Kilo Code) tended to write JSON through PowerShell, whose
  `Out-File` / `Set-Content` / `>` redirection re-encodes to UTF-16 / Windows-1252
  and silently mangles em-dashes (—), curly quotes, and accented names into mojibake
  (`—` → `â€"`). Because the mangled file still parses as valid JSON, the Compiler's
  "JSON parses" guard never caught it. The **Compiler** and **mini-Compiler** now
  carry an explicit **FILE-WRITING & ENCODING guard**: write UTF-8 via the file tool
  or a Python / Node script (never PowerShell), and after each write verify non-ASCII
  survived (grep for `â€` / `Ã`, expect zero) — with matching sign-off checks and a
  `CLAUDE.md` common-failure-mode note. The mini-Compiler guard is doubly load-bearing
  since it reads existing non-ASCII content and rewrites it.

---

## 2026-06-08 — Character & world realism mechanics

Three mechanics that turn NPCs and characters from static descriptions into
persistent agents — the world acts on its own, remembers what `{{user}}` did, and
lets wounds heal visibly — authored as auditable state rather than prose the
runtime model is merely trusted to honor (#23).

### Added
- **NPC agency — standing goals + activity cadence** (both modes). Each principal
  NPC carries a **Standing Goal** (Architect §7.D — an active objective + the moves
  that advance it), and the `ARC_STATE` / `SANDBOX_STATE` Tonal Mandate gains an
  **activity-cadence** directive: when a scene lulls, a present or off-screen NPC
  advances its goal rather than the world freezing on `{{user}}`. The Editor adds a
  conditional hard-fail (Step 4a-3b — arcs with active NPCs need the directive, and
  it must not be dangling); the Voice Auditor adds **Step 3J** (initiative +
  goal-trace in a lull). The generic engine half already lived preset-side
  (`npc_ensemble`); only the world-specific goals live in Tier 3.
- **Relationship & belief state** (arc mode). `CHARACTER_STATE` gains item 6 and
  `NPC_SHIFT` its counterpart — a per-arc **relational-stance delta**: where a
  load-bearing bond now stands, the beat that moved it, and the operative belief
  driving behavior ("believes `{{user}}` spared her brother"). The Arc Transition
  Auditor's new **Check 3b** verifies the drift is earned — no teleporting bonds,
  un-caused belief flips, or silent memory resets. In sandbox mode the equivalent is
  the standing accumulation the aliveness contract already carries (the world
  remembers; attitudes never reset between scenes).
- **Trauma de-escalation tracking** (arc mode). `CHARACTER_STATE` gains item 7 — a
  per-arc **trauma-trajectory delta** (a trigger's current intensity + the beat that
  moved it). The Arc Transition Auditor's trauma-continuity check (Check 2) and the
  Voice Auditor's active-vs-dormant check (Step 3A) now verify against the *authored*
  fade rather than inferring it: fades are shown, never sudden vanishings.
  Intimate-context trauma continues to ride the per-arc Intimacy Register.

### Notes
- All three are authored as **per-arc delta only** — no new entry types, no
  per-dyad-per-arc explosion; only relationships/triggers that actually change get a
  line, and static Tier 2 baselines are never restated. Each is elicited by the
  Interviewer, recorded by the Refiner, and fielded in the World Seed template, with
  consistency-table rows in `CLAUDE.md`. Agency is genuinely cross-mode; memory and
  trauma de-escalation are arc-centric (sandbox has no seam to audit). The revise
  minis inherit the parent rules, and existing scope types cover their revision.

---

## 2026-06-08 — Pipeline reliability: durable loop state

Loop state (current phase, round count, sign-offs) lived only in the runtime
agent's memory, so a context summary or session restart could silently reset a
round counter or mis-route a mode-aware branch. Both pipelines now keep that state
on disk (#23).

### Added
- **Pipeline State Ledger** — a machine-managed block at the top of
  `Master_Design.md` (validated `world_mode`, `intimacy_in_scope`, `current_phase`,
  and a per-phase status + round table). It is the single on-disk source of truth for
  `/worldforge status` and for every `round > N` escalation. The Refiner initializes
  it and now **hard-validates `World Mode`** — an unrecognized value blocks instead of
  silently defaulting to `arc`. The Compiler verifies the ledger before compiling.
- **Bounded auditor loops** — the Voice / Arc Transition / Intimacy auditors
  (Phases 3.5 / 3.6 / 3.7) gain the `round > 3 → escalate` ceiling the Editor loop
  already had; they previously looped with no bound.

### Changed
- **Revise pipeline durable rounds** — the Revision Log entry gains a `Rounds:`
  counter line, and the mini-auditors (R3.5 / R3.6 / R3.7) gain the round-ceiling
  escalation (`R3.x_STALLED`) the mini-Editor already had. The revise pipeline keeps
  its existing Revision Log as its state record — no second ledger.

### Notes
- Additive and documentation-only; no behavior removed, and the tier model and
  override contract are untouched. The orchestrator is the single writer of ledger
  rows, so durability comes from file writes at phase boundaries rather than trusted
  memory.

---

## 2026-06-05 — Sandbox-aware revise pipeline

The post-launch revision pipeline (`/worldforge revise`) now handles sandbox
worlds, closing the gap flagged when Sandbox Mode shipped.

### Added
- Three sandbox revision **scope types** (taxonomy 11 → 14): `sandbox_state_recalibration`
  (the `SANDBOX_STATE` / aliveness-contract analog of `tier3_arc_tonal_recalibration`),
  `sandbox_entry_modify`, and `sandbox_entry_add`. The Reviser reads `World Mode` and
  uses these in place of the `tier3_arc_*` types on sandbox worlds.
- Mode-aware NPC and intimacy scopes: `tier2_new_character` / `tier2_character_voice_calibration`
  classify principal vs. roster NPCs (roster changes fire the Voice Auditor's
  Distinctiveness Matrix); `intimacy_*` scopes target the single standing
  `Sandbox_Intimacy_Register` and NPC intimacy (principal profile / roster §6.5 block).

### Changed
- The **Arc Transition Auditor (R3.6) never fires** on a sandbox revision — no arc seams.
- Thin sandbox deltas threaded through every revise mini (they inherit their now
  sandbox-aware parents); routing matrix, Reviser scope table, and the deferral notes
  in CLAUDE.md / the orchestrator / the tutorial updated accordingly.

### Notes
- *Flipping* a world between arc and sandbox stays out of revise scope — a Section 1
  `World Mode` change bounces to a full rebuild (`skip phase0`). An automated
  arc→sandbox converter remains the one deferred piece.

---

## 2026-06-05 — Sandbox Mode

A first-class alternative to arc-driven worlds, for open-ended experiences that
have no narrative arc — power-fantasy, world-director, and life-sim worlds
anchored by a standing world-state and a large NPC cast.

### Added
- **Sandbox World Mode** (#17). Declared in World Seed §1 (`World Mode: arc | sandbox`)
  or via `/worldforge start --sandbox`. A branch *through* the existing pipeline,
  not a parallel fork — the same agents run with the Tier 3 spine and large-cast
  NPC format repointed. `arc` remains the default; all existing worlds are unaffected.
- **Sandbox Lorebook** (Tier 3, always active) replacing per-arc lorebooks:
  `SANDBOX_STATE` (the `ARC_STATE` analog — standing situation + tonal mandate +
  an **aliveness contract**) and `WORLD_PULSE` (the `TENSION` analog — a sustained
  "the world is alive and reactive" directive). No `CHARACTER_STATE`/`NPC_SHIFT`/
  `DRAMATIC_BEAT`/arc-trigger entries.
- **Two-tier NPC model** for large casts: principal NPCs keep full profiles; the
  rest become compact roster stat blocks with a binding voice-fingerprint
  uniqueness rule. The Voice Auditor gains a sandbox-only **Distinctiveness Matrix**
  (Step 3I) — a blind-line test that flags interchangeable or voiceless NPCs.
- **NPC Ensemble & Enrichment** preset block (`npc_ensemble`, #17): NPC-to-NPC
  dialogue, ensemble prose scaling for multi-NPC scenes, and organic NPC enrichment
  within guardrails (the NPC-roster analogue of `enhanceDefinitions`). Plus a
  sandbox sensory-emphasis weighting on the Sensory Embodiment block.
- **Sandbox + NPC intimacy** (#17): the Tier 3 intimacy register folds into a single
  standing `Sandbox_Intimacy_Register`; NPC intimacy follows the principal/roster
  split (full profiles for principals, compact §6.5 intimate stat blocks for roster
  NPCs). The Intimacy Auditor adds an NPC intimate coverage + distinctiveness check
  (Step 3H).
- **Documentation & template catch-up** (#18): tutorial Section 7 (Sandbox worlds),
  new trigger commands, and sandbox guidance in the lorebook / card / group-lorebook
  authoring templates.

### Changed
- Phase 3.6 (Arc Transition Auditor) is **skipped** in sandbox mode — there are no
  arc seams to audit. The ≥8-entries-per-arc floor and cross-arc qualifiers do not apply.

### Notes
- Pipeline-only; no existing worlds were modified. *(The revise pipeline was made
  sandbox-aware in a follow-up — see the entry above; an automated arc→sandbox
  converter remains deferred future work.)*

---

## 2026-05-23 — Post-launch maintenance & runtime refinements

### Added
- **Revision pipeline** (#11) — `/worldforge revise`, a surgical post-launch fork that
  runs scope-locked mini-agents with read-mostly authority and UID-preserving
  compilation, keeping running SillyTavern chat states viable across edits. Includes a
  cumulative revision manifest in the mini-Compiler.
- **Preset Resync** (#13) — `/worldforge resync-preset`, a maintenance op that
  regenerates a shipped world's Chat Completion Preset against the current template +
  block library, re-deriving block content from the post-revision Master Design while
  preserving identifiers, order, and user customizations.
- **Scope-of-Turn** step in Deep Think (#14) — frames each reply as one move in an
  ongoing scene to curb beat-rushing and premature resolution.

### Changed
- **Deep Think** reframed as a checklist of considerations rather than a numbered
  procedure (#12), so it steers a reasoning model's attention without flattening its
  own process.
- **Jailbreak block** high-risk permission line gated on NSFW scope (#16); a dead group
  preset was removed.
- README documents the revise and resync commands; CLAUDE.md updated for the template
  inventory, the `wiki/` directory, and preset resync (#15).

---

## 2026-05-18 — Optional preset blocks

### Added
- **Opening Variation** and **Perception Boundary** optional Prompt Engineer blocks (#10):
  rotate response entry points to avoid the narration-first AI cadence, and keep
  in-scene characters from "reading" `{{user}}`'s narration and inner thoughts.

---

## 2026-05-15 — Jailbreak frame & setup docs

### Changed
- **Constitutive-fictional jailbreak frame** (#8) — replaced jailbreak boilerplate with a
  world-agnostic frame: a self-contained fictional metaverse, `{{user}}`-as-actor,
  authority deferred to in-context surfaces (lorebooks, chat log), and the four refusal
  axes named explicitly.

### Added
- Dedicated **Kilo Code setup** tutorial; MCP-servers guidance (none required); provider
  coverage for OpenRouter, Nano-GPT, and local models, surfaced across the docs.

---

## 2026-05-14 — Style Contract & architecture pass

### Added
- **Style Contract system** (#5) — per-world prose conventions (perspective, tense,
  narration / dialogue / emphasis markers, paragraph register) with per-card overrides,
  threaded through the World Seed, card template, Interviewer, Refiner, Architect, Editor,
  Voice Auditor, and the Prompt Engineer's preset. Per-card overrides are metadata-only
  (`extensions.world_forge.style_override`), consumed by a `world_forge`-aware extension at
  runtime and inert on stock SillyTavern.
- A phase-by-phase **tutorial** rewrite walking the Lucifer world, and an expanded README
  (architecture, Phase 5.5, Style Contract, Samples reference).
- README model-choice disclaimer and a note on the companion SillyTavern fork.

### Changed
- Agent specs refactored for attention coherence (foundational-rules headers + a shared
  Style Contract reference); Compiler guardrail against echoing the write-tool path into
  JSON content.

### Removed
- `Samples2/` demo-only output (#6), keeping `main` free of large generated artifacts.

---

## 2026-05-12 — Tooling guidance

### Added
- **Agentic Tools & Models** wiki page (#4): tool comparison (Roo / Kilo / Cline) and model
  recommendations, including a documented Gemini Flash failure mode.

---

## 2026-05-09 — `{{user}}` persona artifact

### Added
- **`User.md`** persona artifact (#3) — the paste-ready `{{user}}` Persona Description
  (≤150 words, reference-only) that closes SillyTavern's missing persona-import gap and
  pairs with the Tier 2 Protagonist Lorebook to give `{{user}}` parity with `{{char}}`.

---

## 2026-05-07 — Foundations

### Added
- **`CLAUDE.md`** (#2) — standing context and guardrails for AI coding agents working on the
  pipeline.
- **ARC_STATE two-subsection format** in the Architect and Editor — `Dramatic Situation`
  (descriptive) + `Tonal Mandate` (binding directive), so arc behavioral cues are read as
  commands rather than world-flavor.
