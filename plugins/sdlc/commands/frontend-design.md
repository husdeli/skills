---
description: Agree on the look of a screen before it is built — publishes a static mockup as an Artifact and iterates until you sign it off.
argument-hint: [screen, component, or flow to design]
---

# Frontend design

Agree the visual design of the interface below with the user, before any UI code is written.

Target: $ARGUMENTS

Invoke the **`frontend-design`** skill and follow it end to end:

- If the skill is namespaced here (e.g. `sdlc:frontend-design`), invoke that.
- Load it **before** you draw anything, and follow its process, its visual direction rules, and
  its hard rules exactly.
- Load the **`artifact-design`** skill as the skill requires, and follow the `clean-writing`
  skill for the message that presents the mockup.

You run this in the main session, not in a subagent. Publishing an Artifact and iterating with
the user both need the main loop.

## What this command produces

A published mockup the user can open, and a written record of what they agreed to. It produces
**no production code**. When the user agrees and wants it built, hand the agreed design to
`/code`, or to `/orchestrate-quick` when the work needs a plan.

## Workflow

### 1. Resolve the target

- **Nothing given** → ask which screen, component, or flow to design. Do not guess.
- **A description** → use it as-is.
- **A file path** (a ticket, a feature note, a design doc, a note) → read it and design what it describes.

Say in one line when the target does not need this command — an invisible change, a copy fix, or
one more row in a table that already exists. The skill lists what to skip.

### 2. Run the skill

Read the product documents and the codebase's design system, draft the mockup, publish it, and
present it for agreement, as the skill describes. Iterate on the same artifact URL.

### 3. Close the loop

When the user agrees, record the decisions where the skill says to record them, then offer the
next step in the last line: `/code` to build it, or `/orchestrate-quick` when it needs a plan.

When the user does not agree after three rounds, stop and ask which open question decides it.

## Rules

- **The user agrees, not you.** Explicit agreement ends the loop; silence does not.
- **No production code here.** The mockup is throwaway HTML, and nothing in it is copied into
  the codebase as-is.
- **One artifact, republished.** The URL stays stable across rounds.
- **Say what is fake.** The mockup carries placeholder data and no working logic. Never let the
  user believe otherwise.
