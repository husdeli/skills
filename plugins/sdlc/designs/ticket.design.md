---
type: design
subject: ticket
updated: 2026-10-20
tags:
  - sdlc/design
related:
  - "[[SDLC-framework.design]]"
  - "[[work.design]]"
  - "[[feature.design]]"
---
# Ticket

This doc defines one [[glossary#Ticket|ticket]]: its name, the properties it carries, its status and what blocks it, how its status changes, what its body holds, and the roadmap that lists it. Where a ticket sits, and how it moves between folders, is defined in [[work.design|Work]].

## 1. Name

**A ticket is named `<CODE>-<NNN>-<slug>.md`**: `CHECKOUT-001-saved-card.md`. Its ID is `<CODE>-<NNN>`: `CHECKOUT-001`.

- **`<CODE>` is the `code` of the feature the ticket delivers**, from its [[feature.design#2. The feature note|feature note]]. A ticket whose code no feature carries is valid only on a board that keeps a project-wide scheme, such as `SW-001`: that board continues its scheme until setup migrates it, and never rewrites an ID on its own.
- **`<NNN>` is the ticket's number in its [[glossary#Epic|epic]], and restarts at `001` in each one.** It is written with three digits, zero-padded, and goes on to four past `999`; a number of one to four digits on an existing ticket is read as it is and never renumbered. Two features planned on separate branches write into separate number spaces, so neither overwrites the other on merge.
- **`<slug>` is kebab-case**, a few words on what the ticket delivers.

## 2. Properties

```yaml
---
feature: "[[checkout.feature]]"
status: in progress
priority: High
repositories:
  - api
depends_on:
  - CHECKOUT-001
assigned: coding-1
claimed: orchestrate-1
createdAt: 2026-10-07T09:15
updatedAt: 2026-10-09T14:32
timing: 47
tokens: 1284000
cost: 4.12
related:
  - "[[checkout.design]]"
---
```

- **`feature` links the [[feature.design#2. The feature note|feature note]] of the feature the ticket delivers**: required. That note's `code` is the `<CODE>` the ticket's name starts with; a ticket whose `feature` and name disagree is not a valid ticket.
- **`status` is where the work stands**: required; see 3. States.
- **`priority` is how urgent the ticket is**: required, one of `Critical`, `High`, `Medium`, or `Low`. It orders the [[glossary#Roadmap|roadmap]]; see 6. Roadmap. A ticket with no `priority` reads as `Medium`, and the value is written into the ticket the next time it changes.
- **`repositories` names the [[glossary#Work root|work roots]] the ticket is built in**, by their [[glossary#Registry|registry]] codes, never paths. Planning writes it when the evidence settles it; otherwise the run that picks the ticket has the `repo-resolver` agent fill it before the ticket starts, and every later run reads it. See [[workflow.design#3.1 Behavior|Workflow]].
- **`depends_on` lists every ticket this one cannot start without**, as bare IDs, and is `[]` when there are none. Planning writes it, and it is never pruned: what a ticket depended on stays a fact about it after the other ticket is `done`. It differs from `blocked_by`; see 3. States.
- **`assigned` names the agent that works on the ticket now, or is planned to**, as `<role>-<n>`: `coding-1`, `code-reviewer-1`. `<n>` is the number of the run the agent works for, so `assigned` names the run as well as the role. A session that does the work itself names its command the same way: `code-1`.
- **`claimed` names the [[glossary#Run|run]] that holds the ticket**, as `<command>-<n>`: `orchestrate-1` or `run-roadmap-3`. `<n>` is the lowest positive number no other claim on the board uses, and the run's agents carry the same number. It is a guardrail, not an assignment: a ticket can be claimed before anyone knows which agent will work on it. A [[glossary#Roadmap run|roadmap run]] claims every ticket of a feature's [[glossary#Dependency cluster|dependency cluster]] at once, so a ticket may carry a claim long before it is started; see [[workflow.design#4. Claims|Workflow]].
- **`createdAt` is when the ticket was created**: required. It is set once, in the step that creates the ticket, and never changes.
- **`updatedAt` is when the ticket last changed**: required. It equals `createdAt` on a new ticket, and every step that changes the ticket rewrites it.
- **`related` links the [[glossary#Design doc|design docs]] the ticket builds**, and nothing else. The feature and the dependencies each have their own property.

**A ticket carries no `type`, `id`, `epic`, or `tags`, and no repository path.** Its name says its ID and its epic, its [[glossary#Bucket|bucket]] makes it a ticket, and `repositories` names its work roots by registry code.

**Both times are local date and time, `YYYY-MM-DDTHH:mm`**, the form Obsidian reads as a date-and-time property.

**What implementing the ticket took is three optional properties:**

- **`timing` is how long agents spent implementing the ticket**, in whole minutes, summed over every agent.
- **`tokens` is how many tokens they spent**, input and output together.
- **`cost` is what those tokens cost**, in US dollars to two decimal places, at the price of the model that spent them.

A ticket no agent has worked on has none of the three.

**`assigned` follows the status:**

| Status        | `assigned`                                                   |
| ------------- | ------------------------------------------------------------ |
| `backlog`     | Optional; the agent planned to work on it, once that is known |
| `in progress` | Required; the agent working on it                            |
| `blocked`     | Optional; the agent that resumes it once it is unblocked     |
| `review`      | Optional; the agent that reviews it, once that is known      |
| `done`        | Absent                                                       |

**`claimed` does not follow the status.** It may be set at any status except `done`.

## 3. States

The ticket's `status` property:

| Status        | Meaning                                                           |
| ------------- | ----------------------------------------------------------------- |
| `backlog`     | The ticket is planned, and no work has started                    |
| `in progress` | The ticket is being built                                         |
| `blocked`     | The ticket cannot move forward                                    |
| `review`      | The work is built and waits for verification and a code review    |
| `done`        | The ticket is finished                                            |

**What blocks a ticket is its `blocked_by` property**, kept apart from the status:

```yaml
status: blocked
blocked_by:
  - CHECKOUT-002
  - Payment provider has not issued sandbox keys
```

- **Each entry is a ticket ID or one line naming an outside cause.**
- **`blocked_by` is required while the status is `blocked`, and absent otherwise.** The step that moves a ticket out of `blocked` removes it.
- **A person clears an outside cause by deleting its line.**
- **A blocked ticket is resumable when its `blocked_by` holds only IDs of `done` tickets, or nothing.**

**`depends_on` and `blocked_by` answer different questions.** `depends_on` is planned before work starts, and says what the ticket waits on before it can start. `blocked_by` is found during a run, and says what stopped a ticket that had started.

The transitions:

| From          | To                                    |
| ------------- | ------------------------------------- |
| `backlog`     | `in progress`                         |
| `in progress` | `blocked`, `review`, or `backlog` when work on it stops |
| `blocked`     | `in progress`, or `backlog` when work on it stops |
| `review`      | `done`, or `in progress` when the review asks for changes |
| `done`        | Nothing; `done` is final              |

- **A ticket is `done` only when verification passed and the code review approved.** A passing suite alone never finishes it.
- **Only a person returns a ticket to `backlog`**, when nobody should resume it yet. The step removes `assigned`, `claimed`, and `blocked_by`, and the ticket keeps its worklog; see [[work.design#1. Structure|Work]].

**A ticket is [[glossary#Ready|ready]] when it carries no [[glossary#Claim|claim]] and either:**

- its status is `backlog` and every ID in its `depends_on` names a `done` ticket; or
- its status is `blocked` and it is resumable.

A claimed ticket is never ready for another run. An ID in `depends_on` that no ticket carries is never satisfied, so the ticket stays not ready. Ready tickets are offered in roadmap order.

## 4. Behavior

- **A ticket is cited by its file name, never by a path.** Its path changes as its status changes; its name does not.
- **A number is never reused, and a ticket that exists is never renumbered.** A finished ticket keeps its number.
- **Finished work that needs more work gets a new ticket.** A `done` ticket never changes status; the new ticket names the change.

## 5. Body

**The body says what to build, never how.** It opens with the title `# [<CODE>-<NNN>] Title`, then holds these sections in order:

| Section              | Holds                                                                                       |
| -------------------- | ------------------------------------------------------------------------------------------- |
| Description          | What is needed and why, in two or three sentences                                            |
| Acceptance Criteria  | The observable outcomes, as a checklist                                                      |
| Decisions            | Each choice planning settled, with why it won. The run builds within them and never reopens them. Absent when planning settled nothing |
| Implementation Steps | The outcomes, in order: what has to happen, never how                                        |
| Technical Notes      | The data the ticket needs, and its architectural considerations                              |

- **A ticket has no testing section.** The test plan written during the run decides what is tested.
- **A ticket names no file path, module, or library**, except a library the person chose, recorded under Decisions.
- **A ticket has no Related section.** The `related` property carries the design docs.

## 6. Roadmap

**Each project keeps one roadmap** in its project folder, listing that project's open tickets and nothing else. It has one section per epic, with the feature's link and one sentence on what the epic delivers. Each section holds one row per ticket that is not `done`: its ID, task, priority, status, outstanding dependencies, and file name. A ticket whose feature names several projects has a row in each of their roadmaps.

**A row's status mirrors its ticket's status:**

| Ticket status          | Row status             |
| ---------------------- | ---------------------- |
| `backlog`              | ⬜ **Pending**         |
| `in progress`, `review` | 🚧 **In Progress**    |
| `blocked`              | 🚫 **Blocked**         |

There is no done marker, because a done ticket leaves the roadmap.

- **The ticket is the record, and the row reflects it.** `/plan` adds a row, at ⬜ **Pending**, in the step that writes the ticket. Every change to a ticket's status or priority rewrites its row in the same step. A row that disagrees with its ticket is corrected from the ticket, never the reverse.
- **Finishing a ticket deletes its row** from every roadmap that lists it, and removes its ID from every other row's dependencies. An epic's section is deleted with its last row. The roadmap never holds a finished row; `work/done/` is the record.
- **A row's dependencies are the outstanding part of the ticket's `depends_on`.** An ID leaves the row when its ticket is `done`, and `—` means the ticket can start.

**Reading a section top to bottom is reading the order to build in:**

1. A row never sorts above a ticket it still depends on.
2. A blocker carries the highest priority of any ticket waiting on it.
3. Everything else goes by priority, from `Critical` to `Low`, and a tie goes to the lower ticket number.

**`build-roadmap.py` rebuilds every table from the tickets**, or, with `--check`, reports what differs and writes nothing. It never invents a task, moves a ticket, deletes an epic's section, or marks a feature done.
