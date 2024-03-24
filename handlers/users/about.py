from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("about"))
async def about(message: Message):
    await message.answer("Бот для отправки тестов в Telegram для тестирования сотрудников подготовка и создание "
                         "необходимых тестов осуществляется в проекте на Django")
