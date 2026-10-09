---
type: design
subject: sdlc-framework
updated: 2026-10-09
tags:
  - sdlc/design
---
# SDLC framework

This doc defines the files the framework keeps, where each one sits, and what each one is responsible for. It is written top-down: the outermost folder first, then each level inside it.

## 1. Foundations

A session starts in the [[glossary#Framework root|framework root]]. Each [[glossary#Project|project]] keeps its documents in one folder, and a project kept under `projects/` is opened by its [[glossary#Project note|project note]].

The tree:

```
<framework root>/
└── projects/                    optional
    └── <project-name>/          one project; see project structure
```

What a project folder holds is defined in [[project-structure.design|Project structure]].
