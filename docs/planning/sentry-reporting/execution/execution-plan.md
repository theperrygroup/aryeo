# Sentry Reporting Execution Plan

This file is the checked-in ledger for the planning set. It records what has
landed, what is blocked, and what still remains open.

## 1. Ledger Scope

- This ledger records checked-in proof.
- Use `roadmap.md` for baseline dependency order.
- Use focused trackers for current readiness detail.

## 1A. How To Read This Ledger Now

- This file is the ledger, not proof that the feature is published.
- Strongest checked-in proof: the full integration (module, transport hook,
  client wiring, tests, docs, examples, CI) is implemented and passes the entire
  local gate set, including data-safety tests.
- Biggest remaining gap: the `0.2.0` release is not published to PyPI yet. The
  code is `checked in` and `verified`, not `live` on the index.

## 2. Current Checked-In Status

- Packaging: `aryeo[sentry]` extra added; `dev` includes `sentry-sdk`; version
  bumped to `0.2.0` in `pyproject.toml` and `aryeo/__init__.py`.
- Runtime: `aryeo/sentry.py` implements the enrich-only reporter and scrubber;
  `aryeo/base_client.py` hooks `request_json`; `aryeo/client.py` exposes
  `report_to_sentry`/`sentry_options` and honors `ARYEO_SENTRY_ENABLED`.
- Tests: `tests/test_sentry.py` covers the no-op, capture, breadcrumb,
  scrubbing, never-init, default-off, and client-integration paths.
- Docs and examples: guide, mkdocstrings reference, README section, runnable
  example, nav entries, and a `0.2.0` changelog entry are checked in.
- CI: a `base-install` job proves the no-op path without the extra.

## 3. Current Blockers

- None blocking further code work.
- Release publish is intentionally deferred (see the work queue).

## 4. Completed Planning Or Landed Proof

### Phase 0 (2026-05-28) - Design and foundation

- Checked-in proof: the foundation ADRs, trackers, roadmap, and active plan.
- Result: enrich-only model, data-safety policy, packaging boundary, and public
  API surface decided.

### Phase 1 (2026-05-28) - Integration landed (roadmap P1-P6 minus publish)

- Checked-in proof: `execution/sentry_PHASE_01_integration_landed.md` lists the
  exact files and verification commands.
- Result: enrich-only Sentry reporting is implemented, tested, documented, and
  verified locally. The full gate set passes:
  - `mypy aryeo/ --strict` -> Success, 43 files
  - `pytest --cov=aryeo` -> 123 passed, 97% total
  - `mkdocs build --strict`, `python -m build`, `twine check`, `pip-audit` -> pass

## 5. Current Work Queue

| Task | Status | Why it is still open |
| --- | --- | --- |
| P1-001 Packaging and `0.2.0` bump | Complete | Checked in and verified. |
| P2-001 Implement `aryeo/sentry.py` | Complete | Checked in and verified. |
| P3-001 Hook transport and wire client | Complete | Checked in and verified. |
| P4-001 Tests and coverage | Complete | 123 tests pass; sentry.py at 97%. |
| P5-001 Docs, reference, example | Complete | Strict docs build passes. |
| P6-001 CI both paths and release | In Progress | CI no-op job and changelog landed; PyPI publish of `v0.2.0` not done. |

## 6. Current Conclusion

- The Sentry reporting feature is implemented, tested, documented, and verified
  in the working tree.
- It is `checked in` and `verified`, not yet `live` on PyPI.
- Next action: tag and publish `v0.2.0` through the existing release workflow
  when a maintainer approves the release.
