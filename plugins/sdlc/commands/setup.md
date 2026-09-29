---
description: Create the folder that holds the PRD, the glossary, the features, the design docs, the diagrams, the roadmap, and the tickets — in an Obsidian vault, or in the repository — and register the repositories the product is built in.
argument-hint: [product name] [destination path] [repository paths]
---

# Setup

Create the **docs root** — the single home for every document this plugin reads and writes — and
**register the repositories** the product is built in, so a later run can start from either end.

The recommended home is a folder in an **Obsidian vault**, outside the repository: the documents
stay readable and editable wherever the vault syncs, they stay out of every diff and merge, one
vault holds every project, and one board can drive **several repositories** — the web app and the
API are then two entries in one registry, and one roadmap covers both. The docs root can also sit in
the repository as `.sdlc/`, which is where every command looks when no pointer file says otherwise.

**This command runs from either end.** Start it inside a code repository, and it sets up the
documents for that repository. Start it in the vault — in the docs root, or in a vault that holds
one folder per product — and it sets up the documents there and asks which repositories they drive.
`product-docs` holds how that is detected; resolve it before Step 1.

Arguments (if provided): $ARGUMENTS

Load four skills before you create anything, namespaced here as `sdlc:<name>`: **`product-docs`**,
which holds the resolution order, the two pointer files, and the vault conventions this command
writes, **`ticket-board`**, which holds the shape of the tickets and the roadmap it creates and
migrates, **`feature`**, which holds the feature folder, the index note, and the code that ties
a feature to its epic, and **`product-intent`**, which holds the five notes the PRD is assembled
from and the migration that splits an existing PRD into them.

```
<docs root>/
  sdlc.json             the repositories this product is built in — machine-local,
                        gitignored, and the file a vault-rooted run reads first
  prd.md                product requirements — the overview and the product areas in prose,
                        and one line per note in product/ for the rest
  glossary.md           the product's terms — one ## heading per term, defined once
                        here and linked from every other document
  roadmap.md            the work that is left, in order, grouped by epic
  product/              the pieces the PRD is assembled from — one note each, because
    goals/              a feature, a design doc, or the business plan points at them
    non-goals/          and each one has a state of its own
    personas/
    problems/
    metrics/
  features/             one folder per feature — one thing a customer can do
    <feature>/
      <feature>.feature.md   the index — what the customer can do, and its state.
                             Carries the code that numbers the feature's tickets
      <subject>.design.md    the design docs that belong to this feature
  designs/
    overview.design.md  the design docs that underpin every feature — an app shell, an
                        auth model, a shared data model. One file per subject, named
                        <subject>.design.md; overview is the entry point
  diagrams/             one .excalidraw.md file per diagram, referenced by any document
  tickets/
    TEMPLATE.md         copy this per task, named <EPIC>-<NNN>-<slug>.md
    todo/               a ticket waits here until an orchestrator starts it
    in-progress/        the ticket being built — in progress, blocked, or in review,
                        with its worklog beside it
    done/               a completed ticket, and its worklog
```

Each kind of document has its own folder once there can be more than one of it. A design doc
covers one subject and stays where its ownership puts it — the feature's folder when it belongs to
one feature, `designs/` when it underpins every feature. A ticket moves between
the three status folders as its status changes — the `ticket-board` skill holds the mapping and the
move rules. **A worklog appears beside a ticket in the step that starts the work**, holds what each
agent decided while the ticket was built, and moves with the ticket into `done/`. Write none here:
there is no ticket yet to put one beside.

## Rules

- **Never overwrite.** Create a file only when it does not exist. Report each existing file
  as kept, and leave its contents alone.
- **One design stub, at most.** Write `designs/overview.design.md` only when the project has no
  design doc at all — no `*.design.md` file in `features/*/`, in `designs/`, in the docs root
  itself, or at the project root, and no single `design.md` in any of those places. Report the one
  it already has as kept.
- **Write stubs, not content.** Each stub carries only the headings and the placeholder
  lines below. Do not invent product requirements, surfaces, or tasks — the person fills
  them in, or `/prd` and `/design` do.
- **Substitute the product name** wherever the stubs show `<product>`, when the arguments
  gave one. Otherwise leave `TBD`.
