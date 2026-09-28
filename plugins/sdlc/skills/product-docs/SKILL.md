---
name: product-docs
description: "Rules for where this plugin's documents and code live and how each destination writes them — the docs root, the work root, the `sdlc.json` registry that names every repository a product is built in, the `.sdlc.json` pointer file, and the Obsidian-vault conventions (folder naming, frontmatter properties, wikilinks). INVOKE THIS SKILL before you read, create, move, or update a PRD, a glossary, a design doc, a roadmap, a ticket, or a ticket's worklog, before you resolve any path under either root, and before you run any command against a repository that is not the working directory. Enforces one resolution order for every command and agent, one registry per product, and one document shape per destination."
---

# product-docs skill

Every document this plugin reads or writes sits in one folder: the **docs root**. The docs root
holds `prd.md`, `glossary.md`, `roadmap.md`, `designs/`, `diagrams/`, and `tickets/` — and inside
`tickets/`, a worklog beside each ticket that work has started on. Every line of code it writes
sits in a **work root**: one code repository. This skill says where each root is, how to find one
from the other, and how the documents inside the docs root are written.

Three skills hold what goes *inside* a document: the **`glossary`** skill for the product's terms
and the links that point at their definitions, the **`diagrams`** skill for a picture of a shape,
and the **`ticket-board`** skill for the board.

## The two roots

| Root | What it holds | How many |
| --- | --- | --- |
| **docs root** | Every document: the PRD, the glossary, the design docs, the diagrams, the roadmap, the tickets, and the worklogs | One per product |
| **work root** | The code: one repository, with its own instructions, its own test suite, and its own git history | One per repository — a product may have several |

One docs root drives one or more work roots. The PRD says what the product does; the repositories
the registry names are where that product is built.

**The work root is not always the working directory.** A run started in the vault has the docs root
as its working directory and reaches into a repository somewhere else. Every path and every command
below says which root it belongs to, and none of them assume the two are the same folder.

## The two directions

A session starts in one of two places, and that is what decides how the roots are found.

**Vault-rooted** — the working directory is the docs root itself, usually a folder in an Obsidian
vault. The docs root is where you already are, and the work roots come from the registry,
`sdlc.json`. The run resolves which repository each task is built in. **This is the recommended
shape.** One board drives every repository the product is built from, so a task that lands in the
API and a task that lands in the web app are picked from the same roadmap, in one session.

**Repo-rooted** — the working directory is inside a code repository. That repository is the work
root, and the docs root comes from the forward pointer, `.sdlc.json`. One repository, one product.
This is the shape for a project built from a single repository, and it is what a session started
inside a repository always gets.

Both pointers exist at the same time: the setup entry point writes the registry in the docs root
and a `.sdlc.json` in every repository it names. A product set up once can then be driven from
either end, and the two never disagree.

## Resolve the roots before you read anything

Do this **once**, at the start of the run, and resolve every later path against what it gives you.

**Step 1 — is this session vault-rooted?** A directory is a **docs root** when it holds
`sdlc.json`, or when it holds `roadmap.md` or `prd.md` together with a `tickets/` folder. Test the
working directory, then each parent, stopping at the vault root or the home directory.

- **Found, and the folder sits outside every code repository** → the session is vault-rooted. That
  directory is the docs root, and `sdlc.json` holds the work roots.
- **Found, and the folder sits inside a code repository** — a project that keeps its board at its
  own root, or a docs root in `.sdlc/` you happen to be standing in → the docs root is that folder,
  and the session is **repo-rooted**: the repository around it is the work root, and no registry is
  read. A board inside the code belongs to the code around it.
- **The working directory is a vault root** — it holds `.obsidian/` — **and holds several docs
  roots**, one folder per product → the product is not settled yet. Take it from the command's
  arguments when they name one, and ask the user otherwise. Never guess when two products are in
  reach.

**Step 2 — otherwise the session is repo-rooted.** Find the docs root from the project root, in
this order, and stop at the first hit:

1. **`.sdlc.json` at the project root** — the pointer file. Its `root` field names the docs
   root, and its `kind` field names the destination. Use them.
2. **`.sdlc/` at the project root** — the default. The destination is `repo`.
3. **Neither** — the project has no docs root. Read whatever it already keeps at the project
   root (`prd.md`/`PRD.md`, `glossary.md`/`GLOSSARY.md`, `*.design.md`, `design.md`,
   `roadmap.md`, `diagrams/`, `tickets/`), and name the platform's setup entry point as the way
   to create the structure.

The **project root** is the directory holding `.git`, `package.json`, `AGENTS.md`, or
`CLAUDE.md` — not the working directory when that sits deeper. In a repo-rooted session the
project root is the work root, and no registry is read.

Every path this plugin writes as `.sdlc/…` means `<docs root>/…`.

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

