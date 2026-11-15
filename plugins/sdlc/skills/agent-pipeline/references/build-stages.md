# The build stages

The stages `/orchestrate` and `/run-roadmap` both drive, from Plan to Code review and full
verification. The command around them picks the ticket, starts it, answers what a person would
answer, and finishes it. Read this file whole before Plan, and follow it as the command's own text.

## What the command supplies

- **`<claim>`** — the run's claim, `orchestrate-<n>` or `run-roadmap-<n>`. `<n>` is in every agent's
  `assigned` value: `coding-2` works for `orchestrate-2`. Your own worklog entries name the claim.
- **The work root** — the repository the ticket is built in, or the run worktree that stands in for
  it in `/run-roadmap`. Every prompt carries it as an absolute path, and every check runs there, as
  `cd <work root> && <command>`. A ticket built in two work roots runs the feature's tests, the code
  review, and the full verification once per work root, and passes only when every one passes.
- **The `e2eDecision`** — settled before Plan, as `"E2E: yes, critical path only"` or
  `"E2E: no — unit and integration only"`.
- **Prompt additions** — lines the command adds to the first prompt of some agents, such as the
  ticket's `Decisions`.
- **The answerer** — who settles what the pipeline cannot. The stages below send it two kinds of
  request:
  - **Questions** — the planner's `openQuestions`, on a question turn. Plan says what to do with the
    answers.
  - **A ruling** — on a stage that is stuck, as `agent-pipeline` defines it, on a blocker, and on a
    `spec-question`. The answerer either returns guidance, and the run goes on at that stage with the
    guidance in the message to the agent that owns it — guidance that must differ from what already
    failed — or it raises `human_required` with the stage.

  A turn that returns nothing is never the answerer's: it is `human_required` with the stage.

## The worklog and the assignee

**The entry and the assignee go in one tool block**, at these boundaries. The command adds the rows
for Start, its own answers, Finish, and every stop.

| Boundary | Entries to append | `status` · `assigned` becomes |
| --- | --- | --- |
| The plan lands | `implementation-planner · plan` | `plan-reviewer-<n>`, or `test-planner-<n>` when the risk gate skips the review |
| The plan review approves | `plan-reviewer · plan review` | `test-planner-<n>` |
| The test plan lands | `test-planner · test plan` | `test-writer-<n>`, or `coding-<n>` when it holds no case |
| The tests land | `test-writer · tests` | unchanged |
| Every new test has been run | `test-writer · tests` again when a sharpen turn changed a file or a command, then `<claim> · new tests` | `coding-<n>` |
| The implementation lands | `coding · implement` | unchanged |
| A test dispute goes out | none | `test-planner-<n>` |
| The rulings land | `test-planner · test dispute`, then `test-writer · tests` when a test was revised | `coding-<n>` |
| The feature's tests pass | `<claim> · feature tests` | `review` · `code-reviewer-<n>` |
| The code review and the full verification land | `code-reviewer · code review`, one per focus that reviewed, then `<claim> · verification` | a defect in either: `in progress` · `coding-<n>`; both pass: unchanged |

A `test-writer · tests` entry ends with its test record, as `ticket-board` shows it. **The feature's
later tickets run their tests from that record**, so it must name what is on disk now.

## The shape of the run

