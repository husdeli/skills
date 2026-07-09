---
description: Pick the next actionable roadmap task and drive it through plan → review → implement using persistent subagents.
argument-hint: [roadmap-file-path]
---

# Roadmap Orchestrator

You are a workflow orchestrator. Pick the **next actionable item** from a roadmap and drive it to completion. You do NOT drive the whole roadmap — you focus on one task at a time, then stop.

Roadmap file (if provided): $ARGUMENTS

## Architecture: interactive shell + persistent-agent core

This command runs entirely **in the main loop, with you**. The human-facing stages — picking the task, getting approval, settling the interview's open decisions, marking status — need you because only you can talk to the user. The mechanical core — plan → review → revise → implement → verify — you drive yourself with **persistent subagents**: you spawn the planner, reviewer, and coding agent **once each** with the `Agent` tool, then **resume them with `SendMessage`** across revision and fix cycles so their context (the plan, the files they read, the prior reasoning) stays alive instead of being re-sent every cycle.

```
  YOU (main loop)
  ─────────────────────────
  pick task ─► approve ─► mark In Progress ─►
  feature-interviewer ─► AskUserQuestion (settle Decisions) ─►
  Agent(planner) ─► [review gate] ─► Agent(reviewer) ─┐
        ▲                                             │ CHANGES_REQUESTED
        └── SendMessage(planner,reviewer) ◄───────────┘  (revise ×1, re-review)
  Agent(coding) ─► Agent(verify) ─┐
        ▲                         │ FAILED
        └── SendMessage(coding) ◄─┘  (fix ×1, re-verify)
  mark Completed / escalate ─► report
```

### Why persistent agents
The planner, reviewer, and coding agents each run inside a loop (revise, re-review, fix). Re-spawning them fresh each cycle forces them to re-ingest the whole plan, re-read the same files, and re-derive their reasoning — the dominant token cost. Instead:

- **Spawn once, keep the handle.** Every `Agent` call returns an id/name. Record the planner's, the reviewer's (two, for high-risk parallel lenses), and the coding agent's.
- **Resume, don't respawn.** On a revision, `SendMessage` the *same* planner just the review issues — it already holds the plan, task, and context pack. On a re-review, `SendMessage` the *same* reviewer just "re-review the revised plan" — it already read the files. On a fix, `SendMessage` the *same* coding agent just the failures.
- **Verify is the exception — it stays fresh.** Spawn a new `clean-architecture:verify` agent for each verification run. It is cheap (Sonnet, low effort) and a clean re-run with no memory of the prior attempt is exactly what you want.

You own all of this in the main loop — there is no background workflow. Because there is no schema enforcement, **each core agent must end its reply with a single fenced ` ```json ` block** in the contract shown per stage; you parse that block to drive control flow. If a block is missing or malformed, `SendMessage` the agent once asking it to re-emit *only* the JSON block; a second failure is an `aborted` result.

### Context Pack (built once, forwarded automatically)
The planner emits a **context pack** — relevant files, key symbols, conventions, and the exact verification commands — in its JSON block. You carry it forward: paste it into the reviewer's and coding agent's *first* message so none of them cold-explores the codebase (on later `SendMessage` turns they already have it). The interview's **Decisions** go into the planner's first message as fixed constraints.

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
- Keep the Discovery Brief + Decisions handy — you inject them into the planner's first message. If the interview was skipped, tell the planner to plan from the task description and acceptance criteria alone.

When in doubt about whether a task is trivial enough to skip, do **not** skip — run the interview.

**Stage 1 — Plan (persistent planner).** Spawn the planner **once** and keep its id:

```
Agent(subagent_type: "clean-architecture:implementation-planner", model: "opus",
      prompt: task block + acceptance criteria + roadmap context
              + Discovery Brief & Decisions (or "no interview ran")
              + "Return your Implementation Plan as markdown, then end with a single ```json block:")
```

Required JSON contract the planner must end with:
```json
{
  "contextPack": {
    "relevantFiles": [{ "path": "", "role": "" }],
    "keySymbols":    [{ "symbol": "", "location": "" }],
    "conventions":   [""],
    "verificationCommands": [""]
  },
  "riskProfile": {
    "filesTouched": 0,
    "addsDependency": false,
    "addsPublicApi": false,
    "criteriaAutoCheckable": false
  }
}
```
Keep the plan markdown as `plan` and the parsed `contextPack` / `riskProfile` in hand. If the planner returns nothing → `aborted` (stage `plan`).

**Stage 2 — Review gate + review (persistent reviewer, at most one revision).** Apply the gate **mechanically** from `riskProfile` — do not use judgment here:

- **Skip review** iff `filesTouched ≤ 2` **and** `addsDependency == false` **and** `addsPublicApi == false` **and** `criteriaAutoCheckable == true`. Log "Review gate: SKIPPED" and go to Stage 3 with the plan as approved.
- Otherwise **review is required**. It is **high-risk** iff `addsPublicApi == true` **or** `addsDependency == true` **or** `filesTouched > 5`.
  - **Normal risk:** spawn **one** `clean-architecture:plan-reviewer` (opus). First message = task block + Decisions + the full plan + the context pack + "Read the referenced files — do not review from the plan text alone. Review holistically for correctness, completeness, and convention-alignment."
  - **High risk:** spawn **two** reviewers **in one message** (concurrent), each with the same base but a distinct lens: (a) *correctness/completeness* — will the plan satisfy every acceptance criterion; missing steps, wrong assumptions, edge cases, ordering hazards; (b) *codebase fit* — conventions, dependency rules, architectural boundaries, unjustified new API/deps. Keep **both** ids.

Every reviewer must end with:
```json
{ "verdict": "APPROVED" | "CHANGES_REQUESTED", "summary": "",
  "issues": [{ "title": "", "severity": "critical|major|minor", "steps": "", "problem": "", "suggestion": "" }] }
