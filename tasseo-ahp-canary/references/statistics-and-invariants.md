# Statistics and invariants

These are the initial verified report contracts. Inspect the current Frame
definition and selection before altering calculations. This document is not
an alternate implementation of the original statistical algorithm.

## Cohorts

- Population: positive imported native execution output-token samples.
- Cohort timestamp: native `started_at` in explicit half-open UTC windows.
- Daily: current one day compared with the preceding 14 days.
- Weekly: seven days versus the prior seven, with the observed 3/3 then 1/1
  fallback behavior preserved where the live definition enables it.
- Daily/history use the selected richest run; baseline/weekly use pooled
  raw samples as defined by the live selection.
- The initial expected support was 60 per case/day, with 70% coverage gates
  and deterministic 5,000-bootstrap `canary-v5` comparison rules.
- Do not claim exact CES EventTime, grading, or main-only parity.

Null days stay unavailable; do not interpolate them or count them as zero.
History is 15 aggregate slots per model/scenario, not 690 independent native
daily observations or 690 raw-trace certificates.

## Integrity

The bound registry yields 23 x 2 x 2 = 92 comparison cells and
23 x 2 x 15 = 690 historical slots. Assert the exact key grid, not only a
count of 92 that could conceal duplicate/missing keys.

Each selected Frame must have valid native observation identity/hash,
correct harness/model/scenario/cadence/view/method, receipt cycle/logical
point, current storage address, nonnegative finite facts where required,
ordered confidence intervals, and consistent half-open windows.

For each history slot:

- `effective_at` is the declared date at UTC midnight;
- the date lies in the receipt's 15-day window;
- dates are distinct, with exactly the full calendar window;
- counts are nonnegative integers;
- zero support has null P25/median/P75/source run;
- positive support has positive finite ordered P25 <= median <= P75
  and a real source run ID.

Keep the existing complete validation in the actual renderer. The portable
commit checker independently checks commitment and grid membership only;
it does not replace the statistical or window validators.

## Time vocabulary

| Field | Meaning |
| --- | --- |
| `effective_at` at the current gauge | Persisted series address |
| `effective_at` at a dated cycle fact | Advancing cycle boundary used by native detection |
| `cycle_end` | End of the closed execution cohort |
| `computed_at` | Explicit logical caller/schedule point |
| Frame `recorded_at` | Actual persisted observation write time |
| Success receipt `recorded_at` | Commit cutoff for matching Frame revisions |
| Clock `checked_at` | Explicit logical freshness-check point |
| Clock `recorded_at` | Actual persisted check write time |

Never substitute one of these for another to satisfy a guard.

The policy consumes dated source facts without recomputing the comparison.
Check the bound registry, harness, scenarios, cadences, methodology, schema
and knobs contract against the live definition. Provisional, unusable, or
out-of-scope facts are indeterminate, not healthy and not violating. Preserve
the source distinction between `watch` and `alert`.

## Fail-closed behavior

No published receipt means no committed current snapshot.
An incomplete grid, ambiguous revision, mixed identity, or invalid quantiles
is an error. A legitimate previous committed cycle plus a later failed
refresh may render, but must display the failure and freshness warnings.

A recovery receipt is legitimate only after the corresponding native
candidate publication succeeds and its completeness/non-provisional gates
pass. Synthetic local test fixtures are never ingestion or publication input.
