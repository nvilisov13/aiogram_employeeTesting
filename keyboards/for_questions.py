from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Optional
from aiogram.filters.callback_data import CallbackData


class NumbersCallbackFactory(CallbackData, prefix="fabNum"):
    action: str
    mark: Optional[int] = None
    number: int


def get_inline_kb(button_dict: dict, action_str: str):
    builder = InlineKeyboardBuilder()
    number = 0
    for key, value in button_dict.items():
        builder.button(text=key, callback_data=NumbersCallbackFactory(action=action_str, mark=value, number=number))
        number += 1
    if action_str == "selectAnswer":
        builder.button(text=f"✔ Подтвердить ответ", callback_data=NumbersCallbackFactory(action="confirmAnswers",
                                                                                         number=number))
    builder.adjust(1)
    return builder.as_markup()
