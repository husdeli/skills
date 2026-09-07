# husdeli skills

A Claude Code and Codex plugin marketplace. Two plugins live here: **sdlc**, for architecture
rules and reviewed development workflows, and **daily**, for the routines that have nothing to
do with code.

## Install

In Claude Code:

```
/plugin marketplace add husdeli/skills
/plugin install sdlc@husdeli-skills
/plugin install daily@husdeli-skills
```

In Codex:

```shell
codex plugin marketplace add husdeli/skills
codex plugin add sdlc@husdeli-skills
```

The `daily` plugin is Claude Code only.

Start a new session after installation so the skills become available.

## The plugins

### [`sdlc`](plugins/sdlc/README.md) — plan, review, implement, verify

Ten commands drive six agents through interview → plan → review → implement → verify and code
review, and nine skills hold the rules they follow: Clean Code and Hexagonal Architecture, the
TypeScript, React, and TanStack Start layers, the writing standard every human-facing output
goes through, and the PRD, design-doc, and frontend-design document skills. Every document it
reads or writes lives in one `.sdlc/` folder at your project root.

Claude Code and Codex. See the [plugin README](plugins/sdlc/README.md) for the commands, the
agents, the skills, and the `.sdlc/` layout.

### [`daily`](plugins/daily/README.md) — everyday routines

Kept apart from the coding plugin so neither one loads the other's rules.

**easy-meal** answers "what should I cook?" with one simple recipe and the grocery list for it,
keeping every recipe in a library it reads before it suggests anything — which is what stops the
same four dinners coming round again. **easy-meal-setup** builds that library as a published
page for the places where no file survives, such as a chat session or a phone.

Claude Code only. See the [plugin README](plugins/daily/README.md).

## Repo layout

```
.claude-plugin/marketplace.json     # marketplace manifest (lists plugins)
.agents/plugins/marketplace.json    # Codex marketplace manifest
plugins/
  daily/                            # everyday routines — plugins/daily/README.md
  sdlc/                             # the development workflow — plugins/sdlc/README.md
```

Each plugin's README carries its own layout.

## Local development

To test changes in Claude Code without publishing:

```
/plugin marketplace add /path/to/this/repo
/plugin install sdlc@husdeli-skills
/plugin install daily@husdeli-skills
```

To test changes in Codex without publishing:

```shell
codex plugin marketplace add /path/to/this/repo
codex plugin add sdlc@husdeli-skills
```

After a Claude Code edit, run `/plugin marketplace update husdeli-skills`.
After a Codex edit, run `codex plugin add sdlc@husdeli-skills` and start a new session.
Keep the `sdlc` plugin's two manifest versions equal when publishing a release. The `daily`
plugin has one manifest and one version of its own.
