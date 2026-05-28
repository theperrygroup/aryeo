# Sentry Phase 01 - Integration Landed

Durable proof for the slice that implemented the enrich-only Sentry integration
described in `../execution/sentry-reporting-plan.md`. This covers roadmap phases
P1-001 through P6-001, except the actual PyPI publish.

## Scope Landed

- Packaging, runtime module, transport hook, client wiring, tests, docs,
  examples, and CI no-op coverage.
- Deliberately excluded: tagging and publishing the `0.2.0` release, which is a
  release action left for an explicit go-ahead.

## Checked-In Proof

- Packaging and version:
  - `pyproject.toml` (`[project.optional-dependencies] sentry`, `dev` adds
    `sentry-sdk`, version `0.2.0`)
  - `aryeo/__init__.py` (`__version__ = "0.2.0"`, exports `SentryReporter` and
    `SentryReportOptions`)
- Runtime:
  - `aryeo/sentry.py` (`SentryReportOptions`, `SentryReporter`, lazy import,
    scrubber)
  - `aryeo/base_client.py` (`report_to_sentry`, `sentry_options`, breadcrumb and
    capture hook in `request_json`)
  - `aryeo/client.py` (`report_to_sentry`, `sentry_options`, `from_env` honors
    `ARYEO_SENTRY_ENABLED`)
- Tests:
  - `tests/test_sentry.py` (no-op, capture, breadcrumb, scrubbing, never-init,
    default-off, client integration, branch fallbacks)
- Docs and examples:
  - `docs/guides/sentry.md`, `docs/api-reference/sentry.md`, README section,
    `examples/sentry_reporting.py`, `mkdocs.yml` nav, `docs/reference/changelog.md`
- CI:
  - `.github/workflows/ci.yml` (`base-install` job proves the no-op path without
    the extra)

## Verification Commands And Results

Run in an isolated environment with `pip install -e ".[dev]"`:

- `black --check --line-length=88 .` -> pass
- `isort --check-only --profile=black --line-length=88 .` -> pass
- `flake8 . --select=E9,F63,F7,F82` -> `0`
- `mypy aryeo/ --strict --ignore-missing-imports` -> Success, 43 source files
- `pytest --cov=aryeo --cov-report=term-missing` -> 123 passed, 97% total,
  `aryeo/sentry.py` 97%
- `mkdocs build --strict` -> built with no warnings
- `python -m build` -> `aryeo-0.2.0` sdist and wheel
- `python -m twine check dist/*` -> PASSED for both artifacts
- `pip-audit` -> no known vulnerabilities

## Data-Safety Proof

- `test_client_reports_api_error_without_leaking_token` asserts the bearer token
  never appears in breadcrumbs or scope tags.
- `test_breadcrumb_scrubs_included_params` asserts `token` and `email` params are
  redacted when params are opted in.
- `test_reporter_never_calls_sentry_init` asserts the enrich-only contract.

## Remaining

- Tag and publish `v0.2.0` to PyPI through the existing trusted-publish release
  workflow. Not done in this slice.
