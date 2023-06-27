"""
Файл с моделями машины состояний
"""


from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMRequestData(StatesGroup):
    city = State()
    clarify_city = State()
    check_in_date = State()
    check_out_date = State()
    min_price = State()
    max_price = State()
    min_distance = State()
    max_distance = State()
    count_hotels = State()
    need_photo = State()
    count_photo_hotels = State()
    request = State()
    result = State()


class FSMHistory(StatesGroup):
    history_menu = State()
    option_history = State()
    full_history = State()
    history_entry = State()
    last_5 = State()
    entry_of_last5 = State()
    delete_menu = State()
    deleted_entrys = State()


