#!/usr/bin/env bash
#
# run-roadmap.sh — drive a whole roadmap with no person in the loop.
#
# One roadmap run, one ticket per Claude session: the script names the run `run-roadmap-<n>`, calls
# `claude -p "/sdlc:run-roadmap --run run-roadmap-<n>"` in a loop, reads the RUN-ROADMAP-RESULT line
# that command prints, and decides whether to start another ticket. A fresh session per ticket is
# the point — a long roadmap never runs out of context, and each ticket lands as its own commit on
# the run branch, in a run worktree beside each repository. Your own checkout is never touched.
#
# The command answers every question with the `cto` agent, so nothing in this loop waits for input.
# It stops on its own when the roadmap is done, when --max is reached, and whenever a person is
# needed: a hand-back, a stopped ticket, a lost claim, a worktree it cannot make, or a dead agent.
#
#   ./run-roadmap.sh --max 5
#   ./run-roadmap.sh --run 3 --yes                              # resume run-roadmap-3
#   ./run-roadmap.sh --project ~/Vaults/Personal/Acme          # one board, several repositories
#
# Run it from the repository you want built, or from the project — in your Obsidian vault, holding
# the roadmap — when one board drives several repositories. In that shape the script reads
# sdlc.json for the repositories, gives the session access to each one and to its worktrees, and
# checks every run worktree between tickets. Use --help for every option.

set -uo pipefail

VERSION="2.2.0"

# ---------------------------------------------------------------------------- defaults

COMMAND="/sdlc:run-roadmap"
ROADMAP=""
PROJECT_DIR=""               # set by --project, or detected from the working directory
REPO_ROOT=""                 # the repository the run builds, when it starts in one
MODE=""                      # repo (cwd is the code) or vault (cwd is the project)
WORK_ROOTS=""                # one absolute repository path per line
MAX_TASKS=0                  # 0 = until the roadmap is done
RUN_NAME=""                  # run-roadmap-<n>; set by --run, or the lowest free number
FINAL=0                      # 1 while the session about to start is the run's last
PERMISSION_MODE="bypassPermissions"
MODEL=""
LOG_DIR=""
TIMEOUT=5400                 # per task, seconds. 0 = no limit
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
  Starts one roadmap run, run-roadmap-<n>, and calls `claude -p "/sdlc:run-roadmap --run ..."`
  once per ticket, in a fresh session each time. The run works one feature at a time: that command
  selects the next feature, claims every ticket it still needs with their dependencies, builds the
  feature's next ticket, makes a run worktree on branch run-roadmap-<n> beside each repository the
  ticket changes, has the `cto` agent answer every question a person would normally answer, drives
  plan -> review -> tests -> implement -> verify -> code review, commits the code on the run
  branch and the documents in the framework root, and prints one RUN-ROADMAP-RESULT line. This
  script reads that line and starts the next ticket — of the same feature until it is done, then of
  the next feature — or stops.

WHERE YOU RUN IT
  From a code repository, and it builds that repository.
  From a framework root or a project folder under it — in your vault — and it builds every
  repository the framework root's sdlc.json names for that project, one ticket at a time. The session is given access to each repository
  and to its <repository>-worktrees/ folder with --add-dir.

OPTIONS
  --max N              Stop after N tickets. Default: 0, meaning until the roadmap is done.
                       --max-tasks is the same option.
  --run N              Resume run-roadmap-N: reuse its branch and worktrees, and claim afresh.
                       Default: a new run, numbered with the lowest number no claim, branch, or
                       worktree uses.
  --roadmap PATH       Roadmap file to pass to the command. Default: the project's own roadmap.
  --project PATH       The project folder (projects/<name>/), or a framework root holding one
                       project — in your Obsidian vault. Runs the loop over every repository
                       sdlc.json names for that project. Default: detected from the working
                       directory, or from the repository's .sdlc.json pointer file.
  --model NAME         Model for the main session (the agents pick their own). Default: your config.
  --permission-mode M  Claude permission mode. Default: bypassPermissions, which is what an
                       unattended run needs — a prompt in a headless session is a dead run.
  --timeout SECONDS    Kill a ticket that runs longer than this. Default: 5400. 0 disables it.
  --log-dir DIR        Where the per-ticket logs go. Default: a timestamped folder under TMPDIR.
  --command NAME       Slash command to run. Default: /sdlc:run-roadmap.
  --yes, -y            Skip the confirmation prompt. Required on a non-interactive shell.
  --dry-run            Print the command for the first ticket and exit.
  --quiet, -q          Only print the final summary.
  --version            Print the version and exit.
  --help, -h           Print this help and exit.

