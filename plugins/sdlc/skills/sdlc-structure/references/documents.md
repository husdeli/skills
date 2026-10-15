# The document kinds

Every kind of document a framework root holds: where it sits, what it is named, the states it moves
through, and which skill holds the rules for what goes inside it. This file is the map. The skill
named in each row is the territory — load it before you write that document.

`<project>/` is the project folder, `projects/<project-name>/`, or the framework root itself when
it holds one project directly. Every other path is relative to the framework root.

## The kinds

| Document | Path | `type` | States | Rules in | Written by |
| --- | --- | --- | --- | --- | --- |
| Registry | `sdlc.json` | — | — | `sdlc-structure` | `/setup` |
| Glossary | `glossary.md` | `glossary` | — | `glossary` | whoever coins a term |
| Project note | `<project>/<project-name>.md` | `project` | `backlog`, `in progress`, `done` | `sdlc-structure` | `/setup` |
| PRD | `<project>/prd.md` | `prd` | `Draft`, `Living document`, `Final` | `prd`, `product-intent` | `/prd` |
| Goal | `<project>/product/goals/<slug>.goal.md` | `goal` | `Committed`, `Met`, `Dropped` | `product-intent` | `/prd` |
| Non-goal | `<project>/product/non-goals/<slug>.non-goal.md` | `non-goal` | `Excluded`, `Deferred` | `product-intent` | `/prd` |
| Persona | `<project>/product/personas/<slug>.persona.md` | `persona` | — | `product-intent` | `/prd` |
| Problem | `<project>/product/problems/<slug>.problem.md` | `problem` | — | `product-intent` | `/prd` |
| Success metric | `<project>/product/metrics/<slug>.metric.md` | `metric` | A value with the date it was measured | `product-intent` | `/prd` |
| Roadmap | `<project>/roadmap.md` | `roadmap` | A row mirrors its ticket's status, and is deleted when the ticket is done | `ticket-board` | `/plan`, the orchestrators |
| Feature note | `features/<feature-name>/<feature-name>.feature.md` | `feature` | `backlog`, `in progress`, `done` | `feature` | `/feature` |
| Design doc | `features/<feature-name>/<subject>.design.md` or `designs/<subject>.design.md` | `design` | — | `design-doc` | `/design` |
| Note | `features/<feature-name>/notes/<slug>.note.md` | `note` | `open`, `done` | `feature` | `scripts/create-note.py`, for the orchestrators and `/code`; a person sets `done` |
| Diagram | `diagrams/<name>.excalidraw.md` | — | — | `diagrams` | whoever writes the document it illustrates |
| Ticket | `work/<bucket>/<CODE>-<NNN>-<slug>.md` | — | `backlog`, `in progress`, `blocked`, `review`, `done` | `ticket-board` | `/plan`, the orchestrators |
| Worklog | beside its ticket, `<CODE>-<NNN>-<slug>.worklog.md` | `worklog` | — | `ticket-board` | the orchestrator only |
| Business plan | `<project>/business/business-plan.md` | `business-plan` | `Draft`, `Living document` | `business-plan` | `/business-plan` |
| Competitor | `<project>/business/competitors/<slug>.md` | `competitor` | — | `business-plan` | `/business-plan` |

**A document's `type` property is what makes it that kind of document**, together with where it
sits. A ticket is the exception: it is a ticket because of its name and its bucket, and it carries
no `type`.

## The project note

The note that names a project, says in one paragraph what it is, carries its status, and links
its entry documents. It shares its folder's name, so `[[<project-name>]]` resolves to it.

```yaml
---
type: project
name: acme-billing
status: in progress
tags:
  - sdlc/project
---
# Acme Billing

Invoicing and payment collection for small agencies.

- [[prd]] — what the product does and why
- [[roadmap]] — the work that is left
```

| Responsible for | Never holds |
| --- | --- |
| Naming the project, saying in one paragraph what it is, carrying its status, and linking the project's entry documents | A requirement, a feature, a design decision, a task, or a repository path |

- **`name` is the project's name**: required, short, lower case, and unique within the framework
  root. The registry and every feature's `projects` property name a project by this value.
- **`status`** is `backlog`, `in progress`, or `done`. It says whether the project is worked on,
  not whether the product shipped — the features say that.
- **The paragraph says what the project is**, in one or two sentences. The PRD says why, for whom,
  and how far.
- **The links point at the PRD and the roadmap**, each only when the project has it. The note lists
  no feature, ticket, or design doc.

## How the kinds connect

Each line names a document and the documents it cites. [Ownership and links](ownership.md) holds
why a link points this way and never back.

- **A ticket** cites its feature in its `feature` property, the tickets it depends on in
  `depends_on`, and the design docs it builds in `related:`. It reaches its goal through its feature.
- **A worklog** cites its ticket.
- **A feature note** cites its projects by name, the goals it advances, and the personas it serves.
  It lists its design docs by name.
- **A design doc** cites its feature, or the PRD of each project it serves when it sits in
  `designs/`, the goal it holds to, and the other design docs it touches.
- **A goal** cites the problem it answers and the metric that measures it.
- **A problem** cites the personas it hurts.
- **The PRD** lists every product note of its project, one line each.
- **The roadmap** cites each epic's feature and each row's ticket.
- **The project note** links the PRD and the roadmap.
- **The business plan** cites the PRD and the personas, and lists the features and competitors
  through a query.
- **Every document** links a glossary entry at a term's first use.

## The words that name the structure

Each of these is defined once, in the framework root's `glossary.md`; the definitions below are a
reading aid, and the glossary wins where the two differ.

- **Framework root** — the folder a session starts in, holding the registry, the glossary,
  `features/`, `work/`, and `projects/` or one project's documents.
- **Project** — one product and every document about it.
- **Work root** — one code repository a project is built in.
- **Registry** — `sdlc.json`, naming every work root.
- **Pointer file** — `.sdlc.json` at a repository's root, naming the folder that holds its
  project's documents.
- **Work folder** — `work/`, the ticket board. A work root is a repository, which is a different
  thing.
- **Bucket** — one of `backlog/`, `in-progress/`, and `done/` inside `work/`.
- **Epic** — the group of tickets that delivers one feature. The feature's code is the epic's code,
  it prefixes every ticket ID, and numbering restarts at 001 in each epic.
- **Claim** — the `claimed` property naming the run that holds a ticket.
- **Product note** — a goal, non-goal, persona, problem, or success metric under `product/`.
