import logging
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class Form(StatesGroup):
    city = State()

async def start_command(message: types.Message):
    await Form.city.set()
    await message.reply("Введите название вашего города:")

async def city_input(message: types.Message, state: FSMContext):
    city_name = message.text.strip().capitalize()
    bot = message.bot
    db = bot.get('db')

    logging.info(f"User entered city: {city_name}")

    async with db.pool.acquire() as conn:
        city = await conn.fetchrow("SELECT * FROM cities WHERE name = $1", city_name)
        if city is None:
            await conn.execute("INSERT INTO cities (name) VALUES ($1)", city_name)
            logging.info(f"City {city_name} registered")

        last_city = await conn.fetchrow("SELECT * FROM cities ORDER BY id DESC LIMIT 1")

    if last_city:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text="+", callback_data='next_city'))
        await message.reply(f"Последний зарегистрированный город: {last_city['name']}", reply_markup=keyboard)
        await state.update_data(current_city=city_name, last_city=last_city['name'])
    else:
        await message.reply("Нет других зарегистрированных городов.")
    
    await Form.city.set()

async def next_city(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_city = data.get("last_city")
    bot = callback_query.bot
    db = bot.get('db')

    async with db.pool.acquire() as conn:
        last_city = await conn.fetchrow("SELECT * FROM cities ORDER BY id DESC LIMIT 1")

    if last_city:
        await callback_query.message.reply(f"Последний зарегистрированный город: {last_city['name']}")
        await state.update_data(last_city=last_city['name'])
    else:
        await callback_query.message.reply("Нет других зарегистрированных городов.")

    await callback_query.answer()

def register_handlers(dp: Dispatcher, db):
    dp['db'] = db
    dp.register_message_handler(start_command, commands='start', state="*")
    dp.register_message_handler(city_input, state=Form.city, content_types=types.ContentTypes.TEXT)
    dp.register_callback_query_handler(next_city, state=Form.city, text='next_city')
