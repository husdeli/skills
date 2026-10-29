---
name: design-system
description: Rules for the project's design system — its tokens (color, spacing, radius, type, shadow, motion) in one place, ideally W3C DTCG JSON built by Style Dictionary into CSS variables, a Tailwind theme, the Mantine theme, and native outputs; its shared components, listed in a `design-system.md` catalog every agent reads before building UI; and a design board (Storybook, separate from the app) where anyone can see all of it. INVOKE THIS SKILL before you plan, build, mock up, or review anything a user sees; before you add or change a shared component, a design value, a style, a theme, or a token file; and before you set up or change the design board. Enforces the catalog read first, the project's component over Mantine's over a new one, project-wide component styling in the theme, a catalog and a story in the same change as a new shared component, semantic tokens only with no raw value in code, generated outputs never edited by hand, modes as token sets under the same names, WCAG AA in every mode, and a board that renders the app's own theme and tokens. Builds on the `web-stack` skill — load that one too.
---

# Design system

The design system is everything the interface is built from, kept where every agent and every
person can find it:

| Part | What it is | Where it lives |
| --- | --- | --- |
| Tokens | Every design decision — color, spacing, radius, type, shadow, motion — as a named token | DTCG JSON under `tokens/` with the design-tokens layer, else the Mantine theme |
| Components | The shared presentational components any feature can use | Top-level `components/` (`clean-fullstack-architecture`) |
| Catalog | One entry per shared component: what it is for, and when not to use it | `design-system.md` at the work root |
| Design board | A Storybook showing the catalog, every token, and every component in every state | `.storybook/`, with a stories file beside each shared component |

Each fact has one owner. The token source owns values, the component's props type owns its
variants, the catalog owns when to use it, and the board shows all three without copying any.

## Rule 1 — Read the catalog before building UI

Before you plan, build, mock up, or review anything a user sees, **read `design-system.md`** and
build from what it lists.

- **A planner names the components** each UI work item builds on, by their catalog names, and
  names any new shared component the work adds.
- **A coding agent uses a catalog component** wherever one does the job, and reports a component
  it needed and the catalog lacked.
- **A mockup uses the catalog's components and the tokens** (`frontend-design`), so the screen the
  user signs off is one the code can build.
- **No catalog yet** — the project has shared components but no `design-system.md` — is a gap.
  Read the top-level `components/` instead, and say the catalog is missing; `/design-system board`
  drafts one.

## Rule 2 — The project's component, then Mantine's, then a new one

Pick the first rung that does the job.

| Rung | Use | When |
| --- | --- | --- |
| 1. A catalog component | The project's shared component, through its props | It covers the job, perhaps with a variant it already has |
| 2. A Mantine component | Styled through its own props (`variant`, `color`, `size`, `radius`) | No catalog component covers it |
| 3. A new shared component | Composed from Mantine and tokens in top-level `components/` | The same composition is needed in a second place, or the design calls for a component Mantine does not ship |

- **Never bypass a catalog component** with the Mantine component it wraps, and never write a
  second component for a job a catalog entry already does. Extend the entry with a variant
  instead, within `react-clean`'s props ceiling.
- **A project-wide look goes in the theme.** Set a Mantine component's project defaults —
  `defaultProps`, `classNames`, `vars` — in `theme.components`, not at every call site. A wrapper
  whose only job is to set default props is a `theme.components` entry instead.
- **A feature keeps a component to itself** under `features/<name>/components/` only while no
  other feature needs it. When a second feature does, move it to the top-level `components/` and
  add it to the catalog and the board.
- **Shared components are presentational.** Props in, markup out — no query, no service, no
  router (`clean-fullstack-architecture`). That is also what lets the board render one alone.

## Rule 3 — The catalog lists every shared component

`design-system.md` at the work root opens with a header that links the board and names the token
source, then holds one entry per shared component:

```markdown
# Design system

Board: https://design.example.com — run it locally with `bun run board`.
Tokens: `tokens/` (built by `bun run tokens`).

## Components

### StatusBadge — `src/components/StatusBadge.tsx`

For: the state of a record in a list or a header — published, draft, failed.
Not for: a count or a tag the user can remove; use Mantine's `Badge` or `Pill`.
```

- **Each entry holds a name, a path, one line on what it is for, and one on when not to use it**,
  naming what to use instead. Props and variants are not listed: the props type and the stories
  own them.
- **The change that adds, renames, or removes a shared component updates its entry** and its
  stories in the same commit. A catalog that lags the code misleads every agent that reads it.
- **Patterns get entries too** once a composition repeats — an empty state, a page header, a form
  layout — under a `## Patterns` heading, pointing at the component or the container that holds
  it.

## Rule 4 — Three tiers, and code uses the semantic one

| Tier | Holds | Examples | Who reads it |
| --- | --- | --- | --- |
| Primitive | The raw palette and scales — what values exist | `blue-600`, `gray-50`, `space-4`, `radius-2`, `font-size-3` | Semantic tokens only |
| Semantic | What a value is for — the intent | `color.bg.surface`, `color.text.muted`, `color.action.primary`, `color.border.danger`, `space.inset.md`, `radius.control`, `shadow.overlay`, `motion.duration.fast` | All code |
| Component (optional) | One component's decision, as an alias of a semantic token | `button.primary.bg` → `{color.action.primary}` | That component's own theme entry or file |

