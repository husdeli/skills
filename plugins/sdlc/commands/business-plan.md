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
- Load the **`clean-writing`** skill alongside it and follow it for every sentence of the plan and of each competitor note.
- The plan lives at **`<docs root>/business/business-plan.md`**, and each competitor note in **`<docs root>/business/competitors/`**. **Load the `product-docs` skill** (namespaced `sdlc:product-docs`) and resolve the docs root as it says. When you read code for prices, limits, or shipped integrations, read it in the **work root** that `product-docs` resolves.
- **Load the `glossary` skill** (namespaced `sdlc:glossary`) and use the product's terms as it defines them.
- If a plan already exists, update it in place. A target that names only competitors ("refresh competitors", "add competitor X") changes the competitor notes, and the plan only where a figure it quotes has changed.

If no target was given above, write the plan from scratch when none exists, and ask what to update when one does.
