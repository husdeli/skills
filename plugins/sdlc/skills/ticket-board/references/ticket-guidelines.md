# Ticket Creation Guidelines

Tickets describe WHAT needs to be built, not HOW. Keep them short and scannable — if a task is too complex to describe concisely, split it into multiple tickets.

---

## ✅ Include

- **Feature**: The `feature` property links the feature note the ticket delivers. That feature's
  code prefixes the ticket ID, and the numbering restarts at 001 inside each epic.
- **Priority and dependencies**: `priority`, and `depends_on` with the ID of every ticket this one
  cannot start without.
- **Times**: `createdAt` and `updatedAt`, both set to now. A new ticket has no `claimed` and no usage, and
  `assigned` only when the agent planned to work on it is already known; the run writes the rest as
  the work moves.
- **Requirements**: What features/functionality to deliver
- **Acceptance Criteria**: Observable outcomes and behaviours
- **Decisions**: Each choice planning settled with the person, one line with its reason. The
  run treats each one as a fixed constraint. This is the one place a library may be named, when
  the person chose it.
- **User Experience**: How users interact with the feature
- **Business Logic**: Rules and constraints
- **High-Level Architecture**: Data flow, reusability principles
- **Data Requirements**: What data needs storing/retrieval (not schema details)
- **Related documents**: The design docs the ticket builds, in the `related:` frontmatter
  property. The body holds no Related section. The `sdlc-structure` skill holds the rule.

---

## ❌ Exclude

- Specific file paths
- Library/package names, except one the person chose, recorded under Decisions
- Component/module names
- Implementation patterns
- Data schema details
- Code-level details (imports, hooks, syntax)
- Testing — what to test, test levels, manual scenarios. The test plan written during the run owns it

Implementation decisions belong in the plan written after the codebase is explored.

---

## Good vs Bad Example

❌ **Bad** (prescriptive):

```markdown
### Files to Create

- `src/components/Header.tsx`
- `src/components/UserMenu.tsx`

### Dependencies

- [UI library]: Avatar, Menu, Button components
- [Auth library]: useUser() hook
```

✅ **Good** (outcome-focused):

```markdown
### Components Needed

- Header with branding and user profile area
- User menu with profile info and sign-out action

### Architectural Considerations

- Header reusable across authenticated pages
- Use existing auth system for user data
```
