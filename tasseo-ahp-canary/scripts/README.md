# Offline verification helpers

Python 3.9+ and its standard library are sufficient. No network, authentication,
packages, or Tasseo writes are performed. Run from any working directory:

```sh
python3 /path/to/tasseo-ahp-canary/scripts/verify_commit.py \
  --frames /path/to/complete-frame-observations.json \
  --receipts /path/to/complete-publication-observations.json

python3 /path/to/tasseo-ahp-canary/scripts/verify_snapshot.py \
  --baseline /path/to/baseline-report-read-block.json \
  --candidate /path/to/candidate-report-read-block.json
```

Supply complete native observation arrays or `{rows, nextCursor:null}`
exports to the commit checker. It refuses unfinished pages. Merge complete
pages explicitly into an array; do not remove a cursor from an incomplete page.
Native `series`/`values` records and already flattened rows are accepted.
Use `--bindings` when migrating the report; the default bindings resolve
relative to the installed skill, not the working directory.

The snapshot checker requires `report_read_block` envelopes with explicit
`published_result`, successful status, and its `data` view array. It compares
the same cycle, model verdicts, comparison tooltip facts, history
samples/quantiles/run IDs and median/whisker/line channels, and actual x/y
domains/types. It excludes technical observation UUID/hash differences
between current and dated views and deliberately does not assert pixel
geometry, color, overall plot count, or native HTML export success.

For an explicitly labelled authoring comparison, use `--view effective` to
read only the candidate's `result.payload`. Baselines are always published.
The output retains the view label; an effective pass is not publication proof.
If the live view contract changes, investigate and update the adapter/tests
instead of removing assertions to make a mismatch pass.

Run the synthetic regression suite from the skill directory:

```sh
python3 -m unittest discover -s tests -v
```

Fixtures are synthetic and contain no production report observations,
credentials, traces, proprietary renderer source, or screenshot values.
These tests verify the portable oracle, not the deployed TypeScript guard.
Separately validate the actual report through native MCP and inspect its
published artifacts before claiming the live pipeline fixed.
