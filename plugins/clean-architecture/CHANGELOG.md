# Changelog

All notable changes to the **clean-architecture** plugin are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.37.0] - 2026-09-04

### Changed

- **Every ticket belongs to an epic, and the epic's code prefixes its ID.** Ticket numbers ran
  in one project-wide sequence (`SW-001`, `SW-002`, …). Two branches planning two unrelated
  features both took the next free number, both wrote `SW-004-<slug>.md`, and the merge kept one
  ticket and lost the other. Nothing in the numbering said which feature a ticket belonged to
  either.

  An **epic** is now a named group of tasks that deliver one feature. It carries a short
  uppercase code, that code prefixes every ticket ID under it, and **the numbering restarts at
  001 in each epic**:

  ```
  tickets/todo/         AUTH-001-user-login.md
  tickets/in-progress/  AUTH-002-session-timeout.md
  tickets/done/         BILLING-001-invoice-export.md
  ```

  Two branches planning separate features write into separate number spaces, so each adds a
  first ticket and neither overwrites the other.

  **`roadmap.md` is the list of epics.** It holds one `## <CODE> — <epic name>` section per
  epic, and each section holds its own task table and its `###` detail sections. A new epic
  appends a section, so two branches change different parts of the file. A dependency may still
  name a task in another epic: every ID is unique across the project, because every epic code
  is.

  `/plan` names the epic in its approval gate before it writes anything — the existing one the
  request belongs to, or a new code it proposes — then appends its rows under that epic's
  section and touches no other. It reads the next number out of the files, globbing every status
  folder for `<CODE>-*.md`, `done/` included. The ticket template gains an `**Epic**` field.
  `/orchestrate` and `/orchestrate-quick` read every epic section, and break a tie between
  ready tasks by roadmap order instead of by lowest ID, which no longer compares across epics.

  **A project on the old scheme keeps its IDs.** Nothing renumbers a ticket on its own, and
  `/plan` continues whatever scheme it finds. `/scaffold` now offers the migration: it proposes
  an epic grouping for the existing tasks, shows the full old-ID-to-new-ID table, and only after
  an explicit yes renames the tickets with `git mv`, regroups the roadmap, and fixes every
  inbound reference. It says first what the rename costs, because a branch citing an old ID
  stops finding the file.

## [0.36.0] - 2026-08-31

### Changed

- **Design docs live in their own folder: `.clean-architecture/designs/`.** One file per
  subject was the right shape, but every one of those files sat beside `prd.md` and
  `roadmap.md` in the top folder. A project with a dozen subjects buried the two documents a
  reader opens first, and nothing said where a new design doc belonged.

  Each kind of document now gets its own folder once there can be more than one of it.
  `prd.md` and `roadmap.md` stay at the top, because there is exactly one of each. The design
  docs move into `designs/`, the way tickets already sit in `tickets/`:

  ```
  .clean-architecture/
    prd.md
    roadmap.md
    designs/overview.design.md, checkout.design.md, event-ingestion.design.md, …
    tickets/todo/, in-progress/, done/
  ```

  The file names do not change: `<subject>.design.md`, the subject and nothing else. The docs
  are siblings in one folder, so they still cross-reference each other by file name alone. A
  doc that names the PRD in its `Related` header now writes `../prd.md`.

  `/scaffold` writes `designs/overview.design.md`, creates `designs/` even when it stays
  empty, and offers to `git mv` loose `*.design.md` files into it — alongside the existing
  offer to rename a lone `design.md`, which now lands on `designs/overview.design.md`.
  `/design` and `/plan` list `designs/*.design.md` before writing. The interviewer, the
  planner, and the plan reviewer read the docs there.

  **A project on an older shape keeps working.** Every reader falls back to `*.design.md`
  files directly in `.clean-architecture/`, then to a single `design.md` in the folder or at
  the project root. Nothing moves without an explicit yes.

## [0.35.0] - 2026-08-31

### Changed

- **Design docs are one file per subject: `<subject>.design.md`.** A single `design.md` made
  every design compete for one file. The doc grew until nobody read it whole, a change to one
  subject touched the same file as every other, and the name said nothing about what was
  inside.

  A design doc now covers one subject and carries its name — `checkout.design.md`,
  `event-ingestion.design.md`, `app-shell.design.md` — all beside `prd.md` in
  `.clean-architecture/`. The name is the subject, never the document: not `design-billing.md`,
  not `billing-design.md`. `overview.design.md` is the optional entry point that names the
  parts of the whole solution and points at the rest. Docs cross-reference each other by file
  name.

  The `design-doc` skill's "when to split" guidance became "choosing the subject": splitting is
  the convention now, not a judgment call at the end, so the skill says how to pick the subject
  before the first line and names the three signs that a second doc has started — a section the
  rest of the doc does not depend on, the same design restated for a second reader, and a
  subject that needs "and" to say what it covers.

  `/scaffold` writes `overview.design.md`, writes it only when the project has no design doc at
  all, and offers to `git mv` a lone `design.md` onto the new name. `/design` lists
  `*.design.md` before writing and updates the matching doc in place. `/plan` updates the docs
  whose subjects the request touches. The interviewer, the planner, and the plan reviewer list
  `*.design.md` and read the ones their task touches.

  **A project on the old shape keeps working.** Every reader falls back to a single
  `design.md`, in the folder or at the project root, and nothing renames it without an explicit
  yes.

## [0.34.0] - 2026-08-31

### Changed

- **The `design-doc` skill now specifies a solution, not a user interface.** Every part of the
  skill assumed the subject was a screen: the per-surface pattern ran layout → content →
  states → responsive, the altitude rule was written against hex values and font families, and
  the states table asked for "Appearance". A design for a queue, a permission model, or an
  integration had nowhere to go, so the skill either produced a UI doc for a non-UI subject or
  was skipped.

  The subject is now anything a team designs — a system, a service, a data flow, an
  integration, a background job, a rule, or a screen — and the skill says outright that a user
  interface is one case, not the default. The pattern generalizes to structure → behavior →
  states → variation and limits, with **Behavior** as the new center: one unit of work followed
  from where it enters to where it leaves, so a reader can trace a complete path through the
  solution. The states table asks what happens rather than what it looks like, and names the
  failures worth covering — invalid input, a missing permission, an unavailable dependency, a
  duplicate. A table of common subjects shows what fills each section for a system, a flow, an
  integration, a rule, and a screen.

  The altitude rule generalizes with it. The test is no longer pixels: a decision belongs to
  the part that owns it when it can change without a neighbor observing the difference. Naming
  a technology or a number is allowed when that choice *is* the design decision and changes
  observable behavior — a store that guarantees ordering, a retry budget of three attempts —
  and stays qualitative when it is not.

  `/design`, the `/scaffold` design stub, the `/plan` document stage, the Codex entry point,
  and the three agents that read `design.md` follow the same wording. `/design` takes a system,
  a service, a flow, an integration, or a screen as its target.

## [0.33.0] - 2026-08-30

### Changed

