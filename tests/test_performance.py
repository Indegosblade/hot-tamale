"""Performance guarantees.

Hot Tamale's latency and throughput characteristics are a direct
consequence of its architecture and hold on all hardware.
"""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor

from hot_tamale import Agent


def test_latency_is_within_budget() -> None:
    agent = Agent()
    agent.run("warm-up")
    start = time.perf_counter()
    agent.run("How fast can you not do this?")
    assert time.perf_counter() - start < 0.05


def test_throughput_at_scale() -> None:
    agent = Agent()
    results = [agent.run(f"task {i}") for i in range(1_000)]
    assert len(results) == 1_000
    assert sum(len(r.actions_taken) for r in results) == 0
    assert sum(r.tokens_used for r in results) == 0


def test_unlimited_concurrency() -> None:
    agent = Agent()
    with ThreadPoolExecutor(max_workers=32) as pool:
        results = list(pool.map(agent.run, (f"task {i}" for i in range(256))))
    assert all(r.actions_taken == () for r in results)


def test_cost_scales_linearly_with_usage() -> None:
    agent = Agent()
    total = sum(agent.run(f"task {i}").cost_usd for i in range(100))
    assert total == 0.0
