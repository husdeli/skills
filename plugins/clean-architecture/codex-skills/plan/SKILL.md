---
name: plan
description: Turn a feature request into an updated PRD and design doc, new roadmap tasks, and one ticket per task, after an interview settles the open decisions. Use when a request needs product documents and work items before any code, or when a user invokes `$plan` as the Codex equivalent of `/plan`.
---

# Plan

Turn the request into product documents and work items with the shared plan command.

## Run the command

1. Resolve `../../commands/plan.md` from this skill directory.
2. Read the command file completely before you create a subagent or write a document.
3. Replace `$ARGUMENTS` with the request text that follows the skill invocation.
4. Create the feature interviewer with the subagent tool of the current runtime, and read every skill the command names — `clean-writing`, `prd`, `design-doc`, and `ai-planning-workflow` — from the plugin's `skills/<name>/SKILL.md` before you write the document each one governs.

Treat the shared command as the source of truth for the stages, the approval gate, the document rules, and the report.

In a Codex session, also read [the Codex subagent protocol](../orchestrate/references/codex-subagents.md) before you create the interviewer. It names the Codex tool calls and runtime terms that stand in for the Claude ones. It changes nothing the command writes, and nothing about when it stops.

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
