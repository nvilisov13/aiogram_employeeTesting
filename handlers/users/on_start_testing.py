from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
import requests
import json
import re
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.for_questions import NumbersCallbackFactory, get_inline_kb

router = Router()


@router.message(Command("onstart_test"))
async def cmd_start(message: Message):
    requests_test_info = requests.get("http://127.0.0.1:8000/drf_employees_test/")
    parsing_test_info = json.loads(requests_test_info.text)
    for key_test in parsing_test_info:
        dictionary_tests = {f"✅ {key_test['id']}. {key_test['NameTest']}": key_test['id']}
        await message.answer(
            f"<b><u>{key_test['DescriptionTest']}</u></b>",
            reply_markup=get_inline_kb(dictionary_tests, "showTests")
        )


@router.callback_query(NumbersCallbackFactory.filter(F.action == "showTests"))
async def callbacks_show_tests(callback: CallbackQuery):
    test_id = re.search(r"\d+", callback.data).group(0)
    requests_questions = requests.get(f'http://127.0.0.1:8000/drf_questions/{test_id}/questions_test/')
    parsing_questions = json.loads(requests_questions.text)
    for key_questions in parsing_questions:
        requests_answers = requests.get(f'http://127.0.0.1:8000/drf_questions/{key_questions}/question_answers/')
        parsing_answers = json.loads(requests_answers.text)
        keyboard = InlineKeyboardBuilder()
        dict_question_answers = {}
        for key_answers in parsing_answers:
            dict_question_answers[f"✅ {parsing_answers[key_answers][0]}"] = parsing_answers[key_answers][1]
            keyboard = get_inline_kb(dict_question_answers, "selectAnswer")
        await callback.message.answer(f"<b><i>{parsing_questions[key_questions][0]}</i></b>",
                                      reply_markup=keyboard)
    requests_questions_count = requests.get(f'http://127.0.0.1:8000/drf_questions/{test_id}/question_count/')
    parsing_questions_count = json.loads(requests_questions_count.text)
    await callback.message.answer(
        f"<i><u>Общее количество вопросов тесте - {parsing_questions_count['QuestionCount']}</u></i>")


@router.callback_query(NumbersCallbackFactory.filter(F.action == "selectAnswer"))
async def callbacks_selecta_answer(callback: CallbackQuery):
    list_def = callback.data.split(':')
    await callback.answer(f"➡ action = {list_def[1]} ||\n value = {list_def[2]}")
