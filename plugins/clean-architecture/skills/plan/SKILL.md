---
name: plan
description: Turn a feature request into an updated PRD and design doc, new roadmap tasks, and one ticket per task, after an interview settles the open decisions. Use when a request needs product documents and work items before any code, or when a user invokes `$plan` as the Codex equivalent of `/plan`.
---

# Plan

Turn the request into product documents and work items with the shared plan command.

## Run the command

1. Resolve `../../commands/plan.md` from this skill directory.
2. Read the command file completely before you create a subagent or write a document.
3. Read [the Codex subagent protocol](../orchestrate/references/codex-subagents.md) completely.
4. Replace `$ARGUMENTS` with the request text that follows the skill invocation.
5. Create the feature interviewer as the protocol describes, and read every skill the command names — `clean-writing`, `prd`, `design-doc`, and `ai-planning-workflow` — from `<PLUGIN_ROOT>/skills/<name>/SKILL.md` before you write the document each one governs.

Treat the shared command as the source of truth for the stages, the approval gate, the document rules, and the report. Treat the Codex protocol as the source of truth for tool calls and runtime terms.

The Codex protocol overrides Claude-only tool syntax. It does not change what the command writes or when it stops.

## Required breakdown approval

Invoking this skill with a request authorizes the interview only. It does not approve the task breakdown.

After the interview settles the open decisions:

1. Present the change proposal in the shared command's `Plan` format.
2. End the turn and wait for the user's explicit approval.
3. Do not write the PRD, the design doc, the roadmap, or any ticket in that turn.
4. Continue only after a later user message approves the breakdown.

Do not invoke a nested `/plan` command. Execute the shared instructions directly.

Use these Codex skill names in the handoffs:

- `$clean-architecture:scaffold`
- `$clean-architecture:code`
- `$clean-architecture:orchestrate`
