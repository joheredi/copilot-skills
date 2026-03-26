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

### Source-code usage boundary

Source code may be read to:

* discover routes or URLs that are not easily reachable through the UI
* confirm field names or data model details needed to understand a form
* check whether observed behavior is intentional vs. a bug

Source code must **not** be used to:

* derive expected behavior or test oracles
* replace UI exploration with code reading
* write implementation-aware assertions

## Playwright usage

Use the `playwright-cli` skill or browser tools to interact with the app.

Key operations:

* `open_browser_page` — navigate to URLs
* `click_element` / `type_in_page` — interact with UI elements
* `screenshot_page` — capture evidence
* `read_page` — inspect DOM state and visible text

Device viewports for responsive testing:

| Device  | Width | Height |
|---------|-------|--------|
| Desktop | 1920  | 1080   |
| Tablet  | 768   | 1024   |
| Mobile  | 375   | 812    |

Set the viewport before beginning each device pass.

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

### Scope-limiting strategy

If the app is broad:

1. Explore top-level navigation first to build a sitemap.
2. Pick the top 3–5 modules by apparent centrality to users.
3. Within each module, exercise at most 2–3 representative workflows before moving on.
4. Return to lower-priority modules only after high-priority ones are covered.
5. Document any modules that were discovered but not explored.

## Exit criteria

Exploration is considered complete when:

* All discoverable top-level navigation items have been visited at least once.
* At least one full CRUD or primary workflow has been exercised per major module.
* Responsive checks have been performed on at least 3 key screens (desktop, tablet, mobile).
* A sitemap has been produced.
* All discovered issues have been filed.
* Test cases have been written for every explored workflow.

## Deliverables

Generate the following artifacts.

### 0) Navigation sitemap

Path:

`docs/testing/sitemap.md`

Produce this **first**, before any other deliverable. It grounds all subsequent work.

Contents:

* Top-level navigation items
* Sub-navigation / sidebar items per module
* Key pages and their URLs
* Notes on which areas require authentication
* Any areas that were inaccessible or errored

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

Use this template:

```markdown
# {TEST-CASE-ID}: {Title}

| Field                  | Value                          |
|------------------------|--------------------------------|
| Area / Module          |                                |
| User Goal              |                                |
| Priority               |                                |
| Preconditions          |                                |
| Test Type              |                                |
| Coverage Tags          |                                |

## Related Requirements / Assumptions

-

## Description

...

## Steps

1. ...

## Expected Results / Pass Criteria

- ...

## Fail Criteria

- ...

## Data

### Valid Data

- ...

### Invalid Data

- ...

## Responsive / Device Notes

- ...

## Accessibility Checks

- ...

## UX Heuristics / Design Expectations

- ...

## Notes for Future Execution Agents

- ...

## Related Issues

- ...
```

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

Use this template:

```markdown
# {ISSUE-ID}: {Title}

| Field                    | Value                          |
|--------------------------|--------------------------------|
| Severity                 |                                |
| Priority                 |                                |
| Type                     |                                |
| Area / Module            |                                |
| Environment / Viewport   |                                |

## Summary

...

## Observed Behavior

...

## Expected Behavior

...

## Why This Is a Problem for Users

...

## Reproduction Steps

1. ...

## Evidence

- ...

## Suspected Scope / Affected Flows

- ...

## Hypothesis / Notes for Investigation

- ...

## Recommended Direction for Fix

- ...

## Screenshots / Artifact Paths

- ...

## Related Test Case IDs

- ...
```

### 4) Evidence

Suggested paths:

* `docs/test-results/evidence/`
* `docs/test-results/screenshots/`

Use stable, descriptive names.

### 5) Executive summary

Path:

`docs/testing/summary.md`

A one-page overview produced after exploration is complete:

* Modules explored (with coverage confidence: high / medium / low)
* Total test cases generated
* Total issues found, broken down by severity
* Top 3–5 risk areas
* Modules discovered but not explored
* Key open questions
* Recommended next steps

## Recommended naming conventions

Use kebab-case filenames.

Suggested stable IDs:

