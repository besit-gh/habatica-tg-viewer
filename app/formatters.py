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
