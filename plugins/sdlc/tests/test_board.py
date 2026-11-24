"""board.py: claims under the lock, the frontmatter editor, stop, recover, and run numbers."""

from __future__ import annotations

import importlib.util
import os
import sys
import threading
import time
from pathlib import Path

import pytest

from conftest import SCRIPTS

spec = importlib.util.spec_from_file_location("board", SCRIPTS / "board.py")
board_module = importlib.util.module_from_spec(spec)
sys.modules["board"] = board_module
spec.loader.exec_module(board_module)


def props(path: Path) -> dict:
    return board_module.br.split_frontmatter(path.read_text(encoding="utf-8"))[0]


# ------------------------------------------------------------------ the frontmatter editor


def test_edit_keeps_untouched_lines_and_replaces_lists():
    text = "---\na: 1\nblocked_by:\n  - old\n  - older\nb: two words\n---\nbody\n"
    out = board_module.edit_frontmatter(text, {"blocked_by": ["new: line"], "c": "x"})
    assert out == '---\na: 1\nblocked_by:\n  - "new: line"\nb: two words\nc: x\n---\nbody\n'


def test_edit_removes_a_block_property_with_its_items():
    text = "---\na: 1\nrelated:\n  - x\n  - y\nb: 2\n---\n"
    assert board_module.edit_frontmatter(text, {"related": None, "missing": None}) == "---\na: 1\nb: 2\n---\n"


def test_edit_keeps_crlf_line_endings():
    text = "---\r\na: 1\r\n---\r\nbody\r\n"
    out = board_module.edit_frontmatter(text, {"claimed": "orchestrate-2"})
    assert out == "---\r\na: 1\r\nclaimed: orchestrate-2\r\n---\r\nbody\r\n"
    assert "\n" not in out.replace("\r\n", "")


@pytest.mark.parametrize("text", ["no frontmatter\n", "---\na: 1\n"])
def test_edit_refuses_a_ticket_it_cannot_parse(text):
    with pytest.raises(board_module.BoardFail):
        board_module.edit_frontmatter(text, {"a": "2"})


def test_quoting_round_trips_through_the_parser():
    for value in ["plain", "has: colon", "#hash", "true", 'say "hi"', "trailing "]:
        text = board_module.edit_frontmatter("---\n---\n", {"k": value})
        assert board_module.br.split_frontmatter(text)[0]["k"] == value.strip()


# ------------------------------------------------------------------ claims


def test_claim_writes_claimed_and_claimed_at_and_release_removes_both(board):
    path = board.ticket("CHECKOUT-001", "backlog", "backlog")
    result, code = board.board("claim", "--run", "orchestrate-1", "CHECKOUT-001")
    assert code == 0 and result["held"]
    assert props(path)["claimed"] == "orchestrate-1"
    assert board_module.parse_property_time(props(path)["claimedAt"]) is not None

    result, _ = board.board("release", "--run", "orchestrate-1")
    assert result["released"] == ["CHECKOUT-001"]
    assert "claimed" not in props(path) and "claimedAt" not in props(path)


def test_claim_loses_to_another_runs_claim_and_rolls_back_its_own_writes(board):
    first = board.ticket("CHECKOUT-001", "backlog", "backlog")
    board.ticket("CHECKOUT-002", "backlog", "backlog", extra="claimed: orchestrate-9\n")
    result, code = board.board("claim", "--run", "run-roadmap-1", "CHECKOUT-001", "CHECKOUT-002")
    assert code == 1 and not result["held"]
    assert result["lost"] == [{"id": "CHECKOUT-002", "claimedBy": "orchestrate-9"}]
    assert "claimed" not in props(first)


def test_claim_writes_nothing_when_any_ticket_is_unwritable(board):
    good = board.ticket("CHECKOUT-001", "backlog", "backlog")
    broken = board.ticket("CHECKOUT-002", "backlog", "backlog")
    broken.write_text(broken.read_text().replace("updatedAt: 2026-11-01T09:00\n---", "updatedAt: 2026-11-01T09:00\n"))
    _, code = board.board("claim", "--run", "orchestrate-1", "CHECKOUT-001", "CHECKOUT-002", check=False)
    assert code == 2
    assert "claimed" not in props(good)


