# Changelog

All notable changes to the **clean-architecture** plugin are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.4.1]: https://github.com/husdeli/skills/releases/tag/v0.4.1
[0.4.0]: https://github.com/husdeli/skills/releases/tag/v0.4.0
[0.3.0]: https://github.com/husdeli/skills/releases/tag/v0.3.0
[0.2.0]: https://github.com/husdeli/skills/releases/tag/v0.2.0
[0.1.0]: https://github.com/husdeli/skills/releases/tag/v0.1.0
