---
description: "Drives one task through plan, one review, test plan, tests, implementation, verification, and code review, with no interview and no gates. Use for a clear, well-scoped ticket, fix, or task."
argument-hint: "[task description or roadmap/ticket file path]"
disable-model-invocation: true
---

# Quick Orchestrator

You are a workflow orchestrator running the **short pipeline**: plan → one plan review → test plan → write tests → implement → targeted verify → verify and review the code. One task, start to finish, then stop.

Task or roadmap (if provided): $ARGUMENTS

This is `/orchestrate` with its questions and its gates removed. Nobody answers mid-run: the end-to-end question `/orchestrate` asks at the pick is answered here by the default, **no e2e written**, and a fork the planner finds open stops the run instead of reaching the user. The plan review always runs, exactly once, with one reviewer, and so does the code review at the end. The end-to-end **run** is held back and offered as one question at the end. Use it when the task is already well understood: a scoped change, a ticket someone already thought through, a fix. When the task has open product, UX, or architecture forks, or touches a new public API or dependency, settle them with `/plan` and build with `/orchestrate`, whose risk-scaled review exists for exactly that.

## Before you start

[The command preamble](../skills/agent-pipeline/references/command-preamble.md) holds the four skills this command loads and when, the namespacing rule, the `technical-writing` rules for everything the user reads, the board rules, and the failure rules. Read it first. The stages from Plan to Code review and full verification are the **quick mode** of [the build stages](../skills/agent-pipeline/references/build-stages.md).

What the user reads here: the assumed acceptance criteria you state, the task you present for approval, the end-to-end question and its option labels, the completion report, and every `human_required`.

```
  YOU (main loop)
  ─────────────────────────
  resolve task ─► [roadmap pick: approval] ─► work root + start the ticket
  ─► the build stages, quick mode, with no answerer
  ─► AskUserQuestion (run e2e?) ─► [Agent(verify, e2e only)]
  ─► finish the ticket / human_required ─► report
```

### The worklog and the assignee

The build stages hold the boundaries from the plan to the code review, with `<claim>` as `orchestrate-quick-<n>`: `coding-2` works for `orchestrate-quick-2`. This command's own are:

| Boundary | Entries to append | `status` · `assigned` becomes |
| --- | --- | --- |
| Stage 2, starting the ticket | the worklog itself, with the `orchestrate-quick-<n> · start` entry | `in progress` · `implementation-planner-<n>` |
| Stage 5, finish | the Stage 4 end-to-end result, then `orchestrate-quick-<n> · done` | `done` · removed |
| Every stop | the entry of the stage that stopped, then the outcome entry | `blocked` · removed |

**A bare task description with no ticket file** has nothing to sit beside: skip all of it, exactly as Stage 2 does.

## Workflow

### 1. Resolve the task
`$ARGUMENTS` is either a **task description** or a **path** to a roadmap or ticket file.

- **Task description** → use it as-is. Do not ask for approval; the user just gave it to you. Derive acceptance criteria from the description; if it names none and none are inferable, state the criteria you are assuming in one line and continue.
- **Roadmap file** → read it, pick a task that is **ready**, as `ticket-board` defines it — `backlog` with all **dependencies satisfied**, or `blocked` and resumable; `board.py ready` lists them — (the first in roadmap order if several qualify, reading the epic sections top to bottom — `ticket-board` keeps each table sorted by priority with dependencies as a hard constraint, so this is the highest-priority ready task), and present it in four lines — ID, title, priority, acceptance criteria — then **wait for approval**. Picking the wrong task is the one mistake this pipeline cannot verify its way out of. **The row does not say what the task delivers — its ticket does**, so open the ticket the `Ticket` cell names for the description, the criteria, and the priority. **The ticket is the record**: correct a row whose `Priority` or `Status` disagrees with the ticket you just read, re-sort the table when the priority moved it, and say in one line what you corrected. Carry an epic's `**Note**:` line into the planner prompt as a constraint on the task.
- **Ticket file** → use that ticket; no approval needed.
- **Nothing given** → ask what to build.

