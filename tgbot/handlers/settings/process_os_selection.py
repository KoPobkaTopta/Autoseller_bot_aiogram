from datetime import datetime
from typing import Optional

from aiogram import Router, F
from aiogram.types import CallbackQuery
from tgbot.mongo_db.db_api import subs
from tgbot.phrasebook.lexicon_ru import LEXICON_RU

os_selection_settings_router = Router()

@os_selection_settings_router.callback_query(
    F.data.contains("choose_os"), flags={"throttling_key": "callback"}
)
async def process_os_selection_settings(call: CallbackQuery):
    user_id: int = call.from_user.id
    date: datetime = datetime.now()

    # Проверяем активную подписку
    sub: Optional[dict] = await subs.find_one(
        filter={"user_id": user_id, "end_date": {"$gt": date}}
    )

    if not sub:
        await call.answer(text=LEXICON_RU["not_sub"], show_alert=True)

    data: list[str] = call.data.split(":")
    _os: str = data[1]

    # Переменная для хранения текста
    text_content = ""

    # Логика для операционных систем
    if _os == "iphone":
        text_content = LEXICON_RU["iphone_support"]
    elif _os == "android":
        text_content = LEXICON_RU["android_support"]
    elif _os == "macos":
        text_content = LEXICON_RU["macos_support"]
    elif _os == "windows":
        text_content = LEXICON_RU["windows_support"]

    # Если текст не найден
    if not text_content:
        text_content = "Текстовая информация не найдена, обратитесь к администратору."

    # Отправляем только текстовое сообщение без клавиатуры
    await call.message.edit_text(
        text=text_content,
        disable_web_page_preview=True
    )

    # Логирование для диагностики
    print(f"Sent text for {user_id} ({_os}): {text_content}")
