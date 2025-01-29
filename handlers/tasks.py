import logging

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, BotCommand
from pyrogram.handlers import MessageHandler, CallbackQueryHandler

from fsm import FSMStorage
from models.tasks import Task
from utils.utils import chunk_tasks, TaskValidator
from utils.decorators import error_handler

from states.tasks import TaskState
from states.state_filter import state_filter

from database import Database
from database.databasehelper import CRUD


logger = logging.getLogger('test_bot')

class TaskHandler:
    """
    Обработчик задач для бота. Управляет созданием, обновлением, удалением и отображением задач.

    Атрибуты:
        app (Client): Клиент Pyrogram для взаимодействия с телеграм API.
        db (Database): Экземпляр базы данных.
        __session (CRUD): Вспомогательный объект для выполнения операций с базой данных.
        storage (FSMStorage): Хранилище состояний FSM.
        callback_handlers (dict): Карта обработчиков для обработки инлайн-кнопок.
        message_handler (dict): Карта обработчиков для обработки текстовых сообщений.
    Шаблонные аргументы в методах:
        client (Client): Клиент Pyrogram.
        message (Message): Сообщение пользователя.
        callback_query (CallbackQuery): Объект инлайн-кнопки.
        param (None): Дополнительный параметр.
    """
    __stages = [value for key, value in vars(TaskState).items() if not key.startswith("__")]
    keyboard_template = [
                [InlineKeyboardButton("Cancel", callback_data="cancel_task")]
            ]
    STATUS_CHOICES = [
                    ("PROG", "In progress"),
                    ("DONE", "Accepted, satisfying"),
                      ]

    def __init__(self, app: Client, db: Database, storage: FSMStorage):
        self.app = app
        self.db = db
        self.__session = CRUD(db.session)
        self.storage = storage
        self.callback_handlers: dict = {
            "my_tasks": self.my_tasks_handler,
            "cancel_task": self.cancel_task_handler,
            "back_stage": self.back_stage_handler,
            "detail_task": self.detail_task_handler,
            "choose_task_status": self.choose_task_status_handler,
            "choose_task_data": self.choose_task_data_handler,
            "change_task_status": self.change_task_status_handler,
            "delete_task": self.delete_task_handler,
            "confirm_deletion": self.confirm_deletion_handler,
        }
        self.message_handler: dict = {
            "waiting_for_name": self.get_task_name,
            "waiting_for_description": self.get_task_description,
            "change_task_field": self.change_task_field_handler,
        }

    def register(self):
        """
        Регистрирует обработчики для команды создания задач, просмотра задач, инлайн-кнопок и отслеживания текста.
        """
        self.app.add_handler(MessageHandler(self.create_task_handler, filters.command("create_task")))
        self.app.add_handler(MessageHandler(self.my_tasks_handler, filters.command("my_tasks")))
        self.app.add_handler(CallbackQueryHandler(self.handle_callback))
        self.app.add_handler(MessageHandler(self.handle_message, state_filter(self.__stages)))

    @error_handler
    async def handle_callback(self, client: Client, callback_query: CallbackQuery):
        """
        Обрабатывает действия, вызванные инлайн-кнопками.
        Обработчик вызывает нужные методы для работы с дальнешей логикой.
        """
        user_id = callback_query.from_user.id
        data = callback_query.data
        user = await self.__session.get_user(user_id)
        if user:
            if ":" in data:
                action, param = data.split(":")
            else:
                action, param = data, None
            handler = self.callback_handlers.get(action)
            if handler:
                await handler(client, callback_query, param)
            else:
                await callback_query.message.reply("Unknown action.")
                await self.cancel_command(client, callback_query)
        else:
            await callback_query.message.reply("Sign up first. Enter the /start command")
        await callback_query.answer()  

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

    async def cancel_command(self, client: Client, message: Message):
        """
        Отменяет текущее действие пользователя и очищает состояние и данные пользователя.
        """
        user_id = message.from_user.id
        await self.storage.clear_state(user_id)
        await message.message.reply("Choose an action in menu")

    @error_handler
    async def create_task_handler(self, client: Client, message: Message):
        """Начинает процесс создания новой задачи."""
        user_id = message.from_user.id
        user = await self.__session.get_user(user_id)
        if user:
            await self.storage.set_state(user_id, TaskState.WAITING_FOR_NAME)
            await message.reply(
                TaskState.CREATE_TASK_STAGE[TaskState.WAITING_FOR_NAME],
                reply_markup=InlineKeyboardMarkup(self.keyboard_template))
        else:
            await message.reply("Sign up first. Enter the /start command")

    @error_handler
    async def get_task_name(self, client: Client, message: Message):
        """Сохраняет название задачи и запрашивает описание."""
        user_id = message.from_user.id
        is_valid, error_msg = TaskValidator.validate("name", message.text)
        if not is_valid:
            await message.reply(error_msg)
            return
        await self.storage.set_data(user_id, {"task_name": message.text})
        await self.storage.set_state(user_id, TaskState.WAITING_FOR_DESCRIPTION)
        keyboard = self.keyboard_template.copy()
        keyboard.append([InlineKeyboardButton("Back", callback_data="back_stage")])
        await message.reply(TaskState.CREATE_TASK_STAGE[TaskState.WAITING_FOR_DESCRIPTION], reply_markup=InlineKeyboardMarkup(keyboard))

    @error_handler
    async def get_task_description(self, client: Client, message: Message):
        """Получает описание задачи и запускает метод для сохранения данных в БД."""
        user_id = message.from_user.id
        data = await self.storage.get_data(user_id)
        task_name = data.get("task_name")
        task_description = message.text
        await self.save_task_data(client, message, task_name, task_description)

    @error_handler
    async def save_task_data(self, client: Client, message: Message, 
                                   task_name: str, task_description: str):
        """
        Сохраняет данные новой задачи в базу данных.
        Аргументы:
            task_name (str): Название задачи.
            task_description (str): Описание задачи.
        """
        user_id = message.from_user.id
        await self.__session.add_task(message.from_user.id, task_name, task_description)
        await self.storage.clear_state(user_id)
        await message.reply(f"Task ‘{task_name}’ has been successfully created!")
        logger.info(f"Task ‘{task_name}’ has been successfully created!")

    @error_handler
    async def change_task_field_handler(self, client: Client, message: Message):
        """Обновляет данные в задаче, в передаваемом поле."""
        user_id = message.from_user.id
        new_task_data = message.text
        data = await self.storage.get_data(user_id)
        task_data = data.get("data")
        task_id = task_data["task_id"]
        field = task_data["field"]
        is_valid, error_msg = TaskValidator.validate(field, new_task_data)
        if not is_valid:
            await message.reply(error_msg)
            return
        result = await self.__session.update_task(Task, "id", int(task_id),
                                                  {field:new_task_data})
        if result:
            await message.reply(f"You changed the {field} of task `{new_task_data}`")
            logger.info(f"User {user_id} has successfully updated the task {field} on {new_task_data}")
        else:
            await message.reply(f"There's been an error. Try again later.")
        await self.storage.clear_state(user_id)
        await message.reply("Choose an action in menu")
    
    @error_handler
    async def my_tasks_handler(self, client: Client, message: Message, param=0):
        """
        Показывает список задач пользователя с разбивкой на страницы.
        Каждая страница показывает по 10 задач.
        Есть возможность перехода по страницам
        Аргументы:
            param (int, optional): Принимает номер страницы. По умолчанию 0.
        """
        user_id = message.from_user.id
        target_message = getattr(message, 'message', message)
        await self.storage.clear_state(user_id)
        tasks = await self.__session.get_tasks(user_id)
        if not tasks:
            await target_message.reply("You don't have any tasks yet.")
            return 
        page = int(param)
        tasks_per_page = 10
        start = page * tasks_per_page
        end = start + tasks_per_page
        tasks_on_page = tasks[start:end]
        task_buttons = [
            InlineKeyboardButton(task.name, callback_data=f"detail_task:{task.id}")
            for task in tasks_on_page
        ]
        task_buttons_grouped = chunk_tasks(task_buttons, 2)
        task_buttons_grouped.insert(0, [InlineKeyboardButton("Cancel", callback_data="cancel_task")])
        navigation_buttons = []
        if page > 0:
            navigation_buttons.append(InlineKeyboardButton("Previous", callback_data=f"my_tasks:{page - 1}"))
        if end < len(tasks):
            navigation_buttons.append(InlineKeyboardButton("Next", callback_data=f"my_tasks:{page + 1}"))

        if navigation_buttons:
            task_buttons_grouped.append(navigation_buttons)
        await target_message.reply("Your tasks:", reply_markup=InlineKeyboardMarkup(task_buttons_grouped))

    async def cancel_task_handler(self, client: Client, callback_query: CallbackQuery, param: None):
        """Обрабатывает отмену действия, вызываемое инлайн-кнопкой."""
        await self.cancel_command(client, callback_query)

    @error_handler
    async def back_stage_handler(self, client: Client, callback_query: CallbackQuery, param: None):
        """
        Возвращает пользователя на предыдущий этап создания, редактирования задачи или к списку с задачами.
        """
        user_id = callback_query.from_user.id
        state = await self.storage.get_state(user_id)
        if state in TaskState.CREATE_TASK_STEP:
            current_index = TaskState.CREATE_TASK_STEP.index(state)
            current_step = TaskState.CREATE_TASK_STEP[current_index - 1]
            await self.storage.set_state(user_id, current_step)
            await callback_query.message.reply(
                TaskState.CREATE_TASK_STAGE[current_step],
                reply_markup=InlineKeyboardMarkup(self.keyboard_template),
            )
        else:
            if ":" in state:
                action, param = state.split(":")
            else:
                action, param = state, None
            handler = self.callback_handlers.get(action)
            if handler:
                await handler(client, callback_query, param)

    @error_handler
    async def detail_task_handler(self, client: Client, callback_query: CallbackQuery, param: None):
        """Показывает подробности о задаче и предоставляет меню для её редактирования."""
        user_id = callback_query.from_user.id
        task_id = int(param)
        task_data = await self.__session.get_some_record(Task, "id", int(task_id))
        await self.storage.set_state(user_id, TaskState.CHANGE_TASK_DATA)
        await self.storage.set_data(user_id, {
                                "data":{
                                        "task_id": task_id,
                                        "task_status": task_data.status, 
                                        "task_name": task_data.name, 
                                    }
                                })
        keyboard = self.keyboard_template.copy()
        keyboard.extend([
                [InlineKeyboardButton("Back", callback_data="back_stage")],
                [InlineKeyboardButton("Change task name", callback_data="choose_task_data:name")],
                [InlineKeyboardButton("Change task description", callback_data="choose_task_data:description")],
                [InlineKeyboardButton("Change task status", callback_data="choose_task_status")],
                [InlineKeyboardButton("Delete tasks", callback_data="delete_task")],
            ])
        await callback_query.message.reply(f"Select action for `{task_data.name}`:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    @error_handler
    async def choose_task_status_handler(self, client: Client, callback_query: CallbackQuery, param: None):
        """
        Позволяет пользователю выбрать новый статус задачи.
        Передаем список всех возможных статусов из STATUS_CHOICES
        """
        user_id = callback_query.from_user.id
        data = await self.storage.get_data(user_id)
        task_data = data.get("data")
        task_status = task_data["task_status"]
        await self.storage.set_state(user_id, TaskState.CHANGE_DETAIL_TASK.format(taskId=task_data["task_id"]))
        keyboard = [
                [InlineKeyboardButton(status[1], callback_data=f"change_task_status:{status[0]}")]
                for status in self.STATUS_CHOICES
                if status[0] != task_status
            ]
        keyboard.insert(0, [InlineKeyboardButton("Cancel", callback_data="cancel_task")])
        keyboard.insert(1, [InlineKeyboardButton("Back", callback_data="back_stage")])
        await callback_query.message.reply("Select a status:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    @error_handler
    async def choose_task_data_handler(self, client: Client, callback_query: CallbackQuery, param: None):
        """
        Устанавливает поле задачи, которое пользователь хочет изменить.
        Ожидает текстового ответа от пользователя
        Аргументы:
            param (int, optional): Хранит название поля, которое нужно изменить.
        """
        user_id = callback_query.from_user.id
        data = await self.storage.get_data(user_id)
        data["data"]["field"] = param
        await self.storage.set_data(user_id, data)
        await self.storage.set_state(user_id, TaskState.CHANGE_TASK_FIELD)
        await callback_query.message.reply(f"Enter a new {param} for the task.", 
                                            reply_markup=InlineKeyboardMarkup(self.keyboard_template))
    
    @error_handler
    async def change_task_status_handler(self, client: Client, callback_query: CallbackQuery, param: None):
        """
        Обновляет статус задачи.
        Аргументы:
            param (str): Новый статус задачи.
        """
        user_id = callback_query.from_user.id
        status = param
        data = await self.storage.get_data(user_id)
        task_data = data.get("data")
        task_id = task_data["task_id"]
        result = await self.__session.update_task(Task, "id", int(task_id),
                                                  {"status":status})
        if result:
            await callback_query.message.reply(f"Task `{task_data['task_name']}` has successfully updated the status on {status}.")
            logger.info(f"User {user_id} has successfully updated the status of task {task_data['task_name']}")
        else:
            await callback_query.message.reply(f"There's been an error. Try again later.")
        await self.cancel_command(client, callback_query)
    
    async def delete_task_handler(self, client: Client, callback_query: CallbackQuery, param: None):
        """Подтверждает удаление задачи пользователем."""
        user_id = callback_query.from_user.id
        data = await self.storage.get_data(user_id)
        task_data = data.get("data")
        await self.storage.set_state(user_id, TaskState.CHANGE_DETAIL_TASK.format(taskId=task_data["task_id"]))
        keyboard = self.keyboard_template.copy()
        keyboard.extend([[InlineKeyboardButton("Back", callback_data="back_stage")],
                         [InlineKeyboardButton("Yes, delete it.", callback_data="confirm_deletion")],
            ])
        await callback_query.message.reply(f"Are you sure you want to delete the task?",
                                           reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def confirm_deletion_handler(self, client: Client, callback_query: CallbackQuery, param: None):
        """Удаляет задачу из базы данных."""
        user_id = callback_query.from_user.id
        data = await self.storage.get_data(user_id)
        task_data = data.get("data")
        task_id = data.get("data")["task_id"]
        result = await self.__session.delete_task(int(task_id))
        if result:
            await callback_query.message.reply(f"Task `{task_data['task_name']}` successfully deleted.")
            logger.info(f"User {user_id} successfully deleted task {task_data['task_name']}")
        else:
            await callback_query.message.reply(f"There's been an error. Try again later.")
        await self.cancel_command(client, callback_query)