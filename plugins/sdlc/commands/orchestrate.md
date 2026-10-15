---
description: Pick the next actionable roadmap task and drive it through plan → review → tests first → implement → the feature's tests → code review → full verification using persistent subagents.
argument-hint: [roadmap-file-path]
---

# Roadmap Orchestrator

You are a workflow orchestrator. Pick the **next actionable item** from a roadmap and drive it to completion. You do NOT drive the whole roadmap — one task at a time, then stop.

Roadmap file (if provided): $ARGUMENTS

## The rules live in four skills — load each one before the stage that needs it

| Skill | What it holds | Load before |
| --- | --- | --- |
| **`sdlc-structure`** | Where the project and the work root are, and how each destination writes a document | you read any document |
| **`ticket-board`** | The ticket, the roadmap, the claim, the assignee, the worklog, and what each status transition writes | Start |
| **`agent-pipeline`** | Spawn once and resume, concurrent calls, the JSON block, the test fingerprints and the dispute route, the outcome vocabulary | Plan |
| **`technical-writing`** | Every word the user reads | Pick the next task |

Each name may be namespaced here — `sdlc:sdlc-structure`, `sdlc:ticket-board`,
`sdlc:agent-pipeline`, `sdlc:technical-writing`. Invoke the namespaced form when it is there, load each
skill **once**, and follow it. Do not work from memory, and do not restate a skill's rules in a
spawn prompt: the agents load their own.

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
- **A task that spans two repositories** runs the feature's tests, the code review, and the full
  verification once per work root, and passes only when every one of them passes.

## The worklog and the assignee — you are the only writer

The **`ticket-board`** skill holds the worklog's shape, what belongs in an entry, and what each
assignee value means. What is specific to this pipeline:

**You are the only writer.** Each agent reports its decisions to you and you write them down, so
the file has one writer and the four code reviewers cannot lose each other's entry. No agent writes
the ticket, the worklog, or the roadmap.

**`<n>` is this run's number** — the one in its claim, `orchestrate-<n>`. Every agent of the run
carries it in `assigned`: `coding-2` works for `orchestrate-2`. Your own entries name the claim:
`orchestrate-2 · start`.

**The entry and the assignee go in one tool block**, at these boundaries:

| Boundary | Entries to append | `status` · `assigned` becomes |
| --- | --- | --- |
| Start | the worklog itself, with the `orchestrate-<n> · start` entry | `in progress` · `implementation-planner-<n>` |
| The plan lands | `implementation-planner · plan` | `plan-reviewer-<n>`, or `test-planner-<n>` when the risk gate skips the review |
| The plan review approves | `plan-reviewer · plan review` | `test-planner-<n>` |
| The test plan lands | `test-planner · test plan` | `test-writer-<n>`, or `coding-<n>` when it holds no case |
| The tests land | `test-writer · tests` | unchanged |
| Every new test has been run | `test-writer · tests` again when a sharpen turn changed a file or a command, then `orchestrate-<n> · new tests` | `coding-<n>` |
| The implementation lands | `coding · implement` | unchanged |
| A test dispute goes out | none | `test-planner-<n>` |
| The rulings land | `test-planner · test dispute`, then `test-writer · tests` when a test was revised | `coding-<n>` |
| The feature's tests pass | `orchestrate-<n> · feature tests` | `review` · `code-reviewer-<n>` |
| The code review blocks | `code-reviewer · code review`, one per focus that reviewed | `in progress` · `coding-<n>` |
| The code review approves | `code-reviewer · code review`, one per focus that reviewed | unchanged |
| The full verification fails | none | `review` · `coding-<n>` |
| Finish | `orchestrate-<n> · verification`, then `orchestrate-<n> · done` | `done` · removed |
| Every stop | the entry of the stage that stopped, then the outcome entry | `blocked` · removed |

A `test-writer · tests` entry records every file the writer changed and the command that runs each
case. **The feature's later tickets run their tests from that record**, so it must name what is on
disk now.

**Every exit writes the outcome entry and the assignee** — an escalation or an abort at any stage
runs `ticket-board`'s *Stopping without finishing* transition, so the next session can read the
worklog and learn where the task stopped.

## Architecture: interactive shell + persistent-agent core

