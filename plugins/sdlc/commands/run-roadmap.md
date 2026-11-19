---
description: "Builds the next ticket of an unattended roadmap run: the cto agent answers every question, the code is committed on the run branch in a run worktree, and a result line reports the outcome. Use when the run-roadmap launcher starts a session."
argument-hint: "[--run run-roadmap-<n>] [--project <name>] [--final] [roadmap-file-path]"
disable-model-invocation: true
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
  registered repository uses — `board.py next-run --command run-roadmap` prints it.
- **`--project <name>`** — the project the run builds, by the `name` in its project note. The
  launcher passes it whenever it knows the project; it settles the project before anything else, as
  `sdlc-structure` resolves it. Every work root the run builds in is one the registry lists for
  this project, or one that lists no project.
- **`--final`** — this is the run's last ticket: whatever the outcome, release the run's claims
  before the result line. The launcher passes it when `--max` is about to be reached. A session
  started by hand, with no `--run`, is final too.
- **A roadmap file path**, when given, is the roadmap to read.

This is `/orchestrate` with the human replaced. The stages and the gates are the same;
what changes is who answers, what is claimed, where the code is built, what happens when a stage is stuck, and
that the session ends in commits and a parsable result. One invocation is one ticket of the
feature the run holds — the loop over the feature's tickets and over the roadmap belongs to [`scripts/run-roadmap.sh`](../scripts/run-roadmap.sh), which starts a
fresh session per ticket so a long roadmap never runs out of context. The design is
`designs/workflow.design.md`, sections 3 and 6.1, and `diagrams/run-roadmap.excalidraw.md` draws it.

**Nobody is watching this run.** That is the one fact that shapes every rule below: no
`AskUserQuestion`, a commit per ticket on a branch of its own so `git log` is the audit trail, and
`human_required` as the only thing that ends the run early.

## Before you start

[The command preamble](../skills/agent-pipeline/references/command-preamble.md) holds the four skills this command loads and when, the namespacing rule, the `technical-writing` rules, the board rules, and the failure rules. Read it first. Here `technical-writing` governs what a person reads later — the worklog, the commit message, and the report — and nobody reads anything live. The stages from Plan to Code review and full verification are the **full mode** of [the build stages](../skills/agent-pipeline/references/build-stages.md).

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
  when the framework root is a git tree. Stage 7 holds both.

## The one rule that makes this command different

**Never call `AskUserQuestion`. Not once, at any stage, for any reason.** There is no person on the
other end of this session, so a question is a hang, and a hang inside an unattended loop burns the
whole run.

Every question goes to the `cto` agent, which answers in the user's place:

| What `/orchestrate` asks the user | Who answers here |
| --- | --- |
| Which candidate ticket to build — or that it cannot run | `cto`, request `feature-selection`, which picks a feature instead |
| Whether the ticket gets end-to-end tests | `cto`, in the same `feature-selection` answer, once for the feature |
| A fork the ticket's documents leave open, which the planner names | `cto`, request `decisions` |
| Nothing — it stops on `human_required` | `cto`, request `ruling`, first |

When the CTO sets `humanRequired: true`, **that** is the moment a person is needed. Stop, run
`ticket-board`'s *Stopping without finishing* transition once a ticket has started, and report the
outcome `human_required`. Do not try to answer that question yourself.

## Architecture: the interactive shell, driven by an agent

```
  YOU (main loop)
  ─────────────────────────
  preflight ─► select: a feature this run claims, else the candidate features ─► Agent(cto) pick + e2e
  ─► claim the feature's dependency cluster ─► read back  (lost ─► select again)
  ─► choose the feature's next ticket ─► identify the work roots ─► run worktree per work root (once per run) ─► start the ticket
  ─► the build stages, in the run worktrees, with the cto as the answerer
        [openQuestions] SendMessage(cto, decisions)   [stuck, blocker, spec-question] SendMessage(cto, ruling)
  ─► finish the ticket ─► commit the code (run branch) ─► commit the documents (framework root)
  ─► report + RUN-ROADMAP-RESULT
```

