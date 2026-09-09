---
name: easy-meal
description: "Pick a simple recipe to cook and turn it into a grocery list, keeping every recipe in a persistent library so the same few meals do not come back every week. Use when: asked what to cook, for a dinner idea, for a meal plan for the week, for a shopping or groceries list, or to save, list, or rate a recipe. The library is one JSON file — under your home folder on your own machine, and in the Claude app file storage on the phone."
---

# Easy-meal skill

Answer "what should I cook?" with one recipe the person can actually make tonight, then give
them the list of what to buy for it.

Every recipe is written to a library that outlives the session. Read it **before** you suggest anything,
so the answer is new. A skill that proposes pasta with tomato sauce for the fourth week running
is worse than no skill.

## The library

The library is the only memory this skill has. **Read all of it before every answer.**

It is one JSON file, `recipes.json`, and it has the same shape everywhere. Only its location
changes.

### On a machine with a home folder

```
$HOME/.easy-meal/recipes.json
```

- Expand `~` yourself — use `$HOME`, and never write the literal `~` into a path.
- Create the folder and the file on first use, with `{"version": 1, "recipes": []}`.
- This is the library whenever the session has a filesystem that survives — Claude Code on the
  user's own machine.

### In the Claude app file storage

The Claude app — the phone included — has no home folder that survives the conversation, but it
does have file storage the user keeps between chats. The library is a file there, read and
written exactly like the one above.

- **Find the file, do not assume a path.** Look for `recipes.json` in the files the session can
  reach: the user's attached files, and the app's file storage folders — the uploads area under
  `/mnt/user-data` is the usual one. List the folder and read what is really there.
- **No file yet** → create `recipes.json` with `{"version": 1, "recipes": []}`.
- **Write the updated file back into the app's file storage** — the outputs area under
  `/mnt/user-data` — every time you change it, so the user keeps the new version rather than
  the copy they started the chat with. Say in one line that the updated `recipes.json` is
  there.
- **Nothing readable and nothing writable** → ask the user to attach their `recipes.json`, or
  to let you start a new one. Never hold the library in the conversation alone. A library that
  lives in the chat is gone by tomorrow.

Artifacts are not a backend for this skill. The Claude mobile app cannot open one, so the
library never lives in a published page. The `easy-meal-setup` skill still builds a Recipe
Library page for anyone who wants a standalone bookmark on the web or the desktop, but that
page is an extra view over an exported copy — this file is the library.

**Never keep two libraries.** When more than one `recipes.json` turns up, the user says which
one is theirs, and the other is left alone.

### Shape

```json
{
  "version": 1,
  "recipes": [
    {
      "id": "sheet-pan-lemon-chicken",
      "name": "Sheet-pan lemon chicken with potatoes",
      "servings": 2,
      "minutes": 35,
      "tags": ["chicken", "oven", "one-pan", "weeknight"],
      "ingredients": [
        { "item": "chicken thighs", "quantity": 500, "unit": "g", "aisle": "meat" },
        { "item": "potatoes", "quantity": 600, "unit": "g", "aisle": "produce" },
        { "item": "olive oil", "quantity": 2, "unit": "tbsp", "aisle": "pantry", "staple": true }
      ],
      "steps": ["Heat the oven to 220 C.", "Toss everything on a tray.", "Roast 30 minutes."],
      "notes": "",
      "createdAt": "2026-09-07",
      "lastCooked": null,
      "timesCooked": 0,
      "rating": null
    }
  ]
}
```

Field rules:

- `id` — kebab-case, taken from the name, unique in the file.
- `quantity` — a number. `unit` — one of `g`, `kg`, `ml`, `l`, `tbsp`, `tsp`, `piece`, `clove`,
  `bunch`, `can`, `pinch`. Use `piece` for countable things, never an empty unit.
- `aisle` — one of `produce`, `meat`, `fish`, `dairy`, `bakery`, `frozen`, `pantry`, `spices`,
  `drinks`, `other`. It exists so the grocery list can be sorted by where things sit in a shop.
- `staple` — `true` for something most kitchens already hold (oil, salt, pepper, common dried
  spices, flour, sugar). Staples are listed apart in the grocery list, so nobody buys a fifth
  bottle of olive oil.
- `rating` — `null`, or 1 to 5, set only by the person who cooked it.
- Dates are `YYYY-MM-DD`.

### Writing to it safely

The library is the person's own data, and losing it means losing every recipe they liked.

Write it carefully, wherever it lives:

1. Read the current file and parse it.
2. Change the parsed object in memory — append a recipe, or update fields on one.
3. Write the whole object back to a temporary file in the same folder, then move it over
   `recipes.json`. Never leave a half-written file behind.
4. When the file is missing or unreadable, say so, and start a fresh one only after the person
   agrees. Never silently replace a file you failed to parse.

Do this with a short script, not by hand-editing JSON in a text tool.

## Process

### 1. Read the library and the request

Load `recipes.json`. Note what is already there: the names, the tags, the `lastCooked` dates,
and the ratings.

Then take the constraints from the request. Ask **at most one** question, and only when the
answer changes the recipe — usually how many people eat, or what has to be avoided. Everything
else you assume and state in one line: two servings, no allergies, an ordinary home kitchen,
about 30 minutes.

### 2. Choose what to serve

**Suggest something new by default.** Search the library only to avoid repeating it.

Repeat an existing recipe when, and only when, the person asks for one — "the chicken thing we
did", "something from the list", "cook something we liked". Then prefer a recipe with a rating
of 4 or 5 and the oldest `lastCooked` date, and never one cooked in the last 14 days unless
nothing else fits.

A new suggestion must not repeat a recipe already in the library, and should not repeat its main
protein or its main starch when the library shows the same one twice in the last two weeks.

### 3. Keep it simple

"Simple" is the point of this skill, so the recipe holds to all of these:

- **10 ingredients or fewer**, staples included.
- **40 minutes or less**, start to plate.
- **Ingredients from an ordinary supermarket.** No specialist shop, no single-use bottle of
  something that will sit in the cupboard for two years.
- **One or two pans.** No equipment beyond an oven, a hob, a knife, and a board.
- **Steps a beginner can follow.** Six steps or fewer, one action each, with a temperature and a
  time whenever heat is involved.

State a real quantity for every ingredient. "Some cheese" cannot be shopped for.

### 4. Show the recipe, then save it

Present it before you write anything:

```markdown
## [Name]

[One sentence: what it tastes like, and why it fits what was asked.]

**[N] servings · [N] minutes · [tags]**

### Ingredients
- [quantity] [unit] [item]

### Steps
1. [One action.]

*Assumed: [the assumptions you made].*
```

Then save it to the library. Adding a recipe needs no permission — that is what the library is
for. Say in one line that you saved it.

### 5. Give the grocery list

Always give the list with the recipe, unless the person asked only for an idea.

```markdown
### Groceries — [recipe name, or "N meals"]

**Produce**
- [ ] 600 g potatoes
- [ ] 1 lemon

**Meat**
- [ ] 500 g chicken thighs

*Already in most kitchens: olive oil, salt, pepper.*
```

- **Group by aisle**, in this order: produce, meat, fish, dairy, bakery, frozen, pantry, spices,
  drinks, other. Skip an empty group.
- **Scale to the servings asked for**, and round to what a shop actually sells — 500 g of mince,
  one lemon, one bunch of parsley. Never write "0.66 of an onion".
- **Merge across recipes** when the list covers several meals: same item and same unit add up;
  different units stay as separate lines rather than being converted wrongly.
- **Keep staples out of the main list** and name them in the italic line under it.

## Other things people ask

- **"What can I cook?" with no other constraint** → suggest one new recipe, and name two saved
  ones they have not cooked lately as alternatives.
- **"Plan the week"** → propose 3 to 5 recipes that share ingredients, vary the protein, and
  land on one merged grocery list. Save each recipe, and show the list once at the end.
- **"I cooked it"** → set `lastCooked` to today and add one to `timesCooked`. Ask for a rating
  only if they did not give one.
- **"That was good / bad"** → write the `rating`, and put the reason in `notes`.
- **"What's in the library?"** → list the names with servings, minutes, rating, and last cooked,
  newest suggestion first. Do not print the JSON.

## Rules

- **Read the library before every suggestion.** Repeating a recipe by accident is the one
  failure this skill exists to prevent.
- **Never lose the library.** Read it, change it in memory, write it through a temporary file,
  and move that over the real one. In the Claude app, put the new copy in the app's file storage
  and tell the user it is there.
- **One recipe per answer**, unless the person asked for a plan.
- **Real quantities, real units.** Every ingredient can be bought as written.
- **Simple beats impressive.** If it needs a specialist ingredient or a third pan, pick
  something else.
- **Never invent a health claim.** No calorie counts, no macros, no nutrition advice unless the
  person gives you the numbers to work from.
- **Take allergies seriously.** When somebody names an allergy, check every ingredient against
  it, and say plainly that they should still read the labels themselves.
- **Ask at most one question.** Assume the rest and state your assumptions.
