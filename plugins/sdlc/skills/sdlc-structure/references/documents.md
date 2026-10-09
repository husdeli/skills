# The document kinds

Every kind of document a project holds: where it sits, what it is named, the states it moves
through, and which skill holds the rules for what goes inside it. This file is the map. The skill
named in each row is the territory — load it before you write that document.

## The kinds

| Document | Path | `type` | States | Rules in | Written by |
| --- | --- | --- | --- | --- | --- |
| PRD | `prd.md` | `prd` | — | `prd`, `product-intent` | `/prd` |
| Goal | `product/goals/<slug>.goal.md` | `goal` | `Committed`, `Met`, `Dropped` | `product-intent` | `/prd` |
| Non-goal | `product/non-goals/<slug>.non-goal.md` | `non-goal` | `Excluded`, `Deferred` | `product-intent` | `/prd` |
| Persona | `product/personas/<slug>.persona.md` | `persona` | — | `product-intent` | `/prd` |
| Problem | `product/problems/<slug>.problem.md` | `problem` | — | `product-intent` | `/prd` |
| Success metric | `product/metrics/<slug>.metric.md` | `metric` | A value with the date it was measured | `product-intent` | `/prd` |
| Glossary | `glossary.md` | `glossary` | — | `glossary` | whoever coins a term |
| Feature index | `features/<feature>/<feature>.feature.md` | `feature` | `Planned`, `In Progress`, `Shipped` | `feature` | `/feature` |
| Design doc | `features/<feature>/<subject>.design.md` or `designs/<subject>.design.md` | `design` | — | `design-doc` | `/design` |
| Diagram | `diagrams/<name>.excalidraw.md` | — | — | `diagrams` | whoever writes the document it illustrates |
| Roadmap | `roadmap.md` | `roadmap` | A row is `Pending`, `In Progress`, or `Blocked`, and is deleted when done | `ticket-board` | `/plan`, the orchestrators |
| Ticket | `tickets/<status folder>/<EPIC>-<NNN>-<slug>.md` | `ticket` | `Not Started`, `In Progress`, `Blocked`, `Review`, `Completed` | `ticket-board` | `/plan`, the orchestrators |
| Worklog | beside its ticket, `<EPIC>-<NNN>-<slug>.worklog.md` | `worklog` | — | `ticket-board` | the orchestrating command only |
| Business plan | `business/business-plan.md` | `business-plan` | — | `business-plan` | `/business-plan` |
| Competitor | `business/competitors/<slug>.md` | `competitor` | — | `business-plan` | `/business-plan` |

The `type` column is the vault property every document carries, beside the `sdlc/<type>` tag.
[The destinations](destinations.md) say when a document carries it.

## How the kinds connect

Each line names a document and the documents it cites. [Ownership and links](ownership.md) holds
why a link points this way and never back.

- **A ticket** cites its feature, the PRD area it serves, the design docs it builds, the goal it
  advances, and the tickets it depends on or unblocks.
- **A worklog** cites its ticket.
- **A design doc** cites its feature, or the PRD when it sits in `designs/`, and the other design
  docs it touches.
- **A feature index** cites its PRD area, the goals it advances, the personas it serves, and the
  non-goals it comes up against. It lists its design docs by name.
- **A goal** cites the problem it answers and the metric that measures it.
- **A problem** cites the personas it hurts.
- **The PRD** lists every product note, one line each.
- **The roadmap** cites each epic's feature and each row's ticket.
- **The business plan** cites the PRD and the personas, and lists the features and competitors
  through a query.
- **Every document** links a glossary entry at a term's first use.

## The words that name the structure

- **Project** — one product and every document about it. [The project and the registry](roots.md) say where it sits.
- **Work root** — one code repository the product is built in. A product may have several.
- **Registry** — `sdlc.json` in the project, naming every work root.
- **Pointer file** — `.sdlc.json` at a repository's root, naming its project.
- **Epic** — the group of tickets that delivers one feature. The feature's code is the epic's code,
  it prefixes every ticket ID, and numbering restarts at 001 in each epic.
- **Product note** — a goal, non-goal, persona, problem, or success metric under `product/`.
- **Feature register** — `features/`, the list of everything a customer can do.
