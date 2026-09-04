---
description: Turn a request into updated product documents, roadmap tasks, and tickets for /orchestrate to build.
argument-hint: [feature or change to plan]
---

# Plan

Turn the request below into **product documents and work items**: an interview that settles the open decisions, an updated PRD and design doc, new roadmap tasks, and one ticket per task. You write documents here. You do not write code.

Request: $ARGUMENTS

This is the intake path. `/prd` writes the PRD, `/design` writes the design doc, and `/orchestrate` builds a task that is already on the roadmap — but nothing turned a request into those tasks, so the roadmap had to be filled by hand before any pipeline had something to pick. `/plan` is that missing step, and it stops exactly where `/orchestrate` starts.

**Where the documents live.** This plugin keeps them in `.sdlc/`: `prd.md`, `designs/<subject>.design.md` — one file per design subject, `roadmap.md`, and `tickets/<status>/<ID>-<slug>.md`, where `<status>` is `todo`, `in-progress`, or `done`, and `<ID>` is `<EPIC>-<NNN>`. Every ticket this command writes starts in `todo/`, because no work has started on it. When a project has no such folder, fall back to whatever it already uses at the root. When its design docs sit directly in `.sdlc/`, or its tickets folder is flat, write into the shape the project already has.

## Architecture: you write, one agent researches

Everything here runs **in the main loop, with you**. The documents carry the product's own voice, and only you can ask the user a question. One agent runs beside you: `sdlc:feature-interviewer`, which reads the product docs, explores the codebase, and researches the topic on the web. Spawn it in the **same tool block** as your own first reads — you need the same documents it does, and its web round-trips then cost no wall-clock.

```
  YOU (main loop)
  ─────────────────────────
  resolve request ─┬─ Agent(feature-interviewer) ──┐  concurrent
                   └─ read prd / design / roadmap ─┤
  AskUserQuestion (settle decisions) ◄─────────────┘
  change proposal ─► approval ─► PRD ─► design ─► roadmap ─► tickets ─► report
```

## Everything here is read by a person

Load the **`clean-writing`** skill once, before Stage 1 (namespaced here as `sdlc:clean-writing`), and follow it for every word the user sees and every line you write into a document: each question, the change proposal, the PRD and design edits, each ticket, and the report. The `prd`, `design-doc`, and `ai-planning-workflow` skills say *what belongs in* each document; `clean-writing` says *how each sentence reads*. It governs prose only — IDs, file paths, status values, and anchor codes stay exact.

## Workflow

### 1. Resolve the request

- **Nothing given** → ask what to plan. Do not guess.
- **A description** → use it as-is.
- **A file path** (a note, an issue export, a meeting transcript) → read it and use it as the request.

**Hand off when the request does not need documents.** A fix, a rename, or a change that leaves what the product does unchanged needs no PRD edit and no ticket — name `/code` and stop. A single well-understood task already on the roadmap belongs to `/orchestrate`. Name the command and the reason in one line, then stop.

Plan **one request per run.** When the request is really several unrelated features, say so, plan the one the user names, and stop.

### 2. Check the documents exist

- **No `.sdlc/` folder and no product docs at the root** → name `/scaffold` and stop. Planning into a project with no PRD invents the product instead of extending it.
- **The folder exists but one document is missing** → create that one file with the stub headings `/scaffold` writes, then continue.
- **The PRD is still a stub**, with the placeholder lines unfilled → fill only the sections this request touches, and name `/prd` in your report as the way to write the rest. Do not invent a whole product around one request.

### 3. Interview, and read the documents while it runs

Issue **both calls in one tool block**:

```
Agent(subagent_type: "sdlc:feature-interviewer",
      prompt: the request + any acceptance criteria it already carries
              + "No ticket exists yet — this is the planning pass that writes one.
                 Say where the request extends or contradicts the PRD and the design doc,
                 because the document update follows your brief.")
```

...and read `prd.md`, the `designs/*.design.md` docs this request touches, and `roadmap.md` yourself. You need four things the interviewer will not hand you: the product's vocabulary, the parts and surfaces this request touches, the roadmap's epics and the numbering inside each of them, and the existing tasks the request duplicates or depends on.

The brief comes back as *Understanding*, *What already exists*, *Research findings*, *Open decisions*, *Assumptions*, and *Out of scope*. Nothing returned, or no brief after one retry → report that and stop before writing any file.

**Put the decisions to the user yourself** with `AskUserQuestion` — a subagent cannot ask. Batch them (up to 4 per call), lead each with the interviewer's recommended option labelled "(Recommended)", and surface the brief's assumptions for confirmation. One call, not one per decision. Zero open decisions is a good brief, not a broken one: confirm the assumptions and move on.

Resume the interviewer with `SendMessage` **at most once**, and only when an answer changes the feature enough that its research no longer covers it. Never re-spawn it.

### 4. Propose the change, and wait for a yes

One gate, before you write any file:

```markdown
## Plan: [feature]

**PRD** — [section] — [what changes]  (or: no change)
**Design docs** — [`designs/<subject>.design.md`] — [what changes]  (or: no change)

**Epic** — [CODE] — [epic name] — [existing, or new]

**Roadmap**

| ID | Task | Depends on | Delivers |
| --- | --- | --- | --- |
| [CODE-NNN] | [title] | [IDs or —] | [one line] |

Tickets: one per row, in `.sdlc/tickets/todo/`.

Proceed? (yes / adjust / cancel)
```

How to break the work down:

