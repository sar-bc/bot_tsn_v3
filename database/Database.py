from sqlalchemy import select, and_, delete, case, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from database.models import *
import os
import logging
from datetime import date
from datetime import datetime
import aiohttp

base_url = 'http://127.0.0.1:8000'
# from app.log import Loger

# # Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# logger = Loger(Data)
# logger.get_name_log(__name__)


type_mapping = {
    'hv': 'ХВС',
    'gv': 'ГВС',
    'e': 'ЭЛ-ВО'
}


class DataBase:
    def __init__(self):
        self.connect = 'sqlite+aiosqlite:///db.sqlite3'
        self.async_engine = create_async_engine(url=self.connect, echo=False)
        self.Session = async_sessionmaker(bind=self.async_engine, class_=AsyncSession)

        # self.db_host = os.getenv('DB_HOST')
        # self.db_user = os.getenv('DB_USER')
        # self.db_password = os.getenv('DB_PASSWORD')
        # self.db_name = os.getenv('DB_NAME')
        # self.connect = (f'mysql+aiomysql://{self.db_user}:{self.db_password}@{self.db_host}/'
        #                 f'{self.db_name}?charset=utf8mb4')
        # self.async_engine = create_async_engine(url=self.connect, echo=False)
        # self.Session = async_sessionmaker(bind=self.async_engine, class_=AsyncSession)

    async def create_db(self):
        async with self.async_engine.begin() as connect:
            await connect.run_sync(Base.metadata.create_all)

    async def log_to_db(self, level: str, message: str, logger_name: str):
        async with self.Session() as session:
            log_entry = Logs(
                timestamp=datetime.now(),  # Здесь можете использовать datetime.now().isoformat() для меток времени
                name=logger_name,
                level=level,
                message=message
            )
            session.add(log_entry)
            await session.commit()        

    async def get_state(self, id_tg: int):
        async with self.Session() as session:
            # Попытка получить состояние пользователя по user_id
            state = await session.scalar(select(UserState).where(UserState.user_id == id_tg))

            if state is None:
                logger.info(f'Состояние не найдено для user_state_id: {id_tg}. Создание нового состояния.')
                # Если состояния нет, создаем новое
                state = UserState(user_id=id_tg)
                session.add(state)
                await session.commit()  # Сохраняем изменения
                state = await session.scalar(select(UserState).where(UserState.user_id == id_tg))
                logger.info(f'Создано состояние user_state:{state.user_id}')
                return state
            else:
                logger.info(f'Получено состояние для user_state_id: {id_tg}.')

                return state

    async def update_state(self, state: UserState):
        async with self.Session() as session:
            # Убедитесь, что объект связан с текущей сессией
            existing_state = await session.execute(select(UserState).where(UserState.user_id == state.user_id))
            current_state = existing_state.scalars().one_or_none()

            if current_state:
                # Обновление атрибутов
                current_state.last_message_ids = state.last_message_ids
                current_state.kv = state.kv
                current_state.ls = state.ls
                current_state.home = state.home

                # Сохранение изменений
                await session.commit()
                return current_state  # Возвращаем обновленный объект
            else:
                return None  # Состояние не найдено

    async def delete_messages(self, state):
        if state.last_message_ids:
            from main import bot
            for lst in state.last_message_ids:
                try:
                    await bot.delete_message(chat_id=state.user_id, message_id=lst)
                except Exception as e:
                    logger.error(f"Ошибка при удалении сообщения: {e}")
            state.last_message_ids.clear()

    async def get_userbot(self, id_tg, ls=None):
        url = f"{base_url}/api/userbot/"
        headers = {
            'Authorization': os.getenv('API')
        }
        params = {'id_tg': id_tg}
        if ls:
            params['ls'] = ls

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    return {'error': f'Ошибка: {response.status}'}
                
    async def get_users(self, ls, kv=None):
        # проверяем если такой профиль response {'id': 3, 'ls': 40700101,.....}
        url = f"{base_url}/api/profile/"
        headers = {
            'Authorization': os.getenv('API')
        }
        params = {'ls': ls}     
        if kv:
            params['kv'] = kv

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    return {'error': f'Ошибка: {response.status}'}

    async def create_userbot(self, **kwargs):
        # записываем в базу
        url = f"{base_url}/api/userbot/"
        headers = {
            'Authorization': os.getenv('API'),  # Получаем токен из переменных окружения
            'Content-Type': 'application/json'
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=kwargs) as response:
                if response.status == 201:
                    response_data = await response.json()
                    return response_data
                else:
                    return {'error': f'Ошибка: {response.status}', 'message': await response.text()}
        
    async def get_ipu(self, ls, type_ipu=None):
        url = f"{base_url}/api/meterdev/"
        headers = {
            'Authorization': os.getenv('API')
        }
        params = {'ls': ls}
        if type_ipu:
            params['type'] = type_ipu

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    return {'error': f'Ошибка: {response.status}'}
                

    async def get_pokazaniya(self, ls, flag=None, month=None, year=None):
        url = f"{base_url}/api/pokazaniya/"
        headers = {
            'Authorization': os.getenv('API')
        }
        params = {'ls': ls}
        if flag:
            params['flag'] = flag
        if month:
            params['month'] = month   
        if year:
            params['year'] = year  

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    return {'error': f'Ошибка: {response.status}'}

    async def del_ls(self, id_tg, ls):
        url = f"{base_url}/api/userbot/"
        headers = {
            'Authorization': os.getenv('API')
        }
        params = {'id_tg': id_tg, 'ls': ls}

        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=headers, params=params) as response:
                if response.status == 204:  # Успешное удаление
                    return {'message': 'Пользователь успешно удален.'}
                else:
                    return {'error': f'Ошибка: {response.status}', 'message': await response.text()}
