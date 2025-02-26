from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from datetime import date
from database.Database import DataBase
from datetime import datetime


async def inline_ls(lst):
    keyboard = InlineKeyboardBuilder()
    if lst:
        for i in lst:
            keyboard.add(InlineKeyboardButton(text=f"🏠 {str(i['ls'])}-{str(i['kv'])}", callback_data=f"show_ls:{str(i['ls'])}"))
    keyboard.add(InlineKeyboardButton(text=f'🔍 Добавить лицевой счет', callback_data='add_ls'))
    return keyboard.adjust(1).as_markup()


#--------------------------------------------------------------
async def inline_show_ipu(ls: int, ipu):
    keyword = InlineKeyboardBuilder()
    type_mapping = {
        'hv': 'ХВС',
        'gv': 'ГВС',
        'e': 'ЭЛ-ВО'
    }

    if ipu:
        current_date = date.today()
        db = DataBase()
        # получаем посдедние показания
        last = await db.get_pokazaniya(ls, flag='last')
        # извлекаем дату и переводим в праильный формат
        if last['last']['date']:
            date_last = datetime.strptime(last['last']['date'], '%Y-%m-%d').date()
        else:
            date_last = None    
        # print(f"date_last:{date_last}|type:({type(date_last)})")
        # print(f"ipu:{ipu}")
        # print(f"last:{last}")
        for i in ipu:
            # print(f"i={i['type']}")
            # извлекаем дату и переводим в праильный формат
            if i['data_pov_next']:
                data_pov_next = datetime.strptime(i['data_pov_next'], '%Y-%m-%d').date()
            else:
                data_pov_next = None    
            # print(f"data_pov_next:{data_pov_next}|type:({type(data_pov_next)})")
           
            display_type = type_mapping.get(i['type'], i['type'])
            display_new = ""
            date_message = ""
            
            if last is not None and date_last == current_date:
                if i['type'] == 'hv' and last['hv'] is not None:
                    display_new = ' 🆕'
                elif i['type'] == 'gv' and last['gv'] is not None:
                    display_new = ' 🆕'
                elif i['type'] == 'e' and last['e'] is not None:
                    display_new = ' 🆕'

            if data_pov_next is not None:
                if data_pov_next > current_date:
                    date_message = f"(Поверка:{data_pov_next.strftime('%d-%m-%Y')})"
                else:
                    date_message = "(Счетчик просрочен)"
                    # continue  # надо чтобы если просрочен то пропускать итерацию и не выводить просроченый счетчик

            number_display = f", №{i['number']} " if len(i['number']) > 4 else ' '
            location_display = i['location'] if i['location'] is not None else ' '

            # print(f"{display_type}{display_new}{number_display}{location_display}{date_message}")
            keyword.row(InlineKeyboardButton(
                text=f"{display_type}{display_new}{number_display}{location_display}{date_message}",
                callback_data=f"add_pokazaniya:{i['ls']}:{i['type']}"
            ))

    keyword.row(
        InlineKeyboardButton(text='⬅️ Возврат в начало', callback_data='all_ls_call'),
        InlineKeyboardButton(text='❌ Отвязать счет', callback_data=f'del_ls:{ls}')
    )

    return keyword.as_markup()
#--------------------------------------------------------------
async def inline_del_ls(ls: int):
    keyword = InlineKeyboardBuilder()
    keyword.row(InlineKeyboardButton(text=f'Да', callback_data=f'del_ls_yes:{ls}'),
                InlineKeyboardButton(text=f'Нет', callback_data=f'all_ls_call'))
    return keyword.as_markup()
#--------------------------------------------------------------

