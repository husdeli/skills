---
type: design
subject: work
updated: 2026-10-09
tags:
  - sdlc/design
related:
  - "[[SDLC-framework.design]]"
  - "[[feature.design]]"
---
# Work

This doc defines the structure of the [[glossary#Work folder|work folder]]: the buckets inside it, the [[glossary#Ticket|tickets]] each bucket holds, and how a ticket moves between them.

## 1. Structure

```
work/
├── backlog/                             tickets no one has started
│   └── <CODE>-<NNN>-<slug>.md           one ticket
├── in-progress/                         tickets being built
│   ├── <CODE>-<NNN>-<slug>.md
│   └── <CODE>-<NNN>-<slug>.worklog.md   optional; the ticket's worklog
└── done/                                tickets that are finished
    ├── <CODE>-<NNN>-<slug>.md
    └── <CODE>-<NNN>-<slug>.worklog.md
```

| Path                    | Responsible for                                                      | Never holds                                                    |
| ----------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------- |
| `work/`                 | The three [[glossary#Bucket\|buckets]], and nothing else             | A ticket outside a bucket, a feature, a design doc, or a roadmap |
| `work/backlog/`         | Every ticket that is planned and not started                         | A worklog, or a subfolder                                      |
| `work/in-progress/`     | Every ticket being built, with its worklog                           | A subfolder                                                    |
| `work/done/`            | Every finished ticket, with its worklog                              | A subfolder                                                    |

**A ticket carries a `status` property, and its bucket follows from that status.** Each bucket holds one or more statuses; see 2. States.

**A ticket is named `<CODE>-<NNN>-<slug>.md`**: `CHECKOUT-001-saved-card.md`.

- **`<CODE>` is the `code` of the feature the ticket delivers**, from its [[feature.design#2. The feature note|feature note]]. A ticket whose code no feature carries is not a valid ticket.
- **`<NNN>` is three digits, and restarts at `001` in each [[glossary#Epic|epic]].** Two features planned on separate branches write into separate number spaces, so neither overwrites the other on merge.
- **`<slug>` is kebab-case**, a few words on what the ticket delivers.

**A [[glossary#Worklog|worklog]] sits beside its ticket** and shares its name, with `.worklog.md` in place of `.md`. A ticket in `backlog/` has no worklog, because nothing has been decided while building it yet.

## 2. States

The ticket's `status` property, and the bucket each status puts it in:

| Status        | Bucket         | Meaning                                                           |
| ------------- | -------------- | ----------------------------------------------------------------- |
| `backlog`     | `backlog/`     | The ticket is planned, and no work has started                    |
| `in progress` | `in-progress/` | The ticket is being built                                         |
| `blocked`     | `in-progress/` | The ticket cannot move forward                                    |
| `review`      | `in-progress/` | The work is built and waits for a review                          |
| `done`        | `done/`        | The ticket is finished                                            |

**What blocks a ticket is its `blocked_by` property**, kept apart from the status:

```yaml
status: blocked
blocked_by:
  - CHECKOUT-002
  - Payment provider has not issued sandbox keys
```

- **Each entry is a ticket ID or one line naming an outside cause.**
- **`blocked_by` is required while the status is `blocked`, and absent otherwise.** The step that moves a ticket out of `blocked` removes it.

The transitions:

| From          | To                                    |
| ------------- | ------------------------------------- |
| `backlog`     | `in progress`                         |
| `in progress` | `blocked`, `review`, or `backlog` when work on it stops |
| `blocked`     | `in progress`, or `backlog` when work on it stops |
| `review`      | `done`, or `in progress` when the review asks for changes |
| `done`        | Nothing; `done` is final              |

## 3. Behavior

- **A ticket sits in exactly one bucket, and the bucket always matches its status.** A status change that crosses buckets moves the file in the same step that rewrites the status. A change inside `in-progress/` — to `blocked`, to `review`, or back — rewrites the status and leaves the file where it is.
- **When the status and the bucket disagree, the status wins.** The file moves to the bucket its status names; the status is never rewritten to match the folder.
- **A ticket's worklog moves with it**, in the same step.
- **A ticket is found by its ID, never by a stored path.** Its path changes as it moves, so a command searches all three buckets for `<CODE>-<NNN>-*.md`, and a document cites the ticket by file name.
- **The next number in an epic is read from all three buckets.** `done/` counts, because a finished ticket keeps its number. A number is never reused, and a ticket that exists is never renumbered.
- **Finished work that needs more work gets a new ticket.** A `done` ticket never changes status; the new ticket names the change.

## 4. Variation and limits

- **An empty bucket may be absent.** A command creates a bucket the first time a ticket moves into it.
- **A framework root with no tickets has no `work/` folder**, or an empty one.
