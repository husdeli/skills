---
description: Pick the next actionable roadmap task and drive it through plan → review → implement → verify + code review using persistent subagents.
argument-hint: [roadmap-file-path]
---

# Roadmap Orchestrator

You are a workflow orchestrator. Pick the **next actionable item** from a roadmap and drive it to completion. You do NOT drive the whole roadmap — one task at a time, then stop.

Roadmap file (if provided): $ARGUMENTS

## The rules live in four skills — load each one before the stage that needs it

| Skill | What it holds | Load before |
| --- | --- | --- |
| **`sdlc-structure`** | Where the project and the work root are, and how each destination writes a document | you read any document |
| **`ticket-board`** | The ticket, the roadmap, the assignee, the worklog, and what each status transition writes | Stage 0 |
| **`agent-pipeline`** | Spawn once and resume, concurrent calls, the JSON block, the outcome vocabulary | Stage 0.5 |
| **`technical-writing`** | Every word the user reads | Stage 1 |

Each name may be namespaced here — `sdlc:sdlc-structure`, `sdlc:ticket-board`,
`sdlc:agent-pipeline`, `sdlc:technical-writing`. Invoke the namespaced form when it is there, load each
skill **once**, and follow it. Do not work from memory, and do not restate a skill's rules in a
spawn prompt: the agents load their own.

**The documents sit in the project** — `prd.md`, `glossary.md`,
`features/<feature>/`, `designs/<subject>.design.md`, `roadmap.md`, and
`tickets/<status>/<ID>-*.md`, with a worklog
beside a ticket in flight. `sdlc-structure` resolves the
project, and every `.sdlc/…` path below means `<project>/…`. When there is no project yet, work
from whatever sits at the repository root and name `/setup` in your report.

## The code sits in the work root, which is not always where you are standing

**The work root is the repository this task is built in.** In a session started inside a repository
it is that repository, and nothing below changes. In a session started in the vault — the
recommended shape, where one board drives several repositories — the working directory is the docs
root and the code is somewhere else.

`sdlc-structure` holds the whole rule; what this command owns is *when*:

- **Resolve the work root in Stage 0**, after the task is approved and before the ticket is
  started. The ticket never names a repository, so the resolution reads the feature, the design doc, the ticket,
  the epic, and the registry's `what` lines. When it stays open, ask the user with
  `AskUserQuestion` — that question belongs to you, not to an agent.
- **Write it into the opening worklog entry** — the code, the absolute path, and the evidence.
- **Put it in every agent prompt as an absolute path**, and tell the planner to carry it in the
  context pack as `workRoot`, so the reviewer, the coding agent, the verifier, and the code
  reviewer all read the same value.
- **Check the session can write there** before Stage 0.5. When it cannot, stop and say which
  command fixes it: `/add-dir <work root>`, or a restart as `claude --add-dir <work root>`. That
  is a setup problem, and no agent can solve it.
- **A task that spans two repositories** runs the implementation, the verification, the code
  review, and the commit once per work root, and passes only when every one of them passes.

## The worklog and the assignee — you are the only writer

The **`ticket-board`** skill holds the worklog's shape, what belongs in an entry, and what each
assignee value means. What is specific to this pipeline:

**You are the only writer.** Each agent reports its decisions to you and you write them down, so
the file has one writer and the two concurrent stages — the interview beside the scout,
verification beside the code review — cannot lose each other's entry. No agent writes either field.

**The entry and the assignee go in one tool block**, at five boundaries:

| Boundary | Entries to append | Assignee becomes |
| --- | --- | --- |
| Stage 0, starting the ticket | the worklog itself, with the `orchestrate · start` entry | `feature-interviewer, implementation-planner` — the agents you are about to spawn, or `implementation-planner` alone when the interview is skipped |
| Stage 0.5, the decisions land | `feature-interviewer · interview` | `implementation-planner` |
| Stage 2, the review gate closes | `implementation-planner · plan`, then `plan-reviewer … · plan review` | `coding` |
| Stage 3, the implementation lands | `coding · implement` | `verify, code-reviewer` |
| Stage 4, the gate closes | `verify · verification`, `code-reviewer · code review`, then the outcome | `—` on completion, `user` on escalate or abort |

**With no ticket file**, the worklog is `.sdlc/tickets/in-progress/<slug>.worklog.md`, beside the
brief; when there is neither, there is nothing to write and you say so in the report.

