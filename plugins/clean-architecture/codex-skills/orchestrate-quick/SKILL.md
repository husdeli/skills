---
name: orchestrate-quick
description: Drive one well-scoped task through planning, one review, implementation, and verification with persistent subagents. Use for a clear ticket, fix, or task without open product or architecture decisions, or when a user invokes `$orchestrate-quick` as the Codex equivalent of `/orchestrate-quick`.
---

# Orchestrate Quick

Run the short reviewed workflow with the shared quick-orchestrate command.

## Load the workflow

1. Resolve `../../commands/orchestrate-quick.md` from this skill directory.
2. Read the command file completely before changing task status or creating subagents.
3. Replace `$ARGUMENTS` with the request text that follows the skill invocation.
4. Treat the shared command as the source of truth for stages, limits, contracts, and status changes.
5. Run the workflow with the subagent, file, and user-input tools of the current runtime.

In a Codex session, also read [the Codex subagent protocol](../orchestrate/references/codex-subagents.md) before you create a subagent. It names the Codex tool calls and runtime terms that stand in for the Claude ones. It changes no gate and no retry limit.
