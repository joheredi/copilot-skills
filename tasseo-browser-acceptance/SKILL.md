---
name: tasseo-browser-acceptance
description: >-
  Verify a scoped Tasseo user journey in a real browser with Playwright and
  assess developer experience using revision-bound acceptance evidence. Use
  for local UI acceptance, editor/API discoverability, preview/error recovery,
  and desktop or narrow-layout checks, including Windows Edge from WSL.
  Not for implementation, broad application exploration, deployment, provider
  sending, authentication bypass, or merge approval.
---

# Tasseo browser acceptance

Test what an operator can actually accomplish, not whether a page loads.
Separate observed behavior, source corroboration, driver failures and untested
requirements. Prefer the existing application and browser machinery.

## Read-only bootstrap

1. Establish the requested journey, target environment, permitted test-resource
   writes, protected resources, completion evidence and explicit exclusions.
   Infer Local only when the current request already selects it. Otherwise ask
   before accessing an environment. No publication or external effect is implied
   by a request to review UX.
2. Read the selected checkout's instructions and relevant current runtime,
   auth and testing docs. Verify repository, worktree, branch, head and dirty
   changes with explicit paths. A browser URL does not identify the served
   revision; check the serving process's checkout or equivalent build identity.
3. Probe app responsiveness and the worker needed by the journey. Inspect
   existing browser tools, schemas and test tooling before choosing a driver.
   An HTTP 200 does not prove worker readiness or authenticated access.
4. Discover topology: execution host, visible desktop, WSL/Windows boundary,
   browser executable, existing test-only connection and reachable app URL.
   Do not install a Linux GUI/browser stack before checking whether the user's
   Windows browser is the intended surface.
5. Read [browser setup](references/browser-setup.md) for Edge/WSL, dedicated
   profiles, authentication, tooling installation and safe process ownership.
   Use `tasseo-local-dev` for separately authorized startup or schema work.
   This skill does not itself authorize service or database reconfiguration.

Do not inspect authentication caches, export cookies/storage state, copy personal
browser profiles, fabricate sessions, weaken authorization or invoke a local
providerless login without an explicit separate request for that alternative.
Routine local authentication uses real GitHub OAuth.

## Bound the journey before interacting

Record a compact matrix using [the evidence contract](references/evidence.md).
Map each acceptance requirement to an actual UI action, expected observation
and evidence locator. Include at least:

- a normal end-to-end path;
- one meaningful failure and recovery to success;
- pending/dirty/cancelled state where relevant;
- primary action availability, data/result identity and truthful completion;
- one representative desktop and narrow viewport when layout is in scope.

Use the approved spec for behavior, current source for implementation context,
and the live UI for observations. Source can explain an outcome but cannot
substitute for exercising it. Do not silently expand into a site-wide audit.
The separate `ux-test-plan` skill covers broad test-plan exploration; this skill
covers a bounded acceptance run and an evidence-backed UX/DX assessment.

Name destructive, publishing, notification, provider and setup actions that must
not be clicked. Do not test a protective fence by taking a prohibited action.
For example, inspect disabled Publish state without clicking Publish.

## Execute through the real UI

1. Open an owned tab in a dedicated, operator-approved test browser/context.
   Preserve existing tabs and the operator's current page. Authenticate through
   the normal flow; ask promptly if a visible browser sign-in is required.
2. Use only authorized test resources. Create uniquely named unpublished drafts
   when permitted; record their identifiers and revisions. Do not repurpose or
   delete existing resources. Backend/MCP fixture preparation requires its own
   applicable authority and must be labeled as such.
3. Exercise discovery and authoring as a developer: navigation, visible help,
   API autocomplete, required identifiers, parameter/outcome guidance, save,
   validation and the primary action. For code editors, follow
   [editor interaction](references/editor-interaction.md).
4. Verify the resulting saved source/revision before interpreting execution
   failures. A test that accidentally kept a starter template or typed malformed
   code has not demonstrated a product execution defect.
5. Verify meaningful result content, source identity, timestamps and caveats.
   A success badge, empty list or screenshot alone is not the acceptance oracle.
   Distinguish admission, preparation, publication, delivery and provider receipt.
6. Exercise the recovery path: invalid input -> useful diagnostic -> clear or
   correction -> valid retry. Test delayed response behavior where authorized;
   if network delay is simulated, disclose it and do not claim a real worker
   crash or production fault was injected.
7. Check content hierarchy, duplicate warnings, actionable errors, loading and
   cancellation, identifier discoverability, keyboard focus and narrow layout.
   Observe accessible names/states; DOM checks are not screen-reader testing.

Do not inject application state, call editor model setters or use direct APIs
to bypass authoring while calling the result UI acceptance. A backend-prepared
fixture can support a separate preview-only test, not a full authoring claim.

## Diagnose a failure before retrying

Classify the failure:

| Evidence | Next discriminating check |
| --- | --- |
| Browser unseen or unauthenticated | Check desktop/host topology and test context; request normal sign-in |
| Saved source differs from intended input | Check hydration, focus, selection, paste and persisted revision |
| Expected diagnostic becomes generic | Inspect actual RPC status/result shape without auth headers or cookies |
| Preview never completes | Check worker/job identity, timeout and application logs within approved scope |
| Helper tests pass but production fails | Trace the actual queue/request entry point and settlement ownership |
| Layout assertion fails on capitalization | Compare visible presentation with accessible text; fix the oracle, not app behavior |

Each retry needs a changed input, driver fix, or evidence-based hypothesis.
Keep the failed artifact and explain the correction. Stop on authentication,
authority, protected-resource conflict or unexplained revision drift; never
turn an incomplete run into PASS. Avoid accumulating many near-identical drafts:
reuse only an owned test resource when its current state is verified.

## Evidence and handoff

Save artifacts outside tracked source unless the operator requests otherwise.
Capture application screens only; exclude sign-in screens, cookies, tokens,
private payload dumps and full unredacted network traces. Record the actual
served revision, browser/version, viewport, fixture revision, actions, observed
results, expected failures and test limitations.

Use **PASS / FAIL / BLOCKED / NOT TESTED** per criterion. Separate UI observations
from automated regression corroboration. List bugs, DX friction, optional polish
and driver limitations separately. "No blockers observed in this scoped run" is
not "no bugs remain" or full production/security qualification.

Finish on a successful representative result, not the intentionally failing
negative fixture. Preserve evidence for both. Leave services or a test browser
running only when needed and authorized for operator use; stop bounded helpers
and only processes this run owns. Do not close the operator's personal browser.
Report retained resources and cleanup limitations.

## Package validation and evaluation

Run `python3 -m unittest discover -s tests` from this skill directory to validate
frontmatter, package references and offline case definitions. This needs PyYAML
and does not launch a browser or prove task effectiveness.

See [evaluation cases](references/evaluation.md) for sanitized fresh-session
checks. Executing browser tests, publishing code, operating live environments
and posting review findings each require their own applicable authorization.
