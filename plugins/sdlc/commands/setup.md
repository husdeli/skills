---
description: Set up the SDLC framework structure for a product, in an Obsidian vault or in the repository, and register the repositories the product is built in.
argument-hint: "[product name] [destination path] [repository paths]"
---

# Setup

Create the **framework root** — the folder that holds every document this plugin reads and writes — with a **project** in it, and **register the repositories** the project is built in, so a later run can start from either end.

The recommended home is a folder in an **Obsidian vault**, outside the repository: the documents stay readable and editable wherever the vault syncs, they stay out of every diff and merge, one vault holds every project, and one board can drive **several repositories** — the web app and the API are then two entries in one registry, and one roadmap covers both. The framework root can also sit in the repository as `.sdlc/` — the default, as the `sdlc-structure` skill defines it.

**This command runs from either end.** Start it inside a code repository, and it sets up the documents for that repository. Start it in the vault — in the framework root, or in a project inside it — and it sets up the documents there and asks which repositories they drive. `sdlc-structure` holds how that is detected; resolve it before Step 1.

Arguments (if provided): $ARGUMENTS

Load four skills before you create anything, namespaced here as `sdlc:<name>`: **`sdlc-structure`**, which holds the resolution order, the pointer file, the registry, the vault conventions this command writes, and the layout it creates — read its layout reference before Step 4 — **`ticket-board`**, which holds the `work/` folder, the ticket, and the roadmap it creates and migrates, **`feature`**, which holds the feature folder, the feature note, and the code that ties a feature to its epic, and **`product-intent`**, which holds the five notes the PRD is assembled from and the migration that splits an existing PRD into them.

The tree this command creates, what each folder holds, and what it leaves empty are in the `sdlc-structure` layout reference. Create every folder that reference lists except `business/`, which `/business-plan` creates. Write no ticket and no worklog here, and no ticket template: the template lives in the `ticket-board` skill, and `/plan` writes each ticket from it.

## Rules

- **Never overwrite.** Create a file only when it does not exist. Report each existing file as kept, and leave its contents alone.
- **One design stub, at most.** Write `designs/overview.design.md` only when the project has no design doc at all — no `*.design.md` file in `features/*/`, in `designs/`, in the project itself, or at the repository root, and no single `design.md` in any of those places. Report the one it already has as kept.
- **Write stubs, not content.** Each stub carries only the headings and the placeholder lines below. Do not invent product requirements, surfaces, or tasks — the person fills them in, or `/prd` and `/design` do.
- **Substitute the product name** wherever the stubs show `<product>`, when the arguments gave one. Otherwise leave `TBD`.
- **Settle the destination before you create anything** — Step 1. The repository option puts the project in `.sdlc/` at the repository root, which the `sdlc-structure` skill defines — not the current working directory when that sits deeper.
- **Register every repository** — Step 2. A project with no registry can only be driven from inside a repository, which is the thing this command exists to fix.
- **Write no feature, and no product note.** `features/` and the five folders under `product/` are created empty. A feature is opened when the product has one, and a goal, a persona, or a problem is written when `/prd` settles it. Inventing either here invents a commitment nobody made.
- **Create `features/`, `designs/`, `diagrams/`, `work/` with its three buckets — `backlog/`, `in-progress/`, and `done/` — and the project's `product/` with its five folders**, even though they start empty. Write a `.gitkeep` file into every one that ends up with no file in it **when the framework root sits inside a git working tree**, because git does not track an empty directory. A framework root outside git gets no `.gitkeep` — it is clutter in a vault.

## 1. Settle the destination

The framework root goes where the user keeps this kind of writing. Decide where, in this order, and stop at the first that applies:

