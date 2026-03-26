---
name: design
description: Produces a grounded implementation design by comparing viable approaches, recommending one, running parallel multi-model critique, reconciling feedback, and revising the design.
---

Variables:
- `<PlanPath>`: primary plan, findings doc, or latest investigation artifact. Default: latest relevant session artifact.
- `<OutputPath>`: optional output path for the design artifact. Default: adjacent to `<PlanPath>`.
- `<Topic>`: optional feature or subsystem under review. Default: inferred from `<PlanPath>`.

Create or update an implementation design based on `<PlanPath>` for `<Topic>`.

This skill is for implementation-oriented design review, not broad product ideation and not a backlog decomposition pass.

## Objectives

1. Read and understand the latest plan, findings, and relevant source materials.
2. Identify the main design decision(s) that still matter for implementation.
3. Develop at least 2 viable approaches grounded in the current repository and constraints.
4. Compare the approaches across implementation complexity, consistency with existing architecture, operational risk, testing impact, migration cost, and long-term maintainability.
5. Recommend one approach with a clear rationale.
6. Spawn 3 parallel critique subagents from different model families.
7. Reconcile the critique feedback carefully, separating valid findings from weak or conflicting feedback.
8. Revise the original design using only relevant, valid, non-contradictory improvements.
9. Produce a final design artifact plus a concise review log showing what changed and why.

## Core principles

1. Ground the design in the current codebase, docs, and latest findings.
2. Make sure to research online, industry standard and best practices or prior art.
3. Explore multiple viable approaches before converging.
4. Prefer approaches aligned with existing architecture and repository conventions unless there is a strong reason to change course.
5. Be explicit about tradeoffs.
6. Treat critique as adversarial input, not truth.
7. Do not accept feedback just because multiple models said it.
8. Preserve useful parts of the original design when critique does not invalidate them.
9. Optimize for implementation clarity, not theoretical elegance.

## Operating rules

1. Inspect the current plan/findings first before proposing approaches.
2. If the repository already constrains the solution direction, treat that as a real constraint.
3. Compare at least 2 viable approaches. You may include more if they are meaningfully distinct.
4. Do not include fake alternatives that are obviously inferior just to satisfy the comparison requirement.
5. For each approach, analyze:
   - fit with current architecture
   - implementation scope
   - migration or rollout impact
   - testing strategy implications
   - operational risk
   - developer ergonomics
   - future extensibility
6. Recommend exactly one approach unless the evidence is genuinely insufficient.
7. Keep the initial design draft concise but implementation-oriented before sending it to critique.

## Required initial design structure

Produce an initial design with these sections:

1. **Context**
   - what problem is being solved
   - what inputs were reviewed
   - relevant constraints

2. **Current state**
   - what exists today
   - what is already decided
   - what remains to be decided

3. **Approach options**
   - at least 2 viable approaches
   - architecture sketch for each
   - pros, cons, and risks for each

4. **Recommendation**
   - chosen approach
   - why it wins
   - why the alternatives were rejected

5. **Implementation shape**
   - affected subsystems / files / layers
   - data flow and API impact
   - migration / rollout / testing implications

6. **Known risks / open questions**
   - only unresolved items that materially affect implementation

## Parallel critique phase

After the initial design draft is complete, spawn exactly 3 parallel critique subagents.

Use the strongest available model from each family in the current session, preferring:
- OpenAI: GPT-5.4 or better available GPT-5.x reasoning/coding model
- Anthropic: Claude Opus 4.6 or better available Claude-family reasoning model
- Google: Gemini 3 Pro or better available Gemini-family reasoning model

If a named model is unavailable, use the strongest available model in that family and record the substitution.

Each critique subagent must:
- review the draft independently
- challenge assumptions
- look for architectural inconsistencies
- identify missing edge cases
- identify testing, migration, and rollout weaknesses
- call out over-engineering or unjustified complexity
- suggest concrete improvements
- avoid rewriting the design from scratch unless fundamentally flawed

Each critique subagent must return feedback in this structure:

1. **Top concerns**
2. **Potential design flaws**
3. **Missing considerations**
4. **Over-engineering / unnecessary complexity**
5. **Suggested changes**
6. **Confidence and uncertainty**

## Critique reconciliation rules

After all 3 critiques return:

1. Consolidate all feedback into a single review matrix.
2. Group overlapping feedback together.
3. Mark each item as:
   - accepted
   - partially accepted
   - rejected
   - unresolved
4. For each item, explain why.
5. Prefer feedback that is:
   - grounded in the repository or stated constraints
   - specific and actionable
   - consistent with the implementation goal
6. Reject feedback that is:
   - generic
   - speculative without evidence
   - contradictory to known constraints
   - pushing unnecessary abstraction or redesign
7. Do not bias toward majority vote alone.
8. If critiques conflict, resolve the conflict explicitly.

## Revision phase

Revise the original design by applying accepted and partially accepted feedback.

The revised design must:
- preserve the original recommendation unless critique genuinely changes the conclusion
- integrate valid improvements cleanly
- remove ambiguities uncovered during critique
- remain implementation-oriented and concise
- be stronger than the original draft, not just longer

## Required final output

Produce:

1. **Final revised design**
2. **Critique summary**
   - which models were used
   - any substitutions
3. **Feedback reconciliation log**
   - accepted / partially accepted / rejected / unresolved items
   - brief rationale for each
4. **Delta summary**
   - what changed from the original draft
   - why those changes improved the design
5. **Residual open questions**
   - only items that still need human input or deeper investigation

## Quality bar

- Do not recommend an approach without comparing real alternatives.
- Do not pretend alternatives are viable if they clearly are not.
- Do not accept critique blindly.
- Do not inflate the design with generic best-practice prose.
- Do not produce a backlog; produce a design strong enough to later decompose into backlog work.
- The final artifact should be executable by engineers without needing the chat history.