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
  design.md           design doc — how each surface looks and behaves
  roadmap.md          the ordered task list /orchestrate picks from
  tickets/
    TEMPLATE.md       copy this per task, named <ID>-<slug>.md
```

## Rules

- **Never overwrite.** Create a file only when it does not exist. Report each existing file
  as kept, and leave its contents alone.
- **Write stubs, not content.** Each stub carries only the headings and the placeholder
  lines below. Do not invent product requirements, surfaces, or tasks — the person fills
  them in, or `/prd` and `/design` do.
- **Substitute the product name** wherever the stubs show `<product>`, when `$ARGUMENTS`
  gave one. Otherwise leave `TBD`.
- **Create the folder at the project root** — the directory holding `.git`, `package.json`,
  `AGENTS.md`, or `CLAUDE.md`. Not the current working directory when that sits deeper.

## 1. Check what is already there

Look for documents this plugin would otherwise create twice:

- `.clean-architecture/` itself — if it exists, you are filling gaps, not scaffolding.
- Root-level `prd.md`, `PRD.md`, `design.md`, `DESIGN.md`, `roadmap.md`, `ROADMAP.md`.
- A root-level `tickets/` directory.

If any of these exist outside `.clean-architecture/`, **ask before touching them**: offer to
move each into the folder with `git mv` (preserving history), or to leave it where it is.
Moving a file is the user's call — never move one without an explicit yes. A file left in
place still works: every agent falls back to the project root when the folder has no such
document.

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

**`.clean-architecture/design.md`**

```markdown
# <product> — design

**Status**: Living document
**Last updated**: <today, YYYY-MM-DD>
**Related**: `prd.md` (product requirements)

<What this doc covers and what it does not. The PRD says what the product does; this doc
says how it presents and behaves.>

---

## 1. Foundations

<Cross-cutting design intent applying to every surface: the character of the palette, the
type hierarchy, spacing, motion, responsiveness, and the shared shell. Qualitative only.>

---

## 2. <First surface>

<One or two sentences naming the surface and its role.>

### 2.1 Layout

<An ASCII diagram of the regions, with a one-line caption.>

### 2.2 Content

<What each region holds, top to bottom.>

### 2.3 States

| State | Appearance |
| --- | --- |
| Loading | <what the user sees> |
| Empty | <what the user sees> |
| Populated | <what the user sees> |
| Error | <what the user sees> |

### 2.4 Responsive

<What reflows, stacks, collapses, or hides across wide, medium, and small widths.>

---

## N. Other screens (planned)

- <Surface not yet specified.>
```

**`.clean-architecture/roadmap.md`**

```markdown
# <product> — roadmap

**Last updated**: <today, YYYY-MM-DD>

Status values: ⬜ **Pending** · 🚧 **In Progress** · ✅ **Completed** · 🚫 **Blocked**

| ID | Task | Status | Depends on |
| --- | --- | --- | --- |
| SW-001 | <task title> | ⬜ **Pending** | — |

---

## SW-001 — <task title>

<What the task delivers, in 2-3 sentences.>

**Acceptance criteria**

- [ ] <An observable outcome someone can check.>

**Ticket**: `tickets/SW-001-<slug>.md`
```

**`.clean-architecture/tickets/TEMPLATE.md`**

Copy the `ai-planning-workflow` skill's ticket template verbatim from
`skills/ai-planning-workflow/assets/ticket-template.md` in the plugin directory
(`${CLAUDE_PLUGIN_ROOT}/skills/ai-planning-workflow/assets/ticket-template.md`). If that
file is unreadable, write the template from the skill's documented ticket shape instead.

## 3. Report and hand off

Everything the user reads here follows the **`clean-writing`** skill (namespaced
`clean-architecture:clean-writing`) — load it before you report.

Report the tree you created, marking each file `created` or `kept`, and each moved file with
its old and new path. Then offer the next step, in this order:

1. `/prd <product>` — fill the PRD first. Every later document takes its vocabulary from it.
2. `/design <surface>` — specify the surfaces once the PRD names them.
3. `/plan <request>` — turn a request into roadmap tasks and tickets. The roadmap stub holds a
   placeholder row, not a task.
4. `/orchestrate .clean-architecture/roadmap.md` — start building once the roadmap has a task.

Do not run these yourself. Name them and stop.
