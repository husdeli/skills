---
name: orchestrate-quick
description: "Drives one task through plan, one review, test plan, tests, implementation, verification, and code review, with no interview and no gates. Use for a clear, well-scoped ticket, fix, or task."
---

# Orchestrate Quick

Run the short reviewed workflow with the shared quick-orchestrate command.

## Load the workflow

1. Resolve `../../commands/orchestrate-quick.md` from this skill directory.
2. Read the command file completely before changing task status or creating subagents.
3. Replace `$ARGUMENTS` with the request text that follows the skill invocation, and `${CLAUDE_PLUGIN_ROOT}` with the plugin root that contains this skill.
4. Treat the shared command as the source of truth for stages, gates, contracts, and status changes.
5. Read `skills/agent-pipeline/references/command-preamble.md`, then every skill its table names, from the plugin's `skills/<name>/SKILL.md` — `sdlc-structure`, `ticket-board`, `agent-pipeline`, and `technical-writing` — before the stage that needs each one, and `skills/agent-pipeline/references/build-stages.md` whole before Plan. This command runs its quick mode.
6. Run the workflow with the subagent, file, and user-input tools of the current runtime.

In a Codex session, also read [the Codex subagent protocol](../orchestrate/references/codex-subagents.md) before you create a subagent. It names the Codex tool calls and runtime terms that stand in for the Claude ones. It changes no gate and no retry limit.
