"""
Файл с клавиатурами
"""
from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.base import String

from keyboards.key_text import HISTORY_LIST, HISTORY_SHOW_LIST, RETURNS, KEY_RESULT, KEY_BACK, KEY_LOWPRICE, \
    KEY_HIGHPRICE, KEY_BESTDEAL, KEY_HISTORY, KEY_HELP
from settings import constants
from settings.constants import HISTORY, YES, NO


# start keyboard
def command_keyboard():
    command_keyboard = InlineKeyboardMarkup(row_width=2)
    lowprice = InlineKeyboardButton(text=KEY_LOWPRICE, callback_data=constants.LOWPRICE)
    highprice = InlineKeyboardButton(text=KEY_HIGHPRICE, callback_data=constants.HIGHPRICE)
    bestdeal = InlineKeyboardButton(text=KEY_BESTDEAL, callback_data=constants.BESTDEAL)
    history = InlineKeyboardButton(text=KEY_HISTORY, callback_data=constants.HISTORY)
    help = InlineKeyboardButton(text=KEY_HELP, callback_data=constants.HELP)
    command_keyboard.row(lowprice, highprice).add(bestdeal).row(history, help)
    return command_keyboard


def keyboard_w_num():
    keyboard_w_num = InlineKeyboardMarkup(row_width=5)
    key_list = [InlineKeyboardButton(text=str(i + 1), callback_data=str(i + 1)) for i in range(10)]
    keyboard_w_num.row(*key_list[:5])
    keyboard_w_num.row(*key_list[5:])
    keyboard_w_num.add(InlineKeyboardButton(KEY_BACK, callback_data=KEY_BACK))
    return keyboard_w_num


def yes_no_keyboard():
    yes_no_keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton('Да ✅', callback_data=YES),
        InlineKeyboardButton('Нет ❌', callback_data=NO)
    ]
    yes_no_keyboard.add(*buttons)
    yes_no_keyboard.add(InlineKeyboardButton(KEY_BACK, callback_data='Back'))
    return yes_no_keyboard


def city_markup(cities: List):
    destinations = InlineKeyboardMarkup()
    for city in cities:
        text = f'{city["city_name"].split(", ")[0]}, {city["city_name"].split(", ")[-1]}'
        destinations.add(InlineKeyboardButton(text=text, callback_data=f'{city["destination_id"]}'))
    destinations.add(InlineKeyboardButton(KEY_BACK, callback_data=KEY_BACK))
    return destinations


def history_keyboard(message: String):
    history_keyboard = InlineKeyboardMarkup()
    if message == HISTORY or message in RETURNS:
        keyboard_list = HISTORY_LIST
    else:
        keyboard_list = HISTORY_SHOW_LIST
    for element in keyboard_list:
        history_keyboard.add(InlineKeyboardButton(text=element, callback_data=element))
    history_keyboard.add(InlineKeyboardButton(KEY_BACK, callback_data='Back'))
    return history_keyboard


def back_keyboard():
    back_keyboard = InlineKeyboardMarkup()
    back_keyboard.add(InlineKeyboardButton(text=KEY_BACK, callback_data=KEY_BACK))
    return back_keyboard


async def paginate_keyboard(num_page: int, end: int, state, id, start=1) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=3)
    if start == end:
        return keyboard.add(InlineKeyboardButton(KEY_RESULT, callback_data=f"{KEY_RESULT}&{id}")).add(
            InlineKeyboardButton(KEY_BACK, callback_data=KEY_BACK))
    elif num_page == start:
        left = end
        right = num_page + 1
    elif num_page == end:
        left = num_page - 1
        right = start
    else:
        left = num_page - 1
        right = num_page + 1
    keyboard.add(
        InlineKeyboardButton(text='⬅️', callback_data=f'paginate&{left}'),
        InlineKeyboardButton(text=f'{num_page}/{end}', callback_data=f'pass'),
        InlineKeyboardButton(text='➡️', callback_data=f'paginate&{right}'),
    )
    if await state.get_state() in ['FSMHistory:full_history', 'FSMHistory:last_5']:
        keyboard.add(InlineKeyboardButton(KEY_RESULT, callback_data=f"{KEY_RESULT}&{id}"))
    return keyboard.add(InlineKeyboardButton(KEY_BACK, callback_data=KEY_BACK))