- **This session is vault-rooted** — the working directory is a framework root, or a project inside one → the destination is settled before you ask anything. The project is the working directory, or the one the framework root holds; when it holds several, take the one the arguments name, and ask which one otherwise. A product name no project carries yet is a new project in this framework root. Fill the gaps there and go to Step 2, which is the step that has work to do.
- **`.sdlc.json` already exists** at the repository root → read it. The destination is settled. Report where the documents live and fill the gaps there. Do not ask.
- **`.sdlc/` already exists** → the destination is the repository. You are filling gaps, not choosing. Do not ask.
- **The arguments name a path** — an absolute path, a `~`-prefixed path, or anything holding a path separator → that is the destination. The rest of the arguments is the product name.
- **Otherwise, ask** where the project's documents should live. One question, two options:
  - **In an Obsidian vault** — recommended. The documents are readable and editable without the repository, on every device the vault syncs to, and Obsidian's properties, backlinks, and search work on the whole board. They sit outside the code, so a branch switch never changes the roadmap, two branches never conflict over a ticket, and a pull request carries the code alone. One vault holds every project. Ask for the vault path in the same turn, or take it from the user's "Other" answer.
  - **In the repository (`.sdlc/`)** — the documents are versioned with the code, they travel with a clone, and a review sees a document change beside the change it describes. Take this option when the user keeps no vault, or when the team reads the documents only through the repository.

  In Codex, ask the same question in prose: a Codex session has no `AskUserQuestion` tool.

  **When the user picks the vault and names no path**, offer the vaults you can find: search for a `.obsidian/` folder a few levels deep under the user's home directory — `~/Documents`, `~/Obsidian`, `~/Vaults`, and the iCloud Obsidian folder — and list each vault you find. Keep the search shallow; never walk the whole home directory. When it finds nothing, ask for the path, and take the repository when the user keeps no vault.

**Then classify the destination.** Walk up from the chosen path looking for a `.obsidian/` folder — in the path itself, or in any parent directory:

- **Found** → the destination is a **vault**. Name the vault in your report. Never name a folder in a vault with a leading dot: Obsidian hides it. If the user asked for `.sdlc` inside a vault, say why it would be invisible and offer the product-named folder instead.

  **When the chosen path is the vault root itself**, look at what that folder already holds, ignoring `.obsidian/`:

  - **Nothing, or only this plugin's own documents** — `sdlc.json`, `glossary.md`, `prd.md`, `roadmap.md`, `features/`, `designs/`, `diagrams/`, `work/`, `projects/`, or an older `tickets/` → **the vault root is the framework root.** A vault kept for the framework needs no folder inside it, and a folder named after the vault (`sdlc-obsidian/sdlc-obsidian/`) helps nobody. Do not ask, and never nest.
  - **Notes of its own** — any other note or folder → say that `prd.md`, `glossary.md`, and `roadmap.md` would land among those notes, and offer a product-named folder inside the vault (`<vault>/Acme/`) as the alternative. The user chooses; take the vault root when they confirm it.
- **Not found**, and the path is outside the repository → the destination is a **folder**.
- **Inside the repository** → the destination is the **repository**, and the framework root is `.sdlc/`.

**Then place the project.** A new framework root holds its one project directly: the project note, `prd.md`, and `roadmap.md` sit beside `glossary.md`. A framework root that already holds `projects/` gets the new project as `projects/<project-name>/`. A framework root that already holds another project directly needs `projects/` before it takes a second one: say so, show what moves into `projects/<existing-project-name>/` — its project note, `prd.md`, `roadmap.md`, `product/`, and `business/` — and move them only after a yes. `features/`, `designs/`, `diagrams/`, `work/`, the glossary, and the registry stay where they are, because they belong to the framework root. `<project-name>` is short, lower case, and kebab-case: `acme-billing`.

**Write the pointer file** at the repository root when the framework root is anywhere other than `.sdlc/`, so every other command finds the documents. Its `root` names the project folder, or the framework root when it holds one project directly:

```json
{
  "root": "~/Vaults/Personal/Acme",
  "kind": "vault"
}
```

Use a path relative to the repository root when the project sits near the repository. Otherwise write the absolute path, and say in your report that it only resolves on this machine — the user decides whether to commit the file.

A **vault destination changes how one document links another**, not what it says: a wikilink instead of a relative path, and no `.gitkeep`. Every property is frontmatter in every destination. The `sdlc-structure` skill holds both rules. A **folder** destination changes nothing but the path.

## 2. Register the repositories

The project drives the code. **`sdlc.json` at the framework root names every repository its projects are built in**, and it is what lets a session started in the vault work on any of them. The `sdlc-structure` skill holds its shape; this step writes it.

**Collect the repositories.** Take them in this order:

