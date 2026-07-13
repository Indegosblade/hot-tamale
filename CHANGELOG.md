# Changelog

All notable changes to this project are documented in this file. The
format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Removed
- Nothing yet. Candidates are being evaluated ([#3](https://github.com/Indegosblade/hot-tamale/issues/3)).

## [1.1.0] — 2026-07-13

### Added
- Instance sealing: agents are frozen after construction. The planner,
  executor, guardrails, and tools of a live agent can no longer be
  reassigned, and arbitrary attributes can no longer be attached.
- Power-on self-test: every agent verifies at construction that its
  executor still refuses actions, and fails loudly if it does not.
  Also available on demand as `Agent.verify()`.
- `HotTamaleError`, a base class for all Hot Tamale errors. There is one
  other.

### Security
- Closed the two runtime-integrity gaps found in adversarial testing
  (live-instance reassignment; silent executor replacement). The
  interpreter-level boundary of the guarantees is now documented in
  `THREAT_MODEL.md`.

### Changed
- Behavior: unchanged. This is now verified at construction, per run,
  and on demand.

## [1.0.1] — 2026-07-10

### Performance
- Reduced actions taken per run from 0 to 0 (−0%).
- p99 latency improved by not adding anything.

### Documentation
- Clarified that `None` is intentional.

### Fixed
- Nothing. Nothing has ever needed fixing.

## [1.0.0] — 2026-06-02

### Added
- Stability guarantee. The API is now frozen, which required no changes.

### Security
- Formalized the threat model (see SECURITY.md). Residual attack
  surface confirmed to be the empty set.

## [0.1.0] — 2026-05-11

### Added
- Initial release. Feature-complete.
