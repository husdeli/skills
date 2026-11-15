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
#   ./board.py feature-tests --ticket CHECKOUT-002      # the feature's tests, from the worklogs
#
# It finds the framework root the way `build-roadmap.py` does, and reuses that script's parser for
# tickets, features, and projects, so the two never read a board two ways.
#
# What it never does: move a ticket, change its status, or write a worklog. `claim` and `release`
# write one property, `claimed`, and nothing else.
#
# Exit codes: 0 done, 1 a claim was lost (`claim` only; the JSON says which), 2 an error that
# stopped it — the reason is on stderr.

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

VERSION = "1.0.0"

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
    used = set()
    for tid in board.tickets:
        match = CLAIM.match(board.claimed(tid))
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
    return {"n": n, "run": f"{args.command}-{n}", "used": sorted(used)}


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
    """Write or remove the `claimed` property, leaving every other line as it was."""
    lines = path.read_text(encoding="utf-8").split("\n")
    if not lines or lines[0].strip() != "---":
        raise BoardFail(f"{path.name}: no frontmatter to write the claim into")
    closing = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if closing is None:
        raise BoardFail(f"{path.name}: its frontmatter never closes")
    index = next((i for i in range(1, closing) if re.match(r"^claimed:", lines[i])), None)
    if value is None:
        if index is not None:
            del lines[index]
    elif index is not None:
        lines[index] = f"claimed: {value}"
    else:
        lines.insert(closing, f"claimed: {value}")
    path.write_text("\n".join(lines), encoding="utf-8")


def command_claim(args: argparse.Namespace) -> tuple[dict[str, object], int]:
    board = Board(args)
    tickets = [board.find(ref) for ref in args.tickets]
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

    claim = add("claim", "write the run's claim on tickets and read it back")
    claim.add_argument("--run", required=True)
    claim.add_argument("tickets", nargs="+", help="ticket IDs or paths")

    release = add("release", "remove the run's claims")
    release.add_argument("--run", required=True)
    release.add_argument("tickets", nargs="*", help="ticket IDs or paths; every open ticket the run claims when left out")

    tests = add("feature-tests", "the feature's tests, from its tickets' worklogs")
    tests.add_argument("--ticket", required=True, help="the ticket being built, by ID or path")
    tests.add_argument(
        "--work-root", action="append", default=[],
        help="CODE=DIR keeps only that work root's tests and checks their files exist; a bare DIR applies to all",
    )

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
        else:
            result = command_feature_tests(args)
    except BoardFail as error:
        print(error, file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
