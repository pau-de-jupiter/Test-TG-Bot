
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """
    Класс для управления настройками приложения, загружаемыми из переменных окружения.
    Атрибуты:
        api_id (int): ID API Telegram.
        api_hash (str): Hash API Telegram.
        bot_token (str): Token Telegram-бота.
        redis_password (str): Пароль для Redis.
        postgres_user (str): Имя пользователя PSQL.
        postgres_password (str): Пароль для PSQL.
        postgres_db (str): Название базы данных PSQL.
        postgres_port (int): Порт для подключения к PSQL.
    """
    api_id: int
    api_hash: str
    bot_token: str
    redis_password: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_port: int
    def get_db_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@db/{self.postgres_db}"

    class Config:
        env_file = ".env"

settings = Settings()