BEFORE YOU RUN IT
  This writes code and commits it without asking — on the branch run-roadmap-<n>, in a worktree at
  <repository>-worktrees/run-roadmap-<n> beside each repository. It never touches your checkout,
  never pushes, and never merges. Read the branch afterwards and merge what you keep — a CTO agent
  made every product decision in it.

EXIT CODES
  0  The roadmap is done, or --max was reached.
  1  Preflight failed: no claude, no git, an unreadable registry, or a bad option.
  3  A person is needed: a hand-back, a stopped ticket, nothing selectable, a lost claim, a
     worktree that could not be made, an abort, or a ticket that left its worktree dirty.
  4  A ticket produced no result line, or timed out.
EOF
}

# ---------------------------------------------------------------------------- options

while [ $# -gt 0 ]; do
  case "$1" in
    --max|--max-tasks) MAX_TASKS="${2:-}"; shift 2 ;;
    --run)             RUN_NAME="${2:-}"; shift 2 ;;
    --roadmap)         ROADMAP="${2:-}"; shift 2 ;;
    --project)         PROJECT_DIR="${2:-}"; shift 2 ;;
    --model)           MODEL="${2:-}"; shift 2 ;;
    --permission-mode) PERMISSION_MODE="${2:-}"; shift 2 ;;
    --timeout)         TIMEOUT="${2:-}"; shift 2 ;;
    --log-dir)         LOG_DIR="${2:-}"; shift 2 ;;
    --command)         COMMAND="${2:-}"; shift 2 ;;
    --keep-going|--allow-dirty)
                       warn "$1 is gone: a stopped ticket ends the run, and the run never builds in your checkout"; shift ;;
    -y|--yes)          ASSUME_YES=1; shift ;;
    --dry-run)         DRY_RUN=1; shift ;;
    -q|--quiet)        QUIET=1; shift ;;
    --version)         printf 'run-roadmap.sh %s\n' "$VERSION"; exit 0 ;;
    -h|--help)         usage; exit 0 ;;
    *)                 usage >&2; die "unknown option: $1" 1 ;;
  esac
done

case "$MAX_TASKS" in ''|*[!0-9]*) die "--max needs a whole number" 1 ;; esac
case "$RUN_NAME" in
  "") ;;
  run-roadmap-[1-9]*) ;;
  [1-9]*) RUN_NAME="run-roadmap-$RUN_NAME" ;;
  *) die "--run needs a run number, such as 3 or run-roadmap-3" 1 ;;
esac
case "$RUN_NAME" in ''|run-roadmap-[1-9]|run-roadmap-[1-9]*[0-9]) ;; *) die "--run needs a run number" 1 ;; esac
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

# find_framework_root <dir> — the first folder from <dir> up to the home directory that holds
# sdlc.json, else the first that holds glossary.md beside work/ or features/. Prints nothing when
# there is none.
find_framework_root() {
  d="$1"; fallback=""
  while [ -n "$d" ]; do
    [ -f "$d/sdlc.json" ] && { printf '%s' "$d"; return 0; }
    [ -z "$fallback" ] && [ -f "$d/glossary.md" ] && { [ -d "$d/work" ] || [ -d "$d/features" ]; } \
      && fallback="$d"
    { [ "$d" = "$HOME" ] || [ "$d" = "/" ]; } && break
    d="$(dirname "$d")"
  done
  printf '%s' "$fallback"
}

# project_name <framework root> <dir> — the project <dir> is, by the `name` in its project note:
# empty when <dir> is the framework root and it holds one project directly, or the only project
# under projects/ when <dir> is the framework root and there is exactly one.
project_name() {
  root="$1"; dir="$2"
  if [ "$dir" = "$root" ]; then
    [ -d "$root/projects" ] || return 0
    set -- "$root"/projects/*/
    [ "$#" -eq 1 ] && [ -d "$1" ] || return 0
    dir="${1%/}"
  fi
  note="$dir/$(basename "$dir").md"
  name="$(sed -n '/^---$/,/^---$/s/^name:[[:space:]]*//p' "$note" 2>/dev/null | head -1 | tr -d "\"'")"
  printf '%s' "${name:-$(basename "$dir")}"
}

