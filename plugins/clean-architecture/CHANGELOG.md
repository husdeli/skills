# Changelog

All notable changes to the **clean-architecture** plugin are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.16.0] - 2026-07-24

### Added
- **`ts-clean` skill — clean TypeScript for every `.ts`/`.tsx` file.** The generic rules
  were living inside `react-clean`, so they only fired when someone was editing a
  component: a service could hide an `await import()` in a helper and a domain module could
  narrate itself line by line without ever tripping a rule. `ts-clean` now owns them —
  one module per file named after its primary export (`index.ts` stays a barrel), static
  top-of-file imports with the code-splitting / SSR / optional-dependency exceptions spelled
  out, and self-documenting code over comments with explicit keep and delete lists.

### Changed
- **`react-clean` is now the React layer on top of `ts-clean`.** Its old Rule 6 (static
  imports) and Rule 8 (comments) moved to `ts-clean`; the prop-drilling rule renumbered
  7 → 6, and Rule 1 kept only the component-specific part of one-module-per-file. A new
  prerequisite section tells the reader to load `ts-clean` as well, and the finishing
  checklist defers to its checklist instead of duplicating it.
- **The coding agent loads `ts-clean` for any TypeScript file**, not just React ones —
  `react-clean` is now described as stacking on top of it rather than repeating it.
- **The plan reviewer checks plans against the plugin's skills.** It gained the `Skill`
  tool and a new checklist item ("Plugin skill compliance"): it loads
  `clean-fullstack-architecture`, `ts-clean`, and `react-clean` for the code a plan touches,
  and treats a step that would force a violation as a **major** issue. Previously the coding
  agent was held to these rules but nothing checked the plan for steps that made them
  impossible to follow.

## [0.15.0] - 2026-07-23

### Added
- **`react-clean` Rule 8 — let the code explain itself.** The skill said nothing about
  comments, so generated components came back narrated line by line (`// handle the click`,
  `// --- state ---`, commented-out leftovers). The new rule defaults to zero comments and
  makes the fix a rename, a named constant, an extracted hook, a type, or a test — with an
  explicit keep-list for the things code genuinely cannot say: a *why*, a link to a spec or
  ticket, a justified deviation from another rule, a non-local warning, public API docs, and
  `TODO`s with a concrete referent. Added to the completion checklist.

## [0.14.0] - 2026-07-23

Latency pass on `/orchestrate`: the pipeline was serial end to end, and three stages were
redoing work an earlier stage had already done. Same gates, same caps, less wall-clock.

### Changed
- **The planner now scouts in parallel with the interview.** `/orchestrate` spawns
  `implementation-planner` in **scout-only** mode in the *same tool block* as
  `feature-interviewer`: it surveys the codebase and emits the context pack while the
  interview runs and the user answers `AskUserQuestion`, then parks. When the Decisions are
  settled they go to the *same* agent via `SendMessage` and it plans from files it has
  already read. Removes a full cold codebase exploration from the critical path.
- **The reviewer now pre-reads in parallel with the planning.** `plan-reviewer` is spawned
  in **pre-read only** mode as soon as the context pack exists, gated on the scout's
  provisional risk profile, so its mandatory file reading overlaps with the plan being
  written. The real review gate is still applied mechanically to the final risk profile; a
  pre-warmed reviewer that the gate then skips is simply dropped.
- **The coding agent no longer runs the full suite.** It does a *targeted* self-check on
  what it touched; `verify` remains the sole authoritative gate and runs the gating
  commands concurrently. Previously both ran everything — the coding agent sequentially —
  which duplicated the slowest block on the path, twice when a fix cycle happened.
- **Re-verification fails fast.** After a fix, `/orchestrate` hands the previously failing
  commands to the fresh `verify` agent, which runs those first and reports immediately if
  any still fails instead of running the rest of the suite for a result that cannot pass.