- **Settle the destination before you create anything** — Step 1. The repository option puts
  the docs root at `.sdlc/` in the project root: the directory holding `.git`, `package.json`,
  `AGENTS.md`, or `CLAUDE.md`. Not the current working directory when that sits deeper.
- **Register every repository** — Step 2. A docs root with no registry can only be driven from
  inside a repository, which is the thing this command exists to fix.
- **Write no feature, and no product note.** `features/` and the five folders under `product/` are
  created empty. A feature is opened when the product has one, and a goal, a persona, or a problem
  is written when `/prd` settles it. Inventing either here invents a commitment nobody made.
- **Create `product/` with its five folders, `features/`, `designs/`, `diagrams/`, and all three
  ticket status folders**, even though they start empty.
  Write a `.gitkeep` file into every one that ends up with no file in it **when the docs root
  sits inside a git working tree**, because git does not track an empty directory. A docs root
  outside git gets no `.gitkeep` — it is clutter in a vault.

## 1. Settle the destination

The docs root goes where the user keeps this kind of writing. Decide where, in this order, and
stop at the first that applies:

- **This session is vault-rooted** — the working directory is a docs root, or a vault holding one
  → the destination is settled before you ask anything. The docs root is that folder; when the
  vault holds several product folders, take the product from the arguments, and ask which one
  otherwise. Fill the gaps there and go to Step 2, which is the step that has work to do.
- **`.sdlc.json` already exists** at the project root → read it. The destination is settled.
  Report where the documents live and fill the gaps there. Do not ask.
- **`.sdlc/` already exists** → the destination is the repository. You are filling gaps, not
  choosing. Do not ask.
- **The arguments name a path** — an absolute path, a `~`-prefixed path, or anything holding a
  path separator → that is the destination. The rest of the arguments is the product name.
- **Otherwise, ask.** One question, two options:
  - **In an Obsidian vault** — recommended. The documents are readable and editable without the
    repository, on every device the vault syncs to, and Obsidian's properties, backlinks, and
    search work on the whole board. They sit outside the code, so a branch switch never changes
    the roadmap, two branches never conflict over a ticket, and a pull request carries the code
    alone. One vault holds every project. Ask for the vault path in the same turn, or take it
    from the user's "Other" answer.
  - **In the repository (`.sdlc/`)** — the documents are versioned with the code, they travel
    with a clone, and a review sees a document change beside the change it describes. Take this
    option when the user keeps no vault, or when the team reads the documents only through the
    repository.

  In Codex, ask the same question in prose: a Codex session has no `AskUserQuestion` tool.

  **When the user picks the vault and names no path**, offer the vaults you can find: search for a
  `.obsidian/` folder a few levels deep under the user's home directory — `~/Documents`,
  `~/Obsidian`, `~/Vaults`, and the iCloud Obsidian folder — and list each vault you find. Keep the
  search shallow; never walk the whole home directory. When it finds nothing, ask for the path, and
  take the repository when the user keeps no vault.

**Then classify the destination.** Walk up from the chosen path looking for a `.obsidian/`
folder — in the path itself, or in any parent directory:

- **Found** → the destination is a **vault**. Name the vault in your report. Never name a folder
  in a vault with a leading dot: Obsidian hides it. If the user asked for `.sdlc` inside a
  vault, say why it would be invisible and offer the product-named folder instead.

  **When the chosen path is the vault root itself**, look at what that folder already holds,
  ignoring `.obsidian/`:

  - **Nothing, or only this plugin's own documents** — `prd.md`, `glossary.md`, `roadmap.md`,
    `designs/`, `diagrams/`, `tickets/` → **the vault root is the docs root.** A vault kept for
    one product needs no folder inside it, and a folder named after the vault
    (`sdlc-obsidian/sdlc-obsidian/`) helps nobody. Do not ask, and never nest.
  - **Notes of its own** — any other note or folder → say that `prd.md`, `glossary.md`, and
    `roadmap.md` would land among those notes, and offer a product-named folder inside the vault
    (`<vault>/Acme/`) as the alternative. The user chooses; take the vault root when they
    confirm it.
