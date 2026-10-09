---
description: Create or update a product requirements document that describes what the product does and why.
argument-hint: [product or feature to write or update a PRD for]
---

# PRD

Create or update a **product requirements document** for the target below.

Target: $ARGUMENTS

Invoke the **`prd`** skill and follow it to produce the PRD:

- If the skill is namespaced here (e.g. `sdlc:prd`), invoke that.
- Load the skill **before** writing anything, and follow its product-only rules, cohesive-and-positive framing, document shape, and style rules exactly.
- Load the **`technical-writing`** skill alongside it and follow it for every sentence of the document — a PRD is read end to end by people who were not in the room.
- The PRD lives at **`<docs root>/prd.md`**. **Load the `sdlc-structure` skill** (namespaced `sdlc:sdlc-structure`) and resolve the docs root as it says — it also holds what changes in a vault, where the PRD's `Status`, `Last updated`, and `Product` fields are frontmatter properties rather than lines under the title. Create the folder if it is missing, or run `/setup` first when the project has no structure at all. If the project already keeps a PRD at the root (`prd.md`/`PRD.md`), update that file in place rather than starting a second one.
- **Load the `glossary` skill** (namespaced `sdlc:glossary`) and follow it for the product's terms: each one is defined once in `<docs root>/glossary.md`, and the PRD links that definition rather than repeating it.
- **Load the `product-intent` skill** (namespaced `sdlc:product-intent`). Sections 2, 3, 4, and 7 are not written in the PRD: each goal, non-goal, persona, problem, and success metric is its own note under `<docs root>/product/`, and the PRD lists one line per note. Sections 1, 5, and 6 stay the PRD's own prose. Write or update the notes in the same run, and never change a goal in the list line instead of in its note.
- **The PRD is the highest document, and it owns the fewest facts.** Follow the ownership table in `sdlc-structure` for what belongs here and what links back to here.
- If a PRD for this target already exists, update it in place — fold changes into the existing sections and keep the document whole.

If no target was given above, ask which product or feature to write the PRD for before starting.
