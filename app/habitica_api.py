"""Async Habitica API client with conservative request spacing."""

import asyncio
import time
from typing import Any

import aiohttp


class HabiticaError(RuntimeError):
    def __init__(self, message: str, status: int | None = None) -> None:
        super().__init__(message)
        self.status = status


class HabiticaAPI:
    BASE_URL = "https://habitica.com/api/v3"
    MIN_REQUEST_INTERVAL = 30.0

    def __init__(self, user_id: str, api_token: str, client_header: str) -> None:
        self._headers = {"x-api-user": user_id, "x-api-key": api_token, "x-client": client_header,
                         "accept": "application/json", "content-type": "application/json"}
        self._session: aiohttp.ClientSession | None = None
        self._lock = asyncio.Lock()
        self._last_request_at = 0.0

    async def __aenter__(self) -> "HabiticaAPI":
        self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20), headers=self._headers)
        return self

    async def __aexit__(self, *_: object) -> None:
        if self._session is not None:
            await self._session.close()
            self._session = None

    async def request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
        if self._session is None:
            raise RuntimeError("HabiticaAPI must be used as an async context manager")
        async with self._lock:
            delay = self.MIN_REQUEST_INTERVAL - (time.monotonic() - self._last_request_at)
            if self._last_request_at and delay > 0:
                await asyncio.sleep(delay)
            self._last_request_at = time.monotonic()
            try:
                async with self._session.request(method, f"{self.BASE_URL}{path}", json=payload) as response:
                    try:
                        body = await response.json(content_type=None)
                    except (aiohttp.ContentTypeError, ValueError):
                        body = {}
                    if response.status >= 400 or body.get("success") is False:
                        raise HabiticaError(str(body.get("message") or f"Habitica API HTTP {response.status}"), response.status)
                    return body.get("data", body)
            except asyncio.TimeoutError as exc:
                raise HabiticaError("Habitica API timed out; refresh data before retrying a mutation") from exc
            except aiohttp.ClientError as exc:
                raise HabiticaError("Could not connect to Habitica API") from exc

    async def get_user(self) -> dict[str, Any]:
        return await self.request("GET", "/user")

    async def get_tasks(self, task_type: str) -> list[dict[str, Any]]:
        data = await self.request("GET", f"/tasks/user?type={task_type}")
        return data if isinstance(data, list) else []

    async def get_task(self, task_id: str) -> dict[str, Any]:
        return await self.request("GET", f"/tasks/{task_id}")

    async def create_task(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self.request("POST", "/tasks/user", payload)

    async def update_task(self, task_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return await self.request("PUT", f"/tasks/{task_id}", payload)

    async def score_task(self, task_id: str, direction: str = "up") -> dict[str, Any]:
        if direction not in {"up", "down"}:
            raise ValueError("direction must be 'up' or 'down'")
        return await self.request("POST", f"/tasks/{task_id}/score/{direction}")

    async def delete_task(self, task_id: str) -> Any:
        return await self.request("DELETE", f"/tasks/{task_id}")
