# Dependency Rules - Detailed Reference

## The Dependency Inversion Principle in Practice

The key insight of Hexagonal Architecture: **business logic defines interfaces (ports), and outer layers implement them (adapters)**. The domain says "I need a way to fetch slides" (port), and the service layer provides the actual HTTP implementation (adapter).

In TypeScript/React apps, this often manifests as:
- Domain exports pure functions and types
- Services import domain types to ensure API responses conform
- Feature hooks compose services and domain logic, then feed results to components via props

## Forbidden Import Patterns

### Domain must NEVER import from services

```typescript
// BAD - domain depends on external concern
import { api } from '@/services/api-client';

// GOOD - domain is pure
import type { Slide } from '@/models/presentation';
export function validateSlide(slide: Slide): ValidationResult { ... }
```

### Components must NEVER import from domain or services

```typescript
// BAD - component knows about business logic
import { calculateScore } from '@/domain/scoring';

// GOOD - component receives computed value via props
interface ScoreDisplayProps { score: number; maxScore: number; }
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
import { useAuth } from '@/hooks/useAuth'; // or @/services/auth
```

## Edge Cases

### Shared types between features

Extract to `models/`. If the type is feature-specific but needed by another feature, that's a signal it should be promoted to a shared model.

### Feature needs another feature's service

Extract the service to top-level `services/`. If two features need the same API adapter, it belongs at the top level.

### Component needs to format business data

Create a pure formatting function in `domain/` or `libs/`, pass the formatted result as a prop. The component should never import the formatter directly from domain.

### Where do React context providers go?

- Generic UI contexts (theme, toast) -> `components/` or `libs/`
- Feature-specific contexts -> `features/<name>/`
- App-wide data contexts -> Consider if they should be a service + hook composition

### Domains, sub-domains, and the `common/` slot

Features are grouped by **domain** (a product area), and a domain may nest into
sub-domains (usually platforms) with an optional per-surface level below — but only
when it earns the nesting (see the skill's "Domain-cohesive feature grouping"). The
dependency rules on that shape:

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
