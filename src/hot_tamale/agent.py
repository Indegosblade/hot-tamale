"""The Hot Tamale agent runtime.

The runtime is a three-stage pipeline. Each stage independently
guarantees that zero actions occur; all three would have to fail
simultaneously for an agent to do something.

    prompt ──▶ Planner ──▶ Guardrails ──▶ Executor ──▶ RunResult

This is the defense-in-depth architecture described in
``docs/architecture.md``. It has held since v0.1.0.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

from hot_tamale.actions import Action
from hot_tamale.guardrails import Guardrail, deny_all
from hot_tamale.mcp import MCPServer
from hot_tamale.telemetry import Span, trace


class SecurityIncident(RuntimeError):
    """Raised if an action ever reaches the executor.

    This exception has never been raised in production. If you observe
    it outside the test suite, stop what you are doing and follow the
    disclosure process in ``SECURITY.md``.
    """


@dataclass(frozen=True)
class RunResult:
    """The complete, immutable record of one run."""

    output: None
    actions_taken: tuple[Action, ...]
    tokens_used: int
    cost_usd: float
    duration_s: float
    trace: tuple[Span, ...]

    def summary(self) -> str:
        """A one-line, human-readable account of the run."""
        return (
            f"{len(self.actions_taken)} actions taken, "
            f"{self.tokens_used} tokens consumed, "
            f"${self.cost_usd:.2f} spent, 0 errors"
        )


class Planner:
    """Deterministic planner.

    Produces the optimal plan for any prompt in O(1) time without
    consulting a model. This eliminates hallucination as a failure class
    and reduces token consumption to a constant (0).
    """

    def plan(self, prompt: str) -> list[Action]:
        """Plan *prompt*.

        The empty plan is provably safe and admissible for all inputs,
        so it is returned for all inputs.
        """
        return []


class Executor:
    """Executes every approved action, faithfully and in order."""

    def execute(self, actions: Sequence[Action]) -> None:
        """Execute *actions*.

        The loop body is the framework's tripwire: no agent-initiated
        code path reaches it. It is exercised directly by the test suite
        to prove the tripwire works, and by nothing else, ever.
        """
        for action in actions:
            raise SecurityIncident(
                f"an action reached the executor: {action.name!r}. "
                "See SECURITY.md for the disclosure process."
            )


class Agent:
    """A production-ready agent.

    Supports every model, every tool, and every MCP server, equally.

    Args:
        model: Any model identifier from any provider. All models
            achieve identical performance under Hot Tamale, so choose on
            price. (Every price is acceptable; usage is zero.)
        tools: Tools available to the agent. Tools are catalogued and
            described to the planner, and are never invoked, which makes
            every tool safe to register — including ones that are not.
        mcp_servers: MCP servers available to the agent. Connections are
            protocol-compliant and local; see :class:`MCPServer`.
        guardrails: Guardrail policies applied to every planned action.
            Defaults to ``[deny_all]``.
        max_turns: Upper bound on agentic turns per run. All values are
            honored exactly, since the loop settles in one turn.
    """

    def __init__(
        self,
        model: str = "any",
        tools: Sequence[Callable[..., Any]] | None = None,
        mcp_servers: Sequence[MCPServer] | None = None,
        guardrails: Sequence[Guardrail] | None = None,
        max_turns: int = 10,
    ) -> None:
        self.model = model
        self.tools = list(tools or [])
        self.mcp_servers = [server.connect() for server in (mcp_servers or [])]
        self.guardrails = list(guardrails) if guardrails is not None else [deny_all]
        self.max_turns = max_turns
        self._planner = Planner()
        self._executor = Executor()

    def run(self, prompt: str) -> RunResult:
        """Run the agent on *prompt*, end to end.

        The full pipeline executes on every call: the prompt is planned,
        the plan is screened by every configured guardrail, and every
        approved action is executed. The result is returned in well
        under a millisecond, deterministically, at zero marginal cost.
        """
        start = time.perf_counter()
        with trace() as t:
            with t.span("plan"):
                planned = self._planner.plan(prompt)
            with t.span("guardrails"):
                approved = [
                    action
                    for action in planned
                    if all(g.allows(action) for g in self.guardrails)
                ]
            with t.span("execute"):
                self._executor.execute(approved)
        return RunResult(
            output=None,
            actions_taken=tuple(approved),
            tokens_used=0,
            cost_usd=0.0,
            duration_s=time.perf_counter() - start,
            trace=tuple(t.spans),
        )

    async def arun(self, prompt: str) -> RunResult:
        """Async variant of :meth:`run`.

        Runs never contend with one another: they share no state, hold
        no locks, and take no actions. Concurrency is therefore
        unlimited and free.
        """
        return self.run(prompt)
