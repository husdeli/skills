---
type: design
subject: ticket
updated: 2026-10-09
tags:
  - sdlc/design
related:
  - "[[SDLC-framework.design]]"
  - "[[work.design]]"
  - "[[feature.design]]"
---
# Ticket

This doc defines one [[glossary#Ticket|ticket]]: its name, the properties it carries, its status and what blocks it, and how its status changes. Where a ticket sits, and how it moves between folders, is defined in [[work.design|Work]].

## 1. Name

**A ticket is named `<CODE>-<NNN>-<slug>.md`**: `CHECKOUT-001-saved-card.md`. Its ID is `<CODE>-<NNN>`: `CHECKOUT-001`.

- **`<CODE>` is the `code` of the feature the ticket delivers**, from its [[feature.design#2. The feature note|feature note]]. A ticket whose code no feature carries is not a valid ticket.
- **`<NNN>` is three digits, and restarts at `001` in each [[glossary#Epic|epic]].** Two features planned on separate branches write into separate number spaces, so neither overwrites the other on merge.
- **`<slug>` is kebab-case**, a few words on what the ticket delivers.

## 2. Properties

```yaml
---
feature: "[[checkout.feature]]"
status: in progress
assigned: coding-1
claimed: orchestrate-1
createdAt: 2026-10-07T09:15
updatedAt: 2026-10-09T14:32
timing: 47
tokens: 1284000
cost: 4.12
---
```

- **`feature` links the [[feature.design#2. The feature note|feature note]] of the feature the ticket delivers**: required. That note's `code` is the `<CODE>` the ticket's name starts with; a ticket whose `feature` and name disagree is not a valid ticket.
- **`status` is where the work stands**: required; see 3. States.
- **`assigned` names the agent that works on the ticket now, or is planned to**, by that agent's name.
- **`claimed` names the orchestration agent that holds the ticket**, by that agent's name. It is a guardrail, not an assignment: a ticket can be claimed before anyone knows which agent will work on it.
- **`createdAt` is when the ticket was created**: required. It is set once, in the step that creates the ticket, and never changes.
- **`updatedAt` is when the ticket last changed**: required. It equals `createdAt` on a new ticket, and every step that changes the ticket rewrites it.

**Both times are local date and time, `YYYY-MM-DDTHH:mm`**, the form Obsidian reads as a date-and-time property.

**What implementing the ticket took is three optional properties:**

- **`timing` is how long agents spent implementing the ticket**, in whole minutes, summed over every agent.
- **`tokens` is how many tokens they spent**, input and output together.
- **`cost` is what those tokens cost**, in US dollars to two decimal places, at the price of the model that spent them.

A ticket no agent has worked on has none of the three.

**`assigned` follows the status:**

| Status        | `assigned`                                                   |
| ------------- | ------------------------------------------------------------ |
| `backlog`     | Optional; the agent planned to work on it, once that is known |
| `in progress` | Required; the agent working on it                            |
| `blocked`     | Optional; the agent that resumes it once it is unblocked     |
| `review`      | Optional; the agent that reviews it, once that is known      |
| `done`        | Absent                                                       |

**`claimed` does not follow the status.** It may be set at any status except `done`.

## 3. States

The ticket's `status` property:

| Status        | Meaning                                                           |
| ------------- | ----------------------------------------------------------------- |
| `backlog`     | The ticket is planned, and no work has started                    |
| `in progress` | The ticket is being built                                         |
| `blocked`     | The ticket cannot move forward                                    |
| `review`      | The work is built and waits for a review                          |
| `done`        | The ticket is finished                                            |

**What blocks a ticket is its `blocked_by` property**, kept apart from the status:

```yaml
status: blocked
blocked_by:
  - CHECKOUT-002
  - Payment provider has not issued sandbox keys
```

- **Each entry is a ticket ID or one line naming an outside cause.**
- **`blocked_by` is required while the status is `blocked`, and absent otherwise.** The step that moves a ticket out of `blocked` removes it.

The transitions:

| From          | To                                    |
| ------------- | ------------------------------------- |
| `backlog`     | `in progress`                         |
| `in progress` | `blocked`, `review`, or `backlog` when work on it stops |
| `blocked`     | `in progress`, or `backlog` when work on it stops |
| `review`      | `done`, or `in progress` when the review asks for changes |
| `done`        | Nothing; `done` is final              |

## 4. Behavior

- **A ticket is cited by its file name, never by a path.** Its path changes as its status changes; its name does not.
- **A number is never reused, and a ticket that exists is never renumbered.** A finished ticket keeps its number.
- **Finished work that needs more work gets a new ticket.** A `done` ticket never changes status; the new ticket names the change.
