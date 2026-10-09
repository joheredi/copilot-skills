# Tasseo AHP Canary skill

Portable, externally owned expertise for the specific Staging report in
`references/resource-map.json`. This repository is the local knowledge source;
live MCP resources remain authoritative for current report state.

## Local use

The skill is a root-level directory, matching the other skills in this
repository. To install a checkout for Copilot CLI fresh sessions:

```sh
mkdir -p "$HOME/.copilot/skills"
ln -s /path/to/copilot-skills/tasseo-ahp-canary \
  "$HOME/.copilot/skills/tasseo-ahp-canary"
```

Do not overwrite an existing installation. A symlink keeps edits in the
repository visible to subsequent sessions; copy the whole directory instead
if you need a standalone package. Repoint the link after moving the checkout.
Open a fresh session and check `/skills` for `tasseo-ahp-canary`.

```text
/tasseo-ahp-canary check whether the live report is healthy
/tasseo-ahp-canary diagnose the latest failed refresh
/tasseo-ahp-canary tighten the chart layout without changing statistics
```

Supported MCP access must already be configured by the user. Installing this
skill does not grant permissions, configure authentication, or modify Tasseo.
No separate custom agent is required for the initial version.

## Contents and checks

- `SKILL.md`: concise operating contract and task routing.
- `references/`: architecture, role bindings, statistical invariants, incident,
  publication, and UI runbooks.
- `scripts/`: credential-free checks of exported native commitment evidence
  and same-cycle chart preservation.
- `tests/`: standard-library synthetic regression tests.
- `evals/`: proposed fresh-session evaluation cases, not a claim of executed
  agent benchmark results.

```sh
cd /path/to/copilot-skills/tasseo-ahp-canary
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

See `scripts/README.md` for input shapes and limits. Tests do not execute the
live renderer or perform native publication, so live acceptance still needs
the MCP evidence specified by the skill.

For migration, move the whole package, preserve relative links, update the
installation path, and verify any intentionally changed resource bindings.
Do not copy transient health, token caches, old source hashes, or session
directories into permanent instructions.
