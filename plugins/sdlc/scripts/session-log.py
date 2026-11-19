#!/usr/bin/env python3
#
# session-log.py — read the stream-json log of one `claude -p` session.
#
# The launcher runs each ticket's session with `--output-format stream-json --verbose`, so the log
# holds every event the session produced, and the last one says how it ended and what it cost. This
# script turns that log into the two things the launcher needs:
#
#   ./session-log.py render < task-01.jsonl          # a readable view: text and tool calls
#   ./session-log.py render --follow task-01.jsonl   # the same, following the log as it grows
#   ./session-log.py result task-01.jsonl            # one JSON object: outcome payload, cost, turns
#
# `result` finds the last `<MARKER> {...}` the session printed — RUN-ROADMAP-RESULT by default — and
# decodes the JSON after it with a real parser, so a brace inside a reason cannot cut it short. It
# reads the final `result` event when there is one, and every assistant text block when the session
# was killed before it got there. A log that is plain text, not stream-json, is searched as text.
#
# Exit codes: 0 read, 2 the log could not be read.

from __future__ import annotations

import argparse
import json
import sys

VERSION = "1.0.0"


def events(lines):
    for raw in lines:
        raw = raw.strip()
        if not raw:
            continue
        try:
            event = json.loads(raw)
        except ValueError:
            yield {"type": "text-line", "text": raw}
            continue
        if isinstance(event, dict):
            yield event


def assistant_texts(event: dict) -> list[str]:
    message = event.get("message") or {}
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, list):
        return []
    return [block.get("text", "") for block in content if isinstance(block, dict) and block.get("type") == "text"]


def find_payload(text: str, marker: str):
    """The JSON object after the last marker in `text`, or None; and why it failed, when it did."""
    decoder = json.JSONDecoder()
    start = text.rfind(marker)
    while start != -1:
        brace = text.find("{", start + len(marker))
        if brace != -1 and not text[start + len(marker):brace].strip():
            try:
                value, _ = decoder.raw_decode(text, brace)
                if isinstance(value, dict):
                    return value, ""
                error = "the marker is followed by JSON that is not an object"
            except ValueError as failure:
                error = f"the JSON after the marker does not parse: {failure}"
        else:
            error = "the marker is not followed by a JSON object"
        previous = text.rfind(marker, 0, start)
        if previous == -1:
            return None, error
        start = previous
    return None, "no marker"


def command_result(args: argparse.Namespace) -> int:
    try:
        with open(args.log, encoding="utf-8", errors="replace") as handle:
            all_events = list(events(handle))
    except OSError as error:
        print(f"cannot read {args.log}: {error}", file=sys.stderr)
        return 2

    final = next((e for e in reversed(all_events) if e.get("type") == "result"), None)
    texts = []
    for event in all_events:
        if event.get("type") == "assistant" and not event.get("parent_tool_use_id"):
            texts += assistant_texts(event)
        elif event.get("type") == "text-line":
            texts.append(event["text"])
    if final and isinstance(final.get("result"), str):
        texts.append(final["result"])

    payload, problem = find_payload("\n".join(texts), args.marker)
    print(json.dumps({
        "payload": payload,
        "payloadProblem": "" if payload is not None else problem,
        "ended": final is not None,
        "subtype": (final or {}).get("subtype", ""),
        "isError": bool((final or {}).get("is_error", False)),
        "costUsd": float((final or {}).get("total_cost_usd") or 0),
        "turns": int((final or {}).get("num_turns") or 0),
        "sessionId": (final or {}).get("session_id", ""),
    }, ensure_ascii=False))
    return 0


def follow(path: str):
    """Yield the lines of a file as it grows, like `tail -f`, until the process is killed."""
    import time
    with open(path, encoding="utf-8", errors="replace") as handle:
        pending = ""
        while True:
            chunk = handle.readline()
            if not chunk:
                time.sleep(0.5)
                continue
            pending += chunk
            if pending.endswith("\n"):
                yield pending
                pending = ""


def command_render(args: argparse.Namespace) -> int:
    source = follow(args.log) if args.follow and args.log else (open(args.log, encoding="utf-8", errors="replace") if args.log else sys.stdin)
    for event in events(source):
        kind = event.get("type")
        if kind == "text-line":
            print(event["text"], flush=True)
        elif kind == "assistant":
            indent = "    " if event.get("parent_tool_use_id") else ""
            for block in (event.get("message") or {}).get("content") or []:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "text" and not indent and block.get("text", "").strip():
                    print(block["text"].rstrip(), flush=True)
                elif block.get("type") == "tool_use":
                    print(f"{indent}  · {block.get('name', 'tool')}", flush=True)
        elif kind == "result":
            cost = event.get("total_cost_usd")
            cost_text = f" · ${cost:.2f}" if isinstance(cost, (int, float)) else ""
            print(f"— session ended: {event.get('subtype', '')}{cost_text} · {event.get('num_turns', '?')} turns", flush=True)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="session-log.py", description="Read the stream-json log of a claude -p session.")
    parser.add_argument("--version", action="version", version=f"session-log.py {VERSION}")
    sub = parser.add_subparsers(dest="action", required=True)
    result = sub.add_parser("result", help="print the session's result payload, cost, and turns as JSON")
    result.add_argument("log")
    result.add_argument("--marker", default="RUN-ROADMAP-RESULT")
    render = sub.add_parser("render", help="print a readable view of a stream-json log")
    render.add_argument("log", nargs="?", help="the log; stdin when left out")
    render.add_argument("--follow", action="store_true", help="keep reading as the log grows")
    args = parser.parse_args(argv)
    try:
        return command_result(args) if args.action == "result" else command_render(args)
    except (BrokenPipeError, KeyboardInterrupt):
        return 0


if __name__ == "__main__":
    sys.exit(main())
