# sdlc plugin review: repetition, best practices, and the path to an autonomous framework

Reviewed version: `sdlc` 0.73.0 (commit `0d2ce73`), 2026-11-18. Scope: `plugins/sdlc` except the git-ignored `.obsidian/`, `.claudian/`, and the drawings in `diagrams/`.

## Summary

The pipeline itself is well designed. Its main strengths:

- Each role is a separate agent.
- Tests are planned from the spec and written by an agent that is not the coder.
- The orchestrator runs every check itself.
- One component writes to the board.
- Every ticket ends in one of two outcomes.
- Work happens in worktrees, nothing is ever pushed, and each ticket gets one commit.

That design should be kept.

Three problems stand in the way of turning it into an autonomous framework:

1. **The state machine is written as prose.** About 1 MB of Markdown tells an LLM orchestrator how to run the pipeline, and the LLM is the state machine. Ticket transitions, retry loops, fingerprints, claims cleanup and result parsing are all things the model has to remember and carry out correctly. These instructions are already contradicting each other: this review found about 15 contradictions across files, listed in §2.
2. **Nothing enforces the rules or limits spend.** There are no hooks and no output schemas. The unattended launcher defaults to `bypassPermissions`, has no timeout and no budget, and the design deliberately sets no limit on retries.
3. **The system cannot recover from failure.** A crash, timeout or Ctrl-C leaves a claimed `in progress` ticket and a dirty worktree. The next run then refuses to start, and other runs skip that feature until a person cleans up.

**Recommendation:** move control flow into a deterministic engine (`board.py` grows into it), and let LLMs make judgment calls only. Enforce agent boundaries with hooks and JSON schemas. Bound every run by budget and time. Make every exit path self-cleaning. Only then add the parts that make the system autonomous: scheduling, parallel features, PRs, notifications, and learning from worklogs. The roadmap in §5 is ordered so that each phase stands on its own.

---

## 1. What the plugin is

| Part | Count | Size |
| --- | --- | --- |
| Commands (`commands/*.md`) | 17 | 205 KB |
| Agents (`agents/*.md`) | 10 | 108 KB |
| Skills (`skills/**`) | 21 | 414 KB |
| Codex ports (`codex-skills/**`) | 33 files | 50 KB |
| Design docs (`designs/`) | 9 | 95 KB |
| Scripts (`scripts/`, `skills/diagrams/scripts/`) | 6 | 112 KB, about 2,800 lines |
| README, CHANGELOG | 2 | 51 KB, 173 KB |
| Hooks, tests, CI, evals, LICENSE | 0 | none |

How a ticket gets built:

1. `/plan` runs an interview and writes tickets.
2. `/orchestrate` (interactive), `/orchestrate-quick` (fewer stages) or `/run-roadmap` (unattended, with the `cto` agent in place of the person) drives one ticket through these stages:
   1. plan
   2. plan review
   3. test plan
   4. failing tests
   5. implement
   6. feature tests
   7. 4× code review and full verification
3. `scripts/run-roadmap.sh` runs `/run-roadmap` in a loop, one fresh `claude -p` session per ticket.

The files that change most often are the orchestrator prompts. Since January: README 36 commits, `orchestrate.md` 28, `orchestrate-quick.md` 25, `run-roadmap.md` 23, `ticket-board` 22. Most of the plugin's maintenance cost is in keeping these copies of the procedure in agreement.

---

## 2. Repetition

About **17.6 %** of the plugin's 142,500 words also appear word-for-word in another file (measured as shared 8-word sequences). Reworded copies don't show up in that number, so the real duplication is higher. Duplication matters here because the copies have already started to disagree.

### 2.1 Hotspots, ranked

