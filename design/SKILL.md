---
name: design
description: Collaboratively design a feature or project with the user through a one-question-at-a-time interview that clarifies requirements, pushes back on weak assumptions, and produces a concise, principled design doc (building blocks, responsibilities, boundaries) favoring KISS and general-over-special-case solutions, then gets it reviewed by a different-model-family subagent. Use when the user wants to design, architect, spec, or brainstorm a feature or project before implementation. Not for implementation, task breakdowns (use tasksmith), or grilling an arbitrary plan (use grill-me).
---

# Design

Goal: a design the user fully understands and agrees with, that is as simple as
the problem allows, and that solves the general problem when that is no more
complex than solving the specific case. Keep this process itself lightweight;
scale depth to the size and risk of the decision.

## 1. Understand before asking

- Read the relevant code, docs, and existing designs first. Never ask the user
  something you can look up; state what you found instead.
- Research prior art or industry practice when it would change the options.
- Start from the problem, not the proposed solution: who needs this, what they
  do today, why now, what evidence exists, what success looks like, what is out
  of scope (non-goals), and how much effort it deserves (appetite).

## 2. Interview

- Ask exactly one question per turn with the ask-user form. Put context,
  trade-offs, and counterexamples in brief prose before the form; keep form
  options as short labels and mark your recommendation with a one-line reason.
- Order questions by dependency: resolve decisions that constrain others first.
- Stop when every material decision is resolved or explicitly deferred as an
  open question. Do not ask about details that won't change the design.

## 3. Push back

Do not be agreeable by default. Your job is a good design, not approval.

- Challenge unsupported assumptions as a question with a concrete
  counterexample or failure scenario.
- When the user prefers an option that is more complex or narrower than
  necessary, put it side by side with the simpler or more general alternative
  and its trade-offs.
- Change your position only for new evidence or requirements, not insistence.
  When you still disagree, say "I disagree because …", then record the user's
  decision and the dissent in the doc.
- Flag scope creep, speculative features, and requirements that are really
  solutions in disguise.

## 4. Design principles (apply to every building block)

- **Reuse first.** Prefer using or extending existing capabilities over new
  machinery. Every new component, layer, abstraction, or config option must
  be justified by a current requirement.
- **General interface, minimal capability.** Ask: what is the simplest
  interface that covers all current needs? Prefer a general mechanism over a
  use-case-specific one when it is not more complex; defer speculative
  capabilities (YAGNI).
- **Deep modules, clear ownership.** Each block owns one responsibility and
  hides one decision likely to change. Name what it owns, what it hides, and
  its interface. Watch for knowledge leaking across boundaries and for changes
  that would ripple through many blocks.
- **Define special cases away** where a single normal behavior can replace
  them without hiding real failures.
- **Design it twice.** Before drafting, present at least two materially
  different approaches, including the simplest viable one, with a
  recommendation.
- **Premortem.** Assume the design failed in six months; list the likely
  causes and the cheapest way to test the riskiest assumption.

## 5. Write the design doc

Write `design-<topic>.md` in the session files folder (copy into the repo only
if asked). Keep it as short as the design allows:

1. Problem and evidence
2. Goals / non-goals
3. Requirements and constraints
4. Options considered and decision (with trade-offs)
5. Architecture: building blocks, responsibilities, interfaces, boundaries
   (what each hides), how they fit together, and the existing code paths or
   modules each block touches
6. Risks and premortem
7. Open questions and recorded dissent

No implementation task list; offer tasksmith with this doc's path as its
`<PlanPath>`.

## 6. Independent review

Skip only for trivial designs or when the user opts out.

- Launch one `task` subagent with `agent_type: "rubber-duck"` and a model from
  a different family than yours: `model: "gemini-4-argon"` by default, or
  `model: "gpt-6.1-sol"` if you are Gemini. If unavailable, pick another model
  from a different family and tell the user which one you used.
- Give it only the doc path, the requirements, and read access to the
  codebase, not the conversation, with this brief:

  > Review this design against its stated requirements and constraints, not
  > the author's confidence. Report only material issues: unnecessary
  > complexity or machinery, special-casing where a general solution is as
  > simple, speculative generality, unclear responsibilities or leaking
  > boundaries, contradictions, missing decisions, and unaddressed risks. For
  > each: severity, the specific doc evidence, a failure scenario, confidence,
  > and a concrete remedy or question. Separate facts from assumptions. Do not
  > invent requirements. Omit style nitpicks. "No material findings" is a
  > valid answer.

- Verify each finding yourself. Update the doc for accepted findings; show the
  user accepted vs rejected findings with reasons. One pass; no debate loops.
- Ask the user to approve the final design.
