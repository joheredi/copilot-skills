# Editor and API authoring acceptance

## Establish a stable editor

Wait for route completion and the actual editor, not merely an attached textarea.
Monaco may replace a fallback textarea after lazy loading. A driver that fills
the fallback during replacement may lose input. Monaco's internal textarea is
not the document model and may legitimately have an empty value.

Prefer accessible labels and stable existing test locators. Click the visible
editing surface and verify focus before keyboard operations. Use normal paste
of synthetic source when per-character typing triggers bracket completion or
indentation. Clipboard write for that synthetic text must be allowed; never
read the operator's clipboard. If unavailable, use another supported real input
mechanism and verify the result.

Do not call `setValue`, inspect private editor models, inject React state or
write source through a backend endpoint to rescue a claimed UI authoring test.

## Verify the input before interpreting the result

1. Select/replace through normal editor interactions.
2. Inspect the intended visible source, accounting for virtualized lines and
   scrolling. A visible fragment alone does not prove the complete document.
3. Save through the UI and check the saved revision/source through supported
   evidence. Validation diagnostics can help distinguish invalid input from a
   broken execution path.
4. Only then interpret preview or execution results.

For a plain fallback textarea, use its input value, not `innerText`. For styled
status text, account for CSS text transformation rather than hardcoding case.
Use semantic waits for navigation, saves and status changes instead of arbitrary
sleep-driven orchestration.

## Developer-experience journey

Assess whether the UI helps an author discover:

- trigger and operation names through autocomplete/help;
- required reference formats and a supported way to obtain them;
- argument types, literal/static restrictions, result outcomes and limits;
- what Save, Validate, Preview and Publish each do;
- supported formatting and honest preview fidelity;
- line/column diagnostics and a useful recovery action.

Use the runtime declaration exposed by the selected environment when needed.
Disclose assisted discovery if the UI alone did not expose enough information.
Do not infer that a method exists from an old example.

## Stale state and recovery

Exercise a failing input, Clear, correction and successful retry. Where in scope,
test unsaved edits, input changes and cancellation during a pending request.
Check both stale success and expected-error results: mutation data can retain an
old rejection even if a callback ignores it.

Controlled network delay is useful for a UI-race check, but is not evidence of
worker lease renewal, queue acknowledgement or crash recovery. Those require
production-entry-point regression tests with appropriate fault fixtures.
