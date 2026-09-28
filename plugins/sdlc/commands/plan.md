---
description: Turn a request into updated product documents, roadmap tasks, and tickets for /orchestrate to build.
argument-hint: [feature or change to plan]
---

# Plan

Turn the request below into **product documents and work items**: an interview that settles the open decisions, an updated PRD and design doc, new roadmap tasks, and one ticket per task. You write documents here. You do not write code.

Request: $ARGUMENTS

This is the intake path. `/prd` writes the PRD, `/design` writes the design doc, and `/orchestrate` builds a task that is already on the roadmap — but nothing turned a request into those tasks, so the roadmap had to be filled by hand before any pipeline had something to pick. `/plan` is that missing step, and it stops exactly where `/orchestrate` starts.

**Load these skills before you write anything**, each once, and follow it — namespaced here as `sdlc:<name>`:

| Skill | What it holds |
| --- | --- |
| **`product-docs`** | Where the docs root and the work root are, and how each destination writes a document |
| **`ticket-board`** | The epic that numbers a ticket, the roadmap's shape, and the ticket's own shape |
| **`glossary`** | The product's terms — where each one is defined, and how a document links it |
| **`diagrams`** | A diagram of a shape — how one is drawn, and how a document references it |
| **`clean-writing`** | Every sentence you write, in a document or to the user |

The documents sit in the **docs root**: `prd.md`, `glossary.md`, `features/<feature>/<feature>.feature.md`, `features/<feature>/<subject>.design.md`, `designs/<subject>.design.md`, `diagrams/<name>.excalidraw.md`, `roadmap.md`, and `tickets/<status>/<ID>-<slug>.md`. `product-docs` resolves the root; every `.sdlc/…` path below means `<docs root>/…`.

**A ticket never names the repository it is built in** — the run that builds it works that out, from the feature, the design doc, the ticket, and the docs root's registry. So write the ticket about the product, and never about a repository path. What you *can* do is make that resolution easy: name the surface the work lands on in the ticket's description, in the words the design doc uses. When this session is vault-rooted and the code matters to the research, pass the candidate repositories to the interviewer as absolute paths, and check the session can read them. **Every ticket this command writes starts in `todo/`**, because no work has started on it. When the project keeps its design docs directly in the docs root or all in `designs/`, or its tickets folder is flat, write into the shape it already has.

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

`clean-writing` governs every word the user sees and every line you write into a document: each question, the change proposal, the PRD and design edits, each ticket, and the report. The `prd`, `design-doc`, and `ticket-board` skills say *what belongs in* each document; `clean-writing` says *how each sentence reads*. It governs prose only — IDs, file paths, status values, and anchor codes stay exact.

## Workflow

### 1. Resolve the request

- **Nothing given** → ask what to plan. Do not guess.
- **A description** → use it as-is.
- **A file path** (a note, an issue export, a meeting transcript) → read it and use it as the request.

**Hand off when the request does not need documents.** A fix, a rename, or a change that leaves what the product does unchanged needs no PRD edit and no ticket — name `/code` and stop. A single well-understood task already on the roadmap belongs to `/orchestrate`. Name the command and the reason in one line, then stop.

Plan **one request per run.** When the request is really several unrelated features, say so, plan the one the user names, and stop.

### 2. Check the documents exist

- **No docs root and no product docs at the root** → name `/setup` and stop. Planning into a project with no PRD invents the product instead of extending it.
- **The docs root exists but one document is missing** → create that one file with the stub headings `/setup` writes, then continue.
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

...and read `glossary.md`, `prd.md`, the feature notes in `features/` this request touches, the design docs in those feature folders and in `designs/`, and `roadmap.md` yourself. You need five things the interviewer will not hand you: the product's vocabulary, the features this request touches and the codes they already own, the parts and surfaces it changes, the roadmap's epics and the numbering inside each of them, and the existing tasks the request duplicates or depends on.

The brief comes back as *Understanding*, *What already exists*, *Research findings*, *Open decisions*, *Assumptions*, and *Out of scope*. Nothing returned, or no brief after one retry → report that and stop before writing any file.

**Put the decisions to the user yourself** with `AskUserQuestion` — a subagent cannot ask. Batch them (up to 4 per call), lead each with the interviewer's recommended option labelled "(Recommended)", and surface the brief's assumptions for confirmation. One call, not one per decision. Zero open decisions is a good brief, not a broken one: confirm the assumptions and move on.

Resume the interviewer with `SendMessage` **at most once**, and only when an answer changes the feature enough that its research no longer covers it. Never re-spawn it.

### 4. Propose the change, and wait for a yes

One gate, before you write any file:

```markdown
## Plan: [feature]

**PRD** — [section] — [what changes]  (or: no change)
**Features** — [`features/<feature>/<feature>.feature.md`] — [opened, or what changed]  (or: no change)
**Design docs** — [the doc's path] — [what changes]  (or: no change)

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
- **Order by dependency.** A task's dependencies sit above it, and name only other tasks that are still on the roadmap. Work that is already done is not a dependency — the roadmap holds no finished task to point at.
- **Put every task in one epic**, and name the epic before you number anything. Use the epic the request already belongs to when the roadmap has one; declare a new epic when it does not. `ticket-board` holds what an epic code looks like, how the numbering restarts inside it, where the next free number comes from, and why an existing ID is never renumbered or reused.
- **A pending task the request changes is updated in place**, not duplicated. When the request changes work that is already finished, add a new task: the roadmap no longer holds the finished one, and its ticket in `tickets/done/` stays as it was written.

Wait for approval. Adjust and re-present as many times as the user asks.

### 5. Write the documents

In this order, so each document takes its vocabulary from the one before it. Each skill named
below is namespaced here (`sdlc:prd`, `sdlc:design-doc`, `sdlc:ticket-board`) — load it before you
write the document it governs, and follow it. Do not restate its rules from memory.

**PRD** — load the **`prd`** skill and follow it. Fold the request into the existing sections in place, as the current truth, and keep the document whole. It stays product-only: no ticket ID, no roadmap reference, no library name, no file path. The decisions from the interview live in the tickets, not here. Bump `Last updated`.

**Features** — whenever the request adds something a customer can name, or changes the state of something they already can. Load the **`feature`** skill and follow it: one folder per feature, one `<feature>.feature.md` index, and the code that feature's epic and tickets take. Open the feature **before** you write its design doc or its first ticket, so both have an owner. A request that only changes how an existing feature works updates that feature's index and opens nothing.

**Design docs** — only when the request changes how a part, a flow, or a surface works. Load the **`design-doc`** skill and follow it: one file per subject, in the feature's folder when it belongs to one feature and in `.sdlc/designs/` when it underpins every feature, the per-subject pattern (structure → behavior → states → variation and limits), the structural altitude, no tickets and no code references. Update the doc whose subject the request touches, and start a new one only for a subject that has none. Bump `Last updated` on each file you touch.

**Roadmap** — follow the **`ticket-board`** skill's roadmap rules: one row per task and nothing else, the row cited by ticket file name, and a `Depends on` cell that names outstanding blockers only. Append the approved rows under their epic with status `⬜ **Pending**`, matching the file's existing style — an existing epic gets rows in its table, a new epic gets a new section at the end of the file with one sentence on what it delivers. **Touch no other epic's section**, so a branch planning a different feature changes different lines. Bump `Last updated`. **Never write any status other than pending**: in-progress belongs to whoever builds the task, and a completed task is deleted from the file rather than marked.

**Tickets** — copy `.sdlc/tickets/TEMPLATE.md` once per row into `.sdlc/tickets/todo/`, named `<ID>-<slug>.md`. When there is no template, use the ticket shape and the ticket guidelines from the **`ticket-board`** skill:

- **What, not how.** No file paths, no component or module names, no library names, no schema detail — those are the planner's job inside `/orchestrate`.
- **The `Decisions` section is the one exception**, and the reason this command runs an interview: record each settled choice as a fixed constraint, one line with its rationale. A library chosen in the interview is named here, and nowhere else.
- **Acceptance criteria are observable outcomes**, and they match what the approved breakdown said the task delivers. The ticket is the only place they are written — the roadmap row does not repeat them.
- **Status is `Not Started` and `Assignee` is `—`**, so the file goes in `todo/` and nobody holds it. `Created` is today. The `Epic` field names the epic exactly as its roadmap section does. In a vault these four are frontmatter properties — `status`, `assignee` (left empty), `created`, `epic` — beside `type`, `id`, and `tags`.
- **Write no worklog.** A ticket gets one beside it in the step that starts the work and moves it into `in-progress/`, which is an orchestrator's job, not this command's.
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
- **Statuses stay at the start** — pending in the roadmap, `Not Started` and unassigned in the ticket, and the ticket file in `todo/`. This command never marks progress, never assigns a ticket, never writes a worklog, and never moves a ticket out of `todo/`.
- **The link runs one way.** A ticket cites its feature and may cite a PRD area code; the PRD, the feature index, and the design doc never cite a ticket, an ID, or a roadmap row. The feature index lists open work through a query, which is not a citation.
- **Reuse the product's words** from the PRD for every domain term, in every document you touch — a second name for the same thing is how two documents start disagreeing.
- **Never renumber or overwrite** an existing row, ID, or ticket.
- **Hand off when the request needs code rather than documents** — name `/code`, `/orchestrate-quick`, or `/orchestrate`, and why.
