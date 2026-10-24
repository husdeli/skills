---
description: Show a web project's stack layer by layer — the library the project uses, the default it would get, and every layer where the two differ.
argument-hint: "[a repository code from sdlc.json, a path, or nothing for the current repository]"
---

# Stack

Report the stack of one web repository against the default in the **`web-stack`** skill.

Target: $ARGUMENTS

Load the **`web-stack`** skill (namespaced `sdlc:web-stack`) and the **`technical-writing`** skill (namespaced `sdlc:technical-writing`) first. This command writes no file and installs nothing.

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
