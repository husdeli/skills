---
name: orchestrate-quick
description: Drive one well-scoped task through planning, one review, implementation, and verification with persistent Codex subagents. Use for a clear ticket, fix, or task without open product or architecture decisions, or when a user invokes `$orchestrate-quick` as the Codex equivalent of `/orchestrate-quick`.
---

# Orchestrate Quick

Run the short reviewed workflow with the shared quick-orchestrate command.

## Load the workflow

1. Resolve `../../commands/orchestrate-quick.md` from this skill directory.
2. Read the command file completely before changing task status or creating subagents.
3. Read [the Codex subagent protocol](../orchestrate/references/codex-subagents.md) completely.
4. Replace `$ARGUMENTS` with the request text that follows the skill invocation.
5. Treat the shared command as the source of truth for stages, limits, contracts, and status changes.
6. Treat the Codex protocol as the source of truth for tool calls and runtime terms.

The Codex protocol overrides Claude-only tool syntax. It does not change the workflow's gates or retry limits.