def test_concurrent_claims_have_exactly_one_winner(board):
    for n in range(1, 6):
        board.ticket(f"CHECKOUT-00{n}", "backlog", "backlog")
    ids = [f"CHECKOUT-00{n}" for n in range(1, 6)]
    results = {}

    def claim(run):
        results[run] = board.board("claim", "--run", run, *ids, check=False)[1]

    threads = [threading.Thread(target=claim, args=(f"run-roadmap-{n}",)) for n in range(1, 7)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    winners = [run for run, code in results.items() if code == 0]
    assert len(winners) == 1, results
    claims = {props(board.root / "work" / "backlog" / f"{i}-slug.md")["claimed"] for i in ids}
    assert claims == {winners[0]}


# ------------------------------------------------------------------ run numbers


def test_next_run_skips_claims_of_any_command_and_reserved_numbers(board):
    board.ticket("CHECKOUT-001", "backlog", "backlog", extra='claimed: "orchestrate-1"\n')
    first, _ = board.board("next-run", "--command", "run-roadmap", "--reserve")
    assert first["run"] == "run-roadmap-2"
    assert Path(first["heartbeat"]).exists()
    second, _ = board.board("next-run", "--command", "run-roadmap", "--reserve")
    assert second["run"] == "run-roadmap-3"
    assert (board.root / ".runs" / ".gitignore").read_text() == "*\n"


# ------------------------------------------------------------------ stop


def test_stop_blocks_only_the_runs_in_flight_tickets(board):
    flying = board.ticket("CHECKOUT-001", "in-progress", "in progress", extra="assigned: coding-3\nclaimed: run-roadmap-3\n")
    waiting = board.ticket("CHECKOUT-002", "backlog", "backlog", extra="claimed: run-roadmap-3\n")
    other = board.ticket("CHECKOUT-003", "in-progress", "review", extra="claimed: orchestrate-1\n")

    result, code = board.board("stop", "--run", "run-roadmap-3", "--blocked-by", "session timed out: see log", "--release-rest")
    assert code == 0
    assert [s["id"] for s in result["stopped"]] == ["CHECKOUT-001"]
    assert result["released"] == ["CHECKOUT-002"]

    p = props(flying)
    assert p["status"] == "blocked" and p["blocked_by"] == ["session timed out: see log"]
    assert "assigned" not in p and "claimed" not in p
    worklog = flying.with_name("CHECKOUT-001-slug.worklog.md").read_text()
    assert "— run-roadmap-3 · stop" in worklog and "session timed out" in worklog
    assert "claimed" not in props(waiting)
    assert props(other)["claimed"] == "orchestrate-1" and props(other)["status"] == "review"
    assert "🚫 **Blocked**" in (board.root / "roadmap.md").read_text()


def test_stop_refuses_a_ticket_another_run_holds(board):
    board.ticket("CHECKOUT-001", "in-progress", "in progress", extra="claimed: orchestrate-1\n")
    _, code = board.board("stop", "--run", "run-roadmap-3", "--blocked-by", "x", "CHECKOUT-001", check=False)
    assert code == 2


# ------------------------------------------------------------------ recover


def test_recover_stops_dead_runs_and_spares_live_ones(board):
    dead = board.ticket("CHECKOUT-001", "in-progress", "in progress",
                        extra="claimed: orchestrate-1\nclaimedAt: 2026-01-01T09:00\n")
    dead_waiting = board.ticket("CHECKOUT-002", "backlog", "backlog",
                                extra="claimed: orchestrate-1\nclaimedAt: 2026-01-01T09:00\n")
    live = board.ticket("CHECKOUT-003", "in-progress", "in progress",
                        extra="claimed: run-roadmap-2\nclaimedAt: 2026-01-01T09:00\n")
    heartbeat = board.root / ".runs" / ".live" / "run-roadmap-2"
    heartbeat.parent.mkdir(parents=True)
    heartbeat.touch()
    undated = board.ticket("CHECKOUT-004", "backlog", "backlog", extra="claimed: orchestrate-5\n")

    preview, _ = board.board("recover", "--dry-run")
    assert preview["stopped"][0]["id"] == "CHECKOUT-001" and props(dead)["status"] == "in progress"

    result, _ = board.board("recover")
    assert [s["id"] for s in result["stopped"]] == ["CHECKOUT-001"]
    assert result["released"] == ["CHECKOUT-002"]
    assert [a["id"] for a in result["alive"]] == ["CHECKOUT-003"]
    assert result["undated"] == [{"id": "CHECKOUT-004", "claimed": "orchestrate-5"}]
    assert props(dead)["status"] == "blocked"
    assert "claimed" not in props(dead_waiting)
    assert props(live)["claimed"] == "run-roadmap-2"
    assert props(undated)["claimed"] == "orchestrate-5"


# ------------------------------------------------------------------ ready


def test_ready_offers_unclaimed_backlog_with_done_dependencies_and_resumable_blocked(board):
    board.ticket("CHECKOUT-001", "done", "done")
    board.ticket("CHECKOUT-002", "backlog", "backlog", depends_on=["CHECKOUT-001"])
    board.ticket("CHECKOUT-003", "backlog", "backlog", depends_on=["CHECKOUT-002"])
    board.ticket("CHECKOUT-004", "in-progress", "blocked", extra="blocked_by:\n  - CHECKOUT-001\n")
    board.ticket("CHECKOUT-005", "in-progress", "blocked", extra="blocked_by:\n  - needs a DNS record\n")
    board.ticket("CHECKOUT-006", "backlog", "backlog", extra="claimed: orchestrate-4\n")
    result, _ = board.board("ready")
    ready = {r["id"]: r["resume"] for r in result["ready"]}
    assert ready == {"CHECKOUT-002": False, "CHECKOUT-004": True}
    assert result["remaining"] == 5


# ------------------------------------------------------------------ review follow-ups


LEFTOVERS = """[
  {"title": "Total is NaN on an empty cart", "file": "src/cart/total.ts", "line": "42",
   "problem": "parseTotal returns NaN for an empty cart.", "suggestion": "Return 0 before the reduce.",
   "focus": "correctness", "reason": "raised on the re-review"},
  {"title": "Unused import", "file": "src/cart/cart.ts", "line": "", "problem": "lodash is imported and unused.",
   "suggestion": "", "focus": "conventions", "reason": "a test file"}
]"""


def test_follow_up_creates_a_low_priority_backlog_ticket_in_the_epic_and_claims_it(board):
    board.ticket("CHECKOUT-001", "done", "done")
    board.ticket("CHECKOUT-002", "backlog", "backlog")
    result, code = board.board("follow-up", "--ticket", "CHECKOUT-001", "--run", "run-roadmap-3", "--claim", stdin=LEFTOVERS)
    assert code == 0
    assert result["ticket"]["id"] == "CHECKOUT-003" and result["ticket"]["created"]
    assert result["added"] == ["Total is NaN on an empty cart", "Unused import"] and result["claimed"]

    path = Path(result["ticket"]["path"])
    assert path == board.root / "work" / "backlog" / "CHECKOUT-003-review-follow-ups.md"
    p = props(path)
    assert p["status"] == "backlog" and p["priority"] == "Low" and p["depends_on"] == []
    assert p["follows_up"] == ["CHECKOUT-001"] and p["claimed"] == "run-roadmap-3"
    assert p["feature"] == "[[checkout.feature]]" and p["repositories"] == ["api"]
    text = path.read_text()
    assert "# [CHECKOUT-003] Review follow-ups" in text
    assert "- [ ] **Total is NaN on an empty cart** — `src/cart/total.ts:42`: parseTotal returns NaN" in text
    assert "_(CHECKOUT-001, correctness review; left because raised on the re-review)_" in text
    assert "CHECKOUT-003" in (board.root / "roadmap.md").read_text()


def test_follow_up_appends_to_the_open_one_and_skips_an_issue_already_filed(board):
    board.ticket("CHECKOUT-001", "done", "done")
    board.ticket("CHECKOUT-002", "done", "done")
    first, _ = board.board("follow-up", "--ticket", "CHECKOUT-001", "--run", "run-roadmap-3", stdin=LEFTOVERS)
    more = '[{"title": "Unused import", "file": "src/cart/cart.ts", "problem": "again"},' \
           ' {"title": "Magic number", "file": "src/cart/fee.ts", "line": "7", "problem": "0.3 is unnamed."}]'
    second, _ = board.board("follow-up", "--ticket", "CHECKOUT-002", "--run", "run-roadmap-3", stdin=more)
    assert second["ticket"] == {"id": first["ticket"]["id"], "path": first["ticket"]["path"], "created": False}
    assert second["added"] == ["Magic number"] and second["duplicates"] == ["Unused import"]
    path = Path(first["ticket"]["path"])
    assert props(path)["follows_up"] == ["CHECKOUT-001", "CHECKOUT-002"]
    criteria = [line for line in path.read_text().splitlines() if line.startswith("- [ ]")]
    assert len(criteria) == 3 and criteria[-1].startswith("- [ ] **Magic number**")


def test_follow_up_opens_a_new_ticket_when_the_open_one_is_another_runs(board):
    board.ticket("CHECKOUT-001", "done", "done")
    board.ticket("CHECKOUT-002", "backlog", "backlog", extra="follows_up:\n  - CHECKOUT-009\nclaimed: run-roadmap-1\n")
    result, _ = board.board("follow-up", "--ticket", "CHECKOUT-001", "--run", "run-roadmap-3", stdin=LEFTOVERS)
    assert result["ticket"]["id"] == "CHECKOUT-003" and result["ticket"]["created"]


def test_a_follow_up_tickets_own_leftovers_are_never_filed(board):
    board.ticket("CHECKOUT-001", "done", "done", extra="follows_up:\n  - CHECKOUT-000\n")
    result, code = board.board("follow-up", "--ticket", "CHECKOUT-001", "--run", "run-roadmap-3", stdin=LEFTOVERS)
    assert code == 0 and result["ticket"] is None and "skipped" in result
    assert list((board.root / "work" / "backlog").iterdir()) == []


def test_follow_up_writes_nothing_for_no_issues_and_refuses_an_issue_with_no_problem(board):
    board.ticket("CHECKOUT-001", "done", "done")
    result, code = board.board("follow-up", "--ticket", "CHECKOUT-001", "--run", "run-roadmap-3", stdin="[]")
    assert code == 0 and result["ticket"] is None
    _, code = board.board("follow-up", "--ticket", "CHECKOUT-001", "--run", "run-roadmap-3",
                          stdin='[{"title": "x"}]', check=False)
    assert code == 2
    assert list((board.root / "work" / "backlog").iterdir()) == []
