---
name: agent-pipeline
description: "Defines how a command drives subagents: spawn each role once and resume it, run independent calls together, and act on each agent's closing JSON block. Use before spawning, resuming, re-reviewing, or judging a subagent from a command."
---

# agent-pipeline skill

How a command drives subagents. The stages and the gates belong to each command;
this skill holds the mechanics every one of them shares. The stages `/orchestrate`, `/run-roadmap`,
and `/orchestrate-quick` drive, from Plan to Code review and full verification, are in
[the build stages](references/build-stages.md), in a full and a quick mode: read it whole when one
of those commands says to. The rules those three commands share before their own stages are in
[the command preamble](references/command-preamble.md).

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

**The code review and the full verification run at once.** Both judge the same tree and neither
changes it, so the reviewers and the check commands go out in one tool block, and one fix message
carries every blocking issue and every failed check.

## An approval covers the code it read

A reviewer's `APPROVED` holds for the code it read, not for the code that ships. **Every fix after
the code review starts goes back to every code reviewer**, resumed in one tool block with the coding
agent's summary and `filesChanged`:

- a reviewer that blocked judges each of its prior issues as fixed or still open;
- a reviewer that approved judges only what the fix changed, from its focus.

A fix for a failed check is still a change to the code, so it gets the same re-review as a fix for
a review issue. Skipping it lets code nobody reviewed reach `done`.

## Every agent ends with one JSON block

Each agent ends its reply with exactly **one** fenced ` ```json ` block, in the contract its own
agent definition specifies. Parse it and drive control flow from it. There is no schema
enforcement and no background workflow — the block is the interface.

**The contract lives in the agent definition. Do not restate it in a spawn prompt.** A pre-read or spec-only turn emits no block when its agent definition says none is due; do not ask for one.

When a block is missing or malformed, `SendMessage` the agent, asking it to re-emit *only*
the JSON block. A turn that returns nothing at all is `human_required`.

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

## Hand the long documents over by path

The plan, the context pack, and the test plan go to most of the run's agents, and a pasted copy is
re-typed — as slow output — in every prompt that carries it. **Write each one once to the run
folder, and send its path:**

```
<framework root>/.runs/<claim>/
  .gitignore         one line, `*` — git ignores the folder, wherever the framework root sits
  plan.md            the plan markdown, as the planner returned it
  context-pack.json  the planner's `contextPack`
  test-plan.md       the test plan markdown, with its `cases` and `untested`
```

- **Write it the moment the document lands**, and overwrite it when a revision lands. A resumed agent
  that already read it gets "re-read `plan.md`; the plan was revised" instead of the plan again.
- **In a command's prompt, "the approved plan", "the context pack", and "the test plan" mean that
  file's absolute path**, with the line "read it whole before you start". The agent reads it itself.
- **Delete the folder at every exit**, finish and `human_required`. It is scratch, never a record:
  the worklog entries carry what the plan decided.
- **With no framework root** — `/orchestrate-quick` on a bare task — paste the documents as before.

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
  run is broken: either one goes back to `test-writer`, to sharpen or repair. A `guard` case
  checks behavior that already exists, and is exempt. In `/orchestrate-quick` the test writer
  proves each case fails itself, and its report is the gate.
- **Fingerprint every file `test-writer` changed**, the moment its block lands:
  `git -C <work root> hash-object <file>…`. Compare after every `coding` turn. A file whose
  fingerprint moved goes back to `coding` with "restore this test file exactly; dispute it instead
  of changing it". Take the fingerprints again after every
  `test-writer` turn, since a `revised` ruling changes them legitimately, and drop the ones for
  files it deleted.
- **A test dispute goes to `test-planner`, never straight to `test-writer`.** Forward the coding
  agent's `testDisputes` as they came, with the specification passages they cite. Then act on each
  ruling: `upheld` → `coding` gets the reason and builds against it; `revised` → `test-writer`
  changes the test, and the feature's tests run next, with no new-test check, because the code that
  makes it pass may already exist; `spec-question` → the answerer settles it, and with no answerer it is `human_required`. When one round holds both
  kinds, run the `test-writer` turn first, then send `coding` one message with every ruling.

## Notes for a person are written by the script

The coding agent reports actions only a person can take — a cloud firewall rule, a secret, a DNS
record, a third-party setting — as `notes` in its block. Its latest turn holds the full list.
**Never write a note file yourself.** The script writes every one, so its path, name, and
properties never depend on how a run worded them:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/create-note.py" --root <framework root> \
  --ticket <ticket file> --run <the run's claim, or the command name> <<'NOTES'
<the `notes` array from the coding agent's latest block, as it came>
NOTES
```

