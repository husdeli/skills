---
name: ticket-board
description: "Rules for the ticket board this plugin drives — where a ticket lives, the status folders it moves through, the epic that numbers it and the feature that epic delivers, the roadmap that lists the work that is left, the `Assignee` field that names who holds it, and the worklog that records what was decided while it was built. INVOKE THIS SKILL before you read, write, move, assign, or complete a ticket, before you add or delete a roadmap row, and before you write a worklog entry. Enforces one status record per ticket, a roadmap that only shrinks or gets corrected, one writer for the worklog, and one tool block per status transition."
---

# ticket-board skill

The board is `tickets/` and `roadmap.md` inside the docs root. This skill says how a ticket is
named, where it sits, who holds it, what records what happened to it, and what each status
transition has to write.

**The `product-docs` skill says where the docs root is, and where the work root is** — load it
before you resolve any path, and resolve both roots once. Every `.sdlc/…` path below means `<docs root>/…`. In a vault the
fields below are frontmatter properties and the references are wikilinks; `product-docs` holds
that mapping too.

## The board

**Tickets live in `.sdlc/tickets/`, in one folder per status**, one file per ticket, named
`<ID>-<slug>.md` (e.g. `AUTH-001-user-login.md`):

```
.sdlc/tickets/
  TEMPLATE.md          copy this per ticket — the template itself never moves
  todo/                AUTH-001-user-login.md
  in-progress/         AUTH-002-session-timeout.md
                       AUTH-002-session-timeout.worklog.md
  done/                BILLING-001-invoice-export.md
                       BILLING-001-invoice-export.worklog.md
```

The folder is the board. The `**Status**` field inside the file is the record — the frontmatter
`status` property, in a vault. The two never disagree, because the file moves in the same step
that rewrites its status field. Five status values map onto three folders:

| Status field | Folder |
| --- | --- |
| `Not Started` | `todo/` |
| `In Progress`, `Blocked`, `Review` | `in-progress/` |
| `Completed` | `done/` |

**Move a ticket with `git mv`** when the file sits inside a git working tree, so it keeps its
history. Move it with a plain `mv` when it does not — a vault usually is not a git working tree,
and neither is a project without git. **Whatever sits beside the ticket moves with it** — its
worklog, and a discovery brief when the work produced one.

**Find a ticket by its ID, never by a stored path** — the path changes as the work progresses.
Glob `.sdlc/tickets/*/<ID>-*.md` first, then `.sdlc/tickets/<ID>-*.md` for a project that still
keeps its tickets flat. Cite a ticket by file name, so that no later move invalidates the
reference.

**A flat `tickets/` folder stays flat.** Never build the status folders around tickets that are
already in flight. Keep writing the status field in place, and name the platform's setup entry
point as the way to migrate. Run that entry point when the tickets folder does not exist at all.
A project that already keeps tickets elsewhere keeps them there — do not start a second home.

## Every ticket belongs to an epic, and every epic delivers one feature

An **epic** is the group of tasks that deliver one **feature**. The two are one thing seen from
two sides: the feature is what a customer can do, and the epic is the work that gets it there.
They share one short uppercase code — two to eight letters, taken from the product's own
vocabulary — and that code prefixes every ticket ID under it: `AUTH-001`, `AUTH-002`,
`BILLING-001`.

**The feature note is where the code comes from.** `<docs root>/features/<feature>/<feature>.feature.md`
carries it, and the **`feature`** skill holds how a feature is opened, named, and coded. Load that
skill before you open an epic: an epic with no feature note is an epic whose code nothing owns.
A feature exists before its first ticket, and outlives its last one.

**An epic with no feature is the exception, not the shape.** A migration, an upgrade, or a cleanup
that no customer would name gets an epic and a feature note with `customer_facing: false`, so the
code still has one owner and the work still has one home.

**The numbering restarts at 001 in each epic.** That is what the prefix buys. Two branches that
plan separate features write into separate number spaces, so each can add a first ticket and
neither overwrites the other when the branches merge. One project-wide sequence cannot do that:
both branches take the same next free number, and both name the file the same thing.

**`roadmap.md` is the list of epics that still have work in them.** It holds one
`## <CODE> — <epic name>` section per epic, and that section holds the epic's task table. An epic
exists in the roadmap before any ticket carries its code, and each code is unique in the project.
A code may repeat a PRD area anchor code when the feature fills that whole area. A code never means
two different things.