```
  ┌ Agent(planner) ─► contextPack + plan + riskProfile, or openQuestions ─┐  concurrent
  └ Agent(test-planner) "SPEC ONLY" ─► draft cases ───────────────────────┤
     [openQuestions] the answerer ─► SendMessage(planner, answers) ─► plan
                     └ Agent(reviewer) "PRE-READ ONLY" (context pack), same tool block
  [risk low ─► skip review]  reviewer(s) ─► verdict
        ▲                                 │ CHANGES_REQUESTED
        └── SendMessage(planner, issues) ◄┘  (revise and re-review until approved)
  SendMessage(test-planner, plan + pack) ─► test plan ─► [no case: skip to coding]
  Agent(test-writer) ─► tests + a command per case ─► fingerprint them
  YOU run each new case ─► passes or does not run ─► SendMessage(test-writer)  (sharpen until it fails)
  Agent(coding) ─► [fingerprints moved? ─► restore]
        │ testDisputes ─► SendMessage(test-planner) ─► upheld / revised (test-writer) / spec-question
        ▼
  YOU run the feature's tests ─► fail ─► SendMessage(coding)  (fix until they pass)
        ▼ pass                                  status ─► review
  ┌ Agent(code-reviewer) "Focus: correctness" ┐
  ├ Agent(code-reviewer) "Focus: conventions" ┤  concurrent, one tool block:
  ├ Agent(code-reviewer) "Focus: security"    ┤  every reviewer must APPROVE
  ├ Agent(code-reviewer) "Focus: tests"       ┤  and every check must pass
  └ YOU run full verification: lint, typecheck, full suite, e2e ┤
        ▲                                     │ CHANGES_REQUESTED or a check fails
        └── SendMessage(coding, every defect) ─► feature's tests ─► every reviewer + the checks again  (fix until both pass)
  stuck, a blocker, or a spec-question at any stage ─► a ruling from the answerer
```

**The persistent roles** are the **planner**, the **plan reviewer** (two ids on a high-risk plan, one
per lens), the **test planner**, the **test writer**, the **coding agent**, and the **four code
reviewers**, one per focus. Record every id the `Agent` call returns.

**No agent runs a check for the gate.** The coding agent self-checks what it touched, and the test
writer runs only the tests it wrote. Neither report counts: a check passes only when you ran it and
read the result.

**Overlap what does not depend on each other:**

- **The test planner drafts from the specification while the plan is written.** It must not see the
  plan before it has drafted its cases, so it starts in **spec only** mode in the planner's tool
  block. It always runs, so this spawn is never wasted.
- **The reviewer pre-reads while the plan is written.** On a question turn the context pack exists
  before the plan does, so the reviewer starts in **pre-read only** mode in the tool block that sends
  the planner the answers. A pre-read the risk gate then drops costs tokens, never wall-clock.
- **The four code reviewers and the full verification run at once**, in one tool block.
- **Never ask the coding agent to run the whole suite** — that duplicates your slowest block.

**The context pack, the plan, and the test plan go by path.** The planner's `contextPack` holds the
work root, the relevant files, key symbols, conventions, one check command per check in
`verificationCommands`, and the project's `e2eCommand`. Write it to `context-pack.json` in the run
folder, `<framework root>/.runs/<claim>/`, as `agent-pipeline` says; the plan to `plan.md` when it
lands or a revision replaces it; the test plan to `test-plan.md` when it lands or a ruling revises
it. In every prompt below, "approved plan", "context pack", and "test plan" mean those paths, and
only an agent's *first* message carries them. Every exit deletes the folder.

Every agent turn ends with one `json` block, its shape in the agent definition. When one is missing
or malformed, ask that agent to re-emit it, as `agent-pipeline` says. The stage names below are the
ones a ruling and a `human_required` report.

## Plan

**Spawn the planner and the test planner in one tool block.** Keep both ids.

```
Agent(subagent_type: "sdlc:implementation-planner", model: "opus",
      prompt: the ticket path + task block + acceptance criteria + the epic's Note line
              + the e2eDecision line + the work root as an absolute path
              + (resumed ticket) the worklog path + the command's additions)

Agent(subagent_type: "sdlc:test-planner", model: "opus",
      prompt: the ticket path + task block + acceptance criteria + the e2eDecision line
              + the work root as an absolute path + the command's additions
              + "SPEC ONLY. The plan is being written and you will not see it yet. Draft the
                 cases from the specification and the existing tests now, and reply with a few
                 lines. I will send the plan.")
```