**Code — and every agent writing it — uses semantic tokens only.** A semantic name carries the
intent ("muted text"), so the right token is the one whose name says what the element is, and an
agent picks it from the name instead of guessing a shade. And theming — dark mode, a second brand
— becomes remapping semantic tokens to other primitives, with no component touched.

- **Name a semantic token for its role, never its look**, as `category.property.role`:
  `color.text.danger`, not `color.red-text`. Repainting the brand renames no semantic token.
- **Every semantic token has a `$description`** saying when to use it ("Secondary text: captions,
  helper text, timestamps"). The name and the description are what an agent chooses by.
- **Choose from the semantic set, and grow it on purpose.** Before you style an element, read the
  semantic tokens and pick the one whose role matches. When none matches, add a semantic token —
  named for the role, aliasing a primitive, with its description — and never reach for the
  primitive instead.
- **A primitive in code is a defect.** `bg-blue-600`, `c="blue.6"`, `theme.colors.blue[6]`, and
  `var(--color-blue-600)` each skip the tier that carries intent. The generated Tailwind theme
  holds only semantic names, so a primitive class does not compile; Mantine still needs the
  primitive hues to build its role colors, so a primitive there is a review finding ([the token
  pipeline](./references/token-pipeline.md)).
- **A component token aliases a semantic token, never a primitive**, and only that component
  reads it. Add one when a component's decision must be retunable on its own; most projects need
  few or none.
- **A color scale has ten steps — `50`, then `100` through `900`**, because the Mantine theme takes a
  ten-shade tuple per color (`50` is shade 0, `900` is shade 9).
- **Reach tokens through the theme the code already uses.** A Mantine prop with a semantic key
  (`color="primary"`, `c="dimmed"`, `radius="control"`, `shadow="overlay"`), a Tailwind utility
  from the semantic theme (`bg-bg-surface`, `text-text-muted`, `border-border-danger`,
  `rounded-control`, `p-inset-md`, `duration-(--motion-duration-fast)`), or `var(--…)` in CSS. The
  doubled word in a Tailwind color is the price of a name that says which property it is for, and
  it makes a mismatch such as `text-bg-surface` visible at a glance.
- **No raw value in a component or a stylesheet.** No hex, `rgb()`, or `hsl()` color, no pixel or
  rem spacing, size, or radius, no shadow, no font stack, and no duration or easing — not in a
  `style` prop, a CSS file, or an arbitrary Tailwind value (`bg-[#1e40af]`, `p-[13px]`). Only `0`,
  `100%`, `auto`, and a `1px` hairline stand on their own.
- **A value the tokens lack is a new token.** Add it at the right tier, then use it.
- **Tailwind never redefines a token, and Mantine never holds one the source lacks.**
- **With the design-tokens layer, every theme is generated.** The DTCG source, the Style
  Dictionary build, its outputs — CSS variables, the Tailwind theme, the Mantine theme, board
  data, and native outputs — and the rule that no generated file is edited by hand are in
  **[the token pipeline](./references/token-pipeline.md)**. Read it before you touch a token file.

## Rule 5 — A mode is a token set under the same names

- **Light, dark, and any brand theme are sets of semantic values under the same names.** The
  primitives do not change between modes; the semantic tokens point at different primitives. A
  second brand is a new semantic set, and a theme change that has to edit a component means the
  component named a primitive.
- **The variable switches, not the component.** A component never reads the color scheme to pick
  a value (`colorScheme === 'dark' ? '#fff' : '#000'`). Mantine's `data-mantine-color-scheme`
  attribute on `<html>` is the mode's selector.
- **Every text and surface pair passes WCAG AA in every mode**: 4.5:1 for body text, 3:1 for large
  text and for the edges of controls and focus rings.
- **Motion is tokens too.** Durations, easings, and transitions are `motion.*` tokens, and an
  animation picks one (`react-animations`).

## Rule 6 — The design board shows the whole system, apart from the app

- **The board is a Storybook with its own server and its own static build**, deployed on its own
  URL. It is never a route in the app, and nothing in the app imports from it.
- **It shows three things**: the catalog, rendered from `design-system.md`; every token, rendered
  from the token build or the Mantine theme, never a hand-typed list; and every shared component,
  in every variant and state, in light and dark.
- **It renders the app's own theme.** One `MantineProvider` with the app's theme and the app's
  global stylesheet, so a component looks on the board the way it looks in the app.
- **Every shared component has a `<Name>.stories.tsx` beside it.** A new shared component lands
  with its stories, and `bun run board:build` passes.
- **Publishing it is the owner's call.** Deploying the board publishes the design system; never
  deploy it without the user's go-ahead.

The setup, the pages, and how a story is written are in **[the board
reference](./references/design-board.md)**. Read it before you set up the board or write a story.

## Checklist before finishing a change a user will see

- [ ] The catalog was read, and every component used is the lowest rung that does the job.
- [ ] No catalog component was bypassed or duplicated; project-wide defaults sit in `theme.components`.
- [ ] A new or changed shared component has its catalog entry and its stories in the same change.
- [ ] Code names semantic tokens only — no primitive, no raw value, no arbitrary Tailwind value.
- [ ] Every new semantic token is named for its role and has a `$description`; every component
      token aliases a semantic one.
- [ ] A new value is a token in the one source; no generated file was edited by hand.
- [ ] Each mode defines the same semantic names, and no component branches on the color scheme.
- [ ] Every text and surface pair the change touches passes WCAG AA in every mode.
- [ ] With a board, `bun run board:build` passes.
