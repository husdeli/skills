---
name: design-doc
description: "Create a design doc (design.md) that specifies how a product looks and behaves. Use when: asked to write a design doc, spec a screen/surface/flow, or document how the app is supposed to look and behave. A design doc defines the target state — not how to build it"
argument-hint: "The screen, surface, or system to specify"
---

# Design-doc skill

Create a design doc (conventionally `design.md`) following the structure and style below.

A design doc is a **specification of the intended end state**: the **high-level
structure** of each page — its regions, hierarchy, and flow — how it is arranged, and
how it responds. It is the shared reference designers and engineers agree on *before*
a screen is built or changed.

## Core rules

1. **Define the target state — never a procedure.** A design doc says how the system
   *is supposed to look and work*, in the present tense, as settled fact. It never
   explains *how to build it*: no steps, no "first do X then Y", no implementation
   choices (component names, file paths, libraries, code, API shapes, data schemas
   unless the schema *is* the spec). If a sentence tells someone what to *do*, it does
   not belong here — rewrite it as a statement of what *is*.
2. **Stay at the structural altitude — not the pixel.** Specify the **high-level
   design**: page structure, regions and their arrangement, visual hierarchy,
   navigation and flow between surfaces, and behavior. Do **not** make fine-grained
   visual decisions — no specific colors or hex values, font families or type scales,
   pixel sizes, exact spacing, border radii, or shadow values. Where a visual quality
   genuinely matters, state it **qualitatively** ("a small, consistent palette", "one
   accent color", "a clear three-level heading hierarchy", "generous spacing"), and
   leave the concrete tokens to the design system and implementation. Rule of thumb:
   if a decision could be captured in a theme file or style token, it is too low-level
   for this doc.
3. **No changelog. Ever.** The doc describes the current intended design, not its
   history. Do not add a "Changelog", "History", or "Revisions" section, and do not
   annotate sections with when or why they changed. Version history lives in git.
   When you revise a design doc, edit the affected sections in place and update the
   `Last updated` date — leave no trace of the prior state in the prose.
4. **Split by concern; cross-reference to isolate logic.** Keep one coherent surface
   or family of surfaces per document. When a slice of the design is self-contained
   and reused — a shared app shell, a family of editors, an onboarding flow — give it
   its own design doc and reference it, rather than inlining and duplicating it.
   Cross-reference by named section (`§3.5`) within a doc and by relative filename
   between design docs. **Reference only other design docs and the PRD** — and the
   PRD only when a `PRD.md` (or equivalent) actually exists in the project; otherwise
   omit it. Never link to implementation or technical docs (data models, renderer
   contracts, deployment, API specs). The design doc describes appearance and
   behavior; how it is built is out of scope and belongs elsewhere.

## Document shape

```
# <Doc title> — <what it specifies>

**Status**: Living document
**Last updated**: <YYYY-MM-DD>
**Related**: `PRD.md` (product requirements) — only if a PRD exists; plus any other design docs

<Opening paragraph: what this doc covers and what it does not — the WHAT, not the HOW.
If a PRD exists, state how this doc relates to it (PRD says what the product does;
design says how it presents / behaves).>

---

## 1. Foundations

Cross-cutting design intent that applies to every surface unless a later section
overrides it (color, type, spacing, motion, responsiveness, shared shell/layout).
State each as a short declarative bullet, **qualitatively** — the *character* of the
palette, type hierarchy, and spacing, never concrete hex values, font names, or pixel
sizes (those live in the design system, per rule 2).

---

## 2. <First surface / screen>

<One or two sentences naming the surface and its role.>

### 2.1 Layout
### 2.2 Content
### 2.3 States
### 2.4 Responsive

## 3. <Next surface>
…

## N. Other screens (planned)

A stub list of surfaces not yet specified, to be filled in following the same
layout → content → states → responsive pattern.
```

### The per-surface pattern

Specify each screen/surface in this order (§2.x above). Not every surface needs all
four, but keep the order:

- **Layout** — how the surface is arranged: regions, columns, what sits where. Use an
  **ASCII diagram** for any non-trivial arrangement (see below).
- **Content** — what each region holds: the actual elements, labels, and copy
  examples, top to bottom.
- **States** — a **table** of the meaningful states and how each looks. Columns:
  `State | Appearance`. Cover at least: loading, empty, signed-out/permission-gated,
  populated, and error/edge where relevant.
- **Responsive** — how the layout adapts across wide / medium / small widths (what
  reflows, stacks, collapses, or hides).

## Style rules

- **Present tense, declarative.** "The hero is a two-column split." Not "we will
  build", not "you should add", not "to create the hero…".
- **Bold a term where it is defined**, then reuse it plainly. Bold the load-bearing
  nouns of a sentence (**sidebar**, **backlink**, **default project**) so the
  structure is scannable.
- **ASCII diagrams** for layout — box-drawing characters, labeled regions, and a
  one-line caption underneath explaining any non-obvious relationship. A picture of
  the arrangement beats a paragraph describing it.
- **Tables for states and for matrices** (e.g. auth-dependent chrome). Prose for
  everything with nuance.
- **Cross-reference generously** with `§` section numbers so a rule stated once is
  pointed to, never restated. Between docs, link by relative filename.
- **Copy examples in parentheses or quotes** ("Start free", "No credit card
  required") to make intent concrete without prescribing exact final wording.
- **Name behavior, not mechanism.** "Rotation pauses while the pointer rests on the
  card" — not which event handler or state hook does it.
- Keep prose tight. Every sentence adds a fact about the design.

## When to split into a new doc

Give a slice of the design its own document (and cross-reference it) when it is:

- **Self-contained** — a coherent surface or family describable on its own (the app
  shell, the landing page, the editor family, an onboarding flow).
- **Reused across surfaces** — a shared layout or pattern that would otherwise be
  duplicated and drift.
- **Large enough to stand alone** — a surface whose full spec would swamp the parent.

The split doc stays a **design doc** — appearance and behavior only — and the parent
references it by name (e.g. "see `app-shell.md`") instead of repeating it. Each split
doc carries the same header block (Status / Last updated / Related) and links back
through `Related`. Never spin off (or link to) an implementation doc.

## After drafting

Check the draft against the core rules, then confirm with the user:
1. Does any sentence describe *how to build* rather than *how it looks/works*? Rewrite it.
2. Does any line make a pixel-level call (a hex color, a font, an exact size/spacing)?
   Raise the altitude to qualitative intent, or drop it.
3. Is any part self-contained enough to be its own cross-referenced doc?
4. Are the states complete (loading, empty, gated, populated, error)?
