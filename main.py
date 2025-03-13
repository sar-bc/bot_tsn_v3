import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import logging
from app.user import user
# from app.admin import admin
from database.Database import DataBase
from dotenv import load_dotenv
import os
from core.log import Loger

# # Настройка логирования
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
# )
# logger = logging.getLogger(__name__)
logger = Loger()
logger.get_name_log(__name__)
# Загружаем переменные окружения
load_dotenv()
BASE_URL = os.getenv('BASE_URL')
TOKEN = os.getenv('TOKEN')

bot = Bot(token=TOKEN,
          default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


async def main():
    # dp.include_routers(user, admin)
    dp.include_routers(user)
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)

    await dp.start_polling(bot)


async def startup(dispatcher: Dispatcher):
    db = DataBase()
    await db.create_db()
    await logger.info('Starting up...')


async def shutdown(dispatcher: Dispatcher):
    await logger.info('Shutting down...')


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
