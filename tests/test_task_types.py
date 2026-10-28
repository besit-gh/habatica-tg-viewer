from app.task_types import CREATE_TYPES, task_type_matches


def test_creation_uses_singular_habitica_api_types() -> None:
    assert CREATE_TYPES == {
        "habits": "habit",
        "dailys": "daily",
        "todos": "todo",
        "rewards": "reward",
    }
    assert "completedTodos" not in CREATE_TYPES


def test_completed_todo_category_requires_completed_todo() -> None:
    assert task_type_matches({"type": "todo", "completed": True}, "completedTodos")
    assert not task_type_matches({"type": "todo", "completed": False}, "completedTodos")
    assert not task_type_matches({"type": "daily", "completed": True}, "completedTodos")


def test_category_rejects_mismatched_task_type() -> None:
    assert task_type_matches({"type": "todo"}, "todos")
    assert not task_type_matches({"type": "reward"}, "todos")
    assert not task_type_matches({"type": "todo"}, "unknown")
