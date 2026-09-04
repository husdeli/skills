---
name: clean-fullstack-architecture
description: "Use when: planning a feature implementation, designing a feature, creating an implementation plan, planning architecture, writing feature code, creating a new feature, adding a service, calling an API, defining a DTO or a domain model, mapping an API response, structuring the project, adding a component, adding a hook, adding domain logic, or writing any production code. Enforces Clean Code principles and Hexagonal Architecture with strict dependency rules across all layers — including that every service is a class of static methods owning its DTOs, that domain logic names only domain models and never a DTO, and that an adapter is the only place the two shapes meet."
---

# Clean Fullstack Architecture

Enforces Clean Code principles and Hexagonal Architecture (Ports & Adapters) when designing implementations and writing code. Business logic sits at the center with no knowledge of the outside world; external concerns (APIs, UI frameworks) depend inward toward the domain, never the reverse.

## Core Principles

1. **Dependency Rule**: Dependencies point inward. Outer layers depend on inner layers, never the reverse.
2. **Separation of Concerns**: Each layer has a single responsibility and a clear boundary.
3. **Framework Independence**: Business logic must not import framework-specific code (React hooks, API clients, etc.).
4. **Testability**: Every layer can be tested in isolation by mocking the layer it depends on.
5. **Role-suffixed file names**: A module that fills a layer role is named `<subject>.<role>.ts` — `user.service.ts`, `user.adapter.ts`, `user.dto.ts`, `user.model.ts`. Domain logic, components, containers, hooks, and libs are named after what they do, not after a layer. See `ts-clean` Rule 1.
6. **Self-documenting code**: Names carry the meaning, so comments stay rare. Cap a file at one or two comments, one sentence each, and write one only for a *why* the code cannot state. Never write a comment the next developer cannot verify — no file paths, no line numbers, no finished tickets, no history of a past refactor. See `ts-clean` Rule 3.

## Project Structure

```
src/
├── models/          # Innermost layer - pure DOMAIN models, never DTOs (*.model.ts)
├── domain/          # Business logic - depends only on models
├── components/      # Dumb UI components - no domain/data imports
├── containers/      # Smart components - compose hooks with dumb components
├── hooks/           # Top-level React hooks - no domain/data imports
├── libs/            # Independent library modules
├── adapters/        # DTO -> domain model translation (*.adapter.ts) - the only layer that sees both
├── services/        # Data layer - static-method classes (*.service.ts); own their DTOs
│   └── dto/         # Wire shapes (*.dto.ts) - type-only leaf modules, zero project imports
├── features/        # Feature modules grouped by DOMAIN (compose all layers)
│   ├── <domain>/               # single-surface domain — stays flat
│   │   ├── domain/
│   │   ├── components/
│   │   ├── containers/
│   │   ├── hooks/
│   │   ├── consts/
│   │   ├── adapters/
│   │   └── services/
│   │       └── dto/
│   └── <domain>/               # multi-platform / multi-surface domain — nested
│       ├── common/             # cross-platform code (same layers)
│       │   ├── domain/
│       │   ├── containers/
│       │   ├── hooks/
│       │   ├── adapters/
│       │   └── services/
│       └── <sub-domain>/       # one platform; optional <surface>/ level below
│           ├── domain/
│           └── components/
└── ...
```

Features are grouped by **domain** (a product area), not by surface type. A domain owns all of
its surfaces; nest into sub-domains and surfaces only when the domain earns it (see
"Domain-cohesive feature grouping"). Worked social example:

```
features/socials/
  index.ts                       # client-safe public barrel; re-exports common + platforms
  common/                        # cross-platform code, shared by every platform
    domain/       socialPost.ts, socialRenderer.ts, platformConstraints.ts
    containers/   SocialPostEditor.tsx, PostList.tsx, PostInspector.tsx, postPreviews.ts
    hooks/        useAccounts.ts
    server/       connect.ts, connectionStore.ts, publish.ts, publishConnector.ts
  bluesky/                       # sub-domain: earns only a render/preview surface today
    domain/       blueskyRenderer.ts     # config + registration; imports from common/
    components/   BlueskyPostPreview.tsx
    index.ts
  instagram/
    domain/       instagramRenderer.ts
    components/   InstagramPostPreview.tsx
    index.ts
```

