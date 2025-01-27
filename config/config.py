
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    api_id: int
    api_hash: str
    bot_token: str
    redis_password: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_port: int
    def get_db_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@localhost/{self.postgres_db}"

    class Config:
        env_file = ".env"

settings = Settings()
