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

  ┌ Agent(feature-interviewer) ─► AskUserQuestion (settle Decisions) ─┐   concurrent
  └ Agent(planner) "SCOUT ONLY" ─► context pack ────────────────────┐ │
                          SendMessage(planner, Decisions) ◄─────────┴─┘
  ┌ planner writes the plan ─────────────────────────────────┐          concurrent
  └ Agent(reviewer) "PRE-READ ONLY" (context pack) ──────────┤
              [review gate] ─► SendMessage(reviewer, plan) ◄─┘
        ▲                                             │ CHANGES_REQUESTED
        └── SendMessage(planner, reviewer) ◄──────────┘  (revise ×1, re-review)
  Agent(coding) ─► Agent(verify) ─┐
        ▲                         │ FAILED
        └── SendMessage(coding) ◄─┘  (fix ×1, re-verify failed commands first)
  mark Completed / escalate ─► report
```

### Why persistent agents
The planner, reviewer, and coding agents each run inside a loop (revise, re-review, fix). Re-spawning them fresh each cycle forces them to re-ingest the whole plan, re-read the same files, and re-derive their reasoning — the dominant token cost. Instead:

- **Spawn once, keep the handle.** Every `Agent` call returns an id/name. Record the planner's, the reviewer's (two, for high-risk parallel lenses), and the coding agent's.
- **Resume, don't respawn.** On a revision, `SendMessage` the *same* planner just the review issues — it already holds the plan, task, and context pack. On a re-review, `SendMessage` the *same* reviewer just "re-review the revised plan" — it already read the files. On a fix, `SendMessage` the *same* coding agent just the failures.
- **Verify is the exception — it stays fresh.** Spawn a new `clean-architecture:verify` agent for each verification run. It is cheap (Sonnet, low effort) and a clean re-run with no memory of the prior attempt is exactly what you want.

### Overlap the stages that don't depend on each other
The pipeline is serial by nature, but three stages were paying for work an earlier one already did. Two spawns are therefore **early and concurrent**:

- **Planner scouts during the interview.** The interviewer and the human answering `AskUserQuestion` are minutes of dead air, and the planner would otherwise start cold and re-read the same `prd.md`, `design.md`, `CLAUDE.md`, and feature-adjacent files. Spawn it *alongside* the interviewer in **scout-only** mode: it surveys and emits the context pack, then waits. When the decisions land you `SendMessage` them and it plans immediately, warm.
- **Reviewer pre-reads during planning.** A reviewer must read the referenced files rather than review from the plan text — so start that read while the plan is still being written. Spawn it in **pre-read only** mode as soon as the scout's context pack exists.
- **Coding self-checks, verify gates.** The coding agent runs a cheap targeted check on what it touched; the full concurrent gating run belongs to `verify` alone. Never ask coding to run the whole suite — that duplicates the slowest block on the path, sequentially.

The cost is that a scouted plan or a pre-read review is occasionally discarded (the gate skips review, or the decisions redirect the task). That is a token cost, not a wall-clock one — take it.

You own all of this in the main loop — there is no background workflow. Because there is no schema enforcement, **each core agent must end its reply with a single fenced ` ```json ` block** in the contract shown per stage; you parse that block to drive control flow. If a block is missing or malformed, `SendMessage` the agent once asking it to re-emit *only* the JSON block; a second failure is an `aborted` result.

### Context Pack (built once, forwarded automatically)
The planner emits a **context pack** — relevant files, key symbols, conventions, the exact verification commands, and the project's e2e command — in its JSON block, on its **scout turn**, before the plan exists. You carry it forward: paste it into the reviewer's and coding agent's *first* message, and into every `verify` spawn, so none of them cold-explores the codebase (on later `SendMessage` turns they already have it). The interview's **Decisions** arrive later and go to the planner as its second message.

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
- Do this yourself with file edits — do not delegate it. Issue **both edits in a single tool block** so they run in parallel. If the task has no ticket file, update only the roadmap.

