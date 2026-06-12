# Agentic Tools and Models for World-Forge

This page covers which agentic VS Code extensions can drive the World-Forge pipeline, how to configure them, and which underlying LLMs perform well in each phase. It is aimed at users who already understand what the pipeline does (see the [README](../README.md) and [tutorial.md](../tutorial.md)) and want to set up the *runtime environment* that executes it.

> **TL;DR** — The recommended tool is **Kilo Code**, which this repo ships preconfigured for (`.kilo/kilo.jsonc`). **Cline** works well as a simpler alternative. **Roo Code** — the tool the pipeline was originally designed against — was **retired on May 15, 2026** and should not be adopted for new setups; see [§2.3](#23-roo-code-retired-may-15-2026). The pipeline is **not** optimized for code-focused agents like Claude Code — see [Why Claude Code is a poor fit](#why-claude-code-is-a-poor-fit-currently). For the underlying LLM, prefer literary-register models (Claude Opus / Sonnet, GPT-5, Gemini 2.5 Pro) over coding-tuned variants.

---

## 1. What the pipeline asks of an agentic tool

World-Forge is not application code. It is a set of markdown agent specifications, templates, and an orchestrator (`workflows/world-forge.md`) that an external agentic IDE extension reads and executes. For a tool to drive the pipeline well, it needs:

1. **File read/write tools** across the workspace (the agents produce `Drafts/*.md` and `Export/*.json` artifacts).
2. **Multi-step, multi-file autonomy** — phases run sequentially and each phase consumes the previous phase's outputs.
3. **Long-context tolerance** — by Phase 3 the working set (Master Design + all drafts + Notes_On_functionality.md) can exceed 100K tokens.
4. **Per-phase persona or mode switching** — each agent in `agent_roles/` is a *different* persona with different rules. Tools that can swap system prompts or modes mid-run handle this cleanly.
5. **A trigger-command convention** — the pipeline is driven by `/worldforge start`, `/worldforge resume phase[N]`, etc. The tool needs to let you type free-form instructions that the executing agent interprets against `workflows/world-forge.md`.

You do **not** need: code execution, terminal automation, build/test integration, git automation, or any MCP servers. Nothing in the pipeline runs code, and built-in file edit tools cover the entire workload — adding MCP servers imports complexity for no documented benefit. See the [MCP servers section in the Kilo Code setup page](./Kilo-Code-Setup.md#9-mcp-servers--none-required) for category-by-category guidance and a specific note on Iron Manus MCP, which is sometimes suggested but is the wrong fit.

---

## 2. Supported agentic tools

> **Roo Code retirement (May 15, 2026).** The pipeline was originally authored against Roo Code's Orchestrator mode. Roo Code shut down all its products on May 15, 2026 — the VS Code extension is archived and receives no further updates. The recommended tool is now **Kilo Code**, which began as a Roo fork and is feature-compatible for the pipeline's purposes. See [§2.3](#23-roo-code-retired-may-15-2026) if you are still running Roo.

### 2.1 Kilo Code (recommended — reference tool)

[Kilo Code](https://github.com/Kilo-Org/kilocode) is the recommended tool and the one this repository ships configuration for (`.kilo/kilo.jsonc` per-phase agents, `.kilocodeignore` context discipline). It is an open-source extension that began as a fork of Roo Code — the tool the pipeline was authored against — and merges features from Roo and Cline, so its orchestration model maps cleanly onto World-Forge's phase-by-phase persona swaps.

**Why it fits:**
- **Subagent delegation** is built into the default Code / Plan / Debug agents: the top-level agent dispatches each phase's persona (`agent_roles/00_The_Interviewer.md`, `agent_roles/02_The_Architect.md`, etc.) as a distinct subtask with its own system prompt. You don't have to manually re-prime the agent between phases.
- Strong file-edit toolchain (read, write, diff, search-and-replace) — required for the Architect's draft files and the Compiler's JSON output.
- Supports any OpenAI-compatible API endpoint, so you can route to Anthropic, OpenAI, Google, OpenRouter, or a local server.
- **Custom agents with per-agent model and temperature selection** — each phase's agent pins its system prompt to the matching spec file (e.g., a `WorldForge-Architect` agent pinned to `agent_roles/02_The_Architect.md`), which reduces drift on long runs and mirrors the [Audit-vs-Apply separation](../CLAUDE.md#3-audit-vs-apply-separation). The repo's shipped `.kilo/kilo.jsonc` already defines this agent set.
- Open source under a permissive license — useful if you want to audit or extend the tool itself.

**Terminology caveat (April 2026 rebuild):** Kilo renamed "Modes" to **Agents** and **deprecated the dedicated Orchestrator mode** — subagent delegation is now built into the default Code / Plan / Debug agents. Older Roo-style tutorials that say "switch to Orchestrator mode" do not map directly; use the **Code** agent as the entry point and pin custom subagents per phase.

**Setup:** See the dedicated [Kilo Code Setup tutorial](./Kilo-Code-Setup.md) for step-by-step install, provider configuration, custom-agent definition, and a first-run smoke test. Short version: install the `kilocode.Kilo-Code` extension, configure your provider via the sidebar gear icon, open the World-Forge workspace, select the **Code** agent, and type `/worldforge start`.

### 2.2 Cline

[Cline](https://github.com/cline/cline) (formerly Claude Dev) is a simpler, single-mode agentic extension. It runs the pipeline competently but without per-phase mode switching — you rely on the orchestrator file to keep the agent on-script.

**Why it works:**
- File read/write tools are robust and well-tested.
- Conservative auto-approval defaults make it easy to step through each phase manually, which is useful during your first run.
- Wide model provider support (Anthropic, OpenAI, Bedrock, Vertex, OpenRouter, local).

**Tradeoffs vs. Kilo Code:**
- No native subagent delegation. The agent stays in one persona across the run, so you depend on `workflows/world-forge.md` to instruct it to "now act as the Editor" at the right moment. In practice this works but is more prone to persona bleed on long runs.
- No custom modes — you can't enforce read-only filesystem access for auditor phases at the tool level; you depend on the auditor agent specs themselves to honor the [Audit-vs-Apply separation](../CLAUDE.md#3-audit-vs-apply-separation).

**Setup:**
1. Install Cline from the VS Code marketplace.
2. Configure your model provider in Cline settings.
3. Open the workspace and type `/worldforge start` in the chat.

**Recommendation:** Good first-time choice if you want a simpler tool with fewer knobs. Migrate to Kilo Code's per-phase custom agents once you're comfortable with the pipeline's structure.

### 2.3 Roo Code (retired May 15, 2026)

[Roo Code](https://github.com/RooCodeInc/Roo-Code) is the tool the pipeline was originally authored against; its **Orchestrator mode** shaped the pipeline's phase-dispatch design. **It was retired on May 15, 2026:** all Roo Code products (the VS Code extension, Roo Code Cloud, and the Router) were shut down, the GitHub repository was archived (read-only), and the extension remains on the VS Code Marketplace only in its final state — no bug fixes, no model updates.

**Do not adopt Roo Code for a new setup.** If you are still running the pipeline under a final-state Roo install, it will keep working until a VS Code or provider-API change breaks it, but you should migrate:

- **Kilo Code** ([§2.1](#21-kilo-code-recommended--reference-tool)) started as a Roo fork with shared git history — custom modes, project rules, and per-mode model selection all carry over, and this repo ships a preconfigured `.kilo/kilo.jsonc`. This is the recommended destination.
- **Cline** ([§2.2](#22-cline)) is Roo Code's own parting recommendation for a model-agnostic open-source extension, at the cost of no per-phase mode switching.

Nothing in the pipeline itself is Roo-specific — the trigger commands are free-form prompts interpreted against `workflows/world-forge.md` — so migration is a tool swap, not a pipeline change.

### 2.4 Compatibility summary

| Tool | Orchestrator / multi-mode | File edit tools | Custom modes | Recommended for |
|---|---|---|---|---|
| **Kilo Code** | Yes (subagent delegation from Code/Plan/Debug agents) | Yes | Yes | All runs — ships preconfigured in this repo (`.kilo/kilo.jsonc`) |
| **Cline** | No (single-mode) | Yes | No | First-time users, simpler runs |
| **Roo Code** | Yes (Orchestrator) | Yes | Yes | **Nothing — retired May 15, 2026; migrate to Kilo Code or Cline** |

---

## 3. Model recommendations

The pipeline is unusually demanding of the underlying LLM. Most phases are *literary* tasks (prose drafting, voice consistency, character psychology, tonal register) rather than *engineering* tasks. Choose models accordingly.

### 3.1 What to optimize for

- **Literary register** — the model must hold tone across many turns. The Editor and Voice Auditor explicitly grade this.
- **Character psychology** — the Architect and Intimacy Architect produce prose that depicts internal states, contradiction, trauma response, and shifting registers across arcs. Models that flatten everything to "helpful assistant" voice will fail Phase 3.5.
- **Long context** — Phase 3+ work easily exceeds 100K input tokens once drafts, Notes_On_functionality, and arc files are loaded.
- **Instruction adherence under length** — agent specs are long (some over 1000 lines). Models that "lose the system prompt" after a few thousand tokens of conversation will silently drift off-architecture.

### 3.2 Recommended tiers

**Strongest fit for creative phases (Interviewer, Architect, Editor, all Auditors, Intimacy Architect):**
- **Claude Opus 4.7** — best literary register and characterization currently available; expensive but worth it for the auditor phases where false negatives are costly.
- **Claude Sonnet 4.6** — the best price/quality balance for the bulk of the run. The pipeline was authored against Sonnet-class models and works well end-to-end on it.
- **GPT-5** — strong literary capability, very long context. Slightly more "instructed" feel than Claude in prose registers; sometimes over-explains.
- **Gemini 2.5 Pro** — excellent at long-context cross-reference work (useful for the Editor's cross-tier validation). Prose register is acceptable but tends toward neutral; pair with explicit tonal directives.
- **DeepSeek 4 Pro** — strong literary register and characterization at a materially lower price point than the frontier proprietary models. Solid instruction adherence on long agent specs; a viable alternative for cost-sensitive runs where you still want creative-phase quality. Verify your agentic tool's provider list supports it (Kilo Code and Cline both do via OpenAI-compatible endpoints or OpenRouter). Nominal **1M context window**, so the pipeline never comes close to filling it — but read [§3.4](#34-context-discipline-on-deepseek-and-glm) before committing a full run: *effective* recall under dense instructions, not window size, is what to manage.
- **GLM 5** — capable literary register and good structured-output discipline at DeepSeek-class pricing; a solid pick for the drafting phases on a budget run. Nominal **200K context** — the same class the pipeline was sized against — though the [§3.4 context discipline](#34-context-discipline-on-deepseek-and-glm) still pays off in audit sharpness and cost. Available via OpenRouter (`z-ai/glm-5`) and OpenAI-compatible endpoints.

**Acceptable for utility phases (Refiner classification, Compiler JSON transformation, Prompt Engineer block assembly):**
- Claude Haiku 4.5 — cheap and fast, sufficient for structured-output transformations where literary judgment is not required.
- GPT-4.1 mini / GPT-5 mini — similar role.

**Not recommended:**
- Small open-weights models (7B–13B) — context handling and instruction adherence are insufficient for the multi-phase orchestration.
- Coding-tuned model variants — same failure mode as Claude Code (see below): voice flattens, characterization gets generic.
- Models without ~200K usable context — you will hit context limits in Phase 3.
- **Flash-tier / fast-tier models for Phase 4 (Compiler) and Phase 2 (Architect).** Reported failure mode on **Gemini 3.1 Flash**: the model produced sparse, structurally incomplete JSON in Phase 4 and dropped load-bearing fields from character cards — including the mandatory `{{original}}` macro at the top of `system_prompt` and `post_history_instructions`. That macro is the linchpin of the [Override Architecture](../CLAUDE.md#2-the-override-architecture-paired-contract); dropping it causes the card to silently replace the preset's Main Prompt at runtime, breaking engine-level rules. Flash-tier models in general appear to "summarize" structured output rather than emit it verbatim, which is exactly the wrong behavior for the Compiler. Use a Pro-tier or frontier-tier model for any phase that produces JSON or that must reproduce specific literal strings (macros, position values, sign-off blocks).

### 3.3 Mixing models across phases

If your agentic tool supports per-mode model configuration (Kilo Code does), a cost-effective pattern is:

| Phase | Suggested model |
|---|---|
| Phase 0 (Interviewer) | Sonnet 4.6 |
| Phase 1 (Refiner) | Sonnet 4.6 or Haiku 4.5 |
| Phase 2 / 2.5 (Architect / Intimacy Architect) | Opus 4.7 or Sonnet 4.6 |
| Phase 3 (Editor) | Opus 4.7 |
| Phase 3.5 / 3.6 / 3.7 (Auditors) | Opus 4.7 |
| Phase 4 (Compiler) | Sonnet 4.6 or Haiku 4.5 |
| Phase 5 (Prompt Engineer) | Sonnet 4.6 |

Spend the most where the literary judgment is most load-bearing (Architect, Editor, Auditors). Save on structural transformation phases.

**Aggregator routing note.** The model names above are display names. If you route through OpenRouter or Nano-GPT rather than direct provider accounts, the model strings you actually configure are provider-prefixed in the aggregator's catalog format (e.g., `anthropic/claude-opus-4-7`, `deepseek/deepseek-v4-pro`). For Kilo Code specifically, the per-agent `"model"` field in `kilo.jsonc` then doubles the prefix as `openrouter/anthropic/claude-opus-4-7` — see the [Kilo Code setup page §5.2](./Kilo-Code-Setup.md#52-a-minimal-world-forge-agent-set) for the exact form and a known caching caveat on the OpenRouter → Anthropic path.

### 3.4 Context discipline on DeepSeek and GLM

DeepSeek 4 Pro (1M nominal context) and GLM 5 (200K nominal) are genuinely viable for this pipeline, and neither is window-starved on paper. Treat the discipline below as **quality-and-cost engineering, not a workaround for a hard ceiling**: on every current model — frontier included — effective recall and instruction adherence degrade well before the nominal limit, and the degradation hits exactly the content this pipeline depends on (hard-fail rules buried mid-spec, position tables, sign-off checklists). A Phase 5 run that naively loads the Prompt Engineer spec + the ST reference material + the Master Design + Export JSON puts ~100K tokens in front of the model before it writes a word; a 1M window *holds* that comfortably, but the audit it produces is sharper (and cheaper) when the load is a third of that. The repository ships the discipline — use it:

- **Per-phase custom agents** ([Kilo setup §5](./Kilo-Code-Setup.md#5-recommended-define-custom-agents-per-phase)) — strongly recommended on any model, for two independent reasons: persona isolation (the documented Editor-leniency drift when drafting context stays warm) and a clean window per phase. On GLM 5's 200K they also prevent genuine overflow on large worlds — multiple arcs plus intimacy in scope accumulates past 200K by Phase 3 when run inline. On DeepSeek's 1M, overflow is a non-issue; recall quality and cost are the reasons.
- **Keep the shipped `.kilocodeignore` intact.** It keeps `Samples/` (>1 MB) and maintenance docs out of auto-included context.
- **Honor the `📂 CONTEXT MANIFEST`** at the top of every agent spec. "Load on demand" means *do not preload*. The manifests exist precisely so the model never carries the full 67 KB `Notes_On_functionality.md` when the 5 KB `Notes_Quick_Reference.md` answers the question.
- **Spend your strongest model on the Editor and Auditor seats.** The known weak spot of DeepSeek/GLM-class models in this pipeline is not prose — it is *sycophancy under audit*: agreeing with the Architect's framing instead of hunting for failures. If you can afford one frontier seat, make it the Editor (Phase 3); the Auditors (3.5–3.7) are next. Drafting (Architect, Intimacy Architect) and the Interviewer tolerate DeepSeek/GLM well.
- **The Compiler is fine on DeepSeek/GLM** — they emit verbatim structured output reliably, unlike flash-tier models — but always run the read-only check `python tools/validate_export.py Export/` after Phase 4. It deterministically catches the silent failure modes (dropped `{{original}}` macros, encoding mojibake, out-of-range positions) that no model-side vigilance fully prevents.
- **Caching is a non-issue on DeepSeek.** DeepSeek's API applies automatic context caching to repeated prefixes, so the per-phase reload of a large agent spec is cheap by default — none of the OpenRouter→Anthropic `cache_control` round-trip anxiety documented in the [Kilo setup §3.2](./Kilo-Code-Setup.md#32-aggregators) applies.

A workable budget assignment, all through OpenRouter: DeepSeek 4 Pro (`deepseek/deepseek-v4-pro`) or GLM 5 (`z-ai/glm-5`) for Phases 0, 1, 2, 2.5, 4, and 5; the strongest model you can afford (frontier if possible, otherwise the larger reasoning variant of the same family) for Phases 3 and 3.5–3.7.

### 3.5 Sampling temperature by phase

> **Scope note — two unrelated temperatures.** This section is about the temperature of the **pipeline-running agents** in your agentic tool's API settings. It has nothing to do with the `temperature` field inside the Chat Completion Preset that the Prompt Engineer authors — that one governs the *roleplay model at runtime* in SillyTavern and is set by the pipeline itself.

The pipeline's phases split cleanly into prose seats (where sampling variety is the point), judgment seats (where the same input should produce the same verdict), and transcription seats (where creativity is a bug). One temperature for all of them leaves quality on the table at both ends:

| Phase | Seat | Temperature | Why |
|---|---|---|---|
| 0 | Interviewer | 0.7–0.9 | Creative partnership — varied, probing questions; a cold Interviewer asks the template instead of following threads. |
| 1 | Refiner | 0.3–0.5 | Tier classification and structure, not prose. Consistency over flair. |
| 2 / 2.5 | Architect, Intimacy Architect | 0.7–0.9 | The craft seats. Prose drafting wants the model's full sampling range. |
| 3 | Editor | 0.2–0.4 | Rule application. The same draft should fail the same checks on a re-run; a hot Editor is an inconsistent gate. |
| 3.5–3.7 | Auditors | 0.5–0.7 | A deliberate middle: auditors *generate* sample dialogue and scenes before judging them. Too cold and the simulation is flat, masking the failure modes they exist to catch; too hot and the verdicts get noisy. |
| 4 | Compiler | 0.0–0.2 | Verbatim transcription to JSON — literal macros, exact position values. Any creativity here is a defect. |
| 5 | Prompt Engineer | 0.2–0.4 | Runtime judgments plus structured JSON authoring. |
| R0 / C0 | Reviser, Converter | 0.4–0.6 | Classification plus interview — between the Refiner and the Interviewer. |

**Reasoning-model caveat:** reasoner-class endpoints (e.g. `deepseek/deepseek-r1`) generally ignore sampling parameters — temperature has no effect. The shipped `.kilo/kilo.jsonc` runs every seat — audit seats included — on chat-tuned DeepSeek 4 Pro with per-phase temperatures, so the table applies as-is. If you upgrade an audit seat to a reasoner, drop its `temperature` field; it would be silently ignored.

If maintaining four temperature bands is more fiddling than you want, collapse to two: a **creative** profile (~0.8) for Phases 0, 2, 2.5 and the auditors, and a **precise** profile (~0.2) for Phases 1, 3, 4, 5 — the Compiler and Editor are the two seats where getting this wrong costs the most. Kilo Code users: `temperature` is a per-agent field in `kilo.jsonc`, and the shipped World-Forge config already carries these values — see [Kilo setup §5.4](./Kilo-Code-Setup.md#54-per-phase-temperature).

---

## 4. Why Claude Code is a poor fit (currently)

[Claude Code](https://claude.com/claude-code) is Anthropic's official CLI agent. It is excellent at software engineering. It is **not** a good driver for this pipeline, for reasons unrelated to the underlying model.

The issues are at the agent-harness level, not the model level:

1. **System prompt orientation.** Claude Code's harness primes the model toward "software engineering tasks": bug fixing, refactoring, code review, dependency management. The pipeline's phases — especially the Architect, Editor, and Auditors — are *creative writing* tasks. The harness's "be concise, edit files, run tests, commit" framing actively works against the literary register the pipeline needs.

2. **Discouraged narration and comments.** Claude Code is tuned to write terse code without commentary. Phase 2 (Architect) and Phase 3 (Editor) produce drafts that *are* commentary — long prose, descriptive passages, tonal register notes. The harness frequently shortens or strips this content.

3. **Code-quality reflexes applied to prose.** When the Editor or Architect produces a long, deliberately dense character description, Claude Code's harness instincts (DRY, "remove redundant content," "extract to a helper") fire inappropriately. Prose redundancy is sometimes intentional (e.g., the [ARC_STATE two-subsection structure](../CLAUDE.md#5-arc_state-two-subsection-structure) repeats some content across the descriptive and directive subsections — this is load-bearing, not a bug).

4. **No native multi-persona mode.** Unlike Kilo Code's subagent delegation, Claude Code expects a single coherent task scope per session. Re-priming it with a different persona spec mid-run is awkward and the previous persona bleeds through.

5. **Tool surface is wrong for the job.** Claude Code's strengths (Bash execution, git integration, type checking, build tools) are unused here. Its weaknesses for this use case (terse output, code-style reflexes) are exposed every turn.

The *model* under Claude Code (Claude Opus / Sonnet) is in fact the best model for the pipeline. The issue is the harness. Run the same model through Kilo Code or Cline and the experience is materially different — the agent reads agent specs as creative-writing instructions rather than as engineering tickets, and the prose output matches the pipeline's register expectations.

> **Future note:** If a future Claude Code release supports custom personas or a "creative-writing" mode that swaps the orientation, this guidance would change. As of writing, it does not.

---

## 5. Other tools and IDEs (briefly)

These are not the recommended path but come up often enough to be worth a sentence each:

- **Cursor / Windsurf** — separate IDEs (VS Code forks), not extensions. They can run the pipeline, but their agent UX is optimized for in-editor coding rather than long agentic runs. Workable but not recommended over Kilo Code.
- **GitHub Copilot (Agent mode)** — the agent mode is improving but is currently weaker on long-context multi-file orchestration than Kilo Code or Cline.
- **Continue** — primarily a chat / inline-edit assistant, not an agentic orchestrator. Insufficient for the pipeline.
- **Aider** — CLI, not VS Code. Works if you prefer the terminal, but loses the workspace file tree affordance the pipeline assumes.
- **Antigravity** (Google) — early-stage agentic IDE platform. May be a future option as it matures.

---

## 6. Troubleshooting setup

| Symptom | Likely cause | Fix |
|---|---|---|
| Agent ignores `/worldforge start` and asks "what would you like to build?" | Tool didn't read `workflows/world-forge.md` — usually because the workspace root isn't this repo, or the file isn't visible. | Open this repo (or your world project containing it) as the VS Code workspace root. Confirm `workflows/world-forge.md` exists and is readable. |
| Agent jumps phases or skips auditors | Single-mode tool (e.g., Cline) lost the orchestrator instructions after a long Phase 2. | Re-prime with `/worldforge resume phase[N]`. Consider switching to Kilo Code's per-phase custom agents ([Kilo setup §5](./Kilo-Code-Setup.md#5-recommended-define-custom-agents-per-phase)) for longer worlds. |
| Voice is flat, generic, "AI-assistant" register | Wrong model tier or wrong tool harness. | Switch to Sonnet 4.6 or Opus 4.7. If already on those models via Claude Code, switch tools to Kilo Code or Cline. |
| Editor passes everything on round 1 | Model is being sycophantic (often a small or coding-tuned model). | Switch to a stronger creative model. Verify the Editor agent spec is being loaded. |
| Context-window errors in Phase 3+ | Model has insufficient context. | Use a 200K+ context model. Verify the tool isn't loading every file in the workspace by default (some tools auto-include too much). |
| Phase 4 JSON output is sparse, missing fields, or omits literal strings like `{{original}}` from `system_prompt` / `post_history_instructions` | Flash-tier or summarization-prone model used for the Compiler. Observed on **Gemini 3.1 Flash**. | Switch the Compiler (and ideally the Architect) to a Pro-tier or frontier-tier model. The Compiler must emit verbatim content; summarizing models silently drop macros and break the [Override Architecture](../CLAUDE.md#2-the-override-architecture-paired-contract). |

---

## 7. Summary

- **Tool:** Kilo Code is the reference (the repo ships its per-phase agent set in `.kilo/kilo.jsonc`). Cline is a valid simpler alternative. Roo Code is retired (May 15, 2026) — do not adopt it. Claude Code is not currently recommended.
- **Model:** Spend on Opus 4.7 / Sonnet 4.6 / GPT-5 / Gemini 2.5 Pro for creative phases. Use cheaper models for the Refiner, Compiler, and Prompt Engineer if you want to save cost.
- **Setup:** Open this repo as a VS Code workspace, configure your tool's model provider, switch to orchestrator mode if available, type `/worldforge start`.

If you discover a tool not listed here that works well, please open an issue or PR against this page.
