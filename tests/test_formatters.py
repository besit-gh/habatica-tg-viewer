from app.formatters import format_profile, format_task


def test_format_task_escapes_html_and_shows_status() -> None:
    text = format_task({"text": "<script>", "completed": True, "priority": 1}, "todos")
    assert "&lt;script&gt;" in text
    assert "выполнено" in text
    assert "Лёгкая" in text


def test_format_profile_handles_missing_fields() -> None:
    assert "Профиль Habitica" in format_profile({})
