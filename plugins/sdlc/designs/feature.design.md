---
type: design
subject: feature
updated: 2026-10-09
tags:
  - sdlc/design
related:
  - "[[SDLC-framework.design]]"
  - "[[project-structure.design]]"
---
# Feature

This doc defines the structure of one [[glossary#Feature|feature]] folder: the files inside it, and what each one is responsible for.

## 1. Structure

```
<feature-name>/
├── <feature-name>.feature.md    the feature note
└── <subject>.design.md          optional; zero or more design docs
```

| Path                                       | Responsible for                                                                                                                 | Never holds                                                     |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| `<feature-name>/`                          | The feature note, and every [[glossary#Design doc\|design doc]] that belongs to this feature alone                              | A diagram, a ticket, a worklog, or another feature's design doc |
| `<feature-name>/<feature-name>.feature.md` | Naming the feature, saying what a customer can do with it, carrying its code, projects, and status, and linking its design docs | How the feature works, a task, a price, or a repository path    |

**`<feature-name>` is kebab-case, in the product's own words**: `checkout/`, `saved-searches/`, `team-invites/`. It is unique within the framework root, and the folder name and the feature note's name always match.

**The feature note is `<feature-name>.feature.md`.** The `.feature` suffix keeps its name unique in a vault, so `[[checkout.feature]]` never needs a path.

**A design doc that every feature depends on stays in `designs/`.** Only a design doc that belongs to one feature sits in that feature's folder.

## 2. The feature note

The frontmatter `type` must be `feature`. That property is what marks the note as a feature note: a `<feature-name>.feature.md` with another `type` is not one, and a note with `type: feature` outside `features/<feature-name>/` is not one either.

```yaml
---
type: feature
name: Checkout
code: CHECKOUT
projects:
  - acme-billing
status: backlog
goals:
  - "[[self-hosted-first.goal]]"
personas:
  - "[[solo-operator.persona]]"
tags:
  - sdlc/feature
---
# Checkout

A customer pays for an order in one step, with a saved card or a new one.

- [[checkout.design]] — how an order is taken and paid
```

- **`name` is the feature's display name**: required, in the words a customer would use.
- **`code` is the feature's [[glossary#Epic|epic]] code**: required, two to eight uppercase letters, and unique within the framework root. It prefixes every ticket ID under the feature.
- **`projects` lists the projects the feature relates to**: required, at least one, each named by the `name` in its [[project-structure.design#2. The project note|project note]].
- **`goals` and `personas` link [[glossary#Product note|product notes]]**: the goals the feature advances and the personas it serves. The note links them and never restates them.
- **The paragraph says what a customer can do**, in one or two sentences. The PRD says why; the design docs say how.
- **The links point at the feature's design docs**, one line each. A feature with no design doc yet has no links.

## 3. States

The feature note's `status` property:

| Status        | Meaning                                                   |
| ------------- | --------------------------------------------------------- |
| `backlog`     | The feature is planned, and no work has started           |
| `in progress` | The feature is being built                                |
| `done`        | A customer can use the whole feature in a work root today |


## 4. Behavior

- **A feature is created before its first ticket.** Its code exists because the feature exists; a ticket never mints a code.
- **A feature exists once.** Its name and its code are each unique in the framework root, so a feature that already exists is updated in place, never created twice.
- **A feature note stays after the feature is `done`.** The [[glossary#Roadmap|roadmap]] drops the epic when its last ticket is done, but `features/` keeps the note, so `features/` lists everything the products do.

## 5. Variation and limits

- **A feature with no design doc is still a feature.** Its folder holds the feature note alone until someone specifies how it works.
- **A framework root with no features has an empty `features/` folder**, or none. Nothing links a feature that does not exist.
- **The code never changes once the feature has a ticket.** The tickets, branches, and reviews cite the work by it. The `name` may change freely.
- **A feature is deleted only when the product stops doing the thing**, and its design docs are deleted with it.
