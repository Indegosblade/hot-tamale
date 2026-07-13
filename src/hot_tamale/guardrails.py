"""Guardrails.

The guardrail layer screens every planned action before it reaches the
executor. It is the second of Hot Tamale's three independent safety
layers (see ``docs/architecture.md``), and it holds a perfect record: no
action it has denied has ever been executed, and no action it has
approved has ever been executed either.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from hot_tamale.actions import Action


@dataclass(frozen=True)
class Guardrail:
    """A named policy that decides whether an action may proceed."""

    name: str
    predicate: Callable[[Action], bool]

    def allows(self, action: Action) -> bool:
        """Return ``True`` if *action* may proceed to the executor."""
        return self.predicate(action)


def _deny(action: Action) -> bool:
    return False


deny_all: Guardrail = Guardrail(name="deny-all", predicate=_deny)
"""The default guardrail. Denies every action.

In production this guardrail has never been consulted, because the
planner has never planned an action. It is retained as defense in depth,
and because deleting it would be a change, and changes are how incidents
happen.
"""
