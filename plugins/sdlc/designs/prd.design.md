---
type: design
subject: prd
updated: 2026-10-09
tags:
  - sdlc/design
related:
  - "[[project-structure.design]]"
---
# PRD

This doc defines the [[glossary#PRD|PRD]] file inside a project folder, and what it is responsible for.

## 1. Structure

A project folder **may contain** one `prd.md`, the PRD: what the product does and why. It sits directly in the project folder, beside the project note, and never in a subfolder.

| Path | Responsible for | Never holds |
| --- | --- | --- |
| `<project-name>/prd.md` | What the product does and why, assembled from the project's product notes | A feature list, a ticket, a design decision, a price, or a repository path |

**The frontmatter `type` is `prd`.** That property is what marks the note as the PRD:

```yaml
---
type: prd
---
```

## 2. Behavior

- **A command finds the PRD as `prd.md` in the project folder with `type: prd`.** A note with `type: prd` anywhere else, or a `prd.md` with another `type`, is not the project's PRD.
- **A project holds at most one PRD.** A command that needs a PRD and finds none says so and names `/prd`; it never writes one on its own.

## 3. Variation and limits

- **The PRD is optional.** A project with no `prd.md` still works: its features, design docs, and tickets stand on their own, and nothing links a PRD that does not exist.
