# The command preamble

The rules `/orchestrate`, `/orchestrate-quick`, and `/run-roadmap` share before their own stages.
Each command points here and adds only what is its own.

## The rules live in four skills — load each one before the stage that needs it

| Skill | What it holds | Load before |
| --- | --- | --- |
| **`sdlc-structure`** | Where the project and the work root are, and how each destination writes a document | you read any document |
| **`ticket-board`** | The ticket, the roadmap, the claim, the assignee, the worklog, and what each status transition writes | you read the roadmap or touch a ticket |
| **`agent-pipeline`** | Spawn once and resume, concurrent calls, the JSON block, the test fingerprints and the dispute route, the outcome vocabulary — and, in [the build stages](build-stages.md), every stage from Plan to Code review and full verification | you spawn the first agent, with the build stages read whole before Plan |
| **`technical-writing`** | Every word a person reads — now, or later in the worklog, a commit message, or the report | you write the first sentence a person reads |

Each name may be namespaced here — `sdlc:sdlc-structure`, `sdlc:ticket-board`,
`sdlc:agent-pipeline`, `sdlc:technical-writing`. Invoke the namespaced form when it is there, load
each skill **once**, and follow it. Do not work from memory, and do not restate a skill's rules in a
spawn prompt: the agents load their own. The skills are the rules; the command file is the sequence.

## Everything a person reads goes through `technical-writing`

The command is the only stage that talks to the person, so `technical-writing` governs every word
they see. The rules that bite hardest: name the task and the stake before the detail, give the
verdict before the evidence, keep an option label to one short phrase, and reuse the ticket's, the
roadmap's, and the PRD's own words for every domain term. It governs prose only — IDs, file paths,
commands, status markers, and the agents' `json` blocks stay exact, **beside** the prose: a path, a
symbol, or a snippet never goes inside a sentence, and the sentence names the thing in words instead.

## The board

**The command is the board's only writer**, as `ticket-board` says: it writes the status, the
assignee, the worklog, and the roadmap, at the boundaries the build stages and the command's own
table name. No agent writes any of them.

**`<n>` is this run's number** — the one in its claim, chosen as `ticket-board` says. Every agent of
the run carries it in `assigned`, and the command's own worklog entries name the claim.

**Every exit writes the outcome entry and the assignee.** A `human_required` at any stage runs
`ticket-board`'s *Stopping without finishing* transition, so the next session can read the worklog
and learn where the ticket stopped. Every exit deletes the run folder.

## Failure handling

`agent-pipeline` holds the outcome vocabulary and the conditions for `human_required`, and
`ticket-board` holds the *Stopping without finishing* transition.

- **No stage has a retry limit, and no count ends a loop.** Every loop runs until its gate passes or
  `human_required` stops it.
- **Never finish a ticket unless every gate passed**: the tests the mode runs, every code reviewer's
  `APPROVED`, and every check.
- **Be explicit about failures**, and propose the next step.
