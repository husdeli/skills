# Codex Subagent Protocol

Use this protocol with `commands/orchestrate.md`, `commands/orchestrate-quick.md`, `commands/code.md`, `commands/review.md`, and `commands/plan.md`.
The command file defines workflow behavior. This protocol replaces only Claude-specific tools and runtime terms.

## Contents

1. Resolve runtime paths
2. Translate shared terms
3. Create a role agent
4. Run agents concurrently
5. Resume a persistent agent
6. Wait for results
7. Load plugin skills in an agent
8. Handle user decisions
9. Parse agent contracts
10. Apply role and task names
11. Handle missing collaboration tools

## 1. Resolve runtime paths

Resolve these values before creating an agent:

- `PLUGIN_ROOT`: the plugin directory that contains `.codex-plugin/`, `agents/`, `commands/`, and `skills/`.
- `WORKSPACE_ROOT`: the project directory in which the user invoked the workflow.

Always pass both absolute paths in the agent's first message.
Do not assume that the installed plugin remains in the source checkout or a fixed cache path.

## 2. Translate shared terms

Apply these replacements while executing the shared command:

| Shared command term | Codex behavior |
| --- | --- |
| `Agent(...)` | Call `collaboration.spawn_agent`. |
| `SendMessage(id, message)` | Call `collaboration.followup_task` with the saved target. |
| Agent id or name | Save the canonical task name returned by `spawn_agent`. |
| `AskUserQuestion` | Use the available user-input tool. Otherwise present all decisions in one message and wait. |
| Task or todo tool | Use `update_plan` when it is available. |
| `Skill` tool | Read and follow the matching `skills/<name>/SKILL.md` file completely. |
| `Read`, `Grep`, `Glob`, `Bash` | Use Codex file and shell tools. Prefer `rg` and `rg --files`. |
| `WebSearch`, `WebFetch` | Use Codex web tools and cite the sources that the role requires. |
| `opus`, `sonnet`, or another Claude model | Omit the model override and inherit the current Codex model. |
| `CLAUDE.md` | Read applicable `AGENTS.md` files first. Also read `CLAUDE.md` when present. |
| `/scaffold`, `/orchestrate`, `/orchestrate-quick`, `/code`, `/review`, `/plan` | Use `$scaffold`, `$orchestrate`, `$orchestrate-quick`, `$code`, `$review`, `$plan`. |
| `/design`, `/prd`, `/explain` | Use `$design-doc`, `$prd`, `$explain`. |
| `$ARGUMENTS` | Use the text that follows the Codex skill invocation. |

The nearest `AGENTS.md` applies to files below its directory.
Platform and user instructions take priority over repository files.

## 3. Create a role agent

Call `collaboration.spawn_agent` with:

- `task_name`: the stable name from the task-name table below.
- `fork_turns`: `"none"` to prevent unrelated conversation context from replacing the role input.
- `message`: the role bootstrap followed by the stage input from the shared command.

Use this bootstrap in every first message:

```text
You are the <ROLE> agent for the sdlc workflow.

Runtime paths:
- Plugin root: <PLUGIN_ROOT>
- Workspace root: <WORKSPACE_ROOT>

Before you act:
1. Read <PLUGIN_ROOT>/agents/<ROLE_FILE>.md completely.
2. Ignore only the YAML frontmatter fields named tools and model.
3. Follow the Markdown body as your role contract.
4. Resolve every plugin skill against <PLUGIN_ROOT>/skills.
5. Read each required SKILL.md completely before the action that triggers it.
6. Read applicable AGENTS.md files from the workspace root to the files you touch.
7. Also read applicable CLAUDE.md files when they exist.
8. Use Codex tools that provide the capabilities named in the role contract.
9. Work only in <WORKSPACE_ROOT> and preserve unrelated user changes.

Stage input:
<STAGE_INPUT>
```

Do not paste the role definition into the message.
The agent reads the definition from the installed plugin.

## 4. Run agents concurrently

Codex collaboration calls cannot be nested inside a shell or orchestration tool call.
Replace "one tool block" with this sequence:

1. Call `collaboration.spawn_agent` for the first independent role.
2. Call `collaboration.spawn_agent` for the second independent role immediately.
3. Do not wait between the spawn calls.
4. Wait only after every independent role has started.

