"""
Файл с хэндлерами старт/хэлп и регистрация
"""
from typing import Union
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from database.models import DeleteMessage
from handlers.echo import delete_message
from keyboards.key_text import KEY_BACK
from keyboards.keyboards import command_keyboard, back_keyboard
from loader import bot
from settings import constants


async def start_command(message: Union[types.Message, types.CallbackQuery], state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает команду /start
    :param state:
    :param message: Message
    :return: None
    """
    await delete_message(message.from_user.id)
    if await state.get_state():
        await state.finish()
    if isinstance(message, types.Message):
        await message.delete()
    else:
        pass
    bot_message = await bot.send_message(message.from_user.id, constants.START_COMMAND, reply_markup=command_keyboard())
    DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()


async def help_command(message: Union[types.Message, types.CallbackQuery], state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает команду /help
    :param state:
    :param message: Message
    :return: None
    """
    await delete_message(message.from_user.id)
    if await state.get_state():
        await state.finish()
    if isinstance(message, types.Message):
        await message.delete()
    else:
        pass
    bot_message = await bot.send_message(message.from_user.id, constants.HELP_COMMAND, reply_markup=back_keyboard())
    DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()


def register_start_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(start_command, commands=['start'], state=None)
    dp.register_message_handler(start_command, Text(equals='Старт', ignore_case=True), state=None)
    dp.register_message_handler(help_command, commands=['help'], state=None)
    dp.register_callback_query_handler(help_command, Text(constants.HELP), state=None)
    dp.register_callback_query_handler(start_command, Text(KEY_BACK), state=None)
