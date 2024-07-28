import logging
from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import Database

class Form(StatesGroup):
    city = State()

async def start_command(message: types.Message):
    await message.answer("Введите название вашего города:")

async def city_input(message: types.Message, state: FSMContext, db: Database):
    city = message.text.strip()
    logging.info(f"Adding city: {city}")
    await db.add_city(city)
    logging.info(f"City added: {city}")
    nearest_city = await db.get_nearest_city(city)
    logging.info(f"Nearest city: {nearest_city}")
    if nearest_city:
        inline_kb = InlineKeyboardMarkup().add(InlineKeyboardButton("Следующий город", callback_data="next_city"))
        await message.answer(f"Ближайший зарегистрированный город: {nearest_city}", reply_markup=inline_kb)
        await state.update_data(current_city=city, nearest_city=nearest_city)
    else:
        await message.answer("Других зарегистрированных городов пока нет.")
    await Form.next()

async def next_city(callback_query: types.CallbackQuery, state: FSMContext, db: Database):
    data = await state.get_data()
    current_city = data.get('current_city')
    logging.info(f"Current city: {current_city}")
    nearest_city = await db.get_nearest_city(current_city)
    logging.info(f"Next nearest city: {nearest_city}")
    if nearest_city:
        inline_kb = InlineKeyboardMarkup().add(InlineKeyboardButton("Следующий город", callback_data="next_city"))
        await callback_query.message.edit_text(f"Следующий ближайший зарегистрированный город: {nearest_city}", reply_markup=inline_kb)
        await state.update_data(nearest_city=nearest_city)
    else:
        await callback_query.message.edit_text("Других зарегистрированных городов больше нет.")
    await callback_query.answer()

def register_handlers(dp: Dispatcher, db: Database):
    dp.register_message_handler(start_command, commands='start', state="*")
    dp.register_message_handler(city_input, state=Form.city, content_types=types.ContentTypes.TEXT)
    dp.register_callback_query_handler(next_city, Text(equals='next_city'), state=Form.city)
