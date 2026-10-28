from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    telegram_bot_token: SecretStr
    allowed_telegram_user_id: int = Field(gt=0)
    habitica_user_id: str = Field(min_length=1)
    habitica_api_token: SecretStr
    habitica_client_name: str = "HabiticaCompanion"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def habitica_x_client(self) -> str:
        return f"{self.habitica_user_id}-{self.habitica_client_name}"


def load_settings() -> Settings:
    return Settings()