- **The arguments name repository paths** → use them.
- **This session is repo-rooted** — you are standing in a code repository → that repository is the first entry. Ask whether the product has others, and take the paths the user gives.
- **This session is vault-rooted** — you are standing in the framework root or a project → ask for the path of every repository the product is built in. One is a complete answer; a product with a web app and an API gives two.

**Write one entry per repository**, keyed by a short lower-case code the user recognises — `web`, `api`, `mobile`, `infra`. Derive the code from the repository's own name and offer it; the user overrides it. Each entry carries the `path`, a `what` line, and `projects` — the project names it belongs to — when the framework root holds more than one project:

```json
{
  "repositories": {
    "web": {
      "path": "~/Projects/acme-web",
      "projects": ["acme-billing"],
      "what": "TanStack Start app — every screen, and the server functions behind them"
    },
    "api": {
      "path": "~/Projects/acme-api",
      "what": "Fastify service — the HTTP API, the background jobs, and the database"
    }
  }
}
```

**The `what` line is the one part of this file that has to be written well.** A ticket names its repositories by these codes, in `repositories`, and when that is empty the run's `repo-resolver` agent reads every `what` line to work out which repository the ticket is built in. Write it from the repository itself — read its `README.md`, its `package.json`, and its top-level folders — and name the surface, the stack, and the kind of work that lands there. Never write `what` as the repository's name again. Show each line to the user with the path, and correct what they correct.

**Then write the registry and the pointer files, so the project can be driven from either end:**

1. **`sdlc.json` at the framework root** — the registry above. Never overwrite an existing registry: merge the new entries into it, keep every entry that is already there, and report a path that changed rather than replacing it silently. An older registry — a top-level `repos` object, or an entry written as a bare path — is rewritten into the current form in the same write, and the report says so.
2. **`.sdlc.json` at the root of every repository in the registry** — the pointer back to the project, exactly as Step 1 writes it. A repository you cannot reach from this session is reported as unregistered, with the one command that fixes it: run setup again from inside it.

**Gitignore the registry.** It holds paths that exist on this machine only. When the framework root sits inside a git working tree, append the registry's path relative to that tree's root to its `.gitignore` — `.sdlc/sdlc.json` for a project in the repository — as one line, never replacing the file, and never a second time when the line is already there. A vault is usually no working tree, and then there is nothing to ignore. Say in the report that the file is machine-local either way.

**A product with one repository still gets a registry.** It costs one file, and it is what makes a vault-rooted run possible later without a second setup.

## 3. Check what is already there

Look for documents this plugin would otherwise create twice:

- The framework root and the project — if they exist, you are filling gaps, not setting up.
- `prd.md`, `PRD.md`, `glossary.md`, `GLOSSARY.md`, `design.md`, `DESIGN.md`, `roadmap.md`, or `ROADMAP.md` at the repository root.
- A `tickets/` directory, at the repository root or in the project — the older shape of `work/`.
- A design doc in any shape: `*.design.md` files in `features/*/`, in `designs/`, in the project itself, or at the repository root; or a single `design.md` in any of those.
- A `features/` directory, and whether it holds a feature note.

If any of these exist outside the project, **ask before touching them**: offer to move each into the project with `git mv` (preserving history), or to leave it where it is. Moving a file is the user's call — never move one without an explicit yes. A file left in place still works: every agent falls back to the repository root when the project has no such document.

**A move out of the repository loses the file's git history**, because `git mv` cannot cross into a folder git does not track. Say that plainly whenever the project sits in a vault or an outside folder, before you offer the move, and use a plain `mv` when the user says yes.

**Design docs outside a folder** need the same explicit yes. A design doc lives in `features/<feature>/` when it belongs to one feature, and in `designs/` when it underpins every feature. One file per subject, named `<subject>.design.md`, so anything else is an older shape. Gather them into `designs/` first, then offer the feature migration below:

- `*.design.md` files directly in the project or at the repository root → offer to move each one into `designs/` under the same name, and report the count moved.
- A single `design.md`, in the project or at the repository root → offer to move it to `designs/overview.design.md`. Say the rename is only a rename: no content moves, and splitting it by subject is a later job for `/design`.

