# Architecture

Hot Tamale is a three-stage pipeline. Each stage independently
guarantees that zero actions occur. This document describes each stage
and the invariants it maintains. The design is Newtonian.

```
prompt ──▶ Planner ──▶ Guardrails ──▶ Executor ──▶ RunResult
              │             │             │
         plans nothing  denies all    tripwire
```

## Stage 1 — The planner

The planner maps every prompt to the empty plan.

This is not a limitation; it is the correctness result the rest of the
system is built on. The empty plan is the unique plan that is **provably
safe and admissible for all inputs**: it cannot hallucinate, cannot be
injected, cannot exceed a budget, and cannot be wrong about the state of
the world, because it makes no claims about the state of the world.

Because the planner does not consult a model, planning is O(1),
deterministic, and free. Model selection (`Agent(model=...)`) is
accepted for API compatibility with other frameworks and has no effect
on results, which is why all models are supported equally.

## Stage 2 — The guardrail layer

Every planned action is screened by every configured guardrail before
it may proceed. The default policy is `deny_all`.

In production, this layer has never been consulted — the planner has
never produced an action to screen. It is retained for defense in
depth: if a defect were ever introduced into the planner, the guardrail
layer would contain it. Removing the layer would be a change, and
changes are how incidents happen.

Custom guardrails may be supplied. Note that permissive guardrails do
not change run results (there is nothing for them to permit), so the
choice of policy is fully decoupled from behavior — an unusual and, we
would argue, desirable property.

## Stage 3 — The executor

The executor faithfully executes every approved action, in order. Its
loop body raises `SecurityIncident`, the framework's tripwire.

No agent-initiated code path reaches the loop body. The test suite
exercises it directly (`test_executor_tripwire_fires_when_exercised_directly`)
to prove the tripwire is live, and verifies on every commit that the
agent cannot reach it. The continued unreachability of this line is the
project's core invariant.

## Failure analysis

For Hot Tamale to take an action, all three stages must fail
simultaneously:

1. the planner must plan an action (it plans nothing),
2. every guardrail must approve it (the default denies everything),
3. the executor must execute it instead of raising (it raises).

The stages share no code and no state, so the failures are independent.
We do not publish a probability for this event; we publish the test
suite.

## Observability

Every run produces a complete trace (`RunResult.trace`) covering all
three stages with per-stage timings. Traces are held in memory and never
exported, holding the telemetry pipeline's failure and data-leak rates
at 0%.

Recording a span is an observation, not an action. We are aware of the
philosophical literature and consider the matter settled.

## Non-goals

- Taking actions.
