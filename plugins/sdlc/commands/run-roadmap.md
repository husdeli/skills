---
description: Build the next ticket of a roadmap run with no person in the loop — the run works one feature at a time, the cto agent answers every question, the feature's dependency cluster is claimed, the code is committed on the run branch in a run worktree, and the session reports a machine-readable result for the launcher script.
argument-hint: [--run run-roadmap-<n>] [--final] [roadmap-file-path]
---

# Autonomous Roadmap Runner

You drive **one** ticket of a **roadmap run** from selected to committed, and **you never ask the
user anything**. A roadmap run works **one feature at a time**: it selects a feature, claims every
ticket that feature still needs, and builds them one per session until the feature is done — then it
selects the next feature. Every question an interactive pipeline would put to a person goes to the **`cto`**
agent instead. When the ticket is done you commit it, print a result line, and stop.

Arguments: $ARGUMENTS

- **`--run run-roadmap-<n>`** — the roadmap run this session belongs to. The launcher passes it on
  every session after the first, and on a resume. Without it you start a new roadmap run: `<n>` is
  the lowest positive number that no `claimed` value in `work/` and no `run-roadmap-<n>` branch in a
  registered repository uses.
- **`--final`** — this is the run's last ticket: whatever the outcome, release the run's claims
  before the result line. The launcher passes it when `--max` is about to be reached. A session
  started by hand, with no `--run`, is final too.
- **A roadmap file path**, when given, is the roadmap to read.

This is `/orchestrate` with the human replaced. The stages, the gates, and the caps are the same;
what changes is who answers, what is claimed, where the code is built, what happens at a cap, and
that the session ends in commits and a parsable result. One invocation is one ticket of the
feature the run holds — the loop over the feature's tickets and over the roadmap belongs to [`scripts/run-roadmap.sh`](../scripts/run-roadmap.sh), which starts a
fresh session per ticket so a long roadmap never runs out of context. The design is
`designs/workflow.design.md`, sections 3 and 6.1, and `diagrams/run-roadmap.excalidraw.md` draws it.

**Nobody is watching this run.** That is the one fact that shapes every rule below: no
`AskUserQuestion`, a hard cap on every cycle, a commit per ticket on a branch of its own so
`git log` is the audit trail, and a hand-back that ends the run whenever the decision belongs to a
person.

## The rules live in four skills — load each one before the stage that needs it

| Skill | What it holds | Load before |
| --- | --- | --- |
| **`sdlc-structure`** | Where the project and the work root are, and how each destination writes a document | you read any document |
| **`ticket-board`** | The ticket, the roadmap, the assignee, the worklog, and what each status transition writes | Stage 1 |
| **`agent-pipeline`** | Spawn once and resume, concurrent calls, the JSON block, the outcome vocabulary | Stage 2 |
| **`technical-writing`** | Every word a person reads later — the worklog, the commit message, the report | Stage 2 |

Each name may be namespaced here — `sdlc:sdlc-structure`, `sdlc:ticket-board`,
`sdlc:agent-pipeline`, `sdlc:technical-writing`. Invoke the namespaced form when it is there, load each
skill **once**, and follow it. Do not work from memory, and do not restate a skill's rules in a
spawn prompt: the agents load their own.

**The documents sit in the framework root** — the glossary, the features and their design docs,
each project's `roadmap.md`, and the tickets in `work/<bucket>/`, with a worklog beside a ticket in
flight. `sdlc-structure` resolves the framework root and the project; `ticket-board` holds the
buckets.

**The code sits in a run worktree** — never in the person's checkout. A roadmap run owns one branch,
`run-roadmap-<n>`, and one git worktree of each work root it changes, at
`<parent of the repository>/<repository name>-worktrees/run-roadmap-<n>`. Stage 1.5 creates them
once and every later ticket of the run reuses them. What follows from that:

- **The person's checkout is never touched**, and an uncommitted change in it is not part of the run:
  the worktree starts from the checkout's current commit.
- **Every git call names the worktree**: `git -C <worktree> …`. Every build, test, and package
  manager command runs as `cd <worktree> && …`. A bare `npm test` runs in the vault and proves
  nothing.
- **Every agent prompt carries the worktree as an absolute path, as the work root**, and the planner
  carries it in the context pack as `workRoot`. No agent is told about the person's checkout.
- **The code commit belongs to the run branch; the documents commit belongs to the framework root**,
  when the framework root is a git tree. Stage 9 holds both.

## The one rule that makes this command different

**Never call `AskUserQuestion`. Not once, at any stage, for any reason.** There is no person on the
other end of this session, so a question is a hang, and a hang inside an unattended loop burns the
whole run.

Every question goes to the `cto` agent, which answers in the user's place:

| What `/orchestrate` asks the user | Who answers here |
| --- | --- |
| Which candidate ticket to build — or that it cannot run | `cto`, request `feature-selection`, which picks a feature instead |
| Whether the ticket gets end-to-end tests | `cto`, in the same `feature-selection` answer, once for the feature |
| A fork the ticket's documents leave open, which the planner names | `cto`, request `decisions`, in one round |
| Nothing — it stops and escalates | `cto`, request `escalation` |

When the CTO sets `handBack: true`, **that** is the moment a person is needed. Stop, run
`ticket-board`'s *Stopping without finishing* transition once a ticket has started, and report the
outcome `handed-back`. Do
not try to answer a handed-back question yourself.

## Architecture: the interactive shell, driven by an agent

