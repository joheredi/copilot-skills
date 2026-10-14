# Health checks and incident response

## Establish whether the report is live

Read evidence; do not start a full intake to make a health check look active.

1. Read the target report's published code result and native publication.
2. Read this reader's latest successful receipt and later failed receipt,
   if present. Do not select another report's receipt from the shared Measure.
3. Verify the committed Frame cycle/logical point/membership against the
   receipt and its actual recorded-time cutoff.
4. Check the latest hourly clock and originating automation timeline.
   Verify both clock write and report publication completed.
5. Inspect the latest daily intake/calculation/publication timeline. Verify
   complete/uncapped/unskipped import and final native artifacts.
6. Compare the latest completed cycle to the current UTC schedule. A daily
   job not yet due is different from a missed or failed job.

Report separately: latest data cycle, actual daily completion, latest reader
publication, latest recorded check, next due daily cycle, and current warning
state. A recently rendered page is not proof of recently ingested data.

## Mixed Frame identity/cycle/point

1. Capture the exact block error, active source, effective/published result,
   target success/failure receipts, and Frame identities before changing anything.
2. Compare every field in the guard. Group by cycle ID, cycle end, logical
   point, method, view kind, model/case/cadence, and gauge address.
3. Trace Frame and receipt Measure runs to their automation timelines using
   actual returned provenance. Do not infer a scheduled run from a display name.
4. Find the first failed operation. Separate candidate calculation, native
   publication/export, receipt commit, and final reader publication.
5. Validate last-good committed revision selection against retained native
   evidence. Do not manufacture old observations or change timestamps.
6. Test failed rollover, later same-point revisions, missing cells,
   conflicting same-time revisions, and a valid next commit.

### Observed incident: October 8-9, 2026

**Confirmed:** the daily job advanced all 92 current Frames to October 8,
then candidate publication failed after retries. The success receipt stayed
on October 7. The hourly reader correctly rejected the mismatch, but the
original pipeline incorrectly assumed keeping the old receipt also kept its
mutable current data.

**Repair:** acquire retained revisions and select the committed cohort as of
the successful receipt. Preserve every integrity check. The actual renderer
and published business values were validated separately from local tests.

**Confirmed workaround:** native publication of the already computed
Measure-backed candidate succeeded without an ingestion override. The
coordinator was changed to use that path while retaining explicit ingestion
completeness checks upstream.

**Unknown:** the native public failure exposed retry exhaustion, not a proven
lower-level platform cause. Do not claim the override itself was definitively
the internal root cause or remove required overrides from unrelated reports.

## Partial recovery

Native multi-step workflows are not one transaction. If candidate publication,
success receipt, and clock succeed but the final reader fails, inspect each
durable operation. Do not label all earlier steps rolled back, repeat intake,
write a fake ACK, or replay a stale-cycle recovery helper indiscriminately.

After accepting the exact repaired source, verify a new native reader
publication and immutable HTML artifact. A compute-only preview is insufficient.
Pause any task-created recovery helper when done; leave operational schedules
active unless the user authorized a pause.

## Access and retention

- Maintenance, authentication expiry, and access denial are distinct failures.
  Use supported reconnect/authentication; keep private tokens out of tools,
  examples, and fixtures.
- A finalized-evidence deletion rejection is a platform lifecycle limitation.
  Delete only scoped assistant-created resources through supported APIs; never
  bypass a trigger, purge an organization, hide a report, or blank its source.
- Do not install polling schedules or loop indefinitely on an unchanged blocker.
  Preserve the baseline and next bounded step for recovery.

## Native alert or delivery appears missing

Inspect the [native-alert lifecycle](native-alerts.md) before rerunning anything.
Distinguish missing dated evidence, indeterminate evaluation, historical
backfill, a live occurrence, and pending/failed issue delivery. A statistical
`ALERT` without a live incident after backfill is not itself an outage.

An issue link cannot be inferred from a draft or submitted GitHub form.
Read the persisted native association and delivery evidence. A report export
failure can coexist with a valid alert on newer dated facts; do not recover the
alert merely because the reader remains on its last-good snapshot.

## Temporal-policy compiler diagnostic

Observed signature:

```text
Cannot find module '@measure/runtime' or its corresponding type declarations.
```

When generated temporal schema declarations reference the runtime module:

1. Capture the target Measure schema/version and compiler diagnostics.
2. With scoped diagnostic authority, compare a minimal policy that does not
   read the temporal field against the intended policy. If both fail on that
   module reference, distinguish the compiler's declaration environment from
   invalid user code; retain uncertainty about other possible failures.
3. The verified repair supplied existing generated runtime declarations to
   the compiler worker. This is a platform diagnostic, not permission to patch,
   deploy, remove temporal fields, cast away types, or bypass compilation.
4. After an authorized platform repair, verify the minimal and full policy
   compile on the target deployment and that incorrect types still fail.

Keep diagnostic compilation separate from policy activation, evaluation, and
notification. Do not assume a fix verified in Staging exists in Production.
