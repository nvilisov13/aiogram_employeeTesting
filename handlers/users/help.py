from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("help"))
async def bot_help(message: Message):
    text = ("Список команд: ",
            "/start - Начать диалог",
            "/help - Получить справку",
            "/about - Получить анатацию к проекту",
            "/onstart_test - Начать проходить тест для сотрудников",)
    await message.answer("\n".join(text))
