from aiogram import Router, F
from aiogram.types import CallbackQuery
import requests
import json
import re
from keyboards.for_questions import get_inline_kb, NumbersCallbackFactory
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

router = Router()


class SurveyState(StatesGroup):
    ForNextQuestion = State()
    CountRightAnswer = State()
    CommonMark = State()
    MaxMark = State()


async def out_question_answers(callback: CallbackQuery, state: FSMContext):
    data_dict = await state.get_data()
    list_question = data_dict.get('ForNextQuestion')
    if len(list_question) > 0:
        key_questions = next(iter(list_question.keys()))
        requests_answers = requests.get(f'http://127.0.0.1:8000/drf_questions/{key_questions}/question_answers/')
        parsing_answers = json.loads(requests_answers.text)
        dict_question_answers = {}
        count_right_answer = len([int(parsing_answers[key_answers][1]) for key_answers in parsing_answers
                                  if int(parsing_answers[key_answers][1]) > 0])
        if count_right_answer > 1:
            prefix_char = '☑'
        else:
            prefix_char = '🔵'
        for key_answers in parsing_answers:
            dict_question_answers[f"{prefix_char} {parsing_answers[key_answers][0]}"] = parsing_answers[key_answers][1]
        keyboard = get_inline_kb(dict_question_answers, "selectAnswer")
        await callback.message.answer(f"<b><i>{list_question[key_questions][0]}</i></b>",
                                      reply_markup=keyboard)
        del list_question[key_questions]
        await state.update_data(ForNextQuestion=list_question, CountRightAnswer=count_right_answer)
    else:
        text_message = (f"<b>✔ Тест завершен!!! Общая оценка: <i>{data_dict.get('CommonMark')} из "
                        f"{data_dict.get('MaxMark')} максимально возможных баллов</i></b>")
        await callback.message.answer(text_message)
        await state.clear()


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
    await state.set_data({})
    await state.update_data(ForNextQuestion=parsing_questions, CommonMark=0, MaxMark=0)
    await out_count_questions(test_id, callback)
    await out_question_answers(callback, state)


@router.callback_query(NumbersCallbackFactory.filter(F.action == "selectAnswer"))
async def callbacks_selecta_answer(callback: CallbackQuery, state: FSMContext):
    number = re.search(r"\d+$", callback.data).group(0)
    data_dict = await state.get_data()
    text_message = callback.message.text
    keyboard = callback.message.reply_markup.inline_keyboard
    keyboard_dict = {}
    count_right_answer = data_dict.get('CountRightAnswer')
    if count_right_answer < 2:
        for key in keyboard[:-1]:
            button_list = re.findall(r"\d+", key[0].callback_data)
            button_text = key[0].text
            if button_list[1] == number:
                symbol_sel = '🟢'
            else:
                symbol_sel = '🔵'
            button_text = symbol_sel + button_text[1:]
            keyboard_dict[button_text] = int(button_list[0])
    else:
        for key in keyboard[:-1]:
            button_list = re.findall(r"\d+", key[0].callback_data)
            button_text = key[0].text
            if button_list[1] == number and button_text[:1] == '☑':
                button_text = '✅' + button_text[1:]
                keyboard_dict[button_text] = int(button_list[0])
            elif button_list[1] == number and button_text[:1] == '✅':
                button_text = '☑' + button_text[1:]
                keyboard_dict[button_text] = int(button_list[0])
            else:
                keyboard_dict[button_text] = int(button_list[0])
    keyboard_sel = get_inline_kb(keyboard_dict, "selectAnswer")
    await callback.message.edit_text(f"<b><i>{text_message}</i></b>", reply_markup=keyboard_sel)


@router.callback_query(NumbersCallbackFactory.filter(F.action == "confirmAnswers"))
async def callbacks_confirm_answers(callback: CallbackQuery, state: FSMContext):
    keyboard = callback.message.reply_markup.inline_keyboard
    text_answer = ""
    for key in keyboard[:-1]:
        button_text = key[0].text
        data_dict = await state.get_data()
        mark = int(re.search(r"\d+(?=:*:\d+$)", key[0].callback_data).group(0))
        if mark > 0:
            max_mark = data_dict.get('MaxMark') + mark
            await state.update_data(MaxMark=max_mark)
        if button_text[:1] == '✅' or button_text[:1] == '🟢':
            common_mark = data_dict.get('CommonMark') + mark
            await state.update_data(CommonMark=common_mark)
            if mark < 1:
                text_answer += f"<s>❌{button_text[1:]}</s>\n"
            else:
                text_answer += f"{button_text}\n"
    text_answer = text_answer.rstrip("\n")
    text_message = f"<b><i>{callback.message.text}</i></b>\n\n<u><i>Вы ответили:</i></u>\n<b>{text_answer}</b>"
    await callback.message.edit_text(text_message)
    await out_question_answers(callback, state)
