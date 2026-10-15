#!/usr/bin/env python3
#
# create-note.py — write the notes an agent asked for into its feature's `notes/` folder.
#
# A note is an action only a person can take — a firewall rule in a cloud console, a secret in a
# vault, a DNS record, a setting in a third-party dashboard — that the code an agent wrote depends
# on. The coding agent reports each one in its result block as `notes`; the orchestrator pipes that
# array into this script, and the script writes one `<slug>.note.md` per entry. Nothing about the
# file is left to a model: the path, the name, the properties, and the body come from here.
#
#   ./create-note.py --root <framework root> --ticket <ticket file> --run orchestrate-3 < notes.json
#   ./create-note.py --root <framework root> --feature checkout --run code < notes.json
#
# The input is the `notes` array from the agent's block, or an object holding it under `notes`:
#
#   [{ "title": "", "action": "", "reason": "", "when": "before-release" }]
#
# `when` is `before-release`, `after-release`, or `anytime`, and defaults to `anytime`. With
# `--ticket`, the feature comes from the ticket's `feature` property and the note links the ticket.
#
# A note's file name comes from its title, so the same need reported twice — by a fix turn, or by a
# resumed run — lands on the file that already exists, and that file is kept as it is.
#
# It prints one JSON object — `{"created": [...], "existing": [...]}`, absolute paths — and exits 0.
# Exit 2 means nothing was written: the input was invalid, or the feature could not be found.

from __future__ import annotations

import argparse
import datetime as _datetime
import json
import re
import sys
from pathlib import Path

VERSION = "1.0.0"

WHEN = ("before-release", "after-release", "anytime")
DEFAULT_WHEN = "anytime"
REQUIRED = ("title", "action", "reason")
SLUG_LIMIT = 60

FEATURE_PROPERTY = re.compile(r"^feature:\s*(.+?)\s*$", re.MULTILINE)
WIKILINK = re.compile(r"^\[\[([^\]|#]+)")


class NoteError(Exception):
    pass


def find_framework_root(start: Path) -> Path | None:
    home = Path.home().resolve()
    for folder in [start, *start.parents]:
        if (folder / "sdlc.json").is_file():
            return folder
        if (folder / "glossary.md").is_file() and (
            (folder / "work").is_dir() or (folder / "features").is_dir()
        ):
            return folder
        if folder == home:
            break
    return None


def in_vault(path: Path) -> bool:
    return any((folder / ".obsidian").is_dir() for folder in [path, *path.parents])


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    if len(slug) > SLUG_LIMIT:
        slug = slug[:SLUG_LIMIT].rsplit("-", 1)[0]
    return slug


def feature_from_ticket(ticket: Path) -> str:
    try:
        text = ticket.read_text(encoding="utf-8")
    except OSError as error:
        raise NoteError(f"cannot read the ticket {ticket}: {error}") from error
    head = text.split("\n---", 2)[0] if text.startswith("---") else ""
    match = FEATURE_PROPERTY.search(head)
    if not match:
        raise NoteError(f"the ticket {ticket.name} has no `feature` property")
    value = match.group(1).strip().strip("\"'")
    link = WIKILINK.match(value)
    name = link.group(1) if link else Path(value).name
    name = name.removesuffix(".md").removesuffix(".feature")
    if not name:
        raise NoteError(f"the ticket {ticket.name} has an empty `feature` property")
    return name


def read_notes(raw: str) -> list[dict[str, str]]:
    try:
        data = json.loads(raw, strict=False) if raw.strip() else []
    except ValueError as error:
        raise NoteError(f"the input is not JSON: {error}") from error
    if isinstance(data, dict):
        data = data.get("notes", [])
    if not isinstance(data, list):
        raise NoteError("the input is neither a `notes` array nor an object holding one")

    notes, problems = [], []
    for index, entry in enumerate(data):
        if not isinstance(entry, dict):
            problems.append(f"note {index}: not an object")
            continue
        note = {key: str(entry.get(key) or "").strip() for key in (*REQUIRED, "when")}
        missing = [key for key in REQUIRED if not note[key]]
        if missing:
            problems.append(f"note {index}: missing {', '.join(missing)}")
        note["when"] = note["when"] or DEFAULT_WHEN
        if note["when"] not in WHEN:
            problems.append(f"note {index}: `when` is {note['when']!r}, not one of {', '.join(WHEN)}")
        if note["title"] and not slugify(note["title"]):
            problems.append(f"note {index}: the title has no letter or digit to name the file by")
        notes.append(note)
    if problems:
        raise NoteError("; ".join(problems))
    return notes


def render(note: dict[str, str], feature: str, ticket: Path | None, run: str, vault: bool, now: str) -> str:
    def link(name: str) -> str:
        return f'"[[{name}]]"' if vault else f"{name}.md"

    lines = ["---", "type: note", f"feature: {link(f'{feature}.feature')}"]
    if ticket:
        lines.append(f"ticket: {link(ticket.stem)}")
    lines += [
        "status: open",
        f"when: {note['when']}",
        f"createdAt: {now}",
        f"createdBy: {run}",
        "tags:",
        "  - sdlc/note",
        "  - human-required",
        "---",
        "",
        f"# {note['title']}",
        "",
        "## What to do",
        "",
        note["action"],
        "",
        "## Why",
        "",
        note["reason"],
        "",
    ]
    return "\n".join(lines)


def create(args: argparse.Namespace, raw: str) -> dict[str, list[str]]:
    root = Path(args.root).expanduser().resolve() if args.root else find_framework_root(Path.cwd().resolve())
    if not root or not root.is_dir():
        raise NoteError("no framework root: pass --root, or run from inside one")

    ticket = Path(args.ticket).expanduser().resolve() if args.ticket else None
    feature = args.feature or feature_from_ticket(ticket)
    feature_dir = root / "features" / feature
    if not (feature_dir / f"{feature}.feature.md").is_file():
        raise NoteError(f"no feature note at {feature_dir / f'{feature}.feature.md'}")

    notes = read_notes(raw)
    vault = in_vault(root)
    now = _datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")
    notes_dir = feature_dir / "notes"
    result: dict[str, list[str]] = {"created": [], "existing": []}
    for note in notes:
        path = notes_dir / f"{slugify(note['title'])}.note.md"
        if path.exists():
            result["existing"].append(str(path))
            continue
        notes_dir.mkdir(exist_ok=True)
        path.write_text(render(note, feature, ticket, args.run, vault, now), encoding="utf-8")
        result["created"].append(str(path))
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write an agent's notes into its feature's notes/ folder.")
    parser.add_argument("--root", help="the framework root; found from the working directory when left out")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--ticket", help="the ticket file the notes came from; names the feature")
    target.add_argument("--feature", help="the feature folder name, when there is no ticket")
    parser.add_argument("--run", required=True, help="who asked for the notes, e.g. orchestrate-3")
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    args = parser.parse_args(argv)

    try:
        result = create(args, sys.stdin.read())
    except NoteError as error:
        print(f"create-note: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
