---
name: easy-meal-setup
description: "Build the Recipe Library page — an optional published page that shows the easy-meal recipe library in a browser, suggests a dinner, and prints the grocery list, for people who want a bookmark instead of a chat. Use when: asked for a recipe app, a recipe page, or a shared recipe library to open without Claude. Not a store for easy-meal — that skill keeps its library in recipes.json."
---

# Easy-meal-setup skill

Build an optional extra for the `easy-meal` skill: one published page, a Recipe Library, that
shows the recipes in a browser, asks Claude for a new one, and prints the grocery list. Somebody
who wants a bookmark instead of a conversation opens that page and cooks from it.

**The page is not the library.** `easy-meal` keeps its library in a `recipes.json` file — under
`$HOME/.easy-meal/` on the user's own machine, and in the Claude app file storage on a phone. The
Claude mobile app cannot open an artifact at all, so nothing that matters may live only here. The
page is loaded from a copy of that file, and it hands the file back with its export button.

**Run this once.** After that, changes redeploy to the same URL.

## Before you build anything

1. **Check that the user wants a page.** `easy-meal` works without one. Build it only when they
   asked for a page, an app, or a bookmark.
2. **Look for a library page that is already there.** Run `Artifact` with `action: "list"` and
   look for a page named *Recipe Library*. Ask the user for the URL when the listing is unclear.
3. **A page exists** → do not build a second one. Report the URL, redeploy it if it needs a
   change, and stop.
4. **No page exists** → say in one line what you are about to publish, then build it.

Never seed the page with invented recipes. Load it from the user's own `recipes.json` when there
is one, and leave it empty when there is not — the empty state on the page says what to do about
it.

## Capabilities to declare

```
capabilities: { db: {}, sample: {}, downloads: true }
```

- **`db`** holds the page's copy of the recipes. It survives reloads, republishes, and
  sessions, and it is erased only when the artifact is deleted.
- **`sample`** lets the page ask Claude for a recipe. The viewer's own Claude account pays, and
  the first call in a view asks them to allow it.
- **`downloads`** backs the export button, so the library can always be taken out as a file.

Load the **`artifact-capabilities`** skill before you write the page, and read the type
definitions it points at for `db`, `sample`, and `downloads`. They are authoritative over
anything you remember about the API. Load the **`artifact-design`** skill as well — the page is
an artifact, and the design pass is not optional.

## The store

The page keeps its own copy of the recipes in the artifact database. One collection, one document
per recipe:

```
recipes/<id>          one recipe, the id is the kebab-case slug of its name
meta/settings         servings default, allergies, dislikes, and anything else to remember
```

A recipe document holds exactly the fields the `easy-meal` skill defines for `recipes.json` —
`name`, `servings`, `minutes`, `tags`, `ingredients` (`item`, `quantity`, `unit`, `aisle`,
`staple`), `steps`, `notes`, `createdAt`, `lastCooked`, `timesCooked`, `rating`. Keeping the
shapes identical is what lets the library move between the file and this page without a
conversion step.

Store rules that matter here:

- A document body is a JSON object, at most 256 KiB. One recipe is far below that.
- The database holds at most 5,000 documents. A recipe library never approaches it.
- Writes are last-writer-wins, and there are no transactions. Fine for one household.
- Never put anything secret in it. Everyone who can open the page can read the shared documents.

## A page that already works

`assets/recipe-library.html` in this skill folder is a working Recipe Library, published once and
kept here. **Start from it.** Read it, change what this household needs, and publish that —
writing a second one from nothing wastes the session and loses the details below that took a
build to find.

Publish it with `Artifact`, passing the capabilities above, the title *Recipe Library*, and a
favicon. Keep the file path stable so later changes redeploy to the same URL.

## What the page must do

- **List the library** — name, minutes, servings, rating, and when it was last cooked. Sort by
  least recently cooked, so what to make next is the first thing on screen.
- **Suggest a dinner.** A button that reads the library, then calls `sample.json` with the
  `easy-meal` rules, the names already in the library, and the viewer's settings. It shows the
  recipe, and saves it to `recipes/<id>` only when the viewer keeps it. *Suggest another* calls
  again with `cache: false`, so the second press really asks again.
- **Show the grocery list** for one recipe or for several selected ones — grouped by aisle,
  scaled to the servings, staples listed apart, each line a checkbox.
- **Record what happened.** *I cooked it* sets `lastCooked` to today and adds one to
  `timesCooked`. A rating and a note are one click and one field.
- **Export.** A button that calls `downloads.save` with the whole library as `recipes.json`, in
  the shape `easy-meal` reads. This is how the page gives its recipes back to the library, so it
  belongs where the viewer can find it, not at the bottom of a menu.
- **Import.** A control that takes a `recipes.json` and writes each recipe into the store, so a
  library that grew in the chat reaches the page. Replace a recipe of the same `id`, and leave
  the rest alone.
- **Add by hand.** A form to type in a recipe the household already cooks. The library is worth
  more when it holds the meals they already like.

## What the page must handle

- **Every capability can be absent.** `claude.use(name)` resolves `null` when the view cannot
  run it. The list still renders without `sample`; hide the suggest button. Without `db` the
  page says it cannot reach the library, rather than looking empty. Without `downloads`, hide
  the export button.
- **`sample` takes time and can fail.** Show a thinking state from the click until the first
  text arrives, offer a stop button, and branch on the error `code` — hide the feature on
  `not_granted`, back off on `rate_limited`, never retry in a loop.
- **The empty library** is the first thing most viewers see. Say what the page is for and put
  the suggest button in the middle of it.
- **The states** — empty, loading, a saved library, a failed call — are all designed, not left
  to chance.

## Finish

1. Publish the page with a stable title, *Recipe Library*, and keep the file path so later
   changes redeploy to the same URL.
2. Load the user's `recipes.json` into the store when they have one, so the page opens on their
   real library rather than an empty list.
3. Give the user the URL and tell them to bookmark it. Tell them plainly that the page opens on
   the web and on the desktop, and **not** in the Claude mobile app.
4. Tell them how the two stay in step: the export button gives back `recipes.json`, and that
   file is what `easy-meal` reads. A recipe saved on the page reaches the skill only after an
   export.
5. Say what the page costs to use: the suggest button spends the viewer's own Claude usage, and
   the first press asks them to allow it.

## Rules

- **One page, ever.** Check before you build, and redeploy rather than republish anew.
- **The file is the library, the page is a view of it.** Never tell the user the page is where
  their recipes live.
- **Never invent the user's data.** No seeded recipes, no sample rows left in the store.
- **The file shape and the store shape stay identical.** A recipe exported from the page must
  drop straight into `recipes.json`, and a recipe from the file must load straight into the page.
- **The page must work when Claude cannot be reached.** Reading and cooking from the library
  never depends on `sample`.
- **Do not build features nobody asked for.** A library, a suggestion, a grocery list, an
  export. Meal calendars, nutrition, and sharing are separate decisions.
