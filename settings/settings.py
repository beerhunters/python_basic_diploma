"""
Файл содержащий Token бота и данные для подключения к БД
"""

import os

from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('Файл .env отсутствует')
else:
    load_dotenv()

TOKEN = os.environ.get('TOKEN')
# API_KEY = os.environ.get('API_KEY')

'''База данных'''
DATABASE = os.environ.get('DATABASE')
LOGIN = os.environ.get('LOGIN')
PASSWORD = os.environ.get('PASSWORD')
HOST = os.environ.get('HOST')
PORT = os.environ.get('PORT')

'''Поддержка'''
# токен другого бота
SUPPORT = os.environ.get('SUPPORT')
# id канала
CHANNEL = os.environ.get('CHANNEL')
# название этого бота
BOT_NAME = os.environ.get('BOT_NAME')

'''Токен Api'''
API_KEY = os.environ.get('API_KEY')

HEADERS = {
    'content-type': 'application/json',
    'X-RapidAPI-Key': API_KEY,
    'X-RapidAPI-Host': 'hotels4.p.rapidapi.com'
}

URL_SEARCH = 'https://hotels4.p.rapidapi.com/locations/v3/search'
URL_PROPERTY_LIST = 'https://hotels4.p.rapidapi.com/properties/v2/list'
URL_DETAIL = 'https://hotels4.p.rapidapi.com/properties/v2/detail'
URL_HOTEL = 'https://www.hotels.com/h{}.Hotel-Information'

# query_search
QUERY_SEARCH = {
    'q': None,
    'locale': 'ru_RU',
    'langid': '1033',
    'siteid': '300000001'
}

# query_property_list
QUERY_PROPERTY_LIST = {
    'currency': 'RUB',
    'eapid': 1,
    'locale': 'ru_RU',
    'siteId': 300000001,
    'destination': {
        'regionId': '179995'
    },
    'checkInDate': {
        'day': 5,
        'month': 12,
        'year': 2022
    },
    'checkOutDate': {
        'day': 11,
        'month': 12,
        'year': 2022
    },
    'rooms': [
        {
            'adults': 1
        }
    ],
    'resultsStartingIndex': 0,
    'resultsSize': 200,
    'sort': 'PRICE_LOW_TO_HIGH',
    'filters': {
            'price': {
                'max': None,
                'min': None
            }
        }
}


QUERY_DETAIL = {
    'currency': 'RUB',
    'eapid': 1,
    'locale': 'ru_RU',
    'siteId': 300000001,
    'propertyId': '9209612'
}