* test cases: `TC-AUTH-001`, `TC-SALES-003`, `TC-INVENTORY-002`
* issues: `ISSUE-UX-001`, `ISSUE-A11Y-004`, `ISSUE-RESP-002`

Prefer grouping test cases by module.

## Severity and priority definitions

Use these scales consistently across all issues.

**Severity** (impact on the user):

| Level    | Meaning                                                        |
|----------|----------------------------------------------------------------|
| Critical | Blocks a core workflow, causes data loss, or makes a feature unusable |
| Major    | Significant UX degradation; workaround may exist               |
| Minor    | Cosmetic issue or minor inconvenience                          |
| Low      | Enhancement, polish, or nice-to-have improvement               |

**Priority** (order of addressing):

| Level  | Meaning                                      |
|--------|----------------------------------------------|
| P0     | Must fix before release                      |
| P1     | Should fix soon; high user impact            |
| P2     | Fix when convenient; moderate impact          |
| P3     | Backlog; low urgency                         |

## Execution procedure

Follow this sequence. Write checkpoint notes to session memory after completing each phase so progress is preserved if interrupted.

### Phase 1 — Connect and map (sequential)

1. Launch or connect to the target app.
2. Authenticate if credentials are available.
3. Explore top-level navigation and build the **sitemap** (`docs/testing/sitemap.md`).
4. **Checkpoint**: write the sitemap and save a session note listing discovered modules.

### Phase 2 — Explore modules (parallelizable)

For each major module (top 3–5 by centrality):

5. Exercise representative happy paths, edge cases, and obvious failure cases.
6. Review forms carefully for:
   * input method appropriateness
   * defaults
   * validation
   * error prevention
   * feedback
   * unnecessary typing or repeated work
7. Review tables, search, filters, and list management UX.
8. Evaluate empty, loading, success, warning, and error states.
9. Create issue files immediately when meaningful problems are found.
10. **Checkpoint**: save a session note summarizing findings for that module.

**Parallel sub-agents**: After the sitemap is built, launch one sub-agent per module to explore in parallel. Each sub-agent opens its own browser, explores its assigned module, writes issue files, and returns a structured summary of findings. See the **Parallel sub-agent strategy** section.

### Phase 3 — Device and responsive testing (parallelizable)

11. Re-run key workflows on desktop, tablet, and mobile viewports.
12. Capture screenshots/evidence for important findings.
13. File additional responsive or device-specific issues.

**Parallel sub-agents**: Launch one sub-agent per device viewport. Each sub-agent navigates through the same set of key screens at its assigned viewport size, captures screenshots, and files responsive issues.

### Phase 4 — Synthesize deliverables (parallelizable)

14. Write the **executive summary** (`docs/testing/summary.md`).
15. Synthesize the **master test plan** (`docs/testing/test-plan.md`).
16. Generate **detailed test case files** for all covered areas.

**Parallel sub-agents**: Launch one sub-agent per module to write that module’s test case files in parallel. Each sub-agent receives the exploration findings for its module and produces the test case Markdown files. A final sequential pass assembles the master test plan and executive summary from all module outputs.

### Phase 5 — Final review (sequential)

17. Verify all deliverables are internally consistent (IDs match, links resolve, no orphaned references).
18. Verify every explored workflow has at least one test case.
19. Verify every issue references at least one test case.

## Constraints

* Do not generate shallow or generic test cases.
* Do not focus mainly on implementation details.
* Do not assume UX is acceptable just because a flow technically works.
* Prefer concrete observations from actual UI exploration.
* Document assumptions explicitly.
* Use source inspection only when necessary to validate assumptions.

## Error recovery

When exploration encounters problems:

| Situation                          | Action                                                                 |
|------------------------------------|------------------------------------------------------------------------|
| Page returns 500 or blank screen   | Screenshot, file an issue, skip the page, continue with next area      |
| Login fails                        | Continue with all unauthenticated areas; document the limitation       |
| Form submission crashes            | Screenshot, file an issue, attempt the same action once more, move on  |
| Element not found / timeout        | Refresh page, retry once; if still failing, file issue and move on     |
| App becomes unresponsive           | Reload the page; if persistent, restart the browser and resume         |
| Unexpected modal or dialog blocks  | Dismiss or screenshot, file issue, continue                            |

