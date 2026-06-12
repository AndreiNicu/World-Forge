# Wiki staging

This directory holds markdown source for pages that belong on the project's GitHub Wiki. GitHub wikis are stored in a separate `.wiki` git repository and do not accept pull requests through GitHub's normal PR flow, so wiki content is drafted here in the main repo (where it is reviewable) and then copy-pasted into the wiki after merge.

## Current pages

- [`Agentic-Tools-and-Models.md`](./Agentic-Tools-and-Models.md) — Which agentic VS Code extensions can drive the pipeline (Kilo Code, Cline — plus a migration note on the retired Roo Code), why Claude Code is not currently recommended, and which underlying LLMs perform well in which phases.
- [`Kilo-Code-Setup.md`](./Kilo-Code-Setup.md) — Dedicated step-by-step setup tutorial for users who want to drive the pipeline with Kilo Code. Covers install, provider configuration, per-phase custom agents, and Kilo-specific troubleshooting.

## Publishing a page to the wiki

1. Review and merge the PR introducing the page here.
2. Open the project's GitHub Wiki tab.
3. Create a new page with the same name as the file (minus `.md`).
4. Paste the contents.
5. Adjust any relative links (`../README.md`, `../CLAUDE.md`) to absolute GitHub URLs as needed for the wiki context.
