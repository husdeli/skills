# The work root

Which repository a task is built in, and how a session works in a repository that is not its working directory.

## Resolve the work root

**A ticket names its repositories in `repositories`** — a list of [registry](roots.md#the-registry)
codes, never paths. A code survives a move to another machine, where the registry maps it to a
different path; a path would not. A repository renamed, split, or merged means editing the tickets
that name its old code, which the `repo-resolver` agent below also catches.

The run reads the work roots from the ticket — once, when it starts the ticket, before the first
agent starts:

1. **`repositories` names codes the registry has** → those entries are the work roots. Done.
2. **`repositories` is empty or absent, or names a code the registry does not have** → spawn the
   **`repo-resolver`** agent with the ticket, its feature and design docs, the registry entries, and
   the `repositories` of each ticket in `depends_on`. It reads the documents and the candidate
   repositories' code and returns the codes with the evidence for each.
   - **`settled: true`** → write its codes onto the ticket's `repositories`, in the same tool block
     as the Starting a ticket transition, and the evidence into the opening worklog entry. Every
     later run reads the field instead of resolving again.
   - **`settled: false`** → the answerer chooses among its `candidates`: the person in an
     interactive run; in an autonomous run nobody is there, so the run ends for a person, naming the
     candidates. Write the chosen codes onto the ticket the same way. Never guess in silence, and
     never start in every repository because the evidence was thin.
3. **A repo-rooted run with no registry** — the session's own repository is the only one — skips
   the field: the work root is that repository.

`/plan` writes `repositories` when it creates a ticket and one candidate, or its own reading of the
design, settles them; it leaves the field empty otherwise, and the run fills it.

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

**Write the work root into the worklog, in the entry that starts the ticket** — the registry code,
the absolute path, and, when `repo-resolver` or the answerer settled it, the one line of evidence.
The ticket's `repositories` says where; the worklog says why.

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

