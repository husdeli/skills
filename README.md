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
  dependency rules across all layers; domain-cohesive feature grouping.
- **ai-planning-workflow** — Feedback-driven ticket → plan → implement workflow with
  design-agreement and iteration-logging checkpoints.
- **react-clean** — Rules for clean React components: one component per file, at most one
  `useEffect`, no data-layer access from components, static top-of-file imports, no prop
  drilling (compose instead), and the react.dev "You Might Not Need an Effect"
  anti-patterns.
- **design-doc** — Create or update a design doc specifying how a screen, surface, or flow
  looks and behaves — the intended end state, not how to build it.
- **prd** — Create or update a product requirements document: product-only content,
  cohesive per-area descriptions with stable anchor codes, and positive framing.

### Agents
- **feature-interviewer** — reads `prd.md`/`design.md`, researches the feature, and
  returns a Discovery Brief that challenges the idea with open decisions and options.
- **implementation-planner** — turns a task + codebase into a step-by-step plan.
- **plan-reviewer** — reviews a plan for correctness and convention alignment.
- **coding** — implements an approved plan and verifies it.

### Commands
- **/orchestrate** — picks the next actionable roadmap task and drives it through
  interview → plan → review → implement using the four agents above.
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
