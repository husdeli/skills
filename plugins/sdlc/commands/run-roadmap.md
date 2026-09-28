---
description: Build the next roadmap task with no person in the loop — the cto agent answers every question, the task is committed, and the run reports a machine-readable result for the launcher script.
argument-hint: [roadmap-file-path]
---

# Autonomous Roadmap Runner

You drive **one** roadmap task from pending to committed, and **you never ask the user anything**.
Every question an interactive pipeline would put to a person goes to the **`cto`** agent instead.
When the task is done you commit it, print a result line, and stop.

Roadmap file (if provided): $ARGUMENTS

This is `/orchestrate` with the human replaced. The stages, the gates, and the caps are the same;
what changes is who answers, what happens at a cap, and that the run ends in a commit and a parsable
result. One invocation is one task — the loop over the roadmap belongs to
[`scripts/run-roadmap.sh`](../scripts/run-roadmap.sh), which starts a fresh session per task so a
long roadmap never runs out of context.

**Nobody is watching this run.** That is the one fact that shapes every rule below: no
`AskUserQuestion`, a hard cap on every cycle, a commit per task so `git log` is the audit trail, and
a hand-back that stops the run whenever the decision belongs to a person.

## The rules live in four skills — load each one before the stage that needs it

| Skill | What it holds | Load before |
| --- | --- | --- |
| **`product-docs`** | Where the docs root and the work root are, and how each destination writes a document | you read any document |
| **`ticket-board`** | The ticket, the roadmap, the assignee, the worklog, and what each status transition writes | Stage 1 |
| **`agent-pipeline`** | Spawn once and resume, concurrent calls, the JSON block, the outcome vocabulary | Stage 2 |
| **`clean-writing`** | Every word a person reads later — the worklog, the commit message, the report | Stage 2 |

Each name may be namespaced here — `sdlc:product-docs`, `sdlc:ticket-board`,
`sdlc:agent-pipeline`, `sdlc:clean-writing`. Invoke the namespaced form when it is there, load each
skill **once**, and follow it. Do not work from memory, and do not restate a skill's rules in a
spawn prompt: the agents load their own.

**The documents sit in the docs root** — `prd.md`, `glossary.md`, `designs/<subject>.design.md`,
`roadmap.md`, and `tickets/<status>/<ID>-*.md`, with a worklog beside a ticket in flight.
`product-docs` resolves the root, and every `.sdlc/…` path below means `<docs root>/…`.

**The code sits in the work root** — the repository this task is built in. A run started inside a
repository builds there and nothing changes. A run started in the vault — the recommended shape,
where one board drives several repositories — has the docs root as its working directory, resolves
the work root per task, and reaches into a repository somewhere else. `product-docs` holds the
resolution rule. What is this command's:

- **The work root is resolved in Stage 1.5**, after the CTO picks the task and before the ticket is
  started. The ticket names no repository, so the evidence is the design doc, the ticket, the epic,
  and the registry's `what` lines.
- **Nobody is here to break a tie.** When the evidence leaves it open, the `cto` agent answers —
  request `work-root` — and that answer counts against the same ruling budget as every other.
- **Every git call names the repository**: `git -C <work root> …`. Every build, test, and package
  manager command runs as `cd <work root> && …`. A bare `npm test` runs in the vault and proves
  nothing.
- **Every agent prompt carries the work root as an absolute path**, and the planner carries it in
  the context pack as `workRoot`.
- **The commit belongs to the work root.** The docs root is usually no git tree, so the ticket move
  and the roadmap edit are not part of it — Stage 9 holds both cases.

## The one rule that makes this command different

**Never call `AskUserQuestion`. Not once, at any stage, for any reason.** There is no person on the
other end of this session, so a question is a hang, and a hang inside an unattended loop burns the
whole run.

Every question goes to the `cto` agent, which answers in the user's place:

| What `/orchestrate` asks the user | Who answers here |
| --- | --- |
| Which candidate task to build | `cto`, request `task-selection` |
| Whether the task gets end-to-end tests | `cto`, in the same `task-selection` answer |
| Which repository the task is built in | `cto`, request `work-root` — only when the evidence left it open |
| The interviewer's open decisions and assumptions | `cto`, request `decisions` |
| Nothing — it stops and escalates | `cto`, request `escalation` |

