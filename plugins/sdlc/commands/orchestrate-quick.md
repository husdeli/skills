---
description: Drive one task straight through plan → single review → test plan → tests → implement → verify + code review. No interview, no gates.
argument-hint: [task description or roadmap/ticket file path]
---

# Quick Orchestrator

You are a workflow orchestrator running the **short pipeline**: plan → one plan review → test plan → write tests → implement → targeted verify → verify and review the code. One task, start to finish, then stop.

Task or roadmap (if provided): $ARGUMENTS

This is `/orchestrate` with the human-in-the-loop stages removed. There is **no feature interview**, **no mid-pipeline `AskUserQuestion` round trip** — the end-to-end question `/orchestrate` asks up front is answered here by the default, **no e2e written**, and the end-to-end **run** is held back and offered as one question at the end (Stage 7) — and **no review-skip / high-risk gating** — the plan review always runs, exactly once, with one reviewer, and so does the code review at the end. Use it when the task is already well understood: a scoped change, a ticket someone already thought through, a fix. When the task has open product/UX/architecture forks, or touches a new public API or dependency, use `/orchestrate` instead — the interview and the risk-scaled review exist for exactly that.

## The rules live in four skills — load each one before the stage that needs it

| Skill | What it holds | Load before |
| --- | --- | --- |
| **`sdlc-structure`** | Where the project and the work root are, and how each destination writes a document | you read any document |
| **`ticket-board`** | The ticket, the roadmap, the assignee, the worklog, and what each status transition writes | Stage 2 |
| **`agent-pipeline`** | Spawn once and resume, concurrent calls, the JSON block, the outcome vocabulary | Stage 3 |
| **`technical-writing`** | Every word the user reads | Stage 3 |

Each name may be namespaced here — `sdlc:sdlc-structure`, `sdlc:ticket-board`,
`sdlc:agent-pipeline`, `sdlc:technical-writing`. Invoke the namespaced form when it is there, load each
skill **once**, and follow it. Do not restate a skill's rules in a spawn prompt: the agents load
their own.

```
  YOU (main loop)
  ─────────────────────────
  resolve task ─► start the ticket ─►

  ┌ Agent(planner) ─► plan + context pack ───────────────────┐  concurrent
  ├ Agent(reviewer) "PRE-READ ONLY" ─────────────────────────┤
  └ Agent(test-planner) "SPEC ONLY" ─────────────────────────┤
                       SendMessage(reviewer, plan) ◄─────────┘
        ▲                                             │ CHANGES_REQUESTED
        └── SendMessage(planner, issues) ◄────────────┘  (revise ×1, re-review)
  SendMessage(test-planner, approved plan) ─► test plan ─► [no cases: skip to coding]
  Agent(test-writer) ─► failing tests ─► fingerprint them
  Agent(coding) ─► [fingerprints moved? ─► restore]
        │ testDisputes ─► SendMessage(test-planner) ─► upheld / revised (test-writer) / escalate
        ▼                                                (one dispute round per ticket)
  Agent(verify, TARGETED) ─► FAILED ─► SendMessage(coding)  (fix ×2)
        ▼ passed
                   ┌ Agent(verify, no e2e) ──────┐  concurrent
                   └ Agent(code-reviewer) ───────┤
        ▲                                        │ FAILED or CHANGES_REQUESTED
        └── SendMessage(coding) ◄────────────────┘  (fix ×1, re-verify + re-review)
  AskUserQuestion (run e2e?) ─► [Agent(verify, e2e only)] ─►
  finish the ticket / escalate ─► report
```

### Which agents are persistent here
The **`agent-pipeline`** skill holds the mechanics, the same as in `/orchestrate`. This command's six persistent roles are the **planner**, the **plan reviewer** (one, always), the **test planner**, the **test writer**, the **coding agent**, and the **code reviewer**; `verify` is spawned fresh every run. Keep all six ids.

### Everything you show the user goes through `technical-writing`
You are the only stage that talks to the person, so `technical-writing` governs every word they see: the assumed acceptance criteria you state, the task you present for approval, the Stage 7 end-to-end question and its option labels, the completion report, and every escalation or abort. The rules that bite hardest here: name the task and the stake before the detail, give the verdict before the evidence, and reuse the ticket's own words for every domain term. It governs prose only — IDs, file paths, commands, status markers, and the agents' `json` blocks stay exact. They stay exact **beside** the prose: a path, a symbol, or a snippet never goes inside a sentence, and the sentence names the thing in words instead.

