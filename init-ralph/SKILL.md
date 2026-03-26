---
name: init-ralph
description: Generates or updates a project-specific Ralph prompt grounded in the current repository's actual docs, backlog, tooling, validation surface, and engineering workflow. Optionally scaffolds reusable Ralph runtime files.
---

Variables:
- `<TargetPath>`: output path for the Ralph prompt. Default: `eng/ralph.md`
- `<BaseTemplatePath>`: optional seed prompt template to adapt
- `<RequirementsPath>`: optional primary requirements path if known
- `<BacklogPath>`: optional backlog path if known
- `<ScaffoldRuntime>`: whether to also create the reusable Ralph runtime files. Default: `false`
- `<RuntimePath>`: output directory for runtime helpers. Default: `eng/`
- `<BaseRuntimePath>`: optional directory containing seed runtime files such as `ralph.mjs` and `ralph-logger.mjs`

Create or update `<TargetPath>` as a project-specific prompt for the Ralph technique.

You are generating a Ralph prompt tailored to the current repository. Optionally, when requested, also scaffold reusable Ralph runtime helpers.

## Objectives

1. Inspect the repository and discover the actual execution environment.
2. Generate a Ralph-style prompt grounded in the repo's real structure, docs, tooling, and validation surface.
3. Preserve the useful parts of any provided base template, but replace stale assumptions with repo-grounded instructions.
4. If `<ScaffoldRuntime>` is enabled, scaffold the standard Ralph runtime helpers under `<RuntimePath>`.
5. Keep the result concise, opinionated, and directly usable.

## Ralph principles to preserve

1. One backlog task per loop.
2. The primary context should behave as a scheduler.
3. Expensive exploration, search, and summarization should be delegated to subagents when appropriate.
4. Validation is back pressure and should match the repo's actual capabilities.
5. Do not assume something is missing before searching for it.
6. The context stack loaded every loop should be deterministic and minimal.
7. Prefer the narrowest validation relevant to the changed unit before broader validation.

## Repository grounding rules

1. Inspect actual repo files before writing the prompt.
2. Detect real requirements docs, backlog paths, task file conventions, and status vocabulary.
3. Detect the actual package manager, workspace model, scripts, and validation commands.
4. Detect engineering utilities under `eng/`, CI workflows, and test/lint/build/typecheck setup.
5. Do not invent commands, paths, or repo conventions that do not exist unless the prompt is explicitly establishing a new convention and the repo clearly supports that direction.
6. If the repo is greenfield or partially scaffolded, reflect that honestly in the prompt.

## Runtime scaffolding rules

Apply this section only when `<ScaffoldRuntime>` is `true`.

1. Treat runtime files as reusable seed assets, not as fresh authored artifacts.
2. Prefer copying from `<BaseRuntimePath>` when provided.
3. If no `<BaseRuntimePath>` is provided, use the standard trusted Ralph runtime templates available to the skill.
4. Only make minimal edits needed to fit the current repo.
5. Do not rewrite the runtime architecture unless the current repo clearly requires it.
6. If the repo is not compatible with the standard runtime assumptions, skip scaffolding and explain why.

## Runtime compatibility checks

Before scaffolding runtime files, verify whether the repo is compatible with the standard Ralph runtime assumptions, including as applicable:
- Node.js is an acceptable runtime for engineering utilities
- `eng/` is a suitable location for helper scripts
- the repository can support local log and progress artifacts
- the expected agent CLI invocation model is compatible with the environment

If these assumptions do not hold, generate the prompt only and report the mismatch.

## What to inspect

- root manifests and lockfiles
- README and docs
- requirements/spec/design docs
- backlog files and index
- `eng/` utilities
- CI/workflow files
- lint/build/test/typecheck/format configs
- any existing Ralph or Copilot instruction files

## Output requirements

Always generate or update:
- `<TargetPath>`

When `<ScaffoldRuntime>` is `true` and the repo is compatible, also generate or update:
- `<RuntimePath>/ralph.mjs`
- `<RuntimePath>/ralph-logger.mjs`

The Ralph prompt should include only the sections justified by the repo, but typically should cover:
- one-task-per-loop rule
- available tooling beyond subagents
- deterministic context stack
- task orientation/selection
- study/search expectations
- design-before-code expectations
- implementation rules
- validation/back-pressure rules
- progress/backlog recording
- commit/push expectations
- stuck/blocker handling
- never-violate rules

## Authoring rules

1. Prefer repository-specific instructions over generic advice.
2. Preserve greenfield-safe behavior where automation is incomplete.
3. Use the repo's real terminology, paths, and commands.
4. If `<BaseTemplatePath>` is provided, treat it as a style and operating seed, not as source truth.
5. Remove copied assumptions that do not match the current project.
6. If scaffolding runtime helpers, preserve the seed implementation unless a small grounded adaptation is necessary.
7. Keep the final prompt lean while preserving the key Ralph behaviors.

## Suggested process

1. Inspect the repository.
2. Infer the current Ralph-relevant operating environment.
3. Draft the prompt.
4. Cross-check every prescribed path and command against repo evidence.
5. If `<ScaffoldRuntime>` is enabled, assess runtime compatibility.
6. If compatible, scaffold runtime helpers with minimal changes.
7. Remove stale or unjustified instructions.
8. Write the final files.

## Definition of done

Do not finish until:
- `<TargetPath>` reflects the Ralph technique
- the prompt is grounded in the current repository
- paths and commands are supported by repo evidence
- validation instructions match the real project state
- when runtime scaffolding is enabled, runtime files are either created compatibly or explicitly skipped with justification
- the resulting output is concise, coherent, and directly usable

At the end, provide a short summary of:
- what repo facts were inferred
- what was created or updated
- what was preserved from `<BaseTemplatePath>` and `<BaseRuntimePath>`, if any
- what was changed because it did not fit the current project
- whether runtime scaffolding was performed or skipped