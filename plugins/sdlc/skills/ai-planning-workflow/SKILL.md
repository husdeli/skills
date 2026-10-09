---
name: ai-planning-workflow
description: "Feedback-driven development workflow for implementing tickets and planning features. Use when: starting work on a ticket, creating a ticket, creating an implementation plan, planning a feature, building UI that needs design agreement, requesting feedback after completing a step, marking a ticket complete. Covers the phased implementation with feedback checkpoints, design agreement for UI work, and when to start, log, and complete a ticket. The ticket, roadmap, assignee, and worklog rules themselves live in the `ticket-board` skill."
---

# AI Planning Workflow

A structured, feedback-driven methodology for implementing tickets and features — without completing entire features without review.

## Core Principles

**Never complete an entire feature or ticket without requesting feedback multiple times throughout the process.**

**Keep specs short and scannable.** Every sentence must add information. No filler, no restating the obvious. If a task is too complex to describe concisely, split it into multiple tickets or subtasks instead of writing a bloated spec.

**The board has its own skill.** Load **`ticket-board`** before you touch a ticket, a roadmap row,
or a worklog. It holds where each one lives, what its fields mean, and what every status transition
has to write.

**Everything this workflow produces is read by a person.** Load the **`technical-writing`** skill before you write a ticket, a plan, a feedback request, a design-agreement proposal, or a worklog entry, and follow it for every sentence — context first, one idea per sentence, the active voice, and the project's own term for each concept. This skill decides *what to write and when*; `technical-writing` decides *how it reads*.

---

## Phase 1: Understand the Ticket

1. Read the ticket thoroughly — acceptance criteria, technical notes, related tickets
2. Ask clarifying questions if anything is unclear — don't assume
3. Confirm architectural decisions before starting
4. Once the work starts, run the `ticket-board` skill's **Starting a ticket** transition: the
   status, the assignee, the move into `in-progress/`, the new worklog, and the roadmap row, all
   in one tool block

---

## Phase 1.5: Interview & Challenge (before planning)

Don't plan on unchallenged assumptions. For any non-trivial feature, run a discovery pass **before** writing the plan:

1. Read the PRD if it exists, the feature note the ticket's epic code names (`<project>/features/<feature>/<feature>.feature.md`), and the design docs this ticket touches — the ones in that feature's folder first, then `<project>/designs/*.design.md`, or, on an older shape, `<project>/*.design.md` or a single `<project>/design.md` — for product intent and the intended design. Note where the ticket diverges. Fall back to the repository root when there is no project. The `sdlc-structure` skill resolves the project — load it before you resolve a path.
2. Research the feature topic — established approaches, common pitfalls, relevant libraries, UX/security conventions.
3. Explore the codebase for what already exists and can be reused.
4. Turn the fuzzy parts into **explicit high-level decisions** and put them to the user with concrete options and a recommended default:

```markdown
## 🔎 Before I plan: [Feature]

Understanding: [1-2 sentence restatement]

**Decision 1: [question]** — Option A [trade-off] / Option B [trade-off]. Recommend: A because […]
**Decision 2: [question]** — …

Assumptions I'll make unless you say otherwise: […]

Which options do you want?
```

5. Record the answers in the ticket (a **Decisions** section) so the plan and every later step build on settled choices.

Skip this phase only for small, unambiguous changes with no product/UX/architecture forks.

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
5. Append a worklog entry after each checkpoint — what you decided, what the feedback changed,
   and nothing the ticket already says. The worklog sits beside the ticket, and the
   `ticket-board` skill holds its shape:

```markdown
## 2026-09-27 14:12 — coding · step 2 of 4

- Reused the existing retry wrapper instead of adding one — every caller inherits the policy.
- Feedback: the empty state needed a way out. Added the link; nothing else changed.
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

**Never mark a ticket Complete without explicit user approval.** On approval, run the
`ticket-board` skill's **Finishing a ticket** transition in one step: the status, the assignee
back to `—`, the closing worklog entry, the move into `done/` with the worklog, and the task
deleted from the roadmap.

---

## The board is not this skill's job

Where a ticket lives, how it is named and numbered, what its status field and its folder mean, what
the roadmap holds, who the `Assignee` names, and what the worklog records — all of that is the
**`ticket-board`** skill. **Load it before you read, write, move, assign, or complete a ticket**,
and follow it. This skill decides *when* in the workflow each of those happens; `ticket-board`
decides *what gets written*.

Two of its rules carry every phase above, so they are worth naming here:

- **A ticket describes WHAT, not HOW** — requirements, acceptance criteria, behaviour, and
  constraints. Never a file path, a module name, or a code-level pattern: those belong to the plan
  in Phase 2, written after the codebase is explored.
- **A status transition writes the status field, the folder, and the roadmap row in one tool
  block.** Phase 1 starts the ticket; Phase 4 finishes it.

---

## Templates

- [Plan template](./assets/plan-template.md)
- The ticket template, the worklog template, and the full ticket guidelines live with the
  **`ticket-board`** skill, beside the rules that govern them.

---

## Response Patterns

| User says                     | Your action                                                        |
| ----------------------------- | ------------------------------------------------------------------ |
| "Looks good, continue"        | Append a worklog entry → proceed to next step                       |
| "Can you change X to Y?"      | Acknowledge → clarify if needed → implement → request feedback     |
| "Why did you do it this way?" | Explain rationale → adjust if needed → request feedback            |
| "This won't work because..."  | Mark Blocked, assignee `user` → log the blocker → propose solutions → wait |
| "Can we also add Z?"          | Assess scope → update ticket if needed → get approval for approach |

---