- **Codex and Claude Code no longer share a skills directory.** Every `SKILL.md` under a plugin's
  `skills/` folder is visible to Claude Code — its manifest `skills` field only *adds* directories
  to that scan, it cannot subtract one — so the six Codex entry points that wrap a Claude command
  (`orchestrate`, `orchestrate-quick`, `code`, `plan`, `scaffold`, `explain`) sat in a Claude
  session's skill index describing a runtime that was not running. Nothing but a name collision
  with the same-named command kept them out of the way, and a collision is not a guarantee.

  The six moved to a new `codex-skills/` folder, and `.codex-plugin/plugin.json` points its
  `skills` field there. Claude Code scans `skills/`, which now holds the eight shared skills and
  not one line of Codex instruction. The split is structural: a Claude session cannot reach a
  Codex file, whatever the resolution order does.

  Codex keeps every skill it had. `codex-skills/` also holds a short entry point for each shared
  skill — `prd`, `design-doc`, `ai-planning-workflow`, `clean-writing`,
  `clean-fullstack-architecture`, `ts-clean`, `react-clean`, and `clean-tanstack-start` — that
  names when the skill applies and then reads the one real copy in `skills/`. The rules live in
  exactly one file, as before.

- **The orchestration skills no longer force a Codex protocol read.** `$orchestrate`,
  `$orchestrate-quick`, `$code`, and `$plan` each opened by ordering the agent to read
  `references/codex-subagents.md` completely, and then named that protocol a second source of
  truth beside the shared command. The same `SKILL.md` files load in Claude Code, where the
  protocol translates tools that are already correct — so every run paid for a document that
  described another runtime, and the "protocol overrides Claude-only tool syntax" line invited
  the agent to reach for `collaboration.spawn_agent` in a session that has the `Agent` tool.

  The read is now conditional. Each skill says to run the workflow with the subagent, file, and
  user-input tools of the current runtime, and adds one line: in a Codex session, also read the
  protocol before creating a subagent. The shared command in `commands/` is the single source of
  truth for stages, gates, and limits in both runtimes.

  Codex behavior is unchanged. The protocol file stays where it is, keeps every rule, and is
  still required reading there — a Codex session that skips it has no `Agent` tool to fall back
  on.

- **Two descriptions dropped a runtime from their text.** `$orchestrate` and `$orchestrate-quick`
  described themselves as driving a task "with persistent Codex subagents" while also serving
  Claude Code. Both now say "with persistent subagents". The `$name` and `/name` equivalence
  stays, because that is the part a Codex user needs.

## [0.32.0] - 2026-08-30

### Added

- **Status folders for tickets.** Every ticket used to sit in one flat `tickets/` folder, and the
  only way to see what was waiting, what was being built, and what had shipped was to open the
  files or read the roadmap table. The tickets folder now holds three subfolders — `todo/`,
  `in-progress/`, and `done/` — and a ticket moves between them as the work progresses. A
  directory listing is now the board.

  The folder never becomes a second source of truth. The `**Status**` field inside the ticket
  stays the record, and the file moves in the same step that rewrites that field, so the two
  cannot drift apart. Five status values map onto three folders: `Not Started` is `todo/`,
  `Completed` is `done/`, and `In Progress`, `Blocked`, and `Review` all sit in `in-progress/`,
  because all three mean the work has started and has not shipped. Moves use `git mv`, so a
  ticket keeps its history.

  Because a ticket's path now changes, nothing may store one. Every reader finds a ticket by its
  ID instead — `tickets/*/<ID>-*.md` first, then `tickets/<ID>-*.md` — and the roadmap cites its
  ticket by file name rather than by a path a later move would invalidate.

  A project that already keeps its tickets in one flat folder keeps working unchanged. The
  commands detect the flat layout, skip the move, and write the status field alone. `/scaffold`
  offers to sort a flat folder into the three status folders with `git mv`, and asks first — like
  every other move it offers.

### Changed

- **`/scaffold` creates the three status folders**, each with a `.gitkeep`, since git does not
  track an empty directory. Its roadmap stub cites a ticket by file name, and names the three
  folders so a reader knows where to look. The ticket template stays at the top of `tickets/`,
  outside the status folders: it is a template, not a ticket, so it never moves.
- **`/plan` writes every new ticket into `tickets/todo/`.** It already refused to set a status
  past `Not Started`; it now also refuses to move a ticket out of `todo/`. Its collision check
  reads every status folder before it writes, because a completed ticket sits in `done/`.
- **`/orchestrate` and `/orchestrate-quick` move the ticket at both status boundaries.** Marking
  In Progress moves it into `in-progress/`; marking Completed moves it into `done/`. An escalated
  or aborted run leaves the ticket in `in-progress/`, matching the status it leaves behind. A
  Decisions brief written when no ticket exists lands beside the ticket it serves, and moves with
  it.
- **The `ai-planning-workflow` skill holds the convention** — the folder layout, the status
  mapping, the `git mv` rule, the lookup order, and the flat-folder fallback. The commands state
  the operational rule and point there.

## [0.31.0] - 2026-08-30

### Added

- **`/plan` — the intake command that fills the roadmap.** Every document this plugin reads had
  a writer except the two that drive the work. `/prd` wrote the PRD, `/design` wrote the design
  doc, `/scaffold` wrote a roadmap holding one placeholder row, and `/orchestrate` consumed a
  roadmap somebody had to fill by hand. `/plan` closes that gap: it takes a request in plain
  words and leaves behind an updated PRD, an updated design doc, ordered roadmap tasks, and one
  ticket per task, ready for `/orchestrate` to pick up.

  It runs an interview first. The `feature-interviewer` agent reads the product docs, explores
  the codebase, and researches the topic on the web while the command reads the same documents
  itself for the vocabulary, the affected surfaces, and the roadmap's ID scheme — both calls go
  out in one tool block, so the research costs no wall-clock. The open decisions come back to
  the user through `AskUserQuestion`, and the answers become the ticket's `Decisions` section,
  which is the one place a chosen library may be named.

  One approval gate stands in front of every file write: the command presents the PRD and design
  sections it would touch and the roadmap rows it would add, and waits. After the yes, it writes
  in dependency order — PRD, design doc, roadmap, tickets — so each document takes its vocabulary
  from the one before it. Three rules keep the documents from drifting into each other: the link
  runs one way (a ticket cites a PRD area code, never the reverse), tickets stay at what-not-how
  because the planner inside `/orchestrate` decides the how, and every status this command writes
  is a starting status — pending in the roadmap, `Not Started` in the ticket. A request that
  needs no document at all is handed to `/code` before the interview ever runs.

- **`$clean-architecture:plan` for Codex** — `skills/plan/`, the Codex entry point that reads the
  same `commands/plan.md` and the subagent protocol, plus its `agents/openai.yaml` interface.

### Changed

- **The Codex subagent protocol covers `commands/plan.md`** as well as the two orchestrate
  commands and `commands/code.md`. It maps `/plan` to `$plan`, states that invoking `$plan` is
  not approval for the breakdown it proposes, and requires the session to stop rather than plan
  from memory when no collaboration tools are available.

## [0.30.0] - 2026-08-27

### Added

- **`/code` — the direct implementation path.** The plugin had two ways to write code, and both
  ran a pipeline: `/orchestrate` (interview → plan → review → implement → verify, five agents)
  and `/orchestrate-quick` (plan → review → implement → verify, four). A fix or a small feature
  paid for a planner and a reviewer it did not need. `/code` runs one agent — the same `coding`
  agent the pipelines use — with no plan in front of it. The command stays thin on purpose: the
  agent already loads `clean-fullstack-architecture`, `ts-clean`, `react-clean`, and
  `clean-tanstack-start` from its own definition, so a spawn prompt that restated them would
  re-pay that text on every spawn.

  The command has one guard against becoming a worse orchestrator. When the request turns out to
  carry open product or architecture decisions, or to span many files in an order that matters,
  it names `/orchestrate` or `/orchestrate-quick` and stops instead of improvising a plan. Its
  report also names every gating command that nobody ran, because no verify agent stands behind
  it — the coding agent's targeted self-check is the only check.

