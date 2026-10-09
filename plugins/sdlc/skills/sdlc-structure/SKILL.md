---
name: sdlc-structure
description: "The structure this plugin creates and works in — the project and its folders, every kind of document in it and where each one sits, which document owns each fact and which way links point, the work root, the `sdlc.json` registry that names every repository a product is built in, the `.sdlc.json` pointer file, and the Obsidian-vault conventions (folder naming, frontmatter properties, wikilinks). INVOKE THIS SKILL before you read, create, move, or update a PRD, a product note, a glossary, a feature, a design doc, a diagram, a roadmap, a ticket, a worklog, or the business plan, before you resolve any path in the project or a work root, and before you run any command against a repository that is not the working directory. Enforces one resolution order for every command and agent, one owner per fact, one registry per product, and one document shape per destination."
---

# sdlc-structure skill

Every document this plugin reads or writes belongs to one **project**. Every line of code it
writes sits in a **work root**: one code repository. A project has one or more work roots. This
skill holds the shape of both, and how to get from one to the other.

**This skill is the one place the structure is defined.** Every other skill, command, and agent
names a document by what it is — the PRD, the roadmap, a ticket — and points here for where it
sits. The final structure is still being designed in `designs/SDLC-framework.design.md`; until it
settles, the reference files below hold the rules in force.

The rules sit in the reference files below. This file says which one to read for the job in hand.

## Read before you start

**Resolve the project first, once per run, before you read any document.** Read
[the project and the registry](references/roots.md) and follow its resolution order. Every later
path in the run resolves against what it gives you.

## Then read what the job needs

| The job | Read |
| --- | --- |
| Find a folder, or create or migrate the structure | [The layout](references/layout.md) |
| Find which kind of document holds a fact, its file name, its states, or which skill governs it | [The document kinds](references/documents.md) |
| Write a fact, a link, or a `related:` property | [Ownership and links](references/ownership.md) |
| Write any document, or move a ticket or a worklog | [Destinations and the vault shape](references/destinations.md) |
| Pick the repository a task is built in, or run a command in a repository that is not the working directory | [The work root](references/work-root.md) |

## The rules that hold everywhere

- **One fact, one owner.** Every other document links the owner instead of copying the fact.
- **A link points from the detailed document to the broader one**, never back. A ticket cites its
  feature, and a feature never cites a ticket.
- **The record wins over the summary.** A ticket outranks its roadmap row. The code outranks a
  feature's status.
- **The structure is the same in every destination.** Only how fields and links are written
  changes, and only in a vault.
- **Only the setup entry point moves the project, or writes the pointer file or the registry.**
- **A ticket never names its repository.** The run resolves the work root when it picks the task
  and records it in the worklog.

## Where the rest lives

This skill holds where a document sits and how it is shaped by its destination. What goes inside
each document belongs to its own skill:

| Skill | Holds |
| --- | --- |
| `product-intent` | The goal, non-goal, persona, problem, and success metric notes |
| `prd` | The PRD |
| `glossary` | The terms, and the link a document writes to one |
| `feature` | The feature folder, its index note, and its code |
| `design-doc` | The design doc |
| `diagrams` | The drawing, and how a document references it |
| `ticket-board` | The roadmap, the ticket, the assignee, the worklog, and the status transitions |
| `business-plan` | The business plan and the competitor notes |
