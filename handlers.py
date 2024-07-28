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
    db = state.bot.get('db')

    logging.info(f"User entered city: {city_name}")

    async with db.pool.acquire() as conn:
        city = await conn.fetchrow("SELECT * FROM cities WHERE name = $1", city_name)
        if city is None:

            await conn.execute("INSERT INTO cities (name) VALUES ($1)", city_name)
            logging.info(f"City {city_name} registered")

        cities = await conn.fetch("SELECT * FROM cities")

    nearest_city = None
    for c in cities:
        if c['name'] != city_name:
            nearest_city = c['name']
            break

    if nearest_city:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text="+", callback_data='+'))
        await message.reply(f"Ближайший зарегистрированный город: {nearest_city}", reply_markup=keyboard)
    else:
        await message.reply("Нет других зарегистрированных городов.")
    
    await state.finish()

async def next_city(callback_query: types.CallbackQuery, state: FSMContext):
    current_city = (await state.get_data()).get("current_city")
    db = state.bot.get('db')

    async with db.pool.acquire() as conn:
        cities = await conn.fetch("SELECT * FROM cities")

    nearest_city = None
    for c in cities:
        if c['name'] != current_city:
            nearest_city = c['name']
            break

    if nearest_city:
        await callback_query.message.answer(f"Следующий ближайший зарегистрированный город: {nearest_city}")
        await state.update_data(current_city=nearest_city)
    else:
        await callback_query.message.answer("Нет других зарегистрированных городов.")

    await callback_query.answer()

def register_handlers(dp: Dispatcher, db):
    dp['db'] = db
    dp.register_message_handler(start_command, commands='start', state="*")
    dp.register_message_handler(city_input, state=Form.city, content_types=types.ContentTypes.TEXT)
    dp.register_callback_query_handler(next_city, text='+')
