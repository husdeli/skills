---
name: feature
description: "Rules for the feature — the entity that names one thing a customer can do, kept as a folder under the framework root's features/<feature-name>/ with its feature note, the design docs it owns, and the notes a person must act on, carrying the epic code that numbers its tickets and the projects it relates to. INVOKE THIS SKILL before you create, rename, read, or retire a feature, before you write a design doc that belongs to one, before you open an epic on a roadmap, and before you list what a product can do. Enforces one feature per folder, one feature note per feature, a code that is the epic code, at least one project per feature, and a status verified against the code."
---

# feature skill

A **feature** is one thing a customer can do. It is the unit the product is described in, the work
is grouped by, and the plan is sold on, so it has one home and one record:

```
<framework root>/features/checkout/
├── checkout.feature.md        the feature note
├── checkout.design.md         how it works
├── payment-retry.design.md    a second subject inside the same feature
└── notes/                     actions a person must take, one <slug>.note.md each
```

**The `sdlc-structure` skill resolves the framework root** — load it before you resolve any path
below. It also holds how properties and links are written in each destination.

Three skills hold what sits around a feature: the **`design-doc`** skill for the design docs in its
folder, the **`ticket-board`** skill for the epic and the tickets its code numbers, and the
**`glossary`** skill for every term the feature names.

## One feature, one folder, one note

| Path | Responsible for | Never holds |
| --- | --- | --- |
| `features/<feature-name>/` | The feature note, every design doc that belongs to this feature alone, and its `notes/` | A diagram, a ticket, a worklog, or another feature's design doc |
| `features/<feature-name>/<feature-name>.feature.md` | Naming the feature, saying what a customer can do with it, carrying its code, projects, and status, and linking its design docs | How the feature works, a task, a price, or a repository path |
| `features/<feature-name>/notes/<slug>.note.md` | One action a person must take outside the code for the feature to work — a cloud rule, a secret, a third-party setting | A task an agent can do, a TODO in the code, a recommendation, or a decision |

- **`features/` sits at the framework root, not in a project.** A feature names the projects it
  relates to, and one feature may serve several.
- **`<feature-name>` is kebab-case, in the product's own words**: `checkout/`, `saved-searches/`,
  `team-invites/`. It is unique within the framework root, and the folder name and the feature
  note's name always match.
- **The feature note is `<feature-name>.feature.md`.** The `.feature` suffix keeps its name unique
  in a vault, so `[[checkout.feature]]` never needs a path.
- **A design doc that every feature depends on stays in `designs/`.** Only a design doc that
  belongs to one feature sits in that feature's folder; the `design-doc` skill holds which is
  which.
- **A feature with no design doc is still a feature.** Its folder holds the feature note alone
  until someone specifies how it works.

## The feature note

**The frontmatter `type` must be `feature`.** That property is what marks the note as a feature
note: a `<feature-name>.feature.md` with another `type` is not one, and a note with `type: feature`
outside `features/<feature-name>/` is not one either.

```markdown
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
- [[payment-retry.design]] — what happens when a payment fails
```

