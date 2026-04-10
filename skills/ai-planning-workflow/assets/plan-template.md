# [Feature Name] Development Plan

**Created**: YYYY-MM-DD  
**Status**: Draft | In Progress | Completed

## 1. Feature Overview

### What We're Building

[Clear description of the feature]

### Why We're Building It

[Problem being solved, user need, business value]

### Expected User Impact

[How this improves user experience or capabilities]

---

## 2. Technical Approach

### High-Level Architecture

[Overall design and component structure]

### Design Decisions & Rationale

[Important architectural choices and why they were made]

### Code Reusability Analysis

- **Can be shared**: [Parts that could be reused across features/projects]
- **Feature-specific**: [Parts unique to this feature]

---

## 3. Implementation Steps with Feedback Checkpoints

**IMPORTANT**: Each step includes a feedback checkpoint where the AI agent must request user validation before proceeding.

### Step 1: [Step Name]

**Complexity**: XS | S | M | L | XL

#### What to Implement

- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

#### Deliverable

[Specific, testable outcome]

#### Feedback Checkpoint 🔍

**When**: After completing all tasks in this step  
**What to show**: [What the user should review]  
**How to verify**: [Instructions for testing/validating]  
**Decision point**: [Any choices the user needs to make before next step]

---

### Step 2: [Step Name]

**Complexity**: XS | S | M | L | XL

#### What to Implement

- [ ] Task 1
- [ ] Task 2

#### Deliverable

[Specific, testable outcome]

#### Dependencies

- Requires Step 1 completion

#### Feedback Checkpoint 🔍

**When**: After completing all tasks in this step  
**What to show**: [What the user should review]  
**How to verify**: [Instructions for testing/validating]  
**Decision point**: [Any choices the user needs to make before next step]

---

### Step 3: [Step Name]

[Continue pattern for remaining steps...]

---

## 4. Code Quality Requirements

### Code Style Checklist

- [ ] Matches existing patterns in modified files
- [ ] Proper error handling
- [ ] Consistent naming conventions
- [ ] Clear, documented code

---

## 5. Testing Strategy

**Preferred order**: Unit tests → Integration/API tests → Frontend E2E (critical paths only).

### Unit Tests

- [What components/functions need unit tests]

### Integration / API Tests (preferred over frontend E2E)

- [Endpoint correctness, access-control rules, error handling, data contracts]

### Frontend E2E Tests (critical paths only)

- Only add browser-level tests for flows that CANNOT be covered by other test types
- [ ] [Critical path 1 — e.g. auth redirect, destructive confirmation]

### Manual Testing Checklist

- [ ] Test case 1
- [ ] Test case 2
- [ ] Edge case handling

---

## 6. Rollout Plan

### Pre-Deployment

- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Documentation updated

### Monitoring & Metrics

- Metrics to track: [usage, errors, performance]
- Alerts to configure: [Critical failure conditions]

### Rollback Procedure

[How to revert if issues arise]

---

## 7. Future Enhancements

[Ideas for iteration or expansion]

## 8. Related Documentation

- [Link to ticket]
- [Link to related plans]

---

## Implementation Progress Tracking

### Completed Steps

- [ ] Step 1
- [ ] Step 2
- [ ] Step 3

### Current Status

**Active Step**: [Current step being worked on]  
**Blockers**: [Any blockers encountered]  
**Next Feedback Checkpoint**: [When next feedback is expected]

### Open Questions

1. [Question 1]
2. [Question 2]
