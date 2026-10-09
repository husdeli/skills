---
type: glossary
updated: 2026-10-09
tags:
  - sdlc/glossary
---
# SDLC framework — glossary

## Bucket

One of the three folders inside `work/` — `backlog/`, `in-progress/`, and `done/`. Each bucket holds one or more ticket statuses; `in-progress/` holds `in progress`, `blocked`, and `review`.

## Claim

The `claimed` property on a ticket, naming the run that holds it, such as `orchestrate-2`. A claimed ticket is never picked by another run; the claim guards the ticket, while `assigned` names the agent working on it.

## Context pack

What the planner gathers before it plans: the work root, the relevant files, the conventions, and the exact check commands. The orchestrator hands it to every later agent, so none of them explores the code again.

## Design doc

A document that says how one solution works: the parts it is built from, how work flows through it, and how it behaves. It describes the target state, never the steps to build it, and it sits in its feature's folder or, when every feature depends on it, in `designs/`.

## Epic

The group of tickets that delivers one feature. The feature's code is the epic's code, it prefixes every ticket ID, and ticket numbering restarts at 001 in each epic.

## Feature

One thing a customer can do with the product, kept as a folder under `features/` with an index note and the design docs it owns. A feature keeps its note after it ships, so `features/` lists everything the product does.

## Framework root

The folder a session starts in. It holds the registry and the glossary, and it may hold `projects/`; when it does not, it holds one project's documents directly.

## Gate

A fixed rule that decides whether a run goes on, such as the plan-review skip gate or the rule that finishes a ticket. A gate is applied mechanically, from the numbers and verdicts the agents report.

## Glossary

`glossary.md` at the framework root, defining every term the framework and its projects use, each once, under a heading of its own. Every other document links an entry instead of defining the term again.

## Orchestrator

The session that drives one run: it picks the ticket, starts the agents, and settles every gate. It is the only writer of the ticket, the worklog, and the roadmap; an agent reports to it and writes no document.

## Pointer file

`.sdlc.json` at a repository's root, naming the folder that holds the documents of the project that repository is built for. It points from the code to the documents, the opposite direction to the registry.

## PRD

The product requirements document, `prd.md`: what the product does and why. It is assembled from the product notes and never lists features, tickets, or prices.

## Product note

A goal, non-goal, persona, problem, or success metric, kept as one file under `product/`. The PRD and the features cite product notes instead of restating them.

## Project

One product and every document about it. Its documents sit in `projects/<project-name>/`, or directly in the framework root when there is no `projects/`, and it is built in one or more work roots.

## Project note

`<project-name>.md`, the note that names a project in its `name` property, says in a paragraph what it is, carries its status, and links its PRD and roadmap.

## Registry

`sdlc.json` at the framework root, naming every work root each project is built in and what belongs in each. It is machine-local and gitignored.

## Roadmap

`roadmap.md`, the work that is left, with one section per epic and one row per ticket. It only shrinks: a row is deleted when its ticket is done.

## Run

One pass of the workflow over one ticket, from the pick to `done` or to a stop as `blocked`. Each run has a number, shared by its claim and its agents.

## Stage

One step of a run, such as the plan review or the implementation. Each stage has its own agent and its own worklog entry.

## Ticket

One task, named `<CODE>-<NNN>-<slug>.md`, where `<CODE>` is the code of the feature it delivers. It carries a status, sits in the bucket under `work/` that status names, and never names the repository it is built in.

## Work folder

`work/` at the framework root, holding every ticket in one of three buckets. It is the ticket board; a work root is a code repository, which is a different thing.

## Work root

One code repository the project is built in, with its own instructions, tests, and git history. A project may have several, and one ticket may change several of them.

## Worklog

The record of what was decided while a ticket was built, kept beside the ticket as `<CODE>-<NNN>-<slug>.worklog.md`. Only the orchestrating command writes it, and it names every work root the ticket changed.
