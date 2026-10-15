# Properties, links, and the vault shape

How every document writes its properties and its links, the three places a framework root can sit,
and how a ticket and its worklog move.

## The three destinations

| `kind` | Framework root | What changes |
| --- | --- | --- |
| `vault` | A folder inside an Obsidian vault | Nothing — this is the shape every rule is written for |
| `folder` | Any folder outside the repository | The links: a relative path instead of a wikilink |
| `repo` | `.sdlc/` at the repository root | The links, as in `folder`, and the folder name starts with a dot |

A path is inside an **Obsidian vault** when that path, or one of its parent directories, holds a
`.obsidian/` folder. Check for it by walking up from the framework root.

`vault` is the destination the setup entry point recommends, because the documents then stay
readable outside the repository and out of every branch and diff. `repo` is what every command
falls back to when no pointer file exists.

**No name in a vault starts with a dot.** Obsidian hides dot-folders and dot-files, so a `.sdlc/`
folder inside a vault is invisible. **The vault root is a valid framework root**: a vault kept for
the framework needs no folder inside it. Use a folder inside the vault when the vault root already
holds notes of its own. The setup entry point settles which of the two it is.

## Properties are frontmatter, everywhere

**Every property a document carries is YAML frontmatter, in every destination.** The body never
repeats a property as a `**Field**: value` line, and a command that changes a property rewrites the
frontmatter — there is no second copy to keep in step.

- **`type` names the kind of document** — `project`, `prd`, `glossary`, `goal`, `non-goal`,
  `persona`, `problem`, `metric`, `feature`, `design`, `note`, `roadmap`, `worklog`,
  `business-plan`, or `competitor`. A ticket carries none; its name and its bucket make it a ticket.
- **`tags` holds one entry, `sdlc/<type>`**, so the whole structure is one search. A ticket
  carries none. A note adds a second, `human-required`, so everything that waits on a person is
  one search too.
- **`updated` is the date a document last changed**, `YYYY-MM-DD`, on the kinds whose skill lists
  it — the glossary, the PRD, the roadmap, a design doc, and the business plan. The project note,
  the feature note, and the worklog carry none. A ticket carries `createdAt` and `updatedAt`
  instead; the `ticket-board` skill holds them.
- **Each kind adds its own properties.** The skill that governs the kind holds them: `feature` for
  the feature note, `ticket-board` for the ticket, the roadmap, and the worklog, `product-intent`
  for the five product notes, `design-doc` for the design doc, and so on.
- **Leave a property out when it has no value**, unless its skill says to write it empty.

## Links

**In a vault, a reference from one document to another is a wikilink** — the file name without its
`.md` extension, in double brackets:

- `[[CHECKOUT-001-saved-card]]`, not `` `CHECKOUT-001-saved-card.md` ``
- `[[checkout.feature]]`, not `features/checkout/checkout.feature.md`
- `[[checkout.design]]`, not `checkout.design.md`
- `[[glossary#Work root]]`, not `glossary.md#work-root`

Obsidian resolves a wikilink by name, which is why a ticket keeps its links when it moves between
buckets.

- **Quote a wikilink in a frontmatter property**: `feature: "[[checkout.feature]]"`, because bare
  brackets start a YAML list. In the body, write the wikilink plain.
- **Escape the pipe inside a table**: `[[glossary#Bucket\|buckets]]`. An unescaped pipe ends the
  cell.
- **Cite a section with a heading link labelled in words**:
  `[[checkout.design#3.2 Behavior|how a declined card is retried]]`, never
  `[[checkout.design]] §3.2`. A section number means nothing to a reader, and a `§` breaks the
  technical-writing rule against identifiers in a sentence. A section of the same document is
  `[[#3.2 Behavior|how a declined card is retried]]`.
- **Qualify a name two projects share.** A project's `prd` and `roadmap` are named the same in
  every project, so a link from outside the project names the folder and keeps the display text:
  `[[projects/acme-billing/prd|prd]]`. A link from inside the project's own folder needs no path.

**In a `folder` or a `repo`, a reference is a relative path** from the document to its target:
`../../features/checkout/checkout.feature.md`, `../glossary.md#work-root`. A ticket is named by its
file name alone, because its path changes as it moves.

**Only documents in the framework root become links.** A file path in the code, a command name, a
library, and an external URL stay exactly as they are written elsewhere.

**`depends_on` holds bare IDs, not links** — the one place a reference to another document is not a
link. The ID is what the board cites everywhere else, a ticket's slug can be corrected without
editing every ticket that waits on it, and a query matches an ID exactly.

## One ticket, two destinations

In a vault:

```markdown
---
feature: "[[checkout.feature]]"
status: in progress
priority: High
depends_on:
  - CHECKOUT-001
assigned: coding-2
claimed: orchestrate-2
createdAt: 2026-10-07T09:15
updatedAt: 2026-10-09T14:32
related:
  - "[[checkout.design]]"
---

# [CHECKOUT-002] Saved card

## Description
…
```

In a `repo` or a `folder`:

```markdown
---
feature: ../../features/checkout/checkout.feature.md
status: in progress
priority: High
depends_on:
  - CHECKOUT-001
assigned: coding-2
claimed: orchestrate-2
createdAt: 2026-10-07T09:15
updatedAt: 2026-10-09T14:32
related:
  - ../../features/checkout/checkout.design.md
---

# [CHECKOUT-002] Saved card
```

Same ticket, same properties, same sections. Only the links are shaped for the destination.

## The worklog header

A ticket that work has started on has a worklog beside it — `CHECKOUT-002-saved-card.worklog.md`,
in the ticket's bucket, moving with it. The `ticket-board` skill holds what goes in it.

```markdown
---
type: worklog
ticket: "[[CHECKOUT-002-saved-card]]"
tags:
  - sdlc/worklog
---

# [CHECKOUT-002] Saved card — worklog
```

Outside a vault, `ticket` is the ticket's file name, `CHECKOUT-002-saved-card.md`. A worklog carries
no `status` and no `assigned`: the ticket beside it holds those, and the worklog holds what happened.

## Moving and tracking files

- **Move a ticket with `git mv` only when the file sits inside a git working tree.** A vault is
  usually not one — use a plain `mv` there, and do not report history as preserved.
- **Move a ticket's worklog with it**, in the same step.
- **Write a `.gitkeep` into an empty folder only when the framework root sits inside a git working
  tree.** Git does not track an empty directory; a vault does not need the file.
- **Moving a document out of the repository loses its git history.** Say so before you offer such
  a move, and never make it without an explicit yes.

## Older property values

A document written before the current shape is read with this mapping, and rewritten into the
current form the next time a command writes it:

| Older | Current |
| --- | --- |
| A `**Field**: value` line under the title | The same field as a frontmatter property |
| `**Last updated**:` | `updated` |
| Ticket `Not Started`, `In Progress`, `Blocked`, `Review`, `Completed` | `backlog`, `in progress`, `blocked`, `review`, `done` |
| Ticket `**Assignee**:` or `assignee` | `assigned`, with the run number: `coding-2`. `user` and `—` mean no value |
| Ticket `**Created**:` or `created` | `createdAt`, at `T00:00` when only the date is known |
| Ticket `type`, `id`, `epic`, `tags`, `effort`, `category` | Nothing; the name, the bucket, and `feature` carry them |
| Ticket `**Depends on**:` | `depends_on` |
| Feature `Planned`, `In Progress`, `Shipped` | `backlog`, `in progress`, `done` |
| Registry `repos` | `repositories` |
| `tickets/todo/` | `work/backlog/` |