When the user says no, leave every file where it is: every agent reads the older shapes as a fallback. Skip the offer when the project's `designs/` already holds the docs.

**A PRD that still holds its goals, personas, problems, and metrics inline** needs the same explicit yes. Those five pieces are notes under `product/`, because a feature, a design doc, and the business plan all point at them, and because each has a state of its own — met, dropped, deferred, measured. The `product-intent` skill holds the shape. A PRD whose sections 2, 3, 4, and 7 are written out as prose and tables is on the older shape.

Say what the split buys before you offer it: a goal becomes something a feature can cite and a query can count, so "which features advance this goal" and "which goal has nothing being built for it" become answerable. Say what it costs: the PRD stops being one file a reader can read top to bottom without following links. Then offer it in three steps, and stop at any step the user does not approve:

1. **Propose the notes.** Read the PRD's sections 2, 3, 4, and 7. Each numbered failure mode is a problem, each goal a goal, each non-goal a non-goal, each persona row a persona, and each metric a metric. Show the whole mapping as one table — type, file name, and the statement each note would carry — and name any item that splits into two notes or that you would leave inline because it is really prose. Ask the user to accept it, rename a note, merge two, or drop a row.
2. **Write the notes.** One file per approved row, with the properties `product-intent` defines. Carry the words the PRD already uses; do not rewrite a goal while you move it. Set each `status` from what the PRD says and the work root shows, and report any you could not settle.
3. **Rewrite the PRD and every reference.** Replace sections 2, 3, 4, and 7 with one line per note — the link, then the statement in a few words — and leave sections 1, 5, and 6 untouched: they are prose, and prose does not decompose. Then set the `goals` and `personas` properties on each feature that has an obvious one, link the personas from the business plan's segment table and the metrics from its milestones, and report what you could not match. Report the counts: notes written per type, PRD sections rewritten, features and plan sections linked.

When the user says no, create `product/` empty and leave the PRD whole: every command reads that shape as a fallback. Skip the offer when `product/` already holds a note.

**A framework root with no `features/` folder** needs the same explicit yes. A **feature** is one thing a customer can do: it owns a folder, a feature note that says what the customer can do and whether it is done, the design docs for that feature, and the code that numbers its tickets. The `feature` skill holds the shape. A project whose design docs all sit in `designs/`, or whose roadmap has epics but no feature notes, is on the older shape.

Say what the migration buys before you offer it: the feature register becomes the list of what the product does, so the business plan, the roadmap, and every design doc point at one place instead of three. Say what it costs: a design doc that moves changes its path, so a note or a bookmark that cites the old path stops resolving. Then offer it in three steps, and stop at any step the user does not approve:

1. **Propose the features.** Read the roadmap's epics, the design docs in `designs/`, and the PRD's product areas. Each epic is a candidate feature, and its code is the feature's code. Each design doc is either a feature's doc or cross-cutting. Show the whole mapping as one table — feature name, code, PRD area, status, and the design docs that move into it — with a second short table of the docs that stay in `designs/` and why. Ask the user to accept it, rename a feature, move a doc, or drop a row.
2. **Create the folders and the feature notes.** One folder per approved feature, and one `<feature>.feature.md` in each, with the properties the `feature` skill defines and `projects` naming this project. **Check each status against the work root** before you write it — an epic with rows left is `in progress` or `backlog`, and a feature is `done` only when the code holds the whole of it. Report any feature whose evidence disagreed with the roadmap.
3. **Move the design docs and rewrite every reference.** Move each approved doc with `git mv` into its feature's folder, keeping its name. Add a `**Feature**:` line to each roadmap epic section that now has a feature. Then search the project for every moved path and fix what that finds — a `related:` property, a ticket, a diagram caption, the business plan. Report the counts: features opened, docs moved, docs kept in `designs/`, references rewritten.

When the user says no, create `features/` empty and leave every design doc in `designs/`: every agent reads that shape as a fallback. Skip the offer when `features/` already holds a feature.

**A board on the older shape** needs the same explicit yes. That is a `tickets/` directory — with `todo/`, `in-progress/`, and `done/` inside it, or flat — instead of `work/` at the framework root. Say what the move costs before you offer it: a link or a bookmark that cites a ticket by its path stops resolving, while a wikilink keeps working. Then offer it as one step, and show the mapping first:

- **Move each ticket and its worklog into the `work/` bucket its status names** — `backlog/`, `in-progress/`, or `done/`, as the `ticket-board` skill maps them — with `git mv` inside a git working tree.
- **Rewrite each ticket's properties into the current shape**, by the older-values table in `sdlc-structure`: the status values, `Assignee` into `assigned` (`user` and `—` mean none), `Created` into `createdAt`, every `**Field**:` line into frontmatter, and `type`, `id`, `epic`, and `tags` deleted. Set `feature` to the feature note whose code the ID starts with; a ticket whose code no feature carries keeps no `feature`, and the report names it, because the feature migration above opens it.
- **Delete `tickets/TEMPLATE.md`**, and then `tickets/` once it is empty. The template lives in the `ticket-board` skill.

Report the count moved per bucket and the tickets left without a feature. When the user says no, leave every file where it is: every command reads the older board where it is.

**Ticket IDs with no epic** need the same explicit yes. Every ticket ID starts with the code of the feature it delivers, and the numbering restarts at 001 in each epic — the `ticket-board` skill holds the rule, and the roadmap holds the list of epics. A project whose tickets all share one project-wide prefix (`SW-001`, `SW-002`, …), or whose roadmap has no `## <CODE> — <epic name>` sections, is on the older shape. Say what the rename costs before you offer it: a branch, a review, or a note that cites an old ID stops finding the file, so this belongs in a quiet moment and not in the middle of a task. Then offer the migration in three steps, and stop at any step the user does not approve:

1. **Propose the epics.** Group the existing tasks by the feature each one delivers, name each group, and give it a code. Number the tasks inside each group from 001, following the roadmap's existing order. Show the whole mapping as one table — epic, old ID, new ID, task title — and ask the user to accept it, rename an epic, or move a task to another epic.
2. **Rename the tickets** with `git mv`, one file per row of the approved table. A ticket keeps its slug and its bucket; only the ID in the file name changes. Rewrite the `#` title line inside each file, and set its `feature` property to the feature note whose code the new ID starts with — so a group with no feature note gets one from the feature migration first.
3. **Rewrite every reference.** Group the roadmap rows into one `##` section per epic, and rename each ID in the tables, in the `Depends on` cells, and in the `Ticket` cells. Then search the whole project for each old ID and fix what that finds — a ticket's `related:` property, a design doc, a note, a feature note's `code`. Report the count renamed and the files touched.

When the user says no, leave every ID alone, and say that new tickets keep continuing the project's own scheme. Never rename part of the set: a half-migrated project cites two schemes and matches neither. Skip the offer when the roadmap already has epic sections.

**A roadmap that still holds finished work** needs the same explicit yes. The roadmap lists the work that is left, so a completed row, a `✅ **Completed**` status, a done section, or a `###` detail section per task is the older shape. Say what the cleanup removes before you offer it: the roadmap keeps no history, and the ticket in `work/done/` becomes the only record of a finished task. Then offer it as one edit, and show the user what it does:

- **Delete every completed task** — its row, and its `###` detail section. Confirm each one against the tickets first: a row marked completed whose ticket is not `done` stays, and you report the disagreement instead of resolving it.
- **Delete its ID from every `Depends on` cell**, writing `—` in a cell that has nothing left.
- **Delete every remaining `###` detail section.** What it holds belongs to the ticket, so before you delete one, copy anything the ticket is missing into that ticket — the description into `Description`, the criteria into `Acceptance Criteria`. Never delete the only copy of a pending task's criteria.
- **Add a `Ticket` column** to each table, carrying the file name the deleted detail section cited — the wikilink, in a vault.
- **Delete an epic section** whose last row is gone, and bump `updated`.

Report the counts: tasks removed, detail sections folded into tickets, epics closed. When the user says no, leave the roadmap exactly as it is — every command reads the older shape as a fallback. Skip the offer when the roadmap already holds pending work only.

**A roadmap whose rows disagree with the tickets** gets rebuilt from the tickets. A task command corrects only the rows it reads, so drift nobody has read stays until something rebuilds the whole file. Find out whether there is any, with the script that does it:

```shell
${CLAUDE_PLUGIN_ROOT}/scripts/build-roadmap.py --check --project <project>
```

It writes nothing, prints what differs as a diff, and exits 1 when the tables do not match the tickets. Show the user that output, then offer the rebuild:

```shell
${CLAUDE_PLUGIN_ROOT}/scripts/build-roadmap.py --project <project>
```

It writes each epic's table from the tickets — one row per open ticket, its `Priority` and `Status` from the ticket, its `Depends on` cell computed from the ticket's own `depends_on` list, and the rows in the order the **`ticket-board`** skill defines. It never writes a ticket, invents a task, closes an epic's section, or decides a feature has shipped. Relay what it reports: a ticket with no priority read as `Medium`, a dependency on an ID no ticket carries, a circular dependency, an epic it had to add a section for, and an epic whose work is all finished and whose section a person now has to close.

**When the script cannot run** — no `python3`, or the user says no — do the same work by hand only for the epics the user asks for, and never delete a row whose ticket you did not open. When the user declines the rebuild, change nothing: every command reads a stale row as a stale row and corrects it when it next opens that ticket.

**A ticket with no `depends_on` property** is the one thing to fix in the tickets, not the roadmap. The property is new, so an older ticket has none while its roadmap row still names blockers. Offer to copy each row's outstanding IDs into its ticket's `depends_on` before the first rebuild, because a rebuild computes that cell from the ticket and a ticket with no list produces an empty cell. Say plainly that this is the one migration that loses information if it is skipped, and report the count you copied.

## 4. Write the stubs

**Every stub carries its properties as frontmatter, in every destination** — the `sdlc-structure` skill holds the shape, and the `type` and `tags` every document carries. Only a link changes with the destination: a wikilink in a vault, a relative path in a folder or the repository. `<project>/` below is the project folder, or the framework root when it holds one project directly.

**`<project>/<project-name>.md`** — the project note.

```markdown
---
type: project
name: <project-name>
status: in progress
tags:
  - sdlc/project
---
# <product>

<One or two sentences: what the project is.>

- [[prd]] — what the product does and why
- [[roadmap]] — the work that is left
```

`name` is the project's name: the registry's `projects` and every feature's `projects` name the project by it. `status` is `in progress`, because a project being set up is one that is worked on.

**`glossary.md`**, at the framework root — the title alone. Never invent a term: `/prd`, `/design`, and `/plan` add each entry as the product gains it, and the **`glossary`** skill holds the rules they follow. A framework root that already holds a glossary keeps it, whichever project this setup adds.

```markdown
---
type: glossary
updated: <today, YYYY-MM-DD>
tags:
  - sdlc/glossary
---
# <product> — glossary
```

**`<project>/prd.md`**

```markdown
---
type: prd
product: <product>
status: Draft
updated: <today, YYYY-MM-DD>
tags:
  - sdlc/prd
---
# Product Requirements Document

## 1. Overview

<What the product is and what it does, in 2-4 sentences. End with 3-5 core principles.>

## 2. Problem statement

<One line per note in `product/problems/`: the link, then the failure in a few words. The note holds the failure; the goal that answers it says what this product does about it.>

## 3. Goals & non-goals

### Goals

- <One line per note in `product/goals/`: the link, then the statement in a few words.>

### Non-goals (current scope)

- <One line per note in `product/non-goals/`: the link, then the exclusion in a few words. The reason lives in the note, where it is required.>

## 4. Users & personas

- <One line per note in `product/personas/`: the link, then the need in a few words. The note holds the need and the primary flow.>

## 5. How the product works

### <Product area> `AREA`

<A few short paragraphs describing how this area works and how it connects to the others. One stable uppercase anchor code per area, in the heading.>

## 6. Cross-cutting qualities

<The guarantees holding across the whole product — security, privacy, offline, reliability — grouped by theme, each stated positively.>

## 7. Success metrics

- <One line per note in `product/metrics/`: the link, then the target. The definition and the last measured value live in the note.>

## 8. Open questions

- <A concrete product decision that blocks design or implementation.>
```

**`designs/overview.design.md`** — the entry-point design doc, for the subjects that underpin every feature. A subject that belongs to one feature gets its `<subject>.design.md` in that feature's folder instead. `/design` writes both.

