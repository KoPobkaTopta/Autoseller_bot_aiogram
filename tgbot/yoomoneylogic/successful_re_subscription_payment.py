from datetime import datetime
from aiogram.types import InlineKeyboardMarkup, CallbackQuery
from tgbot.mongo_db.db_api import files, subs
from tgbot.phrasebook.lexicon_ru import LEXICON_RU

async def process_successful_re_subscription_payment(
    call: CallbackQuery,
    end_date_str: str,
    support_keyboard: InlineKeyboardMarkup,
    settings_keyboard: InlineKeyboardMarkup,
) -> None:
    """
    Обрабатывает успешную повторную подписку и отправляет текст.
    """
    user_id = call.from_user.id
    date = datetime.now()
    user_data = await files.find_one({"user_id": user_id})

    sub_flag = (
        await subs.find_one(filter={"user_id": user_id, "end_date": {"$gt": date}})
    ).get("client_id", "")

    if len(sub_flag) > 10:  # Для первой подписки
        # Отправляем текстовое сообщение
        await call.message.answer(
            text=f"✅  Оплата прошла успешно!!! \n\n"
                 f"Ваша подписка активирована до {end_date_str}.\n\n"
                 f"Перейдите в меню настроек для подключения.",
            reply_markup=settings_keyboard,
        )

        # Обновляем client_id в базе данных
        await subs.update_one(
            filter={"user_id": user_id, "end_date": {"$gt": date}},
            update={"$set": {"client_id": f"Client_№{user_id}"}}  # Генерация client_id
        )
    else:  # Для повторной подписки
        # Отправляем сообщение для повторной подписки
        await call.message.answer(
            text=f"✅  Оплата прошла успешно!!! \n\n"
                 f"Спасибо, что снова с нами! Ваша подписка активирована до {end_date_str}.\n\n"
                 f"Меню настроек для подключения.",
            reply_markup=settings_keyboard,
        )
