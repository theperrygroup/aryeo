# Sentry Reporting Readiness Tracker

## Purpose

This tracker records the current readiness state under a strict "planning is not
runtime" interpretation.

## Interpretation Rule

- `Complete` means the tracked planning or prerequisite slice is checked in.
- It does not mean the feature is live in the shipped `aryeo` package.
- Runtime truth still comes from the checked-in codebase under `aryeo/`.

## Current Snapshot

Snapshot date: `2026-05-28`

| Phase | Status | Current answer |
| --- | --- | --- |
| Phase 0 - Design and foundation | Complete | ADRs and the active plan are checked in; the public API surface is defined. |
| Phase 1 - Packaging and version | Complete | `aryeo[sentry]` extra added and version bumped to `0.2.0`. |
| Phase 2 - Reporter module | Complete | `aryeo/sentry.py` implements the reporter and scrubber. |
| Phase 3 - Transport hook | Complete | `BaseClient.request_json` records breadcrumbs and captures errors. |
| Phase 4 - Tests and coverage | Complete | `tests/test_sentry.py`: 123 tests pass; `sentry.py` at 97%. |
| Phase 5 - Docs and examples | Complete | Guide, reference, README, example, and nav are checked in; strict build passes. |
| Phase 6 - Release quality and CI | In Progress | CI no-op job and changelog landed; the `v0.2.0` PyPI publish is not done. |

## Broad Blockers Before A Live Feature

- None blocking code work. The integration is checked in and verified locally.
- The `0.2.0` release is not published to PyPI yet; the feature is verified, not
  yet live on the index.

## Focused Tracker Snapshot

| Focused tracker | Current state | Why it matters |
| --- | --- | --- |
| `data-safety-readiness.md` | Enforced and proven | Token or PII leakage is the highest risk. |
| `docs-tests-readiness.md` | Checked in and verified | The repo rules require docs, tests, and examples to land with the feature. |

## Current Conclusion

- The Sentry reporting feature is implemented, tested, documented, and verified.
- It is `checked in` and `verified`, not yet `live` on PyPI.
