---
type: glossary
updated: 2026-10-20
tags:
  - sdlc/glossary
---
# SDLC framework — glossary

## Answerer

Whoever settles a question a run cannot settle from the documents: the person in `/orchestrate` and `/orchestrate-quick`, and the `cto` agent in a roadmap run. An agent surfaces the question; only the answerer decides it.

## Bucket

One of the three folders inside `work/` — `backlog/`, `in-progress/`, and `done/`. Each bucket holds one or more ticket statuses; `in-progress/` holds `in progress`, `blocked`, and `review`.

## Business plan

`business/business-plan.md` in a project, with its competitor notes beside it: who pays, what they pay for, and how the product reaches them. It owns every price and every claim about the market, which the PRD never states.

## Claim

The `claimed` property on a ticket, naming the run that holds it, such as `orchestrate-2` or `run-roadmap-3`. A claimed ticket is never picked by another run; the claim guards the ticket, while `assigned` names the agent working on it. A roadmap run claims a feature's whole dependency cluster at once.

## Context pack

What the planner gathers before it plans: the work root, the relevant files, the conventions, and the exact check commands. The orchestrator hands it to every later agent, so none of them explores the code again.

## Dependency cluster

What a roadmap run claims when it selects a feature: every ticket of the feature that is not `done`, together with every ticket those depend on, directly or through another ticket, that is not `done` — in any feature. The run claims the cluster at once and builds it in dependency order, so no other run starts a ticket the feature is still building towards.

## Design doc

A document that says how one solution works: the parts it is built from, how work flows through it, and how it behaves. It describes the target state, never the steps to build it, and it sits in its feature's folder or, when every feature depends on it, in `designs/`.

## Destination

Where a framework root sits, named by the pointer file's `kind`: `vault`, a folder in an Obsidian vault; `folder`, any other folder outside the repository; or `repo`, `.sdlc/` inside the repository. It decides how a document writes its links — a wikilink in a vault, a relative path elsewhere.

## Diagram

One drawing, kept as `diagrams/<name>.excalidraw.md` and referenced from any document with a one-line caption. The document stays complete without it.

## End-to-end decision

Whether a ticket gets end-to-end tests, settled before any agent starts: `/orchestrate` asks the person at the pick, `/orchestrate-quick` defaults to no, and a roadmap run asks the `cto` agent. The test planner plans an end-to-end case only on a yes.

## Epic

The group of tickets that delivers one feature. The feature's code is the epic's code, it prefixes every ticket ID, and ticket numbering restarts at 001 in each epic.

## Feature

One thing a customer can do with the product, kept as a folder under `features/` with its feature note, the design docs it owns, and its notes. A feature keeps its folder after it ships, so `features/` lists everything the product does.

## Feature note

`<feature-name>.feature.md`, the note at the top of a feature's folder: its name, its code, its projects, its status, and one or two sentences on what a customer can do. It links the feature's design docs and never says how the feature works.

## Feature's tests

Every test the tickets of one feature have written, collected from their worklogs. `/orchestrate` and a roadmap run run them after every change to the code, so a ticket cannot break what an earlier ticket of the same feature built; `/orchestrate-quick` runs only the ticket's own tests.

## Framework root

The folder that holds the registry, the glossary, `features/`, `work/`, and every other document, and may hold `projects/`; when it does not, it holds one project's documents directly. A session finds it by walking up from where it starts, or from a repository through its pointer file.

## Full verification

Every check command a project has — lint, type check, the test suites, and the end-to-end suite when the end-to-end decision allows it — run by the orchestrator before a ticket finishes. A check passes when its command exits zero; a check the project lacks is skipped, never passed.

## Gate

A fixed rule that decides whether a run goes on, such as the plan-review skip gate or the rule that finishes a ticket. A gate is applied mechanically, from the numbers and verdicts the agents report and the results of the checks the orchestrator runs.

## Glossary

`glossary.md` at the framework root, defining every term the framework and its projects use, each once, under a heading of its own. Every other document links an entry instead of defining the term again.

## Implementation plan

What the planner returns for one ticket: the direction, the best practices it applies, and the ordered work items, each with what done looks like. It sets direction, never code, and the worklog keeps its direction and the approach it turned down.

## Note

