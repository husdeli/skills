---
description: Create or update the business plan and the competitor notes beside it.
argument-hint: [what to write or update, e.g. "refresh competitors" or "add competitor Gamma"]
---

# Business plan

Create or update the **business plan** for the target below.

Target: $ARGUMENTS

Invoke the **`business-plan`** skill and follow it to produce the plan:

- If the skill is namespaced here (e.g. `sdlc:business-plan`), invoke that.
- Load the skill **before** writing anything, and follow its rules, its steps, and each step's done condition exactly.
- Load the **`technical-writing`** skill alongside it and follow it for every sentence of the plan and of each competitor note.
- The plan lives at **`<project>/business/business-plan.md`**, and each competitor note in **`<project>/business/competitors/`**. **Load the `sdlc-structure` skill** (namespaced `sdlc:sdlc-structure`) and resolve the project as it says. When you read code for prices, limits, or shipped integrations, read it in the **work root** that `sdlc-structure` resolves.
- **Load the `glossary` skill** (namespaced `sdlc:glossary`) and use the product's terms as it defines them.
- **The plan owns money, and links everything else.** Follow the ownership table in `sdlc-structure`, and the skill's rule 3 for the commercial half it adds to each fact it links.
- **Load the `product-intent` skill** (namespaced `sdlc:product-intent`). A segment in section 3 is a persona note plus a price, and a metric in section 12 is a link to its note. The plan writes the commercial half and never a second definition.
- **Load the `feature` skill** (namespaced `sdlc:feature`). Section 2 lists what a customer can do, and that list is generated from the project's `features/` — a query in a vault, a written table everywhere else. Never type a capability the register does not hold: open the feature instead. Check each feature's status against the work root before the plan quotes it, and fix the feature note when the two disagree.
- If a plan already exists, update it in place. A target that names only competitors ("refresh competitors", "add competitor X") changes the competitor notes, and the plan only where a figure it quotes has changed.

If no target was given above, write the plan from scratch when none exists, and ask what to update when one does.
