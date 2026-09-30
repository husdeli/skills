---
description: Review code that was already written — the working tree, a branch, a ticket, or named files — with the code-reviewer agent. Add "fix" to hand the blocking issues to the coding agent.
argument-hint: "[what to review — nothing, a path, a branch, a ticket ID] [fix]"
---

# Review

Hand the target below to the **`code-reviewer` agent** and report its verdict. The agent reads the code and reaches the verdict; you resolve the target, spawn it, and relay what it found.

Target: $ARGUMENTS

This is the code gate on its own. Both orchestrators already run it at their verify stage, so use `/review` for code that never went through one: a change `/code` made, work you wrote by hand, a branch someone else pushed, a ticket you want checked before you open a pull request.

The reviewer reads the code itself and loads the plugin's skills itself — `clean-fullstack-architecture`, `ts-clean`, `react-clean`, `clean-tanstack-start`. Leave those rules out of the prompt: its own definition already holds them.

**Load two skills before you spawn anything**, namespaced here as `sdlc:<name>`: **`agent-pipeline`** for how to spawn, resume, and read the agent's JSON block, and **`clean-writing`** for the report. Add **`product-docs`** and **`ticket-board`** when the target is a ticket, and **`product-docs`** whenever this session is not standing in the repository that holds the code.

**Name the work root in the prompt.** A working tree, a branch, and a file path all belong to one repository. In a session started inside it, that is the working directory. In a session started in an Obsidian vault, resolve the work root as `product-docs` says — from the ticket under review, or from the registry when the user names the repository — and pass it to the reviewer as an absolute path, so every `git diff` it runs is the right tree's.

## Workflow

### 1. Resolve the target

`$ARGUMENTS` may name what to review, may end with the word `fix`, and may be empty. Strip `fix` first and keep it as a flag — see Stage 4.

- **Nothing given** → review the uncommitted changes. Run `git -C <work root> status --porcelain` yourself: when the tree is dirty, the target is the working tree against `HEAD`, untracked files included. When it is clean, the target is this branch against the default branch, and say in one line which comparison you chose.
- **A path** (a file or a directory) → review those files as they stand.
- **A branch, a commit, or a range** → review that diff.
- **A ticket ID or ticket path** → find the ticket by its ID as `ticket-board` says, under the docs root `product-docs` resolves. Read it, and review the current change with the ticket's acceptance criteria as the standard.

Derive acceptance criteria from the ticket when there is one. Otherwise take them from the change itself — the commit messages and the code — and state in one line what you took them to be.

Say what you are about to review in one line, then review it. Go straight to it — reading code changes nothing, so approval belongs to the fix in Stage 4.

### 2. Spawn the code reviewer

Spawn it **once** and keep the id:

```
Agent(subagent_type: "sdlc:code-reviewer", model: "opus",
      prompt: the resolved target (the exact git range or file list) + acceptance criteria
              + the ticket text when there is one
              + "No plan and no verification results come with this review — the code and the
                 criteria above are the whole brief. Read the code yourself.")
```

It ends its turn with one fenced `json` block carrying `verdict`, `summary`, and `issues`. Parse it as `agent-pipeline` says.

- `aborted` — nothing returned, or no valid JSON block after the one retry → report that the agent returned no usable result, and stop.
- `APPROVED` with an empty `issues` list → report the approval and stop.
- `APPROVED` with minor issues, or `CHANGES_REQUESTED` → report them, then Stage 4.

### 3. Report

Load the **`clean-writing`** skill (namespaced here as `sdlc:clean-writing`) before you write the report, and follow it for every sentence. It governs prose only — paths, identifiers, quoted code, and the verdict keywords stay exact.

The user did not see the agent's turn, so give them the verdict and the defects in your own words:

```markdown
**[APPROVED | CHANGES_REQUESTED]** — [one sentence: what the change does, and what stands in its way.]

### Blocking (critical / major)
- `path:line` — [problem]. [What to do instead.]

### Non-blocking (minor)
- `path:line` — [problem]. [What to do instead.]

### Reviewed
- [the git range or the file list] — [N] files
```

Drop a section that is empty. A `CHANGES_REQUESTED` verdict leads the first line as a verdict: this code needs work before it ships.

This command runs **no verification**. Nobody ran the tests, the lint, or the typecheck here. Say so in the last line whenever you report on code that skipped a verify stage, and name `/orchestrate-quick` as the way to get the full gate.

### 4. Fix, only when asked

When `$ARGUMENTS` ended with `fix`, or the user asks after the report, hand the blocking issues to the coding agent:

```
Agent(subagent_type: "sdlc:coding", model: "opus",
      prompt: the blocking issues, each with its file, line, problem, and suggestion
              + "Fix ONLY these issues, and leave every other behavior exactly as it is.")
```

Then re-review by resuming the **same** reviewer: `SendMessage(reviewerId, "Re-review the fix below; judge each prior issue as fixed or still open." + the coding agent's summary)`. One fix cycle is the cap. When the second verdict is still `CHANGES_REQUESTED`, report what is left and stop.

With neither the flag nor the ask, report and stop. A request to read code is a request to read it, and the user decides what happens next.

### 5. Record it on the ticket, when you reviewed one

**When the target was a ticket that has a worklog beside it** — the **`ticket-board`** skill holds
the file's shape — append one entry: the verdict, the blocking issues, and what the fix changed
when Stage 4 ran.

```markdown
## 2026-09-27 15:40 — code-reviewer · review

- CHANGES_REQUESTED: two server functions read the session without authenticating it.
- Both fixed, re-review returned APPROVED. Nobody ran the suite.
```

Sign it with the agent whose verdict it carries, `code-reviewer`. **Create no worklog, write no
status, and touch no assignee** — this command does not own the board. With no ticket, or no
worklog beside it, there is nothing to write.

## Rules

- **The agent reviews the code.** You resolve the target, spawn it, and report.
- **Keep the prompt thin.** The checklist, the skills, and the severity rules live in the agent definition.
- **Spawn once, resume with `SendMessage`** — `agent-pipeline` holds the mechanics. One fix cycle, then stop.
- **Report the verdict first.** A blocking issue leads the first line.
- **Fix on an explicit ask alone** — the `fix` argument, or the user saying so.
- **Name every gating command that nobody ran.** Unverified code reaches the user as unverified code.
- **Log onto a ticket only when it already has a worklog.** Never create one, and never write a status or an assignee here.
