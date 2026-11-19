"""Fixtures shared by the script tests: a small board on disk, and a way to run each script."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

PLUGIN = Path(__file__).resolve().parent.parent
SCRIPTS = PLUGIN / "scripts"


def ticket_text(status: str, depends_on: list[str] | None = None, extra: str = "", title: str = "A ticket") -> str:
    deps = "[]" if not depends_on else "\n" + "".join(f"  - {d}\n" for d in depends_on).rstrip("\n")
    return (
        "---\n"
        'feature: "[[checkout.feature]]"\n'
        f"status: {status}\n"
        "priority: High\n"
        "repositories:\n  - api\n"
        f"depends_on: {deps}\n"
        f"{extra}"
        "createdAt: 2026-11-01T09:00\n"
        "updatedAt: 2026-11-01T09:00\n"
        "---\n\n"
        f"# [CHECKOUT-000] {title}\n\n## Description\n\nBody.\n"
    )


class BoardFixture:
    def __init__(self, root: Path) -> None:
        self.root = root

    def ticket(self, ticket_id: str, bucket: str, status: str, depends_on=None, extra: str = "") -> Path:
        path = self.root / "work" / bucket / f"{ticket_id}-slug.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(ticket_text(status, depends_on, extra).replace("CHECKOUT-000", ticket_id), encoding="utf-8")
        return path

    def run(self, script: str, *args: str, check: bool = True) -> subprocess.CompletedProcess:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / script), *args],
            capture_output=True, text=True, cwd=self.root,
        )
        if check and result.returncode not in (0, 1):
            raise AssertionError(f"{script} {args} exited {result.returncode}\n{result.stderr}")
        return result

    def board(self, *args: str, check: bool = True) -> tuple[dict, int]:
        result = self.run("board.py", *args, "--root", str(self.root), check=check)
        return (json.loads(result.stdout) if result.stdout.strip() else {}), result.returncode


@pytest.fixture
def board(tmp_path: Path) -> BoardFixture:
    root = tmp_path / "vault"
    (root / "features" / "checkout").mkdir(parents=True)
    (root / "work" / "backlog").mkdir(parents=True)
    (root / "work" / "in-progress").mkdir(parents=True)
    (root / "work" / "done").mkdir(parents=True)
    (root / "sdlc.json").write_text(json.dumps({"repositories": {}}), encoding="utf-8")
    (root / "glossary.md").write_text("# Glossary\n", encoding="utf-8")
    (root / "features" / "checkout" / "checkout.feature.md").write_text(
        "---\ntype: feature\ncode: CHECKOUT\nname: Checkout\n---\n\n# Checkout\n\nPay for a cart.\n", encoding="utf-8"
    )
    (root / "roadmap.md").write_text(
        "---\nupdated: 2026-11-01\n---\n\n# Roadmap\n\n## CHECKOUT — Checkout\n\n", encoding="utf-8"
    )
    return BoardFixture(root)