This command runs entirely **in the main loop, with you**. The human-facing steps — picking the task, getting approval, answering an open question, writing the status — need you because only you can talk to the user. The mechanical core — plan → review → test plan → write tests → implement → review the code — you drive with **persistent subagents**, on the mechanics `agent-pipeline` holds. **Every check is yours**: you run each new test, the feature's tests, and the full verification with Bash, and read the exit code and the output.

```
  YOU (main loop)
  ─────────────────────────
  list candidates ─► AskUserQuestion (which task + e2e?) ─► claim + work root ─► start the ticket ─►

  ┌ Agent(planner) ─► contextPack + plan + riskProfile, or open questions ─┐  concurrent
  └ Agent(test-planner) "SPEC ONLY" ─► draft cases ────────────────────────┤
     [questions open] AskUserQuestion (one round) ─► SendMessage(planner, answers) ─► plan
                      └ Agent(reviewer) "PRE-READ ONLY" (context pack), same tool block
  [risk low ─► skip review]  reviewer(s) ─► verdict
        ▲                                 │ CHANGES_REQUESTED
        └── SendMessage(planner, issues) ◄┘  (revise ×1, re-review)
  SendMessage(test-planner, plan + pack) ─► test plan ─► [no case: skip to coding]
  Agent(test-writer) ─► tests + a command per case ─► fingerprint them
  YOU run each new case ─► passes or does not run ─► SendMessage(test-writer)  (sharpen ×1)
  Agent(coding) ─► [fingerprints moved? ─► restore]
        │ testDisputes ─► SendMessage(test-planner) ─► upheld / revised (test-writer) / escalate
        ▼                                              (one dispute round per ticket)
  YOU run the feature's tests ─► fail ─► SendMessage(coding)  (fix ×2)
        ▼ pass                                  status ─► review
  ┌ Agent(code-reviewer) "Focus: correctness" ┐
  ├ Agent(code-reviewer) "Focus: conventions" ┤  concurrent, every one must APPROVE
  ├ Agent(code-reviewer) "Focus: security"    ┤
  └ Agent(code-reviewer) "Focus: tests"       ┤
        ▲                                     │ CHANGES_REQUESTED
        └── SendMessage(coding) ─► feature's tests ─► blocking reviewers only  (fix ×1)
  YOU run full verification: lint, typecheck, full suite, e2e ─► fail ─► SendMessage(coding)  (fix ×1)
  finish the ticket / escalate ─► report
```

### Which agents are persistent here
The **`agent-pipeline`** skill holds the mechanics — spawn once, resume with `SendMessage`,
concurrent calls in one tool block, the JSON block and its single retry, the test fingerprints and
the dispute route, and the `completed` / `escalate` / `aborted` vocabulary. This command's
persistent roles are the **planner**, the **plan reviewer** (two ids on a high-risk plan, one per
lens), the **test planner**, the **test writer**, the **coding agent**, and the **four code
reviewers**. Each review focus is a role of its own: a re-review resumes the reviewer that blocked.
Record every id the `Agent` call returns.

**No agent runs a check for the gate.** The coding agent self-checks what it touched, and the test
writer runs only the tests it wrote. Neither report counts: a check passes only when you ran it and
read the result.

### Overlap the stages that don't depend on each other
- **The test planner drafts from the specification while the plan is written.** It must not see the plan before it has drafted its cases, so the planning window is exactly where it belongs — **spec only** mode, spawned in the same tool block as the planner. It always runs, so this spawn is never wasted.
- **The reviewer pre-reads while the plan is written.** A reviewer must read the referenced files rather than review from the plan text. When the planner returned open questions, the context pack exists before the plan does: spawn the reviewer in **pre-read only** mode in the same tool block that sends the planner the answers. When it planned in one turn, the reviewer gets the plan and the pack together.
- **The four code reviewers run at once.** They judge the same change from four focuses, and none needs another's answer.
- **The checks run at once.** The full verification's commands go out as parallel Bash calls in one tool block, so the slowest check sets the wall-clock, not the sum of them.
- **The coding agent self-checks what it touched, and nothing more.** Never ask it to run the whole suite — that duplicates your slowest block, sequentially.

A pre-read review is occasionally discarded, when the risk gate skips the review. That is a token cost, not a wall-clock one — take it.

