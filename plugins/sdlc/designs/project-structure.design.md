---
type: design
subject: project-structure
updated: 2026-10-20
tags:
  - sdlc/design
related:
  - "[[SDLC-framework.design]]"
  - "[[prd.design]]"
  - "[[registry.design]]"
  - "[[workflow.design]]"
---
# Project structure

This doc defines the files inside one [[glossary#Project|project]] folder, what each one is responsible for, and how a session finds the framework root, the project, and the code it works on.

## 1. Foundations

The tree:

```
<project-name>/
├── <project-name>.md       the project note
├── prd.md                  optional; what the product does and why
├── roadmap.md              optional; the work left on this project
├── product/                the product notes the PRD is assembled from
│   ├── goals/              <slug>.goal.md
│   ├── non-goals/          <slug>.non-goal.md
│   ├── personas/           <slug>.persona.md
│   ├── problems/           <slug>.problem.md
│   └── metrics/            <slug>.metric.md
└── business/
    ├── business-plan.md
    └── competitors/        <slug>.md
```

**Every file sits at the path this tree gives it.** A document that belongs to the project never sits outside its folder, and the project folder never holds a glossary, a [[glossary#Feature|feature]], or a [[glossary#Ticket|ticket]]: those belong to the [[glossary#Framework root|framework root]].

**A framework root with no `projects/` holds one project's documents directly.** The project note, `prd.md`, `roadmap.md`, `product/`, and `business/` then sit beside `glossary.md`. A second project needs `projects/`: `/setup` offers to move the first project's documents into `projects/<existing-project-name>/`, shows what moves, and moves them only after a yes. Everything else in the framework root stays where it is.

## 2. The project note

### 2.1 Structure

| Path                               | Responsible for                                                                                                        | Never holds                                                               |
| ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| `<project-name>/<project-name>.md` | Naming the project, saying in one paragraph what it is, carrying its status, and linking the project's entry documents | A requirement, a feature, a design decision, a task, or a repository path |

**The note shares its folder's name.** In a vault, `[[<project-name>]]` resolves to the [[glossary#Project note|project note]], and Obsidian treats it as the folder's note.

**The frontmatter `type` must be `project`.** That property is what marks the note as the project note: a `<project-name>.md` with another `type`, or none, is not the project note, and a note with `type: project` anywhere else is not one either.

**The project note** carries these properties, and a short body:

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

- **`name` is the project's name**: required, short, lower case, and unique within the framework root. The registry's `projects` list and every feature's `projects` property name a project by this value; see [[registry.design|Registry]].
- **The paragraph says what the project is**, in one or two sentences. The PRD says why, for whom, and how far.
- **The links point at the project's entry documents** — the PRD and the roadmap, each only when the project has it. The note lists no feature, ticket, or design doc; those are found through the PRD and the roadmap.

### 2.2 States

The project note's `status` property:

| Status        | Meaning                                    | What a command does                                     |
| ------------- | ------------------------------------------ | ------------------------------------------------------- |
| `backlog`     | The project is planned, and no work has started | Lists it, never picks it unasked, and drives it when named |
| `in progress` | The project is being built                 | Offers it, and drives it                                |
| `done`        | Work on the project has finished           | Leaves it out of every list, and reads it only when named |

The status says whether a project is worked on. It does not say whether the product shipped — the features under the project say that.

## 3. The project's other documents

Each document has one owner of its rules, named in the last column.

| Path | Owns | Defined in |
| --- | --- | --- |
| `prd.md` | What the product does, why, and for whom, with one line per product note | [[prd.design\|PRD]], and the `prd` skill |
| `roadmap.md` | The work left on this project: one section per epic, one row per open ticket | The `ticket-board` skill; see [[glossary#Roadmap\|roadmap]] |
| `product/goals/<slug>.goal.md` | One outcome the product commits to, the problem it answers, and the metric that measures it | The `product-intent` skill |
| `product/non-goals/<slug>.non-goal.md` | One thing the product refuses or defers | The `product-intent` skill |
| `product/personas/<slug>.persona.md` | One kind of person the product serves | The `product-intent` skill |
| `product/problems/<slug>.problem.md` | One failure the product exists to fix, and the personas it hurts | The `product-intent` skill |
| `product/metrics/<slug>.metric.md` | One measure of success, with its value and the date it was measured | The `product-intent` skill |
| `business/business-plan.md` | Who pays, what they pay for, and how the product reaches them — every price and market claim | The `business-plan` skill; see [[glossary#Business plan\|business plan]] |
| `business/competitors/<slug>.md` | The detail on one competitor, which the business plan links and never repeats | The `business-plan` skill |

The five kinds under `product/` are the [[glossary#Product note|product notes]]. `/setup` creates `product/` and its five folders empty, and `/prd` writes the notes. `/business-plan` creates `business/`.

## 4. Finding the framework root, the project, and the work root

Every command and agent resolves these three once, at the start of a run, in the order below. Every later path resolves against what they give.

### 4.1 The framework root

**A session started in the documents walks up.** The framework root is the first directory, from the working directory up to the home directory, that holds `sdlc.json`. When none does, the first directory holding `glossary.md` beside `work/` or `features/` is a framework root with no [[glossary#Registry|registry]]: it can be read, but no run can resolve a work root in it; see [[registry.design|Registry]].

**A session started in a code repository looks at the repository root**, the directory holding `.git`, `package.json`, `AGENTS.md`, or `CLAUDE.md`. The first match wins:

1. **The [[glossary#Pointer file|pointer file]], `.sdlc.json`.** Its `root` names the project folder, or the framework root when it holds one project directly. The framework root is the first directory holding `sdlc.json` at or above that folder.
2. **`.sdlc/`**, which is then the framework root.
3. **Neither.** The repository has no framework root. A command reads what the repository root holds on an older shape (see 5. Older shapes) and names `/setup` as the way to create the structure.

The pointer file carries two properties:

| Property | Holds |
| --- | --- |
| `root` | The folder holding the project's documents: absolute, `~`-prefixed, or relative to the repository root |
| `kind` | The [[glossary#Destination\|destination]]: `vault`, `folder`, or `repo` |

A repository whose framework root is its own `.sdlc/` has no pointer file. Only `/setup` writes one.

### 4.2 Destinations

| `kind` | Where the framework root sits | How a document links another |
| --- | --- | --- |
| `vault` | A folder in an Obsidian vault, or the vault root itself | A wikilink |
| `folder` | Any other folder outside the repository | A relative path |
| `repo` | `.sdlc/` at the repository root | A relative path |

A framework root is in a vault when it, or a parent directory, holds `.obsidian/`. **No name in a vault starts with a dot**, because Obsidian hides it, so a vault never holds `.sdlc/`. `vault` is the destination `/setup` recommends, and `repo` is the one every command falls back to when no pointer file exists.

### 4.3 The project

A framework root with no `projects/` holds one project, and it is the project. Otherwise the first answer wins:

1. **The command's arguments name it**, by the `name` in its project note.
2. **The pointer file names it**, when the session started in a repository whose `root` is one project folder.
3. **The work names it.** A ticket reaches its project through its feature's `projects` property. When that list holds one project, it is the project.
4. **Otherwise the command asks**, offering every project whose note says `in progress`. It never guesses when two are in reach.

The project's `status` then decides whether a command offers it, picks it, or reads it only when named; see 2.2 States.

### 4.4 The work root

A [[glossary#Work root|work root]] is one code repository a project is built in. A ticket names its work roots in `repositories`, as registry codes. When the field is empty, or names a code the registry no longer has, the `repo-resolver` agent reads the ticket, its feature and design docs, each candidate's `what` line, and the candidates' code, and returns the codes with the evidence. An unsettled answer goes to the answerer. A run started inside a repository with no registry builds in that repository alone.

The work root is usually not the working directory. The session is given access to each one, with `--add-dir` or `/add-dir`, and every command names the repository: `git -C <work root> …`, or `cd <work root> && …`. The `sdlc-structure` skill's work-root reference holds the full rules, and [[workflow.design|Workflow]] says when a run resolves it.

## 5. Older shapes

A framework root on an older shape keeps working. Every command reads it where it is, and `/setup` offers each move, showing the mapping first.

| Older shape | Read as |
| --- | --- |
| `tickets/` with `todo/`, `in-progress/`, `done/`, or flat | `work/` with `backlog/`, `in-progress/`, `done/`; a flat folder leaves the state to `status` alone |
| `tickets/TEMPLATE.md` | Nothing |
| A project-level `features/`, `glossary.md`, or `sdlc.json` with no framework root above it | A framework root holding one project directly |
| `prd.md`, `glossary.md`, `roadmap.md`, or `tickets/` at a repository root | A framework root at the repository root |
| A single `design.md`, or loose `*.design.md` files at the top of the project | `designs/` |
| A PRD that still holds its goals, personas, problems, and metrics inline | The PRD, with the product notes not yet split out |
