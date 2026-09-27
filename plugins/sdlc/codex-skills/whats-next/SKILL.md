---
name: whats-next
description: Report what is actionable on the roadmap right now — the tasks in flight and who holds each one, the tasks ready to start, and the tasks waiting on a dependency. Use when a user asks what to work on next, what the roadmap status is, what is blocked, or invokes `$whats-next` as the Codex equivalent of `/whats-next`.
---

# whats-next

Report the roadmap status with the shared command.

## Run the command

1. Resolve `../../commands/whats-next.md` from this skill directory.
2. Read the command file completely before reporting anything.
3. Read the skills the command names from the plugin's `skills/<name>/SKILL.md` — `product-docs`, `ticket-board`, and `clean-writing`.
4. Replace `$ARGUMENTS` with the request text that follows the skill invocation.
5. Use Codex read-only tools to read the roadmap and list the ticket folders.

Treat the shared command as the source of truth for the buckets, the report shape, and the
read-only rule. Write nothing, and move no ticket.

In the final handoff, use these Codex skill names:

- `$sdlc:orchestrate`
- `$sdlc:orchestrate-quick`
- `$sdlc:plan`
- `$sdlc:scaffold`
