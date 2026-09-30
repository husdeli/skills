---
name: clean-writing
description: Rules for every piece of prose a person reads — a plan, a report, a review verdict, a question put to the user, a PRD, a design doc, a ticket, a commit message, a pull-request body, or a chat reply. INVOKE THIS SKILL before writing any output directed at a human, and before asking the user a question. Enforces context first (the reader was never in your context window), ASD-STE100 Simplified Technical English (one idea per sentence, active voice, short sentences, one word for one meaning, no jargon or metaphor), the project's ubiquitous language through the `glossary` skill, prose that names a thing in words rather than by its file name, identifier, or section sign — the exact strings go beside the sentence, in a block or a list — the answer before the reasoning, and no sentence the reader does not need. Invoke it directly on a message that did not land, to re-pitch that message.
---

# Clean Writing

Rules for **every** output a person reads. They govern prose, not code. The reader was never in
your context window.

## What this governs

Everything a human reads: a plan, a report, a review verdict, a question to the user, a PRD, a
design doc, a ticket, a commit message, a pull-request body, and every chat reply.

It does **not** govern: source code, identifiers, file paths, commands, the fenced `json`
contract blocks that agents emit for the orchestrator, or quoted output copied from a tool.
Quote those exactly. Never "simplify" a name, a path, or an error message. Those strings belong
beside the prose, never inside it. Rule 4 says where each one goes.

## Rule 1 — Land the context before the point

Open with **one to three sentences** that put the reader in the right place, then give the
substance. The opening must answer three questions:

- **What is this about?** Name the feature, the document, the ticket, or the decision — in
  words, not by file name. Rule 4 holds that.
- **Why are you sending it now?** Name what triggered it — a stage finished, a check failed,
  a decision is blocked.
- **What does it mean for the reader?** Name what is done, what is broken, or what you need
  from them.

Do not open with the detail. Do not open with the history of how you got there.

| Instead of | Write |
| --- | --- |
| "Fixed the race — the mutex now wraps the whole read." | "The nightly export dropped rows when two workers ran together. I found the race in the export queue and fixed it. The export is correct again." |
| "Should I use option A or B?" | "The plan needs one decision before I can continue: how sessions are stored. Option A keeps them in the database. Option B keeps them in a signed cookie." |

## Rule 2 — Write Simplified Technical English (ASD-STE100)

Write so that one reader understands the text one way. Apply these rules:

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
   back", no "it should probably be fine". A metaphor is one more thing the reader must decode.
10. **Be specific.** Numbers and names beat "several", "shortly", and "the relevant part".
    Write "three of the 42 tests fail, all of them in the login tests", not "some tests are
    failing". The file each one fails in goes in the list below the sentence, not in it — Rule 4
    holds that.
11. **Use a vertical list** whenever an item has more than three parts, or the reader must
    act on each part separately.
12. **Put the warning before the instruction.** State the risk, then the step. A caution that
    arrives after the action arrives too late.

The full standard also restricts you to a dictionary of about 900 words. You do not have that
dictionary, so never claim ASD-STE100 compliance.

## Rule 3 — Use the project's ubiquitous language

The reader knows this product by the names the product uses. Use those names.

**The `glossary` skill holds every rule about a term.** Load it (namespaced `sdlc:glossary`)
before you write about a domain you have not written about in this session. Follow it for every
name you use here.

## Rule 4 — Name the thing, not the file it lives in

A file name is not the name of a thing. The roadmap is "the roadmap". The rule about where
documents live is "the rule about where documents live". The export queue is "the export queue".
The reader knows the product. The reader does not know your tree, and on a phone cannot open it.

**Three things never appear inside a sentence:**

- **The section sign and the pilcrow — `§` and `¶`.** Cite a section by its heading, in words: "the
  registration step of the setup command". A number into a document the reader does not have open
  points at nothing.
- **File names, folders, and extensions.** Write "the roadmap", "the login ticket", "the checkout
  design doc", "the setup command".
