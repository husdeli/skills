---
description: Show a web project's stack layer by layer against the default, or add `install` to propose the missing installs, ask which optional layers the project needs, and install them on your yes.
argument-hint: "[install] [a repository code from sdlc.json, a path, or nothing for the current repository]"
---

# Stack

Report the stack of one web repository against the default in the **`web-stack`** skill, or bring it up to that default.

Target: $ARGUMENTS

Load the **`web-stack`** skill (namespaced `sdlc:web-stack`) and the **`technical-writing`** skill (namespaced `sdlc:technical-writing`) first.

**`install` as the first word** runs the install mode in the last section, on the target that follows it. Without it, this command writes no file and installs nothing.

## Resolve the work root

| The target is | Read |
| --- | --- |
| A repository code | The `path` of that entry in `sdlc.json`. Load the **`sdlc-structure`** skill to find the registry. |
| A path | That directory. |
| Empty | The current repository. |

If the code is not in the registry or the path holds no `package.json`, say so and stop. A repository with no `package.json` is not a web project yet, so every layer would take the default.

## Read the evidence

- `package.json` — dependencies, dev dependencies, and scripts.
- The lockfile, for the versions it pins and the package manager it implies.
- The config files that confirm a layer: `vite.config.*`, `drizzle.config.*`, `biome.json`, `playwright.config.*`, `vitest.config.*`, `postcss.config.*`, the global stylesheet.

A dependency that is installed but never imported counts as the layer's library only when its config or an import confirms it.

## Report

Start with one line: the work root, and how many layers match the default.

Then one table, one row per layer of the `web-stack` table, in its order:

| Layer | Project uses | Default | Status |
| --- | --- | --- | --- |

Status is one of:

- **default** — the project uses the default.
- **project's own** — the project uses another library. It stays, per `web-stack` Rule 1.
- **not set** — the layer is empty. The next change that needs it gets the default.
- **conflict** — two libraries fill the layer, such as ESLint next to Biome. Name both.

After the table, list only what needs action: each **conflict**, and each `web-stack` integration rule the config breaks, such as Mantine styles imported without the cascade layer order. Name the file for each. When nothing needs action, say so in one line.

## Install mode

Run this mode only when the first word of the target is `install`. Resolve the work root as above.

1. **Ask which optional layers the project needs.** One question, multi-select, listing `auth`, `database`, `forms`, `animation`, and `e2e`, each with one line on when a product needs it (`web-stack` Rule 2). Skip a layer the repository already fills, and say which ones you skipped. Ask every time — never infer the answer from the documents or the code.
2. **Run the script** with the layers the user picked:

   ```
   ${CLAUDE_PLUGIN_ROOT}/scripts/stack-install.py --root <work root> --with <layer>,<layer>
   ```

   Pass no `--with` when the user picked none. Exit 2 means nothing was proposed: show the script's `error` and stop.
3. **Show the proposal.** The layer table from the report, built from the script's `layers`, then the exact `commands` and `after` lines in one code block. Say each `conflict` and each layer left as the project's own, and that nothing is added for them. A `note` the script gave goes beside its layer.
4. **Ask once** whether to run the commands. On no, stop: the user has the commands.
5. **On yes, run each command** in the work root (`cd <work root> && …`), in order, then each `after` line. Stop at the first command that fails, show its output, and name the commands that did not run.
6. **Report what was installed** and what is left: the wiring the packages still need — `MantineProvider` and the cascade layer order, the PostCSS config, a `drizzle.config.ts`, the Better Auth handler and its secret, `MotionConfig reducedMotion="user"` at the root, the `test`, `lint`, `typecheck`, and `e2e` scripts in `package.json` (`web-stack` Rules 3–6). This command writes no configuration or code; name `/code` for that.

The script never installs a second library into a layer the project already fills, and never installs a framework. A repository with no `package.json` needs a scaffold first, such as the TanStack Start starter.
