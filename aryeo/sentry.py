"""Optional, enrich-only Sentry reporting for the Aryeo client.

This module cooperates with a Sentry SDK that the consuming application has
already initialized. It never calls :func:`sentry_sdk.init` and silently does
nothing when ``sentry-sdk`` is not installed or when no Sentry client is active
in the current scope.

Install the optional dependency with::

    pip install "aryeo[sentry]"

The reporter is wired into the client through the ``report_to_sentry`` flag and
the optional :class:`SentryReportOptions` configuration object. By default the
client does not report anything.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from aryeo.exceptions import AryeoAPIError, AryeoError

BREADCRUMB_CATEGORY = "aryeo.request"
REDACTED = "[redacted]"
MAX_VALUE_LENGTH = 1024

MANDATORY_SCRUB_KEYS: frozenset[str] = frozenset(
    {
        "authorization",
        "token",
        "access_token",
        "api_key",
        "apikey",
        "password",
        "secret",
        "cookie",
        "set-cookie",
    }
)
DEFAULT_SCRUB_KEYS: frozenset[str] = MANDATORY_SCRUB_KEYS | frozenset(
    {"email", "phone"}
)


def _import_sentry_sdk() -> Any:
    """Import ``sentry_sdk`` lazily.

    Returns:
        The imported ``sentry_sdk`` module, or ``None`` when it is not
        installed. Importing :mod:`aryeo` never imports ``sentry_sdk`` at module
        load because this function is only called on demand.
    """

    try:
        import sentry_sdk
    except ImportError:
        return None
    return sentry_sdk


def _strip_query(path: str) -> str:
    """Return the request path without its query string.

    Args:
        path: Request path that may contain a query string.

    Returns:
        The path with any ``?`` suffix removed.
    """

    return path.split("?", 1)[0]


def _scrub_value(value: Any) -> Any:
    """Truncate overly long string values before sending them to Sentry.

    Args:
        value: Arbitrary value pulled from request context.

    Returns:
        The original value, or a truncated copy for long strings.
    """

    if isinstance(value, str) and len(value) > MAX_VALUE_LENGTH:
        return f"{value[:MAX_VALUE_LENGTH]}..."
    return value


def _scrub_mapping(
    data: Mapping[str, Any],
    scrub_keys: frozenset[str],
) -> dict[str, Any]:
    """Redact sensitive keys and truncate values in a mapping.

    Args:
        data: Mapping whose values may contain secrets or PII.
        scrub_keys: Lower-cased keys whose values must be redacted.

    Returns:
        A new mapping that is safe to attach to Sentry events.
    """

    result: dict[str, Any] = {}
    for key, value in data.items():
        if key.lower() in scrub_keys:
            result[key] = REDACTED
        elif isinstance(value, Mapping):
            result[key] = _scrub_mapping(value, scrub_keys)
        else:
            result[key] = _scrub_value(value)
    return result


def _enter_scope(sentry_sdk: Any) -> Any:
    """Return a fresh Sentry scope context manager across SDK versions.

    Args:
        sentry_sdk: The imported ``sentry_sdk`` module.

    Returns:
        A context manager yielding an isolated Sentry scope.
    """

    new_scope = getattr(sentry_sdk, "new_scope", None)
    if new_scope is not None:
        return new_scope()
    return sentry_sdk.push_scope()


@dataclass(frozen=True)
class SentryReportOptions:
    """Configuration for enrich-only Sentry reporting.

    Attributes:
        capture_exceptions: Whether to capture Aryeo client exceptions.
        record_breadcrumbs: Whether to record a breadcrumb per request.
        breadcrumb_level: Breadcrumb level for successful requests. Failed
            requests always use the ``error`` level.
        extra_tags: Additional static tags attached to captured events.
        scrub_keys: Keys whose values are redacted. Credential keys are always
            scrubbed even if they are removed from this set.
        include_params: Whether to attach scrubbed query parameters to
            breadcrumbs. Disabled by default.
        before_send: Optional hook that receives the scrubbed payload mapping
            and returns a modified mapping, or ``None`` to drop the event.
    """

    capture_exceptions: bool = True
    record_breadcrumbs: bool = True
    breadcrumb_level: str = "info"
    extra_tags: Mapping[str, str] | None = None
    scrub_keys: frozenset[str] = DEFAULT_SCRUB_KEYS
    include_params: bool = False
    before_send: Callable[[dict[str, Any]], dict[str, Any] | None] | None = None


class SentryReporter:
    """Forward Aryeo client errors and breadcrumbs to an active Sentry SDK.

    The reporter is enrich-only. It never initializes Sentry and becomes a
    no-op when ``sentry-sdk`` is missing or no Sentry client is active.
    """

    def __init__(self, options: SentryReportOptions | None = None) -> None:
        """Initialize the reporter.

        Args:
            options: Optional reporting configuration. Defaults are used when
                omitted.
        """

        self.options = options or SentryReportOptions()
        self._sentry_sdk = _import_sentry_sdk()

    def is_active(self) -> bool:
        """Return whether an initialized Sentry client is available.

        Returns:
            ``True`` only when ``sentry-sdk`` is importable and a Sentry client
            is active in the current scope.
        """

        sentry_sdk = self._sentry_sdk
        if sentry_sdk is None:
            return False
        get_client = getattr(sentry_sdk, "get_client", None)
        if get_client is None:
            return False
        try:
            client = get_client()
            return bool(client.is_active())
        except Exception:
            return False

    def _effective_scrub_keys(self) -> frozenset[str]:
        """Return the lower-cased scrub keys, always including credentials."""

        configured = frozenset(key.lower() for key in self.options.scrub_keys)
        return configured | MANDATORY_SCRUB_KEYS

    def _apply_before_send(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Run the optional ``before_send`` hook over a payload mapping.

        Args:
            payload: Already-scrubbed payload mapping.

        Returns:
            The payload to send, or ``None`` to drop the event.
        """

        hook = self.options.before_send
        if hook is None:
            return payload
        return hook(payload)

    def record_request_breadcrumb(
        self,
        *,
        method: str,
        path: str,
        status_code: int | None = None,
        elapsed_ms: float | None = None,
        params: Mapping[str, Any] | None = None,
    ) -> None:
        """Record a scrubbed breadcrumb describing one request.

        Args:
            method: HTTP method of the request.
            path: Request path. The query string is removed before sending.
            status_code: HTTP status code, when a response was received.
            elapsed_ms: Elapsed time in milliseconds, when measured.
            params: Optional query parameters, attached only when
                ``include_params`` is enabled and after scrubbing.
        """

        if not self.options.record_breadcrumbs or not self.is_active():
            return

        data: dict[str, Any] = {"method": method, "path": _strip_query(path)}
        if status_code is not None:
            data["status_code"] = status_code
        if elapsed_ms is not None:
            data["elapsed_ms"] = round(elapsed_ms, 3)
        if self.options.include_params and params:
            data["params"] = dict(params)

        payload = self._apply_before_send(
            _scrub_mapping(data, self._effective_scrub_keys())
        )
        if payload is None:
            return

        is_failure = status_code is not None and status_code >= 400
        level = "error" if is_failure else self.options.breadcrumb_level
        self._sentry_sdk.add_breadcrumb(
            category=BREADCRUMB_CATEGORY,
            type="http",
            level=level,
            data=payload,
        )

    def capture_request_error(
        self,
        error: AryeoError,
        *,
        method: str,
        path: str,
        status_code: int | None = None,
    ) -> None:
        """Capture an Aryeo client exception with scrubbed context tags.

        Args:
            error: The exception being raised by the client.
            method: HTTP method of the failing request.
            path: Request path. The query string is removed before sending.
            status_code: HTTP status code, when a response was received.
        """

        if not self.options.capture_exceptions or not self.is_active():
            return

        tags: dict[str, Any] = {
            "aryeo.request_method": method,
            "aryeo.request_path": _strip_query(path),
        }
        if status_code is not None:
            tags["aryeo.status_code"] = status_code
        if isinstance(error, AryeoAPIError) and error.api_code:
            tags["aryeo.api_code"] = error.api_code
        if self.options.extra_tags:
            tags.update(self.options.extra_tags)

        payload = self._apply_before_send(
            _scrub_mapping(tags, self._effective_scrub_keys())
        )
        if payload is None:
            return

        sentry_sdk = self._sentry_sdk
        with _enter_scope(sentry_sdk) as scope:
            for key, value in payload.items():
                scope.set_tag(key, str(value))
            sentry_sdk.capture_exception(error)


__all__ = [
    "DEFAULT_SCRUB_KEYS",
    "MANDATORY_SCRUB_KEYS",
    "SentryReportOptions",
    "SentryReporter",
]
