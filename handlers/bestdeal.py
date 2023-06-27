"""
Файл с командой /bestdeal
"""

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types.base import String

from database.models import DeleteMessage
from database.states import FSMRequestData
from handlers.echo import delete_message
from keyboards import yes_no_keyboard
from loader import bot, exception_handler_decorator
from settings import constants
from settings.constants import mile_to_km


# Проверка на число
def is_number(str: String):
    try:
        float(str)
        return True
    except ValueError:
        return False


@exception_handler_decorator
# @exception_state_decorator
async def get_min_price(message: types.Message, state: FSMContext):
    await delete_message(message.from_user.id)
    async with state.proxy() as data:
        if message.text.isdigit():
            data['min_price'] = message.text
            await message.delete()
            await FSMRequestData.max_price.set()
            bot_message = await bot.send_message(message.from_user.id, constants.MAX_PRICE)
            DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()
        else:
            await message.delete()
            await bot.send_message(message.from_user.id, constants.INCORRECT_PRICE)
            bot_message = await bot.send_message(message.from_user.id, constants.MIN_PRICE)
            DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()


@exception_handler_decorator
# @exception_state_decorator
async def get_max_price(message: types.Message, state: FSMContext):
    await delete_message(message.from_user.id)
    async with state.proxy() as data:
        if message.text.isdigit():
            if int(message.text) > int(data['min_price']):
                data['max_price'] = message.text
                await message.delete()
                await FSMRequestData.min_distance.set()
                bot_message = await bot.send_message(message.from_user.id, constants.MIN_DISTANCE)
                DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()
            else:
                await message.delete()
                # await bot.delete_message(message.from_user.id, message_id=int(data['message']))
                await bot.send_message(message.from_user.id, constants.INCORRECT_VALUE_PRICE)
                bot_message = await bot.send_message(message.from_user.id, constants.MAX_PRICE)
                DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()
        else:
            await message.delete()
            # await bot.delete_message(message.from_user.id, message_id=int(data['message']))
            await bot.send_message(message.from_user.id, constants.INCORRECT_PRICE)
            bot_message = await bot.send_message(message.from_user.id, constants.MAX_PRICE)
            DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()


@exception_handler_decorator
# @exception_state_decorator
async def get_min_distance(message: types.Message, state: FSMContext):
    await delete_message(message.from_user.id)
    async with state.proxy() as data:
        if is_number(message.text.replace(',', '.')):
            data['min_distance'] = message.text.replace(',', '.')
            await message.delete()
            await FSMRequestData.max_distance.set()
            bot_message = await bot.send_message(message.from_user.id, constants.MAX_DISTANCE)
            DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()
        else:
            await message.delete()
            await bot.send_message(message.from_user.id, constants.INCORRECT_DISTANCE)
            bot_message = await bot.send_message(message.from_user.id, constants.MIN_DISTANCE)
            DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()


@exception_handler_decorator
# @exception_state_decorator
async def get_max_distance(message: types.Message, state: FSMContext):
    await delete_message(message.from_user.id)
    async with state.proxy() as data:
        distance = message.text.replace(',', '.')
        if is_number(distance):
            if float(distance) > float(data['min_distance']):
                data['max_distance'] = message.text.replace(',', '.')
                await message.delete()
                await FSMRequestData.need_photo.set()
                bot_message = await bot.send_message(message.from_user.id, constants.NEED_PHOTO, reply_markup=yes_no_keyboard())
                DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()
            else:
                await message.delete()
                await bot.send_message(message.from_user.id, constants.INCORRECT_VALUE_DISTANCE)
                bot_message = await bot.send_message(message.from_user.id, constants.MAX_DISTANCE)
                DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()
        else:
            await message.delete()
            await bot.send_message(message.from_user.id, constants.INCORRECT_DISTANCE)
            bot_message = await bot.send_message(message.from_user.id, constants.MAX_DISTANCE)
            DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()


@exception_handler_decorator
# @exception_state_decorator
async def check_bestdeal(hotel_response, state):
    result_hotels = []
    async with state.proxy() as data:
        for hotel in hotel_response:
            distance = mile_to_km(hotel['destinationInfo']['distanceFromDestination']['value'])
            price = int(hotel['price']['lead']['formatted'][1:].replace(',', ''))
            if float(data['min_distance']) <= distance <= float(data['max_distance']) and float(data['min_price']) <= price <= float(data['max_price']):
                result_hotels.append(hotel)
    if not result_hotels:
        return False
    else:
        return result_hotels


def register_bestdeal_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(get_min_price, state=FSMRequestData.min_price)
    dp.register_message_handler(get_max_price, state=FSMRequestData.max_price)

    dp.register_message_handler(get_min_distance, state=FSMRequestData.min_distance)
    dp.register_message_handler(get_max_distance, state=FSMRequestData.max_distance)
