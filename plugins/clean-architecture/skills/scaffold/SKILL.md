---
name: scaffold
description: Create the `.clean-architecture/` product-document structure without overwriting existing files. Use when a user asks to scaffold or initialize the plugin documents, migrate existing root documents, or invokes `$scaffold` as the Codex equivalent of `/scaffold`.
---

# Scaffold

Create the project document structure with the shared scaffold command.

## Run the command

1. Resolve `../../commands/scaffold.md` from this skill directory.
2. Read the command file completely before taking action.
3. Treat that command as the source of truth for file discovery, migration, and safeguards.
4. Replace `$ARGUMENTS` with the request text that follows the skill invocation.
5. Replace `${CLAUDE_PLUGIN_ROOT}` with the plugin root that contains this skill.
6. Use Codex file and user-input tools to perform the command.

Do not invoke a nested `/scaffold` command. Execute the shared instructions directly.

In the final handoff, use these Codex skill names:

- `$clean-architecture:prd`
- `$clean-architecture:design-doc`
- `$clean-architecture:orchestrate`
