---
name: ts-clean
description: Rules for writing clean TypeScript in any file. INVOKE THIS SKILL before writing or editing ANY `.ts`/`.tsx` file — a service, domain module, hook, utility, or config file. Enforces one module per file named after its primary export (index files stay re-export barrels), dot-suffixed names for the modules that carry an architecture role (`user.service.ts`, `user.repository.ts`, `user.dto.ts`) while plain modules keep plain names, static top-of-file imports (no `await import()` / `require()` inside a function outside the listed code-splitting, SSR, and optional-dependency exceptions), self-documenting code over comments (at most one or two per file, one sentence each, keeping only a *why* that stays verifiable — never a file path, a line number, a finished ticket, or a past refactor), and configuration in `.config.ts` modules that are the only place `process.env` is read — required variables validated at load and throwing by name, optional ones given a typed default, secrets never defaulted. Framework-agnostic.
---

# Clean TypeScript

Rules for **every** TypeScript file — service, domain module, utility, config, or test. They
govern how a module is shaped and how it reads, not any framework.

## Rule 1 — One module per file, named after what it exports

- **One primary export per file**, and name the file after it: `parseInvoice.ts` exports
  `parseInvoice`, `UserCard.tsx` exports `UserCard`, `user.service.ts` exports `UserService`.
- Additional exports are fine only when they are *part of the same thing* — the types,
  constants, or a tiny private helper that only this export uses. Once a second export grows
  its own logic, its own state, or a second consumer, move it to its own file.
- **`index.ts` is a re-export barrel only.** Never put implementation code in it — a barrel
  that defines behavior hides that behavior from the directory listing.
- A file whose name doesn't tell you what's inside (`utils.ts`, `helpers.ts`, `misc.ts`) is a
  bag, not a module. Split it into named modules by responsibility.

### Dot notation for the modules that carry an architecture role

- **A module that fills a role the architecture names is called `<subject>.<role>.ts`** —
  `user.service.ts`, `user.repository.ts`, `user.adapter.ts`, `user.dto.ts`, `user.model.ts`,
  `stripe.config.ts`. The subject says what the module is about, the suffix says which layer it
  belongs to.
- The export keeps its own natural name; the file name just spells the same thing in two parts.
  `user.service.ts` exports `UserService`, `user.repository.ts` exports `UserRepository`,
  `user.dto.ts` exports the `User*Dto` types. Rule 1 holds unchanged.
- **Not for everything.** A plain module keeps a plain name — `parseInvoice.ts`,
  `formatCurrency.ts`, `useUser.ts`, `UserCard.tsx`. The suffix is for the kinds a reader has to
  place in the architecture to understand the file, and a role exists only if the architecture
  defines it.
- **Never invent a role to earn a suffix.** `user.helpers.ts`, `user.utils.ts`, and
  `user.manager.ts` are the bag from the bullet above with a dot in it. Split by responsibility
  instead.
- **One role per file.** A name that would need `.service.repository.ts` is describing two
  modules. A framework may stack its own marker on top of the role — an environment or boundary
  suffix such as `stripe.config.server.ts` — and that is a different axis, not a second role.

Why: the suffix turns a directory listing into a layer map, keeps one resource's files together
when sorted (`user.dto.ts`, `user.repository.ts`, `user.service.ts`), and gives tooling — lint
rules, import boundaries, codegen — a glob to match a layer on.

## Rule 2 — Static imports at the top of the file

**All imports live at the top of the file as static `import` statements.** No `await import()`,
no `require()` inside a function, no lazily pulling a module in on first use.

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

Why: top-level imports make a module's dependencies readable at a glance, keep them statically
analyzable (tree-shaking, type-checking, refactors, dead-code detection), and avoid turning a
synchronous function async just to load code. An in-function import also papers over a circular
dependency — fix the cycle instead, by moving the shared piece into its own module.

**The exceptions — a dynamic import is the right tool when:**

- **Route- or module-level code splitting** for a heavy dependency most sessions never reach (a
  rich-text editor, a chart or PDF library), loaded lazily at the split point.
- **A heavy dependency on a rare path** — an export-to-XLSX helper behind a rarely clicked
  button — where the bundle savings are measurable.
- **Environment-only modules** that must not load in the other environment: a browser-only
  module touching `window` at import time in an SSR app, or a Node-only module in code that also
  runs in the browser.
- **Optional/conditional dependencies** that may be absent at runtime.

When you take an exception, keep the dynamic import at module scope where possible
(`const X = lazy(() => import('./X'))`), not buried in a handler, and add a one-line comment
saying *why* it is dynamic. "It might be faster" is not a reason — deferring a 3 kB utility costs
clarity and buys nothing.

## Rule 3 — Let the code explain itself; comment only what code can't say

**Default to zero comments.** A comment that restates the code is noise that rots the moment the
code changes. Someone else maintains every line you write, and a comment is a second thing they
must keep true. When you want to explain a line, first make the line not need explaining: rename
the variable, extract the expression into a named constant, or pull the block into a function
whose name *is* the comment.

**The budget is hard: at most one or two comments in a file, one sentence each, never more than
two lines.** A comment that needs a paragraph is a design problem — fix the code instead. If you
are about to add a third comment, you are narrating; delete them and improve the names.

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

- Comments paraphrasing the next line (`// set loading to true`, `// map over the items`).
- Section banners inside a file or function (`// --- state ---`, `// ==== types ====`). If a
  module needs internal chapters, split it (Rule 1).
