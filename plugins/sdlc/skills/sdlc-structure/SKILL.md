---
name: sdlc-structure
description: "The structure this plugin creates and works in — the framework root and the files it holds (the `sdlc.json` registry, the glossary, `features/`, the `work/` folder and its buckets, `projects/`), the project folder and its project note, every kind of document and where each one sits, which document owns each fact and which way links point, the work root, the `.sdlc.json` pointer file, and the Obsidian-vault conventions (folder naming, frontmatter properties, wikilinks). INVOKE THIS SKILL before you read, create, move, or update a project note, a PRD, a product note, the glossary, a feature, a design doc, a diagram, a roadmap, a ticket, a worklog, or the business plan, before you resolve any path in the framework root or a work root, and before you run any command against a repository that is not the working directory. Enforces one resolution order for every command and agent, one owner per fact, one registry per framework root, and one document shape everywhere."
---

# sdlc-structure skill

Every document this plugin reads or writes sits under one **framework root**: the folder a session
starts in. Every line of code it writes sits in a **work root**: one code repository. A framework
root holds one or more **projects**, and a project is built in one or more work roots. This skill
holds the shape of both, and how to get from one to the other.

**This skill is the one place the structure is defined.** Every other skill, command, and agent
names a document by what it is — the PRD, the roadmap, a ticket — and points here for where it
sits.

The rules sit in the reference files below. This file says which one to read for the job in hand.

## Read before you start

**Resolve the framework root and the project first, once per run, before you read any document.**
Read [the framework root and the registry](references/roots.md) and follow its resolution order.
Every later path in the run resolves against what it gives you.

## Then read what the job needs

| The job | Read |
| --- | --- |
| Find a folder, or create or migrate the structure | [The layout](references/layout.md) |
| Find which kind of document holds a fact, its file name, its `type`, its states, or which skill governs it | [The document kinds](references/documents.md) |
| Write a fact, a link, or a `related:` property | [Ownership and links](references/ownership.md) |
| Write any document's properties or links, or move a ticket or a worklog | [Properties, links, and the vault shape](references/destinations.md) |
| Pick the repository a ticket is built in, or run a command in a repository that is not the working directory | [The work root](references/work-root.md) |

## The rules that hold everywhere

- **One fact, one owner.** Every other document links the owner instead of copying the fact.
- **A link points from the detailed document to the broader one**, never back. A ticket cites its
  feature, and a feature never cites a ticket.
- **The record wins over the summary.** A ticket outranks its roadmap row. Its `status` outranks
  the bucket it sits in. The code outranks a feature's status.
- **A document's `type` property is what makes it that kind of document.** A file with the right
  name and another `type`, or the right `type` in the wrong place, is not one.
- **Every term is defined once, in the framework root's `glossary.md`.** A document links the
  entry at the term's first use instead of defining it again.
- **Only the setup entry point moves the structure, or writes the pointer file or the registry.**
- **A ticket names its repositories by registry code**, in `repositories`. When the field is empty,
  the run has the `repo-resolver` agent fill it before the ticket starts.

## Where the rest lives

This skill holds where a document sits and how its properties and links are written. What goes
inside each document belongs to its own skill:

| Skill | Holds |
| --- | --- |
| `product-intent` | The goal, non-goal, persona, problem, and success metric notes |
| `prd` | The PRD |
| `glossary` | The terms, and the link a document writes to one |
| `feature` | The feature folder, its feature note, and its code |
| `design-doc` | The design doc |
| `diagrams` | The drawing, and how a document references it |
| `ticket-board` | The work folder, the ticket, its claim, the roadmap, the worklog, and the status transitions |
| `business-plan` | The business plan and the competitor notes |
