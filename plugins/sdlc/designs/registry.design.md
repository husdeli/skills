---
type: design
subject: registry
updated: 2026-10-20
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

The file:

```json
{
  "repositories": {
    "acme-web": {
      "path": "~/Projects/acme-web",
      "projects": ["acme-billing"],
      "what": "TanStack Start app — every screen, and the server functions behind them"
    },
    "acme-api": {
      "path": "~/Projects/acme-api"
    }
  }
}
```

- **`repositories`** is the only top-level property. It holds one entry per work root, keyed by a short, stable name. The key is how a ticket's `repositories` property, a worklog, and a report name that repository. A project may be built in several work roots, and one ticket may change several of them.
- **`path`** is required in every entry. It is absolute, `~`-prefixed, or relative to the [[glossary#Framework root|framework root]], and `~` expands to the user's home directory.
- **`projects`** is optional in an entry. It lists the projects the work root belongs to, each by the `name` in its [[project-structure.design#2. The project note|project note]]. `/setup` writes it only when the framework root holds more than one project.
- **`what`** is optional in an entry: one line naming the repository's surface, its stack, and the kind of work that lands there. The `repo-resolver` agent reasons over it when a ticket does not name its repositories, so an entry without it turns more tickets into questions.

## 2. Behavior

- **Only `/setup` writes the registry.** It merges new entries into an existing file, keeps every entry already there, and reports a changed path instead of replacing it silently. Every other command reads it. A repository missing from it is added by running `/setup` again.
- **The registry is machine-local.** Its paths exist on one machine, so it is gitignored: when the framework root sits inside a git working tree, that tree's `.gitignore` lists `sdlc.json`.
- **A work root that lists `projects` is changed only while working on one of those projects.** Work on any other project never changes it, and a [[glossary#Roadmap run|roadmap run]] never builds in it for another project. A work root with no `projects` may be changed while working on any project.

## 3. Variation and limits

- **The registry is required.** Every framework root holds one `sdlc.json`. A framework root without it can be read, but no run can resolve a work root in it: the run says so and names `/setup`. No command searches the disk for a repository the registry does not name.
- **An older registry keeps working.** A top-level `repos` object is read as `repositories`, and an entry written as a bare path, such as `"web": "~/Projects/acme-web"`, is read as a `path` with no `projects` and no `what`. `/setup` rewrites both into the current form.