# registry_paths <framework root> <project> — one repository path per line, from sdlc.json: every
# repository whose `projects` names <project> or is empty. With no project, every repository.
registry_paths() {
  reg="$1/sdlc.json"
  [ -f "$reg" ] || return 0
  if [ -n "$JQ" ]; then
    "$JQ" -r --arg p "$2" '(.repositories // .repos // {}) | to_entries[]
      | select((.value|type) == "string" or $p == "" or ((.value.projects // []) | length == 0)
               or ((.value.projects // []) | index($p) != null))
      | (if (.value|type) == "string" then .value else .value.path end)' "$reg" 2>/dev/null && return 0
  fi
  if command -v python3 >/dev/null 2>&1; then
    python3 - "$reg" "$2" <<'PYEOF' 2>/dev/null && return 0
import json, sys
data = json.load(open(sys.argv[1]))
project = sys.argv[2]
for entry in (data.get("repositories") or data.get("repos") or {}).values():
    if isinstance(entry, str):
        print(entry)
    elif not project or not entry.get("projects") or project in entry["projects"]:
        print(entry.get("path", ""))
PYEOF
  fi
  die "cannot read $reg — install jq or python3, or pass the repository as the working directory." 1
}

# pointer_root <repository> — the folder .sdlc.json names, expanded; nothing when there is none.
pointer_root() {
  ptr="$1/.sdlc.json"
  [ -f "$ptr" ] || return 0
  if [ -n "$JQ" ]; then
    value="$("$JQ" -r '.root // empty' "$ptr" 2>/dev/null)"
  else
    value="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("root") or "")' "$ptr" 2>/dev/null)"
  fi
  [ -n "$value" ] || return 0
  value="$(expand_tilde "$value")"
  case "$value" in /*) ;; *) value="$1/$value" ;; esac
  [ -d "$value" ] && (cd "$value" && pwd)
}

JQ=""
command -v jq >/dev/null 2>&1 && JQ="$(command -v jq)"

# ---------------------------------------------------------------------------- which end are we at

FRAMEWORK_ROOT=""          # the folder holding sdlc.json; the session reads every document under it
PROJECT_NAME=""            # the project the run builds, by its note's `name`; empty for a lone project

if [ -n "$PROJECT_DIR" ]; then
  PROJECT_DIR="$(expand_tilde "$PROJECT_DIR")"
  [ -d "$PROJECT_DIR" ] || die "--project is not a directory: $PROJECT_DIR" 1
  PROJECT_DIR="$(cd "$PROJECT_DIR" && pwd)"
  FRAMEWORK_ROOT="$(find_framework_root "$PROJECT_DIR")"
  [ -n "$FRAMEWORK_ROOT" ] \
    || die "$PROJECT_DIR is in no framework root — expected sdlc.json in it or a folder above it.
Run /setup there first." 1
  MODE="vault"
elif ! git rev-parse --is-inside-work-tree >/dev/null 2>&1 \
     && FRAMEWORK_ROOT="$(find_framework_root "$PWD")" && [ -n "$FRAMEWORK_ROOT" ]; then
  # A board inside a code repository belongs to that repository — that is a repo-rooted run.
  PROJECT_DIR="$PWD"
  MODE="vault"
else
  MODE="repo"
fi

if [ "$MODE" = "vault" ]; then
  PROJECT_NAME="$(project_name "$FRAMEWORK_ROOT" "$PROJECT_DIR")"
  [ -n "$PROJECT_NAME" ] || [ ! -d "$FRAMEWORK_ROOT/projects" ] \
    || die "$FRAMEWORK_ROOT holds several projects — pass --project with the one to build." 1
  cd "$PROJECT_DIR" || die "cannot enter the project" 1
  [ -f "$FRAMEWORK_ROOT/sdlc.json" ] \
    || die "$FRAMEWORK_ROOT has no sdlc.json. Run /setup from each repository this product is built in." 1
  WORK_ROOTS="$(registry_paths "$FRAMEWORK_ROOT" "$PROJECT_NAME")"
  [ -n "$WORK_ROOTS" ] \
    || die "no repository in $FRAMEWORK_ROOT/sdlc.json is built for ${PROJECT_NAME:-this project}. Run
/setup from each repository this product is built in, so the registry names it." 1
  resolved=""
  while IFS= read -r wr; do
    [ -n "$wr" ] || continue
    wr="$(expand_tilde "$wr")"
    case "$wr" in /*) ;; *) wr="$FRAMEWORK_ROOT/$wr" ;; esac
    [ -d "$wr" ] || die "a repository in sdlc.json does not exist here: $wr
The registry is machine-local — run /setup on this machine." 1
    wr="$(cd "$wr" && pwd)"
    git -C "$wr" rev-parse --is-inside-work-tree >/dev/null 2>&1 \
      || die "not a git work tree: $wr. Every ticket is committed on a run branch, so this needs git." 1
    resolved="${resolved}${wr}
"
  done <<EOF
$WORK_ROOTS
EOF
  WORK_ROOTS="$resolved"
else
  git rev-parse --is-inside-work-tree >/dev/null 2>&1 \
    || die "not inside a git work tree, and no board here either. Run this from the repository you
want built, or from your project — or pass --project." 1
  REPO_ROOT="$(git rev-parse --show-toplevel)"
  cd "$REPO_ROOT" || die "cannot enter the repository root" 1
  WORK_ROOTS="$REPO_ROOT
"
  # The documents sit where the pointer file says, or in the repository's own .sdlc/.
  pointed="$(pointer_root "$REPO_ROOT")"
  if [ -n "$pointed" ]; then
    FRAMEWORK_ROOT="$(find_framework_root "$pointed")"
    FRAMEWORK_ROOT="${FRAMEWORK_ROOT:-$pointed}"
    PROJECT_NAME="$(project_name "$FRAMEWORK_ROOT" "$pointed")"
  elif [ -d "$REPO_ROOT/.sdlc" ]; then
    FRAMEWORK_ROOT="$REPO_ROOT/.sdlc"
  fi
fi

RUN_ROOT="${FRAMEWORK_ROOT:-$REPO_ROOT}"

# worktree_of <repository> — where the run's worktree of that repository sits.
worktree_of() {
  printf '%s/%s-worktrees/%s' "$(dirname "$1")" "$(basename "$1")" "$RUN_NAME"
}

# run_number_taken <n> — a claim, a branch, or a worktree already uses run-roadmap-<n>.
run_number_taken() {
  grep -rqs --include='*.md' "^claimed: run-roadmap-$1\$" "$RUN_ROOT" && return 0
  while IFS= read -r wr; do
    [ -n "$wr" ] || continue
    git -C "$wr" show-ref --verify --quiet "refs/heads/run-roadmap-$1" && return 0
    [ -e "$(dirname "$wr")/$(basename "$wr")-worktrees/run-roadmap-$1" ] && return 0
  done <<EOF
$WORK_ROOTS
EOF
  return 1
}

if [ -z "$RUN_NAME" ]; then
  n=1
  while run_number_taken "$n"; do n=$((n + 1)); done
  RUN_NAME="run-roadmap-$n"
fi

# dirty_worktrees — prints every run worktree with uncommitted changes.
dirty_worktrees() {
  while IFS= read -r wr; do
    [ -n "$wr" ] || continue
    wt="$(worktree_of "$wr")"
    [ -d "$wt" ] || continue
    [ -n "$(git -C "$wt" status --porcelain 2>/dev/null)" ] && printf '%s\n' "$wt"
  done <<EOF
$WORK_ROOTS
EOF
  return 0
}

DIRTY="$(dirty_worktrees)"
[ -z "$DIRTY" ] || die "a run worktree of $RUN_NAME holds uncommitted work — a ticket neither committed
nor discarded it. Look at it before resuming:
$DIRTY" 1

# Each repository's worktree folder has to exist for the session to be granted it.
[ "$DRY_RUN" -eq 1 ] || while IFS= read -r wr; do
  [ -n "$wr" ] || continue
  mkdir -p "$(dirname "$(worktree_of "$wr")")" \
    || die "cannot create the worktree folder beside $wr" 1
done <<EOF
$WORK_ROOTS
EOF

if [ -z "$LOG_DIR" ]; then
  LOG_DIR="${TMPDIR:-/tmp}/sdlc-run-roadmap/$(basename "$RUN_ROOT")-$(date -u '+%Y%m%dT%H%M%SZ')"
fi
mkdir -p "$LOG_DIR" || die "cannot create the log directory: $LOG_DIR" 1
LOG_DIR="$(cd "$LOG_DIR" && pwd)"

# Where the run branch of every repository starts, so the summary can report what each one gained:
# its tip on a resume, or the commit the branch will be made from.
START_COMMITS="$LOG_DIR/.start-commits"
: >"$START_COMMITS"
while IFS= read -r wr; do
  [ -n "$wr" ] || continue
  start="$(git -C "$wr" rev-parse --short "refs/heads/$RUN_NAME" 2>/dev/null \
           || git -C "$wr" rev-parse --short HEAD 2>/dev/null || printf 'none')"
  printf '%s\t%s\n' "$wr" "$start" >>"$START_COMMITS"
done <<EOF
$WORK_ROOTS
EOF
SUMMARY="$LOG_DIR/summary.tsv"
printf 'task\toutcome\tfeature\ttaskId\tcommit\tremaining\treason\n' >"$SUMMARY"

# ---------------------------------------------------------------------------- the command line

build_prompt() {
  printf '%s --run %s' "$COMMAND" "$RUN_NAME"
  [ -n "$PROJECT_NAME" ] && printf ' --project %s' "$PROJECT_NAME"
  [ "$FINAL" -eq 1 ] && printf ' --final'
  [ -n "$ROADMAP" ] && printf ' %s' "$ROADMAP"
  return 0
}

claude_argv() {
  # Prints one argument per line, so the caller can read them without word splitting.
  printf '%s\n' "claude" "-p" "$(build_prompt)" "--permission-mode" "$PERMISSION_MODE"
  [ -n "$MODEL" ] && printf '%s\n' "--model" "$MODEL"
  # The session writes to each run worktree, beside its repository, and in the project's case reads
  # the repository itself, so every one has to be granted.
  # A repository-rooted run whose documents sit outside it needs the framework root granted too.
  case "$RUN_ROOT" in "$REPO_ROOT"|"$REPO_ROOT"/*) ;; *) [ "$MODE" = "repo" ] && printf '%s\n' "--add-dir" "$RUN_ROOT" ;; esac
  while IFS= read -r wr; do
    [ -n "$wr" ] || continue
    [ "$MODE" = "vault" ] && printf '%s\n' "--add-dir" "$wr"
    printf '%s\n' "--add-dir" "$(dirname "$(worktree_of "$wr")")"
  done <<EOF
$WORK_ROOTS
EOF
  return 0
}

if [ "$DRY_RUN" -eq 1 ]; then
  info "would run, once per ticket, until the roadmap is done:"
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

  board             ${PROJECT_DIR:-$REPO_ROOT}
  repositories      $(printf '%s' "$WORK_ROOTS" | sed '/^$/d' | paste -sd ', ' - 2>/dev/null || printf '%s' "$WORK_ROOTS")
  run               $RUN_NAME — branch and worktree of that name beside each repository
  permission mode   $PERMISSION_MODE
  tickets           $([ "$MAX_TASKS" -eq 0 ] && printf 'until the roadmap is done' || printf '%s at most' "$MAX_TASKS")
  logs              $LOG_DIR

It writes code, runs your test suite, and commits one commit per finished ticket on the run
branch, in a run worktree beside each repository the ticket changes. Your checkout is not touched.
A ${C_BOLD}cto${C_RESET} agent makes every product decision instead of you. Nothing is pushed or merged.
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
  printf '%s\n' "Logs are in $LOG_DIR. A run worktree may hold a half-built ticket, and its claims stay" >&2
  printf '%s\n' "on the board — check both before you resume with --run ${RUN_NAME#run-roadmap-}." >&2
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

info "starting $RUN_NAME · $(printf '%s' "$WORK_ROOTS" | sed '/^$/d' | wc -l | tr -d ' ') repositor$(printf '%s' "$WORK_ROOTS" | sed '/^$/d' | wc -l | tr -d ' ' | sed 's/^1$/y/;s/^[0-9]*$/ies/') · logs in $LOG_DIR"
RUN_START="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
iteration=0
last_remaining=""

while :; do
  if [ "$MAX_TASKS" -gt 0 ] && [ "$iteration" -ge "$MAX_TASKS" ]; then
    STOP_REASON="reached --max $MAX_TASKS"
    break
  fi

  iteration=$((iteration + 1))
  FINAL=0
  [ "$MAX_TASKS" -gt 0 ] && [ "$iteration" -ge "$MAX_TASKS" ] && FINAL=1
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
    printf '%s\t%s\t\t\t\t\t%s\n' "$iteration" "no-result" "claude exited $claude_status" >>"$SUMMARY"
    STOP_REASON="task $iteration printed no RUN-ROADMAP-RESULT line (claude exited $claude_status) — see $task_log"
    EXIT_CODE=4
    break
  fi

  outcome="$(json_field "$payload" outcome)"
  feature="$(json_field "$payload" feature)"
  task_id="$(json_field "$payload" taskId)"
  commit="$(json_field "$payload" commit)"
  remaining="$(json_field "$payload" remaining)"
  next_action="$(json_field "$payload" nextAction)"
  reason="$(json_field "$payload" reason)"

  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$iteration" "${outcome:-unknown}" "$feature" "$task_id" "$commit" "$remaining" "$reason" >>"$SUMMARY"

  case "$outcome" in
    completed)
      TASKS_DONE=$((TASKS_DONE + 1))
      ok "$task_id done${feature:+ (feature $feature)}${commit:+ · $commit}${remaining:+ · $remaining left}"
      ;;
    deferred)
      TASKS_DEFERRED=$((TASKS_DEFERRED + 1))
      warn "$task_id deferred by the cto: ${reason:-no reason given}"
      ;;
    *)
      warn "task $iteration ended as ${outcome:-unknown}: ${reason:-no reason given}"
      ;;
  esac

  # The command decides whether another ticket should start. Anything but a completed ticket ends the
  # run; only a roadmap with nothing left in it ends it cleanly.
  if [ "$next_action" = "stop" ] || [ "$outcome" != "completed" ]; then
    STOP_REASON="the command said stop after ${outcome:-unknown}${reason:+: $reason}"
    if [ "$outcome" = "completed" ] || { [ "$outcome" = "no-work" ] && [ "$remaining" = "0" ]; }; then
      EXIT_CODE=0
    else
      EXIT_CODE=3
    fi
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

  # A dirty worktree here means a ticket neither committed nor discarded its work.
  DIRTY="$(dirty_worktrees)"
  if [ -n "$DIRTY" ]; then
    STOP_REASON="ticket $iteration left uncommitted changes in $(printf '%s' "$DIRTY" | tr '\n' ' ')— stopping so they are not swallowed by the next ticket"
    EXIT_CODE=3
    break
  fi
done

# ---------------------------------------------------------------------------- summary

COMMITS=0
REPO_LINES=""
while IFS=$(printf '\t') read -r wr start; do
  [ -n "$wr" ] || continue
  end="$(git -C "$wr" rev-parse --short "refs/heads/$RUN_NAME" 2>/dev/null || printf '%s' "$start")"
  n="$(git -C "$wr" rev-list --count "${start}..${end}" 2>/dev/null || printf '0')"
  COMMITS=$((COMMITS + n))
  REPO_LINES="${REPO_LINES}$(basename "$wr")|${start}..${end}|${n} commits|$wr
"
done <"$START_COMMITS"

{
  printf '\n%s\n' "${C_BOLD}Run summary${C_RESET}"
  printf '  started        %s\n' "$RUN_START"
  printf '  finished       %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  printf '  board          %s\n' "${PROJECT_DIR:-$REPO_ROOT}"
  printf '  run            %s\n' "$RUN_NAME"
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
    printf '%s\n' "  Review what it built on $RUN_NAME, per repository, and merge what you keep:"
    printf '%s' "$REPO_LINES" | while IFS='|' read -r name range n path; do
      [ -n "$path" ] && printf '%s\n' "    git -C $path log --oneline $range"
    done
  fi
  if [ "$EXIT_CODE" -ne 0 ]; then
    printf '%s\n' "  Resume after a person has looked: $0 --run ${RUN_NAME#run-roadmap-}"
  fi
} | { [ "$QUIET" -eq 1 ] && cat >&2 || cat; }

exit "$EXIT_CODE"
