---
description: World Forge post-launch operations on shipped worlds — revise routing, convert summary, preset resync, audition. Referenced by workflows/world-forge.md.
---

# WORLD FORGE — POST-LAUNCH OPERATIONS
*Referenced by the router (`workflows/world-forge.md`). These are operating modes on **shipped** worlds — not build stages, and not part of the Stage 1–4 dispatch sequence.*

A shipped world (Phase 5.5 complete, Export/ ready, world in play) is changed through the four operations below, each with its own trigger command (router → TRIGGER COMMANDS). The revise and convert operations have their own full workflow files; this file carries the routing rules between them plus the complete PRESET RESYNC and AUDITION operations.

---

## POST-LAUNCH REVISIONS

Once a world has completed Phase 5.5 (pipeline complete, Export/ ready, world in play), surgical changes use the **revision pipeline** — a parallel fork that runs mini-versions of the build agents with read-mostly authority and UID-preserving compilation. See `workflows/world-forge-revise.md` for the full revise pipeline.

The bright line is **Master Design Section 1 (Core Concept & Tone) and Section 11a (Style Contract world defaults)**. Revisions that don't touch these stay in the revision pipeline (faster, surgical, preserves running ST chat states). Revisions that touch them require a full re-run from Phase 1 via `/worldforge skip phase0` — the existing `World_Seed.md` is reused, the Interviewer is skipped, and Phases 1–5 rebuild from scratch. The Reviser performs this classification and bounces out-of-scope revisions automatically.

**When the rebuild is also a reframe — different protagonist, different World Mode, different tonal register — use `/worldforge convert` instead** (see CONVERT below). Convert is the legitimate path for the exact change-categories the revise pipeline bounces: it reads the shipped world's `Master_Design.md` (read-only), captures keep/modify/regenerate decisions, and produces a new `World_Seed.md` in a fresh target folder, then hands off to `/worldforge skip phase0`. Convert preserves the structural world-building work that a from-scratch `/worldforge start` would discard.

---

## CONVERT (reframe a shipped world into a new build)

A shipped world's `Master_Design.md` carries substantial structural work — world rules, factions, cosmology, NPCs — that survives a protagonist swap, a World Mode flip, or a Style Contract change even though the revise pipeline cannot. `/worldforge convert` is the operation that captures the reuse: it reads the source's `Master_Design.md` (read-only), walks the user through a preservation matrix (keep / modify / drop / regenerate, per source section), surfaces role reassignments explicitly (the old protagonist becoming an NPC, a source NPC becoming the new `{{user}}`, power-tier shifts), and authors a new `World_Seed.md` in a target project folder.

It invokes the Converter (`agent_roles/Converter/00_The_Converter.md`) as a single phase (C0). The Converter does not replace any pipeline phase; it produces the input to Phase 1. After C0 completes, the user runs `/worldforge skip phase0` against the target folder and the standard pipeline (Phases 1–5.5) builds the new world end-to-end.

**Load-bearing properties:**
- **Read-only on source.** The Converter never modifies any file in the source project. Hard rule.
- **Write-only on target's `World_Seed.md`.** Does not write `Drafts/`, `Export/`, or any other file in the target project — those are the standard pipeline's job.
- **Overlap floor refusal.** If the conversion replaces 3 or 4 of (setting, protagonist, factions, tone), the Converter refuses. That's a fresh build inspired by the source — `/worldforge start` is the right path. Borderline (2 axes replaced) gets surfaced for explicit user confirmation.
- **Single source.** No mashups. Mashing two worlds together is out of scope; run Convert once, use revise later if you want to splice content from a third source.
- **Always-regenerated content (reframe mode).** Section 3 (`{{user}}`), Section 5 (arcs / Sandbox Charter), Section 7b (test scenarios), per-arc/standing intimate functions, and per-card style overrides are always regenerated downstream. These are protagonist-shaped or downstream-derived, so they cannot transfer mechanically. The Converter does not let the user mark them `keep` — except in Rebaseline mode, where the premise (a changed protagonist) is absent and they flip to keep-by-default.
- **Rebaseline mode (`--rebaseline`).** The zero-axes-replaced conversion: same world, same protagonist, rebuilt clean from its *post-revision* Master Design — the consolidation path for a world whose accumulated revisions (R1…R[N]) have outgrown surgical editing, especially when new mechanics are coming. Revision content carries; revision markers do not; the rebuild gets fresh UIDs (running chats do not migrate — the Converter states this cost explicitly). Spec: `agent_roles/Converter/00_The_Converter.md` Section 9; operation: REBASELINE MODE section of `workflows/world-forge-convert.md`.
- **Convert Brief support.** Users can pre-author the keep/modify/regenerate decisions in a `Convert_Brief.md` (against `templates/Convert_Brief_Template.md`) for version-controllable, reviewable conversions. The Converter validates the brief against the source and interviews only on gaps. Pure interview mode also works for ad-hoc conversions. Briefs declare `Operating mode: reframe | rebaseline` in their Section 1.

See the **CONVERT** workflow at `workflows/world-forge-convert.md` for the full operation, the Conversion Manifest format, and the role-reassignment cases.

---

## PRESET RESYNC (post-launch preset upgrade)

A shipped world's `Export/[WorldName]_ChatPreset.json` can fall behind in two independent ways: the **pipeline's preset spec** evolves (a reframed core block, a new optional block, a changed template flag), and/or the **world's content** changes through the revision pipeline (a revised or added arc, a new character) in ways that surface inside preset blocks (Deep Think names the arcs, Arc Guardian references them, the multi-character lattice names characters) but that the revise mini-Prompt-Engineer never writes — it only toggles Multi-Character Dynamics, NSFW, and the Style Contract's conditional ACTIVE-SPEAKER RULE / DIRECTOR-CARD RULE lines. `/worldforge resync-preset` brings the preset current on both, without touching world content.