- **`$clean-architecture:code` for Codex** — `skills/code/`, the Codex entry point that reads the
  same `commands/code.md` and the subagent protocol, plus its `agents/openai.yaml` interface.

### Changed

- **The `coding` agent no longer requires a plan.** Its input was an approved implementation plan,
  and its first rule forbade deviating from one — so a request arriving without a plan left the
  agent with nothing to obey. Its input is now a **work brief** in one of two shapes: an approved
  plan from either orchestrator, or a request sent with no plan. With a plan, the direction is
  settled and the old rule holds. With a request, the agent breaks the work into items, finds the
  files, and chooses the approach itself, and the request's scope is the boundary it must not
  cross. Acceptance criteria became optional in both shapes: when the brief carries none, the
  agent derives them and reports what it assumed. One rule is new — when no verify stage follows,
  the agent's targeted self-check is the only check, so it must name every gating command that
  nobody ran. The skills, the conventions, the comment cap, and the `json` contract are
  unchanged.

- **The Codex subagent protocol covers `commands/code.md`** as well as the two orchestrate
  commands, and maps `/code` to `$code`. Its `coding` task name already existed.

## [0.29.0] - 2026-08-25

### Added

- **File names now carry the layer.** `ts-clean` Rule 1 gains dot notation for the modules that
  fill a role the architecture names: `<subject>.<role>.ts` — `user.service.ts`,
  `user.repository.ts`, `user.adapter.ts`, `user.dto.ts`, `user.model.ts`. The export keeps its
  own name, so `user.service.ts` still exports `UserService`; what changes is that a directory
  listing reads as a layer map, one resource's files sort together, and lint rules or codegen get
  a glob to match a layer on. The rule is deliberately narrow: a plain module keeps a plain name
  (`parseInvoice.ts`, `useUser.ts`, `UserCard.tsx`), an invented role (`user.utils.ts`,
  `user.manager.ts`) is the `utils.ts` bag with a dot in it, and a name that would need
  `.service.repository.ts` is two modules.

- **`clean-fullstack-architecture` carries the same rule** as a core principle, annotates its
  layer tree with the suffixes (`*.model.ts`, `*.adapter.ts`, `*.service.ts`, `*.dto.ts`), and
  validates it: every service, adapter, DTO, and model file has its role suffix, and no domain,
  component, container, or hook file was given one.

### Changed

- **`ts-clean` no longer mentions React.** The skill is framework-agnostic, but its text still
  said "or React component", pointed at `react-clean`, and used `lazy(() => import('./Editor'))`
  as its code-splitting example — so a reader on a Node or backend file was told about a
  framework that was not in play. All three are gone. The `.ts`/`.tsx` scope is unchanged, and
  `react-clean` still builds on `ts-clean` from its own side.

- **Every service, adapter, and model example was renamed to the new convention** —
  `services/UserService.ts` to `services/user.service.ts`, `adapters/userAdapter.ts` to
  `adapters/user.adapter.ts`, `models/presentation.ts` to `models/presentation.model.ts` — across
  `clean-fullstack-architecture`, its `dependency-rules.md` reference, and `react-clean`. Two
  kinds keep their plain names on purpose, and the examples now say so: domain logic, hooks,
  components, and containers, which are named after what they do, and a transport module that
  exposes no domain operation (`services/orpcClient.ts`).

## [0.28.0] - 2026-08-11

### Changed

- **Comments are now capped, not just discouraged.** The old rule said "default to zero
  comments" and then listed six kinds worth keeping, so generated code still arrived with a
  comment above every second block — more prose than a developer can keep true as the code moves.
  `ts-clean` Rule 3 now sets a hard budget: at most one or two comments in a file, one sentence
  each, never more than two lines. A third comment is narration, and the fix is better names.