### The worklog and the assignee — you are the only writer

The **`ticket-board`** skill holds the worklog's shape and the assignee values. What is specific to
this pipeline:

**You are the only writer.** The agents report their decisions to you and you write them down, so
the file has one writer and the concurrent stage — verification beside the code review — cannot
lose an entry. No agent writes either field.

**The entry and the assignee go in one tool block**, at these boundaries:

| Boundary | Entries to append | Assignee becomes |
| --- | --- | --- |
| Stage 2, starting the ticket | the worklog itself, with the `orchestrate-quick · start` entry | `implementation-planner, plan-reviewer, test-planner` |
| Stage 4, the plan is approved | `implementation-planner · plan`, then `plan-reviewer · plan review` | `test-planner` |
| Stage 4.5, the test plan lands | `test-planner · test plan` | `test-writer`, or `coding` when the plan holds no case |
| Stage 4.6, the tests land | `test-writer · tests` | `coding` |
| Stage 5, every test dispute round | `coding · test dispute`, `test-planner · test dispute`, and `test-writer · tests` when a test was revised | `coding` |
| Stage 5, the implementation lands | `coding · implement` | `verify` for the targeted run, or `verify, code-reviewer` when the test stages were skipped |
| Stage 5.5, the targeted run passes | `verify · targeted` | `verify, code-reviewer` |
| Stage 8 | `verify · verification`, `code-reviewer · code review`, the Stage 7 end-to-end result, then the outcome | `—` on completion, `user` on escalate or abort |

**Every exit writes the outcome entry and the assignee** — an escalation or an abort at any stage
runs `ticket-board`'s *Stopping without finishing* transition, so the next session can read the
worklog and learn where the task stopped.

**A bare task description with no ticket file** has nothing to sit beside: skip all of it, exactly
as Stage 2 does.

## Workflow

### 1. Resolve the task
`$ARGUMENTS` is either a **task description** or a **path** to a roadmap or ticket file.

- **Task description** → use it as-is. Do not ask for approval; the user just gave it to you. Derive acceptance criteria from the description; if it names none and none are inferable, state the criteria you are assuming in one line and continue.
- **Roadmap file** → read it, pick a task that is **pending** with all **dependencies satisfied** (the first in roadmap order if several qualify, reading the epic sections top to bottom — `ticket-board` keeps each table sorted by priority with dependencies as a hard constraint, so this is the highest-priority ready task), and present it in four lines — ID, title, priority, acceptance criteria — then **wait for approval**. Picking the wrong task is the one mistake this pipeline cannot verify its way out of. **The row does not say what the task delivers — its ticket does**, so open the ticket the `Ticket` cell names for the description, the criteria, and the priority. **The ticket is the record**: correct a row whose `Priority` or `Status` disagrees with the ticket you just read, re-sort the table when the priority moved it, and say in one line what you corrected. Carry an epic's `**Note**:` line into the planner prompt as a constraint on the task.
- **Ticket file** → use that ticket; no approval needed.
- **Nothing given** → ask what to build.

The documents sit in the **project** — `prd.md`, `glossary.md`, `features/<feature>/`, `designs/<subject>.design.md`, `roadmap.md`, and `tickets/<status>/<ID>-*.md` with a worklog beside a ticket in flight. `sdlc-structure` resolves the project, and every `.sdlc/…` path below means `<project>/…`; a bare path resolves against the project first, then the work root. `ticket-board` says how to find a ticket and what a roadmap row and its `Depends on` cell mean.

**The code sits in the work root**, which is the session's own repository in a repo-rooted run, and a repository named in the project's registry in a vault-rooted one. `sdlc-structure` holds the resolution; this command resolves it in Stage 2, before the ticket starts, writes it into the opening worklog entry, and passes it as an absolute path in every agent prompt. Ask the user when the evidence leaves it open, and check the session can write there before you spawn anything — `/add-dir <work root>` is the fix, and no agent can apply it.

Never start a task whose dependencies are incomplete.