Use the same sequence for two independent `followup_task` calls.
Send both messages before waiting for either result.

Respect the active concurrency limit.
Do not start a role early when its required input does not exist.

## 5. Resume a persistent agent

Use `collaboration.followup_task` for every later turn of these roles:

- implementation planner
- plan reviewer
- coding agent
- code reviewer

Use the canonical task name returned by the first `spawn_agent` call.
Send only the new input that the shared command specifies.
Do not repeat the role bootstrap, plan, context pack, or prior messages unless the command requires them.

Create a new verification agent for each verification run.
Use a new task name for each run.

## 6. Wait for results

Use `collaboration.wait_agent` after all currently independent work has started.
Prefer a long wait rather than frequent polling.
Agent results arrive as team messages in the parent thread.

Continue waiting while at least one required agent remains active.
Process a result immediately when it unlocks user input or the next independent stage.

Use `collaboration.list_agents` only when agent state is unclear.
Do not interrupt a healthy agent to collect partial output.

## 7. Load plugin skills in an agent

When a role definition says to load a skill, make the agent read the installed skill directly:

```text
<PLUGIN_ROOT>/skills/<skill-name>/SKILL.md
```

The agent must read the complete file before taking the action that triggers it.
The agent must follow any directly required references from that file.

The rule files live in `skills/`, not in `codex-skills/`.
`codex-skills/` holds the entry points a user invokes with `$`, and each one reads the shared file.

Use these local names for the current plugin:

- `clean-writing`
- `clean-fullstack-architecture`
- `ts-clean`
- `react-clean`
- `clean-tanstack-start`

Do not depend on a Claude namespace or a `Skill` tool being present.

## 8. Handle user decisions

The main agent remains the only role that talks to the user.
Never ask a subagent to contact the user.

When the shared workflow requires approval or decisions:

1. Use the available structured user-input tool when the current mode supports it.
2. Otherwise present all current decisions in one concise user-facing message.
3. End the turn and wait for the user's answer.
4. Resume the existing persistent agents after the answer arrives.

Invoking `$orchestrate` with a roadmap is not approval for the selected task.
Do not change task status or create subagents until a later user message approves that task.
Invoking `$plan` with a request is not approval for the task breakdown it proposes.
Do not write a document, a roadmap row, or a ticket until a later user message approves that breakdown.
Do not mark a task complete or choose a product decision on the user's behalf.

## 9. Parse agent contracts

Keep every JSON contract from the shared agent definitions unchanged.
Parse the final fenced `json` block from each role result.

If a required block is missing or invalid:

1. Call `followup_task` on the same agent.
2. Ask it to return only the corrected JSON block for its previous result.
3. Abort the stage if the second response is still missing or invalid.

Do not request a JSON block after a scout or pre-read turn when its role contract says none is due.

## 10. Apply role and task names

| Workflow role | Role file | First task name |
| --- | --- | --- |
| Feature interviewer | `feature-interviewer.md` | `feature_interviewer` |
| Implementation planner | `implementation-planner.md` | `implementation_planner` |
| Normal reviewer | `plan-reviewer.md` | `plan_reviewer` |
| Correctness reviewer | `plan-reviewer.md` | `plan_reviewer_correctness` |
| Codebase-fit reviewer | `plan-reviewer.md` | `plan_reviewer_codebase_fit` |
| Coding agent | `coding.md` | `coding` |
| Code reviewer | `code-reviewer.md` | `code_reviewer` |
| First verification run | `verify.md` | `verify_1` |
| Second verification run | `verify.md` | `verify_2` |

Add a short lens instruction to each high-risk reviewer's stage input.
Do not change the shared plan-reviewer contract.

## 11. Handle missing collaboration tools

The full workflow, the quick workflow, `$code`, `$review`, and `$plan` require Codex collaboration tools.
If `spawn_agent`, `followup_task`, or `wait_agent` is unavailable, stop before changing task status.

Tell the user that this Codex session does not provide subagents.
Suggest starting the workflow in a Codex session with collaboration enabled.
Do not silently replace the reviewed workflow with one main-agent pass.
For `$code`, the coding subagent is the whole workflow, so the same rule applies.
For `$review`, the code-reviewer subagent is the whole workflow, so the same rule applies.
For `$plan`, the interview is the research the documents rest on, so stop rather than plan from memory.
