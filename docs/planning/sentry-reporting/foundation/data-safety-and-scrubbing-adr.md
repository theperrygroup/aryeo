# Data Safety And Scrubbing ADR

## Status

Accepted (planning). This is the highest-risk lens for the initiative.

## Context

- The client sends a bearer token in the `Authorization` header, built in
  `BaseClient._build_headers`.
- Query params and JSON payloads can carry customer PII (emails, phone numbers,
  addresses, names).
- Sentry breadcrumbs, tags, and captured exception context are transmitted to
  the consumer's Sentry project, so anything attached must be safe by default.

## Decision

Safe-by-default scrubbing is mandatory. The execution pass must satisfy every
rule below.

### Never Transmitted

- The bearer token and the `Authorization` header value.
- Raw request headers of any kind.
- Full request or response bodies by default.

### What May Be Attached

- HTTP method.
- Request path with the query string removed (or with query values redacted by
  key).
- HTTP status code for failures.
- Elapsed time for the request.
- Exception metadata: `status_code`, `api_code`, `api_status`, and a truncated
  message.

### Redaction Rules

- Default `scrub_keys` (case-insensitive): `authorization`, `token`,
  `access_token`, `api_key`, `apikey`, `password`, `secret`, `cookie`,
  `set-cookie`, `email`, `phone`.
- Redacted values are replaced with `[redacted]`, never removed silently in a
  way that hides that scrubbing happened.
- Messages and any string fields are truncated to a bounded length before send.
- Consumers may extend `scrub_keys` but cannot remove the token from the
  always-scrub set.

### Consumer Controls

- `SentryReportOptions.before_send` runs last and can drop or further redact any
  event the library would send.
- Attaching scrubbed params is opt-in through options and off by default.

## Breadcrumb And Capture Shape

- Breadcrumb category: `aryeo.request`.
- Breadcrumb type: `http`.
- Breadcrumb level: configurable, default `info`; failures use `error`.
- Captured exceptions carry tags such as `aryeo.status_code` and
  `aryeo.api_code`, never tags derived from secrets.

## Consequences

- The default configuration cannot leak the token or raw PII.
- Consumers who want richer payload context must opt in explicitly and own that
  decision.
- Tests must prove the token never appears in any breadcrumb, tag, or captured
  event.

## Follow-Up

- Phase 4 tests assert the token and a representative PII key are absent from
  all emitted Sentry data.
- Document the scrubbing guarantees in `docs/guides/sentry.md` during Phase 5.
