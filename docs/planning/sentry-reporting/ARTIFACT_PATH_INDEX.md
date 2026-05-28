# Sentry Reporting Artifact Path Index

## Purpose

- This file is the canonical naming and path index for the planning set.
- This file is not the current-status ledger.
- Future prompts should use this file instead of hardcoded path assumptions.

## Canonical Role Index

### Planning Root

- Actual repo path: `docs/planning/sentry-reporting/`
- Already exists: `YES`
- Canonical for future prompts: `YES`
- Confidence: `High`
- Explanation: Single initiative root for the Sentry reporting feature.

### Landing README

- Actual repo path: `docs/planning/sentry-reporting/README.md`
- Already exists: `YES`
- Canonical for future prompts: `YES`
- Confidence: `High`
- Explanation: Operating guide and status snapshot for this tree.

### Artifact Path Index

- Actual repo path: `docs/planning/sentry-reporting/ARTIFACT_PATH_INDEX.md`
- Already exists: `YES`
- Canonical for future prompts: `YES`
- Confidence: `High`
- Explanation: This file. Names and paths only.

### Foundation Directory

- Actual repo path: `docs/planning/sentry-reporting/foundation/`
- Already exists: `YES`
- Canonical for future prompts: `YES`
- Confidence: `High`
- Explanation: Durable design decisions for the integration.

### Integration Model ADR

- Actual repo path: `docs/planning/sentry-reporting/foundation/integration-model-adr.md`
- Already exists: `YES`
- Canonical for future prompts: `YES`
- Confidence: `High`
- Explanation: Enrich-only, never-init, no-op-when-absent contract.

### Data Safety And Scrubbing ADR

- Actual repo path: `docs/planning/sentry-reporting/foundation/data-safety-and-scrubbing-adr.md`
- Already exists: `YES`
- Canonical for future prompts: `YES`
- Confidence: `High`
- Explanation: Token and PII scrubbing policy and allowed fields.

### Optional Dependency And Versioning ADR

- Actual repo path: `docs/planning/sentry-reporting/foundation/optional-dependency-and-versioning-adr.md`
- Already exists: `YES`
- Canonical for future prompts: `YES`
- Confidence: `High`
- Explanation: `aryeo[sentry]` extras boundary and the planned `0.2.0` bump.

### Master Readiness Tracker

- Actual repo path: `docs/planning/sentry-reporting/trackers/readiness-overview.md`
- Already exists: `YES`
- Canonical for future prompts: `YES`
- Confidence: `High`
- Explanation: Aggregate readiness snapshot for the initiative.

### Focused Trackers

- Actual repo path: `docs/planning/sentry-reporting/trackers/data-safety-readiness.md`
- Actual repo path: `docs/planning/sentry-reporting/trackers/docs-tests-readiness.md`
- Already exists: `YES`
- Canonical for future prompts: `YES`
- Confidence: `High`
- Explanation: Highest-risk data-safety lens and docs/tests/examples sync lens.

### Execution Directory

- Actual repo path: `docs/planning/sentry-reporting/execution/`
- Already exists: `YES`
- Canonical for future prompts: `YES`
- Confidence: `High`
- Explanation: Ordered plan plus the checked-in ledger.

### Execution Plan

- Actual repo path: `docs/planning/sentry-reporting/execution/execution-plan.md`
- Already exists: `YES`
- Canonical for future prompts: `YES`
- Confidence: `High`
- Explanation: Live checked-in ledger.

### Active Plan

- Actual repo path: `docs/planning/sentry-reporting/execution/sentry-reporting-plan.md`
- Already exists: `YES`
- Canonical for future prompts: `YES`
- Confidence: `High`
- Explanation: Canonical current rollout sequence and public API surface.

### Roadmap

- Actual repo path: `docs/planning/sentry-reporting/execution/roadmap.md`
- Already exists: `YES`
- Canonical for future prompts: `YES`
- Confidence: `High`
- Explanation: Baseline dependency-aware task order.

### Phase Proof Files

- Actual repo path: `docs/planning/sentry-reporting/execution/sentry_PHASE_##_<slug>.md`
- First file: `docs/planning/sentry-reporting/execution/sentry_PHASE_01_integration_landed.md`
- Already exists: `YES` (Phase 01)
- Canonical for future prompts: `YES`
- Confidence: `High`
- Explanation: Add per-slice proof files during execution, reusing the `sentry` domain prefix.

## Runtime Artifact Homes

These implementation targets are now checked in by the execution pass.

- Reporter module: `aryeo/sentry.py` -- Already exists: `YES`
- Public export: `aryeo/__init__.py` (exports reporter and options) -- Already exists: `YES`
- Transport hook: `aryeo/base_client.py` (`BaseClient.request_json`) -- Already exists: `YES`
- Client wiring: `aryeo/client.py` (`AryeoClient`, `from_env`) -- Already exists: `YES`
- Packaging: `pyproject.toml` (`[project.optional-dependencies] sentry`) -- Already exists: `YES`
- Tests: `tests/test_sentry.py` -- Already exists: `YES`
- Guide: `docs/guides/sentry.md` -- Already exists: `YES`
- API reference: `docs/api-reference/sentry.md` -- Already exists: `YES`
- Example: `examples/sentry_reporting.py` -- Already exists: `YES`

## Directory Structure

```text
docs/planning/sentry-reporting/
  README.md
  ARTIFACT_PATH_INDEX.md
  foundation/
    README.md
    integration-model-adr.md
    data-safety-and-scrubbing-adr.md
    optional-dependency-and-versioning-adr.md
  trackers/
    README.md
    readiness-overview.md
    data-safety-readiness.md
    docs-tests-readiness.md
  execution/
    README.md
    roadmap.md
    execution-plan.md
    sentry-reporting-plan.md
    sentry_PHASE_01_integration_landed.md
```
