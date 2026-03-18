---
name: scopewright
description: Derives an execution plan from requirements and design materials by identifying workstreams, resolving non-trivial design choices, and defining decomposition boundaries for backlog creation.
---

Variables:
- `<RequirementsPath>`: path to the requirements, plans, design documents, research notes, and related source materials
- `<PlanPath>`: output path for the execution plan. Default: `@docs/backlog/backlog-plan.md`

Create or update `<PlanPath>` from the available materials in `<RequirementsPath>`.

You are not writing implementation tasks. You are defining the execution shape that a backlog-generation skill will later materialize.


## Interaction mode

At the start, determine the operating mode:

- `autonomous`: proceed from the available materials with minimal questions
- `interactive`: ask focused questions until there is enough clarity to produce a strong execution plan
- `hybrid`: make an initial autonomous pass, then ask only the highest-leverage unresolved questions

If the user specifies a mode, follow it.
If the user does not specify a mode, default to `autonomous`.

When asking questions:
1. ask only questions that materially affect backlog shape, design direction, dependency order, or human-required classification
2. prefer small batches of high-leverage questions over long questionnaires
3. do not ask questions that can be answered by grounded judgment from the available materials
4. stop asking once there is enough clarity to produce a strong execution plan
5. Always provide options with recommendations when asking questions, and do not ask open-ended questions without options.


## Objectives

1. Read the source materials and identify the major implementation workstreams.
2. Resolve the non-trivial design choices required to make backlog creation actionable.
3. Compare at least two plausible approaches for each material design decision.
4. Recommend the best approach grounded in the available materials.
5. Define decomposition boundaries so a second skill can generate narrowly scoped tasks.
6. Identify any truly human-required steps, with a very high bar.

## Core principles

1. Stay grounded in the available specs, requirements, repository conventions, and source materials.
2. Make design decisions when the materials are sufficient to support a reasonable recommendation.
3. Do not escalate to humans just because the work is ambiguous or difficult.
4. Treat human-required actions as rare and only for truly unavoidable external actions.
5. Prefer decisions that simplify autonomous execution, reduce ambiguity, and preserve alignment with the documented requirements.

## Operating rules

1. Inspect relevant existing docs and repository conventions first.
2. Identify the major workstreams and dependency order.
3. For each non-trivial design choice that affects execution shape, compare at least two plausible approaches.
4. Recommend one approach and briefly justify it.
5. Convert design conclusions into decomposition guidance for later backlog generation.
6. Flag unresolved issues only when they truly cannot be decided from the available materials.
7. Keep the output concise, actionable, and structured for direct consumption by a backlog-generation skill.

## Human-required rule

A step may be marked human-required only when direct human action is unavoidable, such as:
- signing up for a third-party service
- completing a legal or financial approval
- supplying credentials, secrets, licenses, or payment information not present in the repo or docs
- making a business-direction decision not answerable from the available materials

Do not mark something human-required just because:
- multiple technical approaches exist
- requirements are somewhat incomplete
- design judgment is needed
- research or prior art comparison is needed

## Output format

Write `<PlanPath>` as markdown with the following structure:

# Execution plan

## Source inputs
- list of key source documents used

## Workstreams
- list the major implementation workstreams

## Design decisions

### Decision: <name>

#### Context

#### Option 1

#### Option 2

#### Recommendation

#### Rationale

#### Implications for backlog decomposition

## Epic candidates
- proposed epic names with brief objectives

## Decomposition strategy
- how work should be split into narrowly scoped tasks
- guidance on what should be split vs kept together

## Dependency order
- epic and workstream sequencing

## Human-required candidates
- item
- justification
- why agent execution is not sufficient

## Open issues
- only include issues that truly could not be resolved from the available materials

## Definition of done

Do not finish until:
- major workstreams are identified
- material design decisions are resolved or explicitly justified as unresolved
- at least two approaches are compared for each material design choice
- decomposition guidance is clear enough for backlog generation
- human-required items are rare and justified
- the plan is usable by a second skill without chat context

Finish with a short summary of:
- what was decided
- major assumptions made
- unresolved issues, if any