# The layout of a framework root

The folders a framework root holds, what goes in each, how the structure is created, and how it
grows and shrinks as products are built. [The document kinds](documents.md) say what each file
inside it is, and [the framework root and the registry](roots.md) say how a session finds it.

## The tree

```
<framework root>/
├── sdlc.json                        the registry; machine-local, gitignored
├── glossary.md                      every term, defined once
├── features/                        one folder per feature
│   └── <feature-name>/
│       ├── <feature-name>.feature.md    the feature note
│       └── <subject>.design.md          zero or more design docs this feature owns
├── designs/                         design docs every feature depends on
├── diagrams/                        <name>.excalidraw.md, one file per drawing
├── work/                            every ticket, in one bucket per status
│   ├── backlog/                     <CODE>-<NNN>-<slug>.md — tickets no one has started
│   ├── in-progress/                 tickets being built, each with its .worklog.md beside it
│   └── done/                        finished tickets and their worklogs
└── projects/                        optional
    └── <project-name>/              one project
        ├── <project-name>.md        the project note
        ├── prd.md                   optional; what the product does and why
        ├── roadmap.md               optional; the work left on this project
        ├── product/                 the product notes the PRD is assembled from
        │   ├── goals/               <slug>.goal.md
        │   ├── non-goals/           <slug>.non-goal.md
        │   ├── personas/            <slug>.persona.md
        │   ├── problems/            <slug>.problem.md
        │   └── metrics/             <slug>.metric.md
        └── business/                business-plan.md, and competitors/<competitor>.md
```

**A framework root with no `projects/` holds one project's documents directly.** The project note,
`prd.md`, `roadmap.md`, `product/`, and `business/` then sit beside `glossary.md` instead of in a
project folder. Every other folder is the same.

## The folder rules

| Path | Responsible for | Never holds |
| --- | --- | --- |
| `sdlc.json` | Naming every work root of every project | A requirement, a ticket, a status, or a document path |
| `glossary.md` | Defining each term once | A requirement, a behavior, a layout, or a task |
| `features/<feature-name>/` | The feature note, and every design doc that belongs to this feature alone | A diagram, a ticket, a worklog, or another feature's design doc |
| `designs/` | The design docs every feature depends on | A design doc that belongs to one feature |
| `diagrams/` | One file per drawing | Prose a document needs to stay complete |
| `work/` | The three buckets, and nothing else | A ticket outside a bucket, a feature, a design doc, a roadmap, or a template |
| `work/backlog/` | Every ticket that is planned and not started | A subfolder, or a worklog — except the one a ticket returned to the backlog keeps |
| `work/in-progress/` | Every ticket being built, blocked, or in review, with its worklog | A subfolder |
| `work/done/` | Every finished ticket, with its worklog | A subfolder |
| `projects/<project-name>/` | The project note, and every document that belongs to that project alone | A feature, a ticket, or the glossary |

- **Features and tickets belong to the framework root, not to a project.** A feature names the
  projects it relates to in its `projects` property, and a ticket reaches its project through its
  feature. One feature can serve several projects, so it sits above all of them.
- **A file name says what kind of document it is.** The suffix — `.feature.md`, `.design.md`,
  `.goal.md`, `.worklog.md` — names the kind, so a folder listing reads as an inventory.
- **Ownership decides where a design doc sits.** A subject that belongs to one feature sits in that
  feature's folder. A subject every feature depends on sits in `designs/`. The test: would the doc
  still be needed if the feature were dropped? The `design-doc` and `feature` skills hold the rest.
- **A ticket's bucket follows its status.** It moves between `backlog/`, `in-progress/`, and
  `done/` as the status changes, and its worklog moves with it. The `ticket-board` skill holds the
  mapping.
- **An empty bucket may be absent.** A command creates a bucket the first time a ticket moves into
  it.
- **A diagram never moves.** It stays in `diagrams/` for its whole life, so a document that moves
  keeps its reference.
- **A project folder never holds a glossary, a feature, or a ticket.** A second note named
  `glossary` makes every `[[glossary#…]]` link ambiguous, so a project's terms go in the framework
  root's glossary.

## How the structure is created

The setup entry point creates the structure once, and every other command fills it.

- **It writes stubs, never content.** The glossary starts as its title alone, and the project note
  as its name and a one-paragraph placeholder. Inventing a requirement, a feature, or a goal here
  invents a commitment nobody made.
- **It writes the registry and the glossary every time.** Both are required in every framework
  root.
- **It creates `features/`, `designs/`, `diagrams/`, and `work/` with its three buckets**, and a
  project's `product/` folder and its five folders. An empty folder gets a `.gitkeep` only when the
  framework root sits inside a git working tree.
- **It never overwrites.** A file that exists is kept and reported as kept.
- **It writes no feature, no ticket, no PRD, and no product note.** `/feature` opens a feature,
  `/plan` writes tickets, and `/prd` writes the PRD and the notes under `product/`.

| Command | What it writes |
| --- | --- |
| `/setup` | The structure, the registry, the glossary, the project note, and the pointer file in each repository |
| `/prd` | A project's `prd.md`, its notes under `product/`, and the glossary entries for the terms it coins |
| `/feature` | One feature folder and its feature note |
| `/design` | One design doc, in its feature's folder or in `designs/`, and its diagrams |
| `/plan` | Tickets in `work/backlog/` and their roadmap rows, plus any PRD, feature, or design update the request needs |
| `/orchestrate`, `/orchestrate-quick`, `/run-roadmap` | The claim, the status transitions and bucket moves, the worklog, the usage properties, and roadmap row deletions |
| `/business-plan` | A project's `business/business-plan.md` and the notes in `business/competitors/` |

## How the structure grows and shrinks

- **The roadmap shrinks.** A finished ticket loses its row, and an epic loses its section when its
  last row goes.
- **`features/` does not.** A feature that ships keeps its note, at `status: done`, so `features/`
  lists everything the products do.
- **`work/done/` is the record.** The finished ticket and its worklog together say what was built,
  what was decided while building it, and what it cost.
- **A product note outlives a change of mind.** A dropped goal keeps its note. A non-goal the
  product adopts is deleted and becomes a goal. The `product-intent` skill holds both rules.

## Older shapes

A framework root on an older shape keeps working, and every command reads it where it is:

| Older shape | Read it as |
| --- | --- |
| `tickets/` with `todo/`, `in-progress/`, `done/` | `work/` with `backlog/`, `in-progress/`, `done/` |
| A flat `tickets/` folder with no status folders | `work/`, with the status property alone carrying the state |
| `tickets/TEMPLATE.md` | Nothing; the template lives in the `ticket-board` skill |
| A project-level `features/`, `glossary.md`, or `sdlc.json` with no framework root above it | A framework root holding one project directly |
| `prd.md`, `glossary.md`, `roadmap.md`, or `tickets/` at a repository root | A framework root at the repository root |
| A single `design.md`, or loose `*.design.md` files at the top of the project | `designs/` |
| A PRD that still holds its goals, personas, problems, and metrics inline | The PRD, with the notes not yet split out |

[Properties, links, and the vault shape](destinations.md#older-property-values) maps the older
property values onto the current ones.

Update a document in place where it already sits. Move or split one only when the user asks — the
setup entry point offers each migration, shows the mapping first, and makes it only after a yes.
