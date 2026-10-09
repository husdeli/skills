---
description: Show what is actionable on the roadmap right now — what is in flight and who holds it, what is ready to start, and what is blocked and by what.
argument-hint: [epic code to narrow to, or a roadmap path]
---

# What's Next

Answer one question about this project: **what can be worked on right now?** Read the roadmap and
the tickets, sort every task by what stands between it and being started, and report it. You
write nothing here.

Filter (if provided): $ARGUMENTS

**Load three skills before you report**, each once — namespaced here as `sdlc:<name>`:

- **`sdlc-structure`** — where the project and the work root are. Every `.sdlc/…` path below means `<project>/…`.
- **`ticket-board`** — the roadmap's shape, what a `Depends on` cell means, the status-to-folder
  map, the `Assignee` field, and the worklog. It is what you are reading; read it there rather
  than inferring it from the files.
- **`technical-writing`** — this is a status answer a person reads in one pass.

The documents sit in the project: `roadmap.md`, and `tickets/<status>/<ID>-<slug>.md` with a
worklog beside a ticket that work has started on.

**Say where the work happens.** A project with a `sdlc.json` registry drives one repository or
several. List them once, at the top of the report — the code and the path per entry — and, for each
ticket in flight, name the work root its worklog records. That is the only place a task's repository
is written down, and it is what tells a reader which tree to open. Say nothing about a repository
when there is no registry: the code is then wherever this session is standing.

**This command is read-only.** Do not write a file, do not move a ticket, do not change a status,
and do not start a task. It reports what is there and stops. Reading the roadmap wrong is the one
mistake this command can make, so read the files rather than answering from memory.

## 1. Read the roadmap and the tickets

- **The roadmap** is the project's `roadmap.md`, unless `$ARGUMENTS` gives a path. When neither
  exists, look for a roadmap at the repository root. With no roadmap anywhere, say so and name
  `/setup` as the way to create the structure, then stop.
- Read **every** `## <CODE> — <epic name>` section, not just the first. A dependency may name a
  task in another epic. Read an epic's `**Note**:` line when it has one: it constrains every task
  in that epic.
- **List the ticket folders** — `.sdlc/tickets/todo/`, `in-progress/`, and `done/` — in one pass.
  The folder a ticket sits in is the board, and it tells you what is really in flight. `done/` is
  where the finished work is: count it, and read no file in it.
- **A row does not say what its task delivers — its ticket does.** Read the ticket of every task
  you are about to report as **in flight** or **ready**, and take the one-line description and
  the acceptance criteria from there. A waiting task needs its row and nothing more.
- **For an in-flight task, read two more things from its ticket's folder**: the ticket's
  `Assignee` field — the `assignee` property in a vault — which names who holds the work right
  now, and the **last entry of its worklog**, which says what happened most recently. In flight is
  usually one or two tasks, so this costs two reads and it is the only way to answer "where did
  this stop?". A ticket with no `Assignee` field is unassigned; a ticket with no worklog was
  started before the worklog existed, or by hand.
- On an **older roadmap** — rows marked completed, a `###` detail section per task — read what is
  there, take a description from the detail section when a task has no ticket, and say in one line
  that `/setup` cleans the file up.

**When `$ARGUMENTS` names an epic code** (`AUTH`, `BILLING`), narrow every list below to that
epic, and say in one line that you narrowed it.

## 2. Sort every task

Put each task in exactly one bucket:

| Bucket | Test |
| --- | --- |
| **In flight** | Its status is in-progress, blocked, or in review, or its ticket sits in `in-progress/` |
| **Ready** | It is pending, and every ID in its `Depends on` cell is finished |
| **Waiting** | It is pending, and at least one ID in its `Depends on` cell is not finished |

Every row lands in one of the three. There is no done bucket, because a finished task is not in
the file.

Judging the buckets — `ticket-board` says when a `Depends on` cell counts as satisfied, and the
rest is this command's:

- **The ticket folder wins over the roadmap row** when the two disagree, because the folder is
  the board. Report the disagreement in one line — `AUTH-002 sits in in-progress/, the roadmap
  says pending` — and change neither. Fixing it is the orchestrator's job, or the user's.