The pointer file points one way, from a repository to the documents. The registry below points the
other way, from the documents to every repository. The setup entry point writes both, so a product
can be driven from either end.

## The registry

`sdlc.json` sits **in the docs root** and names every repository the product is built in:

```json
{
  "repos": {
    "web": {
      "path": "~/Projects/acme-web",
      "what": "TanStack Start app — every screen, and the server functions behind them"
    },
    "api": {
      "path": "~/Projects/acme-api",
      "what": "Fastify service — the HTTP API, the background jobs, and the database"
    }
  }
}
```

- The key is the repository's **code**: short, lower case, and stable. It is how a worklog, a
  report, and a result line name that repository.
- **`path`** — absolute, `~`-prefixed, or relative to the docs root. Expand `~` to the user's home
  directory.
- **`what`** — one line saying what the repository is and what belongs in it. This line is what the
  work-root resolution below reasons over, so write it for that job: name the surface, the stack,
  and the kind of work that lands there. An entry with no `what` turns every ambiguous task into a
  question for the user.
- `"web": "~/Projects/acme-web"` is accepted shorthand for a path with no `what` line. The setup
  entry point always writes the full form.

**The registry is machine-local, and it is gitignored.** It holds paths that exist on one machine,
so it never travels. When the docs root sits inside a git working tree, the setup entry point adds
`sdlc.json` to that tree's `.gitignore`; a vault is usually no working tree, and then there is
nothing to ignore. Never commit it, and never overwrite another machine's paths in it.

**Only the setup entry point writes the registry.** Every other command reads it. A repository that
is missing from it is added by running setup again from inside that repository — never by editing
the file in the middle of a task.

A docs root with **no `sdlc.json`** drives one repository: the one whose `.sdlc.json` points back at
it. A vault-rooted session cannot find that repository, so it says so and names the setup entry
point. Never search the disk for a repository the registry does not name.

## Resolve the work root

**A ticket never names its repository.** The board stays about the product, and a repository code
written into a ticket goes stale the moment a repository is renamed, split, or merged. The run
works it out instead — once, when the task is picked.

In this order, and stop at the first that answers:

1. **A repo-rooted session** → the work root is the session's own repository. Nothing to resolve.
2. **One entry in the registry** → that entry is the work root.
3. **Several entries** → read the evidence, in this order, and take the repository it points at:
   - the design doc the ticket cites, and the parts of the system it names;
   - the ticket's description, its acceptance criteria, and any path, route, or module it names;
   - the epic's name and its `**Note**:` line;
   - each registry entry's `what` line;
   - the candidate repositories themselves — list the top level, and grep for the symbol, the
     route, or the file the ticket names. The tree that already holds the code the task changes is
     the tree the task lands in.
4. **Still open** → ask. That is one `AskUserQuestion` naming the candidates and what each one would
   mean, or, in an unattended run, a `work-root` request to the `cto` agent. Never guess in silence,
   and never start in two repositories because the evidence was thin.

**Take the smallest set of repositories that satisfies every acceptance criterion** — almost always
exactly one.

**A task that truly spans two repositories keeps both.** Each work root is then its own job: its own
conventions, its own verification commands, its own code review, and its own commit. The task passes
only when every work root passes. Say in the report that the task spanned two repositories, and say
which shape it should have had — a contract change that must land on both sides at once earns one
ticket; anything that could ship in two steps is two tickets, linked by `Depends on`.

**Write the work root into the worklog, in the entry that starts the work** — the code, the absolute
path, and the one line of evidence that settled it. The ticket carries no such field, so the worklog
is the only record. A later session resuming that ticket reads it there instead of resolving it a
second time, and a person reading `done/` can see where each task landed.

## Working in a repository that is not the working directory

This is the vault-rooted session: the docs root is the working directory, and the code is somewhere
else. A repo-rooted session can skip the whole section.

- **The session has to be allowed to reach the repository.** In Claude Code, start it from the docs
  root as `claude --add-dir <work root>`, or run `/add-dir <work root>` once inside the session. A
  tool call that cannot write to the work root is a setup problem, not a task failure: name the
  command that fixes it and stop.
- **Every shell command names the repository.** Run git as `git -C <work root> …`, and run a build,
  a test, or a package manager as `cd <work root> && …`. A bare `npm test` runs in the vault and
  proves nothing.
- **Every brief that leaves this session carries the work root as an absolute path**, and every
  relative path in that brief resolves against it.
- **The repository's own instructions govern its code.** Read the `AGENTS.md` and `CLAUDE.md` of the
  work root, not the ones beside the vault. Two work roots may carry two different sets of
  conventions, and a change follows the ones in the tree it lands in.
- **Git belongs to the work root.** The branch, the diff, the commit, and the history are the
  repository's. The docs root is usually no git working tree at all, so a code commit never carries
  the ticket move or the roadmap edit with it. When the docs root *is* its own git working tree, it
  gets its own commit, in its own tree.

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
