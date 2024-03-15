from datetime import datetime
from sqlite3 import IntegrityError

from aiogram import types, F
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.command import CommandStart

from main import dp, db, bot, CallBackData

boys = {987828750: 'bogdan', 1182690511: 'matveo', 825355608: 'evgenadmin'}


def generate_markup(btn_type: str, back_to: str, pers: str, category: str, data: [list or set]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    cat = category
    for el in data:
        category = el[0] if cat == '-' else category
        builder.row(InlineKeyboardButton(text=el[0],
                                         callback_data=CallBackData(type=btn_type, person=pers, category=category,
                                                                    product=el[0]).pack()))
        print('callback_data =', CallBackData(type=btn_type, person=pers, category=category, product=el[0]).pack())
    if category != 'person':
        builder.row(InlineKeyboardButton(text='⬅️ back', callback_data=f'btn:{back_to}:{pers}:{category}:-'))
    return builder.as_markup()


@dp.message(CommandStart())
async def start(message: types.Message):
    try:
        await db.add_user(message.chat.id, message.chat.username)
    except IntegrityError:
        pass
    finally:
        # if message.chat.id in boys:
        #     markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='🎁 Добавить Подарок')]], resize_keyboard=True)
        #     await message.answer('"', reply_markup=markup)
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text='bogdan', callback_data=CallBackData(type='pers', person='bogdan').pack())) \
            .row(InlineKeyboardButton(text='matveo', callback_data=CallBackData(type='pers', person='matveo').pack()))
        try:
            await message.edit_text('<b>pick someone 🤗🤗🤗</b>', reply_markup=builder.as_markup(),
                                    parse_mode=ParseMode.HTML)
        except Exception as e:
            await message.answer('<b>pick someone 🤗🤗🤗</b>', reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)


@dp.callback_query(CallBackData.filter(F.type == 'pers'))
async def get_person_categories(call: types.CallbackQuery, callback_data: CallBackData):
    categories = set(await db.get_categories(callback_data.person))
    categories_markup = generate_markup(btn_type='category', back_to='to_persons', pers=callback_data.person,
                                        category='-',
                                        data=categories)
    await call.message.edit_text('<b>choose ur position 🤪🤑😎</b>', reply_markup=categories_markup,
                                 parse_mode=ParseMode.HTML)


@dp.callback_query(CallBackData.filter(F.type == 'to_persons'))
async def back_to_pers(call: types.CallbackQuery):
    await start(call.message)


@dp.callback_query(CallBackData.filter(F.type == 'category'))
async def get_gifts_by_category(call: types.CallbackQuery, callback_data: CallBackData):
    gifts = await db.get_gifts(callback_data.category)
    gifts_markup = generate_markup(btn_type='gift', back_to='to_categories', pers=callback_data.person,
                                   category=callback_data.category, data=gifts)
    try:
        await call.message.edit_text('<b>think about it what is more important to him 💯💯💯</b>',
                                     reply_markup=gifts_markup, parse_mode=ParseMode.HTML)
    except Exception as e:
        await call.message.answer('<b>think about it what is more important to him 💯💯💯</b>', reply_markup=gifts_markup,
                                  parse_mode=ParseMode.HTML)


@dp.callback_query(CallBackData.filter(F.type == 'to_categories'))
async def back_to_categories(call: types.CallbackQuery, callback_data: CallBackData):
    await get_person_categories(call, callback_data)


@dp.callback_query(CallBackData.filter(F.type == 'gift'))
async def get__gift(call: types.CallbackQuery, callback_data: CallBackData):
    print(datetime.now(), call.data)
    pers, cat, prod = callback_data.person, callback_data.category, callback_data.product
    gift = await db.get_gift(callback_data.product)
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='✅ add a gift',
                                     callback_data=CallBackData(type='add', person=pers, category=cat,
                                                                product=prod).pack()))
    builder.row(InlineKeyboardButton(text='⬅️ back',
                                     callback_data=CallBackData(type='to_gifts', person=pers, category=cat,
                                                                product=prod).pack()))
    img, desc = gift[0][1], gift[0][0]
    await call.message.delete()
    await call.message.answer_photo(photo=img, caption=desc, reply_markup=builder.as_markup())


@dp.callback_query(CallBackData.filter(F.type == 'to_gifts'))
async def back_to_gifts(call: types.CallbackQuery, callback_data: CallBackData):
    await call.message.delete()
    await get_gifts_by_category(call, callback_data)


@dp.callback_query(CallBackData.filter(F.type == 'add'))
async def add__gift(call: types.CallbackQuery, callback_data: CallBackData):
    gift_to = 'for_' + callback_data.person
    print(gift_to)
    if bool(list(await db.is_gift_chosen_by_user(call.message.chat.id, gift_to))[0]):
        await call.answer(text=f"⚠️ WARNING ⚠️\nyou've already chosen a gift for {callback_data.person}",
                          show_alert=True)
    else:
        try:
            await db.add_gift_to_user(gift_to, callback_data.product, call.message.chat.id)
            link = list(await db.get_link(callback_data.product))[0]
            builder = InlineKeyboardBuilder()
            builder.row(InlineKeyboardButton(text='🔴 link on gift 🔴', url=link))
            builder.row(InlineKeyboardButton(text='remove gift',
                                             callback_data=CallBackData(type='remove_gift', person=callback_data.person,
                                                                        product=callback_data.product).pack()))
            builder.row(InlineKeyboardButton(text='main',
                                             callback_data=CallBackData(type='to_persons').pack()))
            await call.message.edit_reply_markup(reply_markup=builder.as_markup())
            await call.answer(text='good choice✅\nty for gifts🥺♥️', show_alert=True)
            # await db.delete_gift(callback_data.get('product'))
        except IntegrityError:
            await call.answer(text="⚠️ WARNING ⚠️\nthis gift has already chosen", show_alert=True)


@dp.callback_query(CallBackData.filter(F.type == 'remove_gift'))
async def remove_gift(call: types.CallbackQuery, callback_data: CallBackData):
    print('for_' + callback_data.person, call.message.chat.id)
    await db.remove_gift('for_' + callback_data.person, call.message.chat.id)
    await call.answer(text="⚠️ WARNING ⚠️\ngift removed", show_alert=True)
