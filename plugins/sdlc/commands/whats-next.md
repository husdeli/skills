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

- **`sdlc-structure`** — where the framework root, the project, and the work roots are.
- **`ticket-board`** — the roadmap's shape, what a `Depends on` cell means, the status-to-bucket
  map, which tickets are ready, the `assigned`, `claimed`, and `blocked_by` properties, and the
  worklog. It is what you are reading; read it there rather than inferring it from the files.
- **`technical-writing`** — this is a status answer a person reads in one pass.

The roadmap is the project's `roadmap.md`. The tickets sit at the framework root, in
`work/backlog/`, `work/in-progress/`, and `work/done/`, each named `<CODE>-<NNN>-<slug>.md`, with a
worklog beside a ticket that work has started on.

**Say where the work happens.** The framework root's `sdlc.json` registry names every repository
the projects are built in. List the ones this project uses once, at the top of the report — the
code and the path per entry — and, for each ticket in flight, name the codes its `repositories`
property holds. That is what tells a reader which tree to open; the worklog's opening entry says
why. A ticket whose `repositories` is empty gets it filled when a run starts it. Say nothing about
a repository when there is no registry: the code is then wherever this session is standing.

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
- **List the three buckets** — `work/backlog/`, `work/in-progress/`, and `work/done/` — in one
  pass. A ticket of another project shares these buckets: count only the tickets whose IDs this
  project's roadmap lists, or whose feature names this project. `done/` is where the finished work
  is: count it, and read no file in it. On an older board, `tickets/todo/` reads as
  `work/backlog/`, as `sdlc-structure` says.
- **A row does not say what its task delivers — its ticket does.** Read the ticket of every task
  you are about to report as **in flight** or **ready**, and take the one-line description and
  the acceptance criteria from there. A waiting task needs its row and nothing more.
- **For an in-flight task, read two more things**: the ticket's `status`, `assigned`, `claimed`,
  and `blocked_by` properties, which say where it stands and who holds it right now, and the **last
  entry of its worklog**, which says what happened most recently. In flight is usually one or two
  tasks, so this costs two reads and it is the only way to answer "where did this stop?". A ticket
  with no `assigned` is unassigned; a ticket with no worklog was started by hand.
- **Read the `claimed` property of every ticket you are about to report as ready.** A claimed
  ticket is never ready: another run holds it, and a roadmap run claims a feature's whole cluster
  before it builds any of it.
- On an **older roadmap** — rows marked completed, a `###` detail section per task — read what is
  there, take a description from the detail section when a task has no ticket, and say in one line
  that `/setup` cleans the file up.

**When `$ARGUMENTS` names an epic code** (`AUTH`, `BILLING`), narrow every list below to that
epic, and say in one line that you narrowed it.

## 2. Sort every task

Put each task in exactly one bucket:

| Bucket | Test |
| --- | --- |
| **In flight** | Its status is `in progress` or `review`, or it is `blocked` and claimed |
| **Ready** | It is `backlog`, unclaimed, and every ID in its `Depends on` cell is finished — or it is `blocked`, unclaimed, and resumable: its `blocked_by` holds only finished IDs, or nothing |
| **Waiting** | It is `backlog` and claimed or waiting on an unfinished ID, or it is `blocked` on something a person or an unfinished ticket still owes |

Every row lands in one of the three. There is no done bucket, because a finished task is not in
the file.

Judging the buckets — `ticket-board` says when a `Depends on` cell counts as satisfied, and the
rest is this command's:

- **The ticket's `status` wins over the roadmap row and over the bucket the file sits in**,
  because the ticket is the record. Report each disagreement in one line — `AUTH-002 is in
  progress in its ticket, the roadmap says pending`, `AUTH-003 is done but sits in in-progress/` —
  and change neither. Fixing it is the orchestrator's job, or the user's.
- **The ticket also wins on priority and on dependencies.** For every task you open a ticket for,
  compare its `priority` and `depends_on` properties with the row's cells, and report a mismatch in one
  line — `AUTH-002 is Critical in its ticket, High on the roadmap` — then use the **ticket's**
  values when you say what to start first. Say nothing about the priority of a task whose ticket
  you did not open: a waiting task needs its row and nothing more, and an unread ticket is not
  evidence of anything.
- **To judge the whole file instead of the rows you read**, run
  `${CLAUDE_PLUGIN_ROOT}/scripts/build-roadmap.py --check --project <project>`. It writes
  nothing, which is why this read-only command may run it, and it prints exactly which rows differ
  from the tickets. Report its findings in one or two lines, and name the same script without
  `--check` as what rebuilds the file. Skip it when `python3` is missing, and say so once.
- **A row whose ticket is `done` should not be there.** Report it in one line — `AUTH-001
  is done, but the roadmap still lists it` — leave it out of every bucket, and say that the
  command that finished it was meant to delete the row.
- **A blocked task is in flight, not waiting.** Somebody started it and hit something. Quote its
  `blocked_by` entries in their own words.
  - **An entry that is not a ticket ID is waiting on a person** — a run escalated or aborted it,
    and the line names what a person must decide. Say so in the lead line: it is the one thing in
    this report that needs somebody to act rather than to start something new.
  - **A ticket whose `blocked_by` holds only IDs of `done` tickets, or nothing, is resumable**,
    and `/orchestrate` resumes it. One whose entries name unfinished tickets waits on them.
- **An `in progress` or `review` ticket with a claim is being built right now**, by the run its
  `claimed` names. Name that run and the agent in `assigned`. One with **no claim** was left by a
  run that died without exiting: say so, and that a person sets it to `blocked` or back to
  `backlog` before anything resumes it.
- A task with no ticket file is still a task. Report it from its roadmap row.

## 3. Report

Lead with the answer — how many tasks are ready, and which one to start. Then the detail.

```markdown
## What's next

**Ready to start: N.** [Recommended task ID and title], first in roadmap order.
[One line when something needs attention: work already in flight, a blocked task, or a
disagreement between the roadmap and the ticket folders.]

### In flight (N)
- **[ID] — [Title]** · [status] · [assigned] for [claimed] · in [repository codes]
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
  for a task that has no worklog, and say `unassigned` where a ticket carries no `assigned`.

## 4. Offer the next step

End with one line, matching what you found:

- **Something is ready** → `/orchestrate` to build it with the full pipeline,
  `/orchestrate-quick <ID>` when the task is already well understood, or `/run-roadmap` when nobody
  is going to be in the room and the `cto` agent should decide instead.
- **A blocked ticket waits on a person** → name it first, whatever else is ready: an escalated
  task is waiting on a decision only a person can make. Quote its `blocked_by` line, and say that
  deleting that line once it is settled makes the ticket resumable, and `/orchestrate` resumes it.
- **Nothing is ready and something is in flight** → name the in-flight task and say that
  `/orchestrate` continues from where it stopped.
- **Nothing is ready and nothing is in flight** → every pending task waits on something that is
  not done. Name the one dependency that unblocks the most tasks, and say `/plan <request>` adds
  new work.
- **The roadmap has no task at all** → every task that was on it is done, and it holds nothing
  left to build. Name `/plan <request>`.

Offer nothing else, and run nothing yourself.
