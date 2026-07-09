---
name: react-clean
description: Rules for writing clean React components. INVOKE THIS SKILL before writing or editing ANY React component, hook, or `.tsx`/`.jsx` file — when creating a component, adding an effect, wiring up data fetching, or refactoring React code. Enforces one-component-per-file, size limits (component body and props count), at most one useEffect (extract the rest into custom hooks), no data-layer access from components (service + TanStack Query instead), and the "You Might Not Need an Effect" anti-pattern rules from react.dev.
---

# Clean React Components

Rules for writing React components that stay readable, testable, and free of the effect-soup that makes React code fragile. Apply these whenever you write or edit a React component or hook.

Reference: https://react.dev/learn/you-might-not-need-an-effect

## Rule 1 — One component per file (max two)

- **Prefer exactly one React component per file.** Name the file after the component (`UserCard.tsx` exports `UserCard`).
- **At most two components per file**, and only when the second is a *very small*, presentational helper used solely by the first (a few lines, no logic of its own). The moment a helper grows logic, its own state, or a second consumer, move it to its own file.
- Custom hooks live in their own file too (`useUserProfile.ts`), or co-located next to their only consumer — never inlined as a giant closure.
- Never put component code in `index.ts` / `index.tsx`; the index file is a thin re-export barrel only.

## Rule 2 — At most one `useEffect` per component

A component may contain **at most one `useEffect`**. When you need more than one, or an effect grows past a few lines, **extract each effect into a named custom hook** that describes its purpose.

```tsx
// ❌ Avoid — multiple effects pile up in the component
function ChatRoom({ roomId }) {
  useEffect(() => { /* connect socket */ }, [roomId]);
  useEffect(() => { /* sync document title */ }, [roomId]);
  useEffect(() => { /* log analytics */ }, [roomId]);
  // ...
}

// ✅ Good — each effect becomes an intention-revealing hook
function ChatRoom({ roomId }) {
  useChatConnection(roomId);
  useDocumentTitle(`Chat: ${roomId}`);
  useAnalyticsPageView('chat', roomId);
  // ...
}
```

Each `use*` hook owns its single effect plus its cleanup. The component reads as a list of behaviors, not a wall of `useEffect` calls.

**Before writing an effect at all, check Rule 4 — most effects should not exist.**

## Rule 3 — Never touch the data layer from a component

**Never call `fetch`, `axios`, a database client, or any data-source API directly inside a React component or inside a raw `useEffect`.** Components render; they do not talk to the network or persistence.

Use the **service + TanStack Query** combination, optionally wrapped in a custom query hook:

```tsx
// services/userService.ts — the ONLY place that knows how to fetch
export const userService = {
  getById: (id: string) => api.get<User>(`/users/${id}`).then(r => r.data),
};

// hooks/useUser.ts — a custom query hook wrapping TanStack Query
export function useUser(id: string) {
  return useQuery({
    queryKey: ['user', id],
    queryFn: () => userService.getById(id),
  });
}

// UserCard.tsx — the component just consumes the hook
function UserCard({ id }: { id: string }) {
  const { data: user, isPending, error } = useUser(id);
  if (isPending) return <Spinner />;
  if (error) return <ErrorState error={error} />;
  return <div>{user.name}</div>;
}
```

- Mutations go through `useMutation` calling a service method, never a bare `fetch` in an event handler either.
- The component never sees a URL, a request config, or a `fetch`. It sees `data`, `isPending`, `error`, `mutate`.
- This also satisfies Rule 2 and Rule 4: TanStack Query owns the fetching effect, race conditions, caching, and cleanup — you don't write that `useEffect` at all.

## Rule 4 — You Might Not Need an Effect

Effects are for **synchronizing with external systems** (a non-React widget, a subscription, the document title). They are **not** for reacting to state changes or handling user interactions. Before adding any `useEffect`, check this table. Most effects are removable.

**Decision rule:** code that runs *because the component was displayed* belongs in an Effect. **Everything else belongs in an event handler.**

