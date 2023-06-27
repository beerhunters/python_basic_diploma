from typing import Union

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InputMediaPhoto

from database.models import DeleteMessage, User, Hotel, delete_user_and_hotel_records
from database.states import FSMHistory
from handlers.echo import delete_message
from handlers.start import start_command
from keyboards.key_text import KEY_BACK, RETURNS, HISTORY_LIST, HISTORY_SHOW_LIST, KEY_RESULT, KEY_HISTORY
from keyboards.keyboards import history_keyboard, yes_no_keyboard, paginate_keyboard, back_keyboard
from loader import bot, exception_handler_decorator
from settings.constants import REQUEST, HISTORY, RESULT, HISTORY_MENU_MESSAGE, HISTORY_DELETE_QUERY, YES


# @exception_decorator
@exception_handler_decorator
async def history_menu(message: Union[types.Message, types.CallbackQuery]):
    await delete_message(message.from_user.id)
    if isinstance(message, types.Message):
        message_text = message.text
        await message.delete()
    else:
        message_text = message.data
    bot_message = await bot.send_message(message.from_user.id, HISTORY_MENU_MESSAGE,
                                         reply_markup=history_keyboard(message_text))
    DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()
    await FSMHistory.history_menu.set()


# @exception_decorator
@exception_handler_decorator
async def show_history_menu(callback: types.CallbackQuery):
    await delete_message(callback.from_user.id)
    bot_message = await bot.send_message(callback.from_user.id, HISTORY_MENU_MESSAGE,
                                         reply_markup=history_keyboard(callback.data))
    DeleteMessage(chat_id=callback.from_user.id, message_id=str(bot_message.message_id)).save()
    await FSMHistory.option_history.set()


#
@exception_handler_decorator
async def full_history(callback: types.CallbackQuery, state: FSMContext) -> None:
    await delete_message(callback.from_user.id)
    num_page = int(callback.data.split('&')[1]) if 'paginate' in callback.data else 1
    entry = User.get_or_none(User.id_telegram == callback.from_user.id)
    await FSMHistory.full_history.set()
    if entry:
        end = User.select().where(User.id_telegram == callback.from_user.id).count()
        record = User.select().where(User.id_telegram == callback.from_user.id).order_by(User.id.desc()).paginate(
            num_page, 1)
        data = record[0]
        bot_message = await bot.send_message(callback.from_user.id, REQUEST.format(
            end + 1 - num_page,
            data.id_telegram,
            data.name_command,
            data.time_command,
            data.city,
            data.city_id,
            data.city_name,
            data.date_check_in,
            data.date_check_out,
            data.min_price if data.min_price is not None else '-',
            data.max_price if data.max_price is not None else '-',
            data.min_distance if data.min_distance is not None else '-',
            data.max_distance if data.max_distance is not None else '-',
            data.count_hotels,
            data.need_photo,
            data.count_photo_hotels if data.count_photo_hotels is not None else '-'
        ), reply_markup=await paginate_keyboard(num_page, end, state, data.id))
        DeleteMessage(chat_id=callback.from_user.id, message_id=str(bot_message.message_id)).save()
    else:
        bot_message = await bot.send_message(callback.from_user.id, 'Записей не найдено', reply_markup=back_keyboard())
        DeleteMessage(chat_id=callback.from_user.id, message_id=str(bot_message.message_id)).save()


# @exception_state_decorator
@exception_handler_decorator
async def show_history_entry(callback: types.CallbackQuery, state: FSMContext):
    await delete_message(callback.from_user.id)
    if await state.get_state() == 'FSMHistory:full_history':
        await FSMHistory.history_entry.set()
    else:
        await FSMHistory.entry_of_last5.set()
    entry_count = Hotel.select().where(Hotel.id_request == callback.data.split('&')[1]).count()
    print(f'Отелей: {entry_count} шт')
    if entry_count:
        record = Hotel.select().where(Hotel.id_request == callback.data.split('&')[1]).order_by(Hotel.id.desc())
        for hotel in record:
            name_hotel = hotel.name_hotel
            link_hotel = hotel.link_hotel
            address = hotel.address
            distance = hotel.distance
            price_per_day = hotel.price_per_day
            amount = hotel.amount
            photo = hotel.photo
            if photo:
                media_group = []
                for index, url in enumerate(photo.split(' ')[:-1]):
                    caption = RESULT.format(
                        name_hotel,
                        address,
                        distance,
                        price_per_day,
                        amount,
                        link_hotel
                    ) if index == 0 else ''
                    media_group.append(InputMediaPhoto(url, caption=caption, parse_mode='Markdown'))
                await bot.send_media_group(callback.from_user.id, media_group)
            else:
                await bot.send_message(callback.from_user.id, RESULT.format(
                    name_hotel,
                    address,
                    distance,
                    price_per_day,
                    amount,
                    link_hotel
                ))
        bot_message = await bot.send_message(callback.from_user.id, 'Готово ✅', reply_markup=back_keyboard())
        DeleteMessage(chat_id=callback.from_user.id, message_id=str(bot_message.message_id)).save()
    else:
        bot_message = await bot.send_message(callback.from_user.id, 'Записей не найдено', reply_markup=back_keyboard())
        DeleteMessage(chat_id=callback.from_user.id, message_id=str(bot_message.message_id)).save()


