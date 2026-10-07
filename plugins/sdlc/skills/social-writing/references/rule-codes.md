# Social Writing — Rule Codes

Every rule in [the skill](../SKILL.md) carries a stable code, grouped the way the rules are
grouped. A review names the code, so one finding means the same thing in a report, in a
machine-readable block, and in a linter built against this registry later.

**Every code starts with `S` for this skill**, then a letter for its group: `SS` structure, `SV`
stance and voice, `SE` reader engagement, `SH` hedging and boosting, `SG` signposting, `SA` avoid.
The `technical-writing` skill uses `T` the same way, so no code means two things.

**The codes never change meaning.** A new rule takes a new code. A dropped rule leaves its code
retired rather than reused.

**`Severity` is the default a review starts from**, not a verdict. Raise it when the finding costs
this post more, lower it when the post is a draft. Say so in the finding when you move it.

**`Check` says who can decide the finding.** `mechanical` means a script can decide it from the
text alone. `judgment` means a reader must decide it. `mixed` means a script finds the candidates
and a reader confirms each one.

## Structure

| Code | Checks | Severity | Check |
| --- | --- | --- | --- |
| `SS1` | The first line sets context instead of carrying a stance or a stake | critical | judgment |
| `SS2` | The body wanders from the hook's promise, or holds more than one idea | major | judgment |
| `SS3` | The close invites nothing, or invites a reaction rather than a reply | major | judgment |
| `SS4` | A thread post does not open with its own hook | major | judgment |

## Stance and voice

| Code | Checks | Severity | Check |
| --- | --- | --- | --- |
| `SV1` | The post takes no position a reader could agree or disagree with | critical | judgment |
| `SV2` | No self-mention where the claim is the writer's own experience | major | mixed |
| `SV3` | A lesson is given with no cost attached — no days, money, or admitted mistake | major | judgment |
| `SV4` | The voice is flattened into brand or house style | major | judgment |
| `SV5` | The post carries more than one idea | major | judgment |

## Reader engagement

| Code | Checks | Severity | Check |
| --- | --- | --- | --- |
| `SE1` | The post never addresses the reader as "you" | major | mechanical |
| `SE2` | More than one question, or a question before the close | major | mechanical |
| `SE3` | The answer arrives before the reader's situation is named | major | judgment |
| `SE4` | The ask is generic — "thoughts?", "agree?" — rather than a specific response | major | mixed |
| `SE5` | The first line does not stand alone when the platform truncates the rest | critical | judgment |

## Hedging and boosting

| Code | Checks | Severity | Check |
| --- | --- | --- | --- |
| `SH1` | A claim is boosted with no evidence, or hedged where evidence exists | major | judgment |
| `SH2` | A strong claim carries no number, version, or timebox | major | judgment |
| `SH3` | One case is generalised to "always", "never", or "everyone" | major | mixed |
| `SH4` | The hook is hedged, so the post opens with no stake | critical | judgment |
| `SH5` | Authority is claimed in the post rather than shown | minor | judgment |

## Signposting

| Code | Checks | Severity | Check |
| --- | --- | --- | --- |
| `SG1` | The first line signals no payoff | major | judgment |
| `SG2` | More than one part, unnumbered | minor | mixed |
| `SG3` | A wall of text with no line breaks | major | mechanical |
| `SG4` | A document transition — "furthermore", "in conclusion", "that said" | minor | mechanical |
| `SG5` | The post ends by summarising what the reader just read | minor | judgment |

## Avoid

| Code | Checks | Severity | Check |
| --- | --- | --- | --- |
| `SA1` | A context-setting first line | critical | judgment |
| `SA2` | Broetry — one sentence per line with no content behind the rhythm | major | judgment |
| `SA3` | Engagement bait as the close | major | mixed |
| `SA4` | A humble-brag frame | minor | mixed |
| `SA5` | A false reveal — "it is not X, it is Y" with nothing under it | major | mechanical |
| `SA6` | A list of negations — "no fluff, no filler, no excuses" | minor | mechanical |
| `SA7` | A trailing comma clause carrying a thought the sentence did not need | minor | mixed |
| `SA8` | More than three hashtags, or a hashtag nobody searches | minor | mechanical |
| `SA9` | A result claimed that the writer cannot show | critical | judgment |
| `SA10` | Someone else's post or words reused without credit in the post | critical | judgment |

## Out of scope

**No code covers these, and a review never reports one against them:** a quoted source, a handle,
a link, a hashtag the writer chose deliberately and can defend, and the platform's own formatting.
A deliberate stylistic choice the writer owns is not a finding — say you noticed it and move on.
