---
type: design
subject: project-structure
updated: 2026-10-09
tags:
  - sdlc/design
related:
  - "[[SDLC-framework.design]]"
  - "[[prd.design]]"
---
# Project structure

This doc defines the files inside one [[glossary#Project|project]] folder, and what each one is responsible for.

## 1. Foundations

The tree, as far as this doc defines it so far:

```
<project-name>/
├── <project-name>.md    the project note
├── prd.md               optional; see PRD
└── ...                  the project's other documents, defined in the sections that follow
```

The PRD is defined in [[prd.design|PRD]].

**Every file sits directly in the project folder unless its section says otherwise.** A document that belongs to the project never sits outside its folder.

## 2. The project note

### 2.1 Structure

| Path                               | Responsible for                                                                                                        | Never holds                                                               |
| ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| `<project-name>/<project-name>.md` | Naming the project, saying in one paragraph what it is, carrying its status, and linking the project's entry documents | A requirement, a feature, a design decision, a task, or a repository path |

**The note shares its folder's name.** In a vault, `[[<project-name>]]` resolves to the project note, and Obsidian treats it as the folder's note.

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

- **`name` is the project's name**: required, short, lower case, and unique within the framework root. The registry's `projects` list names a project by this value; see [[registry.design|Registry]].
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