## Layer Definitions and Dependency Rules

### 1. `models/` - Domain Models (Innermost)

TypeScript types, interfaces, and enums defining the shape of business data. Types alone are usually sufficient; classes or added logic are not the default. No imports from any other project layer.

These are **domain models** — shaped by the business, not by any external system. A model is written the way the domain wants to talk about the thing: the domain's own names, real `Date` objects, discriminated unions instead of nullable flags, no field that exists only because some API returns it. The wire shape lives in a **DTO** (see `services/`), and the two are never the same type. If a model has `snake_case` keys, `string` dates, or a field named after an API's internals, a DTO has leaked in — fix it in the adapter, not by widening the model.

**Allowed dependencies:** None (zero imports from project layers)

```typescript
// models/presentation.model.ts
export interface Slide {
  id: string;
  title: string;
  content: SlideContent[];
  order: number;
}

export type SlideContent = TextBlock | ImageBlock | ChartBlock;
```

### 2. `domain/` - Business Logic

Pure functions and logic operating on models. Defines *what the app does* without knowing *how* data arrives or *how* results are displayed.

**Domain logic never relies on a DTO.** It operates only on domain models, and it never names a DTO type — not as a parameter, not as a return type, not in a cast. If a domain function needs a field that only exists on the wire shape, either the model is missing that field or the function is doing translation work that belongs in an adapter. The domain must stay valid when the external API changes its shape.

**Allowed dependencies:** `models/`, other `domain/` layers (including feature-level domain layers)  
**Forbidden:** Any import from `services/` (including its `dto/`), `adapters/`, `components/`, `hooks/`, or external API/framework code

```typescript
// domain/presentation-logic.ts
import type { Slide } from '@/models/presentation.model';

export function reorderSlides(slides: Slide[], fromIndex: number, toIndex: number): Slide[] {
  // ...
}
```

### 3. `components/` - Dumb UI Components

Presentational React components receiving all **data** via props. Reusable across any feature. Must not import from `domain/`, `services/`, `features/`, or any data-fetching code.

A component may use a **generic, side-effect-free hook** from top-level `hooks/` — a media query, a debounce, a controlled-input helper, a focus trap. Those are UI utilities, not data access: they read no server state, own no business rules, and swapping one out cannot change what the component renders semantically. Forbidden is any hook that *brings data in*: a feature hook, a hook wrapping `useQuery`/`useMutation` or a service call, or a hook whose effect writes outside the component.

**Allowed dependencies:** Other `components/`, `libs/`, generic side-effect-free `hooks/`, third-party UI libraries  
**Forbidden:** `domain/`, `services/`, `features/`, feature hooks, data-fetching or side-effecting hooks, direct state management

```typescript
// components/SlideCard.tsx
interface SlideCardProps {
  title: string;
  thumbnail: string;
  isActive: boolean;
  onSelect: () => void;
}

export function SlideCard({ title, thumbnail, isActive, onSelect }: SlideCardProps) {
  // ...
}
```

### 4. `containers/` - Smart Components

Connected React components wiring hooks to presentational components. They own local UI state, call hooks for data and actions, and pass everything down to dumb `components/` via props. Not reusable across contexts — each container is purpose-built for a specific screen or section.

**Allowed dependencies:** `models/`, `components/`, `hooks/`, `libs/`  
**Forbidden:** `domain/`, `services/`, `features/`

```typescript
// containers/SlideEditorContainer.tsx
import { useSlideEditor } from '@/hooks/useSlideEditor';
import { SlideList } from '@/components/SlideList';

export function SlideEditorContainer({ presentationId }: { presentationId: string }) {
  const { slides, activeSlide, selectSlide } = useSlideEditor(presentationId);
  return <SlideList slides={slides} activeId={activeSlide?.id} onSelect={selectSlide} />;
}
```

**Reading `react-clean` alongside this skill.** `react-clean` says "component" in the plain React sense — any `.tsx` file exporting one — and its Rule 3 example shows one consuming a TanStack Query hook. In *this* taxonomy that file is a **container**: once a component pulls data through a query hook, it belongs in `containers/`, not `components/`. Both skills agree on the substance — data arrives through a service + query hook, never a `fetch` in the component — they draw the naming line differently. `react-clean`'s size, props, effect, and prop-drilling rules apply to both.

