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
  most kitchens already hold listed apart. Every recipe is saved to a `recipes.json` library —
  `~/.easy-meal/recipes.json` on your own machine, and the Claude app file storage on a phone,
  where there is no home folder that survives the chat. The skill reads that library before it
  suggests anything, so the same few meals stop coming back every week. It also records what you
  cooked, when, and what you thought of it, so "plan the week" and "cook something we liked" both
  have somewhere to look.
- **easy-meal-setup** — Builds the Recipe Library page: an optional published page that shows the
  library in a browser, suggests a dinner with a button, prints the grocery list, and imports and
  exports `recipes.json`. It is for people who want a bookmark instead of a chat. It is not where
  the recipes live — the file is, because the Claude mobile app cannot open a published page at
  all. The skill starts from the built page in `assets/recipe-library.html`, and refuses to build
  a second one when a page already exists.
