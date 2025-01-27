import json
import logging

from redis.asyncio import Redis

from config.config import settings

logger = logging.getLogger('test_bot')

class FSMStorage():
    def __init__(self) -> None:
        self.redis_conn = Redis(
            host="127.0.0.1", 
            port=6379, 
            password=settings.redis_password, 
            decode_responses=True, 
            db=0)
    
    async def set_state(self, user_id, state):
        """Set the status for the user"""
        try:
            await self.redis_conn.set(f"user:{user_id}:state", state)
        except Exception as e:
            logger.error(f'An error occurred in the set_state function when working with redis - {e}.')

    async def get_state(self, user_id):
        """Get the current status of the user"""
        try:
            result = await self.redis_conn.get(f"user:{user_id}:state")
        except Exception as e:
            logger.error(f'An error occurred in the get_state function when working with redis - {e}.')
        return result

    async def set_data(self, user_id, data):
        """Save data for the user"""
        try:
            await self.redis_conn.set(f"user:{user_id}:data", json.dumps(data))
        except Exception as e:
            logger.error(f'An error occurred in the set_data function when working with redis - {e}.')

    async def get_data(self, user_id):
        """Retrieve user data"""
        try:
            data = await self.redis_conn.get(f"user:{user_id}:data")
        except Exception as e:
            logger.error(f'An error occurred in the get_data function when working with redis - {e}.')
        return json.loads(data) if data else {}

    async def clear_state(self, user_id):
        """Clear user status and data"""
        try:
            await self.redis_conn.delete(f"user:{user_id}:state")
            await self.redis_conn.delete(f"user:{user_id}:data")
        except Exception as e:
            logger.error(f'An error occurred in the clear_state function when working with redis - {e}.')

    async def close(self):
        if self.redis_conn:
            await self.redis_conn.close()