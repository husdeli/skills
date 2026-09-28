---
name: product-docs
description: "Rules for where this plugin's product documents live and how each destination writes them — the docs root, the `.sdlc.json` pointer file, and the Obsidian-vault conventions (folder naming, frontmatter properties, wikilinks). INVOKE THIS SKILL before you read, create, move, or update a PRD, a glossary, a design doc, a roadmap, a ticket, or a ticket's worklog, and before you resolve any path under the docs root. Enforces one resolution order for every command and agent, one pointer file per project, and one document shape per destination."
---

# product-docs skill

Every document this plugin reads or writes sits in one folder: the **docs root**. The docs root
holds `prd.md`, `glossary.md`, `roadmap.md`, `designs/`, `diagrams/`, and `tickets/` — and inside
`tickets/`, a worklog beside each ticket that work has started on. This skill says where that folder
is and how the documents inside it are written.

Three skills hold what goes *inside* a document: the **`glossary`** skill for the product's terms
and the links that point at their definitions, the **`diagrams`** skill for a picture of a shape,
and the **`ticket-board`** skill for the board.

## Resolve the docs root before you read anything

In this order, and stop at the first hit:

1. **`.sdlc.json` at the project root** — the pointer file. Its `root` field names the docs
   root, and its `kind` field names the destination. Use them.
2. **`.sdlc/` at the project root** — the default. The destination is `repo`.
3. **Neither** — the project has no docs root. Read whatever it already keeps at the project
   root (`prd.md`/`PRD.md`, `glossary.md`/`GLOSSARY.md`, `*.design.md`, `design.md`,
   `roadmap.md`, `diagrams/`, `tickets/`), and name the platform's setup entry point as the way
   to create the structure.

The **project root** is the directory holding `.git`, `package.json`, `AGENTS.md`, or
`CLAUDE.md` — not the working directory when that sits deeper.

Resolve it **once**, at the start of the run, and resolve every later path against it. Every
path this plugin writes as `.sdlc/…` means `<docs root>/…`.

## The pointer file

`.sdlc.json` lives at the project root and holds two fields:

```json
{
  "root": "~/Vaults/Personal/Acme",
  "kind": "vault"
}
```

- **`root`** — the docs root. An absolute path, a `~`-prefixed path, or a path relative to the
  project root. Expand `~` to the user's home directory. Prefer a relative path when the folder
  sits near the project: an absolute path only resolves on the machine that wrote it.
- **`kind`** — the destination, one of `repo`, `folder`, or `vault`.

The pointer file exists only when the docs root is somewhere other than `.sdlc/`. A project
whose documents live in `.sdlc/` needs no pointer file, and never gets one.

**Never move the docs root on your own.** Only the setup entry point writes or changes
`.sdlc.json`, and only after the user says where the documents go.

## The three destinations

| `kind` | Docs root | What changes |
| --- | --- | --- |
| `repo` | `.sdlc/` at the project root | Nothing — this is the default shape every rule is written for. |
| `folder` | Any folder outside the repository | Only the path. The documents are written exactly as in `repo`. |
| `vault` | A folder inside an Obsidian vault | The path, **and** the document conventions below. |

A path is inside an **Obsidian vault** when that path, or one of its parent directories, holds a
`.obsidian/` folder. Check for it by walking up from the docs root.

`vault` is the destination the setup entry point recommends for a new project, because the
documents then stay readable outside the repository and out of every branch and diff. `repo` stays
the shape every rule below is written for, and the one every command falls back to when no pointer
file exists.

## Writing into a vault

Obsidian reads the docs root as notes. Four things change, and nothing else does — the sections,
the headings, and the words of every document stay the same.

### Folder and file names

- **No name in the docs root starts with a dot.** Obsidian hides dot-folders and dot-files, so a
  `.sdlc/` folder inside a vault is invisible. The docs root is named after the product
  (`Acme/`), and `designs/`, `diagrams/`, `tickets/`, `todo/`, `in-progress/`, and `done/` keep
  their names.
- **The vault root is a valid docs root.** A vault kept for one product needs no folder inside
  it, and a folder named after the vault (`sdlc-obsidian/sdlc-obsidian/`) helps nobody. Use a
  product-named folder inside the vault instead when the vault root already holds notes of its
  own, so `prd.md` does not land among them. The setup entry point settles which of the two it
  is; every other command takes the docs root from `.sdlc.json` and never second-guesses it.
- File names are unchanged: `prd.md`, `glossary.md`, `roadmap.md`, `checkout.design.md`,
  `AUTH-001-user-login.md`.

### Frontmatter properties

