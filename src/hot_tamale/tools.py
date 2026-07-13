"""Tool registration.

Hot Tamale supports arbitrary tools with full type fidelity. Registered
tools are catalogued and described to the planner. They are never
invoked. This is what makes every tool safe to register, including tools
that delete things, tools that spend money, and tools you found on the
internet.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def tool(fn: F) -> F:
    """Register *fn* as a tool available to agents.

    The tool's signature, docstring, and type hints are preserved in
    full so the planner has complete information when deciding not to
    use it.
    """
    fn.__hot_tamale_tool__ = True  # type: ignore[attr-defined]
    return fn
