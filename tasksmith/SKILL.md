---
name: tasksmith
description: Generates and maintains an execution-ready backlog of highly scoped implementation tasks with strict frontmatter metadata from a plan and related source materials.
---

Variables:
- `<BacklogPath>`: backlog directory. Default: `@docs/backlog/` or `@docs/prd` whichever exists. If both exist ask the user to choose or specify a custom path.
- `<PlanPath>`: path to the execution plan. Default: session plan.

Create or update an execution-ready implementation backlog in `<BacklogPath>` using `<PlanPath>`.

The backlog must consist of:
- an index file at `<BacklogPath>/index.md`
- epic files under `<BacklogPath>/epics/` (if useful)
- task files under `<BacklogPath>/tasks/`

You are producing backlog artifacts for autonomous AI coding agents. Do not produce a product summary, broad architecture rewrite, or vague project-management prose.

## Objectives

1. Read the execution plan and source materials.
2. Inspect the existing backlog first and preserve useful structure, IDs, and conventions.
3. Create or update a small set of coherent epics when needed.
4. Break work into the smallest independently reviewable and executable tasks possible.
5. Ensure every task is self-contained and executable without chat context.
6. Update `<BacklogPath>/index.md` so the backlog is navigable, dependency-aware, and ready for parallel agent execution.

## Core principles

1. Default to `owner_type: agent`.
2. Scope tasks as narrowly as possible while preserving meaningful standalone progress.
3. If a task can be split into smaller independently valuable tasks, split it.
4. The bar for `owner_type: human` is very high.
5. Do not reopen design decisions already resolved in `<PlanPath>` unless there is a clear contradiction or critical gap.
6. Reuse and update existing backlog items when appropriate instead of duplicating them.
7. Prefer tasks that can be validated independently and merged safely.
8. Prefer parallelizable decomposition over long serial dependency chains.

## Operating rules

1. Inspect existing backlog files first and follow established repository conventions.
2. Prefer adapting existing structure over inventing a new one.
3. Use `<PlanPath>` as the primary source for workstream boundaries, design direction, and decomposition guidance.
4. Split tasks that mix design, implementation, migration, testing, rollout, or unrelated code areas unless they are inseparable.
5. Split tasks that require different validation strategies.
6. Merge tasks only when separation would create artificial overhead without meaningful execution value.
7. Deduplicate overlapping tasks and normalize terminology before writing files.
8. Keep one epic or task per file.
9. Use kebab-case filenames, prefixed by stable IDs when conventions allow.

## Task quality bar

Every task must:
- be executable without chat history
- identify the relevant code/docs paths or subsystems
- describe the exact intended change
- include explicit acceptance criteria
- include validation steps
- cite the relevant source plan/design sections
- list real dependencies only when required

Do not create tasks that:
- span multiple unrelated modules or layers
- mix vague investigation with implementation
- say “handle edge cases” without naming them
- omit how success will be validated
- require rediscovering decisions already documented in `<PlanPath>`

## Owner type rules

Use `owner_type: human` only when the task primarily requires:
- unresolved business or policy judgment
- stakeholder/product/design approval
- legal/compliance signoff
- credentials or system access unavailable to agents
- real-world operational coordination

Otherwise use `owner_type: agent`.

## Required task frontmatter

Every task file must contain frontmatter with at least:

- `id`
- `title`
- `epic`
- `owner_type`
- `status`
- `priority`
- `depends_on`
- `repo_paths`
- `source_refs`
- `acceptance_criteria`
- `validation_steps`

## Backlog update behavior

When updating an existing backlog:
- preserve stable IDs where possible
- update existing tasks instead of duplicating equivalent work
- mark superseded tasks explicitly and link replacements
- if splitting a large task, update the parent task to reference the new child tasks
- do not silently delete backlog intent unless clearly obsolete

## Index requirements

`<BacklogPath>/index.md` must:
- summarize epics/workstreams
- link every active task
- show status, owner type, and dependencies
- highlight tasks that can run in parallel
- note blocked or superseded work
- link back to the primary source plan/design materials