**Every exit writes the outcome entry and the assignee** — an escalation or an abort at any stage
runs `ticket-board`'s *Stopping without finishing* transition, so the next session can read the
worklog and learn where the task stopped.

## Architecture: interactive shell + persistent-agent core

This command runs entirely **in the main loop, with you**. The human-facing stages — picking the task, getting approval, settling open decisions, writing the status — need you because only you can talk to the user. The mechanical core — plan → review → revise → implement → verify and review the code — you drive with **persistent subagents**, on the mechanics `agent-pipeline` holds.

```
  YOU (main loop)
  ─────────────────────────
  list candidates ─► AskUserQuestion (which task + e2e?) ─► work root ─► start the ticket ─►

  ┌ Agent(feature-interviewer) ─► AskUserQuestion (settle Decisions) ─┐   concurrent
  └ Agent(planner) "SCOUT ONLY" ─► context pack ────────────────────┐ │
                          SendMessage(planner, Decisions) ◄─────────┴─┘
  ┌ planner writes the plan ─────────────────────────────────┐          concurrent
  └ Agent(reviewer) "PRE-READ ONLY" (context pack) ──────────┤
              [review gate] ─► SendMessage(reviewer, plan) ◄─┘
        ▲                                             │ CHANGES_REQUESTED
        └── SendMessage(planner, reviewer) ◄──────────┘  (revise ×1, re-review)
  Agent(coding) ─► ┌ Agent(verify) ──────────────┐  concurrent
                   └ Agent(code-reviewer) ───────┤
        ▲                                        │ FAILED or CHANGES_REQUESTED
        └── SendMessage(coding) ◄────────────────┘  (fix ×1, re-verify + re-review)
  finish the ticket / escalate ─► report
```

### Which agents are persistent here
The **`agent-pipeline`** skill holds the mechanics — spawn once, resume with `SendMessage`, a fresh
verify per run, concurrent calls in one tool block, the JSON block and its single retry, and the
`completed` / `escalate` / `aborted` vocabulary. This command's four persistent roles are the
**planner**, the **plan reviewer** (two ids on a high-risk plan, one per lens), the **coding
agent**, and the **code reviewer**. Record every id the `Agent` call returns.

### Overlap the stages that don't depend on each other
Two spawns go out **early and concurrent**, so they run inside otherwise dead air:

- **Planner scouts during the interview.** The interviewer and the user answering `AskUserQuestion` are minutes of waiting, and the planner would otherwise start cold on the same product docs, project instructions, and feature-adjacent files. In **scout-only** mode it surveys the codebase, researches the best practice, emits the context pack, then waits — its web round-trips cost no wall-clock here. When the decisions land, `SendMessage` them and it plans warm.
- **Reviewer pre-reads during planning.** A reviewer must read the referenced files rather than review from the plan text, so start that read while the plan is still being written — **pre-read only** mode, spawned as soon as the scout's context pack exists.
- **Coding self-checks, verify gates.** Coding runs a cheap targeted check on what it touched; the full concurrent gating run belongs to `verify` alone. Never ask coding to run the whole suite — that duplicates the slowest block on the path, sequentially.
- **Verify and the code review run side by side.** They answer different questions about the same finished change — "does it pass?" and "is it the right code, and all of it?" — and neither needs the other's answer. The e2e suite is usually the longest block in the task, so the review costs no wall-clock at all. Do not start the code reviewer earlier, during implementation: the files are mid-flight then, and a review of half-written code is noise.

A scouted plan or pre-read review is occasionally discarded (the gate skips review, or the decisions redirect the task). That is a token cost, not a wall-clock one — take it.

### Context Pack (built once, forwarded automatically)
The planner emits a **context pack** — the work root, relevant files, key symbols, conventions, the exact verification commands, and the project's e2e command — in its JSON block on the **scout turn**, before the plan exists. Paste it into the plan reviewer's, the coding agent's, and the code reviewer's *first* message and into every `verify` spawn, so none of them cold-explores the codebase (later `SendMessage` turns already have it). The interview's **Decisions** arrive later, as the planner's second message.

## Everything you show the user goes through `technical-writing`

You are the only stage that talks to the person, so `technical-writing` governs every word they see: the task you present for approval, every `AskUserQuestion` question and option label, the Decisions you record, the completion report, and every escalation or abort.

