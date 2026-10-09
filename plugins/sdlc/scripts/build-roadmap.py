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
#   ./build-roadmap.py                      # rebuild the tables in place
#   ./build-roadmap.py --check              # report drift, write nothing (exit 1 when it differs)
#   ./build-roadmap.py --project ~/Vaults/Personal/Acme
#
# Run it from the repository that holds the project, or from the project itself — in an Obsidian
# vault, holding the roadmap and the tickets. The script finds the project the way every command
# does: the `root` in a `.sdlc.json` pointer file, else a `.sdlc/` folder, else the working
# directory when it holds `roadmap.md` and `tickets/`.
#
# What it never does: invent a task, rewrite a ticket, delete an epic's section, or decide that a
# feature has shipped. Those need a person or a command. This script writes table rows and the
# `Last updated` field, and reports everything else it found.
#
# Exit codes: 0 nothing to fix, 1 the roadmap differs from the tickets (--check only), 2 an error
# that stopped the rebuild.

from __future__ import annotations

import argparse
import datetime as _datetime
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

VERSION = "1.0.0"

PRIORITIES = ("Critical", "High", "Medium", "Low")
PRIORITY_RANK = {name.lower(): index for index, name in enumerate(PRIORITIES)}
DEFAULT_PRIORITY = "Medium"

# The roadmap carries three markers. `Review` is in flight, so it reads as in progress; `Completed`
# never reaches a row, because a finished task leaves the file.
STATUS_MARKER = {
    "not started": "⬜ **Pending**",
    "in progress": "🚧 **In Progress**",
    "blocked": "🚫 **Blocked**",
    "review": "🚧 **In Progress**",
}
COMPLETED = "completed"

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
        self.notes.append(message)

    def problem(self, message: str) -> None:
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

    @property
    def stem(self) -> str:
        return self.path.stem

    @property
    def is_done(self) -> bool:
        return self.status.lower() == COMPLETED

    @property
    def rank(self) -> int:
        return PRIORITY_RANK.get(self.priority.lower(), PRIORITY_RANK[DEFAULT_PRIORITY.lower()])

    @property
    def marker(self) -> str:
        return STATUS_MARKER.get(self.status.lower(), STATUS_MARKER["not started"])


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
    status = value_of("status")
    if folder == "done":
        if status and status.lower() != COMPLETED:
            report.problem(
                f"{ticket_id}: sits in done/ but its status says {status!r} — the folder wins, "
                "and somebody has to fix the ticket"
            )
        status = "Completed"
    if not status:
        status = "Not Started"
        report.note(f"{ticket_id}: no status field, so it reads as Not Started")
    elif status.lower() not in STATUS_MARKER and status.lower() != COMPLETED:
        report.problem(f"{ticket_id}: status {status!r} is not one the board uses — read as Not Started")
        status = "Not Started"

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


# ------------------------------------------------------------------------------------ the project


def find_project_dir(given: str | None) -> Path | None:
    if given:
        root = Path(given).expanduser().resolve()
        return root if root.is_dir() else None

    here = Path.cwd().resolve()
    for parent in [here, *here.parents]:
        pointer = parent / ".sdlc.json"
        if pointer.is_file():
            root = _project_dir_from_pointer(pointer)
            if root:
                return root
        candidate = parent / ".sdlc"
        if (candidate / "roadmap.md").is_file():
            return candidate
        if (parent / "roadmap.md").is_file() and (parent / "tickets").is_dir():
            return parent
        if (parent / ".git").exists():
            break
    return None


