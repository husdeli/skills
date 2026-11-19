---
name: whats-next
description: "Shows what is actionable on the roadmap: what is in flight and who holds it, what is ready to start, and what is blocked by what. Use when the user asks what to work on next or for the roadmap's status."
---

# whats-next

Report the roadmap status with the shared command.

## Run the command

1. Resolve `../../commands/whats-next.md` from this skill directory.
2. Read the command file completely before reporting anything.
3. Read the skills the command names from the plugin's `skills/<name>/SKILL.md` — `sdlc-structure`, `ticket-board`, and `technical-writing`.
4. Replace `$ARGUMENTS` with the request text that follows the skill invocation.
5. Use Codex read-only tools to read the roadmap and list the ticket folders.

Treat the shared command as the source of truth for the buckets, the report shape, and the
read-only rule. Write nothing, and move no ticket.

In the final handoff, use these Codex skill names:

- `$sdlc:orchestrate`
- `$sdlc:orchestrate-quick`
- `$sdlc:plan`
- `$sdlc:setup`