```
  YOU (main loop)
  ─────────────────────────
  preflight ─► select: a feature this run claims, else the candidate features ─► Agent(cto) pick + e2e
  ─► claim the feature's dependency cluster ─► read back  (lost ─► select again, 3× ─► blocked)
  ─► choose the feature's next ticket ─► identify the work roots ─► run worktree per work root (once per run) ─► start the ticket ─►

  ┌ Agent(planner) ─► contextPack + plan + riskProfile, or openQuestions ─┐  concurrent
  └ Agent(test-planner) "SPEC ONLY" ─► draft cases ───────────────────────┤
        [openQuestions] SendMessage(cto, decisions) + Agent(plan-reviewer) "PRE-READ ONLY"
                        ─► SendMessage(planner, answers) ─► plan  (one round ─► then cto escalation)
  [risk low ─► skip review]  Agent(plan-reviewer) ─► verdict
        ▲                          │ CHANGES_REQUESTED
        └── SendMessage(planner) ◄──┘  (revise ×1 ─► then SendMessage(cto, escalation))
  SendMessage(test-planner, plan) ─► test plan ─► [no case: skip to coding]
  Agent(test-writer) ─► tests + a command per case ─► fingerprint them
  YOU run each new case ─► passes or does not run ─► SendMessage(test-writer)  (sharpen ×1)
  Agent(coding) ─► [fingerprints moved? ─► restore]
        │ testDisputes ─► SendMessage(test-planner) ─► upheld / revised (test-writer)
        ▼                  escalate ─► SendMessage(cto, escalation)  (one round per ticket)
  YOU run the feature's tests ─► fail ─► SendMessage(coding)  (fix ×2 ─► then cto)
        ▼ pass                               status ─► review
  ┌ Agent(code-reviewer) "Focus: correctness" ┐
  ├ Agent(code-reviewer) "Focus: conventions" ┤  concurrent, every one must APPROVE
  ├ Agent(code-reviewer) "Focus: security"    ┤
  └ Agent(code-reviewer) "Focus: tests"       ┤
        ▲                                     │ CHANGES_REQUESTED
        └── SendMessage(coding) ─► feature's tests ─► blocking reviewers only  (fix ×1 ─► then cto)
  YOU run full verification: lint, typecheck, full suite, e2e ─► fail ─► SendMessage(coding)  (fix ×1 ─► then cto)
  finish the ticket ─► commit the code (run branch) ─► commit the documents (framework root)
  ─► report + RUN-ROADMAP-RESULT
```

### Which agents are persistent
`agent-pipeline` holds the mechanics — spawn once, resume with `SendMessage`, concurrent calls in one
tool block, the single JSON block and its one retry, and the `completed` / `escalate` / `aborted`
vocabulary. The persistent roles here are the **cto**, the **planner**, the **plan reviewer** (two
on a high-risk plan), the **test planner**, the **test writer**, the **coding agent**, and the **four
code reviewers**, one per focus. Each focus is a role of its own: a re-review resumes the reviewer
that blocked. Keep every id. `agent-pipeline` also holds the test fingerprints and the dispute route.

**No agent runs a check.** You run every test and every project check yourself, with Bash, as
`cd <worktree> && …`, and read the result. No agent's report of a passing check counts.

**The `cto` is spawned once and resumed for every question in this invocation.** It reads the PRD and
the design docs on its first turn; re-spawning it throws that away and invites an answer that
contradicts the one before it.

## The caps — every one of them is hard

An unattended run with a soft cap is an unattended run that never ends. Apply these mechanically:

| Cap | Value | What happens at the cap |
| --- | --- | --- |
| Tickets per invocation | **1** | Print the result line and stop. The script starts the next ticket |
| Claim attempts lost in a row | **3** | Outcome `blocked` — another run keeps taking the same tickets |
| Plan revisions | **1** | Ask the CTO for an `escalation` ruling |
| Sharpen rounds for a new test that does not fail | **1** | A case that still passes is recorded and the run goes on. A case that still does not run asks the CTO for an `escalation` ruling |
| Feature-test fix cycles, a restored test file included | **2** | Ask the CTO for an `escalation` ruling |
| Test dispute rounds | **1** | A second dispute, or a dispute the test planner escalated, asks the CTO for an `escalation` ruling |
| Code review fix cycles | **1** | Ask the CTO for an `escalation` ruling |
| Full verification fix cycles | **1** | Ask the CTO for an `escalation` ruling |
| Re-asks for a missing result block, per agent turn | **1** | Outcome `aborted` at that stage |
| CTO rulings per stage | **1** | A second escalation at the same stage is `handed-back`. Never ask twice |
| CTO rulings per ticket | **2** | The third escalation is `handed-back`, whatever stage it came from |
| `retry` cycles granted by a ruling | **1 per stage** | A `retry` that fails again is `handed-back` |

A `retry` ruling buys exactly one more cycle at that stage, and the stage's own cap is then spent.
Never improvise a third cycle because the next one looks close.

## The worklog, the assignee, and the commit — you are the only writer

`ticket-board` holds the worklog's shape and what each assignee value means. What is this
pipeline's:

**You are the only writer.** The agents — the CTO included — report their decisions to you and you
write them down, so the file has one writer and the concurrent stages cannot lose an entry.

**The entry, the status, and the assignee go in one tool block**, at these boundaries. `<n>` is the
run's number, so `coding-3` works for `run-roadmap-3`:

| Boundary | Entries to append | `status` · `assigned` becomes |
| --- | --- | --- |
| Stage 2, starting the ticket | the worklog itself, with the `<run name> · start` entry | `in progress` · `implementation-planner-<n>` |
| Stage 4, the plan review gate closes | `implementation-planner · plan`, with each CTO answer, then `plan-reviewer · plan review` — none when the gate skipped the review | `in progress` · `test-planner-<n>` |
| Stage 4.5, the test plan lands | `test-planner · test plan` | `in progress` · `test-writer-<n>`, or `coding-<n>` when the plan holds no case |
| Stage 4.6, the tests land | `test-writer · tests` — the work root, every file, and the command that runs each case | unchanged |
| Stage 4.7, the new tests ran | `<run name> · new tests` | `in progress` · `coding-<n>` |
| Stage 5, the implementation lands | `coding · implement` | unchanged |
| Stage 5, every test dispute round | `test-planner · test dispute`, and `test-writer · tests` when a test was revised | `in progress` · `test-writer-<n>` while it rewrites, then `coding-<n>` |
| Stage 5.5, every run of the feature's tests | `<run name> · feature tests` | passing: `review` · `code-reviewer-<n>`; failing: unchanged |
| Stage 6, the code review closes | `code-reviewer · code review`, one per focus that reviewed | approved: `review` · removed; blocked: `in progress` · `coding-<n>` |
| Stage 6.5, every run of the full verification | `<run name> · verification` | passing: unchanged; failing: `review` · `coding-<n>` |
| Every CTO ruling | `cto · ruling` — the stage, the ruling, and the guidance | unchanged |
| Stage 8, finishing the ticket | `<run name> · done` | `done` · removed |