When the CTO sets `handBack: true`, **that** is the moment a person is needed. Stop, run
`ticket-board`'s *Stopping without finishing* transition, and report the outcome `handed-back`. Do
not try to answer a handed-back question yourself.

## Architecture: the interactive shell, driven by an agent

```
  YOU (main loop)
  ─────────────────────────
  preflight ─► read roadmap ─► collect candidates ─►

  Agent(cto) ─► task + e2e call ─► start the ticket ─►

  ┌ Agent(feature-interviewer) ─► brief ─┐  concurrent
  └ Agent(planner) "SCOUT ONLY" ─► pack ─┤
        SendMessage(cto, brief) ─► Decisions ◄┘
        SendMessage(planner, Decisions) ─► plan ─►
  ┌ Agent(reviewer) "PRE-READ ONLY" ─────┐  concurrent with planning
  └ [review gate] ─► SendMessage(reviewer, plan) ◄┘
        ▲                          │ CHANGES_REQUESTED
        └── SendMessage(planner) ◄──┘  (revise ×1 ─► then SendMessage(cto, escalation))
  Agent(coding) ─► ┌ Agent(verify) ──────┐  concurrent
                   └ Agent(code-reviewer)┤
        ▲                                │ FAILED or CHANGES_REQUESTED
        └── SendMessage(coding) ◄─────────┘  (fix ×1 ─► then SendMessage(cto, escalation))
  finish the ticket ─► commit ─► report + RUN-ROADMAP-RESULT
```

### Which agents are persistent
`agent-pipeline` holds the mechanics — spawn once, resume with `SendMessage`, a fresh verify per
run, concurrent calls in one tool block, the single JSON block and its one retry, and the
`completed` / `escalate` / `aborted` vocabulary. The persistent roles here are the **cto**, the
**planner**, the **plan reviewer**, the **coding agent**, and the **code reviewer**. Keep every id.

**The `cto` is spawned once and resumed for every question in this invocation.** It reads the PRD and
the design docs on its first turn; re-spawning it throws that away and invites an answer that
contradicts the one before it.

## The caps — every one of them is hard

An unattended run with a soft cap is an unattended run that never ends. Apply these mechanically:

| Cap | Value | What happens at the cap |
| --- | --- | --- |
| Tasks per invocation | **1** | Print the result line and stop. The script starts the next task |
| Plan revisions | **1** | Ask the CTO for an `escalation` ruling |
| Fix cycles after verify and code review | **1** | Ask the CTO for an `escalation` ruling |
| CTO rulings per stage | **1** | A second escalation at the same stage is `handed-back`. Never ask twice |
| CTO rulings per task | **2** | The third escalation is `handed-back`, whatever stage it came from |
| `retry` cycles granted by a ruling | **1 per stage** | A `retry` that fails again is `handed-back` |

A `retry` ruling buys exactly one more cycle at that stage, and the stage's own cap is then spent.
Never improvise a third cycle because the next one looks close.

## The worklog, the assignee, and the commit — you are the only writer

`ticket-board` holds the worklog's shape and what each assignee value means. What is this
pipeline's:

**You are the only writer.** The agents — the CTO included — report their decisions to you and you
write them down, so the file has one writer and the two concurrent stages cannot lose an entry.

**The entry and the assignee go in one tool block**, at six boundaries:

| Boundary | Entries to append | Assignee becomes |
| --- | --- | --- |
| Stage 1, starting the ticket | the worklog itself, with the `run-roadmap · start` entry | `feature-interviewer, implementation-planner` |
| Stage 3, the decisions land | `feature-interviewer · interview`, then `cto · decisions` | `implementation-planner` |
| Stage 4, the review gate closes | `implementation-planner · plan`, then `plan-reviewer … · plan review` | `coding` |
| Stage 5, the implementation lands | `coding · implement` | `verify, code-reviewer` |
| Every CTO ruling | `cto · ruling` — the stage, the ruling, and the guidance | unchanged |
| Stage 6, the gate closes | `verify · verification`, `code-reviewer · code review`, then the outcome | `—` on completion, `user` on every other outcome |

**The CTO's answers are the most valuable thing this run produces.** A person reads them weeks later
to learn why the product went this way, and nothing else records them. Write each one as the CTO
wrote it: the decision, what it beat, and the cost it accepted.