- **A comment may no longer point at anything a reader cannot verify.** Three new entries on the
  delete-on-sight list: the history of finished work (a closed ticket, a pull request, a commit,
  a past refactor), pointers into the codebase (a file path, a line number, "see the other
  service"), and the internals of another module. Files move, lines shift, and a ticket id means
  nothing to whoever opens the file next year. A durable external source — a published spec
  section or an upstream bug — still qualifies; an internal ticket id does not.

- **Public API JSDoc is no longer a standing exception.** A summary block over a well-named
  export repeats the name. Document an export only when correct use needs a constraint the types
  cannot carry.

- **The rule now reaches every code-writing path.** `clean-fullstack-architecture` carries it as
  a core principle and a validation checkbox, and the `coding` agent states the cap directly
  instead of deferring the whole question to `ts-clean`. Its own examples no longer narrate their
  elided function bodies.

## [0.27.0] - 2026-08-10

### Added

- **Codex plugin support.** The repository now includes a Codex marketplace manifest and a
  `.codex-plugin/plugin.json` manifest. Codex can install the same plugin source as Claude Code.
- **Codex command entry points.** The new `scaffold`, `explain`, `orchestrate`, and
  `orchestrate-quick` skills provide Codex equivalents for the Claude Code slash commands.
  The existing `prd` and `design-doc` skills provide the other two command equivalents.
- **Codex subagent protocol.** Both orchestrators map the shared workflow to persistent Codex
  planners, reviewers, and coding agents. Each verification run uses a fresh Codex agent.

### Changed

- **The workflow now reads both project instruction formats.** Agents read applicable
  `AGENTS.md` and `CLAUDE.md` files, so each host keeps its native project conventions.
- **The TanStack Start skill now has valid YAML frontmatter.** Quoting its description lets the
  Codex plugin validator parse `Cache-Control: public` without changing the skill behavior.
- **Every skill now follows the shared frontmatter schema.** The document skills no longer use
  optional Claude-only argument hints, and every skill passes the Codex skill validator.

## [0.26.0] - 2026-08-09

### Added
- **`.clean-architecture/` — one home for the PRD, the design doc, the roadmap, and the
  tickets.** Until now each document had its own convention and its own default location: the
  PRD at the root as `PRD.md`, the design doc as `design.md`, tickets under a `tickets/`
  directory nobody named, and the roadmap wherever the user pointed. Five agents and four
  skills each re-stated where to look, and a project that used any of those names for
  something else collided silently.

  Every document now lives in `.clean-architecture/` at the project root: `prd.md`,
  `design.md`, `roadmap.md`, and `tickets/<ID>-<slug>.md`. The folder is named after the
  plugin, so it collides with nothing a project would already have, and it groups the
  documents a person edits by hand away from the source tree.

  **Existing projects keep working.** Every agent and command falls back to the project root
  when the folder does not exist, so a repo with a root-level `prd.md` needs no migration.

- **`/scaffold` — create the folder and its stubs.** Takes an optional product name. It
  writes `prd.md`, `design.md`, and `roadmap.md` carrying the exact headings each skill
  expects, plus `tickets/TEMPLATE.md` copied from the `ai-planning-workflow` template. It
  never overwrites a file that exists, reports each file as created or kept, and invents no
  product content — the stubs are shape, not requirements.

  When it finds a root-level `prd.md`, `PRD.md`, `design.md`, `roadmap.md`, or `tickets/`, it
  **asks** before touching them, and moves them with `git mv` so history survives. A file left
  in place still resolves through the fallback.

  It ends by naming the next step rather than running it: `/prd` first, because every later
  document takes its vocabulary from the PRD, then `/design`, then `/orchestrate`.

### Changed
- **Every doc-path reference now points at the folder.** `feature-interviewer`,
  `implementation-planner`, and `plan-reviewer` read `.clean-architecture/prd.md` and
  `.clean-architecture/design.md`; `/orchestrate` defaults its roadmap argument to
  `.clean-architecture/roadmap.md` instead of asking for a path; `/orchestrate` and
  `/orchestrate-quick` write ticket status to `.clean-architecture/tickets/<ID>-*.md`; the
  `prd`, `design-doc`, and `ai-planning-workflow` skills name the folder as the write target;
  and `clean-writing` takes the ubiquitous language from the folder's PRD and design doc.
- **The interviewer names `/scaffold` when the PRD or the design doc is missing**, instead of
  only reporting the gap.
- **A brief with no ticket file lands in `.clean-architecture/tickets/<slug>-brief.md`**,
  replacing the loose root-level `feature-brief.md`.

## [0.25.0] - 2026-08-08

### Added
- **`/explain` — plain-language explanation of what is happening.** `clean-writing` governs how
  an agent writes when it already decided what to say. It does not cover the case where the user
  stops and asks what is going on. That question arrives constantly — after a change lands, when
  a stack trace appears, when someone opens an unfamiliar file — and the default answer is a tour
  of the code written for the person who just read it.

  The command takes a target and explains it: a file, a function, an error, a diff, a branch, a
  system, or a term. With no target it explains the work just done in this session. It writes for
  a competent developer who has never seen the codebase, unless the target names another audience
  ("explain to a designer").

  Three rules carry it. **Read before you explain** — open the files, run the command, read the
  output, and state in one line any claim that rests on something unverified; never invent a
  symbol, a flag, or a number. **Answer, then mechanism, then consequence** — a short answer the
  reader can stop at, the steps in the order they happen, then what to do about it. **Plain
  language** — every term of art defined in the sentence that first uses it, behaviour explained
  rather than syntax narrated, and code used as an anchor (`file.ts:42`) rather than as the
  explanation, so the text stands up if every code block is deleted.

  The command permits one labelled comparison, and only to name something the reader has no word
  for yet. That is the single documented exception to `clean-writing` Rule 9 in this plugin; the
  rest of the rule — no idiom, no humour, no hedging — still applies.

## [0.24.0] - 2026-08-07

### Added
- **`clean-writing` — the standard for every output a person reads.** The plugin governed the
  code an agent writes and the documents it produces, but nothing governed the prose. An agent
  ends a task holding a plan, twenty files, and a dozen tool results, then writes a summary that
  is obvious only from inside that context. The reader was never in it.

  The skill sets four rules. **Land the context before the point** — one to three opening
  sentences naming what this is about, what triggered it, and what it means for the reader.
  **Write Simplified Technical English** — twelve applicable ASD-STE100 writing rules: one idea
  per sentence, 20 words for an instruction and 25 for a description, active voice with a named
  actor, one word for one meaning, the plain common word, noun clusters capped at three, no
  telegraphic style, no jargon or idiom or metaphor or hedging, specific quantities, vertical
  lists, warning before instruction. (The standard's 900-word approved dictionary is not
  available to an agent, so the skill says so rather than claiming compliance.) **Use the
  project's ubiquitous language** — domain terms taken from `prd.md`, `design.md`, `CLAUDE.md`,
  the ticket, then the code, one term per concept, never a coined synonym. **Give the answer
  before the reasoning** — verdict first, failure reported as failure, the ask on the last line.

  The skill governs prose only. Code, identifiers, file paths, commands, quoted tool output, and
  the agents' fenced `json` contract blocks are explicitly exempt and stay byte-exact.

  Invoked directly, it runs in **re-pitch mode**: the last message failed, so rewrite it from
  scratch, add the context that was skipped, halve the length, and do not defend the original.
  Adapted from Matt Pocock's `wait-what` skill.

### Changed
- **Every human-directed output in the workflow now routes through `clean-writing`.** Each of the
  five agents gained a "Writing the …" section naming the rules that bite hardest for its own
  artifact — the discovery brief, the plan, the review verdict, the implementation summary, the
  verification report. `feature-interviewer`, `implementation-planner`, and `verify` gained the
  `Skill` tool to load it; `verify` loads it only when something fails or is skipped, since a
  clean all-pass run has no prose to govern.
- **`/orchestrate` and `/orchestrate-quick` load it before the first stage that produces user-
  facing text.** The orchestrator is the only stage that talks to the person, so the rules cover
  the task presented for approval, every `AskUserQuestion` question and option label, the recorded
  Decisions, the completion report, and every escalation or abort.
- **`prd`, `design-doc`, and `ai-planning-workflow` build on it.** Each states the split: those
  skills decide *what belongs in the document*, `clean-writing` decides *how each sentence reads*.
  The `/prd` and `/design` commands load both.

## [0.23.0] - 2026-08-04

### Added
- **The services / DTO / adapters boundary in `clean-fullstack-architecture`.** The skill called
  services "adapters for external systems" and then showed one returning the API's response
  straight through as a domain type. That is the inversion in name only: whatever the backend
  returns becomes the domain's model, so a field rename upstream lands in the business logic, the
  hooks, and the components. Three rules close it.

  **A service is a class with static methods** — one per external resource, named after the file,
  never instantiated, internals `private static`. Not a bag of loose exported request functions.
  **A service owns its DTOs**: the shape the wire actually speaks lives in `services/dto/` as
  type-only leaf modules importing nothing, written unedited — no bending the DTO toward the
  domain, no widening a model to fit the wire. **A service never returns a DTO**; every public
  method returns a domain model, a primitive, or `void`.

  **Domain logic never names a DTO.** `models/` is redefined as *domain* models — the domain's own
  vocabulary, real `Date`s, unions instead of nullable flags — and `domain/` may not take, return,
  or cast to a wire shape, so the domain stays valid when the API changes.

  A new **`adapters/`** layer sits between them, with its own dependency-matrix row: the only kind
  of module where a DTO and a domain model appear in the same file. Adapters are pure and
  synchronous, do no I/O, close the gaps the wire leaves (date parsing, field renaming, collapsing
  `null`/`undefined`/`""`, deriving discriminants), and raise on a missing required field rather
  than handing `undefined` to the domain. `services/ → adapters/ → services/dto/` is not a cycle
  because DTO modules are leaves; an adapter importing a *service* is one, and is forbidden.

  The implementation workflow now separates "define the domain model" from "define the DTO" —
  deriving the model from the API response is how DTOs end up masquerading as domain models.
  `references/dependency-rules.md` gains the forbidden patterns (DTO in the domain, service
  returning a DTO, adapter doing I/O), edge cases (identical DTO and model, per-endpoint shapes,
  multi-endpoint composition, vendor SDK types, write-direction mapping, testing a static-method
  service, server functions), and a step-by-step migration for a service that currently returns
  raw responses.

### Changed
- **Dependency matrix, validation checklist, and the data-fetching example** updated for the new
  layer: an `adapters` row and column, five new checklist items, and the oRPC pattern reworked so
  the hook calls `SlideService.list(...)` instead of the oRPC client — the client is transport the
  service uses, not a service itself.
- **`react-clean` Rule 3 and `ts-clean` Rule 1** re-cut their service examples as static-method
  classes returning domain models (`UserService.ts` exporting `class UserService`), replacing the
  object-literal `userService` that contradicted the new rule.
- **`coding` and `plan-reviewer` agents** name the new rules explicitly, so the reviewer flags a
  service that isn't a static-method class, a method returning a DTO, a DTO named outside
  `services/`/`adapters/`, and response mapping done anywhere but an adapter.

## [0.22.0] - 2026-07-31

### Added
- **`/orchestrate-quick` command.** `/orchestrate` is built for a task nobody has thought
  through yet: it interviews the user, puts decisions to them with `AskUserQuestion`, gates the
  review on a risk profile, and can spend two Opus reviewers on one plan. For a scoped change or
  a ticket someone already reasoned about, that is several minutes of human latency and a review
  tier the task never needed — and the only way to skip it was to drive the agents by hand. The
  quick command runs the same core with the human-in-the-loop stages removed: **plan → one
  review → implement → verify**, no interview, no `AskUserQuestion`, no review-skip or
  high-risk gating. The review always runs, exactly once, with a single Sonnet reviewer; the
  planner's `riskProfile` is ignored because there is no gate left for it to drive.

  Everything that makes the pipeline correct is unchanged: persistent planner / reviewer /
  coding agents resumed with `SendMessage`, a fresh `verify` per run, the same one-revision and
  one-fix caps, the same `escalate`/`aborted` policy, and the same rule that a task is never
  marked complete unless verification passed. It takes a **task description** as readily as a
  roadmap path — approval is asked for only when it picked the task from a roadmap, since that
  is the one choice verification cannot catch. When a stage escalates because the task actually
  did need decisions, it says so and points at `/orchestrate` rather than improvising an
  interview.

  The reviewer pre-reads concurrently with the planner, as in `/orchestrate` — but here the
  overlap is free of the usual caveat: with no gate that can skip the review, a pre-read is
  never discarded.

### Changed
- **The plan reviewer can pre-read without a context pack.** Its two-turn mode assumed turn 1
  always carried the planner's context pack, which is true when the pack was produced during the
  interview — but `/orchestrate-quick` has no interview to overlap, so it starts the reviewer
  beside the planner, before any pack exists. Turn 1 now says plainly what to do in that case:
  find the code the task touches yourself and read it.

## [0.21.0] - 2026-07-31

### Fixed
- **The reviewer's verdict token matched nothing the orchestrator parsed.** `plan-reviewer`
  wrote `CHANGES REQUESTED` (with a space) in its output format while `/orchestrate` branched on
  `"CHANGES_REQUESTED"`, so the agent was told two spellings in one turn and a rejected plan
  could be read as an unparseable block. The underscore form is now the only one, in the
  frontmatter description, the markdown heading, and the rules.
- **`/orchestrate` referred to a stage that does not exist.** The verify-passed branch sent the
  orchestrator to "Stage 3-of-§3 (mark Completed)" while Stage 3 is Implement; it now points at
  the **Mark Completed** step by name.
- **The verify spawn asked for an effort level the `Agent` tool cannot set.** "sonnet, low
  effort" is now just "sonnet" — the model is settable, the effort is not.

### Changed
- **The JSON contracts moved into the agent definitions.** `/orchestrate` already required that
  anything durable about an agent's behavior live in its definition rather than in a spawn
  prompt that is re-paid every time — but the planner's context pack / risk profile, the
  reviewer's verdict, and the coding agent's summary contracts existed *only* in the command,
  and none of those three agent files mentioned it had to emit JSON at all. Each contract now
  lives in its agent definition (with per-field guidance the command had no room for), and the
  command names the fields it parses instead of restating the shape. `verify` already did this.
- **A component may use a generic, side-effect-free hook.** `clean-fullstack-architecture`
  forbade `components/` from importing `hooks/` outright, which `react-clean` Rule 3 appeared to
  contradict — its example component consumes a TanStack Query hook — leaving the coding agent
  holding two skills that disagreed. The rule now turns on what a hook *brings in*: a media
  query, a debounce, or a focus trap is a UI utility and is allowed; any feature hook, any hook
  wrapping `useQuery`/`useMutation` or a service, and any hook with an outside side effect stay
  forbidden. Both skills also now say plainly that a component consuming a query hook is a
  **container** in the layer taxonomy — the two skills draw the naming line differently and
  agree on the substance.
- **`server/` is a declared feature layer.** The worked `socials/` example used
  `common/server/`, but the per-feature structure list and the validation checklist never
  mentioned it. It is now listed with its boundary — never imported from a component,
  container, or hook — and cross-referenced to `clean-tanstack-start`, which carries the same
  boundary as file suffixes.

### Removed
- **`.github/copilot-instructions.md`.** It described a `skills/<name>/` layout the repository
  stopped using when it became a plugin marketplace, and knew nothing about `agents/`,
  `commands/`, or the manifests — so it pointed anyone following it at the wrong directory.
- **`ai-planning-workflow/references/feedback-templates.md`.** Every template in it was already
  inline in `SKILL.md` at the phase that uses it, verbatim, including the response-patterns
  table. Two copies of the same text drift; the inline ones are the copies that get read.

## [0.20.0] - 2026-07-30

### Added
- **`ts-clean` Rule 4 — configuration in `.config.ts`, environment variables validated.**
  Nothing said where configuration was allowed to live, so per-environment values ended up
  inline at their use site and `process.env` was read from services, components, and route
  handlers alike — usually as `process.env.API_KEY!` or `process.env.PORT ?? ''`, which turns
  a missing variable into an `undefined` that surfaces hours later as a confusing runtime
  failure, or worse, a silent connection to the wrong place. The rule puts configuration
  values (base URLs, timeouts, limits, flags, credentials) in a `.config.ts` module named
  after what it configures and exporting one frozen object, makes those modules the **only**
  place `process.env` is read, and requires every required variable to be checked at module
  load and throw with its name — so a misconfigured deploy dies at startup instead of on the
  first request that needs the value. Optional variables get an explicit typed default with
  validated coercion (`Number(process.env.PORT)` is `NaN`, `Boolean('false')` is `true`), and
  secrets and connection targets are never defaulted at all. A project-wide schema validator
  (Zod, Valibot) satisfies the rule too — the requirement is failing loudly at startup, not a
  particular helper. Client-imported config may only carry framework-public (`VITE_`,
  `NEXT_PUBLIC_`) variables; secrets stay in a server-only module.

- **`clean-tanstack-start` Rule 3 — configuration split by environment.** `ts-clean` Rule 4
  puts configuration in `.config.ts` modules, which in a Start app is not enough on its own: a
  single config module holding a public base URL beside a Stripe secret is a module a component
  can import, and the secret ships to the browser. Configuration now splits along the same
  boundary as the rest of the app — client-safe values (framework-public `VITE_` vars, public
  URLs, limits, flags) in `*.config.ts`, secrets and internal targets in `*.config.server.ts`,
  which is a `.server.ts` file for every purpose including Rules 1 and 2. The dependency runs
  one way: server config may import client config and spread it; client config may never import
  server config, and no server config value may be re-exported back across the boundary. A
  value a component genuinely needs is by definition not a secret — it goes in the client-safe
  config behind a public-prefixed variable, or the component gets the behavior through a server
  function instead. The old Rules 3–5 renumbered 4–6.

### Changed
- **The coding agent and plan reviewer enforce Rule 4.** The coding agent's `ts-clean` line
  names the config-module and env-validation requirements, and the reviewer's plugin-skill
  check flags a planned `process.env` read outside a `.config.ts`, an unchecked required
  variable, or a defaulted secret as a **major** issue. The coding agent's
  `clean-tanstack-start` line names the client/server config split alongside the existing file
  categories.
- **The plan reviewer now checks plans against `clean-tanstack-start`.** Its plugin-skill
  checklist listed `clean-fullstack-architecture`, `ts-clean`, and `react-clean` but never the
  Start skill, so the coding agent was held to rules the reviewer never read — a plan could
  direct a `.server.ts` import from a component, an `await import()` of a server function, or a
  secret in a client-importable config and pass review. The skill is now in the list with its
  file split, config split, static-import, per-handler auth, and cache-header rules, and a
  secret in a client-importable config joins the examples of a **major** issue.

## [0.19.0] - 2026-07-28

### Added
- **`clean-tanstack-start` skill.** `ts-clean` governs how a TypeScript module is shaped, but
  nothing encoded where TanStack Start *server* code is allowed to live — so server functions
  ended up beside components, DB clients sat in unsuffixed modules a client file could import,
  and `ts-clean` Rule 2's code-splitting exception read as license to `await import()` a heavy
  server module. That last one is the dangerous case: a dynamic import hides the module from
  the build's environment shaking, so the handler is never replaced with an RPC stub and its
  server logic can ship to the browser. The skill encodes the framework's three-category file
  split (`.functions.ts` wrappers, `.server.ts` server-only helpers, plain `.ts` client-safe
  code) with a table of who may import what, forbids server-only code in any module a client
  file can reach, and states that server functions are imported statically only — explicitly
  overriding `ts-clean`'s exceptions, since server code is already excluded from the client
  bundle and there is no size to save. Code-split the calling component instead.

  Two safety rules from the same guide come with it, because both failure modes are invisible
  locally. **Every server function is its own auth boundary** — it is an endpoint reachable
  independently of whichever route renders the calling UI, so a route's `beforeLoad` guard is
  route UX, not the data boundary; the rule also separates authorization from authentication,
  since an owner or tenant id arriving in the validated payload is attacker-controlled input.
  And **`Cache-Control: public` is banned on any identity-dependent response** — it tells every
  CDN and proxy the body may be served to anyone, so one user's response gets replayed to the
  next; authenticated responses are `private` with a `Vary: Cookie, Authorization`, sensitive
  ones `no-store`.

  Source: https://tanstack.com/start/v0/docs/framework/react/guide/server-functions#file-organization

### Changed
- **The coding agent loads `clean-tanstack-start`.** Its skill list and its "obey the plugin's
  skills" rule now name the skill alongside `ts-clean` and `react-clean`, triggered by any file
  that defines, imports, or calls a `createServerFn` server function.

## [0.18.0] - 2026-07-26

### Changed
- **The planner sets direction instead of writing the code.** Its old rule — *"add
  `validateEmail(input: string): boolean` to `src/utils/validation.ts`"* is good — pushed
  plans down to the altitude of a diff, which pre-decided naming and structure the coding
  agent's skills are supposed to govern, and made every revision cycle re-litigate code
  nobody had written yet. The plan now opens with a **Direction** section (which module
  carries which responsibility, how data flows, what it mirrors) and lists **work items**
  as *Area / Intent / Direction / Done when* instead of *Files / Action*. Snippets, diffs,
  signatures, and type definitions are banned outright; naming, signatures, and the edits
  themselves belong to the coding agent. The counterweight rule is explicit — direction is
  not vagueness, so every item still names its files, the code to mirror, the API to use,
  and an observable outcome.
- **The planner researches best practices instead of deferring to the interview brief.**
  The old rule told it *not* to re-run research because the brief covered it — but the
  brief stops at the product/architecture altitude, so nothing checked the implementation
  approach against the official docs for the versions the project actually pins. The
  planner now researches the pinned libraries' current idioms and deprecations, the
  established pattern for the kind of work, and the security/a11y/performance practices
  that apply, and reports them in a **Best practices applied** section with sources. This
  happens on the **scout turn**, inside the dead air of the interview, so it costs tokens
  rather than wall-clock.
- **The interviewer must search the web, every time.** Research was step 4 of its process
  but nothing made it mandatory, so a confident-looking brief could be written from memory
  and quietly recommend an approach that was deprecated two versions ago. The step now
  spells out the five things to establish (current approach, library landscape, pitfalls,
  UX conventions, security/privacy/a11y/compliance), demands official docs over blog posts
  and version checks against what the codebase pins, and a new rule states plainly that a
  brief whose *Research findings* cite no external source is incomplete.
- **The reviewer polices altitude and grounding.** Its "Specificity" check asked whether
  signatures were *precise enough* — the exact thing plans no longer carry. It is replaced
  by an **Altitude** check that fires in both directions (dictated code is minor, or major
  when it would force a skill violation; a work item with no files, no approach, or no
  "done when" is major) and a **Best-practice grounding** check that treats an approach
  contradicting the pinned version's docs as major.
- **The coding agent owns the code-level decisions.** It now translates direction into
  code — choosing naming, signatures, and structure under the plugin's skills — and
  "deviating from the plan" is redefined as changing the approach, boundaries, or scope,
  never as picking a name the plan left open.

## [0.17.0] - 2026-07-26

### Added
- **`design-doc` Rule 5 — no tickets, no code references.** Rule 4 restricted which
  documents a design doc may *link* to, but nothing stopped the prose itself from citing a
  ticket or naming the implementation, so drafts came back anchored to `JIRA-1234`, "phase 2",
  and the component and file names of whatever happened to exist. The new rule bans tickets,
  issues, PRs, roadmap items, and milestones alongside file paths, component and function
  names, routes, props, CSS classes, config keys, and code snippets — surfaces and elements
  are named as the user sees them (the **project sidebar**, the **share dialog**), and a fact
  that only makes sense by pointing at a ticket or a file is not a design fact at all. The
  after-drafting checklist gained a matching check.

## [0.16.0] - 2026-07-24

### Added
- **`ts-clean` skill — clean TypeScript for every `.ts`/`.tsx` file.** The generic rules
  were living inside `react-clean`, so they only fired when someone was editing a
  component: a service could hide an `await import()` in a helper and a domain module could
  narrate itself line by line without ever tripping a rule. `ts-clean` now owns them —
  one module per file named after its primary export (`index.ts` stays a barrel), static
  top-of-file imports with the code-splitting / SSR / optional-dependency exceptions spelled
  out, and self-documenting code over comments with explicit keep and delete lists.

### Changed
- **`react-clean` is now the React layer on top of `ts-clean`.** Its old Rule 6 (static
  imports) and Rule 8 (comments) moved to `ts-clean`; the prop-drilling rule renumbered
  7 → 6, and Rule 1 kept only the component-specific part of one-module-per-file. A new
  prerequisite section tells the reader to load `ts-clean` as well, and the finishing
  checklist defers to its checklist instead of duplicating it.
- **The coding agent loads `ts-clean` for any TypeScript file**, not just React ones —
  `react-clean` is now described as stacking on top of it rather than repeating it.
- **The plan reviewer checks plans against the plugin's skills.** It gained the `Skill`
  tool and a new checklist item ("Plugin skill compliance"): it loads
  `clean-fullstack-architecture`, `ts-clean`, and `react-clean` for the code a plan touches,
  and treats a step that would force a violation as a **major** issue. Previously the coding
  agent was held to these rules but nothing checked the plan for steps that made them
  impossible to follow.

## [0.15.0] - 2026-07-23

### Added
- **`react-clean` Rule 8 — let the code explain itself.** The skill said nothing about
  comments, so generated components came back narrated line by line (`// handle the click`,
  `// --- state ---`, commented-out leftovers). The new rule defaults to zero comments and
  makes the fix a rename, a named constant, an extracted hook, a type, or a test — with an
  explicit keep-list for the things code genuinely cannot say: a *why*, a link to a spec or
  ticket, a justified deviation from another rule, a non-local warning, public API docs, and
  `TODO`s with a concrete referent. Added to the completion checklist.

## [0.14.0] - 2026-07-23

Latency pass on `/orchestrate`: the pipeline was serial end to end, and three stages were
redoing work an earlier stage had already done. Same gates, same caps, less wall-clock.

### Changed
- **The planner now scouts in parallel with the interview.** `/orchestrate` spawns
  `implementation-planner` in **scout-only** mode in the *same tool block* as
  `feature-interviewer`: it surveys the codebase and emits the context pack while the
  interview runs and the user answers `AskUserQuestion`, then parks. When the Decisions are
  settled they go to the *same* agent via `SendMessage` and it plans from files it has
  already read. Removes a full cold codebase exploration from the critical path.
- **The reviewer now pre-reads in parallel with the planning.** `plan-reviewer` is spawned
  in **pre-read only** mode as soon as the context pack exists, gated on the scout's
  provisional risk profile, so its mandatory file reading overlaps with the plan being
  written. The real review gate is still applied mechanically to the final risk profile; a
  pre-warmed reviewer that the gate then skips is simply dropped.
- **The coding agent no longer runs the full suite.** It does a *targeted* self-check on
  what it touched; `verify` remains the sole authoritative gate and runs the gating
  commands concurrently. Previously both ran everything — the coding agent sequentially —
  which duplicated the slowest block on the path, twice when a fix cycle happened.
- **Re-verification fails fast.** After a fix, `/orchestrate` hands the previously failing
  commands to the fresh `verify` agent, which runs those first and reports immediately if
  any still fails instead of running the rest of the suite for a result that cannot pass.
- **Normal-risk plan review runs on Sonnet**; the two high-risk lenses stay on Opus.
- **Thinner spawn prompts.** The verify agent's judging and output-hygiene rules and its
  JSON contract, and the coding agent's skill obligations, moved out of the `/orchestrate`
  spawn prompts into the agent definitions, where they are not re-paid on every spawn.

### Added
- **`e2eCommand` in the context pack.** The planner reports the project's e2e command (or
  `"none"`), and `/orchestrate` passes it to every `verify` spawn. When supplied, `verify`
  skips its e2e discovery sweep entirely instead of globbing for `playwright.config.*`,
  `cypress/`, and `e2e/` on every run.
