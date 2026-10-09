# The layout of the docs root

The folders the docs root holds, what goes in each, how the structure is created, and how it grows
and shrinks as a product is built. [The document kinds](documents.md) say what each file inside it
is, and [the docs root](roots.md) says where the folder itself sits.

## The tree

```
<docs root>/
  sdlc.json              the registry: every repository this product is built in.
                         Machine-local, and never committed
  prd.md                 what the product does and why, assembled from the notes in product/
  glossary.md            the product's terms, one ## heading per term
  roadmap.md             the work that is left, one section per epic
  product/
    goals/               <slug>.goal.md
    non-goals/           <slug>.non-goal.md
    personas/            <slug>.persona.md
    problems/            <slug>.problem.md
    metrics/             <slug>.metric.md
  features/
    <feature>/           <feature>.feature.md, the index, and the design docs this
                         feature owns, <subject>.design.md
  designs/               overview.design.md and the design docs that underpin every feature
  diagrams/              <name>.excalidraw.md, one file per drawing
  business/              business-plan.md. Created by /business-plan, never by setup
    competitors/         <competitor>.md, one note per competitor
  tickets/
    TEMPLATE.md          the shape every new ticket is copied from. It never moves
    todo/                <EPIC>-<NNN>-<slug>.md, a ticket nobody has started
    in-progress/         a ticket being built, with <EPIC>-<NNN>-<slug>.worklog.md beside it
    done/                a finished ticket and its worklog
```

## The folder rules

- **A kind of document gets its own folder once there can be more than one of it.** The PRD, the
  glossary, and the roadmap are single files. Everything else is one file per item.
- **A file name says what kind of document it is.** The suffix — `.goal.md`, `.feature.md`,
  `.design.md`, `.worklog.md` — names the kind, so a folder listing reads as an inventory.
- **Ownership decides where a design doc sits.** A subject that belongs to one feature sits in that
  feature's folder. A subject every feature depends on sits in `designs/`. The test: would the doc
  still be needed if the feature were dropped? The `design-doc` and `feature` skills hold the rest.
- **A ticket's folder is its status.** It moves between `todo/`, `in-progress/`, and `done/` as the
  work progresses, and its worklog moves with it. The `ticket-board` skill holds the mapping.
- **A diagram never moves.** It stays in `diagrams/` for its whole life, so a document that moves
  keeps its reference.

## How the structure is created

The setup entry point creates the structure once, and every other command fills it.

- **It writes stubs, never content.** `prd.md`, `glossary.md`, `roadmap.md`, and the ticket
  template start as headings and placeholders. Inventing a requirement, a feature, or a goal here
  invents a commitment nobody made.
- **It creates every folder except `business/`, even an empty one.** `product/` and its five folders, `features/`,
  `designs/`, `diagrams/`, and the three ticket status folders. An empty folder gets a `.gitkeep`
  only when the docs root sits inside a git working tree.
- **It never overwrites.** A file that exists is kept and reported as kept.
- **It writes one design stub at most**, `designs/overview.design.md`, and only when the project
  has no design doc anywhere.
- **It writes no feature and no product note.** `/feature` opens a feature, and `/prd` writes the
  notes under `product/`.

| Command | What it writes into the docs root |
| --- | --- |
| `/setup` | The structure, the stubs, the registry, and the pointer file in each repository |
| `/prd` | `prd.md`, the notes under `product/`, and the glossary entries for the terms it coins |
| `/feature` | One feature folder and its index note |
| `/design` | One design doc, in its feature's folder or in `designs/`, and its diagrams |
| `/plan` | Roadmap rows and tickets in `todo/`, plus any PRD, feature, or design update the request needs |
| `/orchestrate`, `/orchestrate-quick`, `/run-roadmap` | Ticket moves, the status and assignee fields, the worklog, and roadmap row deletions |
| `/business-plan` | `business/business-plan.md` and the notes in `business/competitors/` |

## How the structure grows and shrinks

- **The roadmap shrinks.** A finished task loses its row, and an epic loses its section when its
  last row goes.
- **The feature register does not.** A feature that ships keeps its note, marked `Shipped`, so
  `features/` is the list of what the product does.
- **`tickets/done/` is the record.** The finished ticket and its worklog together say what was
  built and what was decided while building it.
- **A product note outlives a change of mind.** A dropped goal keeps its note. A non-goal the
  product adopts is deleted and becomes a goal. The `product-intent` skill holds both rules.

## Older shapes

A project on an older shape keeps working, and every command reads it where it is:

- `prd.md`, `glossary.md`, `roadmap.md`, or `tickets/` at the project root instead of in a docs root;
- a single `design.md`, or loose `*.design.md` files in the docs root;
- design docs in `designs/` that belong to one feature, with no `features/` folder;
- a flat `tickets/` folder with no status folders;
- a PRD that still holds its goals, personas, problems, and metrics inline.

Update a document in place where it already sits. Move or split one only when the user asks — the
setup entry point offers each migration, shows the mapping first, and makes it only after a yes.