### 5. `hooks/` - Top-Level React Hooks

Reusable React hooks for cross-cutting UI concerns (media queries, local storage, debounce). UI utilities, not business logic containers.

**Allowed dependencies:** Other `hooks/`, `libs/`, React APIs  
**Forbidden:** `domain/`, `services/`, `features/`

```typescript
// hooks/useMediaQuery.ts
export function useMediaQuery(query: string): boolean {
  // ...
}
```

### 6. `libs/` - Independent Library Modules

Self-contained utility packages that could be extracted as standalone npm packages. Each subfolder is an independent module.

**Allowed dependencies:** Other `libs/` modules, third-party packages  
**Forbidden:** Any project-specific layer (`models/`, `domain/`, `services/`, `features/`, `components/`, `hooks/`)

```typescript
// libs/color-utils/index.ts
export function parseHexColor(hex: string): RGB { ... }
export function deriveContrastColor(color: RGB): RGB { ... }
```

### 7. `adapters/` - DTO → Domain Translation

The seam between the wire and the domain. An adapter is the **only** kind of module where a DTO
and a domain model are named in the same file. It converts between them and does nothing else —
no fetching, no caching, no business rules.

- **One adapter per resource**, named `<resource>.adapter.ts`: `user.adapter.ts` exports
  `userAdapter` (`ts-clean` Rule 1).
- `toDomain(dto)` maps inbound wire → model. Write-direction methods (`toCreateDto`,
  `toPatchDto`) map an outbound model or intent → wire.
- **Adapters are pure and synchronous.** No `await`, no HTTP client, no reading ambient state —
  anything time- or environment-dependent is passed in by the caller.
- **Close the gaps the wire leaves**: parse date strings into `Date`, rename fields to the
  domain's vocabulary, collapse the API's `null` / `undefined` / `""` into the single
  representation the model defines, derive the discriminant the domain switches on. A missing
  required field is an error the adapter raises — never an `undefined` handed to the domain.
- Where a model carries an invariant, build it through the domain's own factory or validator
  rather than casting an object literal into the type.

**Allowed dependencies:** `models/`, `domain/` (factories/validators), `libs/`, DTO modules
(`import type` only)  
**Forbidden:** service classes, `components/`, `containers/`, `hooks/`, `features/`, any HTTP
client or I/O

```typescript
// adapters/user.adapter.ts
import type { User } from '@/models/user.model';
import type { UserDto } from '@/services/dto/user.dto';

export const userAdapter = {
  toDomain(dto: UserDto): User {
    return {
      id: dto.user_id,
      displayName: dto.display_name,
      createdAt: new Date(dto.created_at),
      isActive: dto.deactivated_at === null,
    };
  },

  toPatchDto(patch: { displayName: string }): Pick<UserDto, 'display_name'> {
    return { display_name: patch.displayName };
  },
};
```

**Why this isn't a cycle.** `services/` imports `adapters/`, and an adapter imports DTO *types*
out of `services/dto/`. DTO modules are type-only leaves importing nothing, so the real edge runs
`dto → adapter → service` and stays acyclic. An adapter that imports a **service** is a genuine
cycle and is forbidden.

### 8. `services/` - Data/API Layer (Outermost)

The only layer that talks to external systems (REST/RPC APIs, WebSocket, localStorage, vendor
SDKs). Services implement ports defined by the business logic — **the domain never imports from
services**.

**A service is a class with static methods.**

- One service class per file, named `<resource>.service.ts`: `user.service.ts` exports
  `class UserService`.
- **Every method is `static`.** The class is never instantiated and holds no instance state — it
  is a named namespace for one external resource, not an object graph. Internals (URL building,
  header assembly, retry wrapping) are `private static`.
- One service per external resource, not one per screen.
- Because the class is static, tests substitute it by mocking the module, not by injecting an
  instance. Keep methods individually mockable — one call path each, no method reaching into
  another's private state.

