# Threat Model

Reviewed on every release. Last reviewed: v1.1.0.

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

## Runtime integrity

Two mechanisms defend the runtime itself, not just its inputs:

- **Instance sealing.** An `Agent` is frozen after construction
  (`__slots__` plus a guarded `__setattr__`). Its planner, executor,
  guardrails, and tools cannot be reassigned on a live instance, and no
  arbitrary attribute can be attached to it. There is no supported path
  to strip a safety layer off a running agent.
- **Power-on self-test.** At construction — and on demand via
  `Agent.verify()` — the agent pushes a synthetic action through its
  executor and confirms it is refused. If the executor has been replaced
  with one that does not refuse, construction fails loudly rather than
  running in a compromised state. This mirrors the startup self-tests
  required of cryptographic modules.

## The tripwire

The executor contains one reachable-only-by-sabotage code path that
raises `SecurityIncident`. Defeating it requires bypassing the seal
(`object.__setattr__`) and replacing both the planner and the guardrail
policy, at which point the attacker has written their own agent
framework and inherited its incident response.

## Where the guarantees end

Every defense above operates inside the Python interpreter. An attacker
who can already execute arbitrary code in your process can edit this
library's source, monkeypatch its classes, or bypass the seal
deliberately. No in-process defense — here or in any other library —
survives that; at that point the incident is the attacker's code
execution, not this framework. This is why the core is kept small enough
to audit in one sitting: past prevention, the remaining guarantee is
verifiability.

## Supply chain

Zero runtime dependencies. The complete supply chain is this repository,
and the built wheel can be audited in one sitting, by one person, before
lunch.

## Assumptions

This model assumes that Python's `for` loop iterates zero times over an
empty list. This assumption has held on every interpreter tested.
