---
name: prd
description: "Create or update a product requirements document at <docs root>/prd.md — .sdlc/prd.md by default, or the folder .sdlc.json points at, such as one in an Obsidian vault. Use when: asked to write a PRD, draft or revise product requirements, document a new product or feature set, update an existing PRD, or maintain a living spec."
---

# PRD Skill

Write or update a product requirements document following the structure and style below.

**Where it lives.** The PRD is `<docs root>/prd.md`, alongside `glossary.md`, `roadmap.md`, the
`product/` folder, the `features/` folder, the `designs/` folder, and the `tickets/` folder. **Load the `product-docs` skill and resolve the docs
root as it says**, before you read or write anything. Create the folder if it is missing. When the project already keeps
a PRD at the root (`prd.md`/`PRD.md`), update that file in place instead — one PRD per
project, never two.

When `kind` is `vault`, load the **`product-docs`** skill as well: the PRD's `Status`,
`Last updated`, and `Product` fields become frontmatter properties there. In every destination,
the PRD lists the design docs it relates to in a `related:` frontmatter property, never in its
body. It never lists the business plan, because the plan links the PRD and not the reverse.

A PRD describes **what the product does and why** — the requirements, from the user's point of view. It is not an implementation plan, a project tracker, or a technical design. Keep it durable: it stays accurate as tickets come and go and as the implementation is rewritten underneath it.

A PRD is read end to end by people who were not in the room. Load the **`technical-writing`** skill on top of this one and follow it for every sentence you write here — it sets the sentence length and the active voice. This skill governs *what belongs in a PRD*; `technical-writing` governs *how each sentence reads*. The PRD is where the product's ubiquitous language is **chosen**, so the terms you pick here are the terms every design doc, ticket, plan, and report must reuse.

**A diagram goes in `diagrams/`, never inline.** When a product area or a user flow needs a picture, load the **`diagrams`** skill and follow it. The PRD's product-only rules still hold inside the picture: no mechanism, no implementation name.

**The PRD composes five kinds of note; it does not contain them.** A goal, a non-goal, a persona, a problem, and a success metric are each their own note under `<docs root>/product/`, because a feature, a design doc, a ticket, and the business plan all point at them, and each one has a state of its own. **Load the `product-intent` skill** and follow it for every one you write or change. Sections 2, 3, 4, and 7 of this document are one line per note. Sections 1, 5, and 6 are the PRD's own prose, and they stay prose.

**Each term is defined in the glossary, not in the PRD.** Load the **`glossary`** skill and follow it: it holds the entry shape, the link form, and the rule that whoever coins a term writes its entry in the same step. The PRD states the requirement and never repeats a definition.

## Product-only: no tickets, no code, no commerce

The PRD describes **product requirements**, nothing else. It is the **highest document**: the
business plan and every feature note link it, and it links neither of them back. The `product-docs`
skill holds the table of which document owns which fact — read it before you write a section.

Never include:

- **Money** — no price, plan, discount, cost, margin, market size, or revenue target, and no claim
  that the product beats a named competitor. The business plan owns all of it and links the PRD for
  the behavior behind it. A requirement that a customer can *choose* a plan is product; what that
  plan costs is not.

- **Ticket or tracking references** — no ticket IDs, roadmap epics, sprint/milestone names, "forthcoming (SW-…)", "resolved in …", or status-of-work notes. Whether something is built yet is tracked elsewhere; the PRD states the requirement, not its delivery state.
- **Code or implementation detail** — no file paths, function/module names, class or component names, API routes, schema/field names, or code snippets.
- **Technology, vendor, or library names** — no engines, frameworks, databases, protocols, or third-party services as the *mechanism*. Describe the capability, not the tool (e.g. "scheduled triggers run server-side and survive restarts", not "Temporal schedules on Postgres"). A concrete external platform is fine only when it is part of the product surface the user sees (e.g. "publish to a connected social account"), not when it is an internal implementation choice.
- **Migration / history notes** — no "supersedes the earlier model", "this replaces the hand-rolled …", "revised", or changelog prose inside requirements. State the current requirement in the present tense as if it were always the target.

