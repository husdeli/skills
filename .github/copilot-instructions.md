# Copilot Instructions

## Repository Purpose

This is a **skills repository** — a collection of reusable AI/Copilot workflow skill definitions. Skills are invoked by AI assistants (like GitHub Copilot) to guide structured, multi-phase workflows.

## Structure

Each skill lives under `skills/<skill-name>/` and must follow this layout:

```
skills/<skill-name>/
  SKILL.md          # Required: skill definition with YAML frontmatter
  assets/           # Optional: templates referenced in the skill (e.g. ticket-template.md)
  references/       # Optional: detailed reference docs linked from SKILL.md
```

## SKILL.md Format

Every `SKILL.md` must begin with YAML frontmatter:

```yaml
---
name: skill-name
description: "One-sentence description of what the skill does and when to invoke it."
argument-hint: "Optional: description of accepted argument"
---
```

- `description` is what AI tools display when deciding whether to invoke the skill — make it specific about trigger conditions ("Use when: ...")
- `argument-hint` describes optional input the user can pass when invoking the skill

## Key Conventions

- **Skill content is instructional** — written as directives to the AI agent, not as documentation for humans
- **Templates use placeholder syntax** like `[TICKET-ID]`, `[Feature Name]`, `YYYY-MM-DD` — keep this consistent when adding new templates
- **Phased workflows** must include explicit feedback checkpoints: the agent must pause and request user approval before advancing to the next phase
- **Tickets describe WHAT, not HOW** — implementation specifics (file paths, library names, code patterns) belong in the plan created after codebase exploration, not in the ticket itself
- **Testing order preference**: Unit tests → Integration/API tests → Frontend E2E (critical paths only)

## Adding a New Skill

1. Create `skills/<new-skill-name>/SKILL.md` with valid frontmatter
2. Add any templates to `assets/` and reference docs to `references/`
3. Link to assets/references using relative paths: `./assets/filename.md`
