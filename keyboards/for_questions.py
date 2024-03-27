from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Optional
from aiogram.filters.callback_data import CallbackData


class NumbersCallbackFactory(CallbackData, prefix='fabNum'):
    action: str
    value: Optional[int] = None


def get_inline_kb(button_dict: dict, action_str: str):
    builder = InlineKeyboardBuilder()
    for key, value in button_dict.items():
        builder.button(text=key, callback_data=NumbersCallbackFactory(action=action_str, value=value))
    builder.adjust(1)
    return builder.as_markup()