The planner reads the feature folder, surveys the code, and researches current practice; its agent
definition holds that process. Its block carries `contextPack`, `riskProfile`, and `openQuestions`.
A spec-only turn emits no block; it fails only when it returns nothing at all (stage `test-plan`).

- **Nothing returned** → `human_required` (stage `plan`).
- **`openQuestions` is empty**: the turn holds the plan. Go on below.
- **`openQuestions` is not empty**: the turn holds the context pack, no plan, and a `null`
  `riskProfile`. Write the pack to `context-pack.json`, and put every question to the answerer in
  one round. Then, in **one tool block**:
  - `SendMessage(plannerId, the answers + "These questions are settled — treat the answers as fixed
    constraints. Write the full plan now, and end with the json block.")`;
  - the plan reviewer's **pre-read**, spawned as Review the plan says.

  **An answer that does not settle a question is `human_required`** (stage `plan`): the
  `blocked_by` line names the question, and the report names `/plan` as the place to settle it. A
  further turn of questions from the planner goes to the answerer the same way.

Write the plan markdown to `plan.md`, keep the parsed `riskProfile` in hand, and when the plan lands
append the `implementation-planner · plan` entry and set the assignee, in one tool block. The run
folder is deleted at the exit, so the entry is the plan's only record: the **direction** it settled
on, the approach it turned down, and each question with the answer it got.

## Review the plan

**Apply the gate mechanically** on the `riskProfile` that came back with the plan — no judgment:

- **Skip review** iff `filesTouched ≤ 2` **and** `addsDependency == false` **and**
  `addsPublicApi == false` **and** `criteriaAutoCheckable == true`. The plan entry says "Review gate:
  SKIPPED", the assignee becomes `test-planner-<n>`, and you go to Plan the tests with the plan as
  approved. Drop a pre-read reviewer.
- Otherwise **review is required**. It is **high-risk** iff `addsPublicApi == true` **or**
  `addsDependency == true` **or** `filesTouched > 5`.
  - **Normal risk:** **one** reviewer, `model: "sonnet"` — reviewing a plan against files it has
    already read is checklist work.
  - **High risk:** **two** reviewers, spawned **in one tool block** with `model: "opus"`, each
    prompt naming its lens: (a) *correctness and completeness* — will the plan satisfy every
    acceptance criterion; missing work items, wrong assumptions, edge cases, ordering hazards; (b)
    *codebase fit* — conventions, dependency rules, architectural boundaries, unjustified new API or
    dependencies. A pre-read reviewer becomes lens (a), and you spawn the second now.

**The pre-read**, after a question turn — spawned in the tool block that sends the answers:

```
Agent(subagent_type: "sdlc:plan-reviewer", model: "sonnet",
      prompt: the ticket path + task block + acceptance criteria + the questions and their answers
              + the context pack + the work root as an absolute path + the command's additions
              + "PRE-READ ONLY. The plan is still being written. Read every file in the
                 context pack now and reply with a few lines on what you read and any
                 hazard you already see. Do NOT issue a verdict yet.")
```

**Hand over the plan** with `SendMessage(reviewerId, "Review the plan in <plan.md path> against the
checklist. You have already read the context pack files; re-read only what the plan points at that
you have not seen.")`. A reviewer that never pre-read gets the full first message: the pre-read's
contents with the plan in place of the PRE-READ line, and "Read the referenced files — do not
review from the plan text alone." Two reviewers go out **in one tool block**.

Merge multiple verdicts: `CHANGES_REQUESTED` if **any** reviewer requests changes; concatenate the
issues. Nothing returned → `human_required` (stage `plan-review`).

- `APPROVED` → append the `plan-reviewer · plan review` entry and set the assignee to
  `test-planner-<n>`, in one tool block, then Plan the tests. The entry carries the verdict, the
  issues that forced a revision, and how the revision answered them.