| # | What is duplicated | Where | Size | Copies already disagree |
| --- | --- | --- | --- | --- |
| 1 | The whole build pipeline | `commands/orchestrate-quick.md:127-306` vs `skills/agent-pipeline/references/build-stages.md:110-407` | ~17 KB | 7 |
| 2 | Data model: statuses, frontmatter, buckets, ownership | `designs/*.design.md` vs the matching skills. Example: `ticket.design.md` ↔ `ticket-board` share 485 8-grams | ~2,000 8-grams | identical today |
| 3 | Command behaviour | `README.md` command and agent sections | ~15 KB | 4 |
| 4 | Which skill to load for which file | `agents/coding.md:48-55` and `:81`, `plan-reviewer.md:44-51`, `code-reviewer.md:72-110`, `commands/code.md:14`, `codex-skills/orchestrate/references/codex-subagents.md:151`, plus 14 skill descriptions | ~6 KB | 2 |
| 5 | Shared opening sections of the three orchestrators: the "rules live in four skills" table, "you are the only writer", the failure rules | `orchestrate.md`, `orchestrate-quick.md`, `run-roadmap.md`, `build-stages.md`, `workflow.design.md` | ~12 KB | 2 |
| 6 | Each agent's JSON fields, restated in spawn prompts | `build-stages.md`, `orchestrate-quick.md` (6×), `code.md:67`, `review.md:47`, `run-roadmap.md:221` | — | 3 |
| 7 | Ticket start and finish transitions | Owned by `ticket-board/SKILL.md:440-489`, restated in 5 other files. The `create-note.py` call alone appears in 13 files | — | 1 |
| 8 | Agent boilerplate: the work-root paragraph, the `technical-writing` loading paragraph, review output templates | 7 to 10 agents each | ~6 KB | — |

Two more things repeat across many files:

- The note that skill names may be `sdlc:`-namespaced appears **64 times in 26 files**.
- "No stage has a retry limit" appears in 5 files.

### 2.2 Contradictions found (all checked against the files)

- **`/orchestrate-quick` never runs the new tests itself.** `agent-pipeline/SKILL.md:131` and `agents/test-writer.md:12` say the orchestrator runs each new test. Quick asks the writer to "prove each fails" (`orchestrate-quick.md:192`).
- **`/orchestrate-quick` doesn't handle the planner's `openQuestions`.** The planner can return questions instead of a plan (`implementation-planner.md:44-48`), but quick only expects `contextPack` and `riskProfile` (`:151`).
- **Stage names differ.** Quick uses `review`, `targeted-verify` and `verify`. The build stages and `run-roadmap` use `plan-review`, `feature-tests` and `verification`.
- **The Codex port has a retry count.** `codex-subagents.md:195` says "Abort the stage if the second response is still missing or invalid". `agent-pipeline` says "no count ever raises" `human_required`.
- **`README.md:342`** says "three lost in a row ends it". No such limit exists in the command, the script or the design.
- **The README contradicts the commands in three more places:**
  - `README.md:623` says quick "asks nothing", but quick asks two questions (`:102`, `:270`).
  - `README.md:652` says `/review` re-reviews "once", but `review.md:86` loops until `APPROVED`.
  - `README.md:618` says a stopped task is "left assigned to you", but `ticket-board:486` removes `assigned`.
- **The design doc and the build stages disagree on blockers.** `workflow.design.md:112,116` makes a blocker `human_required`. `build-stages.md:233,297` sends it to the CTO for a ruling first.
- **`commands/code.md:14`** leaves `web-stack` out of the skills to load. `coding.md` includes it.
- **`ai-planning-workflow` is out of step with three other files:**
  - It records decisions in the worklog, but `ticket-guidelines.md:18` puts them in the ticket's `Decisions`.
  - Its UI-agreement step describes a code prototype. The `frontend-design` skill describes an Artifact mockup with a different list of screen states.
- **Agent models are set in two places that disagree.** `plan-reviewer` and `code-reviewer` say `model: opus` in their frontmatter, but every spawn overrides that with `sonnet` (`build-stages.md:171`, `orchestrate-quick.md:137`).

### 2.3 Fix: give every fact one home

