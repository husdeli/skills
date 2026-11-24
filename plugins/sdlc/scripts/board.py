#!/usr/bin/env python3
#
# board.py — the board bookkeeping a pipeline would otherwise do by reading every file itself.
#
# Every answer here is mechanical: which tickets are ready, which number a new run takes, whether a
# claim held, and which tests a feature's tickets wrote. A model that works them out by hand reads
# every ticket and every worklog to do it, and can misread one. This script reads the same files
# with the same rules — the `ticket-board` skill's — and prints one JSON object.
#
#   ./board.py ready [--project <name>] [--root <dir>]  # ready tickets, in roadmap order
#   ./board.py ready --features --run run-roadmap-3     # a roadmap run's feature candidates
#   ./board.py next-run --command orchestrate           # the lowest free run number
#   ./board.py claim --run orchestrate-2 CHECKOUT-002   # write the claim, read it back
#   ./board.py release --run run-roadmap-3              # remove the run's claims on open tickets
#   ./board.py stop --run run-roadmap-3 --blocked-by "…" # stop the run's in-flight tickets as blocked
#   ./board.py recover --stale-hours 24                 # stop or release claims of runs that died
#   ./board.py feature-tests --ticket CHECKOUT-002      # the feature's tests, from the worklogs
#   ./board.py follow-up --ticket CHECKOUT-002 --run run-roadmap-3 [--claim] < leftovers.json
#                                                       # file leftover review issues in the epic's
#                                                       # follow-up ticket
#
# It finds the framework root the way `build-roadmap.py` does, and reuses that script's parser for
# tickets, features, and projects, so the two never read a board two ways.
#
# `claim` and `release` write `claimed` and `claimedAt`, and nothing else. `stop` and `recover` write
# the one transition a launcher has to make without a model: a ticket in flight becomes `blocked`,
# as the `ticket-board` skill's *Stopping without finishing* says, with an outcome worklog entry and
# a rebuilt roadmap. `follow-up` writes the epic's review follow-up ticket: the minor review issues
# a finished ticket left open, filed where the roadmap builds them. Every write holds the board lock
# (`<root>/.runs/.board.lock`) and replaces the file atomically, so two runs cannot both win a claim
# and a kill never leaves half a ticket.
#
# Exit codes: 0 done, 1 a claim was lost (`claim` only; the JSON says which), 2 an error that
# stopped it — the reason is on stderr.

from __future__ import annotations

import argparse
import contextlib
import datetime as _datetime
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows has no flock; the read-back is all it gets there
    fcntl = None

VERSION = "1.2.0"
LOCK_WAIT_SECONDS = 60
IN_FLIGHT = ("in progress", "review")

_spec = importlib.util.spec_from_file_location("build_roadmap", Path(__file__).with_name("build-roadmap.py"))
br = importlib.util.module_from_spec(_spec)
sys.modules["build_roadmap"] = br
_spec.loader.exec_module(br)

ID = re.compile(r"^[A-Z][A-Z0-9]{1,7}-\d{1,4}$")
CLAIM = re.compile(r"^([a-z][a-z-]*)-(\d+)$")
ENTRY_HEADER = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2}(?:[ T]\d{2}:\d{2})?)\s+—\s+(.+?)\s+·\s+(.+?)\s*$")
FENCE = re.compile(r"^```(\w*)\s*$")
E2E_TYPES = {"e2e", "end-to-end", "end to end"}


class BoardFail(Exception):
    pass


def now_property() -> str:
    """Local date and time in the form every ticket property uses."""
    return _datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")


