import logging
from datetime import datetime
from typing import Any

from aiogram import Bot

from tgbot.config import config
from tgbot.mongo_db.get_data_in_mongodb import get_data_in_subs

async def notification_to_admin_group(bot: Bot) -> None:
    """
    Notify the admin group about subscriptions ending soon.

    Args:
        bot (Bot): The bot instance to send notifications.

    Returns:
        None
    """
    today: datetime = datetime.now()
    reminder_days: int = 1  # How many days before the subscription ends to send a reminder

    # Получаем данные о клиентах с подпиской из MongoDB
    clients: Any = await get_data_in_subs({"client_id": {"$exists": True}})
    
    # Проверяем, есть ли данные
    if not clients:
        logging.warning("No clients found with subscriptions.")
        return

    # Перебираем всех клиентов и проверяем, у кого скоро заканчивается подписка
    for client in clients:
        end_date: datetime = client["end_date"]
        client_id: str = client["client_id"]

        # Рассчитываем, сколько дней осталось до окончания подписки
        days_left: int = (end_date - today).days

        # Если до окончания подписки осталось от 1 до reminder_days дней
        if 0 < days_left <= reminder_days:
            message: str = (
                f"❌ У клиента: {client_id} заканчивается подписка. \n"
                f"Остался {days_left} д."
            )
            try:
                # Отправляем сообщение в группу
                await bot.send_message(chat_id=config.tg_bot.channel_id, text=message)
                logging.info(
                    f"Client: {client_id} is running out of subscriptions. Days left: {days_left}"
                )
            except Exception as e:
                logging.error(f"Failed to send message to admin group: {str(e)}")

async def notification_payment_cleared(
    bot: Bot, chat_id: int, amount: int, user: str, username: str
) -> None:
    """
    Notify about cleared payments.

    Args:
        bot (Bot): The bot instance to send notifications.
        chat_id (int): The ID of the chat to send the notification to.
        amount (int): The amount of payment cleared.
        user (str): The user who made the payment.
        username (str): The username of the user who made the payment.

    Returns:
        None
    """
    text: str = f"📣  Супер! 🔥 Пользователь: {user}({username})👤 оплатил подписку на сумму {amount} 🅿️"
    try:
        await bot.send_message(chat_id, text=text)
        logging.info(f"User: {user}({username}) has paid a subscription of {amount}")
    except Exception as e:
        logging.error(f"Failed to send payment cleared notification: {str(e)}")

async def notification_trial_taken(
    bot: Bot, chat_id: int, user: str, username: str, client_id: str
) -> None:
    """
    Notify about taken trials.

    Args:
        bot (Bot): The bot instance to send notifications.
        chat_id (int): The ID of the chat to send the notification to.
        user (str): The user who took the trial.
        username (str): The username of the user who took the trial.
        client_id (str): The ID of the client.

    Returns:
        None
    """
    text: str = (
        f"⏱ Пользователь: {user}({username})👤 оформил TRIAL(пробный период)\n"
        f"client_id: {client_id}"
    )
    try:
        await bot.send_message(chat_id, text=text)
        logging.info(f"User: {user}({username}) has taken a TRIAL(trial period). ID: {client_id}")
    except Exception as e:
        logging.error(f"Failed to send trial taken notification: {str(e)}")
