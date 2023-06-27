"""
Файл с командами /lowprice и /highprice
"""
import datetime
from typing import Union
import requests
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InputMediaPhoto
from database.models import add_user_bestdeal_data, add_user_lowhigh_data, get_user_id, add_query_info, DeleteMessage
from database.states import FSMRequestData
from handlers.bestdeal import get_min_price, check_bestdeal
from handlers.echo import delete_message
from handlers.start import start_command
from keyboards import key_text, keyboard_w_num, yes_no_keyboard
from keyboards.calendar import CustomCalendar
from keyboards.calendar import LSTEP
from keyboards.key_text import KEY_BACK
from keyboards.keyboards import city_markup, command_keyboard, back_keyboard
from loader import bot, exception_handler_decorator
from requests_api.request_api import request_search, request_property_list, request_details
from settings import constants
from settings.constants import WAITING, REQUEST_CITY_ERROR, YES, mile_to_km
from settings.settings import URL_HOTEL


# Определение команды
@exception_handler_decorator
async def command_definition(message):
    if message == key_text.KEY_HIGHPRICE or message == constants.HIGHPRICE:
        return constants.HIGHPRICE
    elif message == key_text.KEY_LOWPRICE or message == constants.LOWPRICE:
        return constants.LOWPRICE
    elif message == key_text.KEY_BESTDEAL or message == constants.BESTDEAL:
        return constants.BESTDEAL
    else:
        return None