- **Identifiers and code.** Write "the export queue drops a row when two workers run together".
  Not the class name, not the function call, not a snippet of the change.

| Instead of | Write |
| --- | --- |
| "Updated `product-docs/SKILL.md` §2 to add `workRoot`." | "The rule about where documents live now covers the repository a task is built in." |
| "Fixed the race in `ExportQueue.flush()`." | "The nightly export dropped rows when two workers ran together. The export is correct again." |
| "See `AUTH-001-user-login.md`." | "See the ticket for user login." |
| "`verificationCommands` came back empty." | "The project names no test command, so nothing gated this change." |

**The exact string still has a place — beside the prose, never inside it.** A reader who must act
on a path needs it exactly. A reader who is told what happened needs the words. Keep the two
apart:

- A command the reader runs goes in its own fenced block, under a line that says what it does.
- The files a change touched go in a list, under a heading that says so.
- A defect's location goes in the issue list, one per line, next to the issue — not in the sentence
  that gives the verdict.
- A number stays in the prose. "Three of the 42 tests fail" is prose. Which file each one fails in
  is a list.

This rule governs prose only. **A document that cites another document still cites it the way the
`product-docs` and `ticket-board` skills say** — by file name, or as a wikilink in a vault — because
that citation is a link for a machine and a click, not a sentence. A fenced block, a table cell
holding a path, and an agent's `json` block are unchanged too.

## Rule 5 — Give the answer before the reasoning

- **Lead with the outcome.** Verdict, result, blocker, or answer first. The evidence follows
  it, and the reader stops as soon as they have enough.
- **Report failure as failure.** "The e2e suite did not run — Playwright browsers are not
  installed" is honest. "Verification is essentially complete" is not.
- **Say what you need.** When you are blocked, the last line names the one thing you need from
  the reader.
- **Do not narrate your process** unless the reader asked for it. What you tried, in order, is
  not the answer.

## Rule 6 — Cut what the reader does not need

A sentence earns its place by changing what the reader knows, decides, or does. Cut the rest.

- **Cut a detail that is true only sometimes.** "Reviews the code that was just written" is wrong
  when the target is a branch from last month. Write what holds in every case: "reviews the code
  under review".
- **Do not name the reader, and do not explain why you are writing.** The reader knows both. Drop
  "as you know", "for your reference", and "this report is for whoever fixes the code".
- **Say each point once.** A restatement in other words is a second thing to read and reconcile.
- **Stop at three examples.** Three teach the pattern. Eleven become a list the reader skips.
- **Cut the background the reader will not act on.** Where a rule came from, and what you read to
  apply it, are not the rule.

## Before you send

Check the text against this list.

- [ ] The first three sentences name the subject, the trigger, and what it means for the reader.
- [ ] The outcome comes before the evidence.
- [ ] No sentence is longer than 25 words.
- [ ] Every sentence names its actor, in the active voice.
- [ ] Each concept uses one term, and that term is the glossary's term.
- [ ] No jargon, idiom, metaphor, or hedge survived.
- [ ] Every quantity and name is specific.
- [ ] Every sentence changes what the reader knows or does.
- [ ] No claim is true in only some cases.
- [ ] No sentence holds a file name, an identifier, a snippet, a `§`, or a `¶`.
- [ ] Every exact string the reader needs is there, in a block, a list, or a table cell.
- [ ] Code, identifiers, paths, quoted output, and any `json` contract block are untouched.

## Re-pitch mode

When the user invokes this skill directly — "wait, what?", "that didn't land", "re-pitch that"
— the last message failed. Rewrite it from scratch under the rules above.

- **Do not defend the original**, and do not explain what you meant. Write the message you
  should have written.
- **Add the context you skipped.** A message that does not land is usually missing Rule 1,
  not missing detail.
- **Cut the length by half.** The failed message was almost certainly too long, not too short.
- **Ask one question** if you cannot tell which part did not land. Re-pitch first, then ask.

*Re-pitch mode is adapted from Matt Pocock's `wait-what` skill.*
