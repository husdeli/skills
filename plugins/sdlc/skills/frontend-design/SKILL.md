---
name: frontend-design
description: "Agree the visual design of a user interface with the user before any UI code is written, by publishing a static mockup as an Artifact and iterating on it. Use when: asked to design a screen, a component, or a flow; or before implementing a request that changes what a user sees. Produces an agreed design, not production code."
---

# Frontend-design skill

Show the user what a screen will look like, and get their agreement, **before** anyone writes
the code that builds it. The output of this skill is a signed-off design, not a feature.

A design agreement costs one mockup. Skipping it costs a rewrite of working code, because the
user sees the layout for the first time only after it is built.

## What this skill is not

- **Not a design doc.** The `design-doc` skill specifies how a solution works — parts, flow,
  behavior — in prose. This skill settles what the interface looks like. A screen can need both.
- **Not the implementation.** The mockup is throwaway HTML. No live data, no business logic, no
  routing, no state management. Nothing from the mockup is copied into the codebase as-is.
- **Not for a backend change.** Run it only when the change alters what a user sees.

## When to run it

Run it when the request adds a screen, a component, a layout, a flow the user walks through, or
a visible change to any of those.

Skip it, and say in one line that you skipped it, when:

- The change is invisible to the user — a service, a query, a build script, a test.
- The change is a text edit, a copy fix, or a one-property style fix with no layout effect.
- The codebase already fixes the answer: the screen is one more row in an existing table, one
  more field in an existing form, one more item in an existing list, built from components that
  already exist.
- The user has already agreed a design for this work, in this session or in the design doc.
- The user asks to skip it. Their call, not yours.

## Process

### 1. Read before you draw

The mockup must look like it belongs to the product, so learn the product first.

- Read the docs root's `prd.md` for what the screen is for and who uses it. Read the matching
  the screen's design doc — `<docs root>/features/<feature>/<subject>.design.md` when the screen
  belongs to a feature, `<docs root>/designs/<subject>.design.md` when it does not — for the states
  and rules the screen must hold. The
  `product-docs` skill resolves the docs root — load it before you read one.
- Find the design system the codebase already has: the styling approach (Tailwind, CSS
  modules, styled components), the token file or theme config, the font stack, the spacing
  scale, the color palette, the component library, and two or three existing screens.
- **An existing design system wins.** When the project has one, the mockup uses its tokens, its
  components, and its spacing. Invent a new visual language only for a product that has none, or
  when the user asks for a new direction.
- Note what you could not find. A missing token file is a decision to raise, not to guess.

### 2. Draft the mockup

Write one static HTML file, then publish it with the `Artifact` tool so the user can open it in
a browser and click through it.

- **Load the `artifact-design` skill before you write the file**, and the `dataviz` skill as
  well when the screen carries a chart. They govern the page you publish.
- **Static only.** Placeholder data written into the markup. No fetch, no database, no auth.
- **Show every state that matters** — empty, loading, populated, error, and permission-denied
  where it applies. A design that covers only the happy path is agreed on false terms, and the
  states are where the layout usually breaks.
- **Show the real content shape.** Use plausible names, plausible lengths, and the longest label
  the product can produce. Placeholder text that is always short hides the layout that fails.
- **Show the small screen too.** The page is responsive, and the mockup says what happens to the
  layout when the viewport narrows.
- **One page, several artboards.** Put the states and the screens of a flow side by side on the
  same page, under headings, so the user compares them in one view instead of reloading.
- For an interface with many screens, or one the user will want to move things around in, use
  the `design` skill's canvas instead — it publishes the same kind of page with an editor on top.

### 3. Present it for agreement

Publish, then say what you decided and what you are unsure about. Load the `clean-writing`
skill and follow it for the message.

```markdown
## Design: [screen or feature]

[One sentence: what this screen lets the user do.]

Mockup: [artifact URL] — static, no live data.

**Shown:** [states and screens on the page]

**Decisions**
- [choice] — [why, in one line: the existing pattern it follows, or the constraint it answers]

**Open**
- [question the mockup could not answer, with your recommendation]

What do you want changed before I build it?
```

- Ask for changes. Do not ask for approval of a list of options — pick one, publish it, and let
  the user react to something concrete.
- **Iterate on the same artifact.** Republish to the same file path so the URL stays stable and
  the user keeps their tab. Never open a second URL for version two.
- **Stop only on explicit agreement.** Silence is not agreement, and "looks fine" on a mockup
  that skipped the error state is not agreement about the error state.

### 4. Hand over the agreed design

Once the user agrees, write down what was agreed, because the mockup is not the record and the
person or agent who writes the code may never open it.

- Give the implementer: the artifact URL, the states the design covers, the layout and component
  decisions, and the tokens and existing components to build from.
- Update the screen's design doc — in the feature's folder, or in `designs/` — when the project keeps design docs, so the agreed
  behavior survives the session. Follow the `design-doc` skill for that file, and record the
  artifact URL in it.
- Name what the design deliberately leaves out, so nobody reads the gap as a missing feature.

## Visual direction

Follow this only where the project has no design system to follow.

- **Pick a direction and commit to it.** Say in one line what the interface should feel like —
  dense and operational, calm and editorial, bold and consumer — and let it decide the type,
  the spacing, and the color. An interface with no direction reads as a template.
- **Type carries the hierarchy.** Choose a real type scale with visible steps and few of them.
  Size, weight, and color separate levels; boxes and rules rarely need to.
- **Space is the layout.** Use one spacing scale, and let the gaps group things. Crowding is the
  most common reason a screen reads as unfinished.
- **One accent color, used for one job.** Everything else is a neutral. Color states — error,
  warning, success — keep their conventional meaning and never carry the accent's job.
- **Contrast is not optional.** Body text meets WCAG AA against its background, in light and
  dark. State is never carried by color alone: pair it with a label, an icon, or a shape.
- **Motion is a hint, not a show.** Short transitions on what the user acted on. Respect
  `prefers-reduced-motion`.

## Rules

- **Agreement before code.** No UI implementation starts until the user agrees, or says to skip.
- **The mockup is a question, not a deliverable.** Publish early and rough rather than late and
  polished. One screen the user can react to beats three you kept refining.
- **Match the codebase before you improve it.** A better button that matches nothing on the
  neighbouring screen makes the product worse.
- **Never present a mockup as working software.** Say in the first lines that the data is fake
  and nothing is wired up.
- **Never fabricate real data.** No real customer names, no real numbers presented as measured,
  no logos or branding of a real company the product is not.
- **Cap the loop.** After three rounds with the design still moving, stop and ask the user which
  of the open questions decides it. Do not keep publishing.
