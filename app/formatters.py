from typing import Any


def _escape(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def task_type_label(task_type: str) -> str:
    return {"habits": "Привычка", "dailys": "Ежедневное задание", "todos": "Разовое задание", "rewards": "Награда", "completedTodos": "Выполненное"}.get(task_type, task_type)


def format_task(task: dict[str, Any], task_type: str | None = None) -> str:
    lines = [f"<b>{_escape(str(task.get('text') or 'Без названия'))}</b>"]
    if task_type:
        lines.append(f"Тип: {task_type_label(task_type)}")
    if task.get("notes"):
        lines.append(f"Описание: {_escape(str(task['notes']))}")
    if task.get("priority") is not None:
        try:
            priority = {0.1: "Пустяковая", 1.0: "Лёгкая", 1.5: "Средняя", 2.0: "Сложная"}.get(float(task["priority"]), str(task["priority"]))
        except (TypeError, ValueError):
            priority = str(task["priority"])
        lines.append(f"Сложность: {priority}")
    if task.get("completed") is not None:
        lines.append(f"Статус: {'выполнено' if task['completed'] else 'не выполнено'}")
    for key, label in (("dueDate", "Срок"), ("streak", "Серия"), ("value", "Текущий счёт")):
        if task.get(key) is not None:
            lines.append(f"{label}: {_escape(str(task[key]))}")
    tags = task.get("tags")
    if isinstance(tags, list) and tags:
        lines.append("Теги: " + ", ".join(_escape(str(t.get("name", t))) if isinstance(t, dict) else _escape(str(t)) for t in tags))
    return "\n".join(lines)


def format_profile(user: dict[str, Any]) -> str:
    profile, stats = user.get("profile") or {}, user.get("stats") or {}
    lines = ["<b>Профиль Habitica</b>"]
    if profile.get("name"):
        lines.append(f"Имя: {_escape(str(profile['name']))}")
    for key, label in (("lvl", "Уровень"), ("exp", "Опыт"), ("gp", "Золото"), ("hp", "Здоровье"), ("mp", "Мана"), ("toNextLevel", "До следующего уровня")):
        if stats.get(key) is not None:
            lines.append(f"{label}: {stats[key]}")
    if stats.get("class"):
        lines.append(f"Класс: {_escape(str(stats['class']))}")
    return "\n".join(lines)


def format_inventory(user: dict[str, Any]) -> str:
    items = user.get("items") or user.get("inventory") or {}
    lines = ["<b>Инвентарь Habitica</b>"]
    if not isinstance(items, dict):
        return "\\n".join(lines + ["Данные инвентаря недоступны в ответе API."])
    equipment = items.get("gear") or {}
    equipped = equipment.get("equipped") if isinstance(equipment, dict) else None
    if isinstance(equipped, dict):
        current = [f"{key}: {_escape(str(value))}" for key, value in equipped.items() if value]
        if current:
            lines.append("<b>Экипировка</b>")
            lines.extend(current[:12])
    for key, label in (("eggs", "Яйца"), ("food", "Еда"), ("hatchingPotions", "Зелья вылупления"),
                       ("pets", "Питомцы"), ("mounts", "Маунты")):
        values = items.get(key)
        if isinstance(values, dict):
            count = sum(1 for value in values.values() if value)
            lines.append(f"{label}: {count} видов")
        elif isinstance(values, list):
            lines.append(f"{label}: {len(values)}")
    if len(lines) == 1:
        lines.append("В ответе API нет данных об инвентаре.")
    return "\\n".join(lines)


def format_quest(user: dict[str, Any]) -> str:
    party = user.get("party") or {}
    quest = party.get("quest") if isinstance(party, dict) else None
    lines = ["<b>Квест / группа</b>"]
    if isinstance(party, dict) and party.get("name"):
        lines.append(f"Группа: {_escape(str(party['name']))}")
    if isinstance(quest, dict):
        for key, label in (("key", "Квест"), ("name", "Название"), ("type", "Тип"),
                           ("progress", "Прогресс"), ("boss", "Босс"), ("leader", "Лидер")):
            value = quest.get(key)
            if value is not None:
                if isinstance(value, dict):
                    value = value.get("name") or value.get("key") or str(value)
                lines.append(f"{label}: {_escape(str(value))}")
        if len(lines) == 1:
            lines.append("Активный квест найден, но API не вернул отображаемые поля.")
    else:
        lines.append("Информация об активном квесте не возвращена API.")
    return "\\n".join(lines)
