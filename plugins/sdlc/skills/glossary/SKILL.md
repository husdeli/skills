---
name: glossary
description: "Rules for the product's terms — the project's glossary.md that defines each term once under its own heading, how a term is chosen, and how every other document links a definition instead of writing it again. INVOKE THIS SKILL before you name a domain concept in anything a person reads, and before you read, write, rename, or link a glossary entry. Enforces one definition per term, one term per concept, a heading that holds the term alone, and a link at the term's first use in every document."
---

# glossary skill

`<project>/glossary.md` holds the product's **ubiquitous language** — one entry per term the
product uses. **A term is defined once, here.** Every other document links that entry instead of
defining the term again, so no two documents can drift into two meanings.

**The `sdlc-structure` skill resolves the project** — load it before you resolve the path. This
skill holds the term itself: how it is chosen, how its entry is written, and how a document points
at one.

## Choose the term

The reader knows this product by the names the product uses. Use those names.

- **Take the vocabulary from the project**, in this order: `<project>/glossary.md`,
  `<project>/prd.md`, `<project>/features/*/*.feature.md`,
  `<project>/features/*/*.design.md`, `<project>/designs/*.design.md` (or, on an older shape,
  `<project>/*.design.md` or a single `design.md`), `AGENTS.md`, `CLAUDE.md`, the ticket or
  roadmap, then the code. Read these before you write about a domain you have not written about in
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
# Acme — glossary

**Last updated**: 2026-09-27

## Workspace

The container that holds one team's work. A workspace holds many projects, and a person reaches
its content only through a membership in it.

## Workspace owner

The member who can rename a workspace, invite a member, and delete the workspace. Each workspace
has exactly one owner, and the code calls this member an `OrgMember` with the `owner` role.
```

- **The heading is the term, alone.** No definition in the heading, no code symbol, and no trailing
  dash. Every inbound link points at the heading text, so anything else in it breaks the link.
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

In a vault, `**Last updated**` becomes the `updated` property under a `type: glossary` frontmatter
block, and the term headings are unchanged. The `sdlc-structure` skill holds that mapping for every
document.

## Reference the entry

**Every document links the glossary entry at a term's first use in that document**, then uses the
term plainly. Link the load-bearing terms only — a paragraph where every noun is a link reads as
none of them mattered.

| `kind` | The document | The link |
| --- | --- | --- |
| `repo`, `folder` | `prd.md`, `roadmap.md` | `[workspace owner](glossary.md#workspace-owner)` |
| `repo`, `folder` | `designs/checkout.design.md` | `[workspace owner](../glossary.md#workspace-owner)` |
| `repo`, `folder` | `features/checkout/checkout.feature.md` | `[workspace owner](../../glossary.md#workspace-owner)` |
| `repo`, `folder` | `tickets/todo/AUTH-001-user-login.md` | `[workspace owner](../../glossary.md#workspace-owner)` |
| `vault` | any document in the project | `[[glossary#Workspace owner]]` |

- **A repository anchor is the heading in lower case, with each space as a hyphen.**
  `## Workspace owner` is reached as `glossary.md#workspace-owner`.
- **A wikilink carries the heading exactly as it is written**, including its capital letter.
- **Add display text when the sentence needs another form of the word**:
  `[[glossary#Workspace owner|workspace owners]]`, or
  `[workspace owners](glossary.md#workspace-owner)`.
- **A document never repeats a definition it links.** When a definition changes, change the entry
  and leave every link alone.
- **Prose a person reads outside the project carries no link** — a chat reply, a commit message,
  a pull-request body, a review verdict, an agent's report. Use the glossary's term there, plainly.

## Keep it current

- **Whoever coins a term writes its entry**, in the same step that introduces it. A document that
  uses a term with no entry is a document that defines the term twice tomorrow.
- **A rename is one edit**: the heading, and every link that points at it. Search the project for
  the old anchor and the old wikilink before you stop.
- **A term loses its entry when no document uses it.** Delete the entry, and delete the links with
  the prose that carried them.