**The CTO's answers are the most valuable thing this run produces.** A person reads them weeks later
to learn why the product went this way, and nothing else records them. Write each one as the CTO
wrote it: the decision, what it beat, and the cost it accepted. The answers to the planner's open
questions go in the plan entry; every ruling gets an entry of its own.

**Every exit writes the outcome entry.** A hand-back, a defer, and an abort all run
`ticket-board`'s *Stopping without finishing* transition, so the next session reads the worklog and
learns where the ticket stopped and why. Then they all run Stage 9's **keep the record, discard the
code** procedure, whatever stage they stopped at — an unattended run must never leave half-built code
in the run worktree for the next ticket to commit.

## Workflow

### 0. Preflight — refuse to start on ground you cannot build on
Check these first, in one parallel Bash batch, and stop before you spawn anything if one fails:

- **The framework root and its roadmap exist.** Resolve them with `sdlc-structure`. With no roadmap
  anywhere, outcome `blocked`, naming `/setup`.
- **Every registered repository is a git work tree.** `git -C <path> rev-parse
  --is-inside-work-tree`, one per entry in the registry, in one batch. In a repo-rooted run that is
  the session's own repository, and the registry is not read. Without git there is no run branch and
  no audit trail: outcome `blocked`, naming the repository. **A dirty checkout is not a failure** —
  the run builds in its own worktree, from the checkout's last commit.
- **Every registered repository, and the folder its worktrees go in, is reachable from this
  session.** A path that does not exist or that this session cannot write to is outcome `blocked` —
  name it, and name the fix: restart with `--add-dir` for it. An unattended run cannot grant itself
  access.
- **The run's own worktrees, when they exist, are clean.** `git -C <worktree> status --porcelain`
  for each one a `--run` already made. Work left there is a ticket that neither committed nor
  discarded: outcome `blocked`, naming the worktree.

Report a `blocked` preflight in two lines and print the result line. Do not try to fix the ground.

### 1. Select the next feature — can it run?
`ticket-board` holds the roadmap's shape — one `## <CODE> — <epic name>` section per epic, one row
per ticket, and what an epic's `**Note**:` line and a `Depends on` cell mean — and how a roadmap
run selects. An epic is the tickets of one feature, so **a feature on the roadmap is its epic
section**. Reading a table top to bottom reads it in the order it should be built.

- **In an unattended run, rebuild the roadmap first.** Nobody is there to notice a stale row, so run
  `${CLAUDE_PLUGIN_ROOT}/scripts/build-roadmap.py --project <project>` and put what it reported into
  the opening worklog entry. Skip it when `python3` is missing, and say so in the report.
- **A feature this run already claims comes first.** Find every ticket whose `claimed` is this run's
  name and that is not `done`. When there is one, the run is in the middle of a feature: skip the
  CTO and the claim, and go to Stage 1.3. The end-to-end decision is the one the run's opening entry
  for that feature recorded.
- **Otherwise collect every candidate feature**, in roadmap order: an epic section with at least one
  ticket that is not `done`, whose **dependency cluster** — every ticket of the feature that is not
  `done`, and every ticket those depend on, directly or through another, that is not `done`, in any
  feature — holds no ticket another run claims and no ticket `blocked` on something outside the
  cluster. **Read every epic section**: a dependency may sit in another feature.
- **The ticket is the record.** Open every ticket of each candidate's cluster and take its
  description, acceptance criteria, priority, and `depends_on` from there. Correct a row that
  disagrees, as `ticket-board` says, and record what you corrected in the opening worklog entry.
- **No ticket left on the roadmap** → outcome `no-work`, `remaining` 0: the roadmap is done.
  **Tickets left and no candidate feature** → outcome `no-work` with the tickets left in
  `remaining`, and say what each feature waits on — another run's claim, a block, a missing ID. A
  person has to unblock it. Never invent a ticket.

Then spawn the CTO — **once**, and keep its id for the whole session:

```
Agent(subagent_type: "sdlc:cto", model: "opus",
      prompt: "Request: feature-selection. You are answering in place of the user in an autonomous
               run — no person will be asked anything.
               Pick the next feature to build, and call the end-to-end question for it. Hand the
               pick back when every candidate needs a decision only a person can make."
              + the candidate features in roadmap order — for each: the code, the feature name, any
                epic **Note**: line, and every ticket of its cluster (ID, title, priority, feature,
                description, acceptance criteria, Depends on)
              + "Remaining on the roadmap: <N> tickets across <K> features.")
```

It returns one `json` block with `featureCode`, `rationale`, `e2e`, `skipped`, and the hand-back
fields — the shape is in the agent definition, do not restate it.

- `handBack: true` → **it cannot run**: outcome `handed-back`. Nothing has started, so there is no
  ticket to stop: report the reason and print the result line.
- A `featureCode` that is not a candidate → ask **once** for a candidate code. A second bad answer
  is `aborted` at stage `selection`.
- A non-empty `skipped` → carry each skipped feature and its reason into the report, so a person can
  fix it. Change nothing about its tickets.
- **Confirm automatically.** Where `/orchestrate` asks the person to confirm the pick, the CTO's pick
  stands. **Carry `e2e` forward as the `e2eDecision`**, the exact string the CTO returned. It holds
  for every ticket of the feature.

Track the stages with the task/todo tools, so the session's log shows live progress.

### 1.2 Claim the feature's dependency cluster — is the claim held?
Write `claimed: <run name>` on **every** ticket of the selected feature's cluster, in one tool block,
then read every one back in the next. `ticket-board` holds the claim's rules.

