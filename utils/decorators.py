import logging

from pyrogram import Client
from pyrogram.types import Message, CallbackQuery

logger = logging.getLogger("test_bot")

def error_handler(handler):
    async def wrapper(*args, **kwargs):
        client = None
        for arg in args:
            if isinstance(arg, Client):
                client = arg
                break

        if not client:
            logger.error("Client object not found in arguments!")
            return
        try:
            await handler(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in handler '{handler.__name__}': {e}")
            target = None
            for arg in args:
                if isinstance(arg, (Message, CallbackQuery)):
                    target = arg
                    break
            if target:
                user_id = target.from_user.id if isinstance(target, Message) else target.message.chat.id
                await send_error_message(client, user_id)
            else:
                logger.error("Could not determine the target for the error message.")
    return wrapper


async def send_error_message(client: Client, user_id):
    try:
        await client.send_message(
            chat_id=user_id,
            text="An error occurred. Please try again later."
        )
    except Exception as e:
        logger.error(f"Failed to send error message to user {user_id}: {e}")
