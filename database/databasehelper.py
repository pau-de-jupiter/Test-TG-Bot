import logging

from sqlalchemy.future import select
from sqlalchemy import update, delete

from models.users import User
from models.tasks import Task

logger = logging.getLogger('test_bot')

class CRUD:
    def __init__(self, session):
        self.async_session = session

    async def add_user(self, tg_user_id, username, login):
        user = User(tg_user_id=tg_user_id, username=username, login=login)
        async with self.async_session as session:
            try:
                session.add(user)
            except Exception as e:
                logger.error(f"The add_user function crashed with an error: {e}")
                return
            await session.commit()

    async def get_user(self, tg_user_id):
        async with self.async_session as session:
            try:
                result = await session.execute(select(User).where(User.tg_user_id == tg_user_id))
            except Exception as e:
                logger.error(f"The get_user function crashed with an error: {e}")
                return
            return result.scalars().first()

    async def add_task(self, tg_user_id, name, description):
        task = Task(tg_user_id=tg_user_id, name=name, description=description)
        async with self.async_session as session:
            try:
                session.add(task)
            except Exception as e:
                logger.error(f"The add_task function crashed with an error: {e}")
                return
            await session.commit()

    async def get_tasks(self, tg_user_id):
        async with self.async_session as session:
            try:
                result = await session.execute(select(Task).where(Task.tg_user_id == tg_user_id))
            except Exception as e:
                logger.error(f"The get_tasks function crashed with an error: {e}")
                return
            return result.scalars().all()

    async def update_task(self, obj, field, value, update_values: dict):
        async with self.async_session as session:
            try:
                result = await session.execute(update(obj).where(getattr(obj, field) == value).values(**update_values))
            except Exception as e:
                logger.error(f"The update_task function crashed with an error: {e}")
                return False
            await session.commit()
            return result.rowcount > 0

    async def delete_task(self, task_id):
        async with self.async_session as session:
            try:
                result = await session.execute(delete(Task).where(Task.id == task_id))
            except Exception as e:
                logger.error(f"The delete_task function crashed with an error: {e}")
                return False
            await session.commit()
            return result.rowcount > 0

    async def get_some_record(self, obj, field, value):
        async with self.async_session as session:
            try:
                result = await session.execute(select(obj).where(getattr(obj, field) == value))
            except Exception as e:
                logger.error(f"The get_some_record function crashed with an error: {e}")
                return
            return result.scalars().first()