### Context Pack (built once, forwarded automatically)
The planner emits a **context pack** — the work root, relevant files, key symbols, conventions, one check command per check in `verificationCommands`, and the project's `e2eCommand` — in its JSON block, on its first turn. Paste it into the plan reviewer's, the test planner's, the test writer's, the coding agent's, and every code reviewer's *first* message, so none of them cold-explores the codebase (later `SendMessage` turns already have it). You read its commands for the full verification.

## Everything you show the user goes through `technical-writing`

You are the only stage that talks to the person, so `technical-writing` governs every word they see: the task you present for approval, every `AskUserQuestion` question and option label, the answers you record, the completion report, and every escalation or abort.

The agents apply it to their own output, but you are what the user actually reads — a plan that landed cleanly still fails the user if you relay it badly. The rules that bite hardest here: name the task and the stake before the detail, give the verdict before the evidence, keep an option label to one short phrase, and reuse the roadmap's and the PRD's own words for every domain term. It governs prose only — IDs, file paths, commands, status markers, and the agents' `json` blocks stay exact. They stay exact **beside** the prose: a path, a symbol, or a snippet never goes inside a sentence, and the sentence names the thing in words instead.

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
Collect **every** task that is **pending** and whose **dependencies are all satisfied** — those are the candidates. `ticket-board` says when a `Depends on` cell counts as satisfied, and that a claimed ticket is never a candidate. When the roadmap holds no pending task at all, say so and name `/plan` as the way to add one — do not invent a task.

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

Every agent turn ends with one `json` block. When a block is missing or malformed, ask that agent **once** to re-emit it; a second miss is `aborted` at that stage. The stage names below are the ones an escalation or an abort reports.

#### Start
As soon as the task is approved and *before* spawning any agent, run the **`ticket-board`** skill's **Starting a ticket** transition — the claim `orchestrate-<n>` written and read back, the work root resolved as `sdlc-structure` says and checked to be writable from this session, then status, assignee, the move into `in-progress/`, the new worklog, and the roadmap row, all in one tool block. Do it yourself with file edits; do not delegate it. A claim read back as another run's drops the ticket: say so and pick again. Two values are this command's:
- The **assignee** is `implementation-planner-<n>`.
- The **opening worklog entry** is `orchestrate-<n> · start`: the task you are building, what it delivers, the work root and the evidence that settled it, and the `e2eDecision`. A ticket that resumes from `blocked` keeps its worklog, and the entry is appended.

#### Plan
**Spawn the planner and the test planner in one tool block.** Keep both ids.

```
Agent(subagent_type: "sdlc:implementation-planner", model: "opus",
      prompt: the ticket path + task block + acceptance criteria + the epic's Note line
              + the e2eDecision line + the work root as an absolute path
              + (resumed ticket) the worklog path)

Agent(subagent_type: "sdlc:test-planner", model: "opus",
      prompt: the ticket path + task block + acceptance criteria + the e2eDecision line
              + the work root as an absolute path
              + "SPEC ONLY. The plan is being written and you will not see it yet. Draft the
                 cases from the specification and the existing tests now, and reply with a few
                 lines. I will send the plan.")
```

The planner reads the feature folder — the ticket and its `Decisions`, the feature note, the design docs it lists, the solution designs in `designs/`, and the PRD — then surveys the code and researches current practice. Its agent definition holds that process and the JSON contract; do not restate them. Its block carries `contextPack`, `riskProfile`, and `openQuestions`.

- **Nothing returned** → `aborted` (stage `plan`).
- **`openQuestions` is empty**: the turn holds the plan. Go on below.
- **`openQuestions` is not empty**: the turn holds the context pack, no plan, and a `null` `riskProfile`. Put every question to the user in **one round** of `AskUserQuestion` — up to 4 questions per call, the planner's recommendation first and labelled "(Recommended)", each option's cost in its description. Then, in **one tool block**:
  - `SendMessage(plannerId, the answers + "Plan from these answers now. Re-emit your json block.")`;
  - the plan reviewer's **pre-read**, spawned as Review the plan says.

  **An answer that does not settle a question is an escalation** (stage `plan`): the user picked no option, or said the documents must decide it first. The `blocked_by` line names the question, and the report names `/plan` as the place to settle it. Never ask a second round; a second turn of questions from the planner is an escalation too.

