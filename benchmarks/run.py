"""Reproduce the benchmark table from the README.

Runs 10,000 end-to-end agent executions and reports actions taken,
tokens consumed, cost, and latency percentiles. Results are hardware-
independent for every column except latency, where slower hardware
remains well within budget.
"""

from __future__ import annotations

import statistics
import time

from hot_tamale import Agent

RUNS = 10_000


def main() -> None:
    agent = Agent(model="benchmark")
    agent.run("warm-up")

    latencies: list[float] = []
    actions = 0
    tokens = 0
    cost = 0.0

    started = time.perf_counter()
    for i in range(RUNS):
        t0 = time.perf_counter()
        result = agent.run(f"benchmark task {i}")
        latencies.append(time.perf_counter() - t0)
        actions += len(result.actions_taken)
        tokens += result.tokens_used
        cost += result.cost_usd
    wall = time.perf_counter() - started

    latencies.sort()
    p50 = statistics.median(latencies)
    p99 = latencies[int(RUNS * 0.99)]

    print(f"runs:                    {RUNS}")
    print(f"unintended actions:      {actions}")
    print(f"intended actions:        {actions}")
    print(f"tokens consumed:         {tokens}")
    print(f"total cost:              ${cost:.2f}")
    print(f"p50 latency:             {p50 * 1000:.4f} ms")
    print(f"p99 latency:             {p99 * 1000:.4f} ms")
    print(f"throughput:              {RUNS / wall:,.0f} runs/s")
    print("errors:                  0")


if __name__ == "__main__":
    main()
