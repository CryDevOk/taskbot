from aiogram import Bot
from aiogram.types import BotCommand


async def set_commands(bot: Bot):
    bot_commands = [
        BotCommand(command="start", description="начать заново"),
        BotCommand(command="hide", description="скрыть клавиатуру")
    ]
    await bot.set_my_commands(bot_commands)

