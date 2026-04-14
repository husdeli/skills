---
name: clean-fullstack-architecture
description: "Use when: planning a feature implementation, designing a feature, creating an implementation plan, planning architecture, writing feature code, creating a new feature, adding a service, structuring the project, adding a component, adding a hook, adding domain logic, or writing any production code. Enforces Clean Code principles and Hexagonal Architecture with strict dependency rules across all layers."
---

# Clean Fullstack Architecture

This skill enforces Clean Code principles and Hexagonal Architecture (Ports & Adapters) when designing implementations and writing code. The core idea: business logic is at the center, with no knowledge of the outside world. External concerns (APIs, UI frameworks) depend inward toward the domain, never the reverse.

## Core Principles

1. **Dependency Rule**: Dependencies point inward. Outer layers depend on inner layers, never the reverse.
2. **Separation of Concerns**: Each layer has a single responsibility and a clear boundary.
3. **Framework Independence**: Business logic must not import framework-specific code (React hooks, API clients, etc.).
4. **Testability**: Every layer can be tested in isolation by mocking the layer it depends on.

## Project Structure

```
src/
├── models/          # Innermost layer - pure data types
├── domain/          # Business logic - depends only on models
├── components/      # Dumb UI components - no domain/data imports
├── containers/      # Smart components - compose hooks with dumb components
├── hooks/           # Top-level React hooks - no domain/data imports
├── libs/            # Independent library modules
├── services/        # Data layer - external API interactions
├── features/        # Feature modules (compose all layers)
│   └── <feature>/
│       ├── domain/
│       ├── components/
│       ├── containers/
│       ├── hooks/
│       ├── consts/
│       └── services/
└── ...
```

## Layer Definitions and Dependency Rules

### 1. `models/` - Data Models (Innermost)

TypeScript types, interfaces, and enums that define the shape of business data. Types alone are usually sufficient; classes or additional logic may be added when genuinely needed, but are not the default. No imports from any other project layer.

**Allowed dependencies:** None (zero imports from project layers)

```typescript
// models/presentation.ts
export interface Slide {
  id: string;
  title: string;
  content: SlideContent[];
  order: number;
}

export type SlideContent = TextBlock | ImageBlock | ChartBlock;
```

### 2. `domain/` - Business Logic

Pure functions and logic that operate on models. This layer defines *what the app does* without knowing *how* data arrives or *how* results are displayed.

**Allowed dependencies:** `models/`, other `domain/` layers (including feature-level domain layers)  
**Forbidden:** Any import from `services/`, `components/`, `hooks/`, or external API/framework code

```typescript
// domain/presentation-logic.ts
import type { Slide } from '@/models/presentation';

export function reorderSlides(slides: Slide[], fromIndex: number, toIndex: number): Slide[] {
  // Pure business logic - no API calls, no React
}
```

### 3. `components/` - Dumb UI Components

Presentational React components that receive all data via props. Reusable across any feature. Must not import from `domain/`, `services/`, `features/`, or any data-fetching code.

**Allowed dependencies:** Other `components/`, `libs/`, third-party UI libraries  
**Forbidden:** `domain/`, `services/`, `features/`, `hooks/` (top-level), direct state management

```typescript
// components/SlideCard.tsx
interface SlideCardProps {
  title: string;
  thumbnail: string;
  isActive: boolean;
  onSelect: () => void;
}

export function SlideCard({ title, thumbnail, isActive, onSelect }: SlideCardProps) {
  // Pure presentation - all data comes through props
}
```

### 4. `containers/` - Smart Components

Connected React components that wire hooks to presentational components. They own local UI state, call hooks to access data and actions, and pass everything down to dumb `components/` via props. Not reusable across contexts — each container is purpose-built for a specific screen or section.

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

### 5. `hooks/` - Top-Level React Hooks

Reusable React hooks for cross-cutting UI concerns (media queries, local storage, debounce, etc.). These are UI utilities, not business logic containers.

**Allowed dependencies:** Other `hooks/`, `libs/`, React APIs  
**Forbidden:** `domain/`, `services/`, `features/`

```typescript
// hooks/useMediaQuery.ts
export function useMediaQuery(query: string): boolean {
  // Generic, reusable - no business logic
}
```

### 6. `libs/` - Independent Library Modules

Self-contained utility packages that could theoretically be extracted as standalone npm packages. Each subfolder is an independent module.