- **Two-turn modes** documented in the `implementation-planner` (scout → plan) and
  `plan-reviewer` (pre-read → review) agent definitions, so both behave correctly whether
  they are spawned early or in the classic one-turn way.

## [0.13.0] - 2026-07-23

### Added
- **`verify` agent runs end-to-end tests when the project has them.** It now discovers an
  e2e suite on its own (scripts matching `e2e`/`cypress`/`playwright`, `playwright.config.*`
  / `cypress.config.*` / `wdio.conf.*` / `.detoxrc*`, `e2e/` and `cypress/e2e/` directories,
  `Makefile`/`tox` e2e targets) and runs it even when the handed-over verification commands
  omit it. A project with no e2e suite is reported as such, not as a failure.
- **E2E-aware run strategy.** Fast checks (unit tests, lint, typecheck, build) still go out
  as one concurrent batch; e2e runs afterwards on its own with the maximum timeout, since
  those suites bind ports, share a database, and drive a browser. The agent lets the
  project's own tooling start the app (Playwright `webServer`, `start-server-and-test`) and
  prefers headless/CI invocations over watch modes.
- **`skipped` verification results.** An e2e suite that cannot run for environment reasons —
  browsers not installed, no display, a missing service or credentials — is reported as
  skipped with the reason rather than as a pass or a code failure. `/orchestrate` carries a
  `skipped` field in the verify JSON contract and requires skipped commands to be named in
  the completion report.