# @exception_state_decorator
@exception_handler_decorator
async def last_5_requests(callback: types.CallbackQuery, state: FSMContext):
    await delete_message(callback.from_user.id)
    num_page = int(callback.data.split('&')[1]) if 'paginate' in callback.data else 1
    entry = User.get_or_none(User.id_telegram == callback.from_user.id)
    await FSMHistory.last_5.set()
    if entry:
        if User.select().where(User.id_telegram == callback.from_user.id).count() > 5:
            end = 5
        else:
            end = User.select().where(User.id_telegram == callback.from_user.id).count()
        record = User.select().where(User.id_telegram == callback.from_user.id).limit(end).order_by(
            User.id.desc()).paginate(
            num_page, 1)
        data = record[0]
        bot_message = await bot.send_message(callback.from_user.id, REQUEST.format(
            end + 1 - num_page,
            data.id_telegram,
            data.name_command,
            data.time_command,
            data.city,
            data.city_id,
            data.city_name,
            data.date_check_in,
            data.date_check_out,
            data.min_price if data.min_price is not None else '-',
            data.max_price if data.max_price is not None else '-',
            data.min_distance if data.min_distance is not None else '-',
            data.max_distance if data.max_distance is not None else '-',
            data.count_hotels,
            data.need_photo,
            data.count_photo_hotels if data.count_photo_hotels is not None else '-'
        ), reply_markup=await paginate_keyboard(num_page, end, state, data.id))
        DeleteMessage(chat_id=callback.from_user.id, message_id=str(bot_message.message_id)).save()
    else:
        bot_message = await bot.send_message(callback.from_user.id, 'Записей не найдено', reply_markup=back_keyboard())
        DeleteMessage(chat_id=callback.from_user.id, message_id=str(bot_message.message_id)).save()


# @exception_decorator
@exception_handler_decorator
async def history_erase_request(callback: types.CallbackQuery):
    await delete_message(callback.from_user.id)
    await FSMHistory.delete_menu.set()
    bot_message = await bot.send_message(callback.from_user.id, HISTORY_DELETE_QUERY,
                                         reply_markup=yes_no_keyboard())
    DeleteMessage(chat_id=callback.from_user.id, message_id=str(bot_message.message_id)).save()


# @exception_state_decorator
@exception_handler_decorator
async def delete_history(callback: types.CallbackQuery, state: FSMContext):
    await delete_message(callback.from_user.id)
    await FSMHistory.deleted_entrys.set()
    record = User.select().where(User.id_telegram == callback.from_user.id)
    if not record:
        bot_message = await bot.send_message(callback.from_user.id, 'История пустая', reply_markup=back_keyboard())
        DeleteMessage(chat_id=callback.from_user.id, message_id=str(bot_message.message_id)).save()
    else:
        for _ in record:
            await delete_user_and_hotel_records(callback.from_user.id)
        bot_message = await bot.send_message(callback.from_user.id, 'История успешно очищена',
                                             reply_markup=back_keyboard())
        DeleteMessage(chat_id=callback.from_user.id, message_id=str(bot_message.message_id)).save()


def register_history_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(history_menu, commands=['history'], state=None)
    dp.register_message_handler(history_menu, Text(equals=KEY_HISTORY, ignore_case=True), state=None)

    dp.register_callback_query_handler(history_menu, Text(HISTORY), state=None)
    dp.register_callback_query_handler(show_history_menu, Text(HISTORY_LIST[0]), state=FSMHistory.history_menu)
    dp.register_callback_query_handler(start_command, Text(RETURNS), state=FSMHistory.history_menu)

    dp.register_callback_query_handler(history_menu, Text(RETURNS), state=FSMHistory.option_history)
    dp.register_callback_query_handler(show_history_menu, Text(RETURNS), state=FSMHistory.option_history)

    dp.register_callback_query_handler(full_history, Text(HISTORY_SHOW_LIST[0]), state=FSMHistory.option_history)
    dp.register_callback_query_handler(show_history_menu, Text(KEY_BACK), state=FSMHistory.full_history)
    dp.register_callback_query_handler(full_history, lambda x: x.data.split('&')[0] == 'paginate',
                                       state=FSMHistory.full_history)
    dp.register_callback_query_handler(show_history_entry, lambda x: x.data.split('&')[0] == KEY_RESULT,
                                       state=FSMHistory.full_history)

    dp.register_callback_query_handler(last_5_requests, Text(HISTORY_SHOW_LIST[1]), state=FSMHistory.option_history)
    dp.register_callback_query_handler(show_history_menu, Text(KEY_BACK), state=FSMHistory.last_5)
    dp.register_callback_query_handler(last_5_requests, lambda x: x.data.split('&')[0] == 'paginate',
                                       state=FSMHistory.last_5)
    dp.register_callback_query_handler(show_history_entry, lambda x: x.data.split('&')[0] == KEY_RESULT,
                                       state=FSMHistory.last_5)

    dp.register_callback_query_handler(full_history, Text(KEY_BACK), state=FSMHistory.history_entry)
    dp.register_callback_query_handler(last_5_requests, Text(KEY_BACK), state=FSMHistory.entry_of_last5)

    dp.register_callback_query_handler(history_erase_request, Text(HISTORY_LIST[1]), state=FSMHistory.history_menu)
    dp.register_callback_query_handler(history_menu, Text(RETURNS), state=FSMHistory.delete_menu)
    dp.register_callback_query_handler(delete_history, Text(YES), state=FSMHistory.delete_menu)
    dp.register_callback_query_handler(start_command, Text(KEY_BACK), state=FSMHistory.deleted_entrys)
