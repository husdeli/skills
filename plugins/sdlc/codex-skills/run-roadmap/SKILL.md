---
name: run-roadmap
description: Build the next roadmap task with no person in the loop — a CTO agent answers every question, the task is committed, and the run reports a machine-readable result. Use when a user asks for an autonomous or unattended roadmap run, or invokes `$run-roadmap` as the Codex equivalent of `/run-roadmap`.
---

# Run Roadmap

Run one roadmap task autonomously with the shared run-roadmap command.

## Load the workflow

1. Resolve `../../commands/run-roadmap.md` from this skill directory.
2. Read the command file completely before changing task status or creating subagents.
3. Replace `$ARGUMENTS` with the request text that follows the skill invocation.
4. Treat the shared command as the source of truth for the stages, the caps, the contracts, the
   commit, and the result line.
5. Read every skill the command's table names, from the plugin's `skills/<name>/SKILL.md` —
   `sdlc-structure`, `ticket-board`, `agent-pipeline`, and `technical-writing` — before the stage that
   needs each one.
6. Run the workflow with the subagent, file, and shell tools of the current runtime.

In a Codex session, also read [the Codex subagent protocol](../orchestrate/references/codex-subagents.md)
before you create a subagent. It names the Codex tool calls and runtime terms that stand in for the
Claude ones. It changes no gate and no cap.

## Invoking this skill is the approval

`$orchestrate` asks the user which task to build. **This skill does not.** Invoking it authorizes the
`cto` agent to pick the task, settle every open decision, and rule on every escalation, and it
authorizes the command to commit the finished task. That is what the user asked for.

So two rules of the subagent protocol are lifted here, and only here:

- **Never ask the user anything** — no user-input tool, and no turn that ends waiting for an answer.
  Every question goes to the `cto` agent, spawned from `agents/cto.md` as task name `cto`, resumed
  with `followup_task` for every later question in the run.
- **The CTO chooses on the user's behalf**, including the task and the end-to-end call. The command
  records each answer in the ticket and the worklog, which is what makes an unattended run readable
  afterwards.

Everything else the protocol says still holds: one `json` block per agent turn, one spawn per role,
a fresh verification agent per run, and the command as the only writer of the status, the assignee,
the worklog, and the roadmap.

## One task, then stop

One invocation is one task, whatever the runtime. Print the command's `RUN-ROADMAP-RESULT` line as
the last line of the final message, and stop.

The unattended loop over a whole roadmap is a Claude Code script —
[`scripts/run-roadmap.sh`](../../scripts/run-roadmap.sh), which calls
`claude -p "/sdlc:run-roadmap"` once per task, from a repository or from the docs root that drives
several. Codex has no equivalent launcher in this plugin: in a Codex session, invoke `$run-roadmap`
again for the next task.

**A run started in the docs root** builds each task in the repository the command resolves — the
work root. Codex has no `--add-dir`: the session reaches a repository the way that runtime does, so
check you can write to the work root before Stage 2, and stop with outcome `blocked` when you
cannot.
