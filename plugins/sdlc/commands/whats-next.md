---
description: Show what is actionable on the roadmap right now — what is in flight, what is ready to start, and what is blocked and by what.
argument-hint: [epic code to narrow to, or a roadmap path]
---

# What's Next

Answer one question about this project: **what can be worked on right now?** Read the roadmap and
the tickets, sort every task by what stands between it and being started, and report it. You
write nothing here.

Filter (if provided): $ARGUMENTS

Load the **`clean-writing`** skill (namespaced `sdlc:clean-writing`) before you report. This is a
status answer a person reads in one pass.

**Where the documents live.** They sit in the **docs root**: `roadmap.md`, and
`tickets/<status>/<ID>-<slug>.md`, where `<status>` is `todo`, `in-progress`, or `done`.
**Resolve the docs root first**: a `.sdlc.json` file at the project root names it in its `root`
field — that is how a project keeps its documents in an Obsidian vault — and otherwise it is
`.sdlc/` at the project root. Every `.sdlc/…` path below means `<docs root>/…`.

**This command is read-only.** Do not write a file, do not move a ticket, do not change a status,
and do not start a task. It reports what is there and stops. Reading the roadmap wrong is the one
mistake this command can make, so read the files rather than answering from memory.

## 1. Read the roadmap and the tickets

- **The roadmap** is the docs root's `roadmap.md`, unless `$ARGUMENTS` gives a path. When neither
  exists, look for a roadmap at the project root. With no roadmap anywhere, say so and name
  `/scaffold` as the way to create the structure, then stop.
- Read **every** `## <CODE> — <epic name>` section, not just the first. A dependency may name a
  task in another epic.
- **The roadmap holds the work that is left.** A finished task is deleted from it, so every row
  is pending, in progress, or blocked, and the file is the backlog rather than a history. Read
  an epic's `**Note**:` line when it has one: it constrains every task in that epic.
- **List the ticket folders** — `.sdlc/tickets/todo/`, `in-progress/`, and `done/` — in one pass.
  The folder a ticket sits in is the board, and it tells you what is really in flight. `done/` is
  where the finished work is: count it, and read no file in it.
- **A row does not say what its task delivers — its ticket does.** Read the ticket of every task
  you are about to report as **in flight** or **ready**, and take the one-line description and
  the acceptance criteria from there. A waiting task needs its row and nothing more.
- An **older roadmap** may still carry rows marked completed and a `###` detail section per
  task. Read it as it is, take a description from the detail section when a task has no ticket,
  and say in one line that `/scaffold` cleans the file up.

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

Judging the buckets:

- **A `Depends on` cell of `—` is satisfied.** The cell lists outstanding blockers only.
- **An ID still in the cell is finished** when it is no longer a row in the roadmap, or when its
  ticket sits in `done/`. Nothing else counts: in progress does not satisfy a dependency.
- **The ticket folder wins over the roadmap row** when the two disagree, because the folder is
  the board. Report the disagreement in one line — `AUTH-002 sits in in-progress/, the roadmap
  says pending` — and change neither. Fixing it is the orchestrator's job, or the user's.
- **A row whose ticket sits in `done/` should not be there.** Report it in one line — `AUTH-001
  is done, but the roadmap still lists it` — leave it out of every bucket, and say that the
  command that finished it was meant to delete the row.
- **A blocked task is in flight, not waiting.** Somebody started it and hit something. Say what
  the ticket gives as the blocker, in its own words.
- A task with no ticket file is still a task. Report it from its roadmap row.

## 3. Report

Lead with the answer — how many tasks are ready, and which one to start. Then the detail.

```markdown
## What's next

**Ready to start: N.** [Recommended task ID and title], first in roadmap order.
[One line when something needs attention: work already in flight, a blocked task, or a
disagreement between the roadmap and the ticket folders.]

### In flight (N)
- **[ID] — [Title]** · [status] · ticket in `[folder]/`
  [What it delivers, one line. For a blocked task, the blocker in the ticket's own words.]

### Ready to start (N)
- **[ID] — [Title]** · [epic name] ← start here
  [What it delivers, one line.]
  Acceptance: [the criteria, short]
- **[ID] — [Title]** · [epic name]
  …

### Waiting (N)
- **[ID] — [Title]** — waits on [blocking IDs and their status]

### Progress
[N] tasks left across [K] epics; [M] tickets in `done/`. [Per-epic counts of what is left, when
there is more than one epic.]
```

Rules for the report:

- **Roadmap order throughout** — top to bottom, epic by epic. The first ready task carries
  `← start here`, because roadmap order is the default choice.
- **Drop any empty section.** No "In flight (0)".
- **Ready is the section that matters.** Give each ready task its acceptance criteria; give the
  others one line.
- **Cap each list at 7.** Say how many more there are, and let the user ask.
- **Name every ID exactly** as the roadmap writes it. Cite a ticket by file name, never by path.
- **Never invent a task, a dependency, or a status.** When a roadmap row is ambiguous, say what is
  ambiguous about it.

## 4. Offer the next step

End with one line, matching what you found:

- **Something is ready** → `/orchestrate` to build it with the full pipeline, or
  `/orchestrate-quick <ID>` when the task is already well understood.
- **Nothing is ready and something is in flight** → name the in-flight task and say that
  `/orchestrate` continues from where it stopped.
- **Nothing is ready and nothing is in flight** → every pending task waits on something that is
  not done. Name the one dependency that unblocks the most tasks, and say `/plan <request>` adds
  new work.
- **The roadmap has no task at all** → every task that was on it is done, and it holds nothing
  left to build. Name `/plan <request>`.

Offer nothing else, and run nothing yourself.
