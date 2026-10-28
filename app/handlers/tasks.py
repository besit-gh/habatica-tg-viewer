import logging
from typing import Any

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.formatters import format_task, task_type_label
from app.habitica_api import HabiticaAPI, HabiticaError
from app.keyboards import delete_confirmation_keyboard, task_actions_keyboard, task_list_keyboard, task_types_keyboard

router = Router()
logger = logging.getLogger(__name__)
VALID_TYPES = {"habits", "dailys", "todos", "rewards", "completedTodos"}


class TaskForm(StatesGroup):
    create_type = State()
    create_title = State()
    create_notes = State()
    edit_title = State()
    search_name = State()


async def _safe_error(target: Message | CallbackQuery, exc: Exception) -> None:
    logger.warning("Habitica task operation failed: %s", type(exc).__name__)
    text = "Habitica API не выполнил операцию. Автоматического повтора нет; обнови данные и проверь состояние задачи."
    if isinstance(target, CallbackQuery):
        await target.answer("Запрос не выполнен", show_alert=True)
        if target.message:
            await target.message.answer(text)
    else:
        await target.answer(text)


@router.message(F.text == "задания")
async def open_tasks(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Выбери тип заданий:", reply_markup=task_types_keyboard())


@router.message(F.text == "отправить уведомление по задаче")
async def notify_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Выбери тип задачи, карточку которой отправить:", reply_markup=task_types_keyboard())


@router.callback_query(F.data == "tasks:menu")
async def tasks_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.clear()
    if callback.message:
        await callback.message.answer("Выбери тип заданий:", reply_markup=task_types_keyboard())


@router.callback_query(F.data.startswith("list:") | F.data.startswith("page:"))
async def list_tasks(callback: CallbackQuery, state: FSMContext, habitica_api: HabiticaAPI) -> None:
    await callback.answer()
    parts = (callback.data or "").split(":")
    task_type = parts[1] if len(parts) > 1 else ""
    try:
        offset = max(0, int(parts[2])) if parts[0] == "page" and len(parts) == 3 else 0
    except ValueError:
        offset = 0
    if task_type not in VALID_TYPES:
        return
    await state.clear()
    try:
        all_tasks = await habitica_api.get_tasks(task_type)
        total = len(all_tasks)
        tasks = all_tasks[offset:offset + 10]
        for task in tasks:
            task["_type"] = task_type
            task["_id"] = task.get("_id") or task.get("id")
        if not total:
            if callback.message:
                await callback.message.answer(f"В разделе «{task_type_label(task_type)}» пока нет заданий.")
            return
        if callback.message:
            await callback.message.answer(
                f"{task_type_label(task_type)} — {offset + 1}–{min(offset + len(tasks), total)} из {total}:",
                reply_markup=task_list_keyboard(tasks, task_type, offset, total),
            )
    except HabiticaError as exc:
        await _safe_error(callback, exc)


@router.callback_query(F.data.startswith("search:"))
async def start_search(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    task_type = (callback.data or "").split(":", 1)[1]
    if task_type not in VALID_TYPES:
        return
    await state.clear()
    await state.set_state(TaskForm.search_name)
    await state.update_data(search_type=task_type)
    if callback.message:
        await callback.message.answer("Введи часть названия для поиска. Для отмены — /cancel.")


@router.message(TaskForm.search_name)
async def search_tasks(message: Message, state: FSMContext, habitica_api: HabiticaAPI) -> None:
    query = (message.text or "").strip()
    if query == "/cancel":
        await state.clear()
        await message.answer("Поиск отменён.")
        return
    if not query:
        await message.answer("Введи непустую строку для поиска.")
        return
    data = await state.get_data()
    task_type = data["search_type"]
    try:
        all_tasks = await habitica_api.get_tasks(task_type)
        matches = [task for task in all_tasks if query.casefold() in str(task.get("text", "")).casefold()]
        await state.clear()
        if not matches:
            await message.answer("Совпадений не найдено.")
            return
        for task in matches[:15]:
            task["_type"] = task_type
            task["_id"] = task.get("_id") or task.get("id")
        buttons = [
            [InlineKeyboardButton(text=str(task.get("text") or "Без названия")[:45],
                                  callback_data=f"task:{task_type}:{task.get('_id')}")]
            for task in matches[:15]
        ]
        buttons.append([InlineKeyboardButton(text="← К списку", callback_data=f"list:{task_type}")])
        await message.answer(
            f"Найдено: {len(matches)}. Показаны первые {min(15, len(matches))}.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        )
    except HabiticaError as exc:
        await _safe_error(message, exc)


@router.callback_query(F.data.startswith("task:"))
async def show_task(callback: CallbackQuery, habitica_api: HabiticaAPI) -> None:
    await callback.answer()
    parts = (callback.data or "").split(":", 2)
    if len(parts) != 3 or parts[1] not in VALID_TYPES:
        return
    try:
        task = await habitica_api.get_task(parts[2])
        if callback.message:
            await callback.message.answer(format_task(task, parts[1]), reply_markup=task_actions_keyboard(parts[2], parts[1]), parse_mode="HTML")
    except HabiticaError as exc:
        await _safe_error(callback, exc)


@router.callback_query(F.data.startswith("notify:"))
async def notify_task(callback: CallbackQuery, habitica_api: HabiticaAPI) -> None:
    await callback.answer()
    parts = (callback.data or "").split(":", 2)
    if len(parts) != 3 or parts[1] not in VALID_TYPES:
        return
    try:
        task = await habitica_api.get_task(parts[2])
        if callback.message:
            await callback.message.answer("📌 Карточка задачи\n" + format_task(task, parts[1]), parse_mode="HTML")
    except HabiticaError as exc:
        await _safe_error(callback, exc)


@router.callback_query(F.data.startswith("complete:"))
async def complete_task(callback: CallbackQuery, habitica_api: HabiticaAPI) -> None:
    await callback.answer()
    parts = (callback.data or "").split(":", 2)
    if len(parts) != 3 or parts[1] not in VALID_TYPES:
        return
    try:
        current = await habitica_api.get_task(parts[2])
        if parts[1] == "todos" and current.get("completed"):
            if callback.message:
                await callback.message.answer("Задача уже выполнена. Повторное начисление не выполнено.")
            return
        result = await habitica_api.score_task(parts[2], "up")
        task = result if isinstance(result, dict) and result.get("text") else await habitica_api.get_task(parts[2])
        if callback.message:
            await callback.message.answer("Действие выполнено.\n" + format_task(task, parts[1]), parse_mode="HTML")
    except HabiticaError as exc:
        await _safe_error(callback, exc)


@router.callback_query(F.data.startswith("deleteask:"))
async def ask_delete(callback: CallbackQuery, habitica_api: HabiticaAPI) -> None:
    await callback.answer()
    parts = (callback.data or "").split(":", 2)
    if len(parts) != 3 or parts[1] not in VALID_TYPES:
        return
    try:
        task = await habitica_api.get_task(parts[2])
        if callback.message:
            await callback.message.answer("Подтверди удаление:\n" + format_task(task, parts[1]), reply_markup=delete_confirmation_keyboard(parts[2], parts[1]), parse_mode="HTML")
    except HabiticaError as exc:
        await _safe_error(callback, exc)


@router.callback_query(F.data.startswith("delete:"))
async def delete_task(callback: CallbackQuery, habitica_api: HabiticaAPI) -> None:
    await callback.answer()
    parts = (callback.data or "").split(":", 2)
    if len(parts) != 3 or parts[1] not in VALID_TYPES:
        return
    try:
        await habitica_api.get_task(parts[2])
        await habitica_api.delete_task(parts[2])
        if callback.message:
            await callback.message.answer("Задача удалена. Выбери «задания», чтобы обновить список.")
    except HabiticaError as exc:
        await _safe_error(callback, exc)


@router.callback_query(F.data.startswith("edit:"))
async def begin_edit(callback: CallbackQuery, state: FSMContext, habitica_api: HabiticaAPI) -> None:
    await callback.answer()
    parts = (callback.data or "").split(":", 2)
    if len(parts) != 3 or parts[1] not in VALID_TYPES:
        return
    try:
        task = await habitica_api.get_task(parts[2])
        await state.clear()
        await state.set_state(TaskForm.edit_title)
        await state.update_data(task_id=parts[2], task_type=parts[1])
        if callback.message:
            await callback.message.answer(f"Текущее название: {task.get('text', '')}\nОтправь новое название или /cancel.")
    except HabiticaError as exc:
        await _safe_error(callback, exc)


@router.message(TaskForm.edit_title)
async def save_edit(message: Message, state: FSMContext, habitica_api: HabiticaAPI) -> None:
    title = (message.text or "").strip()
    if title in {"/cancel", "Отмена"}:
        await state.clear()
        await message.answer("Изменение отменено.")
        return
    if not title or len(title) > 250:
        await message.answer("Название должно содержать от 1 до 250 символов.")
        return
    data = await state.get_data()
    try:
        await habitica_api.get_task(data["task_id"])
        task = await habitica_api.update_task(data["task_id"], {"text": title})
        await state.clear()
        if not task.get("text"):
            task = await habitica_api.get_task(data["task_id"])
        await message.answer("Название обновлено.\n" + format_task(task, data["task_type"]), parse_mode="HTML")
    except HabiticaError as exc:
        await _safe_error(message, exc)


@router.message(F.text == "создать задачу")
async def create_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(TaskForm.create_type)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Привычка", callback_data="newtype:habits"), InlineKeyboardButton(text="Ежедневное", callback_data="newtype:dailys")],
        [InlineKeyboardButton(text="Разовое", callback_data="newtype:todos"), InlineKeyboardButton(text="Награда", callback_data="newtype:rewards")],
    ])
    await message.answer("Выбери тип новой задачи:", reply_markup=kb)


@router.callback_query(F.data.startswith("newtype:"))
async def create_type(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    task_type = (callback.data or "").split(":", 1)[1]
    if task_type not in VALID_TYPES:
        return
    await state.set_state(TaskForm.create_title)
    await state.update_data(create_type=task_type)
    if callback.message:
        await callback.message.answer("Введи название задачи (1–250 символов). Для отмены отправь /cancel.")


@router.message(TaskForm.create_title)
async def create_title(message: Message, state: FSMContext) -> None:
    title = (message.text or "").strip()
    if title == "/cancel":
        await state.clear()
        await message.answer("Создание отменено.")
        return
    if not title or len(title) > 250:
        await message.answer("Название должно содержать от 1 до 250 символов.")
        return
    await state.update_data(create_title=title)
    await state.set_state(TaskForm.create_notes)
    await message.answer("Введи описание или отправь «-», чтобы оставить пустым. Для отмены — /cancel.")


@router.message(TaskForm.create_notes)
async def create_notes(message: Message, state: FSMContext, habitica_api: HabiticaAPI) -> None:
    notes = (message.text or "").strip()
    if notes == "/cancel":
        await state.clear()
        await message.answer("Создание отменено.")
        return
    data = await state.get_data()
    payload: dict[str, Any] = {"type": data["create_type"], "text": data["create_title"]}
    if notes and notes != "-":
        payload["notes"] = notes
    try:
        task = await habitica_api.create_task(payload)
        await state.clear()
        if not task.get("text"):
            await message.answer("Задача создана. Нажми «задания», чтобы обновить список.")
        else:
            await message.answer("Задача создана.\n" + format_task(task, data["create_type"]), parse_mode="HTML")
    except HabiticaError as exc:
        await _safe_error(message, exc)
