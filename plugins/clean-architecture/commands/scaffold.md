---
description: Create the .clean-architecture/ folder that holds the PRD, the design docs, the roadmap, and the tickets.
argument-hint: [product name]
---

# Scaffold

Create the **`.clean-architecture/`** folder in the project root. It is the single home for
every document this plugin reads and writes.

Product name (if provided): $ARGUMENTS

```
.clean-architecture/
  prd.md                product requirements — what the product does and why
  roadmap.md            the ordered task list /orchestrate picks from, grouped by epic
  designs/
    overview.design.md  design docs — how the solution works, end to end. One file per
                        subject, named <subject>.design.md; overview is the entry point
  tickets/
    TEMPLATE.md         copy this per task, named <EPIC>-<NNN>-<slug>.md
    todo/               a ticket waits here until an orchestrator starts it
    in-progress/        the ticket being built — in progress, blocked, or in review
    done/               a completed ticket
```

Each kind of document has its own folder once there can be more than one of it. A design doc
covers one subject and stays in `designs/` for the life of the project. A ticket moves between
the three status folders as its status changes — the `ai-planning-workflow` skill holds the
mapping and the move rules.

## Rules

- **Never overwrite.** Create a file only when it does not exist. Report each existing file
  as kept, and leave its contents alone.
- **One design stub, at most.** Write `designs/overview.design.md` only when the project has no
  design doc at all — no `*.design.md` file in `designs/`, in `.clean-architecture/` itself, or
  at the root, and no single `design.md` in any of those places. Report the one it already has
  as kept.
- **Write stubs, not content.** Each stub carries only the headings and the placeholder
  lines below. Do not invent product requirements, surfaces, or tasks — the person fills
  them in, or `/prd` and `/design` do.
- **Substitute the product name** wherever the stubs show `<product>`, when `$ARGUMENTS`
  gave one. Otherwise leave `TBD`.
- **Create the folder at the project root** — the directory holding `.git`, `package.json`,
  `AGENTS.md`, or `CLAUDE.md`. Not the current working directory when that sits deeper.
- **Create `designs/` and all three ticket status folders**, even though they start empty.
  Write a `.gitkeep` file into every one that ends up with no file in it, because git does not
  track an empty directory.

## 1. Check what is already there

Look for documents this plugin would otherwise create twice:

- `.clean-architecture/` itself — if it exists, you are filling gaps, not scaffolding.
- Root-level `prd.md`, `PRD.md`, `design.md`, `DESIGN.md`, `roadmap.md`, `ROADMAP.md`.
- A root-level `tickets/` directory.
- A design doc in any shape: `*.design.md` files in `.clean-architecture/designs/`, in
  `.clean-architecture/` itself, or at the root; or a single `design.md` in any of those.

If any of these exist outside `.clean-architecture/`, **ask before touching them**: offer to
move each into the folder with `git mv` (preserving history), or to leave it where it is.
Moving a file is the user's call — never move one without an explicit yes. A file left in
place still works: every agent falls back to the project root when the folder has no such
document.

**Design docs outside `designs/`** need the same explicit yes. Design docs live in
`.clean-architecture/designs/`, one file per subject, named `<subject>.design.md`, so anything
else is an older shape:

- `*.design.md` files in `.clean-architecture/` itself or at the root → offer to `git mv` each
  one into `.clean-architecture/designs/` under the same name, and report the count moved.
- A single `design.md`, in the folder or at the root → offer to `git mv` it to
  `.clean-architecture/designs/overview.design.md`. Say the rename is only a rename: no
  content moves, and splitting it by subject is a later job for `/design`.

When the user says no, leave every file where it is: every agent reads the older shapes as a
fallback. Skip the offer when `.clean-architecture/designs/` already holds the docs.

A **flat tickets folder** needs the same explicit yes. That is a `tickets/` directory holding
ticket files directly, with no `todo/`, `in-progress/`, or `done/` inside it. Offer to create
the three folders and to `git mv` each ticket into the one its status field names, and report
the count per folder afterwards. When the user says no, leave every file where it is: a flat
folder still works, because every agent reads the status field inside the ticket.

**Ticket IDs with no epic** need the same explicit yes. Every ticket ID starts with the code of
the epic that holds it, and the numbering restarts at 001 in each epic — the
`ai-planning-workflow` skill holds the rule, and the roadmap holds the list of epics. A project
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
   line inside each file, and add the `**Epic**` field under it.
3. **Rewrite every reference.** Group the roadmap rows into one `##` section per epic, and
   rename each ID in the tables, in the detail headings, in the `Depends on` cells, and in the
   `**Ticket**` file names. Then search the whole project for each old ID and fix what that
   finds — a ticket's `Related` links, a design doc, a note. Report the count renamed and the
   files touched.

When the user says no, leave every ID alone, and say that new tickets keep continuing the
project's own scheme. Never rename part of the set: a half-migrated project cites two schemes
and matches neither. Skip the offer when the roadmap already has epic sections.

## 2. Write the stubs

**`.clean-architecture/prd.md`**

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

**`.clean-architecture/designs/overview.design.md`** — the entry-point design doc. Every
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

Keep only the sections that have something specific to say — an empty heading is deleted,
never filled — and leave out any part that is not designed yet.

**`.clean-architecture/roadmap.md`**

```markdown
# <product> — roadmap

**Last updated**: <today, YYYY-MM-DD>

Status values: ⬜ **Pending** · 🚧 **In Progress** · ✅ **Completed** · 🚫 **Blocked**

Every task belongs to an epic. The epic's code prefixes every ticket ID under it, and the
numbering restarts at 001 in each epic. Tickets sit in `tickets/todo/`, `tickets/in-progress/`,
or `tickets/done/`. Find one by name.

---

## AREA — <epic name>

<One sentence: what this epic delivers.>

| ID | Task | Status | Depends on |
| --- | --- | --- | --- |
| AREA-001 | <task title> | ⬜ **Pending** | — |

### AREA-001 — <task title>

<What the task delivers, in 2-3 sentences.>

**Acceptance criteria**

- [ ] <An observable outcome someone can check.>

**Ticket**: `AREA-001-<slug>.md`
```

One `##` section per epic, holding that epic's own table and one `###` detail section per task.
A new epic appends a section, so two branches that plan separate features touch separate parts
of the file. A dependency may name a task in another epic: every ID is unique across the
project, because every epic code is.

**`.clean-architecture/tickets/TEMPLATE.md`**

Copy the `ai-planning-workflow` skill's ticket template verbatim from
`skills/ai-planning-workflow/assets/ticket-template.md` in the plugin directory
(`${CLAUDE_PLUGIN_ROOT}/skills/ai-planning-workflow/assets/ticket-template.md`). If that
file is unreadable, write the template from the skill's documented ticket shape instead.

The template stays at the top of `tickets/`, outside the three status folders. It is a
template, not a ticket, so it never moves.

## 3. Report and hand off

Everything the user reads here follows the **`clean-writing`** skill (namespaced
`clean-architecture:clean-writing`) — load it before you report.

Report the tree you created, marking each file `created` or `kept`, and each moved file with
its old and new path. Then offer the next step, in this order:

1. `/prd <product>` — fill the PRD first. Every later document takes its vocabulary from it.
2. `/design <target>` — specify how each system, flow, or surface works once the PRD names
   it. Each run writes or updates one `designs/<subject>.design.md`.
3. `/plan <request>` — turn a request into roadmap tasks and tickets. The roadmap stub holds a
   placeholder row, not a task.
4. `/orchestrate .clean-architecture/roadmap.md` — start building once the roadmap has a task.

Do not run these yourself. Name them and stop.