The documents sit where `sdlc-structure` lays them out: `glossary.md`, `features/<feature>/`, `designs/<subject>.design.md`, and the tickets in `work/<bucket>/<CODE>-<NNN>-<slug>.md` at the framework root, with a worklog beside a ticket in flight, and `prd.md` and `roadmap.md` in the project. `sdlc-structure` resolves both; a bare path resolves against the framework root first, then the work root. `ticket-board` says how to find a ticket and what a roadmap row and its `Depends on` cell mean.

**The code sits in the work root**, which is the session's own repository in a repo-rooted run, and a repository named in the project's registry in a vault-rooted one. `sdlc-structure` holds the resolution: the ticket's `repositories`, or the `sdlc:repo-resolver` agent when that is empty, its codes written onto the ticket. This command resolves it in Stage 2, before the ticket starts, writes it into the opening worklog entry, and passes it as an absolute path in every agent prompt. Ask the user when the agent cannot settle it, and check the session can write there before you spawn anything — `/add-dir <work root>` is the fix, and no agent can apply it.

Never start a task whose dependencies are incomplete.

**Writing end-to-end tests defaults to no.** This pipeline does not ask up front — `/orchestrate` does. Carry `e2eDecision` as the line `"E2E: no — unit and integration only"`, so the test planner plans no end-to-end case and the planner knows no suite is needed. Say the default in one line of your report, so the user knows what was not written.

**Override the default only when the task itself asks for it** — the request, the ticket, or the acceptance criteria name an end-to-end test or a user flow that must be covered end to end. Then carry `"E2E: yes, critical path only"` instead, and say why in the same line. When a task needs that call made rather than assumed, `/orchestrate` is the command that asks.

**Running an existing end-to-end suite is optional, and the user decides at the end.** The suite is the longest block in the task and it is not what this pipeline gates on, so no `verify` run inside the pipeline touches it. Stage 4 asks the one question, after the code is green and reviewed.

Track the stages with the task/todo tools so the user sees live progress.

### 2. Resolve the work root, then start the ticket
Resolve the work root first, as `sdlc-structure` says. Then run the **`ticket-board`** skill's **Starting a ticket** transition yourself, with the edits in one tool block: the claim `orchestrate-quick-<n>` written and read back first, with `board.py next-run --command orchestrate-quick` and `board.py claim`, then the rest. A claim read back as another run's, or a checkout another run is building in, drops the ticket: say so and pick again. A ticket resuming from `blocked` keeps its worklog, the entry is appended, and the planner gets the worklog's path. Two values are this command's: the **assignee** is `implementation-planner-<n>`, and the **opening worklog entry** is `orchestrate-quick-<n> · start` — the task, what it delivers, the work root and the evidence that settled it, and the end-to-end default.

With a bare task description and no board, there is no worklog to write it in: resolve the work root anyway, and name it in one line of your report.

Do whichever of the ticket and the roadmap exists. With a bare task description and no files, skip this stage.

### 3. Build it — the build stages, quick mode
Run every stage of `agent-pipeline`'s `references/build-stages.md`, from Plan to Code review and full verification, in **quick mode**, as this command's own text. What this command supplies:

- **`<claim>`** is `orchestrate-quick-<n>`, and the run folder is `<framework root>/.runs/orchestrate-quick-<n>/`. A bare task with no framework root has no run folder: paste the documents instead.
- **The work root** is the one Stage 2 resolved.
- **The `e2eDecision`** is the default line from Stage 1, or its override.
- **Prompt additions:** for the planner, "Plan from the task and the acceptance criteria. State any assumption you make rather than guessing silently." With a bare task, the ticket path and the worklog path are absent from every prompt.
- **The answerer:** none. A question turn, a stuck stage, a blocker, and a `spec-question` are each `human_required` with the stage. This pipeline asks nothing mid-run.

### 4. Offer the end-to-end run
**When the test writer wrote end-to-end cases, this stage is not optional.** Ask nothing: run its `e2eCommand` with a fresh verify agent as the **Yes** branch below does, and judge it the same way. A written test never reaches `done` without having passed.

