#!/usr/bin/env python3
#
# build-roadmap.py — rebuild the roadmap's tables from the tickets.
#
# The tickets are the record. This script reads every ticket on the board and writes each epic's
# table from what it finds: one row per open ticket, its priority and status taken from the ticket,
# its outstanding blockers computed from the ticket's `depends_on` field, and the rows ordered so
# that a task never sits above something it still depends on. Priority orders everything that is
# not blocking something else.
#
#   ./build-roadmap.py                      # rebuild every project's tables in place
#   ./build-roadmap.py --check              # report drift, write nothing (exit 1 when it differs)
#   ./build-roadmap.py --project acme-billing
#   ./build-roadmap.py --project ~/Vaults/Work/projects/acme-billing
#
# Run it from the framework root, from anywhere inside it, or from a code repository whose
# `.sdlc.json` points at it. It finds the framework root the way every command does — the first
# folder holding `sdlc.json`, else one holding `glossary.md` beside `work/` or `features/`; from a
# repository, the `root` its `.sdlc.json` names, else its `.sdlc/` folder — and reads the tickets
# in `work/backlog/`, `work/in-progress/`, and `work/done/`.
#
# Each project keeps its own `roadmap.md`. A ticket belongs to every project its feature's
# `projects` property names, so with no --project the script rebuilds every project's roadmap,
# each from the tickets that belong to it. A framework root with no `projects/` holds one project.
#
# An older board still reads: `tickets/todo|in-progress|done/` or a flat `tickets/` folder, and the
# statuses `Not Started` and `Completed`.
#
# What it never does: invent a task, rewrite or move a ticket, delete an epic's section, or decide
# that a feature has shipped. Those need a person or a command. This script writes table rows, a
# new epic's section, and the roadmap's `updated` date, and reports everything else it found.
#
# Exit codes: 0 nothing to fix, 1 the roadmap differs from the tickets (--check only), 2 an error
# that stopped the rebuild.

from __future__ import annotations

import argparse
import datetime as _datetime
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

VERSION = "2.1.0"

PRIORITIES = ("Critical", "High", "Medium", "Low")
PRIORITY_RANK = {name.lower(): index for index, name in enumerate(PRIORITIES)}
DEFAULT_PRIORITY = "Medium"

# The roadmap carries three markers. `review` is in flight, so it reads as in progress; `done`
# never reaches a row, because a finished ticket leaves the file.
STATUS_MARKER = {
    "backlog": "⬜ **Pending**",
    "in progress": "🚧 **In Progress**",
    "blocked": "🚫 **Blocked**",
    "review": "🚧 **In Progress**",
}
DONE = "done"
STATUSES = (*STATUS_MARKER, DONE)
OLDER_STATUS = {"not started": "backlog", "completed": DONE}

# A ticket's status is the record, and its bucket follows from it.
BUCKET_OF_STATUS = {
    "backlog": "backlog",
    "in progress": "in-progress",
    "blocked": "in-progress",
    "review": "in-progress",
    DONE: "done",
}
STATUS_OF_BUCKET = {"backlog": "backlog", "in-progress": "in progress", "done": DONE}
OLDER_BUCKET = {"todo": "backlog"}

TICKET_NAME = re.compile(r"^([A-Z][A-Z0-9]{1,7})-(\d{1,4})-(.+)\.md$")
TITLE_LINE = re.compile(r"^#\s*\[([A-Z][A-Z0-9]{1,7}-\d{1,4})\]\s*(.+?)\s*$")
BODY_FIELD = re.compile(r"^\*\*(.+?)\*\*:\s*(.*?)\s*$")
SECTION_HEADING = re.compile(r"^##\s+(.+?)\s*$")
EPIC_HEADING = re.compile(r"^##\s+([A-Z][A-Z0-9]{1,7})\s+—\s+(.+?)\s*$")
LAST_UPDATED = re.compile(r"^\*\*Last updated\*\*:\s*(.*?)\s*$")
UPDATED_PROPERTY = re.compile(r"^updated:\s*(.*?)\s*$")
ID_IN_TEXT = re.compile(r"\b([A-Z][A-Z0-9]{1,7}-\d{1,4})\b")

EMPTY_CELL = "—"


# ------------------------------------------------------------------------------------ reporting


