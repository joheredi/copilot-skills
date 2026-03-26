---
name: investigate
description: Investigates the current implementation state of a feature, traces how it works in code and docs, and compares findings against an expected understanding.
---

Variables:
- `<Topic>`: feature, workflow, module, or behavior to investigate.
- `<Expectation>`: optional expected behavior or understanding to validate against.

Investigate `<Topic>` in the repository and produce a grounded current-state report.

If `<Expectation>` is provided, explicitly compare the observed implementation against it and call out matches, mismatches, and unresolved areas.

## Objectives

1. Determine the current implementation status of `<Topic>`.
2. Trace the main code paths, data flow, configuration, and relevant tests.
3. Identify whether the feature is implemented, partial, stubbed, deprecated, broken, or inconsistent.
4. Compare the actual implementation to `<Expectation>` if provided.
5. Produce a concise evidence-based report that another engineer can trust without relying on chat history.

## Operating rules

1. Inspect code, tests, docs, configs, and relevant history indicators before concluding.
2. Ground every important claim in repository evidence.
3. Prefer direct code evidence over comments or outdated docs when they disagree.
4. Distinguish clearly between:
   - confirmed behavior
   - likely behavior inferred from code structure
   - missing evidence / unknowns
5. Trace the end-to-end path when relevant:
   - entry points
   - domain logic
   - persistence
   - API surface
   - UI integration
   - configuration / feature flags
   - tests
6. Do not propose redesigns unless asked. Focus first on what exists today.
7. Call out stale docs, dead code, partial migrations, feature flags, TODOs, and test gaps.

## Investigation checklist

For the topic under investigation, inspect as relevant:
- entry points and callers
- core implementation files
- domain/model logic
- API handlers or controllers
- UI or client integration
- persistence/schema/migrations
- config, env vars, and feature flags
- tests and fixtures
- docs, ADRs, and backlog references

## Required output

Produce a report with these sections:

1. **Conclusion**
   - current status in 3-6 bullets

2. **What exists today**
   - what is implemented
   - where it lives
   - how it is wired together

3. **Comparison against expectation**
   - matches
   - mismatches
   - ambiguous / unverified points

4. **Evidence**
   - relevant files and symbols
   - short explanation of what each proves

5. **Gaps and risks**
   - missing behavior
   - stale docs
   - test gaps
   - partial or fragile implementation areas

6. **Open questions**
   - only questions that could not be resolved from the repo

## Quality bar

- Do not say a feature is implemented unless code paths and integration evidence support it.
- Do not say a feature is missing if partial support exists; describe the actual boundary precisely.
- Do not rely on a single file when the behavior spans multiple layers.
- Be explicit when a conclusion is an inference rather than directly proven.