# Запись команды и времени запроса
# @exception_state_decorator
@exception_handler_decorator
async def cmd_start(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
    async with state.proxy() as data:
        if isinstance(message, types.Message):
            data['user_id'] = message.from_user.id
            data['command'] = await command_definition(message.text)
            await message.delete()
        else:
            data['user_id'] = message.from_user.id
            data['command'] = await command_definition(message.data)
        data['time'] = datetime.datetime.now()
    await choice_city(message)


# Запрос города ЕСТЬ ВОПРОС ПО data['message'
# @exception_state_decorator
@exception_handler_decorator
async def choice_city(message: types.CallbackQuery):
    await delete_message(message.from_user.id)
    bot_message = await bot.send_message(message.from_user.id, constants.CITY_ENTRY, reply_markup=back_keyboard())
    DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()
    await FSMRequestData.city.set()


#  Отмена
# @exception_state_decorator
@exception_handler_decorator
async def cancel_handler(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.delete()
    await delete_message(message.from_user.id)
    bot_message = await bot.send_message(message.from_user.id, constants.START_COMMAND, reply_markup=command_keyboard())
    DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()


# Уточняем город
# @exception_state_decorator
@exception_handler_decorator
async def get_city(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        response = await request_search(message)
        result = response.json()['sr']
        cities = list()
        for city in result:
            if city['type'] == 'CITY':
                cities.append({'city_name': city['regionNames']['fullName'], 'destination_id': city['gaiaId']})
        if len(cities) > 0:
            data['city'] = message.text.capitalize()
            await delete_message(message.from_user.id)
            await message.delete()
            bot_message = await bot.send_message(message.from_user.id, constants.CLARIFY_CITY,
                                                 reply_markup=city_markup(cities))
            DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()
            await FSMRequestData.clarify_city.set()
        else:
            await delete_message(message.from_user.id)
            await bot.send_message(message.from_user.id, REQUEST_CITY_ERROR)
            await choice_city(message, state)


# Записываем Id города
# @exception_state_decorator
@exception_handler_decorator
async def check_city(callback: types.CallbackQuery, state: FSMContext):
    await delete_message(callback.from_user.id)
    if callback.data != KEY_BACK:
        async with state.proxy() as data:
            data['cityId'] = callback.data
            for name in callback.message.reply_markup.inline_keyboard:
                if name[0]['callback_data'] == callback.data:
                    data['cityName'] = name[0]['text']
                    break
    await FSMRequestData.check_in_date.set()
    calendar, step = CustomCalendar(min_date=datetime.date.today(),
                                    max_date=datetime.date.today() + datetime.timedelta(days=180),
                                    locale='ru').build()
    bot_message = await bot.send_message(chat_id=callback.from_user.id, text=constants.CHECK_IN.format(LSTEP[step]),
                                         reply_markup=calendar)
    DeleteMessage(chat_id=callback.from_user.id, message_id=str(bot_message.message_id)).save()


# Выбираем дату заезда
# @exception_state_decorator
@exception_handler_decorator
async def get_check_in_date(callback: types.CallbackQuery, state: FSMContext):
    result, key, step = CustomCalendar(min_date=datetime.date.today(),
                                       max_date=datetime.date.today() + datetime.timedelta(days=180),
                                       locale='ru').process(callback.data)
    if not result and key:
        await bot.edit_message_text(constants.CHECK_IN.format(LSTEP[step]),
                                    callback.message.chat.id, callback.message.message_id,
                                    reply_markup=key)
    elif result:
        async with state.proxy() as data:
            data['check_in_date'] = result
        await FSMRequestData.check_out_date.set()
        calendar, step = CustomCalendar(min_date=result + datetime.timedelta(days=1),
                                        max_date=result + datetime.timedelta(days=180),
                                        locale='ru').build()
        await callback.message.edit_text(constants.CHECK_OUT.format(LSTEP[step]), reply_markup=calendar)


# Выбираем дату выезда
# @exception_state_decorator
@exception_handler_decorator
async def get_check_out_date(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        min_date = data['check_in_date']
        result, key, step = CustomCalendar(min_date=min_date + datetime.timedelta(days=1),
                                           max_date=min_date + datetime.timedelta(days=180),
                                           locale='ru').process(callback.data)
        if not result and key:
            await bot.edit_message_text(constants.CHECK_OUT.format(LSTEP[step]),
                                        callback.message.chat.id, callback.message.message_id,
                                        reply_markup=key)
        elif result:
            data['check_out_date'] = result
            await count_hotels(callback)
            data['day_period'] = int(str(data['check_out_date'] - data['check_in_date']).split()[0])


# Спрашиваем сколько отелей, функция: чтобы работала кнопка Назад
# @exception_decorator
@exception_handler_decorator
async def count_hotels(callback: types.CallbackQuery):
    await delete_message(callback.from_user.id)
    await FSMRequestData.count_hotels.set()
    bot_message = await bot.send_message(
        chat_id=callback.from_user.id,
        text=constants.COUNT_HOTELS,
        reply_markup=keyboard_w_num()
    )
    DeleteMessage(chat_id=callback.from_user.id, message_id=str(bot_message.message_id)).save()


# Записываем кол-во отелей и Уточняем какая команда была заявлена
# @exception_state_decorator
@exception_handler_decorator
async def callback_count_hotels(callback: types.CallbackQuery, state: FSMContext):
    await delete_message(callback.from_user.id)
    async with state.proxy() as data:
        if callback.data != KEY_BACK:
            data['count_hotels'] = int(callback.data)
        await callback.answer()
        if data['command'] == constants.BESTDEAL:
            await FSMRequestData.min_price.set()
            bot_message = await bot.send_message(callback.from_user.id, constants.MIN_PRICE, parse_mode='Markdown')
            DeleteMessage(chat_id=callback.from_user.id, message_id=str(bot_message.message_id)).save()
        else:
            await FSMRequestData.need_photo.set()
            bot_message = await bot.send_message(callback.from_user.id, constants.NEED_PHOTO,
                                                 reply_markup=yes_no_keyboard(), parse_mode='Markdown')
            DeleteMessage(chat_id=callback.from_user.id, message_id=str(bot_message.message_id)).save()


# Записываем нужны ли фото
# @exception_state_decorator
@exception_handler_decorator
async def callback_need_photo(callback: types.CallbackQuery, state: FSMContext):
    await delete_message(callback.from_user.id)
    if callback.data != 'Back':
        async with state.proxy() as data:
            data['need_photo'] = callback.data
    if callback.data == YES:
        await FSMRequestData.count_photo_hotels.set()
        bot_message = await bot.send_message(callback.from_user.id, constants.COUNT_PHOTO_HOTELS,
                                             reply_markup=keyboard_w_num())
        DeleteMessage(chat_id=callback.from_user.id, message_id=str(bot_message.message_id)).save()
    else:
        async with state.proxy() as data:
            data['count_photo_hotels'] = 0
            await bot.send_message(callback.from_user.id, constants.TIME_AND_COMMAND.format(
                str(data['time'].strftime('%d/%m/%Y - %H:%M:%S')),
                str(data['command'])))
        await callback.answer()
        await FSMRequestData.request.set()
        await request_hotels(callback, state)


# Записываем кол-во фото
# @exception_state_decorator
@exception_handler_decorator
async def callback_count_photo_hotels(callback: types.CallbackQuery, state: FSMContext):
    await delete_message(callback.from_user.id)
    if callback.data != KEY_BACK:
        await FSMRequestData.request.set()
        async with state.proxy() as data:
            data['count_photo_hotels'] = int(callback.data)
            bot_message = await bot.send_message(callback.from_user.id, constants.TIME_AND_COMMAND.format(
                str(data['time'].strftime('%d/%m/%Y - %H:%M:%S')),
                str(data['command'])))
            DeleteMessage(chat_id=callback.from_user.id, message_id=str(bot_message.message_id)).save()
    await callback.answer()
    await request_hotels(callback, state)


# Получаем фотографии
@exception_handler_decorator
async def create_media(hotel_photo, hotel_info):
    media_group = []
    photo_str = ''
    index = 0
    for url in hotel_photo:
        if index == hotel_info['count_photo_hotels']:
            return media_group, photo_str
        else:
            photo = url['image']['url']
            if requests.get(photo).status_code == 200:
                photo_str += photo + ' '
                media_group.append(InputMediaPhoto(photo,
                                                   caption=constants.RESULT.format(
                                                       hotel_info['name'],
                                                       hotel_info['address'],
                                                       hotel_info['distance'],
                                                       hotel_info['price'],
                                                       hotel_info['amount'],
                                                       hotel_info['link'])
                                                   if index == 0 else '',
                                                   parse_mode='Markdown'))
                index += 1


# Сортируем результат
@exception_handler_decorator
async def sort_response(response, state):
    async with state.proxy() as data:
        result = []
        for hotel in response:
            if hotel['price']['lead']['formatted'] != '$0':
                result.append(hotel)
        if data['count_hotels']:
            result = result[:data['count_hotels']]
    return result


# Делаем запрос к API
@exception_handler_decorator
async def request_hotels(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
    async with state.proxy() as data:
        bot_message = await bot.send_sticker(message.from_user.id, WAITING)
        data['waiting'] = bot_message.message_id
        DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()
        response = await request_property_list(state)
        hotels = response.json()['data']['propertySearch']['properties']
        if data['command'] == '/lowprice':
            result = await sort_response(hotels, state)
        elif data['command'] == '/highprice':
            result = await sort_response(hotels[::-1], state)
        else:
            result = await check_bestdeal(hotels, state)
        data['result'] = result
    if result:
        print('Есть результаты')
        await FSMRequestData.result.set()
        if 0 < len(result) < data['count_hotels']:
            await bot.send_message(message.from_user.id, constants.FOUND_NOT_ENOUGH.format(len(result)))
        await get_results(message, state)
    else:
        await bot.delete_message(message.from_user.id, message_id=int(data['waiting']))
        await bot.send_message(message.from_user.id, constants.NOT_FOUND, reply_markup=command_keyboard())
        await state.finish()


# Выводим весь результат
@exception_handler_decorator
async def get_results(message, state):
    async with state.proxy() as data:
        await bot.delete_message(message.from_user.id, message_id=int(data['waiting']))
        if data['command'] == constants.BESTDEAL:
            await add_user_bestdeal_data(state)
        else:
            await add_user_lowhigh_data(state)
        user = get_user_id(message)
        hotel_info = {}
        count = data['count_hotels'] if data['count_hotels'] <= len(data['result']) else len(data['result'])
        for index, hotel in enumerate(data['result']):
            print(f'{index + 1} из {count}')
            response_detail = request_details(hotel['id'])
            hotel_photo = response_detail.json()['data']['propertyInfo']['propertyGallery']['images']
            data['amount'] = int(hotel['price']['lead']['formatted'][1:].replace(',', '')) * int(data['day_period'])
            hotel_info['address'] = \
                response_detail.json()['data']['propertyInfo']['summary']['location']['address']['addressLine']
            hotel_info['distance'] = mile_to_km(hotel['destinationInfo']['distanceFromDestination']['value'])
            hotel_info['price'] = hotel['price']['lead']['formatted'][1:].replace(',', '')
            hotel_info['name'] = hotel['name']
            hotel_info['link'] = URL_HOTEL.format(hotel['id'])
            hotel_info['amount'] = data['amount']
            hotel_info['count_photo_hotels'] = data['count_photo_hotels']
            try:
                if data['count_photo_hotels'] != 0:
                    media_group, photo_str = await create_media(hotel_photo, hotel_info)
                    await bot.send_media_group(message.from_user.id, media_group)
                else:
                    photo_str = None
                    await bot.send_message(
                        message.from_user.id,
                        constants.RESULT.format(
                            hotel_info['name'],
                            hotel_info['address'],
                            hotel_info['distance'],
                            hotel_info['price'],
                            hotel_info['amount'],
                            hotel_info['link']
                        )
                    )
                add_query_info(user, hotel_info, photo_str)
            except Exception:
                pass
            if index == count - 1:
                print('Готово!')
                bot_message = await bot.send_message(
                    message.from_user.id, 'Готово ✅',
                    reply_markup=back_keyboard(),
                )
                DeleteMessage(
                    chat_id=message.from_user.id,
                    message_id=str(bot_message.message_id),
                ).save()
                await state.finish()


def register_low_highprice_handlers(dp: Dispatcher) -> None:
    # обрабатывает messages
    dp.register_message_handler(cmd_start, commands=['lowprice'], state=None)
    dp.register_message_handler(cmd_start, Text(equals=key_text.KEY_LOWPRICE, ignore_case=True), state=None)
    dp.register_message_handler(cmd_start, commands=['highprice'], state=None)
    dp.register_message_handler(cmd_start, Text(equals=key_text.KEY_HIGHPRICE, ignore_case=True), state=None)
    dp.register_message_handler(cmd_start, commands=['bestdeal'], state=None)
    dp.register_message_handler(cmd_start, Text(equals=key_text.KEY_BESTDEAL, ignore_case=True), state=None)
    # обрабатывает callbacks
    dp.register_callback_query_handler(cmd_start, Text('/lowprice'), state=None)
    dp.register_callback_query_handler(cmd_start, Text('/highprice'), state=None)
    dp.register_callback_query_handler(cmd_start, Text('/bestdeal'), state=None)
    # Команда Отмена
    dp.register_message_handler(cancel_handler, Text(equals=['/cancel'], ignore_case=True), state='*')
    # Пользователь вводит город
    dp.register_message_handler(get_city, state=FSMRequestData.city)
    dp.register_callback_query_handler(start_command, Text(KEY_BACK), state=FSMRequestData.city)
    dp.register_callback_query_handler(choice_city, Text(KEY_BACK), state=FSMRequestData.clarify_city)
    dp.register_callback_query_handler(check_city, state=FSMRequestData.clarify_city)
    # Выбираем дату заезда и выезда
    dp.register_callback_query_handler(get_check_in_date, CustomCalendar.func(),
                                       state=FSMRequestData.check_in_date)
    dp.register_callback_query_handler(get_check_out_date, CustomCalendar.func(),
                                       state=FSMRequestData.check_out_date)
    # Какое количество отелей отобразить?
    dp.register_callback_query_handler(check_city, Text(KEY_BACK), state=FSMRequestData.count_hotels)
    dp.register_callback_query_handler(callback_count_hotels, state=FSMRequestData.count_hotels)

    dp.register_message_handler(get_min_price, state=FSMRequestData.min_price)
    # Хотите ли загрузить фото отелей?
    dp.register_callback_query_handler(count_hotels, Text('Back'), state=FSMRequestData.need_photo)
    dp.register_callback_query_handler(callback_need_photo, state=FSMRequestData.need_photo)
    # Какое количество фотографий загрузить?
    dp.register_callback_query_handler(callback_count_hotels, Text(KEY_BACK), state=FSMRequestData.count_photo_hotels)
    dp.register_callback_query_handler(callback_count_photo_hotels, state=FSMRequestData.count_photo_hotels)

    dp.register_callback_query_handler(start_command, Text(KEY_BACK), state=None)
