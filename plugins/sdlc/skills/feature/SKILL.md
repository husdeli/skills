---
name: feature
description: "Rules for the feature — the entity that names one thing a customer can do, holds its design docs in its own folder at <docs root>/features/<feature>/, carries the epic code that numbers its tickets, and is the row every capability table and every feature reference points at. INVOKE THIS SKILL before you create, rename, read, or retire a feature, before you write a design doc that belongs to one, before you open an epic on the roadmap, and before you list what the product can do. Enforces one feature per folder, one index note per feature, a code that is the epic code, and a status verified against the code."
---

# feature skill

A **feature** is one thing a customer can do. It is the unit the product is described in, the
work is grouped by, and the plan is sold on, so it has one home and one record:

```
<docs root>/features/checkout/
  checkout.feature.md        the index — what a customer can do, and the state of it
  checkout.design.md         how it works
  payment-retry.design.md    a second subject inside the same feature
```

**The `product-docs` skill resolves the docs root** — load it before you resolve any path below.
It also holds what a vault changes: the fields become frontmatter properties, and a reference
becomes a wikilink.

Three skills hold what sits around a feature: the **`design-doc`** skill for the design docs in its
folder, the **`ticket-board`** skill for the epic and the tickets its code numbers, and the
**`glossary`** skill for every term the feature names.

## One feature, one folder, one index

- **The folder is the feature**, named in kebab-case after the feature itself: `checkout/`,
  `saved-searches/`, `team-invites/`. Singular where that reads naturally.
- **The index is `<feature>.feature.md`**, named after the folder it sits in. Every feature note
  has a unique name, so a reference never needs qualifying.
- **Every design doc that belongs to one feature sits in that feature's folder.** A design doc
  that underpins every feature stays in `<docs root>/designs/` — the `design-doc` skill holds
  which is which.
- **A feature with no design doc yet is still a feature.** The folder holds the index alone until
  someone specifies how the feature works.
- **Nothing else goes in the folder.** Diagrams stay in `<docs root>/diagrams/`, tickets stay in
  `<docs root>/tickets/`.

## The code is the epic code

A feature carries a short uppercase **code** — two to eight letters, taken from the product's own
vocabulary — and that code is the epic code that prefixes every ticket under it: `CHECKOUT-001`,
`CHECKOUT-002`. One code, one feature, one epic. The `ticket-board` skill holds how the code
numbers a ticket and how the roadmap groups by it.

- **The code is unique in the project**, and it never means two things.
- **The code may repeat a PRD area anchor** when the feature fills that whole area. Usually it does
  not: an area holds several features.
- **A feature is opened before its first ticket.** The code exists because the feature exists, not
  because a ticket needed a prefix.
- **Never renumber or recode a feature that has tickets.** The code is how the board, the branches,
  and the reviews cite the work. A rename of the display name is free; a change of code is not.

## The index

```markdown
---
type: feature
name: Checkout
code: CHECKOUT
area: PAYMENTS
status: Planned | In Progress | Shipped
customer_facing: true
shipped: 2026-08-14
updated: 2026-09-28
related:
  - "[[prd]]"
tags:
  - sdlc/feature
---

# Checkout

<Two or three sentences: what a customer can do, and the one fact that separates this feature
from the one nearest to it. Never what the document covers.>

## Designs

- [[checkout.design]] — how an order is taken and paid
- [[payment-retry.design]] — what happens when a payment fails

## Open work

<The Dataview query below, in a vault. The roadmap section, everywhere else.>
```

| Property | What it holds |
| --- | --- |
| `type` | `feature`, always. It is what every query filters on. |
| `name` | The feature's display name, in the product's own words. |
| `code` | The uppercase epic code. Unique in the project. |
| `area` | The PRD area anchor this feature sits under. Empty when the PRD names no area for it. |
| `status` | `Planned`, `In Progress`, or `Shipped`. Nothing else. |
| `customer_facing` | `true` when a customer can name the thing. `false` keeps it out of every capability table. |
| `shipped` | The date the feature reached `Shipped`. Empty until then, and never cleared afterwards. |
| `updated` | The date the note last changed. |

In a `repo` or `folder` destination the properties become `**Field**: value` lines under the
title, exactly as `product-docs` describes for every other document.

**The body is short.** Two or three sentences, the list of designs, and the open work. What the
feature does in detail belongs to the PRD area it cites; how it works belongs to the design docs it
lists; what is left to build belongs to the tickets. The index points at all three and repeats
none of them.

## Status is verified, never assumed

**A feature is `Shipped` only when the work root holds it.** The roadmap can lag the code, and the
code can lag the roadmap. Before you write or trust a `Shipped` status, read the work root for the
feature: the routes, the modules, or the screens a customer would use. Check the board second.

