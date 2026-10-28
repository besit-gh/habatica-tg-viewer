from app.config import Settings


def test_client_header_uses_user_id_and_client_name() -> None:
    settings = Settings(telegram_bot_token="telegram-secret", allowed_telegram_user_id=123,
                        habitica_user_id="habitica-id", habitica_api_token="habitica-secret",
                        habitica_client_name="TestBot")
    assert settings.habitica_x_client == "habitica-id-TestBot"
