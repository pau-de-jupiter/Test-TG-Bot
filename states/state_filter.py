
from pyrogram.filters import create
from pyrogram.types import Message

from fsm import FSMStorage

storage = FSMStorage()

def state_filter(expected_state):
    async def func(_, __, message: Message):
        user_id = message.from_user.id
        state = await storage.get_state(user_id)
        return state in expected_state
    return create(func)
