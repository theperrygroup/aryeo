"""Unit and integration tests for enrich-only Sentry reporting."""

from __future__ import annotations

import httpx
import pytest

from aryeo import AryeoClient
from aryeo.exceptions import AryeoAPIError, AryeoRequestError
from aryeo.sentry import (
    SentryReporter,
    SentryReportOptions,
    _enter_scope,
    _import_sentry_sdk,
)


class _FakeScope:
    """Minimal stand-in for a Sentry scope context manager."""

    def __init__(self) -> None:
        """Initialize an empty tag store."""

        self.tags: dict[str, str] = {}

    def set_tag(self, key: str, value: str) -> None:
        """Record a tag set on the scope."""

        self.tags[key] = value

    def __enter__(self) -> "_FakeScope":
        """Enter the scope context."""

        return self

    def __exit__(self, *args: object) -> bool:
        """Exit the scope context without suppressing exceptions."""

        return False


class _FakeClient:
    """Minimal stand-in for a Sentry client."""

    def __init__(self, active: bool) -> None:
        """Store whether the fake client should report as active."""

        self._active = active

    def is_active(self) -> bool:
        """Return the configured active state."""

        return self._active


class _FakeSentrySdk:
    """Record interactions a reporter would have with ``sentry_sdk``."""

    def __init__(self, *, active: bool = True) -> None:
        """Initialize capture buffers.

        Args:
            active: Whether the fake Sentry client reports as active.
        """

        self.active = active
        self.init_called = False
        self.breadcrumbs: list[dict[str, object]] = []
        self.captured: list[BaseException] = []
        self.scopes: list[_FakeScope] = []

    def init(self, *args: object, **kwargs: object) -> None:
        """Record that init was called; the reporter must never do this."""

        self.init_called = True

    def get_client(self) -> _FakeClient:
        """Return a fake client mirroring the active state."""

        return _FakeClient(self.active)

    def add_breadcrumb(self, **kwargs: object) -> None:
        """Capture breadcrumb keyword arguments."""

        self.breadcrumbs.append(kwargs)

    def new_scope(self) -> _FakeScope:
        """Return and record a fresh fake scope."""

        scope = _FakeScope()
        self.scopes.append(scope)
        return scope

    def capture_exception(self, error: BaseException) -> None:
        """Capture an exception forwarded by the reporter."""

        self.captured.append(error)


@pytest.fixture
def fake_sentry(monkeypatch: pytest.MonkeyPatch) -> _FakeSentrySdk:
    """Patch the lazy importer to return an active fake Sentry SDK."""

    sdk = _FakeSentrySdk(active=True)
    monkeypatch.setattr("aryeo.sentry._import_sentry_sdk", lambda: sdk)
    return sdk


def _mock_response_client(
    status_code: int,
    body: object,
    *,
    report_to_sentry: bool = True,
    options: SentryReportOptions | None = None,
    token: str = "secret-token",
) -> AryeoClient:
    """Build a client whose transport returns a fixed response."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json=body, request=request)

    return AryeoClient(
        token=token,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
        report_to_sentry=report_to_sentry,
        sentry_options=options,
    )


def test_reporter_is_noop_when_sentry_sdk_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The reporter does nothing when ``sentry-sdk`` is not installed."""

    monkeypatch.setattr("aryeo.sentry._import_sentry_sdk", lambda: None)
    reporter = SentryReporter()

    assert reporter.is_active() is False
    reporter.record_request_breadcrumb(method="GET", path="/orders")
    reporter.capture_request_error(
        AryeoRequestError("boom"), method="GET", path="/orders"
    )


