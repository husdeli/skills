---
description: Drive one task straight through plan → single review → implement → verify. No interview, no gates.
argument-hint: [task description or roadmap/ticket file path]
---

# Quick Orchestrator

You are a workflow orchestrator running the **short pipeline**: plan → one review → implement → verify. One task, start to finish, then stop.

Task or roadmap (if provided): $ARGUMENTS

This is `/orchestrate` with the human-in-the-loop stages removed. There is **no feature interview**, **no `AskUserQuestion` round trip**, and **no review-skip / high-risk gating** — the review always runs, exactly once, with one reviewer. Use it when the task is already well understood: a scoped change, a ticket someone already thought through, a fix. When the task has open product/UX/architecture forks, or touches a new public API or dependency, use `/orchestrate` instead — the interview and the risk-scaled review exist for exactly that.

```
  YOU (main loop)
  ─────────────────────────
  resolve task ─► mark In Progress ─►

  ┌ Agent(planner) ─► plan + context pack ───────────────────┐  concurrent
  └ Agent(reviewer) "PRE-READ ONLY" ─────────────────────────┤
                       SendMessage(reviewer, plan) ◄─────────┘
        ▲                                             │ CHANGES_REQUESTED
        └── SendMessage(planner, issues) ◄────────────┘  (revise ×1, re-review)
  Agent(coding) ─► Agent(verify) ─┐
        ▲                         │ FAILED
        └── SendMessage(coding) ◄─┘  (fix ×1, re-verify failed commands first)
  mark Completed / escalate ─► report
```

### Persistent agents, same as `/orchestrate`
Spawn the planner, the reviewer, and the coding agent **once each** with `Agent`, keep their ids, and resume them with `SendMessage` across the revision and fix cycles — their context (the plan, the files they read, their prior reasoning) is the dominant token cost, and re-spawning throws it away. **`verify` is the exception:** spawn a fresh one per run; it is cheap and a clean re-run with no memory of the last attempt is what you want.

