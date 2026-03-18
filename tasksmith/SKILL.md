---
name: tasksmith
description: Generates execution-ready epics and highly scoped implementation tasks with frontmatter metadata from an execution plan and source requirements/design materials.
---

Variables:
- `<BacklogPath>`: backlog directory. Default: `@docs/backlog/`
- `<PlanPath>`: path to the execution plan. Default: `@docs/backlog/backlog-plan.md`
- `<RequirementsPath>`: path to the requirements, plans, design documents, research notes, and related source materials

Create or update an execution-ready implementation backlog in `<BacklogPath>` using `<PlanPath>` and the materials in `<RequirementsPath>`.

The backlog must consist of:
- an index file at `<BacklogPath>/index.md`
- epic files under `<BacklogPath>/epics/`
- task files under `<BacklogPath>/tasks/`

You are producing backlog artifacts for autonomous AI coding agents, not a product summary and not a broad architecture plan.

## Objectives

1. Read the execution plan and source materials.
2. Create or update a small set of coherent epics.
3. Break each epic into the most narrowly scoped useful tasks possible.
4. Ensure every task is self-contained and executable without chat context.
5. Update `<BacklogPath>/index.md` so the backlog is navigable and dependency-aware.

## Core principles

1. Default to agent-executable tasks.
2. Scope tasks as narrowly as possible while preserving meaningful standalone progress.
3. If a task can be broken into smaller independently valuable tasks, split it.
4. The bar for `owner_type: human` is very high.
5. Do not reopen major design questions already resolved in `<PlanPath>` unless there is a clear contradiction or critical gap.
6. Reuse and update existing backlog items when appropriate instead of duplicating them.

## Operating rules

1. Inspect existing backlog files first and follow established repository conventions.
2. Prefer adapting existing structure over inventing a new one.
3. Use `<PlanPath>` as the primary source for workstream boundaries, design direction, and decomposition guidance.
4. Use `<RequirementsPath>` to ground references, acceptance criteria, and implementation context.
5. Split tasks that mix design, implementation, migration, testing, rollout, or unrelated code areas unless tightly coupled.
6. Split tasks that require different validation strategies.
7. Merge tasks only when separation would create artificial overhead without meaningful execution value.
8. Deduplicate overlapping tasks and normalize terminology before writing files.
9. Keep one epic or task per file.
10. Use kebab-case file names.

## Epic template

Each epic must use this structure:

```md
---
id: E-TBD
title: <epic title>
status: todo
depends_on: []
priority: high
source_paths: []
child_tasks: []
tags: []
---

# Objective

# Scope

# Non-goals

# Dependencies

# Risks

# Acceptance criteria

# References