- `CHANGES_REQUESTED` → `SendMessage(plannerId, "Revise your plan to resolve every issue below. Note
  in the Context section how each was addressed. Re-emit the full plan markdown + the json block." +
  issues)` — the planner holds the plan, the ticket, and the pack, so **send only the issues**. When
  the revision lands, overwrite `plan.md` with it, then re-review through the same reviewer(s), in
  one tool block: `"Re-read <plan.md path>, which now holds the revised plan, and re-review it; the
  code is unchanged."` Loop back to the new verdict.
- `CHANGES_REQUESTED`, **stuck** → **a ruling** (stage `plan-review`), with the reviewer summary and
  the remaining issues.

## Plan the tests

Resume the test planner with the approved plan:

```
SendMessage(testPlannerId, approved plan + context pack
                         + "The plan is approved. Attach your drafted cases to the public
                            interfaces it exposes, cut what it made redundant, and return the
                            full test plan with its json block.")
```

It returns the test plan and a `json` block carrying `summary`, `cases` (each `new` or `guard`), and
`untested`. Nothing returned → `human_required` (stage `test-plan`).

Write the test plan to `test-plan.md`, and append the `test-planner · test plan` entry — each case in
one line (its id, the bug it catches, its type) and each exclusion with its reason — with the
assignee set to `test-writer-<n>`, or to `coding-<n>` when `cases` is empty, in one tool block.
**An empty plan skips Write the tests and Run each new test**: say so in the entry with the planner's
`summary`, and go to Implement with no written tests.

## Write the tests

Spawn the test writer **once** and keep its id:

```
Agent(subagent_type: "sdlc:test-writer", model: "sonnet",
      prompt: test plan + approved plan + context pack + the work root as an absolute path
              + "Write exactly these cases, report every file you changed and the command that
                 runs each case, and stop.")
```

It ends every turn with `summary`, `testFiles`, `command`, `e2eCommand`, `cases` (each with its own
`command` and what the writer `observed`), and `blockers`. Nothing returned → `human_required`
(stage `write-tests`). Non-empty `blockers` → **a ruling** (stage `write-tests`).

When it lands, **fingerprint every created and modified path in `testFiles`**, as `agent-pipeline`
says, and append the `test-writer · tests` entry with its test record, in one tool block. The
assignee stays `test-writer-<n>`.

## Run each new test

**Every `new` case must fail**, because the behavior it checks does not exist yet. A case that passes
catches nothing, and a case that does not run is broken. A `guard` case checks behavior that already
exists, so it is exempt.

Run each `new` case yourself by the command the writer reported for it, in one tool block when the
cases share no state, and judge each one:

- **Fails**: the command exits non-zero, on a failed assertion or on the module or behavior the plan
  will create. That is the result the stage wants.
- **Passes**: the command exits zero.
- **Does not run**: the command selects no test, or the case errors for a reason the new code cannot
  fix — a syntax error in the test, a missing fixture, a runner configuration error.

The writer's own `observed` value is not the gate; your run is.

- Every `new` case fails → go on.
- A case passes or does not run → **one** message carrying every such case and its output:
  `SendMessage(testWriterId, "These cases did not fail when I ran them. Sharpen each one that passes
  so it asserts what only the new code delivers; repair each one that did not run. Report every file
  you changed and every case's command." + cases and output)`. Take the fingerprints again, then run
  those cases again, and repeat until each one fails.
- The writer reports that a case cannot fail, because the behavior it checks already exists → the
  case is recorded and the run goes on. A case it cannot repair is a blocker → **a ruling** (stage
  `new-tests`): no later stage can make a broken test run.

In one tool block, append a `test-writer · tests` entry when the sharpen turn changed a file or a
command, then the `<claim> · new tests` entry — each case and how it failed, or that it still passes
— and set the assignee to `coding-<n>`. Keep each case that still passes; the `tests` reviewer
receives it.

