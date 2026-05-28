# Sentry Reporting Docs

This directory is the canonical operating guide for the Sentry reporting
planning set. It owns the roadmap for an opt-in, enrich-only Sentry integration
shipped inside the `aryeo` client library.

## Role

- This tree is docs-only.
- Runtime truth comes from checked-in code, not roadmap items alone.
- Shared repo rules (`release-quality-contract`, `docs-tests-sync`,
  `api-client-implementation`, `api-source-of-truth`) still apply and are
  cross-linked here, not duplicated.

## Interpretation Rules

- Planning complete is not the same as shipped.
- Readiness does not by itself prove runtime ownership.
- The active plan may outrank the historical roadmap for the current seam.
- The integration is enrich-only: the library never calls `sentry_sdk.init()`
  and degrades to a no-op when `sentry-sdk` is absent or uninitialized.

## Current Status Snapshot

Snapshot date: `2026-05-28`

| Lens | Current answer |
| --- | --- |
| Planning foundation | ADRs, trackers, roadmap, and a phase proof file are checked in. |
| Runtime feature or implementation truth | Implemented and verified locally. `aryeo/sentry.py`, the `aryeo[sentry]` extra, and version `0.2.0` are checked in; the full gate set passes. Not yet published to PyPI. |
| Highest-risk remaining surface | Token and PII leakage is now enforced and proven by tests; the open item is the `v0.2.0` release publish. |

## Fastest Reality Check

- `foundation/integration-model-adr.md`: confirms the enrich-only, no-op contract.
- `foundation/data-safety-and-scrubbing-adr.md`: confirms the token/PII scrubbing policy.
- `execution/sentry-reporting-plan.md`: the canonical active sequence and public API surface.
- `execution/execution-plan.md`: the checked-in ledger of what has actually landed.

## Start Here

1. `foundation/integration-model-adr.md`
2. `execution/sentry-reporting-plan.md`
3. `trackers/data-safety-readiness.md`
4. `trackers/readiness-overview.md`
5. `execution/execution-plan.md`
6. `execution/roadmap.md` only for historical sequencing
7. `ARTIFACT_PATH_INDEX.md` for canonical paths

## Directory Guide

| Folder or file | Role | Open first when you need |
| --- | --- | --- |
| `foundation/README.md` | Durable design decisions | Integration model, data safety, or packaging questions |
| `trackers/README.md` | Live readiness scoreboards | Current blockers and risk lenses |
| `execution/README.md` | Execution navigation | The next implementation slice |
| `execution/sentry-reporting-plan.md` | Canonical active sequence | The current rollout and public API |
| `ARTIFACT_PATH_INDEX.md` | Naming and path index | Canonical artifact homes |

## Document Precedence

1. `foundation/` wins for durable rules (integration model, data safety, packaging).
2. `execution/sentry-reporting-plan.md` wins for the current focused execution seam.
3. Focused trackers plus `execution/execution-plan.md` win for live checked-in status.
4. `execution/roadmap.md` is baseline sequencing, not the freshest status.
5. `ARTIFACT_PATH_INDEX.md` wins for exact paths and naming.

## Common Workflows

| Goal | Open these first |
| --- | --- |
| Start the next slice | `trackers/readiness-overview.md`, `execution/execution-plan.md`, `execution/sentry-reporting-plan.md` |
| Get current reality | `foundation/integration-model-adr.md`, `trackers/readiness-overview.md`, `execution/execution-plan.md` |
| Confirm data-safety guarantees | `foundation/data-safety-and-scrubbing-adr.md`, `trackers/data-safety-readiness.md` |
| Find the right future path | `ARTIFACT_PATH_INDEX.md`, the relevant ADR |

## Update Order

1. Relevant phase proof doc, if a slice needs durable evidence
2. Relevant focused tracker (`data-safety-readiness.md` or `docs-tests-readiness.md`)
3. `trackers/readiness-overview.md`
4. `execution/execution-plan.md`
5. Relevant `foundation/` doc, if durable rules changed
6. `README.md` or `ARTIFACT_PATH_INDEX.md` only if navigation or canonical paths changed

## Working Rules

- Keep this tree docs-only.
- Keep status language honest: `planned`, `checked in`, `in progress`, `complete`, `live`, `blocked`.
- Do not scatter related planning across multiple initiative roots.
- Defer performance and tracing spans; this initiative covers errors and breadcrumbs only.
