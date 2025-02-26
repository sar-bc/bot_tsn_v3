from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='start',
            description='Запустить бота / вернуться в начало'
        ),
        # BotCommand(
        #     command='record',
        #     description='Просмотр своих записей'
        # ),
        # BotCommand(
        #     command='info',
        #     description='Информация'
        # )
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())