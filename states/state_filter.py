
from pyrogram.filters import create
from pyrogram.types import Message

from fsm import FSMStorage

storage = FSMStorage()

def state_filter(expected_state):
    """
    Создает пользовательский фильтр для проверки состояния пользователя в процессе работы FSM.
    Аргументы:
        expected_state (list or str): Состояние или список состояний, которые должны быть у пользователя 
                                      для прохождения фильтра.
    Возвращает:
        Filter: Кастомный фильтр для использования с обработчиками Pyrogram.
    """
    async def func(_, __, message: Message):
        user_id = message.from_user.id
        state = await storage.get_state(user_id)
        return state in expected_state
    return create(func)
