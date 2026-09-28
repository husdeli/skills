---
description: Create or update a design doc that specifies how a solution works, end to end.
argument-hint: [system, service, flow, integration, or screen to specify]
---

# Design

Create or update a **design doc** for the target below.

Target: $ARGUMENTS

Invoke the **`design-doc`** skill and follow it to produce the design doc:

- If the skill is namespaced here (e.g. `sdlc:design-doc`), invoke that.
- Load the skill **before** writing anything, and follow its core rules, document shape, per-subject pattern, and style rules exactly.
- Load the **`clean-writing`** skill alongside it and follow it for every sentence of the doc — the design doc is read by engineers, designers, and product people, and it must read the same way for all three.
- **Load the `diagrams` skill** (namespaced `sdlc:diagrams`) before you draw anything: a diagram is generated into `<docs root>/diagrams/` and referenced from the doc with a caption, and the doc's prose stays complete without it.
- **Load the `glossary` skill** (namespaced `sdlc:glossary`) and follow it for the product's terms: the doc links each definition in `<docs root>/glossary.md`, and a term this design coins gets its entry in the same run.
- A design doc is one file per subject, named `<subject>.design.md` (`checkout.design.md`, `event-ingestion.design.md`, `app-shell.design.md`). **Two folders hold them**: `<docs root>/features/<feature>/` when the subject belongs to one feature, and `<docs root>/designs/` when it underpins every feature. **Load the `feature` skill** (namespaced `sdlc:feature`) to settle which, and open the feature first when the subject belongs to one that has no folder yet — a design doc never creates its feature as a side effect. **Load the `product-docs` skill** (namespaced `sdlc:product-docs`) and resolve the docs root as it says — it also holds what changes in a vault, where `Last updated` and `Related` are frontmatter properties and a reference to another document is a wikilink. Create the folder if it is missing, or run `/setup` first when the project has no structure at all. When you read code to write the design, read it in the **work root** — the repository the docs root's registry names, which in a session started from a vault is not the working directory. `product-docs` resolves it.
- **Look before you write.** List `<docs root>/features/*/*.design.md` and `<docs root>/designs/*.design.md`. When a doc for this target already exists, update it in place — including when it sits in the folder you would not have chosen for it. When the project keeps its design docs on an older shape — every doc in `designs/` whether or not it belongs to a feature, `<subject>.design.md` files directly in the docs root, or a single `design.md` there or at the project root — update the file where it already sits, instead of starting a parallel convention beside it.
- Let the skill choose the subject, and with it the file name. A target that turns out to be two subjects becomes two docs that reference each other — in the same feature folder when both belong to that feature.
- **Report the feature** the doc landed under, or say it went to `designs/` because it underpins every feature.

If no target was given above, ask which system, flow, or surface to specify before starting.
