---
type: design
subject: sdlc-framework
updated: 2026-10-20
tags:
  - sdlc/design
related:
  - "[[project-structure.design]]"
  - "[[registry.design]]"
  - "[[feature.design]]"
  - "[[work.design]]"
  - "[[ticket.design]]"
  - "[[glossary.design]]"
  - "[[workflow.design]]"
---
# SDLC framework

The SDLC framework is one folder tree holding every document its products are planned and built from, with one place for each kind of file and one responsibility for each place.

## 1. Foundations

A session starts in the [[glossary#Framework root|framework root]], or in a code repository that leads to it. A session finds the framework root by walking up to the first folder that holds the [[glossary#Registry|registry]]. Inside a repository with no such folder above it, the framework root is the folder the repository's [[glossary#Pointer file|pointer file]] leads to, or else the repository's own `.sdlc/` folder.

Each [[glossary#Project|project]] keeps its documents in one folder, and a project kept under `projects/` is opened by its [[glossary#Project note|project note]]. A framework root with no `projects/` holds one project's documents directly: the project note, `prd.md`, `roadmap.md`, `product/`, and `business/` sit beside `glossary.md`.

The tree:

```
<framework root>/
├── sdlc.json                    the registry; machine-local, gitignored
├── glossary.md                  every term, defined once; see glossary
├── features/                    one folder per feature; see feature
│   └── <feature-name>/          the feature note and the design docs it owns
│       └── notes/               actions a person must take outside the code
├── designs/                     the design docs every feature depends on
├── diagrams/                    one file per drawing
├── work/                        every ticket, in one bucket per status; see work
│   ├── backlog/
│   ├── in-progress/             with each ticket's worklog beside it
│   └── done/
└── projects/                    optional
    └── <project-name>/          one project; see project structure
        ├── <project-name>.md    the project note
        ├── prd.md               optional
        ├── roadmap.md           optional; the work left on this project
        ├── product/             the product notes the PRD is assembled from
        └── business/            the business plan and its competitor notes
```

What a project folder holds is defined in [[project-structure.design|Project structure]], a feature folder in [[feature.design|Feature]], the work folder in [[work.design|Work]], a ticket in [[ticket.design|Ticket]], the registry in [[registry.design|Registry]], and the glossary in [[glossary.design|Glossary]].

**Every term the framework's documents use is defined once, in the [[glossary#Glossary|glossary]].** A document links the term's entry at its first use instead of defining the term again.
