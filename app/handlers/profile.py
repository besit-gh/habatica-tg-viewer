import logging

from aiogram import F, Router
from aiogram.types import Message

from app.formatters import format_profile
from app.habitica_api import HabiticaAPI, HabiticaError

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text == "посмотреть профиль")
async def profile(message: Message, habitica_api: HabiticaAPI) -> None:
    try:
        user = await habitica_api.get_user()
        await message.answer(format_profile(user), parse_mode="HTML")
    except HabiticaError as exc:
        logger.warning("Habitica profile request failed: %s", type(exc).__name__)
        await message.answer("Не удалось загрузить профиль Habitica. Проверь соединение и попробуй позже; автоматического повтора нет.")
