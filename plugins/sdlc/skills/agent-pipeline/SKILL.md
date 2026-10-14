---
name: agent-pipeline
description: "Rules for driving subagents from a command — spawn each role once and resume it with SendMessage, issue concurrent spawns in one tool block, parse the single fenced JSON block every agent ends with, retry a missing block once before calling the run aborted, and keep the spawn prompt thin because it is re-paid on every spawn. INVOKE THIS SKILL before you spawn a subagent from a command, and before you resume, re-review, or judge one's result. Enforces one spawn per role, no duplicated gating run, and one outcome vocabulary."
---

# agent-pipeline skill

How a command drives subagents. The stages, the gates, and the retry caps belong to each command;
this skill holds the mechanics every one of them shares.

## Spawn once, resume with SendMessage

An agent that runs inside a loop — a planner that revises, a reviewer that re-reviews, a coding
agent that fixes — is spawned **once**. Two agents of one type with different jobs are two roles:
each code-review focus is spawned once, and a re-review resumes the reviewer that blocked. Keep the id or name the `Agent` call returns, and resume
that same agent with `SendMessage` for every later turn.

**Send only what changed.** The agent still holds the plan, the files it read, the context pack,
and its own reasoning; that context is the dominant token cost of the run, and re-spawning throws
it away. Send the planner the review issues alone, the reviewer "re-review the revised plan" with
the plan, the coding agent the failures alone.

**Never re-spawn a role to give it new information**, and never finish an agent's work yourself in
the main loop.

## The orchestrator runs every check

**A check is a command, not a judgment.** The orchestrator runs every test and every project check
itself, with Bash, in the work root, and reads the exit code and the output. No agent reports a
check as passed: an agent's account of a run it made is a guide to its own work, never the gate.

- **A check passes when its command exits zero.** Read the output for which test or which rule
  failed, and send those lines on to whoever fixes it.
- **Independent checks go out as parallel Bash calls in one tool block**, so the slowest one sets
  the wall-clock.
- **After a fix, run the failed checks first**, and the rest only when they pass. A suite that was
  green before the fix still runs again: it proves nothing about the code after it.
- **A check the project lacks is skipped, never passed.** Name it, and the reason, in the report.

**`/orchestrate-quick` is the one exception.** It hands its checks to a fresh `verify` agent per
run instead of running them itself, and every rule above holds for that agent's report: exit code
zero passes, the failed checks run first after a fix, and a missing check is skipped.

## Concurrent calls go in one tool block

Two agents that do not need each other's answer run at the same time — **or they are not
concurrent at all**. Issue both `Agent` calls, or both `SendMessage` calls, in a single tool block.
Two calls in two blocks are two waits.

A pre-read or a spec-only turn that later gets discarded costs tokens, never wall-clock. Take that
trade: start the read while the thing it reads about is still being written.

## Every agent ends with one JSON block

Each agent ends its reply with exactly **one** fenced ` ```json ` block, in the contract its own
agent definition specifies. Parse it and drive control flow from it. There is no schema
enforcement and no background workflow — the block is the interface.

**The contract lives in the agent definition. Do not restate it in a spawn prompt.** A pre-read or spec-only turn emits no block when its agent definition says none is due; do not ask for one.

When a block is missing or malformed, `SendMessage` the agent **once**, asking it to re-emit *only*
the JSON block. A second failure is an `aborted` run.

## Keep the spawn prompt thin

Durable agent behavior — the skills it loads, the conventions it follows, its output contract —
belongs in the agent definition, where it is written once. A spawn prompt is re-paid on **every**
spawn, so it carries only what this run's agent cannot already know: the task, the criteria, the
context pack, the answers to any open question, and what changed since its last turn.

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
  moment the planner starts, in the same tool block. Send it the plan and the context pack when the
  plan review approves, or when the risk gate skips the review. It is persistent: it also rules on
  every test dispute, and it keeps what it decided and why.
- **`test-writer` is persistent** too. A `revised` ruling goes back to the same agent. When an empty test plan meant it was never spawned, spawn it then, with the revised cases, the approved plan, and the context pack.
- **An empty test plan skips the test stages.** `cases == []` means no test is written and no new
  test is run. Record the planner's reason; do not second-guess it.
- **Every new test fails before the code exists.** The orchestrator runs each `new` case by the
  command the writer reported for it. A case that passes catches nothing, and a case that does not
  run is broken: either one goes back to `test-writer` once, to sharpen or repair. A `guard` case
  checks behavior that already exists, and is exempt.
- **Fingerprint every file `test-writer` changed**, the moment its block lands:
  `git -C <work root> hash-object <file>…`. Compare after every `coding` turn. A file whose
  fingerprint moved goes back to `coding` with "restore this test file exactly; dispute it instead
  of changing it", and that costs one feature-test fix cycle. Take the fingerprints again after every
  `test-writer` turn, since a `revised` ruling changes them legitimately, and drop the ones for
  files it deleted.
- **A test dispute goes to `test-planner`, never straight to `test-writer`.** Forward the coding
  agent's `testDisputes` as they came, with the specification passages they cite. Then act on each
  ruling: `upheld` → `coding` gets the reason and builds against it; `revised` → `test-writer`
  changes the test, and the feature's tests run next, with no new-test check, because the code that
  makes it pass may already exist; `escalate` → the run's escalation. When one round holds both
  kinds, run the `test-writer` turn first, then send `coding` one message with every ruling.

## Never duplicate the gating run

- The **coding agent self-checks** what it touched, and nothing more.
- The **test writer runs only the tests it wrote**, while it writes them.
- The **orchestrator runs the gate**: each new test, then the feature's tests after every change to
  the code, then the full verification — every check command the project has. It is the only gate.
- The **code reviewer never runs the suite.** It answers a different question about the same
  change, and reads the code rather than running it.

Asking an agent to run the suite the orchestrator runs doubles the slowest block on the critical
path for no added signal.

## The outcome vocabulary

Every pipeline ends in exactly one of three states. Use these words, and mean only these things:

| Outcome | What happened | What it does to the ticket |
| --- | --- | --- |
| `completed` | Every gate passed — the tests and every check passed **and** every code reviewer returned `APPROVED`. | Finish the ticket. |
| `escalate` | A stage hit its retry cap, an agent reported a blocker it cannot pass, the answerer could not settle an open question, or the test planner ruled that a dispute turns on what the specification means. | Stop without finishing: the ticket becomes `blocked`, with one `blocked_by` line naming what a person must decide. |
| `aborted` | An agent returned no usable result — it died, or produced no valid JSON block after one retry. | Stop without finishing: the ticket becomes `blocked`, with one `blocked_by` line naming the stage and the agent that went silent. |

**Apply each cap mechanically.** A revision cap of one means one, and a fix cap of one covers every
defect found in that cycle together — every blocking issue from every reviewer in one message, and
every failed check in one message, not one message each. Do not improvise an extra cycle because
the next one looks close.

**Never report a skipped check as green**, and never mark work complete on a passing suite alone
when a review is part of the gate.

The `ticket-board` skill holds what each outcome writes to the ticket — its `status`, `assigned`,
`claimed`, `blocked_by`, and usage — to the roadmap, and to the worklog.
