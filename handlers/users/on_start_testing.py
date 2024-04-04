from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
import requests
import json
from keyboards.for_questions import get_inline_kb

router = Router()


@router.message(Command("onstart_test"))
async def cmd_start(message: Message):
    # print(message.model_dump_json(indent=4, exclude_none=True))
    print(message.from_user.id)
    requests_test_info = requests.get("http://127.0.0.1:8000/drf_employees_test/")
    parsing_test_info = json.loads(requests_test_info.text)
    for key_test in parsing_test_info:
        dictionary_tests = {f"📝 {key_test['id']}. {key_test['NameTest']}": key_test['id']}
        await message.answer(
            f"<b><u>{key_test['DescriptionTest']}</u></b>",
            reply_markup=get_inline_kb(dictionary_tests, "showTests")
        )
