from aiogram.types.bot_command import BotCommand


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            BotCommand(command="start", description="Запустить бота"),
            BotCommand(command="help", description="Вывести справку"),
            BotCommand(command="onstart_test", description="Пройти тест сотрудника"),
        ]
    )
