# Requirements interview and implementation plan

## Interview behavior

First read the operator's request and authorized source evidence. Separate facts,
operator decisions, assumptions, and unknowns. Do not ask questions answered by
the source or live capability inspection.

Offer quick, deep, or skip:

- **Quick:** resolve only choices that change architecture, analytical meaning,
  access, cost, publication, or operations.
- **Deep:** walk each relevant decision branch, including failure and correction
  behavior. Ask one decision at a time with viable options and a recommendation.
- **Skip:** produce a proposed plan with visible assumptions and blockers.
  Resolve blocking decisions before execution; still require plan approval.

Respect an explicit interview refusal or plan-only request. An unanswered
question is not approval of its default. Never make the operator choose
undocumented tool names or supply secrets.

## Decision branches

| Branch | Resolve with operator or source evidence |
| --- | --- |
| Purpose | Audience, decisions the report supports, essential views, success criteria |
| Task | New report, migration, or native extension; one-off, stable reader, or dated series |
| Environment | Local / Staging / Prod; Staging default; explicit connection and access confirmation |
| Local readiness | Running configured services, reachable local MCP, valid auth/organization; approved setup handoff if missing |
| Authority | Plan-only or implementation; allowed existing-resource edits; operator/admin prerequisites |
| Sources | Systems, targets, exact datasets/runs, schemas, availability, access, authorized read-only locations |
| Population | Dimensions/registry, inclusion/exclusion, duplicates, execution/member identity, grading context |
| Time | Event/execution/scheduled clock, timezone, interval boundaries, baseline windows, logical cycle, late arrivals |
| Metrics | Units, numerator/denominator, aggregation order, weights, quantiles, comparison method, uncertainty |
| Missingness | Unknown, missing, zero, failed, not applicable; minimum support and acceptable coverage |
| Evidence | Exact native trace drill-down versus aggregate/source lineage, retention, recalculation requirements |
| Historical load | Range, granularity, volume, raw/hybrid choices, correction rules, cost and operation bounds |
| Operations | Refresh cadence, delivery/destination, freshness objective, ownership, retries, alerts if needed |
| Migration | Source contract, parity inputs, tolerances, approved differences, coexistence/cutover/recovery |
| Presentation | Native visualization choices, controls, ordering, scale domains, accessibility, reader methodology |

For a brand-new report, define the analytical contract before choosing a chart.
Recommend reasonable options, but get confirmation of consequential metric and
population choices. The absence of a legacy source does not remove correctness
or operational acceptance criteria.

## Required plan

Write a compact durable plan in an operator-approved artifact location. Do not
commit private data or require a particular source repository/session path.
Use this structure; omit irrelevant sections explicitly rather than silently:

1. **Goal and scope:** task, audience, selected environment, allowed mutations,
   protected sources/resources, exclusions, access and ownership.
2. **Evidence baseline:** source versions, real schema/value examples, native
   resource revisions, pending edits, current publication if any, unknowns.
3. **Analytical contract:** population keys, windows/clock, metric formulas and
   units, weighting, grading context, support, missingness, uncertainty.
4. **Native design:** data flow and necessary report, template, Measure,
   Selection, source, automation, and optional Project/policy components.
   Explain why each exists; do not clone the Canary architecture by default.
5. **Mapping and differences:** direct/adapted/unsupported/unknown mappings and
   their evidence; approved differences and reader disclosure.
6. **Backfill and future intake:** selected approach, exact history range,
   partitioning, idempotency, lineage, producer authority/cutover if relevant,
   and handoff to incremental refresh.
7. **Capability/authority gates:** verified MCP operations and schemas, missing
   capabilities, human acceptance/admin steps, local prerequisites.
8. **Execution plan and budgets:** dependency order, permitted resource IDs or
   new resource roles, maximum runs/rows/bytes/time/operations as appropriate,
   estimated costs and uncertainty, bounded tests, stop/reapproval conditions.
9. **Acceptance and activation:** numerical tolerances and same-input parity
   tests, native renderer/provenance checks, publication evidence, delivery and
   schedule settings, partial-data policy, visible freshness/failure behavior.
10. **Recovery and handoff:** preserve last-good output, correction/retry
    behavior, recovery targets, helper cleanup, source coexistence, owner.

Approval must refer to an identifiable plan revision. If the operator approves
the complete bounded plan, proceed through its lifecycle without redundant
approval requests for each tool call. Ask again for scope, budget, audience,
methodology, environment, activation, or existing-resource changes outside it.
Do not interpret approval as permission to bypass a native authorization gate.

If cost cannot be reliably estimated, approve a small pilot budget first and use
measured volume to revise the plan before a large historical load. "Hybrid" is
not a cost estimate.

## Copyable mapping and differences tables

| Source responsibility | Native target | Class | Meaning preserved | Difference / gap | Evidence and acceptance test |
| --- | --- | --- | --- | --- | --- |
| Operator/source-defined step | Discovered native component | direct / adapted / unsupported / unknown | Explicit semantics | Operator-visible difference or blocker | Exact evidence locator and bounded test |

Direct means semantically equivalent, not just similarly named. Adapted means
the implementation changes while agreed analytical meaning remains intact.
Unsupported blocks execution of that dependency; unknown requires discovery.

| Difference | Kind | Analytical impact | Evidence / tolerance | Approval | Reader disclosure |
| --- | --- | --- | --- | --- | --- |
| Describe the actual change | presentation / capability / methodology / operational | None or explicit | Verified or unresolved | Plan revision / pending | Methodology, status, affected view, or not reader-relevant |

Do not bury changed denominator, cohort, clock, grading, or uncertainty rules in
a "presentation" row. Pure layout differences need not label every chart.

## Optional research

Use relevant primary documentation to inform options when technical evidence
is incomplete. Native deployed contracts outrank historical examples. Research
does not authorize sending private source code or data to external services.
Do not ask an operator to settle facts obtainable through bounded inspection.