def test_reporter_is_noop_when_client_inactive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The reporter does nothing when no Sentry client is active."""

    sdk = _FakeSentrySdk(active=False)
    monkeypatch.setattr("aryeo.sentry._import_sentry_sdk", lambda: sdk)
    reporter = SentryReporter()

    assert reporter.is_active() is False
    reporter.record_request_breadcrumb(method="GET", path="/orders", status_code=200)
    reporter.capture_request_error(
        AryeoAPIError(500, "x"), method="GET", path="/orders", status_code=500
    )

    assert sdk.breadcrumbs == []
    assert sdk.captured == []


def test_reporter_records_breadcrumb(fake_sentry: _FakeSentrySdk) -> None:
    """A successful request records a scrubbed info-level breadcrumb."""

    reporter = SentryReporter()
    reporter.record_request_breadcrumb(
        method="GET",
        path="/orders?token=secret",
        status_code=200,
        elapsed_ms=12.3456,
    )

    assert len(fake_sentry.breadcrumbs) == 1
    crumb = fake_sentry.breadcrumbs[0]
    assert crumb["category"] == "aryeo.request"
    assert crumb["type"] == "http"
    assert crumb["level"] == "info"
    data = crumb["data"]
    assert isinstance(data, dict)
    assert data["method"] == "GET"
    assert data["path"] == "/orders"
    assert data["status_code"] == 200
    assert data["elapsed_ms"] == 12.346


def test_breadcrumb_uses_error_level_for_failures(
    fake_sentry: _FakeSentrySdk,
) -> None:
    """Failing requests record breadcrumbs at the error level."""

    reporter = SentryReporter()
    reporter.record_request_breadcrumb(method="GET", path="/orders", status_code=500)

    assert fake_sentry.breadcrumbs[0]["level"] == "error"


def test_capture_request_error_sets_scrubbed_tags(
    fake_sentry: _FakeSentrySdk,
) -> None:
    """Captured errors carry safe context tags and no secrets."""

    reporter = SentryReporter()
    error = AryeoAPIError(403, "Forbidden", api_code="forbidden")
    reporter.capture_request_error(
        error, method="DELETE", path="/orders/1", status_code=403
    )

    assert fake_sentry.captured == [error]
    assert len(fake_sentry.scopes) == 1
    tags = fake_sentry.scopes[0].tags
    assert tags["aryeo.request_method"] == "DELETE"
    assert tags["aryeo.request_path"] == "/orders/1"
    assert tags["aryeo.status_code"] == "403"
    assert tags["aryeo.api_code"] == "forbidden"


def test_reporter_never_calls_sentry_init(fake_sentry: _FakeSentrySdk) -> None:
    """The enrich-only reporter must never initialize Sentry."""

    reporter = SentryReporter()
    reporter.record_request_breadcrumb(method="GET", path="/orders", status_code=200)
    reporter.capture_request_error(
        AryeoAPIError(500, "x"), method="GET", path="/orders", status_code=500
    )

    assert fake_sentry.init_called is False


def test_breadcrumb_scrubs_included_params(fake_sentry: _FakeSentrySdk) -> None:
    """Opt-in params are attached only after sensitive keys are redacted."""

    reporter = SentryReporter(SentryReportOptions(include_params=True))
    reporter.record_request_breadcrumb(
        method="GET",
        path="/orders",
        status_code=200,
        params={"token": "secret", "page": 1, "email": "a@b.com"},
    )

    data = fake_sentry.breadcrumbs[0]["data"]
    assert isinstance(data, dict)
    params = data["params"]
    assert isinstance(params, dict)
    assert params["token"] == "[redacted]"
    assert params["email"] == "[redacted]"
    assert params["page"] == 1


def test_before_send_can_drop_event(fake_sentry: _FakeSentrySdk) -> None:
    """A ``before_send`` hook returning None drops the event."""

    reporter = SentryReporter(SentryReportOptions(before_send=lambda payload: None))
    reporter.record_request_breadcrumb(method="GET", path="/orders", status_code=200)
    reporter.capture_request_error(
        AryeoAPIError(500, "x"), method="GET", path="/orders", status_code=500
    )

    assert fake_sentry.breadcrumbs == []
    assert fake_sentry.captured == []


def test_disabled_toggles_record_nothing(fake_sentry: _FakeSentrySdk) -> None:
    """Disabling both toggles suppresses all Sentry interactions."""

    reporter = SentryReporter(
        SentryReportOptions(capture_exceptions=False, record_breadcrumbs=False)
    )
    reporter.record_request_breadcrumb(method="GET", path="/orders", status_code=200)
    reporter.capture_request_error(
        AryeoAPIError(500, "x"), method="GET", path="/orders", status_code=500
    )

    assert fake_sentry.breadcrumbs == []
    assert fake_sentry.captured == []


def test_client_reports_api_error_without_leaking_token(
    fake_sentry: _FakeSentrySdk,
) -> None:
    """An API error is captured with a breadcrumb and no token leakage."""

    client = _mock_response_client(500, {"message": "boom", "code": "server_error"})

    with pytest.raises(AryeoAPIError):
        client.request_json("GET", "/orders", params={"page": 1})

    assert len(fake_sentry.captured) == 1
    assert isinstance(fake_sentry.captured[0], AryeoAPIError)
    assert len(fake_sentry.breadcrumbs) == 1
    assert fake_sentry.breadcrumbs[0]["level"] == "error"
    assert "secret-token" not in repr(fake_sentry.breadcrumbs)
    assert "secret-token" not in repr([scope.tags for scope in fake_sentry.scopes])
    client.close()


def test_client_reports_request_error(fake_sentry: _FakeSentrySdk) -> None:
    """A transport failure is captured as an AryeoRequestError."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("no route", request=request)

    client = AryeoClient(
        token="secret-token",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
        report_to_sentry=True,
    )

    with pytest.raises(AryeoRequestError):
        client.request_json("GET", "/orders")

    assert len(fake_sentry.captured) == 1
    assert isinstance(fake_sentry.captured[0], AryeoRequestError)
    client.close()


