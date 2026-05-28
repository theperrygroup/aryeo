# Sentry Reporting

The Aryeo client ships an optional, opt-in integration that reports client
errors and request breadcrumbs to Sentry. It is **enrich-only**: the client
never calls `sentry_sdk.init()` and does nothing unless your application has
already initialized Sentry.

## Install

```bash
pip install "aryeo[sentry]"
```

## Enable Reporting

Reporting is off by default. Your application owns Sentry initialization; the
client only attaches to it.

```python
import sentry_sdk
from aryeo import AryeoClient

sentry_sdk.init()  # owned by your application, never by the client

with AryeoClient(token="...", report_to_sentry=True) as client:
    client.orders.list(params={"page": 1})
```

You can also enable it from the environment:

```bash
export ARYEO_SENTRY_ENABLED=1
```

```python
from aryeo import AryeoClient

with AryeoClient.from_env() as client:
    client.orders.list(params={"page": 1})
```

## What Gets Reported

- `AryeoAPIError` and `AryeoRequestError` are captured with context tags such as
  `aryeo.request_method`, `aryeo.request_path`, `aryeo.status_code`, and
  `aryeo.api_code`.
- One breadcrumb per request records the method, path, status code, and elapsed
  time. Failed requests use the `error` level.

## Data Safety

The integration is safe by default:

- The bearer token and the `Authorization` header are never sent.
- Raw request headers are never attached.
- Request and response bodies are not sent.
- Query parameters are attached only when `include_params=True`, and sensitive
  keys are always redacted.

## Configure

Pass `SentryReportOptions` to tune behavior:

```python
from aryeo import AryeoClient, SentryReportOptions

options = SentryReportOptions(
    capture_exceptions=True,
    record_breadcrumbs=True,
    breadcrumb_level="info",
    extra_tags={"component": "aryeo-client"},
    include_params=False,
)

with AryeoClient(
    token="...",
    report_to_sentry=True,
    sentry_options=options,
) as client:
    client.listings.list(params={"page": 1})
```

When `sentry-sdk` is not installed or Sentry is not initialized, the client is a
no-op and behaves exactly as if reporting were off.
