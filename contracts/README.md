# Shared contracts (canonical)

This directory is the **canonical source of truth** for the design contracts
shared between the World-Forge pipeline and the `world-forge` + `npc-memory`
SillyTavern extensions in the fork.

| File | Covers |
| --- | --- |
| [`MEMORY_CONTRACT.md`](./MEMORY_CONTRACT.md) | The npc-memory data channel: `[[NPC_MANIFEST]]`, facets, stable ids, the `npcmem` turn tag, scenes registry, prose fallback. |
| [`WORLD_FORGE_SYNC.md`](./WORLD_FORGE_SYNC.md) | The runtime seams: Director-card tag, narration-surface alias coverage, the `</style_contract>` marker, `style_override` runtime, the `[[WORLD_CALENDAR]]` Scene Tracker date seed, plus a producer conformance checklist. |
| [`DICE_ORACLE.md`](./DICE_ORACLE.md) | The dice oracle channel: the `[[DICE_TABLES]]` carrier entry, roll-table payload (pools, procedures, conditional steps, `framing`), and the Scene Tracker's authoritative-facts injection. |
| [`BODY_CYCLES.md`](./BODY_CYCLES.md) | 🚧 **Draft — no consumer exists.** Proposed recurring body-state channel: the `[[BODY_CYCLES]]` carrier, per-character cycle payload, and phase derivation from the Scene Tracker day counter. Producers must not emit this carrier yet; open questions in its §7 must be settled first. |

These files live here, next to `tools/validate_export.py` — the producer that
must conform to them. The SillyTavern fork carries a read-only mirror and keeps
it byte-identical via its `scripts/sync-contracts.sh` plus a CI drift check.
Edit the contracts here; the fork re-syncs from this directory.

**Status matters.** An established contract documents a seam the extensions
already read, and the producer pipeline conforms to it. A **draft** records a
design agreement for a seam that does not exist yet — no consumer reads it, no
agent spec references it, and producers must not emit its carrier. Drafts are
here so both sides can be designed against one shape rather than two; they
become established, and binding on producers, only once the consumer lands.
