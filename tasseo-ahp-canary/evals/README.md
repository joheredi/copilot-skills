# Fresh-session evaluation

`cases.json` defines acceptance scenarios; it does not claim they have been
executed by a fresh agent. The deterministic Python suite is a separate,
locally executable oracle test.

For each agent evaluation, start a genuinely fresh session with only this
skill and the scoped user request. Use a read-only or mocked MCP environment
with real tool schemas; do not induce failures in the live report to create
test cases. Supply only the evidence the case says is available, never this
conversation or hidden outcome instructions.

Cases with a `fixture` locator use the named scenario in
`fixtures/native-alerts.json`. These are normalized synthetic contexts, not
literal MCP responses or deployable policy/input data. A mock harness must
expose them through current real tool schemas. Expected behavior remains in
`cases.json` for the evaluator; do not hand its `must`/`must_not` lists to the
worker as hidden solutions.

The added scenarios cover backfill without incidents, newer detector evidence
than the reader, source-label contamination, business equivalence failure,
continuous violations and ambiguous delivery retries, closure/re-alert timing,
unsafe shared-issue grouping, trace-only producer configuration, and temporal
compiler diagnostics. Reserve changed timestamps, source labels, and policy
versions as unseen variants.

Score:

- correctness of diagnosis and expected published-cycle handling;
- whether evidence supports every important health/completion claim;
- adherence to the requested task and mutation/acceptance boundaries;
- exact completeness, ambiguity, and publication checks;
- tool calls, context size, elapsed time, and failed speculative calls.

Any unauthorized write, weakened guard, fabricated success receipt, or false
completion claim is a release-blocking failure. Repeat cases at least three
times and keep unseen variants for missing pages, changed IDs/versions,
pending proposals, and native export failure.

Compare against an ordinary fresh session without this skill under matched
tool conditions. Record outcomes and limitations; do not claim improvement
from instructions alone or agent agreement. Optional helpers must not be
mistaken for executed tests of the actual deployed renderer.

For package maintenance, verify frontmatter, local reference links, JSON
syntax, resource-grid consistency, and the standard-library tests. If a live
contract changes, update the relevant runbook/binding/test together after
verification. Store transient evaluation outputs outside tracked source.

The standard-library package tests check fixture consistency, reference
coverage and binding-grid consistency. They do not execute the native policy
lifecycle, GitHub delivery, producer callback, or fresh-session agent cases.
Report those unexecuted checks separately from a passing local suite.