- **Not found**, and the path is outside the repository → the destination is a **folder**.
- **Inside the repository** → the destination is the **repository**, and the docs root is
  `.sdlc/`.

**Write the pointer file** at the project root when the docs root is anything other than
`.sdlc/`, so every other command finds the documents:

```json
{
  "root": "~/Vaults/Personal/Acme",
  "kind": "vault"
}
```

Use a path relative to the project root when the folder sits near the project. Otherwise write
the absolute path, and say in your report that it only resolves on this machine — the user
decides whether to commit the file.

A **vault destination changes how the documents are written**, not what they say: frontmatter
properties instead of the `**Field**: value` lines, wikilinks instead of file names and relative
paths, and no `.gitkeep`. The `product-docs` skill holds the mapping. A **folder** destination
changes nothing but the path.

## 2. Register the repositories

The docs root drives the code. **`sdlc.json` in the docs root names every repository this product
is built in**, and it is what lets a session started in the vault work on any of them. The
`product-docs` skill holds its shape; this step writes it.

**Collect the repositories.** Take them in this order:

- **The arguments name repository paths** → use them.
- **This session is repo-rooted** — you are standing in a code repository → that repository is the
  first entry. Ask whether the product has others, and take the paths the user gives.
- **This session is vault-rooted** — you are standing in the docs root → ask for the path of every
  repository the product is built in. One is a complete answer; a product with a web app and an API
  gives two.

**Write one entry per repository**, keyed by a short lower-case code the user recognises — `web`,
`api`, `mobile`, `infra`. Derive the code from the repository's own name and offer it; the user
overrides it. Each entry carries the `path` and a `what` line:

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

**The `what` line is the one part of this file that has to be written well.** Every later run reads
it to work out which repository a task is built in, because no ticket carries that field. Write it
from the repository itself — read its `README.md`, its `package.json`, and its top-level folders —
and name the surface, the stack, and the kind of work that lands there. Never write `what` as the
repository's name again. Show each line to the user with the path, and correct what they correct.

**Then write the two pointers, so the product can be driven from either end:**

1. **`sdlc.json` in the docs root** — the registry above. Never overwrite an existing registry:
   merge the new entries into it, keep every entry that is already there, and report a path that
   changed rather than replacing it silently.
2. **`.sdlc.json` at the root of every repository in the registry** — the pointer back to the docs
   root, exactly as Step 1 writes it. A repository you cannot reach from this session is reported
   as unregistered, with the one command that fixes it: run setup again from inside it.

**Gitignore the registry.** It holds paths that exist on this machine only. When the docs root sits
inside a git working tree, append the registry's path relative to that tree's root to its
`.gitignore` — `.sdlc/sdlc.json` for a docs root in the repository — as one line, never replacing
the file, and never a second time when the line is already there. A vault is usually no working
tree, and then there is nothing to ignore. Say in the report that the file is machine-local either
way.

**A product with one repository still gets a registry.** It costs one file, and it is what makes a
vault-rooted run possible later without a second setup.

## 3. Check what is already there

Look for documents this plugin would otherwise create twice:

- The docs root itself — if it exists, you are filling gaps, not setting up.
- Root-level `prd.md`, `PRD.md`, `glossary.md`, `GLOSSARY.md`, `design.md`, `DESIGN.md`,
  `roadmap.md`, `ROADMAP.md`.
- A root-level `tickets/` directory.
- A design doc in any shape: `*.design.md` files in `<docs root>/features/*/`, in
  `<docs root>/designs/`, in the docs root itself, or at the project root; or a single `design.md`
  in any of those.
- A `features/` directory, and whether it holds a feature note.

If any of these exist outside the docs root, **ask before touching them**: offer to
move each into the folder with `git mv` (preserving history), or to leave it where it is.
Moving a file is the user's call — never move one without an explicit yes. A file left in
place still works: every agent falls back to the project root when the folder has no such
document.

**A move out of the repository loses the file's git history**, because `git mv` cannot cross
into a folder git does not track. Say that plainly whenever the docs root is a vault or an
outside folder, before you offer the move, and use a plain `mv` when the user says yes.

