---
type: glossary
updated: 2026-10-09
tags:
  - sdlc/glossary
---
# SDLC framework — glossary

## Design doc

A document that says how one solution works: the parts it is built from, how work flows through it, and how it behaves. It describes the target state, never the steps to build it, and it sits in its feature's folder or, when every feature depends on it, in `designs/`.

## Epic

The group of tickets that delivers one feature. The feature's code is the epic's code, it prefixes every ticket ID, and ticket numbering restarts at 001 in each epic.

## Feature

One thing a customer can do with the product, kept as a folder under `features/` with an index note and the design docs it owns. A feature keeps its note after it ships, so `features/` lists everything the product does.

## Framework root

The folder a session starts in. It holds the registry, and it may hold `projects/`; when it does not, it holds one project's documents directly.

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

## Ticket

One task on the board, named `<EPIC>-<NNN>-<slug>.md`. Its folder under `tickets/` is its status, and it never names the repository it is built in.

## Work root

One code repository the project is built in, with its own instructions, tests, and git history. A project may have several, and one ticket may change several of them.

## Worklog

The record of what was decided while a ticket was built, kept beside the ticket as `<EPIC>-<NNN>-<slug>.worklog.md`. Only the orchestrating command writes it, and it names every work root the ticket changed.
