import sqlite3
import json
import time
from datetime import datetime
from aiogram.types import Message


base = sqlite3.connect('data/db.db', check_same_thread=False)
cursor = base.cursor()


def data_from_(message: Message):
    data = {
        'user_id': message.from_user.id,
        'full_name': message.from_user.full_name,
        'username': message.from_user.username,
        'first_name': message.from_user.first_name,
        'last_name': message.from_user.last_name,
        'is_premium': message.from_user.is_premium,
        'language_code': message.from_user.language_code
    }
    return data


def timestamp_to_date(timestamp):
    try:
        # Преобразуем таймштамп в объект datetime
        dt_object = datetime.fromtimestamp(timestamp)
        # Форматируем дату в нужный формат
        formatted_date = dt_object.strftime("%d.%m.%Y")
        return formatted_date
    except Exception as e:
        print("Ошибка при преобразовании таймштампа:", e)
        return None


def update_users(data):
    data['key'] = data['user_id']
    return update_('users', data)


def update_(table, data):
    """
        Добавляет запись в БД если ранее ключ-значение не существовал и обновляет если это новое
    """
    key = data.get('key', 'default')
    old_data = select_(table, key)
    if old_data is None:
        record_1st = int(datetime.now().timestamp())
        data.update({'record_1st': record_1st})
        cursor.execute(f'INSERT INTO {table} VALUES(?, ?)', (key, json.dumps(data, ensure_ascii=False)))
        base.commit()
        return "INSERT"
    else:
        try:
            data.pop('ref')  # чтобы не перезаписывать того, кто привёл человека в бота
        except KeyError:
            pass
        old_data.update(data)
        cursor.execute(f'UPDATE {table} SET data=? WHERE key=?', (json.dumps(old_data, ensure_ascii=False), key))
        base.commit()
        return "UPDATE"

def select_users(key):
    return select_('users', key)

def select_(table, key):
    res = None

    if type(key) is dict:
        for row in select_all_in(table):
            data = json.loads(row[1])
            if all(item in data.items() for item in key.items()):
                res = data
    else:
        res = cursor.execute(f'SELECT data FROM {table} WHERE key=?', (key,)).fetchone()
        if res is not None:
            res = json.loads(res[0])

    return res

def select_all_in(table):
    res = cursor.execute(f'SELECT * FROM {table}').fetchall()
    return res