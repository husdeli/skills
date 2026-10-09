# The work root

Which repository a task is built in, and how a session works in a repository that is not its working directory.

## Resolve the work root

**A ticket never names its repository.** The board stays about the product, and a repository code
written into a ticket goes stale the moment a repository is renamed, split, or merged. The run
works it out instead — once, when the task is picked.

In this order, and stop at the first that answers:

1. **A repo-rooted session** → the work root is the session's own repository. Nothing to resolve.
2. **One entry in the registry** → that entry is the work root.
3. **Several entries** → read the evidence, in this order, and take the repository it points at:
   - the feature the ticket's code names, and the design docs in that feature's folder;
   - any other design doc the ticket cites, and the parts of the system it names;
   - the ticket's description, its acceptance criteria, and any path, route, or module it names;
   - the epic's name and its `**Note**:` line;
   - each registry entry's `what` line;
   - the candidate repositories themselves — list the top level, and grep for the symbol, the
     route, or the file the ticket names. The tree that already holds the code the task changes is
     the tree the task lands in.
4. **Still open** → ask. That is one `AskUserQuestion` naming the candidates and what each one would
   mean, or, in an unattended run, a `work-root` request to the `cto` agent. Never guess in silence,
   and never start in two repositories because the evidence was thin.

**Take the smallest set of repositories that satisfies every acceptance criterion** — almost always
exactly one.

**A task that truly spans two repositories keeps both.** Each work root is then its own job: its own
conventions, its own verification commands, its own code review, and its own commit. The task passes
only when every work root passes. Say in the report that the task spanned two repositories, and say
which shape it should have had — a contract change that must land on both sides at once earns one
ticket; anything that could ship in two steps is two tickets, linked by `Depends on`.

**Write the work root into the worklog, in the entry that starts the work** — the code, the absolute
path, and the one line of evidence that settled it. The ticket carries no such field, so the worklog
is the only record. A later session resuming that ticket reads it there instead of resolving it a
second time, and a person reading `done/` can see where each task landed.

## Working in a repository that is not the working directory

This is the vault-rooted session: the docs root is the working directory, and the code is somewhere
else. A repo-rooted session can skip the whole section.

- **The session has to be allowed to reach the repository.** In Claude Code, start it from the docs
  root as `claude --add-dir <work root>`, or run `/add-dir <work root>` once inside the session. A
  tool call that cannot write to the work root is a setup problem, not a task failure: name the
  command that fixes it and stop.
- **Every shell command names the repository.** Run git as `git -C <work root> …`, and run a build,
  a test, or a package manager as `cd <work root> && …`. A bare `npm test` runs in the vault and
  proves nothing.
- **Every brief that leaves this session carries the work root as an absolute path**, and every
  relative path in that brief resolves against it.
- **The repository's own instructions govern its code.** Read the `AGENTS.md` and `CLAUDE.md` of the
  work root, not the ones beside the vault. Two work roots may carry two different sets of
  conventions, and a change follows the ones in the tree it lands in.
- **Git belongs to the work root.** The branch, the diff, the commit, and the history are the
  repository's. The docs root is usually no git working tree at all, so a code commit never carries
  the ticket move or the roadmap edit with it. When the docs root *is* its own git working tree, it
  gets its own commit, in its own tree.