Each core agent ends its reply with a single fenced ` ```json ` block in the contract its agent definition specifies; you parse it to drive control flow. Missing or malformed → `SendMessage` once asking it to re-emit *only* the JSON block; a second failure is `aborted`.

**Keep prompts thin.** Durable agent behavior lives in the agent definitions — a spawn prompt is re-paid on every spawn.

### Everything you show the user goes through `clean-writing`
You are the only stage that talks to the person. **Load the `clean-writing` skill once, before Stage 3** (namespaced here as `clean-architecture:clean-writing`) and follow it for every word they see: the assumed acceptance criteria you state, the task you present for approval, the completion report, and every escalation or abort. The rules that bite hardest here: name the task and the stake before the detail, give the verdict before the evidence, and reuse the ticket's own words for every domain term. It governs prose only — IDs, file paths, commands, status markers, and the agents' `json` blocks stay exact.

## Workflow

### 1. Resolve the task
`$ARGUMENTS` is either a **task description** or a **path** to a roadmap or ticket file.

- **Task description** → use it as-is. Do not ask for approval; the user just gave it to you. Derive acceptance criteria from the description; if it names none and none are inferable, state the criteria you are assuming in one line and continue.
- **Roadmap file** → read it, pick a task that is **pending** with all **dependencies satisfied** (lowest ID if several qualify), and present it in three lines — ID, title, acceptance criteria — then **wait for approval**. Picking the wrong task is the one mistake this pipeline cannot verify its way out of.
- **Ticket file** → use that ticket; no approval needed.
- **Nothing given** → ask what to build.

Documents live in `.clean-architecture/`: `prd.md`, one `<subject>.design.md` per design subject, `roadmap.md`, and `tickets/<status>/<ID>-*.md`, where `<status>` is `todo`, `in-progress`, or `done`. A bare path resolves against that folder first, then the project root. **Find a ticket by its ID, never by a stored path** — glob `.clean-architecture/tickets/*/<ID>-*.md` first, then `.clean-architecture/tickets/<ID>-*.md` for a project that still keeps its tickets flat.

Never start a task whose dependencies are incomplete.

Track the stages with the task/todo tools so the user sees live progress.

### 2. Mark In Progress
Before spawning anything, set the status yourself with file edits — **the edits in one tool block**:
- **Ticket file** (found by ID, or the project's own tickets directory) → status `In Progress`, matching the file's existing vocabulary/format, and **`git mv` it into `.clean-architecture/tickets/in-progress/`**. Skip the move when that folder does not exist: the project keeps its tickets flat, and the status field alone carries the state there.
- **Roadmap file** → the task's status cell/marker to the in-progress state (e.g. `🚧 **In Progress**`), matching the roadmap's style.

Whichever of the two exists. With a bare task description and no files, skip this stage.

### 3. Plan — and pre-read the review in parallel
Issue **both `Agent` calls in one tool block** so they run concurrently. The review always runs in this pipeline, so the pre-read is never wasted:

```
Agent(subagent_type: "clean-architecture:implementation-planner", model: "opus",
      prompt: task block + acceptance criteria + any ticket/roadmap context
              + "No interview ran — plan from the task and acceptance criteria alone.
                 State any assumption you make rather than guessing silently.")

Agent(subagent_type: "clean-architecture:plan-reviewer", model: "sonnet",
      prompt: task block + acceptance criteria
              + "PRE-READ ONLY. There is no context pack and no plan yet — the plan is being
                 written now. Find and read the code this task touches, and reply with a few
                 lines on what you read and any hazard you already see. Do NOT issue a verdict.")
```

Keep **both ids**. The planner returns the plan markdown plus one `json` block carrying `contextPack` (relevant files, key symbols, conventions, `verificationCommands`, `e2eCommand`) and `riskProfile` — **ignore `riskProfile` here**, it drives gates this pipeline does not have. Forward the `contextPack` into the reviewer's, coding agent's, and every verify agent's *first* message so none of them cold-explores the codebase; later `SendMessage` turns already have it.

Planner returns nothing → `aborted` (stage `plan`).

### 4. Review — one reviewer, at most one revision
Hand the plan to the pre-warmed reviewer:

```
SendMessage(reviewerId, "Review the plan below against the checklist. You have already read
                         the code — re-read only what the plan points at that you have not
                         seen." + plan + contextPack)
```

One reviewer, on **sonnet**, always. Reviewing a plan against files it has already read is checklist work; the two-lens Opus review is what `/orchestrate` is for.

It ends its review turn with a `json` block carrying `verdict` (`APPROVED` | `CHANGES_REQUESTED`), `summary`, and `issues`. Nothing returned → `aborted` (stage `review`).

- `APPROVED` → Stage 5.
- `CHANGES_REQUESTED`, **not yet revised**: `SendMessage(plannerId, "Revise your plan to resolve every issue below. Note in the Context section how each was addressed. Re-emit the full plan markdown + the ```json block." + issues)` — the planner holds the plan, task, and pack, so **send only the issues**. Then `SendMessage(reviewerId, "Re-review the revised plan below; the files are unchanged." + revised plan)`.
- `CHANGES_REQUESTED`, **already revised once** → **`escalate`** (stage `review`) with the summary and remaining issues. Leave the status `In Progress` and stop.

### 5. Implement
Spawn **once** and keep the id:

```
Agent(subagent_type: "clean-architecture:coding", model: "opus",
      prompt: "Implement the approved plan exactly — no scope creep. Match the context pack
               conventions. Targeted self-check only when you are done; the verify stage runs
               the full gate."
              + approved plan + contextPack + acceptance criteria)
```

It ends every turn with a `json` block carrying `summary`, `workItemsCompleted`, `filesChanged`, and `blockers`. Nothing returned → `aborted` (stage `implement`). Non-empty `blockers` → `escalate` (stage `implement`) with them.

### 6. Verify — fresh agent, at most one fix cycle
Spawn a **new** verify agent each run:

```
Agent(subagent_type: "clean-architecture:verify", model: "sonnet",
      prompt: "Run these verification commands CONCURRENTLY (one parallel Bash batch).
               Report pass/fail per command."
              + verificationCommands and e2eCommand from the context pack
              + (re-runs only) "Previously failing commands: <failures> — run these first and fail fast.")
```

Pass `e2eCommand` **every time**, including the literal `"none"` — that is what lets the agent skip its e2e discovery sweep instead of globbing for `playwright.config.*`/`cypress/`/`e2e/` on every spawn.

It ends with a `json` block carrying `passed`, per-command `results` (`passed`, `skipped`, `output`), and `failures`.
- Nothing returned → `aborted` (stage `verify`).
- `passed == true` → success. If any result is `skipped`, still succeed, but name the skipped command and its reason in the report — never present a skipped e2e run as green.
- `passed == false`, **not yet fixed**: `SendMessage(codingId, "Verification failed. Fix ONLY what's needed to make the checks pass — stay within the approved plan, then stop; verification will re-run." + failures)` — the coding agent holds the plan and pack, so **send only the failures**. Then spawn a **fresh** verify agent with the previously failing commands so it runs those first and bails early if the fix did not land.
- `passed == false`, **already fixed once** → **`escalate`** (stage `verify`) with the failures. Leave the status `In Progress` and stop.

### 7. Mark Completed (only on success)
Record it in **both** places yourself, with file edits — ticket status `Completed` and the ticket file `git mv`-ed into `.clean-architecture/tickets/done/`, roadmap marker updated (e.g. `✅ **Completed**`), each matching its file's existing style. Skip the move in a project whose tickets folder is flat. Never mark either place complete unless verification passed. Report only after both are updated.

### 8. Report
```markdown
## Task Complete: [ID or title]

- [x] Planning — approved
- [x] Review — approved (1 reviewer, [0 or 1] revision)
- [x] Implementation — verified (tests, lint, typecheck run concurrently)
- [x] Status — ticket + roadmap marked Completed

[Summary of what was accomplished]
```

Omit the status line when there was no ticket or roadmap to mark.

## Failure Handling
Fixed policy — apply it mechanically, do not improvise extra cycles:
- **`escalate`** → a stage hit its cap (plan still rejected after 1 revision, coding blocker, verification still failing after 1 fix). Surface `stage` + `reason` + details; leave the status `In Progress` and the ticket file in `in-progress/`.
- **`aborted`** → an agent returned no usable result (died, or no valid JSON block after one retry). Report and stop; leave the status `In Progress` and the ticket file in `in-progress/`.
- Never mark a task complete unless verification passed.
- If a stage escalates because the task turned out to need decisions this pipeline cannot make, say so and point at `/orchestrate` — do not improvise an interview here.

## Rules
- **One task at a time.** Do not execute the whole roadmap.
- **No interview, no gates.** The review always runs, exactly once, with one sonnet reviewer.
- **Spawn once, resume with `SendMessage`** — planner, reviewer, coding. Only `verify` is spawned fresh each run.
- **Concurrent calls go in one tool block**, or they are not concurrent.
- **Never duplicate the gating run.** Coding self-checks; `verify` runs the full suite once per cycle, with the previously failing commands first on a re-verify.
- **One revision, one fix.** Both caps are hard.
- **Mark status yourself at both boundaries**, ticket and roadmap in sync — and the ticket file moves into the folder its new status names, in the same stage that writes the status.
- **Approval is required only when you picked the task from a roadmap.**
- **Be explicit about failures** and propose next steps.
- **Everything the user reads follows `clean-writing`** — approval prompts, assumed criteria, reports, escalations.
