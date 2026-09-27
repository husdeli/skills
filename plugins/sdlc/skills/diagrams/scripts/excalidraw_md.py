#!/usr/bin/env python3
"""Write and read Obsidian Excalidraw drawings (`<name>.excalidraw.md`).

Four commands:

  build <spec.json> <out.excalidraw.md>   spec of nodes and edges -> a drawing
  wrap <scene.json> <out.excalidraw.md>   an Excalidraw scene -> a drawing
  unwrap <in.excalidraw.md> <scene.json>  a drawing -> its Excalidraw scene
  validate <file.excalidraw.md>           check the file the plugin has to parse

The file layout is the one the Obsidian Excalidraw plugin writes and parses:
frontmatter, `# Excalidraw Data`, `## Text Elements` mirroring each text element
as `<text> ^<id>`, then the scene as JSON in a `## Drawing` section commented out
with `%%`.

No third-party packages.
"""

from __future__ import annotations

import json
import random
import re
import string
import sys
import time

FRONTMATTER = (
    "---\n"
    "\n"
    "excalidraw-plugin: parsed\n"
    "tags: [excalidraw]\n"
    "\n"
    "---\n"
    "==⚠  Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document. ⚠==\n"
    "\n"
    "\n"
)

SOURCE = "https://excalidraw.com"
FONT_FAMILY = 5  # Excalifont
FONT_SIZE = 20
LINE_HEIGHT = 1.25
CHAR_WIDTH = 0.6  # of the font size, enough for Excalifont

PALETTE = {
    "blue": ("#1971c2", "#a5d8ff"),
    "green": ("#2f9e44", "#b2f2bb"),
    "yellow": ("#f08c00", "#ffec99"),
    "red": ("#e03131", "#ffc9c9"),
    "violet": ("#6741d9", "#d0bfff"),
    "grey": ("#1e1e1e", "#e9ecef"),
    "none": ("#1e1e1e", "transparent"),
}

# Fractional indices order lexicographically: digits, then upper, then lower case.
INDEX_ALPHABET = string.digits + string.ascii_uppercase + string.ascii_lowercase
ID_ALPHABET = string.ascii_letters + string.digits

DRAWING_REG = re.compile(r"\n##? Drawing\n[^`]*(?:```json\n)([\s\S]*?)```\n")
TEXT_SECTION_REG = re.compile(r"^(?:%%\n+)?##? Text Elements(?:\n|$)", re.M)
DATA_SECTION_REG = re.compile(r"^(?:%%\n+)?# Excalidraw Data(?:\n|$)", re.M)


class SpecError(Exception):
    """The spec cannot be drawn."""


# ---------------------------------------------------------------- ids and text


def new_id() -> str:
    """An 8-character id, so it is also a valid Obsidian block reference."""
    return "".join(random.choice(ID_ALPHABET) for _ in range(8))


def fractional_index(position: int) -> str:
    if position < len(INDEX_ALPHABET):
        return "a" + INDEX_ALPHABET[position]
    high, low = divmod(position, len(INDEX_ALPHABET))
    return "b" + INDEX_ALPHABET[high] + INDEX_ALPHABET[low]


def text_size(text: str, font_size: int = FONT_SIZE) -> tuple[float, float]:
    lines = text.split("\n")
    width = max((len(line) for line in lines), default=0) * font_size * CHAR_WIDTH
    return width, len(lines) * font_size * LINE_HEIGHT


# ------------------------------------------------------------------- elements


def base_element(kind: str, index: str, **fields) -> dict:
    element = {
        "id": fields.pop("id", new_id()),
        "type": kind,
        "x": 0,
        "y": 0,
        "width": 0,
        "height": 0,
        "angle": 0,
        "strokeColor": "#1e1e1e",
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 2,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "groupIds": [],
        "frameId": None,
        "index": index,
        "roundness": None,
        "seed": random.randint(1, 2**31 - 1),
        "version": 1,
        "versionNonce": random.randint(1, 2**31 - 1),
        "isDeleted": False,
        "boundElements": [],
        "updated": int(time.time() * 1000),
        "link": None,
        "locked": False,
    }
    element.update(fields)
    return element


