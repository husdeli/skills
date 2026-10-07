---
name: review-text
description: Review a text written for people against the technical-writing or social-writing rules and return both a report and a machine-readable findings block. Use when a user asks to review, edit, proofread, or improve a text, or invokes `$review-text` as the Codex equivalent of `/review-text`.
---

# Review Text

Review the requested text with the shared review-text command.

## Run the command

1. Resolve `../../commands/review-text.md` from this skill directory.
2. Read the command file completely before you read the text under review.
3. Load the skill for the register the command names — `technical-writing`, `social-writing`, or
   both — and read each one's `references/rule-codes.md`. Resolve every path from the plugin root.
4. Replace `$ARGUMENTS` with the request text that follows the skill invocation.
5. Use Codex read-only tools to read the target. Write to a file only when the request ends with
   `fix`.

Treat the shared command as the source of truth for the target resolution, the severities, the
report shape, and the findings block.