**The roadmap shrinks; the features do not.** An epic's section is deleted when its last row is
gone, and the feature note stays — it moves to `status: Shipped` and becomes the record that the
product has the feature. Never read the roadmap as the list of what the product does; that list is
`features/`.

**Read the next number out of the files.** Glob every status folder for `<CODE>-*.md`, take the
highest number in the epic, and add one. `done/` is part of that search, because a completed
ticket keeps its number. **Never take the next number from the roadmap** — it lists only the
tasks that are left, so the highest number in it is not the highest number used. Never reuse a
number, and never renumber a ticket that exists — the ID is how the roadmap, the branches, and
the reviews cite it.

**A project on a project-wide scheme keeps the IDs it has.** Never rewrite `SW-001` into an epic
ID on your own. Keep continuing that project's scheme, and name the platform's setup entry
point as the way to migrate.

## The roadmap holds the work that is left

`roadmap.md` lists the tasks that are **not done yet**, and nothing else. One
`## <CODE> — <epic name>` section per epic, a `**Feature**:` line linking the feature the epic
delivers, one sentence on what the epic delivers, and one table row per task:

```markdown
## CHECKOUT — Checkout

**Feature**: [[checkout.feature]]

A customer pays for an order without leaving the page.
```

| ID | Task | Priority | Status | Depends on | Ticket |
| --- | --- | --- | --- | --- | --- |
| AUTH-002 | Session timeout | High | ⬜ **Pending** | — | `AUTH-002-session-timeout.md` |

A row carries one of three statuses — `⬜ **Pending**`, `🚧 **In Progress**`, `🚫 **Blocked**`.
There is no completed status, because a completed task leaves the file. In a vault, the `Ticket`
cell is the wikilink `[[AUTH-002-session-timeout]]`, so it follows the file between the status
folders.

**The row is the whole task in this file, except for two fields it mirrors.** What the task
delivers, and what it has to satisfy, live in its ticket — the file every command opens anyway.
Never add a per-task `###` section, a description paragraph, or an acceptance-criteria list to
the roadmap. `Status` and `Priority` are the exception: each repeats the ticket's own field so
the table can be read, and sorted, without opening every ticket.

**The ticket is the record, and the table reflects it.** A row is a view of a ticket, never a
second opinion about it. So:

- **Write the ticket first, then its row, in the same tool block.** Whoever changes a ticket's
  priority or status changes that row in the same edit, and re-sorts the table when the priority
  moved it. A task whose priority changes is one edit, not two.
- **When a row and its ticket disagree, the ticket wins.** Correct the row; never edit the ticket
  to match the row. The ticket carries the whole task, so it is the cheaper thing to trust.
- **Correct a stale row the moment you read its ticket.** Every command that picks a task opens
  its candidates' tickets already, so it costs nothing to fix a `Priority` or `Status` cell that
  does not match what the ticket says. Fix the rows whose tickets you actually read, and leave
  every other row alone — a row you did not verify is not a row you may rewrite.
- **A row whose ticket sits in `done/`** is a row the finishing step failed to delete. Delete it,
  by the four steps below.
- **An open ticket with no row at all** gets one, at its sorted position, with the priority and
  status its ticket carries.
- **Rebuilding the whole file from the tickets** — every row, in every epic — is the setup entry
  point's job, not a task command's. A command in the middle of a task touches the epic it is
  working in, so two branches building different features keep changing different lines.

**A `Depends on` cell lists outstanding blockers only.** A cell of `—` means the task is ready to
start. An ID still in the cell is satisfied only when that work is finished — its ticket sits in
`done/`, or it is no longer a row in the file at all. In progress never satisfies a dependency. A
cell may name a task in another epic, because every ID is unique across the project.

**A table is kept sorted by priority, and a `Depends on` cell always wins the tie.** Within one
epic's table, order rows `Critical` first, then `High`, `Medium`, `Low`; break a tie between
equal priorities by which was added first. Then apply the one hard constraint: **a row never
sorts above a task still named in its own `Depends on` cell.** An urgent task blocked on a slower
one sits below it in the table regardless of priority — the table is an order to build in, and
work that cannot start yet does not belong at the top. A dependency in another epic does not move
the row; it is enforced by the cell alone, because sort order is a per-epic thing and every ID is
unique across the project. Re-sort the table whenever a row's priority changes, a dependency
clears, or a task is added — the position a row lands in is not a record of when it was written,
so the file is not an append log.

