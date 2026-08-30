# husdeli skills

A Claude Code and Codex plugin marketplace for architecture rules and reviewed development
workflows.

## Install

In Claude Code:

```
/plugin marketplace add husdeli/skills
/plugin install clean-architecture@husdeli-skills
```

In Codex:

```shell
codex plugin marketplace add husdeli/skills
codex plugin add clean-architecture@husdeli-skills
```

Start a new session after installation so the skills become available.

## Where your product docs live

Every document the plugin reads or writes sits in one folder at your project root:

```
.clean-architecture/
  prd.md              product requirements — what the product does and why
  design.md           design doc — how each surface looks and behaves
  roadmap.md          the ordered task list the orchestrator picks from
  tickets/
    TEMPLATE.md       copy per task, named <ID>-<slug>.md
    todo/             SW-001-user-login.md
    in-progress/      SW-002-session-timeout.md
    done/             SW-003-password-reset.md
```

A ticket moves between the three status folders as the work progresses, and its `Status` field
always names the folder it sits in. The commands move it for you: into `in-progress/` when an
orchestrator starts the task, into `done/` when verification passes. A project that already
keeps its tickets in one flat folder keeps working — `/scaffold` offers the migration, and
never forces it.

Run **`/scaffold`** in Claude Code or **`$clean-architecture:scaffold`** in Codex to create it.
Every agent falls back to the project root when a project already keeps these documents there.

## What's in the `clean-architecture` plugin

### Skills
- **clean-fullstack-architecture** — Clean Code + Hexagonal Architecture with strict
  dependency rules across all layers; domain-cohesive feature grouping. Services are classes
  of static methods that own the DTOs their API speaks and never return one; domain logic
  names only domain models; an `adapters/` layer is the single place the two shapes meet.
- **ai-planning-workflow** — Feedback-driven ticket → plan → implement workflow with
  design-agreement and iteration-logging checkpoints.
- **ts-clean** — Framework-agnostic rules for any `.ts`/`.tsx` file: one module per file
  named after its primary export, dot notation for the modules that carry an architecture
  role (`user.service.ts`, `user.repository.ts`, `user.dto.ts`) while plain modules keep
  plain names, static top-of-file imports (with the code-splitting /
  SSR / optional-dependency exceptions spelled out), self-documenting code over
  comments (a hard cap of one or two per file, one sentence each, and never a pointer to a
  file, a line, or a finished ticket), and configuration extracted into `.config.ts` modules that are the only place
  `process.env` is read — required variables throw by name when missing, optional ones get
  an explicit typed default, and secrets are never defaulted.
- **react-clean** — The React layer on top of `ts-clean`: one component per file, at most
  one `useEffect`, no data-layer access from components, size and props ceilings, no prop
  drilling (compose instead), and the react.dev "You Might Not Need an Effect"
  anti-patterns.
- **clean-tanstack-start** — The TanStack Start layer on top of `ts-clean`: the
  `.functions.ts` / `.server.ts` / plain `.ts` file split, server-only modules kept out of
  anything a client file can import, configuration split the same way (client-safe values in
  `*.config.ts`, secrets in `*.config.server.ts`, which server code may read from but never
  the reverse), and server functions imported statically only — never
  `await import()`, which defeats environment shaking and can leak server logic into the
  client bundle. Plus the two safety rules: every server function is its own auth boundary
  (a route `beforeLoad` guard isn't the data boundary), and no `Cache-Control: public` on
  an identity-dependent response.
- **clean-writing** — The standard for every output a person reads: a brief, a plan, a review
  verdict, a report, a question, a PRD, a ticket, a chat reply. Context before the point,
  ASD-STE100 Simplified Technical English (one idea per sentence, active voice with a named
  actor, one word for one meaning, no jargon or metaphor), the project's ubiquitous language
  from the PRD, the design doc, `AGENTS.md`, and `CLAUDE.md`, and the answer before the reasoning.
  Governs prose only — code, identifiers, paths, quoted output, and the agents' `json` blocks stay exact.
  Invoked directly, it re-pitches a message that didn't land. Every agent, command, and
  document skill in this plugin routes its human-facing output through it.
- **design-doc** — Create or update a design doc specifying how a screen, surface, or flow
  looks and behaves — the intended end state, not how to build it.
- **prd** — Create or update a product requirements document: product-only content,
  cohesive per-area descriptions with stable anchor codes, and positive framing.

### Agents
- **feature-interviewer** — reads the PRD and design doc, researches the feature on the web,
  and returns a Discovery Brief that challenges the idea with open decisions and options.
- **implementation-planner** — turns a task + codebase + researched best practices into a
  directional plan: where the work lives, what each item must achieve, which approach to
  follow — and no code for the coding agent to copy.
- **plan-reviewer** — reviews a plan for correctness and convention alignment, and returns
  `APPROVED` or `CHANGES_REQUESTED`.
- **coding** — implements a work brief and runs a targeted self-check. The brief is an approved
  plan from either orchestrator, or a request `/code` sends with no plan at all.
- **verify** — runs the project's gating commands (tests, lint, typecheck, e2e when there is
  one) concurrently and reports pass/fail per command. Writes no code.

