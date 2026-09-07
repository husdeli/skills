# daily

Everyday routines, kept away from the coding plugin so neither one loads the other's rules.

Part of the [husdeli skills](../../README.md) marketplace. Claude Code only — there is no Codex
mirror for these skills.

## Install

```
/plugin marketplace add husdeli/skills
/plugin install daily@husdeli-skills
```

Start a new session after installation so the skills become available.

## Layout

```
.claude-plugin/plugin.json       # Claude Code plugin manifest
skills/                          # everyday, non-coding skills
```

## What's in it

### Skills
- **easy-meal** — Answers "what should I cook?" with one simple recipe — 10 ingredients or
  fewer, 40 minutes or less, ordinary supermarket ingredients, one or two pans — and gives the
  grocery list for it, grouped by aisle, scaled to the servings you asked for, with the staples
  most kitchens already hold listed apart. Every recipe is saved to `~/.easy-meal/recipes.json`,
  and the skill reads that library before it suggests anything, so the same few meals stop
  coming back every week. It also records what you cooked, when, and what you thought of it, so
  "plan the week" and "cook something we liked" both have somewhere to look.
- **easy-meal-setup** — Builds the Recipe Library once, for the places `easy-meal` cannot write
  a file: a chat session, a phone, a sandbox that is wiped between conversations. The library is
  then a published page whose database holds the recipes, whose *Suggest a dinner* button asks
  Claude from inside the browser, and whose export button gives the whole library back as
  `recipes.json`. The page works on its own — open the bookmark, pick a dinner, tick the list in
  the shop — with no session running and no Claude Code. The skill starts from the built page in
  `assets/recipe-library.html`, and refuses to build a second library when one already exists.
