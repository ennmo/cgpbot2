from aiogram.dispatcher.middlewares import BaseMiddleware
from create import dp
from aiogram import types


class TypingMiddleware(BaseMiddleware):
    @staticmethod
    async def on_process_update(update: types.Update, data: dict):
        await dp.bot.send_chat_action(update.message.chat.id, "typing")

