---
name: ts-clean
description: Rules for writing clean TypeScript in any file. INVOKE THIS SKILL before writing or editing ANY `.ts`/`.tsx` file — a service, domain module, hook, utility, config, or React component. Enforces one module per file named after its primary export (index files stay re-export barrels), static top-of-file imports (no `await import()` / `require()` inside a function unless it is a justified code-splitting, SSR, or optional-dependency exception), self-documenting code over comments (delete comments that restate the code or banner a section; keep only the *why*, links to a spec or ticket, non-local warnings, public API docs, and `TODO`s with a concrete referent), and configuration extracted into `.config.ts` modules that are the only place `process.env` is read — every required variable validated at load and throwing by name when missing, optional ones given an explicit typed default, and no secret given a fallback. Framework-agnostic — for React files, load `react-clean` as well.
---

# Clean TypeScript

Rules that apply to **every** TypeScript file, whatever it contains — a service, a domain
module, a utility, a config, a test, or a React component. They are about how a module is
shaped and how it reads, not about any framework.

For React components and hooks, these rules still apply — load the **`react-clean`** skill
on top of them for the component-specific rules (effects, props, data access, composition).

## Rule 1 — One module per file, named after what it exports

- **One primary export per file**, and name the file after it: `userService.ts` exports
  `userService`, `parseInvoice.ts` exports `parseInvoice`, `UserCard.tsx` exports `UserCard`.
- Additional exports are fine only when they are *part of the same thing* — the types,
  constants, or a tiny private helper that only this export uses. The moment a second
  export grows its own logic, its own state, or a second consumer, move it to its own file.
- **`index.ts` is a re-export barrel only.** Never put implementation code in it. A barrel
  that defines behavior hides that behavior from anyone reading the directory listing.
- A file whose name doesn't tell you what's inside (`utils.ts`, `helpers.ts`, `misc.ts`) is
  a bag, not a module. Split it into named modules by responsibility.

## Rule 2 — Static imports at the top of the file

**All imports live at the top of the file as static `import` statements.** No
`await import()`, no `require()` inside a function, no lazily pulling a module in on first
use.

```ts
// ❌ Avoid — import hidden inside the function
async function exportRows(rows: Row[]) {
  const { writeXlsx } = await import('./xlsx');
  return writeXlsx(rows);
}

// ✅ Good — dependency visible at the top of the file
import { writeXlsx } from './xlsx';

async function exportRows(rows: Row[]) {
  return writeXlsx(rows);
}
```

Why: top-level imports make a module's dependencies readable at a glance, keep them
statically analyzable (tree-shaking, type-checking, refactors, dead-code detection), and
avoid turning a synchronous function into an async one just to load code. An in-function
import is also a common way to paper over a circular dependency — fix the cycle instead by
moving the shared piece into its own module.

**The exceptions — a dynamic import is the right tool when:**

- **Route- or module-level code splitting** for a genuinely heavy dependency that most
  sessions never reach (a rich-text editor, a chart or PDF library). In React this is
  `const Editor = lazy(() => import('./Editor'))`.
- **A heavy dependency used on a rare path** — an export-to-XLSX helper behind a rarely
  clicked button — where the bundle savings are real and measurable.
- **Environment-only modules** that must not load in the other environment: a browser-only
  module touching `window` at import time in an SSR app, or a Node-only module in code that
  also runs in the browser.
- **Optional/conditional dependencies** that may legitimately be absent at runtime.

When you take an exception, keep the dynamic import at module scope where possible
(`const X = lazy(() => import('./X'))`), not buried in a handler, and add a one-line comment
saying *why* it is dynamic. "It might be faster" is not a reason — deferring a 3 kB utility
costs clarity and buys nothing.

## Rule 3 — Let the code explain itself; comment only what code can't say

**Default to zero comments.** A comment that restates the code is noise that rots the moment
the code changes. When you feel the urge to explain a line, first try to make the line not
need explaining: rename the variable, extract the expression into a named constant, or pull
the block into a function whose name *is* the comment.

```ts
// ❌ Avoid — comments narrating what the code already says
export function getShipping(order: Order) {
  // check if the order is eligible for free shipping
  const e = order.total > 50 && order.items.length > 0;

  // return the cost
  return e ? 0 : STANDARD_SHIPPING_COST;
}

// ✅ Good — names carry the meaning, no comments needed
const FREE_SHIPPING_THRESHOLD = 50;

export function getShippingCost(order: Order) {
  const qualifiesForFreeShipping =
    order.total > FREE_SHIPPING_THRESHOLD && order.items.length > 0;

  return qualifiesForFreeShipping ? 0 : STANDARD_SHIPPING_COST;
}
```

**Delete on sight:**

- Comments that paraphrase the next line (`// set loading to true`, `// map over the items`,
  `// return the result`).
- Section banners inside a file or function (`// --- state ---`, `// helpers`,
  `// ==== types ====`). If a module needs internal chapters, split it (Rule 1).
- Commented-out code. Git remembers it; the file shouldn't.
- Changelog and attribution notes (`// added by ...`, `// updated 2026-01-14`,
  `// was: useState`). That's what history is for.
- Redundant JSDoc on a typed function — `@param id The id` adds nothing over `id: string`.
- Explanations of the language or framework itself (`// await resolves the promise`,
  `// useEffect runs after render`).

**Keep — these carry information the code genuinely cannot:**

