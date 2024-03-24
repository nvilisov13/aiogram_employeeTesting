import asyncio
import logging
from config_reader import config
from aiogram import Bot, Dispatcher
from handlers.users import start, about, help, on_start_testing
from keyboards.set_bot_commands import set_default_commands


async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher()
    dp.include_routers(start.router, about.router, help.router, on_start_testing.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    await set_default_commands(dp)


if __name__ == "__main__":
    asyncio.run(main())
