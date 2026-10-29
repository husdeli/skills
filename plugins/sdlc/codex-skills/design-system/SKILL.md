---
name: design-system
description: Rules for the project's design system — tokens in one place (ideally DTCG JSON built by Style Dictionary), shared components listed in a `design-system.md` catalog, and a Storybook design board separate from the app. Use before planning, building, mocking up, or reviewing UI, before changing a shared component, a design value, a theme, or a token file, and before setting up the board. Also runs the design-system report, or with `board` generates the design board, when a user invokes `$design-system` as the Codex equivalent of `/design-system`. Builds on the `web-stack` skill; follow that one too.
---

# design-system

The rules live in one shared skill. This entry point points at it.

Read `../../skills/design-system/SKILL.md` completely before you plan, build, mock up, or review anything a user sees in a web project, and follow every rule in it. Read the references it names, resolved against `../../skills/design-system/`, when the work touches tokens or the design board.

## Running the command

When the user invokes `$design-system`, with or without `board`:

1. Resolve `../../commands/design-system.md` from this skill directory, and read it completely before reading the repository.
2. Replace `$ARGUMENTS` with the request text that follows the skill invocation.
3. Load the skills the command names from the plugin's `skills/<name>/SKILL.md`.
4. In board mode, read [the Codex subagent protocol](../orchestrate/references/codex-subagents.md) before you create the coding subagent.

Treat the shared command as the source of truth for the report, the board brief, and what is never done — the board is never deployed from it.
