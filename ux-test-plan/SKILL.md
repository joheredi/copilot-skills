---
name: ux-test-plan
description: Explore the ERP web app with Playwright CLI and produce a UX-focused black-box test plan, detailed test cases, and actionable issue files with evidence.
---

# UX Test Plan Generation with Playwright CLI

Use this skill when you want Copilot to autonomously explore the ERP web app through the UI and generate a complete UX-focused black-box test plan for later execution by AI agents.

## Goal

Explore the running application primarily through **Playwright CLI** and produce:

* a master test plan in Markdown
* detailed test case Markdown files
* issue/bug Markdown files for problems found during exploration
* screenshots or other evidence when possible

The emphasis is **UX-first black-box testing** while still validating basic functional correctness.

## What good output looks like

The output should be strong enough that:

* another AI agent can execute the test cases without rediscovering the app
* another AI agent can pick up an issue file and investigate/fix effectively
* UX, responsiveness, accessibility, and design quality are treated as first-class quality criteria
* issues are based on real UI exploration, not speculation

## Inputs

Before starting, gather or infer these inputs:

* app URL or local dev URL
* authentication approach and any credentials/test users if available
* any required setup data or seed data
* repo root
* output folders under `docs/`

If some inputs are missing, proceed with the accessible parts of the app and document assumptions clearly.

## Primary operating mode

Use **UI-first exploration** through Playwright CLI.

Rules:

* Prefer black-box exploration through the browser.
* Use source code only to validate assumptions or clarify behavior.
* Do not turn this into a white-box implementation review.
* When uncertain about expected UX, research current best practices and industry standards online and use that to justify expected behavior.

## UX review standard

Do not stop at “it works.”

Flag issues when UX is suboptimal, confusing, inefficient, inaccessible, or likely to cause user mistakes.

Examples that must be flagged:

* free-text input where the system could provide autocomplete, lookup, select options, or validated choices
* missing loading indicators
* missing success or error feedback
* unclear validation messages
* forms that allow avoidable mistakes
* destructive actions without confirmation or undo
* poor empty states
* confusing navigation or information architecture
* repeated or unnecessary user effort
* inconsistent labels, buttons, or interaction patterns
* broken or degraded mobile/tablet layouts
* poor keyboard support or focus handling
* controls without clear labels or accessible names
* screens that leave the user unsure whether data was saved or what to do next

## Device coverage

At minimum evaluate:

* desktop
* tablet
* mobile

Use representative responsive viewports and capture device-specific issues.

## Accessibility / design expectations

Assess at least:

* keyboard navigation
* focus visibility and focus order
* labels and accessible names
* form validation clarity
* status, warning, success, and error feedback
* responsiveness and touch friendliness
* readability and scanability
* consistency and affordance
* error prevention and recovery
* general enterprise SaaS / ERP UX best practices

## Exploration scope

Autonomously identify and explore, where available:

* main navigation
* key modules
* high-value workflows
* CRUD flows
* forms and validation patterns
* tables, filters, search, pagination, bulk actions
* setup/configuration areas
* authentication/session UX
* empty/loading/error states
* responsive behavior across devices

If the app is broad, prioritize the most central user-facing workflows first.

## Deliverables

Generate the following artifacts.

### 1) Master test plan

Path:

`docs/testing/test-plan.md`

Contents:

* Title
* Objective
* Scope
* Non-scope
* Testing approach
* Environments / assumptions
* Device / viewport coverage
* Quality criteria
* UX review criteria
* Accessibility review criteria
* Risk areas
* Test data strategy
* Module / feature inventory discovered during exploration
* Prioritized test coverage matrix
* List of all test cases with IDs and links
* Open questions / assumptions
* Summary of issues found during exploration

### 2) Individual test cases

Path pattern:

`docs/testing/test-cases/<area>/<test-case-id>.md`

Each test case file must include:

* Test Case ID
* Title
* Area / Module
* User Goal
* Priority
* Preconditions
* Test Type
* Coverage Tags
* Related Requirements / Assumptions
* Description
* Steps
* Expected Results / Pass Criteria
* Fail Criteria
* Valid Data
* Invalid Data
* Responsive / Device Notes
* Accessibility Checks
* UX Heuristics / Design Expectations
* Notes for future execution agents
* Related issues (if any)

The test case must be specific enough that another AI agent can execute it without ambiguity.

### 3) Issues found during exploration

Path pattern:

`docs/test-results/issues/<issue-id>.md`

Each issue file must include:

* Issue ID
* Title
* Severity
* Priority
* Type (`bug`, `ux`, `accessibility`, `responsive`, `design`, or combined)
* Area / Module
* Environment / viewport
* Summary
* Observed behavior
* Expected behavior
* Why this is a problem for users
* Reproduction steps
* Evidence
* Suspected scope / affected flows
* Hypothesis / notes for investigation
* Recommended direction for fix
* Screenshots / artifact paths
* Related test case IDs

Make issues actionable for a future AI investigation/fix agent.

### 4) Evidence

Suggested paths:

* `docs/test-results/evidence/`
* `docs/test-results/screenshots/`

Use stable, descriptive names.

## Recommended naming conventions

Use kebab-case filenames.

Suggested stable IDs:

* test cases: `TC-AUTH-001`, `TC-SALES-003`, `TC-INVENTORY-002`
* issues: `ISSUE-UX-001`, `ISSUE-A11Y-004`, `ISSUE-RESP-002`

Prefer grouping test cases by module.

## Execution procedure

Follow this sequence:

1. Launch or connect to the target app.
2. Use Playwright CLI to explore the UI.
3. Map the navigation, modules, and major workflows.
4. Exercise representative happy paths, edge cases, and obvious failure cases.
5. Review forms carefully for:

   * input method appropriateness
   * defaults
   * validation
   * error prevention
   * feedback
   * unnecessary typing or repeated work
6. Review tables, search, filters, and list management UX.
7. Evaluate empty, loading, success, warning, and error states wherever possible.
8. Re-run key workflows on desktop, tablet, and mobile viewports.
9. Capture screenshots/evidence for important findings.
10. Create issue files immediately when meaningful problems are found.
11. Synthesize a master test plan.
12. Generate detailed test case files for all covered areas.

## Constraints

* Do not generate shallow or generic test cases.
* Do not focus mainly on implementation details.
* Do not assume UX is acceptable just because a flow technically works.
* Prefer concrete observations from actual UI exploration.
* Document assumptions explicitly.
* Use source inspection only when necessary to validate assumptions.

## Quality bar

The final output must be:

* practical
* execution-ready
* organized for future AI agents
* grounded in real exploration
* strong on UX, responsiveness, accessibility, and basic correctness

## Invocation

Provide run-specific inputs at execution time rather than hardcoding them in the skill.

Pass these inputs explicitly when invoking the skill:

* `APP_URL`: base URL of the target environment
* `TEST_USER_EMAIL`: login email for the test user
* `TEST_USER_PASSWORD`: login password for the test user
* `TEST_NOTES` (optional): any environment-specific notes, seed data notes, MFA caveats, or scope limits

Example invocation payload:

```text
APP_URL=https://your-app-url.example.com
TEST_USER_EMAIL=test.user@example.com
TEST_USER_PASSWORD=<secret>
TEST_NOTES=Use seeded tenant Acme Demo. Focus on sales, customers, inventory, settings. Skip billing if unavailable.
```

Use the provided values only for test execution. Do not persist secrets into generated documentation unless the repo already has an approved secure pattern for test credentials.

If credentials are missing or login fails, continue with all accessible unauthenticated areas and document the limitation in the test plan.

## Suggested repo structure

```text
docs/
  testing/
    test-plan.md
    test-cases/
      auth/
      sales/
      inventory/
      customers/
      settings/
  test-results/
    issues/
    evidence/
    screenshots/
```

## Final instruction

Explore the application autonomously through Playwright first, then write the docs from observed behavior. Keep the work black-box and UX-centered.