def parse_property_time(value: object) -> _datetime.datetime | None:
    text = str(value or "").strip()
    for form in ("%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return _datetime.datetime.strptime(text, form)
        except ValueError:
            continue
    return None


# ------------------------------------------------------------------------------------ the lock


def runs_folder(root: Path) -> Path:
    """`<root>/.runs/`, the run scratch space, created with a `.gitignore` that ignores all of it."""
    folder = root / ".runs"
    folder.mkdir(exist_ok=True)
    ignore = folder / ".gitignore"
    if not ignore.exists():
        ignore.write_text("*\n", encoding="utf-8")
    return folder


@contextlib.contextmanager
def board_lock(root: Path):
    """Hold the board's write lock. Every command that writes a ticket takes it first, so the
    write-then-read-back of a claim is one step no other run can interleave with."""
    if fcntl is None:
        yield
        return
    handle = open(runs_folder(root) / ".board.lock", "a+")
    deadline = time.monotonic() + LOCK_WAIT_SECONDS
    try:
        while True:
            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() > deadline:
                    raise BoardFail(f"another process has held the board lock for {LOCK_WAIT_SECONDS}s: {handle.name}")
                time.sleep(0.2)
        yield
    finally:
        with contextlib.suppress(OSError):
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()


# ------------------------------------------------------------------------------------ frontmatter

KEY_LINE = re.compile(r"^([A-Za-z_][\w-]*)\s*:")
PLAIN_SCALAR = re.compile(r"^[\w./@+\[\]-][\w ./@+()\[\]-]*$")


def yaml_scalar(value: str) -> str:
    """A scalar as a ticket writes it: bare when it is plain, double-quoted otherwise."""
    if PLAIN_SCALAR.match(value) and not value.endswith(" ") and value.lower() not in ("true", "false", "null", "yes", "no"):
        return value
    # The board's parser strips one pair of quotes and unescapes nothing, so pick the quote the
    # value does not contain.
    if '"' not in value and "\\" not in value:
        return f'"{value}"'
    if "'" not in value:
        return f"'{value}'"
    return json.dumps(value, ensure_ascii=False)


def edit_frontmatter(text: str, changes: dict[str, object]) -> str:
    """Set, replace, or remove frontmatter properties, leaving every other line as it was.
    A value of None removes the property; a list is written as an indented block; anything else
    is a scalar. The file's own line endings are kept."""
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.split(newline)
    if not lines or lines[0].strip() != "---":
        raise BoardFail("no frontmatter")
    closing = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if closing is None:
        raise BoardFail("its frontmatter never closes")

    blocks: dict[str, tuple[int, int]] = {}
    index = 1
    while index < closing:
        match = KEY_LINE.match(lines[index])
        if not match:
            index += 1
            continue
        end = index + 1
        while end < closing and not KEY_LINE.match(lines[end]):
            end += 1
        blocks[match.group(1)] = (index, end)
        index = end

    def render(key: str, value: object) -> list[str]:
        if isinstance(value, (list, tuple)):
            if not value:
                return [f"{key}: []"]
            return [f"{key}:"] + [f"  - {yaml_scalar(str(item))}" for item in value]
        return [f"{key}: {yaml_scalar(str(value))}"]

    edits = []  # (start, end, replacement) on existing blocks
    additions: list[str] = []
    for key, value in changes.items():
        if key in blocks:
            start, end = blocks[key]
            # Keep blank lines that trailed the old block.
            while end - 1 > start and not lines[end - 1].strip():
                end -= 1
            edits.append((start, end, [] if value is None else render(key, value)))
        elif value is not None:
            additions += render(key, value)
    for start, end, replacement in sorted(edits, reverse=True):
        lines[start:end] = replacement
    if additions:
        closing = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
        lines[closing:closing] = additions
    return newline.join(lines)


def rewrite_ticket(path: Path, changes: dict[str, object]) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        raise BoardFail(f"{path.name}: {error}") from error
    try:
        updated = edit_frontmatter(text, changes)
    except BoardFail as error:
        raise BoardFail(f"{path.name}: {error}") from error
    if updated != text:
        br.atomic_write_text(path, updated)


# ------------------------------------------------------------------------------------ the board


class Board:
    """Every ticket on the board, with the properties the bookkeeping reads."""

    def __init__(self, args: argparse.Namespace) -> None:
        self.report = br.Report(quiet=True)
        namespace = argparse.Namespace(root=args.root, project=getattr(args, "project", None), roadmap=None)
        try:
            self.located = br.locate_board(namespace)
        except br.BoardError as error:
            raise BoardFail(str(error)) from error
        self.root = self.located.root
        folder, self.shared = br.ticket_folder(self.located, self.located.projects[0])
        if folder is None:
            raise BoardFail(f"No work/ or tickets/ folder under {self.root}")
        self.folder = folder
        self.tickets = br.collect_tickets(folder, self.report)
        by_stem, by_code = br.collect_features(self.root, self.report)
        br.attach_features(self.tickets, by_stem, by_code, self.report)
        self.props = {tid: self._properties(t.path) for tid, t in self.tickets.items()}

    @staticmethod
    def _properties(path: Path) -> dict[str, object]:
        try:
            properties, _ = br.split_frontmatter(path.read_text(encoding="utf-8"))
        except OSError:
            return {}
        return properties

    def claimed(self, ticket_id: str) -> str:
        return str(self.props[ticket_id].get("claimed") or "").strip()

    def blocked_by(self, ticket_id: str) -> list[str]:
        return [item.strip() for item in br.as_list(self.props[ticket_id].get("blocked_by")) if item.strip()]

    def repositories(self, ticket_id: str) -> list[str]:
        return [br.link_target(item) for item in br.as_list(self.props[ticket_id].get("repositories"))]

    def find(self, ref: str) -> br.Ticket:
        if ref in self.tickets:
            return self.tickets[ref]
        path = Path(ref).expanduser()
        name = path.name if path.suffix == ".md" else f"{path.name}.md"
        for ticket in self.tickets.values():
            if ticket.path.name == name or ticket.path.resolve() == path.resolve():
                return ticket
        raise BoardFail(f"No ticket {ref!r} under {self.folder}")

    def project(self, args: argparse.Namespace):
        projects = self.located.projects
        if len(projects) > 1:
            names = ", ".join(sorted(next(iter(p.names)) for p in projects))
            raise BoardFail(f"Several projects have a roadmap — pass --project: {names}")
        project = projects[0]
        if project.status == "backlog" and not args.project:
            raise BoardFail(f"{project.label} is in backlog, so its tickets are offered only when --project names it")
        return project

    def of_project(self, project) -> dict[str, br.Ticket]:
        if self.shared and self.located.has_projects:
            return {tid: t for tid, t in self.tickets.items() if br.belongs_to(t, project, self.report)}
        return dict(self.tickets)

    def roadmap_order(self, project, tickets: dict[str, br.Ticket]) -> list[br.Ticket]:
        """Open tickets as the rebuilt roadmap lists them: epics in the file's order, each epic's
        rows in `build-roadmap.py`'s order."""
        open_tickets = [t for t in tickets.values() if not t.is_done]
        blockers = {t.ticket_id: br.outstanding(t, self.tickets, self.report) for t in open_tickets}
        by_code: dict[str, list[br.Ticket]] = {}
        for ticket in open_tickets:
            by_code.setdefault(ticket.code, []).append(ticket)
        codes: list[str] = []
        roadmap_path = project.folder / "roadmap.md"
        if roadmap_path.is_file():
            codes = [s.code for s in br.load_roadmap(roadmap_path, "auto").sections if s.code in by_code]
        codes += sorted(code for code in by_code if code not in codes)
        ordered: list[br.Ticket] = []
        for code in codes:
            ordered.extend(br.sort_epic(by_code[code], blockers, self.report))
        return ordered


def ticket_json(board: Board, ticket: br.Ticket) -> dict[str, object]:
    return {
        "id": ticket.ticket_id,
        "title": ticket.title,
        "priority": ticket.priority,
        "status": ticket.status,
        "feature": ticket.feature.stem if ticket.feature else "",
        "dependsOn": ticket.depends_on,
        "claimed": board.claimed(ticket.ticket_id),
        "repositories": board.repositories(ticket.ticket_id),
        "path": str(ticket.path),
    }


def unsatisfied(board: Board, ids: list[str]) -> list[str]:
    return [i for i in ids if not (board.tickets.get(i) and board.tickets[i].is_done)]


def outside_causes(board: Board, ticket_id: str) -> list[str]:
    """The `blocked_by` lines that are not the ID of a finished ticket."""
    return [
        line
        for line in board.blocked_by(ticket_id)
        if not (ID.match(line) and board.tickets.get(line) and board.tickets[line].is_done)
    ]


# ------------------------------------------------------------------------------------ ready


def command_ready(args: argparse.Namespace) -> dict[str, object]:
    board = Board(args)
    project = board.project(args)
    tickets = board.of_project(project)
    ordered = board.roadmap_order(project, tickets)
    position = {t.ticket_id: index for index, t in enumerate(ordered)}

    missing = sorted({d for t in ordered for d in t.depends_on if d not in board.tickets})
    busy: dict[str, list[dict[str, str]]] = {}
    for ticket in board.tickets.values():
        claim = board.claimed(ticket.ticket_id)
        if claim and ticket.status in ("in progress", "review"):
            for code in board.repositories(ticket.ticket_id):
                busy.setdefault(code, []).append({"id": ticket.ticket_id, "claimed": claim})

    result: dict[str, object] = {
        "root": str(board.root),
        "project": project.label,
        "remaining": len(ordered),
        "busyWorkRoots": busy,
        "missingIds": missing,
    }

    if not args.features:
        ready = []
        for ticket in ordered:
            tid = ticket.ticket_id
            if board.claimed(tid):
                continue
            if ticket.status == "backlog" and not unsatisfied(board, ticket.depends_on):
                ready.append({**ticket_json(board, ticket), "resume": False})
            elif ticket.status == "blocked" and not outside_causes(board, tid):
                ready.append({**ticket_json(board, ticket), "resume": True})
        result["ready"] = ready
        result["problems"] = board.report.problems
        return result

    # A roadmap run selects a feature: its open tickets, and every open ticket they wait on.
    def cluster_of(code: str) -> tuple[list[str], list[str]]:
        seeds = [t.ticket_id for t in board.tickets.values() if t.code == code and not t.is_done]
        members, gaps, queue = set(seeds), [], list(seeds)
        while queue:
            for dep in board.tickets[queue.pop()].depends_on:
                other = board.tickets.get(dep)
                if other is None:
                    gaps.append(dep)
                elif not other.is_done and dep not in members:
                    members.add(dep)
                    queue.append(dep)
        return sorted(members, key=lambda i: (position.get(i, len(position)), i)), sorted(set(gaps))

    def next_in(members: list[str]) -> str:
        for tid in members:
            if not unsatisfied(board, board.tickets[tid].depends_on) and not (
                board.tickets[tid].status == "blocked" and outside_causes(board, tid)
            ):
                return tid
        return ""

    own = sorted(
        (t.ticket_id for t in board.tickets.values() if args.run and not t.is_done and board.claimed(t.ticket_id) == args.run),
        key=lambda i: (position.get(i, len(position)), i),
    )
    result["claimedByRun"] = {"tickets": own, "next": next_in(own)} if own else None

    candidates, excluded = [], []
    codes = list(dict.fromkeys(t.code for t in ordered))
    for code in codes:
        members, gaps = cluster_of(code)
        reasons = [f"depends on {gap}, which no ticket carries" for gap in gaps]
        for tid in members:
            claim = board.claimed(tid)
            if claim and claim != args.run:
                reasons.append(f"{tid} is claimed by {claim}")
            if board.tickets[tid].status == "blocked":
                for cause in outside_causes(board, tid):
                    if cause not in members:
                        reasons.append(f"{tid} is blocked by {cause}")
        feature = next((board.tickets[t].feature for t in members if board.tickets[t].code == code), None)
        entry = {"code": code, "feature": feature.stem if feature else "", "name": feature.name if feature else ""}
        if reasons:
            excluded.append({**entry, "reasons": reasons})
        else:
            candidates.append(
                {**entry, "next": next_in(members), "cluster": [ticket_json(board, board.tickets[t]) for t in members]}
            )
    result["candidates"] = candidates
    result["excluded"] = excluded
    result["problems"] = board.report.problems
    return result


# ------------------------------------------------------------------------------------ claims


def command_next_run(args: argparse.Namespace) -> dict[str, object]:
    board = Board(args)
    with board_lock(board.root) if args.reserve else contextlib.nullcontext():
        used = set()
        for tid in board.tickets:
            match = CLAIM.match(board.claimed(tid))
            if match:
                used.add(int(match.group(2)))
        live = board.root / ".runs" / ".live"
        if live.is_dir():
            for child in live.iterdir():
                match = CLAIM.match(child.name)
                if match:
                    used.add(int(match.group(2)))
        repositories = [Path(p).expanduser() for p in args.repo] or registry_paths(board.root)
        if args.command == "run-roadmap":
            for repo in repositories:
                for n in branch_numbers(repo):
                    used.add(n)
        n = 1
        while n in used:
            n += 1
        result: dict[str, object] = {"n": n, "run": f"{args.command}-{n}", "used": sorted(used)}
        if args.reserve:
            # The heartbeat file reserves the number until the launcher removes it, and its mtime is
            # what `recover` reads to tell a live run from a dead one.
            live = runs_folder(board.root) / ".live"
            live.mkdir(exist_ok=True)
            (live / result["run"]).touch()
            result["heartbeat"] = str(live / result["run"])
    return result


def registry_paths(root: Path) -> list[Path]:
    registry = root / "sdlc.json"
    try:
        entries = json.loads(registry.read_text(encoding="utf-8")).get("repositories", {})
    except (OSError, ValueError, AttributeError):
        return []
    paths = []
    for entry in entries.values():
        raw = str((entry or {}).get("path", "")).strip()
        if raw:
            path = Path(raw).expanduser()
            paths.append(path if path.is_absolute() else (root / path).resolve())
    return paths


def branch_numbers(repo: Path) -> list[int]:
    numbers = []
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), "for-each-ref", "--format=%(refname:short)", "refs/heads/run-roadmap-*"],
            capture_output=True, text=True, check=False,
        ).stdout
    except OSError:
        return numbers
    for line in out.splitlines():
        match = CLAIM.match(line.strip())
        if match:
            numbers.append(int(match.group(2)))
    worktrees = repo.parent / f"{repo.name}-worktrees"
    if worktrees.is_dir():
        for child in worktrees.iterdir():
            match = CLAIM.match(child.name)
            if match and match.group(1) == "run-roadmap":
                numbers.append(int(match.group(2)))
    return numbers


