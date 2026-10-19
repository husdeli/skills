---
description: Open or update a feature — the folder that holds what a customer can do, its design docs, and the code that numbers its tickets.
argument-hint: [the feature, in the words a customer would use]
---

# Feature

Open or update a **feature** for the target below.

Target: $ARGUMENTS

Invoke the **`feature`** skill and follow it. If the skill is namespaced here (e.g.
`sdlc:feature`), invoke that. Load it **before** you write anything, and follow its folder shape,
its feature note's properties, and its status rules exactly.

- **Load the `sdlc-structure` skill** (namespaced `sdlc:sdlc-structure`) and resolve the framework
  root and the projects as it says. It also holds how the feature note's properties and links are
  written in each destination. Run `/setup` first when there is no framework root yet.
- **Load the `technical-writing` skill** and follow it for every sentence of the feature note. Two or three
  sentences carry the whole feature, so each one has to land.
- **Load the `glossary` skill** for the feature's name and every term it uses. A feature that
  coins a term writes that term's entry in the same run.
- **Load the `product-intent` skill** (namespaced `sdlc:product-intent`) and cite the goal this
  feature advances and the personas it serves. When no goal in its projects' `product/goals/` fits,
  say so before opening the feature: either the product gained a goal nobody wrote down, or the
  feature is not worth building.
- **Look before you write.** List the framework root's `features/`, and grep the framework root for
  the code you are about to take. A feature that already exists is updated in place, never opened twice, and a
  code that is already taken means the feature is already there under another name.
- **Check the status against the work root.** `done` is a claim about the code, not about the
  board. Read the repository the registry names — `sdlc-structure` resolves it — before you write or
  change a status, and say what the evidence was.
- **Write the feature note only.** A design doc is written by `/design`, which puts it in this
  feature's folder. A ticket is written by `/plan`, and a note in `notes/` by `create-note.py`. This
  command opens the feature and keeps its feature note true.
- **Repeat nothing.** The feature note is one or two sentences saying what a customer can do, plus the
  links. The PRD says why, the design docs say how it works, the tickets say what is left, and the business plan says what it earns. `sdlc-structure`
  holds the table. A sentence that could be pasted into the PRD belongs there, not here.

**When the feature already exists**, update it in place: the `status`, the `projects`, `goals`,
and `personas` when they changed, and the list of design docs when one was added. Leave an older
property — `area`, `shipped`, `updated` — as it is; the `feature` skill holds why. Never rewrite the
code of a feature that has tickets.

**Then report**: the feature's name, its code, its status and the evidence behind it, the path of
the feature note, and what to do next — `/design` to specify how it works, `/plan` to turn it into
tickets.

If no target was given above, list the features that already exist and ask which one to open or
update.
