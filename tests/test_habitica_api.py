from typing import Any

import pytest

from app.habitica_api import HabiticaAPI, HabiticaError


class FakeResponse:
    def __init__(self, status: int, body: dict[str, Any]) -> None:
        self.status = status
        self.body = body

    async def __aenter__(self) -> "FakeResponse":
        return self

    async def __aexit__(self, *_: object) -> None:
        return None

    async def json(self, content_type: str | None = None) -> dict[str, Any]:
        return self.body


class FakeSession:
    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.calls = 0

    def request(self, *_: Any, **__: Any) -> FakeResponse:
        self.calls += 1
        return self.response


@pytest.mark.asyncio
async def test_request_returns_data_from_success_response() -> None:
    api = HabiticaAPI("user", "token", "user-test")
    session = FakeSession(FakeResponse(200, {"success": True, "data": {"name": "Hero"}}))
    api._session = session  # type: ignore[assignment]
    api.MIN_REQUEST_INTERVAL = 0

    result = await api.request("GET", "/user")

    assert result == {"name": "Hero"}
    assert session.calls == 1


@pytest.mark.asyncio
async def test_api_error_is_not_retried() -> None:
    api = HabiticaAPI("user", "token", "user-test")
    session = FakeSession(FakeResponse(429, {"success": False, "message": "Rate limited"}))
    api._session = session  # type: ignore[assignment]
    api.MIN_REQUEST_INTERVAL = 0

    with pytest.raises(HabiticaError):
        await api.request("GET", "/user")

    assert session.calls == 1