class Report:
    """Everything the run found, printed once at the end."""

    def __init__(self, quiet: bool = False) -> None:
        self.quiet = quiet
        self.notes: list[str] = []
        self.problems: list[str] = []

    def note(self, message: str) -> None:
        if message not in self.notes:
            self.notes.append(message)

    def problem(self, message: str) -> None:
        if message not in self.problems:
            self.problems.append(message)

    def say(self, message: str = "") -> None:
        if not self.quiet:
            print(message)


# ------------------------------------------------------------------------------------ the ticket


@dataclass
class Ticket:
    ticket_id: str
    code: str
    number: int
    title: str
    path: Path
    status: str
    priority: str
    depends_on: list[str]
    epic_name: str = ""
    priority_assumed: bool = False
    folder: str = ""
    feature_ref: str = ""
    feature: "Feature | None" = None

    @property
    def stem(self) -> str:
        return self.path.stem

    @property
    def is_done(self) -> bool:
        return self.status == DONE

    @property
    def rank(self) -> int:
        return PRIORITY_RANK.get(self.priority.lower(), PRIORITY_RANK[DEFAULT_PRIORITY.lower()])

    @property
    def marker(self) -> str:
        return STATUS_MARKER.get(self.status, STATUS_MARKER["backlog"])


@dataclass
class Feature:
    stem: str
    path: Path
    name: str
    code: str
    projects: list[str]
    summary: str


# ------------------------------------------------------------------------------------ parsing


