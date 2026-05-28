# Integration Model ADR

## Status

Accepted (planning). No runtime code has landed.

## Context

- `aryeo` is a client library, not an application. Libraries that own Sentry
  initialization fight the consuming application for global SDK state.
- All HTTP traffic already funnels through one chokepoint,
  `BaseClient.request_json` in `aryeo/base_client.py`, which raises
  `AryeoRequestError` for transport failures and `AryeoAPIError` for non-success
  responses.
- Consumers asked for error reporting that cooperates with their own Sentry
  setup rather than replacing it.

## Decision

- Ship an **enrich-only** integration. The library never calls
  `sentry_sdk.init()` and never owns Sentry configuration.
- The library attaches to the consumer's already-initialized Sentry SDK to add
  breadcrumbs and capture exceptions.
- The integration is **opt-in**, default off. Consumers turn it on with an
  explicit flag, so a base client never changes behavior unexpectedly.
- The integration **degrades to a no-op** when any of these is true:
  - `sentry-sdk` is not installed.
  - No Sentry client is active or enabled in the current scope.
  - The opt-in flag is off.
- `sentry-sdk` is imported lazily inside the reporter so importing `aryeo`
  never imports `sentry_sdk`.

## Runtime Shape (to be implemented by the execution pass)

- New flat module `aryeo/sentry.py` (preferred name; `aryeo/observability.py`
  considered and rejected as less discoverable for a Sentry-specific feature).
- Public surface:
  - `SentryReportOptions`: capture toggles, breadcrumb level, extra tags,
    `scrub_keys`, and an optional `before_send` hook.
  - `SentryReporter`: holds options and exposes `is_active()`,
    `record_request_breadcrumb(...)`, and `capture_request_error(...)`.
- Activity check targets `sentry-sdk>=2.0.0` via `sentry_sdk.get_client()` and
  its `is_active()` result, with a guarded fallback for older hubs.
- Opt-in wiring:
  - `AryeoClient(..., report_to_sentry: bool = False, sentry_options: SentryReportOptions | None = None)`.
  - `BaseClient` accepts the same parameters and owns the hook.
  - `AryeoClient.from_env` reads `ARYEO_SENTRY_ENABLED` to enable reporting.

## Hook Behavior

```text
request_json(method, path, ...)
  if reporter active:
    record breadcrumb {method, scrubbed path, ...} before send
  send via httpx
    on httpx.HTTPError:
      reporter.capture_request_error(AryeoRequestError context)  # then raise
    on response.is_error:
      reporter.capture_request_error(AryeoAPIError context)      # then raise
```

- Capture happens before the exception is raised so the original control flow
  and exception types are unchanged.
- The no-op check must be cheap and run first to avoid overhead on the default
  path.

## Consequences

- Consumers keep full control of DSN, sampling, environment, and release tags.
- The base install gains no new runtime imports.
- The library cannot report when the consumer has not initialized Sentry; this
  is intentional and documented.
- Performance and tracing spans are explicitly out of scope for this initiative
  and may be added later behind the same options object.

## Alternatives Considered

- Self-init (library accepts a DSN and calls `sentry_sdk.init()`): rejected as
  the default because it conflicts with application-owned SDK state.
- Always-on enrichment: rejected because silently mutating Sentry scope for
  every existing consumer is surprising.

## Follow-Up

- Confirm the `sentry-sdk` activity API used across supported versions during
  Phase 2.
- Revisit tracing spans as a separate, additive initiative.
