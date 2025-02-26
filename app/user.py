from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
import app.keyboards as kb
import logging
from aiogram.fsm.context import FSMContext
from app.states import AddLs, AddPokazaniya
from typing import Any, Dict
from database.Database import DataBase
from datetime import date
from core.log import Loger
from core.dictionary import *

# Настройка логирования
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
# )
# logger = logging.getLogger(__name__)
logger = Loger()
logger.get_name_log(__name__)

user = Router()

type_mapping = {
    'hv': 'ХВС',
    'gv': 'ГВС',
    'e': 'ЭЛ-ВО'
}
#========================================================
@user.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await logger.info(f'ID_TG:{message.from_user.id}|Команда старт')
    await state.clear()
    db = DataBase()
    user_state = await db.get_state(message.from_user.id)
    await db.delete_messages(user_state)
    await message.answer(welcom_text)
    await all_ls(user_state, message)
#========================================================
@user.message(AddLs.ls)
async def process_ls(message: Message, state: FSMContext):
    if 6 <= len(message.text) <= 8:  # длина лицевого
        try:
            await state.update_data(ls=int(message.text))
            await state.set_state(AddLs.kv)
            await logger.info(f'ID_TG:{message.from_user.id}|Переходим к вводу квартиры')
            await message.answer("Очень хорошо! Теперь введите номер квартиры (не более 3 символов).")
        except ValueError:
            await logger.error(f'ID_TG:{message.from_user.id}|Введеный лицевой не является числом')
            await message.answer("Вы ввели некорректное значение! Введите номер лицевого счета еще раз")
    else:
        await logger.error(f'ID_TG:{message.from_user.id}|Неправильная длина лицевого')
        await message.answer("Вы ввели некорректное значение! Введите номер лицевого счета еще раз")
#========================================================
@user.message(AddLs.kv)
async def process_kv(message: Message, state: FSMContext):
    if 1 <= len(message.text) <= 3:
        try:
            data = await state.update_data(kv=int(message.text))
            await state.clear()
            await logger.info(f'ID_TG:{message.from_user.id}|Переходим к поиску лицевого')
            await message.answer("Подождите, идёт поиск и привязка лицевого счета..")
            await check_ls(message=message, data=data)
        except ValueError:
            await logger.error(f'ID_TG:{message.from_user.id}|Введенная квартира не является числом')
            await message.answer("Вы ввели некорректное значение! Введите номер квартиры еще раз")
    else:
        await logger.error(f'ID_TG:{message.from_user.id}|Неправильная длина квартиры')
        await message.answer("Вы ввели некорректное значение! Введите номер квартиры еще раз")



############ CALLBACK #####################
@user.callback_query(F.data == 'add_ls')
async def add_ls(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddLs.ls)
    db = DataBase()
    user_state = await db.get_state(callback.from_user.id)
    await db.delete_messages(user_state)
    await callback.answer()
    await callback.message.answer(input_ls_text)
