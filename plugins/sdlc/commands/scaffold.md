---
description: Create the folder that holds the PRD, the glossary, the design docs, the roadmap, and the tickets — in the repository, or in an Obsidian vault.
argument-hint: [product name] [destination path]
---

# Scaffold

Create the **docs root** — the single home for every document this plugin reads and writes. It
sits in the repository as `.sdlc/` by default, and it can sit anywhere else the user keeps their
writing, including a folder in an Obsidian vault.

Arguments (if provided): $ARGUMENTS

Load two skills before you create anything, namespaced here as `sdlc:<name>`: **`product-docs`**,
which holds the resolution order, the pointer file, and the vault conventions this command writes,
and **`ticket-board`**, which holds the shape of the tickets and the roadmap it scaffolds and
migrates.

```
<docs root>/
  prd.md                product requirements — what the product does and why
  glossary.md           the product's terms — one ## heading per term, defined once
                        here and linked from every other document
  roadmap.md            the work that is left, in order, grouped by epic
  designs/
    overview.design.md  design docs — how the solution works, end to end. One file per
                        subject, named <subject>.design.md; overview is the entry point
  tickets/
    TEMPLATE.md         copy this per task, named <EPIC>-<NNN>-<slug>.md
    todo/               a ticket waits here until an orchestrator starts it
    in-progress/        the ticket being built — in progress, blocked, or in review,
                        with its worklog beside it
    done/               a completed ticket, and its worklog
```

Each kind of document has its own folder once there can be more than one of it. A design doc
covers one subject and stays in `designs/` for the life of the project. A ticket moves between
the three status folders as its status changes — the `ticket-board` skill holds the mapping and the
move rules. **A worklog appears beside a ticket in the step that starts the work**, holds what each
agent decided while the ticket was built, and moves with the ticket into `done/`. Write none here:
there is no ticket yet to put one beside.

## Rules

- **Never overwrite.** Create a file only when it does not exist. Report each existing file
  as kept, and leave its contents alone.
- **One design stub, at most.** Write `designs/overview.design.md` only when the project has no
  design doc at all — no `*.design.md` file in `designs/`, in the docs root itself, or
  at the project root, and no single `design.md` in any of those places. Report the one it
  already has as kept.
- **Write stubs, not content.** Each stub carries only the headings and the placeholder
  lines below. Do not invent product requirements, surfaces, or tasks — the person fills
  them in, or `/prd` and `/design` do.
- **Substitute the product name** wherever the stubs show `<product>`, when the arguments
  gave one. Otherwise leave `TBD`.
- **Settle the destination before you create anything** — Step 1. The default docs root is
  `.sdlc/` in the project root: the directory holding `.git`, `package.json`, `AGENTS.md`, or
  `CLAUDE.md`. Not the current working directory when that sits deeper.
- **Create `designs/` and all three ticket status folders**, even though they start empty.
  Write a `.gitkeep` file into every one that ends up with no file in it **when the docs root
  sits inside a git working tree**, because git does not track an empty directory. A docs root
  outside git gets no `.gitkeep` — it is clutter in a vault.

## 1. Settle the destination

The docs root goes where the user keeps this kind of writing. Decide where, in this order, and
stop at the first that applies:

- **`.sdlc.json` already exists** at the project root → read it. The destination is settled.
  Report where the documents live and fill the gaps there. Do not ask.
- **`.sdlc/` already exists** → the destination is the repository. You are filling gaps, not
  choosing. Do not ask.
- **The arguments name a path** — an absolute path, a `~`-prefixed path, or anything holding a
  path separator → that is the destination. The rest of the arguments is the product name.
- **Otherwise, ask.** One question, two options:
  - **In the repository (`.sdlc/`)** — recommended. The documents are versioned with the code,
    they travel with a clone, and a review sees a document change beside the change it
    describes.
  - **In a folder outside the repository** — an Obsidian vault, or any shared writing folder.
    The documents are readable and editable without the repository, and several projects can
    live in one place. Ask for the path in the same turn, or take it from the user's "Other"
    answer.

  In Codex, ask the same question in prose: a Codex session has no `AskUserQuestion` tool.

**Then classify the destination.** Walk up from the chosen path looking for a `.obsidian/`
folder — in the path itself, or in any parent directory:

- **Found** → the destination is a **vault**. Name the vault in your report. When the chosen
  path *is* the vault root, create the docs root as a folder inside it, named after the product
  (`<vault>/Acme/`), so `prd.md` does not land among the user's own notes. Never name a folder
  in a vault with a leading dot: Obsidian hides it. If the user asked for `.sdlc` inside a
  vault, say why it would be invisible and offer the product-named folder instead.
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

## 2. Check what is already there

Look for documents this plugin would otherwise create twice:

- The docs root itself — if it exists, you are filling gaps, not scaffolding.
- Root-level `prd.md`, `PRD.md`, `glossary.md`, `GLOSSARY.md`, `design.md`, `DESIGN.md`,
  `roadmap.md`, `ROADMAP.md`.
