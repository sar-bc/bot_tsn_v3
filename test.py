import aiohttp
from dotenv import load_dotenv
import os
from datetime import datetime, date


load_dotenv()

# base_url = 'http://127.0.0.1:8000'
# base_url = 'https://tsnzv.ru'
base_url = os.getenv('BASE_URL')


async def update_pokazanie(pk, type_ipu, value):
    base_url = "http://127.0.0.1:8000"  # Замените на ваш базовый URL
    url = f"{base_url}/api/pokazaniya/{pk}/"  # URL для PUT-запроса
    headers = {
        'Authorization': os.getenv('API'),  # Получайте токен из переменных окружения
        'Content-Type': 'application/json'
    }
    data = {
        'type_ipu': type_ipu,
        'value': value
    }

    async with aiohttp.ClientSession() as session:
        async with session.put(url, headers=headers, json=data) as response:
            if response.status == 200:  # Успешное обновление
                response_data = await response.json()
                return response_data
            else:
                return {'error': f'Ошибка: {response.status}', 'message': await response.text()}

async def add_or_update_pokazaniya1(ls, kv, type_ipu, value):
        # Получаем текущую дату
        current_date = date.today()

        url = f"{base_url}/api/pokazaniya/"
        headers = {
            'Authorization': os.getenv('API')
        }
        params = {'ls': ls, 'kv': kv, 'flag': 'last'}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200: 
                    data = await response.json()
                    if data['last'] is not None:
                        date_ = datetime.strptime(data['last']['date'], '%Y-%m-%d').date()
                        if date_ == current_date:
                            print("даты равны обновляем")
                            url = f"{base_url}/api/pokazaniya/{data['last']['id']}/"
                            headers = {
                                'Authorization': os.getenv('API'),  # Получайте токен из переменных окружения
                                'Content-Type': 'application/json'
                            }
                            data = {
                                'type_ipu': type_ipu,
                                'value': value
                            }
                            async with aiohttp.ClientSession() as session:
                                async with session.put(url, headers=headers, json=data) as response:
                                    if response.status == 200:  # Успешное обновление
                                        response_data = await response.json()
                                        return response_data
                                    else:
                                        return {'error': f'Ошибка: {response.status}', 'message': await response.text()}
                        else:
                            print("даты не равны просто записываем")
                            url = f"{base_url}/api/pokazaniya/"
                            headers = {
                                'Authorization': os.getenv('API'),  # Получаем токен из переменных окружения
                                'Content-Type': 'application/json'
                            }
                            data = {
                                'ls': ls,
                                'kv': kv,
                                'type_ipu': type_ipu,
                                'value': value
                            }
                            async with aiohttp.ClientSession() as session:
                                async with session.post(url, headers=headers, json=data) as response:
                                    if response.status == 201:
                                        response_data = await response.json()
                                        return response_data
                                    else:
                                        return {'error': f'Ошибка: {response.status}', 'message': await response.text()}   
                    else:
                        print("нет предыдущих просто записываем")
                        url = f"{base_url}/api/pokazaniya/"
                        headers = {
                            'Authorization': os.getenv('API'),  # Получаем токен из переменных окружения
                            'Content-Type': 'application/json'
                        }
                        data = {
                            'ls': ls,
                            'kv': kv,
                            'type_ipu': type_ipu,
                            'value': value
                        }
                        async with aiohttp.ClientSession() as session:
                            async with session.post(url, headers=headers, json=data) as response:
                                if response.status == 201:
                                    response_data = await response.json()
                                    return response_data
                                else:
                                    return {'error': f'Ошибка: {response.status}', 'message': await response.text()}         

                else:
                   # нет ответа от сервкера ошибка
                   return {'error': f'Ошибка: {response.status}', 'message': await response.text()}
###########################################################

async def add_or_update_pokazaniya(ls, kv, type_ipu, value):
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


async def get_users_bot():
        """
        Все активные пользователи бота
        """
        url = f"{base_url}/api/get_userbots/"
        headers = {
            'Authorization': os.getenv('API')
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        return {'error': f'Ошибка: {response.status}'}
        except aiohttp.ClientError as e:
            return {'error': f'Ошибка соединения: {str(e)}'}
        except Exception as e:
            return {'error': f'Произошла ошибка: {str(e)}'}
###########################################################
# Пример вызова
async def main():
    # pk_value = 1  # Замените на нужный pk
    # type_ipu_value = 'hv'  # Пример значения для type_ipu
    # value_to_update = '700'  # Пример нового значения
    # result = await update_pokazanie(pk_value, type_ipu_value, value_to_update)
    # ls = '40706002'
    # kv = '60'
    # type_ipu = 'e'
    # value = '11000'
    # result = await add_or_update_pokazaniya(ls,kv,type_ipu,value)
    # print(result)
    # current_date = date.today()
    # cur_dat = current_date.strftime("%Y-%m-%d")
    # print(type(cur_dat))
    res = await get_users_bot()
    print(res)

# Запуск
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
