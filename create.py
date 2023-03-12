from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from dotenv import load_dotenv
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os


load_dotenv()
tg_token = os.getenv("TGTOKEN")
openai_key = os.getenv("OPENAIKEY")
tgbot = Bot(token=tg_token)
dp = Dispatcher(tgbot, storage=MemoryStorage())