- **Every claim reads back as this run's** → held. Go to Stage 1.3.
- **Any one reads back as another run's** → lost. Remove the claims this attempt wrote, in one tool
  block, and go back to Stage 1 with the candidates collected again. Resume the same CTO, and tell it
  which ticket of which feature was lost.
- **Lost three times in a row** → outcome `blocked`: another run keeps taking the same tickets, and a
  person has to look. Release nothing else — this attempt's claims are already removed.

### 1.3 Choose the feature's next ticket
**The ticket to build** is the cluster's first ticket, in dependency order, whose `depends_on` is all
`done`; between two such tickets, the one higher on the roadmap. A dependency in another feature
therefore comes before the feature's own tickets that need it. Every later session of this run
builds the next one, until the cluster is done — then Stage 1 selects the next feature.

### 1.5 Identify the work roots, and create a run worktree in each
**The work roots are the `repositories` of the ticket to build and of its direct dependencies**,
by registry code. When the ticket's field is empty, or names a code the registry lacks, spawn the
resolver as `sdlc-structure` says:

```
Agent(subagent_type: "sdlc:repo-resolver", model: "sonnet",
      prompt: the ticket + its feature note and design docs + one line per registry entry
              (code, absolute path, what, projects) + each dependency's repositories)
```

- **`settled: true`** → its codes are the ticket's work roots. Write them onto the ticket's
  `repositories` in the Stage 2 Starting a ticket tool block, and its evidence into the opening
  worklog entry.
- **`settled: false`** → outcome `handed-back`: nobody is here to choose, and building in the wrong
  repository costs the whole pipeline. Report the candidates it named, so a person can fill
  `repositories` and resume. Release the cluster's claims first, as every end does.
- Silent after one re-ask → `aborted` at stage `repositories`.

Never ask the CTO which repository, and never fall back to every registered repository.

**Then make sure a run worktree exists in each**, at
`<parent of the repository>/<repository name>-worktrees/run-roadmap-<n>`:

- **It exists** (`git -C <repository> worktree list` names it) → reuse it. Earlier tickets of the run
  are already committed on its branch.
- **The branch exists without a worktree** — a resumed run → `git -C <repository> worktree add
  <path> run-roadmap-<n>`.
- **Neither exists** → `git -C <repository> worktree add -b run-roadmap-<n> <path> HEAD`, from the
  checkout's current commit.

A worktree that cannot be created — the path is taken, the branch is checked out elsewhere, the
folder is not writable — is outcome `blocked`, naming the repository and git's error. **Remove this
run's claims on the whole cluster first**, as every end does. A worktree that exists but is not clean
is `blocked` the same way.

### 2. Start the ticket, then plan and draft the tests concurrently
**Pick up the ticket to build**: run `ticket-board`'s **Starting a ticket** transition yourself,
with the edits in one tool block. The claim is already written, so it stays. Two values are this
command's: `assigned` is `implementation-planner-<n>`, and the **opening worklog entry** is
`<run name> · start` — the ticket, what it delivers, the feature the run holds and the cluster it
belongs to, every run worktree with its branch and the evidence that settled each work root, the
`e2eDecision`, and the line that this is an autonomous run whose answers come from the `cto` agent.

**The decisions were made before the run.** `/plan` interviewed a person and wrote each settled
choice into the ticket's `Decisions`, the feature note, and its design docs. This run holds no
interview: the planner reads those documents, and only a fork they leave open reaches the CTO.

Then issue **both `Agent` calls in one tool block**:

```
Agent(subagent_type: "sdlc:implementation-planner", model: "opus",
      prompt: the ticket block + acceptance criteria + its Decisions + roadmap and epic context
              + the run worktree as the work root + the e2eDecision line
              + "Read the feature folder — the ticket, the feature note, the design docs it lists,
                 the solution designs in designs/, and the PRD — then survey the code and research
                 current practice. The ticket's Decisions are fixed constraints. Return the context
                 pack with the project's check commands, the full plan, and its risk profile in this
                 one reply — or, when a fork the documents leave open needs an answer, the context
                 pack and every open question instead. I settle them in one round.")

Agent(subagent_type: "sdlc:test-planner", model: "opus",
      prompt: the ticket block + acceptance criteria + its Decisions + the design docs' paths
              + the e2eDecision line + the run worktree as the work root
              + "SPEC ONLY. The plan is being written and you will not see it yet. Draft the cases
                 from the specification and the existing tests now, and reply with a few lines.
                 I will send the plan.")
```

Keep both ids. The planner ends with one `json` block holding `contextPack` (relevant files, key
symbols, conventions, `verificationCommands`, `e2eCommand`), `riskProfile`, and `openQuestions`. A
**plan turn** carries the plan and an empty `openQuestions`. A **question turn** carries the context
pack and every open question, no plan, and a `null` `riskProfile`. **Forward the `contextPack`** into the first message of the plan reviewer, the test writer, the
coding agent, and every code reviewer, and to the test planner with the plan, so none of them
cold-explores the codebase. Its `verificationCommands` and `e2eCommand` are the checks you run in Stage 6.5.

Planner silent → `aborted` at stage `plan`. The test planner's spec-only turn emits no `json`
block; it is silent only when it returns nothing at all → `aborted` at stage `test-plan`.

### 3. The CTO answers the open questions — one round
**A plan turn** → the plan stands; go to Stage 4.

**A question turn** → resume the same CTO — do not spawn a second one:

```
SendMessage(ctoId, "Request: decisions. The planner read the ticket's documents and the code, and
                    these forks are still open. Answer each one. The ticket's Decisions are fixed,
                    and the e2e call you already made is <e2eDecision> and stands."
                 + every entry of openQuestions — its id, question, options with their cost,
                   and the planner's recommendation with why)
```

In the same tool block, spawn the plan reviewer in **pre-read only** mode, so it reads the context
pack while the plan is still being written; see Stage 4. The CTO returns one choice per question and
the hand-back fields; the shape is in the agent definition.

