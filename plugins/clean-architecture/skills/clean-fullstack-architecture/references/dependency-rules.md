# Dependency Rules - Detailed Reference

## The Dependency Inversion Principle in Practice

The key insight of Hexagonal Architecture: **business logic defines interfaces (ports), and outer layers implement them (adapters)**. The domain says "I need a way to fetch slides" (port), and the service layer provides the HTTP implementation (adapter).

In TypeScript/React apps, this usually manifests as:
- Domain exports pure functions and domain models
- Services own the DTOs their external system speaks, and convert them through an adapter so every public method returns a domain model
- Adapters are the single seam where both shapes are visible
- Feature hooks compose services and domain logic, then feed results to components via props

The DTO/adapter split is what makes the inversion real rather than nominal. Without it, the
"domain model" is whatever the API decided to return, and a backend rename becomes a change to
the business logic.

## Forbidden Import Patterns

### Domain must NEVER import from services

```typescript
// BAD - domain depends on external concern
import { api } from '@/services/api-client';

// GOOD - domain is pure
import type { Slide } from '@/models/presentation.model';
export function validateSlide(slide: Slide): ValidationResult { ... }
```

### Domain must NEVER name a DTO

```typescript
// BAD - business rule reading the wire shape; a backend rename breaks the domain
import type { UserDto } from '@/services/dto/user.dto';
export function isActive(user: UserDto): boolean {
  return user.deactivated_at === null;
}

// GOOD - the adapter already resolved this into a domain concept
import type { User } from '@/models/user.model';
export function canPromote(user: User): boolean {
  return user.isActive && user.tenureYears >= 1;
}
```

The same applies to a DTO reaching the domain indirectly — as a generic argument, a
`ReturnType<typeof SomeService.get>`, or a structurally-identical inline type. If the field names
came from the wire, it is a DTO whatever it is called.

### Services must NEVER return a DTO

```typescript
// BAD - the wire shape escapes into the hook, the query cache, and every component below
export class UserService {
  static async getById(id: string): Promise<UserDto> {
    return apiClient.get<UserDto>(`/users/${id}`);
  }
}

// GOOD - the boundary converts, so callers only ever see a domain model
export class UserService {
  static async getById(id: string): Promise<User> {
    return userAdapter.toDomain(await apiClient.get<UserDto>(`/users/${id}`));
  }
}
```

### Adapters must NEVER do I/O

```typescript
// BAD - the adapter fetches, so it is really a second service
import { UserService } from '@/services/user.service';
export const orderAdapter = {
  async toDomain(dto: OrderDto): Promise<Order> {
    const owner = await UserService.getById(dto.owner_id); // I/O + a service->adapter->service cycle
    return { id: dto.order_id, owner };
  },
};

// GOOD - the adapter maps what it was given; the service composes the calls
export const orderAdapter = {
  toDomain(dto: OrderDto, owner: User): Order {
    return { id: dto.order_id, owner };
  },
};
```

### Components must NEVER import from domain or services

```typescript
// BAD - component knows about business logic
import { calculateScore } from '@/domain/scoring';

// GOOD - component receives computed value via props
interface ScoreDisplayProps { score: number; maxScore: number; }
```

A generic, side-effect-free hook from top-level `hooks/` is fine in a component — a UI utility,
not a data source. The line is what the hook *brings in*:

```typescript
// OK - generic UI utility, no data, no outside side effect
import { useMediaQuery } from '@/hooks/useMediaQuery';

// BAD - the component now owns data fetching; it belongs in containers/
import { useSlides } from '@/features/slides/hooks/useSlides';
```

### Top-level hooks must NEVER contain business logic

```typescript
// BAD - business logic in a hook
export function useDiscount(price: number, userTier: string) {
  const discount = userTier === 'premium' ? 0.2 : 0.1; // This is domain logic
  return price * (1 - discount);
}

// GOOD - hook is a generic utility
export function useDebounce<T>(value: T, delay: number): T { ... }
```

