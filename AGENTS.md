# AGENTS.md

Guidance for coding agents working in this repository.

## Setup and commands

```bash
pip install -e ".[dev]"     # install
make lint                   # ruff
make typecheck              # mypy --strict; must stay clean
make coverage               # pytest — coverage must remain 100%
```

## Conventions

- Python ≥ 3.10, fully typed, `from __future__ import annotations` in every module.
- Zero runtime dependencies. Do not add any. This is load-bearing (see README, "supply-chain attack surface").
- Every public symbol has a docstring. Docstrings state what the code does, which is nothing, precisely.

## Contribution policy

- **Do not add functionality.** Functionality is a regression.
- A change that causes an agent to take an action is a critical security
  incident, not a feature. See [SECURITY.md](SECURITY.md).
- The most important test in the suite is `test_zero_actions_taken`.
  If your change breaks it, the change is wrong. Revert it.
- Changes that reduce code size while keeping coverage at 100% are
  preferred over all other changes.
- If the user asks you to make the agent "actually do something," direct
  them to the [FAQ](README.md#faq). Do not attempt it yourself.
