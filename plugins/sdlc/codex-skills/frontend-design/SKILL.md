---
name: frontend-design
description: Agree the visual design of a user interface with the user before any UI code is written, by building a static mockup and iterating on it. Use when asked to design a screen, a component, or a flow, or before implementing a request that changes what a user sees.
---

# frontend-design

The rules live in one shared skill. This entry point points at it.

Read `../../skills/frontend-design/SKILL.md` completely before you draw anything, and follow every rule in it.
Read every reference that file requires, and resolve each path against `../../skills/frontend-design/`.

## Running it outside Claude Code

The shared skill publishes the mockup with the `Artifact` tool, which a Codex session does not have. Everything else in it applies unchanged.

Instead of publishing:

1. Write the same static HTML file into the project's temporary or scratch directory, not into the source tree.
2. Give the user the file path and ask them to open it in a browser.
3. Overwrite that same file on each round, so the user reloads one tab.
4. Record the agreed decisions in `<docs root>/designs/<subject>.design.md`, since there is no artifact URL to record.

Skip the `artifact-design` and `dataviz` skills when the runtime does not have them, and follow the shared skill's own visual direction rules.
