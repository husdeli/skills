---
name: ticket-board
description: "Rules for the ticket board this plugin drives — the `work/` folder and its three buckets, how a ticket is named and numbered within the epic of the feature it delivers, the properties it carries (`status`, `assigned`, `claimed`, `blocked_by`, its times and its usage), the transitions between its statuses, the claim that stops two runs building one ticket, each project's roadmap of the work that is left, and the worklog that records what was decided while a ticket was built. INVOKE THIS SKILL before you read, write, move, assign, claim, or finish a ticket, before you add or delete a roadmap row, and before you write a worklog entry. Enforces one status record per ticket, a bucket that always matches the status, one claim per ticket, a roadmap that only shrinks or gets corrected, one writer for the ticket and its worklog, and one step per status change."
---

# ticket-board skill

The board is `work/` at the framework root, with one `roadmap.md` per project listing the work that
is left on it. This skill says how a ticket is named, where it sits, what it carries, who holds it,
what records what happened to it, and what each status change has to write.

**The `sdlc-structure` skill resolves the framework root, the project, and the work root** — load it
before you resolve any path, and resolve each once. Every property below is frontmatter, and every
reference is a wikilink in a vault; `sdlc-structure` holds that shape.

## The work folder

```
work/
├── backlog/                             tickets no one has started
│   └── <CODE>-<NNN>-<slug>.md           one ticket
├── in-progress/                         tickets being built, blocked, or in review
│   ├── <CODE>-<NNN>-<slug>.md
│   └── <CODE>-<NNN>-<slug>.worklog.md   the ticket's worklog
└── done/                                tickets that are finished
    ├── <CODE>-<NNN>-<slug>.md
    └── <CODE>-<NNN>-<slug>.worklog.md
```

`work/` holds the three **buckets** and nothing else — no template, no roadmap, no subfolder inside
a bucket. A ticket in `backlog/` has no worklog, because nothing has been decided while building it
yet — except a ticket a person returned to the backlog, which keeps the worklog it already has.

**A ticket's `status` is the record, and its bucket follows from it:**

| `status` | Bucket |
| --- | --- |
| `backlog` | `backlog/` |
| `in progress` | `in-progress/` |
| `blocked` | `in-progress/` |
| `review` | `in-progress/` |
| `done` | `done/` |

- **A ticket sits in exactly one bucket, and the bucket always matches its status.** A status change
  that crosses buckets moves the file in the same step that rewrites the status. A change inside
  `in-progress/` — to `blocked`, to `review`, or back — rewrites the status and leaves the file
  where it is.
- **When the status and the bucket disagree, the status wins.** Move the file to the bucket its
  status names before anything else; never rewrite the status to match the folder.
- **A ticket's worklog moves with it**, in the same step.
- **Find a ticket by its ID, never by a stored path.** Search all three buckets for
  `work/*/<CODE>-<NNN>-*.md`. Cite a ticket by its file name, so no later move invalidates the
  reference.
- **An empty bucket may be absent.** Create it the first time a ticket moves into it.

**A framework root on an older shape keeps its tickets where they are.** `tickets/todo/`,
`tickets/in-progress/`, and `tickets/done/` are read as the three buckets, and a flat `tickets/`
folder as a board whose status property alone carries the state. Never build the buckets around
tickets already in flight; name the setup entry point as the way to migrate.

## The ticket

### Name

**A ticket is named `<CODE>-<NNN>-<slug>.md`**: `CHECKOUT-001-saved-card.md`. Its ID is
`<CODE>-<NNN>`: `CHECKOUT-001`.

- **`<CODE>` is the `code` of the feature the ticket delivers**, from its feature note. A ticket
  whose code no feature carries is not a valid ticket.
- **`<NNN>` is three digits, and restarts at `001` in each epic.** Two features planned on separate
  branches write into separate number spaces, so neither overwrites the other on merge.
- **`<slug>` is kebab-case**, a few words on what the ticket delivers.

### Properties

```yaml
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
timing: 47
tokens: 1284000
cost: 4.12
related:
  - "[[checkout.design]]"
---
```