### Features must NEVER import from other features

```typescript
// BAD - cross-feature dependency
import { useAuth } from '@/features/auth/hooks/useAuth';

// GOOD - extract shared logic to top-level domain/services/hooks
import { useAuth } from '@/hooks/useAuth'; // or @/services/auth.service
```

## Edge Cases

### The DTO is identical to the domain model

Keep both types and write the trivial adapter anyway. Today's identity is a coincidence of the
current API, and the cost of collapsing them is paid later: the first backend rename turns a
one-line adapter change into an edit across the domain, the hooks, and the components. Do not
alias them (`type UserDto = User`) — that is the same coupling with extra ceremony.

### The API returns a different shape per endpoint

One DTO per *response shape*, not per entity: `UserSummaryDto` for the list endpoint,
`UserDetailDto` for the detail endpoint. The adapter exposes one method per shape
(`toDomain`, `toDomainFromSummary`), and both produce the same domain model — with the summary
mapping either filling defaults or producing a narrower model the domain declares explicitly.
Never let "the list endpoint returns a partial user" become optional fields on the domain model.

### A service call needs data from two endpoints

The **service** composes the calls; the adapter stays pure and takes both pieces as arguments
(`orderAdapter.toDomain(orderDto, ownerDto)`). If the composition needs a *different* resource's
service, that is a signal to compose in a feature hook instead — one service class never calls
another.

### Third-party SDK types

An SDK's exported response type *is* the DTO — re-export it from `services/dto/` rather than
hand-copying it, and keep it behind the adapter exactly like a hand-written DTO. The domain must
never import a type from a vendor package.

### Where write-direction mapping goes

In the same adapter, as a separate method (`toCreateDto`, `toPatchDto`). Take the narrowest input
that expresses the intent — the changed fields, not the whole model — so a partial update does
not require constructing a full domain object first.

### Testing a static-method service

Substitution is at the module level (`vi.mock('@/services/user.service')`), not by injecting an
instance. That means the adapter carries the logic worth unit-testing: it is pure, synchronous,
and testable without any mocking at all. Test adapters directly, and mock services at their
module boundary in hook and container tests.

### Server functions and services

A `createServerFn` wrapper is the transport, like the oRPC client — it belongs behind a service
class, not in a hook. The DTO/adapter boundary still applies on whichever side owns the external
call: a server function reading a third-party API converts to domain models before returning, so
the wire shape never crosses to the client. See the `clean-tanstack-start` skill for the file
suffixes that keep those modules server-only.

### Shared types between features

Extract to `models/`. A feature-specific type needed by another feature is a signal it should be promoted to a shared model.

### Feature needs another feature's service

Extract the service to top-level `services/`. Two features needing the same API adapter means it belongs at the top level.

### Component needs to format business data

Create a pure formatting function in `domain/` or `libs/` and pass the formatted result as a prop. The component never imports the formatter directly from domain.

### Where do React context providers go?

- Generic UI contexts (theme, toast) -> `components/` or `libs/`
- Feature-specific contexts -> `features/<name>/`
- App-wide data contexts -> Consider if they should be a service + hook composition

### Domains, sub-domains, and the `common/` slot

