import asyncio
from aiogram import Bot, Dispatcher
from h import start, command
import os

TOKEN = os.getenv('TGBOT_API')
bot = Bot(TOKEN, parse_mode='HTML')
dp = Dispatcher()

async def main():
    #await command.set_commands(bot)
    dp.include_routers(start.router)
    await dp.start_polling(bot, close_bot_session=True, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        print('Запуск')
        asyncio.run(main())
    except (SystemExit, KeyboardInterrupt):
        print('Ошибка')