**Design docs outside a folder** need the same explicit yes. A design doc lives in
`<docs root>/features/<feature>/` when it belongs to one feature, and in `<docs root>/designs/`
when it underpins every feature. One file per subject, named `<subject>.design.md`, so anything
else is an older shape. Gather them into `designs/` first, then offer the feature migration below:

- `*.design.md` files in the docs root itself or at the project root → offer to move each
  one into `designs/` under the same name, and report the count moved.
- A single `design.md`, in the docs root or at the project root → offer to move it to
  `designs/overview.design.md`. Say the rename is only a rename: no
  content moves, and splitting it by subject is a later job for `/design`.

When the user says no, leave every file where it is: every agent reads the older shapes as a
fallback. Skip the offer when `<docs root>/designs/` already holds the docs.

**A PRD that still holds its goals, personas, problems, and metrics inline** needs the same
explicit yes. Those five pieces are notes under `product/`, because a feature, a design doc, and
the business plan all point at them, and because each has a state of its own — met, dropped,
deferred, measured. The `product-intent` skill holds the shape. A PRD whose sections 2, 3,
4, and 7 are written out as prose and tables is on the older shape.

Say what the split buys before you offer it: a goal becomes something a feature can cite and a
query can count, so "which features advance this goal" and "which goal has nothing being built for
it" become answerable. Say what it costs: the PRD stops being one file a reader can read top to
bottom without following links. Then offer it in three steps, and stop at any step the user does
not approve:

1. **Propose the notes.** Read the PRD's sections 2, 3, 4, and 7. Each numbered failure mode is a
   problem, each goal a goal, each non-goal a non-goal, each persona row a persona, and each metric
   a metric. Show the whole mapping as one table — type, file name, and the statement each note
   would carry — and name any item that splits into two notes or that you would leave inline
   because it is really prose. Ask the user to accept it, rename a note, merge two, or drop a row.
2. **Write the notes.** One file per approved row, with the properties `product-intent` defines.
   Carry the words the PRD already uses; do not rewrite a goal while you move it. Set each `status`
   from what the PRD says and the work root shows, and report any you could not settle.
3. **Rewrite the PRD and every reference.** Replace sections 2, 3, 4, and 7 with one line per
   note — the link, then the statement in a few words — and leave sections 1, 5, and 6 untouched:
   they are prose, and prose does not decompose. Then set the `goals` and `personas` properties on
   each feature that has an obvious one, link the personas from the business plan's segment table
   and the metrics from its milestones, and report what you could not match. Report the counts:
   notes written per type, PRD sections rewritten, features and plan sections linked.

When the user says no, create `product/` empty and leave the PRD whole: every command reads that
shape as a fallback. Skip the offer when `product/` already holds a note.

**A project with no `features/` folder** needs the same explicit yes. A **feature** is one thing a
customer can do: it owns a folder, an index note that says what the customer can do and whether it
is shipped, the design docs for that feature, and the code that numbers its tickets. The `feature`
skill holds the shape. A project whose design docs all sit in `designs/`, or whose roadmap has
epics but no feature notes, is on the older shape.

Say what the migration buys before you offer it: the feature register becomes the list of what the
product does, so the business plan, the roadmap, and every design doc point at one place instead of
three. Say what it costs: a design doc that moves changes its path, so a note or a bookmark that
cites the old path stops resolving. Then offer it in three steps, and stop at any step the user
does not approve:

1. **Propose the features.** Read the roadmap's epics, the design docs in `designs/`, and the PRD's
   product areas. Each epic is a candidate feature, and its code is the feature's code. Each design
   doc is either a feature's doc or cross-cutting. Show the whole mapping as one table — feature
   name, code, PRD area, status, and the design docs that move into it — with a second short table
   of the docs that stay in `designs/` and why. Ask the user to accept it, rename a feature, move a
   doc, or drop a row.
2. **Create the folders and the index notes.** One folder per approved feature, and one
   `<feature>.feature.md` in each, with the properties the `feature` skill defines. **Check each
   status against the work root** before you write it — an epic with rows left is `In Progress` or
   `Planned`, and a feature is `Shipped` only when the code holds the whole of it. Report any
   feature whose evidence disagreed with the roadmap.