- **Normal-risk plan review runs on Sonnet**; the two high-risk lenses stay on Opus.
- **Thinner spawn prompts.** The verify agent's judging and output-hygiene rules and its
  JSON contract, and the coding agent's skill obligations, moved out of the `/orchestrate`
  spawn prompts into the agent definitions, where they are not re-paid on every spawn.

### Added
- **`e2eCommand` in the context pack.** The planner reports the project's e2e command (or
  `"none"`), and `/orchestrate` passes it to every `verify` spawn. When supplied, `verify`
  skips its e2e discovery sweep entirely instead of globbing for `playwright.config.*`,
  `cypress/`, and `e2e/` on every run.
- **Two-turn modes** documented in the `implementation-planner` (scout → plan) and
  `plan-reviewer` (pre-read → review) agent definitions, so both behave correctly whether
  they are spawned early or in the classic one-turn way.

## [0.13.0] - 2026-07-23

### Added
- **`verify` agent runs end-to-end tests when the project has them.** It now discovers an
  e2e suite on its own (scripts matching `e2e`/`cypress`/`playwright`, `playwright.config.*`
  / `cypress.config.*` / `wdio.conf.*` / `.detoxrc*`, `e2e/` and `cypress/e2e/` directories,
  `Makefile`/`tox` e2e targets) and runs it even when the handed-over verification commands
  omit it. A project with no e2e suite is reported as such, not as a failure.
- **E2E-aware run strategy.** Fast checks (unit tests, lint, typecheck, build) still go out
  as one concurrent batch; e2e runs afterwards on its own with the maximum timeout, since
  those suites bind ports, share a database, and drive a browser. The agent lets the
  project's own tooling start the app (Playwright `webServer`, `start-server-and-test`) and
  prefers headless/CI invocations over watch modes.
- **`skipped` verification results.** An e2e suite that cannot run for environment reasons —
  browsers not installed, no display, a missing service or credentials — is reported as
  skipped with the reason rather than as a pass or a code failure. `/orchestrate` carries a
  `skipped` field in the verify JSON contract and requires skipped commands to be named in
  the completion report.

### Changed
- `verify` may re-run a **single** e2e spec once to separate a flake from a real break, and
  must report the retry; whole-suite re-runs remain forbidden. Failure extraction now calls
  for the failing spec plus the assertion or selector, and explicitly bans pasting e2e
  traces.

## [0.12.0] - 2026-07-23

### Added
- **`react-clean` Rule 6 — static imports at the top of the file.** Bans `await import()` /
  in-function `require()` as a default, with a narrow exception list (route- and
  component-level code splitting via `lazy`, a heavy dependency on a rare path, browser-only
  modules under SSR, genuinely optional dependencies). Exceptions must sit at module scope
  and carry a one-line comment explaining why they are dynamic.
- **`react-clean` Rule 7 — no prop drilling.** A prop a component only relays to a child is
  a refactor signal: prefer composition (`children`/slot props), then moving state down or
  the consumer up, then context for truly global values, then a store for server/app-wide
  state. One level of pass-through is fine; two or more with untouched intermediates is not.
  Notes the overlap with the Rule 5 props ceiling — a component with many relayed props
  should be taking `children`.

### Changed
- Extended the `react-clean` skill description and finishing checklist to cover both new
  rules.

## [0.11.0] - 2026-07-13

### Changed
- **`feature-interviewer` agent is now selective about what it escalates.** It surfaces an
  open decision to the user *only* when the choice genuinely needs them: a significant
  architecture decision, a library or framework choice the codebase doesn't already dictate,
  a point of genuinely unclear intent, or a contradiction with `prd.md`/`design.md`. Every
  other choice it resolves itself and records as an assumption. Adds an explicit "what clears
  the bar" filter, a `Type:` tag and "why it needs you" line per decision, and makes
  returning zero open decisions a valid outcome — biasing toward a short, high-stakes brief
  over a long list of choices the user doesn't care about.

## [0.10.0] - 2026-07-13

