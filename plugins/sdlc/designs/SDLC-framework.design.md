---
type: design
subject: sdlc-framework
updated: 2026-10-09
tags:
  - sdlc/design
related:
  - "[[project-structure.design]]"
  - "[[registry.design]]"
  - "[[feature.design]]"
  - "[[work.design]]"
  - "[[glossary.design]]"
---
# SDLC framework

This doc defines the files the framework keeps, where each one sits, and what each one is responsible for. It is written top-down: the outermost folder first, then each level inside it.

## 1. Foundations

A session starts in the [[glossary#Framework root|framework root]]. Each [[glossary#Project|project]] keeps its documents in one folder, and a project kept under `projects/` is opened by its [[glossary#Project note|project note]].

The tree:

```
<framework root>/
├── sdlc.json                    the registry; machine-local, gitignored
├── glossary.md                  every term, defined once; see glossary
├── features/                    one folder per feature; see feature
│   └── <feature-name>/          one feature
├── work/                        every ticket, in one bucket per status; see work
│   ├── backlog/
│   ├── in-progress/
│   └── done/
└── projects/                    optional
    └── <project-name>/          one project; see project structure
```

What a project folder holds is defined in [[project-structure.design|Project structure]], a feature folder in [[feature.design|Feature]], the work folder in [[work.design|Work]], the registry in [[registry.design|Registry]], and the glossary in [[glossary.design|Glossary]].

**Every term the framework's documents use is defined once, in the [[glossary#Glossary|glossary]].** A document links the term's entry at its first use instead of defining the term again.
