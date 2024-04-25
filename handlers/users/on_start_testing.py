from aiogram import Router, F
from aiogram.types import CallbackQuery, URLInputFile
from utility.loadconfpars import pars_drf, convert_date_time, convert_date_time_out_message
import json
import re
from keyboards.for_questions import get_inline_kb, NumbersCallbackFactory
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

router = Router()


class SurveyState(StatesGroup):
    ForNextQuestion = State()
    CountRightAnswer = State()
    CommonMark = State()
    MaxMark = State()
    Nom_id = State()


URL_LINK = "http://127.0.0.1:8000/drf_nominated_tests/"
EMPTY_WRITES = ['', None]


async def show_nominated_tests(callback: CallbackQuery, user_id):
    requests_nom_tests = pars_drf.get_data_db(f"http://127.0.0.1:8000/drf_employees/{user_id}/nom_tests/")
    parsing_nom_tests = json.loads(requests_nom_tests)
    if len(parsing_nom_tests) > 0:
        for value in parsing_nom_tests.values():
            if value['MarksTest'] in EMPTY_WRITES:
                await launch_employee_test(callback, value['Test_id'], value['id'])
            else:
                requests_test_info = pars_drf.get_data_db(
                    f"http://127.0.0.1:8000/drf_employees_test/{value['Test_id']}/")
                test_info = json.loads(requests_test_info)
                await callback.answer(f"<b><u>Тест пройден:</u></b>\n"
                                      f"с - <i>{convert_date_time_out_message(value['SinceDateTime'])}</i>\nпо - "
                                      f"<i>{convert_date_time_out_message(value['DuringDateTime'])}</i>\nна: "
                                      f"{value['MarksTest']} баллов.\n<b><i>Название теста:</i></b>\n"
                                      f"{test_info['NameTest']}\nОписание теста:\n<b>"
                                      f"{test_info['DescriptionTest']}</b>")
    else:
        await callback.answer(
            text="<b>ℹ️️ У вас нет назначенных тестов! ℹ️</b>",
            show_alert=True
        )


async def launch_employee_test(callback: CallbackQuery, test_id, id_nom):
    requests_test_info = pars_drf.get_data_db(f"http://127.0.0.1:8000/drf_employees_test/{test_id}/")
    test_info = json.loads(requests_test_info)
    dictionary_tests = {f"📝 {test_info['id']}. {test_info['NameTest']}": id_nom}
    await callback.answer(
        f"<b><u>{test_info['DescriptionTest']}</u></b>",
        reply_markup=get_inline_kb(dictionary_tests, "showTests")
    )


@router.message(Command("onstart_test"))
async def cmd_start(callback: CallbackQuery):
    # print(callback.model_dump_json(indent=4, exclude_none=True))
    url_employees = "http://127.0.0.1:8000/drf_employees/"
    requests_employees = pars_drf.get_data_db(url_employees)
    parsing_employees = json.loads(requests_employees)
    user_tg_id = str(callback.from_user.id)
    user = False
    user_db_id = ''
    for key_employees in parsing_employees:
        user_db_id = str(key_employees['id'])
        if ((key_employees['FirstName'] == callback.from_user.first_name and
             key_employees['LastName'] == callback.from_user.last_name) and
                (key_employees['TelegramID'] in EMPTY_WRITES)):
            pars_drf.write_data_db(url_employees + user_db_id + "/", {"TelegramID": user_tg_id})
            user = True
        elif key_employees['TelegramID'] == user_tg_id:
            user = True
            break
    if user:
        await show_nominated_tests(callback, user_db_id)
    else:
        await callback.answer(
            text="<b>⚠️ Вы не зарегистрированы на прохождение тестов! ⚠️</b>",
            show_alert=True
        )


async def out_question_answers(callback: CallbackQuery, state: FSMContext):
    data_dict = await state.get_data()
    list_question = data_dict.get('ForNextQuestion')
    if len(list_question) > 0:
        key_questions = next(iter(list_question.keys()))
        requests_answers = pars_drf.get_data_db(
            f'http://127.0.0.1:8000/drf_questions/{key_questions}/question_answers/')
        parsing_answers = json.loads(requests_answers)
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
        if list_question[key_questions][1] is not None:
            image_question = URLInputFile(f"http://127.0.0.1:8000{list_question[key_questions][1]}")
            await callback.message.answer_photo(image_question)
        await callback.message.answer(f"<b><i>{list_question[key_questions][0]}</i></b>",
                                      reply_markup=keyboard)
        del list_question[key_questions]
        await state.update_data(ForNextQuestion=list_question, CountRightAnswer=count_right_answer)
    else:
        data_dict = await state.get_data()
        data = {
            "MarksTest": data_dict.get('CommonMark'),
            "DuringDateTime": convert_date_time(callback.message.date.timestamp()),
        }
        nom_id = data_dict.get('Nom_id')
        pars_drf.write_data_db(URL_LINK + nom_id + "/", data)
        text_message = (f"<b>✔ Тест завершен!!! Общая оценка: <i>{data_dict.get('CommonMark')} из "
                        f"{data_dict.get('MaxMark')} максимально возможных баллов</i></b>")
        await callback.message.answer(text_message)
        await state.clear()


async def out_count_questions(test_id: str, callback: CallbackQuery):
    requests_questions_count = pars_drf.get_data_db(f'http://127.0.0.1:8000/drf_questions/{test_id}/question_count/')
    parsing_questions_count = json.loads(requests_questions_count)
    await callback.message.answer(
        f"<i><u>Общее количество вопросов тесте - {parsing_questions_count['QuestionCount']}</u></i>")


@router.callback_query(NumbersCallbackFactory.filter(F.action == "showTests"))
async def callbacks_show_tests(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    nom_id = re.findall(r"\d+", callback.data)[0]
    number = int(re.findall(r"\d+", callback.data)[1])
    test_id = re.search(r"\d+", callback.message.reply_markup.inline_keyboard[number][0].text).group(0)
    requests_questions = pars_drf.get_data_db(f'http://127.0.0.1:8000/drf_questions/{test_id}/questions_test/')
    parsing_questions = json.loads(requests_questions)
    await state.update_data(Nom_id=nom_id, ForNextQuestion=parsing_questions, CommonMark=0, MaxMark=0)
    await out_count_questions(test_id, callback)
    await out_question_answers(callback, state)
    data = {
        "MarksTest": None,
        "SinceDateTime": convert_date_time(callback.message.date.timestamp()),
        "DuringDateTime": None,
    }
    pars_drf.write_data_db(URL_LINK + nom_id + "/", data)


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
