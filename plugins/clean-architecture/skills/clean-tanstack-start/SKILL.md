---
name: clean-tanstack-start
description: Rules for organizing and securing TanStack Start server functions and server-only code. INVOKE THIS SKILL before writing or editing ANY file that defines, imports, or calls a `createServerFn` server function, touches a database or secret from application code, or lives in a TanStack Start `src/` tree. Enforces the framework's file-organization convention (`.functions.ts` wrappers, `.server.ts` server-only helpers, plain `.ts` for client-safe code), keeps server-only modules out of anything a client module can reach, forbids dynamic `await import()` of server-function modules — which defeats the build's environment shaking and can leak server logic into the client bundle — requires auth on every server function reading or writing private data (a route `beforeLoad` guard is not the data boundary), and bans `Cache-Control: public` on identity-dependent responses. Builds on the `ts-clean` skill (one module per file, static top-of-file imports) — load that one too.
---

# Clean TanStack Start

Rules for structuring server code in a TanStack Start app so that the build can reliably strip
it out of the client bundle. Apply these whenever you create, move, import, or call a server
function.

Reference: https://tanstack.com/start/v0/docs/framework/react/guide/server-functions#file-organization

## Prerequisite — `ts-clean` applies to every file here

Every rule in the **`ts-clean`** skill applies to these files too: one module per file named
after its primary export, static top-of-file imports, and self-documenting code instead of
comments that restate it. **Load `ts-clean` as well** — the rules below are the TanStack Start
layer on top of it. For components and hooks that *call* server functions, load `react-clean`
too.

## Rule 1 — Three file categories, and the suffix decides what may live inside

Every module in a Start app falls into exactly one of three buckets. The suffix is not
decoration — it is the contract that tells the next reader (and you, six months later) whether
a module is safe to import from a component.

```
src/features/users/
├── users.functions.ts   # createServerFn wrappers — safe to import anywhere
├── users.server.ts      # server-only helpers: DB queries, secrets, internal logic
└── users.schemas.ts     # client-safe: types, validation schemas, constants
```

| Suffix | Contains | May be imported from |
|---|---|---|
| **`.functions.ts`** | `createServerFn` wrappers, and nothing else of substance | Anywhere — components, routes, hooks, other server code |
| **`.server.ts`** | Server-only code: DB clients and queries, secrets, filesystem, internal business logic | Only from inside a server function handler, another `.server.ts`, or a server route |
| **`.ts`** (no suffix) | Client-safe code: types, validation schemas, pure helpers, constants | Anywhere |

```ts
// users.server.ts — server-only helper
import { db } from '~/db';

export async function findUserById(id: string) {
  return db.query.users.findFirst({ where: eq(users.id, id) });
}
```

```ts
// users.functions.ts — the network boundary
import { createServerFn } from '@tanstack/react-start';
import { findUserById } from './users.server';

export const getUser = createServerFn({ method: 'GET' })
  .validator((data: { id: string }) => data)
  .handler(async ({ data }) => findUserById(data.id));
```

- **A `.functions.ts` file is a boundary, not a home for logic.** Its handlers validate input
  and delegate to `.server.ts` helpers. When a handler grows a real algorithm, a transaction,
  or branching business rules, move that body into a `.server.ts` module and call it.
- **Validate every input.** A server function is an independently reachable endpoint, so
  `.validator()` is the type *and* trust boundary — not an optional nicety.
- `ts-clean` Rule 1 still governs the naming: one primary export per file, file named after it.
  `users.functions.ts` exporting a cohesive set of user server functions is the one sanctioned
  grouping — the moment a second domain's functions appear, give them their own file.

## Rule 2 — Server-only code never lives in a module a client file can import

The suffix is only worth something if it is honored in both directions.

- **Never import a `.server.ts` module from a component, hook, route component, or plain
  `.ts`.** The only legal importers are server function handlers, other `.server.ts` modules,
  and server routes.
- **Never put a DB client, a secret, an env var read, or a filesystem call in an unsuffixed
  `.ts`** just because "nothing client-side imports it yet". One future import turns that into
  a leaked credential or a broken build.
- **Types and schemas shared across the boundary go in the plain `.ts` file**, and both sides
  import from there. Do not re-declare a shape in a `.server.ts` file to avoid an import, and
  do not export a value from a `.server.ts` file so a component can read it.
- If a component needs something a `.server.ts` module knows, the answer is a server function
  in `.functions.ts` — never a direct import.

