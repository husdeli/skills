# Changelog

All notable changes to the **daily** plugin are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-07

### Added

- **The `daily` plugin.** A home for the routines that have nothing to do with code.
- **`easy-meal` skill.** Suggests one simple recipe — 10 ingredients or fewer, 40 minutes or
  less, ordinary supermarket ingredients — and turns it into a grocery list grouped by aisle,
  scaled to the servings asked for, with kitchen staples listed apart.

  Every recipe is saved to `~/.easy-meal/recipes.json`, which the skill reads before it suggests
  anything. That library is what stops the same few meals coming back every week. It also
  records what was cooked and when, and what the person thought of it, so "cook something we
  liked" has an answer.

- **`easy-meal-setup` skill.** Builds the Recipe Library once: a published page whose database
  holds the recipes, whose *Suggest a dinner* button asks Claude from inside the browser, and
  whose export button hands the whole library back as `recipes.json`. It is what makes
  `easy-meal` work where there is no filesystem — a chat session, a phone — and the page stands
  on its own, so using it needs no session at all. The skill ships the built page as
  `assets/recipe-library.html` to start from, and refuses to build a second library when one
  already exists.

  `easy-meal` now reads and writes either backend: the JSON file where a filesystem persists,
  and the page's store where none does. The recipe fields are identical in both, so a library
  moves between them without conversion.
