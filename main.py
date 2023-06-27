"""Файл для запуска бота. Содержит в себе все регистраторы приложения"""

from aiogram import types, Dispatcher
from loader import dp
from aiogram.utils import executor
from handlers import start, echo, low_highprice, bestdeal, history_cmd


async def set_default_commands(dp: Dispatcher):
    print('Bot online')
    await dp.bot.set_my_commands(
        [
            types.BotCommand('start', 'Старт'),
            types.BotCommand('lowprice', 'Сначала дешевле'),
            types.BotCommand('highprice', 'Сначала дороже'),
            types.BotCommand('bestdeal', 'Топ цена/расстояние'),
            types.BotCommand('history', 'История поиска'),
            types.BotCommand('help', 'Помощь'),
            types.BotCommand('cancel', 'Сброс'),
        ]
    )


start.register_start_handlers(dp)
low_highprice.register_low_highprice_handlers(dp)
bestdeal.register_bestdeal_handlers(dp)
history_cmd.register_history_handlers(dp)
echo.register_echo_handlers(dp)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=set_default_commands, skip_updates=True)
