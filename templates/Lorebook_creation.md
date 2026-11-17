I need you to generate a world lorebook for a text-based roleplaying game.
Please output the result strictly as a valid JSON file using the exact structure provided below. Do not include markdown formatting errors, and do not include any comments in the final JSON output.

Here is the concept for the world, factions, and important items I want you to build:
[INSERT YOUR WORLD LORE, PLACES, FACTIONS, AND IMPORTANT CONCEPTS HERE]

Break down the lore into separate entries. Fill out this exact SillyTavern Lorebook JSON structure. Add as many entries ("0", "1", "2", etc.) as necessary to cover the provided lore.

POSITION VALUES (use the correct one for each entry type):
- 0 = Before Character Definition — world rules, factions, species, mechanics. Must load before the character card so the model understands the world the character inhabits.
- 1 = After Character Definition — character reference data, NPC profiles, arc state, dramatic beats, location entries. Standard default for most entries.
- 2 = Author's Note Top — tone and atmosphere directives only. Not for lore facts.
- 3 = Author's Note Bottom — tone and atmosphere directives only. Not for lore facts.
- 4 = At Depth — TENSION entries and urgency injections. Injects inside chat history at the depth value from the end. Maximum recency for immediate model awareness.
- 5 = Example Messages Top — prepended to the dialogue examples block.
- 6 = Example Messages Bottom — appended to the dialogue examples block.
- 7 = Outlet — sends content to a named outlet channel (advanced use only).

ENTRY TYPE → CORRECT POSITION:
- World rules, factions, species definitions → position: 0
- Character physical descriptions, psychology, NPC profiles → position: 1
- Arc state (ARC_STATE), dramatic beats, NPC behavioral shifts → position: 1
- TENSION entries (narrative urgency, active stakes) → position: 4, depth: 2-4

SANDBOX-MODE ENTRY TYPES (worlds with no narrative arc — one always-active Sandbox Lorebook instead of per-arc lorebooks):
- SANDBOX_STATE (the ARC_STATE analog — standing world-state + tonal mandate + aliveness contract) → position: 1, constant: true, selective: true, ignoreBudget: true
- WORLD_PULSE (the TENSION analog — a sustained "the world is alive and reactive" directive, never a countdown) → position: 4, depth: 2-4
- Roster NPC compact stat block (essence / presence / unique voice fingerprint / signature line / stance / hook) → position: 0 or 1 (same as other NPC profiles)
- Sandbox standing intimacy: INTIMACY_FUNCTION (no arc suffix) → position: 1, constant: true, ignoreBudget: true
- EROTIC_LEXICON (arc: EROTIC_LEXICON_Arc[N]; sandbox: no suffix) — only where the effective Erotic Register is explicit or pornographic → position: 1, constant: false, keyed on intimate lead-in words plus the lexicon's own vocabulary (constant: true is a permitted non-default where the primary function is Indulgence)
- A sandbox world has NO CHARACTER_STATE, NPC_SHIFT, DRAMATIC_BEAT, or arc-trigger entries — there is no arc.
- Tone/atmosphere directives → position: 2 or 3

KEY FIELD RULES:
- "uid": unique integer per entry, sequential from 0, never duplicated within a lorebook.
- ENTRY OBJECT KEYS MUST EQUAL UIDs: each entry's string key in "entries" must equal String(uid) — entry with "uid": 5 is keyed "5". SillyTavern stores and looks up entries as entries[uid]; a file whose keys don't match its UIDs imports without error but its entries never render in the World Info editor.
- "scanDepth" / "caseSensitive" / "matchWholeWords" / "useGroupScoring": per-entry overrides, camelCase exactly as written, set to null to inherit the lorebook/global defaults. Do NOT use the snake_case variants ("case_sensitive", "match_whole_words", "use_regex") or "characterFilterNames"/"characterFilterExclude" — those belong to the embedded character_book card format and are ignored in a standalone lorebook file.
- "displayIndex": integer editor sort position; set it equal to the entry's uid.
- "key": primary activation keywords. Empty array [] for CONSTANT entries only.
- "constant": true = fires every context window regardless of keywords. Must also have selective: true and ignoreBudget: true. Use for ARC_STATE and CHARACTER_STATE entries (arc mode), or SANDBOX_STATE and the standing INTIMACY_FUNCTION (sandbox mode).
- "selective": true on ALL entries including CONSTANT ones.
- "selectiveLogic": 0 = AND ANY (fires if any secondary key present), 1 = NOT ALL, 2 = NOT ANY (fires only if no secondary keys match), 3 = AND ALL.
- "useProbability": false for entries that should always fire when triggered. true only for stochastic entries where probability < 100.
- "ignoreBudget": true for ARC_STATE / SANDBOX_STATE and critical CONSTANT entries that must never be omitted. false for standard entries.
- "disable": false for all active entries. Do NOT use "enabled: true" — the correct field is "disable: false".
- "group": use to group entries by tier for ST lorebook editor management (e.g., "World", "Anna", "Arc1" for arc worlds; "Sandbox" for the single always-active sandbox lorebook).
- "depth": only relevant when position = 4. How many messages from the bottom of chat history to inject.

{
  "name": "Lorebook_Name",
  "description": "General description of the world or setting.",
  "scan_depth": 50,
  "token_budget": 2048,
  "recursive_scanning": false,
  "extensions": {},
  "entries": {
    "0": {
      "uid": 0,
      "comment": "Internal title/memo for the entry.",
      "key": ["Keyword1", "Keyword2"],
      "keysecondary": [],
      "selectiveLogic": 0,
      "content": "The actual lore text that will be injected into the prompt.",
      "position": 1,
      "order": 100,
      "depth": 4,
      "role": 0,
      "selective": true,
      "constant": false,
      "probability": 100,
      "useProbability": false,
      "addMemo": true,
      "disable": false,
      "ignoreBudget": false,
      "vectorized": false,
      "group": "",
      "groupOverride": false,
      "groupWeight": 100,
      "scanDepth": null,
      "caseSensitive": null,
      "matchWholeWords": null,
      "useGroupScoring": null,
      "excludeRecursion": false,
      "preventRecursion": false,
      "delayUntilRecursion": false,
      "matchPersonaDescription": false,
      "matchCharacterDescription": false,
      "matchCharacterPersonality": false,
      "matchCharacterDepthPrompt": false,
      "matchScenario": false,
      "matchCreatorNotes": false,
      "sticky": 0,
      "cooldown": 0,
      "delay": 0,
      "displayIndex": 0,
      "outletName": "",
      "automationId": "",
      "triggers": []
    }
  }
}

Add sequential entries ("1", "2", "3") under "entries" following the exact same field structure — every entry's string key must equal String(uid), and "displayIndex" matches the uid.
"order": higher numbers inject first (appear higher in context). Default 100. Use 90 for NPC shifts, 85 for dramatic beats, 70-80 for locations.
"role": 0 = System (use this for all world/arc/character entries), 1 = User, 2 = Assistant.
