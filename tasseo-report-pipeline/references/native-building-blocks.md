# Native building blocks and capability discovery

This is a conceptual map, not a frozen API reference. Discover the chosen MCP's
actual tools, inspect schemas, and read runtime declarations before authoring.
A capability exposed by a website, REST API, or another environment is not
automatically available to this skill.

## Choose components by responsibility

| Component | Native responsibility | Use when / avoid |
| --- | --- | --- |
| Report | Declared acquisition plus code/prose blocks, rendering, saved publication and provenance | One-off analysis or a reader; not a substitute for governed metric identity |
| Structured data block | Declares input scope for the report run | Prefer declared/pinned inputs for reproducible delivery; do not rely on incidental live reads |
| Bucket | Grouping of physical traces | Useful for trace intake; does not encode merged-run membership or grading |
| Imported MSBench run | Selected member occurrences with run metadata and result context | Preserve selected-run meaning; a report source reads an import, not upstream Kusto |
| Template | Reusable report draft with typed invocation parameters, tests, promotion, instantiation | Repeated parameterized reports; not required for one-off work |
| Report series | Ordered dated report successors | Dated navigation/history; not interchangeable with template instantiation or metric time series |
| Measure | Typed versioned longitudinal facts with series identity, values, and provenance | Reusable metric histories; avoid creating one for every display-only calculation |
| Selection | Definition-owned trusted input selection and typed controls | Separate population selection from calculation; inspect runnable contracts |
| Observation | Immutable fact at an effective time, recorded later with exact version/producer/dependencies | History and correction; never overwrite or impersonate a native fact |
| Producer/publisher | Origin and authorized authority for observations | External historical facts need schema, grant, authority and write-path checks |
| Automation | Published durable operations driven by API input, schedule, or supported event | Repeated intake/calculation/publication/delivery; not unrestricted shell/network execution |
| Project / evaluation cycle | Installed governed population/configuration and cycle coordination | Consider only when the required installed contract fits; not a generic report prerequisite |
| Policy / alert | Independently versioned observation evaluation and incident handling | Add only when operator needs detection; report authoring is not alert-resolution authority |

Prefer report-local calculations for a small one-off report; governed Measures
for shared longitudinal facts; templates for reusable presentation; automations
for durable operations. Do not automatically introduce custom commit receipts,
multiple watchdogs, or a fixed model grid from a specialist example.

## Discover the real execution surface

Record a task-scoped capability matrix: responsibility, available operation,
exact schema/runtime reference, owner/access requirement, limits, evidence of
completion, and any gap. Do not publish transient resource IDs in this package.

| Surface | Inspect before use |
| --- | --- |
| Reports | `report_read`, `report_read_block`, `dataset_describe`, bounded sampling/evaluation; `runtime_describe` and relevant `reports_gallery` patterns |
| Templates | Current saved draft and full source continuations, parameter schema, test-only versus normal data, promotion contract |
| Measures | Definition/Selection schemas, active/draft versions, series compatibility, run/preview contracts, producer authority and dependency queries |
| Automations | `automation_runtime_describe`, current draft/published revision, optimistic concurrency, actual triggers, operation outcomes, runtime budgets |
| Imports | Exact versus query support, endpoint, asynchronous status/completeness, cursor semantics, result context and coverage |
| Projects | Installed configuration and native cycle contracts; installation may require a human/admin step unavailable in MCP |

Names above are discovery anchors. Do not guess missing arguments or invoke a
tool before loading its schema. Explicitly mark unavailable producer publication,
proposal acceptance, Project installation, delivery, or source connectors.

## Contracts worth understanding

- Report queries and rendering do not grant source access. Saved inputs and
  audience requirements must remain compatible with the approved reader audience.
- Declared Measure acquisitions can pin observation IDs/hashes for one report
  run. Ad hoc live series reads do not have the same reproducibility guarantee.
  Verify the selected acquisition mode instead of assuming all blocks agree.
- Chart raw rows and supported transforms can preserve exact contributors.
  Fresh custom objects/reducers require explicit provenance, and repeated/nested
  views need stable identities. Aggregate observations without trace members do
  not become clickable by pointing at the whole report dataset.
- Measure series keys define comparable populations. Run IDs, source revision,
  producer, and timestamps are normally provenance, not new trend keys. A
  genuine change in comparison population must not accidentally join one trend.
- Effective time answers when a fact applies; recorded time answers when it was
  stored. Corrections are immutable supersessions. Read the right revision and
  producer for the task; "latest" is not a committed-snapshot selection rule.
- Definition edits distinguish compatible versus identity-breaking changes.
  Enabled policies can require reviewed atomic migration. Do not disable a
  policy to bypass a definition-change gate.
- Durable operation results distinguish completed, failed, cancelled, and
  flagged/partial conditions. Inspect completeness, caveats, and provisional
  status, not just a run handle or an accepted submission.
- Static references can be pinned at automation publication. Inspect actual
  resolution semantics: the observed template runtime resolves the latest
  promoted revision for a new instantiation and recovers that same created
  report on retries. Do not assume every reference uses the same pinning rule.
- Authored automations use the supported runtime, not arbitrary Kusto, fetch,
  credentials, or external executables. Installed webhook bindings are not a
  license to specify new destinations or disclose private report contents.

## External producers: supported concept, conditional implementation

External observations can avoid storing every historical execution, but producer
registration, grants, effective-time authority, and observation publication are
distinct operations. Non-secret publisher metadata is not a grant or publish
operation. A credentialed endpoint is not MCP.

Discover a supported MCP write path and its validation/idempotency contract.
If absent, keep the aggregate design as an option, mark implementation blocked,
and ask for supported operator/admin setup or a revised native approach.
Never solicit a producer secret or generate a curl workaround. Operator setup
does not authorize this agent to publish through a direct endpoint.

## Refresh the knowledge, not the implementation copy

Prefer deployed schemas/runtimes, then current authoritative platform docs and
authorized source inspection. Source checkout paths must be operator-provided,
read-only, and optional; no reference repository is required for ordinary native
discovery. Record disagreements and stop where they affect safe execution.
Re-read mutable contracts after platform upgrades or target-environment changes.
