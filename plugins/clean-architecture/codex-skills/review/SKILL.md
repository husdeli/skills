---
name: review
description: Review code that was already written — the working tree, a branch, a ticket, or named files — with the code-reviewer subagent, and report APPROVED or CHANGES_REQUESTED. Use for a change that never went through an orchestrated verify stage, or when a user invokes `$review` as the Codex equivalent of `/review`.
---

# Review

Review the requested code with the shared review command.

## Run the command

1. Resolve `../../commands/review.md` from this skill directory.
2. Read the command file completely before you create a subagent.
3. Replace `$ARGUMENTS` with the request text that follows the skill invocation.
4. Create the code-reviewer subagent with the subagent tool of the current runtime, and load the `clean-writing` skill for the report.

Treat the shared command as the source of truth for target selection, the spawn prompt, the fix cap, and the report.

In a Codex session, also read [the Codex subagent protocol](../orchestrate/references/codex-subagents.md) before you create the subagent. It names the Codex tool calls and runtime terms that stand in for the Claude ones. It changes nothing about what the code reviewer is asked to do.

Do not invoke a nested `/review` command. Execute the shared instructions directly.

## Never fix without an explicit ask

Invoking this skill authorizes a review only. Create the coding subagent only when the invocation ends with `fix`, or a later user message asks for the fix.
