---
description: Review code that was already written — the working tree, a branch, a ticket, or named files — with the code-reviewer agent. Add "fix" to hand the blocking issues to the coding agent.
argument-hint: [what to review — nothing, a path, a branch, a ticket ID] [fix]
---

# Review

Hand the target below to the **`code-reviewer` agent** and report its verdict. You do not review the code yourself, and you do not fix what it finds.

Target: $ARGUMENTS

This is the code gate on its own. Both orchestrators already run it at their verify stage, so use `/review` for code that never went through one: a change `/code` made, work you wrote by hand, a branch someone else pushed, a ticket you want checked before you open a pull request.

The reviewer reads the code itself and loads the plugin's skills itself — `clean-fullstack-architecture`, `ts-clean`, `react-clean`, `clean-tanstack-start`. Do not restate those rules in the prompt. Its own definition holds them, and a spawn prompt is re-paid on every spawn.

## Workflow

### 1. Resolve the target

`$ARGUMENTS` may name what to review, may end with the word `fix`, and may be empty. Strip `fix` first and keep it as a flag — see Stage 4.

- **Nothing given** → review the uncommitted changes. Run `git status --porcelain` yourself: when the tree is dirty, the target is the working tree against `HEAD`, untracked files included. When it is clean, the target is this branch against the default branch, and say in one line which comparison you chose.
- **A path** (a file or a directory) → review those files as they stand.
- **A branch, a commit, or a range** → review that diff.
- **A ticket ID or ticket path** → find the ticket by ID (glob `.clean-architecture/tickets/*/<ID>-*.md`, then `.clean-architecture/tickets/<ID>-*.md`), read it, and review the current change with the ticket's acceptance criteria as the standard.

Derive acceptance criteria from the ticket when there is one. Otherwise take them from the change itself — the commit messages and the code — and state in one line what you took them to be.

Say what you are about to review in one line, then review it. Do not ask for approval: reading code changes nothing.

### 2. Spawn the code reviewer

Spawn it **once** and keep the id:

```
Agent(subagent_type: "clean-architecture:code-reviewer", model: "opus",
      prompt: the resolved target (the exact git range or file list) + acceptance criteria
              + the ticket text when there is one
              + "No plan and no verification results come with this review — the code and the
                 criteria above are the whole brief. Read the code yourself.")
```

It ends its turn with one fenced `json` block carrying `verdict`, `summary`, and `issues`. Parse it.

- Nothing returned, or no valid JSON block after one retry → report that the agent returned no usable result, and stop.
- `APPROVED` with an empty `issues` list → report the approval and stop.
- `APPROVED` with minor issues, or `CHANGES_REQUESTED` → report them, then Stage 4.

### 3. Report

Load the **`clean-writing`** skill (namespaced here as `clean-architecture:clean-writing`) before you write the report, and follow it for every sentence. It governs prose only — paths, identifiers, quoted code, and the verdict keywords stay exact.

The user did not see the agent's turn, so give them the verdict and the defects, not a transcript:

```markdown
**[APPROVED | CHANGES_REQUESTED]** — [one sentence: what the change does, and what stands in its way.]

### Blocking (critical / major)
- `path:line` — [problem]. [What to do instead.]

### Non-blocking (minor)
- `path:line` — [problem]. [What to do instead.]

### Reviewed
- [the git range or the file list] — [N] files
```

Drop a section that is empty. Never present a `CHANGES_REQUESTED` verdict as a list of suggestions — the first line says the code is not ready.

This command runs **no verification**. Nobody ran the tests, the lint, or the typecheck here. Say so in the last line whenever you report on code that has not been through a verify stage, and name `/orchestrate-quick` as the way to get the full gate.

### 4. Fix, only when asked

When `$ARGUMENTS` ended with `fix`, or the user asks after the report, hand the blocking issues to the coding agent:

```
Agent(subagent_type: "clean-architecture:coding", model: "opus",
      prompt: the blocking issues, each with its file, line, problem, and suggestion
              + "Fix ONLY these issues. Do not refactor anything else, and do not change
                 behavior the review did not name.")
```

Then re-review by resuming the **same** reviewer: `SendMessage(reviewerId, "Re-review the fix below; judge each prior issue as fixed or still open." + the coding agent's summary)`. One fix cycle is the cap. When the second verdict is still `CHANGES_REQUESTED`, report what is left and stop.

Without the flag and without the ask, report and stop. Fixing code the user only asked you to read is not yours to decide.

## Rules

- **The agent reviews the code.** You resolve the target, spawn it, and report.
- **Keep the prompt thin.** The checklist, the skills, and the severity rules live in the agent definition.
- **Spawn once, resume with `SendMessage`.** One fix cycle, then stop.
- **Report the verdict first.** A blocking issue goes in the first line, not at the end of a list.
- **Never fix without an explicit ask** — the `fix` argument, or the user saying so.
- **Never call unverified code verified.** Name every gating command that nobody ran.
