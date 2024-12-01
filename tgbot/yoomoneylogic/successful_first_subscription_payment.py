from datetime import datetime
from aiogram.types import InlineKeyboardMarkup, CallbackQuery
from tgbot.mongo_db.db_api import subs
from tgbot.phrasebook.lexicon_ru import LEXICON_RU

async def process_successful_first_subscription_payment(
    call: CallbackQuery,
    end_date_str: str,
    support_keyboard: InlineKeyboardMarkup,
    settings_keyboard: InlineKeyboardMarkup,
) -> None:
    """
    Обрабатывает успешную первичную подписку и отправляет текст.
    """
    user_id = call.from_user.id
    date: datetime = datetime.now()

    # Получаем текст из лексикона для отправки
    text_content = LEXICON_RU["first_subscription_success"]  # Пример текста

    # Отправляем сообщение с текстом
    await call.message.answer(
        text=f"✅  Оплата прошла успешно!!! \n\n\n"
             f"{text_content} \n\n"
             f"<b>Срок действия:</b> до {end_date_str}\n\n"
             f"Перейдите в меню настроек для подключения",
        reply_markup=settings_keyboard,
    )

    # Обновляем данные о подписке в базе данных
    await subs.update_one(
        filter={"user_id": user_id, "end_date": {"$gt": date}},
        update={"$set": {"client_id": f"Client_№{user_id}"}}  # Можешь использовать id пользователя или свой client_id
    )