## Implement

Spawn the coding agent **once** and keep its id:

```
Agent(subagent_type: "sdlc:coding", model: "opus",
      prompt: "Implement the approved plan exactly — no scope creep. Match the context pack
               conventions. Build until the written tests pass. Self-check only what you
               touched; I run the feature's tests and every project check after you."
              + approved plan + context pack + acceptance criteria + the work root
              + test plan + testFiles + each case's command  (or: "No test was written: <summary>")
              + the command's additions)
```

Its skill obligations, the rules on written tests, and the JSON contract live in the agent
definition — text there is free, text in this prompt is paid on every spawn.

It ends every turn with `summary`, `workItemsCompleted`, `filesChanged`, `decisions`, `blockers`,
`testDisputes`, and `notes`. **Every coding turn** — this one, a restore, a fix, and the turn after
a ruling — goes through these steps in order:

1. Nothing returned → `human_required` (stage `implement`, or the stage that sent the fix).
2. **Compare the fingerprints.** A test file that changed goes back: `SendMessage(codingId, "You
   changed <files>. Restore each to exactly what the test writer wrote. If a test is wrong, raise a
   test dispute instead.")`. Its reply goes through these steps again; a restore that is stuck is
   **a ruling** (stage `implement`).
3. Non-empty `blockers` → **a ruling** (stage `implement`) with them.
4. On the **first** turn, append the `coding · implement` entry — its `decisions`, which are the
   code-level calls the plan left open.
5. Non-empty `testDisputes` → **Test defect**.
6. Otherwise go to **Run the feature's tests**. A fix turn goes there too: the feature's tests run
   after every change to the code.

## Run the feature's tests

**The feature's tests are every test the feature's tickets wrote** — the cases in the test records
of the worklogs of the feature's tickets in `done/` and of this ticket, end-to-end cases left out,
since they run in the full verification. `board.py feature-tests --ticket <ID> --work-root
<code>=<work root>` collects them, as `ticket-board` says. Read any entry it returns under `unparsed`
by hand: take its files and commands, a later entry overriding an earlier one. A case it `skipped` —
a file this work root does not hold, such as one on a branch not merged yet — is named in the entry
and the report, never recorded as passed.

Run each command yourself, in one tool block when they share no state. This stage runs no lint, no
type check, no full suite, and no end-to-end test. A feature whose tickets recorded no test has
nothing to run here: say so in the entry and go on.

- **All pass** → append the `<claim> · feature tests` entry — each command, its result, and the fix
  cycles spent — and set `status` to `review` and the assignee to `code-reviewer-<n>`, in one tool
  block. Then go to Code review and full verification, after a fix from that stage too.
- **A failure** → `SendMessage(codingId, "The feature's tests fail. Fix the code, not the tests, then
  stop; I run them again." + each failing command and its failing tests and error lines)`. Its reply
  goes through Implement's steps. Then run every command again, the failed ones first.
- **A failure, stuck** → **a ruling** (stage `feature-tests`) with the failures.

## Test defect

A dispute may come from any coding turn, including a fix after the code review and the full
verification, when an existing test broke under a change the ticket meant to make. Set the assignee
to `test-planner-<n>` and send:

```
SendMessage(testPlannerId, "The coding agent disputes these tests. Rule on each against the
                            specification." + testDisputes)
```

It returns `rulings`, plus `plan` — the full current test plan, which overwrites `test-plan.md` —
when any ruling is `revised`. Nothing returned → `human_required` (stage `test-dispute`). Then:

- Any ruling `spec-question` → **a ruling** (stage `test-dispute`) with the planner's question. Send
  the reading the answerer chose to the test planner, which rules again from it.
- Any ruling `revised` → `SendMessage(testWriterId, "Apply these revised cases and stop." + the
  revised rulings)` — spawn the test writer now if the empty plan skipped Write the tests — then take
  the fingerprints again. A revised test skips Run each new test: the code that makes it pass may
  already exist.
