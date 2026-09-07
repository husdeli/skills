---
name: easy-meal-setup
description: "Build the Recipe Library once — a published page that stores recipes, asks Claude for a new one, and shows the grocery list, so easy-meal works where there is no filesystem to keep a file on. Use when: setting up easy-meal, asked for a recipe app or a shared recipe library, or when easy-meal finds no library and no way to write one."
---

# Easy-meal-setup skill

Build the store that the `easy-meal` skill uses when there is no filesystem to write to — a chat
session, a phone, someone else's computer.

The store is one published page: a Recipe Library. It holds the recipes in the artifact's
database, asks Claude for a new recipe from inside the browser, and shows the grocery list. Once
it exists, it works on its own. Nobody needs Claude Code, or a conversation, to use it.

**Run this once.** After that, `easy-meal` reads and writes the library that already exists.

## Before you build anything

1. **Look for a library that is already there.** Run `Artifact` with `action: "list"` and look
   for a page named *Recipe Library*. Ask the user for the URL when the listing is unclear.
2. **A library exists** → do not build a second one. Report the URL, and stop. Two libraries
   means two halves of a collection that never meet.
3. **No library exists** → say in one line what you are about to publish, then build it.

Never seed the store with invented recipes. An empty library is correct on day one, and the
empty state on the page says what to do about it.

## Capabilities to declare

```
capabilities: { db: {}, sample: {}, downloads: true }
```

- **`db`** holds the recipes. It survives reloads, republishes, and sessions, and it is erased
  only when the artifact is deleted.
- **`sample`** lets the page ask Claude for a recipe. The viewer's own Claude account pays, and
  the first call in a view asks them to allow it.
- **`downloads`** backs the export button, so the library can always be taken out as a file.

Load the **`artifact-capabilities`** skill before you write the page, and read the type
definitions it points at for `db`, `sample`, and `downloads`. They are authoritative over
anything you remember about the API. Load the **`artifact-design`** skill as well — the page is
an artifact, and the design pass is not optional.

## The store

One collection, one document per recipe:

```
recipes/<id>          one recipe, the id is the kebab-case slug of its name
meta/settings         servings default, allergies, dislikes, and anything else to remember
```

A recipe document holds exactly the fields the `easy-meal` skill defines for its JSON file —
`name`, `servings`, `minutes`, `tags`, `ingredients` (`item`, `quantity`, `unit`, `aisle`,
`staple`), `steps`, `notes`, `createdAt`, `lastCooked`, `timesCooked`, `rating`. Keeping the two
backends identical is what lets a library move between a file and this store without a
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
  the same shape the file backend uses. The library is never trapped in the page.
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
2. Give the user the URL and tell them to bookmark it. That URL is the library.
3. Save the URL to `$HOME/.easy-meal/library.json` as `{"artifactUrl": "..."}` when a filesystem
   is available, so a later Claude Code session finds the library without asking.
4. Say plainly what the page costs to use: the suggest button spends the viewer's own Claude
   usage, and the first press asks them to allow it.

## Rules

- **One library, ever.** Check before you build, and redeploy rather than republish anew.
- **Never invent the user's data.** No seeded recipes, no sample rows left in the store.
- **The file shape and the store shape stay identical.** A recipe exported from the page must
  drop straight into `recipes.json`, and the reverse.
- **The page must work when Claude cannot be reached.** Reading and cooking from the library
  never depends on `sample`.
- **Do not build features nobody asked for.** A library, a suggestion, a grocery list, an
  export. Meal calendars, nutrition, and sharing are separate decisions.
