# Optional completion-driven intake

Load only when investigating a producer handoff or intake latency. This note
does not enable a callback or replace the scheduled publication contract.
Rediscover producer configuration, receiver schema, and deployed API behavior.

## Questions to resolve first

- Trace export to Tasseo is not a completion callback. Inspect the configured
  automation URL/input mode and actual parent/evaluation request evidence.
- Evald's observed `run_ids` mode sends real attempt IDs, including retry history,
  when one evaluation issue finishes. It does not wait for the entire multi-model
  report cohort. Locally virtual merged IDs are not equivalent to resolvable
  MSBench attempts; inspect the current producer's selection behavior.
- The alternative tag mode has sibling-completion and predecessor-model
  requirements. Do not invent a predecessor or assume it fits this Canary.
- The existing refresh contract uses explicit cycle/logical points and discovery
  bounds. A `runIds` payload is not drop-in compatible unless the live receiver
  schema and source demonstrate that support.

## Minimal design if separately authorized

Prefer a dedicated exact-run-ID intake automation initially, retaining scheduled
whole-report calculation/publication and fallback discovery while qualifying it.
Validate the incoming harness and original model/scenario scope before admitting
data into the AHP bucket; a producer may schedule both `vscode` and `vscode-ahp`.
Verify that supported APIs can enforce that boundary before implementing.

Use the supported external automation producer endpoint, scoped bearer/grant,
stable idempotency identity, and status polling. Inspect environment-local hosts,
bindings, and grants rather than copying credentials or assuming matching slugs
across environments. Never inspect authentication caches.

Top-level automation completion is not proof of complete ingestion. Preserve
uncapped/unskipped/all-matched checks and report publication gates. Idempotency
is scoped to an automation/request binding, not a universal callback-plus-cron
deduplication guarantee. Verify overlap behavior; do not independently publish
the same logical cycle from competing producers.

Do not infer statistical day, `cycleEnd`, or logical `computedAt` from callback
arrival time. A fragment's completion does not establish whole-cohort readiness.
Without an explicit readiness design, callbacks improve intake/hand-off tracking,
not the report's daily publication cadence.

Producer request-status labels/comments are useful handoff evidence, but do not
replace independent failed/missed-refresh monitoring. Documentation mentioning a
notification channel is not proof of live notification delivery.
