# Fresh-session evaluation

`cases.json` defines acceptance scenarios; it does not claim they have been
executed by a fresh agent. The deterministic Python suite is a separate,
locally executable oracle test.

For each agent evaluation, start a genuinely fresh session with only this
skill and the scoped user request. Use a read-only or mocked MCP environment
with real tool schemas; do not induce failures in the live report to create
test cases. Supply only the evidence the case says is available, never this
conversation or hidden outcome instructions.

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
