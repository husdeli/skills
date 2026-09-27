# The spec a diagram is built from

`scripts/excalidraw_md.py build <spec>.json <name>.excalidraw.md` turns a small JSON spec into a
drawing. Write the spec, run the script, delete the spec. You never hand-write Excalidraw JSON.

```bash
python3 <plugin>/skills/diagrams/scripts/excalidraw_md.py build spec.json ../diagrams/checkout.excalidraw.md
python3 <plugin>/skills/diagrams/scripts/excalidraw_md.py validate ../diagrams/checkout.excalidraw.md
```

## The spec

```json
{
  "title": "Checkout — parts",
  "layout": "layered",
  "nodes": [
    {"id": "cart", "label": "Cart", "color": "blue"},
    {"id": "queue", "label": "Order queue", "color": "yellow"},
    {"id": "gateway", "label": "Payment gateway", "color": "green"},
    {"id": "retry", "label": "Retry?", "shape": "diamond", "color": "red"}
  ],
  "edges": [
    {"from": "cart", "to": "queue", "label": "one order"},
    {"from": "queue", "to": "gateway", "label": "charge"},
    {"from": "gateway", "to": "retry", "label": "declined", "style": "dashed"}
  ],
  "regions": [
    {"label": "Our service", "x": -420, "y": -40, "width": 840, "height": 420}
  ],
  "notes": [
    {"text": "The queue keeps one order per attempt.", "x": -420, "y": 420}
  ]
}
```

| Field | What it holds |
| --- | --- |
| `title` | Optional heading text above the drawing. |
| `layout` | `down`, `right`, `grid`, `layered`, or `none`. Defaults to `layered` when there are edges, `grid` when there are none. |
| `nodes` | `id` (unique), `label`, `shape` (`rectangle`, `ellipse`, `diamond`), `color`, and optional `x`, `y`, `width`, `height`. |
| `edges` | `from` and `to` (node ids), optional `label`, `style` (`solid`, `dashed`, `dotted`). |
| `regions` | A labeled box drawn behind the nodes: `x`, `y`, `width`, `height`, `label`, `color`, `style`. Use it for a boundary, a lane, or a group. |
| `notes` | Free text at a position: `text`, `x`, `y`, `fontSize`. |

A `\n` inside a label wraps it. A node keeps its own `x`/`y` when you set them, so one spec may mix
an automatic layout with a few placed nodes.

## The layouts

- **`down`** — one node under the next. A sequence of steps, a pipeline read top to bottom.
- **`right`** — one node after the next, left to right. A short flow, a request path.
- **`grid`** — a square-ish grid. Entities with no direction between them.
- **`layered`** — each node sits one row below the furthest node that points at it. The default for
  anything with edges: a system, a data flow, a dependency graph.
- **`none`** — every node carries its own `x` and `y`. Use it for a shape the layouts cannot make:
  swimlanes, a sequence diagram's lifelines, a floor plan of a screen.

## The colors

One meaning per color, held across every diagram in a project.

| Name | Use it for |
| --- | --- |
| `blue` | The normal part. Most nodes are blue. |
| `green` | Where work leaves the system, or the successful end. |
| `yellow` | Something that holds state — a queue, a store, a cache. |
| `red` | A failure, a rejection, or a limit. |
| `violet` | An outside party the project does not own. |
| `grey` | Context that is not the subject of this diagram. |
| `none` | An unfilled box, for a region or a frame. |

## Shaping the nine kinds of diagram

| The diagram | How the spec says it |
| --- | --- |
| Flow or process | `layout: down`, one node per step, `diamond` for a decision, labels on the edges out of it. |
| System or architecture | `layout: layered`, a `region` per boundary the design names, `violet` for an outside service. |
| Data flow | `layout: right`, `yellow` for each store, edge labels naming what moves — never the order it moves in. |
| Dependency or relationship | `layout: grid` or `layered`, edge labels naming the relation (`owns`, `reads`). |
| Swimlane | `layout: none`, one `region` per actor as a vertical lane, each node placed in its lane, edges crossing between them. |
| Sequence | `layout: none`, one node per participant across the top, `notes` for the lifelines, edges as the messages in time order down the page. |
| Entity relationship | `layout: grid`, one node per entity with its fields in the label (`\n` between them), edge labels carrying the cardinality (`1:N`). |
| Class | `layout: layered`, the class name and its members in one label, edges from the subtype up to the type. |
| Mind map | `layout: grid` with the centre node placed by hand, or `none` for a radial arrangement. |

## Budgets

- **Under 20 elements**, and under 12 nodes. A node, its label, and each edge all count.
- **One shape per diagram.** A second question is a second file, named for what it shows.
- **Every edge carries a label** unless the arrow means only "then". An unlabeled web of arrows
  tells a reader nothing.
- **Nothing decorative.** No shadow boxes, no icons, no colors outside the table above.