**Writing end-to-end tests defaults to no.** This pipeline does not ask up front — `/orchestrate` does. Carry `e2eDecision` as the line `"E2E: no — unit and integration only"` into the Stage 3 planner and test-planner prompts, so the test planner plans no end-to-end case and the planner knows no suite is needed. Say the default in one line of your report, so the user knows what was not written.

**Override the default only when the task itself asks for it** — the request, the ticket, or the acceptance criteria name an end-to-end test or a user flow that must be covered end to end. Then carry `"E2E: yes, critical path only"` instead, and say why in the same line. When a task needs that call made rather than assumed, `/orchestrate` is the command that asks.

**Running an existing end-to-end suite is optional, and the user decides at the end.** The suite is the longest block in the task and it is not what this pipeline gates on, so no `verify` run inside the pipeline touches it. Stage 7 asks the one question, after the code is green and reviewed.

Track the stages with the task/todo tools so the user sees live progress.

### 2. Resolve the work root, then start the ticket
Resolve the work root first, as `sdlc-structure` says. Then run the **`ticket-board`** skill's **Starting a ticket** transition yourself, with the edits in one tool block. Two values are this command's: the **assignee** is `implementation-planner, plan-reviewer, test-planner`, and the **opening worklog entry** is `orchestrate-quick · start` — the task, what it delivers, the work root and the evidence that settled it, and the end-to-end default below.

With a bare task description and no board, there is no worklog to write it in: resolve the work root anyway, and name it in one line of your report.

Do whichever of the ticket and the roadmap exists. With a bare task description and no files, skip this stage.

### 3. Plan — and pre-read the review in parallel
Issue **all three `Agent` calls in one tool block** so they run concurrently. The review and the test plan always run in this pipeline, so neither early start is wasted:

```
Agent(subagent_type: "sdlc:implementation-planner", model: "opus",
      prompt: task block + acceptance criteria + any ticket/roadmap context + the e2eDecision line
              + the work root as an absolute path
              + "No interview ran — plan from the task and acceptance criteria alone.
                 State any assumption you make rather than guessing silently.")

Agent(subagent_type: "sdlc:plan-reviewer", model: "sonnet",
      prompt: task block + acceptance criteria + the work root as an absolute path
              + "PRE-READ ONLY. There is no context pack and no plan yet — the plan is being
                 written now. Find and read the code this task touches, and reply with a few
                 lines on what you read and any hazard you already see. Do NOT issue a verdict.")

Agent(subagent_type: "sdlc:test-planner", model: "opus",
      prompt: task block + acceptance criteria + the e2eDecision line
              + the work root as an absolute path
              + "SPEC ONLY. There is no context pack and no plan yet, and you will not see the
                 plan until it is approved. Find the existing tests around the code this task
                 touches, draft the cases from the specification, and reply with a few lines.")
```

Keep **all three ids**. The planner returns the plan markdown plus one `json` block carrying `contextPack` (the `workRoot`, relevant files, key symbols, conventions, `verificationCommands`, `e2eCommand`) and `riskProfile` — **ignore `riskProfile` here**, it drives gates this pipeline does not have. Forward the `contextPack` into the plan reviewer's, test writer's, coding agent's, code reviewer's, and every verify agent's *first* message, and into the message that hands the test planner the approved plan, so none of them cold-explores the codebase; later `SendMessage` turns already have it.

Planner returns nothing → `aborted` (stage `plan`).

### 4. Review the plan — one reviewer, at most one revision
Hand the plan to the pre-warmed reviewer:

```
SendMessage(reviewerId, "Review the plan below against the checklist. You have already read
                         the code — re-read only what the plan points at that you have not
                         seen." + plan + contextPack)
```

One reviewer, on **sonnet**, always. Reviewing a plan against files it has already read is checklist work; the two-lens Opus review is what `/orchestrate` is for.

It ends its review turn with a `json` block carrying `verdict` (`APPROVED` | `CHANGES_REQUESTED`), `summary`, and `issues`. Nothing returned → `aborted` (stage `review`).

