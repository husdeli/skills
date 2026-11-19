---
name: agent-pipeline
description: "Defines how a command drives subagents: spawn each role once and resume it, run independent calls together, and act on each agent's closing JSON block. Use before spawning, resuming, re-reviewing, or judging a subagent from a command."
---

# agent-pipeline

The rules live in one shared skill. This entry point points at it.

Read `../../skills/agent-pipeline/SKILL.md` completely before you create a subagent, and follow every rule in it.

In a Codex session, read [the Codex subagent protocol](../orchestrate/references/codex-subagents.md) alongside it. That file names the Codex tool calls and runtime terms that stand in for the Claude ones — `Agent`, `SendMessage`, and the tool block that makes two calls concurrent. It changes no outcome.
