import logging

from pyrogram import Client, filters
from pyrogram.types import Message, BotCommand
from pyrogram.handlers import MessageHandler

from states.state_filter import state_filter
from states.registration import RegistrationState
from utils.decorators import error_handler

from fsm import FSMStorage
from models.users import User
from database import Database
from database.databasehelper import CRUD

logger = logging.getLogger('test_bot')

class RegistrationHandler:
    """
    Класс для обработки регистрации пользователей через Telegram-бота.
    Атрибуты:
        app (Client): Клиент Pyrogram для взаимодействия с телеграм API.
        db (Database): Экземпляр базы данных.
        __session (CRUD): Вспомогательный объект для операций с базой данных.
        storage (FSMStorage): Хранилище состояний FSM.
        message_handler (dict): Словарь обработчиков для сообщений на разных этапах регистрации.
    Шаблонные аргументы в методах:
        client (Client): Клиент Pyrogram.
        message (Message): Сообщение пользователя.
    """
    __stages = [value for key, value in vars(RegistrationState).items() if not key.startswith("__")]

    def __init__(self, app: Client, db: Database, storage: FSMStorage):
        self.app = app
        self.db = db
        self.__session = CRUD(db.session)
        self.storage = storage
        self.message_handler: dict = {
            "waiting_for_username": self.get_username,
            "waiting_for_login": self.get_user_login,
        }

    async def set_bot_commands(self):
        """
        Устанавливает команды бота в постоянное меню для пользователей.
        """
        commands = [
            BotCommand("create_task", "Create a new task"),
            BotCommand("my_tasks", "View your tasks"),
        ]
        await self.app.set_bot_commands(commands)

    def register(self):
        """
        Регистрирует обработчики для команд регистрации, отмены и обработки сообщений.
        """
        self.app.add_handler(MessageHandler(self.start_handler, filters.command("start")))
        self.app.add_handler(MessageHandler(self.cancel_handler, filters.command("cancel")))
        self.app.add_handler(MessageHandler(self.handle_message, state_filter(self.__stages)))

    async def start_handler(self, client: Client, message: Message):
        """Обрабатывает команду /start, начиная процесс регистрации."""
        user_id = message.from_user.id
        user = await self.__session.get_user(user_id)
        if user:
            await message.reply("You are already registered! Select an action in menu")
        else:
            await self.storage.set_state(user_id, RegistrationState.WAITING_FOR_USERNAME)
            await message.reply("Enter your name:")

    @error_handler
    async def handle_message(self, client: Client, message: Message):
        """
        Обрабатывает текстовые сообщения пользователя в зависимости от его текущего состояния.
        Вызывает нужные методы для дальнейшей работы.
        """
        user_id = message.from_user.id
        state = await self.storage.get_state(user_id)
        handler = self.message_handler.get(state)
        if handler:
            await handler(client, message)
        else:
            await message.reply("Unknown action.")

    @error_handler
    async def get_username(self, client: Client, message: Message):
        """Сохраняет имя пользователя и переходит к запросу логина."""
        user_id = message.from_user.id
        await self.storage.set_data(user_id, {"username": message.text})
        await self.storage.set_state(user_id, RegistrationState.WAITING_FOR_LOGIN)
        await message.reply("Enter your login:")

    @error_handler
    async def get_user_login(self, client: Client, message: Message):
        """Проверяет уникальность логина и завершает регистрацию."""
        user_id = message.from_user.id
        login = message.text
        existing_user = await self.__session.get_some_record(User, "login", login)
        if existing_user:
            await message.reply("This login is already taken. Please enter a different login:")
            return 
        data = await self.storage.get_data(user_id)
        username = data.get("username")
        await self.save_user_data_to_db(client, message, username, login)

    @error_handler
    async def save_user_data_to_db(self, client: Client, message: Message, 
                                   username: str, login: str):
        """
        Сохраняет данные пользователя в базу данных и завершает процесс регистрации.
        Аргументы:
            username (str): Имя пользователя.
            login (str): Логин пользователя.
        """
        user_id = message.from_user.id
        await self.__session.add_user(message.from_user.id, username, login)
        await self.storage.clear_state(user_id)
        await message.reply(f"Registration is complete! Name: {username}, login: {login}! Select an action in menu")
        logger.info(f"Registration is complete! Name: {username}, login: {login}")
        await self.set_bot_commands()
        await message.reply("Bot commands have been set! Use the menu to start working.")

    @error_handler
    async def cancel_handler(self, client: Client, message: Message):
        """Отменяет текущий процесс регистрации."""
        user_id = message.from_user.id
        state = await self.storage.get_state(user_id)
        if state:
            await self.storage.clear_state(user_id)
            await message.reply("The process has been cancelled.")
        else:
            await message.reply("No active process.")