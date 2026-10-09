---
type: design
subject: work
updated: 2026-10-09
tags:
  - sdlc/design
related:
  - "[[SDLC-framework.design]]"
  - "[[feature.design]]"
  - "[[ticket.design]]"
  - "[[workflow.design]]"
---
# Work

This doc defines the structure of the [[glossary#Work folder|work folder]]: the buckets inside it, the [[glossary#Ticket|tickets]] each bucket holds, and how a ticket moves between them. The ticket itself is defined in [[ticket.design|Ticket]].

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

**A ticket carries a `status` property, and its bucket follows from that status.** Each bucket holds one or more statuses; see 2. Buckets.

**A [[glossary#Worklog|worklog]] sits beside its ticket** and shares its name, with `.worklog.md` in place of `.md`. A ticket in `backlog/` has no worklog, because nothing has been decided while building it yet.

## 2. Buckets

The bucket each [[ticket.design#3. States|status]] puts a ticket in:

| Status        | Bucket         |
| ------------- | -------------- |
| `backlog`     | `backlog/`     |
| `in progress` | `in-progress/` |
| `blocked`     | `in-progress/` |
| `review`      | `in-progress/` |
| `done`        | `done/`        |

## 3. Behavior

- **A ticket sits in exactly one bucket, and the bucket always matches its status.** A status change that crosses buckets moves the file in the same step that rewrites the status. A change inside `in-progress/` — to `blocked`, to `review`, or back — rewrites the status and leaves the file where it is.
- **When the status and the bucket disagree, the status wins.** The file moves to the bucket its status names; the status is never rewritten to match the folder.
- **A ticket's worklog moves with it**, in the same step.
- **A ticket is found by its ID, never by a stored path.** A command searches all three buckets for `<CODE>-<NNN>-*.md`.
- **The next number in an epic is read from all three buckets.** `done/` counts, because a finished ticket keeps its number.

## 4. Variation and limits

- **An empty bucket may be absent.** A command creates a bucket the first time a ticket moves into it.
- **A framework root with no tickets has no `work/` folder**, or an empty one.