Never retry the same failing action more than twice. File an issue and move on.

## Parallel sub-agent strategy

Copilot can launch parallel sub-agents (`runSubagent`) to speed up exploration and deliverable generation. Each sub-agent operates independently with its own browser session.

### Where to parallelize

| Phase                    | Parallel unit          | What each sub-agent does                                                    |
|--------------------------|------------------------|------------------------------------------------------------------------------|
| Module exploration       | 1 agent per module     | Opens own browser, authenticates, explores assigned module, writes issues, returns structured findings |
| Device testing           | 1 agent per viewport   | Opens browser at assigned viewport, navigates key screens, captures screenshots, files responsive issues |
| Test case generation     | 1 agent per module     | Receives exploration findings, writes test case files for its module         |

### What must stay sequential

* **Sitemap creation** — must happen first so modules can be assigned.
* **Master test plan and executive summary** — must happen last, after all module findings are collected.
* **Final consistency review** — must see all deliverables.

### Sub-agent prompt requirements

When launching a sub-agent, include in the prompt:

* The app URL and credentials
* The specific module or viewport to focus on
* The naming conventions and templates from this skill
* The output folder path for its deliverables
* Instruction to return a structured JSON or Markdown summary of: pages visited, issues filed (with IDs and paths), test case IDs drafted, and any areas it could not access

### Merging parallel results

After all parallel sub-agents return:

1. Collect all issue files and verify no duplicate IDs.
2. Collect all test case files and verify no duplicate IDs.
3. Build the master test plan from the union of all module findings.
4. Build the executive summary from coverage and issue counts.
5. Run the final consistency check.

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
* `MAIN_MODEL` (optional): model to use for the main orchestrator agent. Default: `claude-opus-4`. Override if a different model is preferred or available.
* `SUBAGENT_MODEL` (optional): model to use for parallel sub-agents. Default: `claude-sonnet-4`. Override to balance speed, cost, and capability.

Example invocation payload:

```text
APP_URL=https://your-app-url.example.com
TEST_USER_EMAIL=test.user@example.com
TEST_USER_PASSWORD=<secret>
TEST_NOTES=Use seeded tenant Acme Demo. Focus on sales, customers, inventory, settings. Skip billing if unavailable.
MAIN_MODEL=claude-opus-4
SUBAGENT_MODEL=claude-sonnet-4
```

## Model recommendations

The skill works best when the main orchestrator and parallel sub-agents use different model tiers.

| Role | Default model | Rationale |
|------|---------------|-------------------------------------------|
| Main orchestrator | `claude-opus-4.6-1m` | Strongest reasoning and synthesis for UX judgment, module prioritization, and aggregating findings across sub-agents |
| Parallel sub-agents | `gpt-sonnet-4` | Fast and capable at following structured instructions, Playwright interaction, and template-driven output; reduces wall-clock time and cost when spawning multiple agents |

**Why not use the top-tier model for everything?**

Sub-agents perform scoped, template-driven work (explore one module, test one viewport, write test cases from provided findings). They don't need deep strategic reasoning — they need speed and reliable instruction-following. Since 3–5 sub-agents run per parallel phase, using a faster/cheaper model multiplies savings without meaningfully reducing quality.

**Overriding**: Pass `MAIN_MODEL` and/or `SUBAGENT_MODEL` in the invocation payload to use different models. Acceptable alternatives include `gpt-5.4`, `claude-sonnet-4`, or any model available in the current environment. If the environment does not support per-agent model selection, all agents will use the session's active model — in that case, prefer the orchestrator-tier model.

Use the provided values only for test execution. Do not persist secrets into generated documentation unless the repo already has an approved secure pattern for test credentials.

If credentials are missing or login fails, continue with all accessible unauthenticated areas and document the limitation in the test plan.

## Suggested repo structure

```text
docs/
  testing/
    sitemap.md
    summary.md
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
