from aiogram import Router, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import CallbackQuery
import requests
import json
import re
from keyboards.for_questions import get_inline_kb, NumbersCallbackFactory
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

router = Router()


class SurveyState(StatesGroup):
    WAITING_FOR_ANSWER = State()


async def out_question_answers(callback: CallbackQuery, state: FSMContext):
    list_question = await state.get_data()
    if len(list_question) != 0:
        key_questions = next(iter(list_question.keys()))
        requests_answers = requests.get(f'http://127.0.0.1:8000/drf_questions/{key_questions}/question_answers/')
        parsing_answers = json.loads(requests_answers.text)
        keyboard = InlineKeyboardBuilder()
        dict_question_answers = {}
        for key_answers in parsing_answers:
            dict_question_answers[f"✅ {parsing_answers[key_answers][0]}"] = parsing_answers[key_answers][1]
            keyboard = get_inline_kb(dict_question_answers, "selectAnswer")
        await callback.message.answer(f"<b><i>{list_question[key_questions][0]}</i></b>",
                                      reply_markup=keyboard)
        del list_question[key_questions]
        await state.set_data({})
        await state.update_data(list_question)
    else:
        await callback.message.answer("<b><i>✔ Тест завершен!!!</i></b>")


async def out_count_questions(test_id: str, callback: CallbackQuery):
    requests_questions_count = requests.get(f'http://127.0.0.1:8000/drf_questions/{test_id}/question_count/')
    parsing_questions_count = json.loads(requests_questions_count.text)
    await callback.message.answer(
        f"<i><u>Общее количество вопросов тесте - {parsing_questions_count['QuestionCount']}</u></i>")


@router.callback_query(NumbersCallbackFactory.filter(F.action == "showTests"))
async def callbacks_show_tests(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    test_id = re.search(r"\d+", callback.data).group(0)
    requests_questions = requests.get(f'http://127.0.0.1:8000/drf_questions/{test_id}/questions_test/')
    parsing_questions = json.loads(requests_questions.text)
    await state.clear()
    await state.set_data(parsing_questions)
    await out_count_questions(test_id, callback)
    await out_question_answers(callback, state)


@router.callback_query(NumbersCallbackFactory.filter(F.action == "selectAnswer"))
async def callbacks_selecta_answer(callback: CallbackQuery, state: FSMContext):
    list_def = callback.data.split(':')
    await callback.answer(f"➡ action = {list_def[1]} ||\n value = {list_def[2]}")
    await out_question_answers(callback, state)
