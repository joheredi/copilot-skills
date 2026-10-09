# Architecture and source of truth

## Scope and evidence

This package describes one native Tasseo Staging report. The initial bindings
were verified during the October 7-9, 2026 implementation and repair.
Everything described as **observed** is a historical baseline, not a health
claim about a later session. Live MCP definitions and observations win over
this document. Versions and source hashes must be read afresh.

The original Canary implementation can be consulted in a user-provided
read-only `vscode-copilot-evaluation` checkout. No reference checkout is
required for health checks, and its Git state must not be changed.

## Observed native pipeline

1. **Intake:** bounded Corp MSBench discovery for
   `agent:vscode-ahp tag:experiment-id=canary`, imported into the bound bucket.
   The operational daily path used a two-day overlap and explicit complete,
   uncapped, unskipped import checks.
2. **Frames:** native calculation creates daily/weekly comparisons for the
   original 23 models and two scenarios. Each Frame contains comparison facts
   and genuine 15-day history aggregates.
3. **Candidate:** instantiate the promoted template in `mode:"cycle"` with
   explicit `cycleEnd`, `computedAt`, and model registry. Cycle-mode reads
   dated Frame observations.
4. **Candidate publication:** native `report.run` must complete and produce
   non-provisional output without caveats and an immutable HTML artifact.
   Computation alone does not satisfy this gate.
5. **Commit:** write a genuine successful publication-status observation only
   after that publication. Failures use a separate `report_id + ":failure"`
   series and do not supersede the successful pointer.
6. **Clock and reader:** update the operational clock and publish the stable
   live reader. The hourly watchdog changes the clock and reader publication
   only; it does not ingest data or recalculate statistical cohorts.

Daily scheduling is 20:30 UTC. Hourly freshness runs at minute 15 UTC.
The API coordinator is on-demand. Verify all three states and actual
timelines in a fresh session; names and descriptions may contain stale prose.

## Committed reader identity

The fixed current gauge address is `2026-10-07T00:00:00.000Z`, with a
one-millisecond read window. It is a storage identity, **not** the current
cycle, execution day, or report publication time.

The repaired reader acquires retained current-Frame revisions (`revision:
"all"`). It selects the latest revision per model/scenario/cadence matching:

- the successful receipt's `active_cycle`;
- the successful receipt's `cycle_end`;
- the successful receipt's logical `computed_at`;
- a Frame `recorded_at` at or before the receipt's actual `recorded_at`.

It requires exactly the full cell grid, rejects conflicting same-time
revisions, and applies the original identity/window/quantile validation.
Do not treat all acquired ledger rows as displayed Frames: the reader selects
92 committed observations from a potentially larger retained ledger.

The success and failure series must be scoped to this reader. Other report
experiments share Measures; their receipts cannot choose this report's cycle.

## Read surfaces

- `report_read`: effective structure and data-source declarations; active and
  pending blocks are distinguishable.
- `report_read_block`: full source and effective authoring cache; explicitly
  request reader-facing `published_result`.
- Effective cached output uses `result.payload`; published output uses
  `published_result.data`. Inspect the actual response, not assumed aliases.
- Observation-query results retain `series`, `values`, recorded/effective
  times, IDs, hashes, producer, and computation run.
- Automation timelines establish which operation completed and which
  failed. A Measure's native trigger label alone may not identify the
  originating scheduled automation.

Read deployed schemas before calling any of these. CamelCase versus
snake_case fields differ between native records and tool envelopes.

## Authority and limits

This skill owns knowledge, not platform privileges. MCP source edits and
template promotion do not automatically accept ordinary report proposals.
Native evidence retention may prevent deletion; bypassing it is not an
acceptable cleanup strategy.

**Unresolved scalability concern:** all-revision gauge reads grow as revisions
accumulate. Measure actual row/byte budgets and available supported snapshot
APIs before changing the mechanism. Do not truncate the first query page or
discard the committed revision to save memory.
