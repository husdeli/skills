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