#===========================================   
@user.callback_query(F.data.startswith('show_ls:'))
async def show_ls(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await logger.info(f"ID_TG:{callback.from_user.id}|state.get_state()=>{await state.get_state()}")
    db = DataBase()
    user_state = await db.get_state(callback.from_user.id)
    await db.delete_messages(user_state)
    await callback.answer()
    ls = int(callback.data.split(':')[1])
    await logger.info(f'ID_TG:{callback.from_user.id}|callback_show_ls:{ls}')
    await callback.message.answer("Получение списка счётчиков... ожидайте.")
    ipu = await db.get_ipu(ls)
    # print(f"ipu:{ipu}")
    if not ipu:
        await callback.message.answer(f"❌ На лицевом счете №{ls} не найдены приборы учета❗️")
    users = await db.get_users(ls)
    user_state = await db.get_state(callback.from_user.id)

    sent_mess = await callback.message.answer(
        f"Лицевой счет № {ls}\n"
        f"Адрес: {users['address']}\n"
        f"{'Выберите прибор учета из списка' if ipu else '❌ На лицевом счете не найдены приборы учета❗️'}",
        reply_markup=await kb.inline_show_ipu(ls, ipu)
    )
    user_state.last_message_ids.append(sent_mess.message_id)
    await db.update_state(user_state) 
#===========================================  
@user.callback_query(F.data == 'all_ls_call')
async def all_ls_call(callback: CallbackQuery):
    db = DataBase()
    user_bot = await db.get_userbot(callback.from_user.id)
    user_state = await db.get_state(callback.from_user.id)
    await db.delete_messages(user_state)
    await logger.info(f'ID_TG:{callback.from_user.id}|all_ls_call:user_id={callback.from_user.id}')
    sent_mess = await callback.message.answer(text='Выберите Лицевой счёт из списка, либо добавьте новый',
                                              reply_markup=await kb.inline_ls(user_bot))
    user_state.last_message_ids.append(sent_mess.message_id)
    await db.update_state(user_state)  
#===========================================  
@user.callback_query(F.data.startswith('del_ls:'))
async def del_ls(callback: CallbackQuery):
    ls = int(callback.data.split(':')[1])
    db = DataBase()
    users = await db.get_users(ls)
    # print(f"users:{users}")
    user_state = await db.get_state(callback.from_user.id)
    await db.delete_messages(user_state)
    await logger.info(f"ID_TG:{callback.from_user.id}|Поступил запрос на удаление лицевого {ls}")
    sent_mess = await callback.message.answer(f"Вы точно хотите отвязать Лицевой счет?\n"
                                              f"Счет № {ls}\n"
                                              f"Адрес: {users['address']}", reply_markup=await kb.inline_del_ls(ls))
    user_state.last_message_ids.append(sent_mess.message_id)
    await db.update_state(user_state)
  
#===========================================
@user.callback_query(F.data.startswith('del_ls_yes:'))
async def del_ls(callback: CallbackQuery):
    ls = int(callback.data.split(':')[1])
    id_tg = callback.from_user.id
    db = DataBase()
    user_state = await db.get_state(callback.from_user.id)
    if await db.del_ls(id_tg, ls):
        await callback.message.answer(f'Лицевой счет №{ls} успешно отвязан!')
    await db.delete_messages(user_state)
    await all_ls(user_state, callback.message)
    
#===========================================    


############ FUNCTION ######################
async def all_ls(state, message):
    await logger.info(f'ID_TG:{message.from_user.id}|all_ls:user_id={state.user_id}')
    db = DataBase()
    user_bot = await db.get_userbot(state.user_id)

    # print(f"user_bot:{user_bot}")
    sent_mess = await message.answer(text=check_ls_list_text,
                                     reply_markup=await kb.inline_ls(user_bot))
    state.last_message_ids.append(sent_mess.message_id)
    await db.update_state(state)   
# ===================================  
async def check_ls(message: Message, data: Dict[str, Any]):
    db = DataBase()
    await logger.info(f"ID_TG:{message.from_user.id}|check_ls:{data['ls']};kv:{data['kv']}")
    # проверяем если такой профиль
    u = await db.get_users(data['ls'], data['kv'])
    if u:
        await logger.info(f"ID_TG:{message.from_user.id}|такой юзер есть:{u['ls']}")
        if await db.get_userbot(message.from_user.id, u['ls']):
            await message.answer(f"⛔ Лицевой счет уже добавлен!")
            user_state = await db.get_state(message.from_user.id)
            await all_ls(user_state, message)
        else:
            # await db.create_userbot(id_tg=message.from_user.id, ls=u.ls, home=u.home, kv=u.kv)
            kwargs = {
                'id_tg': message.from_user.id,
                'ls': u['ls'],
                'home': u['home'],
                'kv': u['kv']
            }
            if await db.create_userbot(**kwargs):
                await message.answer(f"Лицевой счет №{u['ls']} успешно добавлен.")
                user_state = await db.get_state(message.from_user.id)
                await all_ls(user_state, message)
            else:
                await message.answer('❌ Не удалось добавить лицевой счет! Обратитесь в офис ТСН')

    else:
        await logger.error(f'ID_TG:{message.from_user.id}|такого юзере НЕТ')
        await message.answer('❌ Не удалось найти указанный лицевой счет! Обратитесь в офис ТСН')
        user_state = await db.get_state(message.from_user.id)
        await all_ls(user_state, message) 
# ===================================    
# ===================================
#     