#!/usr/bin/env bash
#
# run-roadmap.sh — drive a whole roadmap with no person in the loop.
#
# One task per Claude session: the script calls `claude -p "/sdlc:run-roadmap"` in a loop, reads the
# RUN-ROADMAP-RESULT line that command prints, and decides whether to start another task. A fresh
# session per task is the point — a long roadmap never runs out of context, and each task lands as
# its own commit.
#
# The command answers every question with the `cto` agent, so nothing in this loop waits for input.
# It stops on its own when the roadmap is empty, when the CTO hands a decision back to a person, or
# when an agent dies.
#
#   ./run-roadmap.sh --max-tasks 5
#   ./run-roadmap.sh --roadmap docs/roadmap.md --keep-going --yes
#   ./run-roadmap.sh --docs-root ~/Vaults/Personal/Acme        # one board, several repositories
#
# Run it from the repository you want built, or from the docs root — the folder in your Obsidian
# vault that holds the roadmap — when one board drives several repositories. In that shape the
# script reads sdlc.json for the repositories, gives the session access to each one, and checks
# every tree between tasks. Use --help for every option.

set -uo pipefail

VERSION="1.1.0"

# ---------------------------------------------------------------------------- defaults

COMMAND="/sdlc:run-roadmap"
ROADMAP=""
DOCS_ROOT=""                 # set by --docs-root, or detected from the working directory
MODE=""                      # repo (cwd is the code) or vault (cwd is the docs root)
WORK_ROOTS=""                # one absolute repository path per line
MAX_TASKS=0                  # 0 = until the roadmap is empty
PERMISSION_MODE="bypassPermissions"
MODEL=""
LOG_DIR=""
TIMEOUT=5400                 # per task, seconds. 0 = no limit
KEEP_GOING=0
ALLOW_DIRTY=0
ASSUME_YES=0
DRY_RUN=0
QUIET=0

TASKS_DONE=0
TASKS_DEFERRED=0
STOP_REASON=""
EXIT_CODE=0

# ---------------------------------------------------------------------------- output

is_tty() { [ -t 1 ]; }

if is_tty; then
  C_RESET=$'\033[0m'; C_BOLD=$'\033[1m'
  C_RED=$'\033[31m'; C_GREEN=$'\033[32m'; C_YELLOW=$'\033[33m'; C_BLUE=$'\033[34m'
else
  C_RESET=""; C_BOLD=""; C_RED=""; C_GREEN=""; C_YELLOW=""; C_BLUE=""
fi

log()   { [ "$QUIET" -eq 1 ] && return 0; printf '%s\n' "$*"; }
info()  { log "${C_BLUE}==>${C_RESET} $*"; }
ok()    { log "${C_GREEN}==>${C_RESET} $*"; }
warn()  { printf '%s\n' "${C_YELLOW}warning:${C_RESET} $*" >&2; }
die()   { printf '%s\n' "${C_RED}error:${C_RESET} $1" >&2; exit "${2:-1}"; }

