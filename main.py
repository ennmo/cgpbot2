from aiogram.utils import executor
from create import dp
from handlers import client

client.register_handlers_client()


async def on_shutdown(dp):
    await dp.storage.close()
    await dp.storage.wait_closed()
    print("The program has been successfully closed")


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=print('The bot is running'),
                           on_shutdown=on_shutdown, skip_updates=True)