def set_claim(path: Path, value: str | None) -> None:
    """Write or remove `claimed` and its `claimedAt`, leaving every other line as it was."""
    rewrite_ticket(path, {"claimed": value, "claimedAt": now_property() if value else None})


def check_writable(tickets: list[br.Ticket]) -> None:
    """Fail before the first write when any ticket could not take one, so a claim never half lands."""
    for ticket in tickets:
        try:
            edit_frontmatter(ticket.path.read_text(encoding="utf-8"), {})
        except (BoardFail, OSError) as error:
            raise BoardFail(f"{ticket.path.name}: {error}") from error


def command_claim(args: argparse.Namespace) -> tuple[dict[str, object], int]:
    board = Board(args)
    with board_lock(board.root):
        return _claim(Board(args), args)


def _claim(board: Board, args: argparse.Namespace) -> tuple[dict[str, object], int]:
    tickets = [board.find(ref) for ref in args.tickets]
    check_writable([t for t in tickets if not t.is_done])
    lost, skipped, written = [], [], []
    for ticket in tickets:
        claim = board.claimed(ticket.ticket_id)
        if ticket.is_done:
            skipped.append({"id": ticket.ticket_id, "reason": "done"})
        elif claim and claim != args.run:
            lost.append({"id": ticket.ticket_id, "claimedBy": claim})
        else:
            if claim != args.run:
                set_claim(ticket.path, args.run)
                written.append(ticket)
    if not lost:
        # The read-back: another run may have written the same files since.
        for ticket in tickets:
            if ticket.is_done:
                continue
            now = str(Board._properties(ticket.path).get("claimed") or "").strip()
            if now != args.run:
                lost.append({"id": ticket.ticket_id, "claimedBy": now})
    if lost:
        released = []
        for ticket in written:
            if str(Board._properties(ticket.path).get("claimed") or "").strip() == args.run:
                set_claim(ticket.path, None)
                released.append(ticket.ticket_id)
        return {"held": False, "lost": lost, "released": released, "skipped": skipped}, 1
    return {"held": True, "claimed": [t.ticket_id for t in tickets if not t.is_done], "skipped": skipped}, 0


