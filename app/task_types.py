"""Translate Telegram list categories to Habitica API task types."""

LIST_TO_API_TYPE = {
    "habits": "habit",
    "dailys": "daily",
    "todos": "todo",
    "rewards": "reward",
    "completedTodos": "todo",
}

CREATE_TYPES = {key: value for key, value in LIST_TO_API_TYPE.items() if key != "completedTodos"}


def task_type_matches(task: dict, category: str) -> bool:
    """Check the current API task type against the selected list category."""
    expected = LIST_TO_API_TYPE.get(category)
    actual = task.get("type")
    if expected is None:
        return False
    if actual is not None and actual != expected:
        return False
    if category == "completedTodos":
        return task.get("completed") is True
    return True
