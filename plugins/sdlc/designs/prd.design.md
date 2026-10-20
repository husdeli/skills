---
type: design
subject: prd
updated: 2026-10-20
tags:
  - sdlc/design
related:
  - "[[project-structure.design]]"
---
# PRD

This doc defines the [[glossary#PRD|PRD]] file inside a project folder, and what it is responsible for.

## 1. Structure

A project folder **may contain** one `prd.md`, the PRD: what the product does and why. It sits directly in the project folder, beside the project note, and never in a subfolder. A [[glossary#Framework root|framework root]] that holds one [[glossary#Project|project]] directly, with no `projects/` folder, holds the PRD itself, beside `glossary.md`.

| Path | Responsible for | Never holds |
| --- | --- | --- |
| `<project-name>/prd.md` | What the product does and why, assembled from the project's product notes | A feature list, a ticket, a design decision, a price, or a repository path |

**The frontmatter `type` is `prd`.** That property is what marks the note as the PRD:

```yaml
---
type: prd
status: Living document
product: Acme Billing — invoicing and payment collection for small agencies
updated: 2026-10-20
tags:
  - sdlc/prd
---
# Product Requirements Document
```

- **`status`** is `Draft`, `Living document`, or `Final`.
- **`product`** is the product's name and a one-line description, or `TBD` in place of the name.
- **`updated`** is the date the PRD last changed.
- **`tags`** holds `sdlc/prd`.
- **The PRD carries no `related:` property.** It is the highest document: a design doc, a feature, and the business plan link the PRD, and it links none of them back.

**The body has eight sections, in this order:**

1. **Overview** — what the product is, in two to four sentences, and three to five core principles.
2. **Problem statement** — one line per problem note.
3. **Goals & non-goals** — one line per goal note, then one line per non-goal note.
4. **Users & personas** — one line per persona note.
5. **How the product works** — one subsection per [[glossary#Product area|product area]].
6. **Cross-cutting qualities** — the guarantees that hold across the whole product, in prose.
7. **Success metrics** — one line per metric note, with its target.
8. **Open questions** — the unresolved product decisions that block design or implementation.

**Sections 2, 3, 4, and 7 compose the project's [[glossary#Product note|product notes]].** Each line is the note's link, then its statement in a few words, so a reader can follow the section without opening the note. The note holds the reasoning, and the PRD never restates it.

**Sections 1, 5, and 6 are the PRD's own prose.** Each product area in section 5 is a few short paragraphs on how that part of the product works and how it connects to the others. Its heading carries a short uppercase anchor code, such as `` ### Workspace `WORKSPACE` ``, which other documents cite. An area never lists its [[glossary#Feature|features]].

## 2. Behavior

- **A command finds the PRD as `prd.md` in the project folder with `type: prd`.** A note with `type: prd` anywhere else, or a `prd.md` with another `type`, is not the project's PRD.
- **A project holds at most one PRD.** `/prd` writes it, and `/plan` creates it when it is missing and folds in the sections a request touches. No other command writes it.
- **The PRD stays high level.** It names the product areas, what each does for its users, and why, in a few short paragraphs each. How a part behaves — its flows, states, screens, edge cases, and data — belongs to a [[glossary#Design doc|design doc]], and a sentence a design doc would also have to say is deleted from the PRD.
- **A redesign leaves the PRD true.** A change to how a part works rewrites a design doc, and changes the PRD only when what the product does for its users changed.
- **A product note's status decides whether its line appears.** A `Dropped` goal leaves the goals list and keeps its note. Every non-goal is listed, because `Excluded` and `Deferred` both mean the product is not building it. A non-goal the product adopts is deleted and replaced by a goal, so its line leaves the non-goals list and the goal gains one.
- **An edit rewrites the affected passage as the current requirement.** The PRD holds no revision section and no history, and a resolved open question is deleted.
- **An area's anchor code stays stable while its prose changes.** A new code appears only for a new product area.

## 3. Variation and limits

- **The PRD is optional.** A project with no `prd.md` still works: its features, design docs, and tickets stand on their own, and nothing links a PRD that does not exist.
- **The PRD holds product requirements only.** It never holds:
  - money — a price, a plan's cost, a margin, a market size, or a claim against a named competitor; the business plan owns these;
  - a ticket ID, an epic, a milestone, or a note on whether something is built yet;
  - a file path, a module or component name, a route, a schema field, or code;
  - a technology, vendor, or library named as the mechanism, unless the user sees it as part of the product;
  - a migration or history note, such as "supersedes" or "revised".