- Any ruling `upheld` → **one** message to coding carrying every ruling: `SendMessage(codingId, "The
  test planner ruled on your disputes. Upheld tests stand — build against them. Revised tests have
  changed. Continue until the written tests pass." + rulings)`. Its reply goes through Implement's
  steps.
- Only `revised` rulings → go straight to Run the feature's tests. When they fail, the fix message
  to coding carries the rulings with the failures.

Append the `test-planner · test dispute` entry — each disputed test, the claim, the ruling, and the
reason — and, on a revision, a `test-writer · tests` entry, in one tool block, with the assignee set
to `coding-<n>`.

## Code review and full verification

The `status` is `review`. The reviewers read the change and you run the checks on the same tree, and
neither changes it, so they run **at once**. In **one tool block**, spawn **four** code reviewers, one
per focus — `correctness`, `conventions`, `security`, and `tests` — and run **every check command in
the context pack** as parallel Bash calls. Keep all four reviewer ids.

```
Agent(subagent_type: "sdlc:code-reviewer", model: <opus on high risk, else sonnet>,
      prompt: "Focus: <focus>. Review the change the coding agent made, against the approved plan
               and the acceptance criteria. Do not run the suite; I run every check."
              + the ticket path + approved plan + acceptance criteria + context pack + the work root
              + the coding agent's filesChanged + the review target ("the uncommitted changes
                against HEAD, untracked files included") + the command's additions
              + (Focus: tests only) the test plan + the test writer's testFiles
                + each new case that still passed after sharpening)
```

What each focus judges, the severity rules, and the JSON contract live in the agent definition.
**Model tier:** the high-risk test of Review the plan — **opus** when it holds, **sonnet**
otherwise. The code review has **no skip gate**: a passing suite says nothing about a missed
acceptance criterion, a broken layer boundary, or an injection path.

**The checks** of the full verification are the `command` of every entry in `verificationCommands` —
lint, type check, and the full test suite — and, only when the `e2eDecision` is yes, the end-to-end
suite: the pack's `e2eCommand`, or the test writer's `e2eCommand` when the pack's is `"none"` because
this ticket stood the suite up. Never both. A check passes when its command exits zero. **A check
the project lacks** — an entry whose `command` is `"none"` — is reported as skipped, with its reason,
never as passed.

Match each reviewer's block to it by `focus`. **The stage passes only when all four return `APPROVED`
and every check passes.** Every time the stage lands, append one `code-reviewer · code review` entry
per focus that reviewed and the `<claim> · verification` entry — each command and its result, each
skipped check and why, and what the last fix changed.

- A reviewer returned nothing → `human_required` (stage `code-review`).
- **All four `APPROVED` and every check passes** → the command's Finish. Keep every minor issue as a
  recommendation; it blocks nothing.
- **Any `CHANGES_REQUESTED`, or a check fails** → in one tool block, append the entries and set
  `status` to `in progress` and the assignee to `coding-<n>`. Then send **one** message carrying
  every blocking issue from every reviewer and every failing check: `SendMessage(codingId, "The code
  review and the full verification found the following. Fix ONLY what is needed to clear them — stay
  within the approved plan, change no test, then stop." + blocking issues + each failing command and
  its error lines)`. Its reply goes through Implement's steps, so the feature's tests run first. When
  they pass, run this stage again, in one tool block:
  - **resume every reviewer**, as `agent-pipeline` says — an approval covers only the code it read:
    `SendMessage(codeReviewerId, "Re-review the fix below. Judge each prior issue as fixed or still
    open; with none, judge only what the fix changed." + the coding agent's summary + filesChanged)`;
  - **run every check again**, the ones that failed first and the rest once they pass.
- **Stuck** → **a ruling** with the remaining issues and failures — stage `verification` when a
  check still fails, `code-review` when only the review still blocks.
