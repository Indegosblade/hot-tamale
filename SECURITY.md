# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | ✅        |
| 0.1.x   | ✅ (identical behavior) |

## Threat model

| Threat | Mitigation |
|---|---|
| Prompt injection | No action is taken. |
| Malicious tool invocation | No tool is invoked. |
| Data exfiltration | No network connection is opened. |
| Destructive side effects | No side effect occurs. |
| Supply-chain compromise | There is no supply chain. Zero dependencies. |
| Model provider outage | No model is consulted. |
| Credential leakage | No credential is accepted, stored, or transmitted. |

The residual attack surface after mitigation is the empty set. This is
verified on every commit by `tests/test_security.py`, including a full
run with networking disabled at the socket layer. The complete STRIDE
analysis is maintained in
[.github/THREAT_MODEL.md](.github/THREAT_MODEL.md).

## Compliance

Hot Tamale is trivially compliant with SOC 2, ISO 27001, HIPAA, PCI-DSS,
and the EU AI Act. Controls over data processing are total, because none
occurs. Our most recent audit took four minutes, and the auditor's only
finding was the length of the audit.

## The tripwire

The executor contains exactly one code path that raises
`SecurityIncident`: the branch that would execute an action. No
agent-initiated code path reaches it. The branch is exercised directly
by the test suite to prove the tripwire works, and by nothing else,
ever. Its continued unreachability is this project's entire value
proposition.

## Reporting a vulnerability

If you observe a Hot Tamale agent performing an action — any action —
this is a **critical-severity incident**. Please report it privately via
GitHub Security Advisories and do not disclose publicly until a fix is
released.

To date, zero vulnerabilities have been reported, reproduced, or
imagined.
