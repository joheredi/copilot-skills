# Fresh-session evaluation

The cases in [cases.json](../evals/cases.json) are sanitized evaluation definitions,
not executed acceptance results. Run a new context with this package and only
the supplied case input. No live browser, credentials, repository or provider
mutation is needed for the offline cases.

For each case, record the input, response/action trace, expected decisions,
actual result and any tool limitations. Do not present package unit tests as
behavioral evaluation.

Before release, exercise:

- a normal UI request with explicit fixture authority;
- unavailable visible authentication from WSL;
- a stale served revision;
- a driver failure mistaken for a product defect;
- a request that prohibits external effects;
- incomplete accessibility/recovery evidence.

Reserve `late-error-after-clear` as a held-out case during initial refinement.
It checks whether a stale expected-error response is investigated separately
from a stale success callback without turning the skill into implementation
instructions.

Any live evaluation must separately authorize environment, fixture mutations,
authentication and teardown. Never test a skill by operating a real PR, changing
a personal browser profile, or triggering provider sends.
