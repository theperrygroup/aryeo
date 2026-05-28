"""Example: enrich-only Sentry reporting with the Aryeo client.

Install the optional dependency first::

    pip install "aryeo[sentry]"

Your application owns ``sentry_sdk.init``. The Aryeo client never initializes
Sentry; it only adds breadcrumbs and captures client errors into an
already-initialized Sentry SDK when reporting is enabled.
"""

from __future__ import annotations

import os

from aryeo import AryeoClient, SentryReportOptions


def _init_sentry() -> None:
    """Initialize Sentry when it is installed.

    Real applications own this call. It lives here only so the example is
    self-contained.
    """

    try:
        import sentry_sdk
    except ImportError:
        return
    sentry_sdk.init(traces_sample_rate=0.0)


def main() -> None:
    """Run reported reads using explicit options and env-driven opt-in."""

    _init_sentry()

    options = SentryReportOptions(extra_tags={"component": "aryeo-client"})
    token = os.getenv("ARYEO_API_TOKEN")
    with AryeoClient(
        token=token,
        report_to_sentry=True,
        sentry_options=options,
    ) as client:
        client.orders.list(params={"page": 1, "per_page": 5})

    # Or enable reporting from the environment via ARYEO_SENTRY_ENABLED:
    with AryeoClient.from_env() as client:
        client.listings.list(params={"page": 1, "per_page": 5})


if __name__ == "__main__":
    main()