**A service owns its DTOs.** The DTO is what the external system actually speaks — `snake_case`
fields, string dates, nullable everything, whatever the wire hands you. It lives in
`services/dto/<resource>.dto.ts` (or `features/<name>/services/dto/`), is **type-only**, and
imports nothing from any project layer. Never bend a DTO toward the domain, and never widen a
model to accommodate the wire — the whole point of the pair is that each side is free to change.

**A service never returns a DTO.** Every public method returns a domain model, a primitive, or
`void`, converted through an adapter. DTOs are private to the services + adapters pair: no hook,
container, component, or domain function ever names one.

**Allowed dependencies:** `adapters/`, its own `dto/`, `models/`, `domain/`, `libs/`,
feature-level `models/`, third-party HTTP/API clients  
**Forbidden:** `components/`, `containers/`, `hooks/`, `features/`; returning a DTO from a public
method

```typescript
// services/dto/user.dto.ts — wire shape, zero project imports
export interface UserDto {
  user_id: string;
  display_name: string;
  created_at: string;
  deactivated_at: string | null;
}

// services/user.service.ts
import type { User } from '@/models/user.model';
import { userAdapter } from '@/adapters/user.adapter';
import { apiClient } from '@/libs/apiClient';
import type { UserDto } from './dto/user.dto';

export class UserService {
  static async getById(id: string): Promise<User> {
    const dto = await apiClient.get<UserDto>(`/users/${id}`);
    return userAdapter.toDomain(dto);
  }

  static async list(): Promise<User[]> {
    const dtos = await apiClient.get<UserDto[]>('/users');
    return dtos.map(userAdapter.toDomain);
  }

  static async rename(user: User, displayName: string): Promise<User> {
    const dto = await apiClient.patch<UserDto>(
      `/users/${user.id}`,
      userAdapter.toPatchDto({ displayName }),
    );
    return userAdapter.toDomain(dto);
  }
}
```

```typescript
// BAD - loose function, and the DTO escapes into everything upstream
export async function fetchUser(id: string): Promise<UserDto> {
  return apiClient.get<UserDto>(`/users/${id}`);
}
```

### 9. `features/` - Feature Modules (Composition Layer)

Each subfolder is a self-contained feature composing all necessary layers. Features are where dependency inversion meets the UI — they wire services to domain logic to components.

**Internal structure per feature:**
- `domain/` - Feature-specific business logic (depends on top-level `models/`)
- `components/` - Feature-specific dumb UI (can use top-level `components/`)
- `containers/` - Feature-specific smart components (wire feature hooks to components)
- `hooks/` - Feature-specific hooks (wire services + domain + UI)
- `consts/` - Feature-specific constants
- `adapters/` - Feature-specific DTO → domain model translation
- `services/` - Feature-specific service classes, with their DTOs in `services/dto/`
- `server/` - Server-only code for the feature (DB access, secrets, server functions). Never imported from a component, container, or hook — client code reaches it through a service or a server function. In a TanStack Start app the file suffixes carry this same boundary; see the `clean-tanstack-start` skill.

**Allowed dependencies:** All top-level layers (`models/`, `domain/`, `components/`, `hooks/`, `libs/`, `adapters/`, `services/`)  
**Forbidden:** Other `features/` (features must not cross-depend)

```typescript
// features/slide-editor/hooks/useSlideEditor.ts
import { reorderSlides } from '@/domain/presentation-logic';
import { SlideService } from '@/services/slide.service';
import type { Slide } from '@/models/presentation.model';

export function useSlideEditor(presentationId: string) {
  // ...
}
```

### Domain-cohesive feature grouping

Split a scattered `social-renderer` / `social-editor` / `social-viewer` set into one `socials/`
domain owning all of its surfaces. Nesting order, outermost to innermost:

- **domain** — a product area (e.g. `socials/`). Domains never import each other.
- **sub-domain** — one variant within the domain, typically a platform (e.g. `bluesky/`,
  `instagram/`). Appears only with **2+ platforms**.
- **surface** — a way the sub-domain is used (e.g. `viewer/`, `editor/`). Appears only with
  **2+ surfaces**; a single-surface sub-domain holds the layers directly.
- **layers** — the usual clean layers (`domain/`, `components/`, `containers/`, `hooks/`,
  `services/`, and `server/` where the feature owns server-only code) at the innermost earned
  nesting level.