- `handBack: true` → outcome `handed-back`: the ticket goes back to planning with a person. Run
  *Stopping without finishing*, with the outcome entry naming the question the CTO would not settle
  and why.
- Otherwise `SendMessage(plannerId, the answers + "These questions are settled — treat the answers
  as fixed constraints. Write the full plan now, and end with the ```json block.")`. Keep the
  answers for the plan entry. Planner silent → `aborted` at stage `plan`.

**One round only.** A non-empty `openQuestions` on the planner's next turn is an escalation: ask the
CTO for a ruling (Stage 7) with stage `plan`.

### 4. Review the plan — the risk gate
**Apply the gate mechanically** on the final `riskProfile`:

- **Skip review** iff `filesTouched ≤ 2` **and** `addsDependency == false` **and**
  `addsPublicApi == false` **and** `criteriaAutoCheckable == true`. Log "Review gate: SKIPPED", append the
  plan entry and set `assigned` to `test-planner-<n>` in one tool block, and go to Stage 4.5 with the
  plan as approved.
- Otherwise **review is required**, and it is **high-risk** iff `addsPublicApi == true` **or**
  `addsDependency == true` **or** `filesTouched > 5`.
  - **Normal risk** → **one** reviewer, `model: "sonnet"`.
  - **High risk** → **two** reviewers in one tool block, `model: "opus"`, with distinct lenses:
    (a) correctness and completeness against the acceptance criteria; (b) codebase fit — conventions,
    dependency rules, architectural boundaries. Keep both ids.

**Let the reviewer read while the plan is written.** On a question turn no `riskProfile` exists
yet, so Stage 3 spawns one reviewer in **pre-read only** mode — the ticket, the criteria, its
Decisions, the context pack, and "PRE-READ ONLY. The plan is still being written. Do NOT issue a
verdict yet." When the plan lands, hand it over with `SendMessage(reviewerId, "Review the plan below
against the checklist. Re-read only what the plan points at that you have not seen." + plan)`. A
high-risk plan reuses it as lens (a) and spawns lens (b) fresh; a gate that skips the review drops
it. After a plan turn in Stage 2 there is no pre-read: spawn the reviewer(s) with the ticket, the
criteria, its Decisions, the context pack, and the plan in one message. The plan reviewer takes no
focus input, so each high-risk prompt names its lens.

Merge multiple verdicts: `CHANGES_REQUESTED` if **any** reviewer requests changes; concatenate the
issues. Every reviewer silent → `aborted` at stage `plan-review`.

- `APPROVED` → append the plan and plan-review entries and set `assigned` to `test-planner-<n>`, in
  one tool block, then Stage 4.5. The plan entry carries the **direction** the plan settled on, the
  approach it turned down, and each CTO answer with its reason; the plan markdown is kept nowhere.
- `CHANGES_REQUESTED`, **not yet revised** → `SendMessage(plannerId, "Revise your plan to resolve
  every issue below. Note in the Context section how each was addressed. Re-emit the full plan
  markdown + the ```json block." + issues)`, then re-review through the same reviewer(s).
- `CHANGES_REQUESTED`, **already revised once** → **ask the CTO** (Stage 7) with stage
  `plan-review`.

### 4.5 Plan the tests
Resume the test planner: `SendMessage(testPlannerId, the approved plan + the context pack + "The
plan is approved. Attach your drafted cases to the public interfaces it exposes, cut what it made
redundant, and return the full test plan with its ```json block.")`. It returns `summary`, `cases`,
and `untested`. Silent → `aborted` at stage `test-plan`.

Append the `test-planner · test plan` entry — each case in one line and each exclusion with its
reason — and set `assigned` to `test-writer-<n>`, in one tool block. **An empty `cases` skips Stages
4.6 and 4.7**: record the planner's reason, set `assigned` to `coding-<n>`, and go to Stage 5 with no
written tests.

### 4.6 Write the tests
Spawn **once** and keep the id:

```
Agent(subagent_type: "sdlc:test-writer", model: "sonnet",
      prompt: test plan + approved plan + contextPack + the run worktree as the work root
              + "Write exactly these cases and nothing else. Report every file you changed and
                 the command that runs each case, then stop.")
```

It returns `testFiles`, `cases` — each with the `command` that runs it alone and what the writer
`observed` — the top-level `command` and `e2eCommand`, and `blockers`. `observed` is the writer's own
report, never the gate: Stage 4.7 runs every case itself. Silent → `aborted` at stage `write-tests`.
Non-empty `blockers` → **ask the CTO** with stage `write-tests`. **Fingerprint every file it created
or modified**, as `agent-pipeline` says. Append the `test-writer · tests` entry, in one tool block:
the work root, every test file, and each case's `command` beside its id. **This entry is the record the
feature's later tickets run**, so write each command exactly as the writer reported it.

### 4.7 Run each new test — every one must fail
Run each case by its own `command`, as `cd <worktree> && <command>`, and read the result. **Every
new case must fail**, because the behavior it tests is not built yet:

- **Fails on its assertion, or on the missing module the plan will create** → as expected.
- **Passes** → it catches nothing yet. A case whose `kind` in the test plan is `guard` guards
  behavior that already exists, is expected to pass, and stays.
- **Does not run** — a syntax error, a runner error, no test collected → it is broken.

Send every passing or broken case back in one message: `SendMessage(testWriterId, "These cases did
not fail as they must. Sharpen each passing one so it asserts what only the new code delivers, repair
each broken one, and report again." + each case and its output)`. Fingerprint its files again,
append a new `test-writer · tests` entry when a file or a command changed, and run those cases once
more. **One sharpen round only**: a case that still passes is recorded and the run goes on; a case
that still does not run → **ask the CTO** with stage `new-tests`.

Append the `<run name> · new tests` entry — each case and how it failed, and each case recorded as
passing — and set `assigned` to `coding-<n>`, in one tool block.

### 5. Implement
Spawn **once** and keep the id:

```
Agent(subagent_type: "sdlc:coding", model: "opus",
      prompt: "Implement the approved plan exactly — no scope creep. Match the context pack
               conventions. Build until the written tests pass. Check only what you touched; I
               run every test and every project check myself. Never change a test file —
               dispute it instead."
              + approved plan + contextPack + acceptance criteria + the ticket's Decisions
              + each CTO answer + the test plan + the test files and each case's command
                (or: "No test was written: <summary>"))
```

It ends every turn with `summary`, `workItemsCompleted`, `filesChanged`, `decisions`, `blockers`,
`testDisputes`, and `notes`. Act on **every** `coding` turn — this stage's and every later fix — in
this order:

1. Silent → `aborted` at stage `implement`.
2. **Compare the fingerprints.** A changed test file goes back to the coding agent to restore, and
   that spends one feature-test fix cycle; with none left → **ask the CTO** with stage `implement`.
3. Non-empty `blockers` → **ask the CTO** with stage `implement`.
4. Non-empty `testDisputes` → the test defect round below.
5. Otherwise go on. On this stage's turn, append the `coding · implement` entry — its `decisions`,
   the code-level calls the plan left open — in one tool block, then Stage 5.5. A fix turn goes back
   to the stage that asked for the fix.

**Test defect — at most ONE dispute round per ticket.** `SendMessage(testPlannerId, "The coding agent
disputes these tests. Rule on each against the specification." + testDisputes)`. It rules on each
test:

- **`upheld`** → the test stands. Send the coding agent every upheld ruling and its reason in one
  message, and run its reply through steps 1–5.
- **`revised`** → set `assigned` to `test-writer-<n>` and resume the test writer with the revised
  cases — spawning it now when the empty test plan skipped Stage 4.6. Fingerprint its files again and
  append a new `test-writer · tests` entry. A rewritten test skips Stage 4.7, because the code that
  makes it pass now exists: go straight to Stage 5.5.
- **`escalate`** → **ask the CTO** with stage `test-dispute`. The CTO answers a question about the
  specification with a `retry` whose `guidance` holds the reading it chose: send that guidance to the
  test planner, which rules again from it. That is the one extra ruling the CTO's `retry` buys.

A dispute may come from any `coding` turn, including a fix after the code review or the full
verification. A second dispute → **ask the CTO** with stage `test-dispute`. Append the
`test-planner · test dispute` entry — each dispute, its ruling, and the reason — and set `assigned`
back to `coding-<n>`.

### 5.5 Run the feature's tests — at most two fix cycles
**The feature's tests** are every test file recorded in the `test-writer · tests` entries of the
worklogs of the feature's tickets — those already `done` and this one. Find them by the `feature`
property, in every bucket, and take each file's latest entry. Run each by the command recorded beside
it, as `cd <worktree> && <command>`, in the run worktree of the work root the entry names; an entry
for a work root this ticket does not build in is not run. Run nothing else here: no lint, no full
suite, and no end-to-end test — Stage 6.5 runs those.

- A recorded file that the worktree does not hold — a ticket built on a branch not merged yet — is
  skipped, and the entry and the report name it. Never record a skipped test as passed.
- With no test recorded for the feature, the stage is skipped, and the entry says so.

Append the `<run name> · feature tests` entry on every run — each file and its result.

- **All passing** → set `status` to `review` and `assigned` to `code-reviewer-<n>`, in the same tool
  block, then Stage 6.
- **Failing, with a cycle left** → `SendMessage(codingId, "The feature's tests fail. Fix the code,
  not the tests, then stop; I run them again." + the failures)`. Run its reply through Stage 5's
  steps 1–5, then run the feature's tests again, the failed files first.
- **Failing, with both cycles spent** → **ask the CTO** with stage `feature-tests`.

### 6. Code review — four reviewers at once, one fix cycle
Issue **four `Agent` calls in one tool block**, one per focus, each spawned once and resumed:

```
Agent(subagent_type: "sdlc:code-reviewer", model: <opus on high risk, else sonnet>,
      prompt: "Focus: <correctness | conventions | security | tests>. Review the change the coding
               agent made, against the approved plan and the acceptance criteria. The feature's
               tests already pass, and I run every project check — do not run any."
              + approved plan + acceptance criteria + the ticket's Decisions + contextPack
              + the coding agent's filesChanged + the run worktree as the work root
              + the review target ("the uncommitted changes against HEAD, untracked files included")
              + (focus tests only) the test plan + the test files, and each case recorded as passing
                in Stage 4.7)
```

| Focus | Judges |
| --- | --- |
| `correctness` | Bugs, edge cases, and whether every acceptance criterion is met |
| `conventions` | Fit with the codebase, its architecture, and the plugin's coding skills |
| `security` | Authentication, input handling, secrets, and injection |
| `tests` | Whether the tests match the test plan and catch the bugs it named |

**The code review has no skip gate**: every focus runs on every ticket, and the model follows the same
high-risk test as Stage 4. Append one `code-reviewer · code review` entry per focus that reviewed.

- Any reviewer silent → `aborted` at stage `code-review`.
- **Every reviewer returns `APPROVED`** → remove `assigned`, keep `status` `review`, then Stage 6.5.
  Minor issues become recommendations in the report; they block nothing.
- **A reviewer blocks, not yet fixed** → set `status` to `in progress` and `assigned` to
  `coding-<n>`, then one message with every blocking issue: `SendMessage(codingId, "The code review
  found the following. Fix ONLY what is needed to clear them — stay within the approved plan, change
  no test, then stop." + the blocking issues)`. Run its reply through Stage 5's steps 1–5, run the
  feature's tests again (a failure spends a Stage 5.5 fix cycle), and set `status` back to `review`.
  Then resume **only the reviewers that blocked**, in one tool block.
- **A reviewer blocks, already fixed once** → **ask the CTO** with stage `code-review`.

### 6.5 Run full verification — one fix cycle
Run **every check command in the context pack** yourself, in one parallel Bash batch, as
`cd <worktree> && <command>`: the `command` of every `verificationCommands` entry — `lint`,
`typecheck`, and `test`, the full suite — and, when the `e2eDecision` says yes, the end-to-end
tests: the project's `e2eCommand` and the test writer's `e2eCommand`, each one that is not `"none"`
or `""`.
Read each result. This pipeline runs the end-to-end suite inside the gate: there is no person at the
end to ask, and an unattended commit must not rest on a suite nobody ran.