**Allowed dependencies:** Other `libs/` modules, third-party packages  
**Forbidden:** Any project-specific layer (`models/`, `domain/`, `services/`, `features/`, `components/`, `hooks/`)

```typescript
// libs/color-utils/index.ts
export function parseHexColor(hex: string): RGB { ... }
export function deriveContrastColor(color: RGB): RGB { ... }
```

### 7. `services/` - Data/API Layer (Outermost)

Adapters for external systems (REST APIs, WebSocket, localStorage, etc.). Services implement ports defined by the business logic. Services depend on domain logic to transform data - **the domain never imports from services**.

**Allowed dependencies:** `models/`, `domain/`, `libs/`, feature-level `models/`, third-party HTTP/API clients  
**Forbidden:** `components/`, `containers/`, `hooks/`, `features/`

```typescript
// services/presentation-api.ts
import type { Slide } from '@/models/presentation';
import { validateSlideOrder } from '@/domain/presentation-logic';

export async function fetchSlides(presentationId: string): Promise<Slide[]> {
  const response = await api.get(`/presentations/${presentationId}/slides`);
  return response.data;
}
```

### 8. `features/` - Feature Modules (Composition Layer)

Each subfolder is a self-contained feature that composes all necessary layers. Features are where dependency inversion meets the UI - they wire services to domain logic to components.

**Internal structure per feature:**
- `domain/` - Feature-specific business logic (depends on top-level `models/`)
- `components/` - Feature-specific dumb UI (can use top-level `components/`)
- `containers/` - Feature-specific smart components (wire feature hooks to components)
- `hooks/` - Feature-specific hooks (wire services + domain + UI)
- `consts/` - Feature-specific constants
- `services/` - Feature-specific API adapters

**Allowed dependencies:** All top-level layers (`models/`, `domain/`, `components/`, `hooks/`, `libs/`, `services/`)  
**Forbidden:** Other `features/` (features must not cross-depend)

```typescript
// features/slide-editor/hooks/useSlideEditor.ts
import { reorderSlides } from '@/domain/presentation-logic';
import { fetchSlides, saveSlides } from '@/services/presentation-api';
import type { Slide } from '@/models/presentation';

export function useSlideEditor(presentationId: string) {
  // Wires together domain logic + services + React state
}
```

## Dependency Matrix (Quick Reference)

| Layer           | models | domain | components | containers | hooks | libs | services | features |
|-----------------|--------|--------|------------|------------|-------|------|----------|----------|
| **models**      | -      | NO     | NO         | NO         | NO    | NO   | NO       | NO       |
| **domain**      | YES    | YES    | NO         | NO         | NO    | NO   | NO       | NO       |
| **components**  | NO     | NO     | YES        | NO         | NO    | YES  | NO       | NO       |
| **containers**  | YES    | NO     | YES        | -          | YES   | YES  | NO       | NO       |
| **hooks**       | NO     | NO     | NO         | NO         | YES   | YES  | NO       | NO       |
| **libs**        | NO     | NO     | NO         | NO         | NO    | YES  | NO       | NO       |
| **services**    | YES    | YES    | NO         | NO         | NO    | YES  | -        | models only |
| **features**    | YES    | YES    | YES        | YES        | YES   | YES  | YES      | NO       |

## Implementation Workflow

When designing or implementing a feature:

1. **Start with models** - Define the data types the feature needs
2. **Write domain logic** - Implement pure business rules using only models
3. **Build services** - Create API adapters that use domain logic for validation/transformation
4. **Create dumb components** - Build presentational UI that takes props
5. **Wire in feature hooks** - Compose services + domain + state in feature-specific hooks
6. **Build containers** - Connect feature hooks to dumb components in smart container components

## Validation Rules

Before writing or reviewing code, verify:

- [ ] No circular dependencies between layers
- [ ] `domain/` has zero imports from `services/`, `components/`, or `hooks/`
- [ ] `components/` has zero imports from `domain/`, `services/`, `hooks/`, or `features/`
- [ ] `containers/` has zero imports from `domain/`, `services/`, or `features/`
- [ ] `hooks/` (top-level) has zero imports from `domain/`, `services/`, or `features/`
- [ ] `libs/` has zero imports from any project-specific layer
- [ ] `models/` has zero imports from any other project layer
- [ ] Features do not import from other features
- [ ] All business logic lives in `domain/` or `features/<name>/domain/`, never in components or hooks