def command_release(args: argparse.Namespace) -> dict[str, object]:
    board = Board(args)
    with board_lock(board.root):
        return _release(Board(args), args)


def _release(board: Board, args: argparse.Namespace) -> dict[str, object]:
    if args.tickets:
        tickets = [board.find(ref) for ref in args.tickets]
    else:
        tickets = [t for t in board.tickets.values() if not t.is_done and board.claimed(t.ticket_id) == args.run]
    released, not_ours = [], []
    for ticket in tickets:
        claim = board.claimed(ticket.ticket_id)
        if claim == args.run:
            set_claim(ticket.path, None)
            released.append(ticket.ticket_id)
        elif claim:
            not_ours.append({"id": ticket.ticket_id, "claimedBy": claim})
    return {"released": released, "notOurs": not_ours}


# ------------------------------------------------------------------------------------ stop and recover


def append_worklog(ticket: br.Ticket, run: str, lines: list[str]) -> Path:
    """Append one outcome entry to the ticket's worklog, creating the worklog when it has none."""
    worklog = ticket.path.with_name(f"{ticket.path.stem}.worklog.md")
    stamp = _datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"## {stamp} — {run} · stop\n\n" + "".join(f"- {line}\n" for line in lines)
    if worklog.is_file():
        text = worklog.read_text(encoding="utf-8")
        separator = "" if text.endswith("\n\n") else ("\n" if text.endswith("\n") else "\n\n")
        br.atomic_write_text(worklog, text + separator + entry)
    else:
        br.atomic_write_text(worklog, f"# [{ticket.ticket_id}] {ticket.title} — worklog\n\n" + entry)
    return worklog