**Nest only when it earns it.** Start flat and add a level only for real plurality:

- A single-surface, single-platform domain stays flat:
  `features/<domain>/{domain,components,containers,hooks,services}`.
- Add `<sub-domain>/` folders only once the domain has **2+ platforms**.
- Add `<surface>/` folders only once a platform has **2+ surfaces**. One earned surface stays
  flat under the sub-domain — do **not** create an empty `viewer/`/`editor/` scaffold.

**The `common/` slot.** Code shared across a domain's sub-domains lives in
`features/<domain>/common/`, organized by the clean layers. It holds the cross-platform core:
shared domain logic, the platform-agnostic editor/viewer shell, shared hooks and server code.

**Dependency rules on the nested shape.** The per-layer matrix below still governs which layer may
import which. Layered on top of it:

- Inner layers never depend outward.
- **Cross-domain imports are forbidden** — one domain never imports another domain's internals
  (the "features must not cross-depend" rule, read as "domains").
- A **sub-domain may depend on its domain's `common/`**, but `common/` must **not** depend on a
  sub-domain. Invert the edge: compose sub-domains at the domain root/barrel, or have each
  sub-domain **self-register** into a shared registry that `common/` reads.
- **Shared cross-cutting seams are a carve-out.** Genuinely cross-domain infrastructure —
  top-level `models/`, and cross-domain registries such as the renderer and editor-surface
  registries — stays in its shared top-level location, consumable by any domain. Such a registry
  is the sanctioned seam through which one domain discovers another's contributions without a
  direct import.

**Reading the `socials/` tree above.** Each platform is a sub-domain holding only its renderer
config + registration and its preview component. **Bluesky earns only a single render/preview
surface today**, so it stays flat — no `viewer/`/`editor/` folders — because the editor is
platform-agnostic and lives in `common/containers/`. Platforms register themselves: a platform's
`domain/` registers its renderer into the shared renderer registry, and its barrel registers its
preview into `common`'s preview registry — so `common/` imports no platform module.

## Dependency Matrix (Quick Reference)

| Layer           | models | domain | components | containers | hooks | libs | adapters | services | features |
|-----------------|--------|--------|------------|------------|-------|------|----------|----------|----------|
| **models**      | -      | NO     | NO         | NO         | NO    | NO   | NO       | NO       | NO       |
| **domain**      | YES    | YES    | NO         | NO         | NO    | NO   | NO       | NO       | NO       |
| **components**  | NO     | NO     | YES        | NO         | generic only | YES  | NO   | NO       | NO       |
| **containers**  | YES    | NO     | YES        | -          | YES   | YES  | NO       | NO       | NO       |
| **hooks**       | NO     | NO     | NO         | NO         | YES   | YES  | NO       | NO       | NO       |
| **libs**        | NO     | NO     | NO         | NO         | NO    | YES  | NO       | NO       | NO       |
| **adapters**    | YES    | YES    | NO         | NO         | NO    | YES  | YES      | DTO types only | NO |
| **services**    | YES    | YES    | NO         | NO         | NO    | YES  | YES      | -        | models only |
| **features**    | YES    | YES    | YES        | YES        | YES   | YES  | YES      | YES      | NO       |

The **services → services** cell covers a service's own `dto/` modules and shared transport (a
typed RPC client, a configured HTTP client) that is bound to project types and so cannot live in
`libs/`. It does **not** license one service class to call another: two services needing the same
call means the call belongs to one of them, and the composition belongs in a feature hook.

## Implementation Workflow

When designing or implementing a feature:

1. **Start with domain models** - Define the types the *business* needs, in the domain's own vocabulary, before looking at any API response
2. **Write domain logic** - Pure business rules using only models
3. **Define the DTOs** - Write down what the external system actually returns, unedited, in `services/dto/`
4. **Write the adapter** - Pure `toDomain` (and any write-direction) mapping between the two shapes
5. **Build the service** - A static-method class calling the external system and returning domain models through the adapter
6. **Create dumb components** - Presentational UI taking props
7. **Wire in feature hooks** - Compose services + domain + state in feature-specific hooks
8. **Build containers** - Connect feature hooks to dumb components

