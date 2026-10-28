from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject


class AllowlistMiddleware(BaseMiddleware):
    def __init__(self, allowed_user_id: int) -> None:
        self.allowed_user_id = allowed_user_id

    async def __call__(self, handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]], event: TelegramObject, data: dict[str, Any]) -> Any:
        user = getattr(event, "from_user", None)
        if user is None or user.id != self.allowed_user_id:
            if isinstance(event, Message):
                await event.answer("Доступ запрещён.")
            elif isinstance(event, CallbackQuery):
                await event.answer("Доступ запрещён.", show_alert=True)
            return None
        return await handler(event, data)
