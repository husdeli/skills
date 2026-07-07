# Ticket Creation Guidelines

Tickets describe WHAT needs to be built, not HOW. Keep them short and scannable — if a task is too complex to describe concisely, split it into multiple tickets.

---

## ✅ Include

- **Requirements**: What features/functionality to deliver
- **Acceptance Criteria**: Observable outcomes and behaviours
- **User Experience**: How users interact with the feature
- **Business Logic**: Rules and constraints
- **High-Level Architecture**: Data flow, reusability principles
- **Data Requirements**: What data needs storing/retrieval (not schema details)
- **Testing Expectations**: What needs testing (not specific test files)

---

## ❌ Exclude

- Specific file paths
- Library/package names
- Component/module names
- Implementation patterns
- Data schema details
- Code-level details (imports, hooks, syntax)

Implementation decisions belong in the plan created during Phase 2, after codebase exploration.

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