def split_frontmatter(text: str) -> tuple[dict[str, object], list[str]]:
    """Return (properties, body lines). Only the small YAML subset these documents use."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, lines

    closing = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            closing = index
            break
    if closing is None:
        return {}, lines

    properties: dict[str, object] = {}
    key = None
    for raw in lines[1:closing]:
        if not raw.strip():
            continue
        if raw.lstrip().startswith("- ") and key:
            item = _clean_scalar(raw.lstrip()[2:])
            bucket = properties.setdefault(key, [])
            if isinstance(bucket, list):
                bucket.append(item)
            continue
        if ":" not in raw:
            continue
        name, _, value = raw.partition(":")
        key = name.strip()
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            properties[key] = [_clean_scalar(p) for p in inner.split(",") if p.strip()] if inner else []
        elif value:
            properties[key] = _clean_scalar(value)
        else:
            properties[key] = []
    return properties, lines[closing + 1 :]


def _clean_scalar(value: str) -> str:
    value = value.strip()
    for quote in ('"', "'"):
        if len(value) >= 2 and value.startswith(quote) and value.endswith(quote):
            value = value[1:-1]
            break
    return value.strip()


def link_target(value: object) -> str:
    """The note name a wikilink or a relative path points at: `[[checkout.feature]]` and
    `../../features/checkout/checkout.feature.md` both give `checkout.feature`."""
    text = str(value or "").strip()
    if text.startswith("[[") and text.endswith("]]"):
        text = text[2:-2]
    text = text.split("|", 1)[0].split("#", 1)[0].strip()
    name = text.replace("\\", "/").rsplit("/", 1)[-1]
    return name[:-3] if name.endswith(".md") else name


def as_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if value is None or not str(value).strip():
        return []
    return [str(value)]


def body_fields(lines: list[str]) -> dict[str, str]:
    """The `**Field**: value` lines above the first `##` heading."""
    fields: dict[str, str] = {}
    for raw in lines:
        if raw.startswith("## "):
            break
        match = BODY_FIELD.match(raw.rstrip())
        if match:
            fields[match.group(1).strip().lower()] = match.group(2).strip()
    return fields


def parse_ids(value: object) -> list[str]:
    """IDs out of a frontmatter list, an inline list, or a comma-separated field."""
    if value is None:
        return []
    items: list[str] = []
    if isinstance(value, list):
        for entry in value:
            items.extend(ID_IN_TEXT.findall(str(entry)))
    else:
        text = str(value).strip()
        if text and text not in {EMPTY_CELL, "-", "--", "none", "None"}:
            items.extend(ID_IN_TEXT.findall(text))
    ordered: list[str] = []
    for item in items:
        if item not in ordered:
            ordered.append(item)
    return ordered


def read_ticket(path: Path, report: Report) -> Ticket | None:
    name_match = TICKET_NAME.match(path.name)
    if not name_match:
        return None

    code, number, slug = name_match.group(1), int(name_match.group(2)), name_match.group(3)
    ticket_id = f"{code}-{name_match.group(2)}"

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        report.problem(f"{path.name}: cannot read it ({error.strerror})")
        return None

    properties, body = split_frontmatter(text)
    fields = body_fields(body)

    def value_of(key: str) -> str:
        found = properties.get(key)
        if isinstance(found, str) and found.strip():
            return found.strip()
        return fields.get(key.replace("_", " "), "").strip()

    title = ""
    for raw in body:
        title_match = TITLE_LINE.match(raw.rstrip())
        if title_match:
            title = title_match.group(2).strip()
            break
    if not title:
        title = slug.replace("-", " ").strip().capitalize()
        report.note(f"{ticket_id}: no title line, so the row takes its title from the file name")

    folder = path.parent.name
    bucket = OLDER_BUCKET.get(folder, folder)
    from_bucket = STATUS_OF_BUCKET.get(bucket, "backlog")
    written = value_of("status")
    status = OLDER_STATUS.get(written.lower(), written.lower())
    if not written:
        status = from_bucket
        report.note(f"{ticket_id}: no status property, so it reads as {status!r} from its folder")
    elif status not in STATUSES:
        report.problem(
            f"{ticket_id}: status {written!r} is not one the board uses — read as {from_bucket!r} "
            "from its folder"
        )
        status = from_bucket
    elif bucket in STATUS_OF_BUCKET and BUCKET_OF_STATUS[status] != bucket:
        report.problem(
            f"{ticket_id}: its status is {status!r} but it sits in {folder}/ — the status wins, "
            f"and the file belongs in {BUCKET_OF_STATUS[status]}/"
        )

    priority = value_of("priority")
    assumed = False
    if priority.lower() not in PRIORITY_RANK:
        # An unfilled template placeholder (`Critical | High | Medium | Low`) lands here too.
        priority = DEFAULT_PRIORITY
        assumed = True
    else:
        priority = PRIORITIES[PRIORITY_RANK[priority.lower()]]

    depends_on = parse_ids(properties.get("depends_on", fields.get("depends on", "")))
    if ticket_id in depends_on:
        report.problem(f"{ticket_id}: depends on itself — that entry is ignored")
        depends_on = [dep for dep in depends_on if dep != ticket_id]

    return Ticket(
        ticket_id=ticket_id,
        code=code,
        number=number,
        title=title,
        path=path,
        status=status,
        priority=priority,
        depends_on=depends_on,
        epic_name=value_of("epic"),
        priority_assumed=assumed,
        folder=folder,
        feature_ref=link_target(properties.get("feature", fields.get("feature", ""))),
    )


def collect_tickets(tickets_dir: Path, report: Report) -> dict[str, Ticket]:
    tickets: dict[str, Ticket] = {}
    for path in sorted(tickets_dir.rglob("*.md")):
        if path.name.endswith(".worklog.md") or path.name == "TEMPLATE.md":
            continue
        ticket = read_ticket(path, report)
        if ticket is None:
            continue
        existing = tickets.get(ticket.ticket_id)
        if existing:
            report.problem(
                f"{ticket.ticket_id}: two files carry this ID — {existing.path.name} and "
                f"{ticket.path.name}. Using the first; the other needs a new number"
            )
            continue
        tickets[ticket.ticket_id] = ticket
    return tickets


def collect_features(root: Path, report: Report) -> tuple[dict[str, Feature], dict[str, Feature]]:
    """Every feature note under `features/`, by note name and by code."""
    by_stem: dict[str, Feature] = {}
    by_code: dict[str, Feature] = {}
    folder = root / "features"
    if not folder.is_dir():
        return by_stem, by_code
    for path in sorted(folder.glob("*/*.feature.md")):
        try:
            properties, body = split_frontmatter(path.read_text(encoding="utf-8"))
        except OSError as error:
            report.problem(f"{path.name}: cannot read it ({error.strerror})")
            continue
        if str(properties.get("type", "")).strip() != "feature":
            report.note(f"{path.name}: its type is not `feature`, so it is not read as a feature note")
            continue
        stem = path.name[: -len(".md")]
        code = str(properties.get("code", "")).strip()
        title = next((line[2:].strip() for line in body if line.startswith("# ")), "")
        summary = next(
            (
                line.strip()
                for line in body
                if line.strip() and not line.lstrip().startswith(("#", "-", "*", "|", ">"))
            ),
            "",
        )
        feature = Feature(
            stem=stem,
            path=path,
            name=str(properties.get("name", "")).strip() or title or stem,
            code=code,
            projects=[link_target(entry) for entry in as_list(properties.get("projects"))],
            summary=summary,
        )
        by_stem[stem] = feature
        if code:
            if code in by_code:
                report.problem(
                    f"{code}: two feature notes carry this code — {by_code[code].path.name} and "
                    f"{path.name}. A code means one feature"
                )
            else:
                by_code[code] = feature
    return by_stem, by_code


def attach_features(
    tickets: dict[str, Ticket],
    by_stem: dict[str, Feature],
    by_code: dict[str, Feature],
    report: Report,
) -> None:
    """Point each ticket at the feature it delivers: its `feature` property, else its code."""
    for ticket in tickets.values():
        feature = None
        if ticket.feature_ref:
            feature = by_stem.get(ticket.feature_ref)
            if feature is None:
                report.problem(
                    f"{ticket.ticket_id}: its feature property points at {ticket.feature_ref}, "
                    "and no feature note has that name"
                )
            elif feature.code and feature.code != ticket.code:
                report.problem(
                    f"{ticket.ticket_id}: its feature property names {feature.stem}, whose code is "
                    f"{feature.code} — a ticket whose feature and name disagree is not valid"
                )
        if feature is None:
            feature = by_code.get(ticket.code)
        ticket.feature = feature


# ------------------------------------------------------------------------------------ ordering


def outstanding(ticket: Ticket, tickets: dict[str, Ticket], report: Report) -> list[str]:
    """The blockers that are not finished yet, in the ticket's own order."""
    blockers = []
    for dep in ticket.depends_on:
        other = tickets.get(dep)
        if other is None:
            report.problem(
                f"{ticket.ticket_id}: depends on {dep}, and no ticket carries that ID — "
                "it reads as unfinished, so the task stays blocked"
            )
            blockers.append(dep)
        elif not other.is_done:
            blockers.append(dep)
    return blockers


