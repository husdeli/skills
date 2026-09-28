---
name: business-plan
description: "Create or update the business plan at <docs root>/business/business-plan.md and one competitor note per competitor in <docs root>/business/competitors/. Use when: asked to write or update a business plan, analyse, add, or refresh a competitor, or model pricing, unit economics, break-even, or go-to-market."
---

# Business plan skill

A business plan states the **commercial case** for the product: who pays, what one customer earns
and costs, how many customers the business needs, and what the next 12 to 18 months must prove. The
PRD already says what the product does. The plan links the PRD for that and never restates it.

Load three skills before you read or write anything:

- **`product-docs`**: resolve the docs root, and follow its vault conventions (frontmatter
  properties, wikilinks, no dot-folders).
- **`clean-writing`**: every sentence of the plan and of each competitor note.
- **`glossary`**: use the product's terms, and link each one at its first use.

## Where it lives

```
<docs root>/
  business/
    business-plan.md          the plan, one per product
    competitors/
      gamma.md                one note per competitor, named by a lower-case slug
      buffer.md
      …
```

Create `business/` and `competitors/` when they are missing. When the docs root already holds a
business plan somewhere else, move it into `business/` with the user's yes, and keep its content.

## The rules

1. **Every figure is a fact or an assumption.** A fact links its source: the PRD, a design doc, a
   ticket, or a web page. Anything else is an assumption with an ID (`A1`, `A2`, …) in the
   assumptions register, and the prose cites that ID. A number with neither is a defect.
2. **Say each thing once.** Each topic has one home section. Every other mention is a link to that
   heading (`[[#7. Unit economics|unit economics]]`), never a second copy. The summary is a list of
   one-line pointers, not a restatement. Risks live only in the risks table. Competitor detail
   lives only in the competitor notes.
3. **Link, never restate.** Product behaviour links the PRD heading. Pricing mechanics link the
   design doc that owns them. Open work links its ticket. Tickets are allowed here, unlike in the
   PRD, because launch readiness depends on the state of the work.
4. **Show the arithmetic.** Every derived figure shows its inputs, so a reader can recompute it
   when an input changes: contribution per customer, break-even count, scenario totals.
5. **Scenarios are models, not forecasts.** Give three cases (conservative, base, optimistic) with
   the same two or three inputs, and say which inputs to replace with measured values, and when.
6. **Name the point where the plan changes course.** A dated threshold, two measurable conditions,
   and the options that follow. A plan with no such point cannot fail, so it cannot guide.
7. **Verify the product state in the code.** A capability is "shipped" only when the work root
   holds it. The PRD and the roadmap can lag the code. Check the feature folders before you mark
   a capability as missing.

## Step 1: Gather the facts

Read the PRD, the glossary, the roadmap, and every design doc that covers pricing, plans,
payments, hosting, or growth. Read the work root for the values the docs do not hold: plan
prices, plan limits, credit or usage rates, and the list of shipped integrations.

**Done when** you hold, with a source for each: what the product sells today, every published
price, every plan limit, the cost of one unit of usage, and the open work that blocks a launch.

## Step 2: Ask what the documents cannot answer

Ask one `AskUserQuestion` with up to four questions, and only for what Step 1 did not settle:

| Question | Why it changes the plan |
| --- | --- |
| **Audience**: the founder, investors, or a lender | Investors add market size, team, the funding ask, and use of funds. A lender adds a conservative-case focus and repayment. The founder gets an operating plan. |
| **Stage and traction**: users, paying customers, revenue | Sets the starting point of every scenario |
| **Primary market** | Sets the launch focus, the currency, and the payment constraints |
| **Team and budget** | Sets fixed costs and the break-even target |

Explain the choice in the question itself: a user who does not know why a question matters picks
at random.

**Done when** every row above has an answer from the user or from the documents.

## Step 3: Analyse the competitors

Write one note per competitor. Research each one on the web, from its own pricing and product
pages first. Never write a price or a feature from memory: an unsourced competitor fact is an
assumption, and it goes to the register with that label.

Take the competitor list from the PRD's problem statement, from the user, and from the products
a target customer would name as the alternative. Include the **main substitute**, the combination
a customer already uses instead (for example "a general AI chat plus a scheduler"), as a note with
`kind: substitute`.

When there are more than four competitors, research them in parallel: one subagent per group of
four, each given this template and told to return the files it wrote.

### The competitor note

```markdown
---
type: competitor
name: <Product name>
website: https://example.com   # empty ("") for a substitute
category: <what it is, in two to four words>
kind: direct | adjacent | substitute
threat: 1 | 2 | 3
price_from: "<lowest paid plan as published, with currency and period>"
free_plan: true | false
checked: <YYYY-MM-DD>
tags:
  - sdlc/competitor
---

# <Product name>

<Two or three sentences: what it is, who it serves, and why a target customer would pick it.>

## Pricing

| Plan | Price | What it adds |
| --- | --- | --- |

## What it does well

## Where <our product> differs

## What to watch

<A change in this competitor that would change the plan: a feature, a price, a market move.>

## Sources

- <URL>: read <YYYY-MM-DD>
```