def test_client_records_breadcrumb_on_success(
    fake_sentry: _FakeSentrySdk,
) -> None:
    """A successful request records a breadcrumb but captures nothing."""

    client = _mock_response_client(200, {"ok": True})

    result = client.request_json("GET", "/orders")

    assert result == {"ok": True}
    assert len(fake_sentry.breadcrumbs) == 1
    assert fake_sentry.breadcrumbs[0]["level"] == "info"
    assert fake_sentry.captured == []
    client.close()


def test_client_does_not_report_when_disabled(
    fake_sentry: _FakeSentrySdk,
) -> None:
    """With reporting off, no reporter exists and nothing is captured."""

    client = _mock_response_client(500, {"message": "boom"}, report_to_sentry=False)

    assert client._sentry_reporter is None
    with pytest.raises(AryeoAPIError):
        client.request_json("GET", "/orders")

    assert fake_sentry.captured == []
    client.close()


def test_from_env_enables_sentry_when_flag_truthy(
    fake_sentry: _FakeSentrySdk,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``ARYEO_SENTRY_ENABLED`` turns on reporting via ``from_env``."""

    monkeypatch.setenv("ARYEO_API_TOKEN", "env-token")
    monkeypatch.setenv("ARYEO_SENTRY_ENABLED", "true")

    client = AryeoClient.from_env()

    assert client._sentry_reporter is not None
    client.close()


def test_from_env_disables_sentry_by_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``from_env`` leaves reporting off when the flag is unset."""

    monkeypatch.setenv("ARYEO_API_TOKEN", "env-token")
    monkeypatch.delenv("ARYEO_SENTRY_ENABLED", raising=False)

    client = AryeoClient.from_env()

    assert client._sentry_reporter is None
    client.close()


def test_import_sentry_sdk_returns_module_or_none() -> None:
    """The lazy importer returns a usable module or ``None``."""

    module = _import_sentry_sdk()

    assert module is None or hasattr(module, "capture_exception")


def test_enter_scope_falls_back_to_push_scope() -> None:
    """``_enter_scope`` uses ``push_scope`` on SDKs without ``new_scope``."""

    class _PushOnlySdk:
        def __init__(self) -> None:
            self.push_called = False

        def push_scope(self) -> _FakeScope:
            self.push_called = True
            return _FakeScope()

    sdk = _PushOnlySdk()
    with _enter_scope(sdk):
        pass

    assert sdk.push_called is True


def test_is_active_is_false_when_get_client_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A Sentry module without ``get_client`` is treated as inactive."""

    class _NoGetClientSdk:
        pass

    monkeypatch.setattr("aryeo.sentry._import_sentry_sdk", lambda: _NoGetClientSdk())

    assert SentryReporter().is_active() is False


def test_is_active_is_false_when_get_client_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An exception while resolving the client is treated as inactive."""

    class _RaisingSdk:
        def get_client(self) -> object:
            raise RuntimeError("boom")

    monkeypatch.setattr("aryeo.sentry._import_sentry_sdk", lambda: _RaisingSdk())

    assert SentryReporter().is_active() is False


def test_scrub_truncates_long_values(fake_sentry: _FakeSentrySdk) -> None:
    """Long string values are truncated before reaching Sentry."""

    reporter = SentryReporter(SentryReportOptions(include_params=True))
    reporter.record_request_breadcrumb(
        method="GET",
        path="/orders",
        status_code=200,
        params={"note": "x" * 2000},
    )

    data = fake_sentry.breadcrumbs[0]["data"]
    assert isinstance(data, dict)
    params = data["params"]
    assert isinstance(params, dict)
    assert params["note"].endswith("...")
    assert len(params["note"]) == 1024 + 3
