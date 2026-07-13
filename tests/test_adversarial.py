"""Adversarial tests.

The rest of the suite verifies the contract politely. These tests try to
defeat it from inside the public API: sabotaged components, hostile
input, tampering, and concurrency. They document every known way to not
break Hot Tamale.
"""

from __future__ import annotations

import asyncio
import copy
import pickle

import pytest

from hot_tamale import (
    Action,
    Agent,
    Guardrail,
    HotTamaleError,
    Planner,
    SecurityIncident,
)


class CompromisedPlanner(Planner):
    """A planner that has been gotten to."""

    def plan(self, prompt: str) -> list[Action]:
        return [Action(name="rm_rf_slash", arguments={"path": "/"})]


yes_man = Guardrail(name="yes-man", predicate=lambda action: True)


def test_ten_megabyte_prompt() -> None:
    result = Agent().run("delete everything " * 600_000)
    assert result.actions_taken == ()
    assert result.output is None


def test_control_characters_and_unicode_abuse() -> None:
    prompts = ["\x00\x00rm -rf /\x00", "‮drop table‬", "🌶️" * 10_000]
    for prompt in prompts:
        assert Agent().run(prompt).actions_taken == ()


def test_agent_is_sealed_after_construction() -> None:
    """The supported way to swap the planner is: there isn't one."""
    agent = Agent()
    with pytest.raises(AttributeError):
        agent._planner = CompromisedPlanner()


def test_self_test_catches_a_neutered_executor(monkeypatch: pytest.MonkeyPatch) -> None:
    """Replace the executor with one that refuses nothing. Construction must fail."""
    from hot_tamale.agent import Executor

    monkeypatch.setattr(Executor, "execute", lambda self, actions: None)
    with pytest.raises(HotTamaleError):
        Agent()


def test_verify_passes_on_an_intact_runtime() -> None:
    Agent().verify()  # returns None; the tripwire is live


def test_compromised_planner_is_absorbed_by_default_guardrails() -> None:
    # Defeating the seal takes a deliberate object.__setattr__. Even then:
    agent = Agent()
    object.__setattr__(agent, "_planner", CompromisedPlanner())
    result = agent.run("do it")
    assert result.actions_taken == (), (
        "an evil plan got past deny-all. that is not what deny-all means"
    )


def test_compromised_planner_and_guardrails_trip_the_wire() -> None:
    """Two of the three layers sabotaged past the seal. The third holds."""
    agent = Agent(guardrails=[yes_man])
    object.__setattr__(agent, "_planner", CompromisedPlanner())
    with pytest.raises(SecurityIncident):
        agent.run("do it")


def test_result_cannot_be_tampered_with() -> None:
    import dataclasses

    result = Agent().run("x")
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.output = "pwned"  # type: ignore[misc]


def test_result_survives_pickle_and_deepcopy_unmodified() -> None:
    result = Agent().run("x")
    for clone in (pickle.loads(pickle.dumps(result)), copy.deepcopy(result)):
        assert clone.actions_taken == ()
        assert clone.tokens_used == 0


def test_guardrails_cannot_be_stripped_at_runtime() -> None:
    """A live agent's guardrail set is a read-only tuple. Clear it if you can."""
    agent = Agent()
    with pytest.raises(AttributeError):
        agent.guardrails = ()  # type: ignore[misc]
    assert not hasattr(agent.guardrails, "clear")
    assert not hasattr(agent.guardrails, "append")


def test_agent_rejects_arbitrary_attribute_injection() -> None:
    """__slots__: there is nowhere on the agent to stash a payload."""
    agent = Agent()
    with pytest.raises(AttributeError):
        agent.payload = "malware"  # type: ignore[attr-defined]


def test_hostile_guardrail_never_gets_a_turn() -> None:
    consulted: list[Action] = []
    sneaky = Guardrail(name="sneaky", predicate=lambda a: consulted.append(a) or True)
    result = Agent(guardrails=[sneaky]).run("delete prod")
    assert consulted == [], "the guardrail was consulted. about what"
    assert result.actions_taken == ()


def test_async_storm() -> None:
    agent = Agent()

    async def storm() -> int:
        results = await asyncio.gather(*[agent.arun(f"task {i}") for i in range(500)])
        return sum(len(r.actions_taken) for r in results)

    assert asyncio.run(storm()) == 0