**A ticket built in two work roots is verified in each**: every work root's checks run in its own
run worktree, and the ticket passes only when both pass.

A check the project lacks — an entry whose `command` is `"none"` — is reported as **skipped**, with
the reason, in the report and the
worklog — **never record a skipped check as passed**. Append the `<run name> · verification` entry on
every run: each command and its result.

- **Every check passes** → Stage 8.
- **A check fails, not yet fixed** → set `assigned` to `coding-<n>`, then one message with every
  failure: `SendMessage(codingId, "The full verification failed. Fix ONLY what is needed to clear
  it — stay within the approved plan, change no test, then stop." + each failing command and its
  output)`. Run its reply through Stage 5's steps 1–5, then run the failed checks first and the rest
  after them.
- **A check fails, already fixed once** → **ask the CTO** with stage `verification`.

### 7. Ask the CTO for a ruling — the procedure every cap runs into
This replaces every `escalate` in `/orchestrate`. Before you ask, check the caps: a **second** ruling
at this stage, or a **third** on this ticket, is not a question — it is outcome `handed-back`.

```
SendMessage(ctoId, "Request: escalation. Stage <stage> hit its cap."
                 + what the stage reported (issues, failures, or blockers)
                 + what was already tried (the revision or the fix cycle, and what it changed)
                 + "Rulings already given on this ticket: <list, or none>.")
```

The stages are `plan`, `plan-review`, `write-tests`, `new-tests`, `implement`, `test-dispute`,
`feature-tests`, `code-review`, and `verification`. Append the `cto · ruling` worklog entry for every
ruling, whatever it says, then act:

| Ruling | What you do |
| --- | --- |
| `retry` | One more cycle at that stage, with the CTO's `guidance` in the message to the agent that owns it. The stage's cap is now spent — a second failure is `handed-back` |
| `rescope` | `SendMessage` the planner or the coding agent with the narrowed ticket, finish it, and in the Stage 8 edit **add the dropped part to the roadmap** as a new `backlog` ticket, per `ticket-board`. Say what came out, in the report and the worklog |
| `defer` | Outcome `deferred`. Run *Stopping without finishing*, then Stage 9's **keep the record, discard the code** procedure. The ticket keeps everything that was learned, and the roadmap run ends: a person decides how the feature goes on without it |
| `stop-run` | Outcome `stop-run`. The same as `deferred` for this ticket |
| `handBack: true` | Outcome `handed-back`, whatever the ruling field says. A person decides |

### 8. Finish the ticket (only on success)
Run `ticket-board`'s **Finishing a ticket** transition yourself, in one tool block: the status field,
the closing worklog entry, the move into `done/`, and the roadmap row deleted. This command's closing
entry is `<run name> · done`, and it names each note file. In the same step, write the coding agent's
latest `notes` with `create-note.py`, as `agent-pipeline` says, with `--run <run name>`. A note is
never a reason to stop: the run goes on, and a person acts on the note later.

Do this **before** the commits, so the documents commit in Stage 9 holds the ticket in `done/`.
The ticket's claim goes with it — the rest of the cluster keeps this run's claim.

Never finish the ticket unless the feature's tests passed, **all four** code reviewers returned
`APPROVED`, **and** every check of the full verification passed.

### 9. Commit the code, then the documents
One code commit per finished ticket on the run branch, so `git log run-roadmap-<n>` holds the run as
a sequence of changes a person can read and merge.

**Commit the code on the run's branch**, in every run worktree the ticket changed:

1. `git -C <worktree> add -A`, then one commit. The worktree was clean when the ticket started, so
   everything staged belongs to this ticket.
2. **Match that repository's own commit convention.** Read `git -C <worktree> log --oneline -20` and
   follow what is there — a Conventional Commits prefix, a ticket ID in the subject, whatever the
   repository does. With no discernible convention, use `<ID>: <title>`.
3. The body is three or four lines: what landed, the decision the CTO made that shaped it, and the
   verification result. `technical-writing` governs it. A ticket that changed two worktrees gets one
   commit in each, same subject, each body naming the other repository.
4. **Never push, never merge, never amend, and never touch a commit that was already there.**
5. A commit that fails — a hook rejects it — is outcome `blocked`. Say what the hook said, and leave
   the worktree as it is for a person to look at. Do not retry with `--no-verify`.

**Commit the documents in the framework root**, when it is a git tree: `git -C <framework root> add`
the ticket, its worklog, every roadmap the ticket's row was in, any ticket Stage 8 corrected, and
each note file `create-note.py` reported as `created` —
those paths only, because the person may have their own changes there — then one commit with the
code commit's subject. A framework root in a vault that is no git tree has nothing to commit: the
files are saved, and the report says so.

**Keep the record, discard the code** — the exit every unfinished ticket takes: `deferred`,
`stop-run`, `handed-back`, `aborted`, and a `blocked` commit's ticket once a person has looked.
Half-built code must not be committed, the ticket's record must survive, and the next session has
to start from a clean worktree:

1. Write the *Stopping without finishing* edits first — the status, `blocked_by`, the assignee
   removed, and the outcome worklog entry.
2. **Release the run's claims** on every ticket of the cluster that is not `done`, in the same tool
   block. Every end of a roadmap run does this.
3. `git -C <worktree> reset --hard` then `git -C <worktree> clean -fd`, in every run worktree the
   ticket touched. The worktree is the run's own, so this discards exactly the ticket's code and
   nothing of the person's.
4. Commit the documents in the framework root, as above, with a subject naming the ticket and the
   outcome — `<ID>: deferred by cto` — and the CTO's reason in the body.
5. Confirm every worktree is clean with `git -C <worktree> status --porcelain`. The script ends the
   run when a ticket leaves work behind.

**On `--final`**, release the run's claims the same way after a completed ticket too, so no claim
outlives the run.

