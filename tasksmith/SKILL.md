---
name: tasksmith
description: Turns a design-ready plan into self-contained GitHub issues with clear acceptance criteria, platform constraints, and real dependencies.
---

Variables:
- `<PlanPath>`: path to the execution plan. Default: session plan.

Create or update an execution-ready backlog as GitHub issues using
`<PlanPath>`. Repository issues are the canonical backlog; do not write
Markdown task files or an index.

## Objectives

1. Read the plan and related source materials, then verify the design is ready
   to decompose.
2. Inspect repository issue conventions and reconcile existing task issues
   before proposing changes.
3. Break work into independently reviewable tasks that preserve the design's
   boundaries and platform constraints.
4. Preview the complete proposed issue batch and get approval before writing
   to GitHub.
5. Verify the resulting issues and relationships, then report their URLs.

## Core principles

1. Default to `owner_type: agent`.
2. Scope tasks to independently reviewable progress while respecting clear
   architectural boundaries; split only when work and validation are
   meaningfully independent.
3. Do not split work just to maximize parallelism or create artificial
   dependencies.
4. Do not reopen design decisions already resolved in `<PlanPath>` unless new
   evidence, a contradiction, infeasibility, or a material platform risk
   warrants it.
5. Preserve design intent and constraints in the tasks without prescribing
   implementation details the design leaves open.
6. Reuse and update matching issues instead of duplicating them.
7. The bar for `owner_type: human` is very high.

## Operating rules

1. Resolve the target repository from the checkout containing `<PlanPath>` if
   it is in a repository; otherwise use the current working directory's
   repository. Ask only if neither or multiple targets are plausible.
2. Inspect existing issues, labels, and any Markdown backlog before proposing
   work. If a Markdown backlog exists, ask whether to migrate it; never rewrite
   or delete those files.
3. Use the plan as the authority for design direction and workstream
   boundaries. Do not use task decomposition to invent or silently settle
   architecture.
4. Before decomposition, check whether consequential design choices are
   supported by evidence and rationale about platform fit, ownership and
   boundaries, maintainability, and lifecycle concerns relevant to the change.
5. If a material omission or contradiction could change the platform approach,
   task boundaries, or acceptance criteria, pause decomposition and explain
   the gap. Offer to return to `design` or `scopewright`; do not manufacture
   implementation tasks that hide the unresolved choice. For non-material
   gaps, state a bounded assumption and proceed.
6. Carry approved architectural constraints and invariants into task
   descriptions and acceptance criteria. Include compatibility, migration,
   operational, or failure-path work when the design requires it; do not add
   generic checklist tasks.
7. Split tasks that mix unrelated ownership or validation only when the split
   yields meaningful standalone progress. Keep design, implementation,
   migration, testing, and rollout together when separating them would break
   an end-to-end outcome.
8. Deduplicate by stable task identity and content. Flag plausible duplicates
   for review instead of merging uncertain matches.

## Task quality bar

Every task must:
- be executable without chat history
- identify relevant code/docs paths or subsystems
- describe the exact intended change
- include explicit acceptance criteria
- include validation steps
- preserve relevant design constraints and cite source sections
- list real dependencies only when required
- be independently reviewable without violating ownership boundaries

Do not create tasks that:
- span multiple unrelated modules or layers
- mix vague investigation with implementation
- say “handle edge cases” without naming them
- omit how success will be validated
- require rediscovering decisions already documented in `<PlanPath>`
- encode an unresolved architectural decision as an implementation detail

## Owner type rules

Use `owner_type: human` only when the task primarily requires:
- unresolved business or policy judgment
- stakeholder/product/design approval
- legal/compliance signoff
- credentials or system access unavailable to agents
- real-world operational coordination

Otherwise use `owner_type: agent`.

## Issue structure

- Create one issue per executable task. Create a parent issue only for a
  meaningful epic/workstream; do not create one mechanically.
- Use native blocked-by relationships for real dependencies.
- Keep each issue self-contained. Include title, task summary, owner type,
  priority, repository paths, source references, acceptance criteria, and
  validation steps in a consistent body. Link to source material when it has
  an accessible URL; otherwise include its path and section without depending
  on it to execute the issue.
- Put a stable, repository-unique ID on a literal body line in every task and
  parent issue: `Tasksmith-ID: <stable-id>`. Scope new IDs to the initiative;
  preserve them when updating and reuse migrated IDs only if they do not
  collide. Verify exact body-line matches across open and closed issues.
- Search can find candidates but a missing search result is not proof of
  absence. Before creating issues, reconcile IDs against a complete paginated
  repository issue listing. If discovery is incomplete or IDs collide, stop
  and report the problem rather than guessing.
- Reuse matching repository labels when useful; do not create labels
  automatically. Do not require issue types or a GitHub Projects board.
- Use open/closed issue state: completed tasks are closed; other actionable
  tasks are open. Blocked state is represented by dependencies, not a manually
  maintained status field.
- When a task is superseded, propose closing it as not planned and link its
  replacement issue(s). For a split, close the old executable issue and link
  the new tasks. Include all closures and relationship changes in the preview.

## Approval and publication

1. Check that `gh` is authenticated and targets the intended repository. Check
   the local `gh` version supports required native hierarchy/dependency
   operations; v2.94.0 introduced those CLI features.
2. Prepare a complete preview of issue titles and bodies, labels, parent and
   blocked-by links, updates, and proposed closures. Request one explicit
   approval before any GitHub write.
3. After approval, create or update issue records first and capture each
   issue's number and URL. Then apply parent and dependency
   additions/removals, and verify the final state. Do not change relationships
   based on truncated reads.
4. If the host or repository rejects a native relationship, stop and report
   what succeeded and what failed. Do not silently flatten relationships or
   fall back to raw API calls.
5. If a batch partially fails or a create outcome is uncertain, report
   completed writes and stop. Reconcile by exact `Tasksmith-ID` against the
   complete listing before retrying; do not retry blindly.