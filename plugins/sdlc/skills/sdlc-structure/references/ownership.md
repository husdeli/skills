# Ownership and links

Which document owns each fact, which way a link points, and how a document names the documents it relates to.

## One fact, one document

Five documents describe the same product, so each fact has **one owner**. Every other document
links that owner instead of writing the fact a second time. A fact written twice is a fact that
disagrees with itself as soon as one copy changes.

| The fact | Owned by | What everyone else does |
| --- | --- | --- |
| What existing tools fail at | a note in `product/problems/` | Link the note. Nothing restates the failure, and nothing but the goal that answers it says what this product does about it. |
| What the product commits to, and what it refuses | a note in `product/goals/` or `product/non-goals/` | Link the note. A feature cites the goal it advances; the PRD lists it in one line. |
| Who the users are, and what each one needs | a note in `product/personas/` | Link the note. The business plan adds only which of them **pays first** and what they pay for. |
| What proves the product is working | a note in `product/metrics/` | Link the note. The measured value lives there, with the date it was read. |
| How a product area works, as a whole | `prd.md` §5 | Link the area's anchor code. A feature note never retells its area's prose. |
| The guarantees that hold across the product | `prd.md` §6 | Link the theme. |
| What one customer can do, and whether it ships | the feature index | Link the note. The PRD never enumerates features; the business plan queries them. |
| How a solution is built and behaves | the design doc | Link the file. The feature index lists its designs and describes none of them. |
| What the product costs, earns, and is worth against a competitor | `business/business-plan.md` | Nothing else carries a price, a margin, or a positioning claim — the PRD is product-only. |
| What is left to build | `roadmap.md` and the tickets | Link the ticket. The PRD, the feature index, and the design docs cite no ticket. |

**The direction of a link is fixed.** The plan links the PRD; the PRD never links the plan. A
ticket links its feature; a feature note never cites a ticket, though its query may list one. A
design doc links its feature; a feature note lists its designs by name. Reading the chain downwards
— plan, PRD, feature, design, ticket — each step adds detail and repeats nothing.

**When two documents need the same sentence, the lower one keeps it and the higher one links.** The
PRD holds the sentence a feature note would otherwise repeat, and the feature note holds the
sentence the business plan would otherwise repeat.

## Related documents are a frontmatter property

**A document names the documents it relates to in one `related:` property, in its YAML
frontmatter.** This is true in every destination: a vault, a `repo`, and a `folder`. The body never
holds a `**Related**:` line, a `## Related` section, a list of related specifications, or any other
block whose only job is to point at other documents.

```yaml
---
related:
  - "[[prd#Authentication `AUTH`|AUTH]]"
  - "[[auth.design]]"
  - "[[AUTH-002-session-timeout]]"
---
```

- **One entry is one link.** In a vault the entry is a quoted wikilink. In a `repo` or a `folder`
  it is a path relative to the document, such as `../prd.md` or `../../designs/auth.design.md`. A
  ticket is the exception: it is named by its file name alone, because it moves between status
  folders. A link to one section keeps its heading.
- **An entry holds no reason.** When a reader needs to know why a document matters, the body says
  so in the sentence that uses it, and links it there.
- **The direction rules in [One fact, one document](#one-fact-one-document) still hold.** `related:` lists only the documents this document may
  link. The PRD never lists the business plan, and a feature note never lists a ticket.
- **A dedicated property is not repeated in `related:`.** A ticket's `feature` and a worklog's
  `ticket` are properties of their own.
- **Leave the property out when it has no entry.** Never write an empty list.
- **Outside a vault, `related:` is the only frontmatter property.** Every other field stays a
  `**Field**: value` line under the title, as [the destinations](destinations.md) describe.

