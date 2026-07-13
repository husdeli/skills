---
description: Create or update a product requirements document that describes what the product does and why.
argument-hint: [product or feature to write or update a PRD for]
---

# PRD

Create or update a **product requirements document** for the target below.

Target: $ARGUMENTS

Invoke the **`prd`** skill and follow it to produce the PRD:

- If the skill is namespaced in this environment (e.g. `clean-architecture:prd`), invoke that.
- Load the skill **before** writing anything, and follow its product-only rules, cohesive-and-positive framing, document shape, and style rules exactly.
- `PRD.md` is the conventional default filename. If a PRD for this target already exists, update it in place rather than creating a new one — fold changes into the existing sections and keep the document whole.

If no target was given above, ask the user which product or feature to write the PRD for before starting.
