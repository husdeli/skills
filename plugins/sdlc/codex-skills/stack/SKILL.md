---
name: stack
description: Report a web repository's stack layer by layer against the default web stack, or with `install` propose the missing installs, ask which optional layers the project needs, and install them on the user's yes. Use when a user asks what stack a project uses or wants the stack installed, or invokes `$stack` as the Codex equivalent of `/stack`.
---

# Stack

Report the stack with the shared stack command.

## Run the command

1. Resolve `../../commands/stack.md` from this skill directory.
2. Read the command file completely before reading the repository.
3. Load the `web-stack` and `technical-writing` skills as the command requires.
4. Replace `$ARGUMENTS` with the request text that follows the skill invocation.
5. Replace `${CLAUDE_PLUGIN_ROOT}` with the plugin root that contains this skill.
6. Use Codex read-only tools to inspect the repository. In install mode, run the installs only after the user says yes.

Treat the shared command as the source of truth for target selection, the report, and the install mode.
