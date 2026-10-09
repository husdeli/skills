---
name: design-doc
description: "Create a design doc at <docs root>/features/<feature>/<subject>.design.md when it belongs to one feature, or <docs root>/designs/<subject>.design.md when it underpins every feature — under .sdlc/ by default, or the folder .sdlc.json points at, such as one in an Obsidian vault — that specifies how a solution works — the parts it is built from, how work flows through it end to end, and how it behaves. Use when: asked to write a design doc, or to specify a system, a service, a flow, an integration, a data model, or a screen. A design doc defines the target state — not how to build it"
---

# Design-doc skill

Create a design doc following the structure and style below.

**Where they live.** A design doc is **one file per subject**, named `<subject>.design.md` —
`checkout.design.md`, `event-ingestion.design.md`, `app-shell.design.md`. There is no single
`design.md`: a design doc covers one subject, and the file name is that subject.

**Two folders hold them, and ownership decides which.**

| The subject | Where the file goes |
| --- | --- |
| Belongs to **one feature** — what that feature is built from, how it behaves | `<docs root>/features/<feature>/<subject>.design.md` |
| Underpins **every feature** — an app shell, an authentication model, a shared data model, an event queue | `<docs root>/designs/<subject>.design.md` |

Create the folder if it is missing. **Load the `feature` skill before you decide**, and open the
feature first when the subject belongs to a feature that has no folder yet: a design doc never
creates the feature it describes as a side effect.

Ask one question to settle it: *would this doc still be needed if the feature were dropped?* Yes →
`designs/`. No → the feature's folder. A doc that two features depend on and a third would not is
still cross-cutting; `designs/` is where a shared subject belongs, not the folder of whichever
feature reached it first.

**Load the `sdlc-structure` skill and resolve the docs root as it says**, before you read or write
anything. It also holds what a vault changes: `Last updated` becomes a frontmatter property there,
and a cross-reference becomes a wikilink. The related documents are the `related:` frontmatter
property in every destination.

- **Name the subject, not the document.** `billing.design.md` — never `design-billing.md`,
  `billing-design.md`, or `billing.design.doc.md`. Kebab-case, and singular where that reads
  naturally.
- **One subject per file.** A name that needs "and" in it describes two docs.
- **`overview.design.md`** is the optional entry point, in `designs/`. It names the parts of the
  whole solution, says how they fit together, and points at the per-subject docs. Write it once a
  project has more than a handful of them.
- **Cross-reference by relative path** — "see `../../designs/app-shell.design.md`" — never by
  copying the content across. In a vault, cross-reference with a wikilink instead, and the folder
  makes no difference: `[[app-shell.design]]`.
- **A doc in a feature's folder names its feature** in its `related:` property, with the
  feature's index note. A doc in `designs/` names the PRD instead.
- **Find the docs by listing** `<docs root>/features/*/*.design.md` and
  `<docs root>/designs/*.design.md`, then read the ones the task touches. A feature's own docs
  are the ones in its folder — list that folder first when the task names a feature.

**A project on an older shape keeps working.** Design docs used to sit in `designs/` whether or
not they belonged to a feature, before that directly in the docs root, and before that in a single
`design.md` there or at the project root. Read whichever shape the project has, and update the file
in place where it already sits. Move the docs into a feature folder, or split a single `design.md`
by subject, only when the user asks — `/setup` offers the move.

A design doc is a **specification of the intended end state of one solution**: the **parts** it
is built from, how those parts fit together, how work flows through it **end to end**, and how
it **behaves** — including when something fails. It is the shared reference the team agrees on
*before* the solution is built or changed.

The subject can be anything a team designs: a whole system, one service, a data flow, an
integration with an outside party, a background job, a permission model, a pricing rule, or a
user-facing screen. **A user interface is one kind of subject, not the default one.** Pick the
subject first, then apply the same pattern to it.

Engineers, designers, and product people all read this doc and must read it the same way. Load
the **`technical-writing`** skill on top of this one and follow it for every sentence — it sets the
sentence length and the active voice. This skill governs *what
belongs in a design doc*; `technical-writing` governs *how each sentence reads*.

**Load the `glossary` skill for every domain term.** It says where a term comes from, that
`<docs root>/glossary.md` defines it under its own heading, how this doc links that definition, and
that a term this design coins gets its entry in the same step.

## Core rules

1. **Write the minimum that makes the solution understood.** A design doc is judged by what a
   reader understands per line. Every sentence must carry a fact about *this* solution that no
   other sentence carries. Cut, in this order:

   - **Prose about the document.** No "this doc covers…", no "what is out of scope", no "as
     described above", no first sentence that repeats its own heading.
   - **Sentences that would stay true for another product.** "Errors are handled gracefully",
     "the layout is responsive", "the code is maintainable" — these tell a reader nothing.
     Either say what *this* design does differently, or delete the line.
   - **A fact stated twice.** State it once, at the highest section it holds for, and point at
     it from everywhere else by its numbered heading (see *Style rules*).
   - **A fact another document owns.** What a customer can do belongs to the feature note; why
     the product does it belongs to the PRD; what it earns belongs to the business plan. This doc
     starts where they stop: at how the thing works. The `sdlc-structure` skill holds the table.
   - **A section with nothing specific to say.** **Delete the heading — never fill it.**
   - **A part you have not designed yet.** It is absent from the doc, not a stub in it.