| Fact | Single home | Everything else |
| --- | --- | --- |
| Agent output contract | A JSON schema per agent (see §3, finding 5) | "Act on its block" |
| Build stages | `build-stages.md`, with slots where the modes differ (answerer, who runs the checks, number of reviewers, end-to-end policy) | Quick keeps only its own Stages 1, 2, 7–9 |
| Ticket transitions | `board.py` subcommands (see §4) | Prompts call the command |
| Data model | Skills | Design docs link to the skill and keep only rationale and diagrams |
| Command behaviour | The command file | README gets 1–2 sentences and a link |
| Skill-to-file map | `paths:` globs in skill frontmatter | Delete the 6 tables |
| Shared orchestrator rules | One reference in `agent-pipeline` | Each command opens with one line pointing to it |
| Codex descriptions | Generated by a script from the Claude sources | — |

---

## 3. Best practices and guidelines broken

Checked against the Claude Code docs (skills, sub-agents, hooks, plugins reference, headless) and the Agent Skills best-practices page. `claude plugin validate` passes, so all of the problems below are ones the validator doesn't check for.

### Violations, ranked

1. **Five commands share a name with a skill** (`business-plan`, `design-system`, `feature`, `frontend-design`, `prd`). Claude Code now puts commands and skills in one namespace. In a live session, `sdlc:feature` and `sdlc:design-system` show the *command's* description. Agents are told to "load the `feature` skill" for its rules and may get the command's workflow instead. **Fix:** rename the rule skills, or merge each pair.
2. **Skill descriptions overflow the listing budget.** The 39 skill and command descriptions total 10,218 characters, plus 4,029 for the agents. The listing gets about 1 % of the context window, and in this session descriptions were already dropped for `run-roadmap`, `stack`, `review-text`, `business-plan`, `react-animations` and `social-writing`. A skill with no description can't trigger on its own. **Fix:**
   - Cut descriptions to 150–250 characters.
   - Add `paths:` globs to `ts-clean`, `react-clean` and `clean-tanstack-start`.
   - Preload the skills an agent always needs with the agent `skills:` field.
3. **14 skill descriptions are second-person and shouted** ("INVOKE THIS SKILL before you…"). The guideline is third person, in the form "Defines X. Use when Y."
4. **Two skills are too big.** `clean-fullstack-architecture` has 590 lines (32 KB) and `ticket-board` has 529 lines (29 KB); the guideline is under 500 lines. Eight reference files over 100 lines have no table of contents, and the `sdlc-structure` references link to each other.
5. **No hooks, no schemas.** Every hard rule is prose that the model has to remember, for example:
   - "Test-writer writes tests only."
   - "Reviewers write no code."
   - "Coding never changes a test."
   - "Exactly one JSON block."

   `agent-pipeline:75` admits it: "There is no schema enforcement". The skills doc says to move a rule that must always hold into a hook. Hooks see the subagent's type, so per-agent rules are possible.
6. **The unattended run has no limits and no permission checks.**
   - It runs with `--permission-mode bypassPermissions` by default (`run-roadmap.sh:39`).
   - `--timeout` defaults to 0, meaning none (`:42`), and no `--max-budget-usd` or `--max-turns` is passed.
   - The design says "Nothing but the person's `--max` and `--timeout` bounds what an unattended run spends" (`workflow.design.md:266`).
   - The result is scraped from a text line instead of using `--output-format json --json-schema`.
7. **Commands use the legacy format and miss frontmatter.** None of the 17 commands sets `disable-model-invocation`, `allowed-tools` or `model`. Commands with side effects can be started by the model on its own: `/setup`, `/run-roadmap` (which only the launcher should start), `/orchestrate*`, `/code` and `/plan`. Plugins should now use `skills/` instead of `commands/`.
8. **Loading skills costs a lot of tokens.** Upper bounds, if every named skill loads:
   - `coding` loads about 30k tokens before it starts work.
   - Each `code-reviewer` loads about 36k, so four parallel reviewers load about 144k per review round.
   - The orchestrator loads about 25–29k before its first agent.

   Each review focus should load only the skills it judges against.