One action a person must take outside the code for a feature to work — a cloud firewall rule, a secret, a DNS record, a third-party setting. The coding agent reports it, `scripts/create-note.py` writes it into `features/<feature-name>/notes/<slug>.note.md` tagged `human-required`, and a person closes it.

## Orchestrator

The session that drives one run: it picks the ticket, starts the agents, runs every test and check itself, and settles every gate. While the run holds a ticket, it is the only writer of that ticket, its worklog, and its roadmap row; an agent reports to it and writes no document.

## Outcome

How a run ends: `completed` when every gate passed, `escalate` when a stage hit its cap or a question needs a person, and `aborted` when an agent returned no usable result. Every outcome but `completed` leaves the ticket `blocked`.

## Pointer file

`.sdlc.json` at a repository's root, naming the folder that holds the documents of the project that repository is built for. It points from the code to the documents, the opposite direction to the registry.

## PRD

The product requirements document, `prd.md`: what the product does and why. It is assembled from the product notes and never lists features, tickets, or prices.

## Product area

One subsection of the PRD's behavior section, describing in a few paragraphs how one part of the product works for its users, with a short uppercase anchor code in its heading. An area holds several features and never lists them.

## Product note

A goal, non-goal, persona, problem, or success metric, kept as one file under `product/`. The PRD and the features cite product notes instead of restating them.

## Project

One product and every document about it. Its documents sit in `projects/<project-name>/`, or directly in the framework root when there is no `projects/`, and it is built in one or more work roots.

## Project note

`<project-name>.md`, the note that names a project in its `name` property, says in a paragraph what it is, carries its status, and links its PRD and roadmap.

## Ready

A ticket a run may pick: unclaimed, and either in `backlog/` with every dependency `done`, or `blocked` with nothing left in `blocked_by` but `done` tickets. A claimed ticket is never ready for another run.

## Registry

`sdlc.json` at the framework root, naming every work root each project is built in and what belongs in each. It is machine-local and gitignored.

## Roadmap

`roadmap.md`, the work that is left, with one section per epic and one row per open ticket. A row is added when `/plan` writes a ticket and deleted when the ticket is done, and every cell is corrected from the ticket, which is the record.

## Roadmap run

One launch of the autonomous loop, named `run-roadmap-<n>`. It works one feature at a time: it selects a feature, claims its dependency cluster, and builds its tickets one after another, each in a fresh session and each as its own run, then selects the next feature, until one of its ends. It owns one claim name, one run branch, and one run worktree per work root it changes.

## Run

One pass of an orchestrating command over one ticket, from the pick to `done` or to a stop as `blocked`. Each run has a number, shared by its claim and its agents; the runs of a roadmap run share its claim, `run-roadmap-<n>`.

## Run worktree

A git worktree of one work root, made for one roadmap run on its own branch `run-roadmap-<n>`, beside the repository at `<repository>-worktrees/run-roadmap-<n>`. The roadmap run builds and commits there, so the person's checkout is never touched; a person reviews the branch and merges it.

## Stage

One step of a run, such as the plan review or the implementation. An agentic stage has its own agent; a deterministic one, such as running the feature's tests, is a command the orchestrator runs. Each stage has its own worklog entry.

## Test dispute

A claim by `coding` that a test, not its code, is wrong — a test defect. It names the test, what is wrong with it, the evidence, and the change it proposes, and `test-planner` rules on it. It is the only way a written test changes once the code is being built.

## Test plan

The tests one ticket gets, decided from the specification before any code exists. Each case names the bug it catches, the input that exposes it, the expected result, and the cheapest test type that catches it. The plan also lists what goes untested and why.

## Ticket

One task, named `<CODE>-<NNN>-<slug>.md`, where `<CODE>` is the code of the feature it delivers. It carries a status, sits in the bucket under `work/` that status names, and names the work roots it is built in by their registry codes.

## Work folder

`work/` at the framework root, holding every ticket in one of three buckets. It is the ticket board; a work root is a code repository, which is a different thing.

## Work root

One code repository the project is built in, with its own instructions, tests, and git history. A project may have several, and one ticket may change several of them.

## Worklog

The record of what was decided while a ticket was built, kept beside the ticket as `<CODE>-<NNN>-<slug>.worklog.md`. The run that starts the ticket creates it and writes every stage's entry, and it names every work root the ticket changed; `/code` and `/review` only append to one that exists.
