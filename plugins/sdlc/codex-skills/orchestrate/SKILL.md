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
5. Read every skill the command's table names, from the plugin's `skills/<name>/SKILL.md` — `product-docs`, `ticket-board`, `agent-pipeline`, and `technical-writing` — before the stage that needs each one.
6. Run the workflow with the subagent, file, and user-input tools of the current runtime.

In a Codex session, also read [the Codex subagent protocol](references/codex-subagents.md) before you create a subagent. It names the Codex tool calls and runtime terms that stand in for the Claude ones. It changes no gate and no retry limit.

## Required roadmap approval

Invoking this skill with a roadmap authorizes task selection only. It does not approve the selected task.

After selecting the next task:

1. Present the candidates in the shared command's `Candidate Tasks` format.
2. Ask the shared command's two Step 2 questions in prose — which task to build, and whether to add end-to-end tests — because a Codex session has no `AskUserQuestion` tool. State your recommendation for each.
3. End the turn and wait for the user's explicit answers.
4. Do not edit status, create subagents, or start work in that turn.
5. Continue the workflow only after a later user message picks a task, and carry the end-to-end answer forward as the `e2eDecision`.