| Status | What is true |
| --- | --- |
| `Planned` | The feature is described. No part of it is in the work root. |
| `In Progress` | Part of it is in the work root, or a ticket for it is in `in-progress/`. |
| `Shipped` | A customer can use the whole feature in the work root today. |

A feature that is partly usable is `In Progress`, not `Shipped`. When the evidence disagrees with
the note, report the disagreement and fix the note in the same step — never quote a status you did
not check.

## The roadmap shrinks; the register does not

The roadmap holds the work that is left, so an epic's section is deleted when its last row is gone.
**The feature note stays.** It moves to `status: Shipped`, takes its `shipped` date, and becomes
the record that the product has this feature at all.

That is the division: `features/` says what the product *is*, `roadmap.md` says what is *left*, and
`tickets/done/` says what *happened*. A feature is deleted from `features/` only when the product
stops doing the thing — and then its design docs go with it.

## Reference a feature

Point at the index note. Never restate what it says.

| Where | The reference |
| --- | --- |
| A vault document | `[[checkout.feature]]`, or `[[checkout.feature\|Checkout]]` |
| A `repo` or `folder` document | `features/checkout/checkout.feature.md`, relative to the document |
| A roadmap epic section | `**Feature**: [[checkout.feature]]` under the epic's sentence |
| A ticket's `Related` block | The same link, beside the PRD area |
| A design doc's `Related` line | The feature it belongs to, plus its sibling designs |
| A capability table | One row per feature, generated by the query below |

Prose a person reads outside the docs root carries no link — a chat reply, a commit message, a
review verdict. Name the feature there, plainly.

## List the features

In a vault, a list of features is a Dataview query, so a new feature appears wherever features are
listed with no edit to the listing document:

````markdown
```dataview
TABLE WITHOUT ID
  file.link AS "Feature",
  area AS "Area",
  status AS "State",
  shipped AS "Since"
FROM "<docs root, relative to the vault root>/features"
WHERE type = "feature" AND customer_facing = true
SORT status ASC, name ASC
```
````

The `FROM` path is relative to the vault root, the folder that holds `.obsidian/`. When the docs
root is the vault root, the path is `features`.

The query needs the Dataview community plugin. Check the vault's list of enabled community plugins
for `dataview`. When it is missing, keep the query, and tell the user to install and enable
Dataview, since the block shows as plain code until then.

**In a `repo` or `folder` destination there is no Dataview.** Write the same columns as a Markdown
table with a relative link per feature, and rewrite the table whenever a feature's status changes.

The **`Open work`** section of a feature's own index lists its tickets the same way:

````markdown
```dataview
TABLE WITHOUT ID
  file.link AS "Ticket",
  status AS "Status",
  assignee AS "Assignee"
FROM "<docs root, relative to the vault root>/tickets"
WHERE type = "ticket" AND startswith(id, "CHECKOUT-") AND status != "Completed"
SORT id ASC
```
````

Outside a vault, that section points at the roadmap section instead: "Open work: the `CHECKOUT`
section of `roadmap.md`."

## Create a feature

1. **Settle the name and the code.** Take both from the product's own vocabulary — the PRD, the
   glossary, the words the user uses. Load the `glossary` skill when the feature coins a term.
2. **Check it does not exist.** List `<docs root>/features/`, and grep the docs root for the code.
   A feature that already exists is updated in place, never opened twice.
3. **Write the folder and the index.** Nothing else. A design doc is written when someone
   specifies how the feature works, and the `design-doc` skill governs it.
4. **Point the PRD at it** when the PRD names the area and does not yet name the feature.
5. **Open the epic on the roadmap** when there is work to do, with `**Feature**:` linking the
   index. The `ticket-board` skill holds the rest.

## Choosing what is a feature

A feature is **what a customer would name**. It is not a layer, a service, a refactor, or a
release.

- **Checkout**, **Saved searches**, **Team invites** — features. A customer asks for each by name.
- **The app shell**, **the auth model**, **the event queue** — not features. They underpin every
  feature, so they are cross-cutting design docs in `designs/`.
- **A migration, an upgrade, or a cleanup** — not a feature. It is an epic with no feature note, or
  work inside the feature it changes.

A feature that no customer sees but that the board still groups work under — a platform epic, a
developer tool — gets its note with `customer_facing: false`. It keeps its folder and its code, and
it stays out of every capability table.

**Split a feature** when its index needs "and" to say what a customer can do, or when two parts of
it ship on different dates to different customers. **Merge two** when neither can be used without
the other.