Obsidian renders YAML frontmatter as properties, which is what makes a ticket queryable. In a
vault, **every field the document would print under its title moves into frontmatter instead**,
with the same value, and it is not repeated in the body.

The key is the field name in lower case, with `Last updated` as the one exception:

| Field in the body | Property |
| --- | --- |
| `**Status**: In Progress` | `status: In Progress` |
| `**Assignee**: coding` | `assignee: coding` — left empty when the value is `—` |
| `**Epic**: AUTH` | `epic: AUTH` |
| `**Priority**: High` | `priority: High` |
| `**Effort**: M` | `effort: M` |
| `**Category**: feature` | `category: feature` |
| `**Created**: 2026-09-10` | `created: 2026-09-10` |
| `**Last updated**: 2026-09-10` | `updated: 2026-09-10` |
| `**Product**: Acme` | `product: Acme` |
| `**Related**: …` | `related:` — a list |

Every document also carries two properties the plugin adds:

- **`type`** — `prd`, `glossary`, `design`, `roadmap`, `ticket`, or `worklog`.
- **`tags`** — one entry, `sdlc/<type>`, so the whole structure is one search.

A ticket adds `id` (`AUTH-001`), a design doc adds `subject` (`checkout`), and a worklog adds
`ticket` — the wikilink to the ticket it belongs to.

**The property is the record.** When a command sets a ticket's status, it rewrites the
frontmatter `status` property — there is no `**Status**` line in the body to keep in step with
it. The status values are unchanged: `Not Started`, `In Progress`, `Blocked`, `Review`,
`Completed`.

### Links

Inside a vault, a reference from one document in the docs root to another is a **wikilink** —
the file name without its `.md` extension, in double brackets:

- `[[AUTH-001-user-login]]`, not `` `AUTH-001-user-login.md` ``
- `[[prd]]`, not `../prd.md`
- `[[checkout.design]]`, not `checkout.design.md`

Obsidian resolves a wikilink by name, which is why a ticket keeps its links when it moves
between the status folders.

- **Quote a wikilink in a frontmatter property**: `related:` takes `"[[prd]]"`, because bare
  brackets start a YAML list. In the body, write the wikilink plain.
- **Qualify an ambiguous name.** When the vault holds more than one product folder, name the
  folder and keep the display text: `[[Acme/prd|prd]]`.

**Only documents in the docs root become wikilinks.** A file path in the code, a command name, a
library, and an external URL stay exactly as they are written elsewhere.

### Moving and tracking files

- **Move a ticket with `git mv` only when the file sits inside a git working tree.** A vault is
  usually not one — use a plain `mv` there, and do not report history as preserved.
- **Move a ticket's worklog with it.** `AUTH-001-user-login.worklog.md` sits in the same folder
  as `AUTH-001-user-login.md` and follows it into `done/`, in the same step.
- **Write a `.gitkeep` into an empty folder only when the docs root sits inside a git working
  tree.** Git does not track an empty directory; a vault does not need the file, and Obsidian
  shows it as clutter.
- **Moving a document out of the repository loses its git history.** Say so before you offer
  such a move, and never make it without an explicit yes.

## One ticket, two destinations

In the repository:

```markdown
# [AUTH-001] User login

**Epic**: AUTH — Authentication
**Status**: In Progress
**Assignee**: coding
**Priority**: High
**Effort**: M
**Category**: feature
**Created**: 2026-09-10

## Description
…

## Related
- PRD area: `AUTH`
- Sibling: `AUTH-002-session-timeout.md`
```

In a vault:

```markdown
---
type: ticket
id: AUTH-001
epic: AUTH — Authentication
status: In Progress
assignee: coding
priority: High
effort: M
category: feature
created: 2026-09-10
tags:
  - sdlc/ticket
---

# [AUTH-001] User login

## Description
…

## Related
- PRD area: `AUTH`
- Sibling: [[AUTH-002-session-timeout]]
```

Same ticket, same sections, same words. Only the fields and the links are shaped for the
destination that holds them.

## The worklog, in both destinations

A ticket that work has started on has a worklog beside it — `AUTH-001-user-login.worklog.md`,
in the ticket's folder, moving with it. The `ticket-board` skill holds what goes in it.
Only its header changes by destination.

In the repository:

```markdown
# [AUTH-001] User login — worklog

**Ticket**: `AUTH-001-user-login.md`
```

In a vault:

```markdown
---
type: worklog
id: AUTH-001
ticket: "[[AUTH-001-user-login]]"
tags:
  - sdlc/worklog
---

# [AUTH-001] User login — worklog
```

The entries under the header are the same in both. A worklog carries no `status` and no
`assignee`: the ticket beside it holds those, and the worklog holds what happened.
