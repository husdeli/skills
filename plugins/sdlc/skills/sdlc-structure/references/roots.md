# The framework root and the registry

Where the documents live, how a session finds them, which project a run works on, and how the
framework root names every repository its projects are built in.

## The framework root, the project, and the work root

| | What it holds | How many |
| --- | --- | --- |
| **framework root** | The registry, the glossary, every feature, every design doc and diagram, every ticket and worklog, and either `projects/` or one project's documents | One per session |
| **project** | One product's project note, PRD, roadmap, product notes, and business plan | One or more per framework root |
| **work root** | The code: one repository, with its own instructions, its own test suite, and its own git history | One per repository — a project may have several, and one ticket may change several |

**The work root is not the framework root.** A run started in the framework root reaches into a
repository somewhere else. Every path and every command says whether it belongs to the framework
root or to a work root, and none of them assume the two are the same folder.

## Resolve the framework root before you read anything

Do this **once**, at the start of the run, and resolve every later path against what it gives you.

**Step 1 — is the working directory inside a framework root?** A directory is a **framework root**
when it holds `sdlc.json`. Test the working directory, then each parent, stopping at the home
directory. Take the first hit.

- **Found** → that directory is the framework root.
- **Not found, but a directory holds `glossary.md` together with `work/` or `features/`** → it is a
  framework root whose registry is missing. Use it, and name the setup entry point as the way to
  write the registry. A run that needs a work root stops before it starts a ticket.

**Step 2 — otherwise the session is inside a code repository.** Find the framework root from the
repository root, in this order, and stop at the first hit:

1. **`.sdlc.json` at the repository root** — the pointer file. Its `root` names the folder that
   holds the documents. Walk up from there to the first directory holding `sdlc.json`; that is
   the framework root, and the folder `root` named is the project.
2. **`.sdlc/` at the repository root** — the in-repository default. It is the framework root.
3. **Neither** — the repository has no framework root. Read whatever it already keeps at the
   repository root on an [older shape](layout.md#older-shapes), and name the setup entry point as
   the way to create the structure.

The **repository root** is the directory holding `.git`, `package.json`, `AGENTS.md`, or
`CLAUDE.md` — not the working directory when that sits deeper.

Every path this plugin writes as `<framework root>/…` resolves against the directory this section
found.

## Resolve the project

A framework root with no `projects/` holds one project, directly. Otherwise the project is settled
in this order, and the first answer wins:

1. **The command's arguments name it**, by the `name` in its project note.
2. **The pointer file names it** — the session started in a repository whose `.sdlc.json` points at
   one project folder.
3. **The work names it.** A ticket reaches its project through its feature's `projects` property; a
   feature names its projects directly. When that list holds one project, it is the project.
4. **Otherwise, ask.** Offer every project whose note says `in progress`, and never guess when two
   are in reach.

**A project note's `status` decides what a command does with it:**

| `status` | What a command does |
| --- | --- |
| `backlog` | Lists it, never picks it unasked, and drives it when named |
| `in progress` | Offers it, and drives it |
| `done` | Leaves it out of every list, and reads it only when named |

The project note is `<project-name>/<project-name>.md` with `type: project`. A note with another
`type` is not the project note, and a `type: project` note anywhere else is not one either.

## The pointer file

`.sdlc.json` lives at a repository's root and points from the code to the documents:

```json
{
  "root": "~/Vaults/Work/projects/acme-billing",
  "kind": "vault"
}
```

- **`root`** — the folder that holds the documents of the project this repository is built for: a
  project folder, or the framework root when it holds one project directly. An absolute path, a
  `~`-prefixed path, or a path relative to the repository root. Expand `~` to the user's home
  directory.
- **`kind`** — where the documents sit: `repo`, `folder`, or `vault`. See
  [Properties, links, and the vault shape](destinations.md).

The pointer file exists only when the documents are somewhere other than `.sdlc/`. A repository
whose framework root is its own `.sdlc/` needs no pointer file, and never gets one.

**Never move the documents on your own.** Only the setup entry point writes or changes
`.sdlc.json`, and only after the user says where the documents go.

The pointer file points one way, from a repository to the documents. The registry points the other
way, from the documents to every repository. The setup entry point writes both, so a project can be
driven from either end.

## The registry

The framework root **holds exactly one** registry, `sdlc.json`. It names every work root of every
project, with its path on this machine:

```json
{
  "repositories": {
    "acme-web": {
      "path": "~/Projects/acme-web",
      "projects": ["acme-billing"],
      "what": "TanStack Start app — every screen, and the server functions behind them"
    },
    "acme-api": {
      "path": "~/Projects/acme-api"
    }
  }
}
```

| Responsible for | Never holds |
| --- | --- |
| Naming every work root of every project, with its path on this machine and one line on what belongs in it | A requirement, a ticket, a project's status, a document path, or a setting a project's documents already carry |

- **`repositories`** is the only top-level property. It holds one entry per work root, keyed by a
  short, stable name. The key is how a worklog, a report, and a result line name that repository.
- **`path`** is required. It is absolute, `~`-prefixed, or relative to the framework root, and `~`
  expands to the user's home directory.
- **`projects`** is optional. It lists the projects the work root belongs to, each by the `name` in
  its project note.
- **`what`** is optional: one line saying what the repository is and what belongs in it. The
  [work-root resolution](work-root.md) reasons over it, so name the surface, the stack, and the
  kind of work that lands there. An entry with no `what` turns more ambiguous tickets into
  questions.

**A work root that lists `projects` is changed only while working on one of those projects.** Work
on any other project never changes it. A work root with no `projects` may be changed while working
on any project.

**The registry is machine-local, and it is gitignored.** Its paths exist on one machine. When the
framework root sits inside a git working tree, that tree's `.gitignore` lists `sdlc.json`. Never
commit it, and never overwrite another machine's paths in it.

**Only the setup entry point writes the registry.** Every other command reads it. A repository that
is missing from it is added by running setup again — never by editing the file in the middle of a
ticket.

**The registry is required.** A framework root with no `sdlc.json` can be read, but no run can
resolve a work root in it; the run says so and names the setup entry point. Never search the disk
for a repository the registry does not name.

**An older registry keeps working.** A top-level `repos` object is read as `repositories`, and an
entry written as `"web": "~/Projects/acme-web"` is read as a `path` with no `projects` and no
`what`. The setup entry point rewrites both into the current form.
