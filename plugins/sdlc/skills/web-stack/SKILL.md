---
name: web-stack
description: "The default stack for a web project — TypeScript on TanStack Start with TanStack Query, TanStack Form, Zod, Mantine with Tailwind CSS, Postgres through Drizzle, Better Auth, Bun, Vitest, Playwright, and Biome — and the rule for when a project already chose otherwise. INVOKE THIS SKILL before you add a dependency to a web project, start a new web project or a layer it does not have yet (a database, auth, forms, UI components, tests, lint), plan or review a change that does either, or decide a library question in an interview. Enforces one library per layer, the project's existing choice over the default, the default over a new pick, no migration nobody asked for, and the integration rules that keep these libraries working together."
---

# Web stack

The libraries a web project is built with when nothing in the project says otherwise. The other
coding skills say how the code is shaped. This one says which library fills each layer.

## Rule 1 — The project's choice wins, then the default, then a decision

Read the work root's `package.json` and lockfile before you name a library. For each layer:

| The work root | Use |
| --- | --- |
| Already fills the layer with a library | That library, even when it is not the default. Never migrate it unless the request asks for the migration. |
| Does not fill the layer yet | The default from Rule 2. |
| Needs something the default cannot do | A library choice. Raise it as a decision, with the default's limit as the reason. |

- **One library per layer.** Do not add a second form library, a second component library, or a
  second test runner next to the one the project has.
- **A library outside this table for a layer the table covers is a deviation.** A planner names
  it as an open question, a reviewer flags it as **major**, and the coding agent stops and reports
  it as a blocker.
- **Versions are not pinned here.** Use the version the lockfile pins. For a new dependency, use
  the current stable release and read its official docs for that version.

## Rule 2 — The default stack

| Layer | Default | Notes |
| --- | --- | --- |
| Language | TypeScript, `strict` on | `ts-clean` governs every file. |
| Framework | TanStack Start (React, TanStack Router file routes) | `clean-tanstack-start` governs server code, `react-clean` governs components. |
| Server state | TanStack Query | Components reach it through feature hooks (`clean-fullstack-architecture`). |
| Validation | Zod | One schema per input, shared by the form and the server function. |
| Forms | TanStack Form | Validates with the Zod schema directly. |
| UI components | Mantine | Interactive components: inputs, buttons, modals, menus, notifications. |
| Styling | Tailwind CSS | Layout, spacing, and one-off adjustments around Mantine components. |
| Database | Postgres | |
| Data access | Drizzle ORM, with drizzle-kit for migrations | |
| Auth | Better Auth, on the Drizzle adapter | |
| Runtime and packages | Bun | `bun.lock` is committed. |
| Unit and integration tests | Vitest | |
| End-to-end tests | Playwright | Only where the end-to-end decision allows one (`test-strategy`). |
| Lint and format | Biome | |

## Rule 3 — Mantine and Tailwind share the page

- **A Mantine component first, Tailwind around it.** Build a control from Mantine and style it
  through its own props (`variant`, `color`, `size`, `radius`) before anything else. Use Tailwind
  for the layout around it and for elements Mantine has no component for. Never rebuild with
  Tailwind a control Mantine already ships.
- **Order the cascade layers.** Import Mantine's layered stylesheet
  (`@mantine/core/styles.layer.css`) and declare the order once in the global stylesheet, so
  Tailwind's reset sits below Mantine and its utilities sit above:

  ```css
  @layer theme, base, mantine, components, utilities;
  ```

  Never fix a cascade conflict with `!important`.
- **The Mantine theme holds the design tokens.** Colors, radii, spacing, and fonts are defined
  once in the Mantine theme. Tailwind's theme refers to the CSS variables Mantine emits
  (`--mantine-color-*`) and never redefines a token.
- **Restyle a Mantine part through `classNames`.** Pass Tailwind classes to the part by name.
  Never target Mantine's internal class names from a stylesheet.
- **The root route sets Mantine up once:** `MantineProvider` with the theme, and
  `ColorSchemeScript` in the document head so the server-rendered color scheme matches the client.
  The PostCSS config uses `postcss-preset-mantine`.

## Rule 4 — One schema from the form to the database

- **A Zod schema in a client-safe module** (a plain `.ts` file, per `clean-tanstack-start`)
  defines each input. TanStack Form validates with it, and the server function's input validator
  parses with the same schema. A schema written twice drifts.
- **The server parses again.** A form's validation helps the user. The server function's
  validation protects the data, because the endpoint can be called without the form.
- **The database schema is Drizzle's**, in TypeScript under the server-only data layer. A Zod
  schema describes an input, and a Drizzle table describes a row. Map between them in the
  adapter, never by passing a row to a client.

## Rule 5 — Data, auth, and configuration stay server-side

- **The Drizzle client lives in a `.server.ts` module.** Its connection string is read in a
  `.config.server.ts` module and validated at load (`ts-clean` Rule 4).
- **Migrations are generated and committed.** Generate them with `drizzle-kit generate`, review
  the SQL, and apply them with `drizzle-kit migrate`. Never run `drizzle-kit push` against a shared
  or production database.
- **Better Auth owns sessions.** Mount its handler on one server route (`/api/auth/$`), keep its
  tables in the Drizzle schema through its CLI, and read the session in every private server
  function — the route guard is not the data boundary (`clean-tanstack-start`).
- **Secrets never reach a client module**: the auth secret, the database URL, and every provider
  key.

## Rule 6 — Tooling runs through `package.json` scripts

- **Run every check through a script**: `bun run test`, `bun run lint`, `bun run typecheck`, and
  `bun run e2e`. An agent reads these scripts for the project's check commands.
- **`bun test` is not Vitest.** It starts Bun's own test runner. The `test` script calls `vitest`,
  so run it as `bun run test`.
- **Biome replaces ESLint and Prettier.** One `biome.json` at the work root, and `biome check`
  for lint and format together. Do not add ESLint or Prettier next to it.
- **Playwright starts the app itself** through its `webServer` setting, so an end-to-end run needs
  no server already running.
