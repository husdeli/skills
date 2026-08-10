---
name: prd
description: "Create or update a product requirements document at .clean-architecture/prd.md. Use when: asked to write a PRD, draft or revise product requirements, document a new product or feature set, update an existing PRD, or maintain a living spec."
---

# PRD Skill

Write or update a product requirements document following the structure and style below.

**Where it lives.** The PRD is `.clean-architecture/prd.md`, alongside the design doc, the
roadmap, and the tickets. Create the folder if it is missing. When the project already keeps
a PRD at the root (`prd.md`/`PRD.md`), update that file in place instead — one PRD per
project, never two.

A PRD describes **what the product does and why** — the requirements, from the user's point of view. It is not an implementation plan, a project tracker, or a technical design. Keep it durable: it stays accurate as tickets come and go and as the implementation is rewritten underneath it.

A PRD is read end to end by people who were not in the room. Load the **`clean-writing`** skill on top of this one and follow it for every sentence you write here — it sets the sentence length, the active voice, and the one-term-per-concept rule. This skill governs *what belongs in a PRD*; `clean-writing` governs *how each sentence reads*. The PRD is also where the product's ubiquitous language is defined, so the terms you choose here are the terms every ticket, plan, and report must reuse.

## Product-only: no tickets, no code

The PRD describes **product requirements**, nothing else. Never include:

- **Ticket or tracking references** — no ticket IDs, roadmap epics, sprint/milestone names, "forthcoming (SW-…)", "resolved in …", or status-of-work notes. Whether something is built yet is tracked elsewhere; the PRD states the requirement, not its delivery state.
- **Code or implementation detail** — no file paths, function/module names, class or component names, API routes, schema/field names, or code snippets.
- **Technology, vendor, or library names** — no engines, frameworks, databases, protocols, or third-party services as the *mechanism*. Describe the capability, not the tool (e.g. "scheduled triggers run server-side and survive restarts", not "Temporal schedules on Postgres"). A concrete external platform is fine only when it is part of the product surface the user sees (e.g. "publish to a connected social account"), not when it is an internal implementation choice.
- **Migration / history notes** — no "supersedes the earlier model", "this replaces the hand-rolled …", "revised", or changelog prose inside requirements. State the current requirement in the present tense as if it were always the target.

If a requirement can only be phrased by naming how it's built or which ticket delivers it, it belongs in a design doc or a ticket. Re-express it as an observable product behavior, or leave it out.

Cross-references to sibling **product specifications** (a design doc, content-model spec) are allowed — those describe the product, not the code or the work.

## Describe how the product works — cohesively and positively

Two rules govern how the behavior sections read:

**Cohesive, by product area — not a per-feature checklist.** Organize section 5 into a handful of **product-area subsections** (Content, Workspace, Outputs, AI, Publishing, …). Each subsection is a **cohesive description in prose** of how that part of the product works and how it connects to the others — a few short paragraphs telling one coherent story, not a list of atomic "the system shall X" line items. Describe the product as a set of interacting parts, so a reader understands the *shape* of each area, not just an inventory of capabilities. Do not decompose an area into numbered, individually-IDed micro-requirements; let related behaviors sit together in the same paragraph. Use a bullet only when enumerating parallel items (e.g. the export formats a deck supports), not as the default unit of a requirement.

Give each subsection **one stable area-level anchor** — a short uppercase code in the heading (e.g. `### Social platforms & publishing \`SOCIAL\``) — so other specs and tickets can cite the area. That is the granularity of traceability: one code per product area, never one per sentence. Keep a code stable as its area's prose evolves; add a new code only for a genuinely new area.

**Positive framing — say what the product does.** State behavior affirmatively: describe what happens, not what doesn't, and don't define a requirement by contrast with a rejected design. A guarantee that is really about restraint gets phrased as the positive behavior that holds — "content stays on the device until the user publishes", not "content is never sent to the server without publishing"; "every output stays editable", not "rendering is never a one-way door". Drop asides like "not a separate subsystem", "no built-in deck", "rather than an ad-hoc poll" — they describe an absent alternative, not the product. (Section 3's *non-goals* are the one exception: they scope what the product isn't building **yet**, which is a scope statement, not a behavior description.)

## Format

Use the exact section order below. Keep prose tight — every sentence must add information.

```
# Product Requirements Document

**Status**: Draft | Living document | Final
**Last updated**: <date>
**Product**: <name or TBD> — <one-line description>

(optional) **Related specifications**: bullet list of sibling product-spec docs, each with a one-line scope.

---

## 1. Overview

What the product is and what it does. 2–4 sentences max. End with the core product principles (bullet list, 3–5 items).

## 2. Problem statement

What existing tools or approaches fail at, and why. Numbered list of failure modes, then one sentence on how this product inverts or solves them. (Critiquing competing tools here is fine — the positive-framing rule governs how you describe *this* product, not the alternatives.)

## 3. Goals & non-goals

### Goals
Bullet list. Each goal is one concrete, testable statement. No vague aspirations.

### Non-goals (current scope)
Bullet list. Explicit exclusions with a reason or qualifier (e.g. "v1 only", "out of scope today").

## 4. Users & personas

Markdown table: Persona | Need | Primary flow
3–6 rows. Each persona is a real usage archetype, not a demographic.

## 5. How the product works

Cohesive descriptions grouped into product-area subsections, each with a stable area-level anchor code in its heading (### Content `CONTENT`, ### Workspace `WORKSPACE`, ### Outputs `OUTPUTS`, …). Each subsection is a short prose narrative of how that part behaves and how it fits with the others, in present tense, from the user's vantage. Describe positively; don't decompose into atomic per-feature IDs.

## 6. Cross-cutting qualities

The qualities holding across the whole product — security, privacy/data sovereignty, offline, content fidelity, extensibility, reliability. Group by theme and describe each as a positive guarantee in prose.

## 7. Success metrics

Bullet list. Each metric: name, definition, and target if known. Metrics must be measurable, not aspirational.

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
- Open questions name what is blocked until each is resolved, and stay product-level (a genuinely undecided product choice — not "which library" or "how to migrate").

## Updating an existing PRD

- **Edit in place; keep it whole.** The PRD is a living document, not an append log. Fold changes into the existing sections — no "changes" or "revisions" section.
- **State the new requirement as the current truth.** Rewrite the affected passage so it reads as if it were always the target. Do not narrate the change ("previously X, now Y", "supersedes …", "revised") — that history lives in version control.
- **Keep area names and anchors stable.** When an area's behavior evolves, revise the prose in place under its existing heading so inbound references stay valid. Add a new subsection only for a genuinely new product area. If a behavior is dropped, remove it and reconcile anything that referenced it.
- **Keep the whole document consistent.** Reflect the change everywhere it lands — overview, goals, personas, related areas, success metrics, open questions — so no two sections disagree.
- **Bump `Last updated`** and revisit `Status`.
- **Retire resolved open questions.** Delete them from section 8 rather than marking them resolved in place.
- **Fix drift while you're there.** Strip any ticket, code, technology, or migration references you encounter, and rewrite atomic-checklist or negatively-framed passages into cohesive, positive prose.

## After drafting or updating

Ask the user:
1. Are there personas or failure modes missing?
2. Are any non-goals actually in scope?
3. Which open questions are already decided and can be removed?
4. Did any passage drift into implementation/ticket detail, an atomic-feature checklist, or negative "what it doesn't do" framing?