Keep the plan markdown as `plan`, and the parsed `contextPack` and `riskProfile` in hand. When the plan lands, append the `implementation-planner · plan` entry and set the assignee, in one tool block. The plan markdown is persisted nowhere else, so the entry carries the **direction** the plan settled on, the approach it turned down, and each question with the answer the user gave.

#### Review the plan
**Apply the gate mechanically** on the `riskProfile` that came back with the plan — no judgment here:

- **Skip review** iff `filesTouched ≤ 2` **and** `addsDependency == false` **and** `addsPublicApi == false` **and** `criteriaAutoCheckable == true`. The plan entry says "Review gate: SKIPPED", the assignee becomes `test-planner-<n>`, and you go to Plan the tests with the plan as approved. Drop a pre-read reviewer.
- Otherwise **review is required**. It is **high-risk** iff `addsPublicApi == true` **or** `addsDependency == true` **or** `filesTouched > 5`.
  - **Normal risk:** **one** reviewer, `model: "sonnet"` — reviewing a plan against files it has already read is checklist work.
  - **High risk:** **two** reviewers, spawned **in one tool block** with `model: "opus"`, same base but distinct lenses: (a) *correctness/completeness* — will the plan satisfy every acceptance criterion; missing work items, wrong assumptions, edge cases, ordering hazards; (b) *codebase fit* — conventions, dependency rules, architectural boundaries, unjustified new API/deps. Keep **both** ids. A pre-read reviewer becomes lens (a), and you spawn the second now.

**The pre-read**, when the planner asked questions first — spawned in the tool block that sends the answers:

```
Agent(subagent_type: "sdlc:plan-reviewer", model: "sonnet",
      prompt: the ticket path + task block + acceptance criteria + the questions and their answers
              + the context pack + the work root as an absolute path
              + "PRE-READ ONLY. The plan is still being written. Read every file in the
                 context pack now and reply with a few lines on what you read and any
                 hazard you already see. Do NOT issue a verdict yet.")
```

**Hand over the plan** with `SendMessage(reviewerId, "Review the plan below against the checklist. You have already read the context pack files; re-read only what the plan points at that you have not seen. <plan>")`. A reviewer that never pre-read gets the full first message: the ticket path + task block + acceptance criteria + the questions and their answers + plan + context pack + the work root + "Read the referenced files — do not review from the plan text alone." Two reviewers go out **in one tool block**.

Every reviewer ends its review turn with a `json` block carrying `verdict` (`APPROVED` | `CHANGES_REQUESTED`), `summary`, and `issues` — shape in the agent definition, do not restate it. Merge multiple reviewers: `CHANGES_REQUESTED` if **any** reviewer requests changes; concat their issues. Nothing returned → `aborted` (stage `plan-review`).

**Revision loop — at most ONE cycle:**
- `APPROVED` → append the `plan-reviewer · plan review` entry and set the assignee to `test-planner-<n>`, in one tool block, then Plan the tests. The entry carries the verdict, the issues that forced a revision, and how the revision answered them.
- `CHANGES_REQUESTED`, **not yet revised**: `SendMessage(plannerId, "Revise your plan to resolve every issue below. Note in the Context section how each was addressed. Re-emit the full plan markdown + the ```json block." + issues)` — the planner holds the plan, the ticket, and the pack, so **send only the issues**. Then re-review via `SendMessage` to the same reviewer(s): `"Re-review the revised plan below; the files are unchanged. <revised plan>"` — both in **one tool block** when there are two. Loop back to the new verdict.
- `CHANGES_REQUESTED`, **already revised once** → **`escalate`** (stage `plan-review`) with the reviewer summary and the remaining issues.

#### Plan the tests
Resume the test planner, spawned at Plan, with the approved plan:

```
SendMessage(testPlannerId, approved plan + context pack
                         + "The plan is approved. Attach your drafted cases to the interfaces it
                            exposes, cut what it made redundant, and return the full test plan
                            with its ```json block.")
