from datetime import time
import time
from aiogram import types, F
from aiogram.enums import ContentType, ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from handlers.users_handlers import start, boys
from main import db, bot, dp


class AddGift(StatesGroup):
    message = State()


admins = (825355608, 825355608)


@dp.message(Command('admin'))
async def get_db(message: types.Message):
    if message.chat.id in admins:
        table_message = ''
        users = await db.get_users_table()
        for user in users:
            for i in range(len(user)):
                if i == 2:
                    table_message += f'tg://user?id={user[1]}\t\t{user[i] if user[i] is not None else "?guest"}\t\t'
                else:
                    table_message += f'{user[i]}\t\t'
            table_message += '\n'
        await message.answer(table_message)
    else:
        msg = await message.answer('😾 Куда лезем')
        time.sleep(3)
        await message.delete()
        await bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id, parse_mode=ParseMode.HTML)


@dp.message(F.text == '🎁 Добавить Подарок')
async def get_gift_data(message: types.Message, state: FSMContext):
    print(message)
    if message.chat.id in boys or message.chat.id in admins:
        await message.answer(text='Введи данные подарка:\nНазвание\nописание\nкатегория\nссылка')
        await state.set_state(AddGift.message)
    else:
        await start(message)


@dp.message(AddGift.message)
async def add__gift(message: types.Message, state: FSMContext):
    print(message)
    if str(message.text)[0] == '/':
        await state.clear()
        await start(message)
    else:
        await state.update_data(message=message)
        data = await state.get_data()
        gift = data['message'].caption.split('\n')
        image = data['message'].photo[0].file_id
        for_who = boys.get(message.chat.id)
        await db.add_gift(gift[0], gift[1], gift[2], image, gift[-1], for_who)
        await state.clear()
        await message.answer('🙈 Подарок Добавлен')


