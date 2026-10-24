# Acceptance evidence contract

Use a compact run record, not a transcript. Keep browser secrets and private
source/data out of portable artifacts.

```json
{
  "revision": "<verified served source/build identity>",
  "environment": "local",
  "browser": "<name/version>",
  "viewport": {"width": 1440, "height": 960},
  "fixtures": [{"role": "owned unpublished draft", "revision": 1}],
  "criteria": [
    {
      "name": "failure -> clear -> successful retry",
      "status": "NOT TESTED",
      "method": "live UI",
      "evidence": [],
      "limitation": "pending execution"
    }
  ],
  "retainedResources": [],
  "cleanup": "pending"
}
```

Add resource URLs only where sharing them is authorized. The placeholders above
are a template, not evidence that any check was executed.

## Interpretation

- **PASS:** the stated criterion was actually exercised and the oracle held.
- **FAIL:** the stated observed behavior contradicted the requirement.
- **BLOCKED:** prerequisites or authority prevented exercising the criterion.
- **NOT TESTED:** the criterion was outside the performed run.

Identify `live UI`, `source inspection`, `automated regression`, and `simulated
network condition` separately. Do not combine them into an unqualified
"everything passed." For example, worker retry logs may corroborate a UI run,
but do not become a live worker-crash test.

Record intentional negative outcomes as expected results, not product bugs.
After a driver correction, preserve the original failure and explain why it was
not a valid product test. A passing test at an old revision is historical.

Review findings include:

- observed behavior and exact step;
- user consequence;
- evidence and confidence/limitations;
- smallest corrective recommendation;
- classification: introduced defect, existing issue, DX friction, optional
  polish, driver failure or unverified hypothesis.

Check chronological and aggregate consistency: each final PASS must have a
matching executed step, and run completion must not predate its checks. Report
rechecks and appended observations explicitly.

## Handoff

Lead with the user journey and outcome, then limitations. Distinguish local
acceptance from CI, reviewer approval, deployment qualification and merge
authorization. Never merge, publish, send feedback or resolve threads merely
because UI acceptance passed.

Retain test fixtures when deletion is not authorized. Leave a representative
successful result visible for the operator if requested, and explain any
intentional negative fixture separately.
