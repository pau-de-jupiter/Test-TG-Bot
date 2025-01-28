
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from config.config import settings

engine = create_async_engine(settings.get_db_url(), echo=False)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

class Database:
    """
    Класс для управления подключением к базе данных.
    Атрибуты:
        session (AsyncSession): Асинхронная сессия для взаимодействия с базой данных.
    """
    def __init__(self):
        self.session = None

    async def init(self):
        self.session = SessionLocal()

    async def close(self):
        if self.session:
            await self.session.close()
