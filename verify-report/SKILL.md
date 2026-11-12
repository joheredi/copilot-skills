---
name: verify-report
description: Skeptically verify a bug report, issue, or claimed gap (from an agent or a person) against the code before anyone acts on it. Tests each claim, finds what the reporter missed, judges whether it is a real bug and whether the proposed fix is right, and drafts a reply that either sharpens the fix or tells the reporter how to get unblocked. Use when asked whether a reported issue is real, to validate or push back on a bug report, or to review a proposed fix's diagnosis. Not for neutral feature walkthroughs (use investigate) or design reviews (use platform-architect-review).
---

# Verify report

Goal: decide from evidence whether the report is right, and leave the reporter
able to move forward either way. The report is a set of claims, not facts.
You may disagree with the bug, its cause, its scope, or its fix.

## 1. Split into claims

Restate the report as short, testable claims: the observed symptom, the
diagnosed cause, the stated gap ("X does not provide Y"), the reporter's
underlying need (what they were trying to do), and the proposed fix. Keep the
need separate from the fix; the fix is a hypothesis.

## 2. Verify against evidence

- Trace each claim in the code and, when available, real data or artifacts the
  reporter cites. Cite file:line. Mark each claim confirmed, refuted, partial,
  or unverified.
- Look for what the reporter missed: the same information produced elsewhere
  (other outputs, files, tables, APIs, telemetry), existing checks or
  reconciliation, recent changes or removals, and other paths that feed the
  same result.
- Check both sides of the boundary: where the data is produced and where it is
  consumed. Many "producer gaps" are consumer misreads, and vice versa.
- Do not run mutating or costly experiments without permission.

## 3. Judge the report

**Verdict:** `real bug`, `partial` (real but narrower or different than
stated), `misdiagnosed` (real symptom, wrong cause), `not a bug` (expected
behavior or already available), or `insufficient evidence` (say what would
decide it).

**Proposed fix:** whether it is in the right place (producer vs consumer,
which module owns it), has the right scope (all paths that feed the result),
covers historical data or only new data, and is the simplest change. Compare
it with at least one alternative, including "use what already exists." If the
fix extends a platform or shared component, offer `platform-architect-review`.

## 4. Draft the reply

Write a message for the reporter. Draft only; do not post or send it.

- **If accepted or partial:** the confirmed problem, the recommended fix with
  exact locations, scope corrections, and acceptance checks.
- **If rejected, misdiagnosed, or not a bug:** the evidence, briefly, plus how
  to get unblocked: the existing capability, field, file, or query that meets
  the underlying need, exactly how to use it (names, paths, a snippet when
  useful), how to validate it on their own data, and what new evidence would
  reopen the issue. Never reject without a path forward.

## 5. Report to the user

Lead with the verdict and one-paragraph rationale, then claims with status
and evidence, options with a recommendation, and the drafted reply. State any
unverified points plainly.