```
Merge multiple reviewers: verdict is `CHANGES_REQUESTED` if **any** reviewer requests changes; concat their issues. If every reviewer returned nothing → `aborted` (stage `review`).

**Revision loop — at most ONE cycle:**
- If verdict is `APPROVED` → proceed to Stage 3.
- If `CHANGES_REQUESTED` and you have **not yet revised**: `SendMessage(plannerId, "Revise your plan to resolve every issue below. Note in the Context section how each was addressed. Re-emit the full plan markdown + the ```json block." + issues)`. The planner already holds the plan/task/pack — **send only the issues**. Then re-review by **`SendMessage`-ing the same reviewer(s)**: `"Re-review the revised plan below; the files are unchanged. <revised plan>"`. Loop back to check the new verdict.
- If `CHANGES_REQUESTED` and you have **already revised once** → **`escalate`** (stage `review`): surface the reviewer summary + remaining issues, leave status `In Progress`, stop.

**Stage 3 — Implement (persistent coding agent).** Spawn coding **once** and keep its id:

```
Agent(subagent_type: "clean-architecture:coding", model: "opus",
      prompt: "Implement the approved plan exactly — no scope creep. Follow the react-clean skill for any React file. Match the context pack conventions."
              + approved plan + context pack + acceptance criteria + the JSON contract)
```
Coding must end with:
```json
{ "summary": "", "stepsCompleted": [""], "filesChanged": { "created": [""], "modified": [""] }, "blockers": [""] }
```
If it returns nothing → `aborted` (stage `implement`). If `blockers` is non-empty → `escalate` (stage `implement`) with the blockers.

**Stage 4 — Verify (fresh agent) + fix (persistent coding, at most ONE fix cycle).** Spawn a **new** `clean-architecture:verify` agent (sonnet, low effort) each run:

```
Agent(subagent_type: "clean-architecture:verify", model: "sonnet",
      prompt: "Run these verification commands CONCURRENTLY (one parallel Bash batch), then report pass/fail per command."
              + verificationCommands from the context pack + the Decisions
              + judging & output-hygiene rules below + the JSON contract)
```
Judging & hygiene rules to include verbatim: judge by whether THIS change *introduced* failures, not absolute exit codes (a command non-zero only due to a known pre-existing baseline, e.g. `tsc -b`, is a PASS at/below baseline); gate only on the project's actual gating commands (build, tests, lint, config validation) per the Decisions/criteria; cap each result's `output` to ~3 short lines, never paste full dumps; make exactly ONE final JSON block. Contract:
```json
{ "passed": true, "results": [{ "command": "", "passed": true, "output": "" }], "failures": [""] }
```
- If it returns nothing → `aborted` (stage `verify`).
- If `passed == true` → success, go to Stage 3-of-§3 (mark Completed).
- If `passed == false` and you have **not yet fixed**: `SendMessage(codingId, "Verification failed. Fix ONLY what's needed to make the checks pass — stay within the approved plan, then stop; verification will re-run." + failures)` — the coding agent already holds the plan/pack, **send only the failures**. Then spawn a **fresh** verify agent and re-check.
- If `passed == false` and you have **already fixed once** → **`escalate`** (stage `verify`) with the failures, leave status `In Progress`, stop.

**Act on the result.** You have assembled one of:
- **`completed`** → proceed to mark Completed (below). Keep `reviewRan`, `interviewRan`, the reviewer summary, and the implementation/verification details for the report.
- **`escalate`** → **do not mark complete.** Surface the `stage`, `reason`, and any `issues`/`failures`/`blockers`; leave the ticket/roadmap as `In Progress`; stop.
- **`aborted`** → an agent returned nothing. Report it; leave status `In Progress`; stop.

**Mark Completed (only on success).** Record completion in **both** places — do this yourself with file edits, do not delegate:
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
The core encodes a fixed retry/escalation policy — apply it mechanically, do not improvise extra cycles:
- **`escalate`** → a stage hit its limit (plan still rejected after 1 revision, coding blocker, or verification still failing after 1 fix cycle). Surface `stage` + `reason` + details. Leave status `In Progress`; never mark Completed.
- **`aborted`** → an agent returned no usable result (died, or emitted no valid JSON block after one retry). Report and stop; leave status `In Progress`.
- Never mark a task complete unless verification passed.

## Rules
- **One task at a time.** Do not execute the whole roadmap.
- **Spawn once, resume with `SendMessage`.** The planner, reviewer(s), and coding agent are persistent — spawn each with `Agent` a single time and resume by id for revisions/fixes. Re-spawning them mid-task defeats the purpose (it re-sends the plan and re-reads files). Only `verify` is spawned fresh each run.
- **Mark status yourself, at both boundaries.** Set the ticket **and** roadmap to `In Progress` before spawning any agent, and to `Completed` in both places only on success. Keep the ticket and roadmap in sync.
- **Interview before planning.** For any non-trivial feature, run `clean-architecture:feature-interviewer` and settle its open decisions with the user *before* spawning the planner — planning on unchallenged assumptions is the failure this prevents. Skip only via the complexity gate; when in doubt, run it.
- **Build the context pack once, forward it.** The planner emits it; you paste it into the reviewer's and coding agent's first message so none of them cold-explores the codebase.
- **Apply the gates mechanically.** The review-skip gate (≤2 files, no dep, no API, criteria auto-checkable), the high-risk test (new API/dep or >5 files), the single revision cap, and the single fix cap are fixed thresholds — do not second-guess or add cycles.
- **Never proceed without approval** on the selected task.
- **Respect dependency order.** Never start a task whose dependencies are incomplete.
- **Be explicit about failures** and propose next steps.