def rebuild_roadmaps(root: Path) -> int:
    """Rebuild every project's roadmap from the tickets, so a stopped row reads `Blocked`."""
    namespace = argparse.Namespace(
        project=None, root=str(root), roadmap=None, check=False, style="auto", strict=False, today=None, quiet=True,
    )
    with contextlib.redirect_stdout(sys.stderr):
        return br.build(namespace)


def stop_tickets(board: Board, tickets: list[br.Ticket], run: str, blocked_by: str, stage: str, details: list[str]) -> list[dict[str, object]]:
    check_writable(tickets)
    stopped = []
    for ticket in tickets:
        rewrite_ticket(ticket.path, {
            "status": "blocked",
            "blocked_by": [blocked_by],
            "assigned": None,
            "claimed": None,
            "claimedAt": None,
            "updatedAt": now_property(),
        })
        worklog = append_worklog(ticket, run, [
            f"Stopped at {stage}, outside the pipeline: {blocked_by}",
            *details,
            "Nothing was committed for this ticket. A person deletes the `blocked_by` line once the cause is "
            "cleared, and the next run starts the ticket again from Plan, with this worklog as input.",
        ])
        stopped.append({"id": ticket.ticket_id, "path": str(ticket.path), "worklog": str(worklog)})
    return stopped


def command_stop(args: argparse.Namespace) -> dict[str, object]:
    board = Board(args)
    with board_lock(board.root):
        board = Board(args)
        if args.tickets:
            tickets = [board.find(ref) for ref in args.tickets]
            foreign = [t.ticket_id for t in tickets if board.claimed(t.ticket_id) not in ("", args.run)]
            if foreign:
                raise BoardFail(f"another run claims {', '.join(foreign)}; stop only what --run holds")
        else:
            tickets = [
                t for t in board.tickets.values()
                if board.claimed(t.ticket_id) == args.run and t.status in IN_FLIGHT
            ]
        tickets = [t for t in tickets if not t.is_done]
        stopped = stop_tickets(board, tickets, args.run, args.blocked_by, args.stage, args.detail)
        released = _release(Board(args), argparse.Namespace(run=args.run, tickets=[]))["released"] if args.release_rest else []
        roadmap = rebuild_roadmaps(board.root) if stopped else 0
    return {"stopped": stopped, "released": released, "roadmapRebuilt": bool(stopped) and roadmap != 2}


def run_last_seen(root: Path, claim: str, claimed_at: _datetime.datetime | None) -> _datetime.datetime | None:
    """The newest sign the run is alive: its claim time, or the heartbeat its launcher touches."""
    seen = [claimed_at] if claimed_at else []
    heartbeat = root / ".runs" / ".live" / claim
    if heartbeat.exists():
        seen.append(_datetime.datetime.fromtimestamp(heartbeat.stat().st_mtime))
    return max(seen) if seen else None


def command_recover(args: argparse.Namespace) -> dict[str, object]:
    board = Board(args)
    with board_lock(board.root):
        board = Board(args)
        limit = _datetime.datetime.now() - _datetime.timedelta(hours=args.stale_hours)
        stale: dict[str, list[br.Ticket]] = {}
        undated, alive = [], []
        for ticket in board.tickets.values():
            claim = board.claimed(ticket.ticket_id)
            if not claim or ticket.is_done or (args.run and claim != args.run):
                continue
            seen = run_last_seen(board.root, claim, parse_property_time(board.props[ticket.ticket_id].get("claimedAt")))
            if seen is None:
                undated.append({"id": ticket.ticket_id, "claimed": claim})
            elif seen < limit:
                stale.setdefault(claim, []).append(ticket)
            else:
                alive.append({"id": ticket.ticket_id, "claimed": claim, "lastSeen": seen.strftime("%Y-%m-%dT%H:%M")})
        stopped, released = [], []
        for claim, tickets in stale.items():
            in_flight = [t for t in tickets if t.status in IN_FLIGHT]
            reason = (f"Run {claim} stopped without exiting and left this ticket in flight. Check its work root "
                      f"for half-built changes, then delete this line.")
            if not args.dry_run:
                stopped += stop_tickets(board, in_flight, claim, reason, "an unknown stage", [])
                for ticket in tickets:
                    if ticket not in in_flight:
                        set_claim(ticket.path, None)
                        released.append(ticket.ticket_id)
            else:
                stopped += [{"id": t.ticket_id, "path": str(t.path)} for t in in_flight]
                released += [t.ticket_id for t in tickets if t not in in_flight]
        if stopped and not args.dry_run:
            rebuild_roadmaps(board.root)
    return {"dryRun": args.dry_run, "stopped": stopped, "released": released, "alive": alive, "undated": undated}


