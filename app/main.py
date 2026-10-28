import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

from app.config import load_settings
from app.habitica_api import HabiticaAPI, HabiticaError
from app.handlers.common import AllowlistMiddleware
from app.handlers.profile import router as profile_router
from app.handlers.tasks import router as tasks_router
from app.keyboards import MAIN_MENU


async def main() -> None:
    settings = load_settings()
    logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO),
                        format="%(asctime)s %(levelname)s %(name)s %(message)s")
    bot = Bot(token=settings.telegram_bot_token.get_secret_value())
    dp = Dispatcher(storage=MemoryStorage())
    dp.message.middleware(AllowlistMiddleware(settings.allowed_telegram_user_id))
    dp.callback_query.middleware(AllowlistMiddleware(settings.allowed_telegram_user_id))
    api = HabiticaAPI(settings.habitica_user_id, settings.habitica_api_token.get_secret_value(), settings.habitica_x_client)
    dp["habitica_api"] = api

    @dp.message(CommandStart())
    async def start(message: Message) -> None:
        try:
            await api.get_user()
            status = "подключение к Habitica работает"
        except HabiticaError as exc:
            logging.getLogger(__name__).warning("/start Habitica check failed: %s", type(exc).__name__)
            status = "Habitica пока недоступна; меню остаётся доступным"
        await message.answer(f"Habitica Companion запущен.\nСтатус: {status}", reply_markup=MAIN_MENU)

    @dp.message(Command("cancel"))
    async def cancel(message: Message, state: FSMContext) -> None:
        await state.clear()
        await message.answer("Текущий ввод отменён.", reply_markup=MAIN_MENU)

    dp.include_router(profile_router)
    dp.include_router(tasks_router)
    async with api:
        try:
            await api.get_user()
            logging.getLogger(__name__).info("Habitica startup check succeeded")
        except HabiticaError as exc:
            logging.getLogger(__name__).warning("Habitica startup check failed: %s", type(exc).__name__)
        try:
            await dp.start_polling(bot)
        finally:
            await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