**Every exit writes the outcome entry and the assignee.** A hand-back, a defer, and an abort all run
`ticket-board`'s *Stopping without finishing* transition, so the next session reads the worklog and
learns where the task stopped and why. Then they all run Stage 9's **keep the record, discard the
code** procedure, whatever stage they stopped at — an unattended run must never leave half-built code
in the tree for the next task to commit.

## Workflow

### 0. Preflight — refuse to start on ground you cannot commit from
Check these first, in one parallel Bash batch, and stop before you spawn anything if one fails:

- **The docs root and the roadmap exist.** Resolve the root with `product-docs`. With no roadmap
  anywhere, outcome `blocked`, naming `/setup`.
- **Every candidate work root is a git work tree with nothing uncommitted in it.** Which repository
  this task lands in is not known yet, so check them all: `git -C <path> rev-parse
  --is-inside-work-tree` and `git -C <path> status --porcelain`, one pair per entry in the docs
  root's registry, in one parallel batch. In a repo-rooted run that is the session's own repository,
  and the registry is not read. Without git there is no per-task commit and no audit trail; with a
  dirty tree the task's `git add -A` would swallow changes it did not make. Either one is outcome
  `blocked`, naming the repository and what is wrong with it.
- **Every registered repository is reachable from this session.** A path that does not exist, or
  that this session cannot write to, is outcome `blocked` — name it, and name the fix: restart as
  `claude --add-dir <work root>`. An unattended run cannot grant itself access.

Report a `blocked` preflight in two lines and print the result line. Do not try to fix the ground.

### 1. Read the roadmap, collect the candidates, and let the CTO pick
`ticket-board` holds the roadmap's shape — one `## <CODE> — <epic name>` section per epic, one row
per task, and what an epic's `**Note**:` line and a `Depends on` cell mean.

- **Read every epic section**, not just the first: a dependency may name a task in another epic.
- **Collect every candidate** — every task that is **pending** with **all dependencies satisfied**.
- **The row does not say what the task delivers — its ticket does.** Open the ticket of every
  candidate and take its description and acceptance criteria from there.
- **No candidate at all** → outcome `no-work`. Say whether the roadmap is empty, or every pending
  task waits on something, and print the result line. Never invent a task.

Then spawn the CTO — **once**, and keep its id for the whole run:

```
Agent(subagent_type: "sdlc:cto", model: "opus",
      prompt: "Request: task-selection. You are answering in place of the user in an autonomous
               run — no person will be asked anything.
               Pick the next task to build, and call the end-to-end question."
              + the candidate list (ID, title, epic, description, acceptance criteria, Depends on)
              + any epic **Note**: lines
              + "Remaining on the roadmap: <N> tasks across <K> epics.")
```

It returns one `json` block with `taskId`, `rationale`, `e2e`, `skipped`, and the hand-back fields —
the shape is in the agent definition, do not restate it.

- `handBack: true` → outcome `handed-back`. Nothing has started, so there is no ticket to stop:
  report the reason and print the result line.
- A `taskId` that is not a candidate → ask **once** for a candidate ID. A second bad answer is
  `aborted` at stage `selection`.
- A non-empty `skipped` → carry each skipped task and its reason into the report, so a person can
  fix the ticket. Change nothing about those tasks.
- **Carry `e2e` forward as the `e2eDecision`**, the exact string the CTO returned. It goes in the
  Decisions block, in the opening worklog entry, and as one line in the Stage 2 scout prompt.

Track the stages with the task/todo tools, so the task's log shows live progress.

### 1.5 Resolve the work root
Resolve it as `product-docs` says, before anything is written and before any agent is spawned. One
entry in the registry answers it outright; several mean reading the design doc the ticket cites, the
ticket itself, the epic, and each entry's `what` line, and then looking inside the candidate
repositories for the code the task names.

**When the evidence still leaves it open, ask the CTO — never guess:**

```
Agent(subagent_type: "sdlc:cto", …resume the id from Stage 1…)
SendMessage(ctoId, "Request: work-root. Which repository is this task built in?"
                 + the ticket, its acceptance criteria, and its epic
                 + one line per candidate: code, path, and the registry's `what`
                 + what you already ruled out, and why)
```

It answers with one `workRoot` code, or with two when the task genuinely spans both. A
`handBack: true` here is outcome `handed-back` before the ticket starts, exactly as in Stage 1. This
ruling counts against the per-task budget like any other.

