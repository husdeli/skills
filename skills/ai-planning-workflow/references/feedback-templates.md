# Feedback Templates Reference

Copy-paste templates for each feedback checkpoint in the workflow.

---

## Implementation Plan (Phase 2)

```markdown
## Implementation Plan for [TICKET-ID]

After reviewing the codebase, I'll follow [existing patterns and conventions found].

I'll break this work into X steps:

**Step 1**: [Description]

- Technical approach: [How, based on existing patterns]
- Files: [list files to create/modify]
- Deliverable: [what will be complete]

**Step 2**: [Description]

- Technical approach: [How, based on existing patterns]
- Files: [list files to create/modify]
- Deliverable: [what will be complete]

After each step, I'll request your feedback before continuing.

Does this approach look good? Any concerns or changes?
```

---

## Design Agreement (Phase 2.5 — UI work only)

```markdown
## 🎨 Design Agreement: [Feature Name]

I've built a static prototype before adding any business logic.

### What's Included

- [Screen/component 1]: [description]
- [Screen/component 2]: [description]

### How to Preview

[Run instructions + URL]

### Design Decisions

- [Decision 1 and rationale]
- [Decision 2 and rationale]

### What's NOT Included Yet

- Real data integration (placeholder data used)
- Business logic and validation
- Auth/permission checks

---

**Does this design look good? Any layout, styling, or UX changes before I wire up the logic?**
```

---

## Step Complete (Phase 3)

```markdown
## ✅ Step [N]/[Total]: [Step Name]

### What I Did

- [Specific change 1]
- [Specific change 2]
- [Specific change 3]

### Files Changed

- Created: [paths]
- Modified: [paths]

### How to Verify

[Testing/review instructions]

### Next Step

[Brief description of what comes next]

---

**Please review these changes. Should I proceed to Step [N+1], or would you like any adjustments?**
```

---

## Iteration Log Entry (after each checkpoint)

```markdown
- **Iteration N (YYYY-MM-DD HH:MM)**
  - Summary: [What was implemented]
  - Feedback: [User's response — approval or change requests]
  - Changes: [Modifications made based on feedback]
  - Status After: [Current status]
```

---

## Final Review (Phase 4)

```markdown
## 🎉 All Implementation Steps Complete

### Summary of Work

- [Major accomplishment 1]
- [Major accomplishment 2]

### Acceptance Criteria Status

- [x] Criterion 1
- [x] Criterion 2

### Testing Results

[Test results summary]

### Files Modified

[Complete list]

---

**This ticket is ready for final review. Please verify all acceptance criteria are met and code quality standards are satisfied. If everything looks good, I'll mark this ticket Completed.**
```

---

## Handling Feedback Types

| User says                     | Your action                                                        |
| ----------------------------- | ------------------------------------------------------------------ |
| "Looks good, continue"        | Update iteration log → proceed to next step                        |
| "Can you change X to Y?"      | Acknowledge → clarify if needed → implement → request feedback     |
| "Why did you do it this way?" | Explain rationale → adjust if needed → request feedback            |
| "This won't work because..."  | Mark Blocked → document issue → propose solutions → wait           |
| "Can we also add Z?"          | Assess scope → update ticket if needed → get approval for approach |
