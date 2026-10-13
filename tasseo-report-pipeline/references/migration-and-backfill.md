# Migration equivalence and cost-aware backfill

## Establish the source contract

Inspect authorized source definitions and a reproducible output baseline, not
only screenshots. Capture exact input identities, source revisions, cohort
selection, interval endpoints, timezone/clock, metric units, aggregation order,
weights, missing-data rules, uncertainty method, and support thresholds.

Separate source defects from intended semantics. Do not silently "correct" a
legacy formula during migration; propose and approve that methodological change.
For new reports, use the operator-approved analytical contract as the oracle.

Map source responsibilities to native components using the
[plan tables](requirements-and-plan.md). Native layouts and pipeline boundaries
may differ substantially. Direct parity is about meaning, not copied code.

## Numerical equivalence

Choose a frozen or otherwise consistently pinned source cohort for both paths.
Capture the actual observations/run-member contexts used by the native result.
Do not compare a live source refresh with an older native cohort and call it drift.

Before running acceptance checks, agree on per-metric tolerances:

- Absolute and relative tolerance with explicit units and near-zero behavior.
  A common proposed rule is `abs(native - source) <= abs_tol + rel_tol * abs(source)`;
  the operator must approve the rule and its thresholds for the metric.
- Exact comparison for identity sets, count/support facts, and categorical
  statuses unless an explicitly approved contract says otherwise.
- Null/missing/undefined versus zero, infinity, and invalid values handled
  explicitly; never allow coercion to create a passing numerical comparison.
- Method-specific stochastic reproducibility: estimator, quantile convention,
  confidence level, seeds or documented variability, and approved test criteria.
  Overlapping confidence intervals alone are not an equivalence test.

Test intermediate quantities as well as headlines: numerator, denominator,
weights/support, per-cell facts, comparison baseline, history, quantiles,
uncertainty endpoints, missingness, and rendered domains. A headline mean can
agree while the cohort or comparison is wrong.

Keep three results separate:

| Result | Meaning |
| --- | --- |
| Analytical parity | Approved population, clock, method, missingness and uncertainty semantics preserved |
| Numerical parity | Same-input outputs satisfy declared tolerances |
| Presentation adaptation | Native UI expresses those facts differently, transparently |

Methodological exceptions require explicit plan approval and durable disclosure;
numeric tolerances do not authorize changing an estimator or denominator.
Insufficient evidence permits an authorized exploratory draft, not verified
migration or operational cutover.

## Pick a historical strategy

Compare applicable choices rather than treating raw intake as mandatory:

| Strategy | Benefits | Required checks / limitations |
| --- | --- | --- |
| Native raw/run import | Recalculation, member context, exact drill-down | Authorized availability, volume/budgets, retention, completeness, native source parity |
| Existing native facts | Avoid duplicate intake/calculation | Population/schema/version/producer equivalence, retained provenance, required revisions |
| Verified external aggregates | Avoid unnecessary historical raw ingestion | Sufficient statistics, lineage, approved reduced drill-down, active definition/grant/authority, supported publication with a named executor |
| Hybrid | Aggregate history plus native incremental future data | Explicit handoff boundary, common semantic contract, overlap validation, correction/authority rules |

Choose the least expensive strategy that satisfies the contract, not simply
the fewest bytes. Include source-query and parity-validation costs in estimates.
Measure a pilot before approving a large uncertain load.

## Aggregate eligibility

For every planned aggregate, answer:

1. What population/window and exact computation does it represent?
2. Is it a final fact to display, or will a downstream calculation combine it?
3. Which sufficient quantities are retained: counts, sums, denominators,
   weights, distribution information, covariance/pairing, uncertainty inputs?
4. Can it reproduce the approved downstream outputs and corrections?
5. What source IDs, versions, hashes, dependency/lineage and audit evidence exist?
6. Who publishes: the agent through MCP, or an operator-owned external job?
   Is that executor's publication/producer-authority path supported and verified?

Do not average averages without the appropriate support/weights. Do not average
medians, P25/P75, P95, confidence bounds, or ratios to reconstruct pooled facts.
An exact precomputed quantile for one fixed approved cohort can be a reusable
final fact, but does not establish that arbitrary regrouping is possible.
Sampling or sketches require an approved accuracy/methodological contract.

Reject reuse when source clock, grading context, cohort, grouping level, support,
or correction lineage cannot be established. Do not add fake trace source sets
to make an external aggregate appear natively drillable.

## Backfill execution gates

- A one-off external producer job is a valid historical backfill mechanism,
  separate from native future intake and calculation. Missing MCP publication
  need not block preparation or that operator-owned execution path. Preserve
  the MCP-only boundary for agent-authored Tasseo writes; do not hide a direct
  endpoint call inside a script or automation to bypass it.
- Confirm the historical range, granularity, approved partitions, and total
  volume/time/operation budgets. Keep effective time distinct from import time.
- Match active Definition/series/value schemas, producer grant/version,
  authoritative periods, and approved visibility. Do not mix incomparable
  producer heads by relying on an automatic fallback.
- Publish candidate/shadow facts and compare them before an authorized authority
  cutover where supported. Registration/grant/authority changes remain distinct
  from publishing the observations.
- Use the supported publisher's deterministic idempotency for each batch;
  persist receipts, range,
  counts and hashes. Retry the same logical submission after uncertainty;
  inspect it before using a fresh key. A correction uses native supersession,
  not deletion or rewriting immutable history.
- Inspect completed outcomes, per-item failures, observed coverage and limits.
  Partial success cannot satisfy the full planned batch by omission.
- Validate the history/future handoff: boundaries, overlapping periods,
  population coverage, compatible versions, producer authority, and late data.
  Avoid double counting or a gap at the cutover.
- Stop the affected publication on exhausted budget, unexpected schema or
  population differences, unverified authority, or no supported path for its
  executor. Missing MCP capability blocks agent-direct publication; evaluate
  an operator-owned external job before calling the backfill itself blocked.
  Continue independent approved preparation; obtain revised approval when the
  executor, scope or analytical/evidence contract changes.

## Reader and operator disclosure

Specify required evidence access separately for compact history and native
future data. Approved limited historical drill-down does not require full raw
imports. A verified report-to-observation-to-source-traces path may satisfy an
evidence contract without direct chart-cell selection; distinguish its whole
input population from metric-specific contributors. If exact cell contributors
are required, keep that gate until verified or explicitly revised.

Keep an operator-facing mapping/differences record and concise native report
methodology. Expose consequential differences: clock/window, coverage,
uncertainty, historical granularity, missingness, drill-down limits, freshness
and failed attempts. Preserve units and statistical meanings in tooltips,
labels, scales and whiskers. Formatting affects displayed text, not data.