### Changed
- `verify` may re-run a **single** e2e spec once to separate a flake from a real break, and
  must report the retry; whole-suite re-runs remain forbidden. Failure extraction now calls
  for the failing spec plus the assertion or selector, and explicitly bans pasting e2e
  traces.

## [0.12.0] - 2026-07-23

### Added
- **`react-clean` Rule 6 — static imports at the top of the file.** Bans `await import()` /
  in-function `require()` as a default, with a narrow exception list (route- and
  component-level code splitting via `lazy`, a heavy dependency on a rare path, browser-only
  modules under SSR, genuinely optional dependencies). Exceptions must sit at module scope
  and carry a one-line comment explaining why they are dynamic.
- **`react-clean` Rule 7 — no prop drilling.** A prop a component only relays to a child is
  a refactor signal: prefer composition (`children`/slot props), then moving state down or
  the consumer up, then context for truly global values, then a store for server/app-wide
  state. One level of pass-through is fine; two or more with untouched intermediates is not.
  Notes the overlap with the Rule 5 props ceiling — a component with many relayed props
  should be taking `children`.

### Changed
- Extended the `react-clean` skill description and finishing checklist to cover both new
  rules.

## [0.11.0] - 2026-07-13

### Changed
- **`feature-interviewer` agent is now selective about what it escalates.** It surfaces an
  open decision to the user *only* when the choice genuinely needs them: a significant
  architecture decision, a library or framework choice the codebase doesn't already dictate,
  a point of genuinely unclear intent, or a contradiction with `prd.md`/`design.md`. Every
  other choice it resolves itself and records as an assumption. Adds an explicit "what clears
  the bar" filter, a `Type:` tag and "why it needs you" line per decision, and makes
  returning zero open decisions a valid outcome — biasing toward a short, high-stakes brief
  over a long list of choices the user doesn't care about.

