import logging
import asyncio

from pyrogram import Client

from config.config import settings
from logger.logger import logger

from database import Database
from fsm import FSMStorage

from models.migrations.create_tables import run_migrations
from handlers.registration import RegistrationHandler
from handlers.tasks import TaskHandler

BOT_NAME = "my_test_bot"
logger = logging.getLogger('test_bot')
storage = FSMStorage()

def create_client(bot_name: str) -> Client:
    """
    Создает клиент Pyrogram для работы с телеграм API.
    Аргументы: 
        - bot_name - принимает название бота.
    Возвращаем:
        Экземляр клиента.
    """
    return Client(
        name=bot_name,
        api_id=settings.api_id,
        api_hash=settings.api_hash,
        bot_token=settings.bot_token
    )

def create_app(client: Client = None) -> "BotApp":
    """
    Создает экземляр приложения бота с клиентом Pyrogram.
    Аргументы: 
        - Client - экземляр клиента Pyrogram.
    Если клиент не указан, создаем новый.
    Возвращаем:
        Экземляр приложения бота.
    """
    return BotApp(client or create_client(BOT_NAME))


class BotApp:
    """
    Основной класс приложения Telegram-бота.
    Атрибуты:
        app (client): Клиент Pyrogram для взаимодействия с телеграм API.
        stop_event (asyncio.Event): Событие для остановки бота.
        db (Database): Экземпляр базы данных для работы с данными.
    """
    def __init__(self, client):
        self.app = client
        self.stop_event = asyncio.Event()
        self.db = Database()

    async def setup(self,):
        """
        Настраивает приложение перед запуском:
        - Применяет миграции базы данных (если нужно).
        - Инициализирует подключение к базе данных.
        - Регистрирует обработчики событий.
        """
        # Проверяет, есть ли нужные таблицы для работы бота, если нет, то создает их.
        logger.info("Applying migrations...")
        await run_migrations()

        await self.db.init()
        logger.info("Registering handlers...")
        RegistrationHandler(self.app, self.db, storage).register()
        TaskHandler(self.app, self.db, storage).register()

    async def _run_bot(self):
        """
        Внутренний метод для запуска бота.
        Выполняет настройку, запускает бота и ожидает события остановки.
        """
        await self.setup()
        logger.info("Starting bot...")
        await self.app.start()
        try:
            await self.stop_event.wait()
        finally:
            await self.app.stop()
            await self.db.close()
            await storage.close()
            logger.info("Bot stopped gracefully..")

    def run(self):
        """
        Запускает асинхронный цикл событий для работы бота.
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._run_bot())
    

if __name__ == "__main__":
    bot_app = create_app()
    bot_app.run()


