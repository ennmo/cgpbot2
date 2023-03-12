import datetime
import handlers.other
from create import dp, openai_key
from aiogram import types
from keyboards.keyboard import *
from answers.answers_dict import *
from database.db_start import users_collection, text, chatgpt_requests
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
import openai
import multiprocessing

openai.api_key = openai_key


class Lang(StatesGroup):
    lang = State()
    chatgpt = State()
    start = State()


async def hello(message: types.Message) -> None:
    dt = datetime.datetime.fromtimestamp(dict(message)["date"])
    user_id = message.from_user.id
    lang = users_collection.find_one({"user_id": user_id})
    if lang:
        if lang['lang_check'] == 2:
            await message.reply(ans['welcomeback' + lang["lang"]],
                                reply_markup=kb3ru if lang["lang"] == "ru" else kb3en)
        else:
            await Lang.lang.set()
            await message.reply("Hello, select language", reply_markup=kb)
    else:
        await Lang.lang.set()
        await message.reply("Hello, select language", reply_markup=kb)
        users_collection.insert_one({
            "user_id": user_id,
            "first_name": message.from_user.first_name,
            "username": message.from_user.username,
            "reg_date": dt.strftime("%Y.%m.%d"),
            "reg_time": dt.strftime("%H:%M:%S"),
            "requests": 0,
            "lang": "en",
            "lang_check": 1
        })
        text.insert_one({
            "user_id": user_id,
            "first_name": message.from_user.first_name,
            "username": message.from_user.username,
            "messages": []
        })
        chatgpt_requests.insert_one({
            "user_id": user_id,
            "messages": []
        })


async def choose_lang(message: types.Message) -> None:
    await Lang.lang.set()
    await message.reply(ans["change_lang" + users_collection.find_one({"user_id": message.from_user.id})['lang']],
                        reply_markup=kb)


async def answer_language(message: types.Message, state: FSMContext) -> None:
    if message.text == "English":
        users_collection.update_one({"user_id": message.from_user.id}, {"$set": {"lang": "en", "lang_check": 2}})
        await message.reply("Language selected", reply_markup=kb3en)
    else:
        users_collection.update_one({"user_id": message.from_user.id}, {"$set": {"lang": "ru", "lang_check": 2}})
        await message.reply("Язык выбран", reply_markup=kb3ru)
    await state.finish()


async def not_answer_language(message: types.Message) -> None:
    await message.reply(ans['choose_from_list' + users_collection.find_one({"user_id": message.from_user.id})['lang']])


async def help_command(message: types.Message) -> None:
    await message.reply(ans_help['help_' + users_collection.find_one({"user_id": message.from_user.id})['lang']])


async def start_chatgpt(message: types.Message) -> None:
    await Lang.chatgpt.set()
    await message.reply(ans['write_text_' + users_collection.find_one({"user_id": message.from_user.id})['lang']],
                        reply_markup=chatgpt_en if users_collection.find_one({"user_id": message.from_user.id})[
                                                       'lang'] == "en" else chatgpt_ru)


async def chatgpt_text(message: types.Message) -> None:
    p = multiprocessing.Process(target=handlers.other.send_action, args=(message.chat.id,))
    p.start()
    chatgpt_requests.update_one({"user_id": message.from_user.id}, {"$push": {"messages": message["text"]}})
    old_mes = str(chatgpt_requests.find_one({"user_id": message.from_user.id})["messages"])
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": old_mes},
                  {"role": "user", "content": f'Предыдущие сообщения: {old_mes}; Запрос: {message.text}'}],
        presence_penalty=0.6)
    await message.answer(response.choices[0].message["content"])
    p.terminate()
    dt = datetime.datetime.fromtimestamp(dict(message)["date"])
    text.update_one({"user_id": message.from_user.id}, {"$push": {"messages": {"date": dt, "text": message["text"]}}})


async def chatgpt_cancel(message: types.Message, state: FSMContext) -> None:
    if message.text not in ("Очистить историю", "Clear history"):
        await message.reply(ans['canceled_' + users_collection.find_one({"user_id": message.from_user.id})['lang']],
                            reply_markup=kb3en if users_collection.find_one({"user_id": message.from_user.id})[
                                                      'lang'] == "en" else kb3ru)
        await state.finish()
    else:
        chatgpt_requests.update_one({"user_id": message.from_user.id}, {"$unset": {"messages": ""}})
        chatgpt_requests.update_one({"user_id": message.from_user.id}, {"$set": {"messages": []}})
        await message.reply(ans["cleaned_" + users_collection.find_one({"user_id": message.from_user.id})['lang']])


async def possible_restart(message: types.Message) -> None:
    try:
        await message.answer(
            ans["write_normal_text_" + users_collection.find_one({"user_id": message.from_user.id})['lang']],
            reply_markup=kb3ru if users_collection.find_one({"user_id": message.from_user.id})[
                                      'lang'] == "ru" else kb3en)
    except TypeError:
        await message.answer("Напиши /start", reply_markup=kb_start_general)


def register_handlers_client() -> None:
    dp.register_message_handler(hello, commands="start", state=None)
    dp.register_message_handler(answer_language, lambda message: message.text in ("Русский", "English"),
                                state=Lang.lang)
    dp.register_message_handler(not_answer_language, lambda message: message.text not in ("Русский", "English"),
                                state=Lang.lang)
    dp.register_message_handler(choose_lang, lambda message: message.text in ("Сменить язык", "Change language"),
                                state=None)
    dp.register_message_handler(help_command, lambda message: message.text in ("Помощь", "Help"), state=None)
    dp.register_message_handler(start_chatgpt,
                                lambda message: message.text in ("Начать чат с ChatGPT", "Start chat with ChatGPT"),
                                state=None)
    dp.register_message_handler(chatgpt_cancel, lambda message: message.text in ("Отменить",
                                                                                 "Cancel", "/start",
                                                                                 "Очистить историю",
                                                                                 "Clear history"),
                                state=Lang.chatgpt)
    dp.register_message_handler(possible_restart, state=None)
    dp.register_message_handler(chatgpt_text, state=Lang.chatgpt)
