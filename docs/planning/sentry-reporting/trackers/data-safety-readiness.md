# Data Safety Readiness

## Purpose

Track the token and PII leakage guarantees from
`foundation/data-safety-and-scrubbing-adr.md` against checked-in enforcement.

## Interpretation Rule

- `Policy checked in` means the guarantee is documented in the ADR.
- `Enforced` means checked-in code implements it.
- `Proven` means a checked-in test asserts it.

## Current Snapshot

Snapshot date: `2026-05-28`

| Guarantee | Status | Notes |
| --- | --- | --- |
| Bearer token and `Authorization` never transmitted | Proven | Reporter never receives headers; integration test asserts absence. |
| Raw request headers never attached | Enforced | Reporter receives only method, path, status, elapsed, and opt-in params. |
| Request and response bodies not sent by default | Enforced | No body is passed to the reporter. |
| Path query values redacted by key | Enforced | `_strip_query` removes the query string; params are opt-in and scrubbed. |
| Default `scrub_keys` applied case-insensitively | Proven | `_effective_scrub_keys` always unions `MANDATORY_SCRUB_KEYS`. |
| Values redacted with `[redacted]` and truncated | Proven | `test_scrub_truncates_long_values` covers truncation. |
| `before_send` hook runs last | Proven | `test_before_send_can_drop_event` covers drop behavior. |
| Tests prove no token or PII leakage | Proven | `test_client_reports_api_error_without_leaking_token` and param scrub tests. |

## Current Blockers

- None. The scrubber is implemented and the guarantees are covered by tests.

## Current Conclusion

- The safety contract is enforced in `aryeo/sentry.py` and proven by
  `tests/test_sentry.py`.
- Treat the token and PII guarantees as verified in the working tree.
