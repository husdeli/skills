---
type: design
subject: feature
updated: 2026-10-20
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
├── <subject>.design.md          optional; zero or more design docs
└── notes/                       optional; <slug>.note.md, one per action a person must take
```

| Path                                       | Responsible for                                                                                                                 | Never holds                                                     |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| `<feature-name>/`                          | The feature note, every [[glossary#Design doc\|design doc]] that belongs to this feature alone, and its `notes/`                 | A diagram, a ticket, a worklog, or another feature's design doc |
| `<feature-name>/<feature-name>.feature.md` | Naming the feature, saying what a customer can do with it, carrying its code, projects, and status, and linking its design docs | How the feature works, a task, a price, or a repository path    |
| `<feature-name>/notes/<slug>.note.md`      | One [[glossary#Note\|note]]: an action a person must take outside the code for the feature to work                                 | A task an agent can do, a TODO, a recommendation, or a decision |

**`<feature-name>` is kebab-case, in the product's own words**: `checkout/`, `saved-searches/`, `team-invites/`. It is unique within the framework root, and the folder name and the feature note's name always match.

**The feature note is `<feature-name>.feature.md`.** The `.feature` suffix keeps its name unique in a vault, so `[[checkout.feature]]` never needs a path.

**A note is written by `scripts/create-note.py`, never by a model.** The coding agent reports it in its result, and the command that ran the agent passes it to the script: an [[glossary#Orchestrator|orchestrator]] when the ticket finishes, or `/code`. A person sets its `status` from `open` to `done` once the action is taken, and nobody deletes a note.

```yaml
---
type: note
feature: "[[checkout.feature]]"
ticket: "[[CHECKOUT-004-stripe-webhooks]]"
status: open
when: before-release
createdAt: 2026-10-15T11:39
createdBy: orchestrate-3
tags:
  - sdlc/note
  - human-required
---
# Allow Stripe's webhook IPs in the WAF rule set
```

- **`feature` links the feature whose folder holds the note**, and **`ticket` links the ticket whose run reported it**. A note no ticket reported carries no `ticket`.
- **`status` is `open` or `done`.** Only a person changes it.
- **`when` is `before-release`, `after-release`, or `anytime`.** `before-release` means production fails without the action. A note reported with no `when` is `anytime`.
- **`createdAt` is when the script wrote the note, and `createdBy` is the run that reported it**: `orchestrate-3`, `orchestrate-quick-2`, a roadmap run's name, `code`, or `review`.
- **`tags` holds `sdlc/note` and `human-required`**, so every action that waits on a person is one search.
- **The body is the title, then `## What to do` and `## Why`.**
- **The title names the file.** The script turns it into `<slug>.note.md`. A note whose file already exists is kept as it is, because the same title is the same need reported again.
- **A feature with no note has no `notes/` folder.** The script creates it with the first note.

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
- **`code` is the feature's [[glossary#Epic|epic]] code**: required, two to eight characters — uppercase letters and digits, starting with a letter, and unique within the framework root. It prefixes every ticket ID under the feature.
- **`projects` lists the projects the feature relates to**: required, at least one, each named by the `name` in its [[project-structure.design#2. The project note|project note]].
- **`goals` and `personas` link [[glossary#Product note|product notes]]**: the goals the feature advances and the personas it serves. The note links them and never restates them.
- **The paragraph says what a customer can do**, in one or two sentences. The PRD says why; the design docs say how.
- **The links point at the feature's design docs**, one line each. A feature with no design doc yet has no links.

## 3. States

The feature note's `status` property:

| Status        | Meaning                                                   |
| ------------- | --------------------------------------------------------- |
| `backlog`     | The feature is planned, and no work has started           |
| `in progress` | The feature is being built: part of it is in a work root, or one of its tickets has started |
| `done`        | A customer can use the whole feature in a work root today |

**A status is verified against the [[glossary#Work root|work root]], never assumed.** Before a command writes or trusts `done`, it reads the work roots for the routes, modules, or screens a customer would use, and checks the board second. A feature that is partly usable is `in progress`. When the evidence disagrees with the note, the command reports the disagreement and fixes the note in the same step.

**A feature note on an older shape** reads `Planned` as `backlog`, `In Progress` as `in progress`, and `Shipped` as `done`.

## 4. Behavior

- **`/feature` creates a feature in five steps:**
  1. It settles the name and the code from the product's own vocabulary: the PRD, the glossary, and the user's words.
  2. It lists `features/` and searches the framework root for the code. A feature that already exists is updated in place.
  3. It names every project the feature relates to.
  4. It cites the goal the feature advances and the personas it serves, from each project's `product/goals/` and `product/personas/`. When no goal fits, it says so before it creates the feature.
  5. It writes the folder and the feature note at `backlog`, and nothing else. `/design` writes a design doc, and `/plan` writes the tickets and opens the epic on each project's roadmap.
- **A feature is created before its first ticket.** Its code exists because the feature exists; a ticket never mints a code.
- **A feature exists once.** Its name and its code are each unique in the framework root, so a feature that already exists is updated in place, never created twice.
- **A feature note stays after the feature is `done`.** The [[glossary#Roadmap|roadmap]] drops the epic when its last ticket is done, but `features/` keeps the note, so `features/` lists everything the products do.
- **A list of features is a query over `features/`.** In a vault it is a Dataview query on `type: feature`, so a new feature appears in every list with no edit; it filters on `projects` to list one project's features. In a `repo` or `folder` destination it is a Markdown table with a relative link per feature, rewritten whenever a feature's status changes.

## 5. Variation and limits

- **A feature with no design doc is still a feature.** Its folder holds the feature note alone until someone specifies how it works.
- **A framework root with no features has an empty `features/` folder**, or none. Nothing links a feature that does not exist.
- **An older property is read and left alone.** `area`, `customer_facing`, `shipped`, `non_goals`, and `updated` stay as they are until a command rewrites the note.
- **The code never changes once the feature has a ticket.** The tickets, branches, and reviews cite the work by it. The `name` may change freely.
- **A feature is deleted only when the product stops doing the thing**, and its design docs are deleted with it.
