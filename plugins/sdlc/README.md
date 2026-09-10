# sdlc

Plan, review, implement, and verify a change, with clean architecture rules for TypeScript,
React, and TanStack Start. Ten commands drive six agents, and ten skills hold the rules they
all follow.

Part of the [husdeli skills](../../README.md) marketplace.

## Install

In Claude Code:

```
/plugin marketplace add husdeli/skills
/plugin install sdlc@husdeli-skills
```

In Codex:

```shell
codex plugin marketplace add husdeli/skills
codex plugin add sdlc@husdeli-skills
```

Start a new session after installation so the skills become available.

## Layout

```
.claude-plugin/plugin.json       # Claude Code plugin manifest
.codex-plugin/plugin.json        # Codex plugin manifest
skills/                          # shared rules and document skills, read by both runtimes
codex-skills/                    # Codex entry points, never loaded by Claude Code
agents/                          # agent definitions and Codex role contracts
commands/                        # Claude commands and shared workflow sources
```

## Where your product docs live

Every document the plugin reads or writes sits in one folder — the **docs root**. By default it
is `.sdlc/` at your project root:

```
.sdlc/
  prd.md                product requirements — what the product does and why
  roadmap.md            the ordered task list the orchestrator picks from, grouped by epic
  designs/
    overview.design.md  design docs — how the solution works, end to end. One file
    checkout.design.md  per subject, named <subject>.design.md
    …
  tickets/
    TEMPLATE.md         copy per task, named <EPIC>-<NNN>-<slug>.md
    todo/               AUTH-001-user-login.md
    in-progress/        AUTH-002-session-timeout.md
    done/               BILLING-001-invoice-export.md
```

Each kind of document gets its own folder once there can be more than one of it. A design doc
covers one subject — a system, a service, a flow, an integration, a rule, or a screen — and
stays in `designs/` for the life of the project. `overview.design.md` is the entry point that
names the parts of the whole solution and points at the rest.

A ticket moves between the three status folders as the work progresses, and its `Status` field
always names the folder it sits in. The commands move it for you: into `in-progress/` when an
orchestrator starts the task, into `done/` when verification passes. A project that already
keeps its design docs or its tickets in one flat folder keeps working — `/scaffold` offers the
migration, and never forces it.

Every ticket belongs to an **epic** — a named group of tasks that deliver one feature. The
roadmap holds one section per epic, the epic's code prefixes every ticket ID under it, and the
numbering restarts at 001 in each epic. That is what keeps two branches apart: each plans into
its own epic, so both can add a first ticket and neither overwrites the other on merge.

Run **`/scaffold`** in Claude Code or **`$sdlc:scaffold`** in Codex to create it.
Every agent falls back to the project root when a project already keeps these documents there.

### Or keep them in an Obsidian vault

`/scaffold` asks where the docs root goes: in the repository as `.sdlc/`, or in a folder outside
it. Point it at an Obsidian vault and it writes the structure there, then writes a pointer file
at your project root so every command still finds it:

```json
{
  "root": "~/Vaults/Personal/Acme",
  "kind": "vault"
}
```

Every command and agent resolves `.sdlc.json` before it reads anything, so `/plan`,
`/orchestrate`, `/prd`, `/design`, and `/review` work against the vault exactly as they work
against `.sdlc/`. A ticket still moves from `todo/` to `in-progress/` to `done/` as the
orchestrator builds it.

Inside a vault the documents are written the way Obsidian reads them, and nothing else changes:

- **No folder starts with a dot**, because Obsidian hides those. The docs root is named after
  the product, and it is always a folder inside the vault, never the vault root.
- **Fields become properties.** `**Status**: In Progress` under the title becomes
  `status: In Progress` in the frontmatter, so a ticket is queryable in Bases or Dataview. The
  property is the record the commands rewrite.
- **References become wikilinks.** The roadmap cites `[[AUTH-001-user-login]]`, and a design doc
  cites `[[prd]]`. Obsidian resolves them by name, so backlinks and the graph work, and a link
  survives the ticket moving between status folders.
- **No `.gitkeep`, and no `git mv`** where git does not track the folder.

The `product-docs` skill holds these rules, and the plugin loads it whenever the destination is a
vault. Pick **In the repository** at the prompt and none of it applies.

## What's in it

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
- **design-doc** — Create or update a design doc specifying how a solution works: the parts
  it is built from, how work flows through it end to end, the states it reaches, and the
  limits it holds within. The subject is a system, a service, a flow, an integration, a rule,
  or a screen — a user interface is one case, not the default. One file per subject in
  `designs/`, named `<subject>.design.md`, so the file name says what it specifies. The doc states the intended
  end state, not how to build it.
- **frontend-design** — Agree what a screen looks like before it is built. Reads the PRD, the
  design doc, and the design system the codebase already has, publishes a static mockup as an
  Artifact — every state, the small screen, placeholder data, nothing wired up — and iterates
  until the user agrees. Then it records the decisions, so the code is written from an agreement
  and not from a picture nobody wrote down. It writes no production code.
- **prd** — Create or update a product requirements document: product-only content,
  cohesive per-area descriptions with stable anchor codes, and positive framing.
- **product-docs** — Where the documents live and how each destination writes them: the docs
  root, the `.sdlc.json` pointer file, and the Obsidian-vault conventions — folder naming,
  frontmatter properties, wikilinks, and when a move uses `git mv`. Every command and agent
  resolves the docs root through it, so one project can keep its documents in the repository and
  the next can keep them in a vault.

### Agents
- **feature-interviewer** — reads the PRD and design doc, researches the feature on the web,
  and returns a Discovery Brief that challenges the idea with open decisions and options.