def text_element(index: str, text: str, x: float, y: float, **fields) -> dict:
    width, height = text_size(text, fields.get("fontSize", FONT_SIZE))
    element = base_element(
        "text",
        index,
        x=x,
        y=y,
        width=width,
        height=height,
        text=text,
        rawText=text,
        originalText=text,
        fontSize=FONT_SIZE,
        fontFamily=FONT_FAMILY,
        textAlign="left",
        verticalAlign="top",
        containerId=None,
        lineHeight=LINE_HEIGHT,
        autoResize=True,
    )
    element.update(fields)
    return element


def shape_element(index: str, shape: str, node: dict) -> dict:
    stroke, background = PALETTE[node.get("color", "blue")]
    roundness = {"type": 3} if shape == "rectangle" else None
    return base_element(
        shape,
        index,
        x=node["x"],
        y=node["y"],
        width=node["width"],
        height=node["height"],
        strokeColor=stroke,
        backgroundColor=background,
        roundness=roundness,
    )


def bound_label(index: str, container: dict, text: str) -> dict:
    """A text element that lives inside a shape or on an arrow."""
    width, height = text_size(text)
    label = text_element(
        index,
        text,
        container["x"] + (container["width"] - width) / 2,
        container["y"] + (container["height"] - height) / 2,
        containerId=container["id"],
        textAlign="center",
        verticalAlign="middle",
        strokeColor="#1e1e1e",
        autoResize=False,
        width=min(width, max(container["width"] - 16, 40)) if container["width"] else width,
        height=height,
    )
    container["boundElements"].append({"id": label["id"], "type": "text"})
    return label


# --------------------------------------------------------------------- layouts


def layer_of_each_node(nodes: list[dict], edges: list[dict]) -> dict[str, int]:
    """Longest path from any root, so an edge always points at a lower layer."""
    layer = {node["id"]: 0 for node in nodes}
    for _ in range(len(nodes)):
        changed = False
        for edge in edges:
            if edge["from"] not in layer or edge["to"] not in layer:
                continue
            candidate = layer[edge["from"]] + 1
            if candidate > layer[edge["to"]]:
                layer[edge["to"]] = candidate
                changed = True
        if not changed:
            break
    return layer