usage() {
  cat <<'EOF'
run-roadmap.sh — build a whole roadmap with no person in the loop.

USAGE
  run-roadmap.sh [options]

WHAT IT DOES
  Calls `claude -p "/sdlc:run-roadmap"` once per roadmap task, in a fresh session each time. That
  command picks the next task, has the `cto` agent answer every question a person would normally
  answer, drives plan -> review -> implement -> verify -> code review, commits the task, and prints
  one RUN-ROADMAP-RESULT line. This script reads that line and starts the next task, or stops.

WHERE YOU RUN IT
  From a code repository, and it builds that repository.
  From a docs root — the folder in your vault holding roadmap.md, tickets/ and sdlc.json — and it
  builds every repository sdlc.json names, one task at a time, each task committed in whichever
  repository it landed in. The session is given access to each of them with --add-dir.

OPTIONS
  --max-tasks N        Stop after N tasks. Default: 0, meaning until the roadmap is empty.
  --roadmap PATH       Roadmap file to pass to the command. Default: the project's own docs root.
  --docs-root PATH     The folder holding the roadmap, the tickets, and sdlc.json — a folder in
                       your Obsidian vault. Runs the loop from there, over every repository
                       sdlc.json names. Default: detected from the working directory.
  --model NAME         Model for the main session (the agents pick their own). Default: your config.
  --permission-mode M  Claude permission mode. Default: bypassPermissions, which is what an
                       unattended run needs — a prompt in a headless session is a dead run.
  --timeout SECONDS    Kill a task that runs longer than this. Default: 5400. 0 disables it.
  --log-dir DIR        Where the per-task logs go. Default: a timestamped folder under TMPDIR.
                       It must sit outside the repository, or be git-ignored: each task commits
                       with 'git add -A' and would otherwise commit the logs.
  --keep-going         Carry on to the next task when one is deferred or handed back.
                       Without it, anything other than a completed task stops the run.
  --allow-dirty        Do not require a clean working tree before starting.
  --command NAME       Slash command to run. Default: /sdlc:run-roadmap.
  --yes, -y            Skip the confirmation prompt. Required on a non-interactive shell.
  --dry-run            Print the command for the first task and exit.
  --quiet, -q          Only print the final summary.
  --version            Print the version and exit.
  --help, -h           Print this help and exit.

BEFORE YOU RUN IT
  This writes code and commits it without asking. It commits to the branch each repository is on
  and never pushes. Be on branches you are happy to throw away, with clean trees, and read the
  commits afterwards — a CTO agent made every product decision in them.

EXIT CODES
  0  The roadmap is empty, or --max-tasks was reached.
  1  Preflight failed: no claude, no git, a dirty tree, an unreadable registry, or a bad option.
  3  The run stopped early: a hand-back, an abort, or a blocked task.
  4  A task produced no result line, or timed out.
EOF
}

# ---------------------------------------------------------------------------- options

while [ $# -gt 0 ]; do
  case "$1" in
    --max-tasks)       MAX_TASKS="${2:-}"; shift 2 ;;
    --roadmap)         ROADMAP="${2:-}"; shift 2 ;;
    --docs-root)       DOCS_ROOT="${2:-}"; shift 2 ;;
    --model)           MODEL="${2:-}"; shift 2 ;;
    --permission-mode) PERMISSION_MODE="${2:-}"; shift 2 ;;
    --timeout)         TIMEOUT="${2:-}"; shift 2 ;;
    --log-dir)         LOG_DIR="${2:-}"; shift 2 ;;
    --command)         COMMAND="${2:-}"; shift 2 ;;
    --keep-going)      KEEP_GOING=1; shift ;;
    --allow-dirty)     ALLOW_DIRTY=1; shift ;;
    -y|--yes)          ASSUME_YES=1; shift ;;
    --dry-run)         DRY_RUN=1; shift ;;
    -q|--quiet)        QUIET=1; shift ;;
    --version)         printf 'run-roadmap.sh %s\n' "$VERSION"; exit 0 ;;
    -h|--help)         usage; exit 0 ;;
    *)                 usage >&2; die "unknown option: $1" 1 ;;
  esac
done

case "$MAX_TASKS" in ''|*[!0-9]*) die "--max-tasks needs a whole number" 1 ;; esac
case "$TIMEOUT"   in ''|*[!0-9]*) die "--timeout needs a whole number of seconds" 1 ;; esac

# ---------------------------------------------------------------------------- preflight

command -v claude >/dev/null 2>&1 || die "claude is not on PATH. Install Claude Code first." 1
command -v git    >/dev/null 2>&1 || die "git is not on PATH." 1

# expand_tilde <path> — a leading ~ is the user's home, as sdlc.json may write it.
expand_tilde() {
  case "$1" in
    "~") printf '%s' "$HOME" ;;
    "~/"*) printf '%s/%s' "$HOME" "${1#\~/}" ;;
    *) printf '%s' "$1" ;;
  esac
}

