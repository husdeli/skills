---
name: ai-planning-workflow
description: "Feedback-driven development workflow for implementing tickets and planning features. Use when: starting work on a ticket, creating a ticket, creating an implementation plan, planning a feature, building UI that needs design agreement, requesting feedback after completing a step, marking a ticket complete. Covers ticket creation guidelines, phased implementation with feedback checkpoints, design agreement for UI work, and iteration logging."
argument-hint: "Optional: ticket ID or feature name to implement"
---

# AI Planning Workflow

A structured, feedback-driven development methodology for implementing tickets and features correctly — without completing entire features without review.

## Core Principles

**Never complete an entire feature or ticket without requesting feedback multiple times throughout the process.**

**Keep specs short and scannable.** Every sentence must add information. No filler words, no restating the obvious. If a task is too complex to describe concisely, split it into multiple tickets or subtasks instead of writing a bloated spec.

## When to Use This Skill

- Starting work on a ticket or feature
- Creating a ticket
- Creating an implementation plan
- Building UI that needs design review
- Requesting feedback after a step
- Writing or reviewing tickets (what to include vs. exclude)
- Marking a ticket as complete

---

## Phase 1: Understand the Ticket

1. Read the ticket thoroughly — acceptance criteria, technical notes, related tickets
2. Ask clarifying questions if anything is unclear — don't assume
3. Confirm architectural decisions before starting

---

## Phase 2: Create & Share the Implementation Plan

After exploring the codebase:

1. Identify existing patterns, libraries, and file organization
2. Break work into **3–7 logical, independently reviewable steps**
3. Share the plan using this format:

```markdown
## Plan: [TICKET-ID]

Following [pattern/convention found in codebase].

**Step 1**: [Description] — Files: [list] — Deliverable: [outcome]
**Step 2**: [Description] — Files: [list] — Deliverable: [outcome]

Feedback requested after each step. Good to go?
```

4. **Wait for plan approval before starting implementation.**

---

## Phase 2.5: Design Agreement (UI Tickets Only)

If the ticket includes **any UI work**, complete this phase before writing business logic.

1. Build a **static prototype** — visual structure only, placeholder data, no live data fetching
2. Cover all meaningful states: empty, loading skeleton, populated, error, mobile
3. Present for review:

```markdown
## 🎨 Design: [Feature Name]

Static prototype — no live data or business logic yet.

- [Component/screen]: [description]
- Preview: [run instructions + URL]
- Decisions: [key choices and rationale]

Changes before I wire up the logic?
```

4. **Iterate until explicitly approved.** Do NOT start business logic until design is signed off.

---

## Phase 3: Iterative Implementation

For **each step**:

1. Implement only that step — don't skip ahead
2. After completing the step, request feedback:

```markdown
## ✅ Step [N]/[Total]: [Step Name]

- [Change 1]
- [Change 2]

Files: Created [paths] / Modified [paths]
Verify: [testing instructions]
Next: [what comes next]

Proceed to Step [N+1]?
```

3. **Wait for explicit approval before proceeding.**
4. If changes requested: implement, then request feedback again.
5. Update the ticket's Iteration Log after each checkpoint:

```markdown
- **Iteration N (YYYY-MM-DD HH:MM)**: [What was done] → [Feedback] → [Changes] → [Status]
```

---

## Phase 4: Final Review & Completion

When all steps are done:

```markdown
## 🎉 Done: [TICKET-ID]

- [x] Criterion 1
- [x] Criterion 2

Tests: [summary] | Files: [list]

Mark as Completed?
```

**Never mark a ticket Complete without explicit user approval.**

---

## Ticket Creation Guidelines

**Summary — tickets should describe WHAT, not HOW:**

✅ Include: requirements, acceptance criteria, UX description, business logic, high-level architecture, data needs, testing expectations  
❌ Exclude: specific file paths, implementation-level names, internal module structure, data layer details, code-level patterns

---

## Templates

- [Ticket template](./assets/ticket-template.md)
- [Plan template](./assets/plan-template.md)
- [Full ticket guidelines](./references/ticket-guidelines.md)
- [Full feedback templates reference](./references/feedback-templates.md)

---

## Response Patterns

| User says                     | Your action                                                        |
| ----------------------------- | ------------------------------------------------------------------ |
| "Looks good, continue"        | Update iteration log → proceed to next step                        |
| "Can you change X to Y?"      | Acknowledge → clarify if needed → implement → request feedback     |
| "Why did you do it this way?" | Explain rationale → adjust if needed → request feedback            |
| "This won't work because..."  | Mark Blocked → document issue → propose solutions → wait           |
| "Can we also add Z?"          | Assess scope → update ticket if needed → get approval for approach |

---
