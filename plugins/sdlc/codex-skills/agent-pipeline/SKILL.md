---
name: agent-pipeline
description: Rules for driving subagents from a command — create each role once and continue it rather than recreating it, run independent calls together, parse the single JSON block every agent ends with, retry a missing block once before calling the run aborted, and keep the spawn prompt thin. Use before creating a subagent from a command, and before continuing, re-reviewing, or judging one's result.
---

# agent-pipeline

The rules live in one shared skill. This entry point points at it.

Read `../../skills/agent-pipeline/SKILL.md` completely before you create a subagent, and follow every rule in it.

In a Codex session, read [the Codex subagent protocol](../orchestrate/references/codex-subagents.md) alongside it. That file names the Codex tool calls and runtime terms that stand in for the Claude ones — `Agent`, `SendMessage`, and the tool block that makes two calls concurrent. It changes no cap and no outcome.
