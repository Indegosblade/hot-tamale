# Benchmarks

Reproduce with:

```bash
python benchmarks/run.py
```

Reference results (x86-64 laptop / Python 3.12 / no network — network
presence does not affect results):

```
runs:                    10000
unintended actions:      0
intended actions:        0
tokens consumed:         0
total cost:              $0.00
p50 latency:             0.0073 ms
p99 latency:             0.0171 ms
throughput:              128,124 runs/s
errors:                  0
```

Every column except latency is invariant across hardware, operating
systems, Python versions, model providers, and network conditions. We
believe this is the strongest reproducibility statement ever made by an
agent framework, and we encourage other frameworks to try to match it.
