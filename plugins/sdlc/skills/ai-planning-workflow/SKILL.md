---
name: ai-planning-workflow
description: "Builds a ticket in phases, with a feedback checkpoint after each step and a design agreement before UI work. Use when starting, logging, or completing a ticket by hand, planning a feature, or asking for feedback on a step."
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
   claim, the `status` and `assigned`, the move into `work/in-progress/`, the new worklog, and the
   roadmap row, all in one tool block

---

## Phase 1.5: Interview & Challenge (before planning)

Don't plan on unchallenged assumptions. For any non-trivial feature, run a discovery pass **before** writing the plan:

1. Read the PRD if it exists, the feature note the ticket's `feature` property links (`features/<feature>/<feature>.feature.md`), and the design docs this ticket touches — the ones in that feature's folder first, then `designs/*.design.md`, or, on an older shape, a project's `*.design.md` or a single `design.md` — for product intent and the intended design. Note where the ticket diverges. Fall back to the repository root when there is no framework root. The `sdlc-structure` skill resolves the framework root and the project — load it before you resolve a path.
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

5. Write each answer into the ticket's **Decisions**, one line with its reason, as the `ticket-board` ticket guidelines say — every later step treats it as a fixed constraint. The worklog entry for this phase records what each decision beat and each assumption the user confirmed.

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

Run the **`mockup-agreement`** skill (namespaced `sdlc:mockup-agreement`). It says when the step can be skipped, publishes a static mockup as an Artifact with every state it lists, and iterates until the user agrees. **Do not start business logic until the user signs the design off.** Carry what they agreed — the artifact URL, the states it covers, and the layout and component decisions — into Phase 3.

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

Mark as done?
```

**Never mark a ticket `done` without explicit user approval.** On approval, run the
`ticket-board` skill's **Finishing a ticket** transition in one step: `status` to `done`,
`assigned` and `claimed` removed, the usage added, the closing worklog entry, the move into
`work/done/` with the worklog, and the row deleted from the roadmap.

---

## The board is not this skill's job

Where a ticket lives, how it is named and numbered, what its `status` and its bucket mean, what
the roadmap holds, who `assigned` and `claimed` name, and what the worklog records — all of that is the
**`ticket-board`** skill. **Load it before you read, write, move, assign, or complete a ticket**,
and follow it. This skill decides *when* in the workflow each of those happens; `ticket-board`
decides *what gets written*.

Two of its rules carry every phase above, so they are worth naming here:

- **A ticket describes WHAT, not HOW** — requirements, acceptance criteria, behaviour, and
  constraints. Never a file path, a module name, or a code-level pattern: those belong to the plan
  in Phase 2, written after the codebase is explored.
- **A status change writes `status`, `assigned`, `updatedAt`, the bucket, the roadmap row, and the
  worklog in one tool block.** Phase 1 starts the ticket; Phase 4 finishes it.

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
| "This won't work because..."  | Mark `blocked` with a `blocked_by` line → log the blocker → propose solutions → wait |
| "Can we also add Z?"          | Assess scope → update ticket if needed → get approval for approach |

---
