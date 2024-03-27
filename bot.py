import asyncio
import sys
import logging
from config_reader import config
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from handlers.users import start, about, help, on_start_testing
from utility import parse_test
from keyboards.set_bot_commands import set_main_menu


async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
                        stream=sys.stdout)
    bot = Bot(token=config.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()
    dp.include_routers(start.router, about.router, help.router, on_start_testing.router, parse_test.router)
    dp.startup.register(set_main_menu)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен!")
