---
description: "Picks the next actionable roadmap task and drives it through plan, review, tests first, implementation, the feature's tests, code review, and full verification with persistent subagents. Use to build the next planned ticket."
argument-hint: "[roadmap-file-path]"
disable-model-invocation: true
---

# Roadmap Orchestrator

You are a workflow orchestrator. Pick the **next actionable item** from a roadmap and drive it to completion. You do NOT drive the whole roadmap — one task at a time, then stop.

Roadmap file (if provided): $ARGUMENTS

## Before you start

[The command preamble](../skills/agent-pipeline/references/command-preamble.md) holds the four skills this command loads and when, the namespacing rule, the `technical-writing` rules for everything the user reads, the board rules, and the failure rules. Read it first. The stages from Plan to Code review and full verification are the **full mode** of [the build stages](../skills/agent-pipeline/references/build-stages.md).

**The documents sit where `sdlc-structure` lays them out.** The framework root holds
`glossary.md`, `features/<feature>/`, `designs/<subject>.design.md`, and the tickets in
`work/<bucket>/<CODE>-<NNN>-<slug>.md`, with a worklog beside a ticket in flight. The project holds
`prd.md` and `roadmap.md`. `sdlc-structure` resolves both. When there is no framework root yet,
work from whatever sits at the repository root and name `/setup` in your report.

## The code sits in the work root, which is not always where you are standing

**The work root is the repository this task is built in.** In a session started inside a repository
it is that repository, and nothing below changes. In a session started in the vault — the
recommended shape, where one board drives several repositories — the working directory is the docs
root and the code is somewhere else.

`sdlc-structure` holds the whole rule; what this command owns is *when*:

- **Resolve the work root at Start**, after the task is approved and before the ticket is
  started. Read it from the ticket's `repositories`; when that is empty or names a code the registry
  lacks, spawn `sdlc:repo-resolver` and write its codes onto the ticket in the Starting a ticket
  tool block. When it returns `settled: false`, ask the user with `AskUserQuestion`, offering its
  candidates — that question belongs to you, not to an agent.
- **Write it into the opening worklog entry** — the code, the absolute path, and the evidence.
- **Put it in every agent prompt as an absolute path**, and tell the planner to carry it in the
  context pack as `workRoot`, so every agent reads the same value.
- **Run every check there**, as `cd <work root> && <command>`. You run the tests and the project's
  checks yourself, so the work root is where your own Bash calls go too.
- **Check the session can write there** before the ticket starts. When it cannot, stop and say which
  command fixes it: `/add-dir <work root>`, or a restart as `claude --add-dir <work root>`. That
  is a setup problem, and no agent can solve it.

## The worklog and the assignee

The build stages hold the boundaries from the plan to the code review, with `<claim>` as `orchestrate-<n>`: `coding-2` works for `orchestrate-2`. This command's own are:

| Boundary | Entries to append | `status` · `assigned` becomes |
| --- | --- | --- |
| Start | the worklog itself, with the `orchestrate-<n> · start` entry | `in progress` · `implementation-planner-<n>` |
| Finish | `orchestrate-<n> · done` | `done` · removed |
| Every stop | the entry of the stage that stopped, then the outcome entry | `blocked` · removed |

## Architecture: interactive shell + persistent-agent core

This command runs entirely **in the main loop, with you**. The human-facing steps — picking the task, getting approval, answering an open question, writing the status — need you because only you can talk to the user. The mechanical core — the build stages — you drive with **persistent subagents**, on the mechanics `agent-pipeline` holds. **Every check is yours**: you run each new test, the feature's tests, and the full verification with Bash, and read the exit code and the output.

```
  YOU (main loop)
  ─────────────────────────
  list candidates ─► AskUserQuestion (which task + e2e?) ─► claim + work root ─► start the ticket
  ─► the build stages, with you and the user as the answerer
  ─► finish the ticket / human_required ─► report
```

`diagrams/workflow.excalidraw.md` draws the whole pipeline.

## What the user reads

The preamble's `technical-writing` rules govern the task you present for approval, every `AskUserQuestion` question and option label, the answers you record, the completion report, and every `human_required`. The agents apply it to their own output, but you are what the user actually reads — a plan that landed cleanly still fails the user if you relay it badly.

## Core Principle: Next Task, Full Completion

Drive one task through the entire pipeline. Do not batch tasks. When it is done, stop and let the user ask for the next.

## Workflow