def place(nodes: list[dict], edges: list[dict], layout: str) -> None:
    for node in nodes:
        label = node.get("label", "")
        width, _ = text_size(label)
        node.setdefault("width", max(160, width + 48))
        node.setdefault("height", 60 + (label.count("\n") * 26))

    unplaced = [node for node in nodes if "x" not in node or "y" not in node]
    if not unplaced:
        return
    if layout == "none":
        raise SpecError("layout 'none' needs an x and a y on every node")

    gap_x, gap_y = 120, 100
    if layout == "down":
        y = 0
        for node in unplaced:
            node["x"], node["y"] = -node["width"] / 2, y
            y += node["height"] + gap_y
    elif layout == "right":
        x = 0
        for node in unplaced:
            node["x"], node["y"] = x, 0
            x += node["width"] + gap_x
    elif layout == "grid":
        columns = max(1, round(len(unplaced) ** 0.5))
        widest = max(node["width"] for node in unplaced)
        tallest = max(node["height"] for node in unplaced)
        for position, node in enumerate(unplaced):
            node["x"] = (position % columns) * (widest + gap_x)
            node["y"] = (position // columns) * (tallest + gap_y)
    elif layout == "layered":
        layer = layer_of_each_node(nodes, edges)
        rows: dict[int, list[dict]] = {}
        for node in unplaced:
            rows.setdefault(layer[node["id"]], []).append(node)
        tallest = max(node["height"] for node in unplaced)
        for depth, row in sorted(rows.items()):
            row_width = sum(node["width"] for node in row) + gap_x * (len(row) - 1)
            x = -row_width / 2
            for node in row:
                node["x"], node["y"] = x, depth * (tallest + gap_y)
                x += node["width"] + gap_x
    else:
        raise SpecError(
            f"unknown layout {layout!r}: use down, right, grid, layered, or none"
        )


def anchors(source: dict, target: dict) -> tuple[float, float, float, float]:
    """Where an arrow leaves one shape and where it arrives at the other."""
    sx, sy = source["x"] + source["width"] / 2, source["y"] + source["height"] / 2
    tx, ty = target["x"] + target["width"] / 2, target["y"] + target["height"] / 2
    if abs(ty - sy) >= abs(tx - sx):
        start_y = source["y"] + (source["height"] if ty > sy else 0)
        end_y = target["y"] + (0 if ty > sy else target["height"])
        return sx, start_y, tx, end_y
    start_x = source["x"] + (source["width"] if tx > sx else 0)
    end_x = target["x"] + (0 if tx > sx else target["width"])
    return start_x, sy, end_x, ty


# ----------------------------------------------------------------------- build


def build_scene(spec: dict) -> dict:
    nodes = spec.get("nodes", [])
    edges = spec.get("edges", [])
    if not nodes and not spec.get("regions") and not spec.get("notes"):
        raise SpecError("the spec draws nothing: give it nodes, regions, or notes")

    by_id: dict[str, dict] = {}
    for node in nodes:
        if "id" not in node:
            raise SpecError("every node needs an id")
        if node["id"] in by_id:
            raise SpecError(f"two nodes share the id {node['id']!r}")
        shape = node.get("shape", "rectangle")
        if shape not in ("rectangle", "ellipse", "diamond"):
            raise SpecError(f"unknown shape {shape!r} on node {node['id']!r}")
        if node.get("color", "blue") not in PALETTE:
            raise SpecError(f"unknown color {node.get('color')!r} on {node['id']!r}")
        by_id[node["id"]] = node
    for edge in edges:
        for end in ("from", "to"):
            if edge.get(end) not in by_id:
                raise SpecError(f"edge {end} names no node: {edge.get(end)!r}")

    place(nodes, edges, spec.get("layout", "layered" if edges else "grid"))

    elements: list[dict] = []
    index = 0

    def next_index() -> str:
        nonlocal index
        value = fractional_index(index)
        index += 1
        return value

    for region in spec.get("regions", []):
        box = base_element(
            "rectangle",
            next_index(),
            x=region["x"],
            y=region["y"],
            width=region["width"],
            height=region["height"],
            strokeColor=PALETTE[region.get("color", "grey")][0],
            backgroundColor="transparent",
            strokeStyle=region.get("style", "dashed"),
            roundness={"type": 3},
        )
        elements.append(box)
        if region.get("label"):
            elements.append(
                text_element(
                    next_index(),
                    region["label"],
                    region["x"] + 12,
                    region["y"] - 32,
                    strokeColor=PALETTE[region.get("color", "grey")][0],
                    fontSize=16,
                )
            )

    if spec.get("title"):
        top = min((node["y"] for node in nodes), default=0)
        left = min((node["x"] for node in nodes), default=0)
        elements.append(
            text_element(
                next_index(),
                spec["title"],
                left,
                top - 90,
                fontSize=28,
            )
        )

    shapes: dict[str, dict] = {}
    for node in nodes:
        shape = shape_element(next_index(), node.get("shape", "rectangle"), node)
        shapes[node["id"]] = shape
        elements.append(shape)
        if node.get("label"):
            elements.append(bound_label(next_index(), shape, node["label"]))

    for edge in edges:
        source, target = shapes[edge["from"]], shapes[edge["to"]]
        x1, y1, x2, y2 = anchors(by_id[edge["from"]], by_id[edge["to"]])
        arrow = base_element(
            "arrow",
            next_index(),
            x=x1,
            y=y1,
            width=abs(x2 - x1),
            height=abs(y2 - y1),
            strokeStyle=edge.get("style", "solid"),
            roundness={"type": 2},
            points=[[0, 0], [x2 - x1, y2 - y1]],
            lastCommittedPoint=None,
            startBinding={"elementId": source["id"], "focus": 0, "gap": 8},
            endBinding={"elementId": target["id"], "focus": 0, "gap": 8},
            startArrowhead=None,
            endArrowhead="arrow",
            elbowed=False,
        )
        source["boundElements"].append({"id": arrow["id"], "type": "arrow"})
        target["boundElements"].append({"id": arrow["id"], "type": "arrow"})
        elements.append(arrow)
        if edge.get("label"):
            elements.append(bound_label(next_index(), arrow, edge["label"]))

    for note in spec.get("notes", []):
        elements.append(
            text_element(
                next_index(),
                note["text"],
                note["x"],
                note["y"],
                fontSize=note.get("fontSize", 16),
            )
        )

    return {
        "type": "excalidraw",
        "version": 2,
        "source": SOURCE,
        "elements": elements,
        "appState": {"gridSize": None, "viewBackgroundColor": "#ffffff"},
        "files": {},
    }


# ------------------------------------------------------------- read and write


def to_markdown(scene: dict) -> str:
    out = [FRONTMATTER, "# Excalidraw Data\n", "\n## Text Elements\n"]
    for element in scene.get("elements", []):
        if element.get("type") != "text":
            continue
        raw = element.get("rawText", element.get("text", ""))
        out.append(f"{raw} ^{element['id']}\n\n")
    out.append("%%\n## Drawing\n```json\n")
    out.append(json.dumps(scene, indent="\t", ensure_ascii=False))
    out.append("\n```\n%%")
    return "".join(out)


def from_markdown(text: str) -> dict:
    if "```compressed-json" in text:
        raise SpecError(
            "this drawing is compressed. In Obsidian run "
            "'Decompress current Excalidraw file', then read it again"
        )
    found = DRAWING_REG.search("\n" + text)
    if not found:
        raise SpecError("no '## Drawing' section with a ```json block")
    return json.loads(found.group(1))


def validate(text: str) -> list[str]:
    problems: list[str] = []
    if "excalidraw-plugin: parsed" not in text.split("---")[1 if text.startswith("---") else 0]:
        problems.append("frontmatter is missing 'excalidraw-plugin: parsed'")
    if not DATA_SECTION_REG.search(text):
        problems.append("no '# Excalidraw Data' heading")
    if not TEXT_SECTION_REG.search(text):
        problems.append("no '## Text Elements' heading")
    if not text.rstrip().endswith("%%"):
        problems.append("the drawing section does not end with '%%'")

    try:
        scene = from_markdown(text)
    except (SpecError, json.JSONDecodeError) as error:
        problems.append(f"the scene does not read back: {error}")
        return problems

    elements = scene.get("elements", [])
    ids = [element.get("id") for element in elements]
    if len(ids) != len(set(ids)):
        problems.append("two elements share an id")
    indices = [element.get("index") for element in elements]
    if indices != sorted(indices):
        problems.append("the 'index' values are not in ascending order")

    mirrored = dict(re.findall(r"^(.*) \^([A-Za-z0-9]{1,})$", text, re.M))
    by_ref = {ref: raw for raw, ref in mirrored.items()}
    for element in elements:
        if element.get("type") != "text":
            continue
        raw = element.get("rawText", element.get("text", ""))
        if element["id"] not in by_ref:
            problems.append(f"text element {element['id']} is not under '## Text Elements'")
        elif by_ref[element["id"]] != raw.split("\n")[-1]:
            problems.append(f"text element {element['id']} does not match its mirrored line")
        if element.get("containerId"):
            container = next((e for e in elements if e["id"] == element["containerId"]), None)
            if container is None:
                problems.append(f"text {element['id']} names a container that is not here")
            elif not any(
                bound.get("id") == element["id"]
                for bound in (container.get("boundElements") or [])
            ):
                problems.append(
                    f"container {element['containerId']} does not list its text {element['id']}"
                )
    for element in elements:
        for end in ("startBinding", "endBinding"):
            binding = element.get(end)
            if binding and not any(e["id"] == binding["elementId"] for e in elements):
                problems.append(f"{element['id']} {end} names an element that is not here")
    return problems


# ------------------------------------------------------------------------ main


def read_json(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def write_text(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__.strip())
        return 2
    command = argv[1]
    try:
        if command == "build" and len(argv) == 4:
            scene = build_scene(read_json(argv[2]))
            write_text(argv[3], to_markdown(scene))
            print(f"{argv[3]}: {len(scene['elements'])} elements")
        elif command == "wrap" and len(argv) == 4:
            write_text(argv[3], to_markdown(read_json(argv[2])))
            print(f"{argv[3]}: wrapped")
        elif command == "unwrap" and len(argv) == 4:
            with open(argv[2], encoding="utf-8") as handle:
                scene = from_markdown(handle.read())
            write_text(argv[3], json.dumps(scene, indent="\t", ensure_ascii=False))
            print(f"{argv[3]}: {len(scene.get('elements', []))} elements")
        elif command == "validate" and len(argv) == 3:
            with open(argv[2], encoding="utf-8") as handle:
                problems = validate(handle.read())
            if problems:
                for problem in problems:
                    print(f"- {problem}")
                return 1
            print(f"{argv[2]}: valid")
        else:
            print(__doc__.strip())
            return 2
    except (SpecError, OSError, json.JSONDecodeError) as error:
        print(f"error: {error}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