If a requirement can only be phrased by naming how it's built, which ticket delivers it, or what it earns, it belongs in a design doc, a ticket, or the business plan. Re-express it as an observable product behavior, or leave it out.

Cross-references to sibling **product specifications** (a design doc, content-model spec) are allowed — those describe the product, not the code or the work.

## Describe how the product works — cohesively and positively

Two rules govern how the behavior sections read:

**Cohesive, by product area — not a per-feature checklist.** Organize section 5 into a handful of **product-area subsections** (Content, Workspace, Outputs, AI, Publishing, …). Each subsection is a **cohesive description in prose** of how that part of the product works and how it connects to the others — a few short paragraphs telling one coherent story, not a list of atomic "the system shall X" line items. Describe the product as a set of interacting parts, so a reader understands the *shape* of each area, not just an inventory of capabilities. Do not decompose an area into numbered, individually-IDed micro-requirements; let related behaviors sit together in the same paragraph. Use a bullet only when enumerating parallel items (e.g. the export formats a deck supports), not as the default unit of a requirement.

Give each subsection **one stable area-level anchor** — a short uppercase code in the heading (e.g. `### Social platforms & publishing \`SOCIAL\``) — so other specs and tickets can cite the area. That is the granularity of traceability: one code per product area, never one per sentence. Keep a code stable as its area's prose evolves; add a new code only for a genuinely new area.

**An area is not a feature.** An area is a handful of paragraphs describing one part of the product; a **feature** is one thing a customer can do, and several of them usually sit inside one area. Each feature has its own note in `<docs root>/features/`, which carries the area's anchor code in its `area` property and holds the design docs and the tickets for that feature. The **`feature`** skill governs those notes. The PRD never becomes a list of them: it keeps telling the area's story in prose, and the register in `features/` is where the inventory lives. When the PRD names a part of the product that has no feature note, open the feature rather than decomposing the area into line items.

**The area says how the parts hold together; the feature says what one customer can do.** That is the line between the two, and it is what keeps them from repeating each other. An area paragraph that could be cut and pasted into a feature note is written at the wrong altitude — raise it until it says something no single feature could say. A feature that needs a paragraph of its area repeated to make sense is a feature whose note should link the anchor instead.

**Positive framing — say what the product does.** State behavior affirmatively: describe what happens, not what doesn't, and don't define a requirement by contrast with a rejected design. A guarantee that is really about restraint gets phrased as the positive behavior that holds — "content stays on the device until the user publishes", not "content is never sent to the server without publishing"; "every output stays editable", not "rendering is never a one-way door". Drop asides like "not a separate subsystem", "no built-in deck", "rather than an ad-hoc poll" — they describe an absent alternative, not the product. (Section 3's *non-goals* are the one exception: they scope what the product isn't building **yet**, which is a scope statement, not a behavior description.)

## Format

Use the exact section order below. Keep prose tight — every sentence must add information.

```
# Product Requirements Document

**Status**: Draft | Living document | Final
**Last updated**: <date>
**Product**: <name or TBD> — <one-line description>

---

## 1. Overview

What the product is and what it does. 2–4 sentences max. End with the core product principles (bullet list, 3–5 items).

## 2. Problem statement

One line per problem note in `product/problems/`: the link, then the failure in a few words. The note holds the failure and who it hurts; the goal that answers it says what this product does about it. Critiquing a category of tool belongs in the note — a named competitor belongs in the business plan.

## 3. Goals & non-goals

### Goals
One line per goal note in `product/goals/`: the link, then the statement in a few words. A goal that is `Dropped` leaves this list and keeps its note. The statement, the problem it answers, and the metric that proves it live in the note.

### Non-goals (current scope)
One line per note in `product/non-goals/`: the link, then the exclusion in a few words. Every non-goal is listed, because `Excluded` and `Deferred` are its only two states and both are things the product is not building. A non-goal the product decides to build is deleted and replaced by a goal, so it leaves this list and gains a line in the goals list. The reason lives in the note, where it is required.

## 4. Users & personas

One line per persona note in `product/personas/`: the link, then the need in a few words. 3–6 of them. Each persona is a real usage archetype, not a demographic, and the note holds the need and the primary flow.

## 5. How the product works

Cohesive descriptions grouped into product-area subsections, each with a stable area-level anchor code in its heading (### Content `CONTENT`, ### Workspace `WORKSPACE`, ### Outputs `OUTPUTS`, …). Each subsection is a short prose narrative of how that part behaves and how it fits with the others, in present tense, from the user's vantage. Describe positively; don't decompose into atomic per-feature IDs.

## 6. Cross-cutting qualities

The qualities holding across the whole product — security, privacy/data sovereignty, offline, content fidelity, extensibility, reliability. Group by theme and describe each as a positive guarantee in prose.

## 7. Success metrics

One line per metric note in `product/metrics/`: the link, then the target. The definition and the last measured value live in the note. A metric must be measurable, not aspirational, and a target with no definition behind it is aspirational.

## 8. Open questions

Bullet list. Concrete unresolved product decisions that block design or implementation. Remove each item once decided.
```

