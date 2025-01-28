import json
import logging

from redis.asyncio import Redis

from config.config import settings

logger = logging.getLogger('test_bot')

class FSMStorage():
    """
    Класс для управления состояниями и данными пользователей с использованием Redis.

    Атрибуты:
        redis_conn (Redis): Асинхронное соединение с Redis.
    """
    def __init__(self) -> None:
        self.redis_conn = Redis(
            host="redis", 
            port=6379, 
            password=settings.redis_password, 
            decode_responses=True, 
            db=0)
    
    async def set_state(self, user_id, state):
        """Установить состояние для пользователя"""
        try:
            await self.redis_conn.set(f"user:{user_id}:state", state)
        except Exception as e:
            logger.error(f'An error occurred in the set_state function when working with redis - {e}.')

    async def get_state(self, user_id):
        """Получить текущее состояние пользователя"""
        try:
            result = await self.redis_conn.get(f"user:{user_id}:state")
        except Exception as e:
            logger.error(f'An error occurred in the get_state function when working with redis - {e}.')
        return result

    async def set_data(self, user_id, data):
        """Сохранить данные для пользователя"""
        try:
            await self.redis_conn.set(f"user:{user_id}:data", json.dumps(data))
        except Exception as e:
            logger.error(f'An error occurred in the set_data function when working with redis - {e}.')

    async def get_data(self, user_id):
        """Получить данные пользователя"""
        try:
            data = await self.redis_conn.get(f"user:{user_id}:data")
        except Exception as e:
            logger.error(f'An error occurred in the get_data function when working with redis - {e}.')
        return json.loads(data) if data else {}

    async def clear_state(self, user_id):
        """Очистить состояние и данные пользователя"""
        try:
            await self.redis_conn.delete(f"user:{user_id}:state")
            await self.redis_conn.delete(f"user:{user_id}:data")
        except Exception as e:
            logger.error(f'An error occurred in the clear_state function when working with redis - {e}.')

    async def close(self):
        """Закрыть соединение"""
        if self.redis_conn:
            await self.redis_conn.close()