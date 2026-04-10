# Ticket Creation Guidelines

When creating tickets, focus on WHAT needs to be built, not HOW to build it.

---

## ✅ DO Include in Tickets

- **Requirements**: What features/functionality need to be delivered
- **Acceptance Criteria**: Observable outcomes and behaviours
- **User Experience**: How users will interact with the feature
- **Business Logic**: What rules and constraints apply
- **High-Level Architecture**: Data flow patterns, reusability principles
- **Data Requirements**: What data needs to be stored or retrieved (not schema details)
- **Testing Expectations**: What needs to be tested (not specific test files)

---

## ❌ DON'T Include in Tickets

- **Specific File Paths**: Don't list exact files to create/modify
- **Library/Package Names**: Don't specify which libraries to use
- **Component/Module Names**: Don't dictate internal naming
- **Implementation Patterns**: Don't prescribe specific code patterns
- **Data Schema Details**: Don't specify exact fields and types
- **Code-Level Details**: No import statements, hooks, or syntax

**Implementation Steps must describe WHAT needs to happen (outcomes, behaviour, data shape), NOT HOW to achieve it.** Exact implementation decisions belong in the plan created during Phase 2, after the agent has reviewed the codebase.

---

## Why This Matters

1. **Flexibility**: Allows choosing the best approach based on existing codebase patterns
2. **Evolution**: Codebase patterns may change over time
3. **Autonomy**: Developers can make decisions that fit the current project state
4. **Focus**: Keeps tickets focused on business value and user outcomes

---

## Good vs Bad Example

❌ **Bad** (too prescriptive):

```markdown
## Technical Notes

### Files to Create

- `src/components/Header.tsx`
- `src/components/UserMenu.tsx`

### Dependencies

- [UI library]: Avatar, Menu, Button components
- [Auth library]: useUser() hook
```

✅ **Good** (outcome-focused):

```markdown
## Technical Notes

### Components Needed

- Header with branding and user profile area
- User menu with profile info and sign-out action

### Architectural Considerations

- Header should be reusable across authenticated pages
- Use existing authentication system for user data
- Follow established UI component patterns
```
