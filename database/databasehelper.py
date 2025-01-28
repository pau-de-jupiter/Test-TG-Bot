import logging

from sqlalchemy.future import select
from sqlalchemy import update, delete, asc

from models.users import User
from models.tasks import Task

logger = logging.getLogger('test_bot')

class CRUD:
    """
    Класс для управления базовыми CRUD-операциями с базой данных.
    Атрибуты:
        async_session: Асинхронная сессия для взаимодействия с базой данных.
    """
    def __init__(self, session):
        self.async_session = session

    async def add_user(self, tg_user_id, username, login):
        """
        Добавляет нового пользователя в базу данных.
        Аргументы:
            tg_user_id (int): Телегарам ID пользователя.
            username (str): Имя пользователя.
            login (str): Логин пользователя.
        """
        user = User(tg_user_id=tg_user_id, username=username, login=login)
        async with self.async_session as session:
            try:
                session.add(user)
            except Exception as e:
                logger.error(f"The add_user function crashed with an error: {e}")
                return
            await session.commit()

    async def get_user(self, tg_user_id):
        """
        Извлекает пользователя из базы данных по телеграм ID.
        Аргументы:
            tg_user_id (int): Телеграм ID пользователя.
        Возвращает:
            Объект пользователя или None, если пользователь не найден.
        """
        async with self.async_session as session:
            try:
                result = await session.execute(select(User).where(User.tg_user_id == tg_user_id))
            except Exception as e:
                logger.error(f"The get_user function crashed with an error: {e}")
                return
            return result.scalars().first()

    async def add_task(self, tg_user_id, name, description):
        """
        Добавляет новую задачу в базу данных.
        Аргументы:
            tg_user_id (int): Телеграм ID пользователя, чтобы привязать задачу к пользователю.
            name (str): Название задачи.
            description (str): Описание задачи.
        """
        task = Task(tg_user_id=tg_user_id, name=name, description=description)
        async with self.async_session as session:
            try:
                session.add(task)
            except Exception as e:
                logger.error(f"The add_task function crashed with an error: {e}")
                return
            await session.commit()

    async def get_tasks(self, tg_user_id):
        """
        Извлекает все задачи пользователя из базы данных, отсортированные по дате создания.
        Аргументы:
            tg_user_id (int): Телеграм ID пользователя.
        Возвращает:
            list: Список задач.
        """
        async with self.async_session as session:
            try:
                result = await session.execute(
                select(Task)
                .where(Task.tg_user_id == tg_user_id)
                .order_by(asc(Task.created_at))
            )
            except Exception as e:
                logger.error(f"The get_tasks function crashed with an error: {e}")
                return
            return result.scalars().all()

    async def update_task(self, obj, field, value, update_values: dict):
        """
        Обновляет объект в базе данных.
        Аргументы:
            obj: Объект SQLAlchemy для обновления.
            field (str): Поле, по которому выполняется поиск задачи.
            value: Значение поля для поиска.
            update_values (dict): Словарь значений для обновления.
        Возвращает:
            bool: True, если обновление прошло успешно, иначе False.
        """
        async with self.async_session as session:
            try:
                result = await session.execute(update(obj).where(getattr(obj, field) == value).values(**update_values))
            except Exception as e:
                logger.error(f"The update_task function crashed with an error: {e}")
                return False
            await session.commit()
            return result.rowcount > 0

    async def delete_task(self, task_id):
        """
        Удаляет задачу из базы данных по её ID.
        Аргументы:
            task_id (int): ID задачи.
        Возвращает:
            bool: True, если задача была успешно удалена, иначе False.
        """
        async with self.async_session as session:
            try:
                result = await session.execute(delete(Task).where(Task.id == task_id))
            except Exception as e:
                logger.error(f"The delete_task function crashed with an error: {e}")
                return False
            await session.commit()
            return result.rowcount > 0

    async def get_some_record(self, obj, field, value):
        """
        Извлекает запись из нужной таблицы (передаваемый объект) по указанному полю и значению.
        Аргументы:
            obj: Объект SQLAlchemy для поиска.
            field (str): Поле, по которому выполняется поиск.
            value: Значение поля для поиска.
        Возвращает:
            object: Найденная запись.
        """
        async with self.async_session as session:
            try:
                result = await session.execute(select(obj).where(getattr(obj, field) == value))
            except Exception as e:
                logger.error(f"The get_some_record function crashed with an error: {e}")
                return
            return result.scalars().first()

