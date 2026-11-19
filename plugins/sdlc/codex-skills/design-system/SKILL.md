---
name: design-system
description: "Reports how complete a web project's design system is (catalog, tokens, components, stories), or with `board` generates the Storybook design board. Use when the user asks to audit the design system or build its board."
---

# design-system

Report the design system, or generate its board, with the shared design-system command.

## Running the command

When the user invokes `$design-system`, with or without `board`:

1. Resolve `../../commands/design-system.md` from this skill directory, and read it completely before reading the repository.
2. Replace `$ARGUMENTS` with the request text that follows the skill invocation.
3. Load the skills the command names from the plugin's `skills/<name>/SKILL.md` — the design-system rules are `../../skills/design-system-rules/SKILL.md`.
4. In board mode, read [the Codex subagent protocol](../orchestrate/references/codex-subagents.md) before you create the coding subagent.

Treat the shared command as the source of truth for the report, the board brief, and what is never done — the board is never deployed from it.
