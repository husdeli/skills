---
name: test-strategy
description: Rules for deciding which tests a change gets and for writing them — a test earns its place by the bug it catches, the fewest and cheapest tests, the type ladder from unit to integration to end-to-end, what a case never is, what makes a valid failing test, and how fixtures and helpers are reused. INVOKE THIS SKILL before you plan a test, write one, rule on a disputed test, or judge tests against a test plan. Enforces one case per bug, the cheapest type that catches it, end-to-end tests only on a critical path the end-to-end decision allows, no test theater, a new test that fails because the behavior is missing, and the project's own runner and fixtures.
---

# Test Strategy

These rules decide which tests a change gets and what makes each one worth running. `test-planner` applies them to choose the cases, `test-writer` applies them to write each case, and a code reviewer with the `tests` focus judges the tests against them.

## Rule 1 — A test earns its place by the bug it catches

Every case answers one question: **which bug does this catch?** A case with no answer is cut.

**Test theater** is a test that exists to raise coverage, to restate the implementation, or to check what the compiler or the framework already guarantees. It costs time on every run and catches nothing.

- **A failure mode earns a case** when it is plausible for this change and costs something real if it ships. Ask what a plausible implementation gets wrong: a boundary value, an empty or missing input, a duplicate, an ordering, a permission it skips, an error it swallows, a state it leaves half-written, two calls racing. Ask what a reviewer would bet breaks.
- **Drop the failure modes something else rules out** — the type system, a schema validator, or the framework.
- **A change no test could catch failing gets no case.** A copy edit, a style tweak, a config value, and a documentation change are examples. An empty test plan is a correct answer.

## Rule 2 — The fewest, cheapest tests

- **One case per bug.** Never test the same bug twice at two levels. One case may cover several criteria when a single input exposes all of them.
- **Fewer is better.** Three cases that catch three real bugs beat twelve that restate the code.
- **Pick the cheapest type that catches the bug**, in this order:
  1. **Unit** — pure logic, a mapping, a rule, a calculation. No I/O.
  2. **Integration** — a boundary this codebase owns: a repository against a real local database, an adapter against a recorded response, a route handler with its middleware.
  3. **End-to-end** — a user's critical path across the whole stack, and only when the end-to-end decision says yes. With no, there is none. With yes, the fewest that cross the path once.

## Rule 3 — A case drives what a caller observes

A case drives the public interface — the function, endpoint, component, or command a caller uses — and asserts on what the caller observes: a return value, a response, a rendered state, a stored row, an error.

- **The assertion names the exact expected value.** An assertion a wrong result would also satisfy is a hole: `toBeDefined`, `toBeTruthy`, a status range, a partial match on the one field that is always present.
- **Mock only what is slow, paid, or outside this repository.** The code under test, and code this repository owns that is cheap to run, run for real.

A case never is:

- a test of the framework, the language, or a library — that the router routes, that the ORM saves;
- a test of a getter, a type, a constant, or a re-export;
- a test of private internals or of how the code is built — call counts, which helper ran, the order of internal calls;
- a large snapshot that someone will re-record without reading;
- a case added because a file has no test.

## Rule 4 — A new test fails because the behavior is missing

Every case is `new` or a `guard`, and each one has a valid state before the code changes.

- **A `new` case fails** because the behavior is missing: an assertion failure on the expected value, or a missing module or export that the approved plan says the change will create. That failure is the state the coder starts from.
- **A `new` case that passes catches nothing yet.** Sharpen it so it asserts what only the new code delivers.
- **A case that fails for a reason of its own is broken**, and it catches nothing either. A syntax error, a wrong import of existing code, a fixture that throws, and a runner misconfiguration are examples. Repair it.
- **A `guard` case passes**, because it pins existing behavior the change could break. A guard earns its place only when the change touches code whose current behavior nothing tests and a caller depends on.
- **The module under test stays absent until the coder writes it.** A test imports it from the path the approved plan names. A stub, a placeholder export, or an empty module would turn a valid failure into a pass.

## Rule 5 — The runner, fixtures, and helpers come from the project

- **Read the existing tests beside the code first**, and match their runner, folder layout, naming, fixtures, and helpers.
- **Reuse a fixture or helper before writing one.** Add one only when a planned case needs it.
- **Use the project's existing test infrastructure.** One case never justifies new infrastructure. The one exception is an end-to-end suite: when the end-to-end decision is yes and the project has none, the implementation plan stands one up — the runner, its config, and the script, with no test in it. End-to-end cases attach to that suite, and none are planned when the plan stands none up.
- **A test file is code.** The same naming, import, and comment rules apply as for production code, and a test's name says what it checks, in the caller's words.
