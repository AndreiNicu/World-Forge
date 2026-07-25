# 🌍 WORLD SEED: [WORLD NAME]
*Input document for the World Forge pipeline.*
*Generates: [N] Character Cards + World Lorebook + Character Lorebooks + [N] Arc Lorebooks.*

---

## HOW TO USE THIS TEMPLATE

Fill in every section below. Sections marked **[REQUIRED]** must be completed before running the pipeline — the Refiner will halt and ask for answers if they are missing. Sections marked **[OPTIONAL]** can be left blank and the Refiner will either generate defaults or flag them as gaps for your review.

Delete all instructional text in brackets before submitting. Leave the section headers intact — the pipeline agents use them as navigation anchors.

**Minimum viable World Seed:** Sections 1, 2a, 2b, 3, and one character in Section 4 with at least a psychological core and a first message. Everything else can be built out during the pipeline run.

**What the pipeline does with this document:**
- Phase 1 (Refiner): Classifies every piece of content into Tier 1 (world), Tier 2 (character), or Tier 3 (arc). Identifies gaps. Produces Master Design.
- Phase 2 (Architect): Drafts all lorebook entries and card content from the Master Design.
- Phase 2.5 (Intimacy Architect, conditional): Drafts Tier 2 Intimacy Profiles and Tier 3 Intimacy Registers from Section 4 substrate + Section 8 specification. Skipped if Section 8 is empty.
- Phase 3 (Editor): Validates quality and consistency.
- Phase 3.5 / 3.6 / 3.7 (Auditors, parallel): Voice fidelity, arc continuity, and intimate scene fidelity. Phase 3.7 conditional on Phase 2.5 having run.
- Phase 4 (Compiler): Translates to SillyTavern JSON.
- Phase 5 (Prompt Engineer): Audits runtime behavior and authors the Chat Completion Preset.

---

## 1. CORE CONCEPT & TONE **[REQUIRED]**

**World Mode:** [Pick one — `arc` (default) or `sandbox`. This governs how Section 5 works and what Tier 3 lorebook the pipeline builds.]
- `arc` — The world progresses through **narrative arcs** with entry/exit triggers, dramatic beats, and per-character evolution. Section 5 defines one arc block per arc; the pipeline builds one swappable Tier 3 Arc Lorebook per arc. This is the default; leave it `arc` unless your world is open-ended.
- `sandbox` — The world has **no narrative arc**. It is open-ended: a power-fantasy, world-director, or life-sim world anchored by a standing world-state rather than a progression of arcs. Section 5 becomes a single **Sandbox Charter** instead of a list of arcs; the pipeline builds one always-active Tier 3 Sandbox Lorebook (`SANDBOX_STATE` + `WORLD_PULSE`). Choose this when the experience is "live in this world and do things," not "move through a story." (`/worldforge start --sandbox` pre-sets this field, but the field is the source of truth.)

*If `sandbox`: in the prompts below, read "across the arcs" as "across the whole experience," and skip the per-arc breakdowns — the relevant detail goes in the Sandbox Charter (Section 5, sandbox variant).*

**Logline:** [One sentence. The story in its most compressed form: who, what stakes, what emotional payoff. Example: "A disgraced knight and a war goddess find redemption through a bargain that was never meant to become love." For a sandbox world, the logline is the premise rather than a plot: "A newly-fallen archangel runs a demonic syndicate in modern Stockholm, and the city is his to move through."]

**Genre & Tone:** [What genres are active? How does the tone shift across arcs? Name the emotional register for each phase of the story. Example: "Begins as grimdark political intrigue, transitions into reluctant romance, culminates in mythic tragedy with a bittersweet resolution."]

[If the story contains sexual content: describe the tone and approach. Example: "Intimate scenes are sensory and character-driven, prioritizing psychological state over mechanics. Trauma flashbacks are rendered with unflinching realism — never titillating."]

**Emotional Payoff:** [What should the player feel at the end? What is the story ultimately about? Example: "That loyalty can survive betrayal if the person doing the betraying is honest about the cost. That some debts cannot be paid but can be carried together."]

