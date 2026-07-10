---
description: Create or update a design doc (design.md) that specifies how a screen, surface, or flow looks and behaves.
argument-hint: [screen, surface, or system to specify]
---

# Design

Create or update a **design doc** for the target below.

Target: $ARGUMENTS

Invoke the **`design-doc`** skill and follow it to produce the design doc:

- If the skill is namespaced in this environment (e.g. `clean-architecture:design-doc`), invoke that.
- Load the skill **before** writing anything, and follow its core rules, document shape, per-surface pattern, and style rules exactly.

If no target was given above, ask the user which screen, surface, or flow to specify before starting.