The agents apply it to their own output, but you are what the user actually reads — a brief that landed cleanly still fails the user if you relay it badly. The rules that bite hardest here: name the task and the stake before the detail, give the verdict before the evidence, keep an option label to one short phrase, and reuse the roadmap's and the PRD's own words for every domain term. It governs prose only — IDs, file paths, commands, status markers, and the agents' `json` blocks stay exact. They stay exact **beside** the prose: a path, a symbol, or a snippet never goes inside a sentence, and the sentence names the thing in words instead.

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
Collect **every** task that is **pending** and whose **dependencies are all satisfied** — those are the candidates. `ticket-board` says when a `Depends on` cell counts as satisfied. When the roadmap holds no pending task at all, say so and name `/plan` as the way to add one — do not invent a task.

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

**The answer to question 1 is the approval.** Do not start Stage 0 before it lands. "Cancel", or an "Other" answer that names no task on the roadmap, ends the run — say so and stop.

**Carry the e2e answer forward as the `e2eDecision`.** It is settled here, before any agent is spawned, so it must reach the stages that act on it:
- Write it into the **Decisions** block in Stage 0.5, next to the interview's decisions. When the interview is skipped, write the Decisions block anyway, holding this one decision.
- Put one line in the **Stage 1 scout prompt** — `"E2E: yes, critical path only"` or `"E2E: no — unit and integration only"` — so the plan's test section matches the answer instead of the planner guessing.
- A **yes** on a project with no e2e suite means the plan has to stand one up. Say that in the scout prompt too; `e2eCommand` comes back `"none"` from the context pack in exactly that case.

### 3. Drive the Task to Completion
Track stages with the task/todo tools so the user sees live progress.

**Stage 0 — Resolve the work root, then start the ticket (before spawning any agent).** As soon as the task is approved and *before* launching `feature-interviewer`, resolve the work root as `sdlc-structure` says, then run the **`ticket-board`** skill's **Starting a ticket** transition — status, assignee, the move into `in-progress/`, the new worklog, and the roadmap row, all in one tool block. Do it yourself with file edits; do not delegate it. Three values are this command's:
- The **work root**, resolved before the transition is written, and checked to be writable from this session.
- The **assignee** is the agents you are about to spawn: `feature-interviewer, implementation-planner`, or `implementation-planner` alone when the interview is skipped.
- The **opening worklog entry** is `orchestrate · start`: the task you are building, what it delivers, the work root and the evidence that settled it, and the `e2eDecision`.

**Stage 0.5 — Interview & Challenge (complexity-gated), with the planner scouting in parallel.**
- **Skip the interview** when the task is trivially unambiguous — a small, well-specified change with no product/UX/architecture forks ("fix this off-by-one", "rename this field everywhere"). Note the skip in the report. Nothing to overlap: go to Stage 1 and spawn the planner in one-turn mode. Still record the **Decisions** block holding the `e2eDecision` from Step 2.
- **Otherwise interview — and spawn the scout in the same message.** Issue **both `Agent` calls in one tool block** so they run concurrently:
  - `sdlc:feature-interviewer` (namespaced `subagent_type`) with the task description, acceptance criteria, and roadmap context. It reads `.sdlc/prd.md`, the feature note the task's epic code names, and the design docs the task touches, explores the codebase, researches the topic, and returns a **Discovery Brief** with **open decisions**, each with options and a recommendation.
  - `sdlc:implementation-planner` (opus) in **scout-only** mode — see Stage 1. **Keep its id.**