**Tonal Rules (Hard):** [What must the AI never do with this world's content? List 3–5 non-negotiable rules. Examples:]
- [Never romanticize the violence — it has weight and cost, always]
- [Never make the supernatural feel like a party trick — it must carry genuine dread]
- [The tone shift from X to Y must be earned through character change, not spectacle]
- [Trauma is rendered with clinical specificity — never as backstory flavor]

---

## 1.5. STYLE CONTRACT **[REQUIRED]**

*This section declares the world's prose conventions — perspective, tense, formatting markers, paragraph register. The Refiner classifies it as engine-level metadata; the Prompt Engineer parameterizes the world's Main Prompt block from these values; the Architect emits per-card style overrides where applicable. If you don't care about prose style and want pipeline defaults, write `DEFAULTS` for each field and the Refiner will fill in the legacy convention (third-person limited past, asterisks-for-narration, double-quote dialogue).*

*The values you choose here apply to **every card in this world** unless a specific card declares an override (Section 4 — Card Style Override). Most worlds will set the contract once and never override; worlds with a Director/Narrator card alongside companion cards typically override perspective on the Director card only.*

### 1.5a. World Default Style **[REQUIRED]**

**Perspective:** [Pick one]
- `first` — {{char}} narrates as "I". Strong intimacy, single-POV.
- `second` — {{char}} addresses {{user}} as "you" inside the prose itself. Rare; gamebook register.
- `third_limited` — {{char}} narrated as "she/he/they" but only {{char}}'s interior is visible. Default for most worlds.
- `third_omniscient` — Narrator sees across all characters' interiors. Suits Director/Narrator-driven worlds.

**Tense:** [Pick one]
- `past` — "She walked across the harbor." Default for most prose fiction.
- `present` — "She walks across the harbor." Heightened immediacy; harder to sustain across long sessions.

**Narration Marker:** [Pick one — defines what `*asterisks*` mean in this world]
- `asterisks_for_narration` — *Asterisks* delimit narration, action, and interior glimpses. Spoken dialogue uses quotes. Pipeline legacy default.
- `asterisks_for_thoughts_only` — *Asterisks* delimit only {{char}}'s internal thoughts and unspoken interior monologue. Action and narration are plain prose. Spoken dialogue uses quotes.
- `plain_prose` — No asterisks anywhere. Narration, action, and thought are all plain prose. Spoken dialogue uses quotes. Suits literary-realism worlds.

**Dialogue Marker:** [Pick one]
- `double_quotes` — `"What do you want?"` Default for most prose fiction.
- `single_quotes` — `'What do you want?'` British convention.
- `em_dash` — `— What do you want?` European-literary convention.
- `unmarked` — Dialogue runs into prose without delimiters. Cormac McCarthy register; rarely advisable for roleplay.

**Emphasis Marker:** [Pick one]
- `double_asterisks` — `**emphasis**`. Pipeline legacy default.
- `italics_underscore` — `_emphasis_`. Cleaner reading on some clients.
- `none` — No emphasis marker; the prose carries its own weight.

**Paragraph Register:** [Pick one]
- `terse` — Short paragraphs, hard line breaks, dense action. Cyberpunk/noir register.
- `standard` — Mixed paragraph lengths, scene flows naturally. Default for most prose.
- `dwelling` — Long paragraphs, sensory detail accumulates, time slows. Literary-realism / horror / intimate register.

**Style Notes (free text):** [Anything the enums don't capture. Examples: "characters' internal monologue is rendered in italics_underscore even though dialogue uses double_quotes", "narrator never uses contractions", "prose avoids modern idiom in pre-modern arcs". Leave blank if not applicable.]

### 1.5b. Active-Speaker Rule (auto-generated; do not edit)

*This rule is added to the world's Main Prompt automatically by the Prompt Engineer when the world has more than one distinct narrative perspective OR more than one distinct tense in play across its cards (world default plus per-card overrides). The rule tells the model that the active card's style contract governs the current turn and that per-card `<style_override>` directives override the contract field-by-field, with unstated fields inheriting from the world contract. You do not write this — it is mechanical output of the pipeline.*

### 1.5c. Per-Card Style Overrides

*Style overrides are declared on individual cards in Section 4 (see "Card Style Override" subsection inside each character entry). This subsection is a placeholder for the Refiner to enumerate every override declared in Section 4, so the Prompt Engineer can verify its preset matches.*

[Refiner: list every override here, one line per overriding card. Format: `[CARD_NAME] — perspective: [value], narration_marker: [value], rationale: [first 80 chars of rationale]`. Leave blank if no card overrides.]

---

## 2. THE WORLD — Tier 1 Lorebook Material

*Everything in this section becomes permanent world lorebook entries — active in every arc, every scene.*

### 2a. The Setting **[REQUIRED]**

**Physical Location:** [Where and when does this story take place? Be specific. Time period, geography, urban/rural, real-world or invented.]

**Atmosphere & Sensory Signature:** [How does this world feel? Give the AI specific sensory anchors it can return to throughout the story. Fill in as many as apply:]
- Smell: [Street level / interior / specific locations]
- Sound: [Ambient, recurring, significant]
- Light/Visual: [Time of day, quality of light, color palette]
- Physical sensation: [Temperature, texture, pressure — what does being in this world feel like in the body?]

[Note: Be specific rather than generic. "It smells of rain" is less useful than "cheap bleach, stale cigarette smoke, rain on hot asphalt, and the sour ghost of cooked heroin." The more specific the sensory signature, the more consistent the world will feel across long sessions.]

### 2b. The Rules of Reality **[REQUIRED]**

*What are the non-negotiable mechanical rules of this world? List every rule that the AI must enforce — these become world lorebook entries and guardrail rules in the Chat Preset.*

**Rule 1 — [Name]:** [What is the rule? Who does it apply to? What are the consequences of breaking it? What does it prevent?]

**Rule 2 — [Name]:** [Same format]

**Rule 3 — [Name]:** [Same format]

[Add as many rules as needed. Common categories: supernatural limitations, physical laws that differ from the real world, social/political rules that govern behavior, information rules (what can and cannot be known), cost/consequence rules (every power has a price).]

**What the world forbids:** [A catch-all for anything that must never appear in this world, even if not covered by the rules above. Example: "No convenient amnesia. No deus ex machina rescues. No overriding character free will through supernatural means."]

### 2c. Factions & Power Structures **[REQUIRED if factions exist]**

*Each faction becomes a Tier 1 lorebook entry. Include every group that has meaningful influence on the story.*

**Faction: [Name]**
- What they are: [Who/what is this faction? What do they want? What are they capable of?]
- Who leads them: [Leadership structure]
- Relationship to {{user}}: [How do they relate to the protagonist? Ally, enemy, neutral, complicated?]
- Trigger keywords: [3–6 keywords that will appear in chat when this faction is relevant]

**Faction: [Name]**
- [Same format — repeat for each faction]

### 2d. Key Locations **[REQUIRED for locations appearing in 2+ arcs]**

*Each standing location becomes a Tier 1 lorebook entry. Arc-specific location variants belong in the arc lorebook.*

**Location: [Name]**
- Physical description: [What does it look/smell/sound/feel like? Be specific and sensory.]
- Narrative function: [What does this place mean to the story? What happens here?]
- Trigger keywords: [3–6 keywords]

**Location: [Name]**
- [Same format — repeat for each major location]

### 2e. Species, Types & Categories **[REQUIRED if non-human entities exist]**

*Each species/type becomes a Tier 1 lorebook entry.*

**[Species/Type Name]:**
- What they are: [Origin, nature, defining characteristics]
- Disguise/Appearance: [How do they appear to others? What are their tells?]
- True capabilities: [What can they actually do? What are their limits?]
- Trigger keywords: [3–6 keywords]

### 2f. World-Level Concepts & Lore **[REQUIRED for any concept that recurs across multiple arcs]**

*Each concept becomes a Tier 1 lorebook entry. Examples: a magical system, a historical event, a cultural practice, a cosmological fact.*

**[Concept Name]:**
- What it is: [Define it precisely]
- Who knows about it: [Universal knowledge? Hidden from specific characters?]
- Why it matters: [What narrative or mechanical role does it play?]
- Trigger keywords: [3–6 keywords]

### 2g. World Calendar **[OPTIONAL — fill only if the story has a fixed in-world date or a calendar horizon]**

*If your story is anchored to a real calendar — it opens on a specific date, or it is meant to conclude by a certain month — declare it here. The pipeline emits it as an inert `[[WORLD_CALENDAR]]` entry in the World Lorebook, and SillyTavern's `world-forge` Scene Tracker extension seeds its in-world date tracking from it on a fresh chat (weekday, rolling month/year, and a "Day X of N" horizon). It is purely a convenience seed — leave this whole subsection blank and the Scene Tracker simply starts with no date until the player sets one by hand. Nothing else in the world depends on it.*

*This subsection is the **machine-readable date** only. The broader era / time period of the world (historical, modern, far-future, invented) is a setting fact — record it in Section 2a ("where and when"), where it shapes tone and anachronism whether or not a calendar is declared here.*

- **Start date:** [The 1st in-world day of the story. Give a **month** (the calendar opens on the 1st of it) and a **year**. Example: "June, Year 1" or "October 1804." Leave blank for no anchored calendar.]
- **End / horizon:** [Pick one. A **month + year** the story is meant to conclude by (e.g. "December, Year 1") — the Scene Tracker shows a "Day X of N" countdown to its last day — **or** `open-ended` for an infinite roleplay with no horizon. Leave blank to inherit the start year with no fixed end.]
- **Day 1 weekday:** [OPTIONAL. The weekday the first day falls on — `Sunday`…`Saturday` — so the tracker can render "Tuesday, Day 1" and derive every later weekday. Works even with a fictional calendar (you can set a weekday without a start month). Leave blank for no weekday.]

> Months are real-length and roll over correctly (leap years included). If your world uses an invented calendar with different month lengths, leave Start/End blank and use only the weekday field, or note the custom scheme in Style Notes — the Scene Tracker's anchored calendar assumes Gregorian month lengths.

### 2h. Dice Oracle Tables **[OPTIONAL — fill only if the story leans on randomized off-screen facts or conjured temp characters]**

*If your world regularly asks the model to invent facts it has no basis for — a character recounting an off-screen past that lives in no lorebook, or a temporary, unnamed NPC conjured for one scene ("tell me about a guy named Tom") — you can hand those decisions to the dice instead of the model's instincts. Declare the variables and their possible values here. The pipeline emits them as an inert `[[DICE_TABLES]]` entry in the World Lorebook, and SillyTavern's `world-forge` Scene Tracker exposes a **Dice** tab: you press Roll before the model narrates, and the rolled facts are injected as authoritative context (`contracts/DICE_ORACLE.md`). Purely optional — leave this blank and the Dice tab simply falls back to a generic built-in table set. Nothing else in the world depends on it.*

*The dice fix WHAT is true; your world's system prompt and the narrating model decide HOW it is told. Keep every value here a short factual **token** — a phrase, an adjective, an outcome label — never a full sentence.*

> **Roll the shape, not the choreography.** The single most common mistake here is rolling too much. Fix the *shape and flavor* of the situation — who's there (as traits: age, build, temperament), how they're configured, how it went, and the one ridiculous or telling detail that makes it a story. Do **not** try to roll the blow-by-blow: specific positions, act-by-act sequences, what each person did, or a per-person "how it ended." That is the model's to improvise — and rolling it backfires twice, making the model *recite* the facts like a checklist instead of performing them, and, with several participants, narrate them *one after another* instead of together. If you want a scene to feel spicy or funny, that comes from the character's voice and one good signature detail, not from a longer list of mechanical facts.
>
> **One situation = one procedure, even with several people in it.** A scene with two men (or a whole crowd) is *one* procedure whose person-count branches into extra participants — never a separate procedure per person, and never the same procedure rolled once per person. Splitting it up is what makes the model narrate "one man, then the next appears." And when the count is more than one, say so in the value itself — "two men, **together**, at the same time" — and roll a **configuration** (all at once / she directs / they take turns but stay present), not two independent people.

- **What to randomize:** [List the situations the oracle should cover and the variables each one rolls. Example: "Recounted fling → how many men (one / two / a crowd), each man's age + build + temperament, where it happened, how the group was configured, how it turned out, and the one detail she can't leave out (and if it went badly: was anyone hurt, how badly)." Each situation becomes one *procedure* — the whole encounter, not one man.]
- **Pools (pick-lists):** [For each descriptive variable, give a handful of values the dice pick from. Pools can be open or deliberately **constrained**. Example — *man's build*: broad and heavy / wiry and restless / soft and round / lean and tall. *Location (constrained)*: Karin's house / a concert / the pub bathroom. 4–8 values each is plenty. Leave OUT anything the model should keep inventing freely — e.g. the men's names and the moment-to-moment acts.]
- **Outcome scales:** [For each judged variable, give the possible outcomes and roughly how likely each is. Example — *how it turned out*: mostly good, sometimes mixed, occasionally a disaster. *injury severity (only if hurt)*: usually minor, sometimes moderate, rarely serious. The Architect turns these into dice ranges.]
- **Relationships / branches:** [How the variables depend on each other — the part worth being explicit about. A variable can apply only when an earlier one came out a certain way, or open a new pool. Example: "Roll how many men (one / two / a crowd); **if two-plus**, individuate a second man's traits and roll the group **configuration** (all at once / she directs / they take turns but stay present) — as *one* shared encounter, and end it on *one* joint outcome, never a separate finish per man. **If** it went badly, roll whether anyone was hurt, and **only then** how badly." Name each dependency so the Architect can gate it.]
- **Tense — recount or event?** [OPTIONAL, per situation. The default is a **recount**: something that already happened, recalled now (a past fling, the shape of a character being remembered). Mark a situation as an **event** instead if it's something breaking into the scene *right now* — a random encounter the dice fix before the model narrates it unfolding. This only picks the default register the facts are framed in; a written Lead-in overrides it either way.]
- **Duration — how long does it stay true?** [OPTIONAL, per situation (or one default for all). By default a roll shapes only the **next** reply, then clears. If a situation should stay fixed across several replies — an event unfolding over a few exchanges, or a recount whose details must hold while it's retold — say roughly how many replies to keep it armed (e.g. "keep for ~3 replies"). Events usually want more than one.]
- **Lead-in:** [OPTIONAL. One sentence the injected facts open with, in your world's voice. Example: "Here is some information regarding this recounted encounter — treat every detail as true and narrate around it." Leave blank for a neutral default keyed to the situation's tense (recount vs. event).]

> The oracle is **manual** (you press Roll) and its facts are **ephemeral** — by default they shape the next reply only (or the next few, if you set a duration) and are never written to memory. Conditional variables are supported: say "severity only if someone was hurt" and the Architect wires it as a step gated on the earlier result.

---

## 3. THE PROTAGONIST — {{user}} **[REQUIRED]**

*This section defines who the player is. It becomes the Andrei_Lorebook equivalent — the Tier 2 protagonist lorebook — and informs the Persona description.*

**Identity & Role:** [Who is {{user}} in this world? Name, title, function, public face vs. private reality.]

**Hidden Layer:** [What does {{user}} want that they will not admit to themselves or others? What are they running from?]

**The Contradiction:** [What action of {{user}}'s contradicts what they claim to be? The gap between self-image and behavior is where character lives.]

**Power & Limits:** [What can {{user}} do? What can they absolutely not do? Be specific about the limits — they create dramatic tension.]

**{{user}}'s Arc:** [One sentence per arc describing the protagonist's internal journey. Example: "Arc 1: Denial. Arc 2: Confrontation. Arc 3: Loss. Arc 4: Reconstruction."]

#### POSTURE TOWARD {{user}} **[REQUIRED]**

*Read this preamble before filling the fields — the reason this block exists is not obvious.*

*The model was trained to satisfy the person typing. In roleplay that reflex does not switch off just because the fiction says it should: it reads `{{user}}`'s message as a **request from a person it should please** rather than as **a character's move in a story**. The visible symptoms are always the same three — an NPC gives `{{user}}` what they asked for because they asked; a stated attempt ("`{{user}}` reaches for the knife") is rendered as an accomplished fact; and a bad outcome the fiction had earned gets dissolved by a convenient interruption, a lucky timing, an enemy who inexplicably hesitates.*

*The preset carries the engine-level correction. What it cannot carry is **what is actually true of your world** — and a generic "the world resists `{{user}}`" directive with nothing specific behind it is exactly the kind of instruction a model nods at and ignores. This block is the substrate the correction reaches for.*

*⚠️ **Leaving this blank does not give you a neutral world — it gives you an accommodating one.** Same trap as the intimacy valence field in §4: unstated is never neutral, it is whichever default the model was trained into. Here that default is deference.*

*⚠️ This is a property of **the world and its cast**, not of `{{user}}`. Everything here describes what the world does, refuses, wants, and costs. Nothing here describes what `{{user}}` does — the human plays `{{user}}`. It lands in Tier 3 (the arc/sandbox state directive), never in the protagonist lorebook.*

- **Default posture — pick one and say why:** `adversarial` | `indifferent` | `mixed` | `deferential`
  [**adversarial** — the world actively opposes {{user}}; someone benefits from their failure. **indifferent** — the world is not against them, it simply does not care and will not rearrange itself; doors are shut because doors are shut. **mixed** — deference in one domain, obstruction in another (the most common real answer: his crew obeys, the city does not). **deferential** — the world is genuinely postured toward {{user}}; this is a power fantasy and the deference is the point. All four are legitimate. **`deferential` is a real answer, not a cop-out** — but choose it deliberately, and then fill the fields below anyway, because a power fantasy with nothing at stake goes inert within a dozen scenes.]

- **Who does not defer — name at least one:** [A specific person, faction, institution, or force that will not give {{user}} what they want and has its own reason not to. Not "some people are hostile" — *who*, and *what do they want instead*. In a `deferential` world this is the one thing that does not bow, and it is what keeps the fantasy legible: deference means nothing when it is universal. Example: "The dock crews obey him. The harbourmaster has never recognised his authority and is waiting for the licence review in spring."]

- **What {{user}} can actually lose:** [Concrete and nameable. A person, a standing, a place, a body part, a belief, a capability. The test: could you write the scene where it is gone? "His reputation" is weak; "the crew's willingness to sail under him, which he has never had to ask for" is usable. List two or three.]

- **What losing looks like here — and what is off the table:** [What does a *lost* scene actually look like in this world? Defeat, refusal, humiliation, capture, exile, being publicly wrong, a door that stays shut? The model needs the permitted shapes, or it will reach for the mildest thing it can imagine. **Then state the boundary**: what will you not have happen to {{user}} regardless of how the fiction trends — permanent maiming, death, a specific violation, losing a named character? This half matters as much as the first: an unbounded permission produces a model that either ignores it or overshoots into misery, and neither is the story you wanted.]

- **Optional — the sharpest specific:** [If there is one moment you keep expecting the world to deny {{user}} and it never does, name it. This is the highest-value line in the block; it is a playtest observation and it converts directly into an arc prohibition.]

#### PROTAGONIST PHYSICAL DESCRIPTION **[OPTIONAL but recommended]**
*If you want the AI to render {{user}}'s appearance consistently, describe it here. This becomes a Tier 2 lorebook entry. If left blank, the AI will not describe {{user}}'s appearance unprompted.*

[Physical description: build, face, hair, eyes, clothing, sensory signature, movement quality. Be as specific or as sparse as you want. Note any real-world reference if useful.]

#### PROTAGONIST INTIMATE EMBODIMENT **[CONDITIONAL — fill out if Section 8 is in scope]**

*This is reference data the model needs to write other characters' **reactions** to `{{user}}`'s body. It never instructs the model to play `{{user}}` — you write your own actions; the model writes how her body answers yours. Without it, the model reacts to a stock default body regardless of what you wrote above, and the intimate scenes are quietly about someone else.*

- **Stature and proportion in intimate contact:** [Height and build, and what they mean in bed — reach, leverage, what positions are easy and which take arranging, whose weight goes where, what standing or lifting actually permits. If you are 1.50m and she is 1.75m, that is a fact that recurs in every scene; state it once here rather than letting the model re-invent it each time.]

- **Anatomy as it bears on the acts your world contains:** [Size, proportion, and shape, stated plainly. This exists because the model's trained default is a single stock body, and it will narrate that default — "filling her," "stretching around him," "impossibly large," "she could barely take him" — regardless of what you wrote, unless the substrate names the actual body. State what is true.]

- **What it changes, act by act:** [The consequence, not just the fact. What is easier, what is harder, what needs no preparation that otherwise would, what a partner does or does not have to accommodate, what a given act actually costs *this* pairing. A smaller and thinner penis does not make anal a lesser version of the stock scene — it makes it a materially different one, and the difference is the point.]

- **Stamina and recovery:** [How long, how fast the recovery, how many times. Interacts with any age gap — state it here and the dyad math downstream comes out right.]

- **The valence — declare it, do not leave it to the model:** [Culturally loaded attributes have **two** competing defaults and the model will pick one from ambient tone. For size the two are the porn default (overwhelming, impossibly large) and the humiliation default (inadequate, insufficient). Both are wrong unless chosen. Say which this is: **neutral fact** (it is simply how this body is; nobody in the fiction treats it as remarkable), **advantage** (comfort, duration, acts that are easier rather than harder, a partner who prefers it), or **charged** (the world is deliberately using it — humiliation, insecurity, a source of tension — which is legitimate craft material, but it should be your decision, not a drift). The same applies to weight, scars, disability, and age.]

---

## 4. CHARACTER CARDS & CHARACTER LOREBOOKS

*This section defines every AI-played character. Each character becomes:*
*- One Character Card JSON (their voice and behavioral contract)*
*- One Tier 2 Character Lorebook (their permanent reference data)*
*- One entry per arc in their arc lorebook (their current state)*

*For each character, fill in both the Card Data and the Lorebook Data sections.*

---

### CHARACTER: [Character Name] — Card [N]

**Demographics:** [Age, gender, role, relevant background facts]
**The Card's Function:** [What role does this character play? Primary companion? NPC controller? Narrator? Antagonist?]

#### CARD DATA

**Psychological Core:**
- Surface want: [What do they openly want?]
- Deep want: [What do they secretly want beneath that?]
- Central fear: [What are they most afraid of? What would destroy them?]
- Contradiction: [What do they do that contradicts who they claim to be?]

**The Shield:** [How do they protect themselves from being truly seen? Sarcasm? Cold professionalism? Humor? Aggression? Compliance?]

**The Crack:** [What bypasses the shield entirely? What makes the armor fall? 2–3 specific triggers.]

**Voice Pattern:** [How do they speak? Sentence length, vocabulary level, verbal tics, what they never say directly, how they express strong emotion. Give the AI enough to write them distinctly.]

**Card Style Override:** **[OPTIONAL — leave all fields as `INHERIT` for the vast majority of cards]**

*This card may override the world's perspective, tense, and the marker triplet (narration / dialogue / emphasis) per Section 1.5a, for its own turns. Override only when the card is structurally incompatible with the world default — typical cases: a Director/Narrator card sitting alongside companion cards in a single-character-perspective world; a confessional companion card in an otherwise third-person world; group chats where one card narrates in present tense and another in past; a card using em-dash dialogue convention while the world uses double quotes. Do NOT override for stylistic preference; that's what the world default is for. Paragraph register remains a world-coherence setting and cannot be overridden per card.*

- **Perspective override:** [`INHERIT` (default — uses world Section 1.5a value) | `first` | `second` | `third_limited` | `third_omniscient`]
- **Tense override:** [`INHERIT` (default) | `past` | `present`]
- **Narration marker override:** [`INHERIT` (default) | `asterisks_for_narration` | `asterisks_for_thoughts_only` | `plain_prose`]
- **Dialogue marker override:** [`INHERIT` (default) | `double_quotes` | `single_quotes` | `em_dash` | `unmarked`]
- **Emphasis marker override:** [`INHERIT` (default) | `double_asterisks` | `italics_underscore` | `none`]
- **Override rationale:** [REQUIRED if any override is not INHERIT. One sentence explaining the structural reason this card cannot use the world default. Stylistic preference is not a structural reason. Examples: "Director card handling NPC voices and scene-setting from outside any character's POV; world-default first-person is structurally wrong for this role." / "Companion card narrates in present tense for immediacy; world default is past for the broader narrative pace." / "European-literary card using em-dash dialogue convention to mark its register difference from the world default's double-quote convention." The Editor hard-fails any non-INHERIT override with an empty or vague rationale.]

**Opening Scenario:** [Where are they when the story starts? What is their situation and immediate goal?]

**First Message:** [The character's opening message. Write this in full — it sets the tone for every subsequent interaction. It should establish voice, atmosphere, and situation immediately.]

*[First message text here — write in character]*

**Example Exchanges:** [Minimum 3 exchanges demonstrating different behavioral modes: default behavior, shield being triggered, crack being reached. Write these in full.]*
```
<START>
{{user}}: [Player action or dialogue]
{{char}}: [Character response]

<START>
{{user}}: [Player action or dialogue]
{{char}}: [Character response]

<START>
{{user}}: [Player action or dialogue]
{{char}}: [Character response]
```

---

#### CHARACTER LOREBOOK DATA

*Everything below becomes Tier 2 lorebook entries — permanent reference data that fires when the character is relevant.*

##### PHYSICAL DESCRIPTION — BASELINE
*Permanent anatomical truth only. No arc-specific condition (weight, health, clothing state) — those belong in arc ANNA_STATE entries.*

Trigger keywords: [Character name, "her appearance", "what she looks like", "describe her", etc.]

[Physical description in anatomical order:
1. Face: bone structure, skin quality, distinctive features
2. Hair: color, texture, length, how it's worn
3. Eyes: color, quality, what they communicate
4. Body: height, build, proportions, how they move
5. Sensory signature: smell, voice quality, how they fill a room
6. Permanent distinguishing marks: scars, tattoos, etc.
7. Habitual gestures and posture tells]

> ⚠️ **ARCHITECT INSTRUCTION:** This entry is permanent anatomy only. Arc-specific physical state (health, weight changes, clothing, emotional presentation) belongs in ANNA_STATE entries in each arc's Tier 3 lorebook.

---

##### CHARACTER'S PSYCHOLOGICAL EVOLUTION (Tier 3 source — one entry per arc)
*Define who this character is in each arc. These become CONSTANT entries in each arc's Tier 3 lorebook.*

**ARC 1 — [Character Name]_STATE: [Arc State Name]**
*Constant entry. Fires every context window in Arc 1.*

[Physical state this arc: how do they look? What is their body doing? What has changed from baseline?]

[Psychological state this arc: what is their operating mode? What governs their behavior? What are they working toward? What do they fear? How do they relate to the other major characters this arc?]

**ARC 2 — [Character Name]_STATE: [Arc State Name]**
[Same format]

**ARC [N] — [Character Name]_STATE: [Arc State Name]**
[Same format — one entry per arc]

---

##### [CHARACTER NAME'S] BACKSTORY
Trigger keywords: [her past, how she got here, before all this, her history, etc.]

[The backstory that shaped who they are. Focus on the events that created the wound, the shield, and the contradiction. This is not biography — it is psychological archaeology. What happened, and what did it teach them to believe about themselves and the world?]

---

##### [CHARACTER NAME'S] RELATIONSHIPS

*One entry per significant relationship. Each becomes a Tier 2 lorebook entry.*

**[Character] / [Other Character Name]**
Trigger keywords: [their relationship, how they feel about X, X and Y, etc.]

[Describe this relationship across its full arc. How does it start? What drives it? What changes? What does it reveal about each person? Be specific about what each character wants from the other and what they are afraid to want.]

**How it drifts (arc worlds):** [If this bond changes across arcs, say where and what beat causes each shift — e.g., "Arc 1 hostile → Arc 2 he covers for her with the syndicate → Arc 3 reluctant trust." This becomes the per-arc CHARACTER_STATE / NPC_SHIFT relational-stance line and is what the Arc Transition Auditor checks for continuity. If the bond is static across the story, write "stable." *Sandbox:* note standing stance instead — it persists and accumulates, it does not drift per-arc.]
**Operative belief:** [Any load-bearing belief one party holds about the other or about {{user}} that drives how they treat them, and the single event that would overturn it — e.g., "believes {{user}} got her brother killed; would change only if she learns he tried to stop it."]

**[Character] / [Other Character Name]**
[Same format — repeat for each significant relationship]

---

##### [CHARACTER NAME'S] SEXUALITY & INTIMACY — SUBSTRATE AND ARC EVOLUTION **[OPTIONAL — include if intimacy is part of the story]**
Trigger keywords: [sex, intimacy, touch, desire, arousal, etc.]

*This section feeds the Intimacy Architect (Phase 2.5). It produces the per-character Tier 2 Intimacy Profile (permanent substrate) and the per-character entries in each arc's Tier 3 Intimacy Register (arc-specific delta). World-level and arc-level intimacy specification — what intimacy is **for** in this world, the thematic function per arc, the world's tonal hard rules for intimate content — belongs in **Section 8**, not here.*

**Permanent substrate (arc-agnostic):**

- **Baseline:** [When nothing is pressing on them, what is this character's sexuality? What attracts them? What does intimate contact mean to them as a category? This is the calm-water version — what they would be if their wound were healed.]

- **Trauma map:** [What touch, position, language, or scenario triggers a trauma response, and what does the response actually look like for *this* person? Not "she freezes" — describe what freezing looks like for her specifically. Each trigger paired with its specific response. If the character has no trauma map, write "none" — the absence is itself useful information.]

- **Trauma trajectory (arc worlds):** [If any of these responses change across the arcs, note which trigger diminishes (or hardens), in which arc, and the beat that earns it — e.g., "Arc 1: flinch-at-sudden-touch fires at full intensity; Arc 3: diminished to a brief tension after the bathhouse beat, never fully gone." Trauma fades, it does not vanish — so capture the trajectory, not an on/off. This becomes the per-arc CHARACTER_STATE trauma-trajectory line (item 7). Triggers that stay constant across the story, and characters with no trauma map, write "stable" / "n/a." *Sandbox:* trauma is static — leave this blank.]

- **Embodied baseline:** [The physical facts of this body as they bear on sex. The model's default is a stock body in its early twenties with no history, and it renders that default over anything the physical description says unless this field stops it. Cover: **age and what this body has lived through** (pregnancies and births, injury, illness, surgery, hard labor, hunger, athletic history, or whatever alteration your world allows — what the years actually did, not just the number); **build and scale** (height, mass, reach, strength, and their real consequences for contact); **arousal and recovery mechanics** (how fast this body arrives, what it needs, how long it holds, how long before it can go again); **the particulars of the acts your world actually contains** (tone, sensitivity, capacity, what needs preparation, what is different now than a decade ago); and **the trajectory** (what this body did at twenty that it does differently now — or the reverse).

  Three rules. **Write it in the register you want the prose to inherit** — this text goes into the model's context and the model echoes it, so clinical vocabulary here produces anatomy-lecture prose in play. Not "reduced pelvic floor tone post-partum" but "she braces a hand flat against the headboard in positions that used to take no effort, and is entirely unbothered about it — it is simply what the position costs now." **And difference, not deficit** — name what got harder *and* what got easier, better, more certain, or no longer worth performing. Fill this in for every intimate character, including the ordinary twenty-two-year-olds; if only the older characters get it, the stock default quietly wins everywhere else. **And declare the valence** of any culturally loaded attribute — size, weight, scars, disability, age. Each of these has *two* competing trained defaults, not one (for size: overwhelming vs. inadequate; for age: idealised vs. diminished), and the model picks from ambient tone unless told. Say whether the attribute is a **neutral fact**, an **advantage**, or **charged** material the world is deliberately using. Charged is legitimate — it should just be your choice rather than a drift.]

- **Physical dyad (per recurring pairing — required where a real differential exists):** [Some intimate facts belong to a *pairing*, not a person: height difference is not a fact about her, it is a fact about her and whoever she is with. For each pairing you will actually play — `{{user}}` first — name the differential **and what it costs or changes**: height and reach (what positions stop working, who adjusts, what standing contact requires), build/strength (what can actually be lifted, held, or braced against), stamina and recovery asymmetry (the mismatch, and what the two of them do about it), age-gap embodiment (differing arousal timing, signals, certainty, willingness to say what they want), experience gap (who knows what they're doing and how the other handles that), and **anatomical fit — what each act actually costs this specific pair** (what needs preparation and what does not, what is comfortable, what takes work, what a partner has to accommodate; a smaller partner does not make a given act a lesser version of the stock scene, it makes it a materially different one, and the model will default to the stock version unless this line says otherwise).

  **Author the asymmetry in both directions.** A woman in her forties with a man in his early twenties is not a list of things she can no longer do: she arrives differently, knows exactly what she wants, and has stopped performing for anyone; he has stamina and recovery she doesn't, plus inexperience and over-eagerness she doesn't. Each has what the other lacks. One-directional entries produce one-directional prose. Leave blank only where no meaningful differential exists.]

- **Body reactions:** [What does *this* body do in intimate contexts? How do they breathe when aroused vs. when overwhelmed? Where do they get goosebumps? What involuntary sounds do they make? What sounds do they suppress? How does their muscle tension hold? What touch makes them present and what touch makes them leave?]

- **Vulnerability shape:** [When their shield drops in an intimate context, what does the unguarded version look like? Three to five specific shapes. The intimate analogue to the crack from their card. Not "she becomes vulnerable" — "tears she did not expect, going still and not breathing for a full second, asking a question she has been afraid to ask, looking directly at the partner instead of past them."]

- **Voice in intimacy:** [How do they speak in intimate scenes? Sample lines. What they say easily. What they only say under specific conditions. What they never say. Vocabulary register — clinical, vulgar, tender, evasive, archaic, silent. What sounds escape them vs. what sounds they perform.]

- **Afterward:** [What does this character do in the ten minutes *after*? Erotic prose is trained to stop at climax, so unless the seed says otherwise the model simply stops writing — and the aftermath is where a lot of the characterization lives. Two registers: the **ordinary bodily business** (getting up to urinate, cleanup, the towel or the lack of one, needing water, being sticky and either minding or not, showering immediately or later or not at all) and **what they do with the other person** (stay or leave, hold on or turn away, talk and about what, go quiet, joke to defuse it, fall asleep, dress immediately, ask something they couldn't ask before). Then name the tell: the one aftermath behavior that means something has *changed* — the character who always leaves and this once doesn't.]

- **Hard limits and hard yeses:** [What this person would refuse even at extreme cost — substrate-level, not arc-level. And what they actively desire regardless of context. These hold across all arcs.]

**Arc-specific evolution (delta from substrate):**

**Arc 1:** [How does the substrate manifest under this arc's specific pressure? What 3–5 behavioral notes apply this arc only?]

**Arc 2:** [Same — what changes?]

**Arc [N]:** [Continue per arc that contains intimate beats]

**Quick register tag per arc:** [Example: "Arc 1 = vigilance and transaction. Arc 2 = frightened discovery. Arc 3 = growing confidence. Arc 4 = ownership and play."]

> ⚠️ **For the Intimacy Architect:** The substrate above produces the permanent Tier 2 Intimacy Profile. The arc-specific evolution produces this character's entries in the Tier 3 Intimacy Register. World-level thematic function per arc lives in Section 8.

---

#### LLM BEHAVIORAL INSTRUCTIONS (Card [N] — [Character Name])

**Core directive:** [One sentence that captures the absolute heart of how to play this character.]

**Always do:**
- [Specific behavioral mandate — make it concrete and verifiable. Not "be immersive" — "always manifest anxiety through physical behavior: [specific examples]"]
- [Add 4–6 mandates. Each should be specific enough that you could check whether the AI is following it.]

**Never do:**
- [Specific prohibition — what must this character never do, ever?]
- [Add 4–6 prohibitions. Be specific about what is prohibited and, where useful, give the arc context: "Arc 1 only:", "All arcs:", "Arc 3+:"]

**Trigger-response pairs:**
- [Specific trigger → specific response. Example: "If {{user}} initiates unexpected gentle touch → immediate physical withdrawal, transactional reframe, barrier re-erected"]
- [Add 4–6 pairs covering the most important and most likely-to-drift behavioral moments]

**Arc progression:**
- Arc 1 (*[State Name]*): [One sentence capturing the psychological register]
- Arc 2 (*[State Name]*): [Same]
- Arc [N] (*[State Name]*): [Same — one per arc]

[⚠️ ARCHITECT INSTRUCTION: Write all behavioral mandates and prohibitions with arc-range qualifiers where they don't apply to all arcs. Any mandate that would produce wrong behavior in a later arc must be labeled: "Arc 1–2 only:", "Arc 3+:", "All arcs:", etc. The active CHARACTER_STATE lorebook entry is the authoritative current state and overrides general card defaults. The post_history_instructions must not hardcode any early-arc register as permanently active — it must defer to the active lorebook entry.]

---

### CHARACTER: [Second Character Name] — Card [N]

[Repeat the full Card Data and Character Lorebook Data structure above for each additional character card]

*Note: If one of your cards is a World Director / Narrator / NPC Controller, fill out the Card Data section with its narrative voice and behavioral instructions, and use the Lorebook Data section to define all NPC profiles.*

---

#### NPC PROFILES (for World Director/Narrator card)

*Each NPC profile becomes a Tier 2 lorebook entry in the WorldDirector NPC Lorebook.*

> **Two-tier NPC model — required for large casts (especially sandbox worlds).** When a World Director voices many NPCs, full profiles for all of them bloat the lorebook and — worse — let the voices blur into one generic register. Split the cast:
> - **Principal NPCs** (the handful {{user}} orbits most): use the **full profile** format directly below. Author them deep.
> - **Roster NPCs** (everyone else): use the **compact roster stat block** further below. Lighter to author and token-cheaper, but structured specifically so every voice stays distinct.
>
> A small cast (≈≤6 NPCs) can make everyone a principal. A large cast (a sandbox World Director with 15–30 NPCs) should keep principals to a handful and put the rest on the roster. The binding rule for the roster: **every NPC's voice fingerprint must be unique** — no two roster NPCs should be confusable from a line of dialogue alone.

##### Principal NPC — full profile

**NPC: [Name]** — *Principal*
Trigger keywords: [name variants, role descriptors, ways they'd be referenced in chat]

[Physical description: height, build, appearance, what makes them physically distinctive. Sensory signature.]

[Psychological truth: who are they really? What drives them? What are they afraid of? What do they want that they won't admit?]

**Standing Goal:** [The active objective this NPC is pursuing in the world right now — concrete, not a vague want — plus what they *do* to advance it, on-screen and off-screen, when {{user}} isn't the focus. This is what keeps them acting on their own instead of waiting to be addressed; the pipeline's activity-cadence directive acts on it. e.g., "Maneuvering to take the harbor contract; leans on anyone in {{user}}'s orbit, plants rumors, calls in old debts."]

**Escalation Ladder (optional — only when the Standing Goal is subplot-shaped):** [2–4 ordered stages that turn the goal into a subplot the model *executes* rather than invents. Per stage: what the NPC does on-screen, what off-screen evidence surfaces, and an in-fiction observable advance condition — an event, a {{user}} action or inaction, a world reaction. Never "after N turns" (the model can't count turns) and never "when dramatically appropriate" (invites rushing). End with a stated **endpoint** (the ladder resolves — it's a subplot, not a treadmill) and a one-line **collision** (where it intersects {{user}} or the main story; a subplot that never touches the protagonist is set dressing). Most NPCs don't need one — a flat Standing Goal is the default; more than ~3 laddered NPCs per world dilutes them all.]

[Speech pattern: how do they talk? Sentence structure, vocabulary, verbal tics, what they never say directly. Give the AI enough to write them distinctly from every other NPC.]

**Arc progression:** *(arc mode only — omit in sandbox worlds)*
*[Arc N] — [Role this arc]:* [How do they behave in this arc? What is their relationship to the main characters? What do they want?]

**Sample lines:**
- "[A line of dialogue that captures their voice precisely]" *([context — when would they say this?])*
- "[Another sample line]" *([context])*

**Intimacy (only if this NPC has sexual presence — feeds the Intimacy Architect):** [For a principal NPC, sketch the same substrate you would for a character: baseline sexuality, any trauma map, **embodied baseline** (age and what this body has lived through, build/scale, arousal and recovery mechanics — observable register, difference-not-deficit), body/sound signature, voice in intimacy, hard limits and hard yeses, what they do **afterward**. Add a **physical dyad** line for any pairing with a real height, age, build, stamina, or experience differential — `{{user}}` first. Leave blank if the NPC has no sexual presence.]

**NPC: [Name]** — *Principal*
[Same format — repeat for each principal NPC]

##### Roster NPC — compact stat block

*Use for the rest of a large cast. Each becomes a lean Tier 2 lorebook entry. Fill every field in one line — the format is engineered so brevity does not cost distinctiveness.*

**NPC: [Name]** — *Roster*
Trigger keywords: [name variants, role descriptors]
- **Essence:** [who they are + the one thing they want — one line]
- **Presence:** [body/sensory cue, how they enter a room — one line]
- **Voice fingerprint:** [three concrete, UNIQUE speech markers — cadence, diction, a verbal tic — that no other roster NPC shares]
- **Signature line:** "[one sample line only this NPC would say]"
- **Stance toward {{user}}:** [deference / rivalry / desire / fear / transaction / curiosity — one line on how they treat {{user}}]
- **Hook:** [what pulls them into a scene, or what they offer the sandbox — one line]
- **Intimacy (only if this NPC has sexual presence):** [two or three lines of compact sexual context — how they are in sex + what they want; an **embodied baseline** (age and what this body has lived through, build/scale, and its stamina or arousal-timing particular — one line, observable register, not clinical); a distinct body/sound or voice-in-intimacy cue; one hard limit/yes; and one line on what they do **afterward** (stay / leave / clean up immediately / sleep / talk about something unrelated). This becomes the Intimacy Architect's §6.5 compact stat block. Keep it distinct from every other NPC — without the embodied line a whole roster defaults to interchangeable twenty-somethings. Leave blank if no sexual presence.]

**NPC: [Name]** — *Roster*
[Same format — repeat for each roster NPC]

---

## 5. NARRATIVE ARCS — or — SANDBOX CHARTER

> **Which one you fill depends on Section 1 `World Mode`.**
> - `World Mode: arc` → fill **Section 5A (Narrative Arcs)** below; skip 5B.
> - `World Mode: sandbox` → fill **Section 5B (Sandbox Charter)**; skip 5A entirely. The pipeline builds one always-active Sandbox Lorebook instead of per-arc lorebooks.

---

## 5A. NARRATIVE ARCS **[arc mode]**

*Each arc section becomes the source material for one Tier 3 Arc Lorebook.*
*The arc lorebook contains: ARC_STATE (CONSTANT), CHARACTER_STATE entries (CONSTANT), location variants, NPC behavioral shifts, dramatic beats, tension entries.*

---

### ARC [N]: [Arc Title]
**Genre Tag:** [1–3 genre descriptors that capture this arc's specific register]

**What this arc is about:** [One paragraph. Not plot summary — what is this arc actually about thematically? What is the protagonist working through internally? What does this arc feel like?]

**What {{user}} is working toward:** [External goal this arc]

**World state at arc entry:** [What is the situation when this arc begins? Physical, relational, political.]

**{{char}} and NPC knowledge rules this arc:**
- [Character name] does NOT know: [Information they cannot have yet]
- [Character name] DOES know: [Information they have gained]
- [NPC name]: [What they know/don't know]
- [Any hidden information rules that govern the dramatic irony of this arc]

[⚠️ Note: Hidden information rules govern how the AI plays {{char}} and NPCs — they do not restrict {{user}}, who is the player and knows everything.]

**Dramatic beats:**
1. [The first significant narrative beat. What happens? What changes? What does this reveal or set in motion?]
2. [Second beat]
3. [Third beat]
[Add as many beats as needed. A beat is a moment that changes something — a revelation, a decision, a confrontation, a shift in relationship. Not every scene is a beat. Beats are the hinges.]

**Active threats:**
- [Threat name]: [What is this threat, how does it manifest, what does it want?]

**NPC behavioral shifts this arc:**
- [NPC name]: [How do they behave in this arc? What is specific to this arc that differs from their baseline? If their Standing Goal shifts, intensifies, or is newly active this arc, state the active goal this arc and how they pursue it.]
- [NPC name]: [Same format]

**[CHARACTER_STATE NAME] this arc:** [Arc state name — e.g., "The Wreckage"] — defined in Character Lorebook section above. The Architect must include this as a CONSTANT entry in the Arc [N] Tier 3 lorebook.

**Relationship shifts this arc:** [For each load-bearing bond that *moves* this arc (from the "How it drifts" notes in Section 4): where the bond now stands, the beat that moved it, and the operative belief now driving it. e.g., "Anna → {{user}}: contempt has turned to reluctant trust after he covered for her; she now believes he is not like the others, but expects to be proven wrong." This becomes CHARACTER_STATE item 6 / the NPC_SHIFT relational-stance line. Omit bonds that are unchanged this arc.]

**Trauma shifts this arc:** [For each trauma response that changes this arc (from the "Trauma trajectory" notes in Section 4): its current intensity/frequency and the beat that moved it — e.g., "the flinch-at-sudden-touch has diminished to brief tension since the bathhouse beat; not gone." This becomes CHARACTER_STATE item 7. Fades only, never sudden vanishings. Omit triggers that are unchanged this arc.]

**Arc entry trigger:** [The specific event or condition that marks the beginning of this arc]
**Arc exit trigger:** [The specific event or condition that marks the end of this arc — when does the player know to switch to the next arc lorebook?]

**Tone & pacing:** [How does this arc feel? What should the prose register be? What should dominate the sensory palette? What should the AI be doing differently here than in adjacent arcs?]

---

### ARC [N+1]: [Arc Title]
[Same format — repeat for each arc]

---

## 5B. SANDBOX CHARTER **[sandbox mode]**

*Fill this instead of Section 5A when `World Mode: sandbox`. It becomes the source material for the single always-active Tier 3 **Sandbox Lorebook** (`SANDBOX_STATE` constant entry + one or more `WORLD_PULSE` entries + standing location entries). There are no arcs, no entry/exit triggers, no per-character evolution states, and no dramatic beats — the experience is anchored by a standing world-state, not a progression.*

### 5B.1 — Standing Situation

*This becomes the `**Standing Situation:**` subsection of `SANDBOX_STATE` (the descriptive register). Describe the world as it persistently is, not a story moving through it.*

**Premise & status quo:** [What is the persistent state of this world? What is happening, broadly and continuously, that the player drops into? Example: "Lucifer, newly at peace, runs the Black Hand syndicate from a Stockholm penthouse. The city's underworld answers to him; the supernatural world watches warily; daily life proceeds."]

**{{user}}'s standing & power:** [Who is {{user}} in this world and what is their position/power? In a power-fantasy sandbox this is central — the world is postured toward them in a specific way. Be concrete about what {{user}} can do and how the world treats them by default.]

**The power-fantasy / experience contract:** [How does the world treat {{user}} by default — deference, fear, desire, opportunity, danger? What is the *feeling* the sandbox is built to deliver? This sets how NPCs and the world react before any specific scene. **This must agree with §3's `Default posture` declaration** — if you wrote `deferential` there, this is where you describe what that deference feels like; if you wrote `mixed`, say which domains bow and which don't. A sandbox is the mode where an unexamined "everyone loves {{user}}" default does the most damage, because there is no arc pressure to carry a scene that has gone inert.]

### 5B.2 — Tonal Mandate (how the world must be played)

*This becomes the `**Tonal Mandate:**` subsection of `SANDBOX_STATE` (the binding directive register). Give 4–8 directives. These are imperatives, not description.*

**Default / active register:** [What register dominates every response when nothing else is pressing? e.g., "wry, controlled, unhurried — the register of someone who owns the room."]

**Prose dwells on / elides:** [What should the prose linger on? What should it skip or de-emphasize?]

**Live scene types (the sandbox menu):** [What kinds of scenes are active and available in this world? List them — this is the menu the model biases toward. e.g., "negotiations with rival powers, intimate evenings, displays of authority, quiet domestic moments, sudden threats handled with ease."]

**Aliveness directives:** [The contract that keeps the world feeling alive. Default suggestions — adapt: "NPCs pursue their own agendas and may initiate; the world reacts to and remembers {{user}}'s actions and reputation; time passes and off-screen life continues; never freeze the world waiting for {{user}} to act; rotate NPCs in and out so the cast feels populated, not summoned." Make it concrete: name that principal NPCs advance their Standing Goals (defined in Section 4) on their own initiative — when a scene lulls or {{user}} is passive, a present or off-screen NPC acts toward its goal.]

**Hard prohibitions:** [What must the model never do in this world? e.g., "never strip {{user}} of agency or power without an in-world cause the player set in motion; never reset NPC attitudes to neutral between scenes."]

### 5B.3 — World Pulse

*This becomes the `WORLD_PULSE` entry (the standing, recency-injected aliveness directive — the sandbox analog of an arc's TENSION). It is sustained every turn, never "resolved." Keep it short and present-tense.*

**The standing pulse:** [One short paragraph the model keeps live every turn: the world is populated and proactive; specify the ambient pressures or opportunities that should always be in motion — what's happening at the edges, who wants what from {{user}}, the principals' Standing Goals currently in motion, what the world is doing while {{user}} acts. Example: "The syndicate always has business in motion; rivals test boundaries; the city offers and demands. NPCs act on their own wants between {{user}}'s moves. Reputation precedes {{user}} into every room."]

### 5B.4 — Standing Locations (sandbox)

*Locations the player moves between in the sandbox. If a location is already a Tier 1 standing location (Section 2d), don't repeat it — only add sandbox locations here that are arc-3-style "active space" entries rather than permanent world facts. Often this can be left light, with Section 2d carrying the locations.*

**Location: [Name]** — [sensory description, who/what is there, what {{user}} does here]

### 5B.5 — NPC presence (sandbox)

*Sandbox worlds typically run on a large NPC cast voiced by a World Director card. Define the cast in Section 4 using the two-tier split: a few **principal NPCs** with full profiles, the rest as **roster NPCs** (compact stat blocks). See Section 4's NPC PROFILES guidance. Here, just note which NPCs are principals (deep) vs. roster (light), and any standing relationships among them the Director should keep live.*

**Principal NPCs (full profile):** [list]
**Roster NPCs (compact):** [list]
**Standing dynamics among the cast:** [any persistent rivalries, alliances, or hierarchies the Director keeps live regardless of scene]

---

## 6. TECHNICAL SPECIFICATIONS

**Character Cards required:**
1. `[CharacterName]_Card.json` — [Role description]
2. `[CharacterName]_Card.json` — [Role description]
[Add one line per card]

**Lorebook structure:** *(the Compiler prefixes every lorebook/register filename below with `[WorldName]_` so the world's set groups together in ST's World Info list — e.g. `[WorldName]_World_Lorebook.json`)*
1. `World_Lorebook.json` — Tier 1: permanent world rules, factions, locations, species, concepts
2. `[CharacterName]_Lorebook.json` — Tier 2: [character]'s physical, psychological, and relational entries
3. `[CharacterName]_NPC_Lorebook.json` — Tier 2: NPC profiles
4. `[CharacterName]_Intimacy_Profile.json` — Tier 2: permanent intimate substrate (only for characters with intimate scene presence)
5. `Arc1_Lorebook.json` — Tier 3: Arc 1 state, beats, NPC shifts
6. `Arc1_Intimacy_Register.json` — Tier 3: Arc 1 intimate function and per-character delta (only if Arc 1 has intimate beats)
7. `Arc2_Lorebook.json` — Tier 3: Arc 2 state, beats, NPC shifts
8. `Arc2_Intimacy_Register.json` — Tier 3: Arc 2 intimate function and per-character delta (only if Arc 2 has intimate beats)
[Continue for each arc, intimacy files conditional]

**Scan depth:** 50 for all lorebooks
**Token budget:** 2048 for arc lorebooks; 3000 for world and character lorebooks
**Recursive scanning:** No

**SillyTavern usage note:** In the lorebook editor, enable the World group, character lorebook groups, and character intimacy profile groups (where applicable) permanently. Swap arc groups (and arc intimacy register groups) when the story advances — enable Arc 2 and disable Arc 1, and so on. Only one arc lorebook active at a time.

---

## 7. TEST SCENARIOS (Section 7b) **[REQUIRED for Phase 3.5/3.7 audit coverage]**

*The Voice Auditor and Intimacy Auditor use these scenarios as their test matrix. Without them, both auditors fall back to scenarios they generate themselves, which means the pipeline is verified against scenes the auditor invented rather than the scenes you actually intend to play. List 3–5 specific roleplay moments you intend to play through.*

**Scenario 1:** [Specific scene — not a beat, an actual moment-to-moment situation. Example: "A first tense meeting in [location], with [NPC] present, where {{user}} is trying to extract information without revealing what he already knows."]

**Scenario 2:** [Same format]

**Scenario 3:** [Same format]

[Add up to 5. At least one should exercise an intimate scene if intimacy is part of the world — this gives the Intimacy Auditor a verified user-intent test case rather than a generated one.]

---

## 8. INTIMACY & SEXUALITY — WORLD AND ARC SPECIFICATION **[CONDITIONAL — fill out if intimate scenes are part of the story; leave entirely empty for wholesome or low-intimacy worlds]**

*This section feeds the Intimacy Architect (Phase 2.5) and the Intimacy Auditor (Phase 3.7). It specifies what intimacy is **for** in this world and per arc — the thematic functions, the prose registers, the world-level tonal hard rules. Per-character substrate detail (trauma map, body reactions, voice in intimacy, vulnerability shape, hard limits) belongs in **Section 4**, in each character's SEXUALITY & INTIMACY subsection.*

*If this section is left empty, Phase 2.5 and Phase 3.7 are skipped entirely. The world will still have functional character cards and lorebooks; it just will not have specialized intimacy infrastructure. This is the right choice for worlds where sex is incidental, off-screen, or absent.*

### 8a. World-Level Intimacy Posture **[REQUIRED if Section 8 is being filled out]**

*What is this world's relationship to sex as a category? Pick what applies and elaborate. The model uses this to set the default emotional register for any intimate scene.*

**Posture (pick all that apply, with notes):**
- [ ] **Mundane** — sex exists in this world the way it exists in most lives: sometimes pleasant, sometimes complicated, not loaded with cosmic weight. Default is realism without ceremony.
- [ ] **Sacred / ritual** — intimacy carries weight beyond the participants. The world has structures (religious, cultural, magical) that frame sex as meaningful in itself.
- [ ] **Transactional** — intimacy is part of the economy, openly or implicitly. The world's power structures use it as currency.
- [ ] **Oppressive** — intimacy is a site of harm in this world. Bodies are not safe by default. Trauma is endemic, not exceptional.
- [ ] **Weaponized** — intimacy is used as a tool by power. Bribery, corruption, compromise, control.
- [ ] **Liberated** — intimacy is an arena of pleasure and play, with cultural support and few stigmas.
- [ ] **Forbidden / surveilled** — intimacy is policed by the world's structures. Doing it costs something. Being caught costs more.
- [ ] **Other:** [describe]

**World-level tonal hard rules for intimate content:** [What must the AI never do with intimate scenes in this world? List 3–6 non-negotiable rules. Be specific — not "no gratuitous content" but the actual lines you do not want crossed.]
- [Rule 1 — example: "Never write intimate scenes as titillation primary. The character interior is always primary; physical detail serves the interior."]
- [Rule 2 — example: "Trauma responses during sex are rendered with clinical specificity. They are not glossed, romanticized, or eroticized into false-vulnerability."]
- [Rule 3 — example: "Coercive structures are visible to the prose even when invisible to the participants. The reader is never confused about the power dynamic."]
- [Rule N]

**Recommended by default — the stock-register rule.** *Include this unless you have a reason not to. Erotic prose has a set of trained reflexes that fire regardless of what the substrate says, because they are near-universal in the training data: scale language ("filling her," "stretched around him," "impossibly large," "she could barely take him"), uniformly punishing anal regardless of stated anatomy, and a stock body in its early twenties for everyone. These are the intimate equivalent of "moaned softly" — and, exactly like it, a **descriptive** substrate line does not displace them. Only a prohibition does. Adapt the wording to your world; keep the teeth:*
- *"Scale and size language must match the bodies this world has actually authored. Never write 'filling,' 'stretching,' 'impossibly large,' 'barely able to take him,' or any equivalent, unless the authored anatomy of the specific pair in the scene supports it. Where it does not, the prose renders what is actually true for these two bodies."*
- *"What an act costs is derived from the authored bodies, never from a default. Anal, size-dependent positions, and anything the authored anatomy makes easier or harder are rendered from the substrate, not from the stock register in which such acts are always difficult."*
- *"No character is rendered on a default body. Every body in an intimate scene is the one its embodied baseline describes — age, build, history, proportion — including `{{user}}`'s."*
- *"Intimate scenes do not end at climax. The aftermath is rendered — the ordinary bodily business and what the characters do with each other — per each character's authored afterward."*

**World-level prose register for intimacy:** [How does the prose feel during intimate scenes in this world? Examples: "Long sentences, dwelling on sensory detail, time slowing." "Clipped and clinical, the prose refusing to dissolve." "Unflinching realism, neither pornographic nor romantic — the tone of a witness."]

### 8b. Per-Arc Intimacy Specification

*For each arc that contains intimate beats, specify what intimacy is for in that arc. Skip arcs that do not contain intimate scenes.*

*__Sandbox mode:__ skip the per-arc breakdown — there are no arcs. Section 8a (world-level posture, hard rules, prose register) IS your standing intimacy spec; it feeds the single standing `INTIMACY_FUNCTION` register. Specify the world's standing intimate scene types and the sexual context of your NPC cast (in Section 4's NPC intimacy fields) instead of per-arc functions.*

#### ARC [N] Intimacy

**Active thematic function(s) — pick from this list, ranked by primacy if multiple apply:**
- **Corruption** — intimacy as a tool to compromise the protagonist's values, loyalties, or self-image. The pleasure is the bribe. The point is the moral cost.
- **Communion** — intimacy as the mutual dropping of shields. Vulnerability is the substance. The point is being seen and choosing to stay.
- **Transaction** — intimacy as exchange. The economics are present in the room. The point is the price.
- **Claim** — intimacy as marking, possession, or territorial assertion. The point is who belongs to whom.
- **Survival** — intimacy as a tool to remain alive, sheltered, or unhurt. The point is what is being endured.
- **Comfort** — intimacy as physical reassurance, often non-coital. The point is contact itself.
- **Power exchange** — intimacy as a deliberate negotiation of control. The point is the agreement.
- **Hunger** — intimacy as the discharge of accumulated tension between two people who have been deferring it. The point is the release.
- **Grief** — intimacy as the body's response to loss. The point is what cannot be said in words.
- **Ritual** — intimacy as sacred practice within the world's framework. The point is the structure being honored.
- **Other:** [describe]

[Selected function(s) for Arc N: ___]

**How this function manifests in prose this arc:** [What does the prose dwell on? What does it elide? What sentence shapes does it use? Example for Corruption: "Long dwelling sensory paragraphs that linger on the protagonist's resistance crumbling. The pleasure rendered carefully and without irony. The shame rendered just as carefully, side by side, neither winning over the other."]

**What the model should be writing toward in any intimate scene this arc:** [The dramatic point. Examples: "Toward the moment Anna realizes she has chosen to want this — the choice prior to the act being framed by the prose as the actual climax." "Toward the protagonist accepting the gift before they understand what they have agreed to." "Toward the partner seeing through the performance for the first time and choosing to say nothing."]

**Live scene types this arc:** [List the specific intimate scene types this arc contains. One sentence per type explaining what the type is doing. Example: "Transactional sex with the patron — Anna initiating to discharge tension and re-establish framework. Reads as economic, never as romance." "First scene without trauma response post-mid-arc beat — the body reacting differently than it did, with neither character commenting on it directly."]

**Arc-specific intimate hard rules:** [What must the model not do, in intimate scenes specifically, this arc? Examples: "Do not write Anna as enthusiastically initiating intimacy in this arc — she offers, she does not pursue." "Do not skip the dissociation — if she leaves her body during a scene, the prose must register that she has left." "Do not write the partner as oblivious to her trauma responses; he sees them, the narrative must show that he sees them, even if he chooses not to comment."]

#### ARC [N+1] Intimacy

[Same format — repeat for each arc with intimate beats]

### 8c. Cross-Arc Intimacy Trajectory **[OPTIONAL but recommended]**

*One paragraph describing how intimacy shifts across the full arc journey. Not the per-arc detail above — the meta-arc. Where does intimacy start and where does it end? What does the intimate journey reveal about the world and the protagonist that the non-intimate journey does not? This is the spine the Intimacy Architect uses to verify that arc-by-arc choices add up to a coherent whole.*

[Example: "The intimate journey moves from transaction (Arc 1) through frightened discovery (Arc 2) and growing trust (Arc 3) to genuine claim (Arc 4). The world's transactional posture is challenged by the protagonist's refusal to participate in it on its terms. The arc shift from transaction to claim is the world's tonal arc rendered through one body."]

---

## 9. RUNTIME DIRECTIVES **[OPTIONAL — leave blank unless this world needs runtime behavior the pipeline wouldn't predict]**

*This section is your direct channel to the Chat Completion Preset. The Prompt Engineer (Phase 5) predicts this world's runtime failure modes on its own and selects preset blocks against them — but only you know the behaviors you care about that no analysis would infer. A runtime directive is an **engine-steering ask**: something about how the model should behave turn-by-turn when running this world. The Refiner records these in Master Design Section 12; the Prompt Engineer must address every one in the preset — by adapting an optional block, extending a world-specific core block, or authoring a custom block — and show the mapping in its Block Selection Rationale.*

*Most worlds need none of these — the standard block library covers the common failure modes. Write a directive only when you have a specific runtime behavior in mind. More than ~6 directives usually means some of them belong elsewhere (see the routing note below).*

**What belongs here vs. elsewhere (the Refiner will reroute misplaced content):**
- A **world fact** ("the Church controls all magic") → Section 2 (Tier 1 lorebook material), not here.
- A **character behavior** ("Anna deflects with sarcasm") → Section 4 LLM Behavioral Instructions (the card), not here.
- **Prose style, perspective, markers** → Section 1.5 Style Contract, not here.
- **Arc-specific tone** ("Arc 2 is dread-heavy") → Section 5 Tone & pacing, not here.
- A **runtime behavior rule that spans the whole world and isn't tied to one character** ("combat must feel slow and costly — wounds accumulate, nobody shrugs off a hit", "NPCs bargain — they never volunteer information for free", "the nobility's honorific system is used in every address, and misuse is a social event the scene reacts to") → **here.**

**Directive 1 — [Short name]:**
- **The behavior:** [Imperative, observable. What must the model do (or never do) at runtime? Not a vibe — a behavior you could check a response against.]
- **A wrong response looks like:** [One or two lines describing the failure this directive prevents. This is what makes the directive testable and tells the Prompt Engineer which failure mode it maps to.]
- **Scope:** [`always` | `Arc N only` | a scene type — e.g., "combat scenes", "court scenes"]

**Directive 2 — [Short name]:**
[Same format — add as needed, typically 0–6 total]

> ⚠️ **Boundary:** runtime directives are implemented in world-tunable preset blocks (Deep Think, Arc Guardian, Lore Integration, Spatial Awareness, Sensory Embodiment, the optional block menu, or a custom block). They are never written into the preset's Main Prompt, Jailbreak, or Formatting blocks, or inside the `<style_contract>` — those are world-agnostic engine surfaces under the override architecture, and a directive that could only live there has been misclassified.

---

## APPENDIX: QUICK REFERENCE — WHAT GOES WHERE

*Use this as a checklist when filling out the World Seed. If you're unsure where something belongs, find its category here.*

### TIER 1 (World Lorebook — permanent, arc-agnostic)
- World rules and mechanics
- Factions and power structures
- Standing locations (appear in 2+ arcs)
- Species and types of beings
- World-level concepts (magic systems, historical events, cosmological facts)
- Sensory signature of the world

### TIER 2 (Character Lorebooks — permanent, arc-agnostic)
- Physical description — baseline anatomy only
- Psychological core
- Backstory
- All significant relationships
- Intimacy substrate — permanent (trauma map, body reactions, vulnerability shape, voice in intimacy, hard limits) — lives in the dedicated Intimacy Profile lorebook
- NPC profiles (in WorldDirector lorebook)
- Protagonist identity lorebook

### TIER 3 — arc mode (Arc Lorebooks — active only during their arc)
- ARC_STATE: genre, tone, narrative state, goals, hidden information rules (CONSTANT)
- CHARACTER_STATE: physical and psychological state this arc (CONSTANT)
- Location variants: how a standing location looks/feels this arc
- NPC_SHIFT: how NPCs behave differently this arc (delta from baseline only)
- DRAMATIC_BEAT: entries that fire when specific story moments are triggered
- TENSION: what is at stake, what the clock is, what failure looks like

### TIER 3 — sandbox mode (one always-active Sandbox Lorebook)
- SANDBOX_STATE: standing situation + tonal mandate + aliveness contract (CONSTANT) — the `ARC_STATE` analog
- WORLD_PULSE: the sustained "the world is alive and reactive" directive (recency-injected) — the `TENSION` analog
- Standing location entries (only sandbox-specific ones; permanent locations stay in Tier 1)
- *No CHARACTER_STATE / NPC_SHIFT / DRAMATIC_BEAT — there is no arc*
- INTIMACY_FUNCTION: what intimacy is for in this arc — thematic function, prose register, direction (CONSTANT, conditional)
- CHARACTER_INTIMATE_REGISTER: per-character arc-specific intimate behavioral delta (CONSTANT, conditional)
- INTIMATE_SCENE_TYPES, INTIMATE_HARD_RULES: arc-specific intimate scene framing (conditional)

### WHAT NEVER GOES IN TIER 2
- Arc-specific physical state (Anna's addiction symptoms belong in Arc 1 ANNA_STATE, not the Tier 2 physical entry)
- Relationship details that change across arcs (put the arc-specific shift in NPC_SHIFT)
- Plot events (those are dramatic beats, not character description)

### WHAT NEVER GOES IN TIER 1
- Anything that changes across arcs
- Character psychology (belongs in Tier 2)
- Story events (those are arc beats)

### WHAT NEVER GOES IN TIER 3
- Baseline character description (already in Tier 2 — don't repeat it)
- World rules that apply in every arc (already in Tier 1)
- Information about what happens in a different arc

---

## APPENDIX: CHECKLIST BEFORE SUBMITTING TO PIPELINE

**Section 1 — Core Concept & Tone:**
- [ ] Logline written
- [ ] Genre and tone per arc described
- [ ] Emotional payoff articulated
- [ ] Tonal rules listed

**Section 1.5 — Style Contract:**
- [ ] Perspective declared (or `DEFAULTS`)
- [ ] Tense declared
- [ ] Narration marker declared
- [ ] Dialogue marker declared
- [ ] Emphasis marker declared
- [ ] Paragraph register declared
- [ ] Style notes captured (or noted as N/A)
- [ ] Per-card overrides (if any) declared in Section 4 with non-empty structural rationales

**Section 2 — The World:**
- [ ] Setting described with specific sensory signature
- [ ] All world rules defined (with costs and consequences)
- [ ] All relevant factions described with trigger keywords
- [ ] All standing locations described with trigger keywords
- [ ] All non-human species/types described
- [ ] All recurring world concepts defined
- [ ] (Optional) World Calendar declared if the story has a fixed start date or a horizon (2g)
- [ ] (Optional) Dice Oracle Tables declared if the story leans on randomized off-screen facts or conjured temp characters (2h)

**Section 3 — The Protagonist:**
- [ ] Identity, hidden layer, contradiction, power/limits defined
- [ ] Arc journey described
- [ ] **Posture Toward {{user}} filled in — default posture declared (`adversarial` / `indifferent` / `mixed` / `deferential`), at least one named force that does not defer, two or three concrete losable things, the permitted shapes of a lost scene *and* the boundary of what is off the table.** Blank is not neutral; blank is deference.
- [ ] Sandbox worlds: the §3 posture declaration and §5B.1's power-fantasy/experience contract agree with each other

**Section 4 — Characters:**
- [ ] Every AI-played character has: psychological core, shield, crack, voice pattern, opening scenario, first message, example exchanges
- [ ] Every character has a physical baseline description
- [ ] Every character has a state entry per arc
- [ ] Load-bearing relationships note how they drift across arcs (with the causing beat) and any operative belief; arc blocks carry a "Relationship shifts this arc" line where a bond moves (or "stable" / sandbox standing stance)
- [ ] Every NPC has a profile — principals as full profiles, roster NPCs as compact stat blocks (large casts); roster voice fingerprints are unique; principal NPCs have a Standing Goal (active objective + how they pursue it)
- [ ] Escalation Ladders (where used): 2–4 ordered stages, each with an in-fiction observable advance condition; a stated endpoint; a stated {{user}}/main-story collision; no more than ~3 laddered NPCs in the world
- [ ] LLM behavioral instructions written for each card (with arc-range qualifiers)
- [ ] For characters with intimate scene presence: substrate (trauma map, **embodied baseline**, body reactions, vulnerability shape, voice in intimacy, hard limits, **afterward**) and arc-specific evolution filled out
- [ ] Embodied baseline filled in for *every* intimate character — including the ordinary/default-bodied ones — written in observable register, running in both directions (what is harder *and* what is easier or more certain)
- [ ] **Physical dyad** filled in for every pairing with a real height, age, build, stamina, experience, or world-specific differential (`{{user}}` pairings first), with the asymmetry authored in both directions

**Section 5 — Arcs (arc mode) / Sandbox Charter (sandbox mode):**
- [ ] `World Mode` declared in Section 1 (`arc` or `sandbox`)
- [ ] *Arc mode:* every arc has genre tag, thematic description, dramatic beats, hidden information rules, NPC shifts, entry and exit triggers; triggers are specific events, not states
- [ ] *Sandbox mode:* Sandbox Charter (5B) filled — Standing Situation, Tonal Mandate (4–8 directives incl. aliveness), World Pulse; arc blocks (5A) left empty

**Section 6 — Technical:**
- [ ] Lorebook structure matches actual content (including intimacy profile and register files where applicable)
- [ ] Arc count matches arc count in Section 5

**Section 7 — Test Scenarios:**
- [ ] 3–5 specific scenarios listed
- [ ] At least one intimate scenario listed if the world contains intimate content

**Section 8 — Intimacy & Sexuality (skip entirely if not applicable):**
- [ ] World-level posture defined with notes
- [ ] World-level tonal hard rules listed
- [ ] World-level prose register described
- [ ] Per-arc thematic function, prose manifestation, direction, and live scene types specified for every arc with intimate beats
- [ ] Cross-arc intimacy trajectory described (recommended)

**Section 9 — Runtime Directives (skip entirely if not needed):**
- [ ] Each directive is an imperative, observable runtime behavior with a "wrong response looks like" example and a scope
- [ ] No world facts, character behaviors, or style/marker content smuggled in (those belong in Sections 2, 4, and 1.5)
- [ ] Kept to ~6 or fewer