Then confirm the chosen repository is clean — `git -C <work root> status --porcelain` — even though
preflight checked it: a run that took minutes to pick a task may have found a tree that changed
under it. A dirty tree here is outcome `blocked`.

### 2. Start the ticket, then interview and scout concurrently
Run `ticket-board`'s **Starting a ticket** transition yourself, with the edits in one tool block.
Two values are this command's: the **assignee** is `feature-interviewer, implementation-planner`, and
the **opening worklog entry** is `run-roadmap · start` — the task, what it delivers, the work root
and the evidence that settled it, the `e2eDecision`, and the line that this is an autonomous run
whose decisions come from the `cto` agent.

Then issue **both `Agent` calls in one tool block**:

```
Agent(subagent_type: "sdlc:feature-interviewer", model: "opus",
      prompt: task block + acceptance criteria + roadmap and epic context)

Agent(subagent_type: "sdlc:implementation-planner", model: "opus",
      prompt: task block + acceptance criteria + roadmap context + the e2eDecision line
              + "SCOUT ONLY. A feature interview is running in parallel; its decisions are not
                 settled yet, so do NOT write the plan. Survey the codebase and research the
                 current best practice for this work now, reply with a few lines on what you
                 found, then end with your ```json block. Then stop and wait — I will send the
                 decisions and ask for the plan.")
```

**The interview always runs here.** `/orchestrate` may skip it on a trivially unambiguous task
because a person is there to catch what the skip missed. Nobody is here, the interview is what the
CTO rules on, and a task with no brief is a task whose assumptions nobody stated. The cost is one
agent on the critical path; take it.

The planner returns `contextPack` (relevant files, key symbols, conventions, `verificationCommands`,
`e2eCommand`) and a provisional `riskProfile` in one `json` block. Forward the `contextPack` into the
plan reviewer's, coding agent's, code reviewer's, and every verify agent's *first* message, so none
of them cold-explores the codebase.

Planner silent at either turn → `aborted` at stage `plan`. Interviewer silent → `aborted` at stage
`interview`; do not plan without a brief.

### 3. The CTO settles the decisions
Resume the same CTO — do not spawn a second one:

```
SendMessage(ctoId, "Request: decisions. The feature interview came back. Settle every open
                    decision, rule on every assumption, and confirm or change the out-of-scope
                    list. The e2e call you already made is <e2eDecision> and stands."
                 + the full Discovery Brief)
