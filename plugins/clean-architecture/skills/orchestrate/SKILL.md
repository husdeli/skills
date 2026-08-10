---
name: orchestrate
description: Pick one actionable roadmap task and drive it through discovery, planning, review, implementation, verification, and status updates with persistent Codex subagents. Use for roadmap work with open product, user experience, dependency, public API, or architecture decisions, or when a user invokes `$orchestrate` as the Codex equivalent of `/orchestrate`.
---

# Orchestrate

Run the full reviewed workflow with the shared orchestrate command.

## Load the workflow

1. Resolve `../../commands/orchestrate.md` from this skill directory.
2. Read the command file completely before changing task status or creating subagents.
3. Read [the Codex subagent protocol](references/codex-subagents.md) completely.
4. Replace `$ARGUMENTS` with the request text that follows the skill invocation.
5. Treat the shared command as the source of truth for stages, limits, contracts, and status changes.
6. Treat the Codex protocol as the source of truth for tool calls and runtime terms.

The Codex protocol overrides Claude-only tool syntax. It does not change the workflow's gates or retry limits.

## Required roadmap approval

Invoking this skill with a roadmap authorizes task selection only. It does not approve the selected task.

After selecting the next task:

1. Present the task in the shared command's `Next Task` format.
2. End the turn and wait for the user's explicit approval.
3. Do not edit status, create subagents, or start work in that turn.
4. Continue the workflow only after a later user message approves that task.