**Stage 0.5 — Interview & Challenge (complexity-gated), with the planner scouting in parallel.** Before any planning, pressure-test the feature with the user:
- **Skip the interview** when the task is trivially unambiguous — a small, well-specified change with no product/UX/architecture forks (e.g. "fix this off-by-one", "rename this field everywhere"). Note in the report that the interview was skipped by the complexity gate. With no interview there is nothing to overlap: go straight to Stage 1 and spawn the planner in one-turn mode.
- **Otherwise interview — and spawn the scout in the same message.** Issue **both `Agent` calls in one tool block** so they run concurrently:
  - `clean-architecture:feature-interviewer` (namespaced `subagent_type`) with the task description, acceptance criteria, and roadmap context. It reads `prd.md`/`design.md`, explores the codebase, researches the topic, and returns a **Discovery Brief** with a list of **open decisions**, each with options and a recommendation.
  - `clean-architecture:implementation-planner` (opus) in **scout-only** mode — see Stage 1. It surveys the codebase and emits the context pack while the interview runs and the user answers. **Keep its id.**
- **When the brief comes back**, settle it with the user while the scout is still running or already parked:
  - **Put the decisions to the user yourself** with `AskUserQuestion` — a subagent cannot ask. Batch decisions (up to 4 per call), lead each with the interviewer's recommended option (label it "(Recommended)"), and also surface the brief's assumptions for confirmation. One call, not one per decision — every round trip is human latency on the critical path.
  - Record the answers as a **Decisions** block. Append it to the ticket file (or write `feature-brief.md` if there's no ticket), so the choices are durable.
  - If the answers materially change scope, restate the revised task before planning.
- Keep the Discovery Brief + Decisions handy — you send them to the already-running planner. If the interview was skipped, tell the planner to plan from the task description and acceptance criteria alone.

When in doubt about whether a task is trivial enough to skip, do **not** skip — run the interview.

**Stage 1 — Plan (persistent planner, spawned back in Stage 0.5).** The planner is spawned **once**, in scout-only mode, concurrently with the interviewer:

```
Agent(subagent_type: "clean-architecture:implementation-planner", model: "opus",
      prompt: task block + acceptance criteria + roadmap context
              + "SCOUT ONLY. A feature interview is running in parallel; its Decisions
                 are not settled yet, so do NOT write the plan. Survey the codebase now
                 and reply with a few lines on what you found, then end with a single
                 ```json block in this contract. Then stop and wait — I will send the
                 Decisions and ask for the plan.")
```

Required JSON contract, emitted on the scout turn and re-emitted with the plan:
```json
{
  "contextPack": {
    "relevantFiles": [{ "path": "", "role": "" }],
    "keySymbols":    [{ "symbol": "", "location": "" }],
    "conventions":   [""],
    "verificationCommands": [""],
    "e2eCommand": ""
  },
  "riskProfile": {
    "filesTouched": 0,
    "addsDependency": false,
    "addsPublicApi": false,
    "criteriaAutoCheckable": false
  }
}
```
`e2eCommand` is the project's end-to-end command, or the literal `"none"` if it has no e2e suite — the planner has already looked at the project's scripts and configs, so this costs nothing here and saves the verify agent a rediscovery on every run. On the scout turn `riskProfile` is the planner's best estimate; treat it as **provisional**.

**Then, once the Decisions are settled**, resume the same planner — do not spawn a second one:

```
SendMessage(plannerId, Discovery Brief & Decisions (or "no interview ran")
                     + "Decisions are settled — treat them as fixed constraints.
                        Write the full Implementation Plan now from the files you
                        already read; do not re-explore. End with the ```json block,
                        updating any value the decisions changed.")
```

Keep the plan markdown as `plan` and the parsed `contextPack` / `riskProfile` in hand. If the planner returns nothing at either turn → `aborted` (stage `plan`).

**Stage 2 — Review gate + review (persistent reviewer, pre-warmed, at most one revision).**

**Pre-warm first (concurrent with planning).** The moment you have sent the Decisions to the planner — i.e. *while it writes the plan* — decide from the **provisional** `riskProfile` whether a review is likely, and if so spawn the reviewer(s) in **pre-read only** mode so their file reading overlaps with the planning:

```
Agent(subagent_type: "clean-architecture:plan-reviewer", model: <see tiering>,
      prompt: task block + acceptance criteria + Decisions + the context pack
              + "PRE-READ ONLY. The plan is still being written. Read every file in the
                 context pack now and reply with a few lines on what you read and any
                 hazard you already see. Do NOT issue a verdict yet.")
```
Skip the pre-warm only when the provisional profile clears the skip gate outright. If the real gate later skips the review, simply drop the pre-warmed reviewer — a discarded pre-read costs tokens, never wall-clock.

**Then apply the gate mechanically** on the *final* `riskProfile` that came back with the plan — do not use judgment here:

- **Skip review** iff `filesTouched ≤ 2` **and** `addsDependency == false` **and** `addsPublicApi == false` **and** `criteriaAutoCheckable == true`. Log "Review gate: SKIPPED" and go to Stage 3 with the plan as approved.
- Otherwise **review is required**. It is **high-risk** iff `addsPublicApi == true` **or** `addsDependency == true` **or** `filesTouched > 5`.
  - **Normal risk:** **one** reviewer, spawned with `model: "sonnet"` — reviewing a plan against files it has already read is checklist work, and the faster model is the right trade here.
  - **High risk:** **two** reviewers, spawned **in one tool block** (concurrent) with `model: "opus"`, each with the same base but a distinct lens: (a) *correctness/completeness* — will the plan satisfy every acceptance criterion; missing steps, wrong assumptions, edge cases, ordering hazards; (b) *codebase fit* — conventions, dependency rules, architectural boundaries, unjustified new API/deps. Keep **both** ids.
  - If the pre-warm guessed the wrong tier (provisional profile said normal, final says high-risk), keep the pre-warmed reviewer as lens (a) and spawn the second one now.

**Hand over the plan** with `SendMessage(reviewerId, "Review the plan below against the checklist. You have already read the context pack files; re-read only what the plan points at that you have not seen. <plan>")` — to both reviewers **in a single tool block** when there are two. If a reviewer was never pre-warmed, its first message is the full one: task block + Decisions + plan + context pack + "Read the referenced files — do not review from the plan text alone."

Every reviewer must end with:
```json
{ "verdict": "APPROVED" | "CHANGES_REQUESTED", "summary": "",
  "issues": [{ "title": "", "severity": "critical|major|minor", "steps": "", "problem": "", "suggestion": "" }] }
```
Merge multiple reviewers: verdict is `CHANGES_REQUESTED` if **any** reviewer requests changes; concat their issues. If every reviewer returned nothing → `aborted` (stage `review`).

**Revision loop — at most ONE cycle:**
- If verdict is `APPROVED` → proceed to Stage 3.
- If `CHANGES_REQUESTED` and you have **not yet revised**: `SendMessage(plannerId, "Revise your plan to resolve every issue below. Note in the Context section how each was addressed. Re-emit the full plan markdown + the ```json block." + issues)`. The planner already holds the plan/task/pack — **send only the issues**. Then re-review by **`SendMessage`-ing the same reviewer(s)**: `"Re-review the revised plan below; the files are unchanged. <revised plan>"` — both in **one tool block** when there are two, so the re-reviews run concurrently. Loop back to check the new verdict.
- If `CHANGES_REQUESTED` and you have **already revised once** → **`escalate`** (stage `review`): surface the reviewer summary + remaining issues, leave status `In Progress`, stop.

**Stage 3 — Implement (persistent coding agent).** Spawn coding **once** and keep its id:

```
Agent(subagent_type: "clean-architecture:coding", model: "opus",
      prompt: "Implement the approved plan exactly — no scope creep. Match the context pack conventions.
               Targeted self-check only when you are done; the verify stage runs the full gate."
              + approved plan + context pack + acceptance criteria + the JSON contract)
```
Its skill obligations (`clean-fullstack-architecture` before any production code, `ts-clean` for any `.ts`/`.tsx` file, `react-clean` for any React file) already live in the agent definition — do not restate them here; text in the agent file is free, text in this prompt is paid on every spawn.
Coding must end with:
```json
{ "summary": "", "stepsCompleted": [""], "filesChanged": { "created": [""], "modified": [""] }, "blockers": [""] }
```
If it returns nothing → `aborted` (stage `implement`). If `blockers` is non-empty → `escalate` (stage `implement`) with the blockers.

**Stage 4 — Verify (fresh agent) + fix (persistent coding, at most ONE fix cycle).** Spawn a **new** `clean-architecture:verify` agent (sonnet, low effort) each run:

```
Agent(subagent_type: "clean-architecture:verify", model: "sonnet",
      prompt: "Run these verification commands CONCURRENTLY (one parallel Bash batch). Report pass/fail per command."
              + verificationCommands and e2eCommand from the context pack + the Decisions
              + (re-runs only) "Previously failing commands: <failures> — run these first and fail fast.")
```
Pass `e2eCommand` **every time**, including the literal `"none"` — that is what lets the agent skip its e2e discovery sweep instead of globbing for `playwright.config.*`/`cypress/`/`e2e/` on each spawn. The judging rules (baseline-aware pass/fail, environment blockers are `skipped` not failures, ~3-line output cap), the fail-fast re-run behaviour, and the JSON contract all live in the agent definition — do not restate them in the prompt.

Contract it returns:
```json
{ "passed": true, "results": [{ "command": "", "passed": true, "skipped": false, "output": "" }], "failures": [""] }
```
- If it returns nothing → `aborted` (stage `verify`).
- If `passed == true` → success, go to Stage 3-of-§3 (mark Completed). If any result is `skipped`, still succeed, but name the skipped command and its reason in the completion report — never present a skipped e2e run as a green one.
- If `passed == false` and you have **not yet fixed**: `SendMessage(codingId, "Verification failed. Fix ONLY what's needed to make the checks pass — stay within the approved plan, then stop; verification will re-run." + failures)` — the coding agent already holds the plan/pack, **send only the failures**. Then spawn a **fresh** verify agent and re-check, passing it the **previously failing commands** so it runs those first and bails out early if the fix did not land.
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
- **Spawn early, overlap the waiting.** The planner scouts concurrently with the interview and the user's answers; the reviewer pre-reads concurrently with the planning. Both are the same persistent agents, just started sooner — never spawn a *second* planner or reviewer for the real turn. Concurrent calls go in **one tool block** or they are not concurrent.
- **Never duplicate the gating run.** Coding does a targeted self-check; `verify` runs the full suite, concurrently, once per cycle. On a re-verify, hand over the previously failing commands so it fails fast instead of re-running everything.
- **Keep prompts thin.** Anything durable about how an agent behaves belongs in its agent definition, not in the spawn prompt — the prompt is re-paid on every spawn.
- **Mark status yourself, at both boundaries.** Set the ticket **and** roadmap to `In Progress` before spawning any agent, and to `Completed` in both places only on success. Keep the ticket and roadmap in sync.
- **Interview before planning.** For any non-trivial feature, run `clean-architecture:feature-interviewer` and settle its open decisions with the user *before* spawning the planner — planning on unchallenged assumptions is the failure this prevents. Skip only via the complexity gate; when in doubt, run it.
- **Build the context pack once, forward it.** The planner emits it; you paste it into the reviewer's and coding agent's first message so none of them cold-explores the codebase.
- **Apply the gates mechanically.** The review-skip gate (≤2 files, no dep, no API, criteria auto-checkable), the high-risk test (new API/dep or >5 files), the single revision cap, and the single fix cap are fixed thresholds — do not second-guess or add cycles.
- **Never proceed without approval** on the selected task.
- **Respect dependency order.** Never start a task whose dependencies are incomplete.
- **Be explicit about failures** and propose next steps.
