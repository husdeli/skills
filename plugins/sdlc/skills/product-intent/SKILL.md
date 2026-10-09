---
name: product-intent
description: "Rules for the product's intent — why it exists, who for, what it refuses, and what proves it worked — held as five kinds of note under <docs root>/product/: a goal, a non-goal, a persona, a problem, and a success metric. These are the pieces the PRD is assembled from, and the pieces a feature, a design doc, and the business plan cite. INVOKE THIS SKILL before you write or change any of those five, before you cite one from a feature, a design doc, a ticket, or the business plan, and before you write the PRD sections that list them. Enforces one note per piece, a statement that stands on its own, a status that is checked rather than assumed, and a citation that links the note instead of repeating it."
---

# product-intent skill

The product's **intent** is why it exists, who it is for, what it refuses to do, and what proves it
worked. Five pieces carry that, they are **referenced from outside the PRD**, and each has
a life of its own — it is met, dropped, deferred, or measured. So each one is a note:

```
<docs root>/product/
  goals/       self-hosted-first.goal.md
  non-goals/   no-mobile-app.non-goal.md
  personas/    solo-operator.persona.md
  problems/    tools-need-a-server.problem.md
  metrics/     weekly-active-vaults.metric.md
```

**The PRD composes these notes; it does not contain them.** Its sections 2, 3, 4, and 7 are one
line per note. Sections 1, 5, and 6 stay the PRD's own prose — an overview, the product areas, and
the cross-cutting qualities are narrative, and narrative does not decompose.

**The `sdlc-structure` skill resolves the docs root** and holds the table of which document owns which
fact — load it before you resolve any path below. The **`prd`** skill holds the document that
composes these notes, the **`feature`** skill holds the feature that cites them, and the
**`glossary`** skill holds every term they name.

## What earns a note

A piece of the product definition becomes a note when **both** of these are true:

1. **Something outside the PRD points at it** — a feature, a design doc, a ticket, the business
   plan, or another note.
2. **It has a state of its own** — it is met or unmet, excluded or deferred, measured or not.

That is why these five and no others. An open question is deleted the week it is answered, so it
stays a bullet in the PRD. A product area is a paragraph that only means something beside the
paragraphs around it, so it stays prose. A risk and an assumption belong to the business plan and
are already numbered inside it.

**Never decompose further than this.** A goal is not split into sub-goals, and a persona is not
split into one note per need. The `prd` skill's rule still holds: a product is described in prose,
not as a tree of individually-IDed micro-requirements.

## The shape every note shares

- **One folder per type**, under `<docs root>/product/`. Create the folder when you write the
  first note in it.
- **The file is `<slug>.<type>.md`** — kebab-case, named after the thing itself:
  `self-hosted-first.goal.md`, `solo-operator.persona.md`. The name is what a link shows, so it
  reads as the thing, not as a category.
- **The title is the name**, and the first line under it is the statement. A reader who opens the
  note gets the whole point in one sentence.
- **The body is short.** Two to five sentences and at most two `##` headings. A note that needs
  more is a design doc, a PRD area, or two notes.
- **No note cites a ticket, a roadmap row, or a file in the code.** They point at notes, and the
  work points at them.

In a `repo` or `folder` destination the properties become `**Field**: value` lines under the title,
and a wikilink becomes a relative path — `sdlc-structure` holds that mapping for every document.

## The goal

`<docs root>/product/goals/<slug>.goal.md`

```markdown
---
type: goal
name: Self-hosted first
status: Committed | Met | Dropped
metric: "[[weekly-active-vaults.metric]]"
answers: "[[tools-need-a-server.problem]]"
updated: 2026-09-28
tags:
  - sdlc/goal
---

# Self-hosted first

<One concrete, testable statement in the present tense: what is true when this goal is met.
Never an aspiration, and never two goals joined by "and".>

## Why

<One or two sentences. Link the problem this answers, and say nothing the problem note
already says.>
```

- **`status`**: `Committed` while the product is working towards it, `Met` when it is true of the
  shipped product, `Dropped` when the product stopped pursuing it. A dropped goal keeps its note
  and says in `Why` what replaced it — deleting it breaks every feature that cites it.
- **`metric`** links the note that says how the goal is measured. Empty when the goal is verified by
  inspection rather than by a number.
- **`answers`** links the problem note. A goal that answers no problem is worth questioning.
- **`Met` is checked, never assumed.** Read the metric's current value, or the work root, before you
  write it.

## The non-goal

`<docs root>/product/non-goals/<slug>.non-goal.md`

```markdown
---
type: non-goal
name: No mobile app
status: Excluded | Deferred
revisit: 2027-03-01
updated: 2026-09-28
tags:
  - sdlc/non-goal
---

# No mobile app

<What the product does not do, in one sentence.>

## Why

<The reason it is not planned. Required: a non-goal with no reason is an omission, not a decision.>
```

- **A non-goal is something the product has not planned.** It is a thing a customer might ask for,
  or a thing a competitor provides, that this product does not do and is not building. It records
  the refusal and its price, so the next person who proposes it argues against a written reason
  rather than against silence.
- **`status`**: `Excluded` is a standing decision, and `Deferred` is a decision with a date in
  `revisit`. There is no third state. A non-goal is the thing the product is not doing, so the
  moment it commits to doing it the note stops being true.
- **A non-goal the product commits to is deleted, and becomes a goal.** Write the goal note, carry
  the reason across, and delete the non-goal in the same step — see "Adopt a non-goal" below. Never
  keep a note whose own type it contradicts: a reader cannot tell a refusal from a commitment by
  reading a status, every query over the folder has to learn to filter it out, and the one that
  forgets reports a goal as "not planned".
