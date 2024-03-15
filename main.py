# 987828750
# 1182690511
import logging
from aiogram import Bot, Dispatcher
import asyncio
from aiogram.filters.callback_data import CallbackData
from aiogram.types.bot_command import BotCommand

from database.db import DataBase

token = '6857554825:AAFUxcc43OfHkTJ7Q13t-_HBwNLCGopQ6V4'

bot = Bot(token=token)
dp = Dispatcher()
db = DataBase("database\\wishlist_data.db3")


class CallBackData(CallbackData, prefix='btn'):
    type: str = '-'
    person: str = '-'
    category: str = '-'
    product: str = '-'


logging.basicConfig(level=logging.INFO)


async def main():
    from handlers import dp
    try:
        await bot.set_my_commands([BotCommand(command='start', description='open')])
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, RuntimeError, SystemExit):
        print('Bot stopped!')
