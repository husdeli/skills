---
description: Review a text written for people against the technical-writing rules — returns a report a person can act on and a findings block a tool can consume.
argument-hint: "[what to review — a path, the text itself, or nothing for the last text in this conversation] [fix]"
---

# Review Text

Review the target text against the **`technical-writing`** rules. Report what a reader loses, and return the findings in a shape a linter can read later.

Target: $ARGUMENTS

## Load the rules before you read the text

**Name the register first, from the text itself rather than from what the user called it.** Then load that skill and read its rule codes in full.

| Register | The text is | Load |
| --- | --- | --- |
| Technical | Something the reader works from — a document, a spec, a PRD, a design doc, a ticket, a report, a review verdict, a commit message, a pull-request body, a runbook, release notes | **`technical-writing`** (namespaced `sdlc:technical-writing`) |
| Social | A social media post, a thread, a caption, or an announcement written for a feed | **`social-writing`** (namespaced `sdlc:social-writing`) |
| Both | A text that is published to a feed and also worked from, such as release notes posted as a thread | Both skills. When two rules disagree, the stricter one wins. |

**The rule codes are required.** Every finding in this command's output names a code from the loaded skill's registry, and a code you guessed is a finding nobody can act on.

**Say which register you applied** in the first line of the report. A review that applied the wrong register reviewed the wrong text, and the reader cannot tell unless you say. When you cannot tell which register a text is in, say so and ask — the two sets disagree on the opening, so guessing wrong inverts half the findings.

Load the **`glossary`** skill (namespaced `sdlc:glossary`) when the register is technical and the text names domain concepts, so that `TG3` findings rest on the product's own terms rather than on your taste.

## Resolve the target

| The target is | Review |
| --- | --- |
| A path to a file | The file's prose. Read the file first. |
| A path to a folder | Every text file in it, one report per file, worst first. |
| Text pasted into the argument | The text as given. |
| Empty | The last text in this conversation that a person reads — the document you just wrote, or the text the user pasted. Name what you picked in the first line. |
| A target that names an audience — "review for a customer" | The same rules, judged for that reader. |

If the target is empty and the conversation holds no such text, ask which text to review. Ask nothing else.

**`fix` as the last word** means apply the findings after you report them. The section at the end says how.

## What you review, and what you skip

**You review prose only.** Inside a document, skip these and never report a finding against them:

- A fenced code block, and the content of any `json` contract block.
- Frontmatter, a table cell that holds a path, and a link target.
- An identifier, a file path, a command, and output quoted from a tool.
- A heading's anchor or its slug. The heading's words are prose and are reviewed.

`TG1` is the one rule that reaches these, and it fires on the sentence that swallowed the string, never on the string. Quote the string exactly when you report it.

## How to judge

Work the text against the final check in each skill you loaded, one line at a time. Then rank what you found.

- **Severity starts at the default in the rule codes.** Raise it when this reader pays more, lower it for a draft note. Say in the finding when you moved it, and why.
- **Judge the text for its own register.** A post that opens with a hook rather than with context is correct, and a document that does the same is not. Never carry a finding from one register into the other.
- **Order the findings by what they cost the reader**, not by where they sit in the text.
- **The verdict is `REVISE` when at least one finding is critical or major.** Otherwise it is `PASS`. A `PASS` with minor findings is normal and correct.
- **Keep the author's meaning and the author's facts.** Rewrite the sentence, never the claim. When a sentence is unclear because you cannot tell what it means, report it and ask — do not guess a meaning and rewrite to it.
- **Do not invent findings.** A sound text gets a `PASS` and a short note on what it does well. Padding a review to look thorough wastes the one read you get.

## The report

Write this for the person, under the loaded skill's own rules — they govern your review as much as the text under it.

```markdown
## Verdict

PASS | REVISE — [the one thing that costs the reader most, in one sentence]

Reviewed as: [technical | social | technical and social]

## Findings

### [severity] `CODE` — [what the reader loses, in a few words] (line N)

> [the text as it stands]

[One short active sentence on the problem.]

**Instead:** [the text you would put in its place]

## What the text does well

- [At most three. Drop the section when the text is a first draft.]
```

Keep each problem and each replacement to one sentence. A finding with no replacement is an opinion, so write the replacement even when it costs you a line.

## The findings block

End every reply with exactly **one** fenced `json` block, as the last thing you write, in this shape:

```json
{ "target": "", "registers": ["technical" | "social"],
  "verdict": "PASS" | "REVISE", "summary": "",
  "counts": { "critical": 0, "major": 0, "minor": 0 },
  "findings": [{ "rule": "CW2.1", "severity": "critical|major|minor", "line": 0,
    "span": "", "problem": "", "fix": "" }] }
```

- **`target`** is the path you reviewed, or `"(inline text)"` when the text came in the argument or from the conversation.
- **`registers`** lists the skills you applied — `["technical"]`, `["social"]`, or both. It is never empty, and a tool uses it to know which codes could have fired.
- **`rule`** is a code from the loaded skill's registry, spelled exactly. A technical code starts with `T`, a social one with `S`, and the second letter names its group — `TA2`, `SH4`. Never invent a code.
- **`span` is the anchor, and `line` is a hint.** Copy the span character for character from the text, long enough to appear once. A tool finds the finding by searching for the span, so a span you tidied on the way out points at nothing.
- **`line`** counts from 1 in the text as you received it. **Set it to `null` rather than guess** — a pasted text with no stable line numbering gets `null`, and the span still locates it.
- **`fix`** is the text that replaces the span. Set it to `null` when the fix adds rather than replaces, as a missing opening does, and let the report carry the sentences to add.
- **`counts`** matches the findings array. **`verdict`** follows the rule above: `REVISE` when `critical` or `major` is above zero.
- **`findings`** is `[]` on a clean text.

The block is data. No writing rule governs it, and nothing in it is softened, shortened, or reworded.

## When the target ends with `fix`

Report first, then apply. Never apply without the report above it.

1. **Apply only a finding whose `fix` is not `null`**, and only to a file target. A text pasted into the conversation has nothing to write to — return the rewritten text in the reply instead.
2. **Replace the span with the fix, and change nothing else.** You are editing prose. Every code block, path, identifier, and quoted string on the line stays exactly as it was.
3. **Leave a `null` fix to the author** and say which findings you left, with their codes.
4. **Re-read the file after you write it** and say in one line whether anything else moved.

Without `fix`, change no file. The review reports, and the edit is the author's to make.