- **`kind`**: `direct` sells the same outcome to the same customer. `adjacent` covers one part of
  the outcome. `substitute` is what the customer uses today instead of any product like ours.
- **`threat`**: 1 is high, 2 is medium, 3 is low. It is a number so the query sorts it.
- **`checked`** is the date the pricing and sources were read. A note older than 90 days is stale:
  refresh it before the plan quotes it.

In a `repo` or `folder` destination, the frontmatter fields become `**Field**: value` lines under
the title, as `product-docs` describes.

**Done when** every competitor has a note, every note has a `checked` date and at least one
source, and no price in any note comes from memory.

## Step 4: Write the plan

### Frontmatter (vault)

```yaml
---
type: business-plan
product: <name>
audience: founder | investors | lender
status: Draft | Living document
updated: <YYYY-MM-DD>
tags:
  - sdlc/business-plan
---
```

Under the title, one **Related** line links the PRD, the roadmap, the design docs the plan cites,
and the competitors folder.

### Sections, in this order

1. **Summary**: one-line pointers to the sections below, each ending in a link.
2. **The product**: what a customer can do today, as a capability and state table that links the
   PRD and the tickets. Then what makes it different, in three to five points.
3. **The problem and the customer**: the problem in one paragraph, then a table of the segments
   who pay first, why they pay, and the plan they land on.
4. **Market and launch focus**: the one launch focus, the first and the second market, and what
   limits each. An investor plan adds a bottom-up market size here.
5. **Competition**: the competitor query below, the positioning line, and one paragraph on the
   main substitute. No per-competitor detail.
6. **Business model**: plans, prices, limits, and the rules that shape revenue.
7. **Unit economics**: contribution and margin per product, the blended figure, and what free
   users cost.
8. **Go-to-market**: the launch sequence, then the ongoing channels with their cost.
9. **Operations**: people, infrastructure, payments and tax, legal, the launch-readiness tickets,
   and a **focus rule** that says which work is allowed until the first milestone is reached.
10. **Financial plan**: fixed costs, break-even targets, the three scenarios, and runway. An
    investor plan adds the funding ask and use of funds. A lender plan adds repayment.
11. **Risks**: one table of risk, effect, and response. Each risk that already has a ticket links it.
12. **Milestones**: a dated table with a proof for each, the point where the plan changes course,
    and the metrics to measure from day one, linked to the PRD's success metrics.
13. **Assumptions register**: every assumption ID, the value used, and how to replace it.

An investor plan adds a **Team** section after Operations.

### The competitor query

In a vault, section 5 lists the competitors with a Dataview query, so a new or refreshed note
appears in the plan with no edit to the plan:

````markdown
```dataview
TABLE WITHOUT ID
  file.link AS "Competitor",
  category AS "Category",
  kind AS "Kind",
  price_from AS "Paid from",
  choice(threat = 1, "High", choice(threat = 2, "Medium", "Low")) AS "Threat",
  checked AS "Checked"
FROM "<docs root, relative to the vault root>/business/competitors"
WHERE type = "competitor"
SORT threat ASC, name ASC
```
````

The `FROM` path is relative to the vault root, the folder that holds `.obsidian/`. When the docs
root is the vault root, the path is `business/competitors`.

The query needs the Dataview community plugin. Check the vault's list of enabled community plugins
for `dataview`. When it is missing, keep the query, and tell the user to install and enable
Dataview, since the block shows as plain code until then.

In a `repo` or `folder` destination there is no Dataview. Write the same columns as a Markdown
table with a relative link per note, and rewrite the table whenever a competitor note changes.

## Step 5: Check the result

- Every wikilink resolves to a note, and every `#heading` link resolves to a heading.
- Every assumption ID the prose cites has a row in the register, and every row is cited.
- No topic is written out in two sections.
- Every competitor note passes its done condition in Step 3.

**Done when** all four checks pass. Report which ones failed, if any, and fix them before you
report the plan as written.

## Updating an existing plan

- **Edit in place.** The plan is a living document. Fold changes into their home section, and
  keep no change log in it.
- **Replace assumptions with measurements.** When a measured value exists, write it into the
  register with its date, and update every figure derived from it.
- **Refresh stale competitor notes** before the plan relies on them, and add a note for each new
  competitor the user names.
- **Bump `updated`.**

## After writing or updating

Ask the user:

1. Which assumptions can they replace with a real number now?
2. Is any competitor missing, or any threat level wrong?
3. Is the point where the plan changes course one they would act on?
