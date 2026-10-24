#!/usr/bin/env python3
#
# stack-install.py — propose the installs that bring a web repository up to the `web-stack` skill.
#
# The core layers are proposed for every repository. An optional layer — auth, database, forms,
# e2e — is proposed only when `--with` names it, because only the person knows whether the product
# needs it. A layer the repository already fills with another library is left alone: the project's
# choice wins. Nothing is installed here; the `/stack install` command shows the commands this
# script prints, asks once, and runs them.
#
#   ./stack-install.py --root <work root>
#   ./stack-install.py --root <work root> --with auth,forms
#
# Auth runs on the Drizzle adapter, so `--with auth` brings the database layer with it unless the
# repository already has a data layer of its own.
#
# It prints one JSON object:
#
#   {"packageManager": "bun", "layers": [{"layer", "status", "add", "addDev", "found", "note"}],
#    "commands": ["bun add …", "bun add -d …"], "after": ["bunx playwright install"]}
#
# `status` is `present`, `incomplete`, `missing`, `project's own`, `conflict`, or `skipped`
# (an optional layer nobody asked for). Exit 2 means nothing was proposed: the root holds no
# `package.json`, the file is not valid JSON, or `--with` named an unknown layer.

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

VERSION = "1.0.0"

# Each layer: the default's runtime and dev packages, the libraries that mean the project already
# chose otherwise, and the commands that finish the setup once the packages are in.
LAYERS = {
    "framework": {
        "deps": ["@tanstack/react-start", "@tanstack/react-router", "react", "react-dom"],
        "dev": [],
        "alternatives": ["next", "@remix-run/react", "react-router", "astro", "@sveltejs/kit", "nuxt", "vue"],
        "report_only": True,
    },
    "server state": {
        "deps": ["@tanstack/react-query"],
        "dev": [],
        "alternatives": ["swr", "@apollo/client", "urql", "@reduxjs/toolkit"],
    },
    "validation": {
        "deps": ["zod"],
        "dev": [],
        "alternatives": ["valibot", "yup", "@sinclair/typebox", "arktype", "joi"],
    },
    "ui components": {
        "deps": ["@mantine/core", "@mantine/hooks"],
        "dev": ["postcss", "postcss-preset-mantine", "postcss-simple-vars"],
        "alternatives": ["@mui/material", "@chakra-ui/react", "antd", "@radix-ui/themes", "@headlessui/react", "react-aria-components"],
    },
    "styling": {
        "deps": [],
        "dev": ["tailwindcss", "@tailwindcss/vite"],
        "alternatives": ["styled-components", "@emotion/react", "@vanilla-extract/css", "@pandacss/dev", "unocss"],
    },
    "tests": {
        "deps": [],
        "dev": ["vitest"],
        "alternatives": ["jest", "mocha", "ava"],
    },
    "lint and format": {
        "deps": [],
        "dev": ["@biomejs/biome"],
        "alternatives": ["eslint", "prettier", "oxlint"],
        "after": ["{x} biome init"],
    },
    "database": {
        "deps": ["drizzle-orm", "postgres"],
        "dev": ["drizzle-kit"],
        "alternatives": ["prisma", "@prisma/client", "kysely", "typeorm", "sequelize", "mongoose", "@mikro-orm/core"],
        "optional": True,
    },
    "auth": {
        "deps": ["better-auth"],
        "dev": [],
        "alternatives": ["@clerk/tanstack-react-start", "@clerk/clerk-react", "lucia", "@auth/core", "next-auth", "@supabase/auth-js", "@workos-inc/authkit-react"],
        "optional": True,
        "needs": "database",
    },
    "forms": {
        "deps": ["@tanstack/react-form"],
        "dev": [],
        "alternatives": ["react-hook-form", "formik", "react-final-form", "@conform-to/react"],
        "optional": True,
    },
    "e2e": {
        "deps": [],
        "dev": ["@playwright/test"],
        "alternatives": ["cypress", "@wdio/cli", "nightwatch"],
        "optional": True,
        "after": ["{x} playwright install"],
    },
}

OPTIONAL = [name for name, layer in LAYERS.items() if layer.get("optional")]

