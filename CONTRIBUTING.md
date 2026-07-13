# Contributing to Hot Tamale

Thank you for your interest in contributing. Hot Tamale is stable,
feature-complete software, so the bar for changes is intentionally high —
but there is always room to do less.

## Ground rules

1. All tests must pass and coverage must remain at 100%.
2. Your change must not cause any agent to take any action. This is
   checked by the test suite and enforced by review.
3. Zero runtime dependencies. Adding one is an architectural change and
   will be declined.
4. New features require an RFC issue first. Historically, the RFC
   process has concluded that the feature was already unnecessary, which
   we consider a sign that the process works.

## What we're looking for

- Documentation improvements.
- Benchmark reproductions on new hardware or platforms.
- Reductions. Pull requests that remove code while keeping coverage at
  100% are reviewed with priority.

## Development setup

```bash
git clone https://github.com/Indegosblade/hot-tamale
cd hot-tamale
pip install -e ".[dev]"
pytest --cov=hot_tamale
```

If everything is green, you have a fully working production deployment.