#=======================================================
    async def add_or_update_pokazaniya(self, ls, kv, type_ipu, value):
        # Получаем текущую дату
        current_date = date.today()

        url = f"{base_url}/api/pokazaniya/"
        headers = {
            'Authorization': os.getenv('API'),
            'Content-Type': 'application/json'
        }
        
        params = {'ls': ls, 'kv': kv, 'flag': 'last'}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status != 200:
                    return await handle_error(response)

                data = await response.json()
                last_reading = data.get('last')

                if last_reading is not None:
                    date_ = datetime.strptime(last_reading['date'], '%Y-%m-%d').date()
                    if date_ == current_date:
                        print("Даты равны, обновляем")
                        return await update_pokazaniya(session, last_reading['id'], type_ipu, value)
                    else:
                        print("Даты не равны, просто записываем")
                else:
                    print("Нет предыдущих, просто записываем")

                return await create_pokazaniya(session, ls, kv, type_ipu, value)

async def update_pokazaniya(session, id, type_ipu, value):
    url = f"{base_url}/api/pokazaniya/{id}/"
    headers = {
        'Authorization': os.getenv('API'),
        'Content-Type': 'application/json'
    }
    data = {
        'type_ipu': type_ipu,
        'value': value
    }
    
    async with session.put(url, headers=headers, json=data) as response:
        if response.status == 200:
            return await response.json()
        else:
            return await handle_error(response)

async def create_pokazaniya(session, ls, kv, type_ipu, value):
    url = f"{base_url}/api/pokazaniya/"
    headers = {
        'Authorization': os.getenv('API'),
        'Content-Type': 'application/json'
    }
    data = {
        'ls': ls,
        'kv': kv,
        'type_ipu': type_ipu,
        'value': value
    }

    async with session.post(url, headers=headers, json=data) as response:
        if response.status == 201:
            return await response.json()
        else:
            return await handle_error(response)

async def handle_error(response):
    """Обрабатывает ошибки и возвращает сообщение."""
    return {
        'error': f'Ошибка: {response.status}',
        'message': await response.text()  # Получаем текст ошибки
    }
#=======================================================