# The project's package manager wins too; Bun is the default only when no lockfile names another.
MANAGERS = [
    ("bun", ("bun.lock", "bun.lockb"), "bun add", "bun add -d", "bunx"),
    ("pnpm", ("pnpm-lock.yaml",), "pnpm add", "pnpm add -D", "pnpm exec"),
    ("yarn", ("yarn.lock",), "yarn add", "yarn add -D", "yarn"),
    ("npm", ("package-lock.json",), "npm install", "npm install -D", "npx"),
]


def fail(message: str) -> None:
    print(json.dumps({"error": message}))
    sys.exit(2)


def package_manager(root: Path) -> tuple[str, str, str, str]:
    for name, lockfiles, add, add_dev, runner in MANAGERS:
        if any((root / lockfile).exists() for lockfile in lockfiles):
            return name, add, add_dev, runner
    name, _, add, add_dev, runner = MANAGERS[0]
    return name, add, add_dev, runner


def assess(name: str, layer: dict, installed: set[str], wanted: bool) -> dict:
    defaults = layer["deps"] + layer["dev"]
    has_default = [pkg for pkg in defaults if pkg in installed]
    has_other = [pkg for pkg in layer["alternatives"] if pkg in installed]
    result = {"layer": name, "status": "", "add": [], "addDev": [], "found": has_default + has_other, "note": ""}

    if has_other and has_default:
        result["status"] = "conflict"
        result["note"] = "Two libraries fill this layer; nothing is added until one is removed."
    elif has_other:
        result["status"] = "project's own"
    elif not wanted:
        result["status"] = "skipped"
    elif len(has_default) == len(defaults):
        result["status"] = "present"
    elif layer.get("report_only"):
        result["status"] = "missing"
        result["note"] = "A framework is scaffolded, not installed into a repository; nothing is added."
    else:
        result["status"] = "incomplete" if has_default else "missing"
        result["add"] = [pkg for pkg in layer["deps"] if pkg not in installed]
        result["addDev"] = [pkg for pkg in layer["dev"] if pkg not in installed]
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Propose the installs that bring a web repository up to the web-stack skill.")
    parser.add_argument("--root", required=True, help="the work root holding package.json")
    parser.add_argument("--with", dest="optional", default="", help=f"comma-separated optional layers: {', '.join(OPTIONAL)}")
    parser.add_argument("--version", action="version", version=VERSION)
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    manifest_path = root / "package.json"
    if not manifest_path.is_file():
        fail(f"{root} holds no package.json, so it is not a web project yet.")
    try:
        manifest = json.loads(manifest_path.read_text())
    except json.JSONDecodeError as error:
        fail(f"{manifest_path} is not valid JSON: {error}")

    requested = {item.strip() for item in args.optional.split(",") if item.strip()}
    unknown = requested - set(OPTIONAL)
    if unknown:
        fail(f"Unknown optional layer: {', '.join(sorted(unknown))}. Known: {', '.join(OPTIONAL)}.")

    installed = set(manifest.get("dependencies", {})) | set(manifest.get("devDependencies", {}))
    manager, add, add_dev, runner = package_manager(root)

    pulled_in = {}
    for name in sorted(requested):
        needed = LAYERS[name].get("needs")
        if needed and needed not in requested:
            pulled_in[needed] = name

    layers = []
    for name, layer in LAYERS.items():
        wanted = not layer.get("optional") or name in requested or name in pulled_in
        result = assess(name, layer, installed, wanted)
        if name in pulled_in and result["status"] in ("missing", "incomplete"):
            result["note"] = f"Added because {pulled_in[name]} runs on it."
        layers.append(result)

    runtime = [pkg for result in layers for pkg in result["add"]]
    dev = [pkg for result in layers for pkg in result["addDev"]]
    commands = []
    if runtime:
        commands.append(f"{add} {' '.join(runtime)}")
    if dev:
        commands.append(f"{add_dev} {' '.join(dev)}")
    after = [
        step.format(x=runner)
        for result in layers
        if result["add"] or result["addDev"]
        for step in LAYERS[result["layer"]].get("after", [])
    ]

    print(json.dumps({"packageManager": manager, "layers": layers, "commands": commands, "after": after}, indent=2))


if __name__ == "__main__":
    main()