| Property | What it holds |
| --- | --- |
| `feature` | Required. A link to the feature note of the feature the ticket delivers. That note's `code` is the `<CODE>` the ticket's name starts with; a ticket whose `feature` and name disagree is not a valid ticket. |
| `status` | Required. Where the work stands; see [States and transitions](#states-and-transitions). |
| `priority` | Required. `Critical`, `High`, `Medium`, or `Low`. The roadmap sorts by it, so roadmap order is priority order. |
| `depends_on` | The IDs of every ticket this one cannot start without, as bare IDs. `[]` when there are none. |
| `assigned` | The agent that works on the ticket now, or is planned to, by its name: `coding-2`. See [Who holds the ticket](#who-holds-the-ticket). |
| `claimed` | The run that holds the ticket: `orchestrate-2`. See [The claim](#the-claim). |
| `blocked_by` | Required while `status` is `blocked`, and absent otherwise. See [What blocks a ticket](#what-blocks-a-ticket). |
| `createdAt` | Required. When the ticket was created. Set once, in the step that creates it, and never changed. |
| `updatedAt` | Required. When the ticket last changed. Equal to `createdAt` on a new ticket, and rewritten by every step that changes the ticket. |
| `timing` | How long agents spent implementing the ticket, in whole minutes, summed over every agent and every run. |
| `tokens` | How many tokens they spent, input and output together. |
| `cost` | What those tokens cost, in US dollars to two decimal places, at the price of the model that spent them. |
| `related` | The design docs the ticket builds. Never the feature or a dependency again — each has its own property. |

**Both times are local date and time, `YYYY-MM-DDTHH:mm`**, the form Obsidian reads as a
date-and-time property. Read the clock with `date "+%Y-%m-%dT%H:%M"`; never guess it.

**A ticket no agent has worked on has no `timing`, `tokens`, or `cost`.** See [Usage](#usage).

**A ticket carries no `type`, no `id`, no `epic`, and no repository.** Its name says its ID and its
epic, its bucket makes it a ticket, and the run resolves the work root when it starts the ticket.

### States and transitions

| `status` | Meaning |
| --- | --- |
| `backlog` | The ticket is planned, and no work has started |
| `in progress` | The ticket is being built |
| `blocked` | The ticket cannot move forward |
| `review` | The work is built and waits for verification and a code review |
| `done` | The ticket is finished |

| From | To |
| --- | --- |
| `backlog` | `in progress` |
| `in progress` | `blocked`, `review`, or `backlog` when work on it stops |
| `blocked` | `in progress`, or `backlog` when work on it stops |
| `review` | `done`, or `in progress` when the review asks for changes |
| `done` | Nothing; `done` is final |

**A ticket is `done` only when verification passed and the code review approved.** A passing suite
alone never finishes a ticket.

**Finished work that needs more work gets a new ticket.** A `done` ticket never changes status; the
new ticket names the change.

### What blocks a ticket

What blocks a ticket is its `blocked_by` property, kept apart from the status:

```yaml
status: blocked
blocked_by:
  - CHECKOUT-002
  - Payment provider has not issued sandbox keys
```

- **Each entry is a ticket ID or one line naming an outside cause.**
- **`blocked_by` is required while the status is `blocked`, and absent otherwise.** The step that
  moves a ticket out of `blocked` removes it.
- **A person clears an outside cause by deleting its line.**
- **A blocked ticket is resumable when its `blocked_by` holds only IDs of `done` tickets, or
  nothing.**

`depends_on` and `blocked_by` answer different questions. `depends_on` is planned, never pruned, and
says what a ticket waits on before it starts. `blocked_by` is found during a run, and says what
stopped a ticket that had started.

## Who holds the ticket

**`assigned` names the agent that works on the ticket now, or is planned to**, as `<role>-<n>`:
`feature-interviewer-2`, `implementation-planner-2`, `plan-reviewer-2`, `coding-2`,
`code-reviewer-2`. `<n>` is the number of the run the agent works for, so `assigned` names the run
as well as the role. A session doing the work itself names its command the same way: `code-1`.

**`assigned` follows the status:**

| `status` | `assigned` |
| --- | --- |
| `backlog` | Optional; the agent planned to work on it, once that is known |
| `in progress` | Required; the agent working on it |
| `blocked` | Optional; the agent that resumes it once it is unblocked |
| `review` | Optional; the agent that reviews it, once that is known |
| `done` | Absent |

**Whoever writes the status writes `assigned`, in the same step,** so the two never disagree.

## The claim

**`claimed` names the run that holds the ticket**, as `<command>-<n>`: `orchestrate-2`. It is a
guardrail, not an assignment: a ticket can be claimed before anyone knows which agent will work on
it, and `claimed` may be set at any status except `done`.

- **`<n>` is the lowest positive number no other claim in `work/` uses.** The run's agents carry the
  same number, so `coding-2` works for `orchestrate-2`.
- **The claim is written first and read back.** A run that reads back another run's claim drops the
  ticket and picks again.
- **A claimed ticket is never ready for another run.**
- **One work root holds one build at a time.** A run whose work root another claimed `in progress`
  or `review` ticket holds releases its claim and picks again. Two builds in one tree would each
  check the other's changes.
- **Every exit removes the claim**: finish, escalation, and abort.

A file cannot hold a lock, so the read-back narrows the race without closing it. A run that dies
without exiting leaves its claim for a person to remove.

## Every ticket belongs to an epic, and every epic delivers one feature

An **epic** is the group of tickets that delivers one **feature**. They share one short uppercase
code — two to eight letters, from the feature note's `code` — and that code prefixes every ticket
ID under it: `CHECKOUT-001`, `CHECKOUT-002`.

**The feature note is where the code comes from.** Load the **`feature`** skill before you open an
epic. A feature is created before its first ticket — the code exists because the feature exists, and
a ticket never mints a code. Work no customer would name, such as a migration or a cleanup, still
gets a feature note, so its code has one owner.

**Read the next number out of the files.** Search all three buckets for `<CODE>-*.md`, take the
highest number in the epic, and add one. `done/` counts, because a finished ticket keeps its number.
**Never take the next number from the roadmap** — it lists only the work that is left. Never reuse
a number, and never renumber a ticket that exists.

**A board on a project-wide scheme keeps the IDs it has.** Never rewrite `SW-001` into an epic ID on
your own; keep continuing that scheme, and name the setup entry point as the way to migrate.

## Which tickets are ready

A run lists the ready tickets in roadmap order, which is priority order. **A ticket is ready when:**

- it sits in `backlog/`, carries no claim, and every ID in its `depends_on` names a `done` ticket; or
- it is `blocked`, carries no claim, and is resumable — its `blocked_by` holds only IDs of `done`
  tickets, or nothing.

A ticket of a project whose note says `done` is never offered, and one whose note says `backlog` is
offered only when the project is named. An ID in `depends_on` that no ticket carries is not
satisfied: the ticket stays not ready, and the report names the missing ID.

## The roadmap holds the work that is left

**Each project keeps one `roadmap.md`, in its project folder**, listing the tickets of that project
that are not done yet, and nothing else. A ticket belongs to the projects its feature's `projects`
property names; when a feature names several, its epic has a section in each of their roadmaps, and
every write to a row writes it in each.

```markdown
---
type: roadmap
updated: 2026-10-09
tags:
  - sdlc/roadmap
---
# Acme Billing — roadmap

## CHECKOUT — Checkout

**Feature**: [[checkout.feature]]

A customer pays for an order without leaving the page.

| ID | Task | Priority | Status | Depends on | Ticket |
| --- | --- | --- | --- | --- | --- |
| CHECKOUT-002 | Saved card | High | 🚧 **In Progress** | — | [[CHECKOUT-002-saved-card]] |
| CHECKOUT-003 | Receipt email | Medium | ⬜ **Pending** | CHECKOUT-002 | [[CHECKOUT-003-receipt-email]] |
```

**A row's `Status` cell mirrors its ticket's status**: `⬜ **Pending**` for `backlog`,
`🚧 **In Progress**` for `in progress` and `review`, and `🚫 **Blocked**` for `blocked`. There is no
done marker, because a done ticket leaves the file.

**The row is the whole task in this file.** What the ticket delivers and what it must satisfy live
in the ticket. Never add a per-task section, a description, or an acceptance-criteria list to the
roadmap. `Status` and `Priority` repeat the ticket's own properties so the table can be read and
sorted without opening every ticket.

**The ticket is the record, and the table reflects it:**

- **Write the ticket first, then its row, in the same step.** Whoever changes a ticket's priority or
  status changes that row in the same edit, and re-sorts the table when the priority moved it.
- **When a row and its ticket disagree, the ticket wins.** Correct the row; never edit the ticket to
  match the row.
- **Correct a stale row the moment you read its ticket.** Fix the rows whose tickets you actually
  read, and leave every other row alone.
- **A row whose ticket sits in `done/`** is a row the finishing step failed to delete. Delete it.
- **An open ticket with no row at all** gets one, at its sorted position.

**The row's `Depends on` cell is the outstanding subset of the ticket's `depends_on`**, and it is
computed: an ID leaves the cell when its ticket is `done`, and a cell of `—` means the ticket can
start. Never edit the cell on its own; change the ticket's `depends_on` and let the cell follow.
`depends_on` itself is never pruned — what a ticket depended on is a fact about it, not a status.

**A table is sorted so that reading it top to bottom is reading the order to build in:**

1. **A row never sorts above a ticket it still depends on.** This is absolute.
2. **A blocker carries the highest priority of anything waiting on it.** A `Low` chore that holds up
   a `Critical` ticket is built at the `Critical` ticket's urgency.
3. **Everything else goes by priority** — `Critical`, `High`, `Medium`, `Low` — and a tie goes to the
   lower ticket number.

Re-sort whenever a priority changes, a dependency clears, or a ticket is added.

**Rebuilding every table from the tickets** is one command, for drift nobody has read yet:

```shell
<plugin>/scripts/build-roadmap.py            # rewrite every table from the tickets
<plugin>/scripts/build-roadmap.py --check    # report what differs, write nothing
```

Run it when the whole board may have moved — after an edit to several tickets, or before a planning
session. In the middle of a run, correct only the rows you read.

**Delete the row when its ticket is done**, in the same step that finishes the ticket:

1. Delete the ticket's row, in every roadmap that lists it.
2. Delete the ticket's ID from every other row's `Depends on` cell, write `—` in a cell left empty,
   and re-sort the table when this frees a row to move up. Leave every ticket's `depends_on` alone.
3. Delete the epic's section once its last row is gone. Set its feature to `status: done` only after
   you check a work root holds the whole feature, as the **`feature`** skill requires.
4. Bump the roadmap's `updated`.

**The roadmap is not a history.** It never grows a done section, a struck-through row, or a note
about work that has already landed — `work/done/` is the record.

**Carry a correction forward, never a report backward.** When finished work changes what a remaining
ticket has to do, rewrite that ticket and its row. When it constrains every remaining ticket in the
epic, add one `**Note**:` line under the epic's sentence, and delete it as soon as it no longer
applies.

**An older roadmap may hold finished rows or a `###` detail section per task.** Read it as it is,
and name the setup entry point as the way to clean it up. **A ticket with no `priority`** reads as
`Medium`; write that value into the ticket and the row the next time either is touched, and say in
the report that the priority was assumed.

## The worklog

**A ticket that has started has a worklog beside it** — `<CODE>-<NNN>-<slug>.worklog.md`, in the
ticket's bucket, moving with it. The ticket says what to build. The worklog says what was decided
while it was built: which approach won, what the review sent back, what the verification found, what
a fix changed. None of that survives anywhere else.

**Create it in the step that starts the ticket**, from [the worklog
template](./assets/worklog-template.md). A resumed ticket keeps its worklog, and the entry is
appended. **Never delete it**: the finished ticket and its worklog together are the record.

**One entry per stage that landed**, appended at the end of the file:

```markdown
## 2026-10-09 14:12 — coding · implement

- Put the retry in the HTTP wrapper, not in each caller — the policy is inherited, not repeated.
- Left the cache out, which the plan left open: the endpoint already sits behind the CDN.
```

The header carries the local date and time, the role whose work it records, and the stage. The run's
own entries name the orchestrator's claim: `orchestrate-2 · start`, `orchestrate-2 · done`.

- **Decisions and outcomes only** — what was chosen, and what it beat. One line each.
- **The opening entry names the ticket, the work root with the evidence that settled it, and the
  end-to-end decision.** The ticket carries no repository, so this entry is the only record of where
  it was built. `sdlc-structure` holds how the work root is resolved.
- **Only what a later reader cannot get elsewhere.** Never the plan in full, never code, never a
  restatement of the ticket, and never pasted command output — name the command and its result.
- **A stage that decided nothing still gets one line**: what ran, and what came back.
- **Never rewrite or delete an earlier entry.** A decision that turns out wrong becomes a new entry
  that says so.

## The orchestrator is the only writer

**Only the orchestrator writes a ticket, its worklog, and the roadmap.** Every agent reports its
decisions to it, and it writes them down at the boundary where the stage lands, so the files have
one writer and two concurrent agents cannot lose each other's entry. A command that does not own the
board — one that neither moves a ticket nor sets its status — appends a worklog entry only when a
worklog is already there, and creates none.

**A status change is one step.** It rewrites `status`, `assigned`, and `updatedAt`, moves the file
and its worklog to their bucket, edits the roadmap row, and appends the worklog entry together, in
one tool block. Never spread a status change across turns, and never delegate one to an agent.

### Starting a ticket

1. **Claim it** — write `claimed`, read it back, and drop the ticket if another run's claim is
   there. Resolve the work root and confirm the session can write to it; a run that cannot stops
   here, removes its claim, and writes nothing else.
2. **`status`** → `in progress`, **`assigned`** → the first agent, **`updatedAt`** → now. Remove
   `blocked_by` when the ticket resumes from `blocked`.
3. **Move it** into `work/in-progress/`.
4. **Write the worklog** beside it with the opening entry — or append to it, when the ticket resumes.
5. **Roadmap row** → `🚧 **In Progress**`, and the `Priority` cell set to what the ticket says.

### Moving inside `in-progress/`

Each of these rewrites `status`, `assigned`, and `updatedAt`, updates the row, and leaves the file
where it is:

- **To `review`** when the change is built and verification and the code review start.
- **Back to `in progress`** when either one fails, and `coding` receives every failure at once.
- **To `blocked`** when the run stops; see [Stopping without finishing](#stopping-without-finishing).

### Finishing a ticket

Only when every check passed and the code review returned `APPROVED`. In one step:

1. **`status`** → `done`, and remove **`assigned`** and **`claimed`**. **`updatedAt`** → now.
2. **Usage** → add the run's totals to `timing`, `tokens`, and `cost`.
3. **Move** the ticket and its worklog into `work/done/`.
4. **Worklog** → the closing entry: what shipped, and each recommendation nobody acted on.
5. **Roadmap** → delete the row, by the four steps above.
6. **Carry corrections forward** — rewrite every remaining ticket this work proved wrong. Write
   nothing about the ticket you just finished.

### Stopping without finishing

Every stop moves the ticket to `blocked`, so the next run can see what it waits on:

| Why the run stopped | `blocked_by` holds |
| --- | --- |
| **Escalated** — a gate failed at its cap, an agent reported a blocker, or the answerer handed it back | One line naming what a person must decide |
| **Aborted** — an agent returned no result block after one re-ask | One line naming the stage and the agent that returned no result |
| **Waits on another ticket**, found during the run | That ticket's ID |

In one step: **`status`** → `blocked`, **`blocked_by`** as above, remove **`assigned`** and
**`claimed`**, **`updatedAt`** → now, add the run's usage, set the row to `🚫 **Blocked**`, and
append the outcome entry: the stage it stopped at, what is open, and what the next run picks up. The
file stays in `in-progress/`.

Never mark a stopped ticket `done`, and never delete its roadmap row on this path.

### Returning a ticket to the backlog

**Only a person returns a ticket to `backlog`**, when work on it stops and nobody should resume it
yet. In one step: **`status`** → `backlog`, remove `assigned`, `claimed`, and `blocked_by`,
**`updatedAt`** → now, move the ticket to `work/backlog/`, set the row to `⬜ **Pending**`, and
append a worklog entry saying why. The worklog moves with the ticket and is never deleted, so it is
the one worklog `backlog/` may hold; the next run that starts the ticket appends to it.

## Usage

**Usage accumulates across runs.** The orchestrator adds each agent's time and tokens as its turn
lands. At every exit — finish, escalation, and abort — it adds the run's totals to the ticket's
`timing`, `tokens`, and `cost`, so a resumed ticket's numbers cover every run.

## What goes in a ticket

**Tickets describe WHAT, not HOW:**

✅ Include: requirements, acceptance criteria, UX description, business logic, high-level architecture,
data needs, testing expectations
❌ Exclude: specific file paths, implementation-level names, internal module structure, data layer
details, code-level patterns

Implementation decisions belong in the plan, written after the codebase is explored. The full rules
are in [the ticket guidelines](./references/ticket-guidelines.md).

**A diagram belongs in `diagrams/`, referenced from the ticket.** The **`diagrams`** skill holds how
one is drawn and how a ticket points at it.

**A ticket writes the product's terms, and links them.** Load the **`glossary`** skill: it holds the
term, its definition, and the link a ticket writes at the term's first use.

## Templates

The templates live in this skill, never in `work/`:

- [Ticket template](./assets/ticket-template.md)
- [Worklog template](./assets/worklog-template.md)
