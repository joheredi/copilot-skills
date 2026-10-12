# MSBench adapter

Use this branch for evaluation data, not as a universal reporting schema.
Discover the selected environment's import/read tools and runtime contracts.
Corp and AME are distinct source targets; never infer authorization or tested
parity for one from a successful operation against the other.

## Intake choices

- Exact native imports can select raw or supported completed merged RunIds.
  IDs are strings. A destination bucket can be optional for exact imports.
  Keep sources within one supported target; reject unsupported cross-target
  merges rather than expanding the selection.
- Query/scheduled native discovery is a bounded raw-run path, requires its
  bucket under the observed contract, and is not merged-run discovery.
  Imported-run listing is not an upstream discovery query.
- Read the supported typed query language and native limits. Arbitrary KQL
  is not part of the automation runtime. An approved read-only external query
  may establish source evidence, but does not become a native import operation.
- API-input automations can receive explicitly typed run sets where supported.
  Producer tags/notifications identify a proposed intake, not trusted metric
  values, source authorization, or evidence that imports have completed.

Starting an import yields a job, not a completed dataset. Track the original
idempotency key and inspect terminal state, successful/failed roots,
completeness and result coverage before downstream use.

## Preserve the selected-run population

An imported run contains member occurrences and their result contexts. Repeated
members or distinct selected runs sharing an execution are not necessarily
duplicates. Physical trace count and selected-member count are different.

| Identity / context | Preserve |
| --- | --- |
| Member `row_id` | One selected occurrence; use for member-specific rows and comparisons |
| Physical `id` / `trace_id` | Execution evidence, steps, attachments; may contribute through multiple members |
| Raw member results | Physical execution's source outcomes/grading |
| Uniquely attributable merged results | Merged selection's member outcome/grading, not a fallback to source grades |
| Ambiguous repeated-task results | Use only the supported attributed context; never multiply task-level results across attempts |
| Unavailable member | Explicit reason/support/missingness; not a fabricated zero or discarded denominator |

Do not deduplicate analytical rows by physical trace ID unless the source
contract explicitly requires execution-level deduplication. A bucket of traces
does not preserve merged selection membership and grading.

## Report acquisition

Run-based trace acquisitions and physical bucket/trace/query acquisitions are
not interchangeable. Under the observed contract they cannot be mixed in the
same report's trace-like source scope. Measure acquisitions use their separate
namespace. Inspect the current acquisition rules before authoring.

Adding an MSBench run as a report source reads an already imported selection;
it does not import from upstream. Normal row, count, aggregate, and grading
APIs then use member context. Steps/attachments still describe physical
executions. Test actual denominator and grading behavior, not only trace count.

## Completeness and version evidence

Check physical source accounting separately from numerical/grading coverage.
Completed intake can still have partial or uncharacterized coverage. Unknown
expected assessment count is not zero missing assessments. A failed multi-run
job must not be presented as the whole requested set having completed.

Capture declared source metadata, selected members, native input revisions and
report provisional/caveat state. Saved report output does not automatically
change after a source refresh; a new run captures inputs again. A later source
refresh can differ from the triggering ingestion, so inspect actual captured
report coverage and hashes.

For parity, use the operator's source grading and time definitions. Do not claim
CES event-time, branch filtering, scheduled-window, retry-winner, or grading
parity merely because ingestion succeeded.

## Incremental operations

Inspect native checkpoint/backlog behavior, lookback bounds, cursor key/version
and query-change policy. Published source changes need not reset a stream.
Do not switch to full snapshot ingestion on every refresh to avoid understanding
cursors. Bound any overlap needed for late data and verify it cannot duplicate
analytical contributions.

When exact-run deliveries target an installed Project, preserve its approved
cycle key, effective time, fixed configuration and population rules. Completed
intake/attachment is not a numerical publication; use native cycle status/wait
evidence where available. Project installation gaps remain operator/admin
prerequisites, not permission to run a setup script through this reporting skill.