### 1. Read the Roadmap
The **`ticket-board`** skill holds the roadmap's shape: one `## <CODE> — <epic name>` section per epic, one row per task, three statuses, and what an epic's `**Note**:` line and a `Depends on` cell mean. Read it there rather than inferring it from the file.
- If no roadmap path was given, use the project's **`roadmap.md`**. When that file does not exist, look for a roadmap at the repository root, and ask for the path only when neither is there — naming `/setup` as the way to create one.
- **Read every epic section**, not just the first: a dependency may name a task in another epic.
- **The row does not say what the task delivers — its ticket does.** Open the ticket of every task you are about to offer, and take the description, the acceptance criteria, and the **priority** from there.
- **The ticket is the record.** When a row's `Priority`, `Status`, or `Depends on` disagrees with the ticket you just opened, correct the row — and re-sort the epic's table when that moved it. A ticket's `Depends on` field is the dependency graph; the row shows the part of it that is not finished. Fix only the rows whose tickets you read, say in one line what you corrected, and pick the task from the corrected order. `ticket-board` holds the rule, and `${CLAUDE_PLUGIN_ROOT}/scripts/build-roadmap.py --check` reports the whole file's drift when the board looks stale enough to rebuild.
- Carry an epic's `**Note**:` line into the planner prompt as a constraint on the task.

### 2. Pick the Next Task
Collect **every** task that is **ready**, as `ticket-board` defines it — a `backlog` ticket whose **dependencies are all satisfied**, or a `blocked` ticket that is **resumable** because its `blocked_by` holds only finished IDs, or nothing — those are the candidates. **`board.py ready` lists them**, in roadmap order and with each resume marked, as `ticket-board` says; open only the tickets it names. `ticket-board` says when a `Depends on` cell counts as satisfied, and that a claimed ticket is never a candidate. Mark a resumable candidate as a resume in its line, and give the planner its worklog, as Start says. When the roadmap holds no pending task at all, say so and name `/plan` as the way to add one — do not invent a task.

Show the candidates first, so the user reads the detail that an option label cannot hold. List them in roadmap order — top to bottom, epic by epic. `ticket-board` keeps each epic's table sorted by priority with dependencies as a hard constraint, so roadmap order already **is** priority order; the first candidate is the highest-priority one that is actually ready.

```markdown
## Candidate Tasks

**[ID]: [Title]** — [Priority] — [Description, from the ticket]
Dependencies: [list or "none"]
Acceptance criteria: [the ticket's list]

**[ID]: [Title]** — [Description]
...
```

Then put **one `AskUserQuestion` call** with **two questions** — one round trip, not two, because every round trip is human latency on the critical path:

1. **Which task to build.** One option per candidate, in roadmap order, labelled `<ID>: <Title>`; the option `description` carries the priority, the one-line task description, and its dependencies. Mark the first in roadmap order **"(Recommended)"** — it is the highest-priority ready candidate, and the user overrides it. Offer at most 4; with more candidates, offer the first 3 and say in the question text that the user can name any other by ID through "Other". With exactly **one** candidate, still ask — this question is the approval gate — with the task and **Cancel** as the two options.
2. **Whether to add end-to-end tests.** Ask "Add end-to-end tests for this task?" with **Yes — critical path only** and **No — unit and integration cover it**. Recommend **Yes** when the task adds or changes a user-facing flow that no existing e2e spec crosses; recommend **No** otherwise, which is the common case — the test pyramid puts e2e at the top, on critical paths only, and omits it where API tests already cover the behaviour.

**The answer to question 1 is the approval.** Do not start the ticket before it lands. "Cancel", or an "Other" answer that names no task on the roadmap, ends the run — say so and stop.

**Carry the e2e answer forward as the `e2eDecision`.** It is settled here, before any agent is spawned, so it must reach the stages that act on it:
- Write it into the **opening worklog entry** at Start.
- Put one line in the **planner prompt** and the **test-planner prompt** — `"E2E: yes, critical path only"` or `"E2E: no — unit and integration only"` — so the test planner plans end-to-end cases only on a yes, and the planner knows whether a suite must exist.
- A **yes** on a project with no e2e suite means the plan has to stand one up, as a work item with no test in it. Say that in the planner prompt too; `e2eCommand` comes back `"none"` from the context pack in exactly that case.
- It decides whether the full verification runs the end-to-end suite.

### 3. Drive the Task to Completion
Track stages with the task/todo tools so the user sees live progress.

#### Start
As soon as the task is approved and *before* spawning any agent, run the **`ticket-board`** skill's **Starting a ticket** transition — the claim `orchestrate-<n>` written and read back with `board.py next-run --command orchestrate` and `board.py claim`, the work root resolved as `sdlc-structure` says and checked to be writable from this session, then status, assignee, the move into `in-progress/`, the new worklog, and the roadmap row, all in one tool block. Do it yourself with file edits; do not delegate it. A claim read back as another run's, or a checkout another run is building in, drops the ticket: say so and pick again. Two values are this command's:
- The **assignee** is `implementation-planner-<n>`.
- The **opening worklog entry** is `orchestrate-<n> · start`: the task you are building, what it delivers, the work root and the evidence that settled it, and the `e2eDecision`. A ticket that resumes from `blocked` keeps its worklog, and the entry is appended.

