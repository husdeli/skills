---
name: code
description: Implement a requested change with the coding subagent, which loads the architecture, TypeScript, React, and TanStack Start rules itself. Use for a fix, a small feature, or an addition that follows an existing pattern, or when a user invokes `$code` as the Codex equivalent of `/code`.
---

# Code

Implement the request with the shared code command.

## Run the command

1. Resolve `../../commands/code.md` from this skill directory.
2. Read the command file completely before you create a subagent.
3. Replace `$ARGUMENTS` with the request text that follows the skill invocation.
4. Create the coding subagent with the subagent tool of the current runtime, and load the `clean-writing` skill for the report.

Treat the shared command as the source of truth for scope, the spawn prompt, the follow-up cap, and the report.

In a Codex session, also read [the Codex subagent protocol](../orchestrate/references/codex-subagents.md) before you create the subagent. It names the Codex tool calls and runtime terms that stand in for the Claude ones. It changes nothing about what the coding subagent is asked to do.

Do not invoke a nested `/code` command. Execute the shared instructions directly.

Use these Codex skill names when the request outgrows this command:

- `$clean-architecture:orchestrate-quick`
- `$clean-architecture:orchestrate`