### Which agents are persistent
The build stages name their persistent roles, and this command adds the **cto**. Keep every id.

**The `cto` is spawned once and resumed for every question in this invocation.** It reads the PRD and
the design docs on its first turn; re-spawning it throws that away and invites an answer that
contradicts the one before it.

## One stop: `human_required`

The command preamble's failure rules hold: no count ends a loop, and `human_required` is the only
thing that ends this run early.

**Ask the CTO first when a person would decide**: a stage that is stuck, a blocker, and a question
about the specification go to Stage 5, and `human_required` follows only when the CTO sets
`humanRequired`. A dead agent and wrong ground go straight to `human_required`.

One ticket per invocation is how the run is built, not a limit: print the result line and stop, and
the script starts the next ticket.

## The worklog, the assignee, and the commit

`ticket-board` holds the worklog's shape, and the command preamble holds the board rules. The CTO
is no exception: it reports its decisions to you, and you write them down.

**The entry, the status, and the assignee go in one tool block.** `<n>` is the run's number, so
`coding-3` works for `run-roadmap-3`. The build stages hold the boundaries from the plan to the code
review, with `<claim>` as the run name; this command's own are:

| Boundary | Entries to append | `status` · `assigned` becomes |
| --- | --- | --- |
| Stage 2, starting the ticket | the worklog itself, with the `<run name> · start` entry | `in progress` · `implementation-planner-<n>` |
| Every CTO ruling | `cto · ruling` — the stage, the ruling, and the guidance | unchanged |
| Stage 6, finishing the ticket | `<run name> · done` | `done` · removed |

**The CTO's answers are the most valuable thing this run produces.** A person reads them weeks later
to learn why the product went this way, and nothing else records them. Write each one as the CTO
wrote it: the decision, what it beat, and the cost it accepted. The answers to the planner's open
questions go in the plan entry; every ruling gets an entry of its own.

**Every exit writes the outcome entry**, as the preamble says. A `human_required` then runs Stage
7's **keep the record, discard the code** procedure, whatever stage it stopped at — an unattended run must never leave half-built code
in the run worktree for the next ticket to commit.

## Workflow

### 0. Preflight — refuse to start on ground you cannot build on
Check these first, in one parallel Bash batch, and stop before you spawn anything if one fails:

- **The framework root and its roadmap exist.** Resolve them with `sdlc-structure`. With no roadmap
  anywhere, outcome `human_required`, naming `/setup`.
- **Every registered repository is a git work tree.** `git -C <path> rev-parse
  --is-inside-work-tree`, one per entry in the registry, in one batch. In a repo-rooted run that is
  the session's own repository, and the registry is not read. Without git there is no run branch and
  no audit trail: outcome `human_required`, naming the repository. **A dirty checkout is not a failure** —
  the run builds in its own worktree, from the checkout's last commit.
- **Every registered repository, and the folder its worktrees go in, is reachable from this
  session.** A path that does not exist or that this session cannot write to is outcome `human_required` —
  name it, and name the fix: restart with `--add-dir` for it. An unattended run cannot grant itself
  access.
- **The run's own worktrees, when they exist, are clean.** `git -C <worktree> status --porcelain`
  for each one a `--run` already made. Work left there is a ticket that neither committed nor
  discarded: outcome `human_required`, naming the worktree.

Report a failed preflight in two lines and print the result line. Do not try to fix the ground.

### 1. Select the next feature — can it run?
`ticket-board` holds the roadmap's shape — one `## <CODE> — <epic name>` section per epic, one row
per ticket, and what an epic's `**Note**:` line and a `Depends on` cell mean — and how a roadmap
run selects. An epic is the tickets of one feature, so **a feature on the roadmap is its epic
section**. Reading a table top to bottom reads it in the order it should be built.

- **In an unattended run, rebuild the roadmap first.** Nobody is there to notice a stale row, so run
  `${CLAUDE_PLUGIN_ROOT}/scripts/build-roadmap.py --project <project>` and put what it reported into
  the opening worklog entry. Skip it when `python3` is missing, and say so in the report.
