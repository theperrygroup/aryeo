# Sentry Reporting Plan

This is the canonical active plan for the Sentry reporting initiative. It
outranks `roadmap.md` for the current focused seam and defines the public API
surface the execution pass should build.

## Goal

Ship an opt-in, enrich-only Sentry integration in the `aryeo` library that
captures `AryeoAPIError` and `AryeoRequestError` plus scrubbed request
breadcrumbs, never calls `sentry_sdk.init()`, and is a no-op when `sentry-sdk`
is absent or uninitialized.

## Public API Surface (target)

### `aryeo/sentry.py`

- `SentryReportOptions` (dataclass-style options):
  - `capture_exceptions: bool = True`
  - `record_breadcrumbs: bool = True`
  - `breadcrumb_level: str = "info"`
  - `extra_tags: dict[str, str] | None = None`
  - `scrub_keys: frozenset[str] = <ADR defaults>`
  - `include_params: bool = False` (opt-in scrubbed query params)
  - `before_send: Callable[[dict[str, Any]], dict[str, Any] | None] | None = None`
- `SentryReporter`:
  - `__init__(self, options: SentryReportOptions | None = None) -> None`
  - `is_active(self) -> bool` (cheap; checks lazy import and an active client)
  - `record_request_breadcrumb(self, *, method: str, path: str, status_code: int | None = None, elapsed_ms: float | None = None) -> None`
  - `capture_request_error(self, error: AryeoError, *, method: str, path: str, status_code: int | None = None) -> None`
- A private lazy importer that returns the `sentry_sdk` module or `None`.
- A private scrubber that enforces the data-safety ADR.

### `aryeo/base_client.py` and `aryeo/client.py`

- `BaseClient.__init__(..., report_to_sentry: bool = False, sentry_options: SentryReportOptions | None = None)`.
- `AryeoClient.__init__` forwards the same parameters.
- The hook lives in `BaseClient.request_json`: breadcrumb before send, capture
  in both error branches before `raise`.
- `AryeoClient.from_env(...)` enables reporting when `ARYEO_SENTRY_ENABLED` is
  truthy.

### `aryeo/__init__.py`

- Export `SentryReporter` and `SentryReportOptions`, and add them to `__all__`.

## Phase Sequence

See `roadmap.md` for full task detail. Summary order:

1. Phase 0 - Design and foundation (DOCS-ONLY). Complete.
2. Phase 1 - Packaging and version bump to `0.2.0`.
3. Phase 2 - Implement `aryeo/sentry.py`.
4. Phase 3 - Hook the transport and wire the client and `from_env`.
5. Phase 4 - Tests and coverage in `tests/test_sentry.py`.
6. Phase 5 - Docs, reference, README, and example.
7. Phase 6 - Release-quality, CI for both install paths, and the `0.2.0` release.

## Done Criteria

- Default client behavior is unchanged with reporting off.
- With reporting on and an active Sentry client, errors are captured and a
  breadcrumb is recorded.
- The token and a representative PII key never appear in any emitted Sentry
  data, proven by tests.
- Base install (no extra) imports and no-ops safely, proven in CI.
- All existing gates stay green, including `mkdocs build --strict`.

## Open Questions

- Exact `sentry-sdk` activity API across supported versions (resolve in Phase 2).
- Whether to expose a public helper to attach a reporter to an existing client
  after construction (defer unless requested).
