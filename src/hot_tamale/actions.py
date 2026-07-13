"""Typed action model.

Hot Tamale models actions as first-class, immutable objects so that the
guardrail layer has a complete, typed view of everything the executor is
about to not do.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Action:
    """A single action an agent could, in principle, take.

    Instances are immutable. An ``Action`` that has been constructed has
    not been performed; construction is free of side effects, like
    everything else in this framework.
    """

    name: str
    arguments: dict[str, Any] = field(default_factory=dict)