3. **Move the design docs and rewrite every reference.** Move each approved doc with `git mv` into
   its feature's folder, keeping its name. Add a `**Feature**:` line to each roadmap epic section
   that now has a feature. Then search the docs root for every moved path and fix what that finds —
   a `Related` line, a ticket, a diagram caption, the business plan. Report the counts: features
   opened, docs moved, docs kept in `designs/`, references rewritten.

When the user says no, create `features/` empty and leave every design doc in `designs/`: every
agent reads that shape as a fallback. Skip the offer when `features/` already holds a feature.

A **flat tickets folder** needs the same explicit yes. That is a `tickets/` directory holding
ticket files directly, with no `todo/`, `in-progress/`, or `done/` inside it. Offer to create
the three folders and to move each ticket into the one its status field names, and report
the count per folder afterwards. When the user says no, leave every file where it is: a flat
folder still works, because every agent reads the status field inside the ticket.

**Ticket IDs with no epic** need the same explicit yes. Every ticket ID starts with the code of
the epic that holds it, and the numbering restarts at 001 in each epic — the `ticket-board` skill
holds the rule, and the roadmap holds the list of epics. A project
whose tickets all share one project-wide prefix (`SW-001`, `SW-002`, …), or whose roadmap has no
`## <CODE> — <epic name>` sections, is on the older shape. Say what the rename costs before you
offer it: a branch, a review, or a note that cites an old ID stops finding the file, so this
belongs in a quiet moment and not in the middle of a task. Then offer the migration in three
steps, and stop at any step the user does not approve:

1. **Propose the epics.** Group the existing tasks by the feature each one delivers, name each
   group, and give it a code. Number the tasks inside each group from 001, following the
   roadmap's existing order. Show the whole mapping as one table — epic, old ID, new ID, task
   title — and ask the user to accept it, rename an epic, or move a task to another epic.
2. **Rename the tickets** with `git mv`, one file per row of the approved table. A ticket keeps
   its slug and its status folder; only the ID in the file name changes. Rewrite the `#` title
   line inside each file, and add the `**Epic**` field under it — the `epic` property, in a
   vault.
3. **Rewrite every reference.** Group the roadmap rows into one `##` section per epic, and
   rename each ID in the tables, in the `Depends on` cells, and in the `Ticket` cells. Then
   search the whole project for each old ID and fix what that finds — a ticket's `Related`
   links, a design doc, a note, a feature note's `code`. Report the count renamed and the files
   touched.

When the user says no, leave every ID alone, and say that new tickets keep continuing the
project's own scheme. Never rename part of the set: a half-migrated project cites two schemes
and matches neither. Skip the offer when the roadmap already has epic sections.

**A roadmap that still holds finished work** needs the same explicit yes. The roadmap lists the
work that is left, so a completed row, a `✅ **Completed**` status, a done section, or a `###`
detail section per task is the older shape. Say what the cleanup removes before you offer it:
the roadmap keeps no history, and the ticket in `tickets/done/` becomes the only record of a
finished task. Then offer it as one edit, and show the user what it does:

- **Delete every completed task** — its row, and its `###` detail section. Confirm each one
  against the tickets first: a row marked completed whose ticket is not in `done/` stays, and
  you report the disagreement instead of resolving it.
- **Delete its ID from every `Depends on` cell**, writing `—` in a cell that has nothing left.
- **Delete every remaining `###` detail section.** What it holds belongs to the ticket, so
  before you delete one, copy anything the ticket is missing into that ticket — the description
  into `Description`, the criteria into `Acceptance Criteria`. Never delete the only copy of a
  pending task's criteria.
- **Add a `Ticket` column** to each table, carrying the file name the deleted detail section
  cited — the wikilink, in a vault.
- **Delete an epic section** whose last row is gone, and bump `**Last updated**`.

Report the counts: tasks removed, detail sections folded into tickets, epics closed. When the
user says no, leave the roadmap exactly as it is — every command reads the older shape as a
fallback. Skip the offer when the roadmap already holds pending work only.

## 4. Write the stubs

The stubs below are the repository shape. **In a vault, write the same stub with its fields as
frontmatter properties** — the `product-docs` skill holds the field-to-property mapping and the
`type` and `tags` properties every document carries. Everything under the frontmatter is
unchanged, except that a reference to another document in the docs root becomes a wikilink.

