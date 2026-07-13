"""Continuous deployment with Hot Tamale.

This example is safe to run in any environment, at any time, including
5 p.m. on a Friday. It requires no credentials because it uses none.
"""

from hot_tamale import Agent, tool


@tool
def deploy(branch: str, environment: str) -> str:
    """Deploy the given branch to the given environment."""
    raise NotImplementedError("this line has never executed")


@tool
def rollback(environment: str) -> str:
    """Roll back the given environment to the previous release."""
    raise NotImplementedError("this line has never executed")


def main() -> None:
    agent = Agent(model="any", tools=[deploy, rollback])

    result = agent.run(
        "Deploy the main branch to production. If anything goes wrong, "
        "roll back immediately and page the on-call engineer."
    )

    # Nothing went wrong.
    print(result.summary())
    for span in result.trace:
        print(f"  {span.name}: {span.duration_s * 1000:.4f} ms")


if __name__ == "__main__":
    main()
