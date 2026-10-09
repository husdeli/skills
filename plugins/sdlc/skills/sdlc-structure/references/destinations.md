# Destinations and the vault shape

The three places a docs root can sit, and how a document is written in each.

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
  (`Acme/`), and `product/`, `goals/`, `non-goals/`, `personas/`, `problems/`, `metrics/`,
  `features/`, `designs/`, `diagrams/`, `tickets/`, `todo/`, `in-progress/`, `done/`, `business/`,
  and `competitors/` keep their names.
- **The vault root is a valid docs root.** A vault kept for one product needs no folder inside
  it, and a folder named after the vault (`sdlc-obsidian/sdlc-obsidian/`) helps nobody. Use a
  product-named folder inside the vault instead when the vault root already holds notes of its
  own, so `prd.md` does not land among them. The setup entry point settles which of the two it
  is; every other command takes the docs root from `.sdlc.json` and never second-guesses it.
- File names are unchanged: `prd.md`, `glossary.md`, `roadmap.md`, `checkout.feature.md`,
  `checkout.design.md`, `AUTH-001-user-login.md`.

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
| `**Feature**: …` | `feature:` — a wikilink, quoted |
| `**Priority**: High` | `priority: High` |
| `**Depends on**: AUTH-001, AUTH-004` | `depends_on:` — a list of bare IDs, one per line; `[]` when there are none |
| `**Effort**: M` | `effort: M` |
| `**Category**: feature` | `category: feature` |
| `**Created**: 2026-09-10` | `created: 2026-09-10` |
| `**Code**: CHECKOUT` | `code: CHECKOUT` |
| `**Target**: 500 by 2027-03` | `target: 500 by 2027-03` |
| `**Area**: PAYMENTS` | `area: PAYMENTS` |
| `**Last updated**: 2026-09-10` | `updated: 2026-09-10` |
| `**Product**: Acme` | `product: Acme` |

`related:` is not in this table because it is frontmatter in every destination. See
[Related documents are a frontmatter property](ownership.md#related-documents-are-a-frontmatter-property).

**`depends_on` holds bare IDs, not wikilinks** — the one place in a vault where a reference to
another document is not a link. Three reasons: the ID is what the board cites everywhere else, a
ticket's slug can be corrected without editing every ticket that waits on it, and a query matches
an ID exactly. The clickable link to that sibling is already in `related:`, so the vault loses no
navigation. Write `depends_on: []` when a ticket waits on nothing.

Every document also carries two properties the plugin adds:

- **`type`** — `prd`, `glossary`, `goal`, `non-goal`, `persona`, `problem`, `metric`, `feature`,
  `design`, `roadmap`, `ticket`, `worklog`, `business-plan`, or `competitor`.
- **`tags`** — one entry, `sdlc/<type>`, so the whole structure is one search.

A ticket adds `id` (`AUTH-001`), a design doc adds `subject` (`checkout`), and a worklog adds
`ticket` — the wikilink to the ticket it belongs to. A feature adds `code` (`CHECKOUT`), `area`,
`customer_facing`, `shipped`, `goals`, `personas`, and `non_goals`; the **`feature`** skill holds
what each one means. Each of the five notes under `product/` carries its own fields, and the
**`product-intent`** skill holds those.

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
- `[[checkout.feature]]`, not `features/checkout/checkout.feature.md`

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
---
related:
  - ../../prd.md#authentication-auth
  - AUTH-002-session-timeout.md
---

# [AUTH-001] User login

**Epic**: AUTH — Authentication
**Feature**: `features/auth/auth.feature.md`
**Status**: In Progress
**Assignee**: coding
**Priority**: High
**Depends on**: —
**Effort**: M
**Category**: feature
**Created**: 2026-09-10

## Description
…
```

In a vault:

```markdown
---
type: ticket
id: AUTH-001
epic: AUTH — Authentication
feature: "[[auth.feature]]"
status: In Progress
assignee: coding
priority: High
depends_on: []
effort: M
category: feature
created: 2026-09-10
related:
  - "[[prd#Authentication `AUTH`|AUTH]]"
  - "[[AUTH-002-session-timeout]]"
tags:
  - sdlc/ticket
---

# [AUTH-001] User login

## Description
…
```

Same ticket, same sections, same words. Only the fields and the links are shaped for the
destination that holds them. In both, the related documents are the `related:` property.

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
