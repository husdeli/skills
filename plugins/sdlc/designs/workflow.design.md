---
type: design
subject: workflow
updated: 2026-10-20
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
- **The decisions are made before the run.** Planning interviews the person, with the `feature-interviewer` agent surfacing the decisions a request needs, and writes each settled choice into the ticket's `Decisions`, the feature, and its design docs. The run reads them; it holds no interview.
- **The [[glossary#Orchestrator|orchestrator]] is the only writer.** It alone writes the ticket, its [[glossary#Worklog|worklog]], and the [[glossary#Roadmap|roadmap]]. Every agent reports to it and writes no document, and the orchestrator records each report in the worklog — so the worklog knows every test the ticket wrote.
- **A status change is one step.** The orchestrator rewrites `status`, `assigned`, and `updatedAt`, moves the file to its [[glossary#Bucket|bucket]], and edits the roadmap together.
- **Every agent works in the [[glossary#Work root|work root]] it is given.** The orchestrator resolves it once, before the first agent starts, and passes it to each agent as an absolute path.
- **A check is a command, not a judgment.** The orchestrator runs every test and every project check itself and reads the result. No agent reports a check as passed. `/orchestrate-quick` alone hands its checks to a fresh `verify` agent, whose report is judged by the same rule; see 6. Variation and limits.
- **[[glossary#Gate|Gates]] and caps are mechanical.** A threshold is a number, a cap of one means one, and no run adds a cycle because the next one looks close.
- **A ticket is `done` only when the [[glossary#Feature's tests|feature's tests]] pass, every code reviewer approves, and every project check passes.** A passing suite alone never finishes a ticket.
- **Tests come before the code, from the specification, and from someone other than the coder.** One agent decides what to test, another writes the tests, the orchestrator proves each one fails, and only then does `coding` build. The code is done when it passes tests it could not shape.
- **A test earns its place by the bug it catches.** The [[glossary#Test plan|test plan]] holds the fewest tests that catch the bugs this change could ship, each of the cheapest type that catches it. Coverage is never a reason to write one. The `test-strategy` skill holds these rules, and both test agents load it.

## 2. Parts

### 2.1 Structure

![[workflow.excalidraw]]
*The stages of one run in order — which are deterministic steps the orchestrator runs and which are agents — what the plan reads, the skill both test agents load, and the loops a run may take: a plan revision, a test that does not fail, a test defect, and a fix after the feature's tests, the code review, or the full verification.*

A run is one orchestrator and the agents it drives. Questions go to the **[[glossary#Answerer|answerer]]**: the person in an interactive run, the `cto` agent in an autonomous one.

| Agent                    | [[glossary#Stage\|Stage]]   | Answers                                                       | Returns                                                                  |
| ------------------------ | --------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------------ |
| `implementation-planner` | Plan, revise the plan       | How the ticket is built, from the feature folder and the code | A [[glossary#Context pack\|context pack]] with the project's check commands, then the [[glossary#Implementation plan\|plan]] and its risk profile — or, instead of the plan, the forks the documents leave open |
| `plan-reviewer`          | Review the plan             | Does the plan meet every acceptance criterion and fit the code | `APPROVED` or `CHANGES_REQUESTED`, with issues                           |
| `test-planner`           | Plan the tests, test defect | Which bugs could this change ship, and which fewest, cheapest tests catch them | The test cases, each with the bug it catches and its type, and what goes untested and why; a ruling on each disputed test |
| `test-writer`            | Write the tests             | Writes the planned tests before the code exists               | The test files, the command that runs each case, the end-to-end command, and any case it cannot write |
| `coding`                 | Implement, fix              | Builds the approved plan until the tests pass                 | The files changed, the calls it made, any blocker, any [[glossary#Test dispute\|test dispute]], and each [[glossary#Note\|note]] for a person |
| `code-reviewer`          | Code review                 | Is the change the right code, judged from one focus           | `APPROVED` or `CHANGES_REQUESTED`, with issues                           |
| `cto`                    | Any question, autonomous only | The call a person would make                                | A decision, what it beat, and the cost it accepted                       |
| `repo-resolver`          | Start                       | Which work roots the ticket is built in                       | The registry codes and the evidence, or the candidates when it cannot settle them |
| `verify`                 | Checks, `/orchestrate-quick` only | Does each check command pass                            | Pass or fail per command, and each check the project lacks as skipped     |
| `feature-interviewer`    | Before the run, in `/plan`  | Which decisions a request needs from the person               | The open decisions with their options, and every assumption it made instead |

- **The code review is four `code-reviewer` agents at once, one per focus**, on every ticket:

  | Focus          | Judges                                                                              |
  | -------------- | ----------------------------------------------------------------------------------- |
  | `correctness`  | Bugs, edge cases, and whether every acceptance criterion is met                      |
  | `conventions`  | Fit with the codebase, its architecture, and the plugin's coding skills              |
  | `security`     | Authentication, input handling, secrets, and injection                               |
  | `tests`        | Whether the tests match the test plan and catch the bugs it named                    |

  A reviewer given no focus judges from all four at once. `/orchestrate-quick` and `/review` each start one such reviewer.

- **Every agent ends its reply with one machine-readable result block.** The orchestrator drives the run from that block alone. It asks once for a missing or malformed block; a second miss aborts the run.
- **Each role starts once per run and is resumed for every later turn.** A resumed agent keeps what it read, so the orchestrator sends only what changed. Each review focus is its own role.
- **Only the orchestrator runs the project's checks**, or the `verify` agent in `/orchestrate-quick`. `coding` checks only what it touched, `test-writer` runs only the tests it wrote, and no reviewer runs a check.
- **Only `test-writer` writes the ticket's tests, and `coding` never changes them.** A test `coding` believes is wrong becomes a test dispute — a test defect — which `test-planner` rules on. `coding` never weakens, skips, or deletes a test to get past it.
- **`test-planner` reads the specification before the plan.** It derives the cases from the ticket's criteria, its decisions, and the design docs, and reads the plan only to learn where each test attaches. Cases drawn from the plan would test what the code does, not what it must do.

### 2.2 What a run reads

The ticket, with its `Decisions`. The feature folder its `feature` property links: the feature note and the design docs it lists, and the solution designs in `designs/` that underpin every feature. The PRD of the feature's project, when the project has one. The worklogs of the feature's other tickets, for the tests the feature already has. The worklog, when the ticket resumes from `blocked`. The [[glossary#Registry|registry]], to resolve the work root.

## 3. The run

### 3.1 Behavior

| Stage                  | `status`      | `assigned`                   | Worklog entry when it lands                              |
| ---------------------- | ------------- | ---------------------------- | -------------------------------------------------------- |
| Pick                   | `backlog`     | unchanged                    | none                                                     |
| Start                  | `in progress` | `implementation-planner-<n>` | `<orchestrator> · start`                                 |
| Plan                   | `in progress` | `implementation-planner-<n>` | `implementation-planner · plan`                          |
| Review the plan        | `in progress` | `plan-reviewer-<n>`          | `plan-reviewer · plan review`                            |
| Plan the tests         | `in progress` | `test-planner-<n>`           | `test-planner · test plan`                               |
| Write the tests        | `in progress` | `test-writer-<n>`            | `test-writer · tests`                                    |
| Run each new test      | `in progress` | `test-writer-<n>`            | `<orchestrator> · new tests`                             |
| Implement              | `in progress` | `coding-<n>`                 | `coding · implement`                                     |
| Run the feature's tests | `in progress` | `coding-<n>`                | `<orchestrator> · feature tests`                         |
| Test defect            | `in progress` | `test-planner-<n>`           | `test-planner · test dispute`                            |
| Code review            | `review`      | `code-reviewer-<n>`          | `code-reviewer · code review`, one per focus             |
| Run full verification  | `review`      | `coding-<n>` while it fixes  | `<orchestrator> · verification`                          |
| Finish                 | `done`        | removed                      | `<orchestrator> · done`                                  |

`<n>` is the run's number; see 4. Claims.

**Pick.** The orchestrator reads every ticket it may offer, because the ticket is the record: a roadmap row whose priority, status, or dependencies disagree with its ticket is corrected and re-sorted before the pick. It then lists the [[glossary#Ready|ready]] tickets in roadmap order, which is priority order. A ticket is ready when it sits in `backlog/` unclaimed and every ticket it depends on is `done`. A resumable `blocked` ticket is ready too; see 5. States. The answerer picks one ticket, and settles the [[glossary#End-to-end decision|end-to-end decision]]. Yes is recommended only when the ticket adds or changes a user-facing flow that no end-to-end test crosses. Picking nothing ends the run; the corrected rows are the only thing it wrote.

**Start.** The orchestrator writes its [[glossary#Claim|claim]], resolves the work root, confirms it can write there, and confirms no other run is building in that checkout; see 4. Claims. Then it starts the ticket in one step: `status`, `assigned`, the move to `in-progress/`, the roadmap row, and the worklog. The opening entry names the ticket, the work root with the evidence that settled it, and the end-to-end decision. A resumed ticket keeps its worklog, and the entry is appended.

The work roots come from the ticket's `repositories`, which names them by registry code:

1. Codes the registry has are the work roots.
2. An empty field, or a code the registry lacks, starts the `repo-resolver` agent. It narrows the registry's candidates by evidence — the design docs, the ticket's text, its dependencies' `repositories`, and which tree already holds the code the ticket changes — and returns the codes.
3. A settled answer is written onto the ticket in the Start step, so no later run resolves it again.
4. When the evidence leaves it open, the answerer chooses among the candidates; an autonomous run has no answerer for this and ends for a person. The orchestrator never guesses.

**Plan.** The planner reads the feature folder — the ticket and its decisions, the feature note, the design docs, the solution designs, and the PRD — then surveys the code and researches current practice. It returns the context pack, with the project's check commands, and the plan with a risk profile: the files touched, whether it adds a dependency or a public interface, and whether a command can check every acceptance criterion. The ticket's decisions are fixed constraints. A fork the documents leave open goes to the answerer in one round, and the answers are recorded; a fork the answerer cannot settle sends the ticket back to planning, as an escalation. A second round of questions from the planner is an escalation too. The plan itself is kept nowhere. The plan entry records the direction it took, the approach it turned down, and any answer the answerer gave.

**Review the plan.** The risk gate in 3.2 Gates decides whether a review runs: a low-risk plan goes straight to Plan the tests. When the planner asked questions first, the reviewer pre-reads the context pack while the plan is being written; otherwise it receives the plan and the pack together. On `CHANGES_REQUESTED`, the planner revises once and the same reviewer reviews again. A second `CHANGES_REQUESTED` is an escalation.

**Plan the tests.** `test-planner` loads the `test-strategy` skill. It starts when the planner starts, and works from the specification alone while the plan is written and reviewed: the ticket's criteria and decisions, the design docs, and the end-to-end decision. When the plan is approved, or its review skipped, it receives the plan and attaches each case to the public interface the plan exposes. Each case is **new**, checking behavior the change adds, or a **guard** on behavior that already exists. Each names the bug it catches, the input that exposes the bug, the expected result, and the cheapest type that catches it: unit, then integration, then end-to-end. An end-to-end case covers a critical path only, and only when the end-to-end decision says yes. The plan also lists what goes untested and why. A plan with no case — a change no test could catch failing, such as a copy edit or a config value — skips Write the tests and Run each new test, and the entry says why. The test plan entry records each case in one line and each exclusion.

**Write the tests.** `test-writer` loads the `test-strategy` skill and writes the cases in the test plan and nothing else: no production code, and no case the plan does not hold. It may add the fixture or helper a case needs. It reports every file it changed and the command that runs each case. A case the writer cannot write is a blocker, and a blocker is an escalation. The orchestrator records a fingerprint of every file the writer changed, and the tests entry records the files and the commands — the record the feature's later tickets run.

**Run each new test.** The orchestrator runs each new case by the writer's command and reads the result. **Every new test must fail**, because the behavior is missing: a case that passes catches nothing, and a case that does not run at all is broken. A guard case is exempt. A case that passes or does not run goes back to `test-writer`, which sharpens or repairs it once. One that still passes is recorded and the run goes on; one that still does not run is an escalation, since no later stage can make it run. The entry records each case and how it failed. A test the writer rewrites after implementation — after a test defect — skips this check and goes straight to Run the feature's tests: the code that makes it pass now exists.

**Implement.** `coding` builds the approved plan until the written tests pass, and nothing beyond it. It writes no test of its own and never changes a file `test-writer` wrote. When it lands, the orchestrator compares the fingerprints. A changed test file goes back to `coding` to restore, and that costs a feature-test fix cycle. A blocker it reports is an escalation. The implement entry records the calls the plan left open.

**Run the feature's tests.** The orchestrator runs **the feature's tests**: every test file recorded in the `tests` entries of the worklogs of the feature's tickets — the ones already `done` and this one — by the commands recorded beside them. It runs no lint, no full suite, and no end-to-end test; those run in the full verification. All passing moves the ticket to Code review. Otherwise `coding` receives the failures and fixes, and the feature's tests run again. A ticket gets two fix cycles here, and a third failure is an escalation.

**Test defect.** When `coding` concludes that a test, not its code, is wrong, it finishes every other work item it can, then returns a dispute instead of working around the test. The dispute names the test, what is wrong with it, the evidence, and the change it proposes. `test-planner` rules on each disputed test:

| Ruling     | What happens                                                                                     |
| ---------- | ------------------------------------------------------------------------------------------------ |
| `upheld`   | The test stands. `coding` receives the reason and builds against it                              |
| `revised`  | The test plan changes. `test-writer` rewrites the test, and the run goes to Run the feature's tests |
| `escalate` | The dispute turns on what the specification means, which only the answerer can settle           |

A dispute may come from any `coding` turn, including a fix after the code review or the full verification, when an existing test broke under a change the ticket meant to make. A ticket gets one dispute round; a second dispute is an escalation. The dispute entry records each dispute, its ruling, and the reason.

**Code review.** The status becomes `review`, and four `code-reviewer` agents start at once on the same change, one per focus; see 2.1 Structure. The `tests` reviewer also gets the test plan. The review passes when every reviewer approves. Otherwise the status returns to `in progress`, and `coding` receives every blocking issue in one message. After the fix the feature's tests run again, and only the reviewers that blocked review again. A second blocked review is an escalation. A minor issue becomes a recommendation and blocks nothing.

**Run full verification.** For the [[glossary#Full verification|full verification]], the orchestrator runs every check command in the context pack — lint, type check, and the full test suite — and, when the end-to-end decision says yes, the end-to-end suite, including one the test writer stood up for this ticket. It reads each result. All passing moves the ticket to Finish. Otherwise `coding` receives every failure in one message, fixes, and the failed checks run first, then the rest. A second failure is an escalation. A check the project lacks is reported as skipped, never as passed.

**Finish.** In one step, the orchestrator:

- sets `status` to `done` and removes `assigned` and `claimed`;
- writes the usage properties; see 6. Variation and limits;
- moves the ticket and its worklog to `done/`;
- appends the closing entry: what shipped, each recommendation nobody acted on, and each note file;
- writes each note the coding agent's latest turn reported, through the note script, into the feature's `notes/` folder — a note already there is kept;
- deletes the roadmap row;
- corrects every remaining ticket this work proved wrong.

**A run ends for a person** at every escalation, and when an agent returns nothing usable after one re-ask. Every run ends in one [[glossary#Outcome|outcome]] — `completed`, `escalate`, or `aborted`; see 5. States. A run that stops writes no note: its outcome entry names each one, and the run that finishes the ticket writes them.

### 3.2 Gates

| Gate               | Rule                                                                                                          |
| ------------------ | ------------------------------------------------------------------------------------------------------------- |
| Risk low           | The plan review is skipped only when the plan touches at most two files, adds no dependency and no public interface, and a command can check every acceptance criterion |
| High risk          | The plan adds a public interface, adds a dependency, or touches more than five files                         |
| Test stages skip   | Write the tests and Run each new test are skipped only when the test plan holds no case                       |
| New tests fail     | Every new case fails when the orchestrator runs it, except a case the test plan marks as a guard              |
| Tests untouched    | Every file `test-writer` changed keeps its fingerprint after every `coding` turn                              |
| Done               | The feature's tests pass, all four code reviewers return `APPROVED`, and every check passed                   |

- **A high-risk plan gets two plan reviewers**, one judging correctness and completeness, one judging fit with the codebase. Either one's `CHANGES_REQUESTED` sends the plan back. A high-risk change also gets the stronger model for its code review.
- **The code review has no skip gate.** Every focus runs on every ticket.

## 4. Claims

The claim stops two runs from building the same ticket at once.

- **The claim is `<command>-<n>`**: `orchestrate-2`, `orchestrate-quick-2`. `<n>` is the lowest positive number no other claim in `work/` uses.
- **The run's agents carry the same number.** `coding-2` works for `orchestrate-2`, so `assigned` names the run as well as the role.
- **The claim is written first and read back.** A run that reads back another run's claim drops the ticket and picks again.
- **A roadmap run claims a feature's whole dependency cluster**, on every ticket at once, and reads every one back. It holds those claims across its sessions until each ticket is `done` or the run ends; see 6.1 The roadmap run.
- **A claimed ticket is never ready for another run.**
- **One checkout holds one build at a time.** Start checks it: a run whose work root another run's claimed `in progress` or `review` ticket names releases its claim and picks again. Two builds in one tree would each check the other's changes. A run worktree is a checkout of its own, so a roadmap run never waits on another run's work root.
- **Every exit removes the claim**: finish, escalation, and abort. A roadmap run's end removes the claims on every ticket of its cluster that is not `done`.

**Weakness:** a file cannot hold a lock, so the read-back narrows the race without closing it. A run that dies without exiting leaves its claim for a person to remove.

## 5. States

| State                          | What happens                                                                                                                                  |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| No ready ticket                | The run says nothing is ready, names planning as the way to add work, and writes nothing beyond the roadmap rows it corrected                |
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
| Command               | `/orchestrate`                         | `/run-roadmap`                                  | `/orchestrate-quick`        |
| Started by            | A person, one ticket per command       | A [[glossary#Roadmap run\|roadmap run]], one fresh session per ticket | A person, with a ticket, a roadmap, or a bare task |
| Answerer              | The person                             | `cto`                                           | Nobody mid-run; the person approves a ticket picked from a roadmap and answers the end-to-end offer |
| End-to-end decision   | The person, at the pick                | `cto`, once per feature                         | No, unless the task itself asks for end-to-end tests |
| Plan review           | Gated; see 3.2 Gates                   | Gated                                           | Always, one reviewer, pre-reading while the plan is written |
| New tests fail        | Proved by the orchestrator, one sharpen round | Proved by the orchestrator, one sharpen round | Proved by the test writer itself |
| After Implement       | The feature's tests                    | The feature's tests                             | A targeted `verify` run: the new tests, and the existing tests of the changed files |
| Checks run by         | The orchestrator                       | The orchestrator                                | A fresh `verify` agent per run |
| Code review           | Four reviewers, one per focus, after the feature's tests | Four reviewers, one per focus      | One reviewer from all four focuses, at the same time as the full verification |
| Fix after review or verification | One cycle each              | One cycle each                                  | One cycle, shared by the verification, the code review, and the end-to-end run |
| End-to-end suite      | In the full verification on a yes      | In the full verification on a yes               | Held out of the full verification and offered to the person as one question at the end; run without asking when the test writer wrote end-to-end cases |
| At a cap              | Escalation                             | A `cto` ruling, then escalation                 | Escalation                  |
| Claimed               | The ticket, as `orchestrate-<n>`       | A feature's [[glossary#Dependency cluster\|dependency cluster]], as `run-roadmap-<n>` | The ticket, as `orchestrate-quick-<n>` |
| Builds in             | The work root                          | A [[glossary#Run worktree\|run worktree]] of each work root | The work root    |
| Finished code         | Left uncommitted for the person        | One commit per ticket on the run branch         | Left uncommitted            |
| A stopped ticket's code | Left in the work root                | Discarded from the run worktree; the ticket and worklog are kept | Left in the work root |
| After a stopped ticket | —                                     | The roadmap run ends                            | —                           |

A stopped ticket becomes `blocked` in every mode, as 5. States says. `/orchestrate-quick` with a bare task and no ticket writes no board file: it names the work root in its report, and writes its notes under the task's feature, or shows them in the report when there is none.

**`/code` and `/review` are not runs.** `/code` hands a request to `coding` with no plan, no tests first, and no gate; `/review` starts one `code-reviewer` from all four focuses on code that already exists, and with "fix" hands its blocking issues to `coding`. Neither claims, moves, or assigns a ticket. Each appends one entry to a worklog that already exists, and creates none. `/code` writes the notes its `coding` turn reports.

### 6.1 The roadmap run

An autonomous run is one ticket of a roadmap run. A roadmap run works one feature at a time: it selects a feature, claims its dependency cluster, and builds the cluster's tickets one by one, then selects the next feature. The launcher starts a fresh session per ticket, so a long roadmap never runs out of context, and the roadmap run carries one name, `run-roadmap-<n>`, across every session. `<n>` is the lowest positive number that no claim in `work/` and no branch in a registered work root uses.

The **launcher** is a script a person starts from a code repository, or from the framework root or a project folder when one board drives several repositories. It gives each session access to every work root of the project and to the folder its run worktrees sit in. It passes each session the run's name, the project, which every work root the run builds in must belong to, and, on the session that reaches `--max`, the mark that this ticket is the run's last.

![[run-roadmap.excalidraw]]
*The roadmap run: selecting a feature and claiming its dependency cluster, a claim lost to another run, the loop over the feature's tickets and back to the next feature, a run worktree per work root, the orchestration pipeline as one step, the two commits, and every end that needs a person.*

| Step                          | What happens                                                                                                  | When it fails                                    |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| Preflight                     | Before anything is written: the framework root and its roadmap exist, every registered work root is a git tree this session can reach and write beside, and the run's existing worktrees are clean. A dirty checkout is no failure | The run ends `blocked`, naming what is missing and the fix |
| Select the next feature       | The roadmap is first rebuilt from the tickets, and the rebuild is recorded. A feature the roadmap run already claims comes first, at its next ticket. Otherwise the orchestrator lists the candidate features in roadmap order: every feature with a ticket not `done` whose cluster holds no ticket another run claims and no ticket `blocked` on something other than a cluster ticket | No ticket left on the roadmap: the run ends, roadmap done. Tickets left and no candidate: the run ends for a person |
| Can it run                    | `cto` picks one candidate feature and calls the end-to-end question once for it, or hands the pick back       | A hand-back ends the run for a person            |
| Confirm                       | Automatic. Nobody is asked; the `cto`'s pick stands                                                           | —                                                |
| Claim its dependency cluster  | The run writes its claim on every ticket of the feature's cluster and reads every one back | Another run's claim read back: the run releases what it wrote and selects again. Lost three times in a row, the run ends for a person |
| Choose the feature's next ticket | The cluster's first ticket, in dependency order, whose dependencies are all `done`. A dependency in another feature comes before the feature's tickets that need it. | —                                  |
| Identify the work roots       | The `repositories` of the ticket to build and of its direct dependencies. A ticket with none gets them from the `repo-resolver` agent, written onto it, as in 3.1 Start | The agent cannot settle them: the run ends for a person, naming the candidates |
| Create a run worktree         | One per work root, at `<repository>-worktrees/run-roadmap-<n>` beside the repository, on branch `run-roadmap-<n>` from that work root's current commit, made once and reused by every later ticket of the run | The run ends for a person, naming the work root and the git error |
| Pick up the ticket            | Start the chosen ticket as in 3.1                                                                            | —                                                |
| Run the orchestration pipeline | Plan to Run full verification, as in 3.1, in the run worktrees                                         | Not completed: the ticket stops as in 5. States, its code is discarded from the run worktrees, and the run ends for a person |
| Commit the code               | Before Finish: one commit per run worktree the ticket changed, on the run branch, following that work root's own convention. A ticket is `done` only once its code is on the run branch | A rejected commit stops the ticket as `blocked`, with the hook's reason in `blocked_by`, and the worktree is left for a person. The hook is never bypassed |
| Finish                        | As in 3.1 Finish. The ticket's claim goes with it; the rest of the cluster keeps the run's claim             | —                                                |
| Commit the documents          | One commit in the framework root holding the ticket, its worklog, the roadmap edit, every ticket Finish corrected, and each new note, when the framework root is a git tree. It names those paths only | —                                  |
| `--max` reached               | The launcher counts tickets. Under the limit, the next session continues. The last session releases the run's claims even after a completed ticket | At the limit, the run ends                       |
| Feature done                  | No ticket of the cluster is left: the next session selects the next feature. Otherwise it builds the feature's next ticket | —                         |

- **Every end reports what happened and how to resume the run.** It releases the claims on every ticket of the cluster that is not `done`, and keeps the branch and the run worktrees. Resuming starts the same roadmap run again by its name; it reuses the branch and the worktrees and claims afresh.
- **The person's checkout is never touched.** A run worktree starts from the work root's current commit, so an uncommitted change in the checkout is not part of it, and the run builds in its worktree alone.
- **The run never pushes, merges, or amends.** A person reviews the run branch and merges it.
- **A run worktree is clean between tickets.** A finished ticket is committed and a stopped one is discarded, so the next ticket starts from the last commit. A worktree left dirty ends the run.
- **A stopped ticket keeps its record and loses its code.** Every unfinished end — `deferred`, `stop-run`, `handed-back`, `aborted`, and a rejected commit once a person has looked — writes the stop as 5. States says, releases the cluster's claims, discards the ticket's changes from every run worktree it touched, and commits the documents. Half-built code is never committed.

**Every session ends with one result line** the launcher parses: the outcome, the run's name, the feature, the ticket, the code commit, the run worktrees written, the tickets left on the roadmap, the next action, and a one-sentence reason.

| Outcome       | What happened                                                         |
| ------------- | --------------------------------------------------------------------- |
| `completed`   | The ticket was finished and committed on the run branch               |
| `deferred`    | The `cto` ruled `defer`                                               |
| `stop-run`    | The `cto` ruled `stop-run`                                            |
| `handed-back` | The `cto` handed a decision back, or a cap ran out of rulings, or the work roots could not be settled |
| `aborted`     | An agent returned nothing usable after one re-ask                     |
| `no-work`     | No ticket is left, or tickets are left and no feature can be selected |
| `blocked`     | The ground is wrong: preflight, the claim, a run worktree, or a commit failed |

**The launcher stops the run** when a session reports any outcome but `completed`, when no ticket is left, at `--max`, when a completed ticket left the count of remaining tickets unchanged, when a run worktree is dirty between tickets, and when a session prints no result line or outlives its time limit. It ends cleanly only when the roadmap is done or `--max` is reached; every other stop needs a person.

**The `cto` answers three kinds of request**: `feature-selection`, which picks the feature and calls its end-to-end decision; `decisions`, which settles the planner's open forks in one round; and `escalation`, which rules on a stage that hit its cap. The `cto` is started once per session and resumed for every request.

**A `cto` ruling** is one of five:

| Ruling      | What the run does                                                                  |
| ----------- | ---------------------------------------------------------------------------------- |
| `retry`     | One more cycle at that stage, carrying the ruling's guidance. The stage's cap is then spent, and a retry that fails again is handed back |
| `rescope`   | Finishes a narrower ticket; the dropped part becomes a new `backlog` ticket        |
| `defer`     | Stops the ticket for a person, and the roadmap run ends                           |
| `stop-run`  | The same as `defer`: the ticket stops and the roadmap run ends                     |
| hand back   | Stops the ticket for a person to decide, and the roadmap run ends                  |

A second escalation at one stage, or a third on one ticket, is handed back without asking the `cto`.

**The caps**, applied by the command named in each column. A dash means the command has no such stage:

| Cap                                   | `/orchestrate` | `/run-roadmap` | `/orchestrate-quick` |
| ------------------------------------- | -------------- | -------------- | -------------------- |
| Tickets per run                       | 1              | 1              | 1                    |
| Plan revisions                        | 1              | 1              | 1                    |
| Rounds of planner questions           | 1              | 1              | —                    |
| Sharpen rounds for a new test that does not fail | 1   | 1              | —                    |
| Feature-test fix cycles, a restored test file included | 2 | 2         | —                    |
| Targeted-verify fix cycles, a restored test file included | — | —        | 2                    |
| Test dispute rounds per ticket        | 1              | 1              | 1                    |
| Code review fix cycles                | 1              | 1              | 1, shared            |
| Full verification fix cycles          | 1              | 1              | 1, shared            |
| End-to-end fix cycles                 | in the full verification | in the full verification | 1, shared |
| Re-asks for a missing result block, per agent turn | 1 | 1            | 1                    |
| Claim attempts lost in a row          | —              | 3              | —                    |
| `cto` rulings per stage               | —              | 1              | —                    |
| `cto` rulings per ticket              | —              | 2              | —                    |

In `/orchestrate-quick`, "shared" means one fix cycle covers the verification failures, the review issues, and an end-to-end failure together.

**A ticket that changes two work roots keeps both.** Each work root gets its own feature tests, code review, full verification, and commit, and the ticket passes only when both pass.

**Usage accumulates across runs.** The orchestrator adds each agent's time and tokens as its turn lands. At every exit it adds the run's totals to the ticket's `timing`, `tokens`, and `cost`, so a resumed ticket's numbers cover every run.
