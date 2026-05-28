# Changelog

## 0.2.0

- Add optional, opt-in, enrich-only Sentry reporting via the `aryeo[sentry]`
  extra. The client captures `AryeoAPIError` and `AryeoRequestError` and records
  request breadcrumbs into an already-initialized Sentry SDK, with bearer-token
  and PII scrubbing. Reporting never calls `sentry_sdk.init()` and is a no-op
  unless explicitly enabled and Sentry is active.
- Add `report_to_sentry` and `sentry_options` to `AryeoClient`, and honor the
  `ARYEO_SENTRY_ENABLED` environment variable in `AryeoClient.from_env`.