```

It returns `decisions`, `assumptions`, `outOfScope`, `scopeChange`, and the hand-back fields.

- `handBack: true` → outcome `handed-back`. Run *Stopping without finishing*, with the outcome entry
  naming the decision the CTO would not make and why.
- **Write the Decisions block onto the ticket file**, holding every choice with its rationale, the
  assumption rulings, the out-of-scope list, and the `e2eDecision`. It is durable; the session is not.
- In the **same tool block**: append the `feature-interviewer · interview` entry — what the brief
  challenged and where the Decisions now live, not a copy of them — then the `cto · decisions` entry,
  which carries each choice and the reason it won. Set the assignee to `implementation-planner`.
- A non-empty `scopeChange` → the revised task is what gets built. Use it in the planner's message
  and in the commit message, and say so in the report.

### 4. Plan, then the review gate
Resume the planner:

```
SendMessage(plannerId, the Decisions
                     + "Decisions are settled — treat them as fixed constraints. Write the full
                        Implementation Plan now from the files and research you already have;
                        explore again only where a decision opened something you did not cover.
                        Re-emit your ```json block, updating any value the decisions changed.")
```

**Pre-warm the reviewer while the plan is being written.** Judge from the provisional `riskProfile`
whether a review is likely, and if so spawn the reviewer(s) in **pre-read only** mode — the same
prompt `/orchestrate` uses, carrying the task, the criteria, the Decisions, and the context pack, and
ending with "Do NOT issue a verdict yet."

**Then apply the gate mechanically** on the *final* `riskProfile` that came back with the plan:

- **Skip review** iff `filesTouched ≤ 2` **and** `addsDependency == false` **and**
  `addsPublicApi == false` **and** `criteriaAutoCheckable == true`. Log "Review gate: SKIPPED" and go
  to Stage 5 with the plan as approved.
- Otherwise **review is required**, and it is **high-risk** iff `addsPublicApi == true` **or**
  `addsDependency == true` **or** `filesTouched > 5`.
  - **Normal risk** → **one** reviewer, `model: "sonnet"`.
  - **High risk** → **two** reviewers in one tool block, `model: "opus"`, with distinct lenses:
    (a) correctness and completeness against the acceptance criteria; (b) codebase fit — conventions,
    dependency rules, architectural boundaries. Keep both ids.

Hand the plan over with `SendMessage(reviewerId, "Review the plan below against the checklist. You
have already read the context pack files; re-read only what the plan points at that you have not
seen." + plan)` — both reviewers in one tool block when there are two.

Merge multiple verdicts: `CHANGES_REQUESTED` if **any** reviewer requests changes; concatenate the
issues. Every reviewer silent → `aborted` at stage `review`.

- `APPROVED` → append the plan and plan-review entries and set the assignee to `coding`, in one tool
  block, then Stage 5. The plan entry carries the **direction** the plan settled on and the approach
  it turned down; the plan markdown is not persisted anywhere else.
- `CHANGES_REQUESTED`, **not yet revised** → `SendMessage(plannerId, "Revise your plan to resolve
  every issue below. Note in the Context section how each was addressed. Re-emit the full plan
  markdown + the ```json block." + issues)`, then re-review through the same reviewer(s).
- `CHANGES_REQUESTED`, **already revised once** → **ask the CTO** (Stage 7's ruling procedure) with
  stage `review`.

### 5. Implement
Spawn **once** and keep the id:

```
Agent(subagent_type: "sdlc:coding", model: "opus",
      prompt: "Implement the approved plan exactly — no scope creep. Match the context pack
               conventions. Targeted self-check only when you are done; the verify stage runs
               the full gate."
              + approved plan + contextPack + acceptance criteria + the Decisions)
```

It ends every turn with `summary`, `workItemsCompleted`, `filesChanged`, `decisions`, and `blockers`.
Silent → `aborted` at stage `implement`. Non-empty `blockers` → **ask the CTO** with stage
`implement`.

When it lands, append the `coding · implement` entry — its `decisions`, the code-level calls the plan
left open — and set the assignee to `verify, code-reviewer`, in one tool block before you spawn them.

### 6. Verify and review the code — concurrent, one fix cycle
Issue **both `Agent` calls in one tool block**. Verify is fresh every run; the code reviewer is
spawned once and resumed.

```
Agent(subagent_type: "sdlc:verify", model: "sonnet",
      prompt: "Run these verification commands CONCURRENTLY (one parallel Bash batch).
               Report pass/fail per command."
              + verificationCommands and e2eCommand from the context pack + the Decisions
              + (re-runs only) "Previously failing commands: <failures> — run these first and fail fast.")

Agent(subagent_type: "sdlc:code-reviewer", model: <opus on high risk, else sonnet>,
      prompt: "Review the change the coding agent just made, against the approved plan and the
               acceptance criteria. Verification is running in parallel — do not run the suite."
              + approved plan + acceptance criteria + Decisions + contextPack
              + the coding agent's filesChanged + the review target ("the uncommitted changes
                against HEAD, untracked files included"))
```

**Pass `e2eCommand` every time, including the literal `"none"`** — that is what stops the verify
agent globbing for `playwright.config.*`/`cypress/`/`e2e/` on every spawn. Unlike
`/orchestrate-quick`, this pipeline **runs the end-to-end suite inside the gate** when the project
has one: there is no user at the end to ask, and an unattended commit must not rest on a suite
nobody ran.

**The code review has no skip gate**, and its model follows the same high-risk test as Stage 4.

**Combine both results into one gate:**

- Either agent silent → `aborted` at stage `verify` or `code-review`.
- `passed == true` **and** `verdict == APPROVED` → success, go to Stage 8. A `skipped` result still
  succeeds, but name the command and the reason in the report and the worklog — **never record a
  skipped command as green**. Minor review issues become recommendations in the report; they do not
  block.
- Anything else, **not yet fixed** → one message carrying both sets of defects:
  `SendMessage(codingId, "Verification and code review found the following. Fix ONLY what is needed
  to clear them — stay within the approved plan, then stop; both will re-run." + failures + blocking
  review issues)`. Then re-run: **always** a fresh verify agent, carrying the previously failing
  commands; re-review **only when the review blocked**. Both in one tool block.
- Anything else, **already fixed once** → **ask the CTO** with stage `verify` when commands still
  fail, `code-review` when only the review still blocks.

### 7. Ask the CTO for a ruling — the procedure every cap runs into
This replaces every `escalate` in `/orchestrate`. Before you ask, check the caps: a **second** ruling
at this stage, or a **third** on this task, is not a question — it is outcome `handed-back`.

```
SendMessage(ctoId, "Request: escalation. Stage <stage> hit its cap."
                 + what the stage reported (issues, failures, or blockers)
                 + what was already tried (the revision or the fix cycle, and what it changed)
                 + "Rulings already given on this task: <list, or none>.")
```

Append the `cto · ruling` worklog entry for every ruling, whatever it says, then act:

| Ruling | What you do |
| --- | --- |
| `retry` | One more cycle at that stage, with the CTO's `guidance` in the message to the agent that owns it. The stage's cap is now spent — a second failure is `handed-back` |
| `rescope` | `SendMessage` the planner or the coding agent with the narrowed task, finish it, and in the Stage 8 edit **add the dropped part to the roadmap** as a new pending task with its own ticket, per `ticket-board`. Say what came out, in the report and the worklog |
| `defer` | Outcome `deferred`. Run *Stopping without finishing*, then Stage 9's **keep the record, discard the code** procedure. The next task starts from a clean tree, and the ticket keeps everything that was learned |
| `stop-run` | Outcome `stop-run`. The same as `deferred` for this ticket, and the result line tells the script not to start another task |
| `handBack: true` | Outcome `handed-back`, whatever the ruling field says. A person decides |

### 8. Finish the ticket (only on success)
Run `ticket-board`'s **Finishing a ticket** transition yourself, in one tool block: the status field,
the closing worklog entries, the move into `done/`, and the roadmap row deleted. This command's
closing entry is `run-roadmap · done`, and the worklog also takes the verification and code-review
entries.

Do this **before** the commit. When the docs root sits inside the work root's git tree, the ticket
move and the roadmap edit then land in the task's own commit. When it does not — a vault, or a folder
outside the repository — the documents are already saved and the commit below covers the code alone.

Never finish the ticket unless verification passed **and** the code review returned `APPROVED`.

### 9. Commit the task
One commit per finished task, so `git log` holds the run as a sequence of changes a person can read.

1. `git -C <work root> add -A`, then one commit in the same repository. The tree was clean at
   preflight, so everything staged belongs to this task: the code, and — when the docs root sits
   inside this tree — the ticket in its new folder, the worklog, and the roadmap edit.
2. **Match that repository's own commit convention.** Read `git -C <work root> log --oneline -20`
   and follow what is there — a Conventional Commits prefix, a ticket ID in the subject, whatever
   the repository does. With no discernible convention, use `<ID>: <title>`. Two work roots may hold
   two different conventions; each commit follows the one in its own tree.
3. The body is three or four lines: what landed, the decision the CTO made that shaped it, and the
   verification result. `clean-writing` governs it.
4. **Never push, never branch, never amend, and never touch a commit that was already there.** The
   run adds commits to the current branch and nothing else.
5. A commit that fails — a hook rejects it, or there is nothing to commit — is outcome `blocked`.
   Say what the hook said, and leave the tree as it is for a person to look at. Do not retry with
   `--no-verify`.
6. **A docs root that is its own git tree gets its own commit**, in its own repository, with the same
   subject. A docs root in a vault is no git tree: nothing to commit, and nothing to report but the
   files written.
7. **A task that spanned two work roots gets one commit in each**, same subject, each body naming the
   other repository. Report both shas.

**Keep the record, discard the code** — the exit every unfinished task takes: `deferred`,
`stop-run`, `handed-back`, and `aborted` alike, once a ticket has been started. Half-built code must
not be committed, the ticket's record must survive, and the next invocation has to start from a clean
tree. That is three requirements and one order of operations:

1. Write the *Stopping without finishing* edits first — the status, the assignee `user`, and the
   outcome worklog entry.
2. **Stage only the record**: `git -C <work root> add <docs root>` and the ticket's own path —
   only when the docs root sits inside that tree. A docs root in a vault is already saved and is
   never staged.
3. `git -C <work root> checkout -- .` then `git -C <work root> clean -fd`. Both leave staged content
   alone, so this discards exactly the code and keeps exactly the record. Run the pair in every work
   root the task touched.
4. Commit it, with a subject naming the task and the outcome — `<ID>: deferred by cto` — and the
   CTO's reason in the body. A person reading `git log` sees why the run stopped here.
5. Confirm the tree is clean with `git -C <work root> status --porcelain`. It has to be empty; the script stops the
   whole run when a task leaves work behind.

Say plainly in the report that the code was discarded and the record kept, so nobody goes looking for
a half-finished branch.

### 10. Report, then print the result line
The report is short — a person reads a hundred of these in a log, not one on a screen:

```markdown
## [ID] — [Title] · [outcome]

- [x] Task chosen by cto — [the rationale, one line]
- [x] Interview — [N] decisions settled by cto
- [x] Planning — approved ([0 or 1] revision, or: review gate skipped)
- [x] Implementation — [N] files
- [x] Verification — passed ([the commands], or: [what was skipped and why])
- [x] Code review — approved
- [x] Work root — [code] `[absolute path]`
- [x] Commit — [sha] [subject]
- [x] Status — ticket Completed and moved to `done/`, roadmap row deleted

[Two or three lines: what shipped, and the decision that shaped it.]
[Any skipped candidate and its reason. Any recommendation nobody acted on.]
```

Then, as the **last line of your final message and nothing after it**, print exactly one result line.
The launcher script parses it to decide whether to start another task:

```
RUN-ROADMAP-RESULT {"outcome":"completed","taskId":"AUTH-002","commit":"a1b2c3d","workRoots":["/Users/me/Projects/acme-api"],"remaining":4,"nextAction":"continue","reason":""}
```

One line, valid compact JSON, no code fence, no text after it. The fields:

| Field | Value |
| --- | --- |
| `outcome` | `completed`, `deferred`, `handed-back`, `aborted`, `stop-run`, `no-work`, or `blocked` |
| `taskId` | The task this invocation worked on, or `""` when none was started |
| `commit` | The short sha, or `""` when nothing was committed. Two repositories give two shas, joined by a comma |
| `workRoots` | Every repository this invocation wrote to, as absolute paths. `[]` when none was started. The script checks these trees between tasks |
| `remaining` | Tasks left on the roadmap **after** this invocation, counted from the file you just wrote |
| `nextAction` | `continue` or `stop` |
| `reason` | One short sentence on a non-`completed` outcome, `""` otherwise. No newline, no quote character |

**`nextAction` follows from `outcome`, mechanically:**

| Outcome | What happened | `nextAction` |
| --- | --- | --- |
| `completed` | The task shipped and was committed | `continue`, or `stop` when `remaining` is 0 |
| `deferred` | The CTO ruled `defer`; the ticket waits for a person | `continue` — the roadmap has other work |
| `handed-back` | The CTO set `handBack`, or a cap ran out of rulings | `stop` |
| `aborted` | An agent returned nothing usable after one retry | `stop` |
| `stop-run` | The CTO ruled that the run must end | `stop` |
| `no-work` | No pending task has its dependencies satisfied | `stop` |
| `blocked` | Preflight or the commit failed — the ground is wrong | `stop` |

`clean-writing` governs the report. **It does not govern the result line**, which is data: keep the
keys, the order, and the spelling exactly as above.

## Rules
The four skills carry the rules they own. What is this command's own:

- **One task per invocation.** Never loop over the roadmap in one session. The script does that.
- **Never call `AskUserQuestion`, and never write a sentence that waits for an answer.** Ask the
  CTO, or hand back.
- **The CTO decides; you execute and record.** Never answer a product question yourself, and never
  overrule the CTO — but never let it past a failing gate either. A test result and a review verdict
  are not product decisions.
- **Every cap is hard**, and the CTO's `retry` buys exactly one cycle. No improvised extra pass.
- **Resolve the work root before the ticket starts**, record it in the worklog, pass it to every agent, and name it in the result line. Never let an agent infer which repository it is working in.
- **You write the status, the assignee, the worklog, the roadmap, and the commit.** No agent writes
  any of them.
- **Never finish a task unless verification passed and the code review approved.**
- **One commit per task, on the current branch. Never push.**
- **A clean tree in, a clean tree out.** A finished task is committed; an unfinished one keeps its
  record and discards its code, by Stage 9's procedure. Either way the next invocation starts on a
  clean tree, because the script stops the run when it does not.
- **The result line is the interface.** Print it on every path, including a preflight failure, and
  print nothing after it.