- A root-level `tickets/` directory.
- A design doc in any shape: `*.design.md` files in `<docs root>/designs/`, in the docs root
  itself, or at the project root; or a single `design.md` in any of those.

If any of these exist outside the docs root, **ask before touching them**: offer to
move each into the folder with `git mv` (preserving history), or to leave it where it is.
Moving a file is the user's call — never move one without an explicit yes. A file left in
place still works: every agent falls back to the project root when the folder has no such
document.

**A move out of the repository loses the file's git history**, because `git mv` cannot cross
into a folder git does not track. Say that plainly whenever the docs root is a vault or an
outside folder, before you offer the move, and use a plain `mv` when the user says yes.

**Design docs outside `designs/`** need the same explicit yes. Design docs live in
`<docs root>/designs/`, one file per subject, named `<subject>.design.md`, so anything
else is an older shape:

- `*.design.md` files in the docs root itself or at the project root → offer to move each
  one into `designs/` under the same name, and report the count moved.
- A single `design.md`, in the docs root or at the project root → offer to move it to
  `designs/overview.design.md`. Say the rename is only a rename: no
  content moves, and splitting it by subject is a later job for `/design`.

When the user says no, leave every file where it is: every agent reads the older shapes as a
fallback. Skip the offer when `<docs root>/designs/` already holds the docs.

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
   links, a design doc, a note. Report the count renamed and the files touched.

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

## 3. Write the stubs

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

<What existing tools fail at, as a numbered list, then one sentence on how this product
solves them.>

## 3. Goals & non-goals

### Goals

- <One concrete, testable statement per goal.>

### Non-goals (current scope)

- <One explicit exclusion per line, each with the reason it is out of scope.>

## 4. Users & personas

| Persona | Need | Primary flow |
| --- | --- | --- |
| <name> | <what they need> | <how they use the product> |

## 5. How the product works

### <Product area> `AREA`

<A few short paragraphs describing how this area works and how it connects to the others.
One stable uppercase anchor code per area, in the heading.>

## 6. Cross-cutting qualities

<The guarantees holding across the whole product — security, privacy, offline, reliability
— grouped by theme, each stated positively.>

## 7. Success metrics

- <Metric name — definition — target.>

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

**`<docs root>/designs/overview.design.md`** — the entry-point design doc. Every
later subject gets its own `<subject>.design.md` beside it, written by `/design`.

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

<An ASCII diagram of the parts and what connects them, with a one-line caption.>

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

Every task belongs to an epic. The epic's code prefixes every ticket ID under it, and the
numbering restarts at 001 in each epic. Tickets sit in `tickets/todo/`, `tickets/in-progress/`,
or `tickets/done/`. Find one by name.

---

## AREA — <epic name>

<One sentence: what this epic delivers.>

| ID | Task | Status | Depends on | Ticket |
| --- | --- | --- | --- | --- |
| AREA-001 | <task title> | ⬜ **Pending** | — | `AREA-001-<slug>.md` |
```

One `##` section per epic, holding that epic's sentence and its own table — and nothing else.
The row is the whole task here; what the task delivers and what it has to satisfy live in its
ticket. A new epic appends a section, so two branches that plan separate features touch
separate parts of the file. A `Depends on` cell lists outstanding blockers only, so `—` means
the task is ready to start, and a cell may name a task in another epic because every ID is
unique across the project. The **`ticket-board`** skill holds the rest of the rules, including what
to delete when a task is done.

In a vault, `**Last updated**` becomes the `updated` property under a `type: roadmap`
frontmatter block, and the ticket citation becomes a wikilink — `[[AREA-001-<slug>]]`.

**`<docs root>/tickets/TEMPLATE.md`**

Copy the `ticket-board` skill's ticket template verbatim from
`skills/ticket-board/assets/ticket-template.md` in the plugin directory
(`${CLAUDE_PLUGIN_ROOT}/skills/ticket-board/assets/ticket-template.md`). If that file is
unreadable, write the template from the skill's documented ticket shape instead.

In a vault, convert the template's leading `**Field**: value` lines into frontmatter properties
once, here, so every ticket copied from it starts in the right shape.

The template stays at the top of `tickets/`, outside the three status folders. It is a
template, not a ticket, so it never moves.

## 4. Report and hand off

Everything the user reads here follows the **`clean-writing`** skill (namespaced
`sdlc:clean-writing`) — load it before you report.

Say **where the docs root is** and, when you wrote one, that `.sdlc.json` now points at it.
Report the tree you created, marking each file `created` or `kept`, and each moved file with
its old and new path. Then offer the next step, in this order:

1. `/prd <product>` — fill the PRD first. It chooses the product's terms and writes each one's
   entry in `glossary.md`. Every later document takes its vocabulary from there.
2. `/design <target>` — specify how each system, flow, or surface works once the PRD names
   it. Each run writes or updates one `designs/<subject>.design.md`.
3. `/plan <request>` — turn a request into roadmap tasks and tickets. The roadmap stub holds a
   placeholder row, not a task.
4. `/orchestrate` — start building once the roadmap has a task.

Do not run these yourself. Name them and stop.