## [0.10.0] - 2026-07-13

### Added
- **`prd` skill.** Guides creating or updating a product requirements document — the
  requirements from the user's point of view, kept durable as tickets and implementation
  change underneath. Enforces product-only content (no ticket, code, technology, or
  migration references), cohesive per-product-area descriptions with stable anchor codes
  instead of atomic per-feature checklists, and positive framing of behavior. Prescribes a
  fixed eight-section structure and rules for revising a living PRD in place.
- **`/prd` command.** Loads the `prd` skill and drives it to create or update a product
  requirements document for a given product or feature. Takes the target as an argument and
  prompts for one if omitted.

## [0.9.0] - 2026-07-10

### Fixed
- **The `coding` agent can now actually invoke skills.** Added the `Skill` tool to the
  agent's `tools` list — previously it was told to "invoke the `react-clean` skill" but
  had no `Skill` tool, so the instruction was impossible to follow.

### Changed
- **`coding` agent loads skills up front.** It now invokes the `clean-fullstack-architecture`
  skill before writing any production code and the `react-clean` skill before touching any
  React file, handles namespaced skill names, and invokes each skill once per session rather
  than per file. The `/orchestrate` implement-stage prompt was updated to match.

## [0.8.1] - 2026-07-10

### Changed
- **`/design` command no longer hardcodes `design.md`.** Clarifies that the skill decides
  the filename and whether the design lives in one doc or splits across several
  cross-referenced docs (`design.md` is only the conventional default), and to update an
  existing design doc in place rather than create a duplicate.

