---
name: orchestrate
description: Pick one actionable roadmap task and drive it through discovery, planning, review, implementation, verification, and status updates with persistent subagents. Use for roadmap work with open product, user experience, dependency, public API, or architecture decisions, or when a user invokes `$orchestrate` as the Codex equivalent of `/orchestrate`.
---

# Orchestrate

Run the full reviewed workflow with the shared orchestrate command.

## Load the workflow

1. Resolve `../../commands/orchestrate.md` from this skill directory.
2. Read the command file completely before changing task status or creating subagents.
3. Replace `$ARGUMENTS` with the request text that follows the skill invocation.
4. Treat the shared command as the source of truth for stages, limits, contracts, and status changes.
5. Run the workflow with the subagent, file, and user-input tools of the current runtime.

In a Codex session, also read [the Codex subagent protocol](references/codex-subagents.md) before you create a subagent. It names the Codex tool calls and runtime terms that stand in for the Claude ones. It changes no gate and no retry limit.

## Required roadmap approval

Invoking this skill with a roadmap authorizes task selection only. It does not approve the selected task.

After selecting the next task:

1. Present the task in the shared command's `Next Task` format.
2. End the turn and wait for the user's explicit approval.
3. Do not edit status, create subagents, or start work in that turn.
4. Continue the workflow only after a later user message approves that task.
