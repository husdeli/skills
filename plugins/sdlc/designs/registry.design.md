---
type: design
subject: registry
updated: 2026-10-09
tags:
  - sdlc/design
related:
  - "[[SDLC-framework.design]]"
  - "[[project-structure.design]]"
---
# Registry

This doc defines `sdlc.json` and what it is responsible for.

## 1. Structure

The framework **holds exactly one** [[glossary#Registry|registry]]: the [[glossary#Work root|work roots]] each project is built in, and what belongs in each.

| Responsible for                                                                                           | Never holds                                                                                                    |
| --------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| Naming every work root of every project, with its path on this machine and one line on what belongs in it | A requirement, a ticket, a project's status, a document path, or a setting a project's documents already carry |

The file, as far as this doc defines it so far:

```json
{
  "repositories": {
    "acme-web": {
      "path": "~/Projects/acme-web",
      "projects": ["acme-billing"]
    },
    "acme-api": {
      "path": "~/Projects/acme-api"
    }
  }
}
```

- **`repositories`** is optional, and is the only top-level property. When present, it holds one entry per [[glossary#Work root|work root]], keyed by a short, stable name. A project may be built in several work roots, and one ticket may change several of them.
- **`path`** is required in every entry. It is absolute, `~`-prefixed, or relative to the [[glossary#Framework root|framework root]], and `~` expands to the user's home directory.
- **`projects`** is optional in an entry. It lists the projects the work root belongs to, each by the `name` in its [[project-structure.design#2. The project note|project note]].

## 2. Behavior

- **The registry is machine-local.** Its paths exist on one machine, so it is gitignored: when the framework root sits inside a git working tree, that tree's `.gitignore` lists `sdlc.json`.
- **A work root that lists `projects` is changed only while working on one of those projects.** Work on any other project never changes it. A work root with no `projects` may be changed while working on any project.

## 3. Variation and limits

- **The registry is required.** Every framework holds one `sdlc.json`.