def carried_ranks(
    open_tickets: list[Ticket], waiting_for: dict[str, set[str]]
) -> dict[str, int]:
    """A blocker carries the highest priority of anything waiting on it.

    The fastest way to reach urgent work is through whatever blocks it, so a Low chore that holds
    up a Critical task is built at the Critical task's urgency. Without this, the chore sorts below
    unrelated middling work and the urgent task waits behind all of it.
    """
    carried = {ticket.ticket_id: ticket.rank for ticket in open_tickets}
    for _ in range(len(carried)):
        settled = True
        for ticket_id, blockers in waiting_for.items():
            for blocker in blockers:
                if carried[ticket_id] < carried[blocker]:
                    carried[blocker] = carried[ticket_id]
                    settled = False
        if settled:
            break
    return carried


def sort_epic(open_tickets: list[Ticket], blockers: dict[str, list[str]], report: Report) -> list[Ticket]:
    """Priority order, with a dependency inside the epic always winning over priority."""
    ids = {ticket.ticket_id for ticket in open_tickets}
    waiting_for = {
        ticket.ticket_id: {dep for dep in blockers[ticket.ticket_id] if dep in ids}
        for ticket in open_tickets
    }
    by_id = {ticket.ticket_id: ticket for ticket in open_tickets}
    carried = carried_ranks(open_tickets, waiting_for)

    def key(ticket_id: str) -> tuple[int, int, int]:
        ticket = by_id[ticket_id]
        return (carried[ticket_id], ticket.rank, ticket.number)

    ordered: list[Ticket] = []
    remaining = set(waiting_for)
    while remaining:
        ready = sorted((tid for tid in remaining if not (waiting_for[tid] & remaining)), key=key)
        if not ready:
            cycle = sorted(remaining, key=key)
            report.problem(
                "these tasks depend on each other in a circle, so no order satisfies them: "
                + ", ".join(cycle)
                + ". They are written in priority order, and somebody has to break the circle"
            )
            ordered.extend(by_id[tid] for tid in cycle)
            break
        chosen = ready[0]
        remaining.discard(chosen)
        ordered.append(by_id[chosen])
    return ordered


# ------------------------------------------------------------------------------------ the table


