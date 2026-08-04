# husdeli skills

A Claude Code plugin marketplace bundling architecture and workflow skills plus the
agents that drive them.

## Install

In Claude Code:

```
/plugin marketplace add husdeli/skills
/plugin install clean-architecture@husdeli-skills
```

That's it — the skills and agents below become available in every session.

## What's in the `clean-architecture` plugin

### Skills
- **clean-fullstack-architecture** — Clean Code + Hexagonal Architecture with strict
  dependency rules across all layers; domain-cohesive feature grouping. Services are classes
  of static methods that own the DTOs their API speaks and never return one; domain logic
  names only domain models; an `adapters/` layer is the single place the two shapes meet.
- **ai-planning-workflow** — Feedback-driven ticket → plan → implement workflow with
  design-agreement and iteration-logging checkpoints.
- **ts-clean** — Framework-agnostic rules for any `.ts`/`.tsx` file: one module per file
  named after its primary export, static top-of-file imports (with the code-splitting /
  SSR / optional-dependency exceptions spelled out), self-documenting code over
  comments, and configuration extracted into `.config.ts` modules that are the only place
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
- **design-doc** — Create or update a design doc specifying how a screen, surface, or flow
  looks and behaves — the intended end state, not how to build it.
- **prd** — Create or update a product requirements document: product-only content,
  cohesive per-area descriptions with stable anchor codes, and positive framing.

### Agents
- **feature-interviewer** — reads `prd.md`/`design.md`, researches the feature on the web,
  and returns a Discovery Brief that challenges the idea with open decisions and options.
- **implementation-planner** — turns a task + codebase + researched best practices into a
  directional plan: where the work lives, what each item must achieve, which approach to
  follow — and no code for the coding agent to copy.
- **plan-reviewer** — reviews a plan for correctness and convention alignment, and returns
  `APPROVED` or `CHANGES_REQUESTED`.
- **coding** — implements an approved plan and runs a targeted self-check.
- **verify** — runs the project's gating commands (tests, lint, typecheck, e2e when there is
  one) concurrently and reports pass/fail per command. Writes no code.

### Commands
- **/orchestrate** — picks the next actionable roadmap task and drives it through
  interview → plan → review → implement → verify using the five agents above.
- **/orchestrate-quick** — the short pipeline for a task that is already well understood:
  plan → one review → implement → verify, with no interview and no review gating. Takes a
  task description or a roadmap/ticket path.
- **/design** — loads the `design-doc` skill to create or update a design doc for a given
  screen, surface, or flow.
- **/prd** — loads the `prd` skill to create or update a product requirements document for
  a given product or feature.

## Repo layout

```
.claude-plugin/marketplace.json     # marketplace manifest (lists plugins)
plugins/
  clean-architecture/
    .claude-plugin/plugin.json       # plugin manifest
    skills/                          # auto-discovered skills
    agents/                          # auto-discovered agents
    commands/                        # auto-discovered slash commands
```

## Local development

To test changes without publishing, add this checkout as a local marketplace:

```
/plugin marketplace add /path/to/this/repo
/plugin install clean-architecture@husdeli-skills
```

After editing a skill or agent, run `/plugin marketplace update husdeli-skills` to pick
up the changes. Bump `version` in `plugins/clean-architecture/.claude-plugin/plugin.json`
when publishing a release.