# ------------------------------------------------------------------------------------ review follow-ups

FOLLOW_UP_PROPERTY = "follows_up"
FOLLOW_UP_TITLE = "Review follow-ups"
FOLLOW_UP_SLUG = "review-follow-ups"
FOLLOW_UP_PRIORITY = "Low"
CRITERIA_HEADING = "## Acceptance Criteria"


def one_line(value: object) -> str:
    return " ".join(str(value or "").split())


def read_leftovers(raw: str) -> list[dict[str, str]]:
    """The leftover minor issues: an array, or an object holding one under `issues`."""
    try:
        data = json.loads(raw, strict=False) if raw.strip() else []
    except ValueError as error:
        raise BoardFail(f"the input is not JSON: {error}") from error
    if isinstance(data, dict):
        data = data.get("issues", [])
    if not isinstance(data, list):
        raise BoardFail("the input is neither an array of issues nor an object holding one under `issues`")
    issues, problems = [], []
    for index, entry in enumerate(data):
        if not isinstance(entry, dict):
            problems.append(f"issue {index}: not an object")
            continue
        issue = {key: one_line(entry.get(key)) for key in ("title", "file", "line", "problem", "suggestion", "focus", "reason")}
        missing = [key for key in ("title", "problem") if not issue[key]]
        if missing:
            problems.append(f"issue {index}: missing {', '.join(missing)}")
        issues.append(issue)
    if problems:
        raise BoardFail("; ".join(problems))
    return issues


def criterion_key(issue: dict[str, str]) -> str:
    """The part of a criterion that names the issue; the same issue filed twice has the same key."""
    where = issue["file"] + (f":{issue['line']}" if issue["file"] and issue["line"] else "")
    return f"**{issue['title']}**" + (f" — `{where}`" if where else "")


def criterion(issue: dict[str, str], source: str) -> str:
    fix = f" {issue['suggestion']}" if issue["suggestion"] else ""
    origin = ", ".join(part for part in (source, f"{issue['focus']} review" if issue["focus"] else "") if part)
    left = f"; left because {issue['reason']}" if issue["reason"] else ""
    return f"- [ ] {criterion_key(issue)}: {issue['problem']}{fix} _({origin}{left})_"


