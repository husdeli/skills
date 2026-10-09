---
name: technical-writing
description: Write technical prose a reader works from — with the context first, the answer before the reasoning, and no sentence the reader does not need. Use whenever the user asks for a document, spec, PRD, design doc, ticket, report, review verdict, commit message, pull-request body, runbook, or release notes, or asks to review one, even if they don't say "document".
---

# Technical Writing

## Purpose and reader

The reader arrived with a job. They will leave as soon as they can do it, and they will not read the part above the part they landed on.

- **The reader was never in your context window.** Everything obvious to you is absent to them.
- **They arrived from a search or a link**, in the middle, not at the top.
- **They are scanning for the one thing they need**, and they will act on the first thing that looks like it.
- **They are not reading for pleasure.** A sentence that does not change what they know, decide, or do is a sentence that costs them.

## Output structure

Every piece follows this shape, long or short.

1. **Context** — one to three sentences naming the subject, what triggered this, and what it means for the reader.
2. **Answer** — the outcome, verdict, result, or blocker. Before the evidence, always.
3. **Body** — the evidence, the mechanism, or the steps, so the reader can stop as soon as they have enough.
4. **Ask** — the one thing you need from the reader, when you need something.

## Rules

### Stance and voice

- **Name the actor in every sentence**, because "the tests are run" leaves the reader guessing who runs them and whether it has happened.
- **Write in the active voice and the present tense**, because it is shorter and it cannot hide the actor.
- **Never state what you did not verify**, because a plausible claim and a checked one look identical to the reader, and only one of them holds.
- **Keep the sales language out** — no "robust", "seamless", "simply", "just", "powerful" — because a technical document describes and does not persuade.
- **Name a weakness in one sentence** when the design has one, because the reader will find it later and trust nothing else you wrote.

### Reader engagement

- **Say what a thing is for before how it works**, because a reader who does not know why it exists cannot judge whether the mechanism is right.
- **Define every term of art at its first use, in the same sentence**, because a term defined in an appendix is a term the reader never sees defined.
- **Write a procedure as numbered steps, one action each**, because a reader following along has one hand on the keyboard.
- **Put the precondition and the warning before the step**, because a caution that arrives after the action arrives too late.
- **Specify the edges** — empty input, failure, the limit, a repeat — because an edge you did not decide is one the reader decides for you, differently.

### Hedging and boosting

- **Mark an assumption as an assumption, in its own sentence**, because an unmarked one is read as a fact and built on.
- **Name what you did not check**, because the reader cannot see the gap and will assume there isn't one.
- **Report a failure as a failure**, because "verification is essentially complete" tells nobody what ran.
- **Be specific with every quantity and name**, because "several", "shortly", and "the relevant part" push the work of guessing onto the reader.
- **Name versions, flags, and defaults exactly**, because "a recent Node" is a support ticket.

### Signposting

- **Name the thing in words, not by its file name, identifier, or `§`**, because the reader does not know your tree and on a phone cannot open it. The exact string goes beside the sentence — in a fenced block, a list, or a table cell — never inside it.
- **Use the project's own term for each concept, every time**, because a rotating synonym makes the reader ask whether you mean two things. The **`glossary`** skill (namespaced `sdlc:glossary`) holds every rule about a term.
- **Give one fact one home and link to it**, because two copies of a rule become two rules.
- **Never write "as described above"**, because the reader landed here from a search. Name the section in words.
- **Pick the shape the reader's job needs** — numbered list to do something in order, table to compare, bullets to act on each item, prose to understand why, a fenced block to copy a string exactly — because the wrong shape makes the reader convert it themselves.

## Avoid

- **Opening with the detail or the history.** The reader needs to know where they are first.
- **Narrating your process.** What you tried, in what order, is not the answer.
- **A sentence past 25 words**, or two ideas joined by a semicolon or a dash. Split it.
- **A noun cluster of four or more words.** "Server function auth boundary check" is a puzzle; break it with prepositions.
- **Telegraphic style.** "Ran tests, all pass, moving on" saves five words and costs the actor.
- **Jargon, idiom, metaphor, humour, and hedging.** Each is one more thing to decode.
- **A claim that holds in only some cases**, written as though it always holds.
- **Naming the reader, or explaining why you are writing.** They know both.
- **The fourth example of the same pattern.** Three teach it; eleven become a list nobody reads.
- **Simplifying a name, a path, a command, or an error message.** Quote those exactly, always.

## Examples

**Weak:** "Fixed the race — the mutex now wraps the whole read."
**Strong:** "The nightly export dropped rows when two workers ran together. I found the race in the export queue and fixed it. The export is correct again."
**Why:** context before the point, the outcome stated plainly, and the defect named in words rather than by its mechanism.

**Weak:** "Updated `sdlc-structure/SKILL.md` §2 to add `workRoot`."
**Strong:** "The rule about where documents live now covers the repository a task is built in."
**Why:** the reader cannot open a path or resolve a section number, and the sentence survives without either.

**Weak:** "Should I use option A or B?"
**Strong:** "The plan needs one decision before I can continue: how sessions are stored. Option A keeps them in the database. Option B keeps them in a signed cookie."
**Why:** it names the decision, the stake, and both options, so the reader can answer in one line.

**Weak:** "The queue holds a row per export, keyed by tenant, with a 30-second visibility timeout."
**Strong:** "The queue stops two workers from exporting the same rows. It holds one row per export, keyed by tenant, with a 30-second visibility timeout."
**Why:** purpose before mechanism, so the reader can judge whether the mechanism is right.

## Final check

Run this against the draft before you return it.

- Do the first three sentences name the subject, the trigger, and what it means for the reader?
- Does the outcome come before the evidence?
- Is every sentence 25 words or fewer, active, with a named actor?
- Does each concept use one term, the glossary's term, every time?
- Is every quantity, name, version, flag, and default specific?
- Is every claim one you verified, and every assumption marked as one?
- Does every behaviour say what happens on empty, on failure, and on a repeat?
- Does any sentence hold a file name, an identifier, a snippet, a `§`, or a `¶`?
- Is every exact string the reader needs present, in a block, a list, or a table cell?
- Does every sentence change what the reader knows, decides, or does?
- Are code, identifiers, paths, quoted output, and any `json` contract block untouched?

## Rule codes

A review names codes rather than impressions, so one finding means the same thing twice. **[The rule codes](./references/rule-codes.md)** give every rule above a stable name, its default severity, and whether a script or a reader decides it. Read it before you review a text, and whenever you report a finding anyone has to act on later. `/review-text` uses it.
