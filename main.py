import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.types import ParseMode, BotCommand
from aiogram.utils import executor
from config import API_TOKEN, REDIS_URL, REDIS_PORT, POSTGRES_URL
from database import Database
import handlers
import redis.asyncio as redis

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)

dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

database = Database(dsn=POSTGRES_URL)

async def on_startup(dispatcher: Dispatcher):
    redis_client = redis.Redis(host=REDIS_URL, port=REDIS_PORT)
    storage = RedisStorage2(redis_client)
    dispatcher.storage = storage

    await database.connect()
    await set_bot_commands(dispatcher)

async def set_bot_commands(dispatcher: Dispatcher):
    commands = [
        BotCommand(command="/start", description="Перезапуск 🚀"),
        BotCommand(command="/menu", description="Меню 📌"),
    ]
    await bot.set_my_commands(commands)

handlers.register_handlers(dp, database)

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