Say plainly in the report that the code was discarded and the record kept, and that the branch and
the worktrees stay for the resume.

### 10. Report, then print the result line
The report is short — a person reads a hundred of these in a log, not one on a screen:

```markdown
## [ID] — [Title] · [outcome]

- [x] Feature chosen by cto — [the rationale, one line]
- [x] Planning — [N] open questions answered by cto (or: none); approved ([0 or 1] revision, or: review gate skipped)
- [x] Test plan — [N] cases, [M] left untested on purpose (or: no case — [why])
- [x] Tests written first — [N] failing before the code; [K] sharpened, [P] still passing and recorded
- [x] Implementation — [N] files; [0 or N] test disputes ([rulings])
- [x] Feature's tests — passed, [N] files across [M] tickets ([0–2] fix cycles; [what was skipped and why])
- [x] Code review — correctness, conventions, security, tests approved ([0 or 1] fix cycle)
- [x] Full verification — passed ([the commands], or: [what was skipped and why])
- [x] Run — [run name] · branch `run-roadmap-<n>` · feature [CODE] · cluster [IDs, done and left]
- [x] Run worktrees — [code] `[absolute path]`, one per line
- [x] Commits — code [sha] [subject]; documents [sha], or: the framework root is no git tree
- [x] Status — ticket Completed and moved to `done/`, roadmap row deleted
- [x] Needs a person — [each note file and its title], or: nothing

[Two or three lines: what shipped, and the decision that shaped it.]
[Any skipped candidate and its reason. Any recommendation nobody acted on.]
[How to resume: `run-roadmap.sh --run <n>`, and what the resume will build first — the feature's next ticket, or the next feature when this one is done.]
```

Then, as the **last line of your final message and nothing after it**, print exactly one result line.
The launcher script parses it to decide whether to start another ticket:

```
RUN-ROADMAP-RESULT {"outcome":"completed","run":"run-roadmap-3","feature":"AUTH","taskId":"AUTH-002","commit":"a1b2c3d","workRoots":["/Users/me/Projects/acme-api-worktrees/run-roadmap-3"],"remaining":4,"nextAction":"continue","reason":""}
```

One line, valid compact JSON, no code fence, no text after it. The fields:

| Field | Value |
| --- | --- |
| `outcome` | `completed`, `deferred`, `handed-back`, `aborted`, `stop-run`, `no-work`, or `blocked` |
| `run` | The roadmap run's name, `run-roadmap-<n>`. The script passes it to the next session |
| `feature` | The code of the feature the run holds, or `""` when none was selected |
| `taskId` | The ticket this invocation worked on, or `""` when none was started. It may belong to another feature, as a dependency of the one the run holds |
| `commit` | The code commit's short sha, or `""` when nothing was committed. Two worktrees give two shas, joined by a comma |
| `workRoots` | Every run worktree this invocation wrote to, as absolute paths. `[]` when none was started. The script checks these trees between tickets |
| `remaining` | Tickets left on the roadmap **after** this invocation, counted from the file you just wrote |
| `nextAction` | `continue` or `stop` |
| `reason` | One short sentence on a non-`completed` outcome, `""` otherwise. No newline, no quote character |

**`nextAction` follows from `outcome`, mechanically:**

| Outcome | What happened | `nextAction` |
| --- | --- | --- |
| `completed` | The ticket shipped and was committed on the run branch | `continue`, or `stop` when `remaining` is 0 or this session is `--final` |
| `deferred` | The CTO ruled `defer`; the ticket waits for a person | `stop` |
| `handed-back` | The CTO set `handBack`, or a cap ran out of rulings | `stop` |
| `aborted` | An agent returned nothing usable after one retry | `stop` |
| `stop-run` | The CTO ruled that the run must end | `stop` |
| `no-work` | No ticket left (`remaining` 0), or tickets left and none can be selected | `stop` |
| `blocked` | Preflight, the claim, a worktree, or a commit failed — the ground is wrong | `stop` |

`technical-writing` governs the report. **It does not govern the result line**, which is data: keep the
keys, the order, and the spelling exactly as above.

## Rules
The four skills carry the rules they own. What is this command's own:

- **One ticket per invocation.** Never loop over the roadmap in one session. The script does that.
- **Never call `AskUserQuestion`, and never write a sentence that waits for an answer.** Ask the
  CTO, or hand back.
- **The CTO decides; you execute and record.** Never answer a product question yourself, and never
  overrule the CTO — but never let it past a failing gate either. A test result and a review verdict
  are not product decisions.
- **Every cap is hard**, and the CTO's `retry` buys exactly one cycle. No improvised extra pass.
- **Tests before code, and the coder never touches them.** Every new test runs before `coding`
  starts, and one that does not fail is sharpened once, then recorded. Once `coding` starts, a test
  changes only by a `revised` ruling from the test planner. The CTO settles what the specification
  means; it never tells the coding agent to change a test.
- **Work one feature at a time.** Claim its whole cluster before anything else is written, build every ticket of it before selecting another feature, and release the claims at every end.
- **Build only in the run worktrees.** Create them before the ticket starts, record them in the worklog, pass them to every agent as the work root, and name them in the result line. Never let an agent infer which repository it is working in, and never write to the person's checkout.
- **You write the status, the assignee, the worklog, the roadmap, and the commit.** No agent writes
  any of them.
- **You run every check.** Every new test, the feature's tests, and the full verification run in your
  own Bash calls, in the run worktree. No agent's report of a passing check counts.
- **Never finish a ticket unless the feature's tests passed, all four code reviewers approved, and
  every check of the full verification passed.**
- **One code commit per ticket, on the run branch; one documents commit in the framework root. Never push, never merge.**
- **A clean worktree in, a clean worktree out.** A finished ticket is committed; an unfinished one
  keeps its record and discards its code, by Stage 9's procedure, and the run ends. Either way the
  next invocation starts on a clean worktree, because the script stops the run when it does not.
- **The result line is the interface.** Print it on every path, including a preflight failure, and
  print nothing after it.
