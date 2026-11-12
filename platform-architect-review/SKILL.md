---
name: platform-architect-review
description: Independent platform-architect review of a design, proposal, or PR in any codebase. A different-model-family subagent checks fit with the existing architecture and patterns, maintainability, special-case fixes masquerading as platform features, and over-engineering, then returns implement, simplify, or do-not-implement with code-cited findings. Use when asked for an architect, platform, or architecture review of a design or change. Not for line-level code review, security review, or designing from scratch (use design).
---

# Platform architect review

Goal: an honest, evidence-based judgment on whether a proposed change makes
the platform better, from a reviewer with no stake in the proposal. One pass.

## 1. Frame the review

Identify, from context or by asking once:

- **Subject:** a design doc path, PR (repo + number), diff, or written
  proposal.
- **Motivating use case** and stated requirements, if known.
- **Repository root** the subject belongs to.

Do not pass the conversation or argue the proposal's merits to the reviewer;
it must form its own view.

## 2. Launch the reviewer

Launch one `task` subagent, `agent_type: "rubber-duck"`, with a model from a
different family than yours: `model: "gpt-6.1-sol"` by default, or
`model: "gemini-4-argon"` if you are GPT. If unavailable, pick another
different-family model and tell the user which one you used. Honor any model
the user names.

Give it the subject locator, the motivating use case, the repository root,
and this brief:

> You are the platform architect for this codebase. Review the proposal for
> what it does to the platform over the long term, not only whether it works
> for the motivating case. Judge against requirements and evidence, not the
> author's confidence.
>
> First learn the platform from the repository: read agent/contributor
> instructions and architecture docs, then find two or three existing
> features most similar to the proposal and note how they are built (where
> they live, extension points, naming, builder/config patterns, data flow,
> ownership boundaries). Cite file:line for every pattern you rely on.
>
> Then assess, reporting only material issues:
> 1. **Platform drift:** new constructs, layers, or conventions where an
>    established pattern or extension point already fits.
> 2. **Special case vs. general capability:** does this enhance the platform
>    for a class of users, or encode one use case into the platform? Could the
>    use case be served by existing capabilities or a smaller general
>    mechanism?
> 3. **Over-engineering:** speculative options, extra abstractions, multiple
>    variants where one would do, configuration nobody needs yet. Name what to
>    delete.
> 4. **Boundaries and maintainability:** responsibility leaks, duplicated
>    knowledge, changes likely to ripple, and migration, compatibility, or
>    operating costs the proposal ignores.
> 5. **Gaps:** contradictions, missing decisions, unaddressed risks.
>
> Return:
> - **Verdict:** `implement`, `simplify then implement`, `do not implement`,
>   or `insufficient evidence`, with a two-sentence rationale. Recommend not
>   implementing when the change is a platform fix for one use case and an
>   existing capability or general alternative would serve.
> - **Simplest acceptable shape:** the smallest change that meets the real
>   requirement, if different from the proposal.
> - **Findings:** for each, severity (blocking/major/minor), evidence with
>   file:line, failure scenario, confidence, and a concrete remedy.
>
> Separate facts from assumptions. Do not invent requirements. Omit style
> nitpicks. "No material findings" with verdict `implement` is valid.

## 3. Verify and report

- Check each finding and cited pattern against the code yourself. Mark it
  accepted, rejected (with reason), or unverified.
- Report the verdict, simplest acceptable shape, and findings by disposition.
  If you disagree with the verdict, say so and why.
- Do not edit the design, code, or PR, or post comments, unless asked. No
  debate loops with the reviewer.