- **Then run `board.py ready --features --run <run name> --project <project>`**, as `ticket-board`
  says. It applies the two rules below and returns `claimedByRun`, the `candidates` with each
  cluster in build order and its `next` ticket, the `excluded` features with what each waits on, and
  `remaining`. Apply the rules by hand only when `python3` is missing.
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
  **Tickets left and no candidate feature** → outcome `human_required` with the tickets left in
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

Act on its block:

- `humanRequired: true` → **it cannot run**: outcome `human_required`. Nothing has started, so there is no
  ticket to stop: report the reason and print the result line.
- A `featureCode` that is not a candidate → ask again, naming the candidates.
- A non-empty `skipped` → carry each skipped feature and its reason into the report, so a person can
  fix it. Change nothing about its tickets.
- **Confirm automatically.** Where `/orchestrate` asks the person to confirm the pick, the CTO's pick
  stands. **Carry `e2e` forward as the `e2eDecision`**, the exact string the CTO returned. It holds
  for every ticket of the feature.

Track the stages with the task/todo tools, so the session's log shows live progress.

### 1.2 Claim the feature's dependency cluster — is the claim held?
Write `claimed: <run name>` on **every** ticket of the selected feature's cluster and read every one
back: `board.py claim --run <run name> <every cluster ID>`. `ticket-board` holds the claim's rules.

- **Every claim reads back as this run's** → held. Go to Stage 1.3.
- **Any one reads back as another run's** → lost. The script has already removed the claims this
  attempt wrote. Go back to Stage 1 with the candidates collected again. Resume the same CTO, and tell it
  which ticket of which feature was lost.

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
- **`settled: false`** → outcome `human_required`: nobody is here to choose, and building in the wrong
  repository costs the whole pipeline. Report the candidates it named, so a person can fill
  `repositories` and resume. Release the cluster's claims first, as every end does.
- Silent → `human_required` at stage `repositories`.

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
folder is not writable — is outcome `human_required`, naming the repository and git's error. **Remove this
run's claims on the whole cluster first**, as every end does. A worktree that exists but is not clean
is `human_required` the same way.

### 2. Start the ticket
**Pick up the ticket to build**: run `ticket-board`'s **Starting a ticket** transition yourself,
with the edits in one tool block. The claim is already written, so it stays. Two values are this
command's: `assigned` is `implementation-planner-<n>`, and the **opening worklog entry** is
`<run name> · start` — the ticket, what it delivers, the feature the run holds and the cluster it
belongs to, every run worktree with its branch and the evidence that settled each work root, the
`e2eDecision`, and the line that this is an autonomous run whose answers come from the `cto` agent.

**The decisions were made before the run.** `/plan` interviewed a person and wrote each settled
choice into the ticket's `Decisions`, the feature note, and its design docs. This run holds no
interview: the planner reads those documents, and only a fork they leave open reaches the CTO.

### 3. Build the ticket — the build stages
Run every stage of `agent-pipeline`'s `references/build-stages.md`, from Plan to Code review and full
verification, in **full mode**, as this command's own text. What this command supplies:

- **`<claim>`** is the run name, and the run folder is `<framework root>/.runs/<run name>/`.
- **The work root** is the run worktree of each work root Stage 1.5 identified — never the person's
  checkout.
- **Prompt additions:** the ticket's `Decisions` in the first prompt of every agent, as fixed
  constraints; the design docs' paths for the test planner; and each CTO answer for the coding agent.
- **The answerer** is the CTO: questions go to Stage 4, and a ruling to Stage 5.
- **The end-to-end suite runs inside the full verification** when the `e2eDecision` says yes: there is
  no person at the end to ask, and an unattended commit must not rest on a suite nobody ran.

### 4. The CTO answers the planner's questions
On a question turn, resume the same CTO — do not spawn a second one:

```
SendMessage(ctoId, "Request: decisions. The planner read the ticket's documents and the code, and
                    these forks are still open. Answer each one. The ticket's Decisions are fixed,
                    and the e2e call you already made is <e2eDecision> and stands."
                 + every entry of openQuestions — its id, question, options with their cost,
                   and the planner's recommendation with why)
```

The plan reviewer's pre-read goes out in the same tool block, as the build stages say. Act on the
CTO's block:

- `humanRequired: true` → outcome `human_required`: the ticket goes back to planning with a person.
  Run *Stopping without finishing*, with the outcome entry naming the question the CTO would not
  settle and why.
- Otherwise the answers go back to the planner as the build stages say. Keep them for the plan entry.

### 5. Ask the CTO for a ruling — the procedure every stuck stage runs into
This replaces `human_required` in `/orchestrate` wherever a person would decide what happens next:

```
SendMessage(ctoId, "Request: ruling. Stage <stage> needs a decision."
                 + what the stage reported (issues, failures, blockers, or the question)
                 + what was already tried (the revisions or the fix cycles, and what they changed)
                 + "Rulings already given on this ticket: <list, or none>.")
```

The stage is one of the names the build stages list. Append the `cto · ruling` worklog entry for every
ruling, whatever it says, then act:

| Ruling | What you do |
| --- | --- |
| `retry` | Go on at that stage, with the CTO's `guidance` in the message to the agent that owns it |
| `rescope` | `SendMessage` the planner or the coding agent with the narrowed ticket, finish it, and in the Stage 6 edit **add the dropped part to the roadmap** as a new `backlog` ticket, per `ticket-board`. Say what came out, in the report and the worklog |
| `humanRequired: true` | Outcome `human_required`, whatever the ruling field says. Run *Stopping without finishing*, then Stage 7's **keep the record, discard the code** procedure. A person decides how the feature goes on |

### 6. Finish the ticket (only on success)
**Commit the code first**, by Stage 7's code-commit steps. A ticket is `done` only once its code is
on the run branch: a commit a hook rejects stops the ticket here instead, as Stage 7 says, and this
stage never runs.

Then run `ticket-board`'s **Finishing a ticket** transition yourself, in one tool block: the status field,
the closing worklog entry, the move into `done/`, the roadmap row deleted, and the run folder deleted. This command's closing
entry is `<run name> · done`, and it names each note file. In the same step, write the coding agent's
latest `notes` with `create-note.py`, as `agent-pipeline` says, with `--run <run name>`. A note is
never a reason to stop: the run goes on, and a person acts on the note later.

Do this **before** the documents commit, so that commit holds the ticket in `done/`.
The ticket's claim goes with it — the rest of the cluster keeps this run's claim.

Never finish the ticket unless the feature's tests passed, **all four** code reviewers returned
`APPROVED`, **and** every check of the full verification passed.

### 7. Commit the code, then the documents
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
5. A commit that fails — a hook rejects it — is outcome `human_required`. The ticket has not finished: run
   *Stopping without finishing*, with `blocked_by` naming the hook and what it said, then commit
   the documents. Leave the worktree as it is for a person to look at. Do not retry with
   `--no-verify`.

**Commit the documents in the framework root**, when it is a git tree: `git -C <framework root> add`
the ticket, its worklog, every roadmap the ticket's row was in, any ticket Stage 6 corrected, and
each note file `create-note.py` reported as `created` —
those paths only, because the person may have their own changes there — then one commit with the
code commit's subject. A framework root in a vault that is no git tree has nothing to commit: the
files are saved, and the report says so.

**A documents commit that fails is outcome `human_required`**, and the ticket stays as it is: its code
commit has landed and its files are already written, so nothing is undone. Say what git said, leave
the framework root's changes uncommitted for a person, and never retry with `--no-verify`.

**Keep the record, discard the code** — the exit every `human_required` ticket takes, and a rejected
commit's ticket once a person has looked.
Half-built code must not be committed, the ticket's record must survive, and the next session has
to start from a clean worktree:

1. Write the *Stopping without finishing* edits first — the status, `blocked_by`, the assignee
   removed, and the outcome worklog entry.
2. **Release the run's claims** on every ticket of the cluster that is not `done`, once those edits
   have landed: `board.py release --run <run name>`. Every end of a roadmap run does this.
3. `git -C <worktree> reset --hard` then `git -C <worktree> clean -fd`, in every run worktree the
   ticket touched. The worktree is the run's own, so this discards exactly the ticket's code and
   nothing of the person's.
4. Commit the documents in the framework root, as above, with a subject naming the ticket and the
   outcome — `<ID>: human_required` — and the reason in the body.
5. Confirm every worktree is clean with `git -C <worktree> status --porcelain`. The script ends the
   run when a ticket leaves work behind.
6. Delete the run folder in the framework root.

**On `--final`**, release the run's claims the same way after a completed ticket too, so no claim
outlives the run.

Say plainly in the report that the code was discarded and the record kept, and that the branch and
the worktrees stay for the resume.

### 8. Report, then print the result line
The report is short — a person reads a hundred of these in a log, not one on a screen:

```markdown
## [ID] — [Title] · [outcome]

- [x] Feature chosen by cto — [the rationale, one line]
- [x] Planning — [N] open questions answered by cto (or: none); approved ([N] revisions, or: review gate skipped)
- [x] Test plan — [N] cases, [M] left untested on purpose (or: no case — [why])
- [x] Tests written first — [N] failing before the code; [K] sharpened, [P] still passing and recorded
- [x] Implementation — [N] files; [N] test disputes ([rulings])
- [x] Feature's tests — passed, [N] files across [M] tickets ([N] fix cycles; [what was skipped and why])
- [x] Code review — correctness, conventions, security, tests approved ([N] fix cycles)
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
| `outcome` | `completed`, `human_required`, or `no-work` |
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
| `human_required` | A person must act: the CTO set `humanRequired`, an agent died, tickets are left and none can be selected, or preflight, a worktree, or a commit failed | `stop` |
| `no-work` | No ticket left (`remaining` 0) | `stop` |

`technical-writing` governs the report. **It does not govern the result line**, which is data: keep the
keys, the order, and the spelling exactly as above.

## Rules
The four skills carry the rules they own, and the command preamble the rules every orchestrator
shares. What is this command's own:

- **One ticket per invocation.** Never loop over the roadmap in one session. The script does that.
- **Never call `AskUserQuestion`, and never write a sentence that waits for an answer.** Ask the
  CTO, or raise `human_required`.
- **The CTO decides; you execute and record.** Never answer a product question yourself, and never
  overrule the CTO — but never let it past a failing gate either. A test result and a review verdict
  are not product decisions.
- **The build stages are the rules from Plan on**: the gates, the tests before the code, and the
  code review from four focuses. The CTO settles what the specification means; it never tells the
  coding agent to change a test.
- **Work one feature at a time.** Claim its whole cluster before anything else is written, build every ticket of it before selecting another feature, and release the claims at every end.
- **Build only in the run worktrees.** Create them before the ticket starts, record them in the worklog, pass them to every agent as the work root, and name them in the result line. Never let an agent infer which repository it is working in, and never write to the person's checkout.
- **You write the commits**, as well as the board. No agent writes either.
- **You run every check.** Every new test, the feature's tests, and the full verification run in your
  own Bash calls, in the run worktree. No agent's report of a passing check counts.
- **Never finish a ticket unless the feature's tests passed, all four code reviewers approved, and
  every check of the full verification passed.**
- **One code commit per ticket, on the run branch; one documents commit in the framework root. Never push, never merge.**
- **A clean worktree in, a clean worktree out.** A finished ticket is committed; an unfinished one
  keeps its record and discards its code, by Stage 7's procedure, and the run ends. Either way the
  next invocation starts on a clean worktree, because the script stops the run when it does not.
- **The result line is the interface.** Print it on every path, including a preflight failure, and
  print nothing after it.
