---
name: agent-pipeline
description: "Rules for driving subagents from a command — spawn each role once and resume it with SendMessage, issue concurrent spawns in one tool block, parse the single fenced JSON block every agent ends with, retry a missing block once before calling the run aborted, and keep the spawn prompt thin because it is re-paid on every spawn. INVOKE THIS SKILL before you spawn a subagent from a command, and before you resume, re-review, or judge one's result. Enforces one spawn per role, no duplicated gating run, and one outcome vocabulary."
---

# agent-pipeline skill

How a command drives subagents. The stages, the gates, and the retry caps belong to each command;
this skill holds the mechanics every one of them shares.

## Spawn once, resume with SendMessage

An agent that runs inside a loop — a planner that revises, a reviewer that re-reviews, a coding
agent that fixes — is spawned **once**. Keep the id or name the `Agent` call returns, and resume
that same agent with `SendMessage` for every later turn.

**Send only what changed.** The agent still holds the plan, the files it read, the context pack,
and its own reasoning; that context is the dominant token cost of the run, and re-spawning throws
it away. Send the planner the review issues alone, the reviewer "re-review the revised plan" with
the plan, the coding agent the failures alone.

**Never re-spawn a role to give it new information**, and never finish an agent's work yourself in
the main loop.

## Verification is the exception

Spawn a **fresh** verification agent for every run. It is cheap, and a clean re-run with no memory
of the previous attempt is exactly what you want from a gate: a suite that was green before the fix
proves nothing about the code after it. On a re-run, name the previously failing commands so it
runs those first and fails fast.

## Concurrent calls go in one tool block

Two agents that do not need each other's answer run at the same time — **or they are not
concurrent at all**. Issue both `Agent` calls, or both `SendMessage` calls, in a single tool block.
Two calls in two blocks are two waits.

A pre-read or a scout turn that later gets discarded costs tokens, never wall-clock. Take that
trade: start the read while the thing it reads about is still being written.

## Every agent ends with one JSON block

Each agent ends its reply with exactly **one** fenced ` ```json ` block, in the contract its own
agent definition specifies. Parse it and drive control flow from it. There is no schema
enforcement and no background workflow — the block is the interface.

**The contract lives in the agent definition. Do not restate it in a spawn prompt.** A scout, pre-read, or spec-only turn emits no block when its agent definition says none is due; do not ask for one.

When a block is missing or malformed, `SendMessage` the agent **once**, asking it to re-emit *only*
the JSON block. A second failure is an `aborted` run.

## Keep the spawn prompt thin

Durable agent behavior — the skills it loads, the conventions it follows, its output contract —
belongs in the agent definition, where it is written once. A spawn prompt is re-paid on **every**
spawn, so it carries only what this run's agent cannot already know: the task, the criteria, the
context pack, the decisions, and what changed since its last turn.

**The work root is one of those things.** Every agent that reads code, writes code, or runs a
command gets the repository it works in as an absolute path, in its first message. A subagent
inherits the session's working directory, which in a run started from an Obsidian vault holds the
documents and not the code — an agent left to assume would read the wrong tree and report a clean
result from it. `sdlc-structure` holds how the work root is resolved; resolving it is the command's
job, once, before the first spawn.

## Tests come before the code, from three different agents

The agent that decides what to test, the agent that writes the tests, and the agent that writes the
code are three different agents. A coder that writes its own tests, or edits them until they pass,
produces tests that describe its code rather than check it.

- **`test-planner` drafts from the specification first.** Spawn it in *spec only* mode at the same
  moment the planner gets the decisions, in the same tool block as the plan reviewer's pre-read.
  Send it the approved plan when the plan review closes. It is persistent: it also rules on every
  test dispute, and it keeps what it decided and why.
- **`test-writer` is persistent** too. A `revised` ruling goes back to the same agent. When an empty test plan meant it was never spawned, spawn it then, with the revised cases, the approved plan, and the context pack.
- **An empty test plan skips the test stages.** `cases == []` means no test is written and no
  targeted verify runs. Record the planner's reason; do not second-guess it.
- **Fingerprint every file `test-writer` changed**, the moment its block lands:
  `git -C <work root> hash-object <file>…`. Compare after every `coding` turn. A file whose
  fingerprint moved goes back to `coding` with "restore this test file exactly; dispute it instead
  of changing it", and that costs one targeted fix cycle. Take the fingerprints again after every
  `test-writer` turn, since a `revised` ruling changes them legitimately, and drop the ones for
  files it deleted.
- **A test dispute goes to `test-planner`, never straight to `test-writer`.** Forward the coding
  agent's `testDisputes` as they came, with the specification passages they cite. Then act on each
  ruling: `upheld` → `coding` gets the reason; `revised` → `test-writer` changes the test, then
  `coding` gets the change; `escalate` → the run's escalation. When one round holds both kinds, run
  the `test-writer` turn first, then send `coding` one message with every ruling.

## Never duplicate the gating run

- The **coding agent self-checks** what it touched, and nothing more.
- The **test writer runs only the tests it wrote**, to prove each one fails before the code exists.
- The **targeted verification** runs only the written tests and the existing tests of the changed
  files. It is a fast gate before the full one, not a second full run.
- The **verification agent** runs the project's gating commands, concurrently, once per cycle. It
  is the authoritative gate.
- The **code reviewer never runs the suite.** It answers a different question about the same
  change, and it runs beside verification rather than after it.

Asking two agents to run the same suite doubles the slowest block on the critical path for no added
signal.

## The outcome vocabulary

Every pipeline ends in exactly one of three states. Use these words, and mean only these things:

| Outcome | What happened | What it does to the ticket |
| --- | --- | --- |
| `completed` | Every gate passed — the commands passed **and** the review returned `APPROVED`. | Finish the ticket. |
| `escalate` | A stage hit its retry cap, an agent reported a blocker it cannot pass, or the test planner ruled that a dispute turns on what the specification means. | Stop without finishing: the ticket becomes `blocked`, with one `blocked_by` line naming what a person must decide. |
| `aborted` | An agent returned no usable result — it died, or produced no valid JSON block after one retry. | Stop without finishing: the ticket becomes `blocked`, with one `blocked_by` line naming the stage and the agent that went silent. |

**Apply each cap mechanically.** A revision cap of one means one, and a fix cap of one covers every
defect found in that cycle together — verification failures and blocking review issues in a single
message, not one message each. Do not improvise an extra cycle because the next one looks close.

**Never report a skipped command as green**, and never mark work complete on a passing suite alone
when a review is part of the gate.

The `ticket-board` skill holds what each outcome writes to the ticket — its `status`, `assigned`,
`claimed`, `blocked_by`, and usage — to the roadmap, and to the worklog.