- **Run it once, when the ticket finishes**, in the same step that finishes it, so a ticket whose
  code is discarded leaves no note behind. A run that stops instead names each note in its outcome
  worklog entry; the run that resumes the ticket reports them again.
- **Pass `--feature <feature-name>` instead of `--ticket`** when the work has a feature and no
  ticket. With neither, there is no folder to write to: show the notes in the report.
- **An empty list writes nothing; skip the call.** A missing `python3` is the same — show the notes
  in the report, and say they were not written.
- **It prints `created` and `existing` paths.** Name them in the closing worklog entry and in the
  report under *Needs a person*. A note already on disk is kept as it is: the same title is the
  same need.
- **Exit 2 means nothing was written**, and the reason is on stderr. Fix what you passed — a wrong
  path, the array cut short — and run it once more. A second failure goes in the report with the
  notes in full; it never changes the outcome.

## Leftover review issues are filed by the script

The minor-fix pass of the build stages leaves **leftovers**: minor review issues the coding agent
declined, or that were still open or newly raised when the code review last passed. A run that only
reports them loses them, so they go into the epic's **review follow-up ticket**, a `Low` ticket in
`backlog/` that the roadmap builds like any other. **Never write that ticket by hand**; `board.py`
creates it, appends to it, and rebuilds the roadmap:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/board.py" follow-up --root <framework root> \
  --ticket <the finished ticket's ID> --run <the run's claim> [--claim] <<'LEFTOVERS'
[{ "title": "", "file": "", "line": "", "problem": "", "suggestion": "", "focus": "", "reason": "" }]
LEFTOVERS
```

- **Run it once, after the *Finishing a ticket* transition has landed**, in the same step as
  `create-note.py`. A ticket that stops instead files nothing: the run that resumes it reviews the
  code again.
- **`--claim` is a roadmap run's**, so the run builds the follow-up before it leaves the feature. An
  interactive run leaves it unclaimed for the person to pick.
- **It appends to the epic's open follow-up ticket** — one in `backlog/` that no other run claims —
  and opens a new one only when there is none. An issue already filed there, by its title and its
  file and line, is skipped.
- **A follow-up ticket's own leftovers are never filed.** The script returns `skipped` and writes
  nothing, so a follow-up never spawns another one. Name them in the closing worklog entry and the
  report instead.
- **An empty list writes nothing; skip the call.** With no ticket — a quick task with no board —
  there is no epic to file in: name the leftovers in the report.
- **It prints the ticket's `id` and `path`, `created`, and the `added` and `duplicates` titles.**
  Name the ticket and how many issues it gained in the closing worklog entry and in the report.
- **Exit 2 means nothing was written**, and the reason is on stderr. Fix what you passed and run it
  once more. A second failure, or a missing `python3`, puts the leftovers in full in the closing
  worklog entry and the report; it never changes the outcome.

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

Every pipeline ends in exactly one of two states. Use these words, and mean only these things:

| Outcome | What happened | What it does to the ticket |
| --- | --- | --- |
| `completed` | Every gate passed — the tests and every check passed **and** every code reviewer returned `APPROVED`. | Finish the ticket. |
| `human_required` | The run cannot go on without a person. It reports the stage and what the person must do. | Stop without finishing: the ticket becomes `blocked`, with one `blocked_by` line naming what a person must do. |

**`human_required` is the only thing that stops a pipeline, and no count ever raises it.** No stage has a limit on revisions, fix cycles, sharpen turns, or dispute rounds: a gate loops until it passes. Raise `human_required` only when one of these is true:

- **A question only a person can settle.** The answerer could not settle it, or the specification does not and there is no answerer.
- **A blocker.** An agent reports something it cannot pass.
- **A dead agent.** A turn returned nothing at all.
- **Stuck.** A fix turn left the same defects as the turn before it, and the agent that owns the fix has nothing different to try. Fewer defects, or different ones, is progress: keep going.
- **The ground is wrong.** A worktree, a commit, or the project itself is in a state the run must not repair.

**One cycle still carries everything found** — every blocking issue from every reviewer in one message, and every failed check in one message, not one message each.

**Never report a skipped check as green**, and never mark work complete on a passing suite alone
when a review is part of the gate.

The `ticket-board` skill holds what each outcome writes to the ticket — its `status`, `assigned`,
`claimed`, `blocked_by`, and usage — to the roadmap, and to the worklog.
