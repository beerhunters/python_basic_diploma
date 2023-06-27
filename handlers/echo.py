"""
Файл - содержит хэндлер для отлова сообщений вне сценария
"""

from aiogram import Dispatcher, types
from database.models import DeleteMessage
from keyboards import command_keyboard
from loader import bot, exception_handler_decorator
from settings import constants


@exception_handler_decorator
async def echo_handler(message: types.Message) -> None:
    """
    Хэндлер - оповещает бота о некорректной команде (Эхо)
    :param message: Message
    :return: None
    """
    await delete_message(message.from_user.id)
    bot_message = await message.answer(constants.INCORRECT_INPUT, reply_markup=command_keyboard())
    DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()
    await message.delete()


@exception_handler_decorator
# async def delete_message(user_id: int) -> None:
#     """
#     Функция - обрабатывает удаление сообщений
#     :param user_id: int
#     :return: None
#     """
#     message = DeleteMessage.select().where(DeleteMessage.chat_id == user_id)
#     if len(message):
#         for mess in message:
#             mes_ids = mess.message_id.split('&') if '&' in mess.message_id else [mess.message_id]
#             for elem in mes_ids:
#                 await bot.delete_message(chat_id=mess.chat_id, message_id=int(elem))
#             mess.delete_instance()
async def delete_message(user_id: int) -> None:
    """
    Функция - обрабатывает удаление сообщений
    :param user_id: int
    :return: None
    """
    try:
        message = DeleteMessage.select().where(DeleteMessage.chat_id == user_id)
        if len(message):
            for mess in message:
                mes_ids = mess.message_id.split('&') if '&' in mess.message_id else [mess.message_id]
                for elem in mes_ids:
                    try:
                        await bot.delete_message(chat_id=mess.chat_id, message_id=int(elem))
                    except Exception:
                        pass
                try:
                    mess.delete_instance()
                except Exception:
                    pass
    except Exception:
        pass
# async def delete_message(user_id: int) -> None:
#     """
#     Функция - обрабатывает удаление сообщений
#     :param user_id: int
#     :return: None
#     """
#     try:
#         message = DeleteMessage.select().where(DeleteMessage.chat_id == user_id)
#         if len(message):
#             for mess in message:
#                 if '&' in mess.message_id:
#                     mes_ids = mess.message_id.split('&')
#                     for elem in mes_ids:
#                         try:
#                             await bot.delete_message(chat_id=mess.chat_id, message_id=int(elem))
#                         except Exception:
#                             pass
#                 else:
#                     try:
#                         await bot.delete_message(chat_id=mess.chat_id, message_id=int(mess.message_id))
#                     except Exception:
#                         pass
#                 try:
#                     mess.delete_instance()
#                 except Exception:
#                     pass
#     except Exception as error:
#         print('В работе бота возникло исключение', error)
# async def delete_message(user_id: int) -> None:
#     """
#     Функция - обрабатывает удаление сообщений
#     :param user_id: int
#     :return: None
#     """
#     try:
#         message = DeleteMessage.get(DeleteMessage.chat_id == user_id)
#         if '&' in message.message_id:
#             mes_ids = message.message_id.split('&')
#             for elem in mes_ids:
#                 try:
#                     await bot.delete_message(chat_id=message.chat_id, message_id=int(elem))
#                 except Exception:
#                     pass
#         else:
#             try:
#                 await bot.delete_message(chat_id=message.chat_id, message_id=int(message.message_id))
#             except Exception:
#                 pass
#         message.delete_instance()
#     except DeleteMessage.DoesNotExist:
#         pass
#     except Exception as error:
#         print('В работе бота возникло исключение', error)



def register_echo_handlers(dp: Dispatcher) -> None:
    """
    Функция - регистрирует все хэндлеры файла echo.py
    :param dp: Dispatcher
    :return: None
    """
    dp.register_message_handler(echo_handler, state="*")
