from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="посмотреть профиль"), KeyboardButton(text="задания")],
        [KeyboardButton(text="создать задачу"), KeyboardButton(text="отправить уведомление по задаче")],
    ],
    resize_keyboard=True,
)


def task_types_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Привычки", callback_data="list:habits"),
                InlineKeyboardButton(text="Ежедневные", callback_data="list:dailys"),
            ],
            [
                InlineKeyboardButton(text="Разовые", callback_data="list:todos"),
                InlineKeyboardButton(text="Награды", callback_data="list:rewards"),
            ],
            [InlineKeyboardButton(text="Выполненные разовые", callback_data="list:completedTodos")],
        ]
    )


def task_list_keyboard(
    tasks: list[dict], task_type: str, offset: int, total: int
) -> InlineKeyboardMarkup:
    rows = []
    for task in tasks:
        title = str(task.get("text") or "Без названия").replace("\n", " ")[:45]
        task_id = task.get("_id") or task.get("id")
        rows.append([InlineKeyboardButton(text=title, callback_data=f"task:{task_type}:{task_id}")])
    navigation = []
    if offset > 0:
        navigation.append(InlineKeyboardButton(text="← Назад", callback_data=f"page:{task_type}:{max(0, offset - 10)}"))
    if offset + len(tasks) < total:
        navigation.append(InlineKeyboardButton(text="Далее →", callback_data=f"page:{task_type}:{offset + 10}"))
    if navigation:
        rows.append(navigation)
    rows.append([InlineKeyboardButton(text="Фильтры", callback_data=f"filters:{task_type}")])
    rows.append([InlineKeyboardButton(text="Поиск по названию", callback_data=f"search:{task_type}")])
    rows.append([InlineKeyboardButton(text="← К типам заданий", callback_data="tasks:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def task_actions_keyboard(task_id: str, task_type: str) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text="Отправить карточку", callback_data=f"notify:{task_type}:{task_id}")]]
    if task_type not in {"completedTodos", "rewards"}:
        rows.append([InlineKeyboardButton(text="Выполнено (+)", callback_data=f"complete:{task_type}:{task_id}")])
        rows.append([InlineKeyboardButton(text="Изменить название", callback_data=f"edit:{task_type}:{task_id}")])
    rows.extend([
        [InlineKeyboardButton(text="Удалить…", callback_data=f"deleteask:{task_type}:{task_id}")],
        [InlineKeyboardButton(text="← К списку", callback_data=f"list:{task_type}")],
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def delete_confirmation_keyboard(task_id: str, task_type: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Да, удалить", callback_data=f"delete:{task_type}:{task_id}"),
        InlineKeyboardButton(text="Отмена", callback_data=f"task:{task_type}:{task_id}"),
    ]])


def task_filter_keyboard(task_type: str) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text="Все", callback_data=f"filter:{task_type}:all")]]
    if task_type not in {"rewards", "completedTodos"}:
        rows.extend([
            [InlineKeyboardButton(text="Выполненные", callback_data=f"filter:{task_type}:completed")],
            [InlineKeyboardButton(text="Не выполненные", callback_data=f"filter:{task_type}:pending")],
        ])
    if task_type != "completedTodos":
        rows.extend([
            [InlineKeyboardButton(text="Лёгкая сложность", callback_data=f"filter:{task_type}:priority:1")],
            [InlineKeyboardButton(text="Средняя сложность", callback_data=f"filter:{task_type}:priority:1.5")],
            [InlineKeyboardButton(text="Сложная", callback_data=f"filter:{task_type}:priority:2")],
        ])
    rows.append([InlineKeyboardButton(text="← К списку", callback_data=f"list:{task_type}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def profile_sections_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Статы", callback_data="profile:stats"),
         InlineKeyboardButton(text="Инвентарь", callback_data="profile:inventory")],
        [InlineKeyboardButton(text="Квест / группа", callback_data="profile:quest")],
    ])
