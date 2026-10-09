---
type: design
subject: workflow
updated: 2026-10-09
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

## 2. Parts

### 2.1 Structure

![[workflow.excalidraw]]
*The stages of one run in order, the status the ticket holds in each, and the two loops a run may take once.*

A run is one orchestrator and the agents it drives. Questions go to the **answerer**: the person in an interactive run, the `cto` agent in an autonomous one.

| Agent                    | [[glossary#Stage\|Stage]]   | Answers                                                       | Returns                                                                  |
| ------------------------ | --------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------------ |
| `feature-interviewer`    | Interview                   | What must be decided before planning                          | Open decisions, each with options and a recommendation                   |
| `implementation-planner` | Plan                        | How the ticket is built                                       | A [[glossary#Context pack\|context pack]], then the plan and its risk profile |
| `plan-reviewer`          | Plan review                 | Does the plan meet every acceptance criterion and fit the code | `APPROVED` or `CHANGES_REQUESTED`, with issues                           |
| `coding`                 | Implement                   | Builds the approved plan                                      | The files changed, the calls it made, and any blocker                    |
| `verify`                 | Verify                      | Does the change pass the project's checks                     | Pass, fail, or skipped, per check                                        |
| `code-reviewer`          | Code review                 | Is the change the right code, and all of it                   | `APPROVED` or `CHANGES_REQUESTED`, with issues                           |
| `cto`                    | Any question, autonomous only | The call a person would make                                | A decision, what it beat, and the cost it accepted                       |

- **Every agent ends its reply with one machine-readable result block.** The orchestrator drives the run from that block alone. It asks once for a missing or malformed block; a second miss aborts the run.
- **Each role starts once per run and is resumed for every later turn.** A resumed agent keeps what it read, so the orchestrator sends only what changed.
- **`verify` starts fresh for every check.** A result from before a fix proves nothing about the code after it.
- **Only `verify` runs the project's checks.** `coding` checks only what it touched, and `code-reviewer` runs no checks.

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
| Implement              | `in progress` | `coding-<n>`                 | `coding · implement`                                     |
| Verify and code review | `review`      | `code-reviewer-<n>`          | `verify · verification`, then `code-reviewer · code review` |
| Finish                 | `done`        | removed                      | `<orchestrator> · done`                                  |

`<n>` is the run's number; see 4. Claims.

**Pick.** The orchestrator lists the ready tickets in roadmap order, which is priority order. A ticket is ready when it sits in `backlog/` unclaimed and every ticket it depends on is `done`. A resumable `blocked` ticket is ready too; see 5. States. The answerer picks one ticket, and says whether it gets end-to-end tests. Yes is recommended only when the ticket adds or changes a user-facing flow that no end-to-end test crosses. Picking nothing ends the run with nothing written.

**Start.** The orchestrator writes its [[glossary#Claim|claim]], resolves the work root, and confirms it can write there. Then it starts the ticket in one step: `status`, `assigned`, the move to `in-progress/`, the roadmap row, and the worklog. The opening entry names the ticket, the work root with the evidence that settled it, and the end-to-end decision. A resumed ticket keeps its worklog, and the entry is appended.

The work root is resolved from the registry:

1. The candidates are every registry entry whose `projects` names a project of the ticket's feature, and every entry with no `projects`.
2. One candidate is the work root.
3. Several candidates are narrowed by evidence: the design docs, the ticket's text, and which tree already holds the code the ticket changes.
4. When the evidence leaves it open, the answerer chooses. The orchestrator never guesses.

**Interview and scout.** Two agents start at once. The interviewer reads the documents and the code, and returns the open decisions. The planner surveys the same code, researches current practice, returns the context pack, and waits. The answerer settles every decision in one round. The interview entry records each decision, what it beat, and each assumption confirmed.

**Plan.** The planner receives the decisions as fixed constraints and writes the plan from what it already read. It returns the plan with a risk profile: the files touched, whether it adds a dependency or a public interface, and whether a command can check every acceptance criterion. The plan itself is kept nowhere. The plan entry records the direction it took and the approach it turned down.

**Plan review.** The review gate in 3.2 Gates decides whether a review runs. The reviewer reads the context pack while the plan is still being written. On `CHANGES_REQUESTED`, the planner revises once and the same reviewer reviews again. A second `CHANGES_REQUESTED` is an escalation.

**Implement.** `coding` builds the approved plan and nothing beyond it. A blocker it reports is an escalation. The implement entry records the calls the plan left open.

**Verify and code review.** The status becomes `review`, and `verify` and `code-reviewer` start at the same time on the same change. The ticket passes when every check passes and the review approves. Otherwise the status returns to `in progress`, and `coding` receives every failure and every blocking issue in one message. After the fix the status is `review` again. A fresh `verify` runs the failed checks first, and `code-reviewer` reviews again only when it had blocked. A second failure is an escalation. A skipped check is reported as skipped, never as passed. A minor review issue becomes a recommendation and blocks nothing.

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
| Done               | Every check passed, and the code review returned `APPROVED`                                                   |

- **A high-risk plan gets two reviewers**, one judging correctness and completeness, one judging fit with the codebase. Either one's `CHANGES_REQUESTED` sends the plan back. A high-risk change also gets the stronger model for its code review.
- **The code review has no skip gate.** It is the last check between a change and `done`.

## 4. Claims

The claim stops two runs from building the same ticket at once.

- **The claim is `<command>-<n>`**: `orchestrate-2`. `<n>` is the lowest positive number no other claim in `work/` uses.
- **The run's agents carry the same number.** `coding-2` works for `orchestrate-2`, so `assigned` names the run as well as the role.
- **The claim is written first and read back.** A run that reads back another run's claim drops the ticket and picks again.
- **A claimed ticket is never ready for another run.**
- **One work root holds one build at a time.** A run whose work root another claimed `in progress` or `review` ticket holds releases its claim and picks again. Two builds in one tree would each check the other's changes.
- **Every exit removes the claim**: finish, escalation, and abort.

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
| Started by            | A person, one ticket per command       | A launcher loop, one fresh session per ticket   | A person                    |
| Answerer              | The person                             | `cto`                                           | The person                  |
| Interview             | Skipped for a ticket with no product, design, or architecture fork | Always                  | Never                       |
| Plan review           | Gated; see 3.2 Gates                   | Gated                                           | Always, one reviewer        |
| At a cap              | Escalation                             | A `cto` ruling, then escalation                 | Escalation                  |
| Finished code         | Left uncommitted for the person        | One commit per ticket in each work root         | Left uncommitted            |
| A stopped ticket's code | Left in the work root                | Discarded; the ticket and worklog are kept      | Left in the work root       |

**An autonomous run starts only on a work root with no uncommitted change**, so its commit holds exactly one ticket. The commit follows the work root's own convention. The run never pushes, branches, or amends. A commit a hook rejects stops the ticket as `blocked`, with the hook's reason in `blocked_by`.

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
| Fix cycles after verify and code review | 1   |
| Re-asks for a missing result block, per agent turn | 1 |
| `cto` rulings per stage               | 1     |
| `cto` rulings per ticket              | 2     |

**A ticket that changes two work roots keeps both.** Each work root gets its own verification, code review, and commit, and the ticket passes only when both pass.

**Usage accumulates across runs.** The orchestrator adds each agent's time and tokens as its turn lands. At every exit it adds the run's totals to the ticket's `timing`, `tokens`, and `cost`, so a resumed ticket's numbers cover every run.
