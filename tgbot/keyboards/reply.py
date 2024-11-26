from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Оплатить"), KeyboardButton(text="Мои настройки")],
        [KeyboardButton(text="Профиль"), KeyboardButton(text="Поддержка")],
    ],
    resize_keyboard=True,
)

choose_plan_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Тариф 1 мес. - 150 руб.")],
        [KeyboardButton(text="Тариф 3 мес. - 450 руб")],
        [KeyboardButton(text="Тариф 6 мес. - 900 руб")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)
