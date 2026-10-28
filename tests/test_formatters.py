from app.formatters import format_profile, format_task


def test_format_task_escapes_html_and_shows_status() -> None:
    text = format_task({"text": "<script>", "completed": True, "priority": 1}, "todos")
    assert "&lt;script&gt;" in text
    assert "выполнено" in text
    assert "Лёгкая" in text


def test_format_profile_handles_missing_fields() -> None:
    assert "Профиль Habitica" in format_profile({})


def test_inventory_and_quest_formatters_handle_missing_data() -> None:
    from app.formatters import format_inventory, format_quest

    assert "Инвентарь Habitica" in format_inventory({})
    assert "Квест / группа" in format_quest({})
