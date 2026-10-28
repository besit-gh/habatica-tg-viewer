import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.formatters import format_inventory, format_profile, format_quest
from app.habitica_api import HabiticaAPI, HabiticaError
from app.keyboards import profile_sections_keyboard

router = Router()
logger = logging.getLogger(__name__)


async def _send_profile_section(
    target: Message | CallbackQuery, habitica_api: HabiticaAPI, section: str
) -> None:
    try:
        user = await habitica_api.get_user()
        text = {
            "stats": format_profile(user),
            "inventory": format_inventory(user),
            "quest": format_quest(user),
        }[section]
        if isinstance(target, CallbackQuery):
            if target.message:
                await target.message.answer(text, parse_mode="HTML", reply_markup=profile_sections_keyboard())
        else:
            await target.answer(text, parse_mode="HTML", reply_markup=profile_sections_keyboard())
    except HabiticaError as exc:
        logger.warning("Habitica profile request failed: %s", type(exc).__name__)
        if isinstance(target, CallbackQuery):
            if target.message:
                await target.message.answer("Не удалось загрузить данные Habitica. Попробуй позже; автоматического повтора нет.")
        else:
            await target.answer("Не удалось загрузить данные Habitica. Попробуй позже; автоматического повтора нет.")


@router.message(F.text == "посмотреть профиль")
async def profile(message: Message, state: FSMContext, habitica_api: HabiticaAPI) -> None:
    await state.clear()
    await _send_profile_section(message, habitica_api, "stats")


@router.callback_query(F.data.startswith("profile:"))
async def profile_section(callback: CallbackQuery, habitica_api: HabiticaAPI) -> None:
    await callback.answer()
    section = (callback.data or "").split(":", 1)[1]
    if section in {"stats", "inventory", "quest"}:
        await _send_profile_section(callback, habitica_api, section)