9. **Pipeline state lives in a context that gets compacted.** The orchestrator has to remember agent IDs, fingerprints, which reviewer blocked, and the dispute rounds. After compaction, Claude Code keeps only the start of an invoked skill, so state stored only in context can be lost.
10. **Hygiene:**
    - `plugin.json` describes an older plugin: "Clean fullstack architecture skill, AI planning workflow…".
    - There is no LICENSE, and the plugin directory refuses a plugin without one.
    - The Codex manifest describes the plugin differently from the Claude one.
    - The plugin repo is also an Obsidian vault, so `designs/`, `diagrams/` and a 173 KB CHANGELOG ship with every install.

### Judgment calls

- **Emphasis.** The long prompts carry 200–250 bold markers each, and "never" or "do not" appears about 40 times per prompt. When everything is bold, nothing stands out. Prefer positive, scoped instructions.
- **Read-only agents with `Bash`.** They need `git diff`, so keep `Bash` and enforce read-only with a hook.
- **TS and React assumptions in generic agents.** `coding` and the reviewers name the TS and React skills directly. With `paths:` globs those skills would load only on matching files, so the agents would work on any stack.
- **Your environment, not the plugin.** Stale un-namespaced copies of `coding`, `implementation-planner`, `plan-reviewer`, `clean-fullstack-architecture` and `ai-planning-workflow` sit in `~/.claude/agents` and `~/.claude/skills`. You can see them in this session's agent list. Delete them.

---

## 4. Deterministic code: the scripts

`board.py` has a clean contract: argparse, one JSON object on stdout, and documented exit codes. But it only reads the board and manages claims. Its own header says it "never moves a ticket or changes a status" (`board.py:20`). The model still does every status transition, bucket move, roadmap edit, usage sum, worklog header, fingerprint check, retry count and cleanup by hand. There are **no tests** for the roughly 2,800 lines of script code, and no CI.

### Defects, ranked

| # | Defect | Evidence | Fix |
| --- | --- | --- | --- |
| 1 | No limit on cost, turns or time | `run-roadmap.sh:36,39,42,410-426` | Default `--timeout 2h`. Pass `--max-budget-usd` per ticket. Add a run-level budget. Cap cycles per stage (§5, phase 1) |
| 2 | A session can hang forever: stdin stays attached to the TTY in a background job, so a tool that reads it gets SIGTTIN and stops; `kill -0` still succeeds | `run-roadmap.sh:495-497` | Add `</dev/null` |
| 3 | A crash, timeout or Ctrl-C leaves the ticket claimed and `in progress` with a dirty worktree. The next `--run` exits 1, though the help documents 3. Claims never expire | `:472-479,574-586,366-368`; `board.py:239` | On those exit paths, stop and release from the launcher. Save the diff on a `-wip` ref. Add `claimedAt` and `release --stale` |
| 4 | Two runs can both claim the same ticket: there is no lock between write and read-back | `board.py:337-366`; run-number pick `run-roadmap.sh:346-350` | Take `fcntl.flock` on `work/.board.lock`. Reserve the run number with an atomic `mkdir` |
| 5 | File writes aren't atomic, and the script's own `kill -KILL`, or Obsidian/iCloud sync, can truncate a ticket mid-write | `board.py:334`, `build-roadmap.py:1014`, `create-note.py:213`, `excalidraw_md.py:499` | Write to a temp file, then `os.replace` |
| 6 | A value option given last (e.g. `--max` with no number) makes the option loop never end (reproduced) | `run-roadmap.sh:133-141` | `[ $# -ge 2 ] \|\| die` |
| 7 | The launcher trusts the model's result line: greedy grep, outcome never validated, `remaining` computed by the model, claude's exit status ignored when a line exists | `:533-537,569-588` | Use `--output-format stream-json`. Compute `remaining` with `board.py`. Verify the commit is on the branch |
| 8 | Nobody is told when the run stops. Logs go to `$TMPDIR`, which macOS purges | `:380,660-691` | Add `--notify CMD`. Keep logs in `.runs/<run>/logs` |
| 9 | Two different implementations pick the run number, and the shell one misses quoted values | `run-roadmap.sh:333-344` vs `board.py next-run` | Use `board.py` |
| 10 | Call sites are inconsistent: `python3 "${CLAUDE_PLUGIN_ROOT}/…"` in some prompts, bare `board.py …` in others. Every rule also has a by-hand fallback for when `python3` is missing | `run-roadmap.md:186`, `orchestrate.md:114`, … | Check for `python3` once in preflight, use one call form, delete the fallbacks |