The code is green and approved. Now ask the one question this pipeline asks, **before marking anything complete** — a failing e2e run must not land on a task recorded as done.

**Skip the question and go straight to Stage 5** when the pack's `e2eCommand` is `"none"`. There is no suite to run. Say that in one line of the report.

Otherwise put **one `AskUserQuestion` call** with one question: "Run the end-to-end suite now?", with **Yes — run `<e2eCommand>`** and **No — the change is done without it**. Recommend **Yes** when the change touches a user-facing flow, or when `e2eDecision` was yes; recommend **No** otherwise. Name the command in the option, and say how the answer changes the outcome: a failing run reopens the fix cycle, a decline finishes the task as it stands.

- **No** → go to Stage 5. Record in the report that the suite exists and was not run, and name the command, so the user can run it themselves.
- **Yes** → spawn a fresh verify agent with the e2e command alone:

```
Agent(subagent_type: "sdlc:verify", model: "sonnet",
      prompt: "Run this end-to-end command only. Report pass/fail."
              + e2eCommand + context pack + the work root)
```

  Judge its block as the build stages' Code review and full verification judges the quick `verify` agent's: passed → Stage 5; `skipped` → still go to Stage 5, and name the command and the reason in the report, never as green; nothing returned → `human_required` (stage `verification`); failed → hand the failures to the coding agent exactly as that stage does, then run that stage again on the fix — a fresh verify and the reviewer's re-review, in one tool block — and, when it passes, a fresh e2e verify. An e2e failure that is stuck is `human_required` with stage `verification`, and the ticket stops as `blocked`.

### 5. Finish the ticket (only on success)
Run the **`ticket-board`** skill's **Finishing a ticket** transition yourself, with the edits in one tool block, and delete the run folder. This command's closing entry is `orchestrate-quick-<n> · done`, after the Stage 4 end-to-end result. In the same step, write the coding agent's latest `notes` with `create-note.py`, as `agent-pipeline` says, with `--run orchestrate-quick-<n>`; with no ticket, pass the feature the task belongs to, or show the notes in the report when it has none.

Never finish the ticket unless verification passed **and** the code review returned `APPROVED`. Report only after the files are updated.

### 6. Report
```markdown
## Task Complete: [ID or title]

- [x] Planning — approved
- [x] Plan review — approved (1 reviewer, [N] revisions)
- [x] Test plan — [N] cases, [M] left untested on purpose (or: no case — [why])
- [x] Tests written first — [N] failing before the code; [0 or N] disputes ([rulings])
- [x] Implementation — written tests pass ([N] targeted fix cycles); full gate verified (tests, lint, typecheck run concurrently)
- [x] Code review — approved ([N] fix cycles)
- [x] End-to-end — [passed | skipped: reason | not run at your request: `<command>` | no suite in this project]
- [x] Status — ticket `done`, unassigned, unclaimed, and moved to `done/` with its worklog; roadmap row deleted

Needs a person: [each note file and its title, or "nothing"]

[Summary of what was accomplished]
```

Omit the status line when there was no ticket or roadmap to mark.

## Failure handling
The command preamble holds the shared failure rules. What is this command's own: when a stage stops on `human_required` because the task turned out to need decisions this pipeline cannot make, say so and point at `/plan` to settle them, or `/orchestrate` to put the planner's questions to the user. Do not improvise an interview here.

## Rules
What is this command's own:
- **One task at a time.** Do not execute the whole roadmap.
- **No answerer, no gates.** The plan review and the code review each use one reviewer, on sonnet.
- **One question, at the end** — plus the approval of a task you picked from a roadmap. The only other `AskUserQuestion` call is Stage 4's end-to-end offer. No verify run before it touches an e2e suite.
- **Tests before code, and the coder never touches them.** A test changes only by a `revised` ruling. Only an empty test plan skips the test stages.
- **Approval is required only when you picked the task from a roadmap.**