def _project_dir_from_pointer(pointer: Path) -> Path | None:
    # A tiny JSON read, so a malformed pointer file cannot stop the run.
    try:
        import json

        data = json.loads(pointer.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    value = data.get("root")
    if not value:
        return None
    root = Path(str(value)).expanduser()
    if not root.is_absolute():
        root = (pointer.parent / root).resolve()
    return root if root.is_dir() else None


# ------------------------------------------------------------------------------------ the run


def build(args: argparse.Namespace) -> int:
    report = Report(quiet=args.quiet)

    project_dir = find_project_dir(args.project)
    if project_dir is None:
        print(
            "No project found. Pass --project, or run this from a repository that has one.\n"
            "The setup command creates it.",
            file=sys.stderr,
        )
        return 2

    roadmap_path = Path(args.roadmap).expanduser() if args.roadmap else project_dir / "roadmap.md"
    tickets_dir = project_dir / "tickets"
    if not roadmap_path.is_file():
        print(f"No roadmap at {roadmap_path}", file=sys.stderr)
        return 2
    if not tickets_dir.is_dir():
        print(f"No tickets folder at {tickets_dir}", file=sys.stderr)
        return 2

    tickets = collect_tickets(tickets_dir, report)
    if not tickets:
        print(f"No tickets found under {tickets_dir}", file=sys.stderr)
        return 2

    roadmap = load_roadmap(roadmap_path, args.style)
    before = roadmap.render()
    cells_now = existing_cells(roadmap)

    blockers = {
        ticket.ticket_id: outstanding(ticket, tickets, report)
        for ticket in tickets.values()
        if not ticket.is_done
    }

    # A row may name a blocker its ticket does not. That happens on a board written before the
    # ticket carried the field, and the roadmap is then the only copy of the graph. Keep those IDs
    # in the cell, and say so, rather than dropping work nobody recorded twice.
    for ticket_id, blocking in blockers.items():
        ticket = tickets[ticket_id]
        unrecorded = [
            dep
            for dep in cells_now.get(ticket_id, [])
            if dep not in ticket.depends_on
            and dep not in blocking
            and not (tickets.get(dep) and tickets[dep].is_done)
        ]
        if unrecorded:
            blocking.extend(unrecorded)
            report.problem(
                f"{ticket_id}: its row names {', '.join(unrecorded)} and its ticket does not. "
                "The row keeps them, and somebody has to copy them into the ticket's Depends on "
                "field — the roadmap is the only copy"
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
            name = next((t.epic_name for t in ordered if t.epic_name), "") or code
            name = name.split("—")[-1].strip() if "—" in name else name
            section = Section(heading=f"## {code} — {name}", code=code, name=name)
            section.lines = ["", "<One sentence: what this epic delivers.>", ""]
            roadmap.sections.append(section)
            sections_by_code[code] = section
            report.note(
                f"{code}: no section in the roadmap, so one was added. Its sentence and its "
                "feature link still need writing"
            )
        replace_table(section, table)

    for section in roadmap.sections:
        if section.code and section.code not in open_by_code:
            had_rows = any(line.lstrip().startswith("|") for line in section.lines)
            replace_table(section, [])
            if had_rows:
                report.note(
                    f"{section.code}: every ticket in this epic is finished, so its rows are gone. "
                    "Closing the section and marking the feature shipped needs a check nothing "
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
        _print_findings(report)
        if changed:
            return 1
        return 2 if report.problems and args.strict else 0

    if changed:
        roadmap_path.write_text(after, encoding="utf-8")
        report.say(f"Rebuilt the tables in {roadmap_path}")
    else:
        report.say(f"Nothing to change in {roadmap_path}")

    rows_total = sum(len(v) for v in open_by_code.values())
    report.say(
        f"{rows_total} open {_plural(rows_total, 'task')} "
        f"across {len(open_by_code)} {_plural(len(open_by_code), 'epic')}."
    )
    _print_findings(report)
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
    parser.add_argument("--project", help="the project holding roadmap.md and tickets/")
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
    parser.add_argument("--today", help="the date to write into Last updated (YYYY-MM-DD)")
    parser.add_argument("-q", "--quiet", action="store_true", help="print only errors")
    parser.add_argument("--version", action="version", version=f"build-roadmap.py {VERSION}")
    args = parser.parse_args(argv)

    try:
        return build(args)
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
