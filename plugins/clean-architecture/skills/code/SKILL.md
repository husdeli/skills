---
name: code
description: Implement a requested change with the coding subagent, which loads the architecture, TypeScript, React, and TanStack Start rules itself. Use for a fix, a small feature, or an addition that follows an existing pattern, or when a user invokes `$code` as the Codex equivalent of `/code`.
---

# Code

Implement the request with the shared code command.

## Run the command

1. Resolve `../../commands/code.md` from this skill directory.
2. Read the command file completely before you create a subagent.
3. Read [the Codex subagent protocol](../orchestrate/references/codex-subagents.md) completely.
4. Replace `$ARGUMENTS` with the request text that follows the skill invocation.
5. Create the coding subagent as the protocol describes, and load the `clean-writing` skill for the report.

Treat the shared command as the source of truth for scope, the spawn prompt, the follow-up cap, and the report. Treat the Codex protocol as the source of truth for tool calls and runtime terms.

The Codex protocol overrides Claude-only tool syntax. It does not change what the command asks the coding subagent to do.

Do not invoke a nested `/code` command. Execute the shared instructions directly.

Use these Codex skill names when the request outgrows this command:

- `$clean-architecture:orchestrate-quick`
- `$clean-architecture:orchestrate`
