"""run-roadmap.sh driven by a fake `claude`: every way a ticket can end, and what the launcher does."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from conftest import PLUGIN, SCRIPTS, ticket_text

FAKE = Path(__file__).resolve().parent / "fake-claude"


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True, text=True).stdout.strip()


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "config", "user.name", "Test")
    (repo / "README.md").write_text("repo\n")
    git(repo, "add", "README.md")
    git(repo, "commit", "-qm", "init")
    root = repo / ".sdlc"
    for bucket in ("backlog", "in-progress", "done"):
        (root / "work" / bucket).mkdir(parents=True)
    (root / "features" / "checkout").mkdir(parents=True)
    (root / "glossary.md").write_text("# Glossary\n")
    (root / "features" / "checkout" / "checkout.feature.md").write_text(
        "---\ntype: feature\ncode: CHECKOUT\nname: Checkout\n---\n\n# Checkout\n")
    (root / "roadmap.md").write_text("---\nupdated: 2026-11-01\n---\n\n# Roadmap\n\n## CHECKOUT — Checkout\n\n")
    for n in (1, 2):
        (root / "work" / "backlog" / f"CHECKOUT-00{n}-slug.md").write_text(
            ticket_text("backlog").replace("CHECKOUT-000", f"CHECKOUT-00{n}"))
    (repo / ".git" / "info" / "exclude").write_text(".sdlc/\n")
    return repo


def launch(repo: Path, scenario: str, *args: str, timeout: int = 90) -> subprocess.CompletedProcess:
    env = {
        **os.environ,
        "PATH": f"{FAKE}:{os.environ['PATH']}",
        "FAKE_SCENARIO": scenario,
        "FAKE_REPO": str(repo),
        "FAKE_ROOT": str(repo / ".sdlc"),
        "FAKE_BOARD": str(SCRIPTS / "board.py"),
        "FAKE_ARGS_LOG": str(repo.parent / "claude-args.log"),
    }
    env.pop("SDLC_NOTIFY", None)
    return subprocess.run(
        ["bash", str(SCRIPTS / "run-roadmap.sh"), "--yes", *args],
        cwd=repo, env=env, capture_output=True, text=True, timeout=timeout,
    )


def frontmatter(path: Path) -> str:
    return path.read_text().split("---")[1]


def test_a_missing_option_value_fails_fast(repo):
    result = launch(repo, "completed", "--max", timeout=10)
    assert result.returncode == 1 and "--max needs a value" in result.stderr


def test_a_bad_run_name_is_refused(repo):
    result = launch(repo, "completed", "--run", "3a4", timeout=10)
    assert result.returncode == 1


def test_completed_ticket_reaches_max_and_passes_the_limits_to_claude(repo):
    result = launch(repo, "completed", "--max", "1", "--notify", "printf '%s|%s' \"$1\" \"$SDLC_RUN\" > ../notified")
    assert result.returncode == 0, result.stderr + result.stdout
    assert "reached --max 1" in result.stdout and "$1.25" in result.stdout
    args = (repo.parent / "claude-args.log").read_text()
    for flag in ("--output-format stream-json", "--permission-mode auto", "--permission-prompts none"):
        assert flag in args
    assert "budget" not in args
    assert (repo.parent / "notified").read_text() == "0|run-roadmap-1"
    logs = list((repo / ".sdlc" / ".runs" / "logs").glob("run-roadmap-1-*/summary.txt"))
    assert logs and "\033" not in logs[0].read_text()
    assert not (repo / ".sdlc" / ".runs" / ".live" / "run-roadmap-1").exists(), "heartbeat left behind"


def test_a_commit_no_run_branch_holds_stops_the_run(repo):
    result = launch(repo, "bogus-commit")
    assert result.returncode == 3 and "deadbeef" in result.stdout


def test_human_required_stops_with_exit_3(repo):
    result = launch(repo, "human")
    assert result.returncode == 3 and "the CTO needs a person" in result.stdout


def test_a_dead_session_is_stopped_and_its_work_set_aside(repo):
    scenario, expected = "no-line", "no valid RUN-ROADMAP-RESULT line"
    result = launch(repo, scenario)
    assert result.returncode == 4, result.stderr + result.stdout
    assert expected in result.stdout
    ticket = repo / ".sdlc" / "work" / "in-progress" / "CHECKOUT-001-slug.md"
    fm = frontmatter(ticket)
    assert "status: blocked" in fm and "claimed" not in fm
    other = repo / ".sdlc" / "work" / "backlog" / "CHECKOUT-002-slug.md"
    assert "claimed" not in frontmatter(other)
    worktree = repo.parent / "repo-worktrees" / "run-roadmap-1"
    assert git(worktree, "status", "--porcelain") == ""
    saved = git(worktree, "show", "refs/sdlc-wip/run-roadmap-1/task-01:half.txt")
    assert saved == "half"
    assert "set aside" in result.stdout


def test_a_hung_session_is_killed_at_the_timeout(repo):
    result = launch(repo, "hang", "--timeout", "5", timeout=60)
    assert result.returncode == 4 and "timed out after 5s" in result.stdout
    assert "status: blocked" in frontmatter(repo / ".sdlc" / "work" / "in-progress" / "CHECKOUT-001-slug.md")


def test_dry_run_reserves_nothing(repo):
    result = launch(repo, "completed", "--dry-run", timeout=20)
    assert result.returncode == 0 and "--output-format" in result.stdout
    assert not (repo / ".sdlc" / ".runs" / ".live").exists()