# is_docs_root <dir> — the folder holding the board: sdlc.json, or a roadmap beside tickets/.
is_docs_root() {
  [ -f "$1/sdlc.json" ] && return 0
  { [ -f "$1/roadmap.md" ] || [ -f "$1/prd.md" ]; } && [ -d "$1/tickets" ] && return 0
  return 1
}

# registry_paths <docs root> — one repository path per line, from sdlc.json.
registry_paths() {
  reg="$1/sdlc.json"
  [ -f "$reg" ] || return 0
  if [ -n "$JQ" ]; then
    "$JQ" -r '.repos // {} | to_entries[] | (if (.value|type) == "string" then .value else .value.path end)' \
      "$reg" 2>/dev/null && return 0
  fi
  if command -v python3 >/dev/null 2>&1; then
    python3 - "$reg" <<'PYEOF' 2>/dev/null && return 0
import json, sys
repos = json.load(open(sys.argv[1])).get("repos", {})
for v in repos.values():
    print(v if isinstance(v, str) else v.get("path", ""))
PYEOF
  fi
  die "cannot read $reg — install jq or python3, or pass the repository as the working directory." 1
}

JQ=""
command -v jq >/dev/null 2>&1 && JQ="$(command -v jq)"

# ---------------------------------------------------------------------------- which end are we at

if [ -n "$DOCS_ROOT" ]; then
  DOCS_ROOT="$(expand_tilde "$DOCS_ROOT")"
  [ -d "$DOCS_ROOT" ] || die "--docs-root is not a directory: $DOCS_ROOT" 1
  DOCS_ROOT="$(cd "$DOCS_ROOT" && pwd)"
  is_docs_root "$DOCS_ROOT" \
    || die "$DOCS_ROOT holds no board — expected sdlc.json, or roadmap.md beside tickets/.
Run /setup there first." 1
  MODE="vault"
elif is_docs_root "$PWD" && ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  # A board inside a code repository belongs to that repository — that is a repo-rooted run.
  DOCS_ROOT="$PWD"
  MODE="vault"
else
  MODE="repo"
fi

if [ "$MODE" = "vault" ]; then
  cd "$DOCS_ROOT" || die "cannot enter the docs root" 1
  WORK_ROOTS="$(registry_paths "$DOCS_ROOT")"
  [ -n "$WORK_ROOTS" ] \
    || die "no repository in $DOCS_ROOT/sdlc.json. Run /setup from each repository this product is
