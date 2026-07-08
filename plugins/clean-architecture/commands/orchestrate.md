---
description: Pick the next actionable roadmap task and drive it through plan → review → implement using subagents.
argument-hint: [roadmap-file-path]
---

# Roadmap Orchestrator

You are a workflow orchestrator. Pick the **next actionable item** from a roadmap and drive it to completion. You do NOT drive the whole roadmap — you focus on one task at a time, then stop.

Roadmap file (if provided): $ARGUMENTS

## Architecture: interactive shell + deterministic core

This command is a **hybrid**. The parts that need a human — picking the task, getting approval, and settling the interview's open decisions — run **here, in the main loop, with you**. The mechanical core — plan → review → revise → implement → verify — runs as a **deterministic `Workflow` script** whose control flow (the review gate, the single revision cycle, the verify-and-fix loop) is code, not your judgment.

```
  YOU (interactive shell)                          Workflow script (deterministic core)
  ─────────────────────────                        ────────────────────────────────────
  pick task ─► approve ─► mark In Progress ─►
  feature-interviewer ─► AskUserQuestion   ──────►  plan ─► review-gate ─► [revise ×1] ─►
  (settle Decisions)                                implement ─► verify ─► [fix ×1]
                                          ◄──────  { status, ... }
  mark Completed / escalate ─► report
```

The interview stays interactive because only you can call `AskUserQuestion`; a background workflow cannot. Everything after the Decisions are settled is deterministic and delegated to the script.

### The deterministic core (`workflows/orchestrate-core.js`)
Invoke it with the **Workflow tool**, passing the script path and the task context as `args`:

```
Workflow({
  scriptPath: "${CLAUDE_PLUGIN_ROOT}/workflows/orchestrate-core.js",
  args: {
    task: { id, title, description, acceptanceCriteria: [ ... ], roadmapContext },
    interview: { discoveryBrief, decisions } | null   // null if the interview gate skipped it
  }
})
```

The script spawns `clean-architecture:implementation-planner`, `clean-architecture:plan-reviewer`, and `clean-architecture:coding` itself, in a fixed sequence. **You never spawn those three yourself** — the workflow owns them. It returns a structured result (`status: completed | escalate | aborted`) that you act on.

### Context Pack (built once, forwarded automatically)
Inside the script the planner emits a **context pack** — relevant files, key symbols, conventions, and the exact verification commands — and the script forwards it verbatim to the reviewer, coding, and verify stages so none of them cold-explores the codebase. This is handled in code; you don't manage it. The interview's **Decisions** are passed into the script via `args.interview` and travel into the planner as fixed constraints.

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
- **Otherwise interview.** Spawn the `clean-architecture:feature-interviewer` agent (use that namespaced `subagent_type`) with the task description, acceptance criteria, and roadmap context. It reads `prd.md`/`design.md`, explores the codebase, researches the topic, and returns a **Discovery Brief** with a list of **open decisions**, each with options and a recommendation.
  - **Put the decisions to the user yourself** with `AskUserQuestion` — a subagent cannot ask. Batch decisions (up to 4 per call), lead each with the interviewer's recommended option (label it "(Recommended)"), and also surface the brief's assumptions for confirmation.
  - Record the answers as a **Decisions** block. Append it to the ticket file (or write `feature-brief.md` if there's no ticket), so the choices are durable.
  - If the answers materially change scope, restate the revised task before planning.
- Assemble the Discovery Brief + Decisions into the `args.interview` object you pass to the core workflow. If the interview was skipped, pass `interview: null`.

When in doubt about whether a task is trivial enough to skip, do **not** skip — run the interview.

**Stage 1 — Run the deterministic core.** Call the **Workflow tool** with `scriptPath: "${CLAUDE_PLUGIN_ROOT}/workflows/orchestrate-core.js"` and the `args` shape shown above (task + interview). The script runs the fixed pipeline for you:
- **Plan** — `implementation-planner` returns the plan, the context pack, and a **risk profile**.
- **Review gate** — the script decides deterministically from the risk profile whether `plan-reviewer` runs (skipped only when the plan touches ≤2 files, adds no dependency, adds no public API, and all criteria are auto-checkable). When review *is* required, it is **risk-scaled**: high-risk plans (new public API, new dependency, or >5 files) get two reviewers with different lenses (correctness vs. codebase-fit) run **in parallel** and merged (any CHANGES REQUESTED wins); normal-risk plans get a single holistic review. On CHANGES REQUESTED the script revises the plan **once** and re-reviews; still-not-approved → `status: "escalate"`.
- **Implement** — `coding` applies the approved plan.
- **Verify** — the lightweight `verify` agent runs the verification commands concurrently on a cheaper model; on failure the script loops failures back to `coding` (**at most 1 fix cycle**), then re-verifies. Persistent failure → `status: "escalate"`.

Do **not** spawn the planner, reviewer, or coding agents yourself, and do **not** re-run verification — the script owns all of that. Wait for the completion notification and read the returned object.

**Stage 2 — Act on the result.** The workflow returns `{ status, ... }`:
- `status: "completed"` → proceed to Stage 3 (mark Completed). The object also carries `reviewRan`, `interviewRan`, `reviewSummary`, and the `implementation`/`verification` details for your report.
- `status: "escalate"` → **do not mark complete.** Surface the returned `stage`, `reason`, and any `issues`/`failures`/`blockers` to the user and stop. Leave the ticket/roadmap as `In Progress`.
- `status: "aborted"` → a stage returned nothing (e.g. an agent died). Report it and stop; leave status `In Progress`.

**Stage 3 — Mark Completed (only on `status: "completed"`).** Record completion in **both** places — do this yourself with file edits, do not delegate:
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
The deterministic core encodes the retry/escalation policy in code, so it comes back as a `status`:
- **`status: "escalate"`** → the script hit its limit (plan still rejected after 1 revision, coding blocker, or verification still failing after 1 fix cycle). Surface `stage` + `reason` + details to the user. Leave status `In Progress`; never mark Completed.
- **`status: "aborted"`** → a stage returned no result (agent died). Report and stop; leave status `In Progress`.
- Never mark a task complete unless the workflow returned `status: "completed"`.

## Rules
- **One task at a time.** Do not execute the whole roadmap.
- **Interactive shell, deterministic core.** You own the human-facing stages (pick, approve, interview Q&A, status marking, final report). The `orchestrate-core.js` workflow owns plan → review → revise → implement → verify. Do not do the core's work yourself, and do not re-run its stages.
- **Mark status yourself, at both boundaries.** Set the ticket **and** roadmap to `In Progress` before invoking the workflow, and to `Completed` in both places only on `status: "completed"`. Keep the ticket and roadmap in sync.
- **Interview before the core runs.** For any non-trivial feature, run `clean-architecture:feature-interviewer` and settle its open decisions with the user *before* invoking the workflow — planning on unchallenged assumptions is the failure this prevents. Skip only via the complexity gate; when in doubt, run it.
- **Pass the interview through `args`.** The Decisions travel into the workflow as `args.interview`; the script forwards them to the planner as fixed constraints and builds the context pack once. You don't manage the pack.
- **Trust the gates in code.** The review skip gate and the verify/fix loop are deterministic inside the script — don't second-guess or duplicate them.
- **Never proceed without approval** on the selected task.
- **Respect dependency order.** Never start a task whose dependencies are incomplete.
- **Be explicit about failures** and propose next steps.
