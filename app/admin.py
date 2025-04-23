import asyncio
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
# from aiogram.types import Message, CallbackQuery, ContentType, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import types
from database.Database import DataBase
from database.models import UserState
import logging
from core.log import Loger
from core.dictionary import *
import app.keyboards as kb
from app.states import SendMess
# для работы с файлами
from dotenv import load_dotenv
import os

import re
import locale
from datetime import datetime, timedelta

import json
import sys
import io

load_dotenv()

# # Установка русской локали
# locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

# Настройка логирования
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
# )
# logger = logging.getLogger(__name__)

# custom loger
logger = Loger()
logger.get_name_log(__name__)

admin = Router()




@admin.message(Command("message", prefix="#")) 
async def handle_id_command(message: types.Message, state: FSMContext):
    await logger.info(f'ID_TG:{message.from_user.id}|Запуск отправки сообщений')
    await state.clear()
    db = DataBase()
    user_state = await db.get_state(message.from_user.id)
    await db.delete_messages(user_state)
    sent_mess = await message.answer(input_message_text)
    user_state.last_message_ids.append(sent_mess.message_id)
    await db.update_state(user_state)
    await state.set_state(SendMess.mess)


@admin.message(SendMess.mess)
async def process_send_mess(message: types.Message, state: FSMContext): 
    await state.clear()
    mess_text = message.text
    db = DataBase()
    user_state = await db.get_state(message.from_user.id)
    await db.delete_messages(user_state)
    await logger.info(f'ID_TG:{message.from_user.id}|Отправка сообщения:{mess_text}')
    ids_bots = await db.get_users_bot()
    await message.answer("Идет отправка. Ожидайте... ")
    if ids_bots:
        res = await send_mess(message, ids_bots, mess_text)
        await message.answer(f"✅ Сообщение успешно отправлено. {res}шт")
    else:
        await message.answer("❌ Нет пользователей")
        await logger.info(f'ID_TG:{message.from_user.id}|Нет пользователей')    




# =============FUNCTIN==================
async def send_mess(message, ids, message_text):
    i = 0
    # from main import bot
    for user_id in ids:
        try:
            await message.bot.send_message(user_id, message_text)
            # await logger.info(f"Сообщение отправлено пользователю {user_id}.")
            i += 1
        except Exception as e:
            await logger.error(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
    return i
