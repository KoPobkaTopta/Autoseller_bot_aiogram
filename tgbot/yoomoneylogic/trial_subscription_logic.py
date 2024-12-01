from datetime import datetime, timedelta
from typing import Union
from aiogram.types import InlineKeyboardMarkup, CallbackQuery, Message
from tgbot.mongo_db.db_api import files, subs, trial

async def process_trial_subscription(
    query: Union[Message, CallbackQuery],
    settings_keyboard: InlineKeyboardMarkup,
    client_id: str,
    text_content: str,  # Это будет передаваемый текст
    pk: str,
) -> None:
    """
    Обрабатывает пробный период с отправкой текста из файла.

    Args:
        query (Union[Message, CallbackQuery]): Объект сообщения.
        settings_keyboard (InlineKeyboardMarkup): Клавиатура.
        client_id (str): ID клиента.
        text_content (str): Содержимое текста.
        pk (str): ID пакета.

    Returns:
        None
    """
    user_id: int = query.from_user.id
    date: datetime = datetime.now()

    # Удаляем старые подписки
    await subs.delete_many(filter={"user_id": user_id})

    end_date = date + timedelta(days=3)

    # Добавляем информацию о пробном периоде в базу
    await trial.insert_one(
        {
            "user_id": user_id,
            "trial_flag": "on",
            "start_date": date,
            "end_date": end_date,
        }
    )

    await subs.insert_one(
        document={
            "user_id": user_id,
            "start_date": date,
            "end_date": end_date,
            "client_id": client_id,
        }
    )

    end_date_str: str = end_date.strftime("%d.%m.%Y")

    # Добавляем или обновляем текст в базе данных
    await files.update_one(
        {"user_id": user_id},  # Фильтр по user_id
        {"$set": {"text_data": text_content}},  # Добавляем или обновляем поле text_data
        upsert=True  # Если пользователя нет, будет создан новый документ
    )

    # Отправляем текст из файла
    await query.answer(
        text=f"✅  Подписка успешно оформлена!!! \n\n\n"
             f"{text_content}\n\n"
             f"<b>Срок действия пробного периода:</b> до {end_date_str}\n\n"
             f"Перейдите в меню настроек для подключения",
        reply_markup=settings_keyboard,
    )

    # Логируем отправку
    await files.insert_one(
        {"user_id": user_id, "content": text_content, "pk": pk}
    )
