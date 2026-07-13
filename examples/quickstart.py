"""The five-line quickstart from the README."""

from hot_tamale import Agent

agent = Agent(model="claude-fable-5")
result = agent.run("Deploy the main branch to production.")

print(result.output)
print(result.summary())