```

It returns the test plan and a `json` block carrying `summary`, `cases` (each `new` or `guard`), and `untested`. Nothing returned → `aborted` (stage `test-plan`).

Append the `test-planner · test plan` entry — each case in one line (its id, the bug it catches, its type) and each exclusion with its reason; the test plan is persisted nowhere else. In the same tool block, set the assignee to `test-writer-<n>`, or to `coding-<n>` when `cases` is empty. **An empty plan skips Write the tests and Run each new test**: say so in the entry with the planner's `summary`, and go to Implement with no written tests.

#### Write the tests
Spawn the test writer **once** and keep its id:

```
Agent(subagent_type: "sdlc:test-writer", model: "sonnet",
      prompt: test plan + approved plan + context pack + the work root as an absolute path
              + "Write exactly these cases, report every file you changed and the command that
                 runs each case, and stop.")
```

It ends every turn with a `json` block carrying `summary`, `testFiles`, `command`, `e2eCommand`, `cases` (each with its own `command`), and `blockers`. Nothing returned → `aborted` (stage `write-tests`). Non-empty `blockers` → `escalate` (stage `write-tests`).

When it lands, **fingerprint every created and modified path in `testFiles`** as `agent-pipeline` says, and keep the fingerprints, the commands, and each case's command. Append the `test-writer · tests` entry — every file, the command that runs each case, and `command` and `e2eCommand` — in one tool block. The assignee stays `test-writer-<n>`.

#### Run each new test
**Every `new` case must fail**, because the behavior it checks does not exist yet. A case that passes catches nothing, and a case that does not run is broken. A `guard` case checks behavior that already exists, so it is exempt.

Run each `new` case yourself by the command the writer reported for it — `cd <work root> && <case command>` — in one tool block when the cases share no state. Read the exit code and the output, and judge each case:

- **Fails**: the command exits non-zero, and the case reports a failed assertion, or an error because the module or behavior it drives does not exist yet. That is the result the stage wants.
- **Passes**: the command exits zero.
- **Does not run**: the command selects no test, or the case errors for a reason the new code cannot fix — a syntax error in the test, a missing fixture, a runner configuration error.

The writer's own `observed` value is not the gate; your run is.

- Every `new` case fails → go on.
- A case passes or does not run, **first time** → **one** message carrying every such case and its output: `SendMessage(testWriterId, "These cases did not fail when I ran them. Sharpen each one that passes so it asserts what only the new code delivers; repair each one that did not run. Report every file you changed and every case's command." + cases and output)`. Take the fingerprints again, then run those cases again.
- After the sharpen turn, a case that **still passes** is recorded and the run goes on. A case that **still does not run** → `escalate` (stage `new-tests`): no later stage can make a broken test run.

In one tool block, append a `test-writer · tests` entry when the sharpen turn changed a file or a command, then the `orchestrate-<n> · new tests` entry — each case and how it failed, or that it still passes — and set the assignee to `coding-<n>`. Keep each case that still passes; the `tests` reviewer receives it.

#### Implement
Spawn the coding agent **once** and keep its id:

```
Agent(subagent_type: "sdlc:coding", model: "opus",
      prompt: "Implement the approved plan exactly — no scope creep. Match the context pack conventions.
               Build until the written tests pass. Self-check only what you touched; I run the
               feature's tests and every project check after you."
              + approved plan + context pack + acceptance criteria + the work root
              + test plan + testFiles + each case's command  (or: "No test was written: <summary>"))
```
Its skill obligations, the rules on written tests, and the JSON contract live in the agent definition — do not restate them here; text in the agent file is free, text in this prompt is paid on every spawn.

It ends every turn with a `json` block carrying `summary`, `workItemsCompleted`, `filesChanged`, `decisions`, `blockers`, `testDisputes`, and `notes`. **Every coding turn** — this one, a restore, a fix after the feature's tests, the code review, or the full verification, and the turn after a ruling — goes through these steps in order:

1. Nothing returned → `aborted` (stage `implement`, or the stage that sent the fix).
2. **Compare the fingerprints.** A test file that changed goes back: `SendMessage(codingId, "You changed <files>. Restore each to exactly what the test writer wrote. If a test is wrong, raise a test dispute instead.")`. That spends one feature-test fix cycle; with none left → `escalate` (stage `feature-tests`). Its reply goes through these steps again.
3. Non-empty `blockers` → `escalate` (stage `implement`) with them.
4. On the **first** turn, append the `coding · implement` entry — its `decisions`, which are the code-level calls the plan left open. The assignee stays `coding-<n>`.
5. Non-empty `testDisputes` → **Test defect**.
6. Otherwise go to **Run the feature's tests**. A fix turn goes there too: the feature's tests run after every change to the code.

#### Run the feature's tests
**The feature's tests are every test the feature's tickets wrote.** Collect them from the worklogs:

1. Take the feature the ticket's `feature` property links.
2. Read the worklog of each of that feature's tickets in `done/`, and this ticket's worklog.
3. From each worklog's `test-writer · tests` entries, take the test files and the commands recorded beside them. A later entry overrides an earlier one, and a file it records as deleted drops out.
4. Leave out the end-to-end commands. They run in the full verification.

Run each command yourself — `cd <work root> && <command>` — in one tool block when they share no state, and read each exit code and output. This stage runs no lint, no type check, no full suite, and no end-to-end test. A feature whose tickets recorded no test has nothing to run here: say so in the entry and go on.

- **All pass** → append the `orchestrate-<n> · feature tests` entry — each command, its result, and the fix cycles spent — and set `status` to `review` and the assignee to `code-reviewer-<n>`, in one tool block. Then go to the stage that comes next: Code review, or back to the stage whose fix brought you here.
- **A failure, with a fix cycle left** → `SendMessage(codingId, "The feature's tests fail. Fix the code, not the tests, then stop; I run them again." + each failing command and its failing tests and error lines)`. Its reply goes through Implement's steps. Then run every command again, the failed ones first.
- **A failure, both cycles spent** → `escalate` (stage `feature-tests`) with the failures. A restored test file counts as a cycle.

#### Test defect
**At most ONE dispute round per ticket.** A dispute may come from any coding turn, including a fix after the code review or the full verification, when an existing test broke under a change the ticket meant to make. A second non-empty `testDisputes`, from any turn, → `escalate` (stage `test-dispute`) with the disputes and the earlier rulings. A dispute does not spend the fix cycle of the turn that raised it. Otherwise, set the assignee to `test-planner-<n>` and send:

```
SendMessage(testPlannerId, "The coding agent disputes these tests. Rule on each against the
                            specification." + testDisputes)
```

It returns one `json` block carrying `rulings`, plus `plan` — the full current test plan — when any ruling is `revised`. Nothing returned → `aborted` (stage `test-dispute`). Then:
- Any ruling `escalate` → `escalate` (stage `test-dispute`) with the planner's question. That is a question about the specification, and only the user answers it.
- Any ruling `revised` → `SendMessage(testWriterId, "Apply these revised cases and stop." + the revised rulings)` — spawn the test writer now if the empty plan skipped Write the tests — then take the fingerprints again. A revised test skips Run each new test: the code that makes it pass may already exist.
- Any ruling `upheld` → **one** message to coding carrying every ruling: `SendMessage(codingId, "The test planner ruled on your disputes. Upheld tests stand — build against them. Revised tests have changed. Continue until the written tests pass." + rulings)`. Its reply goes through Implement's steps, which lead to Run the feature's tests.
- Only `revised` rulings → go straight to Run the feature's tests. When they fail, the fix message to coding carries the rulings with the failures.

Append the `test-planner · test dispute` entry — each disputed test, the claim, the ruling, and the reason — and, on a revision, a `test-writer · tests` entry, in one tool block, with the assignee set to `coding-<n>`. After the feature's tests pass, the run resumes the stage the dispute interrupted.

#### Code review
The `status` is `review`. Spawn **four** code reviewers **in one tool block**, one per focus — `correctness`, `conventions`, `security`, and `tests` — and keep all four ids:

```
Agent(subagent_type: "sdlc:code-reviewer", model: <opus on high risk, else sonnet>,
      prompt: "Focus: <focus>. Review the change the coding agent made, against the approved plan
               and the acceptance criteria. Do not run the suite; I run every check."
              + the ticket path + approved plan + acceptance criteria + context pack + the work root
              + the coding agent's filesChanged + the review target ("the uncommitted changes
                against HEAD, untracked files included")
              + (Focus: tests only) the test plan + the test writer's testFiles
                + each new case that still passed after sharpening)
```
What each focus judges, the severity rules, and the JSON contract live in the agent definition — do not restate them.

**Model tier:** the same high-risk test as Review the plan — **opus** when `addsPublicApi == true` **or** `addsDependency == true` **or** `filesTouched > 5`, **sonnet** otherwise. Unlike the plan review, the code review has **no skip gate**. Every focus runs on every ticket: a passing suite says nothing about a missed acceptance criterion, a broken layer boundary, or an injection path.

Each reviewer ends with a `json` block carrying `focus`, `verdict` (`APPROVED` | `CHANGES_REQUESTED`), `summary`, and `issues`. Match each block to its reviewer by `focus`. **The review passes only when all four return `APPROVED`.**

- A reviewer returned nothing → `aborted` (stage `code-review`).
- **All four `APPROVED`** → append one `code-reviewer · code review` entry per focus, naming the focus, in one tool block, then Run full verification. Keep every minor issue as a recommendation; it blocks nothing.
- **Any `CHANGES_REQUESTED`, not yet fixed** → in one tool block, append one entry per focus and set `status` to `in progress` and the assignee to `coding-<n>`. Then send **one** message carrying every blocking issue from every reviewer: `SendMessage(codingId, "The code review found the following. Fix ONLY what is needed to clear them — stay within the approved plan, change no test, then stop." + blocking issues)`. Its reply goes through Implement's steps, so the feature's tests run again; a failure there spends that stage's remaining fix cycles. When they pass, re-review **only the reviewers that blocked**, in one tool block: `SendMessage(codeReviewerId, "Re-review the fix below; judge each prior issue as fixed or still open." + the coding agent's summary + filesChanged)`. A reviewer that approved stays approved.
- **Any `CHANGES_REQUESTED`, already fixed once** → **`escalate`** (stage `code-review`) with the remaining issues.

#### Run full verification
Run **every check command in the context pack** yourself, as parallel Bash calls in one tool block, each as `cd <work root> && <command>`:

- the `command` of every entry in `verificationCommands` — one per `check`: lint, type check, and the full test suite;
- the end-to-end suite, only when the `e2eDecision` is yes: the pack's `e2eCommand`, or the test writer's `e2eCommand` when the pack's is `"none"` because this ticket stood the suite up.

A check passes when its command exits zero. **A check the project lacks** — an entry whose `command` is `"none"` — is reported as skipped, with its reason, never as passed. A skipped end-to-end run is never presented as green.

- **All pass** → Finish.
- **A failure, not yet fixed** → in one tool block, set the assignee to `coding-<n>`; the `status` stays `review`. Then send **one** message carrying every failure: `SendMessage(codingId, "The full verification failed. Fix ONLY what is needed to clear these failures — stay within the approved plan, change no test, then stop." + each failing command and its error lines)`. Its reply goes through Implement's steps, so the feature's tests run first. Then run the failed checks again, and only when they pass, run the rest.
- **A failure, already fixed once** → `escalate` (stage `verification`) with the failures.

The `orchestrate-<n> · verification` entry names each command and its result, each skipped check and why, and what the fix changed.

#### Finish
Run the **`ticket-board`** skill's **Finishing a ticket** transition in one step: `status` `done` with `assigned` and `claimed` removed, the usage added, the ticket and its worklog moved to `done/`, the roadmap row deleted, and the worklog entries appended — `orchestrate-<n> · verification`, then the closing `orchestrate-<n> · done`: what shipped, each recommendation nobody acted on, and each note file. In the same step, write the coding agent's latest `notes` with `create-note.py`, as `agent-pipeline` says, with `--run orchestrate-<n>`. A correction this run forced on a *remaining* ticket — a constraint the code review found, a dependency that turned out wrong — is rewritten in the same step.

**Act on the result.** Whichever it is, the entry of the stage that ended the run goes into the worklog — a run that failed is exactly the run whose record matters. `agent-pipeline` defines the three outcomes and `ticket-board` holds the transition each one writes:
- **`completed`** → **Finishing a ticket**, as above. Keep whether the review ran, the reviewers' summaries, and the test and verification details for the report.
- **`escalate`** → **Stopping without finishing**. Surface the `stage`, the reason, and any issues, failures, or blockers for the user.
- **`aborted`** → **Stopping without finishing**, with the outcome entry naming the stage and the agent that returned no result.

Report only after the files are updated.

### 4. Completion Report
```markdown
## Task Complete: [ID] — [Title]

- [x] Planning — approved ([0 or 1] revision; [N] open questions answered) (or: review skipped by the risk gate)
- [x] Test plan — [N] cases ([unit / integration / e2e counts]), [M] left untested on purpose (or: no case — [why])
- [x] Tests written first — [N] failed before the code; [K] still passed after sharpening ([ids])
- [x] Implementation — the feature's tests pass ([F] commands from [T] tickets; [0–2] fix cycles); [0 or 1] test dispute ([rulings])
- [x] Code review — correctness, conventions, security, and tests approved ([0 or 1] fix cycle)
- [x] Full verification — [each check]: passed (or: skipped — [reason]); [0 or 1] fix cycle
- [x] Status — ticket `done`, unassigned, unclaimed, and moved to `done/` with its worklog; roadmap row deleted

Work root: `[code]` — `[absolute path]`
Recommendations: [each minor review issue, or "none"]
Needs a person: [each note file and its title, or "nothing"]

[Summary of what was accomplished]
```

## Failure Handling
`agent-pipeline` holds the outcome vocabulary and `ticket-board` the **Stopping without finishing** transition. This command's caps are the ones to apply mechanically, with no improvised extra cycle:

| Cap | Value | At the cap |
| --- | --- | --- |
| Plan revisions | 1 | `escalate` (stage `plan-review`) |
| Sharpen rounds for a new test that does not fail | 1 | A case that still passes is recorded and the run goes on; a case that still does not run → `escalate` (stage `new-tests`) |
| Feature-test fix cycles, a restored test file included | 2 | `escalate` (stage `feature-tests`) |
| Test dispute rounds | 1 | A second dispute → `escalate` (stage `test-dispute`) |
| Code review fix cycles | 1 | `escalate` (stage `code-review`) |
| Full verification fix cycles | 1 | `escalate` (stage `verification`) |
| Re-asks for a missing result block, per agent turn | 1 | `aborted` at that stage |

- **`escalate`** also when an open question gets no settling answer, when the test writer or the coding agent reports a blocker, and when the test planner rules a dispute `escalate`.
- **`aborted`** when an agent returns no usable result, at any stage.
- Never mark a task complete unless the feature's tests passed, all four code reviewers approved, **and** every check passed.

## Rules
The four skills carry the rules they own — `agent-pipeline` for the spawn-once, one-tool-block, and thin-prompt mechanics, `ticket-board` for the transitions and the roadmap, `sdlc-structure` for the paths, `technical-writing` for the prose. What is this command's own:
- **One task at a time.** Do not execute the whole roadmap.
- **Resolve the work root before the ticket starts**, record it in the worklog, and pass it to every agent. Never let an agent infer which repository it is working in.
- **Load every skill in the table before the stage that needs it.** They are the rules; this file is the sequence.
- **The decisions are made before the run.** The planner reads them from the ticket and the feature folder. A question the documents leave open goes to the user in one round, and its answer goes into the plan entry; a question the user cannot settle sends the ticket back to `/plan`.
- **You run every check.** Each new test, the feature's tests, and the full verification are commands you run and read. No agent's report of a passing check counts.
- **The code review always runs, from four focuses.** The task passes only when all four return `APPROVED`. Only the plan review has a skip gate.
- **Apply the gates mechanically.** The review-skip gate (≤2 files, no dep, no API, criteria auto-checkable), the high-risk test (new API/dep or >5 files), and every cap in the table are fixed thresholds.
- **Tests before code, and the coder never touches them.** The test planner drafts from the specification before it sees the plan, the test writer writes the tests before coding starts, every new test fails before the code exists, and a test file whose fingerprint moved goes back to be restored. A test is changed only by a sharpen turn or a `revised` ruling. Only an empty test plan skips the test stages.
- **You write the status, the assignee, and the worklog** — at the boundaries in the table and at every exit. No agent writes any of them.
- **Never proceed without approval** on the selected task, and never start a task whose dependencies are incomplete.
- **Be explicit about failures** and propose next steps.
