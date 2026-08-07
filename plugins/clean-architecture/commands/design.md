---
description: Create or update a design doc that specifies how a screen, surface, or flow looks and behaves.
argument-hint: [screen, surface, or system to specify]
---

# Design

Create or update a **design doc** for the target below.

Target: $ARGUMENTS

Invoke the **`design-doc`** skill and follow it to produce the design doc:

- If the skill is namespaced here (e.g. `clean-architecture:design-doc`), invoke that.
- Load the skill **before** writing anything, and follow its core rules, document shape, per-surface pattern, and style rules exactly.
- Load the **`clean-writing`** skill alongside it and follow it for every sentence of the doc — the design doc is read by designers, engineers, and product people, and it must read the same way for all three.
- Let the skill decide the filename and whether the design belongs in a single doc or splits across several cross-referenced docs — `design.md` is only the conventional default. If a design doc for this target already exists, update it in place.

If no target was given above, ask which screen, surface, or flow to specify before starting.
