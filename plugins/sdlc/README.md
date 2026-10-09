# sdlc

Plan, review, implement, and verify a change, with clean architecture rules for TypeScript,
React, and TanStack Start. Thirteen commands drive seven agents, and fifteen skills hold the rules they
all follow. One of those commands needs nobody in the room: `/run-roadmap` puts a **cto** agent
where the user would be and builds the roadmap unattended.

Part of the [husdeli skills](../../README.md) marketplace.

## Install

In Claude Code:

```
/plugin marketplace add husdeli/skills
/plugin install sdlc@husdeli-skills
```

In Codex:

```shell
codex plugin marketplace add husdeli/skills
codex plugin add sdlc@husdeli-skills
```

Start a new session after installation so the skills become available.

## Layout

```
.claude-plugin/plugin.json       # Claude Code plugin manifest
.codex-plugin/plugin.json        # Codex plugin manifest
skills/                          # shared rules and document skills, read by both runtimes
codex-skills/                    # Codex entry points, never loaded by Claude Code
agents/                          # agent definitions and Codex role contracts
commands/                        # Claude commands and shared workflow sources
scripts/                         # run-roadmap.sh, the unattended launcher
```

## Where your product docs live

Every document the plugin reads or writes belongs to one **project** — one product and every
document about it — and every line of code it writes sits in a **work root**, which is one code
repository. The recommended home for the
documents is a folder in an **Obsidian vault**, outside the repository — [the section below](#recommended-keep-them-in-an-obsidian-vault)
says why. The in-repository option is `.sdlc/` at your repository root, which is what every command
falls back to when nothing points elsewhere. The layout is the same wherever the project sits:

```
<project>/              # a folder in your vault, or .sdlc/ in the repository
  sdlc.json             the repositories this product is built in — machine-local,
                        gitignored, and what lets one board drive several repos
  prd.md                product requirements — what the product does and why
  glossary.md           the product's terms — one ## heading per term, defined once
                        here and linked from every other document
  roadmap.md            the work that is left, in order, grouped by epic
  product/              the pieces the PRD is assembled from — one note each
    goals/              self-hosted-first.goal.md
    non-goals/          no-mobile-app.non-goal.md
    personas/           solo-operator.persona.md
    problems/           tools-need-a-server.problem.md
    metrics/            weekly-active-vaults.metric.md
  features/             one folder per feature — one thing a customer can do
    checkout/
      checkout.feature.md    the index — what the customer can do, its state, and
                             the code that numbers its tickets
      checkout.design.md     the design docs that belong to this feature
      payment-retry.design.md
    …
  designs/
    overview.design.md  the design docs that underpin every feature — an app shell,
    app-shell.design.md an auth model, a shared data model
    …
  diagrams/
    checkout.excalidraw.md   one file per diagram, referenced by any document
  business/
    business-plan.md    the commercial case: who pays, unit economics, break-even
    competitors/        one note per competitor, listed in the plan by a Dataview query
  tickets/
    TEMPLATE.md         copy per task, named <EPIC>-<NNN>-<slug>.md
    todo/               AUTH-001-user-login.md
    in-progress/        AUTH-002-session-timeout.md
                        AUTH-002-session-timeout.worklog.md
    done/               BILLING-001-invoice-export.md
                        BILLING-001-invoice-export.worklog.md
```

**A term is defined once, in `glossary.md`.** Each term is a `##` heading, and every other document
links that heading at the term's first use instead of writing the definition a second time. Whoever
coins a term writes its entry, so `/prd`, `/design`, and `/plan` each keep the file current. The
`glossary` skill holds the rules.

**The PRD is assembled, not written whole.** A goal, a non-goal, a persona, a problem, and a
success metric are each their own note under `product/`, because something outside the PRD points
at each one — a feature cites the goal it advances, the business plan sells to a persona, a
milestone proves a metric — and because each has a state of its own: met, dropped, deferred,
measured. The PRD's sections 2, 3, 4, and 7 are one line per note. Its overview, its
product areas, and its cross-cutting qualities stay prose, because narrative does not decompose.
The `product-intent` skill holds the five shapes.

That is what makes questions answerable that no single document could answer before: which features
advance one goal, which goal has nothing being built for it, which deferred non-goal is due for
review, which metric has gone stale.

**A feature is one thing a customer can do**, and it owns a folder. The index,
`<feature>.feature.md`, says what the customer can do and whether it is `Planned`, `In Progress`,
or `Shipped`, and it carries the uppercase code that numbers the feature's tickets — the feature
and its epic are one thing seen from two sides. Everything that points at the feature points at
that note: the roadmap epic, each ticket, and the business plan's table of what the product does,
which is a Dataview query over `features/` rather than a list anyone maintains by hand. `/feature`
opens one, and the `feature` skill holds the rules.

Each kind of document gets its own folder once there can be more than one of it. A design doc
covers one subject — a system, a service, a flow, an integration, a rule, or a screen. **Ownership
decides where it sits**: in its feature's folder when it belongs to one feature, and in `designs/`
when it underpins every feature. `designs/overview.design.md` is the entry point that names the
parts of the whole solution and points at the rest.

**The roadmap shrinks; the feature register does not.** An epic's section is deleted when its last
task is done, and the feature note stays, marked `Shipped`. So `features/` is the list of what the
product does, `roadmap.md` is the list of what is left, and `tickets/done/` is the record of what
happened.

A ticket moves between the three status folders as the work progresses, and its `Status` field
always names the folder it sits in. The commands move it for you: into `in-progress/` when an
orchestrator starts the task, into `done/` when verification passes. A project that already
keeps its design docs or its tickets in one flat folder, or that has no `features/` folder at all,
keeps working — `/setup` offers each migration, and never forces one.

**A ticket in flight says who holds it, and keeps a worklog of what was decided.** Its
`Assignee` field names whoever is working on it right now — `implementation-planner` while the
plan is written, `coding` while the change is made, `verify, code-reviewer` while the gate runs,
`user` when a run escalates and a person has to act, `—` when nobody holds it. Beside it sits
`<ID>-<slug>.worklog.md`, one entry per stage: the direction the plan settled on, the issues the
review sent back, the code-level calls the plan left open, what the verification found. All of
that used to live in one session's context and vanish with it, so a task picked up a week later
started from the diff. The orchestrating command is the only writer of both — the agents report
their decisions and it writes them down — and the worklog follows the ticket into `done/`, where
the two together are the record of the task.

Every ticket belongs to an **epic** — a named group of tasks that deliver one feature. The
roadmap holds one section per epic, the epic's code prefixes every ticket ID under it, and the
numbering restarts at 001 in each epic. That is what keeps two branches apart: each plans into
its own epic, so both can add a first ticket and neither overwrites the other on merge.

**The roadmap holds the work that is left, and nothing else.** One table row per task — ID,
title, priority, status, the blockers it is still waiting on, and its ticket. No description, no
acceptance criteria: those live in the ticket, so the roadmap stays a page you can read in one
pass.

**Every cell in it comes from a ticket**, which is the record: the priority, the status, the
outstanding blockers computed from the ticket's own `Depends on` field, and the row's very
existence. When a row and its ticket disagree, the ticket wins and the row is corrected — the
commands that pick a task do that for the rows they read, and
[`scripts/build-roadmap.py`](scripts/build-roadmap.py) rebuilds the whole file from the tickets:

```shell
plugins/sdlc/scripts/build-roadmap.py --check    # what differs, as a diff; writes nothing
plugins/sdlc/scripts/build-roadmap.py            # rewrite every table from the tickets
```

**Reading a table top to bottom is reading the order to build in.** Three rules make that true: a
task never sits above something it still depends on; a blocker carries the highest priority of
anything waiting on it, so the small chore holding up critical work rises to the top instead of
sinking below unrelated middling work; everything else goes by priority. A `Low` row at the top is
not a mistake — the row under it is the urgent task it is holding up.

When a task is finished, the orchestrator **deletes its row** instead of marking it completed,
drops its ID from the `Depends on` cells that named it, and closes the epic once its last row
goes. The ticket in `tickets/done/` is the record of what was built, so nothing is lost. What does
get written back is a correction: when finished work changes what a remaining task has to do, that
task's row and ticket are rewritten, and a constraint that governs a whole epic becomes one
`**Note**:` line under it.

Run **`/setup`** in Claude Code or **`$sdlc:setup`** in Codex to create it.
Every agent falls back to the repository root when a repository already keeps these documents there.

### Recommended: keep them in an Obsidian vault

`/setup` asks where the project goes, and recommends a folder in an Obsidian vault outside the
repository. Four reasons:

- **The documents are readable and editable without the repository**, on every device the vault
  syncs to. You can read the roadmap on a phone, and write a ticket without opening an editor.
- **They stay out of the code's history.** A branch switch never rewrites the roadmap, two
  branches never conflict over the same ticket file, and a pull request carries the code alone.
  The board is the same board whatever branch you are on.
- **Obsidian reads the board as a database.** Properties, backlinks, search, and the graph work
  across the whole structure, so `status: In Progress` across every epic is one query.
- **One vault holds every project.** The documents for all of them sit side by side, and a note
  of your own can link straight into any ticket.

Pick **In the repository** instead when you keep no vault, or when the team only ever reads these
documents through the repository: there the documents are versioned with the code, they travel
with a clone, and a review sees a document change beside the change it describes.

Point `/setup` at a vault and it writes the structure there, then writes a pointer file
at your repository root so every command still finds it:

```json
{
  "root": "~/Vaults/Personal/Acme",
  "kind": "vault"
}
```

It writes `sdlc.json` in the project in the same run — the registry naming every repository the
product is built in, which is what lets one board drive several. Every command and agent resolves
`.sdlc.json` before it reads anything, so `/plan`,
`/orchestrate`, `/prd`, `/design`, and `/review` work against the vault exactly as they work
against `.sdlc/`. A ticket still moves from `todo/` to `in-progress/` to `done/` as the
orchestrator builds it.

Inside a vault the documents are written the way Obsidian reads them, and nothing else changes:

- **No folder starts with a dot**, because Obsidian hides those. The project is named after the
  product — or is the vault root itself, when you keep a vault for this one product and
  point `/setup` at it.
- **Fields become properties.** `**Status**: In Progress` under the title becomes
  `status: In Progress` in the frontmatter, so a ticket is queryable in Bases or Dataview. The
  property is the record the commands rewrite.
- **References become wikilinks.** The roadmap cites `[[AUTH-001-user-login]]`, a design doc cites
  `[[prd]]`, and a glossary term is cited as `[[glossary#Workspace owner]]`. Obsidian resolves them
  by name, so backlinks and the graph work, and a link survives the ticket moving between status
  folders.
- **No `.gitkeep`, and no `git mv`** where git does not track the folder.

The `sdlc-structure` skill holds these rules, and the plugin loads it whenever the destination is a
vault. Pick **In the repository** at the prompt and none of it applies.

## One board, several repositories

A product is often more than one repository — a web app and an API, a client and a service, an app
and its infrastructure. The vault is what lets one board cover all of them, because the documents
belong to the product rather than to any one tree.

**`/setup` writes two pointers**, so the pair can be driven from either end:

- **`sdlc.json` in the project** — the registry. One entry per repository: a short code, the path,
  and one line saying what belongs in that repository. It is machine-local and gitignored, because
  the paths exist on one machine.
- **`.sdlc.json` in each repository** — the pointer back to the project, as before.

```json
{
  "repos": {
    "web": { "path": "~/Projects/acme-web", "what": "TanStack Start app — every screen" },
    "api": { "path": "~/Projects/acme-api", "what": "Fastify service — the API and the jobs" }
  }
}
```

**Then run the workflow from the vault:**

```shell
cd ~/Vaults/Personal/Acme
claude --add-dir ~/Projects/acme-web --add-dir ~/Projects/acme-api
```

One `--add-dir` per repository — without it the session can read the board but cannot write code.
Inside a session already open, `/add-dir <path>` does the same. Then `/orchestrate`, `/whats-next`,
`/plan`, and the rest work exactly as they do inside a repository, over every repository at once.

**A ticket never names its repository.** The run works out where a task is built, when it picks the
task: from the design doc the ticket cites, the ticket itself, the epic, each registry entry's
`what` line, and, when that is not enough, the code already in each candidate tree. It asks you when
the evidence leaves it open — and the `cto` agent answers instead in an unattended run. The choice
lands in the worklog beside the ticket, with the evidence that settled it, so a task built two weeks
ago still says which tree it landed in.

From there the run is per repository: that repository's `AGENTS.md`, its test suite, its code review,
its commit, its git history. A task that genuinely has to change two repositories at once does each
of those in both, and passes only when both pass.

**Nothing changes for a single-repository project.** Start a session inside the repository and every
command behaves exactly as it did — the registry is read only when the session starts in the vault.

## Running the roadmap unattended

Every other command in this plugin stops and asks you something. `/run-roadmap` does not, because it
is built for the case where you are not there: the **cto** agent answers in your place, the task is
committed when it passes, and a launcher script starts the next one in a fresh session.

```shell
# from the repository you want built
plugins/sdlc/scripts/run-roadmap.sh --max-tasks 5
plugins/sdlc/scripts/run-roadmap.sh --roadmap docs/roadmap.md --keep-going --yes

# or from the vault, over every repository in the registry
cd ~/Vaults/Personal/Acme && ~/Projects/skills/plugins/sdlc/scripts/run-roadmap.sh --max-tasks 5
plugins/sdlc/scripts/run-roadmap.sh --project ~/Vaults/Personal/Acme --yes
```

**Run it from the project and it drives every repository the registry names.** It grants the
session each one with `--add-dir`, checks every tree is clean before it starts and between tasks,
commits each task in whichever repository that task landed in, and reports the commit range per
repository at the end.

**One task per session** is what makes a long roadmap possible: the script calls
`claude -p "/sdlc:run-roadmap"` once per task, and each task starts with a clean context and ends
with its own commit. The command prints one `RUN-ROADMAP-RESULT` line, the script reads it, and the
roadmap itself is the loop counter — the run ends when the last row is gone.

**What stops a run:**

| It stops when | Because |
| --- | --- |
| The roadmap has no task whose dependencies are satisfied | There is nothing to build |
| The CTO hands a decision back | Money, credentials, anything irreversible, the security model, a legal call, or a PRD contradiction it cannot settle |
| A stage runs out of rulings | One ruling per stage, two per task. A third is a person's problem |
| An agent returns nothing usable | A dead agent is not a thing to retry around |
| A tree is dirty before it starts, or a commit is rejected | Every task commits with `git add -A`, so the ground has to be clean — in every registered repository |
| A registered repository is missing or is not a git tree | The registry is machine-local, so it can point at a path this machine does not have |
| A task runs past `--timeout` | The task and everything it started are killed, and the run stops |

**Before the first run:** be on a branch you are willing to throw away, in every repository the run
can touch. The script checks that each one is in git with a clean tree, and it commits to the branch
each one is on — one commit per task, never a
push. It runs with `--permission-mode bypassPermissions`, because a permission prompt in a headless
session is a dead run, so the tasks it builds get your full tool access without asking. Read
`--help` first, and read `git log` after.

**What you read afterwards** is the worklog beside each ticket in `done/`. Every CTO answer is in
there — the decision, what it beat, and the cost it accepted — because a run nobody watched is only
worth as much as its record.

## What's in it

### Skills
- **clean-fullstack-architecture** — Clean Code + Hexagonal Architecture with strict
  dependency rules across all layers; domain-cohesive feature grouping. Services are classes
  of static methods that own the DTOs their API speaks and never return one; domain logic
  names only domain models; an `adapters/` layer is the single place the two shapes meet.
- **ai-planning-workflow** — The hand-driven ticket → plan → implement workflow: phased
  implementation with a feedback checkpoint after every step, design agreement before UI work,
  and when to start, log, and complete a ticket. The artifacts it works on belong to
  `ticket-board`.
- **ticket-board** — The board itself, and the one place its rules are written: where a ticket
  lives, the three status folders it moves through, the epic that numbers it, the roadmap that
  holds only the work that is left, the `Assignee` field that names who holds it, and the worklog
  that records what was decided. It also defines the three transitions — starting a ticket,
  finishing one, and stopping without finishing — each of which writes the status field, the
  folder, and the roadmap row in one tool block, so the three can never disagree.
- **agent-pipeline** — How a command drives subagents: spawn each role once and resume it with
  `SendMessage` rather than re-spawning, keep a fresh verification agent per run, put concurrent
  calls in one tool block, parse the single JSON block every agent ends with and retry once before
  calling the run aborted, keep the spawn prompt thin, never duplicate the gating run, and end in
  exactly one of `completed`, `escalate`, or `aborted`.
- **ts-clean** — Framework-agnostic rules for any `.ts`/`.tsx` file: one module per file
  named after its primary export, dot notation for the modules that carry an architecture
  role (`user.service.ts`, `user.repository.ts`, `user.dto.ts`) while plain modules keep
  plain names, static top-of-file imports (with the code-splitting /
  SSR / optional-dependency exceptions spelled out), self-documenting code over
  comments (a hard cap of one or two per file, one sentence each, and never a pointer to a
  file, a line, or a finished ticket), and configuration extracted into `.config.ts` modules that are the only place
  `process.env` is read — required variables throw by name when missing, optional ones get
  an explicit typed default, and secrets are never defaulted.
- **react-clean** — The React layer on top of `ts-clean`: one component per file, at most
  one `useEffect`, no data-layer access from components, size and props ceilings, no prop
  drilling (compose instead), and the react.dev "You Might Not Need an Effect"
  anti-patterns.
- **clean-tanstack-start** — The TanStack Start layer on top of `ts-clean`: the
  `.functions.ts` / `.server.ts` / plain `.ts` file split, server-only modules kept out of
  anything a client file can import, configuration split the same way (client-safe values in
  `*.config.ts`, secrets in `*.config.server.ts`, which server code may read from but never
  the reverse), and server functions imported statically only — never
  `await import()`, which defeats environment shaking and can leak server logic into the
  client bundle. Plus the two safety rules: every server function is its own auth boundary
  (a route `beforeLoad` guard isn't the data boundary), and no `Cache-Control: public` on
  an identity-dependent response.
- **technical-writing** — The standard for every text a reader works from: a brief, a plan, a
  review verdict, a report, a PRD, a design doc, a ticket, a commit message, a pull-request body.
  Context first, then the answer, then the evidence. Rules grouped the way they are used — stance
  and voice (a named actor, the active voice, nothing unverified, no sales language), reader
  engagement (purpose before mechanism, a term of art defined at its first use, procedures as
  numbered steps, the warning before the step, the edges specified), hedging and boosting (an
  assumption marked as one, a failure reported as a failure, exact versions and defaults), and
  signposting (the thing named in words rather than by its file name, the glossary's term every
  time, one home per fact, the shape the reader's job needs). Governs prose only — code,
  identifiers, paths, quoted output, and the agents' `json` blocks stay exact, beside the sentence
  rather than inside it: a command in its own block, the files a change touched in a list, a
  defect's location next to the issue. Every agent, command, and document skill in this plugin
  routes its human-facing output through it.
- **social-writing** — The standard for a text written for a feed: a LinkedIn post, a tweet, a
  thread, a caption, an announcement. The reader is mid-scroll and gives the first line about one
  second, so the shape is hook, body, close. The same four rule groups, answered for that reader —
  stance and voice (a point of view, self-mention, the cost of the lesson), reader engagement (one
  question at the end, the reader's situation before your answer, a first line that survives
  truncation), hedging and boosting (boost what you can show, hedge the scope and never the hook,
  a number on every strong claim), and signposting (the payoff signalled up front, numbered parts,
  white space, no document transitions). Names the failure modes it refuses: the context-setting
  opener, broetry, engagement bait, the humble-brag, the false reveal, the list of negations.
  Invoked directly, it re-pitches a message that didn't land.
- **product-intent** — The five pieces the PRD is assembled from, each its own note under
  `product/`: a goal, a non-goal, a persona, a problem, and a success metric. Holds what earns a
  note (something outside the PRD points at it, and it has a state of its own), the properties and
  lifecycle of each — a goal is `Committed`, `Met`, or `Dropped`; a non-goal is `Excluded` or
  `Deferred`, and is deleted rather than restated when the product decides to build it; a metric
  carries its last measured value and the date it was read — and the rule that a citation links the
  note and never repeats its reasoning.
- **feature** — The feature: one thing a customer can do, with its own folder, an index note
  that says what the customer can do and whether it is `Planned`, `In Progress`, or `Shipped`, and
  the uppercase code that numbers its tickets — the feature and its epic are one thing. Holds how a
  feature is chosen, named, coded, and retired, the rule that a `Shipped` status is verified
  against the code and never taken from the board, and the query that turns `features/` into every
  list of what the product does.
- **design-doc** — Create or update a design doc specifying how a solution works: the parts
  it is built from, how work flows through it end to end, the states it reaches, and the
  limits it holds within. The subject is a system, a service, a flow, an integration, a rule,
  or a screen — a user interface is one case, not the default. One file per subject, named
  `<subject>.design.md`, in its feature's folder when it belongs to one feature and in `designs/`
  when it underpins every feature. The doc states the intended end state, not how to build it.
- **frontend-design** — Agree what a screen looks like before it is built. Reads the PRD, the
  design doc, and the design system the codebase already has, publishes a static mockup as an
  Artifact — every state, the small screen, placeholder data, nothing wired up — and iterates
  until the user agrees. Then it records the decisions, so the code is written from an agreement
  and not from a picture nobody wrote down. It writes no production code.
- **diagrams** — A picture of a shape, in one place: `diagrams/` in the project, one
  `<name>.excalidraw.md` file per diagram — the Obsidian Excalidraw format, so a vault renders and
  indexes it. The skill ships its own builder: write a small JSON spec of nodes, edges, regions and
  notes, run `scripts/excalidraw_md.py`, and get a valid drawing with bound labels and bound arrows,
  plus a `validate` command that catches a file Obsidian would not open. It holds five layouts, one
  meaning per color, how each of the nine kinds of diagram is shaped, and the budget — under 20
  elements. A document references the file with a one-line caption, and the prose stays complete
  without the picture, because every agent here reads a document as text. Where `python3` is
  missing, the document carries an ASCII diagram instead — one shape never gets both.
- **glossary** — The product's terms, and the one place each is defined: `glossary.md` in the
  project, one `##` heading per term, in alphabetical order, with two or three sentences under it.
  It holds where a term comes from, one term per concept, the domain word ahead of the code symbol,
  what to do when the product has no name for something yet, and the link every other document
  writes at a term's first use — a relative anchor in the repository,
  `[[glossary#Workspace owner]]` in a vault. Prose outside the project uses the term with no
  link. Every document skill and every agent reaches the terms through this one skill.
- **business-plan** — Create or update the business plan and one note per competitor. Every
  figure is a sourced fact or a numbered assumption in a register, each topic is written once and
  linked everywhere else, competitor prices come from the web with a checked date, and in a vault
  the plan lists the competitors — and the features the product ships — with a Dataview query
  instead of a copied table. What the product does is never typed out here: it comes from
  `features/`, and a status it quotes is checked against the code first.
- **prd** — Create or update a product requirements document: product-only content,
  cohesive per-area descriptions with stable anchor codes, and positive framing. The terms it
  chooses are defined in `glossary.md`, never in the PRD.
- **sdlc-structure** — The structure the plugin creates, and where the documents and the code
  live: the project and its folders, every kind of document with its path, its states, and the
  skill that governs it, which document owns each fact and which way a link points, the work root,
  the `sdlc.json` registry naming every repository the product is built in, the `.sdlc.json`
  pointer file, and the Obsidian-vault conventions — folder naming, frontmatter properties,
  wikilinks, and when a move uses `git mv`. A short index routes to one reference file per topic,
  so a command reads only the part its job needs. It also holds how a run
  started in the vault works out which repository a task is built in, and how it reaches a tree that
  is not its own working directory. Every command and agent resolves the project and the work root through it,
  so one project can keep its documents in the repository and the next can drive four repositories from a
  vault.

**A rule is written in exactly one skill, and the commands load it.** A command file holds its own
sequence — the stages, the gates, the questions it asks — and names the skills that hold everything
else. That is why `/orchestrate` and `/orchestrate-quick` can differ in six ways and still agree on
what a ticket is, and why changing how a status transition works is one edit rather than six.

### Agents
- **feature-interviewer** — reads the PRD and design doc, researches the feature on the web,
  and returns a Discovery Brief that challenges the idea with open decisions and options.
- **implementation-planner** — turns a task + codebase + researched best practices into a
  directional plan: where the work lives, what each item must achieve, which approach to
  follow — and no code for the coding agent to copy.
- **plan-reviewer** — reviews a plan for correctness and convention alignment, and returns
  `APPROVED` or `CHANGES_REQUESTED`.
- **code-reviewer** — reads the code under review — a working-tree diff, a branch, or
  named files — and returns `APPROVED` or `CHANGES_REQUESTED`. Checks the acceptance criteria,
  correctness, scope, the plugin's skills, the codebase's conventions, error handling, tests,
  and secrets, and confirms every issue in the file before reporting it. Writes no code.
  Verification answers "does it pass?"; this answers "is it the right code, and all of it?".
- **coding** — implements a work brief and runs a targeted self-check. The brief is an approved
  plan from either orchestrator, or a request `/code` sends with no plan at all.
- **verify** — runs the repository's gating commands (tests, lint, typecheck, e2e when there is
  one) concurrently and reports pass/fail per command. Writes no code, and reviews none either.
- **cto** — stands in for you when nobody is in the room. It reads the PRD, the glossary, the
  feature notes, and the design docs once, then answers what `/orchestrate` would have asked you: which task to build next,
  whether it gets end-to-end tests, how each open decision goes, and what happens when a stage runs
  out of retries — one more cycle with guidance, a narrower task, a deferred task, or the end of the
  run. It hands a decision back to you only for the things a person must own: money, credentials,
  anything irreversible, the security model, a legal or licensing call, and a contradiction with the
  PRD it cannot settle from the documents. It writes no file — `/run-roadmap` records every answer
  in the ticket and the worklog, which is how an unattended run stays readable afterwards.

### Commands and Codex skills
- **/setup** — asks where the project goes — in an Obsidian vault, which it recommends, or in
  the repository as `.sdlc/` — registers every repository the product is built in as `sdlc.json` in
  the project, then creates it with stub files for the PRD, the glossary,
  the design doc, the roadmap, a ticket template, the `product/` folders, the `features/`,
  `designs/`, and `diagrams/` folders, and the `todo/`, `in-progress/`, and `done/` ticket
  folders. An outside folder gets a `.sdlc.json` pointer file at
  the repository root, and a vault gets the Obsidian shape: frontmatter properties, wikilinks, and no
  dot-folders. Never overwrites an existing file, and offers to move a root-level
  `prd.md`, `glossary.md`, `design.md`, or `tickets/` into the folder with `git mv` — including
  sorting a flat tickets folder into the three status folders, moving loose `*.design.md` files into
  `designs/`, and renaming a lone `design.md` to `designs/overview.design.md`. It also offers to
  **build the feature register** on a project that has none — proposing one feature per roadmap
  epic, showing you which design docs move into each feature folder and which stay cross-cutting,
  and moving them once you approve the table — to **split a PRD that still holds its goals,
  personas, problems, and metrics inline** into notes under `product/`, after it shows you the
  mapping and you approve it, to
  migrate a project-wide ticket scheme (`SW-001`, `SW-002`, …) onto epic-prefixed IDs, after it
  shows you the epic grouping and you approve it, and to clean a roadmap that still holds
  finished work — deleting the completed rows and folding each per-task detail section into the
  ticket that should hold it.
- **/feature** — opens a feature, or keeps an existing one true: the goal it advances and the
  personas it serves, the folder, the index note, the
  code its epic and tickets take, and the status, which it checks against the code rather than the
  board. Run it before `/design` and `/plan` for anything new a customer can name.
- **/plan** — turns a request into the documents the rest of the plugin reads: it interviews
  with the **feature-interviewer** agent, settles the open decisions with you, then updates the
  PRD, opens or updates the feature, writes the design docs, appends one roadmap row per task under its epic, and writes one
  ticket per task into `tickets/todo/`. The detail goes in the ticket, never in the roadmap. It
  writes no code and sets no status past pending — `/orchestrate` takes it from there.
- **/whats-next** — answers what can be worked on right now. It reads the roadmap and the ticket
  folders, sorts every task into in flight, ready to start, and waiting on a dependency, and
  names the one to start next. For a task in flight it names who holds it and quotes the last
  worklog entry, so a task that escalated says where it stopped. It writes nothing and moves no
  ticket: it reports the state and hands off to `/orchestrate`. When the ticket folder and the
  roadmap marker disagree, it says so rather than fixing it.
- **/orchestrate** — offers you every roadmap task whose dependencies are satisfied, asks which
  one to build and whether it gets end-to-end tests, then drives it through
  interview → plan → review → implement → verify and code review using the six agents above.
  The verify stage runs the gating commands and the code review side by side, and the task is
  finished only when the commands pass and the review returns `APPROVED` — then the ticket moves
  to `done/` with its worklog and the roadmap row is deleted. At each stage boundary it rewrites
  the ticket's assignee and appends the stage's worklog entry, so an escalated task is left
  assigned to you with the reason written down.
- **/orchestrate-quick** — the short pipeline for a task that is already well understood:
  plan → one review → implement → verify and code review, with no interview and no review
  gating. Takes a task description or a roadmap/ticket path. It asks nothing: end-to-end tests
  default to no, and it reports that default.
- **/run-roadmap** — `/orchestrate` with nobody in the loop. It never asks you anything: the **cto**
  agent picks the task and calls the end-to-end question, the interview always runs and the CTO
  settles its decisions, and a stage that hits its cap gets a CTO ruling — retry once with guidance,
  narrow the task, defer it, or end the run — instead of stopping to wait for you. The finished task
  is committed on the branch you are on, and nothing is pushed. One invocation is one task, and it
  ends with a machine-readable result line, so
  [`scripts/run-roadmap.sh`](scripts/run-roadmap.sh) can loop it over a whole roadmap in a fresh
  session per task:

  ```shell
  plugins/sdlc/scripts/run-roadmap.sh --max-tasks 5
  ```

  The script refuses to start outside git or on a dirty tree, kills a task that runs too long,
  stops the moment the CTO hands something back, and prints one line per task at the end with the
  commit each one produced. Read `--help` before the first run, and read the commits after it.
- **/code** — hands your request straight to the **coding** agent, which loads the coding skills
  itself. One agent, no planner, no reviewer, no verify agent: it finds the files, writes the
  change, runs a targeted self-check, and the command reports what it did and what nobody ran.
  Use it for a fix or a small feature you already understand; it hands off to
  `/orchestrate-quick` or `/orchestrate` when the request turns out to need a plan. When the
  request changes what a user sees, it runs the `frontend-design` skill first and waits for you
  to agree the mockup before the coding agent starts.
- **/review** — reviews code that already exists with the **code-reviewer** agent: the
  uncommitted changes by default, or a path, a branch, a commit range, or a ticket you name.
  Reports the verdict and the defects, each with its file and line. Add `fix` to hand the
  blocking issues to the coding agent and re-review the result once. Use it for work that never
  went through an orchestrator — a `/code` change, code you wrote by hand, a branch to read
  before a pull request.
- **/design** — loads the `design-doc` skill to create or update a `<subject>.design.md` for a
  given system, service, flow, integration, or screen — in the feature's folder when it belongs to
  one feature, in `designs/` when it underpins every feature.
- **/frontend-design** — loads the `frontend-design` skill to agree the look of a screen, a
  component, or a flow before it is built: it publishes a static mockup as an Artifact, iterates
  with you, and records what you agreed. It writes no production code — `/code` builds it after.
- **/prd** — loads the `prd` skill to create or update a product requirements document for
  a given product or feature, the `product-intent` skill for the goals, non-goals, personas,
  problems, and metrics it writes as notes under `product/`, and the `glossary` skill for the
  terms it introduces.
- **/business-plan** — loads the `business-plan` skill to create or update the business plan in
  `business/`, and researches one note per competitor into `business/competitors/`. Name a
  competitor to add or refresh just that note.
- **/explain** — explains what is happening in plain language: the work you just did, a
  file, an error, a diff, or a concept. Reads the code before explaining, defines every
  term of art on first use, and treats code as an anchor rather than the explanation.
- **/review-text** — reviews a text written for people. It names the register first — technical
  or social — loads that skill, and judges the text by its own rules, because a post that opens
  with a hook is right where a document would be wrong. Every finding names a stable rule code,
  quotes the text as it stands, and carries the sentence that replaces it. The reply ends with a
  `json` findings block a tool can consume, so the same review can drive a linter later. Add `fix`
  to apply the findings that have a replacement.

Use these equivalents in a Codex prompt:

| Claude Code | Codex |
| --- | --- |
| `/setup [product]` | `$sdlc:setup [product]` |
| `/orchestrate [roadmap]` | `$sdlc:orchestrate [roadmap]` |
| `/orchestrate-quick [task]` | `$sdlc:orchestrate-quick [task]` |
| `/run-roadmap [roadmap]` | `$sdlc:run-roadmap [roadmap]` |
| `/code [request]` | `$sdlc:code [request]` |
| `/review [target]` | `$sdlc:review [target]` |
| `/plan [request]` | `$sdlc:plan [request]` |
| `/design [target]` | `$sdlc:design-doc [target]` |
| `/feature [target]` | `$sdlc:feature [target]` |
| `/frontend-design [target]` | `$sdlc:frontend-design [target]` |
| `/prd [target]` | `$sdlc:prd [target]` |
| (product notes) | `$sdlc:product-intent` |
| `/business-plan [target]` | `$sdlc:business-plan [target]` |
| `/explain [target]` | `$sdlc:explain [target]` |
| `/review-text [target] [fix]` | `$sdlc:review-text [target] [fix]` |

Each Codex entry point lives in `codex-skills/`, and each one reads the shared source in
`commands/` or `skills/`. Claude Code scans `skills/` only, so no Codex instruction reaches a
Claude session.