- **The ticket also wins on priority and on dependencies.** For every task you open a ticket for,
  compare its `Priority` and `Depends on` fields with the row's cells, and report a mismatch in one
  line — `AUTH-002 is Critical in its ticket, High on the roadmap` — then use the **ticket's**
  values when you say what to start first. Say nothing about the priority of a task whose ticket
  you did not open: a waiting task needs its row and nothing more, and an unread ticket is not
  evidence of anything.
- **To judge the whole file instead of the rows you read**, run
  `${CLAUDE_PLUGIN_ROOT}/scripts/build-roadmap.py --check --project <project>`. It writes
  nothing, which is why this read-only command may run it, and it prints exactly which rows differ
  from the tickets. Report its findings in one or two lines and name `/setup` as what rebuilds the
  file. Skip it when `python3` is missing, and say so once.
- **A row whose ticket sits in `done/` should not be there.** Report it in one line — `AUTH-001
  is done, but the roadmap still lists it` — leave it out of every bucket, and say that the
  command that finished it was meant to delete the row.
- **A blocked task is in flight, not waiting.** Somebody started it and hit something. Say what
  the ticket gives as the blocker, in its own words.
- **An in-flight task assigned to `user` is waiting on a person** — an orchestrator escalated it
  and stopped. Say so in the lead line: it is the one thing in this report that needs somebody to
  act rather than to start something new. An in-flight task assigned to an agent stopped
  mid-pipeline instead, so name the agent and the last worklog entry, and say `/orchestrate`
  continues it.
- A task with no ticket file is still a task. Report it from its roadmap row.

## 3. Report

Lead with the answer — how many tasks are ready, and which one to start. Then the detail.

```markdown
## What's next

**Ready to start: N.** [Recommended task ID and title], first in roadmap order.
[One line when something needs attention: work already in flight, a blocked task, or a
disagreement between the roadmap and the ticket folders.]

### In flight (N)
- **[ID] — [Title]** · [status] · with [assignee] · ticket in `[folder]/`
  [What it delivers, one line. For a blocked task, the blocker in the ticket's own words.]
  Last worklog entry: [date] — [agent] · [stage] — [the one line that matters]

### Ready to start (N)
- **[ID] — [Title]** · [epic name] · [Priority] ← start here
  [What it delivers, one line.]
  Acceptance: [the criteria, short]
- **[ID] — [Title]** · [epic name] · [Priority]
  …

### Waiting (N)
- **[ID] — [Title]** — waits on [blocking IDs and their status]

### Progress
[N] tasks left across [K] epics; [M] tickets in `done/`. [Per-epic counts of what is left, when
there is more than one epic.]
```

Rules for the report:

- **Roadmap order throughout** — top to bottom, epic by epic. `ticket-board` keeps each epic's
  table sorted by priority, with a `Depends on` cell overriding priority, so roadmap order already
  **is** priority order. The first ready task carries `← start here`, because it is the
  highest-priority one that is actually ready.
- **Drop any empty section.** No "In flight (0)".
- **Ready is the section that matters.** Give each ready task its acceptance criteria; give the
  others one line.
- **Cap each list at 7.** Say how many more there are, and let the user ask.
- **Name every ID exactly** as the roadmap writes it. Cite a ticket by file name, never by path.
- **Never invent a task, a dependency, or a status.** When a roadmap row is ambiguous, say what is
  ambiguous about it.
- **Quote the worklog, never summarise it into something it does not say.** Drop the worklog line
  for a task that has no worklog, and say `unassigned` where a ticket carries no assignee.

## 4. Offer the next step

End with one line, matching what you found:

- **Something is ready** → `/orchestrate` to build it with the full pipeline,
  `/orchestrate-quick <ID>` when the task is already well understood, or `/run-roadmap` when nobody
  is going to be in the room and the `cto` agent should decide instead.
- **Something in flight is assigned to `user`** → name it first, whatever else is ready: an
  escalated task is waiting on a decision only a person can make. Say what its last worklog entry
  gives as the reason, and that `/orchestrate` continues it once that is settled.
- **Nothing is ready and something is in flight** → name the in-flight task and say that
  `/orchestrate` continues from where it stopped.
- **Nothing is ready and nothing is in flight** → every pending task waits on something that is
  not done. Name the one dependency that unblocks the most tasks, and say `/plan <request>` adds
  new work.
- **The roadmap has no task at all** → every task that was on it is done, and it holds nothing
  left to build. Name `/plan <request>`.

Offer nothing else, and run nothing yourself.
