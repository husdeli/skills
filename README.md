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

### Agents
- **implementation-planner** — turns a task + codebase into a step-by-step plan.
- **plan-reviewer** — reviews a plan for correctness and convention alignment.
- **coding** — implements an approved plan and verifies it.

## Repo layout

```
.claude-plugin/marketplace.json     # marketplace manifest (lists plugins)
plugins/
  clean-architecture/
    .claude-plugin/plugin.json       # plugin manifest
    skills/                          # auto-discovered skills
    agents/                          # auto-discovered agents
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
