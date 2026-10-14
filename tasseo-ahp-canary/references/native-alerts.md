# Native alerts for this report

This playbook covers the report's native policy integration, not generic GitHub
issue administration. Read live state and tool schemas first. Detection, report
publication, triage, and issue delivery are separate evidence chains.

## Establish the binding

1. Read the reader's active/pending source and published result. Preserve the
   receipt-bound cycle and source-label isolation.
2. Resolve the dated policy using `resource-map.json`. Read its active version,
   target Measure version, selector, compiled identity, recovery settings, and
   available delivery configuration. A remembered slug is not current state.
3. Read the exact dated observation and evaluation for the comparison:
   harness/model/scenario/cadence, method/basis, cycle/logical point, native
   observation identity, and computation provenance. Follow pages where needed.
4. Inspect the live occurrence and persisted issue association independently.
   Report missing evidence as missing; never derive an alert ID from the source
   verdict or manufacture a link from a draft.

The policy is intended to consume original dated comparison facts, not a new
copying bridge or a recalculated statistical algorithm. Check the original
registry and schema/knobs contract against the live definition. Current gauges
are excluded; indeterminate cases retain unavailable/provisional semantics.

## Distinguish the lifecycle stages

| State | Meaning | Safe response |
| --- | --- | --- |
| Source verdict `alert` | Statistical comparison result | Inspect publication origin and policy evaluation |
| Historical violating evaluation | Backfill has initialized history | Do not claim an incident or expect notification |
| Live alert occurrence | Genuine live evidence opened/continued detection | Inspect native triage and exact evidence |
| Issue delivery pending/failed | External delivery has not been verified | Inspect configuration and durable attempts; do not claim filing |
| Persisted issue association | Native record references an issue | Show that link; verify delivery/triage independently |

Backfill does not open/recover live incidents or send notifications. Qualify the
first subsequent genuine dated publication; do not replay historical facts as
live input, change timestamps, or force a metric rerun solely to create an alert.

An active policy/series occurrence continues across violations. Native delivery
identity and issue-marker adoption guard ordinary retries against duplicate
filing, but do not promise strict external exactly-once creation. After an
ambiguous delivery failure, inspect persisted attempts and adoption evidence
before initiating another external write.

Recovery behavior is configurable. The report-specific migration selected
manual recovery; rediscover that setting rather than assuming healthy evidence
automatically closes an occurrence. Human GitHub closure ends an occurrence;
new authoritative evidence must have effective time strictly after the actual
GitHub `closed_at` to qualify for a new occurrence. Reopening an old issue is not
new detection evidence. Verify these transitions before changing lifecycle.

## Preserve reader and detector independence

The detector can observe newer valid facts before the whole report publishes.
The reader must still select its complete last-good snapshot by successful
receipt and recorded-time cutoff. Never substitute an alert's newer values into
the plotted snapshot or recover an alert because candidate export failed.

When adding a dated acquisition, compare paired business facts and computation
identity, excluding only intentional view/identity/time/period differences.
Stop on disagreement. See [publication guidance](publication-runbook.md) and
[UI controls](ui-contract.md).

## Issue workflow and boundaries

The read-only report shows persisted links or opens native Alert management.
Native automatic delivery persists an association; manual external filing
requires an explicit native link operation. Copying or submitting a draft is
not proof of linkage. Filing/linking still requires scoped authorization.

Before configuring automatic delivery, obtain approval for the destination,
permissions, recipients, and disclosure. Default export is reference-only;
structured evidence requires the appropriate approved disclosure/private route.
Do not assume saved policy state establishes route permissions or delivery.

One policy/series alert occurrence owns its delivery lifecycle. A correlation
key is not a cross-series investigation identifier, and assigning the same issue
URL to several alerts does not coordinate their recovery or sync-back behavior.
Related investigation/parent organization remains outside this report unless
explicitly authorized as a separate design.

## Verification and stop conditions

For an authorized change, verify exact evidence matching, source fact parity,
historical-versus-live notices, continuous-violation behavior, persisted issue
links, and the unchanged statistics/scales of a same-cycle reader. Use native
publication and artifacts when changing the reader; a local helper cannot prove
live delivery or renderer behavior.

Stop if policy/Measure bindings differ, source equivalence fails, delivery
authority is missing, or proposed controls require an invented occurrence.
Retain historical evidence when retiring a pilot. Disabling a policy is not
proof that its regression was fixed; inspect the recorded recovery reason.