- **One task per shippable outcome** — something a person can check when it lands. Not a layer, not a file, not "the backend part".
- **Size each task for a single `/orchestrate` run.** A task you cannot state in a few lines is two tasks.
- **Order by dependency.** A task's dependencies sit above it, and name only other roadmap tasks.
- **Put every task in one epic**, and name the epic before you number anything. An epic is a named group of tasks that deliver one feature. Use the epic the request already belongs to when the roadmap has one; declare a new epic when it does not, with a code of two to eight uppercase letters taken from the product's vocabulary. A code may repeat a PRD area anchor code when the epic covers that area, and it is unique against every other code in the roadmap.
- **Number inside the epic, from 001.** Glob every ticket status folder for `<CODE>-*.md`, including `done/`, take the highest number, and continue from it. The restart per epic is what keeps two branches apart: each plans into its own epic, so both write a first ticket and neither overwrites the other on merge.
- **Never renumber, reuse, or reorder an existing ID**, and never rewrite an ID a project already uses. A project still on a project-wide scheme (`SW-001`, `SW-002`, …) keeps it — continue that scheme and name `/scaffold` in your report as the way to migrate.
- **A pending task the request changes is updated in place**, not duplicated. When the task it changes is already completed, add a new one.

Wait for approval. Adjust and re-present as many times as the user asks.

### 5. Write the documents

In this order, so each document takes its vocabulary from the one before it. Each skill named
below is namespaced here (`sdlc:prd`, `sdlc:design-doc`,
`sdlc:ai-planning-workflow`) — load it before you write the document it governs,
and follow it. Do not restate its rules from memory.

**PRD** — load the **`prd`** skill and follow it. Fold the request into the existing sections in place, as the current truth, and keep the document whole. It stays product-only: no ticket ID, no roadmap reference, no library name, no file path. The decisions from the interview live in the tickets, not here. Bump `Last updated`.

**Design docs** — only when the request changes how a part, a flow, or a surface works. Load the **`design-doc`** skill and follow it: one file per subject at `.sdlc/designs/<subject>.design.md`, the per-subject pattern (structure → behavior → states → variation and limits), the structural altitude, no tickets and no code references. Update the doc whose subject the request touches, and start a new one only for a subject that has none. Bump `Last updated` on each file you touch.

**Roadmap** — append the approved rows under their epic, with status `⬜ **Pending**`, matching the file's existing style. An existing epic already has its `## <CODE> — <epic name>` section, its table, and its detail sections: add to those. A new epic gets a new section at the end of the file — one sentence on what it delivers, then its own table. Add one detail section per row: what the task delivers in two or three sentences, its acceptance criteria as checkboxes, and its ticket file name. Cite the ticket by name (`AUTH-001-<slug>.md`), never by path — the file moves between the status folders as the work progresses. Touch no other epic's section, so a branch planning a different feature changes different lines of the file. Bump `Last updated`. Never write any status other than pending — in-progress and completed belong to whoever builds the task.

**Tickets** — copy `.sdlc/tickets/TEMPLATE.md` once per row into `.sdlc/tickets/todo/`, named `<ID>-<slug>.md`. When there is no template, use the ticket shape from the **`ai-planning-workflow`** skill. Load that skill's ticket guidelines and follow them, including where a ticket lives and when it moves:

- **What, not how.** No file paths, no component or module names, no library names, no schema detail — those are the planner's job inside `/orchestrate`.
- **The `Decisions` section is the one exception**, and the reason this command runs an interview: record each settled choice as a fixed constraint, one line with its rationale. A library chosen in the interview is named here, and nowhere else.
- **Acceptance criteria are observable outcomes**, and they match the roadmap row.
- **Status is `Not Started`**, so the file goes in `todo/`. `Created` is today. The `Epic` field names the epic exactly as its roadmap section does.
- Under `Related`, cite the PRD's area anchor code (e.g. `CONTENT`) and any sibling ticket. The link runs ticket → PRD, never back.
- **Never overwrite an existing ticket file.** Check every status folder for the ID before you write, because a completed ticket sits in `done/`. A name collision means the number is wrong — take the next free one in that epic.

### 6. Report

```markdown
## Planned: [feature]

[One or two sentences: what the feature is, and what a person can do once it ships.]

### Documents
- Updated: [paths — and the sections that changed]
- Created: [paths]

### Tasks added
Epic: [CODE] — [epic name] ([new], or the section it joined)
- [ID] — [title] (depends on: [IDs or none])

### Decisions recorded
- [decision] → [chosen option]

### Still open (if any)
- [question the user deferred, and what it blocks]

Next: `/orchestrate` picks up [first ID].
```

Do not run `/orchestrate` yourself. Name it and stop.

## Rules

- **Documents only.** No code, and no implementation plan — the planner inside `/orchestrate` decides how the work is done.
- **Interview before you write.** Every request that reaches Stage 3 gets one; a request too small to interview was handed to `/code` in Stage 1.
- **Never write a file before the user approves the breakdown.**
- **Statuses stay at the start** — pending in the roadmap, `Not Started` in the ticket, and the ticket file in `todo/`. This command never marks progress, and never moves a ticket out of `todo/`.
- **The link runs one way.** A ticket may cite a PRD area code; the PRD and the design doc never cite a ticket, an ID, or a roadmap row.
- **Reuse the product's words** from the PRD for every domain term, in every document you touch — a second name for the same thing is how two documents start disagreeing.
- **Never renumber or overwrite** an existing row, ID, or ticket.
- **Hand off when the request needs code rather than documents** — name `/code`, `/orchestrate-quick`, or `/orchestrate`, and why.