| If you're using an Effect to… | Do this instead |
|---|---|
| **Transform data for rendering** | Compute it during render: `const visible = filter(items, q)`. No state, no effect. |
| **Cache an expensive calculation** | `useMemo(() => expensive(a, b), [a, b])` — not state + effect. |
| **Reset all state when a prop changes** | Pass a `key` prop so React remounts a fresh instance: `<Profile key={userId} />`. |
| **Adjust some state when a prop changes** | Set state *during render* guarded by a `prev` comparison, or better, derive it (store an ID, `find` the object during render). |
| **Run logic in response to a user event** | Put it in the event handler — you know *what* happened there; an effect doesn't. |
| **Chain effects that update each other's state** | Compute all the next state in one event handler. |
| **Send a POST on interaction** (submit, buy) | Call it from the event handler, not from an effect watching state. |
| **Share logic between two handlers** | Extract a plain function and call it from both handlers. |
| **Notify the parent when state changes** | Update both in the same handler, or lift state up and make the component controlled. |
| **Fetch data** | Use TanStack Query (Rule 3). If you must hand-roll, add an `ignore` cleanup flag to drop stale responses, and wrap it in a custom hook. |
| **Subscribe to an external store** | `useSyncExternalStore`, not a manual subscribe/unsubscribe effect. |
| **Initialize the app once** | Run it at module scope / import time, or guard with a module-level `didInit` flag. |

A **legitimate** effect (allowed under the one-effect budget of Rule 2) looks like: connecting to a chat server, subscribing to a browser event, syncing `document.title`, controlling a non-React map/video widget. If it's synchronizing with something *outside* React, it's fine — otherwise remove it.

## Rule 5 — Keep components and their props small

A component that grows past these limits is doing too much. Treat the limits as **hard ceilings that trigger a refactor**, not style suggestions — when you cross one, split before moving on.

**Size limits (per component):**

- **≤ 150 lines** for the whole file (imports excluded). Past that, extract child components or move logic into hooks.
- **≤ 50 lines** in the returned JSX. A taller tree means you're missing sub-components — pull cohesive branches into their own named components (`<CardHeader />`, `<CardFooter />`).
- **≤ 3 levels of JSX nesting** in a single return. Deeper nesting is a sub-component waiting to be extracted.
- **One reason to render.** If a component both fetches/derives *and* lays out several unrelated sections, split it into a container and presentational pieces.

**Props limits (per component):**

- **≤ 5 props.** Crossing this is a signal, not a crime — but stop and apply one of the fixes below rather than adding a sixth.
- When you need more, prefer, in order:
  1. **Composition** — pass `children` or slot props (`header`, `actions`) instead of many primitive flags.
  2. **Group related props into one object** — `user: { name, avatarUrl, role }` instead of `userName`, `userAvatarUrl`, `userRole`.
  3. **Split the component** — a long prop list usually means two components wearing one costume.
- **No boolean flag soup.** Several `isX` booleans that select a rendering mode should become a single `variant` union (`variant: 'compact' | 'full'`); mutually exclusive booleans are a design smell.
- Don't count these against the budget: a single well-typed props object, `children`, and standard event handlers are fine — the limit targets *unrelated* inputs, not cohesive ones.

```tsx
// ❌ Avoid — 7 props, boolean soup, no cohesion
function UserBadge({
  name, avatarUrl, role, isOnline, isCompact, isClickable, onClick,
}) { /* ... */ }

// ✅ Good — grouped data object + a variant union + composition
function UserBadge({
  user,                       // { name, avatarUrl, role, isOnline }
  variant = 'full',           // 'full' | 'compact'
  onClick,                    // omit onClick → not clickable
}: UserBadgeProps) { /* ... */ }
```

Sub-components extracted to satisfy these limits follow Rule 1: give each its own file (or keep a *tiny* presentational helper alongside its only parent).

## Checklist before finishing a component

- [ ] One component in the file (or one + a tiny presentational helper).
- [ ] Component ≤ 150 lines, JSX return ≤ 50 lines and ≤ 3 nesting levels — otherwise sub-components extracted.
- [ ] ≤ 5 props; extra inputs grouped into an object, passed as `children`/slots, or collapsed into a `variant` union instead of boolean soup.
- [ ] Zero or one `useEffect`; any others extracted into named custom hooks.
- [ ] No `fetch`/`axios`/DB access in the component — data comes from a service + TanStack Query hook.
- [ ] Every remaining effect genuinely synchronizes with an external system (passed the Rule 4 table).
- [ ] Derived data is computed during render (or `useMemo`), not stored in state and synced by an effect.
