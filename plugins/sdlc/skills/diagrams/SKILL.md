---
name: diagrams
description: "Rules for a diagram in any product document — generated into the project's diagrams/<name>.excalidraw.md by this skill's own builder, referenced from the document with a one-line caption, and written as an ASCII diagram only when the builder cannot run. INVOKE THIS SKILL before you put a diagram in a PRD, a design doc, a ticket, or any other document in the project, and before you update a document whose shape a diagram already shows. Enforces one diagram per shape, one home for every diagram file, the Obsidian `.excalidraw.md` format, a caption that carries the meaning in text, and prose that stays complete without the picture."
---

# diagrams skill

A document earns a diagram when its **shape** is the fact — the parts and what connects them, the
stages of a flow, the regions of a screen, the entities and their relations. Prose carries
everything else. A diagram that repeats a sentence is a diagram to delete.

Every diagram in this project is **one `<name>.excalidraw.md` file in `<project>/diagrams/`**,
built by this skill. The **`sdlc-structure`** skill resolves the project.

## Build it

**Write a small JSON spec, then run this skill's builder.** You never hand-write Excalidraw JSON,
and you never draw the picture in prose.

```bash
python3 <skill>/scripts/excalidraw_md.py build spec.json <project>/diagrams/checkout.excalidraw.md
python3 <skill>/scripts/excalidraw_md.py validate <project>/diagrams/checkout.excalidraw.md
```

`<skill>` is this skill's own directory — `${CLAUDE_PLUGIN_ROOT}/skills/diagrams` in Claude Code.
The spec is a scratch file: delete it once the drawing is written.

```json
{
  "title": "Checkout — parts",
  "layout": "layered",
  "nodes": [
    {"id": "cart", "label": "Cart", "color": "blue"},
    {"id": "queue", "label": "Order queue", "color": "yellow"},
    {"id": "gateway", "label": "Payment gateway", "color": "green"}
  ],
  "edges": [
    {"from": "cart", "to": "queue", "label": "one order"},
    {"from": "queue", "to": "gateway", "label": "charge"}
  ]
}
```

- **[The spec reference](./references/diagram-spec.md)** holds every field, the five layouts, the
  colors and what each one means, how the nine kinds of diagram are shaped, and the budgets: under
  20 elements, under 12 nodes, one shape per file.
- **[The format reference](./references/excalidraw-md-format.md)** holds the `.excalidraw.md` file
  itself — read it only to repair a drawing by hand or to work out why one will not open.
- **Name the file after what it shows**, in kebab-case: `checkout.excalidraw.md`. A diagram that
  belongs to a design doc takes that doc's subject — the subject alone, never the feature folder
  that holds the doc — and a second diagram of the same subject adds
  what it shows — `checkout-states.excalidraw.md`.
- **Validate every file you write.** A drawing that fails `validate` does not open cleanly.
- **Editing an existing drawing**: `unwrap` it to a scene, change the scene, `wrap` it back — or
  rebuild it from a fresh spec, which is usually shorter. A person's own edits in Excalidraw survive
  an `unwrap`/`wrap` round trip; rebuilding from a spec discards them, so ask first.

**When the builder cannot run — no `python3` — write an ASCII diagram in the document instead**:
boxes and arrows for parts and flows, labeled regions for a screen layout. Say nothing about the
missing tool inside the document, and never leave a link to a file you did not create. **Never write
both**: one shape has one diagram.

## Reference it from the document

A drawing says nothing to a reader who sees only the document's text. **Every reference carries a
one-line caption** naming what the picture shows that the surrounding prose does not repeat.

| `kind` | The document | The reference |
| --- | --- | --- |
| `repo`, `folder` | `prd.md` | `[Checkout parts](diagrams/checkout.excalidraw.md)` |
| `repo`, `folder` | `designs/checkout.design.md` | `[Checkout parts](../diagrams/checkout.excalidraw.md)` |
| `repo`, `folder` | `features/checkout/checkout.design.md` | `[Checkout parts](../../diagrams/checkout.excalidraw.md)` |
| `repo`, `folder` | `tickets/todo/AUTH-001-user-login.md` | `[Checkout parts](../../diagrams/checkout.excalidraw.md)` |
| `vault` | any document in the project | `![[checkout.excalidraw]]` |

- **In a vault the reference is an embed**, and the wikilink drops the final `.md` — a file named
  `checkout.excalidraw.md` is linked as `[[checkout.excalidraw]]`. Obsidian's Excalidraw plugin
  renders the drawing in place; without that plugin the reader gets a link. The caption is what
  carries the meaning either way.
- **The prose stays complete without the picture.** Every agent in this plugin reads a document as
  text, so a fact that only the diagram shows is a fact the document is missing. Name the parts and
  what crosses each boundary in the prose, and let the diagram show the arrangement.
- **A diagram is not a place to put detail the document may not hold.** The document's own rules
  still apply inside the picture: no implementation names in a design doc, no mechanism in a PRD.

## Keep it current

- **Update the diagram in the step that changes the design**, by rebuilding it or by editing it in
  Excalidraw. A document and its picture never disagree.
- **Delete the file when the last document that pointed at it stops doing so.** An orphan diagram in
  `diagrams/` is read as current by the next person who opens it.
- **Move a diagram with nothing.** The file stays in `diagrams/` for its whole life, so a document
  that moves keeps its reference — only the number of `../` steps changes.
