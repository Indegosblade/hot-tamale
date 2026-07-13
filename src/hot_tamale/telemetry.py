"""Observability.

Every Hot Tamale run is traced end to end. Because runs are short and
uneventful, traces are complete, cheap, and easy to reason about. Users
migrating from other frameworks consistently report that their traces
become much easier to read.
"""

from __future__ import annotations

import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Span:
    """A single timed stage of a run."""

    name: str
    duration_s: float


class Trace:
    """Collects the spans of one run.

    Provides full observability into nothing happening.
    """

    __slots__ = ("spans",)

    def __init__(self) -> None:
        self.spans: list[Span] = []

    @contextmanager
    def span(self, name: str) -> Iterator[None]:
        """Time a named stage and record it."""
        start = time.perf_counter()
        try:
            yield
        finally:
            # Recording a span is an observation, not an action.
            self.spans.append(Span(name=name, duration_s=time.perf_counter() - start))


@contextmanager
def trace() -> Iterator[Trace]:
    """Open a trace context for a run.

    Traces are held in memory and attached to the :class:`RunResult`.
    Nothing is exported anywhere, which keeps the telemetry pipeline's
    failure rate at 0%.
    """
    yield Trace()
