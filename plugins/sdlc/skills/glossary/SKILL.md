---
name: glossary
description: "Rules for the terms — the framework root's one glossary.md that defines every term the framework and its projects use, each once under its own heading, how a term is chosen, and how every other document links a definition instead of writing it again. INVOKE THIS SKILL before you name a domain concept in anything a person reads, and before you read, write, rename, or link a glossary entry. Enforces one definition per term, one term per concept, a heading that holds the term alone, and a link at the term's first use in every document."
---

# glossary skill

The framework root **holds exactly one** glossary: `glossary.md`, directly in the framework root.
It holds the **ubiquitous language** — one entry per term the framework's documents use, including
each project's own terms. **A term is defined once, here.** Every other document links that entry
instead of defining the term again, so no two documents can drift into two meanings.

| Path | Responsible for | Never holds |
| --- | --- | --- |
| `glossary.md` | Defining each term once, in two or three sentences | A requirement, a behavior, a file layout, a task, or a record of how a definition changed |

**The `sdlc-structure` skill resolves the framework root** — load it before you resolve the path.
This skill holds the term itself: how it is chosen, how its entry is written, and how a document
points at one.

- **The glossary is required.** It is created with the framework root, and holds only its title
  until the first term is coined.
- **A project folder never holds a glossary.** A second note named `glossary` makes every
  `[[glossary#…]]` link ambiguous, so a project's terms go in the framework root's glossary.
- **A term means one thing across the whole framework root.** When two projects need different
  meanings for one word, those are two terms, and each gets its own heading.

## Choose the term

The reader knows this product by the names the product uses. Use those names.

- **Take the vocabulary from the framework root**, in this order: `glossary.md`, the project's
  `prd.md`, `features/*/*.feature.md`, `features/*/*.design.md`, `designs/*.design.md` (or, on an
  older shape, a project's `*.design.md` or a single `design.md`), the work root's `AGENTS.md` and
  `CLAUDE.md`, the ticket or roadmap, then the code. Read these before you write about a domain you have not written about in
  this session.
- **One term per concept, everywhere.** If the glossary says "workspace", never write "project",
  "board", or "space" for the same thing.
- **When the domain word and the code symbol differ, lead with the domain word.** Write "the
  workspace owner (`OrgMember` in the code)" once, then keep using "workspace owner".
- **Never invent a synonym for a term the project already has.** When the project has no term for
  the thing, say so and propose one plainly: "there is no name for this yet — I am calling it the
  export queue."
- **Expand an acronym on first use** unless the project's own docs use it bare.

## Write the entry

**Every term is a heading.** The entry is a `##` heading that holds the term and nothing else, and
the definition is the prose under it:

```markdown
---
type: glossary
updated: 2026-09-27
tags:
  - sdlc/glossary
---
# Acme — glossary

## Workspace

The container that holds one team's work. A workspace holds many projects, and a person reaches
its content only through a membership in it.

## Workspace owner

The member who can rename a workspace, invite a member, and delete the workspace. Each workspace
has exactly one owner, and the code calls this member an `OrgMember` with the `owner` role.
```

- **The frontmatter `type` is `glossary`.** That property marks the note as the glossary.
- **The heading is the term, alone.** No definition in the heading, no code symbol, and no trailing
  dash. Every inbound link names the heading text, so anything else in it ends up in every link.
- **A heading is unique in the file**, and never contains `#`, `|`, `^`, `[`, or `]` — Obsidian
  cannot link a heading that holds one of them.
- **The title is the only other heading.** A `###` under an entry becomes a link target that is not
  a term.
- **The entries run in alphabetical order.** A new term is inserted in place, and the entries around
  it do not move.
- **One entry per concept.** Two entries for one thing are two terms, which is what the
  one-term-per-concept rule forbids. When the code uses a different name for the thing, name that
  symbol inside the entry.
- **Two or three sentences per entry**: what the thing is, and the one fact that separates it from
  the term nearest to it. A requirement stays in the PRD, what a customer can do stays in a
  feature note, and behavior stays in a design doc.
- **Only load-bearing terms.** A term earns an entry when a second document uses it, or when a
  reader would otherwise guess what it means. A plain English word gets no entry.
- **No history in the file.** No changelog, no "formerly", no note about when a definition changed.

A glossary on an older shape — a `**Last updated**:` line under the title, or a `glossary.md` inside
a project folder — is read where it is. The setup entry point moves a project's glossary entries into
the framework root's glossary and rewrites the line as the `updated` property.

## Reference the entry

**Every document links the glossary entry at a term's first use in that document**, then uses the
term plainly. Link the load-bearing terms only — a paragraph where every noun is a link reads as
none of them mattered.

| `kind` | The document | The link |
| --- | --- | --- |
| `vault` | any document in the framework root | `[[glossary#Workspace owner]]` |
| `repo`, `folder` | `designs/checkout.design.md` | `[workspace owner](../glossary.md#workspace-owner)` |
| `repo`, `folder` | `projects/acme/prd.md` | `[workspace owner](../../glossary.md#workspace-owner)` |
| `repo`, `folder` | `features/checkout/checkout.feature.md` | `[workspace owner](../../glossary.md#workspace-owner)` |
| `repo`, `folder` | `work/backlog/AUTH-001-user-login.md` | `[workspace owner](../../glossary.md#workspace-owner)` |

- **A repository anchor is the heading in lower case, with each space as a hyphen.**
  `## Workspace owner` is reached as `glossary.md#workspace-owner`.
- **A wikilink carries the heading exactly as it is written**, including its capital letter.
  `[[glossary#workspace owner]]` does not reach `## Workspace owner`.
- **A wikilink names the file as `glossary`, with no path.** The name is unique in the vault, so the
  same link resolves from every folder.
- **Inside a table, escape the pipe**: `[[glossary#Workspace owner\|workspace owners]]`. An
  unescaped pipe ends the table cell.
- **Add display text when the sentence needs another form of the word**:
  `[[glossary#Workspace owner|workspace owners]]`, or
  `[workspace owners](glossary.md#workspace-owner)`.
- **A document never repeats a definition it links.** When a definition changes, change the entry
  and leave every link alone.
- **Prose a person reads outside the framework root carries no link** — a chat reply, a commit message,
  a pull-request body, a review verdict, an agent's report. Use the glossary's term there, plainly.

## Keep it current

- **Whoever coins a term writes its entry**, in the same step that introduces it. A document that
  uses a term with no entry is a document that defines the term twice tomorrow.
- **A rename is one edit**: the heading, and every link that points at it. Search the framework root
  for `glossary#<old term>` and the old anchor, and rewrite each match before you stop.
- **A term loses its entry when no document uses it.** Delete the entry, and delete the links with
  the prose that carried them.