- **implementation-planner** — turns a task + codebase + researched best practices into a
  directional plan: where the work lives, what each item must achieve, which approach to
  follow — and no code for the coding agent to copy.
- **plan-reviewer** — reviews a plan for correctness and convention alignment, and returns
  `APPROVED` or `CHANGES_REQUESTED`.
- **code-reviewer** — reads the code that was just written — a working-tree diff, a branch, or
  named files — and returns `APPROVED` or `CHANGES_REQUESTED`. Checks the acceptance criteria,
  correctness, scope, the plugin's skills, the codebase's conventions, error handling, tests,
  and secrets, and confirms every issue in the file before reporting it. Writes no code.
  Verification answers "does it pass?"; this answers "is it the right code, and all of it?".
- **coding** — implements a work brief and runs a targeted self-check. The brief is an approved
  plan from either orchestrator, or a request `/code` sends with no plan at all.
- **verify** — runs the project's gating commands (tests, lint, typecheck, e2e when there is
  one) concurrently and reports pass/fail per command. Writes no code, and reviews none either.

### Commands and Codex skills
- **/scaffold** — asks where the docs root goes — in the repository as `.sdlc/`, or in a folder
  outside it such as an Obsidian vault — then creates it with stub files for the PRD, the design
  doc, the roadmap, a ticket template, the `designs/` folder, and the `todo/`, `in-progress/`,
  and `done/` ticket folders. An outside folder gets a `.sdlc.json` pointer file at the project
  root, and a vault gets the Obsidian shape: frontmatter properties, wikilinks, and no
  dot-folders. Never overwrites an existing file, and offers to move a root-level
  `prd.md`, `design.md`, or `tickets/` into the folder with `git mv` — including sorting a flat
  tickets folder into the three status folders, moving loose `*.design.md` files into
  `designs/`, and renaming a lone `design.md` to `designs/overview.design.md`. It also offers to
  migrate a project-wide ticket scheme (`SW-001`, `SW-002`, …) onto epic-prefixed IDs, after it
  shows you the epic grouping and you approve it.
- **/plan** — turns a request into the documents the rest of the plugin reads: it interviews
  with the **feature-interviewer** agent, settles the open decisions with you, then updates the
  PRD and the design docs, appends the roadmap tasks under their epic, and writes one ticket per
  task into `tickets/todo/`. It writes no code and sets no status past pending — `/orchestrate` takes it
  from there.
- **/orchestrate** — offers you every roadmap task whose dependencies are satisfied, asks which
  one to build and whether it gets end-to-end tests, then drives it through
  interview → plan → review → implement → verify and code review using the six agents above.
  The verify stage runs the gating commands and the code review side by side, and the task is
  marked complete only when the commands pass and the review returns `APPROVED`.
- **/orchestrate-quick** — the short pipeline for a task that is already well understood:
  plan → one review → implement → verify and code review, with no interview and no review
  gating. Takes a task description or a roadmap/ticket path. It asks nothing: end-to-end tests
  default to no, and it reports that default.
- **/code** — hands your request straight to the **coding** agent, which loads the coding skills
  itself. One agent, no planner, no reviewer, no verify agent: it finds the files, writes the
  change, runs a targeted self-check, and the command reports what it did and what nobody ran.
  Use it for a fix or a small feature you already understand; it hands off to
  `/orchestrate-quick` or `/orchestrate` when the request turns out to need a plan. When the
  request changes what a user sees, it runs the `frontend-design` skill first and waits for you
  to agree the mockup before the coding agent starts.
- **/review** — reviews code that already exists with the **code-reviewer** agent: the
  uncommitted changes by default, or a path, a branch, a commit range, or a ticket you name.
  Reports the verdict and the defects, each with its file and line. Add `fix` to hand the
  blocking issues to the coding agent and re-review the result once. Use it for work that never
  went through an orchestrator — a `/code` change, code you wrote by hand, a branch to read
  before a pull request.
- **/design** — loads the `design-doc` skill to create or update
  `designs/<subject>.design.md` for a given system, service, flow, integration, or screen.
- **/frontend-design** — loads the `frontend-design` skill to agree the look of a screen, a
  component, or a flow before it is built: it publishes a static mockup as an Artifact, iterates
  with you, and records what you agreed. It writes no production code — `/code` builds it after.
- **/prd** — loads the `prd` skill to create or update a product requirements document for
  a given product or feature.
- **/explain** — explains what is happening in plain language: the work you just did, a
  file, an error, a diff, or a concept. Reads the code before explaining, defines every
  term of art on first use, and treats code as an anchor rather than the explanation.

Use these equivalents in a Codex prompt:

| Claude Code | Codex |
| --- | --- |
| `/scaffold [product]` | `$sdlc:scaffold [product]` |
| `/orchestrate [roadmap]` | `$sdlc:orchestrate [roadmap]` |
| `/orchestrate-quick [task]` | `$sdlc:orchestrate-quick [task]` |
| `/code [request]` | `$sdlc:code [request]` |
| `/review [target]` | `$sdlc:review [target]` |
| `/plan [request]` | `$sdlc:plan [request]` |
| `/design [target]` | `$sdlc:design-doc [target]` |
| `/frontend-design [target]` | `$sdlc:frontend-design [target]` |
| `/prd [target]` | `$sdlc:prd [target]` |
| `/explain [target]` | `$sdlc:explain [target]` |

Each Codex entry point lives in `codex-skills/`, and each one reads the shared source in
`commands/` or `skills/`. Claude Code scans `skills/` only, so no Codex instruction reaches a
Claude session.