- Commented-out code. Git remembers it; the file shouldn't.
- Changelog and attribution notes (`// added by ...`, `// updated 2026-01-14`, `// was: useState`).
- **History of work already done** — a finished ticket, a pull request, a commit, a migration, a
  past refactor (`// added for CORE-1421`, `// part of the auth rewrite`, `// since we moved off
  Redux`). The reader cannot check it and cannot maintain it. If the constraint still holds,
  state the constraint; if it no longer holds, the comment is a lie.
- **Pointers into the codebase** — a file path, a line number, a directory, or "see the other
  service". Files move and lines shift, so the pointer is wrong within a month. Let the import
  or the call site show the relationship.
- **Internals of another module** — how a caller behaves, what a service does inside, what shape
  a downstream function expects. That is the other module's job to state through its types.
- JSDoc that a reader gets from the signature — `@param id The id` adds nothing over
  `id: string`, and a summary block over a well-named export adds nothing over its name. Document
  an export only when using it correctly needs a constraint the types don't carry.
- Explanations of the language or framework itself (`// await resolves the promise`).

**Keep — only these carry information the code cannot, and only when the reason is not obvious:**

- **Why, not what** — a non-obvious tradeoff, workaround, or outside constraint that stays true
  as the code around it changes:
  `// Safari fires resize before layout settles, so we read on the next frame`.
- **A required deviation from these rules**, such as the justification a dynamic import owes
  under Rule 2.
- **A warning whose violation isn't visible locally**:
  `// Order matters — the provider must mount before the router`.
- **A link to a durable external source** — a published spec section or an upstream bug — when
  the code exists only because of it: `// Workaround for webkit.org/b/253266`. An internal
  ticket, PR, or commit id is not durable and does not qualify.
- **`TODO`/`FIXME` with an open referent** — an open ticket or a stated condition
  (`// TODO: drop when the v2 endpoint ships`). A bare `// TODO: fix this` is noise.

One sentence each. State the reason, not the mechanism, and never name a file, a line, or a past
piece of work to make the point.

**Prefer these over a comment, in order:** a better name (`qualifiesForFreeShipping` over
`// check eligibility` above `const e`); a named constant (`FREE_SHIPPING_THRESHOLD` over
`// 50 = free shipping threshold`); an extracted function (`connectChatSocket(roomId)` over a
commented block); a type (`variant: 'compact' | 'full'` over a comment listing the modes); a test
(an assertion that fails when the behavior breaks).

When you do write a comment, put it above the code it explains, keep it to a sentence, and state
the *reason*. If you can't finish the sentence without describing what the next line does, delete
the comment and fix the name. Ask one question before you keep it: **will the next developer be
able to tell, a year from now, whether this is still true?** If not, it does not belong in the
file.

## Rule 4 — Configuration lives in `.config.ts`; environment variables are validated where they're read

**A value that *configures* behavior rather than expressing it belongs in a `.config.ts`
module** — base URLs, timeouts, retry counts, page sizes, limits, feature flags, credentials,
anything that changes per environment or deployment. Code that uses a configuration value reads
it from a config module; it never defines it inline and never reaches for `process.env` itself.

- Name the file after what it configures and export one frozen config object — Rule 1 applies:
  `stripe.config.ts` exports `stripeConfig`, `pagination.config.ts` exports `paginationConfig`.
  Keep it beside the feature it configures, not in a global `constants.ts` bag.
- A value used in exactly one module and derived from nothing can stay a named constant at the
  top of that module (`FREE_SHIPPING_THRESHOLD` above). Promote it to a `.config.ts` once a second
  consumer appears, it differs per environment, or it comes from `process.env`.
- **`process.env` is read only inside `.config.ts` files.** One place then lists everything the
  app needs from its environment, and the rest of the codebase depends on typed values instead of
  string keys that may not exist.

**Every required environment variable is checked, and a missing one throws with its name.** Never
`process.env.X!`, never `?? ''`, never a silent fallback. The check runs at module load, so a
misconfigured deploy fails at startup rather than on the first request that needs the value.

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
- **Never default a secret or a connection target.** A fallback for `DATABASE_URL` or `API_KEY`
  turns a misconfigured production deploy into a silent connection to the wrong place. Those are
  required, and required means throw.
- If the project already uses a schema validator (Zod, Valibot, TypeBox), validating the whole
  `process.env` object once in a single config module satisfies this rule — the requirement is
  that something fails loudly at startup, not a particular helper.
- **Only variables the framework marks public** (`VITE_`, `NEXT_PUBLIC_`, …) may appear in a
  config module that client code imports. Secrets belong in a server-only config module — in a
  TanStack Start app that means a `*.config.server.ts` file; see `clean-tanstack-start` Rule 3.

## Checklist before finishing a file

- [ ] One primary export, and the file is named after it — no grab-bag `utils.ts`, no
      implementation inside an `index.ts` barrel.
- [ ] All imports are static and at the top — any dynamic import is a Rule 2 exception, sits at
      module scope, and says why in a comment.
- [ ] The file has at most one or two comments, one sentence each — none restates the code,
      banners a section, or preserves dead code.
- [ ] No comment names a file, a line, a past ticket, a pull request, or a finished migration —
      every surviving comment states a *why* that a reader can still verify next year.
- [ ] Every module with an architecture role is named `<subject>.<role>.ts`, and no plain module
      was given a role it doesn't have.
- [ ] Configuration values live in a `.config.ts` module named after what they configure — no
      per-environment value or `process.env` read anywhere else.
- [ ] Every required environment variable throws by name when missing; optional ones have an
      explicit typed default, coercion is validated, and no secret has a fallback.