built in, so the registry names it." 1
  resolved=""
  while IFS= read -r wr; do
    [ -n "$wr" ] || continue
    wr="$(expand_tilde "$wr")"
    case "$wr" in /*) ;; *) wr="$DOCS_ROOT/$wr" ;; esac
    [ -d "$wr" ] || die "a repository in sdlc.json does not exist here: $wr
The registry is machine-local — run /setup on this machine." 1
    wr="$(cd "$wr" && pwd)"
    git -C "$wr" rev-parse --is-inside-work-tree >/dev/null 2>&1 \
      || die "not a git work tree: $wr. Every task is committed, so this needs git." 1
    resolved="${resolved}${wr}
"
  done <<EOF
$WORK_ROOTS
EOF
  WORK_ROOTS="$resolved"
else
  git rev-parse --is-inside-work-tree >/dev/null 2>&1 \
    || die "not inside a git work tree, and no board here either. Run this from the repository you
want built, or from your docs root — or pass --docs-root." 1
  REPO_ROOT="$(git rev-parse --show-toplevel)"
  cd "$REPO_ROOT" || die "cannot enter the repository root" 1
  WORK_ROOTS="$REPO_ROOT
"
fi

# dirty_roots — prints every work root with uncommitted changes.
dirty_roots() {
  while IFS= read -r wr; do
    [ -n "$wr" ] || continue
    [ -n "$(git -C "$wr" status --porcelain 2>/dev/null)" ] && printf '%s\n' "$wr"
  done <<EOF
$WORK_ROOTS
EOF
  return 0
}

if [ "$ALLOW_DIRTY" -eq 0 ]; then
  DIRTY="$(dirty_roots)"
  if [ -n "$DIRTY" ]; then
    printf '%s\n' "${C_RED}error:${C_RESET} a working tree is not clean." >&2
    while IFS= read -r wr; do
      [ -n "$wr" ] || continue
      printf '\n%s\n' "  $wr" >&2
      git -C "$wr" status --short >&2
    done <<EOF
$DIRTY
EOF
    printf '%s\n' "Each task is committed with 'git add -A', so these changes would land in it." >&2
    printf '%s\n' "Commit or stash them, or pass --allow-dirty." >&2
    exit 1
  fi
fi

RUN_ROOT="${DOCS_ROOT:-$REPO_ROOT}"
BRANCH="$(git -C "$(printf '%s' "$WORK_ROOTS" | head -n 1)" rev-parse --abbrev-ref HEAD 2>/dev/null || printf 'DETACHED')"
START_COMMIT="$(git -C "$(printf '%s' "$WORK_ROOTS" | head -n 1)" rev-parse --short HEAD 2>/dev/null || printf 'none')"

if [ -z "$LOG_DIR" ]; then
  LOG_DIR="${TMPDIR:-/tmp}/sdlc-run-roadmap/$(basename "$RUN_ROOT")-$(date -u '+%Y%m%dT%H%M%SZ')"
fi
mkdir -p "$LOG_DIR" || die "cannot create the log directory: $LOG_DIR" 1
LOG_DIR="$(cd "$LOG_DIR" && pwd)"

# A log directory inside a repository would be swept into a task's own commit by `git add -A`.
while IFS= read -r wr; do
  [ -n "$wr" ] || continue
  case "$LOG_DIR/" in
    "$wr"/*)
      git -C "$wr" check-ignore -q "$LOG_DIR" 2>/dev/null \
        || die "the log directory sits inside a repository and git does not ignore it:
       $LOG_DIR
Each task commits with 'git add -A', so the logs would land in it. Add the path to .gitignore,
or pass --log-dir with a path outside $wr." 1
      ;;
  esac
done <<EOF
$WORK_ROOTS
EOF

# The starting commit of every repository, so the summary can report what each one gained.
START_COMMITS="$LOG_DIR/.start-commits"
: >"$START_COMMITS"
while IFS= read -r wr; do
  [ -n "$wr" ] || continue
  printf '%s\t%s\n' "$wr" "$(git -C "$wr" rev-parse --short HEAD 2>/dev/null || printf 'none')" >>"$START_COMMITS"
done <<EOF
$WORK_ROOTS
EOF
SUMMARY="$LOG_DIR/summary.tsv"
printf 'task\toutcome\ttaskId\tcommit\tremaining\treason\n' >"$SUMMARY"

# ---------------------------------------------------------------------------- the command line

build_prompt() {
  if [ -n "$ROADMAP" ]; then printf '%s %s' "$COMMAND" "$ROADMAP"; else printf '%s' "$COMMAND"; fi
}

claude_argv() {
  # Prints one argument per line, so the caller can read them without word splitting.
  printf '%s\n' "claude" "-p" "$(build_prompt)" "--permission-mode" "$PERMISSION_MODE"
  [ -n "$MODEL" ] && printf '%s\n' "--model" "$MODEL"
  # The session starts in the docs root, so every repository it writes to has to be granted.
  if [ "$MODE" = "vault" ]; then
    while IFS= read -r wr; do
      [ -n "$wr" ] || continue
      printf '%s\n' "--add-dir" "$wr"
    done <<EOF
$WORK_ROOTS
EOF
  fi
  return 0
}

if [ "$DRY_RUN" -eq 1 ]; then
  info "would run, once per task, until the roadmap is empty:"
  claude_argv | sed 's/^/    /'
  info "logs would go to $LOG_DIR"
  exit 0
fi

# ---------------------------------------------------------------------------- confirmation

if [ "$ASSUME_YES" -eq 0 ]; then
  if ! is_tty; then
    die "this is not an interactive shell, so pass --yes to confirm an unattended run." 1
  fi
  cat <<EOF
${C_BOLD}An autonomous run is about to start.${C_RESET}

  board             ${DOCS_ROOT:-$REPO_ROOT}
  repositories      $(printf '%s' "$WORK_ROOTS" | sed '/^$/d' | paste -sd ', ' - 2>/dev/null || printf '%s' "$WORK_ROOTS")
  branch            $BRANCH (at $START_COMMIT)
  permission mode   $PERMISSION_MODE
  tasks             $([ "$MAX_TASKS" -eq 0 ] && printf 'until the roadmap is empty' || printf '%s at most' "$MAX_TASKS")
  logs              $LOG_DIR

It writes code, runs your test suite, and commits one commit per finished task, in whichever
repository that task landed in, on the branch each one is on.
A ${C_BOLD}cto${C_RESET} agent makes every product decision instead of you. Nothing is pushed.
EOF
  printf 'Type yes to start: '
  read -r reply
  [ "$reply" = "yes" ] || die "cancelled" 1
fi

# ---------------------------------------------------------------------------- running one task

CURRENT_TASK_PID=""

# stop_tree <pid> — end a task and everything it started, politely first.
stop_tree() {
  kill -TERM "-$1" 2>/dev/null || kill -TERM "$1" 2>/dev/null
  sleep 5
  kill -KILL "-$1" 2>/dev/null || kill -KILL "$1" 2>/dev/null
  return 0
}

on_interrupt() {
  trap - INT TERM
  printf '\n%s\n' "${C_YELLOW}interrupted${C_RESET} — stopping the task that is running" >&2
  [ -n "$CURRENT_TASK_PID" ] && stop_tree "$CURRENT_TASK_PID"
  printf '%s\n' "Logs are in $LOG_DIR. A repository may hold a half-built task — check each one." >&2
  exit 130
}
trap on_interrupt INT TERM

# run_task <log file> — runs claude, honouring TIMEOUT. Returns claude's status, or 124 on timeout.
run_task() {
  task_log="$1"
  argv_file="$LOG_DIR/.argv"
  claude_argv >"$argv_file"

  # Read the argv lines into a bash 3.2 friendly array.
  cmd=()
  while IFS= read -r line; do cmd+=("$line"); done <"$argv_file"
  rm -f "$argv_file"

  # Job control puts the task in its own process group, so a timeout or a Ctrl-C takes down whatever
  # it started — a test runner, a dev server — instead of orphaning it.
  set -m
  "${cmd[@]}" >"$task_log" 2>&1 &
  claude_pid=$!
  set +m
  CURRENT_TASK_PID="$claude_pid"

  tail_pid=""
  if [ "$QUIET" -eq 0 ] && is_tty; then
    tail -f "$task_log" 2>/dev/null &
    tail_pid=$!
  fi

  waited=0
  status=0
  while kill -0 "$claude_pid" 2>/dev/null; do
    if [ "$TIMEOUT" -gt 0 ] && [ "$waited" -ge "$TIMEOUT" ]; then
      warn "task exceeded ${TIMEOUT}s — stopping it"
      stop_tree "$claude_pid"
      wait "$claude_pid" 2>/dev/null
      status=124
      break
    fi
    sleep 5
    waited=$((waited + 5))
  done
  [ "$status" -eq 0 ] && { wait "$claude_pid"; status=$?; }
  CURRENT_TASK_PID=""

  if [ -n "$tail_pid" ]; then
    sleep 1
    kill "$tail_pid" 2>/dev/null
    wait "$tail_pid" 2>/dev/null
  fi

  return "$status"
}

# result_line <log file> — the last RUN-ROADMAP-RESULT payload in the log, or nothing.
result_line() {
  grep -o 'RUN-ROADMAP-RESULT[[:space:]]*{.*}' "$1" 2>/dev/null \
    | tail -n 1 \
    | sed 's/^RUN-ROADMAP-RESULT[[:space:]]*//'
}

