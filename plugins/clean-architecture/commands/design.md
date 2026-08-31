---
description: Create or update a design doc that specifies how a solution works, end to end.
argument-hint: [system, service, flow, integration, or screen to specify]
---

# Design

Create or update a **design doc** for the target below.

Target: $ARGUMENTS

Invoke the **`design-doc`** skill and follow it to produce the design doc:

- If the skill is namespaced here (e.g. `clean-architecture:design-doc`), invoke that.
- Load the skill **before** writing anything, and follow its core rules, document shape, per-subject pattern, and style rules exactly.
- Load the **`clean-writing`** skill alongside it and follow it for every sentence of the doc — the design doc is read by engineers, designers, and product people, and it must read the same way for all three.
- Design docs live in **`.clean-architecture/designs/`**, one file per subject, named `<subject>.design.md` (`checkout.design.md`, `event-ingestion.design.md`, `app-shell.design.md`). Create the folder if it is missing, or run `/scaffold` first when the project has no structure at all.
- **Look before you write.** List `.clean-architecture/designs/*.design.md`. When a doc for this target already exists, update it in place. When the project keeps its design docs on an older shape — `<subject>.design.md` files directly in `.clean-architecture/`, or a single `design.md` there or at the root — update the file where it already sits, instead of starting a parallel convention beside it.
- Let the skill choose the subject, and with it the file name. A target that turns out to be two subjects becomes two docs that reference each other.

If no target was given above, ask which system, flow, or surface to specify before starting.
