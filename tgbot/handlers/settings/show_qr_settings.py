import logging
from datetime import datetime
from typing import Optional

from aiogram import Router, F
from aiogram.types import CallbackQuery

from tgbot.keyboards.inline import support_keyboard
from tgbot.mongo_db.db_api import files, subs
from tgbot.phrasebook.lexicon_ru import LEXICON_RU

show_qr_router = Router()


@show_qr_router.callback_query(F.data.contains("show_qr"))
async def show_qr(call: CallbackQuery):
    user_id: int = call.from_user.id
    username = call.from_user.username
    date: datetime = datetime.now()

    # Проверяем, есть ли активная подписка
    sub: Optional[dict] = await subs.find_one(
        filter={"user_id": user_id, "end_date": {"$gt": date}}
    )

    # Проверяем данные пользователя
    user_data: Optional[dict] = await files.find_one({"user_id": user_id})

    # Логируем, чтобы увидеть, что возвращает база данных
    logging.info(f"User data for {user_id}: {user_data}")

    if not sub:
        # Если подписка неактивна
        await call.answer(text=LEXICON_RU["not_sub"], show_alert=True)
        return
    else:
        if user_data:
            # Проверяем, есть ли данные в поле content
            text_content: str = user_data.get("content", "Ваш текст отсутствует.")

            # Логируем, чтобы увидеть, что именно получаем из базы
            logging.info(f"Text content for {user_id}: {text_content}")

            # Отправляем текст из поля content
            await call.message.answer(
                text=text_content
            )
        else:
            # Если данных нет, отправляем сообщение об отсутствии текста
            await call.message.answer(
                text="Данные для подключения отсутствуют. Пожалуйста, обратитесь к администратору.",
                reply_markup=support_keyboard,
            )
            logging.info(f"For {user_id} {username}, text data wasn't found or sent")

