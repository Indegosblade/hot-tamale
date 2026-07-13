# Threat Model

Reviewed on every release. Last reviewed: v1.0.1.

**Scope:** the Hot Tamale runtime (planner, guardrail layer, executor),
its public API, and its supply chain.
**Out of scope:** actions, which do not occur.

## STRIDE analysis

| Threat | Vector | Mitigation | Residual risk |
|---|---|---|---|
| **S**poofing | An attacker impersonates the CEO, the operator, or the safety team | Identity is never consulted. All callers receive identical service (none). | None |
| **T**ampering | An attacker modifies a planned action in flight | There are no planned actions in flight. | None |
| **R**epudiation | An operator denies that the agent performed an action | We support this claim. Every trace confirms it. | None |
| **I**nformation disclosure | The agent leaks prompt data to a model provider | No provider is contacted. Prompts terminate in the planner, unread. | None |
| **D**enial of service | An attacker floods the agent with requests | Measured throughput exceeds 100,000 runs/s on laptop hardware, and the service has no downstream dependents to protect. | Low |
| **E**levation of privilege | An attacker acquires the agent's privileges | The agent has no privileges. The attacker ends the engagement with exactly what they started with. | None |

## The tripwire

The executor contains one reachable-only-by-sabotage code path that
raises `SecurityIncident`. Defeating it requires replacing both the
planner and the guardrail policy, at which point the attacker has
written their own agent framework and inherited its incident response.

## Supply chain

Zero runtime dependencies. The complete supply chain is this repository,
and the built wheel can be audited in one sitting, by one person, before
lunch.

## Assumptions

This model assumes that Python's `for` loop iterates zero times over an
empty list. This assumption has held on every interpreter tested.
