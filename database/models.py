"""
Файл - взаимодействует с базой данных
"""
from peewee import *
from settings.settings import DATABASE, LOGIN, PASSWORD, HOST, PORT


db = PostgresqlDatabase(
    database=DATABASE,
    user=LOGIN,
    password=PASSWORD,
    host=HOST,
    port=PORT,
    autorollback=True,
    autoconnect=True,
)


class BaseModel(Model):
    id = PrimaryKeyField(unique=True)

    class Meta:
        database = db


class DeleteMessage(BaseModel):
    chat_id = BigIntegerField()
    message_id = CharField(max_length=200)

    class Meta:
        db_table = 'delete_message'


class User(BaseModel):
    id_telegram = IntegerField()
    name_command = CharField(max_length=10)
    time_command = TextField(null=True)
    city = CharField(max_length=50)
    city_id = IntegerField()
    city_name = CharField(max_length=150)
    date_check_in = DateField(null=True)
    date_check_out = DateField(null=True)
    min_distance = FloatField(null=True)
    max_distance = FloatField(null=True)
    min_price = IntegerField(null=True)
    max_price = IntegerField(null=True)
    count_hotels = IntegerField()
    need_photo = CharField(max_length=3)
    count_photo_hotels = IntegerField(null=True)

    class Meta:
        dt_table = 'Users'


class Hotel(BaseModel):
    id_request = ForeignKeyField(User, on_delete='CASCADE', related_name='hotels')
    name_hotel = TextField(null=True)
    link_hotel = TextField(null=True)
    address = TextField(null=True)
    distance = FloatField()
    price_per_day = FloatField(null=True)
    amount = FloatField(null=True)
    photo = TextField(null=True)

    class Meta:
        dt_table = 'Hotels'


db.create_tables([User, Hotel, DeleteMessage])


async def add_user_bestdeal_data(state):
    async with state.proxy() as data:
        User(
            id_telegram=data['user_id'],
            name_command=data['command'],
            time_command=str(data['time']).split('.')[0],
            city=data['city'],
            city_id=data['cityId'],
            city_name=data['cityName'],
            date_check_in=data['check_in_date'],
            date_check_out=data['check_out_date'],
            min_distance=data['min_distance'],
            max_distance=data['max_distance'],
            min_price=data['min_price'],
            max_price=data['max_price'],
            count_hotels=data['count_hotels'],
            need_photo=data['need_photo'],
            count_photo_hotels=data['count_photo_hotels']
        ).save()


async def add_user_lowhigh_data(state):
    async with state.proxy() as data:
        User(
            id_telegram=data['user_id'],
            name_command=data['command'],
            time_command=str(data['time']).split('.')[0],
            city=data['city'],
            city_id=data['cityId'],
            city_name=data['cityName'],
            date_check_in=data['check_in_date'],
            date_check_out=data['check_out_date'],
            count_hotels=data['count_hotels'],
            need_photo=data['need_photo'],
            count_photo_hotels=data['count_photo_hotels']
        ).save()


def get_user_id(message):
    return User.select().where(User.id_telegram == message.from_user.id).order_by(User.id.desc()).get().id


def add_query_info(user, hotel_info, photo_str):
    print('Записываем отель')
    Hotel(
        id_request=user,
        name_hotel=hotel_info['name'],
        link_hotel=hotel_info['link'],
        address=hotel_info['address'],
        distance=hotel_info['distance'],
        price_per_day=hotel_info['price'],
        amount=hotel_info['amount'],
        photo=photo_str
    ).save()


async def delete_user_and_hotel_records(id_telegram):
    user = User.get(User.id_telegram == id_telegram)
    user.delete_instance(recursive=True)