Steps 1 and 3 are deliberately separate. Deriving the model from the API response is how DTOs end
up masquerading as domain models — decide what the domain wants first, then map onto it.

## Validation Rules

Before writing or reviewing code, verify:

- [ ] No circular dependencies between layers
- [ ] `domain/` has zero imports from `services/`, `components/`, or `hooks/`
- [ ] `components/` has zero imports from `domain/`, `services/`, or `features/`; any `hooks/` import is a generic, side-effect-free UI utility, never a data or feature hook
- [ ] `containers/` has zero imports from `domain/`, `services/`, or `features/`
- [ ] `hooks/` (top-level) has zero imports from `domain/`, `services/`, or `features/`
- [ ] `libs/` has zero imports from any project-specific layer
- [ ] `models/` has zero imports from any other project layer
- [ ] Features do not import from other features
- [ ] No domain imports another domain's internals; shared code is promoted to a top-level layer or a cross-domain registry
- [ ] `common/` does not import from its own sub-domains (invert via self-registration or wire at the domain root)
- [ ] No `server/` module is imported from a component, container, or hook — client code reaches it through a service or a server function
- [ ] All business logic lives in `domain/` or `features/<name>/domain/`, never in components or hooks
- [ ] Every service is a class with only `static` methods, one class per file, the file named `<resource>.service.ts` — no loose exported request functions, no instantiation
- [ ] Every service, adapter, DTO, and model file carries its role suffix (`*.service.ts`, `*.adapter.ts`, `*.dto.ts`, `*.model.ts`), and no domain, component, container, or hook file was given one
- [ ] No public service method returns a DTO; every return is a domain model, a primitive, or `void`
- [ ] DTO types are imported only by `services/` and `adapters/` — never by `domain/`, `models/`, a hook, a container, or a component
- [ ] `models/` and `domain/` name no DTO and carry no wire-shaped field (`snake_case` keys, `string` dates, API-internal names)
- [ ] Every adapter is pure and synchronous, imports no HTTP client, and imports no service (a service → adapter → service cycle)
- [ ] Each file carries at most one or two comments, each a single sentence stating a *why*, and none points at a file, a line, a finished ticket, or a past refactor

## React-Specific Architecture Guidelines

### Avoid Overusing Effects

Effects are an escape hatch for synchronizing with external systems. Data derivation, filtering,
and transformation belong in render logic or `domain/` functions. Before writing a `useEffect`,
ask: is this synchronizing with something *outside* React (DOM, WebSocket, third-party lib)? If
not, it likely doesn't need an Effect. The `react-clean` skill carries the full anti-pattern
table; this is where each concern lands in the layer taxonomy:

| Concern | Wrong place | Right place |
|---------|-------------|-------------|
| Derived/computed values | `useEffect` + `setState` | Inline in render or `domain/` function |
| Data fetching | Component `useEffect` | Feature hook (`features/<name>/hooks/`) |
| Cross-cutting UI side effects | Component `useEffect` | Top-level hook (`hooks/`) |
| Business rules on events | `useEffect` watching state | Event handler calling `domain/` function |

Reference: [You Might Not Need an Effect](https://react.dev/learn/you-might-not-need-an-effect)

### Styling Approach

Prefer styles co-located with the component, in this order:

1. **Tailwind CSS utility classes** — default for all styling. Apply classes directly on JSX elements. Keep conditional class logic readable with `clsx` or `cn` helpers.
2. **CSS-in-JS** (`styled-components`, `emotion`) — when dynamic styles depend on runtime values that would make Tailwind class strings unwieldy.
3. **Separate `.css` / `.module.css` files** — only for what the above cannot handle (complex keyframe animations, third-party component overrides, global resets).

**Rules:**
- Never mix all three in the same component — pick one and stay consistent within a file
- Global styles (resets, CSS variables, font-face) live in a single top-level stylesheet (e.g. `src/styles/globals.css`)
- Design tokens (colors, spacing, radii) are Tailwind theme values or CSS custom properties — never magic strings scattered across components

```tsx
// Preferred: Tailwind with cn() helper for conditional classes
import { cn } from '@/libs/cn';

export function Badge({ variant, children }: BadgeProps) {
  return (
    <span className={cn(
      'inline-flex items-center rounded-full px-2 py-1 text-xs font-medium',
      variant === 'success' && 'bg-green-100 text-green-800',
      variant === 'error' && 'bg-red-100 text-red-800',
    )}>
      {children}
    </span>
  );
}
```

### Data Fetching Flow: useQuery / useMutation + oRPC

Use **React Query** (`useQuery`, `useMutation`) as the data-fetching layer, with **oRPC** as the typed router when available. Never call service functions or fetch APIs directly in components or containers.

**Layer responsibilities:**

| Layer | Role |
|-------|------|
| `services/dto/` | The shapes the API actually returns — type-only, never seen above the service |
| `services/` or `features/<name>/services/` | Static-method service class per resource — calls the oRPC/HTTP client, returns domain models |
| `adapters/` or `features/<name>/adapters/` | Converts the service's DTOs into domain models |
| `features/<name>/hooks/` | Custom hooks wrapping `useQuery`/`useMutation` — single source of truth for a resource |
| `containers/` or `features/<name>/containers/` | Consumes the custom hook, passes data to dumb components |
| `domain/` | Transforms or validates the models returned from the hook before rendering |

The oRPC client is **infrastructure the service uses**, not a service itself: it is the typed
transport, so it stays behind the service class rather than being called from a hook.

**Canonical pattern:**

```typescript
// services/orpcClient.ts — transport, not a service: no domain operation, so no .service.ts
import { createORPCClient } from '@orpc/client';
export const orpc = createORPCClient<AppRouter>({ baseURL: '/api' });

// services/slide.service.ts — the only place the transport is touched
import type { Slide } from '@/models/presentation.model';
import { slideAdapter } from '@/adapters/slide.adapter';
import { orpc } from './orpcClient';
import type { SlideDto } from './dto/slide.dto';

export class SlideService {
  static async list(presentationId: string): Promise<Slide[]> {
    const dtos: SlideDto[] = await orpc.slides.list({ presentationId });
    return dtos.map(slideAdapter.toDomain);
  }

  static async reorder(presentationId: string, from: number, to: number): Promise<Slide[]> {
    const dtos: SlideDto[] = await orpc.slides.reorder({ presentationId, from, to });
    return dtos.map(slideAdapter.toDomain);
  }
}

// features/slides/hooks/useSlides.ts — custom query hook
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { SlideService } from '@/services/slide.service';

export function useSlides(presentationId: string) {
  const queryClient = useQueryClient();

  const slides = useQuery({
    queryKey: ['slides', presentationId],
    queryFn: () => SlideService.list(presentationId),
  });

  const reorder = useMutation({
    mutationFn: ({ from, to }: { from: number; to: number }) =>
      SlideService.reorder(presentationId, from, to),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['slides', presentationId] }),
  });

  return { slides, reorder };
}

// features/slides/containers/SlideEditorContainer.tsx — consumes the hook
import { useSlides } from '../hooks/useSlides';
import { SlideList } from '@/components/SlideList';
import { sortSlides } from '@/domain/presentation-logic'; // domain transforms data

export function SlideEditorContainer({ presentationId }: { presentationId: string }) {
  const { slides, reorder } = useSlides(presentationId);
  const sorted = slides.data ? sortSlides(slides.data) : [];

  return (
    <SlideList
      slides={sorted}
      isLoading={slides.isLoading}
      onReorder={(from, to) => reorder.mutate({ from, to })}
    />
  );
}
```

**Rules:**
- One custom hook per resource/domain entity — don't scatter `useQuery` calls across components
- The hook calls the **service class**, never the oRPC client or `fetch` directly
- What the hook hands back is already domain models — a `queryFn` returning a DTO puts the wire shape into the query cache, the container, and every component below it
- `queryKey` arrays must be consistent — define them as constants in `features/<name>/consts/` if reused
- Data transformation (sorting, filtering, deriving) happens in `domain/` functions, not inside the hook or component; *shape* translation happens in the adapter, not either of them
- Without oRPC, the service calls a plain HTTP client instead — every layer above it is unchanged

## Additional Resources

- **`references/dependency-rules.md`** — dependency rules with edge cases and migration patterns
