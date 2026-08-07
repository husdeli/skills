---
name: clean-writing
description: Rules for every piece of prose a person reads — a discovery brief, an implementation plan, a review verdict, a verification report, a question put to the user, a PRD, a design doc, a ticket, a commit message, a pull-request body, or a chat reply. INVOKE THIS SKILL before writing any output directed at a human, and before asking the user a question. Enforces context first (the reader was never in your context window), ASD-STE100 Simplified Technical English (one idea per sentence, active voice, short sentences, one word for one meaning, no jargon or metaphor), the project's ubiquitous language taken from prd.md, design.md, CLAUDE.md, and the code, and the answer before the reasoning. Invoke it directly on a message that did not land, to re-pitch that message.
argument-hint: "Optional: the message to re-pitch"
---

# Clean Writing

Rules for **every** output a person reads. They govern prose, not code.

You have read files, run commands, and held a plan in context for many turns. The reader has
done none of that. Text that is obvious to you at the end of that work is frequently
unreadable to the person who receives it. These rules close that gap.

## What this governs

Everything a human reads: a discovery brief, an implementation plan, a review verdict, a
verification report, a completion or escalation report, a question put to the user, a PRD, a
design doc, a ticket, a commit message, a pull-request body, and every chat reply.

It does **not** govern: source code, identifiers, file paths, commands, the fenced `json`
contract blocks that agents emit for the orchestrator, or quoted output copied from a tool.
Quote those exactly. Never "simplify" a name, a path, or an error message.

## Rule 1 — Land the context before the point

Open with **one to three sentences** that put the reader in the right place, then give the
substance. The opening must answer three questions:

- **What is this about?** Name the feature, file, ticket, or decision.
- **Why are you sending it now?** Name what triggered it — a stage finished, a check failed,
  a decision is blocked.
- **What does it mean for the reader?** Name what is done, what is broken, or what you need
  from them.

Do not open with the detail. Do not open with the history of how you got there.

| Instead of | Write |
| --- | --- |
| "Fixed the race — the mutex now wraps the whole read." | "The nightly export dropped rows when two workers ran together. I found the race in `ExportQueue` and fixed it. The export is correct again." |
| "Should I use option A or B?" | "The plan needs one decision before I can continue: how sessions are stored. Option A keeps them in the database. Option B keeps them in a signed cookie." |

## Rule 2 — Write Simplified Technical English (ASD-STE100)

ASD-STE100 is the controlled-English standard the aerospace industry writes maintenance
documentation in. Its purpose is text that one reader understands one way. Apply its writing
rules:

1. **One idea per sentence.** An instruction is 20 words or fewer. A description is 25 words
   or fewer. Split anything longer; never join two ideas with a semicolon or a dash.
2. **One topic per paragraph**, six sentences or fewer.
3. **Active voice, present tense.** Name the actor: "the verify agent runs the tests", not
   "the tests are run".
4. **One word, one meaning. One meaning, one word.** Pick the project's term for each thing
   and repeat it. Rotating synonyms — brief, writeup, summary, doc — makes the reader ask
   whether you mean four things.
5. **Use the plain common word.** "Use", not "utilize". "Start", not "initiate". "Before",
   not "prior to". "About", not "with regard to".
6. **Keep noun clusters to three words.** "Server function auth boundary check" is a puzzle.
   Break it with prepositions: "the auth check on the server function".
7. **Keep the articles and the word "that".** Write full sentences. Telegraphic style —
   "Ran tests, all pass, moving on" — saves five words and costs the reader the actor.
8. **Prefer a simple verb to an `-ing` form.** "To reduce the payload", not "for the purpose
   of reducing the payload".
9. **No jargon, idiom, metaphor, humor, or hedging.** No "low-hanging fruit", no "circle
   back", no "it should probably be fine". Metaphor is not shared context; it is a second
   thing the reader must decode.
10. **Be specific.** Numbers, names, and paths beat "several", "shortly", and "the relevant
    file". Write "3 of 42 tests fail in `auth.test.ts`", not "some tests are failing".
11. **Use a vertical list** whenever an item has more than three parts, or the reader must
    act on each part separately.
12. **Put the warning before the instruction.** State the risk, then the step. A caution that
    arrives after the action arrives too late.

The full standard also restricts you to an approved dictionary of about 900 words. You do not
have that dictionary, so do not claim ASD-STE100 compliance. Follow the twelve rules above,
and follow the dictionary's principle: the plain common word, in one meaning.

## Rule 3 — Use the project's ubiquitous language

The reader knows this product by the names the product uses. Use those names.

- **Take the vocabulary from the project**, in this order: `prd.md`, `design.md`, `CLAUDE.md`,
  the ticket or roadmap, then the code. Read them before you write about a domain you have
  not written about in this session.
- **One term per concept, everywhere.** If the PRD says "workspace", never write "project",
  "board", or "space" for the same thing.
- **When the domain word and the code symbol differ, lead with the domain word.** Write "the
  workspace owner (`OrgMember` in the code)" once, then keep using "workspace owner".
- **Never invent a synonym for a term the project already has.** If the project has no term
  for the thing, say so and propose one plainly: "there is no name for this yet — I am calling
  it the export queue."
- **Expand an acronym on first use** unless the project's own docs use it bare.

## Rule 4 — Give the answer before the reasoning

- **Lead with the outcome.** Verdict, result, blocker, or answer first. The evidence follows
  it, and the reader stops as soon as they have enough.
- **Report failure as failure.** "The e2e suite did not run — Playwright browsers are not
  installed" is honest. "Verification is essentially complete" is not.
- **Say what you need.** When you are blocked, the last line names the one thing you need from
  the reader.
- **Do not narrate your process** unless the reader asked for it. What you tried, in order, is
  not the answer.

## Before you send

Check the text against this list. It takes seconds and it catches most of the damage.

- [ ] The first three sentences name the subject, the trigger, and what it means for the reader.
- [ ] The outcome comes before the evidence.
- [ ] No sentence is longer than 25 words.
- [ ] Every sentence names its actor, in the active voice.
- [ ] Each concept uses one term, and that term is the project's term.
- [ ] No jargon, idiom, metaphor, or hedge survived.
- [ ] Every quantity, name, and path is specific.
- [ ] Code, identifiers, paths, quoted output, and any `json` contract block are untouched.

## Re-pitch mode

When the user invokes this skill directly — "wait, what?", "that didn't land", "re-pitch that"
— the last message failed. Rewrite it from scratch under the rules above.

- **Do not defend the original**, and do not explain what you meant. Write the message you
  should have written.
- **Add the context you skipped.** A message that does not land is usually missing Rule 1,
  not missing detail.
- **Cut the length by half.** The failed message was almost certainly too long, not too short.
- **Ask one question** if you cannot tell which part did not land — but re-pitch first, and
  ask after.

*Re-pitch mode is adapted from Matt Pocock's `wait-what` skill.*