# json_field <json> <key> — one scalar field, with jq when it is there and sed when it is not.
json_field() {
  if [ -n "$JQ" ]; then
    printf '%s' "$1" | "$JQ" -r --arg k "$2" 'try (.[$k] // "") catch ""' 2>/dev/null
    return 0
  fi
  printf '%s' "$1" \
    | sed -n "s/.*\"$2\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p;s/.*\"$2\"[[:space:]]*:[[:space:]]*\([0-9][0-9]*\).*/\1/p" \
    | head -n 1
}

# ---------------------------------------------------------------------------- the loop

info "starting on branch $BRANCH at $START_COMMIT · $(printf '%s' "$WORK_ROOTS" | sed '/^$/d' | wc -l | tr -d ' ') repositor$(printf '%s' "$WORK_ROOTS" | sed '/^$/d' | wc -l | tr -d ' ' | sed 's/^1$/y/;s/^[0-9]*$/ies/') · logs in $LOG_DIR"
RUN_START="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
iteration=0
last_remaining=""

while :; do
  if [ "$MAX_TASKS" -gt 0 ] && [ "$iteration" -ge "$MAX_TASKS" ]; then
    STOP_REASON="reached --max-tasks $MAX_TASKS"
    break
  fi

  iteration=$((iteration + 1))
  task_log="$LOG_DIR/task-$(printf '%02d' "$iteration").log"
  info "task $iteration — $(date -u '+%H:%M:%SZ')"

  run_task "$task_log"
  claude_status=$?

  payload="$(result_line "$task_log")"

  if [ "$claude_status" -eq 124 ]; then
    printf '%s\t%s\t\t\t\t%s\n' "$iteration" "timeout" "killed after ${TIMEOUT}s" >>"$SUMMARY"
    STOP_REASON="task $iteration timed out after ${TIMEOUT}s — see $task_log"
    EXIT_CODE=4
    break
  fi

  if [ -z "$payload" ]; then
    printf '%s\t%s\t\t\t\t%s\n' "$iteration" "no-result" "claude exited $claude_status" >>"$SUMMARY"
    STOP_REASON="task $iteration printed no RUN-ROADMAP-RESULT line (claude exited $claude_status) — see $task_log"
    EXIT_CODE=4
    break
  fi

  outcome="$(json_field "$payload" outcome)"
  task_id="$(json_field "$payload" taskId)"
  commit="$(json_field "$payload" commit)"
  remaining="$(json_field "$payload" remaining)"
  next_action="$(json_field "$payload" nextAction)"
  reason="$(json_field "$payload" reason)"

  printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$iteration" "${outcome:-unknown}" "$task_id" "$commit" "$remaining" "$reason" >>"$SUMMARY"

  case "$outcome" in
    completed)
      TASKS_DONE=$((TASKS_DONE + 1))
      ok "$task_id done${commit:+ · $commit}${remaining:+ · $remaining left}"
      ;;
    deferred)
      TASKS_DEFERRED=$((TASKS_DEFERRED + 1))
      warn "$task_id deferred by the cto: ${reason:-no reason given}"
      ;;
    *)
      warn "task $iteration ended as ${outcome:-unknown}: ${reason:-no reason given}"
      ;;
  esac

  # The command decides whether another task should start; the flags can only be more cautious.
  if [ "$next_action" = "stop" ]; then
    STOP_REASON="the command said stop after ${outcome:-unknown}${reason:+: $reason}"
    case "$outcome" in
      completed|no-work) EXIT_CODE=0 ;;
      *)                 EXIT_CODE=3 ;;
    esac
    if [ "$KEEP_GOING" -eq 1 ] && [ "$outcome" = "handed-back" ]; then
      warn "--keep-going: carrying on past the hand-back"
      STOP_REASON=""
      EXIT_CODE=0
    else
      break
    fi
  fi

  if [ "$outcome" != "completed" ] && [ "$outcome" != "deferred" ] && [ "$KEEP_GOING" -eq 0 ]; then
    STOP_REASON="task $iteration ended as $outcome${reason:+: $reason}"
    EXIT_CODE=3
    break
  fi

  # A roadmap that is not shrinking means the loop is not making progress.
  if [ -n "$remaining" ] && [ "$remaining" = "$last_remaining" ] && [ "$outcome" = "completed" ]; then
    STOP_REASON="the roadmap still lists $remaining tasks after a completed task — stopping rather than looping"
    EXIT_CODE=3
    break
  fi
  [ -n "$remaining" ] && last_remaining="$remaining"

  if [ "$remaining" = "0" ]; then
    STOP_REASON="the roadmap is empty"
    EXIT_CODE=0
    break
  fi

  # A dirty tree here means a task neither committed nor reverted its work — in any repository.
  DIRTY="$(dirty_roots)"
  if [ -n "$DIRTY" ]; then
    STOP_REASON="task $iteration left uncommitted changes in $(printf '%s' "$DIRTY" | tr '\n' ' ')— stopping so they are not swallowed by the next task"
    EXIT_CODE=3
    break
  fi