It invokes the Prompt Engineer in **Preset Resync Mode** (`agent_roles/05_The_Prompt_Engineer.md` Section 8). The agent re-derives each block's content from the current `templates/Chat_Completion_Preset_template.json` + block library (`agent_roles/05a_Block_Library.md`) + the post-revision `Drafts/Master_Design.md`, writes the blocks whose content has drifted (from a spec change, a revision content change, or both) and adds newly-warranted optional blocks, preserves block identifiers + `prompt_order` + revision-applied toggles + the user's field-level customizations, re-runs the Section 5f Pass 1 + Pass 2 self-validation, and writes `Export/Preset_Resync_Report.md` documenting every block changed (with cause), added, or preserved.

**Scope and boundaries:**
- **Preset only.** Resync regenerates the Chat Completion Preset — the one Export/ file the Prompt Engineer authors. It does NOT re-audit lorebooks or cards and does NOT emit Section 7/8 manual-apply recommendations. World content (lorebooks, cards, drafts) is untouched.
- **Reads the post-revision world.** Because it re-derives block content from the current `Master_Design.md`, resync picks up content changes made through the revision pipeline that the revise mini-PE leaves out of the preset. It preserves the toggles the revise mini-PE *does* apply (Multi-Character Dynamics, NSFW, ACTIVE-SPEAKER RULE, DIRECTOR-CARD RULE) — while a *missing-but-warranted* DIRECTOR-CARD RULE line (a Director-card world whose preset predates SHARED §3d) counts as ordinary spec drift that resync adds.
- **Distinct from `resume phase5`.** `resume phase5` re-runs the full Phase-5 audit during an in-progress build. `resync-preset` is a maintenance op on an already-shipped world that only refreshes the preset.
- **Distinct from the revise pipeline.** The revise pipeline *makes* surgical content changes. Resync makes none — it reflects already-applied content and spec changes into the preset. A world can be resynced without ever entering revise, and revised worlds can be resynced afterward to bring the preset fully current.
- **Low risk.** A Chat Completion Preset is a global SillyTavern settings profile, not UID-bearing world info, so re-importing a resynced preset does not disturb running chat states. Git is the rollback path if the user wants the prior preset back.

---

## AUDITION (on-demand behavioral probe, post-launch)

You are deep into playing a shipped world and a question surfaces that the personality is too complex to answer from memory: *would this character actually do this, in this moment, under these conditions?* Gambling a real scene to find out is expensive. `/worldforge audition` is the cheap, read-only way to find out first.

It invokes **The Auditioner** (`agent_roles/Auditioner/00_The_Auditioner.md`) as a single standalone post-launch operation — **not** a numbered pipeline phase. The user hands it one focal character, one scene, the active conditions (which arc, or the standing sandbox state), and optionally the behavior they expect; the Auditioner loads that character's spec as runtime context, simulates the scene **as the model would run it**, and returns a verdict with a trace.

It is the **single-scenario, user-driven cousin of the Voice Auditor** (Phase 3.5). Where the Voice Auditor runs at build time, generates its own systematic matrix across the whole cast and every arc, and feeds rewrite directives back to the Architect, the Auditioner runs whenever the user is curious mid-play, tests exactly the one situation the user names, and changes nothing. It reuses the Voice Auditor's simulation discipline and check vocabulary (Step 3) rather than re-deriving them, and applies the Intimacy Auditor's lens when the probed scene is intimate.

**Load-bearing properties:**
- **Read-only on the whole project.** The Auditioner modifies nothing — not `Drafts/`, not `Export/`, not `Master_Design.md`. It answers a question (audit/apply separation, CLAUDE.md principle #3). When it finds a real gap, it hands the user a **revise handle** (the file + element + kind of change) — it does not apply the change. The user decides; the revise pipeline applies.
- **Three honest verdicts.** Every run resolves to **YES** (the spec reliably produces the expected behavior), **NO** (the spec drives a *different* behavior — the character is correct per spec, the spec just doesn't match the expectation), or **IT DEPENDS** (the spec is silent or self-conflicting here, so the outcome isn't determined — a latent coverage gap surfaced on demand). "Probably" is not a verdict.
- **Mode- and intimacy-aware by inheritance.** Arc worlds load the user-named active arc's CHARACTER_STATE/NPC_SHIFT; sandbox worlds use the standing SANDBOX_STATE (and the user-named ladder stage where one exists). Intimate scenarios additionally pull the Intimacy Profile + active register and apply the intimacy lens. No new machinery — it reuses what the build-time auditors already define.
- **World layer, not engine layer.** It simulates from the Drafts (the content spec the Voice Auditor reads), not the Chat Completion Preset (the engine layer). When real play diverges from a YES verdict, the cause may be the preset, and `/worldforge resync-preset` may be the fix — the Auditioner flags this rather than pretending to have simulated the engine.
- **Not a phase.** It does not advance the Pipeline State Ledger, does not invoke any downstream agent, and produces no first-class pipeline artifact. The optional `--save` record (`Drafts/Audition_[Char]_[slug].md`) is an informal log, read by nothing downstream and deletable freely.
- **Shipped-world precondition, detected from the world — not the ledger.** It is a post-launch tool. It confirms shipped-status from the direct signal (a populated `Export/` + Refiner sign-off, with a Revision Log / `REVISED_FILES.md` as conclusive proof), **not** from the Pipeline State Ledger — which on a shipped-and-revised world is routinely stale or absent and must not be read as "mid-build." Likewise it reads **World Mode from Master Design Section 1**, so a sandbox world is never mistaken for an unfinished arc world. Only a world that never reached the Compiler is declined, with a pointer to the Voice Auditor (Phase 3.5).
