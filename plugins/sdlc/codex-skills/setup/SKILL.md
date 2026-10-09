---
name: setup
description: Create the product-document structure — in an Obsidian vault (recommended), or in the repository as `.sdlc/` — and register every code repository the product is built in, without overwriting existing files. Use when a user asks to set up or initialize the plugin documents, choose where the documents live, register a repository, migrate existing root documents, or invokes `$setup` as the Codex equivalent of `/setup`.
---

# Setup

Create the project document structure with the shared setup command.

## Run the command

1. Resolve `../../commands/setup.md` from this skill directory.
2. Read the command file completely before taking action.
3. Treat that command as the source of truth for file discovery, migration, and safeguards.
4. Replace `$ARGUMENTS` with the request text that follows the skill invocation.
5. Replace `${CLAUDE_PLUGIN_ROOT}` with the plugin root that contains this skill.
6. Read `../../skills/sdlc-structure/SKILL.md`, `../../skills/ticket-board/SKILL.md`, and `../../skills/feature/SKILL.md` before you create or migrate anything.
7. Use Codex file and user-input tools to perform the command.

Do not invoke a nested `/setup` command. Execute the shared instructions directly.

Codex has no `AskUserQuestion` tool. Ask the destination question from Step 1, the repository
question from Step 2, and every migration question from Step 3 — including the feature-migration
mapping table — in prose, and wait for each answer before you create or move anything.

A Codex session started in the docs root reaches a repository the way that runtime does — it has no
`--add-dir`. Say which repositories the registry names and which of them this session can write to,
so the user starts the next session in the right place.

In the final handoff, use these Codex skill names:

- `$sdlc:prd`
- `$sdlc:feature`
- `$sdlc:design-doc`
- `$sdlc:plan`
- `$sdlc:orchestrate`
