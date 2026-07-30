# Shared contracts (canonical)

This directory is the **canonical source of truth** for the design contracts
shared between the World-Forge pipeline and the `world-forge` + `npc-memory`
SillyTavern extensions in the fork.

| File | Covers |
| --- | --- |
| [`MEMORY_CONTRACT.md`](./MEMORY_CONTRACT.md) | The npc-memory data channel: `[[NPC_MANIFEST]]`, facets, stable ids, the `npcmem` turn tag, scenes registry, prose fallback. |
| [`WORLD_FORGE_SYNC.md`](./WORLD_FORGE_SYNC.md) | The runtime seams: Director-card tag, narration-surface alias coverage, the `</style_contract>` marker, `style_override` runtime, the `[[WORLD_CALENDAR]]` Scene Tracker date seed, plus a producer conformance checklist. |
| [`DICE_ORACLE.md`](./DICE_ORACLE.md) | The dice oracle channel: the `[[DICE_TABLES]]` carrier entry, roll-table payload (pools, procedures, conditional steps, `framing`), and the Scene Tracker's authoritative-facts injection. |
| [`BODY_CYCLES.md`](./BODY_CYCLES.md) | Recurring body states: the `[[BODY_CYCLES]]` carrier, per-character cycle seed payload, and phase derivation from the Scene Tracker day counter. **Consumer implemented, producer not wired** — no agent spec emits the carrier yet, so it fires only on hand-authored entries. |

These files live here, next to `tools/validate_export.py` — the producer that
must conform to them. The SillyTavern fork carries a read-only mirror and keeps
it byte-identical via its `scripts/sync-contracts.sh` plus a CI drift check.
Edit the contracts here; the fork re-syncs from this directory.

**Status matters, and each contract states its own.** Three states occur, because
the two sides of a seam land independently:

- **Established** — both sides live. The extensions read it and the producer
  pipeline conforms to it. `MEMORY_CONTRACT.md`, `WORLD_FORGE_SYNC.md`,
  `DICE_ORACLE.md`.
- **Established (consumer only)** — the extension reads it, but no agent spec
  emits its carrier yet, so it fires only on hand-authored entries. The payload
  shape is settled and versioned; the producer-conformance section is the expected
  shape rather than an in-force requirement. `BODY_CYCLES.md`.
- **Draft** — a design agreement for a seam that does not exist on either side.
  Nothing reads it, no agent spec references it, producers must not emit its
  carrier. Drafts live here so both sides can be designed against one shape
  rather than two.

Read a contract's header before assuming either side works — "the contract
exists" and "the pipeline emits it" are different claims, and the header is where
that distinction is recorded.
