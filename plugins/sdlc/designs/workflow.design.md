---
type: design
subject: workflow
updated: 2026-10-13
tags:
  - sdlc/design
related:
  - "[[SDLC-framework.design]]"
  - "[[work.design]]"
  - "[[ticket.design]]"
  - "[[feature.design]]"
  - "[[registry.design]]"
---
# Workflow

The workflow turns one planned [[glossary#Ticket|ticket]] into code that has been verified and reviewed. One [[glossary#Run|run]] takes the ticket from `backlog` to `done`, or stops it as `blocked` with the reason written down.

## 1. Foundations

- **One run drives one ticket.** The next ticket is the next run.
- **The [[glossary#Orchestrator|orchestrator]] is the only writer.** It alone writes the ticket, its [[glossary#Worklog|worklog]], and the [[glossary#Roadmap|roadmap]]. Every agent reports to it and writes no document.
- **A status change is one step.** The orchestrator rewrites `status`, `assigned`, and `updatedAt`, moves the file to its [[glossary#Bucket|bucket]], and edits the roadmap together.
- **Every agent works in the [[glossary#Work root|work root]] it is given.** The orchestrator resolves it once, before the first agent starts, and passes it to each agent as an absolute path.
- **[[glossary#Gate|Gates]] and caps are mechanical.** A threshold is a number, a cap of one means one, and no run adds a cycle because the next one looks close.
- **A ticket is `done` only when verification passed and the code review approved.** A passing suite alone never finishes a ticket.
- **Tests come before the code, from the specification, and from someone other than the coder.** One agent decides what to test, another writes the tests, and only then does `coding` build. The code is done when it passes tests it could not shape.
- **A test earns its place by the bug it catches.** The [[glossary#Test plan|test plan]] holds the fewest tests that catch the bugs this change could ship, each of the cheapest type that catches it. Coverage is never a reason to write one.

## 2. Parts

### 2.1 Structure

![[workflow.excalidraw]]
*The stages of one run in order, the status the ticket holds in each, and the loops a run may take: a plan revision, a test dispute, a targeted fix, and a fix after verify and code review.*

A run is one orchestrator and the agents it drives. Questions go to the **answerer**: the person in an interactive run, the `cto` agent in an autonomous one.

| Agent                    | [[glossary#Stage\|Stage]]   | Answers                                                       | Returns                                                                  |
| ------------------------ | --------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------------ |
| `feature-interviewer`    | Interview                   | What must be decided before planning                          | Open decisions, each with options and a recommendation                   |
| `implementation-planner` | Plan                        | How the ticket is built                                       | A [[glossary#Context pack\|context pack]], then the plan and its risk profile |
| `plan-reviewer`          | Plan review                 | Does the plan meet every acceptance criterion and fit the code | `APPROVED` or `CHANGES_REQUESTED`, with issues                           |
| `test-planner`           | Test plan, test dispute     | Which bugs could this change ship, and which fewest, cheapest tests catch them | The test cases, each with the bug it catches and its type, and what goes untested and why; a ruling on each disputed test |
| `test-writer`            | Write tests                 | Writes the planned tests before the code exists               | The test files, the command that runs them, and proof that each test fails for the expected reason |
| `coding`                 | Implement                   | Builds the approved plan until the written tests pass         | The files changed, the calls it made, any blocker, and any [[glossary#Test dispute\|test dispute]] |
| `verify`                 | Targeted verify, Verify     | Does the change pass the tests it was built against, then the project's checks | Pass, fail, or skipped, per check                                        |
| `code-reviewer`          | Code review                 | Is the change the right code, and all of it                   | `APPROVED` or `CHANGES_REQUESTED`, with issues                           |
| `cto`                    | Any question, autonomous only | The call a person would make                                | A decision, what it beat, and the cost it accepted                       |

- **Every agent ends its reply with one machine-readable result block.** The orchestrator drives the run from that block alone. It asks once for a missing or malformed block; a second miss aborts the run.
- **Each role starts once per run and is resumed for every later turn.** A resumed agent keeps what it read, so the orchestrator sends only what changed.
- **`verify` starts fresh for every check.** A result from before a fix proves nothing about the code after it.
- **Only `verify` runs the project's checks.** `coding` checks only what it touched, `test-writer` runs only the tests it wrote, and `code-reviewer` runs no checks.
- **Only `test-writer` writes the ticket's tests, and `coding` never changes them.** A test `coding` believes is wrong becomes a test dispute, which `test-planner` rules on. `coding` never weakens, skips, or deletes a test to get past it.
- **`test-planner` reads the specification before the plan.** It derives the cases from the ticket's criteria, the design docs, and the decisions, and reads the plan only to learn where each test attaches. Cases drawn from the plan would test what the code does, not what it must do.

### 2.2 What a run reads

The ticket, the feature note its `feature` property links, and the design docs that feature lists. The PRD of the feature's project, when the project has one. The worklog, when the ticket resumes from `blocked`. The [[glossary#Registry|registry]], to resolve the work root.

## 3. The run

### 3.1 Behavior

| Stage                  | `status`      | `assigned`                   | Worklog entry when it lands                              |
| ---------------------- | ------------- | ---------------------------- | -------------------------------------------------------- |
| Pick                   | `backlog`     | unchanged                    | none                                                     |
| Start                  | `in progress` | `feature-interviewer-<n>`    | `<orchestrator> · start`                                 |
| Interview and scout    | `in progress` | `feature-interviewer-<n>`    | `feature-interviewer · interview`                        |
| Plan                   | `in progress` | `implementation-planner-<n>` | `implementation-planner · plan`                          |
| Plan review            | `in progress` | `plan-reviewer-<n>`          | `plan-reviewer · plan review`                            |
| Test plan              | `in progress` | `test-planner-<n>`           | `test-planner · test plan`                               |
| Write tests            | `in progress` | `test-writer-<n>`            | `test-writer · tests`                                    |
| Implement              | `in progress` | `coding-<n>`                 | `coding · implement`                                     |
| Test dispute           | `in progress` | `test-planner-<n>`           | `test-planner · test dispute`                            |
| Targeted verify        | `in progress` | `verify-<n>`                 | `verify · targeted`                                      |
| Verify and code review | `review`      | `code-reviewer-<n>`          | `verify · verification`, then `code-reviewer · code review` |
| Finish                 | `done`        | removed                      | `<orchestrator> · done`                                  |

`<n>` is the run's number; see 4. Claims.

**Pick.** The orchestrator lists the ready tickets in roadmap order, which is priority order. A ticket is ready when it sits in `backlog/` unclaimed and every ticket it depends on is `done`. A resumable `blocked` ticket is ready too; see 5. States. The answerer picks one ticket, and says whether it gets end-to-end tests. Yes is recommended only when the ticket adds or changes a user-facing flow that no end-to-end test crosses. Picking nothing ends the run with nothing written.

**Start.** The orchestrator writes its [[glossary#Claim|claim]], resolves the work root, and confirms it can write there. Then it starts the ticket in one step: `status`, `assigned`, the move to `in-progress/`, the roadmap row, and the worklog. The opening entry names the ticket, the work root with the evidence that settled it, and the end-to-end decision. A resumed ticket keeps its worklog, and the entry is appended.

The work roots come from the ticket's `repositories`, which names them by registry code:

1. Codes the registry has are the work roots.
2. An empty field, or a code the registry lacks, starts the `repo-resolver` agent. It narrows the registry's candidates by evidence — the design docs, the ticket's text, its dependencies' `repositories`, and which tree already holds the code the ticket changes — and returns the codes.
3. A settled answer is written onto the ticket in the Start step, so no later run resolves it again.
4. When the evidence leaves it open, the answerer chooses among the candidates; an autonomous run has no answerer for this and ends for a person. The orchestrator never guesses.

**Interview and scout.** Two agents start at once. The interviewer reads the documents and the code, and returns the open decisions. The planner surveys the same code, researches current practice, returns the context pack, and waits. The answerer settles every decision in one round. The interview entry records each decision, what it beat, and each assumption confirmed.

**Plan.** The planner receives the decisions as fixed constraints and writes the plan from what it already read. It returns the plan with a risk profile: the files touched, whether it adds a dependency or a public interface, and whether a command can check every acceptance criterion. The plan itself is kept nowhere. The plan entry records the direction it took and the approach it turned down.

**Plan review.** The review gate in 3.2 Gates decides whether a review runs. The reviewer reads the context pack while the plan is still being written. On `CHANGES_REQUESTED`, the planner revises once and the same reviewer reviews again. A second `CHANGES_REQUESTED` is an escalation.

**Test plan.** `test-planner` starts when the decisions reach the planner, and works from the specification alone while the plan is written and reviewed: the ticket's criteria, the design docs, the decisions, and the end-to-end decision. When the plan is approved, it receives the plan and attaches each case to the public interface the plan exposes. Each case names the bug it catches, the input that exposes the bug, the expected result, and the cheapest type that catches it: unit, then integration, then end-to-end. An end-to-end case covers a critical path only, and only when the end-to-end decision says yes. The plan also lists what goes untested and why. A plan with no case — a change no test could catch failing, such as a copy edit or a config value — skips Write tests and Targeted verify, and the entry says why. The test plan entry records each case in one line and each exclusion.

**Write tests.** `test-writer` writes the cases in the test plan and nothing else: no production code, and no case the plan does not hold. It may add the fixture or helper a case needs. It runs the tests and reports, per case, that each fails because the behavior is missing, and not because the test is broken. A case that already passes catches nothing. The writer sharpens it once and reports it if it still passes, unless the plan marks it as a guard on behavior that already exists. The orchestrator records a fingerprint of every file the writer changed. The tests entry records the files, the command that runs them, and each case that did not fail as expected.

**Implement.** `coding` builds the approved plan until the written tests pass, and nothing beyond it. It writes no test of its own and never changes a file `test-writer` wrote. When it lands, the orchestrator compares the fingerprints. A changed test file goes back to `coding` to restore, and that costs a targeted fix cycle. A blocker it reports is an escalation. The implement entry records the calls the plan left open.

**Test dispute.** When `coding` concludes that a test, not its code, is wrong, it finishes every other work item it can, then returns a dispute instead of working around the test. The dispute names the test, what is wrong with it, the evidence, and the change it proposes. `test-planner` rules on each disputed test:

| Ruling     | What happens                                                                                     |
| ---------- | ------------------------------------------------------------------------------------------------ |
| `upheld`   | The test stands. `coding` receives the reason and builds against it                              |
| `revised`  | The test plan changes. `test-writer` rewrites the test, and `coding` builds against the new one  |
| `escalate` | The dispute turns on what the specification means, which only the answerer can settle           |

A dispute may come from any `coding` turn, including a fix after the full verify, when an existing test broke under a change the ticket meant to make. A ticket gets one dispute round; a second dispute is an escalation. The dispute entry records each dispute, its ruling, and the reason.

**Targeted verify.** A fresh `verify` runs only the tests related to the change: the unit and integration tests `test-writer` wrote, and the existing tests of the files `coding` changed when the project's runner can select them. It runs no lint, no full suite, and no end-to-end test; written end-to-end cases run in the full verify. All passing moves the ticket to Verify and code review. Otherwise `coding` receives the failures. A ticket gets two targeted fix cycles, and a third failure is an escalation.

**Verify and code review.** The status becomes `review`, and `verify` and `code-reviewer` start at the same time on the same change. `code-reviewer` also gets the test plan, and judges whether the tests match it. The ticket passes when every check passes and the review approves. Otherwise the status returns to `in progress`, and `coding` receives every failure and every blocking issue in one message. After the fix the status is `review` again. A fresh `verify` runs the failed checks first, and `code-reviewer` reviews again only when it had blocked. A second failure is an escalation. A skipped check is reported as skipped, never as passed. A minor review issue becomes a recommendation and blocks nothing.

**Finish.** In one step, the orchestrator:

- sets `status` to `done` and removes `assigned` and `claimed`;
- writes the usage properties; see 6. Variation and limits;
- moves the ticket and its worklog to `done/`;
- appends the closing entry: what shipped, and each recommendation nobody acted on;
- deletes the roadmap row;
- corrects every remaining ticket this work proved wrong.

### 3.2 Gates

| Gate               | Rule                                                                                                          |
| ------------------ | ------------------------------------------------------------------------------------------------------------- |
| Plan review skip   | The review is skipped only when the plan touches at most two files, adds no dependency and no public interface, and a command can check every acceptance criterion |
| High risk          | The plan adds a public interface, adds a dependency, or touches more than five files                         |
| Test stages skip   | Write tests and Targeted verify are skipped only when the test plan holds no case                             |
| Tests untouched    | Every file `test-writer` changed keeps its fingerprint after every `coding` turn                              |
| Done               | Every check passed, and the code review returned `APPROVED`                                                   |

- **A high-risk plan gets two reviewers**, one judging correctness and completeness, one judging fit with the codebase. Either one's `CHANGES_REQUESTED` sends the plan back. A high-risk change also gets the stronger model for its code review.
- **The code review has no skip gate.** It is the last check between a change and `done`.

## 4. Claims

The claim stops two runs from building the same ticket at once.

- **The claim is `<command>-<n>`**: `orchestrate-2`. `<n>` is the lowest positive number no other claim in `work/` uses.
- **The run's agents carry the same number.** `coding-2` works for `orchestrate-2`, so `assigned` names the run as well as the role.
- **The claim is written first and read back.** A run that reads back another run's claim drops the ticket and picks again.
- **A roadmap run claims the whole dependency cluster**, on every ticket at once, and reads every one back. It holds those claims across its sessions until each ticket is `done` or the run ends; see 6.1 The roadmap run.
- **A claimed ticket is never ready for another run.**
- **One checkout holds one build at a time.** A run whose work root another claimed `in progress` or `review` ticket holds releases its claim and picks again. Two builds in one tree would each check the other's changes. A run worktree is a checkout of its own, so a roadmap run never waits on another run's work root.
- **Every exit removes the claim**: finish, escalation, and abort. A roadmap run's end removes the claims on every ticket of its cluster that is not `done`.

**Weakness:** a file cannot hold a lock, so the read-back narrows the race without closing it. A run that dies without exiting leaves its claim for a person to remove.

## 5. States

| State                          | What happens                                                                                                                                  |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| No ready ticket                | The run says nothing is ready, names planning as the way to add work, and writes nothing                                                     |
| Work root unresolved or unwritable | The run stops before Start. It removes its claim, writes nothing else, and names the access the session needs                            |
| Completed                      | The Finish step in 3.1 Behavior                                                                                                               |
| Escalated                      | `status` becomes `blocked`, and `blocked_by` holds one line naming what a person must decide. `assigned` and `claimed` are removed. The outcome entry names the stage, what is open, and what the next run picks up |
| Aborted                        | As escalated. The `blocked_by` line names the stage and the agent that returned no result                                                    |
| Waits on another ticket        | Found during the run: `status` becomes `blocked`, and `blocked_by` holds that ticket's ID                                                     |
| Resumable                      | A `blocked` ticket whose `blocked_by` holds only IDs of `done` tickets, or none. A person clears an outside cause by deleting its line        |
| Resumed                        | The run removes `blocked_by` and runs every stage again, with the worklog as input to each agent                                              |
| Status and bucket disagree     | The run moves the file to its status's bucket before anything else; see [[work.design#3. Behavior\|Work]]                                     |

## 6. Variation and limits

|                       | Interactive                            | Autonomous                                      | Quick                       |
| --------------------- | -------------------------------------- | ----------------------------------------------- | --------------------------- |
| Started by            | A person, one ticket per command       | A [[glossary#Roadmap run\|roadmap run]], one fresh session per ticket | A person      |
| Answerer              | The person                             | `cto`                                           | The person                  |
| Interview             | Skipped for a ticket with no product, design, or architecture fork | Always                  | Never                       |
| Plan review           | Gated; see 3.2 Gates                   | Gated                                           | Always, one reviewer        |
| Test plan and tests   | Always                                 | Always                                          | Always                      |
| At a cap              | Escalation                             | A `cto` ruling, then escalation                 | Escalation                  |
| Claimed               | The ticket                             | Its [[glossary#Dependency cluster\|dependency cluster]] | The ticket          |
| Builds in             | The work root                          | A [[glossary#Run worktree\|run worktree]] of each work root | The work root    |
| Finished code         | Left uncommitted for the person        | One commit per ticket on the run branch         | Left uncommitted            |
| A stopped ticket's code | Left in the work root                | Discarded from the run worktree; the ticket and worklog are kept | Left in the work root |
| After a stopped ticket | —                                     | The roadmap run ends                            | —                           |

### 6.1 The roadmap run

An autonomous run is one ticket of a roadmap run. The launcher starts a fresh session per ticket, so a long roadmap never runs out of context, and the roadmap run carries one name, `run-roadmap-<n>`, across every session. `<n>` is the lowest positive number that no claim in `work/` and no branch in a registered work root uses.

![[run-roadmap.excalidraw]]
*The roadmap run: selecting and claiming a ticket with its dependency cluster, a claim lost to another run, a run worktree per work root, the orchestration pipeline as one step, the two commits, and every end that needs a person.*

| Step                          | What happens                                                                                                  | When it fails                                    |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| Select the next ticket        | A ticket the roadmap run already claims comes first. Otherwise the orchestrator lists the candidates in roadmap order: every ticket not `done`, unclaimed, whose cluster holds no ticket another run claims and no ticket `blocked` on something other than a cluster ticket | No ticket left on the roadmap: the run ends, roadmap done. Tickets left and no candidate: the run ends for a person |
| Can it run                    | `cto` picks one candidate and calls the end-to-end question, or hands the pick back                           | A hand-back ends the run for a person            |
| Confirm                       | Automatic. Nobody is asked; the `cto`'s pick stands                                                           | —                                                |
| Claim its dependency cluster  | The run writes its claim on every ticket of the cluster and reads every one back. A ticket the run already claims keeps its claim | Another run's claim read back: the run releases what it wrote and selects again. Lost three times in a row, the run ends for a person |
| Identify the work roots       | The `repositories` of the ticket to build and of its direct dependencies. A ticket with none gets them from the `repo-resolver` agent, written onto it, as in 3.1 Start | The agent cannot settle them: the run ends for a person, naming the candidates |
| Create a run worktree         | One per work root, on branch `run-roadmap-<n>` from that work root's current commit, made once and reused by every later ticket of the run | The run ends for a person, naming the work root and the git error |
| Pick up the ticket            | The cluster's first ticket whose dependencies are all `done` — the selected ticket itself only when it depends on nothing unfinished. Start as in 3.1 | —                                                |
| Run the orchestration pipeline | Interview to Verify and code review, as in 3.1, in the run worktrees                                         | Not completed: the ticket stops as in 5. States, its code is discarded from the run worktrees, and the run ends for a person |
| Commit the code               | One commit per run worktree the ticket changed, on the run branch, following that work root's own convention  | A rejected commit stops the ticket as `blocked`, with the hook's reason in `blocked_by` |
| Commit the documents          | One commit in the framework root holding the ticket, its worklog, and the roadmap edit, when the framework root is a git tree | As for the code                                  |
| `--max` reached               | The launcher counts tickets. Under the limit, the next session selects again                                  | At the limit, the run ends                       |

- **Every end reports what happened and how to resume the run.** It releases the claims on every ticket of the cluster that is not `done`, and keeps the branch and the run worktrees. Resuming starts the same roadmap run again by its name; it reuses the branch and the worktrees and claims afresh.
- **The person's checkout is never touched.** A run worktree starts from the work root's current commit, so an uncommitted change in the checkout is not part of it, and the run builds in its worktree alone.
- **The run never pushes, merges, or amends.** A person reviews the run branch and merges it.
- **A run worktree is clean between tickets.** A finished ticket is committed and a stopped one is discarded, so the next ticket starts from the last commit. A worktree left dirty ends the run.

**A `cto` ruling** is one of five:

| Ruling      | What the run does                                                                  |
| ----------- | ---------------------------------------------------------------------------------- |
| `retry`     | One more cycle at that stage, carrying the ruling's guidance                       |
| `rescope`   | Finishes a narrower ticket; the dropped part becomes a new `backlog` ticket        |
| `defer`     | Escalates the ticket                                                               |
| `stop-run`  | Escalates the ticket, and the launcher starts no further run                       |
| hand back   | Escalates the ticket for a person to decide                                        |

**The caps:**

| Cap                                   | Value |
| ------------------------------------- | ----- |
| Tickets per run                       | 1     |
| Plan revisions                        | 1     |
| Targeted fix cycles, a restored test file included | 2 |
| Test dispute rounds per ticket        | 1     |
| Fix cycles after verify and code review | 1   |
| Re-asks for a missing result block, per agent turn | 1 |
| `cto` rulings per stage               | 1     |
| `cto` rulings per ticket              | 2     |

**A ticket that changes two work roots keeps both.** Each work root gets its own verification, code review, and commit, and the ticket passes only when both pass.

**Usage accumulates across runs.** The orchestrator adds each agent's time and tokens as its turn lands. At every exit it adds the run's totals to the ticket's `timing`, `tokens`, and `cost`, so a resumed ticket's numbers cover every run.
