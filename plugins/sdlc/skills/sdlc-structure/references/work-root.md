# The work root

Which repository a task is built in, and how a session works in a repository that is not its working directory.

## Resolve the work root

**A ticket never names its repository.** The board stays about the product, and a repository name
written into a ticket goes stale the moment a repository is renamed, split, or merged. The run
works it out instead — once, when it starts the ticket, before the first agent starts.

The work root comes from [the registry](roots.md#the-registry), in this order:

1. **List the candidates.** They are every registry entry whose `projects` names a project in the
   `projects` property of the ticket's feature, and every entry with no `projects`. An entry whose
   `projects` names only other projects is never a candidate.
2. **One candidate is the work root.**
3. **Several candidates are narrowed by evidence**, read in this order:
   - the design docs in the feature's folder, and any other design doc the ticket cites;
   - the ticket's description, its acceptance criteria, and any path, route, or module it names;
   - each candidate's `what` line;
   - the candidate repositories themselves — list the top level, and grep for the symbol, the
     route, or the file the ticket names. The tree that already holds the code the ticket changes
     is the tree the ticket lands in.
4. **When the evidence leaves it open, the answerer chooses** — the person in an interactive run,
   one `work-root` request to the `cto` agent in an autonomous one. Name the candidates and what
   each would mean. Never guess in silence, and never start in two repositories because the
   evidence was thin.

**Confirm the session can write to the work root before the ticket starts.** A work root that
cannot be resolved or written stops the run before its Start step: it removes its claim, writes
nothing else, and names the access the session needs. The `ticket-board` skill holds that state.

**Take the smallest set of repositories that satisfies every acceptance criterion** — almost always
exactly one.

**A ticket that changes two work roots keeps both.** Each work root is then its own job: its own
conventions, its own verification, its own code review, and, in an autonomous run, its own commit.
The ticket passes only when every work root passes. Say in the report that the ticket spanned two
repositories, and say which shape it should have had — a contract change that must land on both
sides at once earns one ticket; anything that could ship in two steps is two tickets, linked by
`depends_on`.

**Write the work root into the worklog, in the entry that starts the ticket** — the registry key,
the absolute path, and the one line of evidence that settled it. The ticket carries no such field,
so the worklog is the only record. A later run resuming that ticket reads it there, and a person
reading `work/done/` can see where each ticket landed.

## Working in a repository that is not the working directory

The framework root is the working directory, and the code is somewhere else. A session started
inside the work root itself can skip the whole section.

- **The session has to be allowed to reach the repository.** In Claude Code, start it from the
  framework root as `claude --add-dir <work root>`, or run `/add-dir <work root>` once inside the session. A
  tool call that cannot write to the work root is a setup problem, not a task failure: name the
  command that fixes it and stop.
- **Every shell command names the repository.** Run git as `git -C <work root> …`, and run a build,
  a test, or a package manager as `cd <work root> && …`. A bare `npm test` runs in the framework root and
  proves nothing.
- **Every brief that leaves this session carries the work root as an absolute path**, and every
  relative path in that brief resolves against it.
- **The repository's own instructions govern its code.** Read the `AGENTS.md` and `CLAUDE.md` of the
  work root, not the ones beside the framework root. Two work roots may carry two different sets of
  conventions, and a change follows the ones in the tree it lands in.
- **Git belongs to the work root.** The branch, the diff, the commit, and the history are the
  repository's. The framework root is usually no git working tree at all, so a code commit never
  carries the ticket move or the roadmap edit with it. When the framework root *is* its own git
  working tree, it gets its own commit, in its own tree.
- **A work root holds one build at a time.** Two runs building in one tree would each check the
  other's changes. The `ticket-board` skill holds the claim rule that enforces it.