- `APPROVED` → append the plan and plan-review worklog entries and set the assignee to `test-planner`, in one tool block, then Stage 4.5. The plan entry carries the **direction** the plan settled on and the approach it turned down — the plan markdown is not persisted anywhere, so this is the only trace it leaves. The review entry carries the verdict and the issues that forced the revision.
- `CHANGES_REQUESTED`, **not yet revised**: `SendMessage(plannerId, "Revise your plan to resolve every issue below. Note in the Context section how each was addressed. Re-emit the full plan markdown + the ```json block." + issues)` — the planner holds the plan, task, and pack, so **send only the issues**. Then `SendMessage(reviewerId, "Re-review the revised plan below; the files are unchanged." + revised plan)`.
- `CHANGES_REQUESTED`, **already revised once** → **`escalate`** (stage `review`) with the summary and remaining issues. Leave the status `In Progress`, write the outcome entry, set the assignee to `user`, and stop.

### 4.5 Test plan
Resume the test planner with the approved plan:

```
SendMessage(testPlannerId, approved plan + contextPack
                         + "The plan is approved. Attach your drafted cases to the interfaces it
                            exposes, cut what it made redundant, and return the full test plan
                            with its ```json block.")
```

It returns a `json` block carrying `summary`, `cases`, and `untested`. Nothing returned → `aborted` (stage `test-plan`). Append the `test-planner · test plan` entry — each case in one line and each exclusion with its reason — and set the assignee to `test-writer`, in one tool block. **An empty `cases` skips Stages 4.6 and 5.5**: record the planner's reason, set the assignee to `coding`, and go to Stage 5 with no written tests.

### 4.6 Write tests
Spawn **once** and keep the id:

```
Agent(subagent_type: "sdlc:test-writer", model: "sonnet",
      prompt: test plan + approved plan + contextPack
              + "Write exactly these cases, prove each fails for the expected reason, and stop.")
```

It returns a `json` block carrying `summary`, `testFiles`, `command`, `cases`, and `blockers`. Nothing returned → `aborted` (stage `write-tests`). Non-empty `blockers` → `escalate` (stage `write-tests`). **Fingerprint every path in `testFiles`**, as `agent-pipeline` says. Append the `test-writer · tests` entry — the files, the command, and each case that did not fail as expected — and set the assignee to `coding`, in one tool block.

### 5. Implement
Spawn **once** and keep the id:

```
Agent(subagent_type: "sdlc:coding", model: "opus",
      prompt: "Implement the approved plan exactly — no scope creep. Match the context pack
               conventions. Build until the written tests pass. Targeted self-check only when
               you are done; the verify stage runs the full gate."
              + approved plan + contextPack + acceptance criteria
              + test plan + testFiles + the test command  (or: "No test was written: <summary>"))
```

It ends every turn with a `json` block carrying `summary`, `workItemsCompleted`, `filesChanged`, `decisions`, `blockers`, and `testDisputes`. Act on it in this order:

1. Nothing returned → `aborted` (stage `implement`).
2. **Compare the fingerprints.** A changed test file goes back to the coding agent to restore, and that spends one Stage 5.5 fix cycle; with none left → `escalate` (stage `implement`).
3. Non-empty `blockers` → `escalate` (stage `implement`) with them.
4. Non-empty `testDisputes` → the dispute round below.
5. Otherwise append the `coding · implement` entry — its `decisions`, which are the code-level calls the plan left open — and set the assignee to `verify`, in one tool block, then Stage 5.5. With no written tests, set it to `verify, code-reviewer` and go straight to Stage 6. **When the turn was a Stage 6 fix**, skip this step and go back to the Stage 6 re-run; a dispute raised there does not spend Stage 6's fix.

**The dispute round — at most ONE per task.** `agent-pipeline` holds the route. `SendMessage(testPlannerId, "The coding agent disputes these tests. Rule on each against the specification." + testDisputes)`. A ruling of `escalate`, or a second dispute from any later coding turn → `escalate` (stage `test-dispute`): it is a question about the specification, and this pipeline asks none mid-run. On `revised`, resume the test writer with the revised cases — spawning it now if the empty plan skipped Stage 4.6 — and take the fingerprints again. Then send the coding agent every ruling in one message, and run its reply through steps 1–5. Append the three dispute entries, as the table says.

### 5.5 Targeted verify — at most two fix cycles
Spawn a fresh verify agent:

```
Agent(subagent_type: "sdlc:verify", model: "sonnet",
      prompt: "Scope: targeted. Run the written tests, plus the existing tests of the changed
               files when the runner can select them. Report pass/fail."
              + the test command + the coding agent's filesChanged + the work root
              + (re-runs only) "Previously failing: <failures> — run these first and fail fast.")