### Added
- **`prd` skill.** Guides creating or updating a product requirements document — the
  requirements from the user's point of view, kept durable as tickets and implementation
  change underneath. Enforces product-only content (no ticket, code, technology, or
  migration references), cohesive per-product-area descriptions with stable anchor codes
  instead of atomic per-feature checklists, and positive framing of behavior. Prescribes a
  fixed eight-section structure and rules for revising a living PRD in place.
- **`/prd` command.** Loads the `prd` skill and drives it to create or update a product
  requirements document for a given product or feature. Takes the target as an argument and
  prompts for one if omitted.

## [0.9.0] - 2026-07-10

### Fixed
- **The `coding` agent can now actually invoke skills.** Added the `Skill` tool to the
  agent's `tools` list — previously it was told to "invoke the `react-clean` skill" but
  had no `Skill` tool, so the instruction was impossible to follow.

### Changed
- **`coding` agent loads skills up front.** It now invokes the `clean-fullstack-architecture`
  skill before writing any production code and the `react-clean` skill before touching any
  React file, handles namespaced skill names, and invokes each skill once per session rather
  than per file. The `/orchestrate` implement-stage prompt was updated to match.

## [0.8.1] - 2026-07-10

### Changed
- **`/design` command no longer hardcodes `design.md`.** Clarifies that the skill decides
  the filename and whether the design lives in one doc or splits across several
  cross-referenced docs (`design.md` is only the conventional default), and to update an
  existing design doc in place rather than create a duplicate.

## [0.8.0] - 2026-07-10

### Added
- **`/design` command.** Loads the `design-doc` skill and drives it to create or update a
  design doc for a given screen, surface, or flow. Takes the target as an argument and
  prompts for one if omitted.

## [0.7.0] - 2026-07-10

### Added
- **`design-doc` skill.** Guides creating a design doc (`design.md`) that specifies how a
  product looks and behaves — the intended end state, not how to build it. Enforces four
  core rules (target-state not procedure, structural altitude not pixel-level, no changelog,
  split by concern with cross-references), a standard document shape, a per-surface
  layout → content → states → responsive pattern, and style rules favoring ASCII layout
  diagrams and state tables.

## [0.6.0] - 2026-07-10

### Added
- **`react-clean` skill — Rule 5 "Keep components and their props small."** Adds hard size
  ceilings that trigger a refactor: ≤ 150 lines per component file, ≤ 50 lines of returned
  JSX, ≤ 3 levels of JSX nesting, and one reason to render. Adds props limits: ≤ 5 props,
  with an ordered remediation (composition via `children`/slots → group related props into
  one object → split the component) and a ban on boolean-flag soup in favor of a single
  `variant` union. Cohesive inputs (a typed props object, `children`, event handlers) are
  explicitly exempt from the props budget.
- Two matching checklist items and an updated skill `description` covering the new limits.

## [0.5.0] - 2026-07-09

### Changed
- **`/orchestrate` core is now persistent-agent, main-loop driven.** The plan → review →
  revise → implement → verify pipeline no longer runs as a background `Workflow` script;
  it runs in the main loop with the planner, plan-reviewer, and coding agents each spawned
  **once** via `Agent` and resumed across revision/fix cycles via `SendMessage`. Their
  context (the plan, the files they read, prior reasoning) now survives each cycle instead
  of being re-sent, cutting the token/latency cost of the revision and fix loops. `verify`
  is still spawned fresh each run (cheap Sonnet; a clean re-run is desired).
- Because there is no schema enforcement in the main loop, each core agent now ends its
  reply with a single fenced `json` block (context pack + risk profile, review verdict,
  implementation summary, verify results) that the orchestrator parses to drive control
  flow. The deterministic gates are preserved as explicit, mechanical rules: the review-skip
  gate (≤2 files, no dep, no API, criteria auto-checkable), the high-risk parallel-lens test
  (new API/dep or >5 files), the single revision cap, and the single fix cap are unchanged.

### Removed
- Deleted `workflows/orchestrate-core.js` and the `workflows/` directory. The deterministic
  workflow is fully replaced by the persistent-agent main-loop pipeline above.