## React-Specific Architecture Guidelines

### Avoid Overusing Effects

Effects are an escape hatch for synchronizing with external systems. Most data derivation, filtering, or transformation belongs in render logic or `domain/` functions — not in `useEffect`.

Before writing a `useEffect`, ask: is this synchronizing with something *outside* React (DOM, WebSocket, third-party lib)? If not, it likely doesn't need an Effect.

**Common mistakes to avoid:**

- Deriving state from props/state inside `useEffect` — compute it inline during render or in a `domain/` function instead
- Fetching data in `useEffect` inside components — fetch in hooks (`hooks/` or `features/<name>/hooks/`) and expose the result as state
- Chains of `useEffect` that update state triggering other effects — flatten into a single computation in `domain/`
- Using `useEffect` to handle user events — move logic to event handlers directly

**Where logic belongs instead:**

| Concern | Wrong place | Right place |
|---------|-------------|-------------|
| Derived/computed values | `useEffect` + `setState` | Inline in render or `domain/` function |
| Data fetching | Component `useEffect` | Feature hook (`features/<name>/hooks/`) |
| Cross-cutting UI side effects | Component `useEffect` | Top-level hook (`hooks/`) |
| Business rules on events | `useEffect` watching state | Event handler calling `domain/` function |

Reference: [You Might Not Need an Effect](https://react.dev/learn/you-might-not-need-an-effect)

### Styling Approach

Prefer styles co-located with the component, in this order:

1. **Tailwind CSS utility classes** — default choice for all styling. Apply classes directly on JSX elements. Keep conditional class logic readable using `clsx` or `cn` helpers.
2. **CSS-in-JS** (e.g. `styled-components`, `emotion`) — acceptable when dynamic styles depend on runtime values that would make Tailwind class strings unwieldy.
3. **Separate `.css` / `.module.css` files** — use only exceptionally, for cases that cannot be handled by the above (e.g. complex keyframe animations, third-party component overrides, or global resets).

**Rules:**
- Never mix all three approaches in the same component — pick one and stay consistent within a file
- Global styles (resets, CSS variables, font-face) live in a single top-level stylesheet (e.g. `src/styles/globals.css`)
- Design tokens (colors, spacing, radii) should be defined as Tailwind theme values or CSS custom properties — never as magic strings scattered across components

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

Use **React Query** (`useQuery`, `useMutation`) as the data-fetching layer, with **oRPC** as the typed router when available. Never call service functions or fetch APIs directly inside components or containers.

**Layer responsibilities:**

| Layer | Role |
|-------|------|
| `services/` or `features/<name>/services/` | oRPC router client / API adapter — defines typed procedures |
| `features/<name>/hooks/` | Custom hooks wrapping `useQuery`/`useMutation` — single source of truth for a resource |
| `containers/` or `features/<name>/containers/` | Consumes the custom hook, passes data to dumb components |
| `domain/` | Transforms or validates data returned from the hook before rendering |

**Canonical pattern:**

```typescript
// services/orpc.ts — oRPC client setup (if oRPC is available)
import { createORPCClient } from '@orpc/client';
export const orpc = createORPCClient<AppRouter>({ baseURL: '/api' });

// features/slides/hooks/useSlides.ts — custom query hook
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { orpc } from '@/services/orpc'; // or a plain service function if no oRPC

export function useSlides(presentationId: string) {
  const queryClient = useQueryClient();

  const slides = useQuery({
    queryKey: ['slides', presentationId],
    queryFn: () => orpc.slides.list({ presentationId }),
  });

  const reorder = useMutation({
    mutationFn: orpc.slides.reorder,
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
      onReorder={(from, to) => reorder.mutate({ presentationId, from, to })}
    />
  );
}
```

**Rules:**
- One custom hook per resource/domain entity — don't scatter `useQuery` calls across multiple components
- `queryKey` arrays must be consistent — define them as constants in `features/<name>/consts/` if reused
- Data transformation (sorting, filtering, deriving) happens in `domain/` functions, not inside the hook or component
- If oRPC is not available, the hook calls a plain `services/` function instead — the hook interface stays the same

## Additional Resources

### Reference Files

For detailed patterns and examples, consult:
- **`references/dependency-rules.md`** - Comprehensive dependency rules with edge cases and migration patterns
