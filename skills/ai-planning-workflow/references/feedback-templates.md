# Feedback Templates Reference

---

## Implementation Plan (Phase 2)

```markdown
## Plan: [TICKET-ID]

Following [pattern/convention found in codebase].

**Step 1**: [Description] — Files: [list] — Deliverable: [outcome]
**Step 2**: [Description] — Files: [list] — Deliverable: [outcome]

Feedback requested after each step. Good to go?
```

---

## Design Agreement (Phase 2.5 — UI work only)

```markdown
## 🎨 Design: [Feature Name]

Static prototype — no live data or business logic yet.

- [Component/screen]: [description]
- Preview: [run instructions + URL]
- Decisions: [key choices and rationale]

Changes before I wire up the logic?
```

---

## Step Complete (Phase 3)

```markdown
## ✅ Step [N]/[Total]: [Step Name]

- [Change 1]
- [Change 2]

Files: Created [paths] / Modified [paths]
Verify: [testing instructions]
Next: [what comes next]

Proceed to Step [N+1]?
```

---

## Iteration Log Entry (after each checkpoint)

```markdown
- **Iteration N (YYYY-MM-DD HH:MM)**: [What was done] → [Feedback] → [Changes] → [Status]
```

---

## Final Review (Phase 4)

```markdown
## 🎉 Done: [TICKET-ID]

- [x] Criterion 1
- [x] Criterion 2

Tests: [summary] | Files: [list]

Mark as Completed?
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