- **A non-goal is the one note a feature may contradict.** When a feature crosses one, that is the
  signal to adopt the non-goal deliberately rather than to quietly build past it.

## The persona

`<docs root>/product/personas/<slug>.persona.md`

```markdown
---
type: persona
name: Solo operator
pays: true
updated: 2026-09-28
tags:
  - sdlc/persona
---

# Solo operator

<Who they are as a usage archetype — what they do, and the constraint they work under.
Never a demographic, and never a named customer.>

## Need

<The one thing they need from this product.>

## Primary flow

<How they use the product, in one or two sentences.>
```

- **`pays`** is the one commercial fact the note carries, so the business plan can query which
  personas buy. Everything else commercial — which plan they land on, what they are worth — stays
  in the business plan.

## The problem

`<docs root>/product/problems/<slug>.problem.md`

```markdown
---
type: problem
name: Tools need a server
hurts:
  - "[[solo-operator.persona]]"
updated: 2026-09-28
tags:
  - sdlc/problem
---

# Tools need a server

<What existing tools or approaches fail at, and why they fail at it. Two or three sentences,
about the state of the world — not about this product.>
```

- **The problem note never says what this product does about it.** The goal that links it says
  that, once. This is the rule that keeps the two from becoming one document written twice.
- **Criticising a category of tool belongs here.** Criticising a **named competitor** belongs in the
  business plan's competition section, with a measure.

## The success metric

`<docs root>/product/metrics/<slug>.metric.md`

```markdown
---
type: metric
name: Weekly active vaults
target: "500 by 2027-03-31"
baseline: "40 at 2026-09-01"
value: "112"
measured: 2026-09-28
updated: 2026-09-28
tags:
  - sdlc/metric
---

# Weekly active vaults

<Exactly what is counted, and what is excluded from the count. A definition two people would
apply the same way.>
```

- **`value` and `measured` are read together.** A value with no date is not a measurement. A
  measurement older than the cadence the metric is meant to be read at is stale — say so rather
  than quoting it.
- **The definition is the point.** A metric a reader could count two ways is a metric that will be
  reported two ways.

## Cite a note, never repeat it

| Where | The citation |
| --- | --- |
| The PRD's list sections | One line per note: the link, then the statement in a few words |
| A feature index | The `goals`, `non_goals`, and `personas` properties |
| A design doc | The goal or the quality it holds to, in its `related:` property |
| A ticket | The goal the task advances, in its `related:` property |
| The business plan | The persona a segment is, and the metric a milestone proves |

- **A citation carries enough of the note to read past it.** `[[self-hosted-first.goal]] — the
  product runs with no server the user does not own.` A bare link makes the reader open a file to
  follow a sentence.
- **Never restate the `Why`.** The citing document says what it does with the note; the note says
  why the note exists.
- **A rename is one edit**: the file, and every link that points at it. Search the docs root for the
  old name before you stop.
- **A note is deleted only when nothing cites it.** Check first. A goal that was pursued and
  abandoned is `Dropped`, not deleted.

## List the notes

In a vault, any list of notes is a Dataview query, so a new note appears in every list with no edit
to the listing document:

````markdown
```dataview
TABLE WITHOUT ID file.link AS "Goal", status AS "State", metric AS "Measured by"
FROM "<docs root, relative to the vault root>/product/goals"
WHERE type = "goal" AND status != "Dropped"
SORT name ASC
```
````

The `FROM` path is relative to the vault root, the folder that holds `.obsidian/`. The query needs
the Dataview community plugin — check the vault's enabled community plugins, and when it is
missing, keep the query and tell the user to install and enable Dataview.

**In a `repo` or `folder` destination there is no Dataview.** Write the same rows as a Markdown list
with a relative link per note, and rewrite the list whenever a note is added or its status changes.

Useful queries this shape buys, which no single document could answer before:

- Every feature advancing one goal — `WHERE contains(goals, "[[self-hosted-first.goal]]")`.
- Every goal with no feature pointing at it — a goal nothing is being built for.
- Every deferred non-goal whose `revisit` date has passed.
- Every metric whose `measured` date is stale.

## Write a note

1. **Check it does not exist.** List the type's folder, and read the names. A goal stated twice in
   two words is the thing this structure exists to prevent.
2. **Write the statement first**, and keep the note only if the statement stands on its own. A goal
   that needs the PRD open beside it to make sense is not a goal yet.
3. **Link the note it depends on** — a goal links its problem and its metric, a problem links the
   personas it hurts.
4. **Add the line to the PRD's list section**, in the same step. A note no document composes is a
   note nobody will read.

## Adopt a non-goal

The product decided to build the thing it refused. The non-goal is now false, so it is replaced by a
goal rather than annotated. Do all five steps in one change, because a citation left pointing at a
deleted note is a broken link and a citation left pointing at a live one is a lie:

1. **Write the goal note**, stating what the product now does.
2. **Carry the reason across.** The non-goal's `## Why` holds what the thing costs, and that cost
   does not disappear when the product agrees to pay it — it is what the work has to include. Put it
   in the goal's `## Why`, beside why the product wants it.
3. **Repoint every citation** at the goal: a feature's `non_goals` (move it to `goals`), a competitor
   note's `provides`, a business-plan gap, any design doc or ticket that links the note. Search the
   docs root for the note's name; a wikilink is the only way anything refers to it.
4. **Delete the non-goal note**, and remove its line from the PRD's non-goals list. The history is
   in version control, which is where a superseded decision belongs.
5. **Say in the goal where it came from** — one clause naming the date the product changed its mind.
   A reader who wonders whether the refusal was ever considered gets the answer without the corpse.

A `Deferred` non-goal whose `revisit` date passed is not adopted by default. Either it is adopted by
this procedure, or its `revisit` moves to a new date.
