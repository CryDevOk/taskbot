from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from data.database import *
from notion_client import Client
import dateparser
from openai import AsyncOpenAI
import datetime
from dateutil import tz
import os

router = Router()

client_GPT = AsyncOpenAI(api_key=os.getenv('GPT_API'))
notion = Client(auth=os.getenv('NOTION_API'))
NOTION_DATABASE_ID = os.getenv('NOTION_DB_ID')
time_zone = os.getenv('TIME_ZONE')
tz = tz.gettz(time_zone)


@router.message()
async def simple(message: Message, bot: Bot):
    text = message.text
    if text is not None:
        #проверка есть ли ссылка на гуго мит или зум в тексте
        if text[0] == '!' or 'meet.google.com' in text or 'zoom.us' in text or 'tel.meet' in text:
            if text[0] == '!':
                await message.delete()
                if len(text) < 2:
                    text = None
                else:
                    text = text[1:]

            comments = ''
            if text:
                comments += f'🌚 {text}'

            properties = {}
            if message.reply_to_message is not None:
                comments += f'\n🌝 {message.reply_to_message.html_text}'
                properties["Клиент"] = {"rich_text": [{"text": {"content": f'{message.reply_to_message.from_user.full_name} ({message.reply_to_message.from_user.id})'}}]}

            messages = [
                {
                    "role": "system",
                    "content": '''Твоя задача преобразовывать входящий текст в json формат. Нужно структурировать данные, чтобы их можно было легко использовать в дальнейшем.
                    🌝 - сообщения собеседника, 🌚 - мой комментарий к задаче
                    Если параметр не указан (пустой) НЕ НУЖНО ЕГО ДОБАВЛЯТЬ В JSON
                    Сейчас: 26.03.2024 04:19
                    
                    Доступные параметры: Задача, Дата (формат %d.%m.%Y %H:%M), Место, Сумма сделки, URL
                    ПАРАМЕТР ЗАДАЧА НЕ МОЖЕТ БЫТЬ ПУСТЫМ. Если в тексте только ссылка - значит вероятнее всего это созвон (ссылку помести в ссылку, а в задаче напиши "созвон")       
                    ""
                    '''
                },
                {
                    "role": "user",
                    "content": '🌝 Мне нужно пойти в магазин и купить молоко за 100 долларов, 🌚через день'}
                ,
                {
                    "role": "assistant",
                    "content": '''
                    {
                        "Задача": "Купить молоко",
                        "Дата": "27.03.2024 04:19",
                        "Место": "магазин"
                        "Сумма сделки": 100
                    }
                    '''
                },
                {
                    "role": "user",
                    "content": f'{comments}\n Сейчас: {datetime.datetime.now(tz).strftime("%d.%m.%Y %H:%M")}, если в задаче не было указано время, то по стандарту используй через 1 час'
                },
            ]

            chat_completion = await client_GPT.chat.completions.create(
                messages=messages,
                model="gpt-3.5-turbo-0125",
            )

            result = chat_completion.choices[0].message.content
            print(result)
            gpt_data = json.loads(result)


            if gpt_data.get('Дата') is not None:
                date = dateparser.parse(gpt_data.get('Дата'))
                if date is not None:
                    #с напоминанием за 30 минут до
                    properties["Дата"] = {"date": {"start": date.strftime('%Y-%m-%d %H:%M'), "time_zone": time_zone}}

            if gpt_data.get('Задача') is not None:
                properties["title"] = {"title": [{"text": {"content": gpt_data.get('Задача')}}]}

            if gpt_data.get('Место') is not None:
                properties["Место"] = {"rich_text": [{"text": {"content": gpt_data.get('Место')}}]}

            if gpt_data.get('Сумма сделки') is not None:
                properties["Сумма сделки"] = {"number": gpt_data.get('Сумма сделки')}

            if gpt_data.get('URL') is not None:
                properties["URL"] = {"url": gpt_data.get('URL')}

            if message.chat.title:
                properties["Чат"] = {"rich_text": [{"text": {"content": f'{message.chat.title}'}}]}

            properties["Автор"] = {"rich_text": [{"text": {"content": f'{message.from_user.full_name}'}}]}

            properties["Комментарий"] = {"rich_text": [{"text": {"content": comments}}]}

            page = notion.pages.create(
                parent={"database_id": NOTION_DATABASE_ID},
                properties=properties
            )
            reply_markup = InlineKeyboardBuilder()
            reply_markup.button(text='❌ Удалить', callback_data=f'del')
            if message.reply_to_message is not None:
                tetext = f'@{message.from_user.username} принял задачу от @{message.reply_to_message.from_user.username}'
                if text:
                    tetext += f', ответив:\n"<i>{text}</i>"'
            else:
                tetext = f'@{message.from_user.username} поставил задачу <b>{gpt_data.get("Задача")}</b>'
            if message.reply_to_message is not None:
                await message.answer(tetext, reply_to_message_id=message.reply_to_message.message_id)
            else:
                await message.answer(tetext)



@router.callback_query(F.data == 'del')
async def del_task(call: CallbackQuery):
    await call.message.delete()


