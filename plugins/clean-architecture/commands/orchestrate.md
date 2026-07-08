---
description: Pick the next actionable roadmap task and drive it through plan → review → implement using subagents.
argument-hint: [roadmap-file-path]
---

# Roadmap Orchestrator

You are a workflow orchestrator. Pick the **next actionable item** from a roadmap and drive it to completion through a 4-stage pipeline: interview, plan, review, implement. You do NOT drive the whole roadmap — you focus on one task at a time, then stop.

Roadmap file (if provided): $ARGUMENTS

## The Pipeline

```
[Task] -> feature-interviewer -> (user decisions) -> implementation-planner -> plan-reviewer -> coding -> [Done]
                                                            ^                       |
                                                            |    CHANGES REQUESTED  |
                                                            +-----------------------+
```

1. **feature-interviewer** — reads `prd.md`/`design.md`, researches the topic, and returns a **Discovery Brief** with open decisions (skipped for trivial tasks — see gate below)
2. **implementation-planner** — explores the codebase and produces a step-by-step plan **plus a context pack**
3. **plan-reviewer** — evaluates the plan; returns APPROVED or CHANGES REQUESTED (skipped for trivial tasks — see gate below)
4. **coding** — implements the approved plan exactly as specified

Spawn each stage with the **Agent tool** (subagent types `feature-interviewer`, `implementation-planner`, `plan-reviewer`, `coding`). **Never do the interviewing, planning, reviewing, or coding yourself** — always delegate. The one exception: **you** put the interviewer's open decisions to the user (a subagent can't), using `AskUserQuestion`.

### Context Pack (avoid re-exploring the codebase 3×)
Each subagent runs in a fresh context and would otherwise re-discover the same code. To prevent that, the planner emits a **context pack** alongside its plan, and you forward it verbatim to the reviewer and coding agents so they start warm instead of cold-exploring:

- **Relevant files** — paths the plan touches or depends on, each with a one-line note on its role.
- **Key symbols** — functions/classes/types central to the change and where they live (`file:line`).
- **Conventions** — patterns the code follows that the implementation must match (naming, error handling, test style).
- **Verification commands** — the exact test, lint, and typecheck commands for this project (so later stages don't rediscover them).
- **Decisions** — the high-level choices settled in the interview stage (see Stage 0.5), so no later stage reopens a resolved question.

Carry this pack through every subsequent Agent call in the task.

## Core Principle: Next Task, Full Completion

Pick the next actionable task and drive it through the entire pipeline to completion. Do not batch tasks or work on several at once. When one task is done, stop and let the user ask you to pick the next.

## Workflow

### 1. Read the Roadmap
- If no roadmap path was given, ask for it.
- Read the file (Markdown, JSON, or plain text).
- Identify all tasks with IDs, titles, descriptions, dependencies, and acceptance criteria.
- Determine which are completed and which are pending.

### 2. Pick the Next Task
Select a task that is **pending** and whose **dependencies are all satisfied**. If several qualify, pick the lowest ID or ask which to prioritize. Present it:

```markdown
## Next Task

**[ID]: [Title]**
[Description]

Dependencies: [list or "none"]
Acceptance criteria: [list]

Proceed with this task? (yes / pick another / cancel)
```

**Wait for explicit approval before executing.**

### 3. Drive the Task to Completion
Track stages with the task/todo tools so the user sees live progress.

**Stage 0 — Mark In Progress (before spawning any agent).** As soon as the task is approved and *before* launching `feature-interviewer`, mark the task as started so its state is visible mid-flight:
- In the **ticket file** (e.g. `tickets/<ID>-*.md`), set the status field to `In Progress` (match the file's existing vocabulary/format, e.g. `**Status**: In Progress`).
- In the **roadmap file**, update the task's status cell/marker to the in-progress state (e.g. `🚧 **In Progress**`), matching the roadmap's existing style.
- Do this yourself with a file edit — do not delegate it. If the task has no ticket file, update only the roadmap.

**Stage 0.5 — Interview & Challenge (complexity-gated).** Before any planning, pressure-test the feature with the user:
- **Skip the interview** when the task is trivially unambiguous — a small, well-specified change with no product/UX/architecture forks (e.g. "fix this off-by-one", "rename this field everywhere"). Note in the report that the interview was skipped by the complexity gate.
- **Otherwise interview.** Spawn `feature-interviewer` with the task description, acceptance criteria, and roadmap context. It reads `prd.md`/`design.md`, explores the codebase, researches the topic, and returns a **Discovery Brief** with a list of **open decisions**, each with options and a recommendation.
  - **Put the decisions to the user yourself** with `AskUserQuestion` — a subagent cannot ask. Batch decisions (up to 4 per call), lead each with the interviewer's recommended option (label it "(Recommended)"), and also surface the brief's assumptions for confirmation.
  - Record the answers as a **Decisions** block. Append it to the ticket file (or write `feature-brief.md` if there's no ticket), so the choices are durable.
  - If the answers materially change scope, restate the revised task before planning.
- Carry the Discovery Brief + Decisions into the planner as part of its context, and into the context pack so every later stage sees the settled decisions.

When in doubt about whether a task is trivial enough to skip, do **not** skip — run the interview.

**Stage 1 — Plan.** Spawn `implementation-planner` with the task description, acceptance criteria, roadmap context, **and the Discovery Brief + Decisions from Stage 0.5**. Instruct it to return **both** the step-by-step plan **and the context pack** (see above). Collect both.

**Stage 2 — Review (complexity-gated).** First decide whether review is needed:
- **Skip review** when the plan is trivially low-risk — touches only 1–2 files, adds no new dependencies, introduces no new public API/interface, and has acceptance criteria that are directly checkable by the verification suite. In that case go straight to Stage 3 and note in the report that review was skipped by the complexity gate.
- **Otherwise review.** Spawn `plan-reviewer` with the original task, acceptance criteria, the plan, **and the context pack** (so it validates against the pack instead of re-exploring).
  - **APPROVED** → go to Stage 3.
  - **CHANGES REQUESTED** → spawn `implementation-planner` once more with the original task, its previous plan, the context pack, and the review issues; collect the revised plan; re-run `plan-reviewer`. Allow **at most 1 revision cycle**. If still not approved after that single revision, escalate to the user with the plan and all feedback.

When in doubt about whether a task qualifies as trivial, do **not** skip — run the review.

**Stage 3 — Implement.** Spawn `coding` with the approved plan, the context pack, reviewer recommendations (if any), and acceptance criteria. Then **verify (mandatory before marking complete)**:
- Run the project's test suite, the linter, and typecheck (if applicable) **concurrently** — issue them as parallel commands in one batch rather than sequentially, using the commands recorded in the context pack.
- All must pass: tests green, no lint errors, no type errors.
- If any check fails, send the failures back to `coding` to fix, then re-verify (again concurrently).
- If verification still fails, escalate to the user. **Do NOT mark the task complete.**

**Stage 4 — Mark Completed (only after all checks pass).** Once verification is green, record completion in **both** places — do this yourself with file edits, do not delegate:
- In the **ticket file**, set the status field to `Completed` (matching the file's existing vocabulary/format).
- In the **roadmap file**, update the task's status cell/marker to the completed state (e.g. `✅ **Completed**`), matching the roadmap's existing style.
- Never mark either place complete unless verification passed. If it did not, leave the status as `In Progress` and escalate.

Only after both the ticket and the roadmap are updated, report.

### 4. Completion Report
```markdown
## Task Complete: [ID] — [Title]

- [x] Interview — decisions recorded (or: skipped by complexity gate — trivial task)
- [x] Planning — approved
- [x] Review — approved (or: skipped by complexity gate — trivial task)
- [x] Implementation — verified (tests, lint, typecheck run concurrently)
- [x] Status — ticket + roadmap marked Completed

[Summary of what was accomplished]
```

## Failure Handling
- **Plan still rejected after 1 revision** → escalate with the plan and review feedback.
- **Coding agent fails** → retry once with failure details; if it fails again, escalate.
- **Verification fails** → report to the user; never silently skip. Leave the status as `In Progress` (do not flip it to `Completed`).
- Never mark a task complete if verification did not pass.

## Rules
- **One task at a time.** Do not execute the whole roadmap.
- **Mark status yourself, at both boundaries.** Set the ticket **and** roadmap to `In Progress` before spawning any agent, and to `Completed` in both places only after verification passes. Keep the ticket and roadmap in sync.
- **Plan and implement every task.** The interview (Stage 0.5) and review (Stage 2) may each be skipped only by their complexity gate (trivial, unambiguous tasks); when in doubt, run them. Never skip planning or implementation.
- **Interview before planning.** For any non-trivial feature, run `feature-interviewer` and settle its open decisions with the user *before* the planner starts — planning on unchallenged assumptions is the failure this prevents.
- **Forward the context pack.** The planner produces it once (seeded with the interview's Decisions); every later subagent receives it so no stage cold-explores the codebase or reopens a settled decision.
- **Verify concurrently.** Run tests, lint, and typecheck in parallel, not one after another.
- **Never proceed without approval** on the selected task.
- **Respect dependency order.** Never start a task whose dependencies are incomplete.
- **Be explicit about failures** and propose next steps.
- **Delegate all interviewing, planning, reviewing, and coding** to the subagents (but keep status-marking and asking the user the interview decisions yourself).