### Commands and Codex skills
- **/scaffold** — creates `.clean-architecture/` with stub files for the PRD, the design doc,
  the roadmap, a ticket template, and the `todo/`, `in-progress/`, and `done/` ticket folders.
  Never overwrites an existing file, and offers to move a root-level `prd.md`, `design.md`, or
  `tickets/` into the folder with `git mv` — including sorting a flat tickets folder into the
  three status folders.
- **/plan** — turns a request into the documents the rest of the plugin reads: it interviews
  with the **feature-interviewer** agent, settles the open decisions with you, then updates the
  PRD and the design doc, appends the roadmap tasks, and writes one ticket per task into
  `tickets/todo/`. It writes no code and sets no status past pending — `/orchestrate` takes it
  from there.
- **/orchestrate** — picks the next actionable roadmap task and drives it through
  interview → plan → review → implement → verify using the five agents above.
- **/orchestrate-quick** — the short pipeline for a task that is already well understood:
  plan → one review → implement → verify, with no interview and no review gating. Takes a
  task description or a roadmap/ticket path.
- **/code** — hands your request straight to the **coding** agent, which loads the coding skills
  itself. One agent, no planner, no reviewer, no verify agent: it finds the files, writes the
  change, runs a targeted self-check, and the command reports what it did and what nobody ran.
  Use it for a fix or a small feature you already understand; it hands off to
  `/orchestrate-quick` or `/orchestrate` when the request turns out to need a plan.
- **/design** — loads the `design-doc` skill to create or update a design doc for a given
  screen, surface, or flow.
- **/prd** — loads the `prd` skill to create or update a product requirements document for
  a given product or feature.
- **/explain** — explains what is happening in plain language: the work you just did, a
  file, an error, a diff, or a concept. Reads the code before explaining, defines every
  term of art on first use, and treats code as an anchor rather than the explanation.

Use these equivalents in a Codex prompt:

| Claude Code | Codex |
| --- | --- |
| `/scaffold [product]` | `$clean-architecture:scaffold [product]` |
| `/orchestrate [roadmap]` | `$clean-architecture:orchestrate [roadmap]` |
| `/orchestrate-quick [task]` | `$clean-architecture:orchestrate-quick [task]` |
| `/code [request]` | `$clean-architecture:code [request]` |
| `/plan [request]` | `$clean-architecture:plan [request]` |
| `/design [target]` | `$clean-architecture:design-doc [target]` |
| `/prd [target]` | `$clean-architecture:prd [target]` |
| `/explain [target]` | `$clean-architecture:explain [target]` |

Each Codex entry point lives in `codex-skills/`, and each one reads the shared source in
`commands/` or `skills/`. Claude Code scans `skills/` only, so no Codex instruction reaches a
Claude session.

## Repo layout

```
.claude-plugin/marketplace.json     # marketplace manifest (lists plugins)
.agents/plugins/marketplace.json    # Codex marketplace manifest
plugins/
  clean-architecture/
    .claude-plugin/plugin.json       # Claude Code plugin manifest
    .codex-plugin/plugin.json        # Codex plugin manifest
    skills/                          # shared rules and document skills, read by both runtimes
    codex-skills/                    # Codex entry points, never loaded by Claude Code
    agents/                          # agent definitions and Codex role contracts
    commands/                        # Claude commands and shared workflow sources
```

## Local development

To test changes in Claude Code without publishing:

```
/plugin marketplace add /path/to/this/repo
/plugin install clean-architecture@husdeli-skills
```

To test changes in Codex without publishing:

```shell
codex plugin marketplace add /path/to/this/repo
codex plugin add clean-architecture@husdeli-skills
```

After a Claude Code edit, run `/plugin marketplace update husdeli-skills`.
After a Codex edit, run `codex plugin add clean-architecture@husdeli-skills` and start a new session.
Keep both plugin manifest versions equal when publishing a release.