def frontmatter_block(text: str, key: str) -> list[str]:
    """A property's lines exactly as the ticket wrote them, list items included."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return []
    block: list[str] = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        match = KEY_LINE.match(line)
        if match:
            if block:
                break
            if match.group(1) == key:
                block.append(line)
        elif block:
            block.append(line)
    while block and not block[-1].strip():
        block.pop()
    return block


def backlog_folder(board: Board) -> Path:
    for name in ("backlog", "todo"):
        if (board.folder / name).is_dir():
            return board.folder / name
    if board.folder.name == "work":
        return board.folder / "backlog"
    return board.folder


def new_follow_up(board: Board, source: br.Ticket, criteria: list[str]) -> tuple[str, Path]:
    source_text = source.path.read_text(encoding="utf-8")
    feature = frontmatter_block(source_text, "feature")
    if not feature:
        raise BoardFail(f"{source.path.name} has no `feature` property to give its follow-up ticket")
    repositories = frontmatter_block(source_text, "repositories") or ["repositories: []"]
    number = 1 + max((t.number for t in board.tickets.values() if t.code == source.code), default=0)
    ticket_id = f"{source.code}-{number:03d}"
    now = now_property()
    text = "\n".join([
        "---",
        *feature,
        "status: backlog",
        f"priority: {FOLLOW_UP_PRIORITY}",
        *repositories,
        "depends_on: []",
        f"{FOLLOW_UP_PROPERTY}:",
        f"  - {source.ticket_id}",
        f"createdAt: {now}",
        f"updatedAt: {now}",
        "---",
        "",
        f"# [{ticket_id}] {FOLLOW_UP_TITLE}",
        "",
        "## Description",
        "",
        "The minor issues the code review raised on this feature's finished tickets, which their runs "
        "left open. Each names the code it was raised on, so this ticket names files where others do not.",
        "",
        CRITERIA_HEADING,
        "",
        "Each issue below is fixed, or the plan says why it no longer applies: the code it names has "
        "changed or gone.",
        "",
        *criteria,
        "",
    ])
    folder = backlog_folder(board)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{ticket_id}-{FOLLOW_UP_SLUG}.md"
    br.atomic_write_text(path, text)
    return ticket_id, path


def append_criteria(path: Path, source_id: str, criteria: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.split(newline)
    start = next((i for i, line in enumerate(lines) if line.strip() == CRITERIA_HEADING), None)
    if start is None:
        lines += ["", CRITERIA_HEADING, "", *criteria, ""]
    else:
        end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
        while end - 1 > start and not lines[end - 1].strip():
            end -= 1
        lines[end:end] = criteria
    sources = [str(s) for s in br.as_list(Board._properties(path).get(FOLLOW_UP_PROPERTY))]
    if source_id not in sources:
        sources.append(source_id)
    updated = edit_frontmatter(newline.join(lines), {FOLLOW_UP_PROPERTY: sources, "updatedAt": now_property()})
    br.atomic_write_text(path, updated)


def command_follow_up(args: argparse.Namespace, raw: str) -> dict[str, object]:
    issues = read_leftovers(raw)
    board = Board(args)
    with board_lock(board.root):
        board = Board(args)
        source = board.find(args.ticket)
        if FOLLOW_UP_PROPERTY in board.props[source.ticket_id]:
            return {"ticket": None, "added": [], "duplicates": [], "claimed": False, "roadmapRebuilt": False,
                    "skipped": f"{source.ticket_id} is a follow-up ticket: its leftovers go in the report, never in another ticket"}
        if not issues:
            return {"ticket": None, "added": [], "duplicates": [], "claimed": False, "roadmapRebuilt": False}

        open_follow_ups = sorted(
            (t for t in board.tickets.values()
             if t.code == source.code and t.status == "backlog"
             and FOLLOW_UP_PROPERTY in board.props[t.ticket_id]
             and board.claimed(t.ticket_id) in ("", args.run)),
            key=lambda t: t.number,
        )
        target = open_follow_ups[0] if open_follow_ups else None
        existing = target.path.read_text(encoding="utf-8") if target else ""

        added, duplicates, criteria, seen = [], [], [], set()
        for issue in issues:
            key = criterion_key(issue)
            if key in seen or key in existing:
                duplicates.append(issue["title"])
                continue
            seen.add(key)
            added.append(issue["title"])
            criteria.append(criterion(issue, source.ticket_id))
        if not criteria:
            return {"ticket": {"id": target.ticket_id, "path": str(target.path), "created": False},
                    "added": [], "duplicates": duplicates, "claimed": False, "roadmapRebuilt": False}

        if target:
            check_writable([target])
            append_criteria(target.path, source.ticket_id, criteria)
            ticket_id, path, created = target.ticket_id, target.path, False
        else:
            ticket_id, path = new_follow_up(board, source, criteria)
            created = True

        claimed = False
        if args.claim:
            current = str(Board._properties(path).get("claimed") or "").strip()
            if current != args.run:
                set_claim(path, args.run)
            claimed = True
        roadmap = rebuild_roadmaps(board.root)
    return {
        "ticket": {"id": ticket_id, "path": str(path), "created": created},
        "added": added,
        "duplicates": duplicates,
        "claimed": claimed,
        "roadmapRebuilt": roadmap != 2,
    }


# ------------------------------------------------------------------------------------ the feature's tests


def test_records(worklog: Path) -> tuple[list[tuple[str, int, dict]], list[str]]:
    """Every `test-writer · tests` entry's JSON record, with its time; and the headers of the
    entries that hold none."""
    records, unparsed = [], []
    lines = worklog.read_text(encoding="utf-8").splitlines()
    entries: list[tuple[str, str, str, list[str]]] = []
    for raw in lines:
        header = ENTRY_HEADER.match(raw)
        if header:
            entries.append((header.group(1), header.group(2).strip(), header.group(3).strip(), []))
        elif entries:
            entries[-1][3].append(raw)
    for index, (when, role, stage, body) in enumerate(entries):
        if role != "test-writer" or stage != "tests":
            continue
        record, block, inside = None, [], False
        for raw in body:
            fence = FENCE.match(raw.strip())
            if fence and not inside and fence.group(1) in ("json", ""):
                inside, block = True, []
            elif fence and inside:
                try:
                    record = json.loads("\n".join(block))
                except ValueError:
                    record = None
                inside = False
            elif inside:
                block.append(raw)
        if isinstance(record, dict):
            records.append((when.replace("T", " "), index, record))
        else:
            unparsed.append(f"{when} — {role} · {stage}")
    return records, unparsed


def command_feature_tests(args: argparse.Namespace) -> dict[str, object]:
    board = Board(args)
    ticket = board.find(args.ticket)

    def same_feature(other: br.Ticket) -> bool:
        if ticket.feature is not None:
            return other.feature is ticket.feature
        return other.code == ticket.code

    members = [t for t in board.tickets.values() if same_feature(t) and (t.is_done or t is ticket)]
    members.sort(key=lambda t: t.number)

    roots: dict[str, Path | None] = {}
    bare_root: Path | None = None
    for item in args.work_root:
        code, sep, path = item.partition("=")
        if sep:
            roots[code.strip()] = Path(path).expanduser()
        else:
            bare_root = Path(item).expanduser()

    events, unparsed, no_worklog = [], [], []
    for order, member in enumerate(members):
        worklog = member.path.with_name(f"{member.path.stem}.worklog.md")
        if not worklog.is_file():
            no_worklog.append(member.ticket_id)
            continue
        records, bad = test_records(worklog)
        unparsed += [{"worklog": str(worklog), "entry": header} for header in bad]
        events += [(when, order, index, member.ticket_id, record) for when, index, record in records]
    events.sort(key=lambda e: (e[0], e[1], e[2]))

    cases: dict[tuple[str, str], dict[str, str]] = {}
    for _, _, _, ticket_id, record in events:
        work_root = str(record.get("workRoot") or "").strip()
        files = record.get("testFiles") or {}
        deleted = set(files.get("deleted") or []) if isinstance(files, dict) else set()
        for key in [k for k, case in cases.items() if case["workRoot"] == work_root and case["file"] in deleted]:
            del cases[key]
        e2e_command = str(record.get("e2eCommand") or "").strip()
        for case in record.get("cases") or []:
            if not isinstance(case, dict) or not case.get("id") or not case.get("command"):
                continue
            kind = str(case.get("type") or "").strip().lower()
            command = str(case["command"]).strip()
            if kind in E2E_TYPES or (e2e_command and command == e2e_command):
                continue
            cases[(ticket_id, str(case["id"]))] = {
                "workRoot": work_root, "file": str(case.get("file") or ""), "command": command,
            }

    commands: dict[tuple[str, str], dict[str, object]] = {}
    skipped = []
    for (ticket_id, case_id), case in cases.items():
        label = f"{ticket_id}:{case_id}"
        if roots and case["workRoot"] not in roots and bare_root is None:
            skipped.append({"case": label, "file": case["file"], "reason": f"built in {case['workRoot'] or 'an unnamed work root'}"})
            continue
        base = roots.get(case["workRoot"], bare_root)
        if base is not None and case["file"] and not (base / case["file"]).exists():
            skipped.append({"case": label, "file": case["file"], "reason": "not in this work root"})
            continue
        entry = commands.setdefault(
            (case["workRoot"], case["command"]),
            {"workRoot": case["workRoot"], "command": case["command"], "cases": [], "files": []},
        )
        entry["cases"].append(label)
        if case["file"] and case["file"] not in entry["files"]:
            entry["files"].append(case["file"])

    return {
        "ticket": ticket.ticket_id,
        "feature": ticket.feature.stem if ticket.feature else ticket.code,
        "tickets": [t.ticket_id for t in members],
        "commands": list(commands.values()),
        "skipped": skipped,
        "unparsed": unparsed,
        "noWorklog": no_worklog,
    }


# ------------------------------------------------------------------------------------ main


def main(argv: list[str] | None = None) -> int:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--root", help="the framework root, when it cannot be found from here")
    parser = argparse.ArgumentParser(prog="board.py", description="Board bookkeeping for the pipelines.")
    parser.add_argument("--version", action="version", version=f"board.py {VERSION}")
    sub = parser.add_subparsers(dest="action", required=True)

    def add(name: str, help: str) -> argparse.ArgumentParser:
        return sub.add_parser(name, help=help, parents=[common])

    ready = add("ready", "the ready tickets, or a roadmap run's feature candidates")
    ready.add_argument("--project", help="the project, by its name or its folder")
    ready.add_argument("--features", action="store_true", help="list feature candidates and their clusters")
    ready.add_argument("--run", help="the roadmap run whose own claims count as held, not as another run's")

    nxt = add("next-run", "the lowest run number no claim uses")
    nxt.add_argument("--command", required=True, choices=("orchestrate", "orchestrate-quick", "run-roadmap"))
    nxt.add_argument("--repo", action="append", default=[], help="a repository whose branches count (run-roadmap)")
    nxt.add_argument("--reserve", action="store_true", help="hold the number with a heartbeat file under .runs/.live/")

    claim = add("claim", "write the run's claim on tickets and read it back")
    claim.add_argument("--run", required=True)
    claim.add_argument("tickets", nargs="+", help="ticket IDs or paths")

    release = add("release", "remove the run's claims")
    release.add_argument("--run", required=True)
    release.add_argument("tickets", nargs="*", help="ticket IDs or paths; every open ticket the run claims when left out")

    stop = add("stop", "stop the run's tickets in flight as blocked — what a launcher does after a crash")
    stop.add_argument("--run", required=True)
    stop.add_argument("--blocked-by", required=True, help="the one line naming what a person must do")
    stop.add_argument("--stage", default="an unknown stage", help="the stage the ticket stopped at")
    stop.add_argument("--detail", action="append", default=[], help="another line for the outcome entry")
    stop.add_argument("--release-rest", action="store_true", help="also release the run's other claims")
    stop.add_argument("tickets", nargs="*", help="ticket IDs or paths; every in-flight ticket the run claims when left out")

    recover = add("recover", "stop or release the claims of runs that died without exiting")
    recover.add_argument("--stale-hours", type=float, default=24.0, help="a claim older than this, with no fresher heartbeat, is dead")
    recover.add_argument("--run", help="only this run's claims")
    recover.add_argument("--dry-run", action="store_true", help="report what would change and write nothing")

    tests = add("feature-tests", "the feature's tests, from its tickets' worklogs")
    tests.add_argument("--ticket", required=True, help="the ticket being built, by ID or path")
    tests.add_argument(
        "--work-root", action="append", default=[],
        help="CODE=DIR keeps only that work root's tests and checks their files exist; a bare DIR applies to all",
    )

    follow = add("follow-up", "file a finished ticket's leftover minor review issues in its epic's follow-up ticket")
    follow.add_argument("--ticket", required=True, help="the ticket the issues were raised on, by ID or path")
    follow.add_argument("--run", required=True, help="the run filing them, e.g. run-roadmap-3")
    follow.add_argument("--claim", action="store_true", help="claim the follow-up ticket for --run, so a roadmap run builds it")

    args = parser.parse_args(argv)
    if getattr(args, "run", None) and not CLAIM.match(args.run):
        print(f"--run {args.run!r} is not a claim such as orchestrate-2", file=sys.stderr)
        return 2
    try:
        code = 0
        if args.action == "ready":
            result = command_ready(args)
        elif args.action == "next-run":
            result = command_next_run(args)
        elif args.action == "claim":
            result, code = command_claim(args)
        elif args.action == "release":
            result = command_release(args)
        elif args.action == "stop":
            result = command_stop(args)
        elif args.action == "recover":
            result = command_recover(args)
        elif args.action == "follow-up":
            result = command_follow_up(args, sys.stdin.read())
        else:
            result = command_feature_tests(args)
    except BoardFail as error:
        print(error, file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
