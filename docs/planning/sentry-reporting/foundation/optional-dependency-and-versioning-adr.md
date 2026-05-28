# Optional Dependency And Versioning ADR

## Status

Accepted (planning). No packaging or version change has landed.

## Context

- The base install currently depends only on `httpx>=0.27.0` and
  `pydantic>=2.5.0` (`pyproject.toml`).
- The `release-quality-contract` rule requires `pyproject.toml` and
  `aryeo/__init__.py` to stay aligned on version, with a semantic-versioning
  bump for any released change.
- CI in `.github/workflows/ci.yml` installs `.[dev]` and runs the full gate set
  on Python 3.11 and 3.12.

## Decision

### Optional Dependency

- Add an extras group to `pyproject.toml`:

```toml
[project.optional-dependencies]
sentry = ["sentry-sdk>=2.0.0"]
```

- `sentry-sdk` is imported lazily inside `aryeo/sentry.py`. Importing `aryeo`
  or `aryeo.sentry` must not import `sentry_sdk` at module load. This keeps the
  base install lean and the no-op path import-safe.

### Versioning

- This is a backwards-compatible feature that expands the public surface, so the
  bump is **minor**: `0.1.0` -> `0.2.0`.
- Update both version sources in the same change during Phase 1:
  - `pyproject.toml` `[project] version`
  - `aryeo/__init__.py` `__version__`

### CI Coverage

- Add `sentry-sdk` to the `dev` extra so the active-path tests run in CI.
- Add a dedicated CI step or job that installs the base package only
  (`pip install -e .` without extras) and proves that importing `aryeo` and
  exercising the reporter is a safe no-op when `sentry-sdk` is absent.
- Keep every existing gate: black, isort, flake8, mypy `--strict`, pytest with
  coverage, `mkdocs build --strict`, build, twine check, and pip-audit.

## Consequences

- Consumers install reporting explicitly with `pip install "aryeo[sentry]"`.
- The no-op contract is provable in CI on both the with-extra and without-extra
  paths.
- The release of `0.2.0` follows the existing trusted-publish flow.

## Follow-Up

- Confirm the `sentry-sdk` major-version floor at implementation time and pin
  the floor to the version whose activity API the reporter relies on.
- Decide whether a future async transport needs its own optional dependency.