- **Why, not what** — a non-obvious tradeoff, a workaround, or a constraint from outside the
  file: `// Safari fires resize before layout settles, so we read on the next frame`.
- **Links to a source of truth** — a spec, ticket, or upstream bug:
  `// See CORE-1421: the API returns cents, not dollars`.
- **A required deviation from these rules**, such as the one-line justification a dynamic
  import owes under Rule 2.
- **A genuine warning** whose violation isn't visible locally:
  `// Order matters — the provider must mount before the router`.
- **Public API docs** on an exported, reused module: a short JSDoc summary of what it's for
  and any non-obvious usage constraint — not a restatement of its parameter types.
- **`TODO`/`FIXME` with a concrete referent** — an owner, a ticket, or a condition. A bare
  `// TODO: fix this` is noise.

**Prefer these over a comment, in order:**

1. **A better name** — `qualifiesForFreeShipping` beats `// check eligibility` above `const e`.
2. **A named constant** — `FREE_SHIPPING_THRESHOLD` beats `// 50 = free shipping threshold`
   next to a magic number.
3. **An extracted function** — `connectChatSocket(roomId)` beats a block with a comment
   explaining what it connects to.
4. **A type** — a `variant: 'compact' | 'full'` union documents the allowed modes better than
   a comment listing them.
5. **A test** — the clearest description of intended behavior is an assertion that fails when
   it breaks.

When you do write a comment, put it above the code it explains, keep it to a sentence, and
state the *reason*. If you can't finish the sentence without describing what the next line
does, delete the comment and fix the name instead.

## Rule 4 — Configuration lives in `.config.ts`; environment variables are validated where they're read

**A value that *configures* behavior rather than expressing it belongs in a `.config.ts`
module** — base URLs, timeouts, retry counts, page sizes, limits, feature flags, credentials,
anything that changes per environment or per deployment. Code that uses a configuration value
reads it from a config module; it does not define it inline and never reaches for
`process.env` itself.

- Name the file after what it configures and export one frozen config object — Rule 1 applies:
  `stripe.config.ts` exports `stripeConfig`, `pagination.config.ts` exports `paginationConfig`.
  Keep it beside the feature it configures, not in a global `constants.ts` bag.
- A value used in exactly one module and derived from nothing can stay a named constant at the
  top of that module (`FREE_SHIPPING_THRESHOLD` above). Promote it to a `.config.ts` the moment
  a second consumer appears, it differs per environment, or it comes from `process.env`.
- **`process.env` is read only inside `.config.ts` files.** One place then lists everything the
  app needs from its environment, and the rest of the codebase depends on typed values instead
  of on string keys that may not exist.

**Every required environment variable is checked, and a missing one throws with its name.**
Never `process.env.X!`, never `?? ''`, never a silent fallback. The check runs at module load,
so a misconfigured deploy fails at startup rather than on the first request that happens to
need the value.

```ts
// ❌ Avoid — env read inline, unchecked, next to a magic number
export async function chargeCard(amount: number) {
  const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);
  return stripe.charges.create({ amount, currency: 'usd' }, { timeout: 15000 });
}
```

```ts
// ✅ stripe.config.ts — required values validated, defaults explicit
import { requireEnv } from './requireEnv';

export const stripeConfig = {
  secretKey: requireEnv('STRIPE_SECRET_KEY'),
  currency: 'usd',
  requestTimeoutMs: 15_000,
} as const;
```

```ts
// ✅ requireEnv.ts — its own module, because several config files use it
export function requireEnv(name: string): string {
  const value = process.env[name];

  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }

  return value;
}
```

- **Optional variables get an explicit, typed default** — and coercion is validated too, since
  every env var arrives as a string: `Number(process.env.PORT)` silently yields `NaN`, and
  `Boolean(process.env.DEBUG)` is `true` for the string `'false'`. Parse through a small
  `optionalNumberEnv` / `booleanEnv` helper that rejects garbage, or compare explicitly
  (`process.env.DEBUG === 'true'`).
- **Never default a secret or a connection target.** A friendly fallback for `DATABASE_URL` or
  `API_KEY` turns a misconfigured production deploy into a silent connection to the wrong
  place. Those are required, and required means throw.
- If the project already uses a schema validator (Zod, Valibot, TypeBox), validating the whole
  `process.env` object once in a single config module satisfies this rule — the requirement is
  that something fails loudly at startup, not a particular helper.
- **Only variables the framework marks public** (`VITE_`, `NEXT_PUBLIC_`, …) may appear in a
  config module that client code imports. Secrets belong in a server-only config module — in a
  TanStack Start app that means a `*.config.server.ts` file; see `clean-tanstack-start` Rule 3.

## Checklist before finishing a file

- [ ] One primary export, and the file is named after it — no grab-bag `utils.ts`, no
      implementation inside an `index.ts` barrel.
- [ ] All imports are static and at the top of the file — any dynamic import is one of the
      Rule 2 exceptions, sits at module scope, and says why in a comment.
- [ ] No comment restates the code, banners a section, or preserves dead code — every
      surviving comment explains a *why* the code can't, and the names carry the rest.
- [ ] Configuration values live in a `.config.ts` module named after what they configure — no
      per-environment value or `process.env` read anywhere else.
- [ ] Every required environment variable throws by name when missing; optional ones have an
      explicit typed default, coercion is validated, and no secret has a fallback.
- [ ] For a React file, `react-clean` has been applied on top of this checklist.