**Delete the task when it is done**, in the same step that marks its ticket `Completed`:

1. Delete the task's row.
2. Delete the task's ID from every other row's `Depends on` cell, and write `—` in a cell that
   has nothing left. **Re-sort the table** when this frees a row to move up — a cleared
   dependency can put a `Critical` task at the top that priority alone had ranked below it.
3. Delete the epic's whole section once its last row is gone, and set its feature to
   `status: Shipped` with today's `shipped` date — after you check the work root holds the whole
   feature, as the **`feature`** skill requires. A feature that is only partly usable stays
   `In Progress` and keeps no roadmap section; say so in the report.
4. Bump `**Last updated**`.

The ticket in `done/` is the record of what was built, so the roadmap loses nothing. **The
roadmap is not a history.** It never grows a completed list, a done section, a struck-through
row, a changelog, or a note about work that has already landed.

**Carry a correction forward, never a report backward.** When finished work changes what a
remaining task has to do, rewrite that task — its row here, and its ticket. When it constrains
every remaining task in the epic, add one `**Note**:` line under the epic's sentence, and delete
that line as soon as it no longer applies:

> **Note**: sessions are stored server-side. Every remaining task in this epic reads the session
> from the store, not from the cookie.

**An older roadmap may still hold finished work** — rows marked completed, and a `###` detail
section per task. Read it as it is, take a description from the detail section when a task has no
ticket, and name the platform's setup entry point as the way to clean the file up.

**A row or a ticket from before this rule may carry no `Priority` at all** — a blank cell, no
field in the ticket, or the template's own placeholder left unfilled. Treat it as `Medium`, write
that value into both the row and the ticket the next time either is touched, and say in the report
that a priority was assumed rather than read. This is the one case where the table's sort order is
a guess, not a decision someone made.

## Who holds the ticket

Every ticket carries an **`Assignee`** field, under `Status`. It answers one question: who is
doing this work right now.

| Value | What it means |
| --- | --- |
| `—` | Nobody holds it. A ticket in `todo/`, and a ticket in `done/`. |
| An agent name | That agent is working on the ticket now — `feature-interviewer`, `implementation-planner`, `plan-reviewer`, `coding`, `verify`, `code-reviewer`. |
| A command or skill name | The session is doing the work itself instead of delegating it to an agent, signed with the command that is driving it. |
| `user` | A person has to act before the work goes on: the task escalated, or it is blocked. |

**An agent's name is the `name` field of its definition** — the role it plays, not a codename.
When one role runs twice at once, as two plan reviewers with different lenses do, the lens goes in
brackets after the name: `plan-reviewer (correctness)`, `plan-reviewer (codebase fit)`.

**Two agents holding the ticket at once are two names in one value**, comma separated:
`**Assignee**: verify, code-reviewer`. The worklog names each of them separately.

**Whoever writes the status writes the assignee**, in the same edit, so the two never disagree. A
ticket with no `Assignee` field is unassigned — add the field under `Status` the next time you
write that ticket. In a vault the field is the `assignee` property, and an unassigned ticket
leaves it empty.

## The worklog

**A ticket that is in flight has a worklog beside it** — `<ID>-<slug>.worklog.md`, in the same
folder as the ticket, moving with it.

The ticket says what to build. The worklog says what was decided while it was built — which
approach won, what the review sent back, what the verification found, what a fix changed. None of
that survives anywhere else: a plan, a review verdict, and a test run live in one session and are
gone when it ends.

**Create it in the step that starts the ticket**, from [the worklog
template](./assets/worklog-template.md). **Move it with the ticket** into `done/`, and never
delete it: the finished ticket and its worklog together are the record of the task.

**One entry per agent turn that landed**, appended at the end of the file:

```markdown
## 2026-09-27 14:12 — coding · implement

- Put the retry in the HTTP wrapper, not in each caller — the policy is inherited, not repeated.
- Left the cache out, which the plan left open: the endpoint already sits behind the CDN.
```

