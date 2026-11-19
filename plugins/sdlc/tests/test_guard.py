"""hooks/guard.py: each rule, and that nothing outside an sdlc subagent is ever touched."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import PLUGIN

GUARD = PLUGIN / "hooks" / "guard.py"


def hook(action: str, event: dict, tmp_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(GUARD), action], input=json.dumps(event), capture_output=True, text=True,
        env={"CLAUDE_PLUGIN_DATA": str(tmp_path / "data"), "PATH": "/usr/bin:/bin"},
    )


def edit(agent: str | None, path: str, session: str = "s1") -> dict:
    event = {"session_id": session, "cwd": "/work", "tool_name": "Write", "tool_input": {"file_path": path}}
    if agent:
        event["agent_type"] = agent
    return event


def test_hooks_json_is_valid_and_points_at_the_guard():
    config = json.loads((PLUGIN / "hooks" / "hooks.json").read_text())
    commands = [h["command"] for groups in config["hooks"].values() for g in groups for h in g["hooks"]]
    assert commands and all("${CLAUDE_PLUGIN_ROOT}/hooks/guard.py" in c for c in commands)
    for command in commands:
        assert command.split()[-1] in ("pre-edit", "post-edit", "pre-bash", "subagent-stop")


@pytest.mark.parametrize("agent", [None, "Explore", "other-plugin:coding", "sdlc:coding"])
def test_main_thread_and_other_agents_may_write_anything(agent, tmp_path):
    assert hook("pre-edit", edit(agent, "/work/src/app.ts"), tmp_path).returncode == 0


@pytest.mark.parametrize("agent", ["sdlc:plan-reviewer", "sdlc:code-reviewer", "sdlc:cto", "sdlc:verify"])
def test_read_only_agents_cannot_write(agent, tmp_path):
    result = hook("pre-edit", edit(agent, "/work/src/app.ts"), tmp_path)
    assert result.returncode == 2 and "writes no file" in result.stderr


@pytest.mark.parametrize("path, allowed", [
    ("/work/src/cart.test.ts", True),
    ("/work/tests/e2e/checkout.spec.ts", True),
    ("/work/api/test_cart.py", True),
    ("/work/pkg/cart_test.go", True),
    ("/work/playwright.config.ts", True),
    ("/work/package.json", True),
    ("/work/src/cart.ts", False),
    ("/work/src/contest.ts", False),
])
def test_test_writer_writes_test_files_only(path, allowed, tmp_path):
    result = hook("pre-edit", edit("sdlc:test-writer", path), tmp_path)
    assert (result.returncode == 0) is allowed, result.stderr


def test_coding_cannot_change_a_file_test_writer_wrote_in_the_same_session(tmp_path):
    written = "/work/src/cart.test.ts"
    assert hook("post-edit", edit("sdlc:test-writer", written), tmp_path).returncode == 0
    blocked = hook("pre-edit", edit("sdlc:coding", written), tmp_path)
    assert blocked.returncode == 2 and "test dispute" in blocked.stderr
    assert hook("pre-edit", edit("sdlc:coding", "/work/src/cart.ts"), tmp_path).returncode == 0
    assert hook("pre-edit", edit("sdlc:coding", written, session="other"), tmp_path).returncode == 0


@pytest.mark.parametrize("command, allowed", [
    ("git -C /w diff HEAD", True),
    ("git log --oneline -20", True),
    ("bun test src/cart.test.ts", True),
    ("git -C /w commit -m x", False),
    ("cd /w && git push origin main", False),
    ("git reset --hard HEAD", False),
    ("git clean -fd", False),
    ("npm run lint -- --no-verify", False),
])
def test_sdlc_agents_make_no_git_write(command, allowed, tmp_path):
    event = {"agent_type": "sdlc:coding", "session_id": "s1", "tool_input": {"command": command}}
    assert (hook("pre-bash", event, tmp_path).returncode == 0) is allowed
    del event["agent_type"]
    assert hook("pre-bash", event, tmp_path).returncode == 0


@pytest.mark.parametrize("message, allowed", [
    ("Pre-read done.", True),
    ("Summary\n\n```json\n{\"verdict\": \"APPROVED\"}\n```\n", True),
    ("```json\n{\"verdict\": \"APPROVED\",}\n```", False),
    ("```json\n[1, 2]\n```", False),
    ("```json\n{}\n```\nand\n```json\n{}\n```", False),
    ("```json\n{\"a\": 1}\n", False),
])
def test_subagent_stop_checks_the_result_block(message, allowed, tmp_path):
    event = {"agent_type": "sdlc:plan-reviewer", "last_assistant_message": message, "stop_hook_active": False}
    assert (hook("subagent-stop", event, tmp_path).returncode == 0) is allowed
    event["stop_hook_active"] = True
    assert hook("subagent-stop", event, tmp_path).returncode == 0


def test_unreadable_input_lets_the_call_through(tmp_path):
    result = subprocess.run([sys.executable, str(GUARD), "pre-edit"], input="not json", capture_output=True, text=True)
    assert result.returncode == 0
