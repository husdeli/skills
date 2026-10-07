# Technical Writing — Rule Codes

Every rule in [the skill](../SKILL.md) carries a stable code, grouped the way the rules are grouped. A review names the code, so one finding means the same thing in a report, in a machine-readable block, and in a linter built against this registry later.

**Every code starts with `T` for this skill**, then a letter for its group: `TS` structure, `TV` stance and voice, `TE` reader engagement, `TH` hedging and boosting, `TG` signposting, `TA` avoid. The `social-writing` skill uses `S` the same way, so no code means two things.

**The codes never change meaning.** A new rule takes a new code. A dropped rule leaves its code retired rather than reused.

**`Severity` is the default a review starts from**, not a verdict. Raise it when the finding costs this reader more, lower it when the text is a draft note rather than something a person must act on. Say so in the finding when you move it.

**`Check` says who can decide the finding.** `mechanical` means a script can decide it from the text alone. `judgment` means a reader must decide it. `mixed` means a script finds the candidates and a reader confirms each one.

## Structure

| Code | Checks | Severity | Check |
| --- | --- | --- | --- |
| `TS1` | The opening does not name the subject, the trigger, or what it means for the reader | critical | judgment |
| `TS2` | The evidence comes before the outcome | critical | judgment |
| `TS3` | The text opens with the detail or the history instead of the context | major | judgment |
| `TS4` | The text is blocked and never names what it needs from the reader | critical | judgment |

## Stance and voice

| Code | Checks | Severity | Check |
| --- | --- | --- | --- |
| `TV1` | A sentence names no actor | major | mixed |
| `TV2` | A sentence is passive, or not in the present tense | major | mixed |
| `TV3` | A claim is stated that the writer did not verify | critical | judgment |
| `TV4` | A sales word stands in a technical document | minor | mechanical |
| `TV5` | A known weakness in the design goes unnamed | major | judgment |

## Reader engagement

| Code | Checks | Severity | Check |
| --- | --- | --- | --- |
| `TE1` | A section gives the mechanism without saying what the thing is for | major | judgment |
| `TE2` | A term of art is used before it is defined, or defined away from its first use | major | mixed |
| `TE3` | A procedure's steps are unnumbered where order matters, or a step holds two actions | major | mixed |
| `TE4` | A precondition or a warning arrives after the step it guards | critical | judgment |
| `TE5` | A described behaviour says nothing about empty input, failure, a limit, or a repeat | critical | judgment |

## Hedging and boosting

| Code | Checks | Severity | Check |
| --- | --- | --- | --- |
| `TH1` | An assumption is written as a fact | critical | judgment |
| `TH2` | What the writer did not check goes unsaid | major | judgment |
| `TH3` | A failure, a skip, or a partial result reads as a success | critical | judgment |
| `TH4` | A quantity, a time, or a place is vague where a number or a name is known | major | judgment |
| `TH5` | A version, a flag, or a default is named loosely, or a default is missing | major | mixed |

## Signposting

| Code | Checks | Severity | Check |
| --- | --- | --- | --- |
| `TG1` | A file name, folder, extension, identifier, snippet, `§`, or `¶` sits inside a sentence | major | mixed |
| `TG2` | An exact string the reader must act on is missing from the block or list beside the prose | critical | judgment |
| `TG3` | One thing is called by two names, or a concept does not use the glossary's term | major | judgment |
| `TG4` | A rule another document owns is restated rather than linked | major | judgment |
| `TG5` | The text says "as described above", or the passage uses the wrong shape for the reader's job | minor | mixed |

## Avoid

| Code | Checks | Severity | Check |
| --- | --- | --- | --- |
| `TA1` | The text narrates the process where the reader asked for the answer | minor | judgment |
| `TA2` | A sentence runs past 20 words as an instruction, or 25 as a description | major | mechanical |
| `TA3` | Two ideas joined by a semicolon or a dash | minor | mixed |
| `TA4` | A noun cluster runs to four words or more | minor | mechanical |
| `TA5` | An article or the word "that" is dropped, or the style is telegraphic | major | mixed |
| `TA6` | Jargon, idiom, metaphor, humour, or a hedge | major | judgment |
| `TA7` | A claim holds in only some cases but is written as always true | critical | judgment |
| `TA8` | The text names the reader, or explains why it is being written | minor | mixed |
| `TA9` | A point is restated, or a list runs past three examples of one pattern | minor | judgment |
| `TA10` | A name, path, command, or error message was reworded instead of quoted exactly | critical | mixed |

## Out of scope

**No code covers these, and a review never reports one against them:** source code, an identifier, a file path, a command, quoted output copied from a tool, and the fenced `json` contract blocks agents emit. `TG1` is the one code that touches them, and it fires on the *sentence* that swallowed the string rather than on the string itself.