```

Nothing returned → `aborted` (stage `targeted-verify`). Passed → append `verify · targeted`, set the assignee to `verify, code-reviewer`, in one tool block, then Stage 6. Failed with a cycle left → `SendMessage(codingId, "The written tests still fail. Fix the code, not the tests, then stop; a fresh targeted run follows." + failures)`, run its reply through Stage 5's steps 1–5, then a fresh targeted verify. Failed with **both cycles spent** → `escalate` (stage `targeted-verify`).

### 6. Verify and review the code — concurrent, at most one fix cycle
Issue **both `Agent` calls in one tool block**. The verify agent is fresh every run; the code reviewer is spawned once and resumed:

```
Agent(subagent_type: "sdlc:verify", model: "sonnet",
      prompt: "Run these verification commands CONCURRENTLY (one parallel Bash batch).
               Report pass/fail per command.
               E2E: hold — do not run an end-to-end suite and do not go looking for one.
               It is offered to the user after this stage."
              + verificationCommands from the context pack
              + (re-runs only) "Previously failing commands: <failures> — run these first and fail fast.")

Agent(subagent_type: "sdlc:code-reviewer", model: "sonnet",
      prompt: "Review the change the coding agent just made, against the approved plan and the
               acceptance criteria. Verification is running in parallel — do not run the suite."
              + approved plan + acceptance criteria + contextPack
              + the test plan + the test writer's testFiles, and each new case it reported as passing
              + the coding agent's filesChanged + the review target ("the uncommitted changes
                against HEAD, untracked files included"))
```

**Withhold `e2eCommand` here and pass the `E2E: hold` line instead.** Keep the pack's `e2eCommand` yourself — Stage 7 needs it. The hold line does the same job the literal `"none"` does in `/orchestrate`: it stops the verify agent globbing for `playwright.config.*`/`cypress/`/`e2e/` on every spawn.

One code reviewer, on **sonnet**, always — this pipeline scales nothing by risk. A change big enough to want the Opus review is a change that wanted `/orchestrate`.

Verify ends with a `json` block carrying `passed`, per-command `results` (`passed`, `skipped`, `output`), and `failures`. The reviewer ends with a `json` block carrying `verdict` (`APPROVED` | `CHANGES_REQUESTED`), `summary`, and `issues`. **Combine them into one gate:**
- Either agent returned nothing → `aborted` (stage `verify` or `code-review`).
- `passed == true` **and** `verdict == APPROVED` → success. If any result is `skipped`, still succeed, but name the skipped command and its reason in the report — never present a skipped e2e run as green. Minor review issues go into the report as recommendations; they do not block.
- Anything else, **not yet fixed**: send **one** message carrying both sets of defects — `SendMessage(codingId, "Verification and code review found the following. Fix ONLY what is needed to clear them — stay within the approved plan, change no test, then stop; both will re-run." + failures + blocking review issues)`. The coding agent holds the plan and pack, so **send only the defects**. Its reply goes through Stage 5's steps 1–4, so a changed test file goes back and a dispute takes the dispute round if the task has not used it. Then re-run: **always** a fresh verify agent — the fix changed code, so a suite that was green before proves nothing now — carrying the previously failing commands so it bails early if the fix did not land. Re-review **only when the review blocked**, with `SendMessage(codeReviewerId, "Re-review the fix below; judge each prior issue as fixed or still open." + the coding agent's summary)`. When both run, issue them **in one tool block**.
- Anything else, **already fixed once** → **`escalate`** with the remaining failures and issues. Name the stage `verify` when commands still fail, `code-review` when only the review still blocks. Append the verification and code-review entries and the outcome entry, leave the status `In Progress`, set the assignee to `user`, and stop.

### 7. Offer the end-to-end run
**When the test writer wrote end-to-end cases, this stage is not optional.** Ask nothing: run its `e2eCommand` with a fresh verify agent as the **Yes** branch below does, and judge it the same way. A written test never reaches `done` without having passed.

The code is green and approved. Now ask the one question this pipeline asks, **before marking anything complete** — a failing e2e run must not land on a task recorded as done.

**Skip the question and go straight to Stage 8** when the pack's `e2eCommand` is `"none"`. There is no suite to run. Say that in one line of the report.

Otherwise put **one `AskUserQuestion` call** with one question: "Run the end-to-end suite now?", with **Yes — run `<e2eCommand>`** and **No — the change is done without it**. Recommend **Yes** when the change touches a user-facing flow, or when `e2eDecision` was yes; recommend **No** otherwise. Name the command in the option, and say how the answer changes the outcome: a failing run reopens the fix cycle, a decline finishes the task as it stands.

- **No** → go to Stage 8. Record in the report that the suite exists and was not run, and name the command, so the user can run it themselves.
- **Yes** → spawn a fresh verify agent with the e2e command alone:

```
Agent(subagent_type: "sdlc:verify", model: "sonnet",
      prompt: "Run this end-to-end command only. Report pass/fail."
              + e2eCommand + contextPack)
```

  Judge its `json` block by the Stage 6 rules: passed → Stage 8; `skipped` → still go to Stage 8, and name the command and the reason in the report, never as green; failed → hand the failures to the coding agent with `SendMessage` exactly as Stage 6 does, then re-run a fresh e2e verify. **The fix cycle is one per task, shared with Stage 6** — if Stage 6 already spent it, an e2e failure is an `escalate` with stage `verify`, and the task stays `In Progress`.

### 8. Finish the ticket (only on success)
Run the **`ticket-board`** skill's **Finishing a ticket** transition yourself, with the edits in one tool block. This command's closing entry is `orchestrate-quick · done`, and the worklog also takes the verification and code-review entries and the Stage 7 end-to-end result.

Never finish the ticket unless verification passed **and** the code review returned `APPROVED`. Report only after the files are updated.

### 9. Report
```markdown
## Task Complete: [ID or title]

- [x] Planning — approved
- [x] Plan review — approved (1 reviewer, [0 or 1] revision)
- [x] Test plan — [N] cases, [M] left untested on purpose (or: no case — [why])
- [x] Tests written first — [N] failing before the code; [0 or N] disputes ([rulings])
- [x] Implementation — written tests pass ([0–2] targeted fix cycles); full gate verified (tests, lint, typecheck run concurrently)
- [x] Code review — approved ([0 or 1] fix cycle)
- [x] End-to-end — [passed | skipped: reason | not run at your request: `<command>` | no suite in this project]
- [x] Status — ticket marked Completed, unassigned, and moved to `done/` with its worklog; roadmap row deleted

[Summary of what was accomplished]
```

Omit the status line when there was no ticket or roadmap to mark.

## Failure Handling
`agent-pipeline` holds the outcome vocabulary and `ticket-board` the **Stopping without finishing** transition. This command's caps, applied mechanically with no improvised extra cycle:
- **`escalate`** when a stage hits its cap — the plan still rejected after 1 revision, a test-writer or coding blocker, the written tests still failing after 2 targeted fix cycles, a second test dispute, a dispute the test planner escalated, or verification, the end-to-end run, or the code review still failing after 1 fix.
- **`aborted`** when an agent returns no usable result, at any stage.
- Never mark a task complete unless verification passed **and** the code review approved.
- If a stage escalates because the task turned out to need decisions this pipeline cannot make, say so and point at `/orchestrate` — do not improvise an interview here.

## Rules
The four skills carry the rules they own — `agent-pipeline` for the spawn-once, one-tool-block, thin-prompt and no-duplicate-gate mechanics, `ticket-board` for the transitions and the roadmap, `sdlc-structure` for the paths, `technical-writing` for the prose. What is this command's own:
- **One task at a time.** Do not execute the whole roadmap.
- **Load every skill in the table before the stage that needs it.** They are the rules; this file is the sequence.
- **No interview, no gates.** The plan review and the code review each run exactly once, on sonnet.
- **One question, at the end.** The only `AskUserQuestion` call is Stage 7's end-to-end offer. No verify run before it touches an e2e suite.
- **One revision, two targeted fixes, one dispute round, one fix.** Every cap is hard, and the single fix cycle covers the verification failures, the review issues, and an end-to-end failure together.
- **Tests before code, and the coder never touches them.** A test changes only by a `revised` ruling. Only an empty test plan skips the test stages.
- **You write the status, the assignee, and the worklog** — at the boundaries in the table and at every exit. No agent writes any of them.
- **Approval is required only when you picked the task from a roadmap.**
- **Be explicit about failures** and propose next steps.
