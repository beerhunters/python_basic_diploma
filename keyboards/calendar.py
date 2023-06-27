from telegram_bot_calendar import DetailedTelegramCalendar

MONTHS = {
    'en': ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    'ru': ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"],
}
DAYS_OF_WEEK = {
    'en': ["M", "T", "W", "T", "F", "S", "S"],
    'ru': ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
}

LSTEP = {'y': 'Год', 'm': 'Месяц', 'd': 'День'}


class CustomCalendar(DetailedTelegramCalendar):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.days_of_week = DAYS_OF_WEEK
        self.months = MONTHS
        self.size_year = 3
        self.size_month = 4
        self.empty_nav_button = "-"
        self.empty_month_button = "-"
        self.empty_year_button = "-"
