---
description: Create the .clean-architecture/ folder that holds the PRD, the design doc, the roadmap, and the tickets.
argument-hint: [product name]
---

# Scaffold

Create the **`.clean-architecture/`** folder in the project root. It is the single home for
every document this plugin reads and writes.

Product name (if provided): $ARGUMENTS

```
.clean-architecture/
  prd.md              product requirements — what the product does and why
  overview.design.md  design doc — how the solution works, end to end. One file per
                      subject, named <subject>.design.md; this is the entry point
  roadmap.md          the ordered task list /orchestrate picks from
  tickets/
    TEMPLATE.md       copy this per task, named <ID>-<slug>.md
    todo/             a ticket waits here until an orchestrator starts it
    in-progress/      the ticket being built — in progress, blocked, or in review
    done/             a completed ticket
```

A ticket moves between the three folders as its status changes. The `ai-planning-workflow`
skill holds the mapping and the move rules.

## Rules

- **Never overwrite.** Create a file only when it does not exist. Report each existing file
  as kept, and leave its contents alone.
- **One design stub, at most.** Write `overview.design.md` only when the project has no design
  doc at all — no `*.design.md` file, and no single `design.md` in the folder or at the root.
  Report the one it already has as kept.
- **Write stubs, not content.** Each stub carries only the headings and the placeholder
  lines below. Do not invent product requirements, surfaces, or tasks — the person fills
  them in, or `/prd` and `/design` do.
- **Substitute the product name** wherever the stubs show `<product>`, when `$ARGUMENTS`
  gave one. Otherwise leave `TBD`.
- **Create the folder at the project root** — the directory holding `.git`, `package.json`,
  `AGENTS.md`, or `CLAUDE.md`. Not the current working directory when that sits deeper.
- **Create all three status folders**, even though they start empty. Write a `.gitkeep` file
  into each one, because git does not track an empty directory.

## 1. Check what is already there

Look for documents this plugin would otherwise create twice:

- `.clean-architecture/` itself — if it exists, you are filling gaps, not scaffolding.
- Root-level `prd.md`, `PRD.md`, `design.md`, `DESIGN.md`, `roadmap.md`, `ROADMAP.md`.
- A root-level `tickets/` directory.
- A design doc under either name: `*.design.md` files, or a single `design.md`.

If any of these exist outside `.clean-architecture/`, **ask before touching them**: offer to
move each into the folder with `git mv` (preserving history), or to leave it where it is.
Moving a file is the user's call — never move one without an explicit yes. A file left in
place still works: every agent falls back to the project root when the folder has no such
document.

A **single `design.md`** needs the same explicit yes. Design docs are one file per subject,
named `<subject>.design.md`, so a lone `design.md` is the older shape. Offer to `git mv` it to
`.clean-architecture/overview.design.md` and say the rename is only a rename — no content
moves, and splitting it by subject is a later job for `/design`. When the user says no, leave
it: every agent reads a single `design.md` as a fallback. Skip the offer when the project
already has `*.design.md` files.

A **flat tickets folder** needs the same explicit yes. That is a `tickets/` directory holding
ticket files directly, with no `todo/`, `in-progress/`, or `done/` inside it. Offer to create
the three folders and to `git mv` each ticket into the one its status field names, and report
the count per folder afterwards. When the user says no, leave every file where it is: a flat
folder still works, because every agent reads the status field inside the ticket.

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

**`.clean-architecture/overview.design.md`** — the entry-point design doc. Every later
subject gets its own `<subject>.design.md` beside it, written by `/design`.

```markdown
# <product> — design

**Status**: Living document
**Last updated**: <today, YYYY-MM-DD>
**Related**: `prd.md` (product requirements)

<What this doc covers and what it does not. The PRD says what the product does; this doc
says how the solution works, and points at each `<subject>.design.md` for the detail.>

---

## 1. Foundations

<Cross-cutting design intent applying to every part: the principles the design holds to, the
constraints it works within, and the qualities every part shares. Qualitative only.>

---

## 2. <First part, flow, or surface>

<One or two sentences naming it and its role in the solution.>

### 2.1 Structure

<An ASCII diagram of the parts and what connects them, with a one-line caption.>

### 2.2 Behavior

<One unit of work followed from where it enters to where it leaves.>

### 2.3 States

| State | What happens |
| --- | --- |
| Normal | <the expected outcome> |
| Empty | <no work to do, or nothing to show> |
| Not authorized | <what the caller gets> |
| Failure | <invalid input, or an unavailable dependency> |

### 2.4 Variation and limits

<How the behavior changes by role, configuration, volume, or screen width, and the limits
it holds within.>

---

## N. Other parts (planned)

- <Part not yet specified. A part large enough to stand alone becomes its own
  `<subject>.design.md`.>
```

**`.clean-architecture/roadmap.md`**

```markdown
# <product> — roadmap

**Last updated**: <today, YYYY-MM-DD>

Status values: ⬜ **Pending** · 🚧 **In Progress** · ✅ **Completed** · 🚫 **Blocked**

Tickets sit in `tickets/todo/`, `tickets/in-progress/`, or `tickets/done/`. Find one by name.

| ID | Task | Status | Depends on |
| --- | --- | --- | --- |
| SW-001 | <task title> | ⬜ **Pending** | — |

---

## SW-001 — <task title>

<What the task delivers, in 2-3 sentences.>

**Acceptance criteria**

- [ ] <An observable outcome someone can check.>

**Ticket**: `SW-001-<slug>.md`
```

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
   it. Each run writes or updates one `<subject>.design.md`.
3. `/plan <request>` — turn a request into roadmap tasks and tickets. The roadmap stub holds a
   placeholder row, not a task.
4. `/orchestrate .clean-architecture/roadmap.md` — start building once the roadmap has a task.

Do not run these yourself. Name them and stop.
