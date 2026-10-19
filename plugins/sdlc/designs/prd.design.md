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
- **A project holds at most one PRD.** `/prd` writes it, and `/plan` creates it when it is missing and folds in the sections a request touches. No other command writes it.
- **The PRD stays high level.** It names the product areas, what each does for its users, and why, in a few short paragraphs each. How a part behaves — its flows, states, screens, edge cases, and data — belongs to a [[glossary#Design doc|design doc]], and a sentence a design doc would also have to say is deleted from the PRD.

## 3. Variation and limits

- **The PRD is optional.** A project with no `prd.md` still works: its features, design docs, and tickets stand on their own, and nothing links a PRD that does not exist.