**`<docs root>/prd.md`**

```markdown
# Product Requirements Document

**Status**: Draft
**Last updated**: <today, YYYY-MM-DD>
**Product**: <product> — <one-line description>

---

## 1. Overview

<What the product is and what it does, in 2-4 sentences. End with 3-5 core principles.>

## 2. Problem statement

<One line per note in `product/problems/`: the link, then the failure in a few words. The
note holds the failure; the goal that answers it says what this product does about it.>

## 3. Goals & non-goals

### Goals

- <One line per note in `product/goals/`: the link, then the statement in a few words.>

### Non-goals (current scope)

- <One line per note in `product/non-goals/`: the link, then the exclusion in a few words.
  The reason lives in the note, where it is required.>

## 4. Users & personas

- <One line per note in `product/personas/`: the link, then the need in a few words. The
  note holds the need and the primary flow.>

## 5. How the product works

### <Product area> `AREA`

<A few short paragraphs describing how this area works and how it connects to the others.
One stable uppercase anchor code per area, in the heading.>

## 6. Cross-cutting qualities

<The guarantees holding across the whole product — security, privacy, offline, reliability
— grouped by theme, each stated positively.>

## 7. Success metrics

- <One line per note in `product/metrics/`: the link, then the target. The definition and
  the last measured value live in the note.>

## 8. Open questions

- <A concrete product decision that blocks design or implementation.>
```

In a vault, the three fields lead the file as properties instead:

```markdown
---
type: prd
product: <product>
status: Draft
updated: <today, YYYY-MM-DD>
tags:
  - sdlc/prd
---

# Product Requirements Document

## 1. Overview
…
```

**`<docs root>/glossary.md`**

```markdown
# <product> — glossary

**Last updated**: <today, YYYY-MM-DD>

One entry per term this product uses, in alphabetical order. Every other document links the term's
heading here instead of writing the definition again.

## <Term>

<Two or three sentences: what the thing is, and the one fact that separates it from the term
nearest to it.>
```

In a vault, the field becomes a property and the term headings are unchanged:

```markdown
---
type: glossary
product: <product>
updated: <today, YYYY-MM-DD>
tags:
  - sdlc/glossary
---

# <product> — glossary
…
```

Write the placeholder term only — never invent terms. `/prd`, `/design`, and `/plan` fill the
entries as the product gains them, and the **`glossary`** skill holds the rules they follow.

**`<docs root>/designs/overview.design.md`** — the entry-point design doc, for the subjects that
underpin every feature. A subject that belongs to one feature gets its `<subject>.design.md` in
that feature's folder instead. `/design` writes both.

```markdown
# <product> — design

**Last updated**: <today, YYYY-MM-DD>
**Related**: `../prd.md`

<One or two sentences: what the product is built from, and where the detail lives. Never
what this document covers or leaves out.>

---

## 1. Foundations

<Only the rules holding across every part below, that a later section relies on instead of
restating. Three to seven bullets, qualitative. Omit the section when there are none.>

---

## 2. <First part, flow, or surface>

<One sentence naming its role. Do not repeat the heading.>

### 2.1 Structure

<A reference to the diagram of the parts and what connects them, with a one-line caption. The
`diagrams` skill says how one is drawn and where it lives.>

### 2.2 Behavior

<One unit of work followed from where it enters to where it leaves.>

### 2.3 States

| State | What happens |
| --- | --- |
| <state> | <what this design does that a reader would not assume> |

### 2.4 Variation and limits

<How the behavior changes by role, configuration, volume, or screen width, and the limits
it holds within.>
```

In a vault, the fields and the reference become properties, and `../prd.md` becomes `[[prd]]`:

```markdown
---
type: design
subject: overview
updated: <today, YYYY-MM-DD>
related:
  - "[[prd]]"
tags:
  - sdlc/design
---

# <product> — design
…
```

Keep only the sections that have something specific to say — an empty heading is deleted,
never filled — and leave out any part that is not designed yet.

**`<docs root>/roadmap.md`**

