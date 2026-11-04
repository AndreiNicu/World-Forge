# Kilo_Variants

Drop-in alternates for the shipped `.kilo/kilo.jsonc` — same 24 World-Forge agents (including `WorldForge-Orchestrator`) and the **identical per-agent `permission` blocks** (`wiki/Kilo-Code-Setup.md` §5.5), different model (or provider) on every seat:

| File | Model (all seats) | Temperatures | Reasoning | Routing pin |
|---|---|---|---|---|
| `kilo.glm-5.2.jsonc` | `openrouter/z-ai/glm-5.2` | none (reasoner — ignores sampling) | effort high | `only: ["Z.AI"]` (hard pin, no fallback) |
| `kilo.kimi-k2.5.jsonc` | `openrouter/moonshotai/kimi-k2.5` | per-phase values kept (chat-tuned) | n/a | `order: ["Moonshot AI"]` (fallbacks allowed) |
| `kilo.nano-gpt.jsonc` | `nano-gpt/deepseek/deepseek-v4-pro-0813` (Nano-GPT instead of OpenRouter); the Orchestrator on `deepseek/deepseek-v4-flash-latest`, as in the shipped config | per-phase values kept | n/a | none by default (keeps a Nano-GPT subscription in effect); `X-Provider` header / body `provider` pin to `deepseek` shipped commented out — pay-as-you-go only |

The GLM and Kimi variants differ in shape because the models differ in kind: GLM 5.2 is reasoning-class, so its variant strips every `temperature` field and controls depth via the per-model `reasoning: { "effort": "high" }` routing option; Kimi K2.5 is the general-line chat-tuned Kimi, so its variant keeps the shipped per-phase temperature table (`wiki/Agentic-Tools-and-Models.md` §3.5) exactly as the DeepSeek config does. The Nano-GPT variant keeps the shipped model family and temperatures and changes only the provider: it pins the dated V4 Pro GA slug because Nano-GPT's `deepseek/deepseek-latest` alias routes to the Thinking variant and never to DeepSeek directly (`wiki/Kilo-Code-Setup.md` §3.2, Nano-GPT items 5–6). Activating it needs a Nano-GPT key in Kilo's global provider settings.

**To use one:** back up `.kilo/kilo.jsonc`, copy the variant over it (keeping the name `kilo.jsonc`), reload VS Code, and confirm the `WorldForge-*` agents appear in the agent picker. Kilo does **not** load anything from this folder directly, and the `{file:...}` prompt paths inside the variants only resolve from the `.kilo/` location.

On any variant, watch the Editor's round 1 for sycophancy — the known weak spot of budget-class models under audit — and run `python tools/validate_export.py Export/` after every Phase 4 compile.

To mix models per seat instead of switching wholesale, stay on the shipped `.kilo/kilo.jsonc` — its `agent` section opens with a per-seat swap guide.