## Style rules

- Write behavior as "Users can X", "AI can X", or "The app does X" — present tense, from the user's vantage.
- Describe user-observable behavior, not the mechanism behind it (see "Product-only").
- Keep each product area cohesive: relate its behaviors to one another in prose rather than listing them as independent line items.
- State behavior positively. Reframe any guarantee of restraint as the positive behavior it produces.
- Non-goals must say *why* something is excluded or deferred.
- Success metrics should include a proxy for quality, not just volume.
- **A list section carries enough of each note to read past it.** `[[self-hosted-first.goal]] — the product runs with no server the user does not own.` A bare link makes the reader open a file to follow a sentence.
- **Never restate a note's reasoning in the PRD.** The list says what the product commits to; the note says why.
- Open questions name what is blocked until each is resolved, and stay product-level (a genuinely undecided product choice — not "which library" or "how to migrate").

## Updating an existing PRD

- **Edit in place; keep it whole.** The PRD is a living document, not an append log. Fold changes into the existing sections — no "changes" or "revisions" section.
- **State the new requirement as the current truth.** Rewrite the affected passage so it reads as if it were always the target. Do not narrate the change ("previously X, now Y", "supersedes …", "revised") — that history lives in version control.
- **Keep area names and anchors stable.** When an area's behavior evolves, revise the prose in place under its existing heading so inbound references stay valid. Add a new subsection only for a genuinely new product area. If a behavior is dropped, remove it and reconcile anything that referenced it — including the `area` property of every feature note that cites the anchor.
- **Keep the feature register in step.** A new part of the product earns a feature note; a dropped one has its note retired. The `feature` skill holds both.
- **Change a goal, a non-goal, a persona, a problem, or a metric in its note**, never in the PRD's list line. The line carries a few words of the note; when those words change, update both, and when the note's status changes, the line appears or disappears. A dropped goal keeps its note, because a feature may still cite what the product stopped committing to. A non-goal the product adopted is deleted instead, and every citation of it is repointed at the goal in the same change — the `product-intent` skill holds that procedure.
- **Keep the whole document consistent.** Reflect the change everywhere it lands — overview, goals, personas, related areas, success metrics, open questions — so no two sections disagree.
- **Keep the glossary in step.** The `glossary` skill says what an added, renamed, or dropped term costs — do that in the same run.
- **Bump `Last updated`** and revisit `Status`.
- **Retire resolved open questions.** Delete them from section 8 rather than marking them resolved in place.
- **Fix drift while you're there.** Strip any ticket, code, technology, or migration references you encounter, and rewrite atomic-checklist or negatively-framed passages into cohesive, positive prose.

## After drafting or updating

Ask the user:
1. Are there personas or failure modes missing?
2. Are any non-goals actually in scope?
3. Which open questions are already decided and can be removed?
4. Did any passage drift into implementation/ticket detail, an atomic-feature checklist, or negative "what it doesn't do" framing?
5. Does every term this PRD introduces have a glossary entry, linked at its first use here?