## [0.4.2] - 2026-07-08

### Changed
- Agent invocations now use plugin-namespaced `subagent_type` names. `orchestrate-core`
  spawns `clean-architecture:{implementation-planner,plan-reviewer,coding,verify}`, and the
  `/orchestrate` command spawns `clean-architecture:feature-interviewer`. This prevents
  collisions with same-named agents from other plugins or the host project now that both
  bare and namespaced names are registered.

### Removed
- Dropped the stale `feature-interviewer` agent reference from the `ai-planning-workflow`
  skill's interview phase.

## [0.4.1] - 2026-07-08

### Fixed
- `orchestrate-core` now parses `args` when it arrives as a JSON string, not just as an
  object. Previously a string-typed payload made `args.task` undefined, so the planner
  received an untitled task with no criteria and no interview context.
- `orchestrate-core` Verify stage is now baseline-aware and output-hygienic. It judges
  pass/fail by whether the change *introduced* failures rather than by absolute exit codes
  (a command non-zero only due to a known pre-existing baseline, e.g. `tsc -b`, counts as a
  pass at/below baseline), gates only on the project's named gating commands, and caps each
  result's output to a few lines with a single StructuredOutput call — preventing the
  oversized-output fail loop that could exhaust the retry cap and crash the workflow.

## [0.4.0] - 2026-07-08

### Added
- `verify` agent: a lightweight, run-only verification agent (Bash-focused, no code edits)
  on a cheaper model. The `orchestrate-core` Verify stage now uses it instead of the full
  `coding` agent.

### Changed
- **Model & effort tiering** in `orchestrate-core`: planning runs on Opus at high effort;
  review, revision, implementation, and the fix loop stay on Opus; verification runs on
  Sonnet at low effort. This cuts cost on the loop-prone verify stage without touching
  reasoning-heavy stages.
- **Risk-scaled review**: when the review gate requires a review, high-risk plans (new
  public API, new dependency, or >5 files touched) now get two parallel reviewers with
  distinct lenses (correctness vs. codebase-fit), merged into one verdict; normal-risk plans
  keep the single holistic reviewer. Same wall-clock, broader coverage where risk is highest.

## [0.3.0] - 2026-07-08

### Added
- Deterministic `orchestrate-core` workflow (`workflows/orchestrate-core.js`): a
  code-controlled plan → gated review → single revision → implement → verify (with a
  fix-and-recheck loop) pipeline that returns a structured `completed`/`escalate`/`aborted`
  result.

### Changed
- `/orchestrate` is now a **hybrid**: the interactive shell (task selection, approval, and
  the interview decisions) runs in the main loop, then hands the mechanical core off to the
  `orchestrate-core` workflow. The review skip gate and the verify/fix loop are now
  deterministic code rather than model judgment.

## [0.2.0] - 2026-07-08

### Added
- `feature-interviewer` agent and an interview/challenge stage before planning, so
  non-trivial features settle their open decisions with the user before a plan is written.
- `/orchestrate` command: picks the next actionable roadmap task and drives it through
  interview → plan → review → implement.
- `react-clean` skill: rules for clean React components (one component per file, at most one
  `useEffect`, no data-layer access from components).

## [0.1.0] - 2026-07-07

### Added
- Initial packaging as a Claude Code plugin.
- `clean-fullstack-architecture` skill with hexagonal dependency rules.
- `ai-planning-workflow` skill.
- `implementation-planner`, `plan-reviewer`, and `coding` agents.

[0.5.0]: https://github.com/husdeli/skills/releases/tag/v0.5.0
[0.4.1]: https://github.com/husdeli/skills/releases/tag/v0.4.1
[0.4.0]: https://github.com/husdeli/skills/releases/tag/v0.4.0
[0.3.0]: https://github.com/husdeli/skills/releases/tag/v0.3.0
[0.2.0]: https://github.com/husdeli/skills/releases/tag/v0.2.0
[0.1.0]: https://github.com/husdeli/skills/releases/tag/v0.1.0
