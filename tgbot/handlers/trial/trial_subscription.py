import logging
from datetime import datetime, timedelta
from typing import Optional
import os

from aiogram import Router, F, Bot
from aiogram.types import Message

from tgbot.apscheduler.apscheduler import scheduler
from tgbot.apscheduler.send_to_admin_group import notification_trial_taken
from tgbot.config import config
from tgbot.mongo_db.db_api import subs
from tgbot.utils.get_trial_image import get_text_from_file  # Новый импорт функции
from tgbot.keyboards.reply import choose_plan_keyboard
from tgbot.keyboards.inline import (
    support_keyboard,
    settings_keyboard,
)
from tgbot.yoomoneylogic.trial_subscription_logic import process_trial_subscription

trial_subscription_router = Router()


@trial_subscription_router.message(
    F.text.in_({"🔥 АКЦИЯ!!! 🔥 ⏱ Пробный период на 3 дня"})
)
async def process_pay(query: Message, bot: Bot):
    user_id: int = query.from_user.id
    user = query.from_user.full_name
    username = query.from_user.username

    # Проверяем, есть ли у пользователя активная или завершённая подписка
    sub: Optional[dict] = await subs.find_one(filter={"user_id": user_id})

    if sub:
        sub_flag = sub.get("client_id")
        if len(sub_flag) > 10:
            await query.answer(
                text="Извините! Вы уже воспользовались пробным периодом 😪"
                "Акция доступна только один раз",
                reply_markup=choose_plan_keyboard,
            )
        else:
            await query.answer(
                text="✅ Вы уже оформляли подписку\n"
                "Акция доступна только новым пользователям",
                reply_markup=choose_plan_keyboard,
            )
    else:
        text_content = ""
        client_id = ""
        pk = ""

        # Получаем текст из файла
        async for text in get_text_from_file(config.tg_bot.trial_image_folder):
            text_content = text
            break

        try:
            pk = "123"  # ID пакета, можно заменить на более сложную логику
            client_id = "Client_№" + pk + "_TRIAL"
        except Exception as e:
            logging.error(f"Ошибка обработки подписки: {e}")

        # Если текст не найден, уведомляем об этом пользователя
        if not text_content:
            await query.answer(
                text="Извините! Лимит на бесплатные подписки закончился 😪\n"
                "Ждите анонса новой акции в наших соц сетях 🙈",
                reply_markup=support_keyboard,
            )
        else:
            # Обрабатываем пробный период с текстом из файла
            await process_trial_subscription(
                query, settings_keyboard, client_id, text_content, pk
            )
            logging.info(
                f"{username} ID:{user_id} успешно завершил оформление пробного периода"
            )

            # Добавляем задание в планировщик для уведомления
            scheduler.add_job(
                notification_trial_taken,
                trigger="date",
                run_date=datetime.now() + timedelta(seconds=10),
                kwargs={
                    "bot": bot,
                    "chat_id": config.tg_bot.channel_id,
                    "user": user,
                    "username": username,
                    "client_id": client_id,
                },
            )
