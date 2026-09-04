---
description: Explain what is happening, in plain language a non-expert can follow — the last thing you did, a file, an error, a change, or a concept.
argument-hint: [what to explain — a file, symbol, error, change, or concept; empty means what you just did]
---

# Explain

Explain the target below in **plain language**. The reader wants to understand what is happening. They do not want a tour of the code.

Target: $ARGUMENTS

Load the **`clean-writing`** skill first (namespaced here as `sdlc:clean-writing`) and follow it for every sentence. This command adds the rules below on top of it.

## What to explain

If the target is empty, explain **what you just did in this session**: what you changed, why, what it means for the user, and what happens next. Do not re-explain work the user already read in this conversation unless they ask again.

Otherwise match the target to one of these:

| Target | Explain |
| --- | --- |
| A file, function, class, or module | What it is for, what goes in, what comes out, and who calls it |
| An error, a stack trace, or failing output | What the message means, what caused it, and what fixes it |
| A diff, a branch, a commit, or a pull request | What changed, why it changed, and what behaviour is different now |
| A system, a flow, or a feature | The path a request or a user takes through it, in the order it happens |
| A term, a pattern, or a library | What problem it solves, and how it shows up in this codebase |

If the target names an audience — "explain to a designer", "explain to my manager" — write for that audience. With no audience named, write for **a competent developer who has never seen this codebase**.

## Read before you explain

**Never explain from memory.** Open the files, run the command, or read the output first. An explanation built on a guess is worse than no explanation, because the reader cannot tell the difference.

- Read the actual code paths involved, not the names around them.
- When a claim rests on something you did not verify, say so in one line: "I did not read the migration, so I cannot say whether old rows are backfilled."
- Never invent a file, a symbol, a flag, or a number. Quote paths, identifiers, and error text exactly.

## How to write it

Use this shape. Drop any section that has nothing in it.

1. **The short answer.** One or two sentences. The reader must be able to stop here and still be right about the main point.
2. **How it works.** The steps in the order they happen, cause before effect. Use a numbered list when there is more than one step.
3. **What it means for you.** What the reader should now do, watch out for, or decide. Name the risk before the step that carries it.

Length follows the target. A one-function question gets a paragraph. A whole subsystem gets a page. Never pad a simple answer to look thorough.

## Plain language rules

These are what "plain" means here. They are stricter than everyday writing.

- **Define every term of art on first use, in the same sentence.** Write "the value is memoized — computed once and reused" rather than "the value is memoized". This applies to words the codebase uses freely: hydration, idempotent, race condition, debounce, migration, middleware.
- **Explain the behaviour, not the syntax.** Say what the code makes happen. Do not narrate lines.
- **Code is an anchor, not the explanation.** Point at `path/to/file.ts:42` so the reader can check you. Paste at most a few lines, and only when the words alone cannot carry it. The explanation must stand up if every code block is deleted.
- **Use concrete numbers and names.** "The job retries 3 times, then drops the row" beats "the job retries a few times".
- **Give the reader the actor.** "The router calls the loader" — never "the loader is called".
- **One comparison is allowed**, and only to introduce something the reader has no name for yet. Label it as a comparison: "this works like a queue at a counter — one item served at a time." This is the single place this plugin permits a figure of speech, and `clean-writing` Rule 9 otherwise stands: no idiom, no humour, no hedging.
- **Do not narrate your process.** What you searched, in what order, is not the explanation.
- **Do not sell the work.** No "cleanly handled", no "robust", no "simply". If the design has a weakness, name it in one sentence.

## After the explanation

End with one line offering the next step the reader is most likely to want — going deeper on one part, seeing the code, or changing it. Ask nothing else.