```markdown
---
type: design
subject: overview
updated: <today, YYYY-MM-DD>
tags:
  - sdlc/design
related:
  - "[[prd]]"
---
# <product> — design

<One or two sentences: what the product is built from, and where the detail lives. Never what this document covers or leaves out.>

---

## 1. Foundations

<Only the rules holding across every part below, that a later section relies on instead of restating. Three to seven bullets, qualitative. Omit the section when there are none.>

---

## 2. <First part, flow, or surface>

<One sentence naming its role. Do not repeat the heading.>

### 2.1 Structure

<A reference to the diagram of the parts and what connects them, with a one-line caption. The `diagrams` skill says how one is drawn and where it lives.>

### 2.2 Behavior

<One unit of work followed from where it enters to where it leaves.>

### 2.3 States

| State | What happens |
| --- | --- |
| <state> | <what this design does that a reader would not assume> |

### 2.4 Variation and limits

<How the behavior changes by role, configuration, volume, or screen width, and the limits it holds within.>
```

`related` links the project's PRD. When the framework root holds `projects/`, qualify the wikilink — `"[[projects/<project-name>/prd|prd]]"` — because every project's PRD is named `prd`. Outside a vault it is the relative path: `../prd.md`, or `../projects/<project-name>/prd.md`. Keep only the sections that have something specific to say — an empty heading is deleted, never filled — and leave out any part that is not designed yet.

**`<project>/roadmap.md`** — the title alone. `/plan` adds each epic's section when it plans the first ticket of a feature, and the **`ticket-board`** skill holds the section, the table, and the order its rows keep.

```markdown
---
type: roadmap
updated: <today, YYYY-MM-DD>
tags:
  - sdlc/roadmap
---
# <product> — roadmap
```

**`work/`**, at the framework root — the three buckets, `backlog/`, `in-progress/`, and `done/`, empty. Write no ticket template into it: the template lives in the `ticket-board` skill, and an older `tickets/TEMPLATE.md` reads as nothing.

## 5. Report and hand off

Everything the user reads here follows the **`technical-writing`** skill (namespaced `sdlc:technical-writing`) — load it before you report.

Say **where the framework root and the project are** and, when you wrote one, that `.sdlc.json` now points at the project. Report the tree you created, marking each file `created` or `kept`, and each moved file with its old and new path. When you ran the PRD split, report it as its own block: the notes written per type, the PRD sections rewritten, and anything you left inline because it was prose. When you ran the feature migration, report it as its own block: the features opened with their codes and statuses, the design docs moved into each one, the docs kept in `designs/`, and any feature whose status the work root contradicted. When you moved the board into `work/`, report it as its own block: the tickets moved per bucket, and each ticket left without a feature.

**Then report the registry**: one line per repository — the code, the path, and the `what` line — and say that `sdlc.json` is machine-local and gitignored. Name any repository you could not reach, and say that running setup again from inside it registers it.

**Then say how to start a run from the vault**, which is the shape this registry buys:

```shell
cd <framework root>
claude --add-dir <work root> [--add-dir <work root> …]
```

One `--add-dir` per repository in the registry. Inside a session that is already open, `/add-dir
<work root>` does the same thing. Without it the session can read the board but cannot write code. A repo-rooted run needs none of this, and keeps working exactly as before.

Then offer the next step, in this order:

1. `/prd <product>` — fill the PRD first. It writes the goals, the non-goals, the personas, the problems, and the metrics as notes under `product/`, and the PRD's own prose around them. It also chooses the product's terms and writes each one's entry in `glossary.md`, so every later document takes its vocabulary from there.
2. `/feature <name>` — open a feature for each thing a customer can do. The feature holds its design docs and the code that numbers its tickets, so it comes before both.
3. `/design <target>` — specify how each system, flow, or surface works once the PRD names it. Each run writes or updates one design doc, in its feature's folder or in `designs/`.
4. `/plan <request>` — turn a request into roadmap tasks and tickets in `work/backlog/`. The roadmap starts with no epic in it.
5. `/orchestrate` — start building once the roadmap has a task.

Do not run these yourself. Name them and stop.
