# Tasseo browser acceptance

A bounded, UI-first acceptance and developer-experience workflow. It complements
`tasseo-local-dev` (startup/auth/schema) and `subagent-pr-workflow` (delivery and
review ownership) without inheriting their operational authority.

Use:

> Use tasseo-browser-acceptance to verify the local editor-to-preview journey in
> my dedicated Edge test browser. Create only your own unpublished test draft.
> Exercise an error and successful recovery, check narrow layout, and report
> evidence for the served revision. Do not publish or send anything.

The package includes Windows/WSL browser guidance, editor-driver failure
discrimination, evidence rules and sanitized offline evaluation cases. It does
not ship a stale application-specific renderer, hardcoded machine paths,
credentials, captured sessions or a generic browser automation framework.

## Install

Use the host's supported personal-skill mechanism and expose this whole directory,
not just `SKILL.md`. For a host using `~/.copilot/skills`, a symlink to a stable
checkout can be used where supported. Inspect an existing destination first;
never overwrite an unrelated directory or link.

Re-read current host documentation for discovery/reload behavior. Copilot CLI
supports `copilot skill list --json` for discovery. In an existing interactive
session, use `/skills reload` then `/skills info tasseo-browser-acceptance`.
Do not install only a single `SKILL.md` through a file/URL command and omit the
referenced assets. Installation and successful package parsing do not prove
that the current running session has discovered or loaded the skill.

## Validate

With Python 3 and PyYAML available, from this directory:

```sh
python3 -m unittest discover -s tests
```

The checks parse real YAML, validate relative references and evaluation-case
structure, and reject example paths bound to an individual machine. They do not
run a browser or certify acceptance. Fresh-session evaluation instructions are
in [references/evaluation.md](references/evaluation.md).

No live-system evaluation is authorized merely by installing this package.