## [0.8.0] - 2026-07-10

### Added
- **`/design` command.** Loads the `design-doc` skill and drives it to create or update a
  design doc for a given screen, surface, or flow. Takes the target as an argument and
  prompts for one if omitted.

## [0.7.0] - 2026-07-10

### Added
- **`design-doc` skill.** Guides creating a design doc (`design.md`) that specifies how a
  product looks and behaves — the intended end state, not how to build it. Enforces four
  core rules (target-state not procedure, structural altitude not pixel-level, no changelog,
  split by concern with cross-references), a standard document shape, a per-surface
  layout → content → states → responsive pattern, and style rules favoring ASCII layout
  diagrams and state tables.

## [0.6.0] - 2026-07-10

### Added
- **`react-clean` skill — Rule 5 "Keep components and their props small."** Adds hard size
  ceilings that trigger a refactor: ≤ 150 lines per component file, ≤ 50 lines of returned
  JSX, ≤ 3 levels of JSX nesting, and one reason to render. Adds props limits: ≤ 5 props,
  with an ordered remediation (composition via `children`/slots → group related props into
  one object → split the component) and a ban on boolean-flag soup in favor of a single
  `variant` union. Cohesive inputs (a typed props object, `children`, event handlers) are
  explicitly exempt from the props budget.
- Two matching checklist items and an updated skill `description` covering the new limits.

## [0.5.0] - 2026-07-09

### Changed
- **`/orchestrate` core is now persistent-agent, main-loop driven.** The plan → review →
  revise → implement → verify pipeline no longer runs as a background `Workflow` script;
  it runs in the main loop with the planner, plan-reviewer, and coding agents each spawned
  **once** via `Agent` and resumed across revision/fix cycles via `SendMessage`. Their
  context (the plan, the files they read, prior reasoning) now survives each cycle instead
  of being re-sent, cutting the token/latency cost of the revision and fix loops. `verify`
  is still spawned fresh each run (cheap Sonnet; a clean re-run is desired).
- Because there is no schema enforcement in the main loop, each core agent now ends its
  reply with a single fenced `json` block (context pack + risk profile, review verdict,
  implementation summary, verify results) that the orchestrator parses to drive control
  flow. The deterministic gates are preserved as explicit, mechanical rules: the review-skip
  gate (≤2 files, no dep, no API, criteria auto-checkable), the high-risk parallel-lens test
  (new API/dep or >5 files), the single revision cap, and the single fix cap are unchanged.

### Removed
- Deleted `workflows/orchestrate-core.js` and the `workflows/` directory. The deterministic
  workflow is fully replaced by the persistent-agent main-loop pipeline above.

## [0.4.2] - 2026-07-08

### Changed
- Agent invocations now use plugin-namespaced `subagent_type` names. `orchestrate-core`
  spawns `clean-architecture:{implementation-planner,plan-reviewer,coding,verify}`, and the
  `/orchestrate` command spawns `clean-architecture:feature-interviewer`. This prevents
  collisions with same-named agents from other plugins or the host project now that both
  bare and namespaced names are registered.

### Removed
- Dropped the stale `feature-interviewer` agent reference from the `ai-planning-workflow`
  skill's interview phase.

## [0.4.1] - 2026-07-08

### Fixed
- `orchestrate-core` now parses `args` when it arrives as a JSON string, not just as an
  object. Previously a string-typed payload made `args.task` undefined, so the planner
  received an untitled task with no criteria and no interview context.
- `orchestrate-core` Verify stage is now baseline-aware and output-hygienic. It judges
  pass/fail by whether the change *introduced* failures rather than by absolute exit codes
  (a command non-zero only due to a known pre-existing baseline, e.g. `tsc -b`, counts as a
  pass at/below baseline), gates only on the project's named gating commands, and caps each
  result's output to a few lines with a single StructuredOutput call — preventing the
  oversized-output fail loop that could exhaust the retry cap and crash the workflow.

## [0.4.0] - 2026-07-08

### Added
- `verify` agent: a lightweight, run-only verification agent (Bash-focused, no code edits)
  on a cheaper model. The `orchestrate-core` Verify stage now uses it instead of the full
  `coding` agent.

### Changed
- **Model & effort tiering** in `orchestrate-core`: planning runs on Opus at high effort;
  review, revision, implementation, and the fix loop stay on Opus; verification runs on
  Sonnet at low effort. This cuts cost on the loop-prone verify stage without touching
  reasoning-heavy stages.
- **Risk-scaled review**: when the review gate requires a review, high-risk plans (new
  public API, new dependency, or >5 files touched) now get two parallel reviewers with
  distinct lenses (correctness vs. codebase-fit), merged into one verdict; normal-risk plans
  keep the single holistic reviewer. Same wall-clock, broader coverage where risk is highest.

## [0.3.0] - 2026-07-08

### Added
- Deterministic `orchestrate-core` workflow (`workflows/orchestrate-core.js`): a
  code-controlled plan → gated review → single revision → implement → verify (with a
  fix-and-recheck loop) pipeline that returns a structured `completed`/`escalate`/`aborted`
  result.

### Changed
- `/orchestrate` is now a **hybrid**: the interactive shell (task selection, approval, and
  the interview decisions) runs in the main loop, then hands the mechanical core off to the
  `orchestrate-core` workflow. The review skip gate and the verify/fix loop are now
  deterministic code rather than model judgment.

## [0.2.0] - 2026-07-08

### Added
- `feature-interviewer` agent and an interview/challenge stage before planning, so
  non-trivial features settle their open decisions with the user before a plan is written.
- `/orchestrate` command: picks the next actionable roadmap task and drives it through
  interview → plan → review → implement.
- `react-clean` skill: rules for clean React components (one component per file, at most one
  `useEffect`, no data-layer access from components).

## [0.1.0] - 2026-07-07

### Added
- Initial packaging as a Claude Code plugin.
- `clean-fullstack-architecture` skill with hexagonal dependency rules.
- `ai-planning-workflow` skill.
- `implementation-planner`, `plan-reviewer`, and `coding` agents.

[0.5.0]: https://github.com/husdeli/skills/releases/tag/v0.5.0
[0.4.1]: https://github.com/husdeli/skills/releases/tag/v0.4.1
[0.4.0]: https://github.com/husdeli/skills/releases/tag/v0.4.0
[0.3.0]: https://github.com/husdeli/skills/releases/tag/v0.3.0
[0.2.0]: https://github.com/husdeli/skills/releases/tag/v0.2.0
[0.1.0]: https://github.com/husdeli/skills/releases/tag/v0.1.0
