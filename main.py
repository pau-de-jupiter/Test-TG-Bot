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
    return Client(
        name=bot_name,
        api_id=settings.api_id,
        api_hash=settings.api_hash,
        bot_token=settings.bot_token
    )

def create_app(client: Client = None) -> "BotApp":
    return BotApp(client or create_client(BOT_NAME))


class BotApp:
    def __init__(self, client):
        self.app = client
        self.stop_event = asyncio.Event()
        self.db = Database()

    async def setup(self,):
        # logger.info("Applying migrations...")
        # await run_migrations()

        await self.db.init()
        logger.info("Registering handlers...")
        RegistrationHandler(self.app, self.db, storage).register()
        TaskHandler(self.app, self.db, storage).register()

    async def _run_bot(self):
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
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._run_bot())
    

if __name__ == "__main__":
    bot_app = create_app()
    bot_app.run()