def render_table(rows: list[tuple[Ticket, list[str]]], vault: bool) -> list[str]:
    lines = [
        "| ID | Task | Priority | Status | Depends on | Ticket |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for ticket, blockers in rows:
        cell = ", ".join(blockers) if blockers else EMPTY_CELL
        citation = f"[[{ticket.stem}]]" if vault else f"`{ticket.path.name}`"
        lines.append(
            f"| {ticket.ticket_id} | {ticket.title} | {ticket.priority} | {ticket.marker} "
            f"| {cell} | {citation} |"
        )
    return lines


# ------------------------------------------------------------------------------------ the file


@dataclass
class Section:
    heading: str
    code: str
    name: str
    lines: list[str] = field(default_factory=list)


@dataclass
class Roadmap:
    path: Path
    head: list[str]
    sections: list[Section]
    vault: bool

    def render(self) -> str:
        out = list(self.head)
        for section in self.sections:
            if out and out[-1].strip():
                out.append("")
            out.append(section.heading)
            out.extend(section.lines)
        text = "\n".join(out).rstrip("\n") + "\n"
        return re.sub(r"\n{3,}", "\n\n", text)


def load_roadmap(path: Path, style: str) -> Roadmap:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    head: list[str] = []
    sections: list[Section] = []
    current: Section | None = None
    for raw in lines:
        heading = SECTION_HEADING.match(raw)
        if heading:
            epic = EPIC_HEADING.match(raw)
            code = epic.group(1) if epic else ""
            name = epic.group(2) if epic else heading.group(1)
            current = Section(heading=raw.rstrip(), code=code, name=name)
            sections.append(current)
            continue
        if current is None:
            head.append(raw)
        else:
            current.lines.append(raw)

    if style == "vault":
        vault = True
    elif style == "repo":
        vault = False
    else:
        vault = "[[" in text or _looks_like_vault(path)
    return Roadmap(path=path, head=head, sections=sections, vault=vault)


def existing_cells(roadmap: Roadmap) -> dict[str, list[str]]:
    """The `Depends on` IDs each row names today, read by column name.

    An older table has no `Priority` column, and an older ticket has no `Depends on` field while its
    row still names blockers. Reading what is there is what keeps a rebuild from deleting a
    dependency graph that lives nowhere else yet.
    """
    found: dict[str, list[str]] = {}
    for section in roadmap.sections:
        id_at = depends_at = None
        for raw in section.lines:
            line = raw.strip()
            if not line.startswith("|"):
                continue
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if id_at is None:
                headers = [cell.lower() for cell in cells]
                if "id" in headers:
                    id_at = headers.index("id")
                    depends_at = headers.index("depends on") if "depends on" in headers else None
                continue
            if all(set(cell) <= {"-", ":", " "} for cell in cells if cell):
                continue
            if depends_at is None or id_at >= len(cells) or depends_at >= len(cells):
                continue
            row_id = ID_IN_TEXT.findall(cells[id_at])
            if row_id:
                found[row_id[0]] = parse_ids(cells[depends_at])
    return found


def _looks_like_vault(path: Path) -> bool:
    for parent in [path.parent, *path.parent.parents]:
        if (parent / ".obsidian").is_dir():
            return True
    return False


def replace_table(section: Section, table: list[str]) -> None:
    """Swap the section's table for a new one, keeping every other line where it is.

    An empty table means the epic has no work left. The rows go, and the prose stays — closing the
    section needs a check on the feature that nothing here can make.
    """
    kept: list[str] = []
    table_at = None
    for raw in section.lines:
        if raw.lstrip().startswith("|"):
            if table_at is None:
                table_at = len(kept)
            continue
        kept.append(raw)
    if not table:
        section.lines = kept
        return
    if table_at is None:
        while kept and not kept[-1].strip():
            kept.pop()
        section.lines = kept + [""] + table + [""]
        return
    section.lines = kept[:table_at] + [""] + table + [""] + kept[table_at:]


def bump_last_updated(roadmap: Roadmap, today: str) -> None:
    for index, raw in enumerate(roadmap.head):
        if LAST_UPDATED.match(raw):
            roadmap.head[index] = f"**Last updated**: {today}"
            return
    for index, raw in enumerate(roadmap.head):
        if UPDATED_PROPERTY.match(raw):
            roadmap.head[index] = f"updated: {today}"
            return


# ------------------------------------------------------------------------------------ the board


class BoardError(Exception):
    """Something that stops the run before any roadmap is read."""


@dataclass
class Project:
    folder: Path
    names: set[str]
    status: str = ""

    @property
    def label(self) -> str:
        return self.folder.name


@dataclass
class Board:
    root: Path
    projects: list[Project]
    has_projects: bool


def find_framework_root(start: Path) -> Path | None:
    """The first folder, from `start` up to the home directory, that is a framework root."""
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


def find_repository_root(start: Path) -> Path | None:
    for folder in [start, *start.parents]:
        if any((folder / marker).exists() for marker in (".git", "package.json", "AGENTS.md", "CLAUDE.md")):
            return folder
    return None


def _pointer_target(pointer: Path) -> Path | None:
    # A tiny JSON read, so a malformed pointer file cannot stop the run.
    try:
        import json

        data = json.loads(pointer.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    value = data.get("root") if isinstance(data, dict) else None
    if not value:
        return None
    root = Path(str(value)).expanduser()
    if not root.is_absolute():
        root = pointer.parent / root
    root = root.resolve()
    return root if root.is_dir() else None


def find_from_working_directory() -> tuple[Path | None, Path | None]:
    """(framework root, the folder a pointer file named), from where the script runs."""
    here = Path.cwd().resolve()
    root = find_framework_root(here)
    if root:
        return root, None

    repository = find_repository_root(here)
    if repository:
        pointer = repository / ".sdlc.json"
        if pointer.is_file():
            target = _pointer_target(pointer)
            if target:
                return find_framework_root(target) or target, target
        if (repository / ".sdlc").is_dir():
            return repository / ".sdlc", None

    # An older board: a folder holding the roadmap beside its tickets, with nothing above it.
    for folder in [here, *here.parents]:
        if (folder / "roadmap.md").is_file() and ((folder / "tickets").is_dir() or (folder / "work").is_dir()):
            return folder, None
        if (folder / ".git").exists():
            break
    return None, None


def _looks_like_path(value: str) -> bool:
    return "/" in value or "\\" in value or value.startswith(("~", "."))


def make_project(folder: Path) -> Project:
    """A project answers to the `name` in its project note. A folder with no project note — an
    older shape — answers to its folder name instead."""
    note = folder / f"{folder.name}.md"
    properties: dict[str, object] = {}
    if note.is_file():
        try:
            properties, _ = split_frontmatter(note.read_text(encoding="utf-8"))
        except OSError:
            properties = {}
    if str(properties.get("type", "")).strip() != "project":
        return Project(folder=folder, names={folder.name})
    name = str(properties.get("name", "")).strip()
    status = str(properties.get("status", "")).strip().lower()
    return Project(folder=folder, names={name} if name else {folder.name}, status=status)


def locate_board(args: argparse.Namespace) -> Board:
    named_folder: Path | None = None
    if args.root:
        root = Path(args.root).expanduser().resolve()
        if not root.is_dir():
            raise BoardError(f"No folder at {root}")
    elif args.project and (
        _looks_like_path(args.project)
        or (not find_from_working_directory()[0] and Path(args.project).expanduser().is_dir())
    ):
        named_folder = Path(args.project).expanduser().resolve()
        if not named_folder.is_dir():
            raise BoardError(f"No folder at {named_folder}")
        root = find_framework_root(named_folder) or named_folder
    else:
        root, pointed = find_from_working_directory()
        if not args.project:
            named_folder = pointed
        if root is None:
            raise BoardError(
                "No framework root found. Pass --root or --project, or run this from the framework "
                "root or a repository whose .sdlc.json points at it.\nThe setup command creates it."
            )

    projects_dir = root / "projects"
    has_projects = projects_dir.is_dir()

    if args.project and not _looks_like_path(args.project) and named_folder is None:
        matches = [
            project
            for project in (
                make_project(candidate)
                for candidate in (sorted(projects_dir.iterdir()) if has_projects else [])
                if candidate.is_dir()
            )
            if args.project in project.names
        ]
        if not matches:
            raise BoardError(f"No project named {args.project!r} under {projects_dir}")
        projects = matches[:1]
    elif named_folder is not None and named_folder != root:
        projects = [make_project(named_folder)]
    elif has_projects:
        # A done project is left out unless it is named.
        projects = [
            project
            for project in (
                make_project(folder)
                for folder in sorted(projects_dir.iterdir())
                if folder.is_dir() and (folder / "roadmap.md").is_file()
            )
            if project.status != "done"
        ]
        if not projects:
            raise BoardError(f"No project under {projects_dir} that is not done has a roadmap.md yet")
    else:
        projects = [make_project(root)]

    if args.roadmap and len(projects) > 1:
        raise BoardError("--roadmap names one roadmap; pass --project too, to say whose it is")
    return Board(root=root, projects=projects, has_projects=has_projects)


def ticket_folder(board: Board, project: Project) -> tuple[Path | None, bool]:
    """Where the tickets are, and whether they are shared by every project of the framework root."""
    if (board.root / "work").is_dir():
        return board.root / "work", True
    if project.folder != board.root and (project.folder / "tickets").is_dir():
        return project.folder / "tickets", False
    if (board.root / "tickets").is_dir():
        return board.root / "tickets", True
    return None, False


def belongs_to(ticket: Ticket, project: Project, report: Report) -> bool:
    feature = ticket.feature
    if feature is None:
        report.problem(
            f"{ticket.ticket_id}: no feature note carries the code {ticket.code}, so the ticket "
            "is on no project's roadmap"
        )
        return False
    if not feature.projects:
        report.problem(
            f"{feature.path.name}: its projects property is empty, so none of its tickets is on a "
            "roadmap"
        )
        return False
    return bool(project.names & set(feature.projects))


# ------------------------------------------------------------------------------------ the run


def new_section(code: str, feature: Feature | None, fallback_name: str, roadmap: Roadmap) -> Section:
    name = (feature.name if feature else "") or fallback_name or code
    name = name.split("—")[-1].strip() if "—" in name else name
    section = Section(heading=f"## {code} — {name}", code=code, name=name)
    section.lines = [""]
    if feature:
        if roadmap.vault:
            link = f"[[{feature.stem}]]"
        else:
            link = os.path.relpath(feature.path, roadmap.path.parent).replace(os.sep, "/")
        section.lines += [f"**Feature**: {link}", ""]
    section.lines += [(feature.summary if feature and feature.summary else "<One sentence: what this epic delivers.>"), ""]
    return section


def rebuild(board: Board, project: Project, args: argparse.Namespace, report: Report) -> int:
    """Rebuild one project's roadmap. 0 nothing to fix, 1 it differs (--check), 2 it stopped."""
    roadmap_path = Path(args.roadmap).expanduser() if args.roadmap else project.folder / "roadmap.md"
    if not roadmap_path.is_file():
        print(f"No roadmap at {roadmap_path}", file=sys.stderr)
        return 2

    folder, shared = ticket_folder(board, project)
    if folder is None:
        print(f"No work/ or tickets/ folder under {board.root}", file=sys.stderr)
        return 2

    every_ticket = collect_tickets(folder, report)
    by_stem, by_code = collect_features(board.root, report)
    attach_features(every_ticket, by_stem, by_code, report)

    # Every project's tickets share one board, so a roadmap lists only its own project's tickets.
    # Dependencies still resolve against the whole board: a ticket may wait on another project's.
    if shared and board.has_projects:
        tickets = {tid: t for tid, t in every_ticket.items() if belongs_to(t, project, report)}
    else:
        tickets = every_ticket
    if not tickets:
        print(f"No tickets of {project.label} under {folder}", file=sys.stderr)
        return 2

    roadmap = load_roadmap(roadmap_path, args.style)
    before = roadmap.render()
    cells_now = existing_cells(roadmap)

    blockers = {
        ticket.ticket_id: outstanding(ticket, every_ticket, report)
        for ticket in tickets.values()
        if not ticket.is_done
    }

    # A row may name a blocker its ticket does not. That happens on a board written before the
    # ticket carried the property, and the roadmap is then the only copy of the graph. Keep those
    # IDs in the cell, and say so, rather than dropping work nobody recorded twice.
    for ticket_id, blocking in blockers.items():
        ticket = tickets[ticket_id]
        unrecorded = [
            dep
            for dep in cells_now.get(ticket_id, [])
            if dep not in ticket.depends_on
            and dep not in blocking
            and not (every_ticket.get(dep) and every_ticket[dep].is_done)
        ]
        if unrecorded:
            blocking.extend(unrecorded)
            report.problem(
                f"{ticket_id}: its row names {', '.join(unrecorded)} and its ticket does not. "
                "The row keeps them, and somebody has to copy them into the ticket's depends_on "
                "property — the roadmap is the only copy"
            )

    open_by_code: dict[str, list[Ticket]] = {}
    for ticket in tickets.values():
        if not ticket.is_done:
            open_by_code.setdefault(ticket.code, []).append(ticket)

    sections_by_code = {section.code: section for section in roadmap.sections if section.code}

    for code, open_tickets in sorted(open_by_code.items()):
        ordered = sort_epic(open_tickets, blockers, report)
        rows = [(ticket, blockers[ticket.ticket_id]) for ticket in ordered]
        table = render_table(rows, roadmap.vault)

        section = sections_by_code.get(code)
        if section is None:
            feature = next((t.feature for t in ordered if t.feature), None)
            fallback = next((t.epic_name for t in ordered if t.epic_name), "")
            section = new_section(code, feature, fallback, roadmap)
            roadmap.sections.append(section)
            sections_by_code[code] = section
            if feature and feature.summary:
                report.note(f"{code}: no section in {project.label}'s roadmap, so one was added")
            else:
                report.note(
                    f"{code}: no section in {project.label}'s roadmap, so one was added. Its "
                    "sentence still needs writing"
                )
        replace_table(section, table)

    for section in roadmap.sections:
        if section.code and section.code not in open_by_code:
            had_rows = any(line.lstrip().startswith("|") for line in section.lines)
            replace_table(section, [])
            if had_rows:
                report.note(
                    f"{section.code}: every ticket in this epic is finished, so its rows are gone. "
                    "Closing the section and setting the feature to done needs a check nothing "
                    "here can make"
                )

    for ticket in tickets.values():
        if ticket.priority_assumed and not ticket.is_done:
            report.note(f"{ticket.ticket_id}: no priority in the ticket, so the row reads Medium")

    after_body = roadmap.render()
    changed = after_body != before
    if changed:
        bump_last_updated(roadmap, args.today or _datetime.date.today().isoformat())
    after = roadmap.render()
    changed = after != before

    rows_total = sum(len(v) for v in open_by_code.values())
    summary = (
        f"{rows_total} open {_plural(rows_total, 'ticket')} "
        f"across {len(open_by_code)} {_plural(len(open_by_code), 'epic')}."
    )

    if args.check:
        report.say(f"Roadmap: {roadmap_path}")
        report.say(
            "The tables match the tickets." if not changed else "The tables do not match the tickets."
        )
        if changed:
            import difflib

            report.say("")
            for line in difflib.unified_diff(
                before.splitlines(),
                after.splitlines(),
                fromfile="roadmap.md (now)",
                tofile="roadmap.md (from the tickets)",
                lineterm="",
                n=1,
            ):
                report.say(line)
        report.say(summary)
        return 1 if changed else 0

    if changed:
        roadmap_path.write_text(after, encoding="utf-8")
        report.say(f"Rebuilt the tables in {roadmap_path}")
    else:
        report.say(f"Nothing to change in {roadmap_path}")
    report.say(summary)
    return 0


def build(args: argparse.Namespace) -> int:
    report = Report(quiet=args.quiet)
    try:
        board = locate_board(args)
    except BoardError as error:
        print(error, file=sys.stderr)
        return 2

    results = []
    for index, project in enumerate(board.projects):
        if index:
            report.say("")
        results.append(rebuild(board, project, args, report))

    _print_findings(report)
    if 2 in results:
        return 2
    if 1 in results:
        return 1
    return 2 if report.problems and args.strict else 0


def _plural(count: int, word: str) -> str:
    return word if count == 1 else word + "s"


def _print_findings(report: Report) -> None:
    if report.problems:
        report.say("")
        report.say("Problems somebody has to fix:")
        for line in report.problems:
            report.say(f"  - {line}")
    if report.notes:
        report.say("")
        report.say("Worth knowing:")
        for line in report.notes:
            report.say(f"  - {line}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="build-roadmap.py",
        description="Rebuild the roadmap's tables from the tickets.",
    )
    parser.add_argument(
        "--project",
        help="one project to rebuild, by its name or its folder; every project when left out",
    )
    parser.add_argument("--root", help="the framework root, when it cannot be found from here")
    parser.add_argument("--roadmap", help="a roadmap path, when it is not <project>/roadmap.md")
    parser.add_argument(
        "--check",
        action="store_true",
        help="report what differs and write nothing; exit 1 when the roadmap differs",
    )
    parser.add_argument(
        "--style",
        choices=("auto", "vault", "repo"),
        default="auto",
        help="how a ticket is cited: a wikilink in a vault, a file name in a repository",
    )
    parser.add_argument("--strict", action="store_true", help="exit 2 when anything needs a person")
    parser.add_argument("--today", help="the date to write into the roadmap's updated date (YYYY-MM-DD)")
    parser.add_argument("-q", "--quiet", action="store_true", help="print only errors")
    parser.add_argument("--version", action="version", version=f"build-roadmap.py {VERSION}")
    args = parser.parse_args(argv)

    try:
        return build(args)
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
