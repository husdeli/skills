---
feature: "[[<feature-name>.feature]]"
status: backlog
priority: Critical | High | Medium | Low
repositories: []
depends_on: []
createdAt: YYYY-MM-DDTHH:mm
updatedAt: YYYY-MM-DDTHH:mm
related:
  - "[[<subject>.design]]"
---

# [<CODE>-<NNN>] Ticket Title

## Description

[What needs to be done and why — 2-3 sentences max]

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Decisions

Settled while the ticket was planned. Each is a fixed constraint the run builds within, and never
reopens. Delete the section when planning settled nothing.

- [The choice] — [why it won over the alternative]

## Implementation Steps

Describe WHAT needs to happen (outcomes, behaviour), not HOW. Implementation details are deferred to the plan.

1. **Step 1**: [Outcome-focused description]
2. **Step 2**: [Outcome-focused description]

## Technical Notes

### Data Requirements

- [What data needs storing/retrieval and any constraints]

### Architectural Considerations

- [Data flow, caching, integrations, performance/security considerations]

## Testing

Unit → Integration/API → Frontend E2E (critical paths only).

- **Unit**: [pure functions, services, schema validation]
- **API**: [endpoint correctness, auth rules, error responses]
- **E2E**: [critical paths only — omit if covered by API tests]
- **Manual**:
  - [ ] Scenario 1