| Property | What it holds |
| --- | --- |
| `type` | `feature`, always. |
| `name` | Required. The feature's display name, in the words a customer would use. |
| `code` | Required. The epic code: two to eight characters — uppercase letters and digits, starting with a letter, unique within the framework root. It prefixes every ticket ID under the feature. |
| `projects` | Required, at least one. The projects the feature relates to, each by the `name` in its project note. |
| `status` | `backlog`, `in progress`, or `done`. See [Status is verified, never assumed](#status-is-verified-never-assumed). |
| `goals` | Links to the goal notes the feature advances. |
| `personas` | Links to the persona notes the feature serves. |
| `tags` | `sdlc/feature`. |

`goals` and `personas` link product notes the **`product-intent`** skill governs. The note links them
and never restates them; load that skill before you set them.

**The body is short.** One or two sentences saying what a customer can do, then one line per design
doc. A feature with no design doc yet has no links. The PRD says why; the design docs say how.

**The sentences say one thing no other document can**: what a customer can do, in the words they
would use. Two tests before you keep a sentence. **Could it be pasted into the PRD without looking
out of place?** Then it is the PRD's — delete it here. **Does it say how something works?** Then it
is the design doc's — delete it here.

## The notes folder

A **note** is one action a person has to take outside the code — a WAF rule in a cloud console, a
secret in a vault, a DNS record, a webhook in a third-party dashboard — that the feature's code
depends on. The coding agent reports it in its result block; the orchestrator, `/code`, or `/review` hands it to
`scripts/create-note.py`, and the script writes the file. **No model writes a note file**, so every
note has the same name, properties, and body.

```markdown
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

# Allow Stripe's webhook IPs in the AWS WAF rule set

## What to do

In AWS WAF, add the ranges from Stripe's published webhook IP list to the `api-allow` IP set, then
send a test webhook from the Stripe dashboard and confirm it returns 200.

## Why

The new `/webhooks/stripe` route sits behind WAF; without the rule every webhook gets a 403.
```

| Property | What it holds |
| --- | --- |
| `type` | `note`, always. |
| `feature` | The feature whose folder holds it. |
| `ticket` | The ticket whose run reported it. Left out when no ticket did. |
| `status` | `open` until a person has done it, then `done`. Only a person changes it. |
| `when` | `before-release` — production fails without it; `after-release` — it follows a release; `anytime`. |
| `createdAt` | When the script wrote it. |
| `createdBy` | The run that reported it: `orchestrate-3`, `orchestrate-quick-2`, a roadmap run's name, `code`, or `review`. |
| `tags` | `sdlc/note` and `human-required`, so every action that waits on a person is one search. |

- **The title names the file.** The script turns it into `<slug>.note.md`, and a note whose file
  already exists is kept as it is — the same title is the same need, reported again.
- **A person closes a note** by setting `status: done`. Nobody deletes one: it records what the
  feature needed beyond its code.
- **A feature that has no note has no `notes/` folder.** The script creates it with the first one.

## The code is the epic code

One code, one feature, one epic. The `ticket-board` skill holds how the code numbers a ticket and
how a roadmap groups by it.

- **The code is unique in the framework root**, and it never means two things.
- **A feature is created before its first ticket.** Its code exists because the feature exists; a
  ticket never mints a code.
- **The code never changes once the feature has a ticket.** The tickets, branches, and reviews cite
  the work by it. The `name` may change freely.

## Status is verified, never assumed

| `status` | What is true |
| --- | --- |
| `backlog` | The feature is planned, and no work has started |
| `in progress` | The feature is being built: part of it is in a work root, or one of its tickets has started |
| `done` | A customer can use the whole feature in a work root today |

**A feature is `done` only when a work root holds it.** The roadmap can lag the code, and the code
can lag the roadmap. Before you write or trust `done`, read the work roots for the feature: the
routes, the modules, or the screens a customer would use. Check the board second.

A feature that is partly usable is `in progress`, not `done`. When the evidence disagrees with the
note, report the disagreement and fix the note in the same step — never quote a status you did not
check.

**A feature note on an older shape** reads `Planned` as `backlog`, `In Progress` as `in progress`,
and `Shipped` as `done`. Properties the current note does not carry — `area`, `customer_facing`,
`shipped`, `non_goals`, `updated` — are read and left alone until a command rewrites the note.

## The roadmap shrinks; `features/` does not

A roadmap holds the work that is left, so an epic's section is deleted when its last ticket is done.
**The feature note stays**, at `status: done`, so `features/` lists everything the products do.

That is the division: `features/` says what the products *are*, each project's `roadmap.md` says what
is *left*, and `work/done/` says what *happened*. A feature is deleted only when the product stops
doing the thing — and then its design docs go with it.

## Reference a feature

Point at the feature note. Never restate what it says.

| Where | The reference |
| --- | --- |
| A vault document | `[[checkout.feature]]`, or `[[checkout.feature\|Checkout]]` |
| A `repo` or `folder` document | The path relative to the document, such as `../../features/checkout/checkout.feature.md` from a ticket |
| A roadmap epic section | `**Feature**: [[checkout.feature]]` under the epic's sentence |
| A ticket | Its `feature` property |
| A design doc's `related:` property | The feature it belongs to, plus its sibling designs |

Prose a person reads outside the framework root carries no link — a chat reply, a commit message, a
review verdict. Name the feature there, plainly.

## List the features

In a vault, a list of features is a Dataview query, so a new feature appears wherever features are
listed with no edit to the listing document:

````markdown
```dataview
TABLE WITHOUT ID
  file.link AS "Feature",
  code AS "Code",
  status AS "Status"
FROM "<framework root, relative to the vault root>/features"
WHERE type = "feature" AND contains(projects, "acme-billing")
SORT status ASC, name ASC
```
````

Drop the `contains(projects, …)` clause to list every feature in the framework root. The `FROM` path
is relative to the vault root, the folder that holds `.obsidian/`; when the framework root is the
vault root, the path is `features`.

The query needs the Dataview community plugin. Check the vault's enabled community plugins for
`dataview`; when it is missing, keep the query and tell the user to install and enable Dataview.

**In a `repo` or `folder` destination there is no Dataview.** Write the same columns as a Markdown
table with a relative link per feature, and rewrite it whenever a feature's status changes.

## Create a feature

1. **Settle the name and the code.** Take both from the product's own vocabulary — the PRD, the
   glossary, the words the user uses. Load the `glossary` skill when the feature coins a term.
2. **Check it does not exist.** List `features/`, and grep the framework root for the code. A feature
   that already exists is updated in place, never created twice.
3. **Settle its projects.** Name every project the feature relates to, by the `name` in its project
   note. A feature with no project is not a feature yet.
4. **Find the goal it advances.** List the `product/goals/` of each of its projects and cite the one
   this feature is being built for. When no goal fits, say so before you create the feature: either
   the product gained a goal nobody wrote down, or the feature is not worth building. Cite the
   personas it serves in the same step.
5. **Write the folder and the feature note**, at `status: backlog`. Nothing else. A design doc is
   written when someone specifies how the feature works, and the epic is opened on each project's
   roadmap when `/plan` writes the feature's first ticket — the `ticket-board` skill holds how.

## Choosing what is a feature

A feature is **what a customer would name**. It is not a layer, a service, a refactor, or a release.

- **Checkout**, **Saved searches**, **Team invites** — features. A customer asks for each by name.
- **The app shell**, **the auth model**, **the event queue** — not features. They underpin every
  feature, so they are cross-cutting design docs in `designs/`.
- **A migration, an upgrade, or a cleanup** — work inside the feature it changes. When it changes no
  single feature, it still needs a feature note, because every ticket needs a code and only a
  feature mints one; name it for what it gives the product, such as `platform-upgrades`.

**Split a feature** when its note needs "and" to say what a customer can do, or when two parts of it
ship on different dates to different customers. **Merge two** when neither can be used without the
other.

**A feature is deleted only when the product stops doing the thing**, and its design docs are
deleted with it.
