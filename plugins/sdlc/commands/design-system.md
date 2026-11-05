---
description: Show how complete a web project's design system is — catalog, tokens, components, stories — or add `board` to generate or refresh the Storybook design board, separate from the app, where anyone can see all of it.
argument-hint: "[board] [a repository code from sdlc.json, a path, or nothing for the current repository]"
---

# Design system

Report a web repository's design system against the **`design-system`** skill, or generate its design board.

Target: $ARGUMENTS

Load the **`design-system`** skill (namespaced `sdlc:design-system`) and the **`technical-writing`** skill (namespaced `sdlc:technical-writing`) first.

**`board` as the first word** runs the board mode in the last section, on the target that follows it. Without it, this command writes no file.

## Resolve the work root

| The target is | Read |
| --- | --- |
| A repository code | The `path` of that entry in `sdlc.json`. Load the **`sdlc-structure`** skill to find the registry. |
| A path | That directory. |
| Empty | The current repository. |

If the code is not in the registry or the path holds no `package.json`, say so and stop.

## Read the evidence

- `design-system.md` at the work root — the catalog.
- The top-level `components/` folder — every shared component and every `*.stories.tsx` beside one.
- The token source — `tokens/` and `style-dictionary.config.*` with the design-tokens layer, else the Mantine theme module.
- `.storybook/` — the board's config and pages — and the `board`, `board:build`, `tokens`, and `tokens:check` scripts in `package.json`.
- A sample of feature components and stylesheets, for raw values and bypassed catalog components (`design-system` Rules 2 and 4). Search for hex colors, `rgb(`, arbitrary Tailwind values (`-[`), and direct Mantine imports of a component the catalog wraps.

## Report

Start with one line: the work root, how many shared components there are, and how many are both catalogued and on the board.

Then one table, one row per shared component:

| Component | Catalog | Stories | Note |
| --- | --- | --- | --- |

Mark each cell **yes** or **missing**, and use the note for a catalog entry whose component no longer exists, an entry with no *Not for* line, or a stories file that skips a variant the props type has.

Then the system-wide rows, each **set**, **missing**, or **broken** with the file that shows it: the catalog header, the token source, the generated outputs (stale when `tokens:check` fails), the board config, the board's token pages, and the scripts.

End with what needs action, most impactful first: raw values and bypassed components by file, then the gaps above. When nothing needs action, say so in one line.

## Board mode

Run this mode only when the first word of the target is `board`. Resolve the work root as above.

1. **Check the board's packages.** When `storybook` and `@storybook/react-vite` are not in the dev dependencies, say so, name `/stack install` with the `board` layer, and stop. This mode installs nothing.
2. **Build the report above**, so the brief names every gap by file.
3. **Load the `agent-pipeline` skill** (namespaced `sdlc:agent-pipeline`), and spawn the coding agent **once**:

   ```
   Agent(subagent_type: "sdlc:coding", model: "opus",
         prompt: "Work root: <absolute path>.
                  Generate or refresh the design board as the design-system skill and its
                  board reference describe:
                  - set up .storybook/ (main.ts, preview.tsx) where it is missing or broken;
                  - write the Introduction page and the token pages where they are missing;
                  - write a stories file for each shared component listed below without one,
                    and add the missing variants to each listed stories file;
                  - add the board and board:build scripts where they are missing;
                  - draft a design-system.md entry for each uncatalogued component listed
                    below, from its code and its call sites, and mark each draft in notes.
                  Change no component, no token, and no app code. Run bun run board:build.
                  <the report's gaps, by file>")
   ```

   Parse its `json` block as `agent-pipeline` says. On `human_required` or non-empty `blockers`, report them and stop. When `board:build` failed, resume the agent with the failing output until it passes; when it is stuck, as `agent-pipeline` defines it, report what is left and stop.
4. **Show the drafted catalog entries** to the user. Each *For* and *Not for* line is a design judgment the agent inferred from code, so ask the user to confirm or correct them, and apply the corrections to `design-system.md` yourself.
5. **Report** what the board now shows: the pages written, the stories added, the components still missing from it, and the result of `bun run board:build`. Name `bun run board` to open it locally. Deploying it is the user's decision (`design-system` Rule 6) — offer it in the last line, and never deploy it from this command.

## Rules

- **The report writes nothing.** Only board mode writes, and only through the coding agent and the catalog corrections the user gave.
- **Board mode changes no component and no token.** A raw value or a bypassed component it finds is reported, and fixing it is a `/code` request.
- **The board renders the app's own theme.** A board with a theme of its own is broken, not finished.
- **Never deploy the board here.** It publishes the design system, and the user decides where and to whom.