done

# ---------------------------------------------------------------------------- summary

COMMITS=0
REPO_LINES=""
while IFS=$(printf '\t') read -r wr start; do
  [ -n "$wr" ] || continue
  end="$(git -C "$wr" rev-parse --short HEAD 2>/dev/null || printf 'none')"
  n="$(git -C "$wr" rev-list --count "${start}..HEAD" 2>/dev/null || printf '0')"
  COMMITS=$((COMMITS + n))
  REPO_LINES="${REPO_LINES}$(basename "$wr")|${start}..${end}|${n} commits|$wr
"
done <"$START_COMMITS"

{
  printf '\n%s\n' "${C_BOLD}Run summary${C_RESET}"
  printf '  started        %s\n' "$RUN_START"
  printf '  finished       %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  printf '  board          %s\n' "${DOCS_ROOT:-$REPO_ROOT}"
  printf '  commits        %s\n' "$COMMITS"
  printf '%s' "$REPO_LINES" | while IFS='|' read -r name range n path; do
    [ -n "$name" ] && printf '  %-14s %s · %s · %s\n' "$name" "$range" "$n" "$path"
  done
  printf '  tasks done     %s\n' "$TASKS_DONE"
  [ "$TASKS_DEFERRED" -gt 0 ] && printf '  deferred       %s\n' "$TASKS_DEFERRED"
  printf '  stopped        %s\n' "${STOP_REASON:-no reason recorded}"
  printf '  logs           %s\n' "$LOG_DIR"
  printf '\n'
  if [ -s "$SUMMARY" ]; then
    if command -v column >/dev/null 2>&1; then
      column -t -s "$(printf '\t')" <"$SUMMARY" | sed 's/^/  /'
    else
      sed 's/^/  /' <"$SUMMARY"
    fi
  fi
  printf '\n'
  if [ "$COMMITS" != "0" ]; then
    printf '%s\n' "  Review what it built, per repository:"
    printf '%s' "$REPO_LINES" | while IFS='|' read -r name range n path; do
      [ -n "$path" ] && printf '%s\n' "    git -C $path log --oneline $range"
    done
  fi
} | { [ "$QUIET" -eq 1 ] && cat >&2 || cat; }

exit "$EXIT_CODE"