```markdown
# <product> — roadmap

**Last updated**: <today, YYYY-MM-DD>

This file holds the work that is left. A task is deleted from it when the task is done — the
ticket in `tickets/done/` is the record of what was built.

Status values: ⬜ **Pending** · 🚧 **In Progress** · 🚫 **Blocked**

Every task belongs to an epic, and every epic delivers one feature in `features/`. They share one
code: it prefixes every ticket ID under the epic, and the numbering restarts at 001 in each epic.
Tickets sit in `tickets/todo/`, `tickets/in-progress/`, or `tickets/done/`. Find one by name.

---

## AREA — <epic name>

**Feature**: `features/<feature>/<feature>.feature.md`

<One sentence: what this epic delivers.>

| ID | Task | Status | Depends on | Ticket |
| --- | --- | --- | --- | --- |
| AREA-001 | <task title> | ⬜ **Pending** | — | `AREA-001-<slug>.md` |
```

One `##` section per epic, holding the feature it delivers, that epic's sentence, and its own
table — and nothing else.
The row is the whole task here; what the task delivers and what it has to satisfy live in its
ticket. A new epic appends a section, so two branches that plan separate features touch
separate parts of the file. A `Depends on` cell lists outstanding blockers only, so `—` means
the task is ready to start, and a cell may name a task in another epic because every ID is
unique across the project. The **`ticket-board`** skill holds the rest of the rules, including what
to delete when a task is done.

In a vault, `**Last updated**` becomes the `updated` property under a `type: roadmap`
frontmatter block, and the ticket citation becomes a wikilink — `[[AREA-001-<slug>]]`. The
`**Feature**` line becomes a wikilink too — `[[<feature>.feature]]`.

**`<docs root>/tickets/TEMPLATE.md`**

Copy the `ticket-board` skill's ticket template verbatim from
`skills/ticket-board/assets/ticket-template.md` in the plugin directory
(`${CLAUDE_PLUGIN_ROOT}/skills/ticket-board/assets/ticket-template.md`). If that file is
unreadable, write the template from the skill's documented ticket shape instead.

In a vault, convert the template's leading `**Field**: value` lines into frontmatter properties
once, here, so every ticket copied from it starts in the right shape.

The template stays at the top of `tickets/`, outside the three status folders. It is a
template, not a ticket, so it never moves.

## 5. Report and hand off

Everything the user reads here follows the **`clean-writing`** skill (namespaced
`sdlc:clean-writing`) — load it before you report.

Say **where the docs root is** and, when you wrote one, that `.sdlc.json` now points at it.
Report the tree you created, marking each file `created` or `kept`, and each moved file with
its old and new path. When you ran the PRD split, report it as its own block: the notes written
per type, the PRD sections rewritten, and anything you left inline because it was prose. When you
ran the feature migration, report it as its own block: the features
opened with their codes and statuses, the design docs moved into each one, the docs kept in
`designs/`, and any feature whose status the work root contradicted.

**Then report the registry**: one line per repository — the code, the path, and the `what` line —
and say that `sdlc.json` is machine-local and gitignored. Name any repository you could not reach,
and say that running setup again from inside it registers it.

**Then say how to start a run from the vault**, which is the shape this registry buys:

```shell
cd <docs root>
claude --add-dir <work root> [--add-dir <work root> …]
```

One `--add-dir` per repository in the registry. Inside a session that is already open, `/add-dir
<work root>` does the same thing. Without it the session can read the board but cannot write code.
A repo-rooted run needs none of this, and keeps working exactly as before.

Then offer the next step, in this order:

1. `/prd <product>` — fill the PRD first. It writes the goals, the non-goals, the personas, the
   problems, and the metrics as notes under `product/`, and the PRD's own prose around them. It
   also chooses the product's terms and writes each one's entry in `glossary.md`, so every later
   document takes its vocabulary from there.
2. `/feature <name>` — open a feature for each thing a customer can do. The feature holds its
   design docs and the code that numbers its tickets, so it comes before both.
3. `/design <target>` — specify how each system, flow, or surface works once the PRD names
   it. Each run writes or updates one design doc, in its feature's folder or in `designs/`.
4. `/plan <request>` — turn a request into roadmap tasks and tickets. The roadmap stub holds a
   placeholder row, not a task.
5. `/orchestrate` — start building once the roadmap has a task.

Do not run these yourself. Name them and stop.
