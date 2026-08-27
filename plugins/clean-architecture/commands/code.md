---
description: Implement what the user asks with the coding agent, which loads every coding skill. No planner, no reviewer.
argument-hint: [what to build, change, or fix]
---

# Code

Hand the request below to the **`coding` agent** and report what it did. You do not write the code yourself.

Request: $ARGUMENTS

This is the direct path. `/orchestrate` runs interview → plan → review → implement → verify with five agents. `/orchestrate-quick` runs plan → review → implement → verify with four. `/code` runs one: the coding agent, with no plan in front of it. Use it when the change is one the user already understands — a fix, a small feature, an addition that follows a pattern the codebase already has.

The coding agent takes a request with no plan as one of its two input shapes, so this command needs no planner. It is also the right worker because it already loads the plugin's coding skills itself — `clean-fullstack-architecture` for any production code, `ts-clean` for any `.ts`/`.tsx` file, `react-clean` for a component or a hook, `clean-tanstack-start` for TanStack Start server code. Do not restate those rules in the prompt. Its own definition holds them, and a spawn prompt is re-paid on every spawn.

## Workflow

### 1. Resolve the request

- **Nothing given** → ask what to build. Do not guess.
- **A task description** → use it as-is. The user just gave it to you, so do not ask for approval.
- **A file path** (a ticket, a note, an issue export) → read it and use it as the request.

Derive acceptance criteria from the request. When it names none and none are inferable, state the criteria you are assuming in one line and continue.

**Stop and point at another command when the request outgrows this one.** Open product, UX, or architecture forks belong in `/orchestrate`. A change that spans many files in an order that matters belongs in `/orchestrate-quick`. Name the command and the reason in one line, then stop. Do not improvise a plan here, and do not spawn a planner.

### 2. Spawn the coding agent

Spawn it **once** and keep the id:

```
Agent(subagent_type: "clean-architecture:coding", model: "opus",
      prompt: the request + acceptance criteria + any file you read in Stage 1
              + "No plan and no context pack come with this task — the request above is the
                 brief. Raise a blocker only for work you genuinely cannot complete.")
```

It ends every turn with one fenced `json` block carrying `summary`, `workItemsCompleted`, `filesChanged`, and `blockers`. Parse it.

- Nothing returned, or no valid JSON block after one retry → report that the agent returned no usable result, and stop.
- Non-empty `blockers` → report them and stop. Do not fix the blocker yourself.

### 3. Follow up at most once

The agent holds the request, the files it read, and its own reasoning. Resume it with `SendMessage(codingId, ...)` — never re-spawn it, and never finish its work in the main loop.

Send one follow-up when its self-check failed, or when its summary shows it missed part of the request. Send only what changed: the failing output, or the missed part. One follow-up is the cap. When the second turn still does not clear it, report what is left and stop.

### 4. Report

Load the **`clean-writing`** skill (namespaced here as `clean-architecture:clean-writing`) before you write the report, and follow it for every sentence. It governs prose only — paths, identifiers, commands, and quoted output stay exact.

The user did not see the agent's turn, so give them the outcome, not a transcript:

```markdown
[One or two sentences: what the change does for the user, and whether it is finished.]

### Files changed
- Created: [paths]
- Modified: [paths]

### Checked
- [command the agent ran]: [pass / fail]
- Not run: [command] — [reason]

### Blockers and assumptions (if any)
- [what blocked the agent, or what it assumed]
```

There is **no verify stage behind this command.** The coding agent runs a targeted self-check only. Name every gating command that nobody ran, and never present an unrun suite as green. Offer `/orchestrate-quick` in the last line when the user wants the full gate.

## Rules

- **The agent writes the code.** You resolve the request, spawn it, and report.
- **Keep the prompt thin.** The skills, the conventions, and the comment rules live in the agent definition.
- **Spawn once, resume with `SendMessage`.** One follow-up, then stop.
- **One request at a time.** Finish what was asked and stop.
- **Report failure as failure.** A failing check or a blocker goes in the first line.
- **Hand off when the request outgrows the command** — name `/orchestrate-quick` or `/orchestrate` and why.
