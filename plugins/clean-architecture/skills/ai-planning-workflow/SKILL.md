---
name: ai-planning-workflow
description: "Feedback-driven development workflow for implementing tickets and planning features. Use when: starting work on a ticket, creating a ticket, creating an implementation plan, planning a feature, building UI that needs design agreement, requesting feedback after completing a step, marking a ticket complete. Covers ticket creation guidelines, phased implementation with feedback checkpoints, design agreement for UI work, and iteration logging."
---

# AI Planning Workflow

A structured, feedback-driven methodology for implementing tickets and features — without completing entire features without review.

## Core Principles

**Never complete an entire feature or ticket without requesting feedback multiple times throughout the process.**

**Keep specs short and scannable.** Every sentence must add information. No filler, no restating the obvious. If a task is too complex to describe concisely, split it into multiple tickets or subtasks instead of writing a bloated spec.

**Everything this workflow produces is read by a person.** Load the **`clean-writing`** skill before you write a ticket, a plan, a feedback request, a design-agreement proposal, or an iteration log, and follow it for every sentence — context first, one idea per sentence, the active voice, and the project's own term for each concept. This skill decides *what to write and when*; `clean-writing` decides *how it reads*.

---

## Phase 1: Understand the Ticket

1. Read the ticket thoroughly — acceptance criteria, technical notes, related tickets
2. Ask clarifying questions if anything is unclear — don't assume
3. Confirm architectural decisions before starting
4. Once the work starts, set the ticket's status to `In Progress` and move the file into
   `in-progress/` — see [Where tickets live](#where-tickets-live)

---

## Phase 1.5: Interview & Challenge (before planning)

Don't plan on unchallenged assumptions. For any non-trivial feature, run a discovery pass **before** writing the plan:

1. Read `.clean-architecture/prd.md` and `.clean-architecture/design.md` if they exist — for product intent and intended UX. Note where the ticket diverges. Fall back to the project root when the folder is absent.
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

**Never mark a ticket Complete without explicit user approval.** On approval, write the status
into the ticket and move the file into `done/` in the same step — see
[Where tickets live](#where-tickets-live).

---

## Ticket Creation Guidelines

### Where tickets live

**Tickets live in `.clean-architecture/tickets/`, in one folder per status**, one file per
ticket, named `<ID>-<slug>.md` (e.g. `SW-001-user-login.md`):

```
.clean-architecture/tickets/
  TEMPLATE.md          copy this per ticket — the template itself never moves
  todo/                SW-001-user-login.md
  in-progress/         SW-002-session-timeout.md
  done/                SW-003-password-reset.md
```

The folder is the board. The `**Status**` field inside the file is the record. The two never
disagree, because the file moves in the same step that rewrites its status field. Five status
values map onto three folders:

| Status field | Folder |
| --- | --- |
| `Not Started` | `todo/` |
| `In Progress`, `Blocked`, `Review` | `in-progress/` |
| `Completed` | `done/` |

**Move a ticket with `git mv`**, so the file keeps its history. Move it plainly in a project
without git.

**Find a ticket by its ID, never by a stored path** — the path changes as the work progresses.
Glob `.clean-architecture/tickets/*/<ID>-*.md` first, then `.clean-architecture/tickets/<ID>-*.md`
for a project that still keeps its tickets flat. Cite a ticket by file name, so that no later
move invalidates the reference.

**A flat `tickets/` folder stays flat.** Never build the status folders around tickets that are
already in flight. Keep writing the status field in place, and name the platform's scaffold
entry point as the way to migrate. Run that entry point when the tickets folder does not exist
at all. The roadmap that orders the tickets is `.clean-architecture/roadmap.md`. A project that
already keeps tickets elsewhere keeps them there — do not start a second home.

**Tickets describe WHAT, not HOW:**

✅ Include: requirements, acceptance criteria, UX description, business logic, high-level architecture, data needs, testing expectations  
❌ Exclude: specific file paths, implementation-level names, internal module structure, data layer details, code-level patterns

---

## Templates

- [Ticket template](./assets/ticket-template.md)
- [Plan template](./assets/plan-template.md)
- [Full ticket guidelines](./references/ticket-guidelines.md)

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
