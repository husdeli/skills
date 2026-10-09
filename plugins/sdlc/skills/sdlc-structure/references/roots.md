# The project and the registry

Where a project's documents live, how a session finds them, and how a project names every
repository it is built in.

> **Placeholder — the final structure is defined here.** Where a project sits, and how a session
> finds it, is being redesigned in `designs/SDLC-framework.design.md`. When that design settles,
> this file states the final rules and every other skill, command, and agent keeps pointing here.
> Until then, the rules below hold.

## The project and the work root

| | What it holds | How many |
| --- | --- | --- |
| **project** | Every document: the PRD, the glossary, the features, the design docs, the diagrams, the roadmap, the tickets, and the worklogs | One per product |
| **work root** | The code: one repository, with its own instructions, its own test suite, and its own git history | One per repository — a project may have several |

One project drives one or more work roots. The PRD says what the product does; the repositories
the registry names are where that product is built.

**The work root is not always the working directory.** A run started in the vault has the project
as its working directory and reaches into a repository somewhere else. Every path and every command
below says whether it belongs to the project or to a work root, and none of them assume the two are
the same folder.

## The two directions

A session starts in one of two places, and that is what decides how the project and the work roots
are found.

**Vault-rooted** — the working directory is the project itself, usually a folder in an Obsidian
vault. The project is where you already are, and the work roots come from the registry,
`sdlc.json`. The run resolves which repository each task is built in. **This is the recommended
shape.** One board drives every repository the product is built from, so a task that lands in the
API and a task that lands in the web app are picked from the same roadmap, in one session.

**Repo-rooted** — the working directory is inside a code repository. That repository is the work
root, and the project comes from the forward pointer, `.sdlc.json`. One repository, one product.
This is the shape for a product built from a single repository, and it is what a session started
inside a repository always gets.

Both pointers exist at the same time: the setup entry point writes the registry in the project and
a `.sdlc.json` in every repository it names. A project set up once can then be driven from either
end, and the two never disagree.

## Resolve the project before you read anything

Do this **once**, at the start of the run, and resolve every later path against what it gives you.

**Step 1 — is this session vault-rooted?** A directory is a **project** when it holds `sdlc.json`,
or when it holds `roadmap.md` or `prd.md` together with a `tickets/` folder. Test the working
directory, then each parent, stopping at the vault root or the home directory.

- **Found, and the folder sits outside every code repository** → the session is vault-rooted. That
  directory is the project, and `sdlc.json` holds the work roots.
- **Found, and the folder sits inside a code repository** — a repository that keeps its board at
  its own root, or a project in `.sdlc/` you happen to be standing in → the project is that folder,
  and the session is **repo-rooted**: the repository around it is the work root, and no registry is
  read. A board inside the code belongs to the code around it.
- **The working directory is a vault root** — it holds `.obsidian/` — **and holds several
  projects**, one folder per product → the project is not settled yet. Take it from the command's
  arguments when they name one, and ask the user otherwise. Never guess when two projects are in
  reach.

**Step 2 — otherwise the session is repo-rooted.** Find the project from the repository root, in
this order, and stop at the first hit:

1. **`.sdlc.json` at the repository root** — the pointer file. Its `root` field names the
   project, and its `kind` field names the destination. Use them.
2. **`.sdlc/` at the repository root** — the default. The destination is `repo`.
3. **Neither** — the repository has no project. Read whatever it already keeps at the repository
   root (`prd.md`/`PRD.md`, `glossary.md`/`GLOSSARY.md`, `features/`, `*.design.md`, `design.md`,
   `roadmap.md`, `diagrams/`, `tickets/`), and name the platform's setup entry point as the way
   to create the structure.

The **repository root** is the directory holding `.git`, `package.json`, `AGENTS.md`, or
`CLAUDE.md` — not the working directory when that sits deeper. In a repo-rooted session the
repository root is the work root, and no registry is read.

Every path this plugin writes as `.sdlc/…` means `<project>/…`.

## The pointer file

`.sdlc.json` lives at the repository root and holds two fields:

```json
{
  "root": "~/Vaults/Personal/Acme",
  "kind": "vault"
}
```

- **`root`** — the project. An absolute path, a `~`-prefixed path, or a path relative to the
  repository root. Expand `~` to the user's home directory. Prefer a relative path when the project
  sits near the repository: an absolute path only resolves on the machine that wrote it.
- **`kind`** — the destination, one of `repo`, `folder`, or `vault`.

The pointer file exists only when the project is somewhere other than `.sdlc/`. A repository whose
project lives in `.sdlc/` needs no pointer file, and never gets one.

**Never move the project on your own.** Only the setup entry point writes or changes `.sdlc.json`,
and only after the user says where the documents go.

The pointer file points one way, from a repository to the documents. The registry below points the
other way, from the documents to every repository. The setup entry point writes both, so a project
can be driven from either end.

## The registry

`sdlc.json` sits **in the project** and names every repository the product is built in:

```json
{
  "repos": {
    "web": {
      "path": "~/Projects/acme-web",
      "what": "TanStack Start app — every screen, and the server functions behind them"
    },
    "api": {
      "path": "~/Projects/acme-api",
      "what": "Fastify service — the HTTP API, the background jobs, and the database"
    }
  }
}
```

- The key is the repository's **code**: short, lower case, and stable. It is how a worklog, a
  report, and a result line name that repository.
- **`path`** — absolute, `~`-prefixed, or relative to the project. Expand `~` to the user's home
  directory.
- **`what`** — one line saying what the repository is and what belongs in it. This line is what the
  [work-root resolution](work-root.md) reasons over, so write it for that job: name the surface, the stack,
  and the kind of work that lands there. An entry with no `what` turns every ambiguous task into a
  question for the user.
- `"web": "~/Projects/acme-web"` is accepted shorthand for a path with no `what` line. The setup
  entry point always writes the full form.

**The registry is machine-local, and it is gitignored.** It holds paths that exist on one machine,
so it never travels. When the project sits inside a git working tree, the setup entry point adds
`sdlc.json` to that tree's `.gitignore`; a vault is usually no working tree, and then there is
nothing to ignore. Never commit it, and never overwrite another machine's paths in it.

**Only the setup entry point writes the registry.** Every other command reads it. A repository that
is missing from it is added by running setup again from inside that repository — never by editing
the file in the middle of a task.

A project with **no `sdlc.json`** drives one repository: the one whose `.sdlc.json` points back at
it. A vault-rooted session cannot find that repository, so it says so and names the setup entry
point. Never search the disk for a repository the registry does not name.