## Rule 3 — Import server functions statically; never `await import()` them

**Server functions are statically importable from any file, including client components.**
The build replaces each implementation with an RPC stub in the client bundle, so the handler
body never reaches the browser. That transform depends on the import being statically
analyzable.

```tsx
// ✅ Good — static import; the build swaps in an RPC stub client-side
import { getUser } from '~/features/users/users.functions';

function useUser(id: string) {
  return useQuery({
    queryKey: ['user', id],
    queryFn: () => getUser({ data: { id } }),
  });
}

// ❌ Never — the bundler can't see through this
const { getUser } = await import('~/features/users/users.functions');
```

A dynamic import hides the module from the build's environment shaking. The server function
is then not transformed into a stub, which causes bundler errors at best and ships the
handler's server logic — and whatever it imports — to the client at worst.

**This overrides `ts-clean` Rule 2's exceptions for these modules.** "It's a heavy dependency"
and "it's only used on a rare path" are not reasons to dynamically import a `.functions.ts` or
`.server.ts` module: the server code is already excluded from the client bundle, so there is no
size to save. Code-split the *component* that calls the server function
(`lazy(() => import('./ReportPanel'))`) — never the server function module itself.

The same holds for `require()`, computed import specifiers, and re-exporting a server function
through a dynamically imported barrel. If the bundler cannot resolve the path at build time,
the transform does not happen.

## Rule 4 — Every server function is its own auth boundary

**A server function is an API endpoint reachable independently of whichever route renders the
UI that calls it.** Anyone can hit it directly with the right payload, without ever loading
your route.

- **Apply `authMiddleware` — or an equivalent in-handler check — to every server function that
  reads or writes private data.** No exceptions for "it's only called from an admin screen".
- **A route's `beforeLoad` is not the data boundary.** It is route UX: it decides what the user
  sees, not what the endpoint will answer. A server function protected only by the guard on the
  route that calls it is unprotected.
- **Authorize, don't just authenticate.** Knowing *who* is calling is not the same as checking
  they own the record the `data` payload names. Resolve the actor from the request context and
  check it against the resource — never trust an owner id, tenant id, or role that arrived in
  the validated input.

## Rule 5 — Never `Cache-Control: public` on an identity-dependent response

`public` tells every CDN and proxy between you and the user that the response may be served to
anyone. If a handler reads a session, a cookie, or an auth header — or branches on identity at
all — `public` will cache one user's response and replay it to the next. That is a cross-tenant
data leak, and it is invisible in development where no proxy sits in the path.

```ts
// ✅ Authenticated response — only the user-agent may cache, and any intermediary
//    that does cache keys by identity rather than URL alone
setResponseHeaders(
  new Headers({ 'Cache-Control': 'private, max-age=60', Vary: 'Cookie, Authorization' }),
);

// ✅ Sensitive data — don't cache it at all
setResponseHeaders(new Headers({ 'Cache-Control': 'no-store' }));

// ❌ Never on anything that depends on who is asking
setResponseHeaders(new Headers({ 'Cache-Control': 'public, max-age=60' }));
```

`public` is reserved for responses that are genuinely identical for every caller — a public
price list, a static config. The moment a handler touches the request's identity, it is
`private` (with `Vary`) or `no-store`.

## Checklist before finishing a file

- [ ] Every module is clearly one of the three categories, and its suffix matches what's inside
      — `.functions.ts` wrappers, `.server.ts` server-only helpers, plain `.ts` client-safe.
- [ ] No `.server.ts` module is imported from a component, hook, or plain `.ts` — only from a
      handler, another `.server.ts`, or a server route.
- [ ] No DB client, secret, env read, or filesystem call sits in an unsuffixed `.ts`.
- [ ] Handlers validate their input with `.validator()` and delegate real logic to `.server.ts`.
- [ ] Every server function is imported statically — no `await import()`, no `require()`, no
      dynamic barrel, whatever the bundle-size argument. Code-split the calling component
      instead.
- [ ] Every server function touching private data carries `authMiddleware` or an in-handler
      check — a `beforeLoad` guard on the calling route does not count.
- [ ] Ownership/tenancy is checked against the resolved actor, not against ids supplied in the
      validated input.
- [ ] No identity-dependent response sets `Cache-Control: public` — it's `private` with a
      `Vary`, or `no-store`.
- [ ] The `ts-clean` checklist passes for the file (and `react-clean` too, if it's a component
      or hook).
