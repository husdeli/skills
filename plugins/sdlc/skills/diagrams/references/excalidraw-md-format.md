# The `.excalidraw.md` file

This is the format the Obsidian Excalidraw plugin writes and reads. The scene is JSON, and it
lives inside a markdown file, so a vault indexes the drawing's text, links it, and embeds it.

`scripts/excalidraw_md.py` writes this file for you. Read this page when you write or repair one
by hand, or when a drawing fails to open.

## The skeleton

````markdown
---

excalidraw-plugin: parsed
tags: [excalidraw]

---
==⚠  Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document. ⚠==


# Excalidraw Data

## Text Elements
Cart ^2x96070E

Order queue ^JRPVPik0

%%
## Drawing
```json
{
	"type": "excalidraw",
	"version": 2,
	"source": "https://excalidraw.com",
	"elements": [ … ],
	"appState": { "gridSize": null, "viewBackgroundColor": "#ffffff" },
	"files": {}
}
```
%%
````

Every part of it carries a rule:

- **`excalidraw-plugin: parsed`** in the frontmatter is what makes the file a drawing. Without it
  Obsidian opens a markdown note.
- **`# Excalidraw Data`** opens the data block. Anything above it is the "back of the note" — the
  prose a reader sees. Keep it empty except for the warning line.
- **`## Text Elements`** mirrors every text element in the scene, one per entry, as
  `<the text> ^<the element id>`, separated by a blank line. This is what a vault search finds.
  A text element missing from this section loses its text the next time the plugin saves.
- **`%%` before `## Drawing`** comments the scene out, so reading mode shows the drawing and not
  the JSON. The file ends with a second `%%`.
- **The fence is ```` ```json ````.** A file whose fence says `compressed-json` holds base64, not
  JSON: open it in Obsidian and run *Decompress current Excalidraw file* before you read or edit
  it. Never write a compressed file by hand.

## Element ids

**A text element's id is also an Obsidian block reference**, so it holds 8 characters from
`A-Za-z0-9` and nothing else. An id with `_` or `-` in it breaks the `^ref`. Ids are unique across
the scene.

## The scene

The JSON is an ordinary Excalidraw scene. Each element carries the full set of fields Excalidraw
writes — `id`, `type`, `x`, `y`, `width`, `height`, `angle`, `strokeColor`, `backgroundColor`,
`fillStyle`, `strokeWidth`, `strokeStyle`, `roughness`, `opacity`, `groupIds`, `frameId`, `index`,
`roundness`, `seed`, `version`, `versionNonce`, `isDeleted`, `boundElements`, `updated`, `link`,
`locked` — plus what its own type needs.

Three rules are easy to get wrong:

1. **`index` orders the elements and must ascend** through the array. The values are fractional
   indices compared as text, so `a0` < `a1` < … < `a9` < `aA` < … < `aZ` < `aa`. An out-of-order
   index makes Excalidraw reorder the scene on load.

2. **Text inside a shape is its own element.** The shape holds
   `boundElements: [{"id": "<text id>", "type": "text"}]`, and the text holds
   `containerId: "<shape id>"`, `textAlign: "center"`, `verticalAlign: "middle"`. A `text` field on
   a rectangle is ignored — the label disappears. The same pairing labels an arrow.

3. **An arrow binds to what it connects.** The arrow holds
   `startBinding: {"elementId": …, "focus": 0, "gap": 8}` and the matching `endBinding`, plus
   `points: [[0, 0], [dx, dy]]` relative to its own `x`/`y`. Each bound shape lists the arrow in
   its `boundElements` as `{"id": "<arrow id>", "type": "arrow"}`. Without the bindings the arrow
   stops following the shapes a person moves.

Every `text` element also needs `text`, `rawText`, and `originalText` with the same string,
`fontSize`, `fontFamily`, and `lineHeight` (1.25). `rawText` is what the `## Text Elements`
section mirrors.

## Checking a file

```bash
python3 scripts/excalidraw_md.py validate <file>.excalidraw.md
```

It reports a missing section, a fence it cannot read, a scene that does not parse, duplicate ids,
an index out of order, a text element that is not mirrored, and a binding that names an element
the scene does not hold. A drawing that fails this does not open cleanly in Obsidian.