2. **Define the target state — never a procedure.** A design doc says how the solution *is
   supposed to work*, in the present tense, as settled fact. It never explains *how to build
   it*: no steps, no "first do X then Y", no migration order, no build tasks. If a sentence
   tells someone what to *do*, rewrite it as a statement of what *is*.
3. **Stay at the structural altitude — not the implementation detail.** Specify the parts and
   what each one is responsible for, the boundaries between them, what crosses each boundary,
   the path work takes through them, and the behavior at every step. Do **not** make
   fine-grained decisions that a part can change on its own without anyone outside it
   noticing — class, function, and file names, code, library calls, query text, framework
   choices, config keys, and, for a screen, hex colors, font families, pixel sizes, spacing,
   or radii. Rule of thumb: **if a decision could change without changing anything a
   neighboring part observes, it is too low-level for this doc.**

   Name a part by the **role it plays** (the **event queue**, the **rate limiter**, the
   **project sidebar**). Name a concrete technology or a concrete number only when that
   choice *is* the design decision and changes observable behavior — a store that guarantees
   ordering, a retry budget of three attempts, a page size of 50. Where a quality matters but
   the value does not, state it **qualitatively** ("a small, consistent palette", "retried
   until it succeeds or the deadline passes").
4. **No changelog. Ever.** The doc describes the current intended design, not its history.
   No "Changelog", "History", or "Revisions" section, and no annotations for when or why a
   section changed. Version history lives in git. When you revise a design doc, edit the
   affected sections in place and update the `Last updated` date — leave no trace of the
   prior state in the prose.
5. **One subject per document; cross-reference to isolate logic.** Every design doc covers
   one subject and carries its name — a shared app shell, an authentication model, an
   ingestion pipeline, an onboarding flow. When the design needs a second subject, write a
   second `<subject>.design.md` and reference it, rather than inlining and duplicating it.
   Cross-reference by numbered heading ("see 3.5 Behavior") within a doc and by relative path
   between design docs. **Reference only other design docs, the feature this doc belongs to, the
   glossary, and the PRD** — the glossary for a term's definition, and
   the PRD only when it actually exists in the project; otherwise omit it. Never link to build or operations docs
   (deployment runbooks, setup guides, generated API references).
6. **No tickets, no code references.** The doc stands on its own and stays true as the work
   and the codebase move. Never cite a ticket, issue, PR, roadmap item, or milestone
   (`JIRA-1234`, "per the linked issue", "shipping in phase 2"), and never point at the
   implementation — file paths, directories, class or function names, routes, props, CSS
   classes, config keys, or code snippets. Name every part by what it *is* in the solution,
   not by what it is called in the source. If a fact only makes sense by pointing at a ticket
   or a file, it is not a design fact — drop it or restate it as an observable property of
   the solution.

## Document shape

The file is `<subject>.design.md`, and the title names the same subject.

```
---
related:
  - <the feature this doc belongs to, checkout.feature.md, or for a doc in designs/ the PRD
    when one exists>
  - <each other-subject.design.md this design touches>
---

# <Subject> — design

**Last updated**: <YYYY-MM-DD>

<One or two sentences: what the subject is, and what it is for. Never what the document
covers, leaves out, or how it relates to the PRD — the related property carries that.>

---

## 1. Foundations

Only the rules that hold across **every** part below and that a later section relies on
instead of restating. Three to seven short declarative bullets, stated **qualitatively**
per rule 3. A bullet that names no constraint on the design is filler — cut it. When the
subject has no such shared rule, omit the whole section.

---

## 2. <First part, surface, or flow>

<One sentence naming it and its role. The heading already says what it is; do not repeat it.>

### 2.1 Structure
### 2.2 Behavior
### 2.3 States
### 2.4 Variation and limits

## 3. <Next part>
…
```

**Size.** A part is about 40 lines. A whole doc is under 300. Passing that means the subject
is really two subjects (split it), or the prose is padded (cut it).

### The per-subject pattern

Specify each part, surface, or flow in this order (the `2.x` headings above). **Keep the order,
and write only the sections that have something specific to say about this part** — a part with one
state and no variation is three headings shorter, not three headings of filler.

- **Structure** — what the subject is built from and how it is arranged: the components and
  the boundaries between them, the stages of a flow, or the regions of a screen. Any non-trivial
  arrangement gets a **diagram** — load the **`diagrams`** skill, which holds how one is drawn and
  where it lives.
- **Behavior** — how it actually works, end to end. Follow one unit of work from where it
  enters to where it leaves: what triggers it, what each part decides, what it hands on, and
  what the caller gets back. Name what each boundary carries. A reader must be able to trace
  a complete path through the subject from this section alone.
- **States** — a **table** of the outcomes that differ from each other, and what each one
  means here. Columns: `State | What happens`. Check the easy-to-forget ones — empty, not yet
  authorized, invalid input, a slow or unavailable dependency, a retry or a duplicate, a
  conflict, and, for a screen, loading, empty, gated, populated, error — and keep the rows
  where this design does something worth knowing. Drop a row whose answer is the generic one
  ("shows an error"); it costs a line and teaches nothing.
- **Variation and limits** — how the subject changes under different conditions (role or
  permission, configuration, tenant, region, volume, or screen width for a user interface),
  and the boundaries it holds within (capacity, timeouts, retry budgets, ordering and
  consistency guarantees). State a number only when it is a design decision, per rule 3.

### Common subjects

The pattern is the same for every subject; only what fills each section changes.

| Subject | Structure | Behavior | States | Variation and limits |
| --- | --- | --- | --- | --- |
| System or service | Components and their boundaries | The path of one request | Success, rejection, dependency failure | Load, configuration, guarantees |
| Flow or pipeline | Stages and what connects them | What each stage does to one item | Skipped, retried, dead-lettered | Volume, ordering, backlog |
| Integration | The two sides and the contract between them | One exchange, both directions | Accepted, rejected, timed out, replayed | Rate limits, versioning |
| Rule or model | The entities and their relations | How a decision is reached | Allowed, denied, undefined | Role, tenant, edge cases |
| Screen or surface | Regions and their arrangement | What the user does and what answers | Loading, empty, gated, populated, error | Screen width, permission |

## Style rules

- **Present tense, declarative.** "Each upload enters the queue once." Not "we will build",
  not "you should add", not "to create the queue…".
- **Bold a load-bearing noun where this doc first names it** (**event queue**, **default
  project**, **sidebar**) so the structure is scannable, and link its glossary entry there.
- **A diagram for anything with shape** — the parts and what connects them, the stages of a flow,
  the regions of a screen — referenced with a one-line caption under it. The **`diagrams`** skill
  holds the rest, and the prose stays complete without the picture.
- **Tables for states and for matrices** (e.g. permission-dependent behavior). Prose for
  everything with nuance.
- **Cross-reference generously** by numbered heading — "see 3.5 Behavior" — so a rule stated once
  is pointed to, never restated. Between docs, link by relative filename.
- **One concrete example** where the intent is otherwise ambiguous — a sample value, message,
  or label ("Start free"). One is enough; a list of examples restates the rule.
- **Name behavior, not mechanism.** "A second submission of the same order changes nothing" —
  not which lock, index, or state hook enforces it.
- **No filler openers or closers.** No "In summary", no "It is important to note that", no
  paragraph that introduces the paragraph after it. Start with the fact.
- Every sentence adds a fact about the design. A sentence that only connects two other
  sentences is a sentence to delete.

## Choosing the subject of a doc

The subject decides the file name, so choose it before you write a line. A good subject is:

- **Self-contained** — describable on its own (an authentication model, an ingestion
  pipeline, the app shell, an onboarding flow).
- **Reused across parts** — a shared contract, layout, or pattern that would otherwise be
  duplicated in several docs and drift.
- **Whole** — big enough that the four sections have something to say, small enough that one
  reader holds it in their head.

Start a second doc — `<other-subject>.design.md` — as soon as one of these appears:

- A section describes something the rest of the doc does not depend on.
- The same design is being restated for a second reader or a second part.
- The doc needs "and" to say what it covers.

Every doc carries the same header (Status / Last updated), links to its feature and its siblings
through the `related:` property, and stays a **design doc** — structure and behavior only. The
doc that references another names it by file (e.g. "see `event-ingestion.design.md`") instead of
repeating it. Never spin off (or link to) a build or operations doc.

**A new subject inherits the folder of the doc it came out of** when it belongs to the same
feature, and moves to `designs/` when the split is what made it cross-cutting.

## After drafting

Read the draft once with only one question in mind: **what can go?** Delete every sentence
whose removal costs the reader no understanding — meta-prose, generic truths, restatements,
empty headings, examples that repeat the rule. Then check the rest against the core rules,
and confirm with the user:
1. Does any sentence describe *how to build* rather than *how it works*? Rewrite it.
2. Can a reader trace one complete path through the solution, from what starts it to what
   comes out? If not, the Behavior section is incomplete.
3. Does any line make a call a single part could change on its own — a name in the source, a
   library, a query, a hex color, a font, an exact size? Raise the altitude, or drop it.
4. Does any line cite a ticket/issue/PR or point at the code (a path, class name, route,
   prop)? Remove it, or restate it as an observable property.
5. Is any part self-contained enough to be its own `<subject>.design.md` beside this one,
   cross-referenced from here? If it is, does it belong to this feature, or to `designs/`?
6. Are the states complete, including the failures — invalid input, a missing permission, an
   unavailable dependency, a duplicate?
7. Would the doc lose anything if it were half as long? If not, cut it in half.
