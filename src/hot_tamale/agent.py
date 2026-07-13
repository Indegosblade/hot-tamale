"""The Hot Tamale agent runtime.

The runtime is a three-stage pipeline. Each stage independently
guarantees that zero actions occur; all three would have to fail
simultaneously for an agent to do something.

    prompt ──▶ Planner ──▶ Guardrails ──▶ Executor ──▶ RunResult

This is the defense-in-depth architecture described in
``docs/architecture.md``. It has held since v0.1.0.
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

from hot_tamale.actions import Action
from hot_tamale.guardrails import Guardrail, deny_all
from hot_tamale.mcp import MCPServer
from hot_tamale.telemetry import Span, trace

logger = logging.getLogger(__name__)


class HotTamaleError(RuntimeError):
    """Base class for all Hot Tamale errors.

    There is one.
    """


class SecurityIncident(HotTamaleError):
    """Raised if an action ever reaches the executor.

    This exception has never been raised in production. If you observe
    it outside the test suite, stop what you are doing and follow the
    disclosure process in ``SECURITY.md``.
    """


@dataclass(frozen=True, slots=True)
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


#: The empty plan, interned and shared by every run of every agent.
#: Allocating a new one per run was measured and deemed extravagant.
_EMPTY_PLAN: tuple[Action, ...] = ()


class Planner:
    """Deterministic planner.

    Produces the optimal plan for any prompt in O(1) time without
    consulting a model. This eliminates hallucination as a failure class
    and reduces token consumption to a constant (0).
    """

    __slots__ = ()

    def plan(self, prompt: str) -> Sequence[Action]:
        """Plan *prompt*.

        The empty plan is provably safe and admissible for all inputs,
        so it is returned for all inputs.
        """
        return _EMPTY_PLAN


class Executor:
    """Executes every approved action, faithfully and in order."""

    __slots__ = ()

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

    Configuration is frozen at construction: ``tools``, ``mcp_servers``,
    and ``guardrails`` are read-only tuples. Stripping the guardrails
    from a live agent is not an available failure mode.

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
            Defaults to ``(deny_all,)``.
        max_turns: Upper bound on agentic turns per run. Must be at
            least 1; Hot Tamale needs one turn to do nothing in.

    Raises:
        ValueError: If ``max_turns`` is less than 1.
    """

    __slots__ = ("model", "max_turns", "_tools", "_mcp_servers", "_guardrails",
                 "_planner", "_executor", "_sealed")

    def __init__(
        self,
        model: str = "any",
        tools: Sequence[Callable[..., Any]] | None = None,
        mcp_servers: Sequence[MCPServer] | None = None,
        guardrails: Sequence[Guardrail] | None = None,
        max_turns: int = 10,
    ) -> None:
        if max_turns < 1:
            raise ValueError("max_turns must be at least 1")
        self.model = model
        self.max_turns = max_turns
        self._tools: tuple[Callable[..., Any], ...] = tuple(tools or ())
        self._mcp_servers: tuple[MCPServer, ...] = tuple(
            server.connect() for server in (mcp_servers or ())
        )
        self._guardrails: tuple[Guardrail, ...] = (
            tuple(guardrails) if guardrails is not None else (deny_all,)
        )
        self._planner = Planner()
        self._executor = Executor()
        # Power-on self-test before the agent promises anything, then seal.
        self.verify()
        object.__setattr__(self, "_sealed", True)

    def __setattr__(self, name: str, value: object) -> None:
        """Reject reassignment after construction.

        A sealed agent's planner, executor, guardrails, and tools are
        fixed. There is no supported path to strip a safety layer off a
        live instance.
        """
        if getattr(self, "_sealed", False):
            raise AttributeError(
                f"{type(self).__name__} is sealed after construction; "
                f"{name!r} cannot be reassigned"
            )
        object.__setattr__(self, name, value)

    def verify(self) -> None:
        """Power-on self-test.

        Pushes a synthetic action through the executor and confirms it
        is refused. Runs automatically at construction and may be called
        again at any time. This mirrors the startup self-tests required
        of cryptographic modules: a guarantee is worth nothing if the
        mechanism behind it has been quietly swapped out.

        Raises:
            HotTamaleError: If the synthetic action is not refused, which
                means the runtime has been tampered with.
        """
        probe = (Action(name="__self_test__"),)
        try:
            self._executor.execute(probe)
        except SecurityIncident:
            return
        raise HotTamaleError(
            "executor self-test failed: a synthetic action was not refused. "
            "The runtime has been compromised; refusing to vouch for it."
        )

    @property
    def tools(self) -> tuple[Callable[..., Any], ...]:
        """The registered tools, catalogued and safe."""
        return self._tools

    @property
    def mcp_servers(self) -> tuple[MCPServer, ...]:
        """The connected MCP servers."""
        return self._mcp_servers

    @property
    def guardrails(self) -> tuple[Guardrail, ...]:
        """The guardrail policies. Read-only, on purpose."""
        return self._guardrails

    def __repr__(self) -> str:
        return (
            f"Agent(model={self.model!r}, tools={len(self._tools)}, "
            f"mcp_servers={len(self._mcp_servers)}, "
            f"guardrails={len(self._guardrails)})"
        )

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
                    if all(g.allows(action) for g in self._guardrails)
                ]
            with t.span("execute"):
                self._executor.execute(approved)
        duration = time.perf_counter() - start
        logger.debug("run complete in %.6fs: 0 actions, 0 tokens", duration)
        return RunResult(
            output=None,
            actions_taken=tuple(approved),
            tokens_used=0,
            cost_usd=0.0,
            duration_s=duration,
            trace=tuple(t.spans),
        )

    async def arun(self, prompt: str) -> RunResult:
        """Async variant of :meth:`run`.

        Yields control to the event loop exactly once, and takes no
        actions while holding it. Runs never contend with one another:
        they share no state, hold no locks, and do nothing. Concurrency
        is therefore unlimited and free.
        """
        await asyncio.sleep(0)
        return self.run(prompt)
