---
type: design
subject: glossary
updated: 2026-10-09
tags:
  - sdlc/design
related:
  - "[[SDLC-framework.design]]"
---
# Glossary

This doc defines `glossary.md`, the framework's one [[glossary#Glossary|glossary]], and how every other document links a term in it.

## 1. Structure

The framework **holds exactly one** glossary: `glossary.md`, directly in the [[glossary#Framework root|framework root]]. It defines every term the framework's documents use, including each [[glossary#Project|project]]'s own terms. Each term is defined once, under a heading of its own.

| Path          | Responsible for                                          | Never holds                                                                          |
| ------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `glossary.md` | Defining each term once, in two or three sentences | A requirement, a behavior, a file layout, a task, or a record of how a definition changed |

**The frontmatter `type` is `glossary`.** That property marks the note as the glossary:

```yaml
---
type: glossary
updated: 2026-10-09
tags:
  - sdlc/glossary
---
# SDLC framework — glossary

## Bucket

One of the three folders inside `work/` — `backlog/`, `in-progress/`, and `done/`. ...

## Design doc

A document that says how one solution works. ...
```

**Every term is a `##` heading, and the heading holds the term alone.** The definition is the prose under it. A link names the heading text, so a definition, a code symbol, or a trailing dash in the heading would end up in every link to it.

- **A heading is unique in the file.** Two entries with the same heading make every link to them ambiguous, and two entries for one concept are two terms for one thing.
- **A heading never contains `#`, `|`, `^`, `[`, or `]`.** Obsidian cannot link a heading that holds one of them.
- **The title is the only other heading.** A `###` under an entry becomes a link target that is not a term.
- **The entries run in alphabetical order.** A new entry goes in its place, and the entries around it do not move.
- **An entry says what the thing is, and the one fact that separates it from the term nearest to it.** Behavior stays in a design doc, requirements stay in the PRD, and what a customer can do stays in a feature note.
- **Only terms that matter get an entry.** A term gets one when a second document uses it, or when a reader would otherwise guess what it means. A plain English word gets none.

## 2. Reference

**A document links the entry at the term's first use in that document**, then uses the term without a link:

| Link                            | When                                                                  |
| ------------------------------- | --------------------------------------------------------------------- |
| `[[glossary#Work root]]`        | The sentence uses the term exactly as the heading writes it           |
| `[[glossary#Work root\|work roots]]` | The sentence needs another form: a plural, or a lower-case first letter |

- **The link names the heading exactly as it is written**, including its capital letter. `[[glossary#work root]]` does not reach `## Work root`.
- **The link names the file as `glossary`, with no path.** The file name is unique in the vault, so the same link resolves from every folder.
- **Inside a table, the pipe is escaped**: `[[glossary#Bucket\|buckets]]`. An unescaped pipe ends the table cell.
- **A document never repeats a definition it links.** When a definition changes, the entry changes and every link stays as it is.

## 3. Behavior

- **Whoever coins a term writes its entry**, in the same step that first uses it. A document that uses a term with no entry leaves the next writer to define it a second time.
- **A rename changes the heading and every link to it in one step.** The step searches the framework root for `glossary#<old term>` and rewrites each match.
- **An entry no document links is deleted**, with the prose that used the term.

## 4. Variation and limits

- **The glossary is required.** It is created with the framework root, and holds only its title until the first term is coined.
- **A term means one thing across the whole framework.** When two projects need different meanings for one word, those are two terms, and each gets its own heading.
- **A project folder never holds a glossary.** A second note named `glossary` makes every `[[glossary#…]]` link ambiguous, so a project's terms go in the framework's glossary.
