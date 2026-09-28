---
name: setup
description: Create the product-document structure — in an Obsidian vault (recommended), or in the repository as `.sdlc/` — without overwriting existing files. Use when a user asks to set up or initialize the plugin documents, choose where the documents live, migrate existing root documents, or invokes `$setup` as the Codex equivalent of `/setup`.
---

# Setup

Create the project document structure with the shared setup command.

## Run the command

1. Resolve `../../commands/setup.md` from this skill directory.
2. Read the command file completely before taking action.
3. Treat that command as the source of truth for file discovery, migration, and safeguards.
4. Replace `$ARGUMENTS` with the request text that follows the skill invocation.
5. Replace `${CLAUDE_PLUGIN_ROOT}` with the plugin root that contains this skill.
6. Read `../../skills/product-docs/SKILL.md` and `../../skills/ticket-board/SKILL.md` before you create or migrate anything.
7. Use Codex file and user-input tools to perform the command.

Do not invoke a nested `/setup` command. Execute the shared instructions directly.

Codex has no `AskUserQuestion` tool. Ask the destination question from Step 1 in prose, and wait
for the answer before you create anything.

In the final handoff, use these Codex skill names:

- `$sdlc:prd`
- `$sdlc:design-doc`
- `$sdlc:plan`
- `$sdlc:orchestrate`