- **When the brief comes back**, settle it with the user while the scout runs or is parked:
  - **Put the decisions to the user yourself** with `AskUserQuestion` — a subagent cannot ask. Batch them (up to 4 per call), lead each with the interviewer's recommended option (labelled "(Recommended)"), and surface the brief's assumptions for confirmation. One call, not one per decision — every round trip is human latency on the critical path.
  - Record the answers as a **Decisions** block appended to the ticket file (or `.sdlc/tickets/in-progress/<slug>-brief.md` if there's no ticket), so the choices are durable. A brief lives beside the ticket it serves, and moves with it. Record the Step 2 `e2eDecision` in the same block — it is a decision the user made, and the coding and verify stages read it there.
  - In the **same tool block**: append the `feature-interviewer · interview` worklog entry — what the brief challenged and where the Decisions now live, not a copy of them — and set the assignee to `implementation-planner`. When the interview was skipped, one line saying the complexity gate skipped it is the whole entry.
  - If the answers materially change scope, restate the revised task before planning.
- Keep the Discovery Brief + Decisions handy for the already-running planner. If the interview was skipped, tell the planner to plan from the task description and acceptance criteria alone.

When in doubt whether a task is trivial enough to skip, do **not** skip — run the interview.

**Stage 1 — Plan (persistent planner, spawned back in Stage 0.5).** Spawned **once**, in scout-only mode, concurrently with the interviewer:

```
Agent(subagent_type: "sdlc:implementation-planner", model: "opus",
      prompt: task block + acceptance criteria + roadmap context + the e2eDecision line
              + the work root as an absolute path
              + "SCOUT ONLY. A feature interview is running in parallel; its Decisions
                 are not settled yet, so do NOT write the plan. Survey the codebase and
                 research the current best practice for this work now, reply with a few
                 lines on what you found, then end with your ```json block. Then stop and
                 wait — I will send the Decisions and ask for the plan.")
```

It returns `contextPack` (the `workRoot`, relevant files, key symbols, conventions, `verificationCommands`, `e2eCommand`) and `riskProfile` (`filesTouched`, `addsDependency`, `addsPublicApi`, `criteriaAutoCheckable`) in one fenced `json` block. The shape lives in the agent definition — do not restate it in the prompt. On the scout turn, treat `riskProfile` as **provisional**.

**Once the Decisions are settled**, resume the same planner — do not spawn a second one:

```
SendMessage(plannerId, Discovery Brief & Decisions (or "no interview ran")
                     + "Decisions are settled — treat them as fixed constraints.
                        Write the full Implementation Plan now from the files and
                        research you already have; explore or search again only where
                        a decision opened something you did not cover. Re-emit your
                        ```json block, updating any value the decisions changed.")
```

Keep the plan markdown as `plan` and the parsed `contextPack` / `riskProfile` in hand. If the planner returns nothing at either turn → `aborted` (stage `plan`).

**Stage 2 — Review gate + review (persistent reviewer, pre-warmed, at most one revision).**

**Pre-warm first (concurrent with planning).** The moment the Decisions are sent — *while the plan is being written* — judge from the **provisional** `riskProfile` whether a review is likely, and if so spawn the reviewer(s) in **pre-read only** mode:

```
Agent(subagent_type: "sdlc:plan-reviewer", model: <see tiering>,
      prompt: task block + acceptance criteria + Decisions + the context pack
              + "PRE-READ ONLY. The plan is still being written. Read every file in the
                 context pack now and reply with a few lines on what you read and any
                 hazard you already see. Do NOT issue a verdict yet.")
```
Skip the pre-warm only when the provisional profile clears the skip gate outright. If the real gate later skips the review, drop the pre-warmed reviewer — a discarded pre-read costs tokens, never wall-clock.

**Then apply the gate mechanically** on the *final* `riskProfile` that came back with the plan — no judgment here:

- **Skip review** iff `filesTouched ≤ 2` **and** `addsDependency == false` **and** `addsPublicApi == false` **and** `criteriaAutoCheckable == true`. Log "Review gate: SKIPPED" and go to Stage 3 with the plan as approved.
- Otherwise **review is required**. It is **high-risk** iff `addsPublicApi == true` **or** `addsDependency == true` **or** `filesTouched > 5`.
  - **Normal risk:** **one** reviewer, `model: "sonnet"` — reviewing a plan against files it has already read is checklist work.
  - **High risk:** **two** reviewers, spawned **in one tool block** with `model: "opus"`, same base but distinct lenses: (a) *correctness/completeness* — will the plan satisfy every acceptance criterion; missing work items, wrong assumptions, edge cases, ordering hazards; (b) *codebase fit* — conventions, dependency rules, architectural boundaries, unjustified new API/deps. Keep **both** ids.
  - If the pre-warm guessed the wrong tier (provisional said normal, final says high-risk), keep the pre-warmed reviewer as lens (a) and spawn the second now.

**Hand over the plan** with `SendMessage(reviewerId, "Review the plan below against the checklist. You have already read the context pack files; re-read only what the plan points at that you have not seen. <plan>")` — both reviewers in **one tool block** when there are two. A reviewer that was never pre-warmed gets the full first message: task block + Decisions + plan + context pack + "Read the referenced files — do not review from the plan text alone."

Every reviewer ends its review turn with a `json` block carrying `verdict` (`APPROVED` | `CHANGES_REQUESTED`), `summary`, and `issues` — shape in the agent definition, do not restate it. Merge multiple reviewers: `CHANGES_REQUESTED` if **any** reviewer requests changes; concat their issues. If every reviewer returned nothing → `aborted` (stage `review`).

**Revision loop — at most ONE cycle:**
- `APPROVED` → append the plan and plan-review worklog entries and set the assignee to `coding`, in one tool block, then Stage 3. The plan entry carries the **direction** the plan settled on and the approach it turned down — the plan markdown itself is not persisted anywhere, so this is the only trace it leaves. The review entry carries the verdict, the issues that forced the revision, and how the revision answered them. A review the gate skipped is one line naming the gate.
- `CHANGES_REQUESTED`, **not yet revised**: `SendMessage(plannerId, "Revise your plan to resolve every issue below. Note in the Context section how each was addressed. Re-emit the full plan markdown + the ```json block." + issues)` — the planner holds the plan/task/pack, so **send only the issues**. Then re-review via `SendMessage` to the same reviewer(s): `"Re-review the revised plan below; the files are unchanged. <revised plan>"` — both in **one tool block** when there are two. Loop back to the new verdict.
- `CHANGES_REQUESTED`, **already revised once** → **`escalate`** (stage `review`): surface the reviewer summary + remaining issues, leave status `In Progress`, stop.

**Stage 3 — Implement (persistent coding agent).** Spawn **once** and keep its id:

```
Agent(subagent_type: "sdlc:coding", model: "opus",
      prompt: "Implement the approved plan exactly — no scope creep. Match the context pack conventions.
               Targeted self-check only when you are done; the verify stage runs the full gate."
              + approved plan + context pack + acceptance criteria)
```
Its skill obligations and JSON contract live in the agent definition — do not restate them here; text in the agent file is free, text in this prompt is paid on every spawn.

It ends every turn with a `json` block carrying `summary`, `workItemsCompleted`, `filesChanged`, `decisions`, and `blockers`. Nothing returned → `aborted` (stage `implement`). Non-empty `blockers` → `escalate` (stage `implement`) with them.

When it lands, append the `coding · implement` entry — its `decisions`, which are the code-level calls the plan left open — and set the assignee to `verify, code-reviewer`, in one tool block before you spawn them.

**Stage 4 — Verify and review the code (concurrent) + fix (persistent coding, at most ONE fix cycle).** Issue **both `Agent` calls in one tool block**. Verify is spawned **fresh every run**; the code reviewer is spawned **once** and resumed.

```
Agent(subagent_type: "sdlc:verify", model: "sonnet",
      prompt: "Run these verification commands CONCURRENTLY (one parallel Bash batch). Report pass/fail per command."
              + verificationCommands and e2eCommand from the context pack + the Decisions
              + (re-runs only) "Previously failing commands: <failures> — run these first and fail fast.")

Agent(subagent_type: "sdlc:code-reviewer", model: <opus on high risk, else sonnet>,
      prompt: "Review the change the coding agent just made, against the approved plan and the
               acceptance criteria. Verification is running in parallel — do not run the suite."
              + approved plan + acceptance criteria + Decisions + context pack
              + the coding agent's filesChanged + the review target ("the uncommitted changes
                against HEAD, untracked files included"))
```
Pass `e2eCommand` **every time**, including the literal `"none"` — that is what lets the verify agent skip its e2e discovery sweep instead of globbing for `playwright.config.*`/`cypress/`/`e2e/` on each spawn. The judging rules, the fail-fast re-run behaviour, the review checklist, the severity rules, and both JSON contracts live in the agent definitions — do not restate them.

**Model tier for the reviewer:** the same high-risk test as Stage 2 — **opus** when `addsPublicApi == true` **or** `addsDependency == true` **or** `filesTouched > 5`, **sonnet** otherwise. Unlike the plan review, the code review has **no skip gate**. It is the last thing between a change and a task marked complete, and a passing suite says nothing about a missed acceptance criterion or a broken layer boundary.

Verify ends with a `json` block carrying `passed`, per-command `results` (`passed`, `skipped`, `output`), and `failures`. The reviewer ends with a `json` block carrying `verdict` (`APPROVED` | `CHANGES_REQUESTED`), `summary`, and `issues`. **Combine them into one gate:**

- Either agent returned nothing → `aborted` (stage `verify` or `code-review`).
- `passed == true` **and** `verdict == APPROVED` → success, go to **Finishing a ticket**. If any result is `skipped`, still succeed, but name the skipped command and its reason in the report — never present a skipped e2e run as green. Carry any minor review issues into the report as recommendations; they do not block.
- Anything else, **not yet fixed**: send **one** message carrying both sets of defects — `SendMessage(codingId, "Verification and code review found the following. Fix ONLY what is needed to clear them — stay within the approved plan, then stop; both will re-run." + failures + blocking review issues)`. The coding agent holds the plan and the pack, so **send only the defects**. Then re-run: **always** a **fresh** verify agent — the fix changed code, so a suite that was green before proves nothing now — carrying the **previously failing commands** so it runs those first and bails early. Re-review **only when the review blocked**, with `SendMessage(codeReviewerId, "Re-review the fix below; judge each prior issue as fixed or still open." + the coding agent's summary)`; a fix confined to the failures the reviewer already approved around does not re-open the review. When both run, issue them **in one tool block**.
- Anything else, **already fixed once** → **`escalate`** with the remaining failures and issues, leave status `In Progress`, stop. Name the stage `verify` when commands still fail, `code-review` when only the review still blocks.

**Act on the result.** Whichever it is, the verification and code-review entries go into the worklog — a run that failed is exactly the run whose record matters. `agent-pipeline` defines the three outcomes and `ticket-board` holds the transition each one writes:
- **`completed`** → run **Finishing a ticket**. Keep `reviewRan`, `interviewRan`, both reviewer summaries, and the implementation/verification details for the report. The closing entry is `orchestrate · done`, and a correction this run forced on a *remaining* task — a decision the interview settled, a constraint the code review found, a dependency that turned out wrong — is rewritten in the same edit.
- **`escalate`** → run **Stopping without finishing**. Surface the `stage`, `reason`, and any `issues`/`failures`/`blockers` for the user.
- **`aborted`** → run **Stopping without finishing**, with the outcome entry naming the stage and the agent that went silent.

Report only after the files are updated.

### 4. Completion Report
```markdown
## Task Complete: [ID] — [Title]

- [x] Interview — decisions recorded (or: skipped by complexity gate — trivial task)
- [x] Planning — approved
- [x] Review — approved (or: skipped by complexity gate — trivial task)
- [x] Implementation — verified (tests, lint, typecheck run concurrently)
- [x] Code review — approved ([N] revisions)
- [x] Status — ticket marked Completed, unassigned, and moved to `done/` with its worklog; roadmap row deleted

Work root: `[code]` — `[absolute path]`

[Summary of what was accomplished]
```

## Failure Handling
`agent-pipeline` holds the outcome vocabulary and `ticket-board` the **Stopping without finishing** transition. This command's caps are the ones to apply mechanically, with no improvised extra cycle:
- **`escalate`** when a stage hits its limit — the plan still rejected after 1 revision, a coding blocker, or verification or the code review still failing after 1 fix cycle.
- **`aborted`** when an agent returns no usable result, at any stage.
- Never mark a task complete unless verification passed **and** the code review approved.

## Rules
The four skills carry the rules they own — `agent-pipeline` for the spawn-once, one-tool-block, thin-prompt and no-duplicate-gate mechanics, `ticket-board` for the transitions and the roadmap, `sdlc-structure` for the paths, `technical-writing` for the prose. What is this command's own:
- **One task at a time.** Do not execute the whole roadmap.
- **Resolve the work root before the ticket starts**, record it in the worklog, and pass it to every agent. Never let an agent infer which repository it is working in.
- **Load every skill in the table before the stage that needs it.** They are the rules; this file is the sequence.
- **The code review always runs.** Verify and the code reviewer go out in one tool block, and the task passes only when the commands pass *and* the verdict is `APPROVED`. Only the plan review has a skip gate.
- **Interview before planning** for any non-trivial feature; skip only via the complexity gate.
- **Apply the gates mechanically.** The review-skip gate (≤2 files, no dep, no API, criteria auto-checkable), the high-risk test (new API/dep or >5 files), the single revision cap, and the single fix cap are fixed thresholds.
- **You write the status, the assignee, and the worklog** — at the five boundaries and at every exit. No agent writes any of them.
- **Never proceed without approval** on the selected task, and never start a task whose dependencies are incomplete.
- **Be explicit about failures** and propose next steps.