### Work the model still does by hand that belongs in code

1. Status transitions: start, finish, stop, return, and moving between buckets.
2. Roadmap row edits and re-sorting.
3. Usage arithmetic (timing, tokens, cost).
4. Worklog entries, including copying the test record from the writer's block.
5. Choosing the next ticket in a cluster. `board.py` already computes it, but the prompt re-derives it.
6. `remaining`, `nextAction` and the decision to stop.
7. Releasing claims on every exit, including a crash.
8. Discarding a stopped ticket's code.
9. Creating or reusing the run worktree.
10. The list of paths to commit for the documents commit.
11. Detecting that another run is building in the same checkout.
12. Saving and checking test-file fingerprints.
13. Validating each agent's JSON block.
14. Counting retries and detecting a stuck stage.
15. Numbering a new ticket on `rescope`.
16. Creating and deleting the `.runs/<claim>/` folder.

---

## 5. How to evolve it into an autonomous framework

### 5.1 Target architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│ Supervisor   cron / CI / routine · picks features · runs N in        │
│              parallel worktrees · opens PRs · notifies · enforces    │
│              run budget                                              │
├──────────────────────────────────────────────────────────────────────┤
│ Engine       `sdlc` CLI (board.py grown up): ticket state machine,   │
│              run state in .runs/<claim>/state.json, gates, cycle     │
│              caps, budgets, locks, atomic writes, crash recovery,    │
│              schema validation of every agent result                 │
├──────────────────────────────────────────────────────────────────────┤
│ Agents       planner · reviewers · test-planner · test-writer ·      │
│              coding · cto · resolver: judgment only, each with a     │
│              JSON-schema output contract                             │
├──────────────────────────────────────────────────────────────────────┤
│ Guardrails   hooks.json: per-agent write scopes, test-file           │
│              protection, schema checks on SubagentStop, no push,     │
│              no --no-verify                                          │
├──────────────────────────────────────────────────────────────────────┤
│ Knowledge    slim, path-scoped rule skills · product docs · learned  │
│              lessons from worklogs                                   │
└──────────────────────────────────────────────────────────────────────┘
```

**The principle:** *code decides what happens next; models decide what is right.* The LLM orchestrator becomes a thin driver. It asks the engine "what's the next step?", spawns the agent it names, and passes the agent's validated result back. Gates, transitions and loops can then be tested with pytest instead of by hoping the model followed the instructions.

**Where the engine runs.** There are two options; take them in order:

- **A, keep the LLM orchestrator, drive it from the engine.** The command prompt shrinks to a loop: `sdlc step --run X` returns JSON such as `{action: "spawn", agent: "plan-reviewer", input: {...}}`, the model does what it says, then calls `sdlc report --run X < block.json`. This works in Claude Code and Codex today and keeps `SendMessage` resumption.
- **B, an engine on the Claude Agent SDK.** A Python process drives the agents directly and calls models only for agent turns. That removes the orchestrator's context cost, makes runs replayable, and lets it run in CI with no terminal. Do this after A has proven the state machine.

### 5.2 Autonomy levels

| Level | What it means | Where sdlc is |
| --- | --- | --- |
| L1 | Supervised: a person starts each ticket and watches | `/orchestrate`, met |
| L2 | Unattended but bounded: runs alone within a budget and time box, and stops safely | `/run-roadmap`, partly met: no budget, unbounded loops, unsafe permissions |
| L3 | Recovers on its own: survives a crash or timeout, cleans up, resumes, and expires stale claims | Not met |
| L4 | Continuous: triggered by schedule or events, builds several features in parallel, opens PRs, notifies people, and merges what passes policy | Not met |
| L5 | Improves itself: learns from worklogs, measures itself with evals, and proposes changes to its own rules | Not met |

### 5.3 Roadmap

Each phase can ship on its own. The phases are ordered by risk removed per unit of effort.

#### Phase 0: stop the drift (about 1 week, prompts only)

- Fold `/orchestrate-quick`'s pipeline into `build-stages.md`, with mode slots for the differences. This removes 17 KB and 7 contradictions.
- Pull the shared orchestrator opening (skills table, only-writer rule, failure rules, namespace note) into one `agent-pipeline` reference.
- Remove the JSON field lists from spawn prompts and the skill-to-file tables from agents.
- Cut the README command sections to 1–2 sentences plus a link. Cut the design docs down to rationale, diagrams and links to the skills.
- Fix the contradictions in §2.2, and set each agent's model in one place.
- Rename the five rule skills that collide with commands. Rewrite all descriptions in third person at no more than 250 characters. Add `paths:` globs.
- Split `clean-fullstack-architecture` and `ticket-board` into a short core plus references. Add tables of contents.
- Update `plugin.json`, add a LICENSE, and generate the Codex descriptions with a script.

**Done when:** no stage procedure exists in more than one file, every skill description is visible in a fresh session, and `claude plugin validate` passes.

#### Phase 1: make L2 safe (about 1–2 weeks)

- **Launcher fixes:**
  - Add `</dev/null` to the session command.
  - Fail on an option with no value.
  - Default `--timeout 7200`.
  - Add `--budget-usd`, passed per ticket as `--max-budget-usd`, plus a run-level total read from each session's `total_cost_usd`.
  - Replace bypass with `--permission-mode auto` (or `acceptEdits`) and an `--allowedTools` allowlist.
  - Use `--output-format json --json-schema` for the result.
  - Add `--notify`, and keep logs under `.runs/`.
- **Bounded loops that don't stop the run.** Keep the "no count stops a run" idea, but make the count escalate: after *N* cycles on one stage (default 4), the engine asks the CTO for a ruling, and if the CTO rules `retry` again, the ticket is `human_required`. This keeps the design's intent, a gate is never abandoned just because a counter ran out, while putting a ceiling on spend.
- **`hooks/hooks.json`:**
  - `PreToolUse` on `Edit|Write`: deny for the planner, reviewers, cto, resolver and verify agents. Allow only test-file globs for `test-writer`. Deny `coding` edits to files listed in `.runs/<claim>/fingerprints`.
  - `PreToolUse` on `Bash`: deny `git push`, `--no-verify`, `reset --hard` outside the run worktree, and `rm -rf` outside the work roots.
  - `SubagentStop` (matcher `^sdlc:`): validate the last message's JSON block against `schemas/<agent>.json`, and send it back with the error if it fails.
- **Tests:** pytest with board fixtures in `tmp_path`, plus a fake `claude` on `PATH` that plays back scripted result lines (completed, human_required, no-work, no line, hang) to drive every path through the launcher. Run them in GitHub Actions.

**Done when:** a fault-injection suite (kill mid-ticket, hang, malformed block, a gate that never converges) ends every time with a bounded cost and a clean board.

#### Phase 2: the engine, to reach L3 (about 3–4 weeks)

- Grow `board.py` into `sdlc` with these subcommands:
  - `start | finish | stop | return`: transitions from an allowed-transition table, with the lock, atomic moves, the roadmap rebuild and usage sums.
  - `log`: takes an agent block on stdin and writes the worklog entry.
  - `fingerprint save | check`
  - `run init | step | report | end`: the run state lives in `.runs/<claim>/state.json`, holding stage, cycle counts, agent IDs, the issues still open, and spend.
  - `recover`: finds stale claims (via `claimedAt` plus heartbeat), stops the ticket as `blocked: session crashed`, saves the diff on a `-wip` ref, and releases the claims.
- Rewrite `/orchestrate`, `/orchestrate-quick` and `/run-roadmap` as thin `step`/`report` loops. Expected size: each under 150 lines, down from 205 / 325 / 505.
- Detect "stuck" deterministically: hash each agent's normalized issue list, so the same hash twice in a row means stuck. The CTO is asked only when the engine says the stage is stuck.
- The launcher runs `sdlc recover` before each session and on every abnormal exit.

**Done when:** the state machine has unit tests for every transition, a session killed at any stage can be resumed with no manual cleanup, and the orchestrator prompts no longer describe any bookkeeping.

#### Phase 3: continuous delivery, to reach L4 (about 3–4 weeks)

- **Triggers:**
  - a scheduled routine, or a GitHub Actions cron that runs the launcher;
  - an event trigger when a ticket enters `backlog` or an issue gets a label;
  - `/whats-next` as a status page.
- **Parallel features.** The supervisor runs one worker per independent feature cluster, each in its own run worktree. The engine's lock and the work-root busy check already make this safe once Phase 2 is done.
- **PRs instead of long-lived branches.** Open one PR per feature (or per ticket, configurable) with the worklog summary, the test plan, the review verdicts and the cost. Branch protection and CI decide whether it can merge. Auto-merge is policy-driven and off by default: allowed only for a low-risk profile with green CI and all reviewers approving.
- **Notifications.** On `human_required`, send one message with the ticket, the stage, the question, and the exact resume command (Slack, a GitHub issue comment, or a push notification). A person answers by editing the ticket's `Decisions` or `blocked_by`, and the next scheduled pass picks it up. That turns `human_required` into an asynchronous hand-off instead of a stop.
- **Budget policy as config.** Add `sdlc.json` keys `budget.perTicketUsd`, `budget.perDayUsd`, `models.<agent>` and `parallelism`. The supervisor enforces them.

#### Phase 4: self-improvement, to reach L5 (ongoing)

- **Retrospective agent.** After each finished or stopped ticket, it reads the worklog and extracts recurring causes: a reviewer's repeated issue types, test disputes upheld vs revised, planner forks the CTO kept deciding the same way. It proposes:
  - new `Decisions` defaults in the product docs;
  - a rule for the relevant skill, as a PR against the plugin, reviewed by a person;
  - ADR entries for CTO rulings that set a precedent.
- **Metrics from the board.** Track tickets per day, cost per ticket, cycles per stage, how often a stage ends `human_required`, review-blocking rate by focus, and how often a test that failed first is then disputed. Show them in `/whats-next --stats`.
- **Evals for the plugin itself.** A small fixture repo plus a ticket set, with expected outcomes, run on every plugin change through `claude plugin eval` in CI. Prompt changes then ship with measured effects instead of a CHANGELOG entry. The 173 KB CHANGELOG shows how much change happens without any way to measure it.
- **Model routing by risk.** The engine picks the model per agent from the plan's risk profile and from history, for example Haiku for `verify` and Sonnet for low-risk reviews, and records which choice reached `done` cheaper.

### 5.4 What not to change

- **The role split and tests-first from separate agents.** This is what makes unattended output trustworthy.
- **The orchestrator running every check itself.** In the new design the engine does it.
- **One writer for the board.** In the new design that is the engine.
- **Worktrees, one commit per ticket, never push or merge without policy.**
- **`human_required` as the only stop outcome.** It becomes an asynchronous hand-off rather than the end of the run.
- **The CTO agent.** Narrow it to rulings the engine asks for, and record its precedents so later rulings stay consistent.

---

## 6. First ten actions

1. Add `</dev/null` to the session command and fail on an option with no value in `run-roadmap.sh` (two lines, removes a hang).
2. Default `--timeout` and add `--max-budget-usd` (removes unbounded spend).
3. Change the default from `bypassPermissions` to `auto` plus an allowlist.
4. Add `flock` and atomic writes to `board.py`. Add `claimedAt` and `release --stale`.
5. Make the launcher release claims and save the worktree diff on timeout, crash and Ctrl-C.
6. Add a pytest suite for `board.py` and `build-roadmap.py`, plus a fake-`claude` launcher test, and run it in CI.
7. Fold quick's pipeline into `build-stages.md` and fix the §2.2 contradictions.
8. Rename the five colliding rule skills, then shorten every description and add `paths:` globs.
9. Ship `hooks/hooks.json` with per-agent write scopes and a `SubagentStop` schema check.
10. Start `board.py start|finish|stop` and `run step|report`. This is the beginning of the engine.
