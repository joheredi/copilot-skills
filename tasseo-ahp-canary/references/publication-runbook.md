# Authoring, promotion, and publication

## Before writes

Read the report's effective structure and source, real observations, and
deployed runtime. Respect foreign pending changes. Prefer `report_edit update`
to wholesale replacement. Save baseline source/hash and operation IDs outside
tracked source when needed; re-read before any later recovery write.

Ordinary report DATA edits were observed to require canonical acquisition
statements whose arguments are JSON literals, one statement per line:

```ts
await measures.addSeries({"measure":"slug","from":"UTC instant","to":"UTC instant","revision":"all"});
```

This is a shape example, not executable source to paste unchanged.
Unquoted JavaScript object keys are not JSON. The host may canonicalize
whitespace/newlines, so compare semantics or its normalized source hash.

The parameterized template DATA block can use invocation parameters to
declare its windows. Source discovery is declaration-only: do not read
observation rows in DATA to decide a later acquisition. Such reads may work
at computation time yet fail planning/pinned-manifest checks. Put committed
revision selection in a subsequent CODE block over declared sources.

## Current and dated sources; policy reads

Declare current-gauge and dated-cycle Frame acquisitions separately, using
their bound source labels. Scope current selection to its own acquisition
before applying the receipt cutoff. Scope policy matching to dated facts.
Adding the dated source must not double the current reader's candidate rows.

Before changing the acquisition contract, compare paired current/dated facts:
all business values must agree, as must their native computation run and
producer/definition identity. Exclude only intentional technical differences
such as view kind, observation identity/hash, effective time, and period.
If equivalence fails, stop and diagnose; do not strip differing business fields
or choose whichever revision makes the UI pass.

Observed authoring constraint: ordinary DATA discovery accepted canonical
JSON-literal `measures.addSeries` declarations but rejected policy acquisition
statements. The working report declares metric sources in DATA and uses
supported policy helpers in CODE, with separate durable run-scoped snapshots.
CODE is not permission to add undeclared metric sources; `addSeries` there
was guarded. Inspect deployed contracts before choosing this path, and prefer
a supported DATA acquisition if the platform subsequently provides one.

Match policy evidence by exact series, cycle/logical point, and native evidence
identity rather than nearest date or model name alone. Metric reads and policy
reads have separate snapshot boundaries: re-read after state changes, preserve
historical/no-live-incident notices, and distinguish newer native evidence from
the last-good plotted cycle. See [native alerts](native-alerts.md).

## Changes to the reader

1. Validate the effective DATA and CODE proposal against actual native rows.
2. Check the original identity, windows, coverage, quantiles, status semantics,
   contributor behavior, and reader-facing intended data.
3. Obtain acceptance. No supported acceptance tool was available in the
   initial deployment; re-discover capabilities rather than assuming one
   still does or does not exist.
4. Read back active source and zero pending edits.
5. When export/publication is in scope, complete native `report.run` and verify
   the reader plus its non-provisional immutable HTML artifact and caveats.

`report_compute` can validate an effective pending preview, but must not be
described as acceptance or proof of successful native export.

## Templates and pins

- Read `template_get`, complete paged source where required, and its
  optimistic concurrency timestamp before `template_replace`.
- Template draft writes are immediate and separate from the live reader.
  Editing the template does not update an existing instantiated report.
- `template_publish` is guarded testing plus promotion of the exact revision.
- The chosen immutable sample must match invocation parameters and its source
  manifest. A pending reader using `revision:"all"` may not match the older
  active sample's effective-only manifest. Use a genuinely matching sample;
  do not bypass the manifest guard.
- After promotion, validate/publish affected automations to capture their
  template pins. Verify unchanged cron/time zone, state, and unrelated source.
- Inspect the actual response fields; authoring objects, promotion responses,
  and template metadata need not use the same casing.

## Candidate and receipt gates

The daily path must check complete intake before Frame calculation. Publish
the actual candidate, reject provisional output/caveats, then record its
genuine successful receipt with real view/download/artifact evidence.

The observed Measure-only candidate does not need a fresh ingestion override
in `report.run`; completeness remains explicitly verified upstream. Read the
deployed automation contract before adapting that finding elsewhere.

Record failures separately. Preserve public failure outcome details when an
SDK omits a message, and do not convert missing details into success.

## Verification evidence

For same-cycle UI/source-preserving changes, compare the reader-facing result
to a same-cycle native baseline. Use the snapshot checker on exported MCP
responses. Compare business fields, mark channels, actual domains, and status
badges. Observation UUID/hash differences between dated and current views
may be explicitly excluded, but statistics must not be excluded.

For next-cycle changes, validate against that cycle's archived native candidate,
not the previous day's values. Never hardcode a screenshot's values.

Final state must explicitly identify:

- accepted saved source;
- successful native reader publication and artifact;
- target successful receipt/cycle/logical point and committed Frames;
- intended template revision and automation pins;
- active operational schedules and any current warnings.

If any step is blocked, stop claiming completion and state what evidence is
missing. Publication permission is not deletion permission or production
deployment permission.
