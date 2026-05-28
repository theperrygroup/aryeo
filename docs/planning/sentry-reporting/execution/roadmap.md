# Sentry Reporting Task Roadmap

This roadmap converts the current understanding of the initiative into a phased,
dependency-aware task plan.

Treat this file as the baseline dependency map. For the freshest checked-in
status, use `execution-plan.md` plus the focused trackers. The active plan in
`sentry-reporting-plan.md` outranks this roadmap for the current seam.

## Scope And Evidence

- Source references:
  - `../foundation/integration-model-adr.md`
  - `../foundation/data-safety-and-scrubbing-adr.md`
  - `../foundation/optional-dependency-and-versioning-adr.md`
- Primary code anchors:
  - `aryeo/base_client.py` (`BaseClient.request_json`, `_build_headers`)
  - `aryeo/exceptions.py` (`AryeoAPIError`, `AryeoRequestError`)
  - `aryeo/client.py` (`AryeoClient`, `from_env`)
  - `pyproject.toml`, `aryeo/__init__.py` (version sources)
  - `.github/workflows/ci.yml` (quality gates)
- Historical blockers at roadmap creation:
  - No reporter module or transport hook exists.
  - Data-safety enforcement is documented but unimplemented.

## Current Checked-In Progress Snapshot

- Phase 0 design docs are checked in.
- No runtime code, packaging, version, test, doc, or example change has landed.

## Harsh Sequencing Rule

- Do not implement the transport hook (Phase 3) before the reporter and its
  scrubber (Phase 2) exist and the safety contract is encoded.
- Do not claim the feature is live until tests prove no token or PII leakage.

## Phase 0 - Design And Foundation

### P0-001 - Capture durable design decisions

- Why this task exists: lock the enrich-only model, data-safety policy, and
  packaging boundary before code.
- Exact files or modules affected: `foundation/*.md`, `sentry-reporting-plan.md`.
- Dependency prerequisites: none.
- Severity: High.
- Estimated complexity: Low.
- Feature domain: Foundation.
- Whether this is: `DOCS-ONLY`.
- Acceptance criteria: three ADRs and the active plan are checked in.
- What could break if skipped: implementation drifts from the chosen model and
  may leak secrets.

## Phase 1 - Packaging And Version

### P1-001 - Add the `sentry` extra and bump to `0.2.0`

- Why this task exists: gate `sentry-sdk` behind opt-in extras and keep the
  version sources aligned.
- Exact files or modules affected: `pyproject.toml`
  (`[project.optional-dependencies]`, `dev`), `aryeo/__init__.py` (`__version__`).
- Dependency prerequisites: P0-001.
- Severity: High.
- Estimated complexity: Low.
- Feature domain: Packaging.
- Whether this is: implementation.
- Acceptance criteria: `sentry = ["sentry-sdk>=2.0.0"]` exists, `dev` includes
  `sentry-sdk`, both version sources read `0.2.0`.
- What could break if skipped: base install bloats, or version sources diverge
  and fail the release contract.

## Phase 2 - Reporter Module

### P2-001 - Implement `aryeo/sentry.py`

- Why this task exists: provide the enrich-only reporter and the scrubber.
- Exact files or modules affected: `aryeo/sentry.py`, `aryeo/__init__.py`
  (exports and `__all__`).
- Dependency prerequisites: P1-001.
- Severity: High.
- Estimated complexity: Medium.
- Feature domain: Runtime.
- Whether this is: implementation.
- Acceptance criteria: `SentryReportOptions` and `SentryReporter` exist with
  lazy import, `is_active()`, breadcrumb and capture methods, and a scrubber
  enforcing the data-safety ADR; Google docstrings and full type hints; no
  module-load import of `sentry_sdk`.
- What could break if skipped: there is nothing to hook into.

## Phase 3 - Transport Hook And Client Wiring

### P3-001 - Hook `request_json` and wire the client

- Why this task exists: emit breadcrumbs and capture errors at the single HTTP
  chokepoint.
- Exact files or modules affected: `aryeo/base_client.py`, `aryeo/client.py`.
- Dependency prerequisites: P2-001.
- Severity: High.
- Estimated complexity: Medium.
- Feature domain: Runtime.
- Whether this is: implementation.
- Acceptance criteria: `report_to_sentry` and `sentry_options` parameters on
  `BaseClient` and `AryeoClient`; breadcrumb recorded before send; capture in
  both error branches before `raise`; `from_env` honors `ARYEO_SENTRY_ENABLED`;
  no headers or token passed to the reporter; default-off path unchanged.
- What could break if skipped: errors are never reported.

## Phase 4 - Tests And Coverage

### P4-001 - Add `tests/test_sentry.py`

- Why this task exists: prove behavior and the no-leak guarantees.
- Exact files or modules affected: `tests/test_sentry.py`, `tests/conftest.py`
  if a fixture is needed.
- Dependency prerequisites: P3-001.
- Severity: High.
- Estimated complexity: Medium.
- Feature domain: Tests.
- Whether this is: implementation.
- Acceptance criteria: cases for no-op when `sentry-sdk` absent, capture on
  error, breadcrumb recorded, token and PII scrubbed, never calls `init()`,
  default-off; coverage maintained on `aryeo/sentry.py`.
- What could break if skipped: regressions and silent secret leakage.

## Phase 5 - Docs, Reference, And Examples

### P5-001 - Publish docs and a runnable example

- Why this task exists: satisfy the docs-tests-sync and api-client rules.
- Exact files or modules affected: `docs/guides/sentry.md`,
  `docs/api-reference/sentry.md`, `README.md`, `examples/sentry_reporting.py`,
  `mkdocs.yml` (nav entries for the new pages).
- Dependency prerequisites: P3-001 (API stable).
- Severity: Medium.
- Estimated complexity: Medium.
- Feature domain: Docs.
- Whether this is: implementation.
- Acceptance criteria: guide, mkdocstrings reference, README section, and
  example exist; nav updated; `mkdocs build --strict` passes.
- What could break if skipped: users cannot discover or safely use the feature.

## Phase 6 - Release Quality And CI

### P6-001 - Cover both install paths and release `0.2.0`

- Why this task exists: prove the no-op path on a base install and ship.
- Exact files or modules affected: `.github/workflows/ci.yml`,
  `docs/reference/changelog.md`, release workflow.
- Dependency prerequisites: P4-001, P5-001.
- Severity: High.
- Estimated complexity: Medium.
- Feature domain: Release.
- Whether this is: implementation.
- Acceptance criteria: CI installs and tests both with `.[dev]` and a base-only
  path; all gates green; changelog updated; trusted `0.2.0` release.
- What could break if skipped: the no-op contract is unproven and the feature
  is unreleased.
