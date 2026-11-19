#!/usr/bin/env python3
#
# guard.py — the plugin's hooks: rules every sdlc agent's definition states, held by code instead of
# by the agent remembering them.
#
#   pre-edit       an Edit or Write by a read-only agent is denied; `test-writer` may write test
#                  files only; `coding` may not change a file `test-writer` wrote in this session
#   post-edit      records each file `test-writer` wrote, which is what `pre-edit` protects
#   pre-bash       no sdlc agent commits, pushes, resets, cleans, or skips a hook — the orchestrator
#                  owns every git write
#   subagent-stop  an agent whose reply carries a ```json block that does not parse, or carries two,
#                  is sent back to re-emit exactly one valid block
#
# Every rule applies only when the hook input names an sdlc subagent (`agent_type` = `sdlc:<name>`).
# A tool call on the main thread, or by another plugin's agent, is never touched. Anything this
# script cannot read lets the call through: the hooks add a guard, they never become a way to break
# a run. A denial exits 2 with the reason on stderr, which Claude Code hands to the agent.

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

READ_ONLY = {
    "plan-reviewer", "code-reviewer", "implementation-planner", "test-planner",
    "cto", "repo-resolver", "verify", "feature-interviewer",
}

TEST_PATH = re.compile(
    r"(^|/)(tests?|__tests__|__mocks__|specs?|e2e|cypress|playwright|fixtures?|test-?utils|testing)(/|$)"
    r"|(^|/)[^/]+\.(test|spec|e2e|cy)\.[^/]+$"
    r"|(^|/)(test_[^/]+|[^/]+_test)\.(py|go|rb|exs?)$"
    r"|(^|/)conftest\.py$"
    r"|(^|/)(playwright|vitest|jest|cypress)\.config\.[cm]?[jt]s$"
    # Standing up an end-to-end suite the project lacks can need a script or a dev dependency.
    r"|(^|/)(package\.json|package-lock\.json|pnpm-lock\.yaml|yarn\.lock|bun\.lockb?)$",
    re.IGNORECASE,
)

GIT_WRITE = re.compile(
    r"\bgit\b[^;&|\n]*?\s(commit|push|merge|rebase|reset\s+--hard|clean\s+-[a-z]*f[a-z]*|update-ref|"
    r"checkout\s+--|restore\b|stash|tag|branch\s+-[dDmM]|worktree\s+(add|remove|prune))\b"
    r"|--no-verify\b"
)

JSON_FENCE = re.compile(r"^```json[ \t]*$", re.MULTILINE)


def deny(reason: str) -> int:
    print(reason, file=sys.stderr)
    return 2


def sdlc_agent(event: dict) -> str:
    agent = str(event.get("agent_type") or "")
    return agent.split(":", 1)[1] if agent.startswith("sdlc:") else ""


def edited_path(event: dict) -> str:
    tool_input = event.get("tool_input") or {}
    raw = str(tool_input.get("file_path") or tool_input.get("notebook_path") or "")
    if not raw:
        return ""
    path = Path(raw)
    if not path.is_absolute():
        path = Path(str(event.get("cwd") or os.getcwd())) / path
    return os.path.normpath(str(path))


def ledger(event: dict) -> Path | None:
    """Where this session's test-writer files are recorded: the plugin's data folder, by session."""
    base = os.environ.get("CLAUDE_PLUGIN_DATA") or os.path.join(Path.home(), ".claude", "sdlc-hooks")
    session = re.sub(r"[^A-Za-z0-9_.-]", "", str(event.get("session_id") or ""))
    if not session:
        return None
    return Path(base) / "test-writer-files" / f"{session}.txt"


def protected(event: dict) -> set[str]:
    path = ledger(event)
    try:
        return set(path.read_text(encoding="utf-8").splitlines()) if path else set()
    except OSError:
        return set()


def pre_edit(event: dict) -> int:
    agent = sdlc_agent(event)
    if not agent:
        return 0
    path = edited_path(event)
    if agent in READ_ONLY:
        return deny(f"The {agent} agent writes no file — its definition says it returns a result only. "
                    "Put what you meant to write in your reply instead.")
    if agent == "test-writer" and path and not TEST_PATH.search(path):
        return deny(f"test-writer writes test files only, and {path} does not look like one. If a case "
                    "needs production code to exist, report it as a case you cannot write. If this file "
                    "is a test helper in an unusual place, say so in your reply and name the path.")
    if agent == "coding" and path and path in protected(event):
        return deny(f"{path} was written by test-writer in this run, and coding never changes a written "
                    "test. If the test is wrong, finish the rest and return a test dispute instead.")
    return 0


def post_edit(event: dict) -> int:
    if sdlc_agent(event) != "test-writer":
        return 0
    path, store = edited_path(event), ledger(event)
    if not path or store is None or path in protected(event):
        return 0
    try:
        store.parent.mkdir(parents=True, exist_ok=True)
        with store.open("a", encoding="utf-8") as handle:
            handle.write(path + "\n")
    except OSError:
        pass
    return 0


def pre_bash(event: dict) -> int:
    agent = sdlc_agent(event)
    if not agent:
        return 0
    command = str((event.get("tool_input") or {}).get("command") or "")
    if GIT_WRITE.search(command):
        return deny(f"The {agent} agent makes no git write — the orchestrator owns every commit, reset, "
                    "and branch, and no hook is ever skipped. Report what you need done in your reply.")
    return 0


def subagent_stop(event: dict) -> int:
    if not sdlc_agent(event) or event.get("stop_hook_active"):
        return 0
    message = str(event.get("last_assistant_message") or "")
    fences = list(JSON_FENCE.finditer(message))
    if not fences:
        return 0  # A pre-read or spec-only turn ends with no block; the orchestrator asks when one is due.
    if len(fences) > 1:
        return deny("Your reply carries more than one ```json block. End it with exactly one — the result "
                    "block your agent definition specifies — and nothing after it.")
    body = message[fences[0].end():]
    closing = body.find("\n```")
    if closing == -1:
        return deny("Your ```json block is never closed. Re-emit only the result block, complete.")
    try:
        value = json.loads(body[:closing])
    except ValueError as error:
        return deny(f"Your ```json block does not parse ({error}). Re-emit only the result block, as valid JSON.")
    if not isinstance(value, dict):
        return deny("Your ```json block must be one JSON object, as your agent definition specifies. Re-emit it.")
    return 0


HANDLERS = {"pre-edit": pre_edit, "post-edit": post_edit, "pre-bash": pre_bash, "subagent-stop": subagent_stop}


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] not in HANDLERS:
        print(f"usage: guard.py {{{'|'.join(HANDLERS)}}} < hook-input.json", file=sys.stderr)
        return 1
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    if not isinstance(event, dict):
        return 0
    try:
        return HANDLERS[argv[1]](event)
    except Exception:  # A guard that crashes must never be what stops a run.
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
