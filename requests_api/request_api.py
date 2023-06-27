"""
Файл с запросами
"""
import requests
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from aiogram.types.base import Integer
from requests import Response, get, post

from keyboards import key_text
from loader import logger
from settings.settings import QUERY_PROPERTY_LIST, HEADERS, URL_PROPERTY_LIST, QUERY_SEARCH, URL_SEARCH, \
    QUERY_DETAIL, URL_DETAIL


async def request_search(message: Message) -> Response:
    """
    Функция - делающая запрос на API по адресу: 'https://hotels4.p.rapidapi.com/locations/v3/search'
    """
    try:
        QUERY_SEARCH['q'] = message.text
        response = get(URL_SEARCH, headers=HEADERS, params=QUERY_SEARCH, timeout=15)
        print(f'Все ок - код {response.status_code}')
        return response
    except requests.Timeout as error:
        logger.error('В работе бота возникло исключение', exc_info=error)
        print(error)
        await request_search(message)


async def request_property_list(state: FSMContext) -> Response:
    """
       Функция - делающая запрос на API по адресу: 'https://hotels4.p.rapidapi.com/properties/list'
    """
    async with state.proxy() as data:
        try:
            QUERY_PROPERTY_LIST['destination']['regionId'] = data['cityId']
            QUERY_PROPERTY_LIST['checkInDate']['day'] = int(str(data['check_in_date']).split('-')[2])
            QUERY_PROPERTY_LIST['checkInDate']['month'] = int(str(data['check_in_date']).split('-')[1])
            QUERY_PROPERTY_LIST['checkInDate']['year'] = int(str(data['check_in_date']).split('-')[0])
            QUERY_PROPERTY_LIST['checkOutDate']['day'] = int(str(data['check_out_date']).split('-')[2])
            QUERY_PROPERTY_LIST['checkOutDate']['month'] = int(str(data['check_out_date']).split('-')[1])
            QUERY_PROPERTY_LIST['checkOutDate']['year'] = int(str(data['check_out_date']).split('-')[0])
            if data['command'] == key_text.KEY_BESTDEAL or data['command'] == '/bestdeal':
                QUERY_PROPERTY_LIST['filters']['price']['min'] = int(data['min_price'])
                QUERY_PROPERTY_LIST['filters']['price']['max'] = int(data['max_price'])
            response = post(URL_PROPERTY_LIST, json=QUERY_PROPERTY_LIST, headers=HEADERS, timeout=15)
            return response
        except requests.Timeout as error:
            logger.error('В работе бота возникло исключение', exc_info=error)
            print(error)
            await request_property_list(state)


def request_details(hotel_id: Integer):
    try:
        QUERY_DETAIL['propertyId'] = str(hotel_id)
        response = post(URL_DETAIL, json=QUERY_DETAIL, headers=HEADERS, timeout=15)
        return response
    except requests.Timeout as error:
        logger.error('В работе бота возникло исключение', exc_info=error)
        print(error)
        request_details(hotel_id)