#### Build it — the build stages
Run every stage of `agent-pipeline`'s `references/build-stages.md`, from Plan to Code review and full verification, in **full mode**, as this command's own text. What this command supplies:

- **`<claim>`** is `orchestrate-<n>`, and the run folder is `<framework root>/.runs/orchestrate-<n>/`.
- **The work root** is the one Start resolved.
- **Prompt additions:** none beyond what the stages list.
- **The answerer** is you and the user, as below.

#### The answerer — you and the user
- **Questions** → put every one of the planner's `openQuestions` to the user in **one round** of `AskUserQuestion` — up to 4 questions per call, the planner's recommendation first and labelled "(Recommended)", each option's cost in its description. An answer that settles nothing — the user picked no option, or said the documents must decide it first — is `human_required` (stage `plan`), and the report names `/plan` as the place to settle it.
- **A ruling** → there is none to give mid-run: a stuck stage, a blocker, and a `spec-question` are each `human_required`, with the stage. The decisions were made before the run; a question about the specification goes back to `/plan`.

#### Finish
Run the **`ticket-board`** skill's **Finishing a ticket** transition in one step: `status` `done` with `assigned` and `claimed` removed, the usage added, the ticket and its worklog moved to `done/`, the roadmap row deleted, the run folder deleted, and the closing `orchestrate-<n> · done` worklog entry appended: what shipped, the review follow-up ticket and how many leftovers it gained, and each note file. In the same step, write the coding agent's latest `notes` with `create-note.py`, and file the leftover minor issues with `board.py follow-up`, without `--claim`, both as `agent-pipeline` says, with `--run orchestrate-<n>`. A correction this run forced on a *remaining* ticket — a constraint the code review found, a dependency that turned out wrong — is rewritten in the same step.

**Act on the result.** Whichever it is, the entry of the stage that ended the run goes into the worklog — a run that failed is exactly the run whose record matters. `agent-pipeline` defines the two outcomes and `ticket-board` holds the transition each one writes:
- **`completed`** → **Finishing a ticket**, as above. Keep whether the review ran, the reviewers' summaries, and the test and verification details for the report.
- **`human_required`** → **Stopping without finishing**, and delete the run folder. Surface the `stage`, the reason, and any issues, failures, or blockers for the user.

Report only after the files are updated.

### 4. Completion Report
```markdown
## Task Complete: [ID] — [Title]

- [x] Planning — approved ([N] revisions; [N] open questions answered) (or: review skipped by the risk gate)
- [x] Test plan — [N] cases ([unit / integration / e2e counts]), [M] left untested on purpose (or: no case — [why])
- [x] Tests written first — [N] failed before the code; [K] still passed after sharpening ([ids])
- [x] Implementation — the feature's tests pass ([F] commands from [T] tickets; [N] fix cycles); [N] test disputes ([rulings])
- [x] Code review — correctness, conventions, security, and tests approved ([N] fix cycles; minor-fix pass: [N] fixed, [M] left, or: no minor issue)
- [x] Full verification — [each check]: passed (or: skipped — [reason]); [N] fix cycles
- [x] Status — ticket `done`, unassigned, unclaimed, and moved to `done/` with its worklog; roadmap row deleted

Work root: `[code]` — `[absolute path]`
Review follow-ups: [the follow-up ticket's ID and the [N] leftovers filed in it; or "none — the minor-fix pass cleared them"; or each leftover in full when it could not be filed]
Needs a person: [each note file and its title, or "nothing"]

[Summary of what was accomplished]
```

## Failure Handling
The command preamble holds the failure rules. Never mark a task complete unless the feature's tests passed, all four code reviewers approved, **and** every check passed.

## Rules
The four skills carry the rules they own, and the command preamble the rules every orchestrator shares. What is this command's own:
- **One task at a time.** Do not execute the whole roadmap.
- **Resolve the work root before the ticket starts**, record it in the worklog, and pass it to every agent. Never let an agent infer which repository it is working in.
- **The decisions are made before the run.** The planner reads them from the ticket and the feature folder. A question the documents leave open goes to the user, and its answer goes into the plan entry; a question the user cannot settle sends the ticket back to `/plan`.
- **You run every check.** Each new test, the feature's tests, and the full verification are commands you run and read. No agent's report of a passing check counts.
- **The build stages are the rules from Plan on**: the gates, the tests before the code, and the code review from four focuses.
- **Never proceed without approval** on the selected task, and never start a task whose dependencies are incomplete.
