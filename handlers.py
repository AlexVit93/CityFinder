import logging
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class Form(StatesGroup):
    city = State()

async def start_command(message: types.Message):
    await Form.city.set()
    await message.reply("Введите название вашего города или список городов через запятую:")

async def city_input(message: types.Message, state: FSMContext):
    city_names = [city.strip().title() for city in message.text.split(',')]
    bot = message.bot
    db = bot.get('db')

    logging.info(f"User entered cities: {city_names}")

    registered_cities = []

    async with db.pool.acquire() as conn:
        for city_name in city_names:
            city = await conn.fetchrow("SELECT * FROM cities WHERE name = $1", city_name)
            if city is None:
                await conn.execute("INSERT INTO cities (name) VALUES ($1)", city_name)
                registered_cities.append(city_name)
                logging.info(f"City {city_name} registered")

    if registered_cities:
        last_registered_city = registered_cities[-1]
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text="+", callback_data='next_city'))
        await message.reply(f"Последний зарегистрированный город: {last_registered_city}", reply_markup=keyboard)
        await state.update_data(current_city=registered_cities, last_city=last_registered_city)
    else:
        await message.reply("Все введенные города уже зарегистрированы.")

    await Form.city.set()

async def next_city(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_cities = data.get("current_city", [])
    if current_cities:
        last_registered_city = current_cities.pop()
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text="+", callback_data='next_city'))
        await callback_query.message.reply(f"Последний зарегистрированный город: {last_registered_city}", reply_markup=keyboard)
        await state.update_data(current_city=current_cities, last_city=last_registered_city)
    else:
        await callback_query.message.reply("Нет других зарегистрированных городов.")
        await state.finish()
    await callback_query.answer()

async def show_cities(message: types.Message):
    bot = message.bot
    db = bot.get('db')

    async with db.pool.acquire() as conn:
        cities = await conn.fetch("SELECT name FROM cities ORDER BY name")

    if cities:
        cities_list = "\n".join([city['name'] for city in cities])
        await message.reply(f"Список всех зарегистрированных городов:\n{cities_list}")
    else:
        await message.reply("Нет зарегистрированных городов.")

def register_handlers(dp: Dispatcher, db):
    dp['db'] = db
    dp.register_message_handler(start_command, commands='start', state="*")
    dp.register_message_handler(show_cities, commands='show_cities', state="*")
    dp.register_message_handler(city_input, state=Form.city, content_types=types.ContentTypes.TEXT)
    dp.register_callback_query_handler(next_city, state=Form.city, text='next_city')