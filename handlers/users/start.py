from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def bot_start(message: Message):
    await message.answer(f"Здравствуйте, {message.from_user.full_name}!\nЭто бот был создан для тестирования "
                         f"сотрудников.\nНапишите комманду /help чтобы получить подробную информацию о возможностях"
                         f" бота")