Features are grouped by **domain** (a product area), and a domain may nest into sub-domains
(usually platforms) with an optional per-surface level below — but only when it earns the
nesting (see the skill's "Domain-cohesive feature grouping"). The dependency rules on that
shape:

- **Domains don't cross-import.** One domain never imports another domain's internals —
  the "features must not cross-depend" rule, read at the domain granularity.
- **A sub-domain may consume its domain's `common/`.** Platform code composes the
  cross-platform core in `common/`.
- **`common/` never depends on a sub-domain.** If `common/` appears to need a platform,
  invert the edge: have each platform **self-register** into a registry `common/` reads,
  or wire the platforms together at the **domain root/barrel** rather than inside `common/`.

```typescript
// BAD - common/ reaches into a sub-domain
// features/socials/common/containers/postPreviews.ts
import { BlueskyPostPreview } from '../../bluesky/components/BlueskyPostPreview';

// GOOD - common/ exposes a registry; each platform registers itself
// features/socials/common/containers/postPreviews.ts
export function registerPostPreview(platform: string, c: PostPreviewComponent) { ... }
// features/socials/bluesky/index.ts
registerPostPreview(BLUESKY_RENDERER_ID, BlueskyPostPreview);
```

- **Shared registries are the sanctioned cross-domain seam.** A genuinely cross-domain
  registry (the renderer registry, the editor-surface registry) lives in its shared
  top-level location and is consumable by any domain — that indirection, not a direct
  import, is how one domain discovers another's contributions.

## Migration Patterns

### Moving logic from component to domain

1. Identify the pure logic (no React APIs, no side effects)
2. Extract to a function in `domain/`
3. Import in the feature hook, pass result to component via props
4. Verify component no longer imports from `domain/`

### Introducing the DTO/adapter boundary into a service that returns raw responses

When a service hands the API's own shape upward, the wire shape is already spread across hooks,
containers, and components. Unpick it from the inside out:

1. **Name the current shape as a DTO.** Move the response interface to
   `services/dto/<resource>.dto.ts` unchanged — no renaming yet. Everything still compiles.
2. **Write the domain model** in `models/<resource>.model.ts` the way the *domain* wants it: its
   own field names, real `Date`s, unions instead of nullable flags. Decide this from the
   business, not from the DTO.
3. **Write the adapter** in `adapters/<resource>.adapter.ts` — `toDomain(dto) => model` — and
   unit-test it. It is pure, so this is the cheapest test in the migration.
4. **Convert at the service boundary.** Change each public method's return type to the domain
   model and map through the adapter. Every consumer now fails to typecheck; that failure list is
   the exact scope of the change.
5. **Fix consumers upward**, replacing wire field names with model ones. Any consumer that was
   doing its own date parsing, null-collapsing, or field renaming loses that code — the adapter
   now owns it.
6. **Convert the functions to a static-method class** last, once the shapes are settled, so the
   two refactors don't interleave in the same diff.
7. **Verify** no DTO type is imported outside `services/` and `adapters/`.

### Moving shared feature code to top level

1. Identify code used by 2+ features
2. Determine which layer it belongs to (model, domain, service, component, hook, lib)
3. Move to the appropriate top-level directory
4. Update imports in all consuming features
5. Verify no circular dependencies introduced

### Regrouping a type-grouped domain into domain-cohesive shape

When a product area is scattered across type-grouped slices (`x-renderer`, `x-viewer`,
`x-editor`), consolidate it under one `features/<domain>/`:

1. **Inventory** every slice that belongs to the domain and classify each file as
   cross-platform (`common/`) or platform-specific (a sub-domain).
2. **Promote genuinely cross-domain seams first.** Anything shared beyond this domain — a
   cross-domain registry, a shared dumb component — moves to its shared top-level home, not
   under the domain. Add public exports for the registry so consumers reach it by alias.
3. **Move the cross-platform core into `common/`**, preserving the clean layers
   (`domain/`, `containers/`, `hooks/`, `server/`). Keep server-only code out of the
   client barrel.
4. **Extract each platform into a sub-domain**, moving its renderer config + registration
   and its components; shared value constants stay in `common/`.
5. **Invert any `common/ → platform` edge** into self-registration: `common/` exposes a
   registry, each platform's barrel registers into it (see above).
6. **Wire barrels as re-exports, not bare imports** — a re-export (`export * from "./x"`)
   carries the module's self-registration side effect *and* its symbols, so both survive.
   The domain root barrel re-exports `common/` plus each platform; keep it a superset of
   the old public barrel so external importers are unaffected.
7. **Re-point external importers** to the new domain barrel / sub-paths, prefer `git mv`
   so history follows, and verify no new type errors and a green build (the build proves
   self-registration survives tree-shaking).