The header carries the local date and time, the name of the agent or command whose work it
records, and the stage. In the body:

- **Decisions and outcomes only** — what was chosen, and what it beat. One line each.
- **The opening entry names the work root** — the repository code, its absolute path, and the one
  line of evidence that settled it. A ticket carries no repository field, so this entry is the only
  record of where the task was built. `product-docs` holds how the work root is resolved.
- **Only what a later reader cannot get elsewhere.** Never the plan in full, never code, never a
  restatement of the ticket, and never pasted command output — name the command and its result.
- A stage that decided nothing still gets one line: what ran, and what came back.
- **Never rewrite or delete an earlier entry.** A decision that turns out wrong becomes a new
  entry that says so.

**Whoever runs the stage writes the entry**, at the boundary where that stage lands. Agents report
their decisions and the session that spawned them writes them down, so the file has one writer and
two concurrent agents cannot lose each other's entry. A command that does not own the board —
one that neither moves a ticket nor sets its status — appends an entry only when a worklog is
already there, and creates none.

## The three transitions

A ticket's state lives in three places: the status field, the folder it sits in, and its roadmap
row. They stay consistent only because each transition writes **all of them in one tool block**.
Never spread a transition across turns, and never delegate one to an agent.

### Starting a ticket

1. **Find it by its ID.**
2. **Status field** → `In Progress`, in the file's existing vocabulary and format.
3. **`Assignee`** → whoever is about to do the work.
4. **Move it** into `.sdlc/tickets/in-progress/`. Skip the move in a flat tickets folder — the
   status field alone carries the state there.
5. **Write the worklog** beside it, in its destination folder, with the opening entry: the task,
   what it delivers, the **work root** this task is built in, and any decision already settled. A
   ticket escalated by an earlier run already has a worklog — append to it, never overwrite it.
6. **Roadmap row** → the in-progress marker, in the file's own style, and the `Priority` cell set
   to what the ticket you just opened actually says. This is the cheapest place to catch a stale
   row: you are holding the ticket, and you are already writing the row.

With no ticket file, update the roadmap alone.

### Finishing a ticket

Only when the work is both verified and reviewed. A passing suite on its own is not enough.

1. **Status field** → `Completed`, and **`Assignee`** → `—`.
2. **Worklog** → the entries for the stages that just landed, then a closing entry: what shipped,
   and any recommendation nobody acted on.
3. **Move it** into `.sdlc/tickets/done/`, with its worklog and any brief.
4. **Roadmap** → delete the task, by the four steps above.
5. **Carry corrections forward** — rewrite any *remaining* task this work changed, in the same
   edit. Write nothing about the task you just finished.

### Stopping without finishing

A run that escalates, or that dies with an agent returning nothing, leaves the ticket where it is:
status `In Progress`, file in `in-progress/`, roadmap row untouched.

1. **`Assignee`** → `user`. A person has to act.
2. **Worklog** → the outcome entry: the stage it stopped at, what is still open, and what the next
   session should pick up.

Never mark a ticket `Completed`, and never delete its roadmap row, on this path.

## What goes in a ticket

**Tickets describe WHAT, not HOW:**

✅ Include: requirements, acceptance criteria, UX description, business logic, high-level architecture, data needs, testing expectations  
❌ Exclude: specific file paths, implementation-level names, internal module structure, data layer details, code-level patterns

Implementation decisions belong in the plan, written after the codebase is explored. The full
rules are in [the ticket guidelines](./references/ticket-guidelines.md).

**A ticket's related documents are its `related:` property**, never a section in its body: the
PRD area it serves, the design docs it builds, the goal it advances, and the sibling tickets it
depends on or unblocks. The `product-docs` skill holds the rule.

**A diagram belongs in `diagrams/`, referenced from the ticket.** The **`diagrams`** skill holds
how one is drawn and how a ticket points at it.

**A ticket writes the product's terms, and links them.** Load the **`glossary`** skill: it holds
the term, its definition, and the link a ticket writes at the term's first use. Never restate a
definition in a ticket.

## Templates

- [Ticket template](./assets/ticket-template.md) — the shape `tickets/TEMPLATE.md` is copied from
- [Worklog template](./assets/worklog-